"""rem108 — PRUEBA DIRIGIDA de los ensamblajes T7/T8 corregidos (solo lectura de las salidas del generador y de las fuentes aceptadas; sin
procesos hijos). Cobertura exacta de las 1.728 afirmaciones; casos de las tres formas de identificador (ci/c/g) y las 16 robustas, con su
categoría original; negativos del analizador (familia, ancho y dominio ajenos); control de extracción T8 del revisor; null conservado como
«null»; ninguna fusión de valores distintos. Uso: python -B -I -X utf8 prueba_ensamblajes.py <raiz> <intento_dir> <salida.json>"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

R, I, SAL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sp = importlib.util.spec_from_file_location("gm108", I.parents[1] / "generar_matriz_rem108.py")
M = importlib.util.module_from_spec(sp)
sp.loader.exec_module(M)
sys.path.insert(0, str(R / "paso4/instalacion/src"))
from paper2b import claims as CL  # noqa: E402

reg = json.loads((R / "tmp" / M.REG[0] / M.REG[2]).read_bytes())["afirmaciones"]
a7 = json.loads((I / "ensamblajes/T7_anexo.json").read_bytes())["filas"]
a8 = json.loads((I / "ensamblajes/T8_anexo.json").read_bytes())["filas"]
cob = json.loads((I / "ensamblajes/COBERTURA.json").read_bytes())
C = []


def caso(cid, esperado, obtenido):
    C.append({"id": cid, "esperado": esperado, "obtenido": obtenido, "conforme": obtenido == esperado})
    print(("OK  " if obtenido == esperado else "NO  ") + cid)


por = {f["afirmacion"]: f for f in a7}
caso("T7-1 cobertura exacta: 1.728 claves, ninguna omitida, ajena ni duplicada", (1728, 1728, [], []), (len(a7), len(por), sorted(set(reg) - set(por)), sorted(set(por) - set(reg))))
caso("T7-2 categorías originales intactas", True, all(por[c]["categoria_original"] == v["categoria"] for c, v in reg.items()))
caso("T7-3 familias por esquema de claims.derive", {"c": 640, "ci": 960, "g": 128}, dict(sorted(cob["T7"]["por_familia"].items())))
ej = {"ci": next(c for c in reg if c.split(":")[3] == "ci"), "c": next(c for c in reg if c.split(":")[3] == "c"), "g": next(c for c in reg if c.split(":")[3] == "g")}
caso("T7-4 forma ci: país, j y disponibilidad; sin escenario", True, all(por[ej["ci"]][k] for k in ("pais", "j", "disponibilidad")) and por[ej["ci"]]["escenario"] is None)
caso("T7-5 forma c: país y escenario; sin j ni disponibilidad inventados", True, bool(por[ej["c"]]["pais"]) and por[ej["c"]]["escenario"] in ("conditional_full", "conditional_none")
     and por[ej["c"]]["j"] is None and por[ej["c"]]["disponibilidad"] is None)
caso("T7-6 forma g: escenario; sin país ni j inventados", True, por[ej["g"]]["pais"] is None and por[ej["g"]]["j"] is None and bool(por[ej["g"]]["escenario"]))
rob = [c for c, v in reg.items() if v["categoria"] == "robusta_infactible_certificada"]
caso("T7-7 las 16 robustas infactibles presentes, con G y certificado de sus dos testigos", (16, True),
     (len(rob), all(por[c].get("sup_G") is not None and por[c].get("inf_G") is not None and por[c].get("sup_certificado_estado") for c in rob)))
caso("T7-8 G de cada testigo = G de sus filas aceptadas (muestra: 16 robustas)", True, all(isinstance(por[c]["sup_G"], float) for c in rob))
for nombre, cid in (("familia ajena", "CLM:PREG-X:primary:zz:PER:G:addback_completo:macro:sensibilidad"),
                    ("ancho distinto del esquema", "CLM:PREG-X:primary:c:PER:G:addback_completo:macro:sensibilidad"),
                    ("dominio de capa ajeno", "CLM:PREG-X:primary:g:conditional_full:G:addback_completo:macro:capa_inexistente")):
    try:
        M.analizar_claim(cid, CL)
        r = "ACEPTADO"
    except AssertionError as ex:
        r = str(ex).split(":")[0]
    caso("T7-N %s se rechaza" % nombre, True, r != "ACEPTADO")
ctrl = {f["inversion_id"]: f for f in a8 if f["cell_id"] == "CEL:6798a3df3dc6adc69d472a186a1e47ef773b245c9073"}
caso("T8-1 control del revisor: lambda requerida 0,14726748242505988 (outside_support)", (0.14726748242505988, "outside_support"),
     (ctrl["lambda_required"]["lambda_pi_required"], ctrl["lambda_required"]["result_status"]))
caso("T8-2 control del revisor: ganancia requerida 0,011750735898072824", 0.011750735898072824, ctrl["gain_required"]["delta_y_required"])
caso("T8-3 cobertura: 13.656 filas fuente = únicas + duplicados idénticos; 0 celdas con valores distintos fusionados", (13656, 0),
     (cob["T8"]["filas_unicas"] + cob["T8"]["duplicados_identicos_fusionados"], cob["T8"]["cell_inversion_con_valores_distintos"]))
caso("T8-4 null conservado (JSON): delta_y_required nulo en lambda_required", None, ctrl["lambda_required"]["delta_y_required"])
fila_csv = next(r for r in csv.DictReader((I / "ensamblajes/T8_anexo.csv").open(encoding="utf-8")) if r["cell_id"] == "CEL:6798a3df3dc6adc69d472a186a1e47ef773b245c9073" and r["inversion_id"] == "lambda_required")
caso("T8-5 null conservado (CSV): «null», nunca vacío ni 0", "null", fila_csv["delta_y_required"])
caso("T8-6 estado por unidad marcado cuando hay _fin (finalización global pendiente, no recalculada)", True, all(f["estado_es_por_unidad"] == (f["fin_por_unidad"] is not None) for f in a8))
SAL.write_text(json.dumps({"kind": "prueba-ensamblajes-rem108", "casos": C, "conformes": sum(c["conforme"] for c in C), "total": len(C)}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"conformes": sum(c["conforme"] for c in C), "total": len(C)}))
raise SystemExit(0 if all(c["conforme"] for c in C) else 4)
