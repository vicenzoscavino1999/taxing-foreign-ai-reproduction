"""rem128 — CERTIFICADO DIAGNÓSTICO (NO PRODUCTIVO, candidato para revisión) del ALCANCE del supremo de R en una clave G con rho = 1
y menú df, sin rama y cota nueva: no llama a capture_ceiling ni a sup_bound; usa el valor certificado PERSISTIDO del techo.

Teoría (model.py de C0; la regla S13 está en partition(): F1-F0 idénticamente nula ⇒ no adopta). Con rho = 1 cada diferencia de ganancias es
T(z) = A z^theta + L z = z (A z^(theta-1) + L) con L = B + C, y para z >= z_m = 1 se cumple z^(theta-1) >= 1 (theta > 1). Sobre la caja de
tasas T = [dl, dh] × [fl, fh] (cerrada) se comprueban POR INTERVALOS (redondeo hacia afuera, elementales demostrados de C0):
  H1  F0-I0 > 0 para todo z >= 1  ⇐ delta − tau_d·beta > 0                      (estatus previo F en todo el soporte)
  H2  I1-F0 < 0 para todo z >= 1  ⇐ tau_d·beta + gamma − kappa0 < delta          (la adopción informal nunca gana)
  H3  F1-I1 > 0 para todo z >= 1  ⇐ tau_d·beta + t~_d·gamma + kappa0·phi·t~_f < delta
  F1-F0 = c(tau)·z con c = (1 − t~_d) gamma − k_F (la curva de salto de model.jump_functions). Por H1–H3 y la regla de partition():
  c > 0 ⇒ todo el soporte adopta formal (FF) y R = R+(tau) = m1 [gamma tau_d r* + kappa0 tau_f q* x_f^-phi], m1 = a z_m/(a − 1);
  c <= 0 ⇒ ningún tipo adopta (NF; en c = 0 por S13) y R = 0.
  H4  R+ estrictamente creciente en tau_d y tau_f: 1 − (1 + eta_d) tau_d > 0 y 1 − (1 + eta_f − phi) tau_f > 0 en T; gamma, kappa0, m1 > 0.
  H5  c estrictamente decreciente: dc/dtau_d = −gamma x_d^eta_d < 0; dc/dtau_f = −kappa0 phi x_f^(alpha−1) (x_f + phi tau_f) < 0
      (alpha = eta_f − phi; derivada de t~_f verificada simbólicamente; se contrasta además con el gradiente AD de C0).
  H6  c(dl, fl) > 0 (región de adopción no vacía) y c(dh, fh) < 0 (la curva corta la caja).
Teorema (H1–H6): el supremo de R en T NO se alcanza. Si tau* lo alcanzara, R(tau*) > 0 exige c(tau*) > 0; si tau*_f < fh, subir tau_f un
poco mantiene c > 0 (continuidad) y aumenta R+ (H4); si tau*_f = fh, entonces tau*_d < dh (H6) y lo mismo con tau_d: contradicción. El
supremo es max de R+ sobre K = {c >= 0} ∩ T, que se toma en la curva Γ = {c = 0}; en Γ el valor de R es 0 (S13) y su límite lateral desde
c > 0 es R+. Si además h'(tau_f) = R+_f − R+_d c_f / c_d > 0 en una caja que contiene Γ, el máximo en Γ está en P1 = (tau_d*, fh), con
c(tau_d*, fh) = 0 encerrado por bisección: S = R+(P1), testigo lateral.
I2 (tras el intento I1, conservado en certificado_salto_I1.py con su salida CERTIFICADO_d59edf8a.json): los encierros naturales sobre la
caja entera sobreestiman por dependencia (M llegaba a 1,29 y el gradiente AD de t~_d a [−0,63; 2,5]); H1–H3 se acotan ahora en la esquina
desfavorable, con la monotonía demostrada por derivadas cerradas de factores positivos, y el signo de h' se toma de su factor B.
Si c(dh, fh) > 0, c > 0 en toda la caja: R = R+ continua y creciente, supremo ALCANZADO en (dh, fh). Cualquier hipótesis no demostrada, o
una clave fuera de este alcance (diseño N, rho < 1, z_m != 1, menú distinto de df), da «no_decidido»: nunca se promueve.
Uso (diagnóstico de la clave real): python -B -I certificado_salto.py <raiz> <manifiesto_ABL_ENF> <enf_techos.jsonl> <sha256_techos> <clave16> <salida.json>"""
import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
C0 = AQUI.parents[2] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
if str(C0 / "src") not in sys.path:
    sys.path.insert(0, str(C0 / "src"))
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import model as M  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
CODIGO_C0 = ("model.py", "encierros_modelo.py", "elementales.py", "intervalos.py")


def _iv(x: Iv):
    return [x.lo, x.hi]


def _fun(P, Td: Iv, Tf: Iv, grad: bool):
    """(c, R+) como AD de C0 sobre la caja (tax_side de encierros_modelo: mismas fórmulas que model.py)."""
    tdv, tfv = EM.AD.var(Td, 0, grad), EM.AD.var(Tf, 1, grad)
    x = EM.tax_side(P, tdv, tfv, EM.AD.var(P.phi, 2, grad))
    c = EM.sub(EM.mul(x.one_td, P.gamma), x.kF)
    m1 = P.a * P.z_m / (P.a - 1.0)
    rp = EM.mul(m1, EM.add(EM.mul(EM.mul(tdv, x.rstar), P.gamma), EM.mul(EM.mul(EM.mul(tfv, x.qstar), P.kappa0), x.gf)))
    return c, rp, x


def _c(P, td: float, tf: float) -> Iv:
    return _fun(P, Iv.point(td), Iv.point(tf), False)[0].v


def _biseccion(f, lo: float, hi: float, n: int = 400):
    """Raíz de f decreciente en [lo, hi] con f(lo) > 0 > f(hi) demostrados: estrecha mientras el signo se decide."""
    for _ in range(n):
        m = 0.5 * (lo + hi)
        if not (lo < m < hi):
            break
        v = f(m)
        if v.lo > 0.0:
            lo = m
        elif v.hi < 0.0:
            hi = m
        else:
            break
    return lo, hi


def certificar(prim: dict, diseno: str, j: str, tau: dict, cotas_R=None) -> dict:
    """Devuelve el certificado (dict). cotas_R = (lower_R, upper_R) persistidas del techo, si existen."""
    out = {"estado": "no_decidido", "hipotesis": {}, "motivo": None}
    hip = out["hipotesis"]
    try:
        state = M.state_from_primitives({p: float(v) for p, v in prim.items()})
    except M.DomainError as ex:
        out["motivo"] = "DOMINIO:%s" % ex
        return out
    dl, dh, fl, fh = (float(tau[k]) for k in ("tau_d_lower", "tau_d_upper", "tau_f_lower", "tau_f_upper"))
    cerr = all(tau.get(k) is True for k in ("tau_d_lower_closed", "tau_d_upper_closed", "tau_f_lower_closed", "tau_f_upper_closed"))
    alcance = {"diseno_G": diseno == "G", "rho_1": state.rho == 1.0, "z_m_1": state.z_m == 1.0, "menu_df": j == "df",
               "caja_cerrada": cerr, "caja_admisible": 0.0 <= dl < dh < 1.0 and 0.0 <= fl < fh < 1.0}
    hip["H0_alcance_del_certificado"] = alcance
    if not all(alcance.values()):
        out["motivo"] = "FUERA_DEL_ALCANCE_DEL_CERTIFICADO"
        return out
    P = EM.IParams.from_state(state)
    Td, Tf = Iv(dl, dh), Iv(fl, fh)
    c_b, rp_b, x = _fun(P, Td, Tf, True)
    d = P.delta
    # I2: las cantidades monótonas se acotan en la esquina desfavorable; la monotonía se demuestra con las derivadas en forma cerrada
    # (factores positivos, sin dependencia): t~_d' = x_d^eta_d; t~_f' = x_f^(alpha-1) (1 - (1 - phi) tau_f). Los encierros AD sobre la caja
    # entera (sobreestimados por dependencia en el intento I1) quedan solo como información.
    alpha = P.eta_f - P.phi
    xd_pow, xf_pow, xf_fac = EM.ipow(1.0 - Td, P.eta_d), EM.ipow(1.0 - Tf, alpha - 1.0), 1.0 - (1.0 - P.phi) * Tf
    td_crec, tf_crec = xd_pow.lo > 0.0, xf_pow.lo > 0.0 and xf_fac.lo > 0.0
    _, _, xc = _fun(P, Iv.point(dh), Iv.point(fh), False)
    h1 = (d - dh * P.beta)
    h2 = (dh * P.beta + P.gamma - P.kappa0)
    h3 = (dh * P.beta + xc.td.v * P.gamma + P.kappa0 * P.phi * xc.tf.v)
    hip["H1_previo_F"] = {"delta_menos_tau_d_beta_en_tau_d_sup": _iv(h1), "theta": _iv(P.theta), "beta": _iv(P.beta),
                          "ok": h1.lo > 0.0 and P.theta.lo > 1.0 and P.beta.lo >= 0.0 and dl >= 0.0}
    hip["H2_informal_nunca"] = {"L_I1F0_en_tau_d_sup": _iv(h2), "delta": _iv(d), "ok": h2.hi < d.lo and P.beta.lo >= 0.0}
    hip["H3_F1_sobre_I1"] = {"M_en_la_esquina_superior": _iv(h3), "delta": _iv(d), "t_d_creciente": td_crec, "t_f_creciente": tf_crec,
                             "M_box_AD_informativo": _iv(dh * P.beta + x.td.v * P.gamma + P.kappa0 * P.phi * x.tf.v),
                             "ok": h3.hi < d.lo and td_crec and tf_crec and P.beta.lo >= 0.0 and P.gamma.lo > 0.0 and (P.kappa0 * P.phi).lo >= 0.0}
    m4d, m4f = 1.0 - (1.0 + P.eta_d) * Td, 1.0 - (1.0 + alpha) * Tf
    m1 = P.a * P.z_m / (P.a - 1.0)
    hip["H4_R_mas_creciente"] = {"factor_d": _iv(m4d), "factor_f": _iv(m4f), "gamma": _iv(P.gamma), "kappa0": _iv(P.kappa0), "m1": _iv(m1),
                                 "grad_AD_informativo": [_iv(g) for g in rp_b.g[:2]],
                                 "ok": m4d.lo > 0.0 and m4f.lo > 0.0 and P.gamma.lo > 0.0 and P.kappa0.lo > 0.0 and m1.lo > 0.0}
    hip["H5_c_decreciente"] = {"x_d_pot_eta_d": _iv(xd_pow), "x_f_pot_alpha_menos_1": _iv(xf_pow), "uno_menos_(1-phi)_tau_f": _iv(xf_fac), "phi": _iv(P.phi),
                               "grad_AD_c_informativo": [_iv(g) for g in c_b.g[:2]],
                               "ok": P.gamma.lo > 0.0 and P.kappa0.lo > 0.0 and P.phi.lo > 0.0 and td_crec and tf_crec}
    c00, c11 = _c(P, dl, fl), _c(P, dh, fh)
    hip["H6_esquinas"] = {"c_inferior": _iv(c00), "c_superior": _iv(c11), "region_no_vacia": c00.lo > 0.0, "curva_corta_la_caja": c11.hi < 0.0,
                          "sin_curva": c11.lo > 0.0}
    base = all(hip[k]["ok"] for k in ("H1_previo_F", "H2_informal_nunca", "H3_F1_sobre_I1", "H4_R_mas_creciente", "H5_c_decreciente"))
    if not base or not c00.lo > 0.0:
        out["motivo"] = "HIPOTESIS_NO_DEMOSTRADAS"
        return out
    if c11.lo > 0.0:
        v = _fun(P, Iv.point(dh), Iv.point(fh), False)[1].v
        out.update(estado="alcanzado_demostrado", motivo=None, punto=[dh, fh], valor_R=_iv(v))
        return out
    if not c11.hi < 0.0:
        out["motivo"] = "ESQUINA_SOBRE_LA_CURVA_NO_DECIDIDA"
        return out
    # ---- teorema: no alcanzado. Testigo lateral en Γ.
    out.update(estado="no_alcanzado_demostrado", motivo=None)
    a_d, b_d = _biseccion(lambda t: _c(P, t, fh), dl, dh)
    a_f, b_f = (_biseccion(lambda t: _c(P, dh, t), fl, fh) if _c(P, dh, fl).lo > 0.0 else (fl, fl))
    caja_g = (Iv(a_d, dh), Iv(a_f, fh))
    hp = None
    tiras, k = [caja_g], 0
    while k <= 6:
        # I2: h'(tau_f) = R+_f − R+_d c_f / c_d = m1 kappa0 x_f^(alpha−1) · B, con
        # B = (1 − (1 + alpha) tau_f) − phi (1 − (1 − phi) tau_f) (1 − (1 + eta_d) tau_d) / (1 − tau_d); signo(h') = signo(B).
        vals = [(1.0 - (1.0 + alpha) * Bf) - P.phi * (1.0 - (1.0 - P.phi) * Bf) * (1.0 - (1.0 + P.eta_d) * Bd) / (1.0 - Bd) for (Bd, Bf) in tiras]
        ok = all(v.lo > 0.0 for v in vals)
        if ok:
            hp = Iv(min(v.lo for v in vals), max(v.hi for v in vals))
            break
        k += 1
        n = 2 ** k
        cortes = [a_f + (fh - a_f) * i / n for i in range(n)] + [fh]
        raiz = [(_biseccion(lambda t, y=y: _c(P, t, y), dl, dh)) for y in cortes]
        tiras = [(Iv(raiz[i + 1][0], max(raiz[i][1], raiz[i + 1][1])), Iv(cortes[i], cortes[i + 1])) for i in range(n)]
    S = _fun(P, Iv(a_d, b_d), Iv.point(fh), False)[1].v
    out["curva"] = {"tau_d_estrella_en_tau_f_sup": [a_d, b_d], "ancho": b_d - a_d, "tau_f_estrella_en_tau_d_sup": [a_f, b_f],
                    "caja_que_contiene_gamma": [_iv(caja_g[0]), _iv(caja_g[1])]}
    if hp is not None:
        out["maximo_en_gamma"] = {"signo_de_h_prima_B": _iv(hp), "subdivision": k, "en": "P1 = (tau_d*, tau_f superior)"}
        out["testigo_lateral"] = {"tau_d": [a_d, b_d], "tau_f": fh, "lado": "c > 0 (FF, adopción formal)", "eje": "tau_d desde abajo",
                                  "limite_R": _iv(S), "valor_en_la_curva_R": 0.0, "limite_desde_c_negativo_R": 0.0}
        out["supremo_R_independiente"] = _iv(S)
    else:
        out["maximo_en_gamma"] = {"derivada_a_lo_largo_de_gamma": None, "en": "no decidido (el no alcance sigue demostrado)"}
    if cotas_R is not None:
        lo, hi = float(cotas_R[0]), float(cotas_R[1])
        inter = None if hp is None else (max(lo, S.lo), min(hi, S.hi))
        out["cotas_persistidas_R"] = [lo, hi]
        out["compatibilidad"] = {"interseccion": None if inter is None or inter[0] > inter[1] else list(inter),
                                 "compatible": inter is None or inter[0] <= inter[1], "supremo_positivo": lo > 0.0}
        if not out["compatibilidad"]["compatible"] or not lo > 0.0:
            out.update(estado="no_decidido", motivo="COTA_PERSISTIDA_INCOMPATIBLE")
    out["B_pot"] = _iv(P.B_pot)
    return out


def laterales(prim: dict, diseno: str, cert: dict, pasos=(1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10)) -> list:
    """Pruebas puntuales y laterales (DIAGNÓSTICO) con model.evaluate de C0 en tau_f superior, a ambos lados de P1."""
    s = M.state_from_primitives({p: float(v) for p, v in prim.items()})
    a_d, b_d = cert["curva"]["tau_d_estrella_en_tau_f_sup"]
    tf = cert["testigo_lateral"]["tau_f"]
    filas = []
    for h in pasos:
        for lado, td in (("c>0", a_d - h), ("c<0", b_d + h)):
            e = M.evaluate(s, td, tf, diseno)
            filas.append({"lado": lado, "paso": h, "tau_d": td, "tau_f": tf, "R": e.R, "CS": e.CS, "topologia": e.topology})
    return filas


def main(raiz, man_p, techos_p, sha_techos, clave16, salida):
    R = Path(raiz)
    b = Path(techos_p).read_bytes()
    assert H(b) == sha_techos, "TECHOS_NO_AUTENTICOS"
    rawm = Path(man_p).read_bytes()
    co = json.loads(rawm)["ABL-ENF"]
    filas = [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]
    t = [x for x in filas if x.get("clave_transformada_sha256") == clave16]
    assert len(t) == 1, "CLAVE_AUSENTE_O_DUPLICADA"
    t = t[0]
    cl = co["claves_recalculadas"][clave16]
    assert (t["parametros"], t["diseno"], t["j"], t["tau"]) == (cl["clave"], cl["diseno"], cl["j"], cl["tau"]), "FILA_DISTINTA_DEL_MANIFIESTO"
    cert = certificar(cl["clave"], cl["diseno"], cl["j"], cl["tau"], (t["lower_R"], t["upper_R"]))
    lat = laterales(cl["clave"], cl["diseno"], cert) if cert.get("testigo_lateral") else []
    doc = {"kind": "certificado-alcance-supremo-salto-rem128", "estado_documento": "DIAGNOSTICO_NO_PRODUCTIVO (candidato para revisión; no incorporado)",
           "clave": clave16, "clave_completa_sha256": cl["clave_completa_sha256"], "diseno": cl["diseno"], "j": cl["j"], "tau": cl["tau"], "primitivas": cl["clave"],
           "fuente_techo": {"ruta": str(Path(techos_p)), "sha256": sha_techos, "estado": t["estado"], "motivo": t["motivo"], "attained": t["attained"],
                            "lower_R": t["lower_R"], "upper_R": t["upper_R"], "C_2": t["C_2"], "error_normalizado": t["error_normalizado"],
                            "error_R": t["error_R"], "testigo": t["testigo"]},
           "manifiesto_sha256": H(rawm), "codigo_c0_sha256": {n: H((C0 / "src/paper2b" / n).read_bytes()) for n in CODIGO_C0},
           "certificador_sha256": H(AQUI.read_bytes()), "certificado": cert, "pruebas_laterales_model_evaluate": lat,
           "llamadas": {"capture_ceiling": 0, "sup_bound": 0, "busqueda_global": 0}}
    with Path(salida).open("x", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"estado": cert["estado"], "motivo": cert["motivo"], "hipotesis": {k: v.get("ok", v) for k, v in cert["hipotesis"].items()},
                      "curva": cert.get("curva"), "maximo_en_gamma": cert.get("maximo_en_gamma"), "testigo_lateral": cert.get("testigo_lateral"),
                      "compatibilidad": cert.get("compatibilidad"), "laterales": [(r["lado"], r["paso"], r["R"], r["topologia"]) for r in lat]},
                     ensure_ascii=False, indent=1))
    return 0 if cert["estado"] != "no_decidido" else 4


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:7]))
