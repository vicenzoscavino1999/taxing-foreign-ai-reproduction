"""Diagnostico PUNTUAL (flotante, sin certificar) del umbral de adopcion formal con topes bajos, con una regla.

Generaliza diagnostico_salto.py del chequeo estatutario (que fija tau_f = 0,6 y busca en [0; 0,6]) a un tope de retencion
tau_f dado y un tope domestico dado. Con rho = 1 el trinomio F1-F0 no depende de z: su signo L decide a la vez, para todos
los establecimientos formales, si adoptan (L > 0) o no (L <= 0; regla de desempate S13). Disenio G:
L = (1 - tilde_d) gamma - k_F, decreciente en tau_d; disenio N: L = (1 - tilde_d)(gamma - k_F), cuyo signo no depende de
tau_d. Se informa L y R/B_pot en el tope, R/B_pot en una malla hasta el tope y, solo para ubicarlo, el cruce de L sobre
tau_d en [0; 0,95] con tau_f fijo, aunque quede por encima del tope. Explica el estado del certificador; no lo sustituye.

Uso: python -B -I diagnostico_umbral.py <E11|estatutaria> <G|N> <tau_f> <tope_d> <salida.json>
"""
import json
import math
import os
import sys
from pathlib import Path

ESTAT = Path(__file__).resolve().parent
sys.path.insert(0, str(ESTAT))
import calculo as CA  # noqa: E402  (el calculo.py de esta carpeta)

TD_MAX = 0.95


def main():
    regla, dis, tf, bd, salida = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), Path(sys.argv[5])
    if salida.exists():
        raise SystemExit("LA SALIDA YA EXISTE; no se sobrescribe: %s" % salida)
    faltan = sorted(k for k, v in CA.ENTORNO.items() if os.environ.get(k) != v)
    if faltan:
        raise SystemExit("ENTORNO DISTINTO DEL DE PRODUCCION: %s" % faltan)
    src = CA.REGLAS[regla]
    sys.path.insert(0, str(src))
    from paper2b import model as M
    if not str(Path(M.__file__).resolve()).startswith(str(src.resolve())):
        raise SystemExit("paper2b cargado desde otra ruta: %s" % M.__file__)
    _, pay, _ = CA.cargar_testigo(dis)
    s = M.state_from_primitives({v["parameter_id"]: float(v["value"]) for v in pay["values"]})

    def L(td):
        return M.pair_trinomials(s, td, tf, dis)["F1-F0"].L

    def punto(td):
        ev = M.evaluate(s, td, tf, dis)
        return {"tau_d": td, "tau_d_hex": float(td).hex(), "L_F1_F0": L(td), "R_sobre_Bpot": ev.R / ev.B_pot,
                "R_sobre_Bpot_hex": (ev.R / ev.B_pot).hex(), "topologia": ev.topology, "A": ev.A, "W_F": ev.W_F,
                "B_d": ev.B_d, "B_f": ev.B_f, "masa_formal": ev.mass_F}

    out = {"regla": regla, "diseno": dis, "tau_f": tf, "tope_d": bd, "phi": s.phi, "k_F": M.k_formal(s, tf),
           "L_en_0": L(0.0), "L_en_tope": L(bd), "td_max_busqueda": TD_MAX, "cruce": None}
    if L(0.0) > 0.0 >= L(TD_MAX):
        lo, hi = 0.0, TD_MAX
        while math.nextafter(lo, 1.0) < hi:
            m = 0.5 * (lo + hi)
            if m <= lo or m >= hi:
                break
            lo, hi = (m, hi) if L(m) > 0.0 else (lo, m)
        out["cruce"] = {"ultimo_con_adopcion": punto(lo), "primero_sin_adopcion": punto(hi), "por_encima_del_tope": lo >= bd}
    out["tope"] = punto(bd)
    out["malla"] = [punto(td) for td in (0.0, 0.10, 0.20, 0.25, 0.30, 0.33, 0.34, bd)]
    salida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    c = out["cruce"]
    print(regla, dis, "tau_f=%g" % tf, "k_F=%.12g" % out["k_F"], "L(tope)=%.6g" % out["L_en_tope"],
          "R/B tope=%r" % out["tope"]["R_sobre_Bpot"],
          "cruce tau_d=%r" % (c["ultimo_con_adopcion"]["tau_d"] if c else None))


if __name__ == "__main__":
    main()
