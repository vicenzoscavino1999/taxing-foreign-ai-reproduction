"""rem140 — LECTOR CANDIDATO de la FUENTE NUEVA del techo alto (enmienda v2; pieza separada, no aceptada). Solo lee y escribe evidencia
candidata en <salida_dir> (nuevo y fuera de las ubicaciones aceptadas); nunca toca FUENTES_CAPTURA, PRUEBAS_FILA_v3, productos aceptados,
ledgers ni la entrega leída.
Cadena de autoridad (cada eslabón sobre los MISMOS bytes, leídos una vez):
  1. documento de INCORPORACIÓN (esquema incorporacion-fuente-testigo-alto-v1) con su sha256 fijado en el comando; en produccion cita además
     el dictamen del revisor por ruta y huella, y ese dictamen debe nombrar literalmente el inventario sellado y el RESULTADO incorporados;
  2. cada archivo (alcance, decisión, INICIO, RESULTADO, sello, VALIDACION, estado de la receta y las cinco piezas productoras) contra el
     inventario de SU entrega (huella del inventario fijada en la incorporación) y sus bytes; el manifiesto v2 contra el inventario sellado
     de rem139; el código productor debe ser byte a byte el de este paquete;
  3. la puerta común (testigo_comun.puerta) sobre el alcance de origen: en produccion relee la decisión nativa con el lector C0 sin cambios;
  4. la validación común CORREGIDA (testigo_comun.validar_bytes) sobre los bytes del RESULTADO; la VALIDACION entregada debe coincidir con
     la recalculada (no basta por sí sola);
  5. vínculo con la clave e8b1f7fd… y con EQ-TECHO-T8-1: clave del manifiesto, del RESULTADO y de la incorporación; equivalencia efectiva del
     techo (fuente del manifiesto) con huella única por archivo igual a los módulos REALES de la ejecución nueva; grupo de la plantilla en el
     Contexto aceptado de captura;
  6. testigo inferior aceptado CEI:dc4e1ba9… de la prueba aceptada de la fila 9638 (PRUEBAS_FILA_v3 690dfef9…), revalidado con
     certificacion_fila.validar sin cambios y cotejado con la vista aceptada 66891b45….
La ejecución nueva conserva su identidad real (área, inventario, alcance, decisión, fechas, módulos y plataforma) y un run_origen propio
TRUN-…; la plantilla BRUN-cb33e6b2… es solo la referencia de equivalencia; la identidad técnica histórica declarada va aparte.
Modos: produccion (fuente productiva, decisión y dictamen obligatorios) | sintetico (fuente SINTETICA explícita, sin decisión ni dictamen;
su evidencia nunca habilita la vía productiva). Una mezcla se rechaza.
Retornos: 0 evidencia escrita (con las filas que cubre); 3 rechazo (nada escrito). Uso: python -B -I -X utf8 lector_fuente_testigo.py <raiz>
<incorporacion.json> <incorporacion_sha256> <salida_dir> --modo produccion|sintetico"""
import datetime as dt
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

MI_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adaptador_fila_testigo as AD  # noqa: E402
import testigo_comun as TC  # noqa: E402

AQUI = Path(__file__).resolve().parent
KIND_INC = "incorporacion-fuente-testigo-alto-v1"
CAMPOS_INC = frozenset(("kind", "modo", "etiqueta", "clave", "grupo", "plantilla_equivalencia", "manifiesto", "fuente", "codigo_productor",
                        "ejecucion_declarada", "dictamen", "inferior"))
ARCHIVOS = ("alcance", "decision_ref", "inicio", "resultado", "resultado_sello", "validacion", "estado_receta")
DECLARADOS = ("base", "alcance_sha256", "decision_uuid", "inicio_utc", "fin_utc")
CLAVE = "e8b1f7fdb9c7017605e0a4162fc6688e7b6ed01d2308ff72106ed6cf6834a97b"
FILA_INF = 9638
MANIFIESTO = {"base": "tmp/paso4_emision_captura_correcciones_testigo_desde_rem139",
              "inventario_sha256": "794841511784da49ab9d357db7de4bdbf4ff967ab02570c475d0d182af2ce5fd",
              "rel": "testigo_alto_corregido/MANIFIESTO_TESTIGO_v2.json",
              "sha256": "3ed91d323c7f0f0e56eb31b01b41ef864c68bea029936afd4d090f36c9939ad4"}
VISTA = {"base": "tmp/paso4_emision_captura_correcciones_testigo_desde_rem139",
         "inventario_sha256": "794841511784da49ab9d357db7de4bdbf4ff967ab02570c475d0d182af2ce5fd",
         "rel": "captura_vista_CAPTURA_T8/VISTA_T8_CAPTURA.jsonl",
         "sha256": "66891b45282cae1c08c0a86131d194631e1d9a39351e26cfc137255e6b489992"}
PRUEBAS_FILA = {"base": "tmp/paso4_emision_lambda_conexion_captura_desde_rem137",
                "inventario_sha256": "59188e65c2d8dd665679f3b47780e2859633505b260127cc435c772431bf92b2",
                "rel": "c2_conexion/candidato_v3/PRUEBAS_FILA_v3.json",
                "sha256": "690dfef933447410fd9653201ec92631cb7af52a6364db4b70606833e8be5efa"}
SINTETICO = "SINTETICO — fuente de prueba, NO productiva: "
PROHIBIDAS = (AD.CAPTURA, MANIFIESTO["base"], PRUEBAS_FILA["base"], "paso4/instalacion", "fase2_datos")
W = Path(r"@@W_BS1@@")


class Lector:
    def __init__(self, raiz):
        self.R, self.inv = Path(raiz), {}

    def inventario(self, base, sha_fijado):
        if (base, sha_fijado) not in self.inv:
            b = (self.R / base / "audit/entrega.json").read_bytes()
            TC.need(TC.sha(b) == sha_fijado, "INVENTARIO_NO_AUTENTICO", base)
            self.inv[(base, sha_fijado)] = json.loads(b)["files"]
        return self.inv[(base, sha_fijado)]

    def archivo(self, nombre, e):
        """Bytes de un archivo de una entrega: listado en su inventario fijado, con la misma huella que declara la entrada y que sus bytes."""
        TC.need(isinstance(e, dict) and set(e) == {"base", "inventario_sha256", "rel", "sha256"}, "ENTRADA_FUERA_DE_ESQUEMA", nombre)
        TC.need(isinstance(e["base"], str) and e["base"].startswith("tmp/") and ".." not in Path(e["base"]).parts
                and ".." not in Path(e["rel"]).parts, "ENTRADA_FUERA_DE_ESQUEMA", nombre)
        f = self.inventario(e["base"], e["inventario_sha256"])
        b = (self.R / e["base"] / e["rel"]).read_bytes()
        TC.need(f.get(e["rel"], {}).get("sha256") == e["sha256"] == TC.sha(b), "ARCHIVO_NO_AUTENTICO", nombre)
        return b


def leer(raiz, inc_path, inc_sha, modo):
    """Autentica y valida la fuente; devuelve (lectura, filas). Lanza TC.Rechazo ante cualquier eslabón roto."""
    raiz = Path(raiz)
    TC.need(modo in ("produccion", "sintetico"), "MODO_INVALIDO", str(modo))
    raw = Path(inc_path).read_bytes()
    TC.need(TC.sha(raw) == inc_sha, "INCORPORACION_NO_AUTENTICA")
    inc = json.loads(raw)
    TC.need(isinstance(inc, dict) and inc.get("kind") == KIND_INC and set(inc) == CAMPOS_INC, "INCORPORACION_FUERA_DE_ESQUEMA")
    sint = inc["modo"] == "SINTETICO"
    TC.need(inc["modo"] in ("produccion", "SINTETICO") and (modo == "sintetico") == sint, "MEZCLA_SINTETICA_PRODUCTIVA", str(inc["modo"]))
    et = str(inc["etiqueta"])
    if sint:
        TC.need(et.startswith(SINTETICO) and inc["dictamen"] is None and inc["fuente"].get("decision_ref") is None,
                "MEZCLA_SINTETICA_PRODUCTIVA", "una fuente sintética no lleva decisión ni dictamen")
    else:
        TC.need(not et.startswith(("SINTETICO", "FIXTURE")), "MEZCLA_SINTETICA_PRODUCTIVA", "etiqueta de prueba en produccion")
        TC.need(inc["fuente"].get("decision_ref") is not None, "DECISION_REFERENCIA_AUSENTE")
        TC.need(isinstance(inc["dictamen"], dict) and set(inc["dictamen"]) == {"ruta", "sha256"}, "DICTAMEN_AUSENTE")
    TC.need(inc["clave"] == CLAVE, "CLAVE_AJENA")
    TC.need(inc["grupo"] == AD.GRUPO, "GRUPO_AJENO")
    TC.need(inc["plantilla_equivalencia"] == AD.PLANTILLA, "PLANTILLA_AJENA")
    TC.need(inc["manifiesto"] == MANIFIESTO, "MANIFIESTO_AJENO")
    TC.need(inc["inferior"] == {"ceiling_id": AD.CEI_INF, "prueba_aceptada_fila": FILA_INF}, "TESTIGO_INFERIOR_AJENO")
    TC.need(isinstance(inc["fuente"], dict) and set(inc["fuente"]) == set(ARCHIVOS), "INCORPORACION_FUERA_DE_ESQUEMA", "fuente")
    TC.need(isinstance(inc["codigo_productor"], dict) and set(inc["codigo_productor"]) == set(TC.PIEZAS), "CODIGO_PRODUCTOR_INCOMPLETO")
    L = Lector(raiz)
    B = {n: L.archivo(n, e) for n, e in inc["fuente"].items() if e is not None}
    # manifiesto v2 sellado (inventario rem139) y sus fijaciones
    bm = L.archivo("manifiesto", MANIFIESTO)
    m, msha = TC.cargar_manifiesto(raiz, raiz / MANIFIESTO["base"] / MANIFIESTO["rel"])
    TC.need(msha == TC.sha(bm) == MANIFIESTO["sha256"] and m["clave"] == CLAVE and m["grupo"] == AD.GRUPO and m["corrida_plantilla"] == AD.PLANTILLA,
            "MANIFIESTO_AJENO")
    # código productor: listado en su entrega y byte a byte el de este paquete (el mismo que fija el alcance)
    prod = {}
    for n, e in inc["codigo_productor"].items():
        prod[n] = TC.sha(L.archivo("codigo:" + n, e))
        TC.need(prod[n] == TC.HF(AQUI / n), "CODIGO_PRODUCTOR_DISTINTO", n)
    # alcance de origen: la puerta común (relee la decisión nativa en produccion) sobre los MISMOS bytes autenticados
    ent = inc["fuente"]
    pal = raiz / ent["alcance"]["base"] / ent["alcance"]["rel"]
    pdec = raiz / ent["decision_ref"]["base"] / ent["decision_ref"]["rel"] if ent["decision_ref"] else None
    ev = TC.puerta(raiz, "produccion" if not sint else "fixture", str(pal), str(pdec) if pdec else None, m, msha, "validador",
                   AQUI / "validar_testigo.py", TC.HF(AQUI / "validar_testigo.py"))
    TC.need(ev["alcance_sha256"] == TC.sha(B["alcance"]) and TC.HF(pal) == TC.sha(B["alcance"]), "ALCANCE_AJENO")
    TC.need(ev["piezas_alcance"] == prod, "CODIGO_PRODUCTOR_DISTINTO", "piezas del alcance")
    if not sint:
        TC.need(ev.get("decision_ref_sha256") == TC.sha(B["decision_ref"]) and TC.HF(pdec) == TC.sha(B["decision_ref"]), "DECISION_AJENA")
    al = json.loads(B["alcance"])
    # RESULTADO: validación común corregida sobre sus bytes; la VALIDACION entregada debe coincidir con la recalculada
    rrel = ent["resultado"]["rel"]
    TC.need(ent["resultado_sello"]["rel"] == rrel + ".sha256" and ent["validacion"]["rel"] == str(Path(rrel).parent.as_posix()) + "/VALIDACION.json"
            and ent["inicio"]["rel"] == str(Path(rrel).parent.as_posix()) + "/INICIO.json"
            and all(ent[k]["base"] == ent["resultado"]["base"] for k in ("resultado_sello", "validacion", "inicio")), "FUENTE_FUERA_DE_ESQUEMA")
    inv = L.inventario(ent["resultado"]["base"], ent["resultado"]["inventario_sha256"])
    dsal = Path(rrel).parent.as_posix()
    n_res = sum(1 for k in inv if k.startswith(dsal + "/RESULTADO") and k.endswith(".json") and "/" not in k[len(dsal) + 1:])
    TC.need(not any(k.startswith(dsal + "/FALLO") for k in inv), "FUENTE_CON_FALLO")
    sello_txt = B["resultado_sello"].decode("utf-8").split()
    doc, fallos = TC.validar_bytes(raiz, m, msha, B["resultado"], sello_txt[0] if sello_txt else None, n_res,
                                   "produccion" if not sint else "fixture", ev)
    TC.need(doc["clase"] == "complete" and doc["cumple_garantia"] is True and not fallos, "TECHO_NO_VALIDO",
            "%s %s" % (doc["clase"], ",".join(fallos)))
    vd = json.loads(B["validacion"])
    TC.need(isinstance(vd, dict) and all(vd.get(k) == doc[k] for k in ("kind", "modo", "clave", "manifiesto_sha256", "clase", "cumple_garantia",
                                                                      "fallos", "promueve", "resultado_sha256", "filas_cuya_mitad_superior_cubriria")),
            "VALIDACION_ENTREGADA_DISTINTA")
    r = json.loads(B["resultado"])
    TC.need(r["clave"] == CLAVE and r["manifiesto_sha256"] == msha, "CLAVE_AJENA")
    TC.need((r["modo"] == "fixture" and r["sintetico"] is True) if sint else (r["modo"] == "produccion" and r["sintetico"] is False),
            "MEZCLA_SINTETICA_PRODUCTIVA", "resultado")
    ini = json.loads(B["inicio"])
    TC.need(ini.get("kind") == "inicio-testigo-alto-c3-v2" and ini.get("clave") == CLAVE and ini.get("manifiesto_sha256") == msha
            and (ini.get("puerta") or {}).get("alcance_sha256") == ev["alcance_sha256"] and ini.get("inicio_utc") == r["inicio_utc"]
            and (ini.get("puerta") or {}).get("ejecutado") == r["puerta"]["ejecutado"], "INICIO_INCOHERENTE")
    est = json.loads(B["estado_receta"])
    TC.need(est.get("estado_final") == "completo" and est.get("rc_final_esperado") == 0 and est.get("cierre_conforme") is True, "RECETA_NO_COMPLETA")
    # ejecución nueva: identidad real derivada de los bytes; lo declarado solo se coteja
    base_f = ent["resultado"]["base"]
    dec = ev.get("decision") if not sint else None
    ts = [al["emitida_utc"]] + ([dec["timestamp"]] if dec else []) + [r["inicio_utc"], r["fin_utc"]]
    TC.need(all(isinstance(t, str) for t in ts) and [dt.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in ts]
            == sorted(dt.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in ts), "FECHAS_INCOHERENTES", " <= ".join(ts))
    er = r["evidencia_real"]
    run_nuevo = "TRUN-" + TC.H({"base": base_f, "alcance_sha256": ev["alcance_sha256"], "resultado_sha256": doc["resultado_sha256"]})[:24]
    ejec = {"run_origen": run_nuevo, "base": base_f, "inventario_sha256": ent["resultado"]["inventario_sha256"], "alcance_sha256": ev["alcance_sha256"],
            "alcance_emitida_utc": al["emitida_utc"], "decision": dec, "decision_ref_sha256": ev.get("decision_ref_sha256"),
            "decision_uuid": (dec or {}).get("uuid"), "inicio_utc": r["inicio_utc"], "fin_utc": r["fin_utc"],
            "modulos": {"n": len(er["modulos"]), "sha256": TC.H(er["modulos"]), "origen": er["origen_modulos"]},
            "plataforma": er.get("plataforma"), "python": er.get("python"), "ejecutable": er.get("ejecutable"),
            "garantia_plataforma": er.get("garantia_plataforma"), "sintetico": sint}
    decl = inc["ejecucion_declarada"]
    TC.need(isinstance(decl, dict) and set(decl) == set(DECLARADOS), "EJECUCION_DECLARADA_FUERA_DE_ESQUEMA")
    TC.need(AD.PLANTILLA not in json.dumps(decl), "PROCEDENCIA_DE_LA_PLANTILLA", "la ejecución declarada cita la plantilla")
    TC.need(all(decl[k] == ejec[k] for k in DECLARADOS), "EJECUCION_DECLARADA_DISTINTA",
            ",".join(k for k in DECLARADOS if decl[k] != ejec[k]))
    if not sint:
        dp = Path(inc["dictamen"]["ruta"])
        db = dp.read_bytes()
        TC.need(TC.sha(db) == inc["dictamen"]["sha256"], "DICTAMEN_NO_AUTENTICO")
        txt = db.decode("utf-8", errors="replace")
        TC.need(ent["resultado"]["inventario_sha256"] in txt and doc["resultado_sha256"] in txt, "DICTAMEN_NO_CITA_LA_FUENTE")
    # vínculo con EQ-TECHO-T8-1 y la clave: equivalencia efectiva del techo = huella única por archivo = módulos reales de la ejecución nueva
    eq = json.loads((raiz / m["fuentes"]["equivalencia_techo"]["ruta"]).read_bytes())
    TC.need(TC.HF(raiz / m["fuentes"]["equivalencia_techo"]["ruta"]) == m["fuentes"]["equivalencia_techo"]["sha256"], "EQUIVALENCIA_AJENA")
    # (corrección tras REM140-L1: d7view.py y raices.py son archivos clave del techo pero no módulos requeridos de la ruta real; su vínculo
    # pasa por el árbol fijado del núcleo —archivos_fijados_sha256 de la ejecución, ya validado— y, si la ejecución los cargó, por su huella)
    vinc, req = {}, m["modulos_ruta_real"]["archivos"]
    for f, hs in eq["archivos_clave_del_techo"].items():
        rel = "paper2b/" + f
        h = hs[0] if isinstance(hs, list) and len(hs) == 1 else None
        cargado = er["modulos"].get(rel)
        fijada = h is not None and h == m["nucleo"]["archivos"].get(rel)
        vinc[f] = {"huella_unica": h, "fijada_en_el_nucleo": fijada, "requerido_ruta_real": rel in req, "cargado": cargado is not None,
                   "ok": fijada and (cargado == h if rel in req else cargado in (None, h))}
    TC.need(vinc and all(v["ok"] for v in vinc.values()) and er.get("archivos_fijados_sha256") == TC.H(m["nucleo"]["archivos"])
            and Fraction(str(eq["banda_tol_converge"])) == Fraction(str(m["config"]["sup"]["tol_converge"])),
            "VINCULO_EQUIVALENCIA_ROTO", ",".join(k for k, v in vinc.items() if not v["ok"]))
    CF = AD.cargar_cf(raiz)
    ctx = CF.Contexto(raiz)
    TC.need(ctx.grupo.get(AD.PLANTILLA) == AD.GRUPO and ctx.eq_sha, "VINCULO_EQUIVALENCIA_ROTO", "grupo de la plantilla")
    # testigo inferior aceptado: prueba aceptada de la fila 9638, revalidada con el validador aceptado y cotejada con la vista aceptada
    pruebas = json.loads(L.archivo("pruebas_fila_v3", PRUEBAS_FILA))
    p9638 = [p for p in pruebas if p.get("fila") == FILA_INF]
    TC.need(len(p9638) == 1 and CF.validar(ctx, p9638[0]) == (True, "computed"), "TESTIGO_INFERIOR_NO_ACEPTADO")
    wi = p9638[0]["testigo_inferior"]
    TC.need(wi["ceiling_id"] == AD.CEI_INF and CF._testigo(ctx, wi) is None and wi["run_origen"] == AD.PLANTILLA, "TESTIGO_INFERIOR_AJENO")
    vista = {}
    for ln in L.archivo("vista", VISTA).splitlines():
        if ln.strip():
            x = json.loads(ln)
            vista[x["fila_anexo"]] = x
    TC.need(vista[FILA_INF]["captura_c2"]["estado_candidato"] == "computed"
            and vista[FILA_INF]["captura_c2"]["prueba_sha256"] == CF.H(CF.canon(p9638[0])), "TESTIGO_INFERIOR_NO_ACEPTADO", "vista")
    # (corrección tras REM140-L2: solo las 2.111 filas de captura llevan captura_c2; el resto de la vista no es de captura)
    cap = {i: x["captura_c2"] for i, x in vista.items() if isinstance(x.get("captura_c2"), dict)}
    pend = sorted(i for i, x in cap.items() if x.get("estado_candidato") == "pendiente")
    TC.need(pend == sorted(f["fila"] for f in m["cobertura_prevista"]["filas"]) and len(pend) == 40
            and all(cap[i].get("causa_pendiente") == "SIN_PRUEBA_POR_FILA" and cap[i].get("prueba_sha256") is None for i in pend),
            "FILAS_PENDIENTES_DISTINTAS")
    techo = {"incorporacion_sha256": inc_sha, "fuente_inventario_sha256": ent["resultado"]["inventario_sha256"], "fuente_base": base_f,
             "resultado_sha256": doc["resultado_sha256"], "validacion_recalculada_sha256": TC.H({k: v for k, v in doc.items() if k != "validada_utc"}),
             "run_origen": run_nuevo, "clave": CLAVE, "grupo": AD.GRUPO, "plantilla_equivalencia": AD.PLANTILLA, "C_2": r["C2"],
             "numerical_error": r["numerical_error_share"], "escala": "C_2_share", "computation_status": r["computation_status"],
             "sup_not_attained": r["sup_not_attained"], "garantia": "certified_bound validado (testigo_comun v3)", "sintetico": sint}
    filas = []
    for i in pend:
        TC.need(vista[i]["run_id"] == ctx.run_de.get(ctx.captura[i]["ref"].split("/", 1)[0]), "FILA_NO_COINCIDE", str(i))
        p = AD.prueba_candidata(CF, ctx, i, wi, techo)
        ok, mot = AD.validar_candidata(CF, ctx, p, techo)
        filas.append({"fila": i, "clave_fila": CF.clave(ctx.captura[i]), "run_destino": p["run_destino"], "valor_requerido": p["valor_requerido"],
                      "estado_candidato": mot if ok else "pendiente", "causa_pendiente": None if ok else mot,
                      "no_es_exclusion": True, "prueba_candidata": p, "prueba_sha256": CF.H(CF.canon(p)), "candidata": True,
                      "promueve": False, "sintetico": sint})
    lect = {"kind": "lectura-fuente-testigo-alto-v1", "modo": modo, "sintetico": sint, "incorporacion_sha256": inc_sha, "lector_sha256": MI_SHA,
            "adaptador_sha256": TC.HF(AQUI / "adaptador_fila_testigo.py"), "testigo_comun_sha256": TC.PROPIO,
            "certificacion_fila_sha256": AD.CF_SHA256, "manifiesto_sha256": msha, "clave": CLAVE, "grupo": AD.GRUPO,
            "ejecucion_nueva": ejec,
            "plantilla": {"run": AD.PLANTILLA, "rol": "referencia de equivalencia y del dominio de destino; NO es la corrida que calculó este techo"},
            "identidad_tecnica_historica_declarada": m["payload"]["technical"], "vinculo_equivalencia": vinc,
            "validacion_recalculada": {k: doc[k] for k in ("kind", "clase", "cumple_garantia", "fallos", "resultado_sha256", "estado_motor")},
            "techo": techo, "testigo_inferior": {"ceiling_id": wi["ceiling_id"], "prueba_aceptada_fila": FILA_INF,
                                                  "prueba_sha256": CF.H(CF.canon(p9638[0])), "extremo_superior": str(Fraction(wi["C_2"]) + Fraction(wi["numerical_error"]))},
            "filas": len(filas), "por_estado": {e: sum(1 for x in filas if x["estado_candidato"] == e) for e in sorted({x["estado_candidato"] for x in filas})},
            "cubiertas": [x["fila"] for x in filas if x["estado_candidato"] == "computed_candidato"],
            "no_cubiertas": {x["fila"]: x["causa_pendiente"] for x in filas if x["estado_candidato"] != "computed_candidato"},
            "promueve": False,
            "nota": "evidencia CANDIDATA separada por fila; no modifica FUENTES_CAPTURA, PRUEBAS_FILA_v3, productos aceptados ni ledgers; una fila "
                    "no cubierta queda pendiente (no es exclusión ni imposibilidad); sintetico=true nunca habilita la vía productiva"}
    return lect, filas


def salida_permitida(raiz, salida, fuente_base):
    s = Path(salida).resolve()
    extra = (fuente_base,) if isinstance(fuente_base, str) and fuente_base.startswith("tmp/") and len(Path(fuente_base).parts) > 1 else ()
    prohib = [(Path(raiz) / p).resolve() for p in PROHIBIDAS + extra] + [W.resolve()]
    TC.need(not s.exists() and s.parent.is_dir() and not any(s == q or q in s.parents for q in prohib), "SALIDA_PROHIBIDA", str(s))
    return s


def main(argv):
    if len(argv) < 6 or "--modo" not in argv:
        print(__doc__.splitlines()[-1], file=sys.stderr)
        return 2
    raiz, inc, inc_sha, salida, modo = Path(argv[0]), Path(argv[1]), argv[2], Path(argv[3]), argv[argv.index("--modo") + 1]
    try:
        try:
            fb = json.loads(inc.read_bytes())["fuente"]["resultado"]["base"]
        except (OSError, ValueError, KeyError, TypeError):
            fb = None
        s = salida_permitida(raiz, salida, fb)
        lect, filas = leer(raiz, inc, inc_sha, modo)
    except TC.Rechazo as e:
        print(json.dumps({"rechazo": e.codigo, "detalle": e.detalle}, ensure_ascii=False))
        return 3
    except (KeyError, TypeError, ValueError, AttributeError, OSError, AD.Rechazo) as e:
        print(json.dumps({"rechazo": "FUENTE_ILEGIBLE", "detalle": "%s: %s" % (type(e).__name__, str(e)[:300])}, ensure_ascii=False))
        return 3
    s.mkdir()
    with (s / "EVIDENCIA_CANDIDATA_FILAS.jsonl").open("x", encoding="utf-8", newline="\n") as fh:
        for x in filas:
            fh.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
    lect["evidencia_filas_sha256"] = TC.HF(s / "EVIDENCIA_CANDIDATA_FILAS.jsonl")
    lect["leida_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    TC.escribir_x(s / "LECTURA_FUENTE_TESTIGO.json", lect)
    print(json.dumps({k: lect[k] for k in ("modo", "sintetico", "filas", "por_estado")} | {"run_origen": lect["ejecucion_nueva"]["run_origen"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
