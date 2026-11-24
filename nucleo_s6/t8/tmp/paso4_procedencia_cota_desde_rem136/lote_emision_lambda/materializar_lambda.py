"""rem136 — PROCEDENCIA: el resumen registra como «puerta» el contexto autenticado de esta invocación (validar_emision_lambda.puerta) y
deriva kind/productivo del modo por VE.KIND_PRODUCTO (la misma tabla que coteja verificar). Resto sin cambios (derivado de rem135 6f73b50e…).
rem135 — ETAPA 1 de la receta de emisión lambda: MATERIALIZAR el producto sucesor de T8 (candidato; producción NO habilitada).
Aplica la PUERTA antes de leer fuentes o crear la salida; carga entrada y finalizador por el manifiesto de emisión (validar_emision_lambda.cargar)
y escribe en un directorio NUEVO: PRODUCTO_T8_LAMBDA.jsonl (una fila por fila del anexo, con clave estable, histórico completo, clasificación
derivada, finalización y procedencia), PRODUCTO_RESUMEN.json y PRODUCTO.sha256 (sello de los bytes del producto). El anexo histórico no se toca.
En modo candidata el producto queda marcado CANDIDATA; en ensayo, ENSAYO. Retornos: 0 escrito; 3 puerta negada; 6 error de trabajo.
Uso: python -B -I -X utf8 materializar_lambda.py <raiz> <manifiesto_emision> <salida_dir> --modo <produccion|candidata|ensayo>
     [--alcance <alcance_v3.json> --decision <referencia.json>]"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import validar_emision_lambda as VE  # noqa: E402

a = sys.argv[1:]
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
OP = {a[i]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
R, ME, OUT = Path(pos[0]), Path(pos[1]), Path(pos[2])
modo = OP.get("--modo")
me_raw = ME.read_bytes()
me = json.loads(me_raw)
ok, puerta = VE.puerta(R, me_raw, me, modo, OP.get("--alcance"), OP.get("--decision"), "LAMBDA-T8-MATERIALIZAR")
if not ok:
    print(json.dumps({"etapa": "materializar", "puerta": puerta}, ensure_ascii=False))
    raise SystemExit(3)
try:
    E, fin = VE.cargar(R, me)
    filas = VE.construir_producto(E, fin, me)
    rs = VE.resumen_de(filas, me)
    raw = b"".join(VE.canon(f) + b"\n" for f in filas)
    OUT.mkdir(parents=True, exist_ok=False)
    with (OUT / VE.PRODUCTO).open("xb") as fh:
        fh.write(raw)
    sha = VE.H(raw)
    with (OUT / VE.SELLO).open("x", encoding="utf-8") as fh:
        fh.write(sha + "\n")
    doc = {"kind": VE.KIND_PRODUCTO[modo], "modo": modo,
           "productivo": modo == "produccion", "puerta": puerta, "manifiesto_emision_sha256": VE.H(me_raw), "producto": VE.PRODUCTO,
           "producto_sha256": sha, "resumen": rs, "anexo_historico": "se conserva aparte, sin cambios (fuente anexo_t8 del manifiesto de fuentes)"}
    with (OUT / VE.RESUMEN).open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    print(json.dumps({"etapa": "materializar", "modo": modo, "producto_sha256": sha, "resumen": rs}, ensure_ascii=False, default=str))
except Exception as ex:  # noqa: BLE001 — un error de trabajo nunca es éxito
    print(json.dumps({"etapa": "materializar", "error": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
    raise SystemExit(6)
