"""Propagación a los extremos de G de las familias que usan df (ci-df, country conditional_full y global
conditional_full) sobre una SELECCIÓN DE VALIDACIÓN fijada antes de calcular cotas (CIERRE G DF 3.7, NO OFICIAL).
VERSIÓN v5 (v1–v4 se conservan): como v4, y además η_f entra en la partición (pérdida estimada 0,01·C2_d·Δη_f): con η_f en
su rango completo, t̃_f (varias apariciones de η_f) se sobreestima y la cota pierde ~8,6e-5 en a = 2,14 (DUU2).
De v4: la cota inferior del ínfimo usa la COTA DE UN UMBRAL (codigo/cota_un_umbral_v2.py,
FUNDAMENTO_G_DF §2), que admite informales y contiene como caso particular la de «todos formales»; τ por rejilla + patrones
con semilla del τ de la caja madre; partición en (a, κ̃, φ, ρ) por PÉRDIDA ESTIMADA (anchura x sensibilidad aproximada de
la cota conjunta: a: (4,14·C2_d + k κ̃ ∂q/∂a)·Δa; κ̃: k q Δκ̃; ρ: k κ̃ ∂q/∂ρ Δρ; φ: 1e-4·Δφ), que solo decide dónde se
refina (la cota es válida en toda caja). Registra el contexto de los testigos (sup: el de k mínimo; inf: el de k máximo).
<solo>: índices (orden de claim_id) de las ci-df de la selección que calcula este proceso ("todos" = todas); la
agregación country/global se hace aquí si están todas sus componentes, o con codigo/agregar_G_df.py.

  <py_integracion> -m codigo.extremos_G_df_v5 <G|N> <puntos_U.json[,...]> <salida.json> <tope_s> <tope_por_afirmacion_s> <solo>

Regla de selección SEL-PROPAGACION-DF-v1 (depende solo de las claves del registro v4 y de los datos de contexto; se
escribe en la salida ANTES de calcular cualquier cota):
  (1) g*: la afirmación global conditional_full del diseño con menor sha256("SEL-PROPAGACION-DF-v1|" + claim_id);
  (2) sus componentes: para cada país de g*, la afirmación country conditional_full y las ci-d (domestic_unchanged),
      ci-df y ci-f (conditional_full) con la misma (preregistro, tipo, diseño, cota, bloque, capa);
  (3) casos difíciles: la ci-df del diseño con MAYOR k_max (K1 máxima: el ínfimo más exigente) y la de MENOR k_min
      (el supremo más alto), con su country conditional_full y las componentes de esta.
Fundamento: review/FUNDAMENTO_INFIMOS_DF.md §4. Hechos usados:
  - K1_c(θ) = k_c (1 − s(θ)), k_c = n_min/(s_π gain) por contexto, s = q_pot = κ̃ (a − 1)/(a − ρ) (cobertura.g_enclosure);
    G_c = C2_df(θ) − k_c (1 − s(θ)) es decreciente en k_c: inf_ω usa k* = max_c k_c (c* su contexto), sup_ω usa min_c k_c;
  - sup_ω G (ci-df): C2 <= U_sup (supremo cerrado de C2 df, SRED, autenticado) y s <= s_max ⇒ G <= U_sup − k_min (1 − s_max);
    el punto p⁺ del supremo tiene s(p⁺) = s_max (κ̃ = 0,2, ρ = 1): L = C2(p⁺).lo − K1_c(p⁺).hi en el MISMO ω (conjunta =
    individual, se comprueba s(p⁺) = s_max);
  - inf_ω G (ci-df): rama y cota en (a, κ̃, φ) con la cota CONJUNTA afín en s («todos formales», lema de
    inf_cota_formal_v2): para τ común admisible en la caja, G >= τ_d r* + s (D(τ) + k*) − k*, mínimo en s.lo o s.hi
    (D de inf_df_bb_v3; los demás ejes en su rango completo, ver inf_df_bb_v4); además G >= s k* − k* (C2 >= 0).
    U: min_j [U_C2(p_j) − K1_c*(p_j).lo] en los puntos admisibles p_j de <puntos_U.json> (techo v3 certificado), con C2 y
    K1 en el MISMO p_j; el mejor se recomprueba con cobertura.g_enclosure;
  - country conditional_full = unión de sus instrumentos (d, df, f) ⇒ sup = max y inf = min de los de sus ci; global =
    unión de sus países. Se COMPRUEBA que los contextos de la country/global son exactamente la unión de los de sus ci.
Extremos ci-d y ci-f: de sus entregas (autenticados por inventario): sup ci-d (extremos_df_d), inf ci-d (producción
candidata de cierre_df_paso4), sup e inf ci-f (cierre_candidato).
"""
from __future__ import annotations

import hashlib
import heapq
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

AREA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AREA / "integracion/src"))
import paper2b  # noqa: E402

assert Path(paper2b.__file__).resolve().parent == (AREA / "integracion/src/paper2b").resolve(), "PAPER2B_NO_AISLADO"
from codigo import extremos_dfd as XD  # noqa: E402
from codigo import extremos_G as EG  # noqa: E402
from codigo import inf_df_bb_v3 as B3  # noqa: E402
from codigo import cota_un_umbral_v2 as CU  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from codigo.demo.cobertura_compartida import q_pot_exact  # noqa: E402
from paper2b import cobertura as COV  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2_G = 1e-4
EPS = 0.01
REGLA = "SEL-PROPAGACION-DF-v1"
T = N.ROOT / "tmp"
SRC = {
    "RES": ("resolucion_3_7_2026-10-04_lima1941", "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"),
    "XDD": ("extremos_df_d_3_7_2026-10-05_lima0738", "116a3f06bb8f5dc449e6c9921a6fd4600abb2f349bb61b3ee8667b412d796bd4"),
    "CAN": ("cierre_candidato_3_7_2026-10-04_lima2103", "ea126009763844cf58f365fc5b9c8e68f8141a4302be59562e0b914094e0d9db"),
    "PRV": ("cierre_df_paso4_3_7_2026-10-05_lima1958", "f62789edc1e7f22c307e23cad95d71dcdff07f99715c63d5dbea9f5d0a991f8c"),
}
EJES = ("a", "kappa_tilde", "phi", "rho", "eta_f")


def auth(clave, rel):
    base, h = SRC[clave]
    return EG.auth(T / base, h, rel)


def campos(cid):
    p = cid.split(":")
    if p[3] == "ci":
        return {"pid": p[1], "kind": p[2], "fam": "ci", "pais": p[4], "j": p[5], "avail": p[6], "dis": p[7], "resto": tuple(p[8:])}
    if p[3] == "c":
        return {"pid": p[1], "kind": p[2], "fam": "c", "pais": p[4], "scen": p[5], "dis": p[6], "resto": tuple(p[7:])}
    return {"pid": p[1], "kind": p[2], "fam": "g", "scen": p[4], "dis": p[5], "resto": tuple(p[6:])}


def ci_id(pid, kind, pais, j, dis, resto):
    avail = "domestic_unchanged" if j == "d" else "conditional_full"
    return ":".join(["CLM", pid, kind, "ci", pais, j, avail, dis] + list(resto))


def c_id(pid, kind, pais, dis, resto):
    return ":".join(["CLM", pid, kind, "c", pais, "conditional_full", dis] + list(resto))


def k_iv(c):
    return Iv(c.n_min, c.n_min) / (Iv(c.s_pi, c.s_pi) * Iv(c.gain, c.gain))


def ctx_key(c):
    return (c.design, c.instrument, tuple(c.bars), c.s_pi, c.s_t, c.eta_h, c.gain, c.n_min)


def cota_G(th, fixed, dis, td, tf, k):
    """Cota inferior conjunta de G = C2 − k (1 − s) en la caja θ con τ común (None si (P), (F), (I) no valen)."""
    if B3.cota_inf_tau_v3(th, fixed, dis, td, tf) is None:
        return None
    P = EM.IParams.from_primitive_box(th, fixed)
    Td, Tf = Iv(td, td), Iv(tf, tf)
    x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
    S = B3.s_rango(th)
    base = Td * x.rstar.v
    D = Tf * x.qstar.v * x.gf.v
    if dis == "N":
        D = D - Td * x.rstar.v * (1.0 + P.phi * x.tf.v)
    K = Iv(k, k)
    return min((base + Iv(s, s) * (D + K) - K).lo for s in (S.lo, S.hi))


def lb_G(th, fixed, dis, bd, bf, k, fr_d=(1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0), nbis=32):
    S = B3.s_rango(th)
    K = Iv(k, k)
    best = (min((Iv(s, s) * K - K).lo for s in (S.lo, S.hi)), (0.0, 0.0))    # C2 >= 0
    ok = lambda a, b: B3.cota_inf_tau_v3(th, fixed, dis, a, b) is not None  # noqa: E731
    lo, hi = 0.0, bd
    for _ in range(nbis + 8):
        m = 0.5 * (lo + hi)
        if m > 0 and ok(m, 0.0):
            lo = m
        else:
            hi = m
    for fr in fr_d:
        td = fr * lo
        a, b = 0.0, bf
        for _ in range(nbis):
            m = 0.5 * (a + b)
            if ok(td, m):
                a = m
            else:
                b = m
        for kk in (1.0, 0.85, 0.7, 0.55, 0.4, 0.25):
            tf = kk * a
            if td == 0.0 and tf == 0.0:
                continue
            v = cota_G(th, fixed, dis, td, tf, k)
            if v is not None and v > best[0]:
                best = (v, (td, tf))
    return best


def anchura(th, p, full):
    """Anchura normalizada: κ̃ en escala logarítmica (su escala relevante es relativa, cerca de κ̃_min), a y φ lineales."""
    if p == "kappa_tilde":
        return math.log(th[p][1] / th[p][0]) / math.log(full[p][1] / full[p][0])
    return (th[p][1] - th[p][0]) / (full[p][1] - full[p][0])


def lb_umbral(th, fixed, dis, bd, bf, k, semilla=None):
    cc = CU.CotaCaja(th, fixed, dis)
    v, t = CU.mejor_tau(cc, bd, bf, k=k, semilla=semilla, pasos=6 if semilla is not None else 14)
    if semilla is not None:                       # además la rejilla completa si la semilla no da nada útil
        S = cc.S
        triv = min((Iv(s, s) * Iv(k, k) - Iv(k, k)).lo for s in (S.lo, S.hi))
        if v <= triv:
            v, t = CU.mejor_tau(cc, bd, bf, k=k)
    return v, t, cc.evaluaciones


def perdida(th, p, k, fixed):
    """Pérdida estimada de la cota conjunta por la anchura del eje p (solo orienta la partición)."""
    a0, a1 = th["a"]
    r0, r1 = th["rho"]
    k0_, k1_ = th["kappa_tilde"]
    if p == "a":
        u1, zc1 = th["u_theta"][1], th["z_cost"][1]
        c2d = zc1 ** (-u1 * (a1 - 1.0)) / (th["beta_tilde"][1] + 1.0)
        return (a1 - a0) * (4.14 * c2d + k * k0_ * (1.0 - r0) / (a0 - r0) ** 2)
    if p == "kappa_tilde":
        return k * (a1 - 1.0) / (a1 - r1) * (k1_ - k0_)
    if p == "rho":
        return k * k1_ * (a1 - 1.0) / (a0 - r1) ** 2 * (r1 - r0)
    if p == "eta_f":
        u1, zc1 = th["u_theta"][1], th["z_cost"][1]
        c2d = zc1 ** (-u1 * (a1 - 1.0)) / (th["beta_tilde"][1] + 1.0)
        return 0.01 * c2d * (th[p][1] - th[p][0])
    return 1e-4 * (th[p][1] - th[p][0])


def inf_bb(full, fixed, dis, bd, bf, k, U, tope):
    t0 = time.time()
    v0, t0_, ne = lb_umbral(full, fixed, dis, bd, bf, k)
    heap, cont, n, nev = [(v0, 0, full, t0_)], 1, 0, ne
    estado = "tope"
    usos = {p: 0 for p in EJES}
    while heap:
        L = heap[0][0]
        if L > U:
            return {"L": L, "estado": "INCOMPATIBLE_L_MAYOR_QUE_U", "divisiones": n}
        if U - L <= T2_G:
            estado = "convergido"
            break
        if time.time() - t0 > tope:
            break
        plb, _, th, tau = heapq.heappop(heap)
        n += 1
        ls = [p for p in EJES if th[p][1] > th[p][0]]
        if not ls:
            heapq.heappush(heap, (plb, cont, th, tau))
            estado = "caja_degenerada_viva"
            break
        p = max(ls, key=lambda q: perdida(th, q, k, fixed))
        usos[p] += 1
        lo, hi = th[p]
        m = math.sqrt(lo * hi) if p == "kappa_tilde" else lo + (hi - lo) / 2
        for h in (dict(th, **{p: (lo, m)}), dict(th, **{p: (m, hi)})):
            v, t, ne = lb_umbral(h, fixed, dis, bd, bf, k, semilla=tau if tau and tau != (0.0, 0.0) else None)
            nev += ne
            heapq.heappush(heap, (max(v, plb), cont, h, t if v >= plb else tau))
            cont += 1
    return {"L": heap[0][0] if heap else U, "estado": estado, "divisiones": n, "evaluaciones_cota": nev, "usos_por_eje": usos,
            "segundos": round(time.time() - t0, 1), "vivas": len(heap),
            "caja_de_menor_cota": {q: list(v) for q, v in heap[0][2].items()} if heap else None, "tau": heap[0][3] if heap else None}


def main():
    dis, pts_p, out, tope = sys.argv[1], [Path(x) for x in sys.argv[2].split(",")], Path(sys.argv[3]), float(sys.argv[4])
    tpa = float(sys.argv[5])
    solo = sys.argv[6]
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    reg = auth("RES", "demo/registro/registro_candidato_v4.json")["afirmaciones"]
    claims = {c.claim_id: c for c in ctx.claims}
    N.need(set(claims) == set(reg), "REGISTRO_Y_CONTEXTO_DISTINTOS")
    Gr = XD.grupo(dis, "df")
    full, fixed_g, bd, bf = Gr["full"], Gr["fixed"], Gr["bd"], Gr["bf"]
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "propagación a extremos de G de ci-df, country y global (cf)",
           "diseno": dis, "regla": REGLA, "identidad_sha256": ctx.identity_sha256, "T2_G": T2_G}
    # ---------------------------------------------------- familias: qué usa df (instrumentos de cada afirmación)
    fam = Counter()
    for cid, cl in claims.items():
        f = campos(cid)
        fam[(f["fam"], f.get("j") or f.get("scen"), "usa_df" if "df" in cl.instruments else "no_usa_df")] += 1
    doc["familias_instrumentos"] = {"|".join(k): v for k, v in sorted(fam.items())}
    # ---------------------------------------------------- selección (antes de cualquier cota)
    cidf = sorted(c for c in claims if campos(c)["fam"] == "ci" and campos(c)["j"] == "df" and campos(c)["dis"] == dis)
    st_all = EG.preparar(ctx, dis, cidf)
    fixed = st_all["fixed"]
    for kf in ("gamma", "z_m", "bar_tau_d", "bar_tau_f"):
        N.need(float(fixed[kf]) == float(fixed_g[kf]), "FIJO_DISTINTO:" + kf)
    root = {p: (st_all["axes"][p][0][0], st_all["axes"][p][-1][1]) for p in COV.STRUCT}
    N.need(all(abs(root[p][0] - full[p][0]) <= 1e-12 and abs(root[p][1] - full[p][1]) <= 1e-12 for p in full), "SOPORTE_DISTINTO_DEL_DE_C2")
    kmax = {c: max(k_iv(x).hi for x in st_all["univ"][c]) for c in cidf if st_all["univ"][c]}
    kmin = {c: min(k_iv(x).lo for x in st_all["univ"][c]) for c in cidf if st_all["univ"][c]}
    gcf = sorted((c for c in claims if campos(c)["fam"] == "g" and campos(c)["scen"] == "conditional_full" and campos(c)["dis"] == dis),
                 key=lambda c: hashlib.sha256((REGLA + "|" + c).encode()).hexdigest())
    g_star = gcf[0]
    fg = campos(g_star)
    sel_c = [c_id(fg["pid"], fg["kind"], p, dis, fg["resto"]) for p in claims[g_star].countries]
    dif = [max(kmax, key=kmax.get), min(kmin, key=kmin.get)]
    for c in dif:
        f = campos(c)
        sel_c.append(c_id(f["pid"], f["kind"], f["pais"], dis, f["resto"]))
    sel_c = list(dict.fromkeys(sel_c))
    comp = {}
    for c in sel_c:
        f = campos(c)
        comp[c] = {j: ci_id(f["pid"], f["kind"], f["pais"], j, dis, f["resto"]) for j in ("d", "df", "f")}
        N.need(all(x in claims for x in comp[c].values()) and c in claims, "COMPONENTE_INEXISTENTE:" + c)
    sel_df = sorted({comp[c]["df"] for c in sel_c})
    doc["seleccion"] = {"g": g_star, "country": sel_c, "ci_df": sel_df, "dificiles": {"k_max_mayor": dif[0], "k_min_menor": dif[1]},
                        "escrita_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    N.write_json_atomic(out, doc)
    # ---------------------------------------------------- universos: country/global = unión de sus ci
    st_cg = EG.preparar(ctx, dis, sel_c + [g_star] + sorted({x for c in sel_c for x in comp[c].values()}))
    uni = {}
    for c in sel_c:
        u = Counter(ctx_key(x) for x in st_cg["univ"][c])
        v = Counter(ctx_key(x) for j in ("d", "df", "f") for x in st_cg["univ"][comp[c][j]])
        uni[c] = {"contextos": sum(u.values()), "union_de_ci": sum(v.values()), "iguales": u == v}
    ug = Counter(ctx_key(x) for x in st_cg["univ"][g_star])
    vg = sum((Counter(ctx_key(x) for j in ("d", "df", "f") for x in st_cg["univ"][comp[c][j]]) for c in sel_c
              if campos(c)["pid"] == fg["pid"] and campos(c)["resto"] == fg["resto"] and campos(c)["kind"] == fg["kind"]), Counter())
    uni[g_star] = {"contextos": sum(ug.values()), "union_de_ci": sum(vg.values()), "iguales": ug == vg}
    doc["universos"] = uni
    # ---------------------------------------------------- sup ci-df
    sred = auth("PRV", "demo/hito2/sred_%s_df.json" % dis)
    pplus = {p: float(v) for p, v in sred["punto_cota_inferior"].items() if p in COV.STRUCT}
    bxp = {p: (pplus[p], pplus[p]) for p in COV.STRUCT}
    N.need(COV.box_admissible(bxp, fixed), "P_MAS_NO_ADMISIBLE")
    s_p, s_max = q_pot_exact(bxp), q_pot_exact(root).hi
    C2p = Iv(sred["L"], sred["U"])
    doc["sup_C2"] = {"L": sred["L"], "U": sred["U"], "p_mas": pplus, "s_p_mas": [s_p.lo, s_p.hi], "s_max": s_max,
                     "conjunta_igual_individual": s_p.hi >= s_max}
    # ---------------------------------------------------- puntos U de inf (techo v3 certificado por diseño)
    puntos, fuentes = [], []
    for fp in pts_p:                                   # varios archivos de techo v3 (certificar_inf_df / certificar_puntos)
        pu = json.loads(fp.read_text(encoding="utf-8"))
        fuentes.append({"archivo": fp.as_posix(), "sha256": N.sha(fp.read_bytes())})
        for f in pu["filas"]:
            if f.get("admisible") and "U" in f and not f.get("incompatible"):
                N.need(f.get("diseno", dis) == dis and all(full[p][0] <= f["theta"][p] <= full[p][1] for p in full), "PUNTO_U_INVALIDO")
                bx = {p: (f["theta"][p], f["theta"][p]) for p in COV.STRUCT}
                puntos.append((f["theta"], bx, f["U"], f["L_punto"], q_pot_exact(bx)))
    N.need(puntos, "SIN_PUNTOS_U")
    doc["puntos_U"] = {"fuentes": fuentes, "n": len(puntos)}
    res = {}
    a_calcular = sel_df if solo == "todos" else [sel_df[int(i)] for i in solo.split(",")]
    doc["calcula_este_proceso"] = a_calcular
    for cid in a_calcular:
        if time.time() - t0 > tope:
            res[cid] = {"estado": "no_procesada_por_tope"}
            continue
        cx = st_all["univ"][cid]
        ks = [(k_iv(x), x) for x in cx]
        k_lo, c_lo = min(ks, key=lambda t: t[0].lo)
        k_hi, c_hi = max(ks, key=lambda t: t[0].hi)
        # sup
        U_sup = (Iv(sred["U"], sred["U"]) - k_lo * (1.0 - Iv(s_max, s_max))).hi
        L_sup = (Iv(sred["L"], sred["L"]) - k_lo * (1.0 - s_p)).lo
        g_dir = COV.g_enclosure(st_all["model"], bxp, c_lo, fixed, C2p)
        # inf: U en los puntos (mismo ω), L por rama y cota conjunta
        U_inf, arg = math.inf, None
        for th, bx, u2, l2, s in puntos:
            u = (Iv(u2, u2) - k_hi * (1.0 - s)).hi
            if u < U_inf:
                U_inf, arg = u, (th, bx, u2, l2)
        gi = COV.g_enclosure(st_all["model"], arg[1], c_hi, fixed, Iv(arg[3], arg[2]))
        bb = inf_bb(full, fixed, dis, bd, bf, k_hi.hi, U_inf, min(tpa, max(30.0, tope - (time.time() - t0))))
        r = {"categoria_v4": reg[cid]["categoria"], "contextos": len(cx), "k_min": k_lo.lo, "k_max": k_hi.hi,
             "sup_G": [L_sup, U_sup], "brecha_sup": U_sup - L_sup, "sup_directo_g_enclosure": [g_dir.lo, g_dir.hi] if g_dir else None,
             "inf_G": [bb["L"], U_inf], "brecha_inf": U_inf - bb["L"], "inf_bb": bb, "punto_U_inf": arg[0],
             "inf_directo_g_enclosure": [gi.lo, gi.hi] if gi else None,
             "testigo_sup": {"punto": pplus, "contexto": list(ctx_key(c_lo)), "indice_contexto": cx.index(c_lo)},
             "testigo_inf": {"punto": arg[0], "contexto": list(ctx_key(c_hi)), "indice_contexto": cx.index(c_hi)}}
        r["estado_sup"] = "convergida" if r["brecha_sup"] <= T2_G else "no_convergida"
        r["estado_inf"] = "convergida" if r["brecha_inf"] <= T2_G and bb["estado"] == "convergido" else "no_convergida"
        r["coherente_v4"] = (r["categoria_v4"] != "cambio_de_signo_certificado") or (L_sup >= EPS and U_inf <= -EPS)
        res[cid] = r
        doc["ci_df"] = res
        N.write_json_atomic(out, doc)
    # ---------------------------------------------------- agregación country y global (cf)
    xdd = auth("XDD", "demo/extremos/extremos_G_d.json")["afirmaciones"]
    pid_ = auth("PRV", "demo/hito2/produccion_inf_G_cid_%s.json" % dis)["afirmaciones"]
    xf = auth("CAN", "demo/extremos/extremos_G_f.json")["afirmaciones"]
    agg = {}
    for c in sel_c:
        d_, df_, f_ = comp[c]["d"], comp[c]["df"], comp[c]["f"]
        if df_ not in res or "sup_G" not in res[df_]:
            agg[c] = {"estado": "componente_df_sin_calcular"}
            continue
        sups = {"d": xdd[d_]["sup_G"], "df": res[df_]["sup_G"], "f": xf[f_]["sup_G"]}
        infs = {"d": pid_[d_]["inf_G"], "df": res[df_]["inf_G"], "f": xf[f_]["inf_G"]}
        js = max(sups, key=lambda j: sups[j][1])
        ji = min(infs, key=lambda j: infs[j][0])
        sup = [max(v[0] for v in sups.values()), max(v[1] for v in sups.values())]
        inf = [min(v[0] for v in infs.values()), min(v[1] for v in infs.values())]
        agg[c] = {"categoria_v4": reg[c]["categoria"], "sup_G": sup, "inf_G": inf, "brecha_sup": sup[1] - sup[0], "brecha_inf": inf[1] - inf[0],
                  "instrumento_sup": js, "instrumento_inf": ji, "universo_igual_a_union": uni[c]["iguales"],
                  "componentes_convergidas": {"sup_d": xdd[d_]["estado_sup"], "inf_d": pid_[d_]["estado_inf"], "f": xf[f_]["estado"],
                                              "sup_df": res[df_]["estado_sup"], "inf_df": res[df_]["estado_inf"]}}
    ps = [c for c in sel_c if campos(c)["pid"] == fg["pid"] and campos(c)["resto"] == fg["resto"] and campos(c)["kind"] == fg["kind"]]
    if all("sup_G" in agg.get(c, {}) for c in ps):
        sup = [max(agg[c]["sup_G"][0] for c in ps), max(agg[c]["sup_G"][1] for c in ps)]
        inf = [min(agg[c]["inf_G"][0] for c in ps), min(agg[c]["inf_G"][1] for c in ps)]
        agg[g_star] = {"categoria_v4": reg[g_star]["categoria"], "paises": list(claims[g_star].countries), "sup_G": sup, "inf_G": inf,
                       "brecha_sup": sup[1] - sup[0], "brecha_inf": inf[1] - inf[0], "universo_igual_a_union": uni[g_star]["iguales"]}
    for c, v in agg.items():
        if "sup_G" in v:
            v["convergida"] = v["brecha_sup"] <= T2_G and v["brecha_inf"] <= T2_G
            v["coherente_v4"] = (v["categoria_v4"] != "cambio_de_signo_certificado") or (v["sup_G"][0] >= EPS and v["inf_G"][1] <= -EPS)
    doc["agregadas"] = agg
    doc["resumen"] = {"ci_df": len(res), "ci_df_sup_convergidas": sum(1 for v in res.values() if v.get("estado_sup") == "convergida"),
                      "ci_df_inf_convergidas": sum(1 for v in res.values() if v.get("estado_inf") == "convergida"),
                      "agregadas": len(agg), "agregadas_convergidas": sum(1 for v in agg.values() if v.get("convergida")),
                      "universos_iguales": all(v["iguales"] for v in uni.values()),
                      "coherentes_v4": all(v.get("coherente_v4", False) for v in list(res.values()) + list(agg.values()) if "sup_G" in v)}
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    print(json.dumps(doc["resumen"], ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
