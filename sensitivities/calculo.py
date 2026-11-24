"""Un techo C_2 por proceso con el certificador del paquete (ModeloTeorico.capture_ceiling), regla E11 o estatutaria.

E11: nucleo_s6/instalacion/src del paquete. Estatutaria: <variante>/src (paquete derivado; ruta en SENS_VARIANTE_SRC,
que fija run_sensitivities.py). Cada regla en su
propio proceso, asi que los dos paquetes nunca conviven. Configuracion de produccion: RunConfig() por defecto
(SupConfig(), tol_converge 1e-7) y provider_for(cfg). Punto estructural fijo del testigo; phi puede sustituirse por 0 o 1
solo para los controles de esquina.

Uso: python -B -I calculo.py <E11|estatutaria> <G|N> <df|d> <bar_d> <bar_f> <testigo|0|1> <salida.json>
"""
import ctypes, ctypes.wintypes, hashlib, json, os, platform, sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PAQUETE = AQUI.parent
REGLAS = {"E11": PAQUETE / "nucleo_s6" / "instalacion" / "src",
          "estatutaria": Path(os.environ.get("SENS_VARIANTE_SRC") or AQUI / "variante" / "src")}
TESTIGOS = {
    "G": ("80438281a3a71e247e90cfa15da28abd1491faf4029d64e2516fbea6a5915d77", "80438281a3a71e24_filas.json",
          "b9a1dd995b45daf0d229a5070abbdb890ff2e295cfd4f114a4597a1cdb5ae191"),
    "N": ("36b1932e30fc81da31b81628100ef63f0ec9be5b9fdccd8cf75ffa70710f3860", "36b1932e30fc81da_filas.json",
          "b7ea92838964c4f2b10bbd9b10d5eb0364fc59e7e8b30035fa30867ef122b160"),
}
ENTORNO = {"PYTHONHASHSEED": "0", "TZ": "UTC", "BLIS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
           "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"}


class PMC(ctypes.Structure):
    _fields_ = [("cb", ctypes.wintypes.DWORD), ("PageFaultCount", ctypes.wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def pico_memoria_mb():
    c = PMC()
    c.cb = ctypes.sizeof(PMC)
    k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
    k32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PMC), ctypes.wintypes.DWORD]
    psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 2**20


def huella_paquete(src: Path) -> str:
    h = hashlib.sha256()
    for f in sorted((src / "paper2b").rglob("*.py")):
        h.update(f.relative_to(src).as_posix().encode() + b"\0" + hashlib.sha256(f.read_bytes()).hexdigest().encode() + b"\n")
    return h.hexdigest()


def cargar_testigo(diseno: str):
    unidad, archivo, h = TESTIGOS[diseno]
    raw = (AQUI / "inputs" / archivo).read_bytes()
    if hashlib.sha256(raw).hexdigest() != h:
        raise SystemExit("FILAS DEL TESTIGO ALTERADAS")
    filas = json.loads(raw)
    fc, cc = filas["frontier_context"][0], filas["capture_ceiling_result"][0]
    pay = fc["structural_key_payload"]
    if not (pay["design_v"] == diseno and pay["instrument_j"] == "df" and cc["computation_status"] == "complete"):
        raise SystemExit("TESTIGO INESPERADO")
    return unidad, pay, cc


def main():
    regla, diseno, menu, bd, bf, phi_arg, salida = sys.argv[1:8]
    bd, bf, salida = float(bd), float(bf), Path(salida)
    if salida.exists():
        raise SystemExit("LA SALIDA YA EXISTE; no se sobrescribe: %s" % salida)
    faltan = sorted(k for k, v in ENTORNO.items() if os.environ.get(k) != v)
    if faltan:
        raise SystemExit("ENTORNO DISTINTO DEL DE PRODUCCION: %s" % faltan)
    src = REGLAS[regla]
    sys.path.insert(0, str(src))
    unidad, pay, cc = cargar_testigo(diseno)
    prim = {v["parameter_id"]: float(v["value"]) for v in pay["values"]}
    if phi_arg != "testigo":
        prim["phi"] = float(phi_arg)

    from paper2b import elementales as EL
    from paper2b import run as RUN
    from paper2b.intervalos import Iv
    from paper2b.modelos import ModeloTeorico
    if not str(Path(RUN.__file__).resolve()).startswith(str(src.resolve())):
        raise SystemExit("paper2b cargado desde otra ruta: %s" % RUN.__file__)
    regla_modulo = None
    if regla == "estatutaria":
        from paper2b import incidencia_estatutaria as IE
        regla_modulo = {"regla": IE.REGLA, "supuesto_ocultamiento": IE.SUPUESTO_OCULTAMIENTO}
    cfg = RUN.RunConfig()
    modelo = RUN.provider_for(cfg)
    if not (isinstance(modelo, ModeloTeorico) and modelo.certified):
        raise SystemExit("PLATAFORMA NO CERTIFICADA (elementales.GARANTIA=%r)" % EL.GARANTIA)
    estado = modelo.state(prim)

    t0 = time.perf_counter()
    techo = modelo.capture_ceiling(estado, diseno, menu, bd, bf, True, cfg.sup)
    dt = time.perf_counter() - t0
    s = techo.sup
    Bi = modelo.engine(estado, diseno).P.B_pot
    lo = (Iv.point(s.lower) / Bi).lo if s.lower is not None else None
    hi = (Iv.point(s.upper) / Bi).hi if s.upper is not None else None
    res = {
        "regla": regla, "regla_modulo": regla_modulo, "modelo_kind": modelo.kind, "diseno": diseno, "menu": menu,
        "topes": {"bar_tau_d": bd, "bar_tau_f": bf}, "phi": prim["phi"], "phi_origen": phi_arg,
        "testigo_unidad": unidad, "punto_estructural": prim,
        "C2": techo.C2, "C2_hex": techo.C2.hex() if techo.C2 is not None else None,
        "error_certificado": techo.numerical_error,
        "error_hex": techo.numerical_error.hex() if techo.numerical_error is not None else None,
        "intervalo_certificado": [lo, hi], "estado": techo.status, "motivo": techo.reason,
        "tau_d_en_sup": s.tau_d, "tau_f_en_sup": s.tau_f, "alcanzado": s.attained, "cajas": s.final_n,
        "tipo_error": s.error_kind, "segundos": dt, "pico_memoria_mb": pico_memoria_mb(),
        "referencia_paso3": {"C2": cc["C_2"], "error": cc["numerical_error"],
                             "tau": [cc["tau_d_at_sup"], cc["tau_f_at_sup"]]},
        "configuracion": {"sup": cfg.sup.as_dict(), "sup_max_boxes": modelo.sup_max_boxes,
                          "jump_budget": modelo.jump_budget, "param_budget_s": modelo.param_budget_s,
                          "garantia": modelo.garantia},
        "paquete": {"src": str(src), "huella_py": huella_paquete(src)},
        "plataforma": {"python": sys.version, "ejecutable": sys.executable, "sistema": platform.platform()},
    }
    salida.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("regla", "diseno", "menu", "phi", "C2", "error_certificado", "intervalo_certificado",
                                          "estado", "tau_d_en_sup", "tau_f_en_sup", "segundos")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
