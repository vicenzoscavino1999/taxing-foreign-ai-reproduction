"""rem139 — C3 TESTIGO ALTO v2: TRABAJADOR de UNA clave (preparado; en rem139 solo se ejecuta en modo fixture con el doble sintético).
Orden: manifiesto v2 y fijaciones → PUERTA (alcance completo frente al esperado y frente a los bytes ejecutados: este script tal como se leyó
al importarse, testigo_comun, receta y emisor; decisión nativa en produccion) → valores desde D7 y clave recalculada → salida EXCLUSIVA (un
único intento: si existe, DUPLICADO sin tocarla) → INICIO.json → cálculo → RESULTADO.json + .sha256. Nada se crea antes de la puerta.
Cálculo de produccion = la MISMA llamada de run.py (núcleo histórico 3af84a1d): state = model.state(_to_state_prim(v));
ceil = model.capture_ceiling(state, "G", "df", float(bar_tau_d), float(bar_tau_f), True, RunConfig().sup) con
model = ModeloTeorico(param_budget_s=RunConfig().inversion_budget_seconds). Sin respaldo, sin otra clave, sin cambiar tolerancias ni barrer.
Persistencia ESTRICTA de los campos reales del motor (Ceiling y SupResult completos; un campo ausente es FALLO, nunca None silencioso).
Evidencia real de módulos (produccion: sys.modules paper2b tras el cálculo) separada del entorno histórico declarado del manifiesto.
fixture: exige --doble-sintetico <modulo.py> (doble SINTÉTICO con la misma interfaz y el mismo formato) y nunca carga el modelo.
Retornos: 0 resultado escrito (cualquier clase; la valida validar_testigo.py); 3 puerta/fuentes/duplicado; 6 fallo del cálculo (sin RESULTADO).
Uso: python -B -I -X utf8 trabajador_testigo.py <raiz> <manifiesto> <salida_dir> --modo produccion|fixture
         --alcance <a.json> [--decision <ref.json>] [--doble-sintetico <doble.py>]"""
import dataclasses
import datetime as dt
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
import traceback
from pathlib import Path

MI_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()      # bytes de este script al importarse
sys.path.insert(0, str(Path(__file__).resolve().parent))
import testigo_comun as TC  # noqa: E402


def opt(a, k):
    return a[a.index(k) + 1] if k in a else None


def plano(v):
    """Copia JSON estricta de un valor del motor (sin NaN; inf como texto declarado)."""
    if isinstance(v, float):
        return v if math.isfinite(v) else {"no_finito": repr(v)}
    if isinstance(v, (bool, int, str)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [plano(x) for x in v]
    if isinstance(v, dict):
        return {str(k): plano(x) for k, x in v.items()}
    raise TC.Rechazo("CAMPO_DEL_MOTOR_NO_SERIALIZABLE", type(v).__name__)


def campos(obj, nombres, codigo):
    TC.need(dataclasses.is_dataclass(obj) and not isinstance(obj, type), codigo, type(obj).__name__)
    TC.need(tuple(f.name for f in dataclasses.fields(obj)) == nombres, codigo, "campos distintos")
    return {n: getattr(obj, n) for n in nombres}


def main(argv):
    if len(argv) < 5 or "--modo" not in argv:
        print(__doc__.splitlines()[-2], file=sys.stderr)
        return 2
    raiz, man, salida = Path(argv[0]), Path(argv[1]), Path(argv[2])
    modo, alc, dec, doble = opt(argv, "--modo"), opt(argv, "--alcance"), opt(argv, "--decision"), opt(argv, "--doble-sintetico")
    t0 = time.time()
    try:
        TC.need(not (modo == "produccion" and doble), "DOBLE_EN_PRODUCCION")
        TC.need(not (modo == "fixture" and not doble), "FIXTURE_SIN_DOBLE")
        m, msha = TC.cargar_manifiesto(raiz, man)
        ev = TC.puerta(raiz, modo, alc, dec, m, msha, "trabajador", __file__, MI_SHA)
        base = raiz / m["nucleo"]["raiz"]
        spec = importlib.util.spec_from_file_location("numeric_testigo", base / "paper2b/numeric.py")
        NUM = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(NUM)
        TC.need(TC.HF(base / "paper2b/numeric.py") == m["nucleo"]["archivos"]["paper2b/numeric.py"], "IDENTIDAD_DISTINTA", "numeric.py")
        vals = TC.valores_d7(raiz, m)
        payload, clave = TC.payload_desde_valores(m, vals, NUM.canon_dec)
        TC.need(clave == m["clave"], "CLAVE_AJENA", clave)
        TC.need(not salida.exists(), "DUPLICADO", str(salida))
        salida.mkdir(parents=True)
    except TC.Rechazo as e:
        print(json.dumps({"rechazo": e.codigo, "detalle": e.detalle}, ensure_ascii=False))
        return 3
    inicio = {"kind": "inicio-testigo-alto-c3-v2", "modo": modo, "clave": clave, "manifiesto_sha256": msha, "puerta": ev,
              "inicio_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "doble_sintetico": str(doble) if doble else None}
    TC.escribir_x(salida / "INICIO.json", inicio)
    bd, bf = float(vals["bar_tau_d"]), float(vals["bar_tau_f"])
    try:
        if modo == "produccion":
            sys.path.insert(0, str(base))
            from paper2b import modelos as MO
            from paper2b import run as RUN
            TC.need(Path(RUN.__file__).resolve().parent == (base / "paper2b").resolve(), "IDENTIDAD_DISTINTA", RUN.__file__)
            cfg = RUN.RunConfig()
            TC.need(cfg.sup.as_dict() == m["config"]["sup"] and cfg.inversion_budget_seconds == m["config"]["inversion_budget_seconds"],
                    "CONFIG_DISTINTA")
            prov = MO.ModeloTeorico(param_budget_s=cfg.inversion_budget_seconds)
            TC.need(prov.certified and prov.kind == m["config"]["proveedor"], "PROVEEDOR_NO_CERTIFICADO")
            state = prov.state(RUN._to_state_prim(vals))
            ceil = prov.capture_ceiling(state, m["diseno"], m["instrumento"], bd, bf, True, cfg.sup)
            kind, sintetico, garantia_pl, origen = prov.kind, False, prov.garantia, "sys.modules"
            modulos = {Path(mod.__file__).resolve().relative_to(base.resolve()).as_posix(): TC.HF(mod.__file__)
                       for n, mod in list(sys.modules.items()) if n.startswith("paper2b") and getattr(mod, "__file__", None)}
        else:
            spec = importlib.util.spec_from_file_location("doble_testigo", doble)
            DB = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(DB)
            TC.need(getattr(DB, "SINTETICO", False) is True, "DOBLE_NO_DECLARADO")
            ceil = DB.capture_ceiling(None, m["diseno"], m["instrumento"], bd, bf, True, None)
            kind, sintetico, garantia_pl, origen = DB.KIND, True, None, "doble_sintetico"
            modulos = DB.modulos_declarados(raiz, m)
        c = campos(ceil, TC.CAMPOS_CEIL, "CEILING_FUERA_DE_FORMATO")
        s = campos(c["sup"], TC.CAMPOS_SUP, "SUPRESULT_FUERA_DE_FORMATO")
        sup_campos = plano(s)
    except TC.Rechazo as e:
        TC.escribir_x(salida / "FALLO.json", {"rechazo": e.codigo, "detalle": e.detalle, "pared_s": round(time.time() - t0, 3)})
        print(json.dumps({"fallo": e.codigo}, ensure_ascii=False))
        return 6
    except Exception as e:  # noqa: BLE001 — se conserva la traza y se detiene; nunca se reintenta
        TC.escribir_x(salida / "FALLO.json", {"excepcion": repr(e), "traza": traceback.format_exc()[-4000:], "pared_s": round(time.time() - t0, 3)})
        print(json.dumps({"fallo": repr(e)}, ensure_ascii=False))
        return 6
    res = {"kind": "resultado-testigo-alto-c3-v2", "modo": modo, "sintetico": sintetico, "proveedor_kind": kind, "clave": clave,
           "payload_sha256": clave, "manifiesto_sha256": msha,
           "puerta": {"alcance_sha256": ev["alcance_sha256"], "fixture": ev["fixture"], "ejecutado": ev["ejecutado"]},
           "instrument_available": c["instrument_available"], "C2": c["C2"], "numerical_error_share": c["numerical_error"], "B_pot": c["B_pot"],
           "computation_status": c["status"], "reason_code": c["reason"], "attained": s["attained"], "sup_not_attained": not s["attained"],
           "converged": s["converged"], "error_kind": s["error_kind"], "tau_d_at_sup": s["tau_d"], "tau_f_at_sup": s["tau_f"],
           "sup_lower": s["lower"], "sup_upper": s["upper"], "sup_R": s["sup"], "numerical_error_R": s["numerical_error"],
           "level_values": sup_campos["level_values"], "final_n": s["final_n"], "sup_campos": sup_campos, "bd_bf": [bd, bf],
           "evidencia_real": {"origen_modulos": origen, "modulos": modulos, "archivos_fijados_sha256": TC.H(m["nucleo"]["archivos"]),
                              "garantia_plataforma": garantia_pl, "python": sys.version, "plataforma": platform.platform(), "ejecutable": sys.executable},
           "entorno_historico_declarado": m["payload"]["technical"], "inicio_utc": inicio["inicio_utc"],
           "fin_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "pared_s": round(time.time() - t0, 3)}
    TC.escribir_x(salida / "RESULTADO.json", res)
    (salida / "RESULTADO.json.sha256").write_text(TC.HF(salida / "RESULTADO.json") + "  RESULTADO.json\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("modo", "sintetico", "C2", "numerical_error_share", "computation_status", "sup_not_attained")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
