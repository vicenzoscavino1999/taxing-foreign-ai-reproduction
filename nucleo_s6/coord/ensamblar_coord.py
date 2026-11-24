"""rem123 (P4-COORD-ENSAMBLADO-PROCEDENCIA): cada tarea se acepta con validar_coord_rec.validar_tarea, la MISMA validación completa que aplica
el validador de tarea (coherencia sintético/real y vínculo de cada techo con la tarea, el manifiesto y el alcance de su resultado incluidos),
sobre los bytes que esa función lee y autentica una vez; el ensamblado usa las filas que devuelve. La procedencia de cada tarea (directorio,
lanzamiento, sha256 del resultado y de los productos, alcance y modo) se conserva por tarea; no se exige que todas compartan alcance.
rem122 — ENSAMBLADO de la recuperación COORD (paquete lote_rec). Lo lanza el conductor como operación contenida después de validar TODAS las
tareas de la partición en el mismo lanzamiento; si las tareas se ejecutaron en lanzamientos distintos, se lanza aparte con sus directorios.
Comprueba la identidad de C0; para cada tarea de la partición localiza UNA sola salida (<lanzamiento>/<tarea>/), autentica resultado y
productos por los BYTES (mismo manifiesto, código del paquete, estado completa) y vuelve a aplicar validar_techos a ESOS productos; después
construye con validar_ensamblado las comparaciones de las 1.532 celdas del manifiesto LOTE2 autenticado, cada una con el techo de SU clave
(recalculado o reutilizado desde su fuente autenticada), K1 sin cambio y G = C2' − K1. Escribe en exclusiva <salida_lanzamiento>/ENSAMBLADO/
(coord_techos_ensamblados.jsonl, coord_comparacion_ensamblada.jsonl, ENSAMBLADO.json) y en la última línea {aceptada, dictamen, fallos}.
Uso: python -B -I -X utf8 ensamblar_coord.py <raiz> <manifiesto> <cobertura.json> <salida_lanzamiento> [<otro_lanzamiento> ...]"""
import hashlib
import json
import sys
from pathlib import Path

R, MAN, COB = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
LANZ = [Path(x) for x in sys.argv[4:]]
AQUI = Path(__file__).resolve().parent
NUCLEO = AQUI.parents[1] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False))
    raise SystemExit(rc)


if not LANZ:
    salir({"aceptada": False, "dictamen": "rechazada", "fallos": ["SIN_DIRECTORIO_DE_LANZAMIENTO"]}, 4)
sys.path.insert(0, str(NUCLEO / "herramientas/b"))
import aprobacion_alcance as _AA  # noqa: E402
if _AA.identidad_instalacion(NUCLEO) != NUCLEO_IDENTIDAD:
    salir({"aceptada": False, "dictamen": "fallo_controlado", "fallos": ["NUCLEO_DE_OTRA_IDENTIDAD"]}, 4)
sys.path.insert(0, str(AQUI))
import validar_coord_rec as VC  # noqa: E402

raw = MAN.read_bytes()
man = json.loads(raw)
co = man["L1-COORD-REC"]
an = json.loads(COB.read_bytes())
fallos, techos, origen = [], [], {}
if an.get("kind") != "cobertura-nacional-lote1" or an.get("manifiesto_sha256") != H(raw):
    fallos.append("ANEXO_DE_OTRO_MANIFIESTO")
for tarea in co["tareas"]:
    dirs = [d / tarea for d in LANZ if (d / tarea / "resultado.json").is_file()]
    if len(dirs) != 1:
        fallos.append("TAREA_SIN_SALIDA_UNICA:%s (%d)" % (tarea, len(dirs)))
        continue
    v = VC.validar_tarea(raw, dirs[0] / "resultado.json", dirs[0] / "salida")      # rem123: la misma validación completa que el validador de tarea
    if v["tarea"] != tarea:
        fallos.append("RESULTADO_DE_OTRA_TAREA_EN_SU_DIRECTORIO:%s" % tarea)
    if not v["aceptada"]:
        fallos.append("TAREA_NO_VALIDA_EN_EL_ENSAMBLADO:%s:%s" % (tarea, v["fallos"][:3] or v["incompletos"][:1]))
    techos += v["techos"]                                                          # filas de los MISMOS bytes autenticados y validados
    origen[tarea] = {"directorio": str(dirs[0]), "lanzamiento": str(dirs[0].parent), "resultado_sha256": v["resultado_sha256"], "productos": v["productos_sha256"],
                     "alcance_sha256": v["alcance_sha256"], "modo": v["modo"], "dictamen_tarea": v["dictamen"]}
ens, filas = VC.validar_ensamblado(R, co, techos)
fallos += ens["fallos"]
dictamen = "rechazada" if fallos else ens["dictamen"]
out = {"kind": "ensamblado-coord-rec-rem122", "manifiesto_sha256": H(raw), "variante": co.get("variante"), "sintetico": str(man.get("kind", "")).endswith("-SINTETICO"),
       "tareas": origen, "dictamen": dictamen, "aceptada": dictamen == "completa_validada", "fallos": fallos, "ensamblado": {k: v for k, v in ens.items() if k != "fallos"}}
D = LANZ[0] / "ENSAMBLADO"
D.mkdir()
for nombre, contenido in (("coord_techos_ensamblados.jsonl", techos), ("coord_comparacion_ensamblada.jsonl", filas)):
    with (D / nombre).open("x", encoding="utf-8") as f:
        f.write("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in contenido))
    out.setdefault("productos", {})[nombre] = H((D / nombre).read_bytes())
with (D / "ENSAMBLADO.json").open("x", encoding="utf-8") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
salir({"aceptada": out["aceptada"], "dictamen": dictamen, "fallos": fallos[:8], "filas": ens.get("filas"), "por_origen": ens.get("por_origen"),
       "con_techo_incompleto": ens.get("con_techo_incompleto")}, 0 if out["aceptada"] else 4)
