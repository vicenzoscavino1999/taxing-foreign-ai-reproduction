"""rem129 — ENSAMBLADO INTEGRAL ENF (entrada final 1 del paquete lote_integracion_enf; derivado de ensamblar_coord.py de lote_enf rem125,
fcb40469…/copia rem125: misma idea —aceptar cada fuente con la validación completa y ensamblar con las filas validadas— pero las fuentes
salen de la RUTA ÚNICA validar_integracion.validar_fuentes, que también usa el conciliador).
Puerta ANTES de leer fuentes o crear la salida (validar_integracion.puerta): produccion exige alcance v3 de integración verificado por C0 y
ligado a este manifiesto/índice/código + decisión humana nativa válida; ensayo, manifiesto -ENSAYO sin alcance; preflight, manifiesto real
sin alcance: valida fuentes y resolución hasta la selección y escribe solo PREFLIGHT.json (ningún producto integral).
Productos en <salida_nueva>/ (solo si todo se acepta): enf_techos_integrados.jsonl (26 filas: fila histórica SIN cambios + origen, tarea y
alcance de origen + procedencia declarada; la clave resuelta lleva su resolución aparte), enf_comparacion_ensamblada.jsonl (validar_ensamblado
histórico: la clave resuelta conserva G = null y su estado incomplete), enf_brechas_resueltas.jsonl (G derivado de la clave resuelta con K1
fijo y enlace al certificado), enf_comparacion_integral.jsonl (todas las celdas con G_enf, dG y origen del G) y ENSAMBLADO_INTEGRAL.json.
Si la validación falla, escribe solo ENSAMBLADO_INTEGRAL.json con el dictamen y los fallos. Última línea: {aceptada, dictamen, fallos}.
Uso: python -B -I -X utf8 ensamblar_integracion.py <raiz> <manifiesto_integracion> <salida_nueva> --modo produccion|ensayo|preflight
     [--alcance <alcance_v3.json> --decision <referencia.json>]"""
import hashlib
import json
import sys
from pathlib import Path

a = sys.argv[1:]
R, MIP, SAL = (Path(x) for x in a[:3])
OP = {a[i]: a[i + 1] for i in range(3, len(a) - 1) if a[i].startswith("--")}
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validar_integracion as VI  # noqa: E402

H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False, default=str))
    raise SystemExit(rc)


MI_RAW, MI = VI.cargar_mi(MIP)
modo = OP.get("--modo", "")
ok, puerta = VI.puerta(R, MI_RAW, MI, modo, OP.get("--alcance"), OP.get("--decision"), "ENF-ENSAMBLADO-INTEGRAL")
if not ok:
    salir({"aceptada": False, "dictamen": "detenida_en_la_puerta", "fallos": [puerta["motivo"]]}, 3)
if SAL.exists():
    salir({"aceptada": False, "dictamen": "rechazada", "fallos": ["SALIDA_YA_EXISTE"]}, 3)
F = VI.validar_fuentes(R, MI_RAW, MI, hasta="seleccion" if modo == "preflight" else "completo")
SAL.mkdir()
cab = {"manifiesto_integracion_sha256": H(MI_RAW), "modo": modo, "puerta": {k: v for k, v in puerta.items() if k != "decision"},
       "decision": puerta.get("decision"), "ensayo": F["ensayo"], "dictamen": F["dictamen"], "aceptada": F["aceptada"], "fallos": F["fallos"]}
if modo == "preflight":
    doc = dict(cab, kind="preflight-integracion-enf-rem129", origen=F.get("origen"), cobertura=F.get("cobertura"),
               resoluciones={k: {c: v[c] for c in ("estado_historico", "resolucion", "certificado", "valor_limite_R", "testigo_lateral")}
                             for k, v in (F.get("resoluciones") or {}).items()},
               nota="preflight hasta selección: fuentes y resolución validadas; ningún ensamblado ni producto integral")
    with (SAL / "PREFLIGHT.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    salir({"aceptada": F["aceptada"], "dictamen": F["dictamen"], "fallos": F["fallos"][:8], "cobertura": F.get("cobertura")}, 0 if F["aceptada"] else 4)
productos = {}
if F["aceptada"]:
    integrados = []
    for f_ in F["filas_techo"]:
        o_ = F["origen"][f_["tarea_origen"]]
        fila = {"clave_transformada_sha256": f_["clave"], "origen": f_["origen"], "tarea_origen": f_["tarea_origen"],
                "alcance_origen_sha256": o_["alcance_origen_sha256"], "resultado_origen_sha256": o_["resultado_sha256"],
                "producto_origen_sha256": o_["productos"]["enf_techos.jsonl"], "fila_historica": f_["fila"],
                "enriquecimiento": "solo procedencia declarada; la fila histórica no se recalcula ni se modifica"}
        if f_.get("resolucion"):
            fila["resolucion"] = f_["resolucion"]
        integrados.append(fila)
    for nombre, filas in (("enf_techos_integrados.jsonl", integrados), ("enf_comparacion_ensamblada.jsonl", F["filas_base"]),
                          ("enf_brechas_resueltas.jsonl", F["filas_resueltas"]), ("enf_comparacion_integral.jsonl", F["filas_integrales"])):
        with (SAL / nombre).open("x", encoding="utf-8") as f:
            f.write("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in filas))
        productos[nombre] = {"sha256": H((SAL / nombre).read_bytes()), "filas": len(filas)}
doc = dict(cab, kind="ensamblado-integral-enf-rem129", origen=F.get("origen"), cobertura=F.get("cobertura"), ensamblado=F.get("ensamblado"),
           resumen=F.get("resumen"), resoluciones=F.get("resoluciones"), productos=productos,
           alcance_de_la_integracion="deriva productos de resultados ya calculados; no reemplaza los alcances de origen de cada tarea")
with (SAL / "ENSAMBLADO_INTEGRAL.json").open("x", encoding="utf-8") as f:
    f.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
salir({"aceptada": F["aceptada"], "dictamen": F["dictamen"], "fallos": F["fallos"][:8], "cobertura": F.get("cobertura"), "resumen": F.get("resumen"),
       "productos": {k: v["filas"] for k, v in productos.items()}}, 0 if F["aceptada"] else 4)
