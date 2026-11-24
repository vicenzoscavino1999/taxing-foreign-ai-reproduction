"""Extremos globales de C2 por (diseño, instrumento) con el motor θ (valor medio + monotonía) (EXTREMOS df/d 3.7, NO OFICIAL).

  <py_integracion> -m codigo.extremos_dfd sonda <salida.json> <tope_s>
  <py_integracion> -m codigo.extremos_dfd conocidos <salida.json>
  <py_integracion> -m codigo.extremos_dfd sup <G|N> <d|df|f> <salida.json> <eventos.jsonl> <tope_s>
  <py_integracion> -m codigo.extremos_dfd inf <G|N> <d|df|f> <salida.json> <eventos.jsonl> <tope_s>

Objeto (DI-08 / §19.6 del antecedente; matriz de cierre_candidato_3_7): C2(θ) = sup_τ R(τ; θ) / B_pot(θ) =
sup_τ Rn(τ; θ) / γ sobre el menú τ del instrumento y la caja COMPLETA del soporte continuo del grupo (plan autenticado de
certificacion_3_7, demo/C2/plan.json: una caja por (diseño, instrumento), común a sus 10 conjuntos). T2 = 1e-4.

sup_θ C2 = sup_(τ,θ) Rn / γ: rama y cota CONJUNTA en (τ, θ), mejor primero por la cota superior.
  - cota superior de una caja = (natural ∩ valor medio).hi (codigo.motor_theta.encierro);
  - cota inferior GLOBAL = máx de encierros PUNTUALES .lo en puntos (τ, θ) admisibles visitados (el punto queda registrado:
    es la cota «por punto admisible»; la cota global es U = máx de cotas superiores de las cajas vivas);
  - monotonía: si ∂_i Rn tiene signo demostrado en la caja, el eje i se fija en la cara favorable (lo que se descarta
    tiene Rn menor o igual en el mismo punto de la cara: el supremo no cambia);
  - poda: caja con cota superior <= cota inferior; parada: U - L <= T2 (convergido) o tope.
inf_θ C2 = inf_θ sup_τ Rn / γ: rama y cota en θ, mejor primero por la cota inferior.
  - cota inferior de una caja B: máx sobre τ candidatos t de encierro(B; τ = t).lo (C2(θ) >= Rn(t; θ) para todo θ de B);
  - cota superior GLOBAL: techo certificado C2(θ0) en puntos θ0 (paper2b.encierros_modelo.sup_bound con el motor
    normalizado en la caja degenerada θ0: cota superior demostrada de sup_τ); el punto queda registrado;
  - monotonía: si ∂_i Rn tiene signo demostrado en (menú τ completo) x B, C2 es monótona en θ_i en B y el ínfimo está
    en la cara (inferior si ∂_i >= 0);
  - poda: caja con cota inferior >= U; parada: U - L <= T2.
Cada caja evaluada se escribe al instante en eventos.jsonl (fsync) y el resumen se reescribe de forma atómica cada 15 s.
"""
from __future__ import annotations

import heapq
import json
import math
import os
import random
import sys
import time
from pathlib import Path

AREA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AREA / "integracion/src"))     # paper2b de la INTEGRACIÓN CANDIDATA (bytes probados)
import paper2b  # noqa: E402

_INT, _CAN = (AREA / "integracion/src/paper2b").resolve(), (AREA / "candidato/src/paper2b").resolve()
if Path(paper2b.__file__).resolve().parent == _CAN:
    # INTEGRACION E12: núcleo CANDIDATO del paso 4 (flujo_paso4). Se admite solo si es byte a byte la integración
    # salvo run.py (caché de techos compartida, ver review/diffs).
    _a = {f.name: f.read_bytes() for f in _INT.glob("*.py")}
    _b = {f.name: f.read_bytes() for f in _CAN.glob("*.py")}
    # VALIDACION PAQUETE 3.7 (COPIA): solo difieren de la integración los archivos listados con su sha256 en
    # candidato/CAMBIOS_NUCLEO.json (cambios candidatos explícitos y documentados); el resto, byte a byte igual.
    import hashlib as _h
    import json as _j
    _m = _j.loads((AREA / "candidato/CAMBIOS_NUCLEO.json").read_bytes())["cambios"]
    # CONTRATO PAQUETE 3.7: un archivo NUEVO del núcleo candidato se admite solo declarado con "integracion": null y su sha256.
    assert set(_a) <= set(_b) and all(k in _a or (k in _m and _m[k]["integracion"] is None and _h.sha256(_b[k]).hexdigest() == _m[k]["candidato"])
                                      for k in _b) and all(_a[k] == _b[k] or (k in _m and _h.sha256(_b[k]).hexdigest() == _m[k]["candidato"]
                                                                               and _h.sha256(_a[k]).hexdigest() == _m[k]["integracion"]) for k in _a), "NUCLEO_CANDIDATO_NO_DECLARADO"
else:
    assert Path(paper2b.__file__).resolve().parent == _INT, "PAPER2B_NO_AISLADO"
from .demo import nucleo_v as N  # noqa: E402
from paper2b import c2_normalizado as C2N  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import motor_theta as MT  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402
from paper2b.supremum import axes as sup_axes  # noqa: E402

T2 = 1e-4
CERT = N.ROOT / "tmp/certificacion_3_7_2026-10-04"
CERT_INV = "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5"
PLAN_REL = "demo/C2/plan.json"


def autenticado(base, inv_h, rel):
    inv_raw = (base / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == inv_h, "INVENTARIO:" + base.name)
    raw = (base / rel).read_bytes()
    N.need(json.loads(inv_raw)["files"][rel]["sha256"] == N.sha(raw), "NO_AUTENTICADO:" + rel)
    return json.loads(raw), N.sha(raw)


def grupo(dis, j):
    """Caja completa del soporte, fijos y barras del grupo (diseño, instrumento) del plan AUTENTICADO."""
    plan, h = autenticado(CERT, CERT_INV, PLAN_REL)
    gs = [g for g in plan["grupos"] if g["clave"]["diseno"] == dis and g["clave"]["instrumento"] == j]
    N.need(len(gs) == 1, "GRUPO_NO_UNICO")
    key = gs[0]["clave"]
    full = {p: (float.fromhex(v[0]), float.fromhex(v[1])) for p, v in key["caja"].items()}
    fixed = dict(key["fijos"])
    from paper2b import cobertura as COV
    from .demo.cobertura_compartida import q_pot_exact
    COV.q_pot = q_pot_exact              # rango EXACTO de q_pot por vértices (como c2_extremos); la natural no prueba q_pot < 1
    N.need(COV.box_admissible(full, fixed), "CAJA_NO_ADMISIBLE")
    return {"grupo": gs[0]["grupo"], "sid_ref": gs[0]["sid_ref"], "plan_sha256": h, "full": full, "fixed": fixed,
            "bd": float(fixed["bar_tau_d"]), "bf": float(fixed["bar_tau_f"])}


def menu(j, bd, bf):
    (dl, dh), (fl, fh) = sup_axes(j, bd, bf)
    return {"tau_d": (dl, dh), "tau_f": (fl, fh)}


def split_box(box):
    th = {p: box[p] for p in MT.STRUCT}
    return th, Iv(*box["tau_d"]), Iv(*box["tau_f"])


class CotaIncompatible(RuntimeError):
    """Dos encierros RIGUROSOS del mismo objeto que no se intersecan: al menos uno es inválido. Nunca se «repara» moviendo
    un extremo (la versión anterior hacía Iv(min(lo, U), U) y ocultaba el defecto de cota_umbral en N): la corrida se
    detiene con estado INVALIDO_COTA_INCOMPATIBLE y el diagnóstico (caja, encierro, cota)."""


def evaluar(box, fixed, dis, stats=None):
    th, Td, Tf = split_box(box)
    e, g = MT.encierro(th, fixed, dis, Td, Tf, stats)
    ub = MT.cota_analitica(box, fixed, dis)
    if ub < e.lo:
        raise CotaIncompatible("COTA_INCOMPATIBLE: cota cerrada %r < encierro.lo %r; diseño %s; caja %s" % (ub, e.lo, dis, json.dumps(box)))
    if ub < e.hi:
        e = Iv(e.lo, ub)
    return e, g


def punto(pt, fixed, dis):
    th = {p: (pt[p], pt[p]) for p in MT.STRUCT}
    return MT.valor(th, fixed, dis, Iv(pt["tau_d"], pt["tau_d"]), Iv(pt["tau_f"], pt["tau_f"]))


def centro(box):
    return {p: lo + (hi - lo) / 2 for p, (lo, hi) in box.items()}


class Bitacora:
    def __init__(self, ev_p: Path | None, out: Path, doc: dict):
        self.fh = open(ev_p, "a", encoding="utf-8") if ev_p else None
        self.out, self.doc, self.t_esc, self.t0 = out, doc, 0.0, time.time()

    def ev(self, **kw):
        if self.fh:
            kw["t"] = round(time.time() - self.t0, 2)
            self.fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
            self.fh.flush()
            os.fsync(self.fh.fileno())

    def resumen(self, force=False, **kw):
        self.doc.update(kw)
        if force or time.time() - self.t_esc > 15:
            self.doc["segundos"] = round(time.time() - self.t0, 1)
            N.write_json_atomic(self.out, self.doc)
            self.t_esc = time.time()


# ============================================================================================ rama y cota genérica
def bb_sup(root, evaluar_caja, punto_val, tol, tope, bit: Bitacora, escala=1.0, max_cajas=10 ** 7, irrelevantes=(),
           cota_natural=None, inicio=()):
    """Supremo de f sobre `root` (dict eje -> (lo, hi)); evaluar_caja(box) -> (Iv, gradiente por eje o None);
    punto_val(pt) -> Iv. Devuelve dict con L (cota inferior por punto), U (cota global), punto, estado.
    irrelevantes: ejes de los que f NO depende (demostrado por el llamador): nunca se parten.
    cota_natural(box) -> float: cota superior barata para elegir el eje por ENSAYO cuando no hay gradiente (se elige el
    eje cuya bisección da la menor cota superior máxima de las hijas).
    inicio: puntos candidatos (p. ej. de una optimización en flotante): solo aportan cotas inferiores por encierro puntual."""
    ejes = list(root)
    W = {p: (root[p][1] - root[p][0]) or 1.0 for p in ejes}
    best = {"L": -math.inf, "pt": None}
    n = {"cajas": 0, "mono": 0, "sin_grad": 0, "podadas": 0, "ensayos": 0}
    for pt in inicio:
        v = punto_val(pt)
        if v.lo > best["L"]:
            best["L"], best["pt"] = v.lo, dict(pt)

    def visitar(box, techo=math.inf):
        c = centro(box)
        v = punto_val(c)
        if v.lo > techo:                                     # el punto está en la caja: su valor no puede superar su cota
            raise CotaIncompatible("PUNTO_SOBRE_CAJA: encierro puntual.lo %r > cota de la caja %r; punto %s" % (v.lo, techo, json.dumps(c)))
        if v.lo > best["L"]:
            best["L"], best["pt"] = v.lo, c

    def mono(box, g):
        b2, cambio = dict(box), False
        for i, p in enumerate(ejes):
            lo, hi = box[p]
            if hi > lo and g is not None:
                if g[i].lo > 0.0:
                    b2[p], cambio = (hi, hi), True
                elif g[i].hi < 0.0:
                    b2[p], cambio = (lo, lo), True
        return b2, cambio

    def ev(box, techo_padre=math.inf):
        e, g = evaluar_caja(box)
        if e.lo > techo_padre:                              # hija ⊆ padre: su cota inferior no puede superar la del padre
            raise CotaIncompatible("HIJA_SOBRE_PADRE: encierro.lo %r > cota del padre %r; caja %s" % (e.lo, techo_padre, json.dumps(box)))
        if e.hi > techo_padre:                              # sup sobre la hija <= cota superior del padre (hija ⊆ padre)
            e = Iv(e.lo, techo_padre)
        n["cajas"] += 1
        b2, cambio = mono(box, g)
        if cambio:
            n["mono"] += 1
            e2, g2 = evaluar_caja(b2)
            n["cajas"] += 1
            if e2.lo > e.hi:                                 # cara ⊆ caja: su cota inferior no puede superar la de la caja
                raise CotaIncompatible("CARA_SOBRE_CAJA: encierro de la cara.lo %r > cota de la caja %r; cara %s" % (e2.lo, e.hi, json.dumps(b2)))
            # el supremo de la caja se alcanza en la cara: el encierro de la cara es válido para el supremo de la caja
            e, g, box = Iv(e2.lo, min(e.hi, e2.hi)), g2, b2
        if g is None:
            n["sin_grad"] += 1
        visitar(box, e.hi)
        return e, g, box

    e0, g0, b0 = ev(root)
    heap = [(-e0.hi, 0, b0, g0)]
    cont = 1
    estado = "tope"
    traza = []
    while heap:
        U = max(-heap[0][0], best["L"])
        brecha = (U - best["L"]) / escala
        traza.append([round(time.time() - bit.t0, 1), n["cajas"], best["L"] / escala, U / escala])
        bit.resumen(L=best["L"] / escala, U=U / escala, brecha=brecha, vivas=len(heap), **n)
        if brecha <= tol:
            estado = "convergido"
            break
        if time.time() - bit.t0 > tope or n["cajas"] >= max_cajas:
            break
        nh, _, box, g = heapq.heappop(heap)
        if -nh <= best["L"]:
            n["podadas"] += 1
            continue
        libres = [p for p in ejes if box[p][1] > box[p][0] and p not in irrelevantes]
        if not libres:
            heapq.heappush(heap, (nh, cont, box, g))
            estado = "caja_degenerada_viva"
            break
        sc = None
        if g is not None:
            sc = {p: max(abs(g[ejes.index(p)].lo), abs(g[ejes.index(p)].hi)) * (box[p][1] - box[p][0]) for p in libres}
            if max(sc.values()) <= 0.0:
                sc = None
        if sc is None and cota_natural is not None:
            sc = {}
            for q in libres:                                   # ensayo: menor máximo de las cotas de las hijas
                lo_, hi_ = box[q]
                m_ = lo_ + (hi_ - lo_) / 2
                sc[q] = -max(cota_natural(dict(box, **{q: (lo_, m_)})), cota_natural(dict(box, **{q: (m_, hi_)})))
                n["ensayos"] += 2
            # sin mejora apreciable (< 10 % de la brecha de la caja) el ensayo se estanca en un eje: ancho relativo
            if -nh - (-max(sc.values())) < 0.1 * max(-nh - best["L"], 0.0):
                sc = None
                n["ensayo_sin_mejora"] = n.get("ensayo_sin_mejora", 0) + 1
        if sc is None:
            sc = {p: (box[p][1] - box[p][0]) / W[p] for p in libres}
        p = max(libres, key=lambda q: sc[q])
        lo, hi = box[p]
        m = lo + (hi - lo) / 2
        for h in (dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})):
            e, gh, hb = ev(h, -nh)
            bit.ev(evento="caja", eje=p, E=[e.lo, e.hi], grad=gh is not None, caja={q: list(v) for q, v in hb.items()})
            if e.hi > best["L"]:
                heapq.heappush(heap, (-e.hi, cont, hb, gh))
                cont += 1
            else:
                n["podadas"] += 1
        heap = [x for x in heap if -x[0] > best["L"]]
        heapq.heapify(heap)
    U = max(-heap[0][0], best["L"]) if heap else best["L"]
    if not heap:
        estado = "convergido"
    return {"L": best["L"] / escala, "U": U / escala, "brecha": (U - best["L"]) / escala, "estado": estado,
            "punto_cota_inferior": best["pt"], "vivas": len(heap), **n, "traza": traza[:: max(1, len(traza) // 80)] + traza[-1:]}


# ============================================================================================ C2 sup / inf
IRRELEVANTES = {"d": {"eta_f", "phi"}, "f": {"beta_tilde", "eta_d"}, "df": set()}
FUNDAMENTO_IRR = {
    "d": "menú d: τ_f ≡ 0 => l_f = log1p(-τ_f) = 0, de modo que tilde_f = 0, q* = 1, x_f^(-φ) = 1, k_F = κ0 y φ tilde_f = 0 "
         "(tax_side): η_f y φ no aparecen en los trinomios ni en R = τ_d (E0 + r* A) + 0",
    "f": "menú f: τ_d ≡ 0 => tb = τ_d β = 0, tilde_d = 0, r* = 1 y R = τ_f q* κ0 x_f^(-φ) W: β (β̃) y η_d no aparecen en los "
         "trinomios ni en R",
    "df": "ninguno"}


def _mid(v: Iv) -> float:
    return 0.5 * (v.lo + v.hi)


def natural(box, fixed, dis) -> Iv:
    th, Td, Tf = split_box(box)
    return MT.MotorTheta(th, fixed, dis).R(Td, Tf)[0]


def optimizar(root, f, irrelevantes, sentido=1, n_azar=300, n_arranques=4, pasos=20, semilla=20261005):
    """Búsqueda en FLOTANTE (solo orienta): muestreo aleatorio + búsqueda por patrones coordenada a coordenada desde los
    mejores; sentido = 1 maximiza, -1 minimiza. Devuelve [{punto, valor}] ordenados."""
    rng = random.Random(semilla)
    ejes = [p for p in root if root[p][1] > root[p][0] and p not in irrelevantes]
    base = {p: lo + (hi - lo) / 2 for p, (lo, hi) in root.items()}
    pts = []
    for _ in range(n_azar):
        q = dict(base, **{p: root[p][0] + (root[p][1] - root[p][0]) * rng.random() for p in ejes})
        pts.append((sentido * f(q), q))
    mejor_v = {}
    for p in ejes:                                            # vértices de cada eje desde el centro
        vals = []
        for v in root[p]:
            q = dict(base, **{p: v})
            fv = sentido * f(q)
            pts.append((fv, q))
            vals.append((fv, v))
        mejor_v[p] = max(vals)[1]
    q = dict(base, **mejor_v)                                 # vértice combinado: cada eje en su mejor extremo
    pts.append((sentido * f(q), q))
    pts.sort(key=lambda t: -t[0])
    out = []
    for val, q in pts[:n_arranques]:
        h = {p: (root[p][1] - root[p][0]) / 8 for p in ejes}
        for _ in range(pasos):
            mejora = True
            while mejora:
                mejora = False
                for p in ejes:
                    for s in (1, -1):
                        r = dict(q, **{p: min(max(q[p] + s * h[p], root[p][0]), root[p][1])})
                        v = sentido * f(r)
                        if v > val:
                            val, q, mejora = v, r, True
            h = {p: x / 2 for p, x in h.items()}
        out.append({"punto": q, "valor": sentido * val})
    out.sort(key=lambda d: -sentido * d["valor"])
    return out


def correr_sup(dis, j, out, ev_p, tope):
    G = grupo(dis, j)
    mm = dict(menu(j, G["bd"], G["bf"]), **G["full"])
    root = {p: mm[p] for p in MT.VARS}                     # orden del gradiente de motor_theta
    gam = float(G["fixed"]["gamma"])
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "sup_theta C2", "diseno": dis, "instrumento": j,
           "grupo": G["grupo"], "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in root.items()},
           "fijos": G["fixed"], "T2": T2, "metodo": "rama y cota conjunta (tau, theta) con motor_theta (natural ∩ valor medio + monotonía)"}
    irr = IRRELEVANTES[j]
    doc["ejes_irrelevantes"] = {"ejes": sorted(irr), "fundamento": FUNDAMENTO_IRR[j]}
    bit = Bitacora(ev_p, Path(out), doc)
    t_opt = time.time()
    ini = optimizar(root, lambda pt: _mid(punto(pt, G["fixed"], dis)), irr, sentido=1)
    doc["optimizacion_inicial"] = {"puntos": ini[:3], "segundos": round(time.time() - t_opt, 1)}
    try:
        res = bb_sup(root, lambda b: evaluar(b, G["fixed"], dis), lambda pt: punto(pt, G["fixed"], dis), T2, tope, bit, escala=gam,
                     irrelevantes=irr, cota_natural=lambda b: natural(b, G["fixed"], dis).hi, inicio=[x["punto"] for x in ini])
    except CotaIncompatible as exc:
        res = {"estado": "INVALIDO_COTA_INCOMPATIBLE", "diagnostico": str(exc)[:2000], "L": None, "U": None, "brecha": None}
        res["lema_E0"] = dict(MT.ESTADISTICA)
        bit.resumen(force=True, **res)
        print(json.dumps({k: res[k] for k in ("estado", "diagnostico")}, ensure_ascii=False)[:600])
        raise SystemExit(2)
    res["lema_E0"] = dict(MT.ESTADISTICA)
    if MT.ESTADISTICA["lema_violaciones"]:
        res["estado"] = "INVALIDO_VIOLACION_DEL_LEMA"
    bit.resumen(force=True, **res)
    print(json.dumps({k: res[k] for k in ("L", "U", "brecha", "estado", "cajas", "mono", "sin_grad", "vivas")}))


def tau_estrella(th_pt, fixed, dis, j, bd, bf, n=24):
    """τ que maximiza Rn en el punto θ (búsqueda en flotante sobre una rejilla + refinamiento): SOLO orienta; las cotas
    se calculan después con encierros."""
    m = menu(j, bd, bf)
    (dl, dh), (fl, fh) = m["tau_d"], m["tau_f"]
    eng = C2N.MotorNormalizado(EM.IParams.from_primitive_box({p: (v, v) for p, v in th_pt.items()}, fixed), dis)

    def f(x, y):
        v, _ = eng.R(Iv(x, x), Iv(y, y))
        return 0.5 * (v.lo + v.hi)
    xs = [dl + (dh - dl) * i / n for i in range(n + 1)] if dh > dl else [dl]
    ys = [fl + (fh - fl) * i / n for i in range(n + 1)] if fh > fl else [fl]
    best = max(((f(x, y), x, y) for x in xs for y in ys))
    _, x, y = best
    hx, hy = (dh - dl) / n, (fh - fl) / n
    for _ in range(30):
        hx, hy = hx / 2, hy / 2
        cand = [(x + sx * hx, y + sy * hy) for sx in (-1, 0, 1) for sy in (-1, 0, 1)]
        cand = [(min(max(a, dl), dh), min(max(b, fl), fh)) for a, b in cand]
        best = max(best, max((f(a, b), a, b) for a, b in cand))
        _, x, y = best
    return best


def c2_punto_cert(th_pt, fixed, dis, j, bd, bf):
    """Techo certificado sup_τ Rn(τ; θ0)/γ en el punto θ0 (sup_bound con el motor normalizado): (cota inferior, superior)."""
    P = EM.IParams.from_primitive_box({p: (v, v) for p, v in th_pt.items()}, fixed)
    eng = C2N.MotorNormalizado(P, dis)
    sb = EM.sup_bound(eng, j, bd, bf, tol=1e-7, max_boxes=4000, jump_budget=0)
    return sb.lower / P.gamma.lo, max(sb.lower, sb.upper) / P.gamma.lo


def correr_inf(dis, j, out, ev_p, tope):
    G = grupo(dis, j)
    fixed, bd, bf = G["fixed"], G["bd"], G["bf"]
    gam = float(fixed["gamma"])
    full = G["full"]
    m = menu(j, bd, bf)
    Tdm, Tfm = Iv(*m["tau_d"]), Iv(*m["tau_f"])
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "inf_theta C2", "diseno": dis, "instrumento": j,
           "grupo": G["grupo"], "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in full.items()},
           "menu": m, "fijos": fixed, "T2": T2,
           "metodo": "rama y cota en theta; cota inferior por tau candidatos con motor_theta; techo certificado en puntos"}
    bit = Bitacora(ev_p, Path(out), doc)
    W = {p: (full[p][1] - full[p][0]) or 1.0 for p in MT.STRUCT}
    best = {"U": math.inf, "pt": None, "techo": None}
    n = {"cajas": 0, "mono": 0, "techos": 0, "podadas": 0, "sin_grad": 0}

    def techo(th):
        c = centro(th)
        n["techos"] += 1
        lo, hi = c2_punto_cert(c, fixed, dis, j, bd, bf)
        if hi < best["U"]:
            best.update(U=hi, pt=c, techo=[lo, hi])

    def cota_inf(th):
        c = centro(th)
        _, x, y = tau_estrella(c, fixed, dis, j, bd, bf)
        e, g = MT.encierro(th, fixed, dis, Iv(x, x), Iv(y, y))
        n["cajas"] += 1
        if g is None:
            n["sin_grad"] += 1
        return e.lo / gam, (x, y)

    def mono(th):
        st = {}
        e, g = MT.encierro(th, fixed, dis, Tdm, Tfm, st)
        if g is None:
            return th, False
        b2, cambio = dict(th), False
        for i, p in enumerate(MT.STRUCT):
            lo, hi = th[p]
            gi = g[2 + i]
            if hi > lo and (gi.lo > 0.0 or gi.hi < 0.0):
                b2[p] = (lo, lo) if gi.lo > 0.0 else (hi, hi)
                cambio = True
        return b2, cambio

    # (a) cota inferior GLOBAL trivial y rigurosa: τ = 0 está en el menú y Rn(0; θ) = 0, así que C2(θ) >= 0 para todo θ
    # (b) cota superior: optimización en flotante de C2 aproximada (máximo sobre una rejilla de τ) + techo CERTIFICADO
    irr = IRRELEVANTES[j]
    doc["ejes_irrelevantes"] = {"ejes": sorted(irr), "fundamento": FUNDAMENTO_IRR[j]}
    (dl, dh), (fl, fh) = m["tau_d"], m["tau_f"]

    def eje_tau(lo, hi):
        """Rejilla de τ lineal + LOGARÍTMICA hacia 0 (el ínfimo puede estar en τ ~ 1e-3: medido en G-d)."""
        if hi == lo:
            return [lo]
        lin = [lo + (hi - lo) * i / 4 for i in range(5)]
        log = [lo + (hi - lo) * 2.0 ** -k for k in range(2, 16, 1 if dh == dl or fh == fl else 2)]
        return sorted(set(lin + log))
    rej = [(x, y) for x in eje_tau(dl, dh) for y in eje_tau(fl, fh)]
    if len(rej) > 80:                               # df: rejilla producto reducida
        rd = sorted(set([dl + (dh - dl) * i / 2 for i in range(3)] + [dl + (dh - dl) * 2.0 ** -k for k in range(2, 14, 3)]))
        rf = sorted(set([fl + (fh - fl) * i / 2 for i in range(3)] + [fl + (fh - fl) * 2.0 ** -k for k in range(2, 14, 3)]))
        rej = [(x, y) for x in rd for y in rf]

    def c2_aprox(th_pt):
        eng = C2N.MotorNormalizado(EM.IParams.from_primitive_box({p: (v, v) for p, v in th_pt.items()}, fixed), dis)
        return max(_mid(eng.R(Iv(x, x), Iv(y, y))[0]) for x, y in rej) / gam
    t_opt = time.time()
    ini = optimizar(full, c2_aprox, irr, sentido=-1, n_azar=60, n_arranques=2, pasos=10)
    doc["optimizacion_inicial"] = {"puntos": ini, "segundos": round(time.time() - t_opt, 1)}
    for x in ini:
        c = x["punto"]
        n["techos"] += 1
        lo, hi = c2_punto_cert(c, fixed, dis, j, bd, bf)
        x["techo_certificado"] = [lo, hi]
        if hi < best["U"]:
            best.update(U=hi, pt=c, techo=[lo, hi])
    bit.resumen(force=True, L=0.0, U=best["U"], brecha=best["U"], punto_cota_superior=best["pt"], techo_punto=best["techo"],
                cota_inferior_trivial="C2 >= 0 porque tau = 0 pertenece al menú y Rn(0; theta) = 0", **n)
    th0, _ = mono(dict(full))
    L0, t0 = cota_inf(th0)
    heap = [(max(L0, 0.0), 0, th0)]
    cont = 1
    estado = "tope"
    traza = []
    while heap:
        L = min(heap[0][0], best["U"])
        brecha = best["U"] - L
        traza.append([round(time.time() - bit.t0, 1), n["cajas"], L, best["U"]])
        bit.resumen(L=L, U=best["U"], brecha=brecha, vivas=len(heap), punto_cota_superior=best["pt"], techo_punto=best["techo"], **n)
        if brecha <= T2:
            estado = "convergido"
            break
        if time.time() - bit.t0 > tope:
            break
        lb, _, th = heapq.heappop(heap)
        if lb >= best["U"]:
            n["podadas"] += 1
            continue
        libres = [p for p in MT.STRUCT if th[p][1] > th[p][0] and p not in irr]
        if not libres:
            heapq.heappush(heap, (lb, cont, th))
            estado = "caja_degenerada_viva"
            break
        p = max(libres, key=lambda q: (th[q][1] - th[q][0]) / W[q])
        lo, hi = th[p]
        mid = lo + (hi - lo) / 2
        for h in (dict(th, **{p: (lo, mid)}), dict(th, **{p: (mid, hi)})):
            h, cambio = mono(h)
            if cambio:
                n["mono"] += 1
            lbh, tt = cota_inf(h)
            lbh = max(lbh, lb, 0.0)               # la cota del padre y C2 >= 0 siguen valiendo en la hija
            # techo en el centro si la estimación en flotante puede mejorar U
            c = centro(h)
            est, _, _ = tau_estrella(c, fixed, dis, j, bd, bf)
            if est / gam < best["U"]:
                techo(h)
            bit.ev(evento="caja", eje=p, L=lbh, caja={q: list(v) for q, v in h.items()}, tau=tt)
            if lbh < best["U"]:
                heapq.heappush(heap, (lbh, cont, h))
                cont += 1
            else:
                n["podadas"] += 1
        heap = [x for x in heap if x[0] < best["U"]]
        heapq.heapify(heap)
    L = min(heap[0][0], best["U"]) if heap else best["U"]
    if not heap:
        estado = "convergido"
    if MT.ESTADISTICA["lema_violaciones"]:
        estado = "INVALIDO_VIOLACION_DEL_LEMA"
    bit.resumen(force=True, L=L, U=best["U"], brecha=best["U"] - L, estado=estado, vivas=len(heap), punto_cota_superior=best["pt"],
                lema_E0=dict(MT.ESTADISTICA),
                techo_punto=best["techo"], traza=traza[:: max(1, len(traza) // 80)] + traza[-1:], **n)
    print(json.dumps({"L": L, "U": best["U"], "brecha": best["U"] - L, "estado": estado, **n}))


# ============================================================================================ validación
def sonda(out, tope):
    """Para cada uno de los 6 grupos: (1) gradiente puntual frente a diferencias centradas; (2) contención del gradiente
    puntual en el de una caja pequeña que lo contiene; (3) el encierro (natural ∩ valor medio) de cajas pequeñas
    aleatorias contiene el valor en puntos de la caja; (4) anchos natural vs valor medio y tiempos por evaluación."""
    rng = random.Random(20261005)
    t0 = time.time()
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "grupos": {}}
    for dis in ("G", "N"):
        for j in ("d", "df", "f"):
            if time.time() - t0 > tope:
                break
            G = grupo(dis, j)
            fixed = G["fixed"]
            mm = dict(menu(j, G["bd"], G["bf"]), **G["full"])
            root = {p: mm[p] for p in MT.VARS}
            ejes = list(root)
            fila = {"fd": [], "contencion_grad": [], "contencion_valor": [], "anchos": [], "tiempos_s": []}
            for rep in range(6):
                pt = {p: lo + (hi - lo) * rng.random() for p, (lo, hi) in root.items()}
                # (1) diferencias centradas en cada eje libre
                ta = time.time()
                eb, g = evaluar({p: (v, v) for p, v in pt.items()}, fixed, dis)
                fila["tiempos_s"].append(round(time.time() - ta, 3))
                if g is None:
                    fila["fd"].append({"rep": rep, "sin_gradiente": True})
                    continue
                errs = {}
                for i, p in enumerate(ejes):
                    lo, hi = root[p]
                    if hi == lo:
                        continue
                    h = 1e-6 * (hi - lo)
                    a_, b_ = max(lo, pt[p] - h), min(hi, pt[p] + h)
                    va = punto(dict(pt, **{p: a_}), fixed, dis)
                    vb = punto(dict(pt, **{p: b_}), fixed, dis)
                    fd = (0.5 * (vb.lo + vb.hi) - 0.5 * (va.lo + va.hi)) / (b_ - a_)
                    gi = g[i]
                    tolr = 1e-4 * max(1.0, abs(fd)) + 2 * (vb.hi - vb.lo + va.hi - va.lo) / (b_ - a_)
                    errs[p] = {"fd": fd, "g": [gi.lo, gi.hi], "ok": gi.lo - tolr <= fd <= gi.hi + tolr}
                fila["fd"].append({"rep": rep, "ok": all(v["ok"] for v in errs.values()), "ejes": errs})
                # (2)/(3) caja pequeña alrededor del punto
                rel = 10 ** rng.uniform(-4, -1.5)
                box = {p: (max(lo, pt[p] - rel * (hi - lo)), min(hi, pt[p] + rel * (hi - lo))) for p, (lo, hi) in root.items()}
                ta = time.time()
                st = {}
                e, gb = evaluar(box, fixed, dis, st)
                tb = time.time() - ta
                nat = MT.valor({p: box[p] for p in MT.STRUCT}, fixed, dis, Iv(*box["tau_d"]), Iv(*box["tau_f"]))
                fila["anchos"].append({"rel": rel, "natural": nat.hi - nat.lo, "encierro": e.hi - e.lo, "con_gradiente": gb is not None,
                                       "motivo": st.get("motivo_sin_gradiente"), "s": round(tb, 3)})
                if gb is not None:
                    fila["contencion_grad"].append(all(gb[i].lo <= g[i].lo and g[i].hi <= gb[i].hi for i in range(len(ejes))))
                ok = True
                for _ in range(8):
                    q = {p: lo + (hi - lo) * rng.random() for p, (lo, hi) in box.items()}
                    v = punto(q, fixed, dis)
                    ok = ok and (e.lo <= v.hi and v.lo <= e.hi)
                fila["contencion_valor"].append(ok)
            fila["cumple"] = (all(x.get("ok", True) for x in fila["fd"]) and all(fila["contencion_grad"]) and all(fila["contencion_valor"]))
            doc["grupos"][f"{dis}-{j}"] = fila
            doc["segundos"] = round(time.time() - t0, 1)
            N.write_json_atomic(Path(out), doc)
    doc["lema_E0"] = dict(MT.ESTADISTICA)
    doc["cumple_todo"] = all(f["cumple"] for f in doc["grupos"].values()) and MT.ESTADISTICA["lema_violaciones"] == 0
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({k: (f["cumple"], sum(1 for x in f["fd"] if x.get("sin_gradiente")), [round(a["encierro"] / max(a["natural"], 1e-300), 4) for a in f["anchos"]])
                      for k, f in doc["grupos"].items()}))


def conocidos(out):
    """Rama y cota (bb_sup) en funciones con extremos CONOCIDOS, con encierros por intervalos y gradientes exactos:
    K1 máximo interior f = 1 - (x-0,3)^2 - (y-0,7)^2 en [0,1]^2 -> 1; K2 máximo en vértice f = x y en [-1,2]^2 -> 4;
    K3 mínimo en vértice (sup de -x y) -> 2; K4 quiebre f = -|x - 0,5| - (y - 0,25)^2 (gradiente sin cota en el quiebre:
    None) -> 0; K5 función plana en un eje f = x (1 - x) + 0 y -> 0,25; K6 seis variables f = -Σ (x_i - c_i)^2 -> 0."""
    def mk(fun, grad):
        def evc(b):
            X = {p: Iv(*v) for p, v in b.items()}
            return fun(X), grad(X)
        def pv(pt):
            return fun({p: Iv(v, v) for p, v in pt.items()})
        return evc, pv
    casos = {
        "K1": ({"x": (0.0, 1.0), "y": (0.0, 1.0)}, lambda X: 1.0 - (X["x"] - 0.3).sqr() - (X["y"] - 0.7).sqr(),
               lambda X: (-2.0 * (X["x"] - 0.3), -2.0 * (X["y"] - 0.7)), 1.0),
        "K2": ({"x": (-1.0, 2.0), "y": (-1.0, 2.0)}, lambda X: X["x"] * X["y"], lambda X: (X["y"], X["x"]), 4.0),
        "K3": ({"x": (-1.0, 2.0), "y": (-1.0, 2.0)}, lambda X: -(X["x"] * X["y"]), lambda X: (-X["y"], -X["x"]), 2.0),
        "K4": ({"x": (0.0, 1.0), "y": (0.0, 1.0)},
               lambda X: -(Iv(0.0, max(abs(X["x"].lo - 0.5), abs(X["x"].hi - 0.5))) if X["x"].lo <= 0.5 <= X["x"].hi
                           else Iv(min(abs(X["x"].lo - 0.5), abs(X["x"].hi - 0.5)), max(abs(X["x"].lo - 0.5), abs(X["x"].hi - 0.5)))) - (X["y"] - 0.25).sqr(),
               lambda X: None if X["x"].lo <= 0.5 <= X["x"].hi else (Iv(-1.0, -1.0) if X["x"].lo > 0.5 else Iv(1.0, 1.0), -2.0 * (X["y"] - 0.25)), 0.0),
        "K5": ({"x": (0.0, 1.0), "y": (0.0, 1.0)}, lambda X: X["x"] - X["x"].sqr() + 0.0 * X["y"],
               lambda X: (1.0 - 2.0 * X["x"], Iv(0.0, 0.0)), 0.25),
        "K6": ({f"x{i}": (-1.0, 1.0) for i in range(6)},
               lambda X: -sum(((X[f"x{i}"] - 0.1 * i).sqr() for i in range(6)), Iv(0.0, 0.0)),
               lambda X: tuple(-2.0 * (X[f"x{i}"] - 0.1 * i) for i in range(6)), 0.0),
    }
    doc = {"etiqueta": N.ETIQUETA, "casos": {}}
    for k, (root, fun, grad, exacto) in casos.items():
        evc, pv = mk(fun, grad)
        bit = Bitacora(None, Path(out).with_suffix(".tmp.json"), {})
        r = bb_sup(root, evc, pv, 1e-6, 60.0, bit)
        r.pop("traza", None)
        r["exacto"] = exacto
        r["contiene"] = r["L"] - 1e-12 <= exacto <= r["U"] + 1e-12
        r["cumple"] = r["contiene"] and r["estado"] == "convergido"
        doc["casos"][k] = r
    tmp = Path(out).with_suffix(".tmp.json")
    if tmp.exists():
        tmp.unlink()
    doc["cumple_todo"] = all(c["cumple"] for c in doc["casos"].values())
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({k: (c["cumple"], c["L"], c["U"], c["cajas"], c["mono"]) for k, c in doc["casos"].items()}))


def main():
    m = sys.argv[1]
    if m == "sonda":
        sonda(sys.argv[2], float(sys.argv[3]))
    elif m == "conocidos":
        conocidos(sys.argv[2])
    elif m == "sup":
        correr_sup(sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5]), float(sys.argv[6]))
    elif m == "inf":
        correr_inf(sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5]), float(sys.argv[6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
