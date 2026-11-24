"""Suplemento P7 (FAM12, F12-P7-G): siete afirmaciones conciliadas por canal (COV, ENF, padre).

Lógica científica extraída de conciliar_p7.py (rem153, 6c9fb4a5…, la que usó la producción rem154), bucle por afirmación y canal,
sin cambios de fórmula:
  - lado faltante: G = C2 − K1 con C2 ∈ [C_2 − e, C_2 + e] (e = error normalizado del techo COV/ENF; error certificado del techo
    padre), K1 binary64 sin cota adicional, con cotas_G, lado (eps = 1/100, desigualdades estrictas) y signo del conciliador i5;
  - lado presente: fila COV aceptada; techo ENF completo; o, si el techo ENF histórico es incompleto, las cotas EXACTAS de la
    resolución aceptada (rem148), marcadas como tales, sin promover ni recalcular el techo;
  - canal_phi(categoría original, testigo sup, testigo inf); el padre informa el lado faltante y no fabrica el canal combinado.
Adaptación de interfaz: las afirmaciones, el lado presente y los techos llegan como datos (datos/p7_suplemento.json) y el K1 de
cada celda llega ya calculado (comando p7-k1), en vez de leer el manifiesto y los directorios de tareas. Se omiten la puerta
nativa, la validación de tareas y la escritura de archivos del arnés histórico. G es el módulo src/conciliar_cov.py (i5)."""
from collections import Counter
from fractions import Fraction


def conciliar_siete(datos, k1, G):
    """Filas del suplemento, una por afirmación, en el orden de las entradas. k1: {unidad: K1 binary64}."""
    cel = datos["unidades"]
    filas = []
    for a in datos["afirmaciones"]:
        u = a["unidad_faltante"]
        c = cel[u]
        k, lf = k1[u], a["lado_faltante"]
        canales = {}
        for canal in ("COV", "ENF", "padre"):
            tc = c["techos"][canal]
            e = tc.get("error_normalizado") if canal != "padre" else tc.get("error")
            # criterio de evidencia del conciliador i5 aceptado (evidencia()): techo completo, certified_bound y error float; si no, sin_evidencia
            apto = isinstance(e, float) and tc.get("C_2") is not None and (canal == "padre" or (tc.get("estado") == "complete"
                                                                                                and tc.get("error_kind") == "certified_bound"))
            if apto:
                lo, hi = G.cotas_G(tc["C_2"], e, k, 0.0)
                falt = {"clave": tc.get("clave"), "C_2": tc["C_2"], "e": e, "error_R": tc.get("error_R"), "K1": k, "g_lo": lo, "g_hi": hi,
                        "lado": G.lado(lo, hi, G.EPS, lf), "signo": G.signo(lo, hi)}
            else:
                falt = "sin_evidencia"
            pres, origen_pres = None, None
            if canal == "COV":
                p = a["presente"]["COV"]
                pres, origen_pres = {"g_lo": Fraction(p["g_lo"]), "g_hi": Fraction(p["g_hi"])}, "fila_COV_aceptada"
            elif canal == "ENF" and a["presente"].get("ENF_techo"):
                pe, te = a["presente"]["ENF"], a["presente"]["ENF_techo"]
                ra = a["presente"].get("ENF_resolucion_aceptada")
                if te.get("estado") == "complete" and te.get("error_kind") == "certified_bound" and isinstance(te.get("error_normalizado"), float):
                    plo, phi_ = G.cotas_G(te["C_2"], te["error_normalizado"], pe["K1_reutilizado"], 0.0)
                    pres, origen_pres = {"g_lo": plo, "g_hi": phi_}, "techo_ENF_complete"
                elif (ra and ra.get("promovido_a_complete") is False and ra.get("recalculado") is False and ra.get("clave") == pe.get("clave_transformada_sha256")
                      and ra.get("estado_historico_del_techo") == te.get("estado") != "complete"):
                    # rem153 (P4-P7-ENF-RESOLUCION-ACEPTADA): cotas EXACTAS aceptadas (rem148) para la clave resuelta (rem132); el techo sigue
                    # incompleto en su historial y la resolución se conserva aparte; no se promueve ni se recalcula
                    pres, origen_pres = {"g_lo": Fraction(ra["G_lower"]), "g_hi": Fraction(ra["G_upper"])}, "resolucion_aceptada_rem148_%s" % ra["clave"]
                else:
                    pres, origen_pres = "sin_evidencia", "sin_evidencia"
            if pres is not None:
                s, i = (pres, falt) if lf == "inf" else (falt, pres)
                cob, lab = G.canal_phi(a["categoria_original"], s, i)
            else:
                cob, lab = None, None
            canales[canal] = {"faltante": falt if falt == "sin_evidencia" else {kk: (str(vv) if isinstance(vv, Fraction) else vv) for kk, vv in falt.items()},
                              "presente": pres if pres in (None, "sin_evidencia") else {kk: str(vv) for kk, vv in pres.items()},
                              "presente_origen": origen_pres, "cobertura": cob, "canal": lab}
        filas.append({"afirmacion": a["afirmacion"], "pais": a["pais"], "lado_faltante": lf, "unidad": u, "cell_id": c["cell_id"],
                      "K1": k, "K1_tipo": c["K1_tipo"], "categoria_original": a["categoria_original"],
                      "canal_eta_f_aceptado": a["canal_eta_f_aceptado"], "canal_phi_COV_aceptado": a["canal_phi_COV_aceptado"], "canales": canales})
    return filas


def resumen(filas):
    """Conteos por canal, como el resumen histórico SUPLEMENTO_P7.json (canal_COV, canal_ENF)."""
    return {"filas": len(filas), "canal_COV": dict(Counter(x["canales"]["COV"]["canal"] for x in filas)),
            "canal_ENF": dict(Counter(str(x["canales"]["ENF"]["canal"]) for x in filas))}
