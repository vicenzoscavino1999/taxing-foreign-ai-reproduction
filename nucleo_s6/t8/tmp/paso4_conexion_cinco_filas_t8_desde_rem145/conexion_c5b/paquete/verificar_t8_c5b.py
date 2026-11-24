"""rem145 — ETAPA 2 de la receta T8-C5B: VERIFICAR la vista materializada con la ÚNICA validación (conexion_c5b.verificar, que usa la
misma validar_contenido que el materializador), re-autenticando el contexto de ESTA invocación, recargando las fuentes por la autoridad
fijada y cotejando sello, procedencia, universo, claves, bytes preservados, las cinco exclusiones C5B, desigualdades, recuentos con su
identidad y corridas (derivado de verificar_t8_testigo.py de rem142, 3e20c16b…, con sustituciones contadas). Aplica la MISMA puerta antes de leer. Escribe en exclusiva
<vista_dir>/VERIFICACION.json. Retornos: 0 conforme; 3 puerta negada; 4 no conforme; 6 error.
Uso: python -B -I -X utf8 verificar_t8_c5b.py <raiz> <manifiesto> <vista_dir> --modo <...> [--alcance A [--decision D]]"""
import datetime as dt
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import conexion_c5b as CC  # noqa: E402

a = sys.argv[1:]
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
OP = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
R, ME, PD = Path(pos[0]), Path(pos[1]), Path(pos[2])
modo = OP.get("--modo")
me_raw = ME.read_bytes()
me = json.loads(me_raw)
ok, puerta = CC.puerta(R, me_raw, me, modo, OP.get("--alcance"), OP.get("--decision"), "T8-C5B-VERIFICAR")
if not ok:
    print(json.dumps({"etapa": "verificar", "puerta": puerta}, ensure_ascii=False))
    raise SystemExit(3)
try:
    conforme, fallos, det = CC.verificar(R, me_raw, PD, puerta)
    doc = {"kind": "verificacion-vista-t8-captura-c5b", "utc": dt.datetime.now(dt.timezone.utc).isoformat(), "modo": modo, "puerta": puerta,
           "manifiesto_sha256": CC.H(me_raw), "conforme": conforme, "fallos": fallos, "detalle": det}
    with (PD / "VERIFICACION.json").open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    print(json.dumps({"etapa": "verificar", "conforme": conforme, "fallos": fallos[:5]}, ensure_ascii=False))
    raise SystemExit(0 if conforme else 4)
except SystemExit:
    raise
except Exception as ex:  # noqa: BLE001
    print(json.dumps({"etapa": "verificar", "error": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
    raise SystemExit(6)
