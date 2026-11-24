"""rem139 — C3 TESTIGO ALTO v2: VALIDADOR (solo lectura salvo <salida_dir>/VALIDACION.json, exclusivo). Vuelve a pasar la MISMA puerta
(alcance completo y bytes ejecutados, con este script como validador asignado) y las fijaciones del manifiesto v2 y clasifica el resultado:
complete | incomplete | sup_not_attained | sin_resultado. Nunca promueve: un resultado conforme solo lista las filas cuya MITAD SUPERIOR
cubriría (v <= C2 - err), sin sumarlas. Retornos: 0 conforme con garantía; 4 no conforme; 3 puerta/fuentes.
Uso: python -B -I -X utf8 validar_testigo.py <raiz> <manifiesto> <salida_dir> --modo produccion|fixture --alcance <a> [--decision <ref>]"""
import hashlib
import json
import sys
from pathlib import Path

MI_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()      # bytes de este script al importarse
sys.path.insert(0, str(Path(__file__).resolve().parent))
import testigo_comun as TC  # noqa: E402


def opt(a, k):
    return a[a.index(k) + 1] if k in a else None


def main(argv):
    if len(argv) < 5 or "--modo" not in argv:
        print(__doc__.splitlines()[-1], file=sys.stderr)
        return 2
    raiz, man, salida = Path(argv[0]), Path(argv[1]), Path(argv[2])
    modo = opt(argv, "--modo")
    try:
        m, msha = TC.cargar_manifiesto(raiz, man)
        ev = TC.puerta(raiz, modo, opt(argv, "--alcance"), opt(argv, "--decision"), m, msha, "validador", __file__, MI_SHA)
    except TC.Rechazo as e:
        print(json.dumps({"rechazo": e.codigo, "detalle": e.detalle}, ensure_ascii=False))
        return 3
    doc, fallos = TC.validar_resultado(raiz, m, msha, salida, modo, ev)
    doc["puerta_validador"] = {k: ev[k] for k in ("alcance_sha256", "fixture", "ejecutado")}
    if salida.is_dir():
        TC.escribir_x(salida / "VALIDACION.json", doc)
    print(json.dumps({k: doc[k] for k in ("clase", "cumple_garantia", "fallos", "promueve")}, ensure_ascii=False))
    return 0 if doc["cumple_garantia"] else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
