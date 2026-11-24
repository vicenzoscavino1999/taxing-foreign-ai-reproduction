"""rem125 — VALIDACIÓN COMÚN DEL CONTRASTE ABL-ENF (copia de validar_coord_rec.py rem123 cc83b778…: mismas comprobaciones de techo, garantía,
tarea y ensamblado; cambian la sección ABL-ENF, los productos enf_*, la fuente de celdas —el censo rem113 autenticado, familia ABL-ENF, con
las celdas afectadas del manifiesto obligadas a coincidir con ella— y el contraste con comparaciones previas, que solo se aplica si el
manifiesto declara esa fuente).
rem122 — VALIDACIÓN COORD DE RECUPERACIÓN (paquete operativo; derivado de correccion/validar_coord_rec.py, que corrige P4-COORD-COTA-VALOR
sobre la copia rem121 f06da81b…). Las comprobaciones por techo son las de la corrección; cambian el esquema (manifiestos de recuperación A/B,
sección L1-COORD-REC) y la entrada de las fuentes:
- toda fuente (manifiesto LOTE2, techos rem112/rem120, comparaciones rem120) se LEE AQUÍ desde su ruta del manifiesto, se autentica por el
  sha256 de sus BYTES antes de deserializarla y se usan esos mismos bytes; ningún diccionario de filas del llamante se acepta como fuente;
- techos recalculados (validar_techos): cobertura exacta de las claves pedidas, clave/parámetros/código/configuración del manifiesto, y un
  'complete' solo con la garantía efectiva del motor (lo_s/hi_s = cotas en R / intervalo de B_pot con redondeo hacia afuera; error normalizado
  que cubre las distancias de C_2 a ambos extremos; B_pot, C_2 y error_R en sus encierros; cierre normalizado <= 1e-7; testigo y detalle);
- reutilizados (reutilizados_autenticados): cada clave reutilizada sale de SU fuente autenticada con valor, estado, error y motivo iguales a
  los declarados y su garantía original (convergence_estimate), nunca promovida a certificado;
- ensamblado (validar_ensamblado): las comparaciones de TODAS las celdas del manifiesto LOTE2 autenticado (1.532), cada una con el techo de su
  propia clave (recalculado o reutilizado), K1 del manifiesto sin cambio y G = C2' − K1; unión exacta y disjunta de recalculadas y reutilizadas
  = las 26 claves; conjuntos fuera del lote (COL-2024p) sin filas; las filas de claves reutilizadas coinciden con las comparaciones rem120.
Un techo incompleto deja la tarea incompleta con sus cotas; una etiqueta certified_bound o un error 0 no acreditan por sí solos un certificado.
rem123 (P4-COORD-ENSAMBLADO-PROCEDENCIA): validar_tarea es la validación COMPLETA de una tarea, única y común al validador de tarea
(validar_lote.py) y al ensamblador (ensamblar_coord.py): lee una sola vez los BYTES del resultado y de cada producto, los autentica antes de
deserializarlos y aplica a ESOS bytes todos los controles (manifiesto, código, tarea de la partición, estado, coherencia sintético/real,
vínculo de cada fila con su tarea, manifiesto y alcance, y validar_techos); devuelve las filas validadas para que el ensamblado use las mismas."""
import hashlib
import json
import math
import sys
from pathlib import Path

NUCLEO = Path(__file__).resolve().parents[2] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"   # C0 en su ubicación sellada
if str(NUCLEO / "src") not in sys.path:
    sys.path.insert(0, str(NUCLEO / "src"))
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import model as M  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

TOL_CONVERGE = 1e-7
GARANTIA = "ieee754_binary64_rn"
SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")


def finito(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def leer_autenticado(R, ref):
    """Lee los BYTES de ref['ruta'] (relativa a la raíz), comprueba su sha256 con ref['sha256'] y SOLO entonces los deserializa."""
    p = Path(R) / ref["ruta"]
    if not p.is_file():
        return None, "FUENTE_AUSENTE:%s" % ref["ruta"]
    b = p.read_bytes()
    if hashlib.sha256(b).hexdigest() != ref["sha256"]:
        return None, "FUENTE_NO_AUTENTICA:%s" % ref["ruta"]
    t = b.decode("utf-8")
    return (json.loads(t) if ref["ruta"].endswith(".json") else [json.loads(x) for x in t.splitlines() if x.strip()]), None


def garantia(t, clave):
    """Garantía efectiva de modelos.ModeloTeorico.capture_ceiling (ver correccion/validar_coord_rec.py): devuelve (exigido, Bi)."""
    Bi = EM.IParams.from_state(M.state_from_primitives({p: float(x) for p, x in clave.items()})).B_pot
    lo_s, hi_s = (Iv.point(t["lower_R"]) / Bi).lo, (Iv.point(t["upper_R"]) / Bi).hi
    c2 = Iv.point(t["C_2"])
    return max(0.0, (Iv.point(hi_s) - c2).hi, (c2 - Iv.point(lo_s)).hi), Bi


def validar_techos(co, techos, comp, claves):
    """Techos recalculados de `claves` (las de una tarea o todas) y comparaciones de sus celdas afectadas."""
    fallos, incompletos = [], []
    falla = fallos.append
    rec = co["claves_recalculadas"]
    if not set(claves) <= set(rec):
        falla("CLAVES_PEDIDAS_FUERA_DE_LAS_RECALCULADAS")
    ks = [t.get("clave_transformada_sha256") for t in techos]
    if set(ks) != set(claves) or len(ks) != len(set(ks)):
        falla("COBERTURA_DE_TECHOS (faltan %s; ajenas %s; duplicadas %d)" % (sorted(set(claves) - set(ks)), sorted(set(map(str, ks)) - set(claves)), len(ks) - len(set(ks))))
    motor = co["motor"]
    por_clave = {}
    for t in techos:
        k = t.get("clave_transformada_sha256")
        if k not in claves or k not in rec:
            continue
        por_clave[k] = t
        cl = rec[k]
        if (t.get("parametros"), t.get("diseno"), t.get("j"), t.get("tau")) != (cl["clave"], cl["diseno"], cl["j"], cl["tau"]):
            falla("CLAVE_DISTINTA_DEL_MANIFIESTO:%s" % k)
        if t.get("codigo") != motor["codigo"]:
            falla("IDENTIDAD_DE_CODIGO_DISTINTA:%s" % k)
        if t.get("configuracion") != motor["configuracion"]:
            falla("CONFIGURACION_DISTINTA:%s" % k)
        if t.get("estado") != "complete":
            incompletos.append({"clave": k, "motivo": t.get("motivo"), "lower_R": t.get("lower_R"), "upper_R": t.get("upper_R"),
                                "error_normalizado": t.get("error_normalizado"), "error_R": t.get("error_R")})
            if not t.get("motivo"):
                falla("INCOMPLETO_SIN_MOTIVO:%s" % k)
            if t.get("error_kind") == "certified_bound" and not (finito(t.get("lower_R")) and finito(t.get("upper_R"))):
                falla("INCOMPLETO_SIN_COTAS:%s" % k)
            if t.get("motivo") in SIN_CALCULO and t.get("C_2") is not None:
                falla("INCOMPLETO_SIN_CALCULO_CON_VALOR:%s" % k)
            if t.get("error_kind") == "certified_bound" and all(finito(t.get(c)) for c in ("lower_R", "upper_R", "C_2", "error_normalizado")) \
                    and t["error_normalizado"] < garantia(t, cl["clave"])[0]:
                falla("COTA_NO_RESPALDA_EL_VALOR:%s" % k)
            continue
        if t.get("error_kind") != "certified_bound" or t.get("garantia") != GARANTIA:
            falla("COMPLETO_SIN_COTA_CERTIFICADA:%s" % k)
            continue
        campos = ("C_2", "B_pot", "valor_R", "error_normalizado", "error_R", "lower_R", "upper_R")
        if not all(finito(t.get(c)) for c in campos) or t["error_normalizado"] < 0 or t["error_R"] < 0:
            falla("COMPLETO_CON_VALORES_NO_FINITOS:%s" % k)
            continue
        exigido, Bi = garantia(t, cl["clave"])
        if not (Bi.lo <= t["B_pot"] <= Bi.hi):
            falla("B_POT_FUERA_DE_SU_ENCIERRO:%s" % k)
        q, e = Iv.point(t["valor_R"]) / Iv.point(t["B_pot"]), Iv.point(t["error_normalizado"]) * Iv.point(t["B_pot"])
        if not (q.lo <= t["C_2"] <= q.hi):
            falla("C2_DISTINTO_DE_VALOR_R_ENTRE_B_POT:%s" % k)
        if not (e.lo <= t["error_R"] <= e.hi):
            falla("ERROR_R_INCOHERENTE_CON_EL_NORMALIZADO:%s" % k)
        if t["error_normalizado"] > TOL_CONVERGE:
            falla("COMPLETO_FUERA_DE_TOLERANCIA_NORMALIZADA:%s" % k)
        if not (t["lower_R"] <= t["upper_R"]):
            falla("COTAS_INCOHERENTES:%s" % k)
        if t["error_normalizado"] < exigido:
            falla("COTA_NO_RESPALDA_EL_VALOR:%s" % k)
        w = t.get("testigo") or {}
        dom = cl["tau"]
        if not (finito(w.get("tau_d")) and finito(w.get("tau_f")) and float(dom["tau_d_lower"]) <= w["tau_d"] <= float(dom["tau_d_upper"])
                and float(dom["tau_f_lower"]) <= w["tau_f"] <= float(dom["tau_f_upper"])):
            falla("TESTIGO_AUSENTE_O_FUERA_DEL_DOMINIO:%s" % k)
        if t.get("attained") is not True or not isinstance(t.get("level_values"), list) or not t["level_values"] \
                or not isinstance(t.get("final_n"), int) or t["final_n"] < 0:
            falla("DETALLE_INCOMPLETO:%s" % k)
    cel = {(c["unidad"], c["cell_id"]): c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in claves}
    vistos = [(x.get("unidad"), x.get("cell_id")) for x in comp]
    if set(vistos) != set(cel) or len(vistos) != len(set(vistos)):
        falla("COMPARACIONES_NO_CORRESPONDEN (faltan %d; ajenas %d; duplicadas %d)" % (len(set(cel) - set(vistos)), len(set(vistos) - set(cel)), len(vistos) - len(set(vistos))))
    for x in comp:
        c = cel.get((x.get("unidad"), x.get("cell_id")))
        if c is None:
            continue
        if x.get("K1_reutilizado") != c["K1_reutilizado"]:
            falla("K1_CAMBIADO:%s" % c["cell_id"])
        t = por_clave.get(c["clave_transformada_sha256"]) or {}
        g = (t["C_2"] - c["K1_reutilizado"]) if t.get("estado") == "complete" and t.get("C_2") is not None else None
        if x.get("C2_coord") != t.get("C_2") or x.get("G_coord") != g or x.get("estado_techo") != t.get("estado"):
            falla("COMPARACION_DISTINTA_DE_SU_TECHO:%s" % c["cell_id"])
    dictamen = "rechazada" if fallos else ("incompleta" if incompletos else "completa_validada")
    return {"dictamen": dictamen, "fallos": fallos, "incompletos": incompletos}


CODIGO_TRABAJADOR = ("tarea_lote.py", "conexion_coord_cert.py")
PRODUCTOS = ("enf_techos.jsonl", "enf_comparacion.jsonl")


def validar_tarea(raw, resultado, salida):
    """Validación COMPLETA de una tarea sobre los bytes que se leen AQUÍ (raw: bytes del manifiesto; resultado: ruta de resultado.json;
    salida: directorio de sus productos). Controles: resultado del mismo manifiesto, del código del trabajador de ESTE paquete, de una tarea de
    la partición y completo; coherencia sintético/real (indicador sintetico y modo del resultado frente al kind del manifiesto; un resultado real
    lleva el sha256 de su alcance, como lo escribe el trabajador tras la puerta); cada producto autenticado por sus bytes antes de deserializarlo
    y conjunto exacto de productos; cada techo ligado a la tarea, el manifiesto y el alcance del resultado que lo contiene (y cada comparación a
    su tarea); validar_techos (conjunto exacto, garantía numérica, atribución por clave y comparaciones). Devuelve el dictamen, la procedencia
    (sha256 de los bytes leídos) y las filas validadas."""
    H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    man = json.loads(raw)
    co = man.get("ABL-ENF") or {}
    sint = str(man.get("kind", "")).endswith("-SINTETICO")
    rp = Path(resultado)
    rb = rp.read_bytes() if rp.is_file() else b"{}"
    res = json.loads(rb)
    tarea = res.get("tarea")
    codigo = {n: H((Path(__file__).resolve().parent / n).read_bytes()) for n in CODIGO_TRABAJADOR}
    al = res.get("alcance_sha256")
    fallos = [m for c, m in ((res.get("manifiesto_sha256") == H(raw), "RESULTADO_DE_OTRO_MANIFIESTO"), (res.get("codigo_sha256") == codigo, "RESULTADO_DE_OTRO_CODIGO"),
                             (tarea in (co.get("tareas") or {}), "TAREA_FUERA_DE_LA_PARTICION"), (res.get("estado") == "completa", "RESULTADO_NO_COMPLETO"),
                             (res.get("sintetico") is sint and res.get("modo") == ("sintetico" if sint else "produccion"), "COHERENCIA_SINTETICO_REAL"),
                             (sint or (isinstance(al, str) and len(al) == 64), "RESULTADO_REAL_SIN_ALCANCE")) if not c]
    prods, shas = {}, {}
    for p in res.get("productos") or []:
        f = Path(salida) / str(p.get("archivo", ""))
        b = f.read_bytes() if f.is_file() else None
        if b is None or H(b) != p.get("sha256"):
            fallos.append("PRODUCTO_NO_AUTENTICO:%s" % p.get("archivo"))
            continue
        prods[p["archivo"]] = [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]
        shas[p["archivo"]] = H(b)
    if set(prods) != set(PRODUCTOS) or len(res.get("productos") or []) != len(PRODUCTOS):
        fallos.append("PRODUCTOS_DISTINTOS_DE_LOS_ESPERADOS:%s" % sorted(prods))
    base = {"tarea": tarea, "resultado_sha256": H(rb), "productos_sha256": shas, "alcance_sha256": al, "modo": res.get("modo"),
            "techos": [], "comparaciones": [], "incompletos": []}
    if fallos:
        return dict(base, aceptada=False, dictamen="rechazada", fallos=fallos)
    techos, comp = prods[PRODUCTOS[0]], prods[PRODUCTOS[1]]
    for t in techos:
        if t.get("tarea") != tarea or t.get("manifiesto_sha256") != H(raw) or t.get("alcance_sha256") != al or t.get("sintetico") is not sint:
            fallos.append("TECHO_NO_LIGADO_A_TAREA_MANIFIESTO_O_ALCANCE:%s" % t.get("clave_transformada_sha256"))
    for x in comp:
        if x.get("tarea") != tarea or x.get("sintetico") is not sint:
            fallos.append("COMPARACION_NO_LIGADA_A_SU_TAREA:%s" % x.get("cell_id"))
    v = validar_techos(co, techos, comp, co["tareas"][tarea])
    fallos += v["fallos"]
    dictamen = "rechazada" if fallos else v["dictamen"]
    return dict(base, aceptada=dictamen == "completa_validada", dictamen=dictamen, fallos=fallos, incompletos=v["incompletos"], techos=techos, comparaciones=comp)


def reutilizados_autenticados(R, co):
    """Filas de los techos reutilizados construidas SOLO desde las fuentes autenticadas del manifiesto. Devuelve (filas, fallos)."""
    fallos, filas, cache = [], [], {}
    for k, e in sorted(co["claves_reutilizadas"].items()):
        ref = co["fuentes"].get(e.get("fuente"))
        if ref is None:
            fallos.append("REUTILIZADO_SIN_FUENTE_DECLARADA:%s" % k)
            continue
        if e["fuente"] not in cache:
            cache[e["fuente"]] = leer_autenticado(R, ref)
        datos, err = cache[e["fuente"]]
        if err:
            fallos.append("%s (reutilizado %s)" % (err, k))
            continue
        f = [x for x in datos if x.get("clave_transformada_sha256") == k]
        if len(f) != 1 or any(f[0].get(c) != e[c] for c in ("C_2", "estado", "error", "motivo")):
            fallos.append("REUTILIZADO_SIN_RESPALDO_EN_SU_FUENTE_SELLADA:%s" % k)
            continue
        if e.get("error_kind_original") != "convergence_estimate" or e.get("certificado") is True:
            fallos.append("REUTILIZADO_PROMOVIDO_O_SIN_GARANTIA_ORIGINAL:%s" % k)
        if f[0].get("estado") != "complete":
            fallos.append("REUTILIZADO_NO_COMPLETO:%s" % k)
        filas.append({"clave_transformada_sha256": k, "C_2": f[0]["C_2"], "estado": f[0]["estado"], "error": f[0]["error"], "motivo": f[0]["motivo"],
                      "reutilizado_de": ref["ruta"], "reutilizado_sha256": ref["sha256"], "error_kind_original": e["error_kind_original"]})
    return filas, fallos


def celdas_del_lote(R, co):
    """Celdas (1.532) y conjuntos fuera del lote desde el manifiesto LOTE2 AUTENTICADO; en un manifiesto sintético, las celdas de las claves
    renombradas pasan a sus claves SINT- (y unidad SINT-), declaradas en co['sintetico']['renombre']."""
    fuente = co["fuente_celdas"]                          # rem125: censo rem113 autenticado, familia declarada (ABL-ENF)
    censo, err = leer_autenticado(R, fuente)
    if err:
        return None, None, err
    ren = {v: k for k, v in ((co.get("sintetico") or {}).get("renombre") or {}).items()}
    celdas, fuera = [], {}
    for s_f, v in sorted(censo[fuente["familia"]].items()):
        if not v["celdas"]:
            fuera[s_f] = v.get("causa_sin_celdas") or "SIN_CELDAS_PADRE_TESTIGO"
        for c in v["celdas"]:
            c = dict(c, conjunto_coord=s_f)
            if c["clave_transformada_sha256"] in ren:
                c["clave_transformada_sha256"], c["unidad"] = ren[c["clave_transformada_sha256"]], "SINT-" + c["unidad"]
            celdas.append(c)
    return celdas, fuera, None


def validar_ensamblado(R, co, techos):
    """Ensamblado de la tarea COORD completa con los productos AUTENTICADOS: devuelve (resultado, filas_ensambladas)."""
    fallos = []
    falla = fallos.append
    rec, reu_decl = set(co["claves_recalculadas"]), set(co["claves_reutilizadas"])
    if rec & reu_decl:
        falla("CLAVES_RECALCULADAS_Y_REUTILIZADAS_SOLAPADAS:%s" % sorted(rec & reu_decl))
    if rec | reu_decl != set(co["claves_coord_total"]) or len(co["claves_coord_total"]) != len(set(co["claves_coord_total"])):
        falla("UNION_DISTINTA_DE_LAS_CLAVES_COORD")
    reus, f = reutilizados_autenticados(R, co)
    fallos += f
    celdas, fuera, err = celdas_del_lote(R, co)
    if err:
        return {"dictamen": "rechazada", "fallos": fallos + [err], "filas": 0}, []
    por_clave = {r["clave_transformada_sha256"]: r for r in reus}
    for t in techos:
        if t.get("clave_transformada_sha256") in por_clave:
            falla("TECHO_DUPLICADO_ENTRE_FUENTES:%s" % t.get("clave_transformada_sha256"))
        por_clave[t.get("clave_transformada_sha256")] = t
    filas, incompletas, vistos = [], 0, set()
    for c in celdas:
        u = (c["unidad"], c["cell_id"])
        if u in vistos:
            falla("CELDA_DUPLICADA_EN_EL_MANIFIESTO:%s" % c["cell_id"])
        vistos.add(u)
        if c.get("conjunto_coord") in fuera:
            falla("CELDA_DE_CONJUNTO_FUERA_DEL_LOTE:%s" % c["cell_id"])
        t = por_clave.get(c["clave_transformada_sha256"])
        if t is None:
            falla("CELDA_SIN_TECHO_DE_SU_CLAVE:%s" % c["cell_id"])
            continue
        completo = t.get("estado") == "complete" and t.get("C_2") is not None
        incompletas += not completo
        filas.append({"unidad": c["unidad"], "cell_id": c["cell_id"], "clave_transformada_sha256": c["clave_transformada_sha256"], "K1_reutilizado": c["K1_reutilizado"],
                      "G_padre": c["G_padre"], "C2_coord": t.get("C_2"), "G_coord": (t["C_2"] - c["K1_reutilizado"]) if completo else None,
                      "estado_techo": t.get("estado"), "origen_techo": "recalculado" if c["clave_transformada_sha256"] in rec else "reutilizado"})
    if len(filas) != co["celdas_total"]:
        falla("ENSAMBLADO_NO_CUBRE_LAS_CELDAS (%d de %d)" % (len(filas), co["celdas_total"]))
    previa = {(c["unidad"], c["cell_id"], c["clave_transformada_sha256"], c["K1_reutilizado"]) for c in celdas if c["clave_transformada_sha256"] in rec}
    if previa != {(c["unidad"], c["cell_id"], c["clave_transformada_sha256"], c["K1_reutilizado"]) for c in co["celdas_afectadas"]}:
        falla("CELDAS_AFECTADAS_DISTINTAS_DE_LA_FUENTE")    # rem125: el manifiesto no puede declarar otras celdas que las de su fuente
    ref_prev = co["fuentes"].get("comparaciones_previas")
    comp120, err = (leer_autenticado(R, ref_prev) if ref_prev else (None, None))
    if err:
        falla(err)
    elif comp120 is not None:
        previas = {(x["unidad"], x["cell_id"]): x for x in comp120}
        for x in filas:
            if x["origen_techo"] != "reutilizado":
                continue
            p = previas.get((x["unidad"], x["cell_id"]))
            if p is None or p.get("K1_reutilizado") != x["K1_reutilizado"] or p.get("C2_coord") != x["C2_coord"] or p.get("G_coord") != x["G_coord"]:
                falla("REUTILIZADA_DISTINTA_DE_LA_COMPARACION_REM120:%s" % x["cell_id"])
    dictamen = "rechazada" if fallos else ("incompleta" if incompletas else "completa_validada")
    return {"dictamen": dictamen, "fallos": fallos, "filas": len(filas), "con_techo_incompleto": incompletas,
            "por_origen": {o: sum(1 for x in filas if x["origen_techo"] == o) for o in ("recalculado", "reutilizado")},
            "fuera_del_lote": {k: "pendiente (sin testigos), no NA" for k in fuera}}, filas
