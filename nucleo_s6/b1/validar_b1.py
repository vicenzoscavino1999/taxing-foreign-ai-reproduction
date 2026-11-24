"""rem163 — VALIDACIÓN Y LECTURA del paquete B1 (tarea B1-VALIDACION). Derivado de paquete_p7/validar_p7.py (rem153 d7ac7392…):
- ANTES de leer la evidencia pasa por puerta_b1.puerta_comun (producción: alcance verificado contra el esperado + decisión nativa ORIGINAL
  sin modo_arnes ligada a los mismos bytes; sintético nunca habilita producción). Un rechazo escribe VALIDACION_B1.json con dictamen
  «rechazada_por_puerta», sin leer nada, y termina con rc 3;
- rem164: después de la puerta, comun_b1.procedencia (la MISMA que usa la continuación del conductor) autentica la FUENTE DE EJECUCIÓN y
  devuelve los bytes de EVIDENCIA_B1.json ligados a ella; el directorio de trabajo ya no lo elige el llamador (sale del registro p3ctl de la
  ejecución <L>_TRABAJO). Sin fuente auténtica: VALIDACION_B1.json «rechazada_por_procedencia», SIN LECTURA_B1.json, rc 4. El validador
  solo valida dentro de su propia directa <L>_VALIDACION del área indicada (entrada directa fuera de ella: rechazada);
- aplica comun_b1.validar_evidencia (la validación única de contenido, sin cambios) a esos mismos bytes;
- si es aceptada, escribe la SALIDA DERIVADA LECTURA_B1.json (comun_b1.lectura: eps 1/100 exacto, seis grupos, doce afirmaciones), y después
  VALIDACION_B1.json, que liga las huellas de la evidencia, de la lectura y de la procedencia.
NO vuelve a llamar al encierro, al modelo ni a ningún supremo. Lo que valida: procedencia (fuente de ejecución, alcance/decisión, manifiesto,
índice, tarea, modo), identidad de la pieza y de sus módulos, raíz/fijos/cotas/menú/configuración efectivos, garantía de plataforma, una
solicitud con un sup_bound de contrato fijo, intervalo finito y ordenado y U_C2 = extremo superior EXACTO del intervalo devuelto. Lo que NO
valida (depende de la garantía del motor productor aceptado): que ese intervalo encierre de verdad el supremo.
Escribe en exclusiva en <dir_salida>/ (directorio nuevo). rc 0 aceptada, 3 rechazada por la puerta, 4 rechazada.
Uso: python -B -I -X utf8 validar_b1.py <manifiesto> <modo> <dir_salida> --area A --lanzamiento L [--evidencia-sha256 H]
     [--previo RUTA_ABSOLUTA_estado_b1.json] [--alcance F [--decision D]]
     (sin --previo: fuente «lanzamiento» = ejecución <L>_TRABAJO del área A; con --previo: fuente «previo», solo la fijada por la autoridad)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b1 as C  # noqa: E402
import puerta_b1 as PU  # noqa: E402

QUE_VALIDA = ("procedencia y autoridad (fuente de ejecución autenticada, alcance, decisión nativa, manifiesto, índice, tarea, modo), identidad "
              "de la pieza y de sus módulos, raíz, fijos, cotas, menú y configuración efectivos, garantía de plataforma, una solicitud con un "
              "sup_bound de contrato fijo, intervalo finito y ordenado, U_C2 igual al extremo superior exacto del intervalo devuelto")
DEPENDE_DEL_MOTOR = ("que el intervalo devuelto encierre el supremo de C2 sobre la raíz: garantía de c2_normalizado/EM.sup_bound en "
                     "ieee754_binary64_rn (cota superior demostrada de las cajas vivas, también al alcanzar el tope de cajas); no se recalcula")
OPCIONES = ("--area", "--lanzamiento", "--evidencia-sha256", "--previo", "--alcance", "--decision")


def escribir(p, doc):
    with Path(p).open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    return C.HF(p)


def main(a):
    if len(a) < 3 or (len(a) - 3) % 2:
        print(json.dumps({"estado": "rechazada", "motivo": "USO"}))
        raise SystemExit(3)
    man_p, modo, ds = a[0:3]
    o = {a[i]: a[i + 1] for i in range(3, len(a) - 1, 2)}
    if set(o) - set(OPCIONES) or len(o) * 2 != len(a) - 3 or not (o.get("--area") and o.get("--lanzamiento")):
        print(json.dumps({"estado": "rechazada", "motivo": "USO_SIN_FUENTE_DE_PROCEDENCIA"}))
        raise SystemExit(3)
    alc_p, dec_p = o.get("--alcance"), o.get("--decision")
    raw = Path(man_p).read_bytes()
    man = json.loads(raw)
    out = Path(ds)
    out.mkdir(parents=True, exist_ok=False)
    base = {"kind": "validacion-b1-rem163", "tarea": C.TAREA_VALIDACION, "modo": modo, "manifiesto_sha256": C.H(raw), "que_valida": QUE_VALIDA,
            "depende_del_motor": DEPENDE_DEL_MOTOR, "correccion": "rem164 procedencia"}
    try:
        alc, ev = PU.puerta_comun(modo, man, C.H(raw), C.TAREA_VALIDACION, alc_p, dec_p)
    except Exception as ex:  # noqa: BLE001 — rechazo antes de toda lectura de la evidencia
        doc = dict(base, alcance_sha256=None, evidencia_sha256=None, lectura_sha256=None, fallos=["PUERTA_NATIVA: %s" % str(ex)[:240]],
                   aceptada=False, dictamen="rechazada_por_puerta")
        escribir(out / "VALIDACION_B1.json", doc)
        print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos")}, ensure_ascii=False))
        raise SystemExit(3)
    if o.get("--previo"):
        fuente = {"tipo": "previo", "estado_previo": o["--previo"]}
    else:
        fuente = {"tipo": "lanzamiento", "area": o["--area"], "lanzamiento": o["--lanzamiento"], "evidencia_sha256": o.get("--evidencia-sha256")}
    fp, er, proc = C.procedencia(fuente, modo, C.H(raw), alc, propia={"area": o["--area"], "lanzamiento": o["--lanzamiento"], "argv": list(a)})
    if fp:
        doc = dict(base, alcance_sha256=alc, puerta_nativa=ev, evidencia_sha256=None, lectura_sha256=None, procedencia=proc,
                   fallos=["PROCEDENCIA: %s" % str(x)[:240] for x in fp], aceptada=False, dictamen="rechazada_por_procedencia")
        escribir(out / "VALIDACION_B1.json", doc)
        print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos")}, ensure_ascii=False))
        raise SystemExit(4)
    idx_sha = C.HF(C.AQUI / "PAQUETE_B1.json")
    esha = C.H(er)
    f, datos = C.validar_evidencia(man, C.H(raw), er, modo, alc, idx_sha, ev)
    f = [x if isinstance(x, str) else str(x)[:300] for x in f]
    lsha = None
    if not f:
        lec = C.lectura(man, datos)
        lsha = escribir(out / "LECTURA_B1.json", {"kind": "lectura-b1-rem163", "modo": modo, "manifiesto_sha256": C.H(raw), "alcance_sha256": alc,
                                                   "evidencia_sha256": esha, "indice_sha256": idx_sha, "procedencia": proc,
                                                   "datos_validados": datos, "lectura": lec})
    doc = dict(base, alcance_sha256=alc, puerta_nativa=ev, indice_sha256=idx_sha, evidencia_sha256=esha, lectura_sha256=lsha, procedencia=proc,
               fallos=f, datos=datos, aceptada=not f, dictamen="validada" if not f else "rechazada")
    escribir(out / "VALIDACION_B1.json", doc)
    print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos", "evidencia_sha256", "lectura_sha256")}, ensure_ascii=False))
    raise SystemExit(0 if not f else 4)


if __name__ == "__main__":
    main(sys.argv[1:])
