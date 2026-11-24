"""rem108 (corrige T7/T8 por esquema de claims.derive y valores de inversión; C8 con el gate del plan de datos; Exp0 con denominadores y corridas; selección F-LAMBDA resuelta desde D7; lote 1 y decisiones) — sucede a rem107: CONCILIACIÓN GLOBAL PROD4 POR CRITERIO (administrativa; solo lectura del proyecto; sin evaluar el modelo). Sucede a
generar_matriz_rem106.py (FUENTE ÚNICA de la matriz, sus vistas, la tabla Exp8, los ensamblajes y las fichas) y corrige/avanza:
  P4-PROD4-DIAGNOSTICO-EXP8 (rem107): tabla COMPLETA por afirmación inconclusa (testigos autenticados, G, C2, K1, λπ, Q de la grilla
    autenticada, g derivada de EQ24 con DME_gAI=0 y contrastada con los nodos D7 de gain_share, diferencias y residual de ΔG=ΔC2−ΔK1).
    Sin umbral de predominio: se dan los términos; la atribución causal/ceteris paribus queda NO probada. Siete casos sin testigos completos,
    identificados por su motivo y sin extrapolarles el diagnóstico.
  PROD4.1 ensamblajes: T7 (registro v4 por capa y cota), T8 (inversion_result con banderas), admissibility_report §18.8 por conjunto
    de soporte (D7), input_audit_report parcial (sin inventar run_id, level ni n_cells_affected).
  PROD4.2: incorpora los resultados de las validaciones sintéticas E1/E2/E3/E5 (validaciones/, prerregistradas) como evidencia.
  PROD4.3–4.5: fichas por tipo de trabajo con IDs reales (conjuntos, padres, filas de capa y país/menú de D7), coste medido o no medido,
    impacto y respaldo de supuestos.
rem106 (conservado):
  P4-PROD4-AUTORIDAD: Entregas.archivo exige PERTENENCIA al inventario fijado con sha256 y tamaño (o una cadena externa autenticada
    explícita); un archivo ausente, agregado fuera del inventario o alterado se rechaza; las exclusiones históricas («externos_al_inventario»
    o «exclusions») solo cubren el propio inventario.
  P4-PROD4-CORRESPONDENCIA: cada obligación del diseño vigente (C1–C10 §4, experimentos 0–6/8/9 §13, T1–T8 §21.1, E1–E6 §19.2, las 16
    afirmaciones de lista_PROD) se desglosa en COMPONENTES por su criterio, con evidencia exacta (archivo, sha256, tabla/fila o clave,
    ámbito y contraste) y una de cinco clases: producto_conciliado · evidencia_existente_pendiente_de_extraccion_o_ensamblaje ·
    calculo_nuevo_necesario · decision_cientifica_pendiente · limite_o_NA_admitido. Exp7 figura como retirado (M3), fuera de obligaciones.
Solo extrae, ordena, une, cuenta y contrasta resultados ACEPTADOS (contrastes C_2 G/N y d/f/df, pares ceteris paribus en η_f, descomposición
exacta del cruce de las afirmaciones inconclusas con K1 = Q/(λπ·g) de EQ24, ensamblaje de auditorías desde D7). Lo que exigiría evaluar el
modelo queda como ficha (FICHAS_PENDIENTES), sin ejecutarse.
Uso: python -B -I -X utf8 generar_matriz_rem108.py <raiz> <revisor> <area> <intento>  (escribe en <area>/conciliacion/intentos/<intento>/)"""
import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CLASES = ("producto_conciliado", "evidencia_existente_pendiente_de_extraccion_o_ensamblaje", "calculo_nuevo_necesario", "decision_cientifica_pendiente",
          "limite_o_NA_admitido")
FIJADOS = {"diseno": ("fase6_planes/PLAN_DISENO_v2_2_30.md", "08fc62957ca33f413cb0c82760426b4d57b7d37f24421d6c35d5670a23e47c9a"),
           "lista_PROD": ("paso4/instalacion/datos/paso4/lista_PROD.json", "42fe89148b4346e3b9defe6f91ff7920823570afe77a932ffdc690373c33bf8b"),
           "plan_prod": ("tmp/paso4_continuacion_p3_desde_rem89/p3/plan_prod.json", "3774c5904f48713a838a0adb2764a70f5371e66f39515ec916848fcfa2cbe79b"),
           "grilla": ("fase5_cuantificacion/extraccion_grilla/grilla_efectiva.csv", "b94b9eedeea87d08071366e2bd8a5b7cd9662ce6f9fd9d7bee42848d6c4c5f90"),
           "paper_to_code": ("contracts/package_a/paper_to_code.csv", None), "solver_error_report": ("reports/validation/solver_error_report.json", None),
           "ledger_lambda": ("fase5_cuantificacion/LEDGER_LAMBDA_PI.md", None), "manifiesto_envolvente": ("fase5_cuantificacion/MANIFIESTO_ENVOLVENTE.md", None),
           "plan_datos": ("fase6_planes/PLAN_BASE_DE_DATOS_v4_1_33.md", "2ac5acc1fadbf0bd38cb70816915a1712eea55ccf147921f0e94b000752c2d85"),
           "freeze": ("fase6_planes/freeze_plans_manifest.json", "79ed9af518385d40a5c936f1c3ab76037374afa2cc956634dc09ee93dce656e2"),
           "protocolo_lambda": ("fase5_cuantificacion/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_v1_2_7.md", "00364bbd0b820cb07fc5b6c5bc2498d80eb92ee5363b8d36de96af9139a8db5f"),
           "claims_py": ("paso4/instalacion/src/paper2b/claims.py", None)}
PLAN_DATOS, FREEZE = FIJADOS["plan_datos"], FIJADOS["freeze"]
LEDGER = ("review_20261028_rem105_produccion_aceptada.json", "76ead00dd977fbd62969adbcf47027d0312456e42567855670347103aaa75c1e")
PAQ = ("pv12_consumidor_cierre_paso4_3_7_2026-10-12_lima1018", "e1538d3a59de50cf2231b9b39e232de0634ecfbcae0c99bae19c5304b2547d5e", "demo/integracion/paquetes_finales_lima1018")
COB = ("comparador_r1_cierre_paso4_3_7_2026-10-12_lima1618", "d7ae61a734af928ec7077d221cfa532cf778050db00b19e3b25cbd90cd7f74a6", "demo/plan15/cobertura_r1.json")
REG = ("resolucion_3_7_2026-10-04_lima1941", "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f", "demo/registro/registro_candidato_v4.json",
       "4cf24bc0d9a407db3afa81042419add41256366311d38f36b0a329384ac7ba31")
SEL = ("p1b_global_h4_paso4_3_7_2026-10-09_lima1913", "829c6663e527075f4966ddf549f4a95ca36154f224602004a194f0ad9e436c8b", "demo/b_v2_p1b/cell_selection.json")
D7 = "salidas_s6/d7/versions/2a25893b09c097b2af22ed2e5be9a4014851faf55bbaaf380c7a078f1a740591"
EPS = 0.01
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731


def hf(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Entregas:
    """rem106 (P4-PROD4-AUTORIDAD): un archivo es evidencia SOLO si pertenece al inventario sellado fijado de su entrega con el MISMO sha256 y
    tamaño. Encontrarlo en disco no basta. Las exclusiones del esquema histórico solo cubren el inventario y su .sha256."""

    def __init__(self, T):
        self.T, self.inv = Path(T), {}

    def inventario(self, nombre):
        if nombre not in self.inv:
            p = self.T / nombre / "audit/entrega.json"
            raw = p.read_bytes() if p.is_file() else None
            d = json.loads(raw) if raw else {}
            excl = d.get("externos_al_inventario", d.get("exclusions", [])) or []
            self.inv[nombre] = (H(raw) if raw else None, d.get("files") if isinstance(d.get("files"), dict) else None, list(excl))
        return self.inv[nombre]

    def archivo(self, nombre, rel, sha_fijado=None, inventario_fijado=None):
        ih, files, excl = self.inventario(nombre)
        p = self.T / nombre / rel
        real = hf(p) if p.is_file() else None
        size = p.stat().st_size if p.is_file() else None
        ent = (files or {}).get(rel)
        if ih is None or files is None:
            mot = "INVENTARIO_AUSENTE_O_ILEGIBLE"
        elif inventario_fijado is not None and ih != inventario_fijado:
            mot = "INVENTARIO_DISTINTO_DEL_FIJADO"
        elif rel in excl:
            mot = "ES_EL_PROPIO_INVENTARIO"
        elif real is None:
            mot = "AUSENTE"
        elif not isinstance(ent, dict):
            mot = "FUERA_DEL_INVENTARIO"
        elif ent.get("sha256") != real or ("bytes" in ent and ent["bytes"] != size):
            mot = "DISTINTO_DEL_INVENTARIO"
        elif sha_fijado is not None and real != sha_fijado:
            mot = "DISTINTO_DEL_SHA_FIJADO"
        else:
            mot = None
        return {"entrega": nombre, "inventario_sha256": ih, "archivo": rel, "sha256": real, "bytes": size, "conforme": mot is None, "motivo": mot,
                "tamano_en_esquema": isinstance(ent, dict) and "bytes" in ent}


def fuente(R, rel, fijado):
    real = hf(R / rel) if (R / rel).is_file() else None
    return {"archivo": rel, "sha256": real, "fijado": fijado, "conforme": real is not None and (fijado is None or real == fijado)}


def ev(archivo, sha, clave, ambito, contraste=None):
    return {"archivo": archivo, "sha256": sha, "clave": clave, "ambito": ambito, "contraste": contraste}


def comp(nombre, clase, criterio, evidencia, nota="", ficha=None):
    assert clase in CLASES, clase
    return {"componente": nombre, "clase": clase, "criterio": criterio, "evidencia": evidencia, "nota": nota, "ficha": ficha}


def unidades(R, E):
    T = R / "tmp"
    base = T / PAQ[0] / PAQ[2]
    aut = [E.archivo(PAQ[0], PAQ[2] + "/paquetes_indice.json", inventario_fijado=PAQ[1])]
    idx = json.loads((base / "paquetes_indice.json").read_bytes())
    U, rech, porsha = {}, [], {}
    for nom, meta in idx["paquetes"].items():
        a = E.archivo(PAQ[0], PAQ[2] + "/" + meta["archivo"], sha_fijado=meta["sha256"], inventario_fijado=PAQ[1])
        aut.append(a)
        if not a["conforme"]:
            continue
        pq = json.loads((base / meta["archivo"]).read_bytes())
        ent = pq["entrega"]
        _, files, _ = E.inventario(ent)
        porsha.setdefault(ent, {v["sha256"]: k for k, v in (files or {}).items()})
        for u in pq["unidades"]:
            fs = u.get("filas_sha256")
            rel = porsha[ent].get(fs) if fs else None           # localización por el sha FIJADO en el paquete, DENTRO del inventario de su entrega
            if rel is None:
                rech.append((u["unidad"], "FILAS_FUERA_DEL_INVENTARIO_DE_SU_ENTREGA"))
                continue
            chk = E.archivo(ent, rel, sha_fijado=fs)
            if not chk["conforme"]:
                rech.append((u["unidad"], chk["motivo"]))
                continue
            d = json.loads((T / ent / rel).read_bytes())
            cc = (d.get("cell_context") or [{}])[0]
            cr = (d.get("confrontation_result") or [{}])[0]
            ce = (d.get("capture_ceiling_result") or [{}])[0]
            lp = (d.get("lambda_pi_envelope") or [{}])[0]
            fc = (d.get("frontier_context") or [{}])[0]
            vals = {v.get("parameter_id"): v.get("value") for v in ((fc.get("structural_key_payload") or {}).get("values") or []) if isinstance(v, dict)}
            inv = [dict(r) for r in (d.get("inversion_result") or [])]          # rem108: filas COMPLETAS (valores requeridos incluidos)
            cg = [r for r in (d.get("convergence_result") or []) if str(r.get("quantity_id", "")).startswith("G:")]
            tid = fc.get("tau_domain_id") or ""
            U[u["unidad"]] = {"familia": u.get("familia"), "contrato": pq["contrato"], "clasificacion": u.get("clasificacion"), "numerico": u.get("numerico"),
                              "entrega": ent, "archivo": rel, "sha256": fs, "pais": cc.get("country_id"), "diseno": cc.get("design_v"), "j": cc.get("instrument_j"),
                              "bloque": cc.get("eta_w_block"), "cota": cc.get("bound_variant"), "capa": cc.get("layer"), "ext": cc.get("external_cell_id"),
                              "coord_cc": cc.get("coordination_scenario_id"), "coord_ce": ce.get("coordination_scenario_id"), "tau": fc.get("tau_domain_id"),
                              "C2": ce.get("C_2"), "C2_estado": ce.get("computation_status"), "tau_f_sup": ce.get("tau_f_at_sup"), "err": ce.get("numerical_error"),
                              "K1": cr.get("K_comp_1"), "G": cr.get("G"), "veredicto": cr.get("verdict"), "lam": lp.get("lambda_pi"), "thetaneg": lp.get("theta_W_negative"),
                              "vals": vals, "run": fc.get("run_id"), "tablas": sorted(k for k, v in d.items() if isinstance(v, list) and v),
                              "cell_id": cc.get("cell_id"), "frontera": fc.get("frontier_id"), "omega": cc.get("omega_id"), "inv": inv,
                              "set": tid.split(":")[1] if tid.count(":") == 2 else None, "tau_dom": (fc.get("structural_key_payload") or {}).get("tau_domain"),
                              "convG": [{k: r.get(k) for k in ("method_id", "status", "change_bound", "tolerance", "value_after", "evidence_ref")} for r in cg],
                              "run_cc": cc.get("run_id")}
    return U, aut, rech


CATS_INCON = ("cambio_de_signo_certificado", "inconclusa_por_testigos_en_tolerancia")
DME_GAI_S6 = 0.0          # contexto_s6.py: RunInputs(..., dme_gai=0.0); K1 = (Q + DME_gAI)/(λπ·g) (external.K1, EQ24)


def grilla(R):
    """Q por celda externa y cota desde la grilla AUTENTICADA (FIJADOS["grilla"]), con external.GridCell.Q del núcleo instalado (aritmética pura)."""
    sys.path.insert(0, str(R / "paso4/instalacion/src"))
    from paper2b import external as X
    raw = (R / FIJADOS["grilla"][0]).read_bytes()
    assert H(raw) == FIJADOS["grilla"][1], "GRILLA_DISTINTA"
    return {c.external_cell_id: c for c in X.read_grid(raw)}


def soportes_g(R):
    """Nodos de nivel 0 del soporte primario de gain_share por conjunto de soporte (D7 support_set.csv)."""
    out = {}
    for r in csv.DictReader((R / D7 / "support_set.csv").open(encoding="utf-8")):
        if r["parameter_id"] == "gain_share" and r["variant_id"] == "primary":
            out[r["support_set_id"]] = {"nodos": [float(x) for x in json.loads(r["level0_nodes"])], "lower": float(r["lower"]), "upper": float(r["upper"])}
    return out


def exp8_tabla(U, reg, sel, G, GS):
    """Tabla COMPLETA por afirmación inconclusa. Identidad descriptiva ΔG = ΔC2 − ΔK1 (niveles) y Δlog K1 = Δlog Q − Δlog λπ − Δlog g. Q sale de
    la grilla; g NO está en las filas aceptadas: se DERIVA de EQ24 (g = (Q+DME_gAI)/(K1·λπ)) y se contrasta con los nodos D7 de su conjunto.
    No se usa umbral de predominio ni se mezclan coordenadas de dos ω: los dos testigos son extremos distintos (sup/inf) de la misma afirmación."""
    test = defaultdict(dict)
    for r in sel["S1"]:
        test[r["afirmacion"]][r["reason"]] = r.get("cell_id")
    filas = []
    for c in sorted(k for k, v in reg.items() if v["categoria"] in CATS_INCON):
        ids = {"sup": test.get(c, {}).get("witness_sup"), "inf": test.get(c, {}).get("witness_inf")}
        f = {"afirmacion": c, "categoria": reg[c]["categoria"], "testigo_sup": ids["sup"], "testigo_inf": ids["inf"]}
        motivos, w = [], {}
        for lado in ("sup", "inf"):
            u = U.get(ids[lado]) if ids[lado] else None
            if ids[lado] is None:
                motivos.append("%s: sin testigo en cell_selection S1" % lado)
            elif u is None:
                motivos.append("%s: el testigo no está entre las 2276 unidades aceptadas" % lado)
            else:
                for k in ("G", "C2", "K1", "lam"):
                    if u[k] is None:
                        motivos.append("%s: %s nulo (%s; veredicto %s)" % (lado, k, u.get("C2_estado"), u.get("veredicto")))
                w[lado] = u
                cel = G.get(u["ext"])
                Q = cel.Q(u["cota"]) if cel is not None and u["cota"] in ("addback_completo", "sin_addback") else None
                g = (Q + DME_GAI_S6) / (u["K1"] * u["lam"]) if None not in (Q, u["K1"], u["lam"]) and u["K1"] > 0 and u["lam"] > 0 else None
                nod = (GS.get(u["set"]) or {}).get("nodos") or []
                gn = next((n for n in nod if g is not None and abs(g - n) <= 1e-9 * n), None)
                f.update({lado + "_unidad": ids[lado], "%s_ref" % lado: "%s/%s" % (u["entrega"], u["archivo"]), lado + "_filas_sha256": u["sha256"], lado + "_cell_id": u["cell_id"],
                          lado + "_pais": u["pais"], lado + "_diseno": u["diseno"], lado + "_j": u["j"], lado + "_cota": u["cota"], lado + "_capa": u["capa"],
                          lado + "_bloque": u["bloque"], lado + "_set": u["set"], lado + "_ext": u["ext"], lado + "_omega": u["omega"], lado + "_veredicto": u["veredicto"],
                          lado + "_G": u["G"], lado + "_C2": u["C2"], lado + "_K1": u["K1"], lado + "_lambda_pi": u["lam"], lado + "_theta_W_neg": u["thetaneg"],
                          lado + "_Q_grilla": Q, lado + "_g_derivada": g, lado + "_g_nodo_D7": gn})
        if not motivos and min(w["sup"]["K1"], w["inf"]["K1"], w["sup"]["lam"], w["inf"]["lam"]) <= 0:
            motivos.append("K1 o λπ no positivos")
        f["motivo_sin_descomposicion"] = "; ".join(motivos) or None
        if not motivos:
            s, i = w["sup"], w["inf"]
            dG, dC2, dK1 = s["G"] - i["G"], s["C2"] - i["C2"], s["K1"] - i["K1"]
            dlK, dlL = math.log(s["K1"] / i["K1"]), math.log(s["lam"] / i["lam"])
            Qs, Qi, gs, gi = f["sup_Q_grilla"], f["inf_Q_grilla"], f["sup_g_derivada"], f["inf_g_derivada"]
            dlQ = math.log(Qs / Qi) if Qs and Qi else None
            dlg = math.log(gs / gi) if gs and gi else None
            f.update({"dG": dG, "dC2": dC2, "dK1": dK1, "residual_identidad_G": dG - (dC2 - dK1), "aporte_C2_a_dG": dC2, "aporte_K1_a_dG": -dK1,
                      "dlogK1": dlK, "dlogQ": dlQ, "dlog_lambda": dlL, "dlog_g": dlg,
                      "residual_log_K1": None if None in (dlQ, dlg) else dlK - (dlQ - dlL - dlg),
                      "parte_log_Q": dlQ / dlK if dlK and dlQ is not None else None, "parte_log_lambda": -dlL / dlK if dlK else None,
                      "parte_log_g": -dlg / dlK if dlK and dlg is not None else None,
                      "misma_celda_externa": s["ext"] == i["ext"], "mismo_bloque": s["bloque"] == i["bloque"], "mismo_conjunto": s["set"] == i["set"],
                      "misma_cota": s["cota"] == i["cota"], "misma_capa": s["capa"] == i["capa"], "mismo_omega": s["omega"] == i["omega"],
                      "g_en_nodos_D7_ambos": f["sup_g_nodo_D7"] is not None and f["inf_g_nodo_D7"] is not None,
                      "termino_mayor_abs_niveles": "C2" if abs(dC2) > abs(dK1) else ("K1" if abs(dK1) > abs(dC2) else "empate"),
                      "termino_mayor_abs_log_K1": max((("Q", abs(dlQ or 0.0)), ("lambda_pi", abs(dlL)), ("g", abs(dlg or 0.0))), key=lambda z: z[1])[0]})
        filas.append(f)
    ok = [f for f in filas if f["motivo_sin_descomposicion"] is None]
    cnt = lambda pred: sum(1 for f in ok if pred(f))  # noqa: E731
    res = {"inconclusas": len(filas), "descompuestas": len(ok), "sin_descomposicion": len(filas) - len(ok),
           "C2_cambia": cnt(lambda f: f["dC2"] != 0), "lambda_cambia": cnt(lambda f: f["dlog_lambda"] != 0), "K1_cambia": cnt(lambda f: f["dK1"] != 0),
           "Q_cambia": cnt(lambda f: f["dlogQ"] not in (0, None)), "g_cambia": cnt(lambda f: f["dlog_g"] not in (0, None)),
           "misma_celda_externa": cnt(lambda f: f["misma_celda_externa"]), "mismo_bloque": cnt(lambda f: f["mismo_bloque"]), "mismo_omega": cnt(lambda f: f["mismo_omega"]),
           "g_en_nodos_D7_ambos": cnt(lambda f: f["g_en_nodos_D7_ambos"]),
           "max_abs_residual_identidad_G": max(abs(f["residual_identidad_G"]) for f in ok) if ok else None,
           "max_abs_residual_log_K1": max(abs(f["residual_log_K1"]) for f in ok if f["residual_log_K1"] is not None) if ok else None,
           "termino_mayor_abs_niveles": dict(Counter(f["termino_mayor_abs_niveles"] for f in ok)),
           "termino_mayor_abs_log_K1": dict(Counter(f["termino_mayor_abs_log_K1"] for f in ok)),
           "por_pais_j": {"%s|%s" % k: v for k, v in sorted(Counter((f["sup_pais"], f["sup_j"]) for f in ok).items())},
           "por_pais_j_termino_niveles": {"%s|%s|%s" % k: v for k, v in sorted(Counter((f["sup_pais"], f["sup_j"], f["termino_mayor_abs_niveles"]) for f in ok).items())},
           "lambda_no_nula_en_todas": all(f["parte_log_lambda"] not in (0, None) for f in ok if f["dlogK1"]),
           "rango_parte_log_lambda": [min(f["parte_log_lambda"] for f in ok if f["parte_log_lambda"] is not None), max(f["parte_log_lambda"] for f in ok if f["parte_log_lambda"] is not None)] if ok else None,
           "casos_sin_descomposicion": [{k: f.get(k) for k in ("afirmacion", "categoria", "testigo_sup", "testigo_inf", "motivo_sin_descomposicion", "sup_veredicto", "inf_veredicto",
                                                                "sup_C2", "inf_C2", "sup_K1", "inf_K1", "sup_lambda_pi", "inf_lambda_pi")} for f in filas if f["motivo_sin_descomposicion"]],
           "metodo": ("testigos sup/inf de cell_selection.json (S1) → unidades ACEPTADAS por inventario; ΔG = ΔC2 − ΔK1 en niveles (identidad del contrato G = C2 − K1); "
                      "K1 = (Q + DME_gAI)/(λπ·g) con DME_gAI = 0 en el contexto S6; Q = GridCell.Q(cota) de la grilla autenticada; g no figura en las filas y se DERIVA de la "
                      "identidad (por eso residual_log_K1 ≈ 0 por construcción); su contraste independiente es la pertenencia a los nodos D7 de gain_share del conjunto"),
           "lectura": ("contribución aritmética: los términos se presentan sin umbral; predominio descriptivo: término de mayor valor absoluto, solo como descripción; "
                       "efecto causal / ceteris paribus: NO probado (los testigos son ω distintos y cambian varios términos a la vez)")}
    return filas, res


ESQUEMA_CLAIM = {"ci": ("pais", "j", "disponibilidad", "diseno", "cota", "bloque", "capa"),      # claims.derive: CLM:{pid}:{kind}:ci:{c}:{j}:{avail}:...
                 "c": ("pais", "escenario", "diseno", "cota", "bloque", "capa"),                   # CLM:{pid}:{kind}:c:{c}:{scen}:...
                 "g": ("escenario", "diseno", "cota", "bloque", "capa")}                           # CLM:{pid}:{kind}:g:{scen}:...


def analizar_claim(cid, CL):
    """rem108 (P4-PROD4-ENSAMBLAJE): identificador → campos por el ESQUEMA AUTÉNTICO de claims.derive (familia ci/c/g en la 4.ª posición,
    que es el discriminador del propio esquema), con validación de dominios contra las constantes del núcleo y reconstrucción exacta del id."""
    p = cid.split(":")
    assert p[0] == "CLM" and p[3] in ESQUEMA_CLAIM, "CLAIM_FUERA_DE_ESQUEMA:" + cid
    sc = ESQUEMA_CLAIM[p[3]]
    assert len(p) == 4 + len(sc), "CLAIM_ANCHO_DISTINTO_DEL_ESQUEMA:" + cid
    d = dict(zip(sc, p[4:]), pid=p[1], kind=p[2], familia=p[3])
    assert d["diseno"] in CL.DESIGNS and d["cota"] in CL.BOUNDS and d["bloque"] in CL.BLOCKS and d["capa"] in CL.LAYERS, "CLAIM_DOMINIO:" + cid
    assert d.get("escenario", "conditional_full") in ("conditional_full", "conditional_none"), "CLAIM_ESCENARIO:" + cid
    rest = {"ci": [d.get("pais"), d.get("j"), d.get("disponibilidad")], "c": [d.get("pais"), d.get("escenario")], "g": [d.get("escenario")]}[p[3]]
    assert ":".join(["CLM", d["pid"], d["kind"], p[3]] + rest + [d["diseno"], d["cota"], d["bloque"], d["capa"]]) == cid, "CLAIM_NO_RECONSTRUYE:" + cid
    return d


def _nulo(v):
    return "null" if v is None else (json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else v)


def ensamblajes(R, U, reg, sel):
    """PROD4.1: tablas ensambladas SOLO desde valores almacenados (sin evaluar). rem108: T7 con TODAS las afirmaciones por esquema y su anexo
    de G con certificados; T8 con los VALORES requeridos por fila e identidad; admisibilidad con denominadores y corridas demostrables."""
    sys.path.insert(0, str(R / "paso4/instalacion/src"))
    from paper2b import claims as CL
    test = defaultdict(dict)
    for r in sel["S1"]:
        test[r["afirmacion"]][r["reason"]] = r.get("cell_id")
    por_celda = defaultdict(list)
    for r in sel["S1"]:
        por_celda[r.get("cell_id")].append(r["afirmacion"])
    anexo7, t7, cob = [], defaultdict(lambda: {"cats": Counter(), "Gsup": [], "Ginf": []}), Counter()
    for c in sorted(reg):
        d = analizar_claim(c, CL)
        cob[d["familia"]] += 1
        f = {"afirmacion": c, "categoria_original": reg[c]["categoria"], **{k: d.get(k) for k in ("pid", "kind", "familia", "pais", "j", "disponibilidad", "escenario", "diseno", "cota", "bloque", "capa")}}
        for lado in ("sup", "inf"):
            uid = test[c].get("witness_" + lado)
            u = U.get(uid)
            f["testigo_" + lado] = uid
            if u is None:
                f[lado + "_estado_evidencia"] = "testigo en S1 sin filas aceptadas"
                continue
            cg = (u["convG"] or [{}])[0]
            f.update({lado + "_estado_evidencia": "filas aceptadas", lado + "_G": u["G"], lado + "_C2": u["C2"], lado + "_K1": u["K1"], lado + "_veredicto": u["veredicto"],
                      lado + "_error_techo": u["err"], lado + "_certificado_G": cg.get("method_id"), lado + "_certificado_estado": cg.get("status"),
                      lado + "_certificado_cota_cambio": cg.get("change_bound"), lado + "_certificado_tolerancia": cg.get("tolerance"),
                      lado + "_ref": "%s/%s" % (u["entrega"], u["archivo"]), lado + "_filas_sha256": u["sha256"]})
        anexo7.append(f)
        k = (d.get("pais") or "global(%s)" % d["pid"], d["familia"], d["diseno"], d["cota"], d["capa"], d["bloque"])
        t7[k]["cats"][reg[c]["categoria"]] += 1
        for lado, lst in (("sup", "Gsup"), ("inf", "Ginf")):
            if f.get(lado + "_G") is not None:
                t7[k][lst].append(f[lado + "_G"])
    T7 = [{"pais_o_ambito": k[0], "familia": k[1], "diseno": k[2], "cota": k[3], "capa": k[4], "bloque": k[5], **dict(sorted(v["cats"].items())), "total": sum(v["cats"].values()),
           "G_sup_min": min(v["Gsup"]) if v["Gsup"] else None, "G_sup_max": max(v["Gsup"]) if v["Gsup"] else None,
           "G_inf_min": min(v["Ginf"]) if v["Ginf"] else None, "G_inf_max": max(v["Ginf"]) if v["Ginf"] else None} for k, v in sorted(t7.items())]
    ids7 = [f["afirmacion"] for f in anexo7]
    cobertura7 = {"fuente": len(reg), "anexo": len(anexo7), "unicas": len(set(ids7)), "omitidas": sorted(set(reg) - set(ids7)), "ajenas": sorted(set(ids7) - set(reg)),
                  "por_familia": dict(cob), "categorias": dict(Counter(f["categoria_original"] for f in anexo7)),
                  "testigos_con_filas": sum(1 for f in anexo7 for l in ("sup", "inf") if f.get(l + "_G") is not None),
                  "testigos_sin_filas": sum(1 for f in anexo7 for l in ("sup", "inf") if f.get(l + "_estado_evidencia") != "filas aceptadas")}
    filas8, grupos = [], {}
    for uid, x in sorted(U.items()):
        for i, r in enumerate(x["inv"]):
            canon_r = json.dumps(r, sort_keys=True, ensure_ascii=False)
            key = (r.get("cell_id"), r.get("inversion_id"), canon_r)
            if key in grupos:
                grupos[key]["unidades_fuente"].append(uid)
                continue
            fila = {"cell_id": r.get("cell_id"), "inversion_id": r.get("inversion_id"), "equation_id": r.get("equation_id"), "method_id": r.get("method_id"),
                    "result_status": r.get("result_status"), "computation_status": r.get("computation_status"), "reason_code": r.get("reason_code"),
                    "lambda_pi_required": r.get("lambda_pi_required"), "delta_y_required": r.get("delta_y_required"), "C_2_required": r.get("C_2_required"),
                    "external_factor_required": r.get("external_factor_required"), "phi_critical_partial": r.get("phi_critical_partial"),
                    "phi_critical_total": r.get("phi_critical_total"), "target_unit": r.get("target_unit"), "target_value": r.get("target_value"),
                    **{b: r.get(b) for b in ("admissibility_violated", "corner_binding", "kink_adjacent", "outside_support", "no_solution", "fixed_point_converged")},
                    "fin_por_unidad": r.get("_fin"), "estado_es_por_unidad": "_fin" in r, "pais": x["pais"], "conjunto": x["set"], "familia_unidad": x["familia"],
                    "unidad_primera": uid, "ref": "%s/%s" % (x["entrega"], x["archivo"]), "filas_sha256": x["sha256"], "fila_en_unidad": i,
                    "afirmaciones_testigo": len(por_celda.get(r.get("cell_id"), [])), "unidades_fuente": [uid]}
            grupos[key] = fila
            filas8.append(fila)
    por_ci = defaultdict(set)
    for f in filas8:
        por_ci[(f["cell_id"], f["inversion_id"])].add(json.dumps({k: f[k] for k in ("lambda_pi_required", "delta_y_required", "C_2_required", "result_status")}, sort_keys=True))
    t8 = defaultdict(lambda: {"filas": 0, "valores": []})
    for f in filas8:
        k = (f["pais"], f["inversion_id"], f["result_status"])
        t8[k]["filas"] += 1
        v = f["lambda_pi_required"] if f["lambda_pi_required"] is not None else f["delta_y_required"]
        if isinstance(v, (int, float)) and math.isfinite(v):
            t8[k]["valores"].append(v)
        for b in ("admissibility_violated", "corner_binding", "kink_adjacent", "outside_support", "no_solution"):
            t8[k][b] = t8[k].get(b, 0) + bool(f[b])
    T8 = [{"pais": k[0], "inversion_id": k[1], "result_status": k[2], "filas_unicas": v["filas"], "con_valor_finito": len(v["valores"]),
           "valor_min": min(v["valores"]) if v["valores"] else None, "valor_max": max(v["valores"]) if v["valores"] else None,
           **{b: v.get(b, 0) for b in ("admissibility_violated", "corner_binding", "kink_adjacent", "outside_support", "no_solution")}}
          for k, v in sorted(t8.items(), key=lambda z: tuple(str(a) for a in z[0]))]
    ctrl = [f for f in filas8 if f["cell_id"] == "CEL:6798a3df3dc6adc69d472a186a1e47ef773b245c9073" and f["inversion_id"] in ("lambda_required", "gain_required")]
    cobertura8 = {"filas_fuente": sum(len(x["inv"]) for x in U.values()), "unidades": len(U), "filas_unicas": len(filas8), "duplicados_identicos_fusionados": sum(len(f["unidades_fuente"]) - 1 for f in filas8),
                  "celdas": len({f["cell_id"] for f in filas8}), "cell_inversion_con_valores_distintos": sum(1 for v in por_ci.values() if len(v) > 1),
                  "por_inversion": dict(Counter(f["inversion_id"] for f in filas8)), "estado_por_unidad_con_fin": sum(1 for f in filas8 if f["estado_es_por_unidad"]),
                  "control_revisor": [{k: f[k] for k in ("inversion_id", "lambda_pi_required", "delta_y_required", "result_status")} for f in ctrl],
                  "regla_de_deduplicacion": "solo filas IDÉNTICAS byte a byte (JSON canónico) de la misma celda e inversión repetidas en varias unidades; se conservan todas las unidades fuente; valores distintos nunca se fusionan"}
    sm = list(csv.DictReader((R / D7 / "scenario_map.csv").open(encoding="utf-8")))
    paises = defaultdict(set)
    for x in sm:
        if x["country_id"]:
            paises[x["support_set_id"]].add(x["country_id"])
    adm = defaultdict(dict)
    for a in csv.DictReader((R / D7 / "d7_admissibility_report.csv").open(encoding="utf-8")):
        fam = a["constraint_id"].split(".")[1]
        adm[a["support_set_id"]][fam] = (int(a["evaluated_count"]), int(a["accepted_count"]), int(a["rejected_count"]), a["layer_id"])
    corridas = defaultdict(lambda: {"conjuntos": Counter(), "unidades": 0, "celdas": set(), "familias": Counter()})
    for x in U.values():
        rid = x["run"] or x["run_cc"]
        corridas[rid]["unidades"] += 1
        corridas[rid]["conjuntos"][x["set"]] += 1
        corridas[rid]["celdas"].add(x["cell_id"])
        corridas[rid]["familias"][x["familia"]] += 1
    run_por_set = defaultdict(set)
    for rid, v in corridas.items():
        for s in v["conjuntos"]:
            run_por_set[s].add(rid)
    A8 = []
    for ss, d in sorted(adm.items()):
        rech = sum(v[2] for v in d.values())
        npais = len(paises.get(ss, ()))
        A8.append({"support_set_id": ss, "capa": d["QPOT"][3], "paises": ",".join(sorted(paises.get(ss, ()))), "n_paises": npais,
                   "run_ids_de_unidades_aceptadas": ",".join(sorted(r for r in run_por_set.get(ss, ()) if r)) or None,
                   "n_declared_por_conjunto": d["QPOT"][0], "n_admissible_por_conjunto": d["QPOT"][0] if rech == 0 else None,
                   "n_violates_q_pot": d["QPOT"][2], "n_violates_eta_H": d["ETAH"][2], "n_violates_shares": d["SPI"][2] + d["STMARG"][2],
                   "evaluadas_SPI_por_conjunto_pais": d["SPI"][0], "razon_SPI_QPOT": d["SPI"][0] / d["QPOT"][0] if d["QPOT"][0] else None,
                   "razon_igual_n_paises": (d["SPI"][0] == d["QPOT"][0] * npais) if npais else None, "share_discarded": 0.0 if rech == 0 else None,
                   "otras_restricciones_rechazos": {k: v[2] for k, v in d.items() if k not in ("QPOT", "ETAH", "SPI", "STMARG")},
                   "nota": "QPOT/ETAH cuentan combinaciones POR CONJUNTO; SPI/STMARG POR CONJUNTO-PAÍS (razón = número de países); D7 es previo a la corrida: run_id solo se enlaza desde las unidades aceptadas"})
    AC = [{"run_id": rid, "unidades": v["unidades"], "celdas": len(v["celdas"]), "conjuntos": dict(v["conjuntos"]), "familias": dict(v["familias"]),
           "gates_D7": "G01–G14 (20 filas; 18 pass, 2 limitation), por alcance de datos, no por corrida", "level": None, "n_cells_affected": None,
           "nota": "run_id demostrable desde cell_context/frontier_context; level y n_cells_affected no los produce run.py ni constan en las 14 entregas de unidades"} for rid, v in sorted(corridas.items(), key=lambda z: str(z[0]))]
    return {"T7": T7, "T7_anexo": anexo7, "T8": T8, "T8_anexo": filas8, "admissibility_report": A8, "auditoria_por_corrida": AC,
            "_cobertura": {"T7": cobertura7, "T8": cobertura8, "corridas": len(AC), "razon_SPI_QPOT_explicada": all(a["razon_igual_n_paises"] for a in A8 if a["razon_igual_n_paises"] is not None)}}


def escenarios_d7(R):
    """Unidades REALES de ejecución de las clases de coordinación/ablación (scenario_map + support_sets de D7), sin duplicar niveles."""
    sm = list(csv.DictReader((R / D7 / "scenario_map.csv").open(encoding="utf-8")))
    ss = {r["support_set_id"]: r for r in csv.DictReader((R / D7 / "support_sets.csv").open(encoding="utf-8"))}
    out = {}
    for cls, tr in (("ABL-COV", "coverage_half: φ/2"), ("ABL-ENF", "enforcement_half: η_f/2"), ("COORD-HALF", "coordination_half: η_f/2 y φ/2")):
        rr = [x for x in sm if x["coordination_scenario_id"] == cls]
        sets = sorted({x["support_set_id"] for x in rr})
        out[cls] = {"transformacion": tr, "filas_scenario_map": len(rr), "filas_capa": sum(1 for x in rr if not x["country_id"]),
                    "filas_pais_menu": sum(1 for x in rr if x["country_id"]), "conjuntos": len(sets),
                    "por_conjunto": [{"support_set_id": s, "padre_support_set": ss.get(s, {}).get("parent_support_set_id"), "ambito": s.split("-")[0],
                                      "escenario_capa": [x["scenario_id"] for x in rr if x["support_set_id"] == s and not x["country_id"]],
                                      "padre_escenario": sorted({x["parent_scenario_id"] for x in rr if x["support_set_id"] == s and not x["country_id"]}),
                                      "pais_menu": sorted("%s:%s:%s" % (x["country_id"], x["instrument"], x["availability_case_id"]) for x in rr if x["support_set_id"] == s and x["country_id"])}
                                     for s in sets],
                    "paises": sorted({x["country_id"] for x in rr if x["country_id"]}), "ambitos": sorted({s.split("-")[0] for s in sets})}
    return out


SIMBOLO_D7 = {"a": ("a", "directo"), "θ": ("u_theta", "θ = 1 + u_θ(a−1) (model.derive)"), "ρ": ("rho", "directo"), "β̃": ("beta_tilde", "directo"),
              "δ̃": ("z_cost", "δ̃ = z_cost^(1−θ) (model.derive)"), "κ̃_0": ("kappa_tilde", "directo"), "η_d": ("eta_d", "directo"), "η_f": ("eta_f", "directo"), "φ": ("phi", "directo")}


def tablas_diseno(R):
    """T1 (§6.2 × D7: soporte, naturaleza y estado de los nueve números) y T2 (§6.3: ocho ecuaciones de observación con su estado), y la
    evidencia de C8 (filas b/c de §6.3 y parámetros s_AI/s_FN de D7). Extracción literal + unión por identificador; sin evaluar."""
    txt = (R / FIJADOS["diseno"][0]).read_text(encoding="utf-8").splitlines()
    i62 = next(i for i, x in enumerate(txt) if x.startswith("## 6.2 "))
    i63 = next(i for i, x in enumerate(txt) if x.startswith("## 6.3 "))
    i64 = next(i for i, x in enumerate(txt) if i > i63 and x.startswith("## "))
    limpia = lambda s: re.sub(r"[*`]", "", s).strip()  # noqa: E731
    reg = {r["parameter_id"]: r for r in csv.DictReader((R / D7 / "parameter_registry.csv").open(encoding="utf-8"))}
    ss = {r["support_set_id"]: r for r in csv.DictReader((R / D7 / "support_sets.csv").open(encoding="utf-8"))}
    sup = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader((R / D7 / "support_set.csv").open(encoding="utf-8")):
        if r["variant_id"] == "primary" and ss.get(r["support_set_id"], {}).get("kind") == "base":
            sup[r["parameter_id"]][(r["lower"], r["upper"], r["level0_nodes"], r["central"])].append(r["support_set_id"])
    T1 = []
    for x in txt[i62:i63]:
        m = re.match(r"\|\s*(\d)\s*\|\s*`([^`]+)`\s*\|([^|]*)\|([^|]*)\|", x)
        if m:
            pid, rel = SIMBOLO_D7[m.group(2)]
            g = reg.get(pid, {})
            T1.append({"n": int(m.group(1)), "parametro": m.group(2), "gobierna": limpia(m.group(3)), "naturaleza_diseno": limpia(m.group(4)), "parametro_D7": pid, "relacion": rel,
                       "rol_D7": g.get("role"), "activo_primario_D7": g.get("active_primary"), "motivo_inactivo_D7": g.get("inactive_reason") or None,
                       "soportes_base_D7": json.dumps([{"lower": k[0], "upper": k[1], "nodos": k[2], "central": k[3] or None, "conjuntos": len(v)} for k, v in sorted(sup.get(pid, {}).items())], ensure_ascii=False)})
    T2 = []
    for x in txt[i63:i64]:
        m = re.match(r"\|\s*\*\*([a-h])\*\*\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", x)
        if m:
            T2.append({"fila": m.group(1), "objeto": limpia(m.group(2)), "ecuacion": limpia(m.group(3)), "estado_asignado": limpia(m.group(4))})
    c8 = {"filas_b_c": [r for r in T2 if r["fila"] in ("b", "c")], "D7_parametros": {p: {k: reg.get(p, {}).get(k) for k in ("role", "active_primary", "inactive_reason")} for p in ("s_AI", "s_FN", "external_factor")},
          "D7_source_evidence_filas": sum(1 for r in csv.DictReader((R / D7 / "source_evidence.csv").open(encoding="utf-8")) if re.search(r"s_AI|s_FN", json.dumps(r)))}
    return T1, T2, c8


def main(raiz, revisor, area, intento):
    R, W = Path(raiz), Path(revisor)
    OUT = Path(area) / "conciliacion/intentos" / intento
    OUT.mkdir(parents=True, exist_ok=False)
    salida, fichas_sal = str(OUT / "MATRIZ_CONCILIACION_GLOBAL"), str(OUT / "FICHAS_PENDIENTES")
    VS = Path(area) / "validaciones"
    sint = {"E1235_i1": json.loads((VS / "resultados_E1235_i1.json").read_bytes()), "E1_i2": json.loads((VS / "resultados_E1_i2.json").read_bytes())}
    sint_sha = {k: hf(VS / f) for k, f in (("E1235_i1", "resultados_E1235_i1.json"), ("E1_i2", "resultados_E1_i2.json"), ("prerregistro_E1235", "prerregistro_E1235.json"),
                                          ("prerregistro_E1_i2", "prerregistro_E1_i2.json"))}
    T = R / "tmp"
    E = Entregas(T)
    F = {k: fuente(R, *v) for k, v in FIJADOS.items()}
    F["ledger_rem105"] = {"archivo": str(W / LEDGER[0]), "sha256": hf(W / LEDGER[0]), "fijado": LEDGER[1], "conforme": hf(W / LEDGER[0]) == LEDGER[1]}
    F["cobertura_r1"] = E.archivo(COB[0], COB[2], inventario_fijado=COB[1])
    F["registro_v4"] = E.archivo(REG[0], REG[2], sha_fijado=REG[3], inventario_fijado=REG[1])
    F["cell_selection"] = E.archivo(SEL[0], SEL[2], inventario_fijado=SEL[1])
    F["d7"] = {p.name: hf(p) for p in sorted((R / D7).iterdir())}
    U, aut_paq, rech = unidades(R, E)
    F["paquetes"] = {"conformes": sum(a["conforme"] for a in aut_paq), "total": len(aut_paq), "no_conformes": [a for a in aut_paq if not a["conforme"]]}
    cob = json.loads((T / COB[0] / COB[2]).read_bytes())
    citas = []
    for t in cob["tareas"]:
        c = (t.get("referencia") or {}).get("cita")
        if c:
            citas.append(dict(E.archivo(c["entrega"], c["archivo"], sha_fijado=c["sha256"], inventario_fijado=c["inventario_sha256"]), tarea=t["tarea"]))
    reg = json.loads((T / REG[0] / REG[2]).read_bytes())["afirmaciones"]
    cats = Counter(v["categoria"] for v in reg.values())
    sel = json.loads((T / SEL[0] / SEL[2]).read_bytes())
    led = json.loads((W / LEDGER[0]).read_bytes())
    lista = json.loads((R / FIJADOS["lista_PROD"][0]).read_bytes())
    # ---------- contrastes derivados de resultados aceptados ----------
    c2 = {}
    for uid, x in U.items():
        m = re.fullmatch(r"C2[:-]([GN])[:-](df|d|f)[:-](sup|inf)", uid)
        if m:
            c2[m.groups()] = {"C_2": x["C2"], "estado": x["C2_estado"], "tau_f_sup": x["tau_f_sup"], "err": x["err"], "unidad": uid, "archivo": x["archivo"], "entrega": x["entrega"], "sha256": x["sha256"]}
    gn = {"%s:%s" % (j, s): {"G": c2.get(("G", j, s), {}).get("C_2"), "N": c2.get(("N", j, s), {}).get("C_2")} for j in ("d", "f", "df") for s in ("sup", "inf")}
    for v in gn.values():
        v["dif"] = None if None in (v["G"], v["N"]) else v["G"] - v["N"]
    jj = {"%s:%s" % (dz, s): {j: c2.get((dz, j, s), {}).get("C_2") for j in ("d", "f", "df")} for dz in ("G", "N") for s in ("sup", "inf")}
    num = {k: x for k, x in U.items() if x["numerico"] and x["C2"] is not None}

    def grupos(excluir):
        g = defaultdict(list)
        for k, x in num.items():
            vv = {a: b for a, b in x["vals"].items() if a != excluir}
            clave = tuple(None if c == excluir else x[c] for c in ("pais", "diseno", "j", "bloque", "cota", "capa", "ext")) + (json.dumps(vv, sort_keys=True),) + \
                (x["tau"] if excluir not in ("j", "diseno") else None,)
            g[clave].append(k)
        return {c: v for c, v in g.items() if len(v) > 1}

    def contraste(excluir, campo):
        out = []
        for c, ks in grupos(excluir).items():
            niveles = {}
            for k in ks:
                lv = U[k]["vals"].get("eta_f") if campo == "eta_f" else U[k][campo]
                niveles.setdefault(lv, k)
            if len(niveles) > 1:
                out.append({"clave": c[:7], "niveles": {str(lv): {"unidad": k, "C_2": U[k]["C2"], "G": U[k]["G"], "veredicto": U[k]["veredicto"]} for lv, k in sorted(niveles.items(), key=lambda z: str(z[0]))}})
        return out
    cp_eta = contraste("eta_f", "eta_f")
    cp_gn = contraste("diseno", "diseno")
    cp_j = contraste("j", "j")

    def resumen_cp(cp):
        dif = [abs(v1["C_2"] - v0["C_2"]) for x in cp for v0, v1 in [tuple(list(x["niveles"].values())[:2])]]
        return {"pares": len(cp), "C2_distinto": sum(d > 0 for d in dif), "C2_igual": sum(d == 0 for d in dif), "max_abs_dif_C2": max(dif) if dif else None,
                "ejemplos": cp[:3]}
    contr = {"C2_G_vs_N": gn, "C2_por_instrumento": jj, "C2_fuentes": {"%s:%s:%s" % k: v for k, v in sorted(c2.items())},
             "eta_f_ceteris_paribus": resumen_cp(cp_eta), "G_vs_N_ceteris_paribus": resumen_cp(cp_gn), "instrumento_ceteris_paribus": resumen_cp(cp_j)}
    # ---------- Exp8 (rem107): tabla completa por afirmación inconclusa; sin umbral ni atribución causal ----------
    filas8, exp8 = exp8_tabla(U, reg, sel, grilla(R), soportes_g(R))
    incon = [f["afirmacion"] for f in filas8]
    ej = next((f for f in filas8 if f["afirmacion"] == "CLM:PREG-COL-E2-2023:primary:c:COL:conditional_full:G:addback_completo:macro:buffer_destacado"), None)
    exp8["ejemplo_del_revisor"] = {k: ej.get(k) for k in ("dC2", "dK1", "dG", "sup_lambda_pi", "inf_lambda_pi", "parte_log_lambda", "parte_log_Q", "parte_log_g", "misma_celda_externa")} if ej else None
    campos8 = sorted({k for f in filas8 for k in f}, key=lambda k: (k not in ("afirmacion", "categoria", "motivo_sin_descomposicion"), k))
    with (OUT / "EXP8_TABLA.csv").open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=campos8)
        wr.writeheader()
        for f in filas8:
            wr.writerow({k: f.get(k) for k in campos8})
    (OUT / "EXP8_TABLA.json").write_text(json.dumps({"kind": "exp8-tabla-rem107", "resumen": exp8, "filas": filas8}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    ens = ensamblajes(R, U, reg, sel)
    ens["T1"], ens["T2"], c8ev = tablas_diseno(R)
    cob_ens = ens.pop("_cobertura")
    (OUT / "ensamblajes").mkdir()
    for nom, tab in ens.items():                     # rem108: null se escribe «null» (nunca vacío ni cero); listas/dicts en JSON canónico
        cols = sorted({k for r in tab for k in r}, key=lambda k: (k in ("otras_restricciones_rechazos", "nota", "unidades_fuente", "fin_por_unidad"), k))
        with (OUT / "ensamblajes" / (nom + ".csv")).open("w", encoding="utf-8", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=cols)
            wr.writeheader()
            for r in tab:
                wr.writerow({k: _nulo(r.get(k)) for k in cols})
        if nom.endswith("_anexo"):
            (OUT / "ensamblajes" / (nom + ".json")).write_text(json.dumps({"kind": nom + "-rem108", "filas": tab}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    (OUT / "ensamblajes/COBERTURA.json").write_text(json.dumps(cob_ens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    esc = escenarios_d7(R)
    fronteras = Counter((x["pais"], x["diseno"], x["j"]) for x in {x["frontera"]: x for x in U.values() if x["frontera"] and x["numerico"]}.values())
    # ---------- Exp9 (iii) y ablaciones preespecificadas en D7 ----------
    sm = list(csv.DictReader((R / D7 / "scenario_map.csv").open(encoding="utf-8")))
    coord = Counter((x["coordination_scenario_id"], x["transformation_id"], x["layer_id"]) for x in sm if x["coordination_scenario_id"])
    coord_u = Counter((x["coord_cc"], x["coord_ce"]) for x in U.values())
    # ---------- Exp0: auditorías ensambladas desde D7 y registros ----------
    gates = list(csv.DictReader((R / D7 / "d7_gate_report.csv").open(encoding="utf-8")))
    adm = list(csv.DictReader((R / D7 / "d7_admissibility_report.csv").open(encoding="utf-8")))
    runs = sorted({x["run"] for x in U.values() if x["run"]})
    audit_ins = [{"run_id": None, "gate_id": g["gate_id"], "level": None, "n_cells_affected": None, "decision": g["status"], "note": g["reason_code"],
                  "fuente": "d7_gate_report.csv", "requerida": g["required"], "bloqueante": g["blocking"]} for g in gates]
    adm_agg = defaultdict(lambda: {"evaluadas": 0, "aceptadas": 0, "rechazadas": 0, "por_restriccion": Counter()})
    for a in adm:
        k = (a["support_set_id"], a["layer_id"])
        adm_agg[k]["evaluadas"] += int(a["evaluated_count"] or 0)
        adm_agg[k]["aceptadas"] += int(a["accepted_count"] or 0)
        adm_agg[k]["rechazadas"] += int(a["rejected_count"] or 0)
        adm_agg[k]["por_restriccion"][a["constraint_id"]] += int(a["rejected_count"] or 0)
    exp0 = {"compuertas_d7": len(gates), "estados": dict(Counter(g["status"] for g in gates)), "runs_de_las_unidades": len(runs), "filas_input_audit_ensamblables": len(audit_ins),
            "campos_no_reconstruibles": ["run_id por compuerta (las compuertas D7 son de datos, no de una corrida)", "level (hard_fail/robustness_only: sin mapeo sellado desde required/blocking)",
                                         "n_cells_affected (D7 no cuenta celdas por compuerta)"],
            "admisibilidad_por_conjunto": len(adm_agg), "restricciones": sorted({a["constraint_id"] for a in adm})[:20]}
    # ---------- validaciones del Paquete A (antecedente, no autoridad S6) ----------
    ser = json.loads((R / FIJADOS["solver_error_report"][0]).read_bytes())
    sub = Counter(r.get("subcase_id") for r in ser["rows"])
    paqA = {"suite": ser.get("suite_id"), "run_id": ser.get("run_id"), "resumen": ser.get("summary"), "subcasos": {k: v for k, v in sub.items() if k and re.match(r"S1-E(1|13|15|4|02|03)-|S2-E18", k)},
            "nota": "identidades exactas de fórmulas de src/paper2 (Paquete A) con fixtures sintéticos; src/paper2b (núcleo S6) no importa paper2"}
    # ---------- 16 afirmaciones ----------
    por_u = {u: t for t in led["tasks"] for u in t["units"]}
    claims = sorted({u["afirmacion"] for u in lista["unidades"]})
    rob = sorted(k for k, v in reg.items() if v["categoria"] == "robusta_infactible_certificada")
    E_UN = "unidades detalladas (lima1018; filas por sha fijado y PERTENENCIA al inventario de su entrega)"
    sha_led = F["ledger_rem105"]["sha256"]
    fsel = F["cell_selection"]["sha256"]
    O = []

    def ob(i, tipo, linea, texto, comps, retirado=False):
        orden = ["calculo_nuevo_necesario", "decision_cientifica_pendiente", "evidencia_existente_pendiente_de_extraccion_o_ensamblaje", "limite_o_NA_admitido", "producto_conciliado"]
        cl = [c["clase"] for c in comps]
        est = "retirado_M3" if retirado else min(cl, key=orden.index)
        O.append({"id": i, "tipo": tipo, "linea_diseno": linea, "texto": texto, "componentes": comps, "estado": est})

    FE = "F-ELAST"
    ob("C1", "afirmacion", 941, "Dos bases con interacción: ε_ij con términos cruzados no nulos (A1; Exp.1)", [
        comp("ε_ij y términos cruzados", "calculo_nuevo_necesario", "matriz ε_ij por frontera con ε_fd, ε_df ≠ 0", [ev("src/paper2b/run.py", None, "frontier_result (eps_fd, eps_ff, regime, s_P), l. ~603", "por frontera")],
             "run.py produce frontier_result, pero el contrato de exportación (contrato_paquete TABLAS_V2/HIJAS) no lo incluye: no hay valores aceptados que extraer", FE)])
    S1 = sint["E1235_i1"]
    e1ok = sint["E1_i2"]["conforme"] and all(f["B_f0_identicos_exactos"] and f["B_f0_positivo"] for f in S1["E1"]["filas"])
    e2ok, e3ok, e5ok = S1["E2"]["conforme"], S1["E3"]["conforme"], S1["E5"]["conforme"]
    VAL = "validaciones/resultados_E1235_i1.json"
    nota_e1 = ("validación SINTÉTICA de la implementación sobre el núcleo vigente (no evidencia empírica): B_f(0) idéntico bit a bit en los cuatro η_f, G y N, dos estados; "
               "τ̃_f(0)=0 y τ̃_f'(0)=1 exactos; derivada unilateral: i1 NO conforme con su tolerancia prerregistrada (Richardson 1e-9; dispersión 1.2e-8–2.8e-7 por el resto O(h²)∝η_f³), "
               "i2 conforme (Romberg 3 niveles ≤1e-8 y desacuerdo O(h)); SALVEDAD: el método de i2 se fijó tras observar i1")
    ob("C2", "afirmacion", 942, "Condición de esquina en τ_f independiente de η_f (A2; §19.2 E1)", [
        comp("E1: B_f(0) y dR/dτ_f|0 idénticos para η_f ∈ {0.8,1.2,4,8}", "producto_conciliado" if e1ok else "calculo_nuevo_necesario", "§19.2 E1 completo",
             [ev(VAL, sint_sha["E1235_i1"], "E1 (B_f0 exacto; i1 derivada no conforme)", "sintético, prerregistro %s" % sint_sha["prerregistro_E1235"][:12]),
              ev("validaciones/resultados_E1_i2.json", sint_sha["E1_i2"], "E1 i2 (Romberg)", "sintético, prerregistro %s" % sint_sha["prerregistro_E1_i2"][:12])],
             nota_e1, None if e1ok else "F-E1")])
    gn_dif = [v["dif"] for v in gn.values() if v["dif"] is not None]
    ob("C3", "afirmacion", 943, "G y N generan fronteras distintas: supremos y geometría de regímenes (A2; Exp.2; E4)", [
        comp("supremos C_2 de G frente a N", "producto_conciliado" if len(gn_dif) == 6 else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
             "C_2^G frente a C_2^N por instrumento y sentido (12 techos C2) y pares ceteris paribus de celdas",
             [ev(v["archivo"], v["sha256"], "capture_ceiling_result.C_2 de %s" % v["unidad"], "global por diseño/instrumento") for v in c2.values()],
             "contraste hecho; OBSERVACIÓN para el autor/revisor: difieren en d y df y son IDÉNTICOS en j=f (sup e inf); pares de celdas G/N: %s. Diferencias G−N: %s" % (
                 {k: contr["G_vs_N_ceteris_paribus"][k] for k in ("pares", "C2_distinto", "C2_igual")}, {k: v["dif"] for k, v in gn.items()})),
        comp("geometría de regímenes", "calculo_nuevo_necesario", "la geometría de regímenes no coincide", [ev("unidades r1_components", None, "contornos sin etiqueta de régimen", "por celda")],
             "los contornos r1 existen (871 unidades) pero sin régimen; el régimen está en frontier_result, no exportado", FE)])
    ob("C4", "afirmacion", 944, "s_P ≠ 1−φ salvo en el límite (A1; §19.2 E3; Exp.3; T5)", [
        comp("s_P(τ_f, φ) exacta por τ_f en producción", "calculo_nuevo_necesario", "tabla s_P exacta contra 1−φ por τ_f", [ev("src/paper2b/run.py", None, "frontier_result.s_P", "por frontera")],
             "no exportado en el contrato del paquete", FE),
        comp("E3: diferencia a τ_f finito y convergencia τ_f→0", "producto_conciliado" if e3ok else "calculo_nuevo_necesario", "§19.2 E3 completo",
             [ev(VAL, sint_sha["E1235_i1"], "E3 (φ∈{0.25,0.5,0.75}; τ_f finitos y sucesión 2^-1..2^-20; referencia decimal)", "sintético")],
             "validación sintética de model.provider_share: s_P≠1−φ a τ_f finito y diferencia monótona → 0 (~ −φ(1−φ)τ_f/2); no cubre φ∈{0,1} ni la tabla de producción s_P(τ_f) por frontera (F-ELAST)",
             None if e3ok else "F-E3")])
    e2 = S1["E2"]
    ob("C5", "afirmacion", 945, "Ampliar la base con adopción no viable reduce la captura relativa (A2; §19.2 E2)", [
        comp("E2: ΔCS<0; masa 23.93% frente a B_pot 8.71%, neto −0.86%", "producto_conciliado" if e2ok else "calculo_nuevo_necesario", "§19.2 E2",
             [ev(VAL, sint_sha["E1235_i1"], "E2 (entradas originales del ledger: a=1.5, z_m=0.5, ρ=0, κ_0=0.6, γ=1)", "sintético"),
              ev(FIJADOS["ledger_lambda"][0], F["ledger_lambda"]["sha256"], "§1.2 vector de diagnóstico y formas cerradas m_-, b_-", "ejemplo original")],
             "exactos %s; presentación recalculada %s frente a la publicada %s (tolerancia de redondeo 0.005 pp); ΔCS<0 en G y N" % (
                 {k: round(v, 12) for k, v in e2["exactos"].items()}, e2["presentacion_recalculada_pct"], e2["presentacion_publicada"]), None if e2ok else "F-E2")])
    ob("C6", "afirmacion", 946, "La confrontación con el requerimiento externo es clasificable (B; Exp.5)", [
        comp("clasificación §17.1 de las afirmaciones", "producto_conciliado", "veredicto por afirmación con ε_econ = 0.01",
             [ev(REG[0] + "/" + REG[2], F["registro_v4"]["sha256"], "afirmaciones[*].categoria", "1728 afirmaciones", str(dict(cats)))],
             "las inconclusas son un resultado de la clasificación (§17.1), no un hueco; su eslabón se trata en Exp8")])
    lam_cnt = Counter((x["pais"], x["bloque"], x["thetaneg"]) for x in U.values() if x["lam"] is not None)
    ob("C7", "afirmacion", 947, "λ_π descompuesto y acotable condicionalmente (B; Exp.4; T6)", [
        comp("descomposición s_Π/(1−q_pot) con componentes de procedencia declarada", "producto_conciliado", "cada fila λπ con s̄_L, q_pot, s_T^marg, η_H, η_w, θ_W",
             [ev(E_UN, None, "lambda_pi_envelope (2276 filas)", "por celda", "componentes presentes en todas")]),
        comp("envolvente sup/inf sobre Ω por país y bloque, con y sin vértices θ_W<0", "calculo_nuevo_necesario", "§13 Exp.4 / T6",
             [ev(E_UN, None, "lambda_pi_envelope.theta_W_negative", "por celda", "una fila por celda: %d combinaciones país/bloque/θ" % len(lam_cnt)),
              ev(FIJADOS["ledger_lambda"][0], F["ledger_lambda"]["sha256"], "ledger del módulo λπ (fase 3)", "protocolo")],
             "las unidades dan λπ en el vértice de cada celda, no el sup/inf sobre Ω con y sin θ_W<0", "F-LAMBDA")])
    ob("C8", "afirmacion", 948, "Nivel puntual de la base externa no identificado (provisional; §12.0 Gate 0)", [
        comp("veredicto del gate del plan de datos sobre las filas (b)/(c)", "producto_conciliado" if c8ev["D7_source_evidence_filas"] == 0 and all(
                 c8ev["D7_parametros"][p]["inactive_reason"] == "NOT_IDENTIFIED_M3_OR_EXTENSION" for p in ("s_AI", "s_FN")) else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
             "§4 l.954: si el plan de datos encuentra una fuente que cierre (b) o (c), C8 se retira; si confirma que no la hay, C8 pasa a resultado declarado",
             [ev(PLAN_DATOS[0], F["plan_datos"]["sha256"], "§10 «C8 — Confirmado para el universo de fuentes públicas reproducibles disponible al 2026-07-26»; base: la línea "
                 "«servicios de IA» no existe en BPM6, EBOPS ni CPC; retiro ante cualquier fuente pública reproducible que identifique s_AI y s_FN para los cuatro países; §15.1 y compuerta D-0", "plan de datos congelado"),
              ev(FREEZE[0], F["freeze"]["sha256"], "documents: PLAN_BASE_DE_DATOS_v4_1_33.md con sha256 %s" % PLAN_DATOS[1], "congelamiento S6 2026-10-18"),
              ev(D7 + "/parameter_registry.csv", F["d7"].get("parameter_registry.csv"), "s_AI, s_FN, external_factor", "D7", json.dumps(c8ev["D7_parametros"], ensure_ascii=False)),
              ev(D7 + "/source_evidence.csv", F["d7"].get("source_evidence.csv"), "filas para s_AI/s_FN: %d" % c8ev["D7_source_evidence_filas"], "D7"),
              ev(FIJADOS["diseno"][0], F["diseno"]["sha256"], "§6.3 filas b y c", "diseño", json.dumps(c8ev["filas_b_c"], ensure_ascii=False))],
             "RESULTADO DECLARADO CON ALCANCE: el gate del plan de datos (PLAN_BASE_DE_DATOS v4.1.33 §10, congelado en S6) confirma C8 para las fuentes públicas reproducibles disponibles al "
             "2026-07-26, con regla de retiro explícita; D7 (insumos usados) es coherente: s_AI/s_FN inactivos NOT_IDENTIFIED_M3_OR_EXTENSION y sin evidencia. NO se afirma que no exista evidencia "
             "admisible en general ni después de esa fecha")])
    ecp = contr["eta_f_ceteris_paribus"]
    ob("C9", "afirmacion", 949, "La frontera se desplaza con η_f (A2; Exp.9 i)", [
        comp("desplazamiento ceteris paribus de ambas fronteras en η_f", "producto_conciliado" if ecp["pares"] and ecp["C2_distinto"] else "calculo_nuevo_necesario",
             "pares de celdas iguales salvo η_f, en G y en N", [ev(E_UN, None, "capture_ceiling_result.C_2 por par", "por celda", json.dumps({k: ecp[k] for k in ("pares", "C2_distinto", "C2_igual", "max_abs_dif_C2")}))],
             "pares compatibles hallados entre unidades aceptadas" if ecp["pares"] else "ninguna pareja de unidades aceptadas difiere solo en η_f", None if ecp["pares"] else "F-EXP9-ENF")])
    jd = {k: v for k, v in jj.items()}
    ob("C10", "afirmacion", 950, "El diseño de base mueve la frontera por un canal distinto (A2+B; Exp.9 ii)", [
        comp("disponibilidad: C_2^{j=d} frente a C_2^{j=f} y C_2^{j=df}", "producto_conciliado" if all(None not in v.values() for v in jd.values()) else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
             "contraste del techo por instrumento con el mismo diseño y sentido", [ev(c2[k]["archivo"], c2[k]["sha256"], "C_2 de %s" % c2[k]["unidad"], "global") for k in sorted(c2)], json.dumps(jd)),
        comp("intensidad vía τ_f", "producto_conciliado", "τ_f en el supremo por instrumento y diseño", [ev(E_UN, None, "capture_ceiling_result.tau_f_at_sup (C2)", "global",
                                                                                                    json.dumps({"%s:%s:%s" % k: v["tau_f_sup"] for k, v in sorted(c2.items())}))]),
        comp("forma vía G contra N", "producto_conciliado" if gn_dif else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje", "ver C3 (supremos)", [ev(E_UN, None, "C3", "global")])])
    a8 = ens["admissibility_report"]
    ob("Exp0", "experimento", 2205, "Auditoría de insumos: input_audit_report y admissibility_report", [
        comp("admissibility por conjunto de soporte (D7, previo a la corrida)", "producto_conciliado", "n_declared, n_admissible, n_violates_q_pot/eta_H/shares, share_discarded",
             [ev(D7 + "/d7_admissibility_report.csv", F["d7"].get("d7_admissibility_report.csv"), "evaluated/accepted/rejected por restricción", "%d conjuntos" % len(a8)),
              ev("conciliacion/ensamblajes/admissibility_report.csv", None, "tabla ensamblada con denominadores", "%d filas" % len(a8))],
             "ENSAMBLADO: %d conjuntos, rechazos totales %d; QPOT/ETAH cuentan por conjunto y SPI/STMARG por conjunto-país (razón = número de países en todos: %s), no son comparables directamente" % (
                 len(a8), sum(r["n_violates_q_pot"] + r["n_violates_eta_H"] + r["n_violates_shares"] + sum(r["otras_restricciones_rechazos"].values()) for r in a8), cob_ens["razon_SPI_QPOT_explicada"])),
        comp("identidad de las corridas (run_id) de los productos aceptados", "producto_conciliado", "run_id por corrida con sus conjuntos y celdas",
             [ev("conciliacion/ensamblajes/auditoria_por_corrida.csv", None, "run_id desde cell_context/frontier_context de las 2276 unidades", "%d corridas" % cob_ens["corridas"])],
             "demostrable desde las filas aceptadas; enlazado por conjunto en admissibility_report"),
        comp("input_audit_report §18.6 y admissibility §18.8 POR CORRIDA (level, n_cells_affected, recuentos por run_id)", "decision_cientifica_pendiente", "run_id·gate_id·level·n_cells_affected·decision·note",
             [ev(D7 + "/d7_gate_report.csv", F["d7"].get("d7_gate_report.csv"), "%d compuertas (por alcance de datos)" % len(gates), "D7"),
              ev("src/paper2b/run.py", None, "Run.rows: sin input_audit_report ni run_manifest", "productor"),
              ev("14 entregas de unidades (audit/entrega.json)", None, "sin run_manifest, input_audit_report, admissibility_report ni gate_report por corrida", "inventarios")],
             "LIMITACIÓN EXACTA: el productor no emitió esas tablas y no constan en ninguna entrega aceptada; level y n_cells_affected no se reconstruyen sin inventarlos. Afecta solo a Exp0 (§18.6/§18.8 por corrida). "
             "Alternativa honesta recomendada: declarar la auditoría por conjunto + identidad de corridas como evidencia de Gate 0 con esta limitación y añadir la emisión de input_audit_report/run_manifest "
             "por corrida a las corridas NUEVAS del lote propuesto (sin regenerar la ciencia pasada)", "F-EXP0")])
    ob("Exp1", "experimento", 2206, "Frontera y matriz de elasticidades", [comp("supremos", "producto_conciliado", "C_2 por diseño/instrumento", [ev(E_UN, None, "C2 (12)", "global")]),
                                                                       comp("ε_ij y regímenes", "calculo_nuevo_necesario", "ver C1", [], "", FE)])
    ob("Exp2", "experimento", 2207, "Comparación de diseños G y N", [comp("supremos lado a lado", O[2]["componentes"][0]["clase"], "ver C3", [ev(E_UN, None, "C3", "global")]),
                                                                 comp("geometría", "calculo_nuevo_necesario", "ver C3", [], "", FE)])
    ob("Exp3", "experimento", 2208, "Incidencia s_P(τ_f, φ) exacta frente a 1−φ", [comp("s_P por τ_f", "calculo_nuevo_necesario", "ver C4", [], "", FE)])
    ob("Exp4", "experimento", 2209, "Envolvente de λ_π", [comp("componentes", "producto_conciliado", "ver C7", []), comp("sup/inf con y sin θ_W<0 por bloque", "calculo_nuevo_necesario", "ver C7", [], "", "F-LAMBDA")])
    capas = Counter(x["capa"] for x in U.values())
    ob("Exp5", "experimento", 2210, "Confrontación G celda por celda, dos cotas, por capa", [
        comp("clasificación y G por celda, dos cotas, cuatro capas", "producto_conciliado", "veredicto por celda y capa",
             [ev(E_UN, None, "confrontation_result (G, K_comp_1, veredicto)", "2276 celdas", json.dumps({"cotas": dict(Counter(x["cota"] for x in U.values())), "capas": dict(capas)}))])])
    ob("Exp6", "experimento", 2211, "Inversión y margen de robustez", [
        comp("inversion_result con banderas", "producto_conciliado", "(29)–(30) con banderas", [ev(E_UN, None, "inversion_result", "por celda")]),
        comp("margen de robustez de las 16 robustas: 52 completas", "producto_conciliado", "§7.9.8", [ev(LEDGER[0], sha_led, "tareas PROD1/PROD2 completa_verificada", "16 afirmaciones")]),
        comp("68 búsquedas D4 (límite de la escalera declarada)", "limite_o_NA_admitido", "QUIEBRES-D4 aprobada", [ev(LEDGER[0], sha_led, "incompleta_declarada_D4", "16 afirmaciones")],
             "no demuestran ausencia de quiebre fuera del rango"),
        comp("sensibilidad Q (32 salidas)", "producto_conciliado", "Q-CONTINUO-COTA-SUPERIOR-v2", [ev(LEDGER[0], sha_led, "PROD3 rows m_Q_critical", "16 afirmaciones MEX × 2 ámbitos")])])
    ob("Exp7", "experimento", 2215, "Retirado bajo M3", [comp("no reactivar", "limite_o_NA_admitido", "§13", [], "sin celdas, parámetros ni salidas")], retirado=True)
    ob("Exp8", "experimento", 2212, "Ablación de eslabones (solo confrontaciones inconclusas): qué eslabón mueve más la clasificación, por país", [
        comp("tabla descriptiva completa por afirmación (testigos autenticados, G, C2, K1, λπ, Q, g, diferencias, residual)", "producto_conciliado",
             "identidad ΔG=ΔC2−ΔK1 y términos de K1 por afirmación, sin umbral",
             [ev(SEL[0] + "/" + SEL[2], fsel, "S1 testigos sup/inf", "%d inconclusas" % len(incon)), ev("conciliacion/EXP8_TABLA.csv", None, "una fila por afirmación", "%d filas" % len(filas8)),
              ev(FIJADOS["grilla"][0], F["grilla"]["sha256"], "Q por celda externa y cota", "grilla autenticada")],
             "descompuestas %d de %d; C2 cambia en %d, λπ en %d, Q en %d, g en %d; residual máx. %s; ESTO ES DESCRIPCIÓN, no causalidad" % (
                 exp8["descompuestas"], exp8["inconclusas"], exp8["C2_cambia"], exp8["lambda_cambia"], exp8["Q_cambia"], exp8["g_cambia"], exp8["max_abs_residual_identidad_G"])),
        comp("afirmaciones sin testigos completos (%d)" % exp8["sin_descomposicion"], "calculo_nuevo_necesario", "identificadas por motivo; sin extrapolarles el diagnóstico",
             [ev("conciliacion/EXP8_TABLA.csv", None, "motivo_sin_descomposicion", "%d afirmaciones" % exp8["sin_descomposicion"]),
              ev(SEL[0] + "/" + SEL[2], fsel, "S1 (los testigos figuran, sus filas no)", "celdas %s" % sorted({(c["testigo_sup"] if c["motivo_sin_descomposicion"].startswith("sup") else c["testigo_inf"])[:12]
                                                                                                         for c in exp8["casos_sin_descomposicion"]}))],
             "un testigo de cada una no tiene filas entre las 2276 unidades ni en ningún inventario sellado (búsqueda en audit/entrega.json de tmp/), y el registro v4 no guarda valores de testigos: "
             "recuperarlas exige evaluar esas celdas testigo (techo + confrontación). " +
             "; ".join("%s: %s" % (c["afirmacion"].split("PREG-")[1], c["motivo_sin_descomposicion"]) for c in exp8["casos_sin_descomposicion"]), "F-EXP8"),
        comp("eslabón que MUEVE la clasificación (ceteris paribus), por país", "decision_cientifica_pendiente", "§13 Exp.8 «qué eslabón mueve más la clasificación» y §17.4",
             [ev(D7 + "/support_sets.csv", F["d7"].get("support_sets.csv"), "conjuntos preespecificados: ABL-COV (φ/2), ABL-ENF (η_f/2), EXT-Q (Q), ROB-TEC/LABH/LABW/TAX (componentes de λπ)", "D7")],
             "ABL-COV y ABL-ENF solo reducen φ y η_f (mueven C2), no g, Q ni λπ; los canales de K1 tienen otros conjuntos preespecificados (EXT-Q, ROB-*) y g solo varía dentro de su soporte base. "
             "Qué subconjunto mínimo exige Exp8 es una decisión del autor; no se diseña ninguna sensibilidad nueva", "F-EXP8"),
        comp("propuesta N3 (§17.4) reformulada, para firma del autor", "decision_cientifica_pendiente", "elevar N3 si el eslabón no puede estrecharse decisivamente",
             [ev("FICHAS_PENDIENTES.json", None, "N3 propuesta (texto, evidencia, límites, efecto)", "afirmaciones inconclusas")], "texto preparado; NO firmado ni activado", "N3-PROPUESTA")])
    ob("Exp9", "experimento", 2213, "Estática comparativa de política", [
        comp("(i) enforcement η_f", O[8]["componentes"][0]["clase"], "ver C9", [ev(E_UN, None, "C9", "pares")], "", O[8]["componentes"][0]["ficha"]),
        comp("(ii) diseño de base", O[9]["estado"] if O[9]["estado"] != "calculo_nuevo_necesario" else "calculo_nuevo_necesario", "ver C10", [ev(E_UN, None, "C10", "global")]),
        comp("(iii) coordinación sobre η_f y φ (COORD-HALF preespecificado)", "calculo_nuevo_necesario", "régimen conjunto η_f × φ",
             [ev(D7 + "/scenario_map.csv", F["d7"].get("scenario_map.csv"), "coordination_scenario_id = COORD-HALF", "80 escenarios", str(dict(coord)))],
             "escenarios preespecificados en D7 sin producto aceptado (coordination_scenario_id nulo en las 2276 unidades: %s)" % dict(coord_u), "F-EXP9-COORD")])
    tab = {"T1": ("Los nueve números: soporte, naturaleza y estado", "producto_conciliado" if len(ens["T1"]) == 9 else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
                  "conciliacion/ensamblajes/T1.csv (§6.2 × D7 parameter_registry/support_set; θ y δ̃ por u_θ y z_cost según model.derive)"),
           "T2": ("Ecuaciones de observación con su estado", "producto_conciliado" if len(ens["T2"]) == 8 else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
                  "conciliacion/ensamblajes/T2.csv (§6.3: %d filas con estado asignado)" % len(ens["T2"])),
           "T3": ("Elasticidades y regímenes", "calculo_nuevo_necesario", "C1"), "T4": ("G y N: supremos y geometría", "calculo_nuevo_necesario", "C3 (geometría)"),
           "T5": ("Incidencia s_P por τ_f", "calculo_nuevo_necesario", "C4"), "T6": ("Envolvente λπ por país, con y sin θ_W<0", "calculo_nuevo_necesario", "C7"),
           "T7": ("Confrontación G por capa, dos cotas", "producto_conciliado" if not cob_ens["T7"]["omitidas"] and not cob_ens["T7"]["ajenas"] and cob_ens["T7"]["anexo"] == cob_ens["T7"]["unicas"] == len(reg)
                  else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
                  "conciliacion/ensamblajes/T7.csv (%d grupos) + T7_anexo (%d afirmaciones por esquema de claims.derive: %s; G, C2, K1, veredicto y certificado de cada testigo; %d testigos sin filas aceptadas)" % (
                      len(ens["T7"]), cob_ens["T7"]["anexo"], cob_ens["T7"]["por_familia"], cob_ens["T7"]["testigos_sin_filas"])),
           "T8": ("Inversión: puente requerido y ganancia potencial requerida, con banderas",
                  "producto_conciliado" if cob_ens["T8"]["cell_inversion_con_valores_distintos"] == 0 and len(cob_ens["T8"]["control_revisor"]) == 2 else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje",
                  "conciliacion/ensamblajes/T8.csv (%d grupos con mín./máx.) + T8_anexo (%d filas únicas de %d fuente; lambda_pi_required, delta_y_required y demás valores con estado, banderas, celda, unidad y ref.; "
                  "null conservado; %d filas con estado por unidad previo a la finalización global _fin)" % (len(ens["T8"]), cob_ens["T8"]["filas_unicas"], cob_ens["T8"]["filas_fuente"],
                                                                                                           cob_ens["T8"]["estado_por_unidad_con_fin"]))}
    for k, (tx, cl, src) in tab.items():
        ob(k, "tabla", 2687 + int(k[1]), tx, [comp("tabla del artículo", cl, "§21.1", [ev("ver " + src, None, "", "")],
                                                   "ENSAMBLADA desde valores almacenados aceptados (sin evaluar); su forma tipográfica final es del artículo" if cl == "producto_conciliado"
                                                   else "una tabla poblada no es la tabla ensamblada")])
    e5 = S1["E5"]
    for e_id, crit, cl, nota, fi, evi in (
            ("E1", "B_f(0) y dR/dτ_f|0 idénticos en η_f ∈ {0.8,1.2,4,8}", "producto_conciliado" if e1ok else "calculo_nuevo_necesario", nota_e1, None if e1ok else "F-E1",
             [VAL, "validaciones/resultados_E1_i2.json"]),
            ("E2", "ΔCS<0; 23.93% / 8.71% / −0.86%", "producto_conciliado" if e2ok else "calculo_nuevo_necesario", "ver C5 (ejemplo original del ledger reconstruido; presentación redondeada distinguida)",
             None if e2ok else "F-E2", [VAL]),
            ("E3", "s_P ≠ 1−φ a τ_f finito y convergencia τ_f→0", "producto_conciliado" if e3ok else "calculo_nuevo_necesario", "ver C4 (sintético; sin extrapolar a φ∈{0,1})",
             None if e3ok else "F-E3", [VAL]),
            ("E4", "supremos distintos y geometría de regímenes distinta", "calculo_nuevo_necesario", "supremos conciliados (C3); falta la geometría de regímenes (frontier_result); no se cierra por analogía con E1–E3/E5", FE, []),
            ("E5", "r* decreciente en τ_d; τ̃_d < τ_d para η_d>0", "producto_conciliado" if e5ok else "calculo_nuevo_necesario",
             "sintético: η_d∈{0.02,0.5,1,4}, τ_d 0.01..0.98; r* coincide con el mínimo independiente del problema de reporte (error máx. %s); fuera del criterio η_d=0 da τ̃_d=τ_d" % (
                 max(f["max_error_optimo_vs_busqueda"] for f in e5["filas"])), None if e5ok else "F-E5", [VAL]),
            ("E6", "incluir vértices θ_W<0 eleva λπ y reduce K1", "calculo_nuevo_necesario", "una fila λπ por celda; falta la comparación con/sin (envolvente, F-LAMBDA); no se cierra por analogía", "F-LAMBDA", [])):
        ob(e_id, "validacion", 2592 + int(e_id[1]), crit, [comp("criterio completo de §19.2", cl, crit,
                                                                [ev(x, sint_sha["E1235_i1"] if x == VAL else sint_sha["E1_i2"], e_id, "sintético") for x in evi] or
                                                                [ev(FIJADOS["solver_error_report"][0], F["solver_error_report"]["sha256"], "Paquete A (antecedente)", "sintético")], nota, fi)])
    for c in claims:
        g = c.split(":")[7] == "G"
        ts = [(u, por_u.get(u["id"])) for u in lista["unidades"] if u["afirmacion"] == c]
        her = [(u, por_u.get(u["id"])) for u in lista["unidades"] if c in (u.get("duplica_a") or [])]
        bus = [t for u, t in (ts if g else her) if u["familia"] != "PROD3"]
        d4 = sum(1 for t in bus if t and t["accepted_state"] == "incompleta_declarada_D4")
        q = [t for u, t in ts if u["familia"] == "PROD3"]
        nb = [x for x in lista["sin_busqueda"] if x["afirmacion"] == c]
        cs = [comp("categoría robusta_infactible_certificada", "producto_conciliado" if c in rob else "evidencia_existente_pendiente_de_extraccion_o_ensamblaje", "registro v4",
                   [ev(REG[0] + "/" + REG[2], F["registro_v4"]["sha256"], "afirmaciones[%s]" % c, "ci MEX")]),
              comp("búsquedas %s completas" % ("propias" if g else "heredadas de G"), "producto_conciliado", "QUIEBRES (§7.9.8)",
                   [ev(LEDGER[0], sha_led, "%s (%s)" % (t["id"], t["tree_sha256"][:12]), "afirmación") for t in bus if t and t["accepted_state"] == "completa_verificada"])]
        if d4:
            cs.append(comp("búsquedas D4 (%d)" % d4, "limite_o_NA_admitido", "QUIEBRES-D4", [ev(LEDGER[0], sha_led, "incompleta_declarada_D4", "afirmación")], "límite de la escalera declarada"))
        cs.append(comp("Q en dos ámbitos", "producto_conciliado", "Q-CONTINUO-COTA-SUPERIOR-v2", [ev(LEDGER[0], sha_led, "%s (%s)" % (t["id"], t["tree_sha256"][:12]), "global y MEX") for t in q if t]))
        if nb:
            cs.append(comp("sin búsqueda por contrato (%d)" % len(nb), "limite_o_NA_admitido", "lista_PROD.sin_busqueda", [ev(FIJADOS["lista_PROD"][0], F["lista_PROD"]["sha256"], "sin_busqueda", "afirmación")],
                           "; ".join("%s %s: %s" % (x["parametro"], x["direccion"], x["estado_por_contrato"]) for x in nb)))
        ob("AF:" + c.split("PREG-")[1], "afirmacion_16", None, c, cs)
    fichas = fichas_de(R, contr, exp8, exp0, U, esc, fronteras, S1)
    comps = [c for o in O if o["estado"] != "retirado_M3" for c in o["componentes"]]
    res = {"obligaciones": len(O), "obligaciones_vigentes": sum(o["estado"] != "retirado_M3" for o in O), "por_estado": dict(Counter(o["estado"] for o in O)),
           "componentes": len(comps), "componentes_por_clase": dict(Counter(c["clase"] for c in comps)), "fichas": sorted({c["ficha"] for c in comps if c["ficha"]})}
    sub = {"PROD4.1": ["Exp0", "C8", "T1", "T2", "T7", "T8"], "PROD4.2": ["E1", "E2", "E3", "E5"], "PROD4.3": ["C1", "C4", "C7", "Exp1", "Exp3", "Exp4", "T3", "T4", "T5", "T6", "E4", "E6"],
           "PROD4.4": ["C9", "Exp9"], "PROD4.5": ["Exp8"]}
    por_id = {o["id"]: o for o in O}
    res["subdivision_prod4"] = {k: {i: por_id[i]["estado"] for i in v} for k, v in sub.items()}
    doc = {"kind": "matriz-conciliacion-global-prod4-rem108", "generado_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "clases": CLASES,
           "validaciones_sinteticas": {"sha256": sint_sha, "conforme": {"E1": e1ok, "E2": e2ok, "E3": e3ok, "E5": e5ok}, "E1_salvedad": nota_e1},
           "ensamblajes": {k: len(v) for k, v in ens.items()}, "escenarios_d7": esc, "fronteras_unicas_por_pais_diseno_j": {"%s|%s|%s" % k: v for k, v in sorted(fronteras.items())},
           "fuentes": F, "citas_cobertura": {"conformes": sum(c["conforme"] for c in citas), "total": len(citas)},
           "unidades": {"localizadas_y_autenticadas": len(U), "rechazadas": rech, "por_familia": dict(Counter(x["familia"] for x in U.values())),
                        "por_contrato": dict(Counter(x["contrato"] for x in U.values())), "NA": sum(1 for x in U.values() if not x["numerico"])},
           "registro_v4_categorias": dict(cats), "contrastes": contr, "exp8_descomposicion": exp8, "exp0_ensamblaje": exp0, "input_audit_ensamblado": audit_ins,
           "coordinacion_d7": {"%s|%s|%s" % k: v for k, v in coord.items()}, "paquete_A": paqA, "obligaciones": O, "resumen": res,
           "dictamen_propuesto": "PROD4 NO cerrable: remanente demostrado (ver resumen y fichas)" if res["componentes_por_clase"].get("calculo_nuevo_necesario") or
           res["componentes_por_clase"].get("decision_cientifica_pendiente") or res["componentes_por_clase"].get("evidencia_existente_pendiente_de_extraccion_o_ensamblaje") else "PROD4 propuesto cerrado"}
    Path(salida + ".json").write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    Path(fichas_sal + ".json").write_text(json.dumps({"kind": "fichas-pendientes-rem108", "fichas": fichas}, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    L = ["# Matriz de conciliación global PROD4 por criterio (rem108)", "", "Generada desde la misma estructura que `%s.json` (fuente única: generar_matriz_rem108.py). Sin evaluar el modelo." % Path(salida).name, "",
         "Subdivisión informativa del mismo paso4.productos (no son hitos nuevos): " + "; ".join("%s → %s" % (k, ", ".join("%s %s" % (i, e) for i, e in v.items()))
                                                                                                for k, v in res["subdivision_prod4"].items()), "",
         "**%s.** Obligaciones vigentes: %d (Exp7 retirado aparte). Componentes: %d — %s." % (doc["dictamen_propuesto"], res["obligaciones_vigentes"], res["componentes"],
                                                                                           ", ".join("%s %d" % kv for kv in sorted(res["componentes_por_clase"].items()))), "",
         "| Obligación | Diseño | Estado | Componentes (clase — nota) |", "|---|---|---|---|"]
    for o in O:
        L.append("| %s | %s | %s | %s |" % (o["id"], ("l.%s" % o["linea_diseno"]) if o["linea_diseno"] else "lista_PROD", o["estado"],
                                          "<br>".join("%s: **%s**%s%s" % (c["componente"], c["clase"], (" — " + c["nota"]) if c["nota"] else "", (" [%s]" % c["ficha"]) if c["ficha"] else "")
                                                      for c in o["componentes"]).replace("|", "/")))
    L += ["", "## Contrastes derivados de resultados aceptados", "", "- C_2 G frente a N: `%s`" % json.dumps(gn), "- C_2 por instrumento: `%s`" % json.dumps(jj),
          "- η_f ceteris paribus: `%s`" % json.dumps({k: ecp[k] for k in ("pares", "C2_distinto", "C2_igual", "max_abs_dif_C2")}),
          "- Exp8 (DESCRIPTIVO; tabla completa en EXP8_TABLA.csv): `%s`" % json.dumps({k: exp8[k] for k in ("inconclusas", "descompuestas", "sin_descomposicion", "C2_cambia", "lambda_cambia",
                                                                                                      "Q_cambia", "g_cambia", "misma_celda_externa", "g_en_nodos_D7_ambos", "max_abs_residual_identidad_G",
                                                                                                      "termino_mayor_abs_niveles", "termino_mayor_abs_log_K1", "rango_parte_log_lambda")}, ensure_ascii=False),
          "- Exp8 lectura: %s" % exp8["lectura"],
          "- Ensamblajes PROD4.1: `%s` (conciliacion/ensamblajes/)" % json.dumps({k: len(v) for k, v in ens.items()}),
          "- Validaciones sintéticas PROD4.2: `%s`" % json.dumps({"E1": e1ok, "E2": e2ok, "E3": e3ok, "E5": e5ok}),
          "- Escenarios de coordinación/ablación en D7: `%s`" % json.dumps({"%s|%s|%s" % k: v for k, v in coord.items()}, ensure_ascii=False),
          "- Auditoría de insumos: `%s`" % json.dumps({k: exp0[k] for k in ("compuertas_d7", "estados", "campos_no_reconstruibles")}, ensure_ascii=False)]
    Path(salida + ".md").write_text("\n".join(L) + "\n", encoding="utf-8")
    FL = ["# Fichas de pendientes (rem108)", "", "Generadas desde la misma estructura que `%s.json`. Ninguna se ha ejecutado ni firmado; las sintéticas E1/E2/E3/E5 figuran como completadas en esta ronda." % Path(fichas_sal).name, ""]
    for f in fichas:
        FL += ["## %s — %s" % (f["id"], f["obligacion"]), ""] + ["- **%s:** %s" % (k, v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)) for k, v in f.items() if k not in ("id", "obligacion")] + [""]
    Path(fichas_sal + ".md").write_text("\n".join(FL) + "\n", encoding="utf-8")
    print(json.dumps({"resumen": res, "dictamen": doc["dictamen_propuesto"], "unidades": len(U), "rechazadas": len(rech), "citas": doc["citas_cobertura"],
                      "fuentes_ok": {k: v.get("conforme") for k, v in F.items() if isinstance(v, dict) and "conforme" in v},
                      "exp8": {k: exp8[k] for k in ("inconclusas", "descompuestas", "sin_descomposicion", "C2_cambia", "lambda_cambia", "Q_cambia", "g_cambia", "g_en_nodos_D7_ambos",
                                                    "max_abs_residual_identidad_G", "termino_mayor_abs_niveles", "termino_mayor_abs_log_K1")},
                      "eta_f": {k: ecp[k] for k in ("pares", "C2_distinto")}, "gn": {k: v["dif"] for k, v in gn.items()}}, ensure_ascii=False, default=str))


MEDIDO = {"contexto_S6_s": "132.8 y 143.4 (PREP_i2/PREP_i1 rem107), 144.4 (trabajador hasta contexto, rem107 R4); 79–158 por proceso (rem104)",
          "busqueda_Q_s": "11–24 por tarea (rem104, 16 tareas)", "techo_por_celda_s": "0.03–7 (d/f) a cientos (ínfimos df) (lima0746)",
          "R1_por_afirmacion_s": "≈24 de pared con contexto (lima1913)", "tope_tarea_s": 2400}
SUPUESTOS = {s: t for s, t in (
    ("S1", "Economía pequeña y proveedor extranjero con rentas"), ("S2", "Heterogeneidad Pareto"), ("S3", "Renta previa y ganancia proporcionales a productividad"),
    ("S4", "Pago de IA κ0 z^ρ"), ("S5", "Instrumentos y soporte institucional"), ("S7", "Elección del estatus previo"), ("S8", "Diseños domésticos G y N"),
    ("S9", "Reporte doméstico y costo de ocultamiento"), ("S10", "Reporte extranjero por coalición"), ("S11", "Gross-up e incidencia"), ("S13", "Elección y desempate"),
    ("S14", "Base incremental"), ("S16", "Equilibrio parcial estático"), ("S17", "Regiones suaves"), ("S18", "Integrabilidad y límites"))}


def respaldo(ids, teoria, empirico, estres, aporta, no_demuestra):
    return {"supuestos_del_plan": {i: SUPUESTOS[i] for i in ids}, "justificacion_teorica_o_bibliografica": teoria, "soporte_empirico": empirico,
            "rango_de_estres_del_autor": estres, "que_aporta_evidencia": aporta, "que_no_puede_demostrar": no_demuestra,
            "nota": "referencia a los supuestos YA registrados (PLAN_CIERRE assumptions S1–S18) y a sus tareas de referencias; no se abre revisión bibliográfica ni se amplían"}


EJES_LAMBDA = ("a", "rho", "kappa_tilde", "pi_iva", "pi_otros_productos", "pi_produccion", "eta_H", "eta_w")   # λπ = s_Π/(1−q_pot); q_pot(a,ρ,κ̃); s_Π(π, η_w, η_H)


def seleccion_lambda(R):
    """rem108 (P4-PROD4-CORRESPONDENCIA): selección de F-LAMBDA RESUELTA desde D7 por conjunto base: para cada eje de λπ, la variante que D7
    declara para ese conjunto (eta_H:H0, eta_w según el bloque, el resto primary), exigiendo que sea ÚNICA; gain_share fuera de λπ (solo extiende
    K1). Cuenta: malla completa de nivel 0; esquinas que bastan por la monotonía documentada (protocolo λπ v1.2.7 §7: λπ monótona en cada
    argumento; q_pot = κ̃(a−1)/(a−ρ) no decreciente en a, ρ, κ̃ con 1<a, 0<ρ≤1; θ_W = (η_w+η_H)/(1+η_H)); variante sin θ_W<0 por filtrado de
    los pares (η_w, η_H) de nivel 0; extensión por g (K1 decreciente en g) con sus dos nodos extremos."""
    ss = {r["support_set_id"]: r for r in csv.DictReader((R / D7 / "support_sets.csv").open(encoding="utf-8"))}
    sm = list(csv.DictReader((R / D7 / "scenario_map.csv").open(encoding="utf-8")))
    var = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader((R / D7 / "support_set.csv").open(encoding="utf-8")):
        if ss.get(r["support_set_id"], {}).get("kind") == "base" and r["parameter_id"] in EJES_LAMBDA + ("gain_share",) and r["domain_kind"] != "inactive":
            var[r["support_set_id"]][r["parameter_id"]].append(r)
    out = {}
    for s, d in sorted(var.items()):
        amb = {p: [x["variant_id"] for x in v] for p, v in d.items() if len(v) != 1}
        nod = {p: [float(z) for z in json.loads(v[0]["level0_nodes"])] for p, v in d.items() if len(v) == 1 and v[0]["level0_nodes"]}
        falt = [p for p in EJES_LAMBDA if p not in nod]
        paises = sorted({x["country_id"] for x in sm if x["support_set_id"] == s and x["country_id"]})
        pares = [(w, h) for w in nod.get("eta_w", []) for h in nod.get("eta_H", [])]
        sin_neg = [(w, h) for w, h in pares if (w + h) / (1 + h) >= 0]
        malla = math.prod(len(nod[p]) for p in EJES_LAMBDA if p in nod)
        out[s] = {"variantes": {p: v[0]["variant_id"] for p, v in d.items() if len(v) == 1}, "ambiguas": amb, "ejes_faltantes": falt, "paises": paises,
                  "nodos": {p: nod[p] for p in EJES_LAMBDA if p in nod}, "nodos_g_para_K1": nod.get("gain_share"),
                  "malla_nivel0_por_pais": malla, "esquinas_con_thetaW_neg_por_pais": 2 ** len(EJES_LAMBDA),
                  "pares_etaw_etaH": len(pares), "pares_sin_thetaW_neg": len(sin_neg), "evaluaciones_sin_thetaW_neg_por_pais": len(sin_neg) * 2 ** (len(EJES_LAMBDA) - 2),
                  "extension_K1_por_g": 2, "total_por_conjunto": len(paises) * (2 ** len(EJES_LAMBDA) + len(sin_neg) * 2 ** (len(EJES_LAMBDA) - 2))}
    return out


def fichas_de(R, contr, exp8, exp0, U, esc, fronteras, S1):
    nfr = sum(fronteras.values())
    vm = seleccion_lambda(R)
    lote_per = {c: [x for x in esc[c]["por_conjunto"] if x["support_set_id"].startswith("PER-E1.macro")] for c in esc}
    ids = lambda c: [{"support_set_id": x["support_set_id"], "padre": x["padre_support_set"], "escenario_capa": x["escenario_capa"], "padre_escenario": x["padre_escenario"],  # noqa: E731
                      "filas_pais_menu": len(x["pais_menu"])} for x in esc[c]["por_conjunto"]]
    tdom = sorted({json.dumps(x["tau_dom"], sort_keys=True) for x in U.values() if x["tau_dom"]})
    per_fr = {}
    for x in sorted(U.values(), key=lambda z: str(z["frontera"])):
        if x["pais"] == "PER" and x["numerico"] and x["frontera"] and x["set"] and x["set"].startswith("PER-E1.macro"):
            per_fr.setdefault("%s|%s" % (x["diseno"], x["j"]), {"frontier_id": x["frontera"], "conjunto": x["set"], "unidad_con_clave": x["sha256"][:16]})
    return [
        {"id": "F-ELAST", "obligacion": "C1, C3 (geometría), C4 (tabla de producción s_P), Exp1, Exp2 (geometría), Exp3, T3–T5, E4", "tipo_de_trabajo": "evaluación de una MALLA por frontera (no búsqueda de techo)",
         "ya_existe": "por cada unidad aceptada: frontier_context con la clave estructural (13 valores: a, beta_tilde, c_legal, eta_d, eta_f, gamma, kappa_tilde, phi, rho, t, u_theta, z_cost, z_m) y el dominio τ; techo C2 y su testigo",
         "no_existe": "frontier_result (eps_dd, eps_df, eps_fd, eps_ff, s_P, regime por punto): run.py lo produce (Run.frontier_rows) pero el contrato del paquete no lo exportó",
         "recorrido_que_exige_evaluar": "Run.frontier_rows → frontier.frontier_grid(state, diseño, j, τ̄_d, τ̄_f, cfg.frontier_n): malla de frontier_n+1 nodos por eje (supremum.nodes: bar·i/n; con frontier_n=4 por defecto: 5 puntos en d o f y 25 en df) con point_rows en cada nodo; "
                                        "NO necesita repetir la búsqueda del supremo ni los techos (la malla depende solo del estado ω y de las cotas τ)",
         "ids_reales": {"fronteras_unicas": nfr, "por_pais_diseno_j": {"%s|%s|%s" % k: v for k, v in sorted(fronteras.items())}, "dominios_tau_distintos": len(tdom)},
         "entradas": "claves estructurales y dominios τ ALMACENADOS de esas fronteras (sin nueva selección), contexto S6 vigente para la identidad",
         "salida_requerida": "frontier_result por frontera ligado a frontier_id; evidencia de régimen (topologías) por frontera",
         "criterio": "E4 (geometría de regímenes G≠N), C1 (ε_fd, ε_df ≠ 0), C4 (s_P por τ_f frente a 1−φ); mismas identidades T1 y el mismo validador de filas",
         "productor": "src/paper2b/run.py (Run.frontier_rows) y frontier.py (frontier_grid, point_rows) del núcleo vigente", "dependencias": "autorización científica del lote; contexto S6",
         "reutilizacion": "una malla por frontier_id (varias celdas comparten frontera); C2/G aceptados no se tocan",
         "coste": {"base_medida": MEDIDO["contexto_S6_s"], "no_medido": "coste de frontier_grid por frontera ((frontier_n+1)² nodos para df)",
                   "primer_lote_propuesto": "las fronteras únicas de PER (país principal) en un solo proceso con un contexto: mide segundos por frontera 1-D y 2-D; sus resultados válidos cuentan como producción candidata"},
         "impacto": "salida adicional con modelo e insumos intactos (no cambia quiebres, Q ni clasificaciones)",
         "respaldo": respaldo(["S2", "S3", "S4", "S7", "S8", "S9", "S10", "S11", "S13", "S14", "S17"], "teoría v2.2 (fase4_teoria/baseline_model_v2_2.md) y su verificación determinista",
                              "los soportes de D7 (source_evidence) para los parámetros; la forma funcional no se valida empíricamente aquí",
                              "dominios τ y escaleras declarados por el autor", "E1/E3/E5 sintéticos (rem107) prueban la implementación de reporte e incidencia",
                              "ni las pruebas sintéticas ni la malla validan empíricamente Pareto, κ0 z^ρ ni las elasticidades de reporte")},
        {"id": "F-LAMBDA", "obligacion": "C7 (envolvente), Exp4, T6, E6", "tipo_de_trabajo": "evaluación de una MALLA de vértices de Ω (forma cerrada de λπ; sin frontera ni techo)",
         "ya_existe": "lambda_pi_envelope de las 2276 unidades: λπ y sus componentes (s̄_L, q_pot, s_T^marg, η_H, η_w, θ_W) en el vértice de CADA celda visitada",
         "no_existe": "sup/inf de λπ sobre Ω por país y bloque η_w, con y sin vértices θ_W<0",
         "correccion_rem108": "rem107 tomaba solo variant_id=primary: omitía eta_H (H0) y eta_w (macro/micro) e incluía gain_share, que no entra en λπ (16.200 por conjunto era un conteo erróneo)",
         "recorrido_que_exige_evaluar": "por conjunto base y país: λπ en las ESQUINAS de los 8 ejes resueltos desde D7 (a, ρ, κ̃, π_iva, π_otros, π_producción, η_H, η_w); variante sin θ_W<0 con los pares (η_w, η_H) admitidos; "
                                        "K1 = Q/(λπ·g) se extiende con los 2 nodos extremos de g; la malla completa de nivel 0 NO es necesaria si se acepta la propiedad citada",
         "seleccion_resuelta_D7": vm,
         "propiedad_que_reduce": "PROTOCOLO_ENVOLVENTE_LAMBDA_PI_v1_2_7.md §7 (sha 00364bbd…): «λπ es monótona en cada argumento» (∂λπ/∂θ_W<0, ∂λπ/∂s_T<0, ∂λπ/∂q_pot>0, ∂λπ/∂η_H<0 si η_w<1) y "
                                 "«Simulación densa solo si las dependencias del §3 impiden localizar los extremos analíticamente»; con q_pot = κ̃(a−1)/(a−ρ) (model.derive) no decreciente en a, ρ y κ̃ "
                                 "para 1<a y 0<ρ≤1. Los soportes η_w de D7 (≤1) cumplen η_w≤1. No exige hipótesis nueva; si el revisor no la acepta, la alternativa es la malla completa (ver malla_nivel0_por_pais)",
         "contraste_del_revisor": "PER-E1: 5·5·6·3³·3·2 = 24.300 puntos de malla de nivel 0 por país/conjunto (antes de admisibilidad/deduplicación); coincide con malla_nivel0_por_pais; no es selección autorizada",
         "entradas": "D7 support_set (variantes resueltas arriba) y el módulo macro del núcleo; dos variantes (con y sin θ_W<0) PREESPECIFICADAS en §13 Exp4",
         "salida_requerida": "λπ sup/inf y K1 asociados por país × bloque × variante", "criterio": "Gate 3 (extremos = vértices analíticos dentro de ε_num) y E6 (con θ_W<0 eleva λπ y reduce K1)",
         "productor": "src/paper2b/run.py (build_macro) y macro.py", "dependencias": "autorización; contexto S6 para la identidad", "reutilizacion": "ningún techo; los vértices ya visitados deben reproducir su λπ aceptado",
         "coste": {"base_medida": "tamaño exacto de la malla (vértices por conjunto, arriba); " + MEDIDO["contexto_S6_s"], "no_medido": "segundos por vértice del módulo macro",
                   "primer_lote_propuesto": "PER-E1.macro y PER-E1.micro con y sin θ_W<0 en un proceso"},
         "impacto": "salida adicional con modelo e insumos intactos (la envolvente no cambia K1 de las celdas aceptadas)",
         "respaldo": respaldo(["S2", "S4", "S16", "S18"], "protocolo de la envolvente λπ v1.2.7 y LEDGER_LAMBDA_PI (forma cerrada de q_pot verificada frente a integración, error 1.3e-15)",
                              "fuentes D7 de π, η_w, η_H (source_evidence)", "bloques de robustez ROB-LABH/LABW/TAX/TEC elegidos por el autor",
                              "E2 sintético (composición del ledger) y la verificación del momento Pareto", "la envolvente no valida empíricamente la incidencia laboral ni la cuña tributaria")},
        {"id": "F-EXP9-ENF", "obligacion": "C9, Exp9 (i) enforcement", "tipo_de_trabajo": "optimización/búsqueda: techo C2 por celda en el contraste de η_f",
         "ya_existe": "%d pares de unidades iguales salvo η_f (η_f varía como soporte de Ω, sin ceteris paribus)" % contr["eta_f_ceteris_paribus"]["pares"],
         "no_existe": "desplazamiento de ambas fronteras en η_f con todo lo demás fijo",
         "ids_reales": {"contraste_preespecificado_en_D7": "ABL-ENF (enforcement_half: η_f/2 frente a su padre)", "conjuntos": ids("ABL-ENF")},
         "entradas": "conjuntos ABL-ENF y sus padres EXISTENTES; no se diseña otra rejilla de η_f", "salida_requerida": "C2 y frontera por celda en padre y ABL-ENF, G y N",
         "criterio": "mismo validador; contraste padre frente a ABL-ENF", "productor": "núcleo S6 vía tarea de producción con los conjuntos de D7", "dependencias": "DECISIÓN: confirmar que el contraste preespecificado ABL-ENF sirve para Exp9 (i) (D7 lo rotula «ablación»)",
         "reutilizacion": "los techos del padre ya aceptados donde coincidan las celdas; caché de techos persistente por clave estructural",
         "coste": {"base_medida": "%s; %s" % (MEDIDO["techo_por_celda_s"], MEDIDO["contexto_S6_s"]), "no_medido": "número de celdas por conjunto ABL-ENF",
                   "primer_lote_propuesto": "PER-E1.macro.ABL-ENF: %s" % [{"capa": x["escenario_capa"], "filas_pais_menu": len(x["pais_menu"])} for x in lote_per["ABL-ENF"]]},
         "impacto": "escenario ya previsto (no cambia los resultados aceptados del padre)",
         "respaldo": respaldo(["S9", "S10", "S16"], "reporte por coalición y costo de ocultamiento (teoría v2.2)", "η_f sin medición local (S9: no tratar estimaciones de otros contextos como medición local)",
                              "η_f/2 elegido por el autor en D7", "el contraste mide la sensibilidad del modelo a η_f", "no mide el enforcement efectivo de ningún país")},
        {"id": "F-EXP9-COORD", "obligacion": "Exp9 (iii) coordinación", "tipo_de_trabajo": "optimización/búsqueda: techo C2 por celda bajo COORD-HALF",
         "ya_existe": "ninguna unidad aceptada con coordination_scenario_id (nulo en las 2276)", "no_existe": "techos y confrontación bajo COORD-HALF",
         "ids_reales": {"escenario": "COORD-HALF", "conjuntos": ids("COORD-HALF"), "filas_scenario_map": esc["COORD-HALF"]["filas_scenario_map"],
                        "conjuntos_n": esc["COORD-HALF"]["conjuntos"], "filas_capa": esc["COORD-HALF"]["filas_capa"], "filas_pais_menu": esc["COORD-HALF"]["filas_pais_menu"],
                        "ambitos": esc["COORD-HALF"]["ambitos"], "paises": esc["COORD-HALF"]["paises"]},
         "entradas": "conjuntos *.COORD de D7 (coordination_half: η_f/2 y φ/2 sobre cada par, DI-07)", "salida_requerida": "capture_ceiling_result y confrontación con coordination_scenario_id = COORD-HALF",
         "criterio": "mismo validador; contraste con su escenario padre", "productor": "núcleo S6 con los conjuntos de D7", "dependencias": "autorización del lote",
         "reutilizacion": "80 filas no son 80 corridas: 10 conjuntos (uno por ámbito y bloque); las 70 filas país/menú son menús dentro de su conjunto",
         "coste": {"base_medida": "%s; %s" % (MEDIDO["techo_por_celda_s"], MEDIDO["contexto_S6_s"]), "no_medido": "celdas por conjunto *.COORD",
                   "primer_lote_propuesto": "PER-E1.macro.COORD: %s" % [{"capa": x["escenario_capa"], "padre": x["padre_escenario"], "filas_pais_menu": len(x["pais_menu"])} for x in lote_per["COORD-HALF"]]},
         "impacto": "escenario ya previsto en D7 (contribución 3 del diseño: Exp9 no es opcional)",
         "respaldo": respaldo(["S5", "S10", "S11", "S16"], "coordinación como régimen conjunto sobre η_f y φ (§13 Exp9)", "ninguno local para η_f; φ con fuentes D7",
                              "mitad/mitad elegido por el autor", "sensibilidad del modelo al régimen conjunto", "no es evaluación de una política real")},
        {"id": "F-EXP8", "obligacion": "Exp8 (qué eslabón MUEVE la clasificación, por país) y §17.4", "tipo_de_trabajo": "DECISIÓN científica previa; después, evaluación local o búsqueda según el canal",
         "ya_existe": "tabla descriptiva de %d afirmaciones (EXP8_TABLA.csv): en todas cambian C2 y λπ; Q cambia en %d y g en %d" % (exp8["descompuestas"], exp8["Q_cambia"], exp8["g_cambia"]),
         "no_existe": "ningún contraste ceteris paribus por eslabón; la descomposición entre testigos no lo sustituye",
         "celdas_testigo_sin_filas": {"celdas": sorted({c["testigo_sup"] if c["motivo_sin_descomposicion"].startswith("sup") else c["testigo_inf"] for c in exp8["casos_sin_descomposicion"]}),
                                      "afirmaciones": [c["afirmacion"] for c in exp8["casos_sin_descomposicion"]], "tipo": "evaluación local de techo + confrontación de esas celdas (búsqueda de techo por celda)",
                                      "coste": "%s por celda; un proceso con contexto" % MEDIDO["techo_por_celda_s"], "impacto": "completa la tabla descriptiva; no cambia la categoría de las 7 (registro v4)"},
         "canales_y_escenarios_preespecificados": {
             "techo C2 vía φ": {"conjuntos": "ABL-COV (φ/2)", "tipo": "búsqueda de techo (cambia la clave estructural)", "ids": ids("ABL-COV")},
             "techo C2 vía η_f": {"conjuntos": "ABL-ENF (η_f/2)", "tipo": "búsqueda de techo", "ids": ids("ABL-ENF")},
             "K1 vía Q": {"conjuntos": "EXT-Q (escala de Q: m_Q global primario, país adicional)", "tipo": "evaluación LOCAL: reutiliza C2 aceptado (Q no entra en la clave estructural)"},
             "K1 vía λπ": {"conjuntos": "ROB-LABH, ROB-LABW, ROB-TAX (ejes de λπ)", "tipo": "evaluación LOCAL: reutiliza C2 (los ejes macro no entran en la clave estructural)",
                           "excepcion": "ROB-TEC cambia a, ρ, κ̃ (estructurales y q_pot): búsqueda de techo"},
             "K1 vía g": {"conjuntos": "ninguno aparte: g varía dentro de su soporte base (nodos D7 0.01–0.1)", "tipo": "sin escenario preespecificado: un contraste propio sería una sensibilidad NUEVA → decisión pendiente, no se diseña"}},
         "decision_pendiente": "qué subconjunto mínimo de estos canales exige Exp8 para las inconclusas, o elevar N3 (§17.4) sin más rondas",
         "salida_requerida": "por afirmación inconclusa y canal: G y veredicto bajo el escenario, contra su padre", "criterio": "clasificación §17.1 con ε_econ = 0.01 y el mismo validador",
         "reutilizacion": "las 1712 inconclusas no son 1712 corridas: comparten fronteras y techos; los canales de K1 reutilizan los techos aceptados",
         "coste": {"base_medida": "%s; %s" % (MEDIDO["R1_por_afirmacion_s"], MEDIDO["techo_por_celda_s"]), "no_medido": "evaluación local de K1 por afirmación (forma cerrada) y techos nuevos por conjunto"},
         "impacto": "escenarios ya previstos; NO cambian quiebres ni Q aceptados",
         "respaldo": respaldo(["S1", "S11", "S16"], "§17.4 gobierno del caso inconcluso", "—", "escenarios D7 elegidos por el autor", "contrastes del modelo bajo escenarios previstos", "ninguno prueba causalidad empírica")},
        {"id": "F-EXP0", "obligacion": "Exp0 (input_audit_report §18.6)", "tipo_de_trabajo": "DECISIÓN (sin cálculo científico)",
         "ya_existe": "20 filas ensambladas desde d7_gate_report (gate_id, decision, note, incluidas las que pasaron); admissibility_report §18.8 ensamblado por conjunto (rechazos 0)",
         "no_existe": "; ".join(exp0["campos_no_reconstruibles"]),
         "decision_pendiente": "emitir input_audit_report por run_id en la próxima corrida autorizada, o aceptar el ensamblaje parcial como evidencia de Gate 0", "coste": {"base_medida": "sin cálculo científico"},
         "impacto": "documental", "respaldo": respaldo([], "§12.0 Gate 0", "D7 gate report", "—", "trazabilidad de compuertas", "no crea run_id ni afectaciones retroactivas")},
        {"id": "F-E1", "obligacion": "C2 / E1", "estado": "COMPLETADA en rem107 (sintética): B_f(0) idéntico exacto; derivada conforme en i2 (método fijado tras el i1 no conforme: salvedad)",
         "evidencia": "validaciones/resultados_E1235_i1.json (B_f0 exacto; derivada i1 no conforme) y resultados_E1_i2.json (Romberg conforme; método fijado tras i1)"},
        {"id": "F-E2", "obligacion": "C5 / E2", "estado": "COMPLETADA en rem107 (sintética; ejemplo original del ledger reconstruido)", "evidencia": "validaciones/resultados_E1235_i1.json:E2"},
        {"id": "F-E3", "obligacion": "C4 / E3", "estado": "COMPLETADA en rem107 (sintética)", "evidencia": "validaciones/resultados_E1235_i1.json:E3"},
        {"id": "F-E5", "obligacion": "E5", "estado": "COMPLETADA en rem107 (sintética)", "evidencia": "validaciones/resultados_E1235_i1.json:E5"},
        {"id": "LOTE-1-PROPUESTO", "obligacion": "primer lote representativo de PROD4.3/4.4 (PROPUESTO, no autorizado ni ejecutado)",
         "tareas": [
             {"id": "L1-LAMBDA", "ficha": "F-LAMBDA", "entradas": {s: vm[s]["variantes"] for s in ("PER-E1.macro", "PER-E1.micro") if s in vm},
              "unidades_de_trabajo": {s: vm[s]["total_por_conjunto"] for s in ("PER-E1.macro", "PER-E1.micro") if s in vm}, "salida": "λπ sup/inf y K1 extremos (×2 nodos de g) por bloque y variante θ_W",
              "criterio": "Gate 3 (extremos = vértices analíticos dentro de ε_num); E6", "dependencias": "contexto S6; ningún techo"},
             {"id": "L1-ELAST", "ficha": "F-ELAST", "entradas": {"fronteras": per_fr}, "unidades_de_trabajo": "%d mallas (una por diseño × j de PER)" % len(per_fr),
              "salida": "frontier_result por frontier_id", "criterio": "T1; mismo validador; ε_fd/ε_df ≠ 0 y geometría G frente a N", "dependencias": "contexto S6; claves estructurales almacenadas; ningún techo"},
             {"id": "L1-COORD", "ficha": "F-EXP9-COORD", "entradas": [{"capa": x["escenario_capa"], "padre": x["padre_escenario"], "pais_menu": x["pais_menu"]} for x in lote_per["COORD-HALF"]],
              "unidades_de_trabajo": "1 conjunto (PER-E1.macro.COORD) con sus filas país/menú; celdas no contadas (se cuentan al admitir)", "salida": "capture_ceiling_result/confrontation_result con coordination_scenario_id = COORD-HALF",
              "criterio": "mismo validador; contraste con su padre", "dependencias": "contexto S6; búsqueda de techo por celda (caché persistente por clave estructural)"}],
         "orden": ["0. Decisiones sin cálculo (ver DECISIONES)", "1. L1-LAMBDA (sin techos; menor riesgo)", "2. L1-ELAST (malla sin techos)", "3. L1-COORD (búsqueda de techos)"],
         "limites": {"por_tarea_s": 2400, "suite_s": 3600, "procesos": 3, "union_ronda_s": 10800, "admision": "conservadora: una tarea por proceso; ninguna promete cubrir todas las fronteras PER"},
         "parada": "al agotar el tope por tarea, la suite o el corte de la ronda, o ante cualquier rechazo del validador; no se lanza la siguiente si no cabe con margen (suite_cabe)",
         "terminacion_incompleta": "lo parcial se retira y no se acepta; no se repite sin permiso del alcance (reglas del coordinador ya revisadas); lo completo y validado cuenta como producción candidata",
         "coste": {"medido": "contexto S6 %s; no es la terminación de ningún producto" % MEDIDO["contexto_S6_s"], "no_medido": "evaluación de vértices λπ, mallas de frontera y techos COORD (lo mide el propio lote)"},
         "conexion_operativa": {"hallazgo": "las tareas de producción vigentes (tarea_prod.py: quiebres y Q) NO producen frontier_result, la envolvente λπ ni escenarios COORD",
                                "preparado_rem108": {"L1-LAMBDA": "lote/conexion_lambda.py → paper2b.macro.bridge (prueba sintética 5/5: TST exacto, esquinas = malla, E6)",
                                                     "L1-ELAST": "lote/conexion_frontera.py → model.state + model.frontier_grid, misma ruta que Run.frontier_rows (prueba sintética 8/8)",
                                                     "L1-COORD": "NO preparado: exige la búsqueda de techo de run.py con el conjunto PER-E1.macro.COORD de D7 dentro de una corrida; queda como corrección técnica"},
                                "falta_antes_de_ejecutar": "envolver las dos conexiones en una tarea contenida del coordinador (identidad, validador de filas y diario) y preparar L1-COORD; el algoritmo de run.py/macro.py no cambia"},
         "materializacion": "lote/LOTE1_MANIFIESTO.json (entradas resueltas y hashes; verificar_lote.py 11/11)",
         "no_se_recalcula": "quiebres (2276 unidades, 120 búsquedas) ni Q (16): ninguna tarea cambia un insumo usado por ellos"},
        {"id": "DECISIONES", "obligacion": "decisiones que realmente hacen falta (ninguna activada)",
         "lista": [
             {"id": "D-EXP8", "pregunta": "qué subconjunto mínimo de escenarios ya preespecificados completa Exp8 «qué eslabón mueve más la clasificación, por país»",
              "recomendada": "los dos canales locales que reutilizan los techos aceptados (EXT-Q para Q y ROB-LABH/LABW/TAX para λπ) sobre las 1.705 inconclusas descompuestas, más ABL-COV/ABL-ENF solo si se quiere el canal C2; "
                             "N3 se eleva para lo que quede sin estrechar",
              "alcance_exacto": "afirmaciones inconclusas con testigos completos; las 7 restantes requieren antes sus 4 celdas testigo; g no tiene escenario propio (un contraste en g sería sensibilidad NUEVA: no se propone)",
              "efecto_en_el_articulo": "Exp8 queda respondido por canal preespecificado y país; ninguna clasificación aceptada cambia"},
             {"id": "D-EXP9i", "pregunta": "usar ABL-ENF (η_f/2 frente a su padre) como el contraste de enforcement de Exp9 (i)",
              "recomendada": "sí, como ÚNICO contraste preespecificado de η_f disponible, declarando que cubre una reducción a la mitad y no una rejilla ni el canal de coordinación (Exp9 iii sigue con COORD-HALF)",
              "alcance_exacto": "10 conjuntos ABL-ENF y sus padres; no sustituye Exp9 (ii) ni (iii)", "efecto_en_el_articulo": "Exp9 (i) pasa a resultado del contraste preespecificado; no se diseña otra rejilla"},
             {"id": "D-EXP0", "pregunta": "tratamiento de input_audit_report/admissibility por corrida no conservados",
              "recomendada": "declarar la auditoría por conjunto + identidad de las 14 corridas como evidencia de Gate 0 con la limitación exacta, y emitir ambos informes por corrida en las corridas nuevas",
              "alcance_exacto": "solo Exp0 (§18.6/§18.8 por corrida)", "efecto_en_el_articulo": "limitación declarada en el apéndice de auditoría; no se regenera ciencia"},
             {"id": "D-LAMBDA", "pregunta": "aceptar la reducción a esquinas por la monotonía documentada del protocolo λπ v1.2.7 §7",
              "recomendada": "sí (propiedad ya documentada; no es hipótesis nueva); si no se acepta, usar la malla completa de nivel 0 indicada en F-LAMBDA",
              "alcance_exacto": "F-LAMBDA / T6 / E6", "efecto_en_el_articulo": "ninguno sobre resultados aceptados; reduce el trabajo de la envolvente"}],
         "no_se_pide": "ninguna firma ni acto en esta ronda; la autorización del lote y del paquete portable es el último paso sobre los paquetes completos"},
        {"id": "N3-PROPUESTA", "obligacion": "§17.4 (afirmaciones inconclusas)",
         "texto": ("N3 (PROPUESTA, NO FIRMADA). De las %d afirmaciones con confrontación inconclusa (cambio de signo certificado o testigos en tolerancia), %d tienen sus dos testigos aceptados completos. "
                   "En esas %d se cumple la identidad ΔG = ΔC2 − ΔK1 (residual máximo %.1e) y entre testigos cambian a la vez el techo C2 y el puente λπ (en todas), además de Q en %d y de g en %d; "
                   "por tanto la diferencia entre testigos NO se atribuye a un único eslabón y no se ha probado qué cambio aislado movería la clasificación. "
                   "Se propone: (a) declarar las %d inconclusas como resultado de la clasificación §17.1 (no como omisión de Exp8); (b) publicar la tabla descriptiva por afirmación con sus límites; "
                   "(c) decidir si Exp8 se completa con el subconjunto mínimo de escenarios ya preespecificados en D7 (ver F-EXP8) o se eleva esta N3 sin más rondas. "
                   "Las %d afirmaciones sin testigos completos quedan identificadas y fuera del diagnóstico.") % (
                      exp8["inconclusas"], exp8["descompuestas"], exp8["descompuestas"], exp8["max_abs_residual_identidad_G"] or 0.0, exp8["Q_cambia"], exp8["g_cambia"],
                      exp8["inconclusas"], exp8["sin_descomposicion"]),
         "demostrado": "identidad aritmética y qué términos cambian entre los testigos de cada afirmación", "no_demostrado": "efecto causal / ceteris paribus de cada eslabón; predominio como regla científica",
         "limitaciones": "g no figura en las filas: se deriva de EQ24 y se contrasta con los nodos D7; los testigos son ω distintos (no se construyen estados híbridos)",
         "efecto_en_el_articulo": "las inconclusas se reportan como categoría de resultado con la tabla descriptiva; ninguna clasificación cambia; Exp8 queda completo o explícitamente acotado según la decisión (c)",
         "estado": "texto concreto; no firmado ni activado"}]


if __name__ == "__main__":
    main(*sys.argv[1:5])
