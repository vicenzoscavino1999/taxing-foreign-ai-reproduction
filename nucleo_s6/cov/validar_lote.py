"""rem123 (P4-COORD-ENSAMBLADO-PROCEDENCIA): los controles de tarea pasan a validar_coord_rec.validar_tarea, la MISMA función que aplica el
ensamblador a cada tarea; aquí quedan la identidad de C0, la lectura del manifiesto y la salida. Ningún control se elimina.
rem122 — VALIDADOR DE TAREA de la recuperación COORD (paquete lote_rec; lo invoca el conductor tras cada trabajo con la misma firma que el
validador rem119). Comprueba la identidad de C0 ANTES de importar paper2b; autentica el manifiesto, el resultado (mismo manifiesto, código del
trabajador del paquete, tarea de la partición, estado completa) y cada producto por el sha256 de sus BYTES antes de deserializarlo; después
aplica validar_coord_rec.validar_techos a ESOS productos (techos de las claves de la tarea y comparaciones de sus celdas afectadas, con la
garantía efectiva del motor). Imprime en la última línea {aceptada, dictamen, fallos}; rc 0 solo si completa_validada.
Uso: python -B -I -X utf8 validar_lote.py <raiz> <manifiesto> <resultado.json> <salida_dir> [<cobertura.json>]"""
import json
import sys
from pathlib import Path

R, MAN, RES, SAL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
AQUI = Path(__file__).resolve().parent
NUCLEO = AQUI.parents[1] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"   # C0 en su ubicación sellada
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False))
    raise SystemExit(rc)


sys.path.insert(0, str(NUCLEO / "herramientas/b"))
try:
    import aprobacion_alcance as _AA  # noqa: E402  (solo la identidad canónica de la instalación)
    ident = _AA.identidad_instalacion(NUCLEO)
except Exception as ex:  # noqa: BLE001
    salir({"aceptada": False, "dictamen": "fallo_controlado", "fallos": ["NUCLEO_ILEGIBLE:%r" % ex]}, 4)
if ident != NUCLEO_IDENTIDAD:
    salir({"aceptada": False, "dictamen": "fallo_controlado", "fallos": ["NUCLEO_DE_OTRA_IDENTIDAD"]}, 4)
sys.path.insert(0, str(AQUI))
import validar_coord_rec as VC  # noqa: E402

v = VC.validar_tarea(MAN.read_bytes(), RES, SAL)
salir({"tarea": v["tarea"], "aceptada": v["aceptada"], "dictamen": v["dictamen"], "fallos": v["fallos"], "incompletos": v["incompletos"],
       "techos": len(v["techos"]), "comparaciones": len(v["comparaciones"]), "resultado_sha256": v["resultado_sha256"], "productos_sha256": v["productos_sha256"]},
      0 if v["aceptada"] else 4)
