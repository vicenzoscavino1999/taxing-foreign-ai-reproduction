"""CONTRATO DE RESULTADOS del paquete por selección del paso 4 (CANDIDATO 3.7, NO OFICIAL; núcleo candidato aislado).

Fuente ÚNICA de las reglas de CONTENIDO por celda. La usan la ruta común de verificación
(herramientas/s3/validadores/paquete_seleccion.py: validación, reanudación y adaptadores) y el productor, que construye
con ella su resumen canónico antes de escribirlo. Dependencias explícitas: solo paper2b (inversion, convergencia,
supremum, tables, model) y los objetos que se le pasan: el Contracts de la autoridad y el Run del núcleo de la celda
DERIVADA (selección + autoridad), nunca la salida que se verifica salvo las filas que se contrastan.

Clases de fuente de cada campo (MATRIZ):
  A  autoridad / configuración / selección: se DERIVA y se compara exactamente;
  R  recálculo barato desde entradas autenticadas y filas ya verificadas (fórmulas cerradas con las funciones del
     propio núcleo, evaluación puntual del modelo, filas de convergencia recalculadas);
  E  evidencia numérica del productor (búsquedas costosas): no se recalcula; se exige coherencia con el contrato del
     núcleo, con sus tablas hijas y con su fila de convergencia recalculada desde esas hijas;
  P  provisional: depende del soporte GLOBAL de la corrida y se cierra al ensamblar (herramientas/b/unidades._finalize);
     en el paquete se exige valor y `_fin` exactos y bandera coherente; NO es consumible como resultado;
  D  diagnóstico: tipo comprobado, excluido del consumo científico (consumir_celda).
Ninguna regla pendiente se vuelve opcional: lo que no puede comprobarse con lo exportado deja la celda INCOMPLETA o
INVÁLIDA, nunca «completa».
"""
from __future__ import annotations

import json
import math

from . import convergencia as CV
from . import inversion as INV
from . import tables as T
from .supremum import axes as sup_axes

TABLAS_V2 = ("cell_context", "confrontation_result", "inversion_result", "r1_summary", "r1_components", "r1_vertices", "r1_edges",
             "r1_rejected_crossings", "r2_sections", "r2_roots", "frontier_context", "capture_ceiling_result", "lambda_pi_envelope",
             "convergence_result")
HIJAS = ("sup_witness", "scalar_inversion_roots", "scalar_inversion_intervals", "inversion_targets", "numerical_evidence")
TABLAS = {"v2": TABLAS_V2, "v3": TABLAS_V2 + HIJAS}
ALGEBRAICAS = ("capture_required", "gain_required", "lambda_required", "phi_partial")
ENDOGENAS = ("external_factor", "phi_total")
PROVISIONALES = ("capture_required", "lambda_required")
DOMINIO_ENDOGENO = {"phi_total": (0.0, 1.0), "external_factor": (1e-6, 1.0)}
DEF_FISCAL = "C2(phi) = K1 en [0, 1]: C2 > K1 certificado en todo [0, 1] por cota inferior con puntos fiscales"
RAZONES_SIN_SOLUCION = {"phi_total": ("NO_ROOT_CERTIFIED_COVERAGE", "NO_ROOT_CERTIFIED_FISCAL_LOWER_BOUND"),
                        "external_factor": ("NO_ROOT_CERTIFIED_COVERAGE",)}
DIAGNOSTICO = ("tiempos_s", "celda_reutilizada", "frontera_reutilizada", "macro_reutilizado", "techo_reutilizado_entre_conjuntos")
RESUMEN = {  # campo de resultados.json -> (fuente, regla)
    "clave_celda": ("A", "clave de la fila de la selección sellada (orden del plan)"),
    "etiqueta": ("A", "'<lote>:<diseño>-<menú>-<país>' desde el plan y la selección"),
    "extreme_id": ("A", "testigo de la selección"), "claim_id_hoja": ("A", "testigo de la selección"),
    "indice_contexto": ("A", "testigo de la selección"),
    "precomprobaciones": ("R", "Generador.previas sobre el testigo (recalculadas)"),
    "set_id": ("A", "conjunto localizado por la referencia"), "omega_id": ("A", "ω por valores del testigo"),
    "pais": ("A", "país de la celda localizada"), "diseno": ("A", "afirmación hoja"), "instrumento": ("A", "afirmación hoja"),
    "caso": ("A", "caso D4 de la afirmación hoja"), "estado_nacional": ("A", "contexto localizado"), "macro": ("A", "contexto localizado"),
    "celda_externa": ("A", "contexto localizado"), "clave_estructural": ("R", "Run.structural(ω, diseño, menú)"),
    "frontier_id": ("A", "derivado (run_id del productor)"), "cell_id": ("R", "recalculado desde el contexto"),
    "techo": ("R", "copia exacta de 5 campos de la fila capture_ceiling_result validada"),
    "confrontacion": ("R", "copia exacta de 5 campos de la fila confrontation_result validada (K1, G y veredicto recalculados)"),
    "completitud": ("R", "rules.e12_verificar_celda sobre las filas exportadas"),
    "poscomprobaciones": ("R", "K1 y C2 frente al testigo, recalculadas"),
    "estado": ("R", "estado recalculado por la ruta común"), "motivos": ("R", "motivos de E12 + poscomprobaciones, recalculados"),
    "clave_E12": ("A", "derivada; cell_id recalculado"),
    "tiempos_s": ("D", "segundos por fase (no consumible)"), "celda_reutilizada": ("D", "caché del proceso"),
    "frontera_reutilizada": ("D", "caché del proceso"), "macro_reutilizado": ("D", "caché del proceso"),
    "techo_reutilizado_entre_conjuntos": ("D", "caché del proceso")}

# Matriz de contrato por tabla exportada: columnas, tipos y nulabilidad = las del CONTRATO DE LA AUTORIDAD (Contracts.table,
# reutilizado); aquí, la fuente y la regla de contenido de cada campo y la cardinalidad/relación de la tabla.
_A, _R, _E, _P, _D = "A", "R", "E", "P", "D"
MATRIZ = {
    "cell_context": {"cardinalidad": "1 por celda", "relacion": "cell_id = CEL:H(contexto)[:44]; macro y frontera cruzados",
                     "campos": {"*": (_A, "contexto derivado de la selección, la grilla, D4 y la fila λ_π validada"),
                                "cell_id": (_R, "recalculado desde los 16 campos de la clave")}},
    "frontier_context": {"cardinalidad": "1 por celda (frontier_id derivado)", "relacion": "frontier_id = FRN:H(run_id, diseño, país, menú, caso, ω, TAU)",
                         "campos": {"*": (_A, "presencia y clave por E12; contenido estructural del productor")}},
    "capture_ceiling_result": {"cardinalidad": "1 por frontier_id", "relacion": "ceiling_id = CEI:+frontier_id[4:]",
                               "campos": {"C_2": (_E, "rama y cota certificada; = valor del modelo en el punto (R)"),
                                          "numerical_error": (_E, "cota certificada <= tol_converge si complete; = change_bound de la fila C2 (v3)"),
                                          "tau_d_at_sup": (_R, "en el dominio del menú (supremum.axes) y valor del modelo = C_2; nulo si no alcanzado"),
                                          "tau_f_at_sup": (_R, "ídem"),
                                          "sup_not_attained": (_E, "alcance demostrado por el proveedor certificado (sin cajas vivas en curvas de salto)"),
                                          "sup_lateral_low": (_R, "no alcanzado: límite lateral; C_2 = máx(laterales); nulo si alcanzado"),
                                          "sup_lateral_high": (_R, "ídem"),
                                          "computation_status": (_E, "complete <=> cota cerrada <= tol_converge"),
                                          "ceiling_id": (_A, "derivado"), "frontier_id": (_A, "derivado"),
                                          "instrument_available": (_A, "D4: disponible"), "*": (_A, "D4/D7")}},
    "sup_witness": {"cardinalidad": "0 si alcanzado; >= 1 por lado si no alcanzado (v3)", "relacion": "ceiling_id -> capture_ceiling_result",
                    "campos": {"*": (_R, "índices 0..n-1 por lado; distancias >= 0 estrictamente decrecientes; punto en el dominio; limit_value = C_2; residual >= 0")}},
    "lambda_pi_envelope": {"cardinalidad": "1 por celda (macro_id de la confrontación)", "relacion": "macro_id = MAC:H(run_id, país, ω, bloque, clave); clave = H(payload)",
                           "campos": {"lambda_pi": (_R, "MC.bridge con el estado nacional y ω derivados (barato, exacto)"),
                                      "macro_key_payload": (_A, "desde las tablas del bundle autenticado con la técnica del productor (validate_key: E)"),
                                      "*": (_R, "fila completa = Run.macro_row con entradas derivadas (macro_esperada)")}},
    "confrontation_result": {"cardinalidad": "1 por celda", "relacion": "cell_id, ceiling_id, macro_id",
                             "campos": {"K_comp_1": (_R, "X.K1(Q, DME_gAI, λ_π, y)"), "C_2": (_R, "= C_2 del techo"), "G": (_R, "C_2 - K1"),
                                        "verdict": (_R, "±EPS_ECON con el error certificado"), "computation_status": (_R, "derivado de disponibilidad, admisibilidad y techo"),
                                        "*": (_A, "referencias derivadas")}},
    "inversion_result": {"cardinalidad": "6 por celda (INV.INVERSIONS)", "relacion": "(cell_id, inversion_id); hijas por conteo",
                         "campos": {"lambda_pi_required": (_R, "N/(C2·y) (EQ29)"), "delta_y_required": (_R, "N/(C2·λ) (EQ30); estado por el soporte gain_share de D7"),
                                    "C_2_required": (_R, "K1 (EQ7_9_3)"), "phi_critical_partial": (_R, "EQ28 con objetivos predeclarados"),
                                    "phi_critical_total": (_E, "raíz única aislada (búsqueda certificada); menú d: prueba de invariancia (R)"),
                                    "external_factor_required": (_E, "mapeo externo identificado; si no, not_identified (A)"),
                                    "result_status": (_R, "computed/outside_support PROVISIONAL (P) en lambda_required y capture_required"),
                                    "outside_support": (_R, "= (estado outside_support)"), "_fin": (_R, "exacto; cierre global al ensamblar"),
                                    "n_scalar_solutions": (_E, "= filas de scalar_inversion_roots"), "n_scalar_intervals": (_E, "= filas de scalar_inversion_intervals"),
                                    "*": (_R, "fila producida por Run.inversion_rows del núcleo con las entradas derivadas")}},
    "scalar_inversion_roots": {"cardinalidad": "n_scalar_solutions por inversión endógena completa", "relacion": "(cell_id, inversion_id, root_index)",
                               "campos": {"*": (_E, "converged; residual <= T_root_residual; bracket_low <= value <= bracket_high; dentro del dominio")}},
    "scalar_inversion_intervals": {"cardinalidad": "n_scalar_intervals por inversión endógena completa", "relacion": "(cell_id, inversion_id, interval_index)",
                                   "campos": {"*": (_E, "lower < upper; disjuntos y ordenados; menú d: [0, 1] por invariancia (R)")}},
    "inversion_targets": {"cardinalidad": "1 por inversión (v3)", "relacion": "(cell_id, inversion_id)",
                          "campos": {"*": (_A, "objetivos predeclarados, definición del núcleo y grilla de la autoridad")}},
    "numerical_evidence": {"cardinalidad": "las de la celda (record_pk de sus filas o de su techo) (v3)", "relacion": "evidence_ref <- convergence_result.evidence_ref; (result_table, record_pk) -> fila B",
                           "campos": {"*": (_E, "evidencia del productor; Checker.audit (record_pk resuelve), Checker.inversions (cobertura certificada) y referencias de convergencia resueltas")}},
    "convergence_result": {"cardinalidad": "G:1, INV: 1 por endógena con búsqueda, R1:1 con geometría, C2:1 por techo certificado (v3)",
                           "relacion": "quantity_id -> fila de resultado (result_ref)",
                           "campos": {"*": (_R, "G: convergencia.fila_G; INV: convergencia.fila_raices desde las hijas; R1: contrato certified_contour; C2: contrato certified_branch_and_bound"),
                                      "evidence_ref": (_E, "v2: referencia a numerical_evidence no exportada; v3: debe resolver en la numerical_evidence exportada")}},
    "r1_summary": {"cardinalidad": "1 por celda con geometría", "relacion": "cell_id",
                   "campos": {"*": (_E, "cotas <= r1_geometry_tol / T_root_residual; topología estable")}},
    "r1_components": {"cardinalidad": "n_components", "relacion": "(cell_id, component_id)", "campos": {"*": (_E, "presencia por E12")}},
    "r1_vertices": {"cardinalidad": ">= 1 por componente", "relacion": "(cell_id, vertex_id)", "campos": {"residual": (_E, "|residual| <= T_root_residual"), "*": (_E, "presencia por E12")}},
    "r1_edges": {"cardinalidad": "componentes con >= 2 vértices", "relacion": "(cell_id, edge_id)", "campos": {"*": (_E, "presencia por E12")}},
    "r1_rejected_crossings": {"cardinalidad": "n_rejected_crossings", "relacion": "cell_id", "campos": {"*": (_E, "presencia por E12")}},
    "r2_sections": {"cardinalidad": "4 secciones (R2.SECTIONS)", "relacion": "(cell_id, section_id)", "campos": {"*": (_E, "presencia por E12")}},
    "r2_roots": {"cardinalidad": "n_roots_by_section", "relacion": "(cell_id, section_id, root_index)", "campos": {"residual": (_E, "|residual| <= T_root_residual"), "*": (_E, "presencia por E12")}},
}

# Enlace EJECUTABLE de cada tabla con las funciones que la comprueban y la familia de pruebas que lo demuestra
# (codigo/probar_contrato.py); las ramas v2 sin evidencia exportada lo declaran.
REGLAS_TABLA = {
    "cell_context": [("contexto y cell_id derivados", "paquete_seleccion.verificar_celda (uk, cell_id)", "contexto, revisor")],
    "frontier_context": [("contexto y clave estructural con la técnica del productor", "paquete_seleccion.verificar_celda (der['frontera'])", "contexto")],
    "capture_ceiling_result": [("dominio, valor en el punto, laterales/testigos", "verificar_techo", "techo, techo_sintetico"),
                               ("estados y monotonicidad del núcleo", "checker_nucleo -> Checker.ceilings (v3)", "techo")],
    "sup_witness": [("testigos laterales", "verificar_techo", "techo_sintetico, hijas (v3)")],
    "lambda_pi_envelope": [("fila completa = la del núcleo para (ω, país, estado nacional) con run_id y técnica del productor", "macro_esperada + verificar_macro", "macro"),
                           ("clave macro, payload/hash, estado nacional, país/escenario, técnica, protocolo, η frente a ω auténtico",
                            "verificar_macro -> Checker.omega + Checker.macro (contexto auténtico)", "macro")],
    "confrontation_result": [("K1, C2, G, veredicto y estado recalculados", "paquete_seleccion.verificar_celda", "resumen, techo, revisor")],
    "inversion_result": [("filas del núcleo / coherencia de endógenas", "inversiones_nucleo + verificar_inversiones", "inversiones, provisionales, inversiones_sinteticas"),
                         ("estados, conteos y evidencia certificada", "checker_nucleo -> Checker.inversions (v3)", "inversiones")],
    "scalar_inversion_roots": [("hijas por conteo y contenido", "verificar_inversiones; Checker.inversions (v3)", "hijas, inversiones_sinteticas")],
    "scalar_inversion_intervals": [("hijas por conteo y contenido", "verificar_inversiones; Checker.inversions (v3)", "hijas, inversiones_sinteticas")],
    "inversion_targets": [("objetivos derivados", "verificar_inversiones", "hijas")],
    "r1_summary": [("conteos, residuos, cota y vacío demostrado", "verificar_geometria; Checker.geometry (v3)", "geometria")],
    "r1_components": [("extremos, bordes y topología desde sus vértices", "verificar_geometria; Checker.geometry (v3)", "geometria")],
    "r1_vertices": [("dominio del menú, etiqueta de borde = posición, residuo = |f(vértice)|", "verificar_geometria", "geometria (revisor)")],
    "r1_edges": [("vértices de su componente y cota geométrica <= r1_geometry_tol (el residuo de la CUERDA es diagnóstico)", "verificar_geometria; Checker.geometry (v3)", "geometria")],
    "r1_rejected_crossings": [("cajas dentro del dominio", "verificar_geometria", "—")],
    "r2_sections": [("conteos/índices/tangencias y vacío demostrado", "verificar_geometria; Checker.geometry (v3)", "geometria"),
                    ("una evidencia certificada por sección completa, método según el vacío demostrado", "verificar_evidencia (v3)", "evidencia")],
    "r2_roots": [("punto sobre la trayectoria de su sección dentro de su intervalo; |f(raíz)| <= residuo <= T_root", "verificar_geometria", "geometria")],
    "convergence_result": [("G (fila_G), INV (fila_raices desde hijas), R1 (certified_contour), C2 (certified_branch_and_bound) recalculadas",
                            "verificar_celda / verificar_inversiones / verificar_techo", "revisor, inversiones, techo, hijas"),
                           ("cada fila ligada a SU evidencia: tabla/PK, método, unidad, cota = change_bound, estado (G y C2 con sus cotas propias)",
                            "verificar_evidencia (v3)", "evidencia")],
    "numerical_evidence": [("referencia = hash de su contenido; record_pk resuelve; explicada por una regla del núcleo; ninguna huérfana",
                            "verificar_evidencia + Checker.audit (v3)", "evidencia")],
}


def _fin(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _c(x):
    return json.loads(json.dumps(x, sort_keys=True, default=str))


# ================================================================================================ esquema y filas
def esquema(C, tabla, filas):
    """Esquema del CONTRATO DE LA AUTORIDAD (columnas exactas, tipos, nulabilidad, PK/UK) sobre las filas exportadas;
    `_fin` (solo inversion_result) se comprueba aparte. Devuelve None o el motivo."""
    try:
        norm = [T.normalize_row(C, tabla, {k: v for k, v in r.items() if not (tabla == "inversion_result" and k == "_fin")}) for r in filas]
        C.table(tabla, T.sort_rows(C, tabla, norm))
    except Exception as e:  # noqa: BLE001  (rechazo con motivo; nunca una excepción hacia fuera)
        return "%s: %s" % (type(e).__name__, str(e)[:200])
    return None


def filas_de_celda(rows, cid, fid, contrato):
    """Filas de la celda que exige el contrato `contrato` (v2: tablas E12; v3: además las hijas y la fila C2)."""
    from . import rules as RULES
    out = RULES.e12_filas_de_celda(rows, cid, fid)
    if contrato == "v3":
        ceid = "CEI:" + fid[4:]
        out["sup_witness"] = [x for x in rows.get("sup_witness", []) if x.get("ceiling_id") == ceid]
        for t in ("scalar_inversion_roots", "scalar_inversion_intervals", "inversion_targets"):
            out[t] = [x for x in rows.get(t, []) if x.get("cell_id") == cid]
        out["convergence_result"] = out["convergence_result"] + [x for x in rows.get("convergence_result", []) if x.get("quantity_id") == "C2:" + ceid]
        out["numerical_evidence"] = [x for x in rows.get("numerical_evidence", []) if isinstance(x.get("record_pk"), dict)
                                     and (x["record_pk"].get("cell_id") == cid or x["record_pk"].get("ceiling_id") == ceid)]
    return out


def checker_nucleo(C, d7, filas, tolerances):
    """Errores del CHECKER DEL NÚCLEO (rules.Checker: ceilings, inversions, geometry y audit) sobre las filas v3 de UNA celda,
    normalizadas como en el ensamblaje. Las tablas que estos pasos leen y la celda no produce van vacías."""
    from . import rules as RULES
    tablas = {}
    for t in TABLAS["v3"] + ("computation_coverage", "witness_sets"):   # cell_context incluido: Checker.geometry lee el país
        tablas[t] = [T.normalize_row(C, t, {k: v for k, v in r.items() if k != "_fin"}) for r in filas.get(t, [])]
    ch = RULES.Checker(tablas, C, d7, tolerances=tolerances)
    for paso in (ch.ceilings, ch.inversions, ch.geometry, ch.audit):
        paso()
    refs = {e["evidence_ref"] for e in tablas["numerical_evidence"]}
    for r in tablas["convergence_result"]:
        if r.get("evidence_ref") not in refs:
            ch.errors.append("convergence_result %s: evidence_ref %r sin numerical_evidence exportada" % (r.get("quantity_id"), r.get("evidence_ref")))
    return ch.errors


# ================================================================================================ inversiones
def _scratch(run, fn):
    """Filas que produce el NÚCLEO (Run.inversion_rows) para un Inversion, sin dejar rastro en el Run."""
    lens = {t: len(v) for t, v in run.rows.items()}
    fn()
    nuevas = {t: [dict(x) for x in run.rows[t][lens[t]:]] for t in run.rows if len(run.rows[t]) > lens[t]}
    for t in nuevas:
        del run.rows[t][lens[t]:]
    return nuevas


def inversiones_nucleo(run, cid, e, declarado):
    """{inversion_id: filas del núcleo} para las inversiones RECALCULABLES con las entradas derivadas `e`, más el
    conjunto de las que dependen de evidencia costosa del productor. Réplica exacta de Run.inversions salvo las búsquedas
    endógenas costosas (phi_total f/df, external_factor con mapeo identificado), que no se recalculan."""
    ok = e["status"] == "complete"
    C2, lam, y, K1 = (e["C2"], e["lam"], e["y"], e["K1"]) if ok else (None, None, None, None)
    N = e["N"]

    def soporte(iid, v):   # P: lambda/C2 globales; se reproduce el estado provisional DECLARADO solo si el valor es exacto
        st = (declarado.get(iid) or {}).get("result_status")
        return (v, v) if st == "computed" else (math.inf, -math.inf)
    lam_req = N / (C2 * y) if (C2 is not None and y is not None and C2 * y != 0.0) else None
    sup = {"lambda": soporte("lambda_required", lam_req), "gain_share": tuple(e["gain_support"]), "C2": soporte("capture_required", K1)}
    invs = INV.algebraic(N, C2, lam, y, K1, sup)
    tgt = e["targets"]
    invs.append(INV.phi_partial(tgt[0] if tgt else None, tgt[1] if tgt else None) if C2 is not None
                else INV.Inversion("phi_partial", result_status="undefined_denominator", reason="C2_UNDEFINED"))
    costosas = set()
    if C2 is None:
        invs.append(INV.Inversion("external_factor", result_status="undefined_denominator", reason="C2_UNDEFINED", method_id="fixed_point_bracket_bisection"))
        invs.append(INV.Inversion("phi_total", result_status="undefined_denominator", reason="C2_UNDEFINED", method_id="fixed_point_bracket_bisection"))
    else:
        if not e["mapping"]:
            invs.append(INV.not_identified("external_factor", "EXTERNAL_FACTOR_NOT_IDENTIFIED"))
        elif not e["run_endogenous"]:
            invs.append(INV.Inversion("external_factor", result_status="incomplete", reason="ENDOGENOUS_NOT_RUN", method_id="fixed_point_bracket_bisection"))
        else:
            costosas.add("external_factor")
        if not e["run_endogenous"]:
            invs.append(INV.Inversion("phi_total", result_status="incomplete", reason="ENDOGENOUS_NOT_RUN", method_id="fixed_point_bracket_bisection"))
        elif e["menu"] == "d":
            invs.append(INV.endogenous("phi_total", None, K1, 0.0, 1.0, invariance_proof="MENU_D_TAU_F_ZERO_PHI_ABSENT", constant_value=C2))
        else:
            costosas.add("phi_total")
    out = {}
    for inv in invs:
        filas = _scratch(run, lambda inv=inv: run.inversion_rows(cid, inv))
        fila = filas["inversion_result"][0]
        if e["con_unidad"] and inv.inversion_id in PROVISIONALES and inv.result_status in ("computed", "outside_support"):
            fila["_fin"] = {"k": "lambda" if inv.inversion_id == "lambda_required" else "C2", "set": e["set"], "country": e["pais"],
                            "value": inv.value, "c2_defined": C2 is not None}
        out[inv.inversion_id] = filas
    return out, costosas


def _sin_ref(x):
    return {k: v for k, v in x.items() if k != "evidence_ref"}


def verificar_inversiones(rows, cid, run, e):
    """(inválidos, incompletos) de las 6 inversiones de la celda y sus hijas. Recalculables: fila del núcleo IGUAL campo a
    campo (incluidos valor, estado, banderas, motivo y `_fin`), fila de convergencia y, en v3, hijas y objetivos.
    Costosas: estado, banderas, valor resumen, conteos, hijas y convergencia recalculada desde las hijas."""
    inv_, inc = [], []
    f1 = lambda t, **k: [x for x in rows.get(t, []) if all(x.get(a) == b for a, b in k.items())]  # noqa: E731
    filas = f1("inversion_result", cell_id=cid)
    ids = [x.get("inversion_id") for x in filas]
    if sorted(ids) != sorted(INV.INVERSIONS):
        return ["inversiones %s distintas de las 6 del núcleo" % sorted(map(str, ids))], []
    decl = {x["inversion_id"]: x for x in filas}
    esper, costosas = inversiones_nucleo(run, cid, e, decl)
    v3 = e["contrato"] == "v3"
    conv = {x.get("quantity_id"): x for x in rows.get("convergence_result", []) if str(x.get("quantity_id", "")).startswith("INV:%s:" % cid)}
    hijas_v2 = {t: f1(t, cell_id=cid) for t in ("scalar_inversion_roots", "scalar_inversion_intervals", "inversion_targets")}
    for iid in INV.INVERSIONS:
        row = decl[iid]
        qid = "INV:%s:%s" % (cid, iid)
        if iid in esper:
            fe = esper[iid]
            dif = sorted(k for k in set(row) | set(fe["inversion_result"][0]) if _c(row.get(k)) != _c(fe["inversion_result"][0].get(k)))
            if dif:
                inv_.append("inversión %s distinta de la del núcleo con entradas autenticadas en %s" % (iid, dif[:6]))
            ce = [x for x in fe.get("convergence_result", [])]
            if ce:
                if qid not in conv or _sin_ref(conv[qid]) != _c(_sin_ref({k: ce[0][k] for k in CV.COLUMNAS})):
                    inv_.append("convergencia INV de %s distinta de la recalculada" % iid)
                elif ce[0]["status"] != "pass":
                    inc.append("convergencia INV de %s en %s" % (iid, ce[0]["status"]))
            elif qid in conv:
                inv_.append("convergencia INV de %s no exigida por el núcleo" % iid)
            for t in ("scalar_inversion_roots", "scalar_inversion_intervals") + (("inversion_targets",) if v3 else ()):
                got = sorted((_c(x) for x in hijas_v2[t] if x.get("inversion_id") == iid), key=json.dumps)
                exp = sorted((_c(x) for x in fe.get(t, [])), key=json.dumps)
                if got != exp:
                    if not v3 and t != "inversion_targets" and not got and exp:
                        inc.append("%s de %s no exportadas (contrato v2)" % (t, iid))
                    else:
                        inv_.append("%s de %s distintas de las del núcleo" % (t, iid))
            continue
        # ---- costosa (evidencia del productor)
        rs, cs = row.get("result_status"), row.get("computation_status")
        lo, hi = DOMINIO_ENDOGENO[iid]
        vf = INV.VALUE_FIELD[iid]
        roots = sorted(hijas_v2["scalar_inversion_roots"], key=lambda x: x.get("root_index", -1))
        roots = [x for x in roots if x.get("inversion_id") == iid]
        ivs = sorted((x for x in hijas_v2["scalar_inversion_intervals"] if x.get("inversion_id") == iid), key=lambda x: x.get("interval_index", -1))
        mal = []
        base = {"method_id": "fixed_point_bracket_bisection", "equation_id": INV.EQUATION[iid], "outside_support": False, "admissibility_violated": False,
                "kink_adjacent": False, "target_value": 0.0, "target_unit": "share"}
        mal += ["%s=%r" % (k, row.get(k)) for k, v in base.items() if row.get(k) != v]
        mal += ["%s no nulo" % f for f in INV.VALUE_FIELD.values() if f != vf and row.get(f) is not None]
        if rs not in INV.STATUS_TO_COMPUTATION or INV.STATUS_TO_COMPUTATION[rs] != cs or rs in ("outside_support", "not_identified", "undefined_denominator"):
            mal.append("estado %r/%r imposible para una búsqueda costosa ejecutada" % (rs, cs))
        if row.get("no_solution") is not (rs == "no_feasible_solution"):
            mal.append("no_solution incoherente")
        if cs == "complete":
            n_r, n_i = row.get("n_scalar_solutions"), row.get("n_scalar_intervals")
            if row.get("fixed_point_converged") is not True or not isinstance(n_r, int) or not isinstance(n_i, int) or isinstance(n_r, bool) or isinstance(n_i, bool):
                mal.append("completa sin convergencia o sin conteos enteros")
            else:
                if (rs == "computed") != (n_r + n_i > 0):
                    mal.append("computed exige raíces o intervalos; no_feasible, ninguno")
                if rs == "no_feasible_solution" and row.get("reason_code") not in RAZONES_SIN_SOLUCION[iid]:
                    mal.append("motivo de inexistencia %r" % row.get("reason_code"))
                if rs == "computed" and row.get("reason_code") is not None:
                    mal.append("computed con motivo")
                if v3 or n_r + n_i > 0:
                    if len(roots) != n_r or len(ivs) != n_i:
                        (mal if v3 else inc).append("hijas (%d, %d) distintas de los conteos (%s, %s)" % (len(roots), len(ivs), n_r, n_i))
                for k, x in enumerate(roots):
                    if not (x.get("root_index") == k and x.get("converged") is True and x.get("method_id") == "certified_root_search"
                            and _fin(x.get("residual")) and abs(x["residual"]) <= e["tol_root"] and _fin(x.get("value"))
                            and _fin(x.get("bracket_low")) and _fin(x.get("bracket_high")) and x["bracket_low"] <= x["value"] <= x["bracket_high"]
                            and lo <= x["value"] <= hi):
                        mal.append("raíz %d sin índice, convergencia, residuo, intervalo aislante o dominio" % k)
                for k, x in enumerate(ivs):
                    if not (x.get("interval_index") == k and _fin(x.get("lower")) and _fin(x.get("upper")) and x["lower"] < x["upper"]
                            and lo <= x["lower"] and x["upper"] <= hi and isinstance(x.get("lower_closed"), bool) and isinstance(x.get("upper_closed"), bool)
                            and _fin(x.get("residual_bound")) and x["residual_bound"] >= 0 and x.get("method_id") == "invariance_proof"):
                        mal.append("intervalo %d fuera de contrato" % k)
                for a, b in zip(ivs, ivs[1:]):
                    if _fin(a.get("upper")) and _fin(b.get("lower")) and not a["upper"] < b["lower"]:
                        mal.append("intervalos no disjuntos u ordenados")
                uno = len(roots) == 1 and not ivs and n_r == 1 and n_i == 0
                val = row.get(vf)
                if uno and val != roots[0].get("value") or (not uno and val is not None):
                    mal.append("valor resumen %r sin raíz única aislada igual" % (val,))
                if row.get("corner_binding") is not any(x.get("value") in (lo, hi) for x in roots):
                    mal.append("corner_binding incoherente con las raíces")
        else:
            if any(row.get(k) is not None for k in ("n_scalar_solutions", "n_scalar_intervals", vf, "fixed_point_converged")):
                mal.append("no completa con conteos, valor o convergencia")
            if not row.get("reason_code"):
                mal.append("no completa sin motivo")
            if roots or ivs:
                mal.append("hallazgos de una búsqueda no completa publicados como hijas")
            if row.get("corner_binding") is not False:
                mal.append("corner_binding en búsqueda no completa")
            inc.append("inversión %s en %s (%s)" % (iid, rs, row.get("reason_code")))
        # convergencia recalculada desde las hijas (si v2 sin hijas y conteos 0: lista vacía, ausencia justificada)
        ras = [(x.get("value"), x.get("bracket_low"), x.get("bracket_high"), x.get("converged")) for x in roots]
        ivv = [(x.get("lower"), x.get("upper")) for x in ivs]
        cands = [_c({k: CV.fila_raices(qid, CV.ref("inversion_result", {"cell_id": cid, "inversion_id": iid}), raices=ras, intervalos=ivv, coverage=cov,
                                       computation_status=cs, no_solution=row.get("no_solution") is True, dominio=(0.0, 1.0),
                                       dominio_cubierto=(0.0, 1.0) if cov == "certified" else None, tolerancia=e["xtol"],
                                       unidad="phi" if iid == "phi_total" else "share", evidence_ref=None)[k] for k in CV.COLUMNAS if k != "evidence_ref"})
                 for cov in ("certified", "not_certified")]
        if qid not in conv or _sin_ref(conv[qid]) not in cands:
            mal.append("convergencia INV distinta de la recalculada desde las hijas")
        elif cs == "complete" and conv[qid].get("status") != "pass":
            inc.append("convergencia INV de %s en %s" % (iid, conv[qid].get("status")))
        if v3:
            defin = DEF_FISCAL if row.get("reason_code") == "NO_ROOT_CERTIFIED_FISCAL_LOWER_BOUND" else \
                "C2(x) = K1 con x en [%s, %s], recalculando adopción y bases en cada x" % (lo, hi)
            exp = {"cell_id": cid, "inversion_id": iid, "tau_f_given": None, "supplier_share_target": None, "definition": defin,
                   "evidence_ref": "CONTRATOS_D7_B_D8.md#inversion_result; grilla " + e["grid_sha256"][:16]}
            if [_c(x) for x in hijas_v2["inversion_targets"] if x.get("inversion_id") == iid] != [_c(exp)]:
                mal.append("inversion_targets distinto del derivado")
        if mal:
            inv_.append("inversión %s (evidencia del productor) fuera de contrato: %s" % (iid, mal[:4]))
    ajenas = {t: [x for x in xs if x.get("inversion_id") not in INV.INVERSIONS] for t, xs in hijas_v2.items()}
    if any(ajenas.values()):
        inv_.append("hijas de inversiones inexistentes")
    return inv_, inc


# ================================================================================================ techo
def verificar_techo(te, rows, e):
    """(inválidos, incompletos) del techo: dominio y admisibilidad del punto, valor del modelo en el punto, laterales y
    testigos de supremos no alcanzados (sin convertirlos en máximo) y, en v3, la fila C2 de convergencia certificada."""
    inv_, inc = [], []
    st = te.get("computation_status")
    C2, err = te.get("C_2"), te.get("numerical_error")
    ceid = te.get("ceiling_id")
    (dl, dh), (fl, fh) = sup_axes(e["menu"], *e["barras"])
    wit = [x for x in rows.get("sup_witness", []) if x.get("ceiling_id") == ceid]
    if st == "complete":
        if not (_fin(C2) and _fin(err) and 0 <= err <= e["tol_converge"] and te.get("reason_code") is None):
            inv_.append("techo complete sin C_2 finito o con numerical_error %r > tol_converge %r" % (err, e["tol_converge"]))
    elif st in ("incomplete", "failed"):
        if not te.get("reason_code"):
            inv_.append("techo %s sin motivo" % st)
        inc.append("techo %s (%s)" % (st, te.get("reason_code")))
    else:
        inv_.append("techo con estado %r para un instrumento disponible" % st)
    na = te.get("sup_not_attained")
    if na is False:
        td, tf = te.get("tau_d_at_sup"), te.get("tau_f_at_sup")
        if not (_fin(td) and _fin(tf) and dl <= td <= dh and fl <= tf <= fh):
            inv_.append("punto del supremo (%r, %r) fuera del dominio del menú %s [%s,%s]x[%s,%s]" % (td, tf, e["menu"], dl, dh, fl, fh))
        elif _fin(C2):
            try:
                v = e["valor_en"](td, tf)
            except Exception as x:  # noqa: BLE001
                v = None
                inv_.append("punto del supremo no evaluable por el modelo: %s" % x)
            if v is not None and not (_fin(v) and abs(v - C2) <= e["tol_valor"] * max(1.0, abs(C2))):
                inv_.append("C_2 %r distinto del valor del modelo en el punto alcanzado %r" % (C2, v))
        if te.get("sup_lateral_low") is not None or te.get("sup_lateral_high") is not None or wit:
            inv_.append("supremo alcanzado con laterales o testigos")
    elif na is True:
        if te.get("tau_d_at_sup") is not None or te.get("tau_f_at_sup") is not None:
            inv_.append("supremo no alcanzado con punto (el supremo no es un máximo)")
        if st == "complete":
            if e["certificado"]:
                inv_.append("proveedor certificado: un supremo completo es alcanzado (no alcance => incomplete)")
            lats = [x for x in (te.get("sup_lateral_low"), te.get("sup_lateral_high")) if x is not None]
            if te.get("sup_lateral_low") is None or te.get("sup_lateral_high") is None or not all(_fin(x) for x in lats):
                inv_.append("supremo no alcanzado sin los dos laterales finitos")
            elif not (_fin(C2) and C2 == max(lats)):
                inv_.append("C_2 %r distinto del mayor límite lateral %r" % (C2, max(lats)))
            if e["contrato"] != "v3":
                inv_.append("techo no alcanzado: testigos laterales no exportados (contrato v2)")
            elif not wit:
                inv_.append("supremo no alcanzado sin sup_witness")
            else:
                lados = {x.get("side") for x in wit}
                if not lados <= {"left_limit", "right_limit"} or len(lados) != 1:
                    inv_.append("sup_witness con lados %s" % sorted(map(str, lados)))
                lado = "left_limit" if _fin(C2) and C2 == te.get("sup_lateral_low") else "right_limit"
                seq = sorted(wit, key=lambda x: x.get("sequence_index", -1) if isinstance(x.get("sequence_index"), int) else -1)
                ds = [x.get("approach_distance") for x in seq]
                if [x.get("sequence_index") for x in seq] != list(range(len(seq))):
                    inv_.append("sup_witness con índices distintos de 0..n-1")
                if not (all(_fin(d) and d >= 0 for d in ds) and all(a > b for a, b in zip(ds, ds[1:]))):
                    inv_.append("sup_witness con distancias negativas o no estrictamente decrecientes")
                for x in seq:
                    if not (_fin(x.get("tau_d")) and _fin(x.get("tau_f")) and dl <= x["tau_d"] <= dh and fl <= x["tau_f"] <= fh):
                        inv_.append("sup_witness fuera del dominio del menú")
                        break
                    if x.get("limit_value") != C2 or not (_fin(x.get("residual")) and x["residual"] >= 0) or x.get("side") != lado:
                        inv_.append("sup_witness con límite distinto de C_2, residuo inválido o lado incoherente")
                        break
    else:
        inv_.append("sup_not_attained %r no booleano" % (na,))
    # ---- fila C2 de convergencia (v3, proveedor certificado)
    if e["contrato"] == "v3" and e["certificado"]:
        cr = [x for x in rows.get("convergence_result", []) if x.get("quantity_id") == "C2:" + str(ceid)]
        esper = {"level_before": 0, "level_after": 1, "result_ref": "capture_ceiling_result:" + json.dumps({"ceiling_id": ceid}, sort_keys=True, separators=(",", ":")),
                 "method_id": "certified_branch_and_bound", "value_before": C2, "change_bound": err, "tolerance": e["tol_converge"], "unit": "share",
                 "topology_before": None, "topology_after": None, "verdict_changes": 0, "coverage_complete": st == "complete",
                 "status": "pass" if (st == "complete" and _fin(err) and err <= e["tol_converge"]) else "fail"}
        if len(cr) != 1:
            inv_.append("fila C2 de convergencia certificada ausente o duplicada (%d)" % len(cr))
        else:
            r = cr[0]
            dif = [k for k, v in esper.items() if _c(r.get(k)) != _c(v)]
            va = r.get("value_after")
            if dif:
                inv_.append("fila C2 distinta del contrato en %s" % dif)
            elif not (_fin(va) and _fin(C2) and _fin(err) and C2 <= va <= C2 + err * (1 + 1e-9) + 1e-15):
                inv_.append("fila C2: cota superior %r incompatible con C_2 %r y el error %r" % (va, C2, err))
    return inv_, inc


# ================================================================================================ resumen canónico
def resumen_canonico(base, filas, comp, post, estado, motivos, clave):
    """Campos NO diagnósticos de una celda de resultados.json, desde la derivación (`base`: identidad, contexto y
    precomprobaciones) y las filas validadas. Única fuente: el productor la usa para escribir y la ruta común para
    contrastar exactamente."""
    ce = filas["capture_ceiling_result"][0] if len(filas.get("capture_ceiling_result", [])) == 1 else {}
    cf = filas["confrontation_result"][0] if len(filas.get("confrontation_result", [])) == 1 else {}
    out = dict(base)
    out.update(estado=estado, motivos=list(motivos), completitud=comp, poscomprobaciones=post, cell_id=clave["cell_id"],
               techo={k: ce.get(k) for k in ("C_2", "numerical_error", "computation_status", "reason_code", "sup_not_attained")},
               confrontacion={k: cf.get(k) for k in ("G", "K_comp_1", "verdict", "computation_status", "reason_code")}, clave_E12=clave)
    return _c(out)


def comprobar_resumen(c, esperado):
    """Motivos por los que la celda `c` de resultados.json no es la canónica: campos exactos (no diagnósticos) iguales
    y diagnósticos del tipo declarado; ningún campo extra."""
    mot = []
    claves = set(esperado) | set(DIAGNOSTICO)
    if set(c) != claves:
        mot.append("campos del resumen distintos del contrato: sobran %s faltan %s" % (sorted(set(c) - claves)[:4], sorted(claves - set(c))[:4]))
    for k, v in esperado.items():
        if _c(c.get(k)) != v:
            mot.append("resumen.%s distinto del derivado de filas y autoridad" % k)
    t = c.get("tiempos_s")
    if not (isinstance(t, dict) and all(isinstance(k, str) and _fin(x) and x >= 0 for k, x in t.items())):
        mot.append("resumen.tiempos_s (diagnóstico) mal formado")
    for k in DIAGNOSTICO[1:]:
        if not isinstance(c.get(k), bool):
            mot.append("resumen.%s (diagnóstico) no booleano" % k)
    return mot


def consumir_celda(c):
    """Lo ÚNICO consumible de una celda ya validada: el resumen sin campos diagnósticos (los estados provisionales de
    las inversiones no están en el resumen: se cierran al ensamblar con unidades.cerrar_provisionales_seleccion)."""
    return {k: v for k, v in c.items() if k not in DIAGNOSTICO}


# ================================================================================================ RELACIONES (RELACIONES CONTRATO 3.7)
# Macro, geometría y evidencia numérica: relaciones con la autoridad y entre tablas, con contexto AUTÉNTICO (no vacío).
def ref_evidencia(e):
    """evidence_ref que el núcleo (Run.evidence) asigna a esta evidencia: hash de su CONTENIDO completo."""
    from .keys import H
    from .run import _dec
    return "NEV:" + H({"k": e.get("kind"), "t": e.get("result_table"), "pk": e.get("record_pk"), "d": e.get("definition"), "box": e.get("domain_box"),
                       "err": _dec(e["error_bound"]) if e.get("error_bound") is not None else None, "u": e.get("unit"), "m": e.get("method_id"),
                       "s": e.get("status")})[:40]


def macro_esperada(run, om, oid, country, st, context, run_id, technical, payload_cond):
    """Fila lambda_pi_envelope que produce Run.macro_row para (ω, país, estado nacional) DERIVADOS, con el run_id y la
    técnica del PRODUCTOR. El payload condicional (macro-ca2-v2) lo construye `payload_cond` desde las tablas del bundle
    autenticado; la validación completa del bundle (validate_key) es evidencia del productor y no se repite."""
    from . import keys as K
    from . import macro as MC
    from .run import _dec, _finite_dec
    from .numeric import canon_dec
    v = om["values"]
    m = MC.bridge(st.share_dict(), v)
    block = om["block"]
    prim_rows = [{"parameter_id": p.replace("!", "_").replace(":", "_"), "value": canon_dec(float(x)) if not _finite_dec(x) else canon_dec(x),
                  "value_unit": u} for p, x, u in st.primitive_values]
    national = K.national_state(sorted(prim_rows, key=lambda r: r["parameter_id"]), {k: float(x) for k, x in st.shares}, st.joint_domain_sha256)
    nsha = K.H(national)
    if st.channel == "strict":
        payload = K.macro_strict(country, block, v, run.C.K, run.units, national, list(st.dependencies), run.inp.protocol[2], technical)
        msha = run.C.key("macro", payload)
    else:
        payload = payload_cond(st, om, block, context, technical)
        msha = K.H(payload)
    mid = "MAC:" + K.H({"r": run_id, "c": country, "o": oid, "b": block, "m": msha})[:40]
    admissible = m.admissible and v["eta_H"] > -1
    lam = float(m.lambda_pi) if m.lambda_pi is not None else None
    return {"macro_id": mid, "run_id": run_id, "country_id": country, "omega_id": oid,
            "s_L_bar": float(dict(st.shares)["s_L_bar"]), "eta_w": _dec(v["eta_w"]), "eta_H": _dec(v["eta_H"]),
            "theta_W": float(m.theta_W), "s_T_marg": float(m.s_T_marg), "q_pot": float(m.q_pot), "lambda_pi": lam,
            "admissible": admissible, "eta_w_block": block, "theta_W_negative": m.theta_W_negative,
            "computation_status": "complete" if admissible else "excluded",
            "reason_code": None if admissible else (m.reasons[0] if m.reasons else "INADMISSIBLE"),
            "macro_key_sha256": msha, "macro_key_payload": payload, "national_state_sha256": nsha}


def omega_autentico(run, oid):
    """Filas omega y omega_values de ω, reconstruidas por el NÚCLEO (como Run.build_omegas) desde sus valores derivados:
    el contexto auténtico de Checker.omega/Checker.macro (nunca las del paquete, que no las exporta)."""
    from .run import COMMON_DERIVED, DERIVED_FORMULA, _dec
    om = run.omegas[oid]
    fila = [x for x in run.rows["omega"] if x["omega_id"] == oid]
    v, derived, set_id = om["values"], om["derived"], om["set"]
    vals = [{"omega_id": oid, "parameter_id": pid, "value": _dec(v[pid]), "value_unit": run.units[pid], "binding_id": f"BND:{set_id}:{pid}:global",
             "formula_id": None, "reason_code": None} for pid in sorted(v)]
    vals += [{"omega_id": oid, "parameter_id": pid, "value": _dec(derived[pid]) if derived else None, "value_unit": run.units[pid],
              "binding_id": f"BND:{set_id}:{pid}:global", "formula_id": DERIVED_FORMULA[pid], "reason_code": None if derived else "DERIVED_UNDEFINED"}
             for pid in COMMON_DERIVED]
    return fila[:1], vals


def verificar_macro(rows, mac, esperada, run, oid, technical):
    """(inválidos, incompletos) de la fila λ_π de la celda: igualdad EXACTA con la fila esperada y Checker.omega +
    Checker.macro del núcleo con el contexto auténtico de ω, la técnica y el protocolo del productor."""
    from . import rules as RULES
    inv_ = []
    dif = sorted(k for k in set(mac) | set(esperada) if _c(mac.get(k)) != _c(esperada.get(k)))
    if dif:
        inv_.append("fila λ_π distinta de la derivada de la autoridad en %s" % dif[:6])
    om_rows, om_vals = omega_autentico(run, oid)
    tablas = {"omega": om_rows, "omega_values": om_vals, "lambda_pi_envelope": [T.normalize_row(run.C, "lambda_pi_envelope", mac)]}
    try:
        ch = RULES.Checker(tablas, run.C, run.inp.d7, technical=technical, protocol_sha256=run.inp.protocol[2], tolerances=run.inp.tolerances)
        ch.omega()
        ch.macro()
        inv_ += ["Checker.macro: " + x for x in ch.errors[:4]]
    except Exception as x:  # noqa: BLE001
        inv_.append("Checker.macro no ejecutable: %s: %s" % (type(x).__name__, x))
    return inv_, []


def verificar_geometria(rows, cid, e):
    """(inválidos, incompletos) LOCALES de R1/R2 de la celda (todas las ramas): dominio del menú, etiqueta de borde,
    residuo de vértice = |f| en el vértice, extremos y bordes de componentes, raíz R2 sobre la trayectoria de su sección
    con |f(raíz)| <= residuo <= T_root (el residuo de una CUERDA de arista no se exige: es diagnóstico), cajas rechazadas
    en el dominio y relación conjunto vacío demostrado <-> R1/R2. Las reglas con evidencia (Checker.geometry) van en
    checker_nucleo (v3)."""
    from . import sections as R2M
    from .contour import _boundary_label
    inv_ = []
    (dl, dh), (fl, fh) = sup_axes(e["menu"], *e["barras"])
    box = ((dl, dh), (fl, fh))
    f, tol = e["f"], e["tol_root"]
    dentro = lambda x, y: _fin(x) and _fin(y) and dl <= x <= dh and fl <= y <= fh  # noqa: E731
    vs = [v for v in rows.get("r1_vertices", []) if v.get("cell_id") == cid]
    mal = 0
    for v in vs:
        x, y = v.get("tau_d"), v.get("tau_f")
        if not dentro(x, y):
            inv_.append("vértice R1 %s fuera del dominio del menú (%r, %r)" % (v.get("vertex_id"), x, y))
            break
        lab = _boundary_label(x, y, box)
        if v.get("boundary_label") != lab or v.get("is_boundary") is not (lab is not None):
            inv_.append("vértice R1 %s con etiqueta de borde %r distinta de la de su posición %r" % (v.get("vertex_id"), v.get("boundary_label"), lab))
            break
        fv = abs(f(x, y))
        if not (_fin(v.get("residual")) and abs(v["residual"] - fv) <= 1e-15 + 1e-12 * fv):
            mal += 1
    if mal:
        inv_.append("%d vértices R1 con residuo distinto de |f| en el vértice" % mal)
    for cp in [x for x in rows.get("r1_components", []) if x.get("cell_id") == cid]:
        cv = [v for v in vs if v.get("component_id") == cp.get("component_id")]
        if not cv or not all(dentro(v.get("tau_d"), v.get("tau_f")) for v in cv):
            inv_.append("componente R1 %s sin vértices válidos" % cp.get("component_id"))
            continue
        if (cp.get("tau_d_min"), cp.get("tau_d_max"), cp.get("tau_f_min"), cp.get("tau_f_max"), cp.get("n_boundary_intersections")) != (
                min(v["tau_d"] for v in cv), max(v["tau_d"] for v in cv), min(v["tau_f"] for v in cv), max(v["tau_f"] for v in cv),
                sum(1 for v in cv if v.get("is_boundary"))):
            inv_.append("componente R1 %s con extremos o bordes distintos de sus vértices" % cp.get("component_id"))
    ids = {(v.get("component_id"), v.get("vertex_id")) for v in vs}
    if len(ids) != len(vs) or {v.get("component_id") for v in vs} - {x.get("component_id") for x in rows.get("r1_components", []) if x.get("cell_id") == cid}:
        inv_.append("vértices R1 duplicados o de componentes inexistentes")
    for x in [x for x in rows.get("r1_rejected_crossings", []) if x.get("cell_id") == cid]:
        if not (dentro(x.get("tau_d_low"), x.get("tau_f_low")) and dentro(x.get("tau_d_high"), x.get("tau_f_high"))):
            inv_.append("cruce rechazado fuera del dominio")
    for rt in [x for x in rows.get("r2_roots", []) if x.get("cell_id") == cid]:
        sec = rt.get("section_id")
        try:
            path = R2M._path(sec, e["menu"], e["barras"][0], e["barras"][1], e["tasa"])
        except ValueError:
            path = None
        if path is None:
            inv_.append("raíz R2 en una sección %r no aplicable al menú" % sec)
            continue
        g, t0, t1 = path
        x, y = rt.get("tau_d_root"), rt.get("tau_f_root")
        t = {"tau_f_0": x, "tau_d_0": y, "paridad": x, "tau_d_estatutario": y}[sec]
        lo, hi = rt.get("parameter_low"), rt.get("parameter_high")
        if not (_fin(t) and _fin(lo) and _fin(hi) and t0 <= lo <= t <= hi <= t1 and g(t) == (x, y) and dentro(x, y)):
            inv_.append("raíz R2 %s/%s fuera de la trayectoria de su sección o de su intervalo" % (sec, rt.get("root_index")))
            continue
        res = rt.get("residual")
        if not (_fin(res) and 0 <= res <= tol and abs(f(x, y)) <= res * (1 + 1e-9) + 1e-16):
            inv_.append("raíz R2 %s/%s con residuo %r incompatible con |f| = %r o con T_root" % (sec, rt.get("root_index"), res, abs(f(x, y))))
    # relaciones de topología y conteos SIN evidencia (subconjunto de Checker.geometry válido también en v2)
    comps = [x for x in rows.get("r1_components", []) if x.get("cell_id") == cid]
    for r1 in [x for x in rows.get("r1_summary", []) if x.get("cell_id") == cid and x.get("computation_status") == "complete"]:
        if r1.get("n_components") != len(comps) or (r1.get("no_solution") is True) != (len(comps) == 0):
            inv_.append("R1 con n_components/no_solution distintos de sus componentes")
        if not all(_fin(v.get("residual")) and v["residual"] <= tol for v in vs) or not (_fin(r1.get("residual_bound")) and r1["residual_bound"] <= tol):
            inv_.append("R1 completo con residuos sobre T_root")
    porv = {(v.get("component_id"), v.get("vertex_id")): v for v in vs}
    for ed in [x for x in rows.get("r1_edges", []) if x.get("cell_id") == cid]:
        a_, b_ = porv.get((ed.get("component_id"), ed.get("from_vertex_id"))), porv.get((ed.get("component_id"), ed.get("to_vertex_id")))
        if a_ is None or b_ is None or not (_fin(ed.get("geometric_error_bound")) and 0 <= ed["geometric_error_bound"] <= e["r1_tol"]):
            inv_.append("arista R1 con vértices ausentes en su componente o cota geométrica fuera de r1_geometry_tol")
            break
    for s_ in [x for x in rows.get("r2_sections", []) if x.get("cell_id") == cid]:
        rs = sorted((x for x in rows.get("r2_roots", []) if x.get("cell_id") == cid and x.get("section_id") == s_.get("section_id")), key=lambda x: x.get("root_index", -1))
        if s_.get("computation_status") == "complete":
            if not (s_.get("n_roots_by_section") == len(rs) and [x.get("root_index") for x in rs] == list(range(len(rs)))
                    and s_.get("n_tangential_roots") == sum(1 for x in rs if x.get("root_type") == "tangent") and (s_.get("no_solution") is True) == (not rs)):
                inv_.append("sección R2 %s con conteos o índices distintos de sus raíces" % s_.get("section_id"))
        elif rs:
            inv_.append("sección R2 %s no completa con raíces publicadas" % s_.get("section_id"))
    # vacío demostrado (cota certificada de C2 < K1): R1 sin componentes y secciones aplicables completas sin raíces
    if e["vacio_demostrado"]:
        r1 = [x for x in rows.get("r1_summary", []) if x.get("cell_id") == cid]
        if not (len(r1) == 1 and r1[0].get("computation_status") == "complete" and r1[0].get("n_components") == 0 and r1[0].get("no_solution") is True
                and r1[0].get("residual_bound") == 0.0 and r1[0].get("geometry_error_bound") == 0.0 and not vs):
            inv_.append("C2 + cota < K1 (vacío demostrado) pero R1 no es el conjunto vacío certificado")
        for s in [x for x in rows.get("r2_sections", []) if x.get("cell_id") == cid]:
            aplic = R2M._path(s.get("section_id"), e["menu"], e["barras"][0], e["barras"][1], e["tasa"]) is not None
            if aplic and (s.get("section_id") != "tau_d_estatutario" or e["tasa"] is not None) and not (
                    s.get("computation_status") == "complete" and s.get("n_roots_by_section") == 0 and s.get("no_solution") is True):
                inv_.append("vacío demostrado pero la sección %s no está completa y vacía" % s.get("section_id"))
    return inv_, []


def verificar_evidencia(rows, cid, ceid, e):
    """(inválidos, incompletos) de numerical_evidence de la celda (v3): referencia autocertificada; cada fila de
    convergencia ligada a SU evidencia (tabla/PK, método, unidad, cota = change_bound, estado), con las cotas propias de
    G y de C2; las demás evidencias explicadas por una regla del núcleo (raíz de inversión, sección R2); ninguna huérfana."""
    inv_ = []
    evs = [x for x in rows.get("numerical_evidence", []) if isinstance(x.get("record_pk"), dict)
           and (x["record_pk"].get("cell_id") == cid or x["record_pk"].get("ceiling_id") == ceid)]
    por_ref = {}
    for x in evs:
        if x.get("evidence_ref") != ref_evidencia(x):
            inv_.append("evidencia %s con contenido que no corresponde a su referencia (hash del contenido)" % str(x.get("evidence_ref"))[:16])
        por_ref.setdefault(x.get("evidence_ref"), []).append(x)
    if any(len(v) > 1 for v in por_ref.values()):
        inv_.append("evidencias duplicadas con la misma referencia")
    explicadas = set()
    convs = [x for x in rows.get("convergence_result", []) if str(x.get("quantity_id", "")).split(":", 1)[0] in ("G", "R1", "INV", "C2")
             and (cid in str(x.get("quantity_id")) or ceid in str(x.get("quantity_id")))]
    for cv in convs:
        x = (por_ref.get(cv.get("evidence_ref")) or [None])[0]
        if x is None:
            inv_.append("convergencia %s sin su evidencia" % str(cv.get("quantity_id"))[:24])
            continue
        explicadas.add(cv.get("evidence_ref"))
        ref_res = (x.get("result_table") or "") + ":" + json.dumps(x.get("record_pk"), sort_keys=True, separators=(",", ":"))
        estado_ok = (x.get("status") == "pass") if cv.get("status") == "pass" else (x.get("status") in ("limitation", "fail"))
        if not (cv.get("result_ref") == ref_res and x.get("method_id") == cv.get("method_id") and x.get("unit") == cv.get("unit")
                and _c(x.get("error_bound")) == _c(cv.get("change_bound")) and estado_ok):
            inv_.append("evidencia de %s contradice su convergencia (referencia, método, unidad, cota o estado)" % str(cv.get("quantity_id"))[:24])
    for x in evs:
        if x.get("evidence_ref") in explicadas:
            continue
        t, m, s = x.get("result_table"), x.get("method_id"), x.get("status")
        if t == "inversion_result" and m in ("certified_root_search", "invariance_proof") and s == "pass" and x.get("kind") == "root":
            ok = _c(x.get("error_bound")) == _c(e["tol_root"]) if m == "certified_root_search" else (_fin(x.get("error_bound")) and x["error_bound"] >= 0)
            iid = (x.get("record_pk") or {}).get("inversion_id")
            fila = [r for r in rows.get("inversion_result", []) if r.get("cell_id") == cid and r.get("inversion_id") == iid]
            ok = ok and len(fila) == 1 and fila[0].get("computation_status") == "complete" and iid in ENDOGENAS
        elif t == "inversion_result" and m == "uncertified_root_scan":
            iid = (x.get("record_pk") or {}).get("inversion_id")
            fila = [r for r in rows.get("inversion_result", []) if r.get("cell_id") == cid and r.get("inversion_id") == iid]
            ok = s == "limitation" and x.get("error_bound") is None and len(fila) == 1 and fila[0].get("computation_status") != "complete"
        elif t == "r2_sections" and m in ("certified_root_search", "certified_empty_by_C2_bound"):
            sec = [r for r in rows.get("r2_sections", []) if r.get("cell_id") == cid and r.get("section_id") == (x.get("record_pk") or {}).get("section_id")]
            ok = (s == "pass" and _c(x.get("error_bound")) == _c(e["tol_root"]) and x.get("unit") == "tau" and len(sec) == 1
                  and sec[0].get("computation_status") == "complete" and (m == "certified_empty_by_C2_bound") == bool(e["vacio_demostrado"]))
        elif t == "r2_sections" and m == "uncertified_root_scan":
            ok = s == "limitation" and x.get("error_bound") is None
        else:
            ok = False
        if not ok:
            inv_.append("evidencia %s (%s/%s/%s) no explicada por ninguna regla del núcleo o contradictoria" % (str(x.get("evidence_ref"))[:16], t, m, s))
    for s in [r for r in rows.get("r2_sections", []) if r.get("cell_id") == cid and r.get("computation_status") == "complete"]:
        n = [x for x in evs if x.get("result_table") == "r2_sections" and (x.get("record_pk") or {}).get("section_id") == s.get("section_id") and x.get("status") == "pass"]
        if len(n) != 1:
            inv_.append("sección R2 %s completa con %d evidencias certificadas" % (s.get("section_id"), len(n)))
    return inv_, []
