"""rem130 — corrección P4-ENF-T1-BYTES sobre la copia rem129: las filas de T1, incluida la abierta, salen de los MISMOS bytes autenticados y validados por recuperar(); no hay segunda lectura del producto.
rem129 — RUTA ÚNICA DE VALIDACIÓN DE LA INTEGRACIÓN ENF (paquete lote_integracion_enf; candidato no emitido). La comparten las dos entradas
finales (ensamblar_integracion.py y conciliar_integracion.py): ninguna acepta filas que no hayan pasado por validar_fuentes().
Piezas reutilizadas sin cambios, autenticadas antes de importarlas:
- validación común histórica de lote_enf (validar_coord_rec.py, índice PAQUETE_ABL_ENF.json fijado en el manifiesto de integración):
  validar_tarea para T2–T6 (código productor verificado contra SU paquete histórico), validar_techos dentro de la recuperación de T1 y
  validar_ensamblado para las comparaciones de todas las celdas del universo;
- recuperación granular de T1 (recuperar_t1.py, copia del adaptador aceptado en rem128; diferencial declarado) y certificador de alcance
  (certificado_salto.py, copia idéntica al aceptado: a9b4e6ad…).
Pasos de validar_fuentes (sobre los bytes que se leen aquí): (1) identidad de C0 y del paquete histórico; (2) manifiesto de techos fijado;
(3) T2–T6 con validar_tarea completa: aceptada, tarea, resultado, productos y alcance de ORIGEN iguales a los fijados; (4) T1 con recuperar():
fuente incompleta auténtica, 17 techos cerrados validados con validar_techos, claves abiertas separadas sin promoción; (5) cada clave abierta
SOLO se resuelve contra el certificado fijado en el manifiesto de integración: contexto completo (clave completa, parámetros, diseño, menú,
caja, fuente del techo y sus cotas, manifiesto, código de C0 y del certificador) y certificado RECALCULADO aquí, idéntico al fijado y en
estado no_alcanzado_demostrado; sin caché; en producción, solo la clave aceptada por el revisor; cualquier otra o no_decidido bloquea;
(6) cobertura exacta: cerradas + nuevas + resueltas = claves del manifiesto = universo, sin duplicadas, faltantes ni ajenas; (7) ensamblado
con validar_ensamblado histórico sobre las filas históricas SIN cambios (la clave resuelta conserva G = null en esas comparaciones) y,
aparte, la derivación de G de la clave resuelta (C2 persistido − K1 fijo) con su enlace a la resolución. componer() no se usa como
validación. Ninguna resolución entregada por el llamador cuenta como prueba."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
# Resolución aceptada por el revisor (rem129) para el caso exacto; en producción ninguna otra clave puede resolverse.
RESOLUCION_ACEPTADA = {"d59edf8a9d1461d1": "d59edf8a9d1461d135ecb84f7cf0fbf1a332ea182ad1acde96113702f4a8d40e"}
PIEZAS = ("validar_integracion.py", "recuperar_t1.py", "certificado_salto.py", "ensamblar_integracion.py", "conciliar_integracion.py",
          "emitir_alcance_integracion.py", "admision_integracion.py", "receta_integracion.sh")
TAREAS_INTEGRACION = ("ENF-ENSAMBLADO-INTEGRAL", "ENF-CONCILIACION-INTEGRAL")
OPERACION = "INTEGRACION_ENF"
LIMITES = {"procesos": 3, "tope_s": 2400.0, "suite_s": 3600.0, "union_s": 10800.0}


def _cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def autenticar_paquete():
    """Piezas del paquete frente a su índice (PAQUETE_INTEGRACION_ENF.json, junto a este archivo). Devuelve (sha256 del índice, fallos)."""
    p = AQUI / "PAQUETE_INTEGRACION_ENF.json"
    if not p.is_file():
        return None, ["INDICE_DEL_PAQUETE_AUSENTE"]
    idx = json.loads(p.read_bytes())
    mal = [n for n in PIEZAS if n not in idx.get("piezas", {}) or not (AQUI / n).is_file() or HF(AQUI / n) != idx["piezas"][n]["sha256"]]
    return HF(p), (["CODIGO_DEL_PAQUETE_NO_AUTENTICO:%s" % mal] if mal else [])


def cargar_mi(mi_path):
    raw = Path(mi_path).read_bytes()
    return raw, json.loads(raw)


def es_ensayo(mi):
    return str(mi.get("kind", "")).endswith("-ENSAYO")


def puerta(R, mi_raw, mi, modo, alcance, decision, tarea):
    """Puerta de cada entrada, ANTES de leer fuentes o escribir productos. produccion: manifiesto real + alcance v3 de integración verificado
    por C0 (verificar_documento) y ligado a ESTE manifiesto, índice, código e instalación + decisión humana nativa válida (decision_humana de
    C0, sin arnés). ensayo: solo manifiesto -ENSAYO y sin alcance. preflight: manifiesto real, sin alcance, sin productos integrales."""
    R = Path(R)
    C0 = R / mi["nucleo"]["ruta"]
    sys.path.insert(0, str(C0 / "herramientas/b"))
    import aprobacion_alcance as AA
    if AA.identidad_instalacion(C0) != NUCLEO_IDENTIDAD or mi["nucleo"]["identidad"] != NUCLEO_IDENTIDAD:
        return False, {"motivo": "NUCLEO_DE_OTRA_IDENTIDAD"}
    idx_sha, mal = autenticar_paquete()
    if mal:
        return False, {"motivo": mal[0]}
    if modo == "ensayo":
        if not es_ensayo(mi):
            return False, {"motivo": "ENSAYO_CON_MANIFIESTO_REAL"}
        if alcance or decision:
            return False, {"motivo": "ENSAYO_NO_ADMITE_ALCANCE"}
        return True, {"modo": modo, "indice_sha256": idx_sha}
    if es_ensayo(mi):
        return False, {"motivo": "MANIFIESTO_DE_ENSAYO_EN_%s" % modo.upper()}
    if modo == "preflight":
        if alcance or decision:
            return False, {"motivo": "PREFLIGHT_NO_ADMITE_ALCANCE"}
        return True, {"modo": modo, "indice_sha256": idx_sha}
    if modo != "produccion":
        return False, {"motivo": "MODO_NO_ADMITIDO"}
    if not alcance or not decision:
        return False, {"motivo": "PRODUCCION_SIN_ALCANCE_NI_DECISION"}
    ap = Path(alcance)
    if not ap.is_file():
        return False, {"motivo": "ALCANCE_NO_MATERIALIZADO"}
    ab = ap.read_bytes()
    al = json.loads(ab)
    try:
        AA.verificar_documento(al)
    except AA.Rechazo as ex:
        return False, {"motivo": "ALCANCE_NO_VERIFICABLE:%s" % ex.codigo}
    ent = al.get("entradas") or {}
    codigo = {n: HF(AQUI / n) for n in PIEZAS}
    for cond, causa in ((al.get("operaciones") == [OPERACION], "ALCANCE_DE_OTRA_OPERACION"),
                        (tarea in (al.get("tareas") or []), "TAREA_FUERA_DEL_ALCANCE"),
                        (al.get("lote_manifiesto_sha256") == ent.get("manifiesto_integracion") == H(mi_raw), "ALCANCE_DE_OTRO_MANIFIESTO"),
                        (ent.get("paquete_integracion") == idx_sha and ent.get("codigo_integracion") == codigo, "ALCANCE_DE_OTRO_CODIGO"),
                        (al.get("instalacion_identidad") == NUCLEO_IDENTIDAD, "ALCANCE_DE_OTRA_INSTALACION"),
                        (al.get("limites") == LIMITES, "ALCANCE_CON_OTROS_LIMITES")):
        if not cond:
            return False, {"motivo": causa}
    try:
        dec = AA.decision_humana(str(decision), H(ab), al["emitida_utc"])
    except AA.Rechazo as ex:
        return False, {"motivo": "DECISION_NO_VALIDA:%s" % ex.codigo}
    return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab), "decision": dec}


def validar_fuentes(R, mi_raw, mi, hasta="completo"):
    """Validación completa de todas las fuentes de la integración. hasta = 'seleccion' (preflight: sin ensamblado) o 'completo'."""
    R = Path(R)
    fallos = []
    falla = fallos.append
    out = {"manifiesto_integracion_sha256": H(mi_raw), "ensayo": es_ensayo(mi)}

    def fin():
        return dict(out, aceptada=not fallos, fallos=fallos,
                    dictamen="rechazada" if fallos else ("seleccion_validada" if hasta == "seleccion" else "completa_validada_con_resolucion"))
    # (1) paquete histórico de techos y su validación común (autenticados antes de importar)
    ph = mi["paquete_historico_techos"]
    ip = R / ph["indice"]["ruta"]
    if not ip.is_file() or HF(ip) != ph["indice"]["sha256"]:
        falla("INDICE_HISTORICO_NO_AUTENTICO")
        return fin()
    LENF = ip.parent
    idx = json.loads(ip.read_bytes())["piezas"]
    hist = ("validar_coord_rec.py", "tarea_lote.py", "conexion_coord_cert.py")
    if any(HF(LENF / n) != idx[n]["sha256"] for n in hist):
        falla("PAQUETE_HISTORICO_ALTERADO")
        return fin()
    VC = _cargar("validar_coord_rec_historico_integracion", LENF / "validar_coord_rec.py")
    RT = _cargar("recuperar_t1_integracion", AQUI / "recuperar_t1.py")
    CS = _cargar("certificado_salto_integracion", AQUI / "certificado_salto.py")
    # (2) manifiesto de techos fijado
    mp = R / ph["manifiesto"]["ruta"]
    raw_t = mp.read_bytes() if mp.is_file() else b""
    if H(raw_t) != ph["manifiesto"]["sha256"]:
        falla("MANIFIESTO_DE_TECHOS_NO_AUTENTICO")
        return fin()
    man_t = json.loads(raw_t)
    co = man_t["ABL-ENF"]
    if str(man_t.get("kind", "")).endswith("-SINTETICO") != es_ensayo(mi):
        falla("COHERENCIA_SINTETICO_REAL (manifiesto de techos frente al de integración)")
        return fin()
    out["manifiesto_techos_sha256"] = H(raw_t)
    # (3) tareas completas (T2–T6) con la validación completa aceptada
    filas, origen, vistas = [], {}, []
    for e in mi["tareas_completas"]:
        t = e["tarea"]
        if t in vistas:
            falla("TAREA_DUPLICADA_EN_EL_MANIFIESTO:%s" % t)
            continue
        vistas.append(t)
        d = R / e["directorio"]
        v = VC.validar_tarea(raw_t, d / "resultado.json", d / "salida")
        for cond, causa in ((v["aceptada"], "TAREA_NO_VALIDA:%s:%s" % (t, v["fallos"][:3] or v["incompletos"][:1])), (v["tarea"] == t, "RESULTADO_DE_OTRA_TAREA:%s" % t),
                            (v["resultado_sha256"] == e["resultado_sha256"], "RESULTADO_DISTINTO_DEL_FIJADO:%s" % t),
                            (v["productos_sha256"] == e["productos"], "PRODUCTOS_DISTINTOS_DE_LOS_FIJADOS:%s" % t),
                            (v["alcance_sha256"] == e["alcance_origen_sha256"], "ALCANCE_DE_ORIGEN_DISTINTO:%s" % t)):
            if not cond:
                falla(causa)
        for x in v["techos"]:
            filas.append({"clave": x["clave_transformada_sha256"], "origen": "tarea_completa", "tarea_origen": t, "fila": x})
        origen[t] = {"directorio": e["directorio"], "resultado_sha256": v["resultado_sha256"], "productos": v["productos_sha256"],
                     "alcance_origen_sha256": v["alcance_sha256"], "modo": v["modo"], "dictamen": v["dictamen"]}
    # (4) T1 por la recuperación revisada (fuente incompleta auténtica; sin resultado completo fabricado)
    t1 = mi["t1"]
    o, sel = RT.recuperar(R, R / t1["directorio"], None, pin_resultado=t1["resultado_sha256"], pin_alcance=t1["alcance_origen_sha256"], lenf=LENF, manifiesto=mp)
    if not o.get("aceptada"):
        falla("T1_NO_RECUPERABLE:%s" % o.get("fallos", [])[:3])
        return fin()
    if o["productos_sha256"] != t1["productos"]:
        falla("T1_PRODUCTOS_DISTINTOS_DE_LOS_FIJADOS")
    for x in sel["techos"]:
        r = json.loads(x)
        filas.append({"clave": r["clave_transformada_sha256"], "origen": "T1_recuperado", "tarea_origen": t1["tarea"], "fila": r})
    techos_t1 = [json.loads(x) for x in sel["abiertas"]]      # rem130 (P4-ENF-T1-BYTES): mismos bytes autenticados y validados por recuperar()
    if sorted(x["clave_transformada_sha256"] for x in techos_t1) != sorted(o["pendientes"]):
        falla("T1_FILAS_ABIERTAS_DISTINTAS_DE_LAS_PENDIENTES")
        return fin()
    origen[t1["tarea"]] = {"directorio": t1["directorio"], "resultado_sha256": o["resultado_sha256"], "productos": o["productos_sha256"],
                           "alcance_origen_sha256": o["alcance_sha256"], "estado_historico": "incompleta", "reutilizables": o["reutilizables"]}
    # (5) resolución de cada clave abierta contra el certificado fijado (contexto completo, recálculo, sin caché)
    resoluciones = {}
    rm = mi.get("resolucion") or {}
    for k, pinfo in o["pendientes"].items():
        fila_h = next(x for x in techos_t1 if x["clave_transformada_sha256"] == k)
        cl = co["claves_recalculadas"][k]
        if rm.get("clave") != k or not rm.get("certificado"):
            falla("CLAVE_NO_DECIDIDA:%s (sin resolución fijada)" % k)
            continue
        if not es_ensayo(mi) and RESOLUCION_ACEPTADA.get(k) != cl["clave_completa_sha256"]:
            falla("RESOLUCION_FUERA_DE_LA_ACEPTADA:%s" % k)
            continue
        cp = R / rm["certificado"]["ruta"]
        cb = cp.read_bytes() if cp.is_file() else b""
        if H(cb) != rm["certificado"]["sha256"]:
            falla("CERTIFICADO_AUSENTE_O_NO_AUTENTICO:%s" % k)
            continue
        cd = json.loads(cb)
        ft = cd.get("fuente_techo") or {}
        ctx = {"kind": cd.get("kind") == "certificado-alcance-supremo-salto-rem128", "clave": cd.get("clave") == k,
               "clave_completa": cd.get("clave_completa_sha256") == cl["clave_completa_sha256"] == rm.get("clave_completa_sha256"),
               "primitivas_diseno_menu_caja": (cd.get("primitivas"), cd.get("diseno"), cd.get("j"), cd.get("tau")) == (cl["clave"], cl["diseno"], cl["j"], cl["tau"]),
               "fuente_techo": ft.get("sha256") == o["productos_sha256"]["enf_techos.jsonl"] and ft.get("lower_R") == fila_h["lower_R"]
               and ft.get("upper_R") == fila_h["upper_R"] and ft.get("estado") == fila_h["estado"] == "incomplete",
               "manifiesto": cd.get("manifiesto_sha256") == H(raw_t),
               "codigo_c0": cd.get("codigo_c0_sha256") == {n: HF(CS.C0 / "src/paper2b" / n) for n in CS.CODIGO_C0},
               "certificador": cd.get("certificador_sha256") == HF(AQUI / "certificado_salto.py"),
               "motivo_historico": fila_h.get("motivo") == "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE" and fila_h.get("attained") is False}
        if not all(ctx.values()):
            falla("CERTIFICADO_DE_OTRO_CONTEXTO:%s:%s" % (k, sorted(c for c, v in ctx.items() if not v)))
            continue
        c = json.loads(json.dumps(CS.certificar(cl["clave"], cl["diseno"], cl["j"], cl["tau"], (fila_h["lower_R"], fila_h["upper_R"]))))
        if c.get("estado") != "no_alcanzado_demostrado" or c != cd.get("certificado"):
            falla("CERTIFICADO_NO_REPRODUCIDO_O_NO_DECIDIDO:%s (%s)" % (k, c.get("estado")))
            continue
        tl = c["testigo_lateral"]
        B = c["B_pot"]
        lim = tl["limite_R"]
        resoluciones[k] = {
            "clave": k, "clave_completa_sha256": cl["clave_completa_sha256"], "tarea_origen": t1["tarea"],
            "estado_historico": fila_h["estado"], "motivo_historico": fila_h["motivo"], "attained_historico": fila_h["attained"],
            "resolucion": "no_alcanzado_demostrado", "regla": "supremo no alcanzado demostrado (G, rho = 1, S13; caja cerrada del manifiesto); aceptada en rem129 para esta clave exacta",
            "certificado": {"ruta": rm["certificado"]["ruta"], "sha256": H(cb), "recalculado_identico": True},
            "cota_inferior_historica": {"lower_R": fila_h["lower_R"], "valor_R_factible": fila_h["valor_R"], "C_2_factible": fila_h["C_2"],
                                        "testigo_factible": fila_h["testigo"], "nota": "punto factible de la rama y cota; NO es un maximizador"},
            "cota_superior_historica_R": fila_h["upper_R"], "error_normalizado_historico": fila_h["error_normalizado"],
            "valor_limite_R": lim, "valor_limite_C2": [lim[0] / B[1], lim[1] / B[0]], "testigo_lateral": tl,
            "esquema_supremo_no_alcanzado": {"tau_d_at_sup": None, "tau_f_at_sup": None, "sup_not_attained": True,
                                             "sup_lateral_low": [lim[0] / B[1], lim[1] / B[0]], "sup_lateral_high": 0.0,
                                             "eje_lateral": "tau_d en tau_f = %s: low = desde tasas menores (c > 0, FF); high = desde tasas mayores (c < 0, NF)" % tl["tau_f"],
                                             "sup_witness": [{"side": "minus", "tau_d": tl["tau_d"], "tau_f": tl["tau_f"], "limit_value": [lim[0] / B[1], lim[1] / B[0]],
                                                              "branch_id": "FF"}]},
            "C2_para_brecha": fila_h["C_2"], "origen_C2_para_brecha": "C_2 persistido de T1 (valor factible certificado; |C_2 − sup/B_pot| <= error_normalizado)"}
        filas.append({"clave": k, "origen": "resolucion_no_alcanzado", "tarea_origen": t1["tarea"], "fila": fila_h, "resolucion": resoluciones[k]})
    out.update(origen=origen, resoluciones=resoluciones)
    # (6) cobertura exacta
    ks = [f["clave"] for f in filas]
    dup = sorted({k for k in ks if ks.count(k) > 1})
    todas, uni = set(co["claves_recalculadas"]), set(mi["universo"]["claves"])
    if dup:
        falla("CLAVES_DUPLICADAS:%s" % dup)
    if set(ks) != todas or todas != uni or len(uni) != len(mi["universo"]["claves"]):
        falla("COBERTURA_DE_CLAVES (faltan %s; ajenas %s; universo distinto %s)" % (sorted(todas - set(ks)), sorted(set(ks) - todas), sorted(todas ^ uni)))
    cuenta = {o_: sum(1 for f in filas if f["origen"] == o_) for o_ in ("T1_recuperado", "tarea_completa", "resolucion_no_alcanzado")}
    out["cobertura"] = {"claves": len(set(ks)), "por_origen": cuenta, "duplicadas": dup}
    out["filas_techo"] = filas
    if fallos or hasta == "seleccion":
        return fin()
    # (7) ensamblado histórico sin cambios + derivación separada de la clave resuelta
    ens, base = VC.validar_ensamblado(R, co, [f["fila"] for f in filas])
    fallos.extend(ens["fallos"])
    abiertas = {(x["unidad"], x["cell_id"]) for x in base if x["G_coord"] is None}
    de_resueltas = {(x["unidad"], x["cell_id"]) for x in base if x["clave_transformada_sha256"] in resoluciones}
    if abiertas != de_resueltas:
        falla("CELDAS_SIN_TECHO_FUERA_DE_LA_RESOLUCION (%d frente a %d)" % (len(abiertas), len(de_resueltas)))
    if ens.get("filas") != mi["universo"]["celdas_total"]:
        falla("CELDAS_DISTINTAS_DEL_UNIVERSO (%s de %s)" % (ens.get("filas"), mi["universo"]["celdas_total"]))
    if sorted((ens.get("fuera_del_lote") or {})) != sorted(mi["universo"]["fuera_del_nivel"]):
        falla("FUERA_DEL_NIVEL_DISTINTO")
    if fallos:
        out["ensamblado"] = {k: v for k, v in ens.items() if k != "fallos"}
        return fin()
    integ, resueltas = [], []
    for x in base:
        k = x["clave_transformada_sha256"]
        if k in resoluciones:
            g = resoluciones[k]["C2_para_brecha"] - x["K1_reutilizado"]
            d = {"unidad": x["unidad"], "cell_id": x["cell_id"], "clave_transformada_sha256": k, "K1_reutilizado": x["K1_reutilizado"], "G_padre": x["G_padre"],
                 "C2_enf": resoluciones[k]["C2_para_brecha"], "G_enf": g, "dG": g - x["G_padre"], "estado_techo_historico": x["estado_techo"],
                 "G_historico_persistido": x["G_coord"], "resolucion": "no_alcanzado_demostrado", "certificado_sha256": resoluciones[k]["certificado"]["sha256"]}
            resueltas.append(d)
            integ.append(dict(d, origen_G="resolucion_no_alcanzado_demostrado"))
        else:
            integ.append({"unidad": x["unidad"], "cell_id": x["cell_id"], "clave_transformada_sha256": k, "K1_reutilizado": x["K1_reutilizado"], "G_padre": x["G_padre"],
                          "C2_enf": x["C2_coord"], "G_enf": x["G_coord"], "dG": x["G_coord"] - x["G_padre"], "estado_techo_historico": x["estado_techo"],
                          "origen_G": "techo_cerrado"})
    out.update(ensamblado={k: v for k, v in ens.items() if k != "fallos"}, filas_base=base, filas_resueltas=resueltas, filas_integrales=integ,
               resumen={"celdas": len(integ), "celdas_resueltas": len(resueltas), "G_enf_negativo": sum(1 for x in integ if x["G_enf"] < 0),
                        "G_padre_negativo": sum(1 for x in integ if x["G_padre"] < 0),
                        "cambios_de_signo_G": sum(1 for x in integ if (x["G_enf"] < 0) != (x["G_padre"] < 0)),
                        "dG_min": min((x["dG"] for x in integ), default=None), "dG_max": max((x["dG"] for x in integ), default=None)})
    return fin()
