"""Techo v3 CERTIFICADO de C2 df en una lista de puntos θ (CIERRE INF DF Y PASO 4 3.7, NO OFICIAL). Igual que el modo
certificar de codigo/certificar_inf_df.py (que no se modifica), con tope de tiempo POR PUNTO y la familia de puntos
declarada aquí: la esquina del ínfimo de C2 (κ̃ = κ̃_min, ρ = ρ_min, z_cost, u_θ, β̃, η_d, η_f al máximo, φ = φ*) con a en
una rejilla. Sirve de cota superior conjunta (mismo ω) para inf_ω G (codigo/extremos_G_df.py).

  <py_integracion> -m codigo.certificar_puntos <G|N> <phi> <a1,a2,...> <salida.json> <tope_por_punto_s>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from codigo import certificar_inf_df as CI
from codigo import extremos_dfd as XD
from codigo import inf_df_techo_v3 as TV3
from codigo.demo import nucleo_v as N


def main():
    dis, phi, aa, out, tpp = sys.argv[1], float(sys.argv[2]), [float(x) for x in sys.argv[3].split(",")], Path(sys.argv[4]), float(sys.argv[5])
    t0 = time.time()
    G = XD.grupo(dis, "df")
    fixed, bd, bf, full = G["fixed"], G["bd"], G["bf"], G["full"]
    esq = {p: v[1] for p, v in full.items()}
    esq.update(kappa_tilde=full["kappa_tilde"][0], rho=full["rho"][0], phi=phi)
    filas = []
    for a in aa:
        th = dict(esq, a=a)
        f = {"diseno": dis, "theta": th, "admisible": CI.admisible(th, full, fixed)}
        if f["admisible"]:
            r = TV3.techo(th, fixed, dis, bd, bf, tol=2e-6, tope_s=tpp)
            lp, tl = CI.l_punto(th, fixed, dis, [tuple(r["tau_sup_puntos"])])
            f.update(techo=r, U=r["U_C2"], L_punto=lp, tau_L_punto=list(tl), holgura_punto=r["U_C2"] - lp, incompatible=r["U_C2"] < lp)
        filas.append(f)
        N.write_json_atomic(out, {"etiqueta": N.ETIQUETA, "parcial": True, "diseno": dis, "filas": filas})
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "techo v3 certificado en la familia de puntos de la esquina con a variable",
           "diseno": dis, "plan_sha256": G["plan_sha256"], "phi": phi, "a": aa, "filas": filas,
           "incompatibles": sum(1 for f in filas if f.get("incompatible")), "segundos": round(time.time() - t0, 1)}
    N.write_json_atomic(out, doc)
    print(json.dumps({"diseno": dis, "U": [[f["theta"]["a"], f.get("U"), f.get("L_punto")] for f in filas], "segundos": doc["segundos"]}))


if __name__ == "__main__":
    raise SystemExit(main())
