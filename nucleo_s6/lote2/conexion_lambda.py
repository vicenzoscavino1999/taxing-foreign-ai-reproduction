"""rem114 (G-E0E3, COPIA AISLADA del lote 2): vertices_estrictos() ENUMERA estructuralmente un dominio nacional estricto (sin bridge ni
strict_vertices): los vértices de su caja de primitivas, como macro.strict_vertices (cada primitiva no degenerada en sus dos extremos
cerrados), agrupados por su vector de shares (macro.shares_from_terms). λπ depende solo de los shares, así que cada vector distinto es UN
candidato; evaluarlos TODOS en el testigo ω es la enumeración exhaustiva que strict_vertices recorre para elegir dos (sin esa preselección,
que exigiría bridge antes de fijar la cobertura). La regla de extremos se mantiene: el testigo ω es común a todos los candidatos solo si
ningún share es negativo (monotonía en θ_W y en cada π_j); si no, la envolvente no está cubierta. envolvente() no cambia.
rem111 (P4-LOTE1-COBERTURA-NACIONAL): cada entrada de evidencia lleva «shares_sha256», huella del vector de shares EVALUADO (huella_shares),
para que el validador contraste la identidad y la cobertura exactas con el anexo de cobertura nacional; el cálculo no cambia.
rem110 (P4-PROD4-LAMBDA-ADMISIBILIDAD): cobertura POR ESTADO NACIONAL; un vértice candidato inadmisible deja la envolvente «pendiente_no_cubierto»
(sin descartar el estado ni certificar el resto); evidencia de admisibilidad por estado, testigo nacional y ω por extremo, y recuento de llamadas.
rem109 — CONEXIÓN de L1-LAMBDA CORREGIDA (P4-PROD4-LAMBDA-DOMINIO). Sustituye a la de rem108, que filtraba θ_W<0 sobre los NODOS del
rectángulo (η_w, η_H) y perdía la frontera θ_W = 0 cuando η_w es continuo. El núcleo (paper2b.macro) no cambia.
Justificación (diseño v2.2.30): §14.2 «λπ es monótona en cada argumento por P1–P4, de modo que sus extremos están en vértices del soporte»;
§14.3 «η_w y η_H entran solo por θ_W; los vértices se toman sobre θ_W, no sobre el rectángulo» y «(κ̃_0, a, ρ) conjunta, con filtro (20)»;
protocolo λπ v1.2.7 §7. Con λπ = (1 − s̄_L·θ_W − Σ π_j s̄_j)/(1 − q_pot): decreciente en θ_W (s̄_L>0) y en cada π_j (s̄_j>0), creciente en q_pot
(s_Π>0), y q_pot = κ̃(a−1)/(a−ρ) no decreciente en κ̃, a y ρ (1<a, ρ≤1).
Dominio de θ_W: para cada nodo h de η_H (discreto), θ_W(η_w) = (η_w+h)/(1+h) es creciente en η_w ⇒ intervalo con extremos ABIERTOS/CERRADOS
según D7; variante «sin»: intersección con θ_W ≥ 0 (la frontera θ_W = 0 se alcanza en η_w = −h si cae dentro del soporte de η_w).
λπ_max: θ_W mínimo, π mínimos, q_pot máximo; λπ_min: θ_W máximo, π máximos, q_pot mínimo. Cada extremo se evalúa con macro.bridge (Fraction) y
se devuelve con su testigo ω. NO cubierto por la propiedad (se marca, no se inventa garantía): extremo en un borde abierto («no_alcanzado»),
testigo inadmisible por (20)/s_T/s_Π (el corte de admisibilidad desplaza el extremo fuera de los vértices) y dominio vacío.
K1/Q = 1/(λπ·g) con g en sus extremos (K1 decreciente en λπ y en g).
Uso: python -B -I -X utf8 conexion_lambda.py prueba-sintetica <raiz> <salida.json>"""
import hashlib
import itertools
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

PI = ("pi_iva", "pi_otros_productos", "pi_produccion")


def huella_shares(s):
    """rem111: identidad del estado nacional en la evidencia = sha256 del JSON canónico {clave: str(Fraction(valor))} del vector evaluado."""
    return hashlib.sha256(json.dumps({k: str(Fr(v)) for k, v in s.items()}, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def definicion_sha256(st):
    """rem114: identidad de un dominio estricto = sha256 del JSON canónico de su definición completa (la del censo nacional)."""
    return hashlib.sha256(json.dumps(st, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def vertices_estrictos(MC, st):
    """rem114: enumeración ESTRUCTURAL de un dominio estricto {domains, terms, denominator}. Mismas reglas que macro.strict_vertices antes de
    evaluar: extremos invertidos ⇒ DOMAIN_INVERTED; denominador no positivo en el dominio ⇒ DENOMINATOR_NOT_POSITIVE_ON_DOMAIN; primitiva
    degenerada ⇒ un solo valor. Devuelve (candidatos ordenados por huella [{huella, shares, primitivas}], vértices de la caja, signo_no_negativo)."""
    ids = sorted(st["domains"])
    for p in ids:
        if Fr(st["domains"][p][0]) > Fr(st["domains"][p][1]):
            raise ValueError("DOMAIN_INVERTED:" + p)
    if Fr(st["domains"][st["denominator"]][0]) <= 0:
        raise ValueError("DENOMINATOR_NOT_POSITIVE_ON_DOMAIN")
    choices = [((Fr(st["domains"][p][0]),) if Fr(st["domains"][p][0]) == Fr(st["domains"][p][1]) else (Fr(st["domains"][p][0]), Fr(st["domains"][p][1]))) for p in ids]
    grupos, n = {}, 0
    for combo in itertools.product(*choices):
        vals = dict(zip(ids, combo))
        sh = MC.shares_from_terms(vals, st["terms"], st["denominator"])
        n += 1
        g = grupos.setdefault(huella_shares(sh), {"shares": sh, "primitivas": []})
        g["primitivas"].append({p: str(v) for p, v in vals.items()})
    cand = [dict(huella=h, **g) for h, g in sorted(grupos.items())]
    return cand, n, all(Fr(x) >= 0 for c in cand for x in c["shares"].values())


def dominio(row):
    """Dominio de un eje desde una fila de D7 support_set: continuo [lo,hi] con cierres, o discreto con sus nodos."""
    k = row["domain_kind"]
    if k in ("discrete", "singleton"):
        return {"tipo": "discreto", "valores": sorted({Fr(str(x)) for x in json.loads(row["level0_nodes"])})}
    return {"tipo": "continuo", "lo": Fr(row["lower"]), "hi": Fr(row["upper"]), "lo_cerrado": row["lower_closed"] == "true", "hi_cerrado": row["upper_closed"] == "true"}


def extremos_eje(d):
    """(mín, cerrado, máx, cerrado) de un eje."""
    if d["tipo"] == "discreto":
        return d["valores"][0], True, d["valores"][-1], True
    return d["lo"], d["lo_cerrado"], d["hi"], d["hi_cerrado"]


def intervalos_theta(dw, dh, variante):
    """Dominio de θ_W como unión de intervalos (uno por nodo de η_H); variante «sin» lo corta en θ_W ≥ 0."""
    lo_w, lc, hi_w, hc = extremos_eje(dw)
    hs = dh["valores"] if dh["tipo"] == "discreto" else None
    if hs is None:
        raise ValueError("ETA_H_CONTINUO_NO_CUBIERTO")      # el soporte vigente de η_H es discreto (H0); otro caso no está cubierto aquí
    out = []
    for h in hs:
        if not h > -1:
            raise ValueError("ETA_H_GT_MINUS1")
        t = lambda w: (w + h) / (1 + h)  # noqa: E731
        a, ac, b, bc, wa, wb = t(lo_w), lc, t(hi_w), hc, lo_w, hi_w
        if variante == "sin":
            if b < 0 or (b == 0 and not bc):
                continue                                      # intervalo entero negativo: sin intersección
            if a < 0:
                a, ac, wa = Fr(0), True, -h                   # frontera θ_W = 0, alcanzada en η_w = −h (dentro del soporte)
        out.append({"h": h, "lo": a, "lo_cerrado": ac, "hi": b, "hi_cerrado": bc, "eta_w_lo": wa, "eta_w_hi": wb})
    return out


def envolvente(MC, shares, dom, variante):
    """Extremos admisibles de λπ y K1/Q por θ_W (§14.3); dom: {eje: fila D7 normalizada por dominio()} incl. gain_share."""
    iv = intervalos_theta(dom["eta_w"], dom["eta_H"], variante)
    if not iv:
        return {"variante": variante, "estado": "dominio_vacio", "detalle": "ningún θ_W admisible en la variante"}
    tmin = min(iv, key=lambda x: (x["lo"], not x["lo_cerrado"]))
    tmax = max(iv, key=lambda x: (x["hi"], x["hi_cerrado"]))
    ex = {p: extremos_eje(dom[p]) for p in PI + ("a", "rho", "kappa_tilde", "gain_share")}
    om_max = {"eta_w": tmin["eta_w_lo"], "eta_H": tmin["h"], **{p: ex[p][0] for p in PI}, "a": ex["a"][2], "rho": ex["rho"][2], "kappa_tilde": ex["kappa_tilde"][2]}
    om_min = {"eta_w": tmax["eta_w_hi"], "eta_H": tmax["h"], **{p: ex[p][2] for p in PI}, "a": ex["a"][0], "rho": ex["rho"][0], "kappa_tilde": ex["kappa_tilde"][0]}
    alc_max = tmin["lo_cerrado"] and all(ex[p][1] for p in PI) and all(ex[p][3] for p in ("a", "rho", "kappa_tilde"))
    alc_min = tmax["hi_cerrado"] and all(ex[p][3] for p in PI) and all(ex[p][1] for p in ("a", "rho", "kappa_tilde"))
    # shares: vector fijo o PROVEEDOR por ω (en producción, los estados nacionales de Run.states_for: vector publicado o vértices de
    # MC.strict_vertices para las coordenadas macro de ESE ω); λπ decrece en θ_W para todo vector con s̄_L>0, así que el testigo ω no cambia
    lista = (lambda om: shares(om)) if callable(shares) else (lambda om: [shares])  # noqa: E731
    # rem110 (P4-PROD4-LAMBDA-ADMISIBILIDAD): COBERTURA POR ESTADO NACIONAL. Para un estado, si su vértice de máximo es admisible es el máximo de su
    # región admisible (desde cualquier punto admisible, bajar θ_W y π sube s_Π y λπ, y subir q_pot con s_Π>0 sube λπ); si su vértice de mínimo
    # es admisible es el mínimo (subir θ_W y π baja s_Π monótonamente hasta un valor >0, y bajar q_pot con s_Π>0 baja λπ). Si el vértice es
    # INADMISIBLE, el extremo de ese estado no está en el vértice (p. ej. ínfimo hacia s_Π→0+): la propiedad no lo cubre y NO se descarta el
    # estado; la envolvente queda «pendiente_no_cubierto» y solo se informa un resultado PARCIAL de los estados cubiertos, marcado como tal.
    smax, smin = lista(om_max), lista(om_min)
    cmax = [MC.bridge(s, om_max) for s in smax]
    cmin = [MC.bridge(s, om_min) for s in smin]
    ev_max = [{"estado_nacional": i, "shares_sha256": huella_shares(smax[i]), "admisible": v.admissible, "motivos": list(v.reasons),
               "lambda": str(v.lambda_pi) if v.lambda_pi is not None else None} for i, v in enumerate(cmax)]
    ev_min = [{"estado_nacional": i, "shares_sha256": huella_shares(smin[i]), "admisible": v.admissible, "motivos": list(v.reasons),
               "lambda": str(v.lambda_pi) if v.lambda_pi is not None else None} for i, v in enumerate(cmin)]
    no_cub_max = [e["estado_nacional"] for e in ev_max if not e["admisible"]]
    no_cub_min = [e["estado_nacional"] for e in ev_min if not e["admisible"]]
    imax = max((i for i, v in enumerate(cmax) if v.admissible), key=lambda i: cmax[i].lambda_pi, default=None)
    imin = min((i for i, v in enumerate(cmin) if v.admissible), key=lambda i: cmin[i].lambda_pi, default=None)
    cubierto = not no_cub_max and not no_cub_min
    estado = "ok" if cubierto else "pendiente_no_cubierto"
    notas = []
    if not cubierto:
        notas.append("estados nacionales con vértice candidato INADMISIBLE (máx %s; mín %s): su extremo no está cubierto por la propiedad; no se certifica la envolvente "
                     "global ni se descarta el estado; los valores informados son PARCIALES (solo estados cubiertos)" % (no_cub_max, no_cub_min))
    if not (alc_max and alc_min):
        notas.append("extremo en un borde abierto: supremo/ínfimo NO alcanzado (se informa como límite)")
    g_lo, _, g_hi, _ = ex["gain_share"]
    clave = "" if cubierto else "_parcial_cubiertos"
    r = {"variante": variante, "estado": estado, "notas": notas, "intervalos_theta_W": [{k: str(v) for k, v in x.items()} for x in iv],
         "lambda_max" + clave: str(cmax[imax].lambda_pi) if imax is not None else None, "lambda_max_alcanzado": alc_max,
         "testigo_max": {k: str(v) for k, v in om_max.items()}, "testigo_nacional_max": imax, "theta_W_en_max": str(MC.theta_W(om_max["eta_w"], om_max["eta_H"])),
         "lambda_min" + clave: str(cmin[imin].lambda_pi) if imin is not None else None, "lambda_min_alcanzado": alc_min,
         "testigo_min": {k: str(v) for k, v in om_min.items()}, "testigo_nacional_min": imin, "theta_W_en_min": str(MC.theta_W(om_min["eta_w"], om_min["eta_H"])),
         "evidencia_por_estado": {"max": ev_max, "min": ev_min}, "estados_no_cubiertos": {"max": no_cub_max, "min": no_cub_min},
         "llamadas_bridge": len(cmax) + len(cmin)}
    if cubierto:
        r["K1_sobre_Q_min"] = str(1 / (cmax[imax].lambda_pi * g_hi))
        r["K1_sobre_Q_max"] = str(1 / (cmin[imin].lambda_pi * g_lo))
    return r


def envolvente_nodos_rem108(MC, shares, nodos, variante):
    """REPRODUCCIÓN del defecto (lógica de rem108: θ_W<0 filtrado sobre los nodos del rectángulo). Solo para la prueba."""
    ejes = ("a", "rho", "kappa_tilde") + PI + ("eta_H", "eta_w")
    todos = ("eta_w", "eta_H") if variante == "sin" else ()
    sel = {p: (sorted(nodos[p])[:1] + sorted(nodos[p])[-1:] if p not in todos else sorted(nodos[p])) for p in ejes}
    mn = mx = None
    for c in itertools.product(*(sel[p] for p in ejes)):
        om = dict(zip(ejes, c))
        if variante == "sin" and MC.theta_W(om["eta_w"], om["eta_H"]) < 0:
            continue
        v = MC.bridge(shares, om)
        if v.admissible:
            mn = v.lambda_pi if mn is None or v.lambda_pi < mn else mn
            mx = v.lambda_pi if mx is None or v.lambda_pi > mx else mx
    g = sorted(nodos["gain_share"])
    return {"lambda_max": str(mx), "K1_sobre_Q_min": str(1 / (mx * g[-1]))}


def malla_densa(MC, shares, dom, variante, paso):
    """CONTRASTE INDEPENDIENTE: barrido racional fino de η_w (con sus extremos cerrados) × todos los nodos discretos × extremos del resto."""
    lo_w, lc, hi_w, hc = extremos_eje(dom["eta_w"])
    n = int((hi_w - lo_w) / paso)
    ws = [lo_w + paso * i for i in range(n + 1)] + [hi_w]
    ws = [w for w in ws if (w > lo_w or lc) and (w < hi_w or hc)]
    ejes = {p: list(dict.fromkeys(extremos_eje(dom[p])[0::2])) for p in PI + ("a", "rho", "kappa_tilde")}
    mx = mn = None
    for h in dom["eta_H"]["valores"]:
        for w in ws:
            if variante == "sin" and MC.theta_W(w, h) < 0:
                continue
            for c in itertools.product(*ejes.values()):
                v = MC.bridge(shares, dict(zip(ejes, c), eta_w=w, eta_H=h))
                if v.admissible:
                    mx = v.lambda_pi if mx is None or v.lambda_pi > mx else mx
                    mn = v.lambda_pi if mn is None or v.lambda_pi < mn else mn
    return mx, mn


if __name__ == "__main__" and sys.argv[1] == "prueba-sintetica":
    R, SAL = Path(sys.argv[2]), Path(sys.argv[3])
    sys.path.insert(0, str(R / "paso4/instalacion/src"))
    from paper2b import macro as MC
    cont = lambda lo, hi, lc="true", hc="true": dominio({"domain_kind": "continuous", "lower": lo, "upper": hi, "lower_closed": lc, "upper_closed": hc})  # noqa: E731
    disc = lambda xs: dominio({"domain_kind": "discrete", "level0_nodes": json.dumps(xs)})  # noqa: E731
    # caso SINTÉTICO del revisor (rem109): shares s_L=3/10, s_iva=1/10, demás 0; π=1; a=3/2, ρ=1/2, κ̃=1/5; g=1/10; η_w continuo [0,4;1] y η_H {−0,5;0;0,5} (forma PER-E1.macro)
    sh = {"s_L_bar": Fr(3, 10), "s_bar_iva": Fr(1, 10), "s_bar_otros_productos": Fr(0), "s_bar_produccion": Fr(0)}
    dom = {"eta_w": cont("0.4", "1"), "eta_H": disc([-0.5, 0.0, 0.5]), **{p: disc([1]) for p in PI}, "a": disc([1.5]), "rho": disc([0.5]), "kappa_tilde": disc([0.2]), "gain_share": disc([0.1])}
    nod = {"eta_w": [Fr(2, 5), Fr(1)], "eta_H": [Fr(-1, 2), Fr(0), Fr(1, 2)], **{p: [Fr(1)] for p in PI}, "a": [Fr(3, 2)], "rho": [Fr(1, 2)], "kappa_tilde": [Fr(1, 5)], "gain_share": [Fr(1, 10)]}
    C = []

    def caso(cid, ok, det=None):
        C.append({"id": cid, "conforme": bool(ok), "detalle": det})
        print(("OK  " if ok else "NO  ") + cid)
    viejo = envolvente_nodos_rem108(MC, sh, nod, "sin")
    caso("L1 REPRODUCE el defecto rem108: λ_max = 13/15 y K1/Q mín = 150/13 (pierde la frontera θ_W = 0)", viejo == {"lambda_max": "13/15", "K1_sobre_Q_min": "150/13"}, viejo)
    nuevo = envolvente(MC, sh, dom, "sin")
    caso("L2 CORRECCIÓN: λ_max = 1 en la frontera θ_W = 0 (η_w = 1/2, η_H = −1/2) y K1/Q mín = 10", (nuevo["lambda_max"], nuevo["K1_sobre_Q_min"], nuevo["theta_W_en_max"],
         nuevo["testigo_max"]["eta_w"], nuevo["testigo_max"]["eta_H"]) == ("1", "10", "0", "1/2", "-1/2"), nuevo)
    mx, mn = malla_densa(MC, sh, dom, "sin", Fr(1, 1000))
    caso("L3 CONTRASTE INDEPENDIENTE (barrido racional de η_w con paso 1/1000 y extremos): máx = 1 y mín coinciden con la derivación por θ_W",
         (str(mx), str(mn)) == (nuevo["lambda_max"], nuevo["lambda_min"]), {"densa": [str(mx), str(mn)]})
    dom3 = dict(dom, eta_H=disc([-1 / 3, 0.0, 0.5]))                     # corte en η_w = 1/3 ∉ rejilla de 1/1000
    n3 = envolvente(MC, sh, dict(dom3, eta_w=cont("0.3", "1")), "sin")
    mx3, _ = malla_densa(MC, sh, dict(dom3, eta_w=cont("0.3", "1")), "sin", Fr(1, 1000))
    caso("L4 frontera fuera de la rejilla (η_H = −1/3 ⇒ η_w = 1/3): la derivación acota por arriba al barrido y la diferencia es O(paso)",
         Fr(n3["lambda_max"]) >= mx3 and Fr(n3["lambda_max"]) - mx3 <= Fr(1, 1000), {"derivacion": n3["lambda_max"], "densa": str(mx3)})
    con = envolvente(MC, sh, dom, "con")
    mxc, mnc = malla_densa(MC, sh, dom, "con", Fr(1, 1000))
    caso("L5 variante con θ_W<0: extremos derivados = barrido denso; λ_max(con) ≥ λ_max(sin) (E6)", (Fr(con["lambda_max"]), Fr(con["lambda_min"])) == (mxc, mnc)
         and Fr(con["lambda_max"]) >= Fr(nuevo["lambda_max"]), {"con": [con["lambda_max"], con["lambda_min"]]})
    vac = envolvente(MC, sh, dict(dom, eta_w=cont("0.05", "0.2"), eta_H=disc([-0.5])), "sin")
    caso("L6 dominio vacío (η_w ∈ [0,05;0,2], η_H = −1/2 ⇒ θ_W < 0 siempre): estado dominio_vacio, sin extremos inventados", vac["estado"] == "dominio_vacio", vac)
    sinint = envolvente(MC, sh, dict(dom, eta_w=cont("0.05", "0.2"), eta_H=disc([-0.5, 0.5])), "sin")
    caso("L7 un nodo de η_H sin intersección (−1/2) y otro sí (1/2): solo cuenta el intervalo admisible", len(sinint["intervalos_theta_W"]) == 1 and sinint["intervalos_theta_W"][0]["h"] == "1/2", sinint["intervalos_theta_W"])
    abierto = envolvente(MC, sh, dict(dom, eta_w=cont("0.4", "1", lc="false")), "con")
    caso("L8 borde abierto de η_w en el extremo: λ_max marcado NO alcanzado (límite), no se presenta como vértice", abierto["lambda_max_alcanzado"] is False and bool(abierto["notas"]), abierto["notas"])
    corte = envolvente(MC, {"s_L_bar": Fr(3, 10), "s_bar_iva": Fr(9, 10), "s_bar_otros_productos": Fr(0), "s_bar_produccion": Fr(0)}, dict(dom, pi_iva=disc([0.5, 1.2])), "con")
    caso("L9 corte de admisibilidad en el extremo (s_Π ≤ 0 en el testigo del mínimo): estado pendiente_no_cubierto, sin garantía inventada", corte["estado"] == "pendiente_no_cubierto", corte["notas"])
    sh2 = dict(sh, s_L_bar=Fr(1, 5))
    prov = envolvente(MC, lambda om: [sh, sh2], dom, "con")
    m1, m2 = envolvente(MC, sh, dom, "con"), envolvente(MC, sh2, dom, "con")
    caso("L10 proveedor de dos estados nacionales por ω: el extremo es el mejor de los estados en el MISMO testigo (máx de máximos, mín de mínimos)",
         Fr(prov["lambda_max"]) == max(Fr(m1["lambda_max"]), Fr(m2["lambda_max"])) and Fr(prov["lambda_min"]) == min(Fr(m1["lambda_min"]), Fr(m2["lambda_min"])),
         {"proveedor": [prov["lambda_max"], prov["lambda_min"]], "estado1": [m1["lambda_max"], m1["lambda_min"]], "estado2": [m2["lambda_max"], m2["lambda_min"]]})
    # rem110: contraejemplo del revisor (admisibilidad parcial); defecto reproducido con la conexión SELLADA de rem109
    import importlib.util
    sp9 = importlib.util.spec_from_file_location("conexion_lambda_rem109", R / "tmp/paso4_conciliacion_portabilidad_desde_rem109/lote/conexion_lambda.py")
    C9 = importlib.util.module_from_spec(sp9)
    sp9.loader.exec_module(C9)
    e1 = {"s_L_bar": Fr(3, 10), "s_bar_iva": Fr(1, 10), "s_bar_otros_productos": Fr(0), "s_bar_produccion": Fr(0)}
    e2 = dict(e1, s_bar_iva=Fr(9, 10))
    domr = {"eta_w": cont("0.4", "1"), "eta_H": disc([-0.5, 0.0, 0.5]), "pi_iva": disc([0.5, 0.75, 1]), "pi_otros_productos": disc([1]), "pi_produccion": disc([1]),
            "a": disc([1.5]), "rho": disc([0.5]), "kappa_tilde": disc([0.2]), "gain_share": disc([0.1])}
    viejo9 = C9.envolvente(MC, lambda om: [e1, e2], domr, "con")
    caso("L11 REPRODUCE el defecto rem109: estado ok y λ_min = 2/3 (descartaba el estado 2 por fallar en el vértice)", (viejo9["estado"], viejo9["lambda_min"], viejo9.get("K1_sobre_Q_max")) == ("ok", "2/3", "15"),
         {k: viejo9.get(k) for k in ("estado", "lambda_min", "K1_sobre_Q_max")})
    corr = envolvente(MC, lambda om: [e1, e2], domr, "con")
    caso("L12 CORRECCIÓN: pendiente_no_cubierto, estado 2 no cubierto en el mínimo, sin K1/Q certificados y el parcial marcado como tal",
         corr["estado"] == "pendiente_no_cubierto" and corr["estados_no_cubiertos"]["min"] == [1] and "K1_sobre_Q_max" not in corr and "lambda_min" not in corr
         and corr["lambda_min_parcial_cubiertos"] == "2/3", {k: corr.get(k) for k in ("estado", "estados_no_cubiertos", "lambda_min_parcial_cubiertos", "testigo_nacional_min")})
    pint = MC.bridge(e2, {"eta_w": Fr(1), "eta_H": Fr(-1, 2), "pi_iva": Fr(3, 4), "pi_otros_productos": Fr(1), "pi_produccion": Fr(1), "a": Fr(3, 2), "rho": Fr(1, 2), "kappa_tilde": Fr(1, 5)})
    caso("L13 por qué no se certifica: el punto interior (η_w=1, η_H=−1/2, π_IVA=3/4) del estado 2 es ADMISIBLE con λ = 1/36 < 2/3 y K1/Q = 360 > 15",
         pint.admissible and pint.lambda_pi == Fr(1, 36) and 1 / (pint.lambda_pi * Fr(1, 10)) == 360, {"admisible": pint.admissible, "lambda": str(pint.lambda_pi)})
    cub = envolvente(MC, lambda om: [e1], domr, "con")
    caso("L14 positivo cubierto: el estado 1 solo (todos sus vértices admisibles) sí certifica la envolvente con K1/Q = 1/(λ·g)",
         cub["estado"] == "ok" and Fr(cub["K1_sobre_Q_max"]) == 1 / (Fr(cub["lambda_min"]) * Fr(1, 10)) and Fr(cub["K1_sobre_Q_min"]) == 1 / (Fr(cub["lambda_max"]) * Fr(1, 10)), {k: cub.get(k) for k in ("estado", "lambda_max", "lambda_min")})
    caso("L15 recuento de llamadas: 2 por estado y variante (máx y mín); con 9 estados, 36 por conjunto entre las dos variantes",
         envolvente(MC, lambda om: [e1] * 9, domr, "con")["llamadas_bridge"] + envolvente(MC, lambda om: [e1] * 9, domr, "sin")["llamadas_bridge"] == 36, None)
    hu = [[e["shares_sha256"] for e in corr["evidencia_por_estado"][x]] for x in ("max", "min")]
    caso("L16 rem111: la evidencia de CADA estado lleva la huella del vector evaluado, en el orden del proveedor (también si el estado no queda cubierto)",
         hu == [[huella_shares(e1), huella_shares(e2)]] * 2 and huella_shares(e1) != huella_shares(e2)
         and huella_shares({k: float(v) for k, v in e1.items()}) == huella_shares({k: Fr(float(v)) for k, v in e1.items()}), {"huellas": [[h[:12] for h in x] for x in hu]})
    res = {"kind": "prueba-sintetica-lambda-dominio-rem111", "datos": "SINTÉTICOS (caso del revisor y variantes declaradas); ningún share ni soporte empírico", "casos": C,
           "conformes": sum(c["conforme"] for c in C), "total": len(C)}
    SAL.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"conformes": res["conformes"], "total": res["total"]}))
    raise SystemExit(0 if res["conformes"] == res["total"] else 4)
