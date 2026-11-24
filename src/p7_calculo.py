def derivar_k1(e, X, MC):
    """Ruta aceptada mínima de run.py:704-707 para UNA celda: Q = gcell.Q(bound); m = macro.bridge(shares, omega); lam = float(m.lambda_pi)
    si admisible; y = float(omega['gain_share']); K1 = external.K1(Q, dme, lam, y). Sin techos, supremos, modelo ni corrida."""
    g = e["grid"]
    gc = X.GridCell(g["country_id"], g["policy_variant_id"], g["regime_id"], g["requirement_basis"], g["xi"],
                    *(float(g[k]) for k in ("cost_gross", "F_admin", "F_trans", "F_leak", "F_fix", "F_fix_perp", "s_PB", "Q_grid")))
    Q = gc.Q(e["bound"])
    v = {k: MC.F(x) for k, x in e["omega"].items()}
    m = MC.bridge({k: MC.F(x) for k, x in e["shares"].items()}, v)
    adm = bool(m.admissible and v["eta_H"] > -1)                       # run.py:654
    lam = float(m.lambda_pi) if m.lambda_pi is not None else None      # run.py:655
    y = float(v["gain_share"])                                         # run.py:706
    dme = float(e["dme_gai"])
    k1 = X.K1(Q, dme, lam, y) if (adm and lam is not None) else None   # run.py:707
    return {"external_cell_id": gc.external_cell_id, "Q": Q, "lambda_pi": lam, "macro_admisible": adm, "razones_macro": list(m.reasons),
            "gain_share": y, "dme_gai": dme, "K1": k1}
