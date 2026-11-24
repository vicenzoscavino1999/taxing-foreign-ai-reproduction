"""rem163 — TRABAJADOR B1 (tarea B1-TRABAJO): UNA solicitud paper2b.c2_normalizado.c2_normalizado en la raíz D7 COV, diseño G compartido con N,
menú f, ModeloTeorico C0. Derivado de paquete_p7/k1_p7.py (rem153 0856f784…) y de X/preparacion/CONEXION_B1.py (rem162 43c1dfce…):
- la AUTORIDAD de la caja, fijos, cotas, menú y configuración sale del MANIFIESTO autenticado (no del llamador); la caja enviada a la pieza es
  bit a bit la raíz binaria fijada (una subcaja, otra edición o un fijo distinto no son posibles: no hay argumento para pasarlos);
- producción: puerta_b1.puerta_comun ANTES de toda otra operación (alcance verificado + decisión nativa sin modo_arnes); después manifiesto
  con procedencia completa, piezas frente al índice, cierre C0 cargado desde sus bytes con identidad de módulos (comun_b1.cargar_cierre_c0),
  plataforma ieee754_binary64_rn, configuración efectiva igual a la fijada, espías y bloqueadores; solo entonces la ÚNICA solicitud;
- sintético: manifiesto …-SINTETICO y el DOBLE INERTE declarado (pruebas/doble_b1.py, huella del manifiesto); nunca carga C0 ni calcula nada.
Escribe en exclusiva <salida>/SOLICITUD_INICIO.json (antes de la solicitud) y <salida>/EVIDENCIA_B1.json (después). No hay reintento.
Retornos: 0 completa; 3 rechazada (puerta/manifiesto/índice, sin cargar la pieza); 4 incompleta (evidencia conservada).
rem164: única diferencia, la última línea incluye evidencia_sha256 de los bytes escritos (fuente de ejecución para comun_b1.procedencia).
Uso: python -B -I -X utf8 b1_trabajo.py --modo produccion|sintetico --manifiesto M --salida DIR [--alcance A --decision D]"""
import datetime as dt
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b1 as C  # noqa: E402


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
        raise C.B1Error("DOBLE_DISTINTO_DEL_DECLARADO")
    sp = importlib.util.spec_from_file_location("doble_b1_inerte", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.modulos(d["comportamiento"]), {"tipo": "doble_inerte", "ruta": d["ruta"], "sha256": C.H(b)}


def main(a):
    op = {a[i]: a[i + 1] for i in range(0, len(a) - 1, 2)}
    modo, man_p, sal = op.get("--modo"), op.get("--manifiesto"), op.get("--salida")
    if not (modo and man_p and sal):
        salir({"estado": "rechazada", "motivo": "USO"}, 3)
    raw = Path(man_p).read_bytes()
    man, man_sha = json.loads(raw), C.H(raw)
    import puerta_b1 as PU
    try:
        alc_sha, ev = PU.puerta_comun(modo, man, man_sha, C.TAREA_TRABAJO, op.get("--alcance"), op.get("--decision"))
    except Exception as ex:   # noqa: BLE001 — cualquier rechazo de la puerta detiene antes de toda operación
        salir({"estado": "rechazada", "motivo": "PUERTA_NATIVA", "detalle": str(ex)[:300]}, 3)
    fm = C.validar_manifiesto(man)
    if fm:
        salir({"estado": "rechazada", "motivo": "MANIFIESTO_NO_VALIDO", "detalle": [str(x)[:200] for x in fm[:6]]}, 3)
    idx_p = C.AQUI / "PAQUETE_B1.json"
    cambiadas = C.piezas_cambiadas(idx_p)
    if cambiadas:
        salir({"estado": "rechazada", "motivo": "PIEZAS_DISTINTAS_DEL_INDICE", "detalle": cambiadas}, 3)
    caja, fijos, bd, bf = C.caja_de(man)
    for p in C.STRUCT:          # la raíz binaria fijada es exactamente la conversión hacia afuera de la raíz decimal fijada
        b = C.iv_bin(*man["raiz"]["decimal"][p])
        if not (C.iguales_bits(b["lo"], caja[p][0]) and C.iguales_bits(b["hi"], caja[p][1])):
            salir({"estado": "rechazada", "motivo": "RAIZ_BINARIA_NO_ES_LA_CONVERSION_FIJADA", "detalle": p}, 3)
    sint = modo == "sintetico"
    d = Path(sal)
    d.mkdir(parents=True, exist_ok=False)
    ev_doc = {"kind": "evidencia-b1-rem163", "tarea": C.TAREA_TRABAJO, "modo": modo, "sintetico": sint, "manifiesto_sha256": man_sha,
              "alcance_sha256": alc_sha, "puerta_nativa": ev, "indice_sha256": C.HF(idx_p), "inicio_utc": utc(),
              "raiz_binaria": {p: [caja[p][0], caja[p][1]] for p in C.STRUCT}, "raiz_binaria_hex": {p: [float.hex(caja[p][0]), float.hex(caja[p][1])] for p in C.STRUCT},
              "fijos": fijos, "cotas": [bd, bf], "cotas_hex": [float.hex(bd), float.hex(bf)], "diseno": C.DISENO, "j": C.MENU,
              "no_medido": ["memoria de la solicitud", "evaluaciones internas por caja", "tiempo de importación separado del de la solicitud"]}
    escribir(d / "SOLICITUD_INICIO.json", {"kind": "solicitud-b1-inicio-rem163", "manifiesto_sha256": man_sha, "alcance_sha256": alc_sha, "modo": modo,
                                           "solicitudes_planificadas": 1, "inicio_utc": ev_doc["inicio_utc"]})
    estado, motivo, out, stats, reg = "incomplete", None, None, {}, {"c2_normalizado": 0, "sup_bound": [], "bloqueadas": {}}
    try:
        if sint:
            mods, pieza_id = cargar_doble(man)
        else:
            mods, ident = C.cargar_cierre_c0()
            pieza_id = {"tipo": "c0", "ruta": str(C.C0_SRC / "paper2b"), "identidad": ident}
        ev_doc["pieza"] = pieza_id
        EL, MO, CO = mods["elementales"], mods["modelos"], mods["cobertura"]
        ev_doc["plataforma"] = {"garantia": EL.GARANTIA, "controles": EL.PLATAFORMA.get("controles")}
        if EL.GARANTIA != C.GARANTIA:
            raise C.B1Error("PLATAFORMA_NO_CONFORME")
        reg, pieza = C.espias(mods)
        model = MO.ModeloTeorico(param_budget_s=man["modelo"]["configuracion"]["param_budget_s"])
        cfg = {"proveedor": model.kind, "param_budget_s": model.param_budget_s, "struct_tol": model.struct_tol, "struct_max_boxes": model.struct_max_boxes,
               "sup_max_boxes": model.sup_max_boxes, "jump_budget_modelo": model.jump_budget, "jump_budget_encierro": 0,
               "certificado": bool(model.certified), "garantia": model.garantia}
        ev_doc["configuracion_efectiva"] = cfg
        if cfg != man["modelo"]["configuracion"]:
            raise C.B1Error("CONFIGURACION_EFECTIVA_DISTINTA")
        if tuple(CO.STRUCT) != C.STRUCT or CO.clase_c2("G", C.MENU) != "GN" or CO.clase_c2("N", C.MENU) != "GN":
            raise C.B1Error("CONTRATO_G_N_DISTINTO")
        t0 = time.time()
        ev_doc["solicitud"] = {"funcion": "paper2b.c2_normalizado.c2_normalizado", "inicio_utc": utc()}
        try:
            out = pieza(model, dict(caja), C.DISENO, C.MENU, bd, bf, fixed=dict(fijos), stats=stats)
        except Exception as ex:  # noqa: BLE001 — excepción de la solicitud: sin resultado válido, evidencia conservada
            motivo = "EXCEPCION_EN_LA_SOLICITUD:%r" % (ex,)
        ev_doc["solicitud"].update(fin_utc=utc(), pared_s=round(time.time() - t0, 3), contador=reg["c2_normalizado"])
        if not sint:
            pieza_id["identidad_posterior"] = C.comprobar_identidad(mods, ident)
    except Exception as ex:  # noqa: BLE001 — carga, plataforma o configuración: no se llegó a una solicitud válida
        motivo = motivo or "ANTES_DE_LA_SOLICITUD:%r" % (ex,)
    ev_doc["sup_bound"] = reg.get("sup_bound", [])
    ev_doc["bloqueadas"] = reg.get("bloqueadas", {})
    ev_doc["prohibidas_cargadas"] = sorted(m for m in sys.modules if m.startswith("paper2b.") and m.split(".")[1] not in C.ORDEN_CARGA)
    ev_doc["estadisticas"] = {k: stats.get(k) for k in ("normalizado", "evaluaciones", "segundos")}
    lo, hi = getattr(out, "lo", None), getattr(out, "hi", None)
    valido = isinstance(lo, float) and isinstance(hi, float) and math.isfinite(lo) and math.isfinite(hi) and lo <= hi
    ev_doc["intervalo_normalizado"] = {"lo": lo, "hi": hi, "lo_hex": float.hex(lo) if isinstance(lo, float) else None,
                                       "hi_hex": float.hex(hi) if isinstance(hi, float) else None}
    ev_doc["U_C2"] = hi if valido else None
    ev_doc["U_C2_hex"] = float.hex(hi) if valido else None
    if motivo is None:
        if out is None:
            motivo = "RESULTADO_NONE"
        elif not valido:
            motivo = "INTERVALO_INVALIDO"
        elif stats.get("normalizado") is not True:
            motivo = "NO_NORMALIZADO"
        elif reg["c2_normalizado"] != 1 or len(reg["sup_bound"]) != 1:
            motivo = "NO_ES_UNA_SOLICITUD_CON_UN_SUP_BOUND"
        elif reg["bloqueadas"] or ev_doc["prohibidas_cargadas"] or (ev_doc.get("pieza") or {}).get("identidad_posterior"):
            motivo = "BLOQUEOS_O_IDENTIDAD_POSTERIOR"
        else:
            estado = "complete"
    if estado == "complete" and reg["sup_bound"]:
        b = reg["sup_bound"][0]
        ev_doc["parada_motor"] = "tope_de_cajas" if b["boxes"] >= C.CONFIG_ESPERADA["struct_max_boxes"] else "tolerancia_o_caja_no_refinable"
        ev_doc["precision_real"] = hi - lo
    ev_doc.update(estado=estado, motivo=motivo, fin_utc=utc())
    escribir(d / "EVIDENCIA_B1.json", ev_doc)
    # rem164: la huella de los bytes escritos sale en la ÚLTIMA línea del trabajador, que el supervisor p3ctl copia a su registro de la directa
    # (logs/p3_directas/<id>.stdout.log, longitud en directa_fin): esa es la fuente de ejecución que procedencia() autentica.
    salir({"tarea": C.TAREA_TRABAJO, "estado": estado, "motivo": motivo, "U_C2": ev_doc["U_C2"], "solicitudes": reg.get("c2_normalizado"),
           "sup_bound": len(reg.get("sup_bound", [])), "bloqueadas": reg.get("bloqueadas"), "evidencia_sha256": C.HF(d / "EVIDENCIA_B1.json")},
          0 if estado == "complete" else 4)


if __name__ == "__main__":
    main(sys.argv[1:])
