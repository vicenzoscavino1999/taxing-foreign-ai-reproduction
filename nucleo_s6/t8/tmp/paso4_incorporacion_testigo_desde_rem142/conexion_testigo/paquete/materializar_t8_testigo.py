"""rem142 — ETAPA 1 de la receta T8-testigo: MATERIALIZAR la VISTA de captura T8 con la fuente nueva del testigo alto (derivado de
materializar_captura.py de P, rem137; producción NO habilitada). Aplica la PUERTA antes de leer fuentes o crear la salida; después
conexion_testigo.materializar carga por la autoridad fijada, construye las 13.656 líneas y las somete a la MISMA validación común que usa el
verificador (validar_contenido) ANTES de escribir: si falla, no se escribe nada (rc 6). Escribe en un directorio NUEVO: VISTA_T8_CAPTURA.jsonl,
VISTA_RESUMEN.json y VISTA.sha256; el resumen registra como «puerta» el contexto autenticado y deriva kind/productivo del modo.
Retornos: 0 escrito; 3 puerta negada (nada se crea); 6 error de trabajo (nada se crea).
Uso: python -B -I -X utf8 materializar_t8_testigo.py <raiz> <manifiesto> <salida_dir> --modo <produccion|candidata|ensayo>
     [--alcance <alcance_v3.json> [--decision <referencia.json>]]"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import conexion_testigo as CC  # noqa: E402

a = sys.argv[1:]
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
OP = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
R, ME, OUT = Path(pos[0]), Path(pos[1]), Path(pos[2])
modo = OP.get("--modo")
me_raw = ME.read_bytes()
me = json.loads(me_raw)
ok, puerta = CC.puerta(R, me_raw, me, modo, OP.get("--alcance"), OP.get("--decision"), "T8-TESTIGO-MATERIALIZAR")
if not ok:
    print(json.dumps({"etapa": "materializar", "puerta": puerta}, ensure_ascii=False))
    raise SystemExit(3)
try:
    sha, rs = CC.materializar(R, me_raw, me, OUT, puerta)
    print(json.dumps({"etapa": "materializar", "modo": modo, "producto_sha256": sha, "resumen": {k: rs[k] for k in ("filas", "definitivas_candidatas",
                      "pendientes", "captura_computed", "captura_outside_support", "captura_pendiente")}}, ensure_ascii=False, default=str))
except Exception as ex:  # noqa: BLE001 — un error de trabajo nunca es éxito
    print(json.dumps({"etapa": "materializar", "error": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
    raise SystemExit(6)
