"""rem137 — ETAPA 1 de la receta de captura: MATERIALIZAR la VISTA de captura por fila de T8 (candidato; producción NO habilitada; mismo patrón
que materializar_lambda.py de rem136). Aplica la PUERTA antes de leer fuentes o crear la salida; carga certificación, finalizador, base λ y
pruebas por el manifiesto (conexion_captura.cargar) y escribe en un directorio NUEVO: VISTA_T8_CAPTURA.jsonl (13.656 filas; las no-captura,
copiadas sin cambios de la base λ; las de captura, con «captura_c2»), VISTA_RESUMEN.json y VISTA.sha256 (sello de los bytes de la vista).
El resumen registra como «puerta» el contexto autenticado de esta invocación y deriva kind/productivo del modo (KIND_PRODUCTO).
Retornos: 0 escrito; 3 puerta negada (nada se crea); 6 error de trabajo.
Uso: python -B -I -X utf8 materializar_captura.py <raiz> <manifiesto_captura> <salida_dir> --modo <produccion|candidata|ensayo>
     [--alcance <alcance_v3.json> --decision <referencia.json>]"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import conexion_captura as CC  # noqa: E402

a = sys.argv[1:]
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
OP = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
R, ME, OUT = Path(pos[0]), Path(pos[1]), Path(pos[2])
modo = OP.get("--modo")
me_raw = ME.read_bytes()
me = json.loads(me_raw)
ok, puerta = CC.puerta(R, me_raw, me, modo, OP.get("--alcance"), OP.get("--decision"), "CAPTURA-T8-MATERIALIZAR")
if not ok:
    print(json.dumps({"etapa": "materializar", "puerta": puerta}, ensure_ascii=False))
    raise SystemExit(3)
try:
    carga = CC.cargar(R, me)
    filas = CC.construir_vista(carga, me)
    rs = CC.resumen_de(filas, me)
    raw = b"".join(CC.canon(f) + b"\n" for f in filas)
    OUT.mkdir(parents=True, exist_ok=False)
    with (OUT / CC.PRODUCTO).open("xb") as fh:
        fh.write(raw)
    sha = CC.H(raw)
    with (OUT / CC.SELLO).open("x", encoding="utf-8") as fh:
        fh.write(sha + "\n")
    doc = {"kind": CC.KIND_PRODUCTO[modo], "modo": modo, "productivo": modo == "produccion", "puerta": puerta,
           "manifiesto_captura_sha256": CC.H(me_raw), "producto": CC.PRODUCTO, "producto_sha256": sha, "resumen": rs,
           "base_lambda_sha256": CC.H(carga["base_raw"]), "pruebas_sha256": CC.H(carga["pruebas_raw"]),
           "nota": "vista de captura: no finaliza estados reales, no modifica el producto λ ni promueve λ; la base se conserva aparte"}
    with (OUT / CC.RESUMEN).open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    print(json.dumps({"etapa": "materializar", "modo": modo, "producto_sha256": sha, "resumen": rs}, ensure_ascii=False, default=str))
except Exception as ex:  # noqa: BLE001 — un error de trabajo nunca es éxito
    print(json.dumps({"etapa": "materializar", "error": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
    raise SystemExit(6)
