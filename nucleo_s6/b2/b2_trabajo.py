"""rem167 — TRABAJADOR B2 (tarea B2-TRABAJO). Derivado de A/paquete_b1/b1_trabajo.py (2ddd202c…):
- la AUTORIDAD del plan (afirmaciones, grupos, entradas nacionales, vértices, nodos, celdas, cotas, DME, q exterior y U_C2) sale del
  MANIFIESTO autenticado; no hay argumento para pasar otra entrada;
- producción: puerta_b2.puerta_comun ANTES de toda otra operación (alcance verificado + decisión nativa sin modo_arnes); después manifiesto con
  procedencia completa, piezas frente al índice, cierre C0 B2 (__init__, intervalos, macro, external) cargado desde sus bytes, espías de
  macro.bridge y GridCell.Q, bloqueadores del resto; proveedor REAL (comun_b2.ProveedorReal: literales autenticados, claves recomputadas);
- sintético: manifiesto …-SINTETICO y el DOBLE declarado (pruebas/doble_b2.py, huella del manifiesto) como proveedor de literales y grilla;
  el cierre C0 y la forma acoplada son los mismos. Un doble nunca habilita producción.
Escribe en exclusiva <salida>/PLAN_INICIO.json (antes de evaluar) y <salida>/EVIDENCIA_B2.json (después). Sin reintento.
Retornos: 0 completa; 3 rechazada (puerta/manifiesto/índice, sin cargar nada); 4 incompleta (evidencia conservada).
Uso: python -B -I -X utf8 b2_trabajo.py --modo produccion|sintetico --manifiesto M --salida DIR [--alcance A --decision D]"""
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b2 as C  # noqa: E402


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False, default=str))
    raise SystemExit(rc)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def escribir(p, doc):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")


def cargar_doble(man):
    d = man["doble"]
    p = C.Y / d["ruta"]
    b = p.read_bytes()
    if C.H(b) != d["sha256"]:
        raise C.B2Error("DOBLE_DISTINTO_DEL_DECLARADO")
    sp = importlib.util.spec_from_file_location("doble_b2_inerte", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.proveedor(d["comportamiento"], man), C.H(b)


def main(a):
    op = {a[i]: a[i + 1] for i in range(0, len(a) - 1, 2)}
    modo, man_p, sal = op.get("--modo"), op.get("--manifiesto"), op.get("--salida")
    if not (modo and man_p and sal):
        salir({"estado": "rechazada", "motivo": "USO"}, 3)
    raw = Path(man_p).read_bytes()
    man, man_sha = json.loads(raw), C.H(raw)
    import puerta_b2 as PU
    try:
        alc_sha, ev = PU.puerta_comun(modo, man, man_sha, C.TAREA_TRABAJO, op.get("--alcance"), op.get("--decision"))
    except Exception as ex:   # noqa: BLE001 — cualquier rechazo de la puerta detiene antes de toda operación
        salir({"estado": "rechazada", "motivo": "PUERTA_NATIVA", "detalle": str(ex)[:300], "evaluaciones": 0}, 3)
    fm = C.validar_manifiesto(man)
    if fm:
        salir({"estado": "rechazada", "motivo": "MANIFIESTO_NO_VALIDO", "detalle": [str(x)[:200] for x in fm[:6]], "evaluaciones": 0}, 3)
    idx_p = C.AQUI / C.INDICE
    cambiadas = C.piezas_cambiadas(idx_p)
    if cambiadas:
        salir({"estado": "rechazada", "motivo": "PIEZAS_DISTINTAS_DEL_INDICE", "detalle": cambiadas, "evaluaciones": 0}, 3)
    fc = C.validar_cobertura(man)
    if fc:
        salir({"estado": "rechazada", "motivo": "COBERTURA_NO_CONFORME", "detalle": [str(x)[:200] for x in fc[:6]], "evaluaciones": 0}, 3)
    sint = modo == "sintetico"
    d = Path(sal)
    d.mkdir(parents=True, exist_ok=False)
    p = C.plan(man)
    ev_doc = {"kind": C.KIND_EVIDENCIA, "tarea": C.TAREA_TRABAJO, "modo": modo, "sintetico": sint, "manifiesto_sha256": man_sha,
              "alcance_sha256": alc_sha, "puerta_nativa": ev, "indice_sha256": C.HF(idx_p), "inicio_utc": utc(), "q": man["q"], "b1": man["b1"],
              "dme_gai": man["dme_gai"]["por_cota"],
              "no_medido": ["memoria del trabajo", "tiempo de importación separado del de la evaluación"]}
    escribir(d / "PLAN_INICIO.json", {"kind": "plan-b2-inicio-rem167", "manifiesto_sha256": man_sha, "alcance_sha256": alc_sha, "modo": modo,
                                      "entradas_planificadas": {"puentes": len(p["puentes"]), "celdas": len(p["celdas"]), "contextos": len(p["union"])},
                                      "inicio_utc": ev_doc["inicio_utc"]})
    estado, motivo, reg, cuerpo = "incomplete", None, {"bridge": 0, "GridCell.Q": 0, "bloqueadas": {}}, None
    ident = None
    try:
        mods, ident = C.cargar_cierre_c0()
        ev_doc["pieza"] = {"tipo": "c0", "ruta": str(C.C0_SRC / "paper2b"), "identidad": ident}
        reg = C.espias(mods)
        if sint:
            prov, dsha = cargar_doble(man)
            ev_doc["pieza"].update(proveedor="doble_inerte", doble_sha256=dsha)
        else:
            prov = C.ProveedorReal()
            ev_doc["pieza"]["proveedor"] = "real"
        cuerpo = C.evaluar(man, mods, prov, reg)
        ev_doc["pieza"]["identidad_posterior"] = C.comprobar_identidad(ident)
    except Exception as ex:  # noqa: BLE001 — carga, proveedor o evaluación: sin resultado válido, evidencia conservada
        motivo = "EXCEPCION_EN_EL_TRABAJO:%r" % (ex,)
    if cuerpo:
        ev_doc.update(cuerpo)
    ev_doc["bloqueadas"] = reg.get("bloqueadas", {})
    ev_doc["prohibidas_cargadas"] = sorted(m for m in sys.modules if m.startswith("paper2b.") and m.split(".")[1] not in C.ORDEN_CARGA)
    if motivo is None:
        if ev_doc["bloqueadas"] or ev_doc["prohibidas_cargadas"] or (ev_doc.get("pieza") or {}).get("identidad_posterior"):
            motivo = "BLOQUEOS_O_IDENTIDAD_POSTERIOR"
        elif reg["bridge"] != len(p["puentes"]) or reg["GridCell.Q"] != len(p["celdas"]):
            motivo = "LLAMADAS_DISTINTAS_DEL_PLAN"
        else:
            estado = "complete"
    ev_doc.update(estado=estado, motivo=motivo, fin_utc=utc())
    escribir(d / "EVIDENCIA_B2.json", ev_doc)
    gr = {g: (v.get("L_K1_hex"), v.get("pendientes")) for g, v in (ev_doc.get("grupos") or {}).items()}
    salir({"tarea": C.TAREA_TRABAJO, "estado": estado, "motivo": motivo, "grupos": gr, "llamadas": {"macro.bridge": reg.get("bridge"),
           "GridCell.Q": reg.get("GridCell.Q")}, "bloqueadas": reg.get("bloqueadas"), "evidencia_sha256": C.HF(d / "EVIDENCIA_B2.json")},
          0 if estado == "complete" else 4)


if __name__ == "__main__":
    main(sys.argv[1:])
