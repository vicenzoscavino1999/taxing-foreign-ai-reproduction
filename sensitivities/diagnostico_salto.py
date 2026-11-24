"""Diagnostico PUNTUAL (flotante, sin certificar) de la curva de salto de adopcion formal en tau_f = 0,6, con una regla.

Con rho = 1 el trinomio F1-F0 no depende de z: su signo L decide a la vez para todos los establecimientos formales si
adoptan (L > 0) o no (L <= 0; regla de desempate S13: con L = 0 no adoptan). Disenio G: L = (1 - tilde_d) gamma - k_F;
disenio N: L = (1 - tilde_d)(gamma - k_F), cuyo signo no depende de tau_d. Se busca por biseccion en flotantes el cruce
de L sobre tau_d en [0; 0,6] con tau_f = 0,6 y se evalua la recaudacion a ambos lados, en el tope y en una malla. Sirve
para explicar el estado del certificador, no lo sustituye.

Uso: python -B -I diagnostico_salto.py <E11|estatutaria> <G|N> <salida.json>
"""
import json, math, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import calculo as CA  # noqa: E402

TF = 0.6


def main():
    regla, dis, salida = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if salida.exists():
        raise SystemExit("LA SALIDA YA EXISTE")
    src = CA.REGLAS[regla]
    sys.path.insert(0, str(src))
    from paper2b import model as M
    if not str(Path(M.__file__).resolve()).startswith(str(src.resolve())):
        raise SystemExit("paper2b cargado desde otra ruta")
    _, pay, _ = CA.cargar_testigo(dis)
    s = M.state_from_primitives({v["parameter_id"]: float(v["value"]) for v in pay["values"]})

    def L(td):
        return M.pair_trinomials(s, td, TF, dis)["F1-F0"].L

    def punto(td):
        ev = M.evaluate(s, td, TF, dis)
        return {"tau_d": td, "tau_d_hex": float(td).hex(), "L_F1_F0": L(td), "R_sobre_Bpot": ev.R / ev.B_pot,
                "topologia": ev.topology, "A": ev.A, "W_F": ev.W_F, "B_d": ev.B_d, "B_f": ev.B_f, "masa_formal": ev.mass_F}

    out = {"regla": regla, "diseno": dis, "tau_f": TF, "phi": s.phi, "k_F": M.k_formal(s, TF),
           "L_en_0": L(0.0), "L_en_tope": L(0.6), "cruce": None}
    if L(0.0) > 0.0 >= L(0.6):
        lo, hi = 0.0, 0.6
        while math.nextafter(lo, 1.0) < hi:
            m = 0.5 * (lo + hi)
            if m <= lo or m >= hi:
                break
            lo, hi = (m, hi) if L(m) > 0.0 else (lo, m)
        out["cruce"] = {"ultimo_con_adopcion": punto(lo), "primero_sin_adopcion": punto(hi)}
    out["tope"] = punto(0.6)
    out["malla"] = [punto(td) for td in (0.50, 0.55, 0.57, 0.58, 0.585, 0.5875, 0.59, 0.595, 0.6)]
    salida.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    c = out["cruce"]
    print(regla, dis, "k_F=%.12g" % out["k_F"], "L(0,6)=%.6g" % out["L_en_tope"],
          "cruce tau_d=%r" % (c["ultimo_con_adopcion"]["tau_d"] if c else None),
          "R/B izq=%r der=%r" % ((c["ultimo_con_adopcion"]["R_sobre_Bpot"], c["primero_sin_adopcion"]["R_sobre_Bpot"]) if c else (None, None)),
          "R/B tope=%r" % out["tope"]["R_sobre_Bpot"])


if __name__ == "__main__":
    main()
