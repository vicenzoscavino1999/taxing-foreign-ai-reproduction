"""rem108 — CONEXIÓN AISLADA de L1-ELAST (F-ELAST: C1, C3 geometría, C4, T3–T5, E4) con la MISMA ruta que Run.frontier_rows del núcleo vigente,
sin cambiar el algoritmo: clave estructural almacenada (13 valores) → model.state(_to_state_prim) → model.frontier_grid(state, diseño, j, τ̄_d, τ̄_f,
frontier_n) → filas frontier_result (eps_dd, eps_df, eps_fd, eps_ff, s_P, regime…). NO repite techos. En esta ronda SOLO se prueba su estructura con
una clave SINTÉTICA; las 6 claves reales del lote quedan resueltas en LOTE1_MANIFIESTO.json, sin evaluar.
Uso: python -B -I -X utf8 conexion_frontera.py prueba-sintetica <raiz> <salida.json>"""
import json
import math
import sys
from pathlib import Path


def filas_frontera(RUN, M, valores, tau_dom, diseno, j, n=None, frontier_id="FRN:sintetica"):
    cfg = RUN.RunConfig()
    model = RUN.provider_for(cfg)
    state = model.state(RUN._to_state_prim(valores))
    bd, bf = float(tau_dom["tau_d_upper"]), float(tau_dom["tau_f_upper"])
    rows = model.frontier_grid(state, diseno, j, bd, bf, n if n is not None else cfg.frontier_n)
    return state, [{"frontier_id": frontier_id, "point_id": r.point_id, "side": r.side, "tau_d": r.tau_d, "tau_f": r.tau_f, "B_d": r.B_d, "B_f": r.B_f, "R": r.R, "B_pot": r.B_pot,
                    "CS": None if r.R is None else r.R / r.B_pot, "eps_dd": r.eps.get("eps_dd"), "eps_df": r.eps.get("eps_df"), "eps_fd": r.eps.get("eps_fd"),
                    "eps_ff": r.eps.get("eps_ff"), "s_P": r.s_P, "regime": r.regime, "kink_adjacent": r.kink_adjacent, "audit_status": r.audit_status,
                    "computation_status": r.computation_status, "reason_code": r.reason_code} for r in rows], cfg.frontier_n


if __name__ == "__main__" and sys.argv[1] == "prueba-sintetica":
    R, SAL = Path(sys.argv[2]), Path(sys.argv[3])
    sys.path.insert(0, str(R / "paso4/instalacion/src"))
    from paper2b import run as RUN
    from paper2b import model as M
    sint = {"a": "1.5", "beta_tilde": "0.5", "c_legal": "1", "eta_d": "0.5", "eta_f": "1.2", "gamma": "1", "kappa_tilde": "0.6", "phi": "0.5", "rho": "0.5",
            "t": "0", "u_theta": "0.5", "z_cost": "1", "z_m": "1"}          # clave SINTÉTICA declarada (13 valores; ninguna de un soporte real)
    res = {"kind": "prueba-sintetica-conexion-frontera-rem108", "datos": "SINTÉTICOS", "clave": sint, "casos": []}

    def caso(cid, ok, det=None):
        res["casos"].append({"id": cid, "conforme": bool(ok), "detalle": det})
        print(("OK  " if ok else "NO  ") + cid)
    for j, dom in (("d", {"tau_d_upper": "0.6", "tau_f_upper": "0"}), ("df", {"tau_d_upper": "0.6", "tau_f_upper": "0.6"})):
        st, filas, n = filas_frontera(RUN, M, sint, dom, "G", j)
        caso("F1-%s filas frontier_result con las columnas del productor" % j, filas and all(set(("eps_dd", "eps_df", "eps_fd", "eps_ff", "s_P", "regime")) <= set(f) for f in filas),
             {"filas": len(filas), "frontier_n": n})
        caso("F2-%s malla de frontier_n+1 nodos por eje (supremum.nodes: bar·i/n, i=0..n; 1-D en d, 2-D en df)" % j, len({(f["tau_d"], f["tau_f"]) for f in filas}) == ((n + 1) if j == "d" else (n + 1) ** 2), {"puntos": len({(f["tau_d"], f["tau_f"]) for f in filas})})
        ok_sp = all(f["s_P"] is None or (f["tau_f"] == 0 and abs(f["s_P"] - (1 - st.phi)) <= 1e-12) or abs(f["s_P"] - M.provider_share(f["tau_f"], st.phi)) <= 1e-12 for f in filas)
        caso("F3-%s s_P de cada punto = model.provider_share (incidencia exacta)" % j, ok_sp)
        ok_r = all(f["R"] is None or abs(f["R"] - (f["tau_d"] * f["B_d"] + f["tau_f"] * f["B_f"])) <= 1e-12 * max(1, abs(f["R"])) for f in filas)
        caso("F4-%s identidad R = τ_d·B_d + τ_f·B_f en cada punto (T1)" % j, ok_r)
    res["conformes"], res["total"] = sum(x["conforme"] for x in res["casos"]), len(res["casos"])
    SAL.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"conformes": res["conformes"], "total": res["total"]}))
    raise SystemExit(0 if res["conformes"] == res["total"] else 4)
