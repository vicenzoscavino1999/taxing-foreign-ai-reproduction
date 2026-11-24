"""rem130 (P4-ENF-T1-BYTES): recuperar() devuelve también, en sel["abiertas"], las líneas de las claves abiertas tomadas de los MISMOS bytes autenticados, para que la integración no vuelva a leer el producto.
rem129 — COPIA EN lote_integracion_enf (diferencial: el certificador se carga junto al adaptador; el manifiesto de techos es un parámetro, por defecto el de lote_enf; ninguna otra lógica cambia).
rem128 — RECUPERACIÓN GRANULAR de los techos persistidos de ABL-ENF-T1 (CANDIDATA para revisión; no incorporada ni usada en producción).
T1 terminó «incompleta» en rem127 (una clave sin cierre) y el conductor no la validó. Este adaptador NO recalcula ni fabrica un resultado de
trabajador completo: lee los BYTES sellados de T1, los autentica y les aplica los mismos controles de validar_coord_rec.validar_tarea
(paquete lote_enf, sin cambios) salvo el de «resultado completo», que sustituye por la coherencia del estado incompleto:
- resultado.json igual a su sha256 fijado; mismo manifiesto, código del trabajador, tarea de la partición, coherencia sintético/real y
  alcance fijado; productos autenticados por el sha256 del resultado y conjunto exacto; cada techo y comparación ligados a su tarea,
  manifiesto y alcance;
- estado «incompleta» con motivo TECHOS_INCOMPLETOS que enumera exactamente las claves no cerradas de los productos;
- techos cerrados: validar_techos (común) sobre esas claves y sus comparaciones → debe dar completa_validada (garantía, código,
  configuración, testigo, detalle, K1 y comparaciones);
- claves no cerradas: validar_techos sobre ellas → incompleta sin fallos (cotas y motivo conservados); su estado de recuperación es
  «no_decidido» salvo que se aporte un certificado de alcance que se VUELVE A CALCULAR aquí con el certificador sobre la misma fila y
  coincida (estado no_alcanzado_demostrado): nunca pasa a «complete».
Escribe en exclusiva <salida_nueva>/: REUTILIZACION_T1.json, techos_reutilizables.jsonl y comparaciones_reutilizables.jsonl (líneas
originales byte a byte). componer() une lo recuperado con techos de tareas nuevas ya validadas sin duplicados ni faltantes.
Uso: python -B -I recuperar_t1.py <raiz> <dir_T1> <salida_nueva> [--certificado <json>] [--pin-resultado <sha>] [--pin-alcance <sha>]"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
PIN_RESULTADO = "0e1900aa5b4e0a6dcba4080a50d2587ba20cc5c3b93a1196b65eb13544064c68"
PIN_ALCANCE = "5c64a6da4d9182f03e1739cf3ff006b14b23787db5b1076cf349df66f1be58cc"
TAREA = "ABL-ENF-T1"


def _cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _lineas(b: bytes):
    return [x for x in b.split(b"\n") if x.strip()]


def recuperar(raiz, dir_t1, certificado=None, pin_resultado=PIN_RESULTADO, pin_alcance=PIN_ALCANCE, lenf=None, cert_mod=None, manifiesto=None):
    R = Path(raiz)
    LENF = Path(lenf) if lenf else R / "tmp/paso4_enforcement_desde_rem125/lote_enf"
    VC = _cargar("validar_coord_rec_recuperacion", LENF / "validar_coord_rec.py")
    raw = Path(manifiesto).read_bytes() if manifiesto else (LENF / "MANIFIESTO_ABL_ENF.json").read_bytes()
    man = json.loads(raw)
    co = man["ABL-ENF"]
    sint = str(man.get("kind", "")).endswith("-SINTETICO")
    D = Path(dir_t1)
    rb = (D / "resultado.json").read_bytes()
    fallos = []
    falla = fallos.append
    if H(rb) != pin_resultado:
        falla("RESULTADO_NO_AUTENTICO (sha256 distinto del fijado)")
    res = json.loads(rb)
    codigo = {n: H((LENF / n).read_bytes()) for n in VC.CODIGO_TRABAJADOR}
    for c, m in ((res.get("manifiesto_sha256") == H(raw), "RESULTADO_DE_OTRO_MANIFIESTO"), (res.get("codigo_sha256") == codigo, "RESULTADO_DE_OTRO_CODIGO"),
                 (res.get("tarea") == TAREA and TAREA in co["tareas"], "TAREA_DISTINTA_O_FUERA_DE_LA_PARTICION"),
                 (res.get("sintetico") is sint and res.get("modo") == ("sintetico" if sint else "produccion"), "COHERENCIA_SINTETICO_REAL"),
                 (res.get("alcance_sha256") == pin_alcance, "RESULTADO_DE_OTRO_ALCANCE")):
        if not c:
            falla(m)
    prods, lineas, shas = {}, {}, {}
    for p in res.get("productos") or []:
        f = D / "salida" / str(p.get("archivo", ""))
        b = f.read_bytes() if f.is_file() else None
        if b is None or H(b) != p.get("sha256") or len(_lineas(b)) != p.get("filas"):
            falla("PRODUCTO_NO_AUTENTICO:%s" % p.get("archivo"))
            continue
        lineas[p["archivo"]] = _lineas(b)
        prods[p["archivo"]] = [json.loads(x) for x in lineas[p["archivo"]]]
        shas[p["archivo"]] = H(b)
    if set(prods) != set(VC.PRODUCTOS) or len(res.get("productos") or []) != len(VC.PRODUCTOS):
        falla("PRODUCTOS_DISTINTOS_DE_LOS_ESPERADOS:%s" % sorted(prods))
    out = {"kind": "reutilizacion-granular-T1-rem128", "estado_documento": "CANDIDATO_NO_INCORPORADO", "tarea": TAREA, "fuente": str(D),
           "resultado_sha256": H(rb), "productos_sha256": shas, "manifiesto_sha256": H(raw), "alcance_sha256": res.get("alcance_sha256"),
           "codigo_sha256": res.get("codigo_sha256"), "validador_comun_sha256": H((LENF / "validar_coord_rec.py").read_bytes())}
    if fallos:
        return dict(out, aceptada=False, dictamen="rechazada", fallos=fallos), None
    techos, comp = prods[VC.PRODUCTOS[0]], prods[VC.PRODUCTOS[1]]
    for t in techos:
        if t.get("tarea") != TAREA or t.get("manifiesto_sha256") != H(raw) or t.get("alcance_sha256") != res.get("alcance_sha256") or t.get("sintetico") is not sint:
            falla("TECHO_NO_LIGADO_A_TAREA_MANIFIESTO_O_ALCANCE:%s" % t.get("clave_transformada_sha256"))
    for x in comp:
        if x.get("tarea") != TAREA or x.get("sintetico") is not sint:
            falla("COMPARACION_NO_LIGADA_A_SU_TAREA:%s" % x.get("cell_id"))
    claves_t1 = co["tareas"][TAREA]
    ks = [t.get("clave_transformada_sha256") for t in techos]
    if sorted(ks) != sorted(claves_t1) or len(ks) != len(set(ks)):
        falla("COBERTURA_DE_TECHOS_DE_T1 (faltan %s; ajenas %s; duplicadas %d)" % (sorted(set(claves_t1) - set(ks)), sorted(set(map(str, ks)) - set(claves_t1)),
                                                                              len(ks) - len(set(ks))))
    cerradas = sorted(k for k, t in zip(ks, techos) if t.get("estado") == "complete")
    abiertas = sorted(k for k, t in zip(ks, techos) if t.get("estado") != "complete")
    m = re.fullmatch(r"TECHOS_INCOMPLETOS: (\[.*\])", str(res.get("motivo")))
    declaradas = sorted(json.loads(m.group(1).replace("'", '"'))) if m else None
    if res.get("estado") != "incompleta" or declaradas != abiertas or not abiertas:
        falla("ESTADO_DEL_RESULTADO_INCOHERENTE_CON_SUS_TECHOS (estado %s; declaradas %s; abiertas %s)" % (res.get("estado"), declaradas, abiertas))
    if fallos:
        return dict(out, aceptada=False, dictamen="rechazada", fallos=fallos), None
    cel_de = {(c["unidad"], c["cell_id"]): c["clave_transformada_sha256"] for c in co["celdas_afectadas"]}
    sel = lambda claves: ([t for t in techos if t["clave_transformada_sha256"] in claves],  # noqa: E731
                          [x for x in comp if cel_de.get((x.get("unidad"), x.get("cell_id"))) in claves])
    tc, cc = sel(set(cerradas))
    v_c = VC.validar_techos(co, tc, cc, cerradas)
    ta, ca = sel(set(abiertas))
    v_a = VC.validar_techos(co, ta, ca, abiertas)
    if v_c["dictamen"] != "completa_validada":
        falla("CERRADOS_NO_VALIDADOS:%s" % v_c["fallos"][:4])
    if v_a["dictamen"] != "incompleta" or v_a["fallos"]:
        falla("ABIERTOS_CON_FALLOS:%s" % v_a["fallos"][:4])
    if len(cc) + len(ca) != len(comp):
        falla("COMPARACIONES_SIN_CLAVE_DE_T1")
    pend = {}
    cert_doc = json.loads(Path(certificado).read_bytes()) if certificado else None
    for t in ta:
        k = t["clave_transformada_sha256"]
        e = {"estado_persistido": t["estado"], "motivo": t["motivo"], "lower_R": t["lower_R"], "upper_R": t["upper_R"], "C_2": t["C_2"],
             "error_normalizado": t["error_normalizado"], "error_R": t["error_R"], "attained": t["attained"], "comparaciones": sum(1 for x in ca if cel_de[(x["unidad"], x["cell_id"])] == k),
             "estado_recuperacion": "no_decidido", "certificado": None}
        if cert_doc is not None and cert_doc.get("clave") == k:
            CS = cert_mod or _cargar("certificado_salto_recuperacion", AQUI.parent / "certificado_salto.py")
            cl = co["claves_recalculadas"][k]
            re_c = CS.certificar(cl["clave"], cl["diseno"], cl["j"], cl["tau"], (t["lower_R"], t["upper_R"]))
            fuente_ok = (cert_doc.get("fuente_techo") or {}).get("sha256") == shas[VC.PRODUCTOS[0]] and cert_doc.get("manifiesto_sha256") == H(raw)
            coincide = (re_c["estado"] == (cert_doc.get("certificado") or {}).get("estado")
                        and re_c.get("testigo_lateral") == (cert_doc.get("certificado") or {}).get("testigo_lateral"))
            e["certificado"] = {"sha256": H(Path(certificado).read_bytes()), "fuente_autentica": fuente_ok, "recalculado_coincide": coincide,
                                "estado_recalculado": re_c["estado"]}
            if fuente_ok and coincide and re_c["estado"] == "no_alcanzado_demostrado":
                e["estado_recuperacion"] = "no_alcanzado_demostrado"
                e["testigo_lateral"] = re_c.get("testigo_lateral")
        pend[k] = e
    if fallos:
        return dict(out, aceptada=False, dictamen="rechazada", fallos=fallos), None
    out.update(aceptada=True, dictamen="recuperacion_parcial_validada", fallos=[],
               reutilizables={"claves": cerradas, "techos": len(tc), "comparaciones": len(cc), "validacion_comun": v_c["dictamen"]},
               pendientes=pend, validacion_pendientes=v_a["dictamen"],
               composicion={"claves_T1": len(claves_t1), "regla": "el ensamblado integral exige que cada clave pendiente tenga una resolución "
                                                                 "aceptada por regla revisada; no_decidido la bloquea y nunca se convierte en complete"})
    sel_l = {"techos": [lineas[VC.PRODUCTOS[0]][i] for i, t in enumerate(techos) if t["clave_transformada_sha256"] in set(cerradas)],
             "abiertas": [lineas[VC.PRODUCTOS[0]][i] for i, t in enumerate(techos) if t["clave_transformada_sha256"] in set(abiertas)],
             "comparaciones": [lineas[VC.PRODUCTOS[1]][i] for i, x in enumerate(comp) if cel_de.get((x["unidad"], x["cell_id"])) in set(cerradas)]}
    return out, sel_l


def componer(co, reut: dict, techos_reutilizables: list, techos_nuevos: list, resoluciones: dict | None = None):
    """Une los techos reutilizables (validados por recuperar), los de tareas nuevas YA validadas (validar_tarea) y, por clave pendiente,
    su resolución. Devuelve (techos, informe). Sin duplicados ni faltantes frente a claves_recalculadas; una clave pendiente sin resolución
    aceptada queda como faltante declarada (bloquea el ensamblado integral)."""
    resoluciones = resoluciones or {}
    por, dup = {}, []
    for t in techos_reutilizables + techos_nuevos:
        k = t.get("clave_transformada_sha256")
        if k in por:
            dup.append(k)
        por[k] = t
    pend = sorted(reut.get("pendientes") or {})
    for k in pend:
        if k in por:
            dup.append(k)
        if k in resoluciones:
            por[k] = resoluciones[k]
    todas = set(co["claves_recalculadas"])
    falt = sorted(todas - set(por))
    ajenas = sorted(set(por) - todas)
    return list(por.values()), {"duplicadas": sorted(set(dup)), "faltantes": falt, "ajenas": ajenas, "pendientes_sin_resolucion": sorted(set(pend) - set(resoluciones)),
                                "completa": not dup and not falt and not ajenas}


def main(argv):
    pos = [x for i, x in enumerate(argv) if not x.startswith("--") and (i == 0 or not argv[i - 1].startswith("--"))]
    op = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--")}
    raiz, dir_t1, sal = pos[:3]
    out, sel = recuperar(raiz, dir_t1, op.get("--certificado"), op.get("--pin-resultado", PIN_RESULTADO), op.get("--pin-alcance", PIN_ALCANCE))
    S = Path(sal)
    S.mkdir()
    if sel is not None:
        for nombre, ls in (("techos_reutilizables.jsonl", sel["techos"]), ("comparaciones_reutilizables.jsonl", sel["comparaciones"])):
            with (S / nombre).open("xb") as f:
                f.write(b"".join(x + b"\n" for x in ls))
            out.setdefault("archivos", {})[nombre] = {"sha256": H((S / nombre).read_bytes()), "filas": len(ls)}
    with (S / "REUTILIZACION_T1.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: out.get(k) for k in ("dictamen", "fallos", "reutilizables", "archivos")}, ensure_ascii=False))
    print(json.dumps({k: {c: v[c] for c in ("estado_persistido", "motivo", "estado_recuperacion", "comparaciones")} for k, v in (out.get("pendientes") or {}).items()},
                     ensure_ascii=False))
    return 0 if out.get("aceptada") else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
