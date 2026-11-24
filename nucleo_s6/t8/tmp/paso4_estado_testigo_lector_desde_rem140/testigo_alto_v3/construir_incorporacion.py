"""rem140 — CONSTRUCTOR del documento de INCORPORACIÓN (esquema incorporacion-fuente-testigo-alto-v1) de la fuente nueva del techo alto.
Lo rellena desde los bytes REALES de una entrega con inventario (audit/entrega.json): cada archivo con su huella y la del inventario que lo
lista; el código productor, desde la entrega que contiene este paquete; nada se inventa ni se copia de la plantilla. No valida la fuente (eso
lo hace el lector); escribe en exclusiva <salida.json> y <salida.json>.sha256. En produccion exige --decision y --dictamen (ruta del dictamen
del revisor que acepte esa entrega); en sintetico los rechaza y la etiqueta lleva el prefijo SINTETICO.
Uso: python -B -I -X utf8 construir_incorporacion.py <raiz> <salida.json> --modo produccion|sintetico --fuente <base_entrega> --etiqueta <E>
     --alcance <rel> [--decision <rel>] --codigo <base_entrega_codigo> <rel_dir_paquete> [--dictamen <ruta>] [--texto <etiqueta_doc>]"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lector_fuente_testigo as LF  # noqa: E402
import testigo_comun as TC  # noqa: E402


def opt(a, k, n=1):
    if k not in a:
        return None
    i = a.index(k)
    return a[i + 1] if n == 1 else a[i + 1:i + 1 + n]


def entrada(R, base, rel):
    inv_b = (R / base / "audit/entrega.json").read_bytes()
    f = json.loads(inv_b)["files"]
    TC.need(rel in f, "NO_LISTADO_EN_EL_INVENTARIO", "%s/%s" % (base, rel))
    h = TC.HF(R / base / rel)
    TC.need(f[rel]["sha256"] == h, "ARCHIVO_DISTINTO_DEL_INVENTARIO", rel)
    return {"base": base, "inventario_sha256": TC.sha(inv_b), "rel": rel, "sha256": h}


def main(argv):
    if len(argv) < 2 or "--modo" not in argv:
        print(__doc__.splitlines()[-2], file=sys.stderr)
        return 2
    R, out = Path(argv[0]), Path(argv[1])
    modo, base, E, alc, dec = opt(argv, "--modo"), opt(argv, "--fuente"), opt(argv, "--etiqueta"), opt(argv, "--alcance"), opt(argv, "--decision")
    cod, dicta, texto = opt(argv, "--codigo", 2), opt(argv, "--dictamen"), opt(argv, "--texto") or "techo alto e8b1f7fd… (fuente nueva)"
    try:
        TC.need(modo in ("produccion", "sintetico") and base and E and alc and cod, "USO")
        TC.need((modo == "produccion") == bool(dec) == bool(dicta), "MEZCLA_SINTETICA_PRODUCTIVA", "produccion exige decisión y dictamen; sintético ninguno")
        TC.need(not out.exists(), "SALIDA_YA_EXISTE")
        s = "testigo_salida_%s" % E
        fuente = {"alcance": entrada(R, base, alc), "decision_ref": entrada(R, base, dec) if dec else None,
                  "inicio": entrada(R, base, s + "/INICIO.json"), "resultado": entrada(R, base, s + "/RESULTADO.json"),
                  "resultado_sello": entrada(R, base, s + "/RESULTADO.json.sha256"), "validacion": entrada(R, base, s + "/VALIDACION.json"),
                  "estado_receta": entrada(R, base, "testigo_estado_%s.json" % E)}
        r = json.loads((R / base / fuente["resultado"]["rel"]).read_bytes())
        dref = json.loads((R / base / dec).read_bytes()) if dec else {}
        doc = {"kind": LF.KIND_INC, "modo": "produccion" if modo == "produccion" else "SINTETICO",
               "etiqueta": (LF.SINTETICO if modo == "sintetico" else "") + texto, "clave": LF.CLAVE, "grupo": LF.AD.GRUPO,
               "plantilla_equivalencia": LF.AD.PLANTILLA, "manifiesto": dict(LF.MANIFIESTO), "fuente": fuente,
               "codigo_productor": {n: entrada(R, cod[0], "%s/%s" % (cod[1], n)) for n in TC.PIEZAS},
               "ejecucion_declarada": {"base": base, "alcance_sha256": fuente["alcance"]["sha256"], "decision_uuid": dref.get("uuid"),
                                       "inicio_utc": r["inicio_utc"], "fin_utc": r["fin_utc"]},
               "dictamen": {"ruta": str(Path(dicta)), "sha256": TC.HF(dicta)} if dicta else None,
               "inferior": {"ceiling_id": LF.AD.CEI_INF, "prueba_aceptada_fila": LF.FILA_INF}}
    except (TC.Rechazo, KeyError, OSError, ValueError) as e:
        print(json.dumps({"rechazo": getattr(e, "codigo", type(e).__name__), "detalle": getattr(e, "detalle", str(e))[:300]}, ensure_ascii=False))
        return 3
    TC.escribir_x(out, doc)
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    with Path(str(out) + ".sha256").open("x", encoding="utf-8") as fh:
        fh.write(h + "  " + out.name + "\n")
    print(json.dumps({"incorporacion": str(out), "sha256": h, "modo": doc["modo"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
