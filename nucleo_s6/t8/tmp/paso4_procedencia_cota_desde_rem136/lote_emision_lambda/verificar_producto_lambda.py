"""rem136 — PROCEDENCIA: el contexto autenticado que devuelve la puerta de ESTA invocación se pasa a la única validación, que lo re-autentica y
coteja con él el origen declarado por el materializador (derivado de rem135 a2ec7cf1…; antes la puerta no llegaba a verificar).
rem135 — ETAPA 2 de la receta de emisión lambda: VERIFICAR el producto materializado con la ÚNICA validación (validar_emision_lambda.verificar):
lee una vez los bytes del producto, los autentica contra su sello, recomputa por la ruta aceptada y coteja universo, claves, duplicados y
faltantes, recuentos esperados, corridas, plan, procedencia y preservación de definitivas y captura. Aplica la MISMA puerta antes de leer.
Escribe en exclusiva <producto_dir>/VERIFICACION.json. Retornos: 0 conforme; 3 puerta negada; 4 no conforme; 6 error.
Uso: python -B -I -X utf8 verificar_producto_lambda.py <raiz> <manifiesto_emision> <producto_dir> --modo <...> [--alcance A --decision D]"""
import datetime as dt
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import validar_emision_lambda as VE  # noqa: E402

a = sys.argv[1:]
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
OP = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
R, ME, PD = Path(pos[0]), Path(pos[1]), Path(pos[2])
modo = OP.get("--modo")
me_raw = ME.read_bytes()
me = json.loads(me_raw)
ok, puerta = VE.puerta(R, me_raw, me, modo, OP.get("--alcance"), OP.get("--decision"), "LAMBDA-T8-VERIFICAR")
if not ok:
    print(json.dumps({"etapa": "verificar", "puerta": puerta}, ensure_ascii=False))
    raise SystemExit(3)
try:
    conforme, fallos, det = VE.verificar(R, me_raw, PD, puerta)
    doc = {"kind": "verificacion-producto-t8-lambda", "utc": dt.datetime.now(dt.timezone.utc).isoformat(), "modo": modo, "puerta": puerta,
           "manifiesto_emision_sha256": VE.H(me_raw), "conforme": conforme, "fallos": fallos, "detalle": det}
    with (PD / "VERIFICACION.json").open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    print(json.dumps({"etapa": "verificar", "conforme": conforme, "fallos": fallos[:5]}, ensure_ascii=False))
    raise SystemExit(0 if conforme else 4)
except SystemExit:
    raise
except Exception as ex:  # noqa: BLE001
    print(json.dumps({"etapa": "verificar", "error": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
    raise SystemExit(6)
