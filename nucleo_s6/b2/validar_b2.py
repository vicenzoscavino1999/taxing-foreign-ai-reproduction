"""rem167 — VALIDACIÓN, LECTURA Y CONCILIACIÓN del paquete B2 (tarea B2-VALIDACION). Derivado de A/paquete_b1/validar_b1.py (a43114db…):
- ANTES de leer la evidencia pasa por puerta_b2.puerta_comun; un rechazo escribe VALIDACION_B2.json «rechazada_por_puerta», rc 3;
- comun_b2.procedencia autentica la FUENTE DE EJECUCIÓN (registro p3ctl de <L>_TRABAJO, salida del trabajador copiada por el supervisor,
  huella del conductor) y entrega los bytes de EVIDENCIA_B2.json; fuera de su propia directa <L>_VALIDACION no hay validación (rc 4);
- carga el cierre C0 B2 con macro.bridge y GridCell.Q BLOQUEADOS (cero llamadas) y aplica comun_b2.validar_evidencia: recálculo exacto de
  s_Pi/s_T, Q (exacto y réplica float), n_min, K1 intervalar con la misma clase Iv y referencia EXACTA independiente por contexto;
- si es aceptada escribe LECTURA_B2.json (regla G_hi = U_C2 - L_K1 <= -1/100 exacta, seis grupos, doce afirmaciones, conciliación) y
  después VALIDACION_B2.json con las huellas y los recuentos de validación separados de los del trabajo.
rc 0 aceptada, 3 rechazada por la puerta, 4 rechazada.
Uso: python -B -I -X utf8 validar_b2.py <manifiesto> <modo> <dir_salida> --area A --lanzamiento L [--evidencia-sha256 H] [--alcance F [--decision D]]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b2 as C  # noqa: E402
import puerta_b2 as PU  # noqa: E402

QUE_VALIDA = ("procedencia y autoridad, identidad del cierre C0 B2 y del proveedor, q/B1/DME del manifiesto, cobertura del plan (480 puentes, "
              "60 celdas, 1.920 contextos), s_Pi/s_T exactos, Q exacto y float, n_min, premisas P7/s_T/eta_H por estado y nodo, K1 intervalar "
              "reproducido bit a bit y su encierro de la referencia exacta, minimos por grupo, lectura y conciliacion")
DEPENDE_DE = ("la autenticidad de los literales nacionales y de la grilla (produccion: claves y huellas de fila comprobadas por el trabajador "
              "y fijadas por el manifiesto) y la cota B1 aceptada por el libro 19")
OPCIONES = ("--area", "--lanzamiento", "--evidencia-sha256", "--alcance", "--decision")


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
    base = {"kind": "validacion-b2-rem167", "tarea": C.TAREA_VALIDACION, "modo": modo, "manifiesto_sha256": C.H(raw), "que_valida": QUE_VALIDA,
            "depende_de": DEPENDE_DE}
    try:
        alc, ev = PU.puerta_comun(modo, man, C.H(raw), C.TAREA_VALIDACION, alc_p, dec_p)
    except Exception as ex:  # noqa: BLE001
        doc = dict(base, alcance_sha256=None, evidencia_sha256=None, lectura_sha256=None, fallos=["PUERTA_NATIVA: %s" % str(ex)[:240]],
                   aceptada=False, dictamen="rechazada_por_puerta")
        escribir(out / "VALIDACION_B2.json", doc)
        print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos")}, ensure_ascii=False))
        raise SystemExit(3)
    fuente = {"tipo": "lanzamiento", "area": o["--area"], "lanzamiento": o["--lanzamiento"], "evidencia_sha256": o.get("--evidencia-sha256")}
    fp, er, proc = C.procedencia(fuente, modo, C.H(raw), alc, propia={"area": o["--area"], "lanzamiento": o["--lanzamiento"], "argv": list(a)})
    if fp:
        doc = dict(base, alcance_sha256=alc, puerta_nativa=ev, evidencia_sha256=None, lectura_sha256=None, procedencia=proc,
                   fallos=["PROCEDENCIA: %s" % str(x)[:240] for x in fp], aceptada=False, dictamen="rechazada_por_procedencia")
        escribir(out / "VALIDACION_B2.json", doc)
        print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos")}, ensure_ascii=False))
        raise SystemExit(4)
    idx_sha = C.HF(C.AQUI / C.INDICE)
    esha = C.H(er)
    mods, ident = C.cargar_cierre_c0()
    reg = C.espias(mods, permitir=False)          # validación: bridge y GridCell.Q bloqueados
    f, datos, rv = C.validar_evidencia(man, C.H(raw), er, modo, alc, idx_sha, ev, IV=mods["intervalos"].Iv)
    f = [x if isinstance(x, str) else str(x)[:300] for x in f]
    rv.update({"macro.bridge": reg["bridge"], "GridCell.Q": reg["GridCell.Q"], "bloqueadas": reg["bloqueadas"]})
    if reg["bloqueadas"] or C.comprobar_identidad(ident):
        f.append("VALIDACION_LLAMO_A_UNA_ENTRADA_BLOQUEADA_O_CAMBIO_SU_CIERRE")
    lsha, conc = None, None
    if not f:
        lec = C.lectura(man, datos)
        conc = C.conciliacion(man, datos, lec)
        if not conc["conforme"]:
            f.append(("CONCILIACION_NO_CONFORME", conc["fallos"]))
            f = [x if isinstance(x, str) else str(x)[:300] for x in f]
        else:
            lsha = escribir(out / "LECTURA_B2.json", {"kind": "lectura-b2-rem167", "modo": modo, "manifiesto_sha256": C.H(raw), "alcance_sha256": alc,
                                                       "evidencia_sha256": esha, "indice_sha256": idx_sha, "procedencia": proc,
                                                       "datos_validados": datos, "lectura": lec, "conciliacion": conc,
                                                       "recuentos": {"trabajo": json.loads(er).get("llamadas_trabajo"), "validacion": rv,
                                                                     "conciliacion": conc["comprobaciones"]}})
    doc = dict(base, alcance_sha256=alc, puerta_nativa=ev, indice_sha256=idx_sha, evidencia_sha256=esha, lectura_sha256=lsha, procedencia=proc,
               fallos=f, datos=datos, recuentos_validacion=rv, conciliacion=conc, aceptada=not f, dictamen="validada" if not f else "rechazada")
    escribir(out / "VALIDACION_B2.json", doc)
    print(json.dumps({k: doc[k] for k in ("tarea", "aceptada", "dictamen", "fallos", "evidencia_sha256", "lectura_sha256")}, ensure_ascii=False))
    raise SystemExit(0 if not f else 4)


if __name__ == "__main__":
    main(sys.argv[1:])
