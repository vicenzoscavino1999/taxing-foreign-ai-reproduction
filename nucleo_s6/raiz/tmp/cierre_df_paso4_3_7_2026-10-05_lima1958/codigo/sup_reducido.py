"""Supremo de C2 en df (G y N) con ELIMINACIÓN ANALÍTICA de (κ̃, a, ρ): rama y cota en 5 ejes (CIERRE DF Y PASO 4 3.7,
NO OFICIAL). Versión candidata nueva; no modifica sup_formal_mvf, sup_restringido ni sup_eliminado(_v2).

  <py_integracion> -m codigo.sup_reducido <G|N> <salida.json> <tope_s>

Notación (z_m = 1, γ del plan, κ0 = κ̃ γ, q = (a − 1)/(a − ρ) ∈ (0, 1], encierros_modelo.tax_side):
  A = τ_d r* γ,  B̃ = τ_f q* γ g_f  (>= 0),  c_G = (1 + φ t̃_f)/(1 − t̃_d),  c_N = 1 + φ t̃_f.
Cota formal (FUNDAMENTO §3, z_c <= z_m):  UB_G = A + κ̃ q B̃;  UB_N = A + κ̃ q D,  D = B̃ − τ_d r* γ (1 + φ t̃_f).
G (FUNDAMENTO §8 y §8.1): sup Rn <= sup {UB_G : r_G <= 1}; UB_G es creciente en κ̃ y en q (B̃ >= 0) y r_G <= 1 ⟺
  κ̃ <= κ̃* = 1/c_G (r_G no depende de a ni de ρ con z_m = 1); como q <= 1 con igualdad en ρ = 1 (ρ = 1 está en el
  soporte, y entonces q = 1 para todo a):  sup Rn <= sup_{τ, η_d, η_f, φ} F_G,  F_G = A + B̃ · min(κ̃_max, κ̃*),
  con la precondición κ̃* >= κ̃_min comprobada por SUBDIVISIÓN (sup_restringido.precondicion).
N (§8.2): r_N = κ̃ c_N <= κ̃_max · c_N,hi <= 0,535 < 1 en TODO el soporte (c_N,hi por subdivisión; se comprueba aquí), así que
  UB_N >= Rn en todo el dominio; UB_N es lineal en s = κ̃ q y el rango conjunto de s sobre el soporte es
  [κ̃_min q_min, κ̃_max] (κ̃ y (a, ρ) varían por separado; q_min = (a_min − 1)/(a_min − ρ_min), q creciente en a y en ρ):
  sup Rn <= sup_{τ, η_d, η_f, φ} F_N,  F_N = A + max(κ̃_max D, s_min D)   (s_min encerrado por abajo: conservador).
Rama y cota en (τ_d, τ_f, η_d, η_f, φ) (no dependen de β̃, z_cost, u_θ): valor medio con el AD de motor_theta; en las
cajas donde min/max no está en una sola rama se usa, para G, min(cota de A + B̃ κ̃_max, cota de A + B̃ κ̃*) y, para N,
max(cota de A + κ̃_max D, cota de A + s_min D), cada una por valor medio. Colapso por monotonía DEMOSTRADA solo en
cajas de una sola rama (F suave). L = encierros PUNTUALES del motor normalizado en el punto que realiza la eliminación:
G: ρ = 1, a = a_min, κ̃ = min(κ̃_max, κ̃*.lo (1 − 1e-9)) (r < 1 estricto); N: D >= 0 -> κ̃ = κ̃_max, ρ = 1, a = a_min;
D < 0 -> κ̃ = κ̃_min, a = a_min, ρ = ρ_min; con β̃ = 0,25, z_cost = 1, u_θ = 0,5. Controles: PUNTO_SOBRE_CAJA
(Rn(p) <= F(p) <= U(caja)) y PUNTO_SOBRE_COTA_GLOBAL (L <= U): detienen la corrida como INVALIDO_COTA_INCOMPATIBLE.
Si el supremo no se alcanza (G con ρ = 1: límite lateral κ̃ -> κ̃*⁻), los puntos de L son la secuencia testigo.
"""
from __future__ import annotations

import heapq
import json
import math
import sys
import time
from pathlib import Path

AREA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AREA / "integracion/src"))
import paper2b  # noqa: E402

assert Path(paper2b.__file__).resolve().parent == (AREA / "integracion/src/paper2b").resolve(), "PAPER2B_NO_AISLADO"
from codigo import extremos_dfd as XD  # noqa: E402
from codigo import sup_restringido as SR  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from paper2b import motor_theta as MT  # noqa: E402
from paper2b.encierros_modelo import add, div, mul, sub  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = 1e-4
EJES = ("tau_d", "tau_f", "eta_d", "eta_f", "phi")
FIJOS = {"beta_tilde": 0.25, "z_cost": 1.0, "u_theta": 0.5}


class Incompatible(RuntimeError):
    pass


class Problema:
    def __init__(self, dis):
        self.dis = dis
        G = XD.grupo(dis, "df")
        self.G, self.fixed = G, G["fixed"]
        N.need(float(self.fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
        mm = dict(XD.menu("df", G["bd"], G["bf"]), **G["full"])
        self.full = {p: mm[p] for p in MT.VARS}
        self.kmin, self.kmax = mm["kappa_tilde"]
        self.amin, self.rmin = mm["a"][0], mm["rho"][0]
        N.need(mm["rho"][1] == 1.0, "RHO_MAX_DISTINTO_DE_1")
        qmin = (Iv(self.amin, self.amin) - 1.0) / (Iv(self.amin, self.amin) - Iv(self.rmin, self.rmin))
        self.smin = self.kmin * qmin.lo * (1.0 - 1e-12)
        self.c_hi, self.td_max, self.ptf_max = SR.precondicion(self.full, self.fixed, dis)
        if dis == "G":
            N.need(self.c_hi < math.inf and 1.0 / self.c_hi >= self.kmin, "PRECONDICION_KAPPA_ESTRELLA")
        else:
            N.need(self.kmax * self.c_hi < 1.0, "R_N_PUEDE_SUPERAR_1")
        self.root = {p: mm[p] for p in EJES}

    def partes(self, box):
        """(A, B̃, κ̃* o None, D o None) como AD; a = a_min, ρ = 1 (q = 1), κ̃ ficticio (F no lo usa)."""
        th = dict({p: box[p] for p in ("eta_d", "eta_f", "phi")}, a=(self.amin, self.amin), rho=(1.0, 1.0),
                  kappa_tilde=(self.kmax, self.kmax), **{k: (v, v) for k, v in FIJOS.items()})
        Q = MT.QParams(th, self.fixed)
        td, tf = MT.var(Iv(*box["tau_d"]), 0), MT.var(Iv(*box["tau_f"]), 1)
        x = MT.tax_ad(Q, td, tf)
        A = mul(mul(td, x.rstar), Q.gamma)
        Bt = mul(mul(mul(tf, x.qstar), Q.gamma), x.gf)
        num = add(1.0, mul(Q.phi, x.tf))
        if self.dis == "G":
            ks = div(x.one_td, num) if num.v.lo > 0.0 else None
            return A, Bt, ks, None
        D = sub(Bt, mul(mul(mul(td, x.rstar), Q.gamma), num))
        return A, Bt, None, D

    def ramas(self, box):
        """Lista de funciones suaves (callables caja -> AD) cuya combinación (min para G, max para N) da F en la caja, y la
        rama única si la hay."""
        A, Bt, ks, D = self.partes(box)
        if self.dis == "G":
            f1 = lambda b: (lambda A, Bt, ks, D: add(A, mul(Bt, self.kmax)))(*self.partes(b))  # noqa: E731

            def f2(b):
                A2, B2, k2, _ = self.partes(b)
                return None if k2 is None else add(A2, mul(B2, k2))
            if ks is None:
                return "min", [f1], None
            if ks.v.lo >= self.kmax:
                return "min", [f1], f1
            if ks.v.hi <= self.kmax:
                return "min", [f2], f2
            return "min", [f1, f2], None
        fh = lambda b: (lambda A, Bt, ks, D: add(A, mul(D, self.kmax)))(*self.partes(b))  # noqa: E731
        fl = lambda b: (lambda A, Bt, ks, D: add(A, mul(D, self.smin)))(*self.partes(b))  # noqa: E731
        if D.v.lo >= 0.0:
            return "max", [fh], fh
        if D.v.hi <= 0.0:
            return "max", [fl], fl
        return "max", [fh, fl], None


def _mv(fun, face):
    Fa = fun(face)
    if Fa is None:
        return math.inf
    if Fa.g is None:
        return Fa.v.hi
    c = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in face.items()}
    Fc = fun(c)
    if Fc is None:
        return Fa.v.hi
    mv = Fc.v
    for i, p in enumerate(MT.VARS):
        if p in face:
            mv = mv + Fa.g[i] * (Iv(*face[p]) - c[p][0])
    return min(Fa.v.hi, mv.hi)


def cota(pr, box, n, col):
    """(U de la caja, gradiente de F sobre la caja COMPLETA si F es suave en ella)."""
    face = dict(box, **{k: (v, v) for k, v in col.items()})
    modo, funs, unica = pr.ramas(box)
    _, funs_f, _ = pr.ramas(face)
    us = [_mv(f, face) for f in funs_f]
    U = min(us) if modo == "min" else max(us)
    n["valor_medio" if len(funs_f) == 1 else "ramas_mixtas"] += 1
    g = None
    if unica is not None:
        Ff = unica(box)
        g = Ff.g if Ff is not None else None
    return U, g


def main():
    dis, out, tope = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3])
    t0 = time.time()
    pr = Problema(dis)
    root = pr.root
    libres0 = [p for p in EJES if root[p][1] > root[p][0]]
    W = {p: root[p][1] - root[p][0] for p in libres0}
    gam = float(pr.fixed["gamma"])
    n = {"cajas": 0, "podadas": 0, "puntos": 0, "valor_medio": 0, "ramas_mixtas": 0, "colapsos": 0}
    best = {"L": -math.inf, "pt": None}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "diseno": dis, "instrumento": "df",
           "objeto": "sup C2 %s-df = sup F_%s (κ̃, a, ρ eliminados; 5 ejes)" % (dis, dis), "plan_sha256": pr.G["plan_sha256"],
           "dominio": {p: list(v) for p, v in pr.full.items()}, "T2": T2, "ejes": libres0, "fijos_de_punto": FIJOS,
           "precondicion": {"c_hi": pr.c_hi, "max_t_d": pr.td_max, "max_phi_t_f": pr.ptf_max,
                            "kappa_estrella_min" if dis == "G" else "r_N_max": (1.0 / pr.c_hi) if dis == "G" else pr.kmax * pr.c_hi},
           "s_min": pr.smin if dis == "N" else None}
    t_esc = [0.0]

    def punto(p5, techo=math.inf):
        bx = {k: (v, v) for k, v in p5.items()}
        A, Bt, ks, D = pr.partes(bx)
        if dis == "G":
            N.need(ks is not None, "KAPPA_ESTRELLA_INDEFINIDA")
            pt = dict(p5, a=pr.amin, rho=1.0, kappa_tilde=min(pr.kmax, ks.v.lo * (1.0 - 1e-9)), **FIJOS)
        elif D.v.lo >= 0.0:
            pt = dict(p5, a=pr.amin, rho=1.0, kappa_tilde=pr.kmax, **FIJOS)
        else:
            pt = dict(p5, a=pr.amin, rho=pr.rmin, kappa_tilde=pr.kmin, **FIJOS)
        n["puntos"] += 1
        v = XD.punto(pt, pr.fixed, dis)
        if v.lo > techo:
            raise Incompatible("PUNTO_SOBRE_CAJA: %r > %r en %s" % (v.lo, techo, json.dumps(pt)))
        if v.lo > best["L"]:
            best["L"], best["pt"] = v.lo, pt

    def escribir(force=False, **kw):
        doc.update(kw)
        if force or time.time() - t_esc[0] > 15:
            doc.update(L=best["L"] / gam, punto_cota_inferior=best["pt"], segundos=round(time.time() - t0, 1), **n)
            N.write_json_atomic(out, doc)
            t_esc[0] = time.time()

    def colapsar(box, col, g):
        c2 = dict(col)
        for i, p in enumerate(MT.VARS):
            if p in libres0 and p not in c2 and box[p][1] > box[p][0] and g is not None:
                if g[i].lo > 0.0:
                    c2[p] = box[p][1]
                elif g[i].hi < 0.0:
                    c2[p] = box[p][0]
        return c2
    estado, traza, heap = "tope", [], []
    try:
        for p5 in ({"tau_d": 0.6, "tau_f": 0.6, "eta_d": 0.1, "eta_f": 0.1, "phi": ph} for ph in (0.0, 0.25, 0.5, 0.667, 0.75, 0.9, 0.9414, 0.95, 1.0)):
            punto({k: min(max(v, root[k][0]), root[k][1]) for k, v in p5.items()})
        u0, g0 = cota(pr, root, n, {})
        heap = [(-u0, 0, root, g0, {})]
        cont = 1
        while heap:
            if best["L"] > -heap[0][0] + 1e-12 * max(1.0, abs(best["L"])):
                raise Incompatible("PUNTO_SOBRE_COTA_GLOBAL: L %r > U %r" % (best["L"], -heap[0][0]))
            Ucur = max(-heap[0][0], best["L"])
            brecha = (Ucur - best["L"]) / gam
            if n["cajas"] % 200 == 0:
                traza.append([round(time.time() - t0, 1), n["cajas"], best["L"] / gam, Ucur / gam])
            escribir(U=Ucur / gam, brecha=brecha, vivas=len(heap))
            if brecha <= T2:
                estado = "convergido"
                break
            if time.time() - t0 > tope:
                break
            nu, _, box, g, col = heapq.heappop(heap)
            if -nu <= best["L"]:
                n["podadas"] += 1
                continue
            n["cajas"] += 1
            if g is not None:
                c2 = colapsar(box, col, g)
                if c2 != col:
                    n["colapsos"] += 1
                    u2, g2 = cota(pr, box, n, c2)
                    u2 = min(u2, -nu)
                    punto({p: (c2[p] if p in c2 else lo + (hi - lo) / 2) for p, (lo, hi) in box.items()}, u2)
                    if u2 > best["L"]:
                        heapq.heappush(heap, (-u2, cont, box, g2 if g2 is not None else g, c2))
                        cont += 1
                    else:
                        n["podadas"] += 1
                    continue
            if n["cajas"] % 10 == 0:
                punto({p: (col[p] if p in col else lo + (hi - lo) / 2) for p, (lo, hi) in box.items()}, -nu)
            libres = [p for p in libres0 if box[p][1] > box[p][0] and p not in col]
            if not libres:
                punto({p: (col[p] if p in col else lo) for p, (lo, hi) in box.items()}, -nu)
                if -nu - best["L"] <= T2 * gam:
                    continue
                heapq.heappush(heap, (nu, cont, box, g, col))
                estado = "caja_degenerada_viva"
                break
            if g is not None:
                q = max(libres, key=lambda p: max(abs(g[MT.VARS.index(p)].lo), abs(g[MT.VARS.index(p)].hi)) * (box[p][1] - box[p][0]))
            else:
                q = max(libres, key=lambda p: (box[p][1] - box[p][0]) / W[p])
            lo, hi = box[q]
            m = lo + (hi - lo) / 2
            for h in (dict(box, **{q: (lo, m)}), dict(box, **{q: (m, hi)})):
                u, gh = cota(pr, h, n, col)
                u = min(u, -nu)
                if u > best["L"]:
                    heapq.heappush(heap, (-u, cont, h, gh, col))
                    cont += 1
                else:
                    n["podadas"] += 1
            heap = [x for x in heap if -x[0] > best["L"]]
            heapq.heapify(heap)
        if not heap and estado != "convergido":
            estado = "convergido"
        Ufin = max(-heap[0][0], best["L"]) if heap else best["L"]
    except Incompatible as exc:
        estado, Ufin = "INVALIDO_COTA_INCOMPATIBLE", None
        doc["diagnostico"] = str(exc)[:1000]
    escribir(force=True, U=None if Ufin is None else Ufin / gam, brecha=None if Ufin is None else (Ufin - best["L"]) / gam,
             estado=estado, vivas=len(heap) if estado != "INVALIDO_COTA_INCOMPATIBLE" else None,
             mejor_caja_viva={p: list(v) for p, v in heap[0][2].items()} if (estado != "INVALIDO_COTA_INCOMPATIBLE" and heap) else None,
             traza=traza[:: max(1, len(traza) // 60)] + traza[-1:], lema_E0=dict(MT.ESTADISTICA))
    print(json.dumps({k: doc.get(k) for k in ("diseno", "L", "U", "brecha", "estado", "cajas", "colapsos", "valor_medio", "ramas_mixtas", "puntos", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
