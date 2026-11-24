"""rem144 — CINCO FILAS T8 (bloque acotado de 90 min): COTA SUPERIOR POR MASA ADOPTANTE para G con rho < 1 y TRASLADO BINARY64 de C5.
Solo lectura de fuentes autenticadas y aritmética exacta (Fraction). NO llama al modelo (evaluate, capture_ceiling, sup_bound, bridge), no
recorre soportes reales ni busca máximos: verifica cotas cerradas con encierros dirigidos; Decimal solo PROPONE candidatos de raíces que se
COMPRUEBAN con enteros exactos (lo^n <= x^m <= hi^n).

Premisas citadas (aceptadas): P1 lema E0 <= 0 y cota U (nota rem137 cf738de6…); P2 acoplamiento por adopción (C3_ACOPLADA §1 de rem137,
aceptado en el dictamen rem138 §4); H3 signos verdaderos de los trinomios (nota rem137 §5); plan 6cec0a6d… = retícula L0 completa de los diez
conjuntos base (843.750 puntos estructurales por conjunto), menús d/f/df, diseños G/N, tasas en [0,3/5]^2 ⊇ [0, binary64(0.6)]^2.

Lema nuevo L-MASA (diseño G, rho < 1; gamma = z_m = 1, kappa0 = kappa_tilde, Pareto(a), Bpot = a/(a-1)):
  rótulo F ⇒ prior F (Lema 1 de rem136) y F1-F0 = (1-t̃_d) z - k_F z^rho > 0 ⇔ z^(1-rho) > c := k_F/(1-t̃_d), k_F = κ̃(1+φ t̃_f).
  Luego F ⊆ {z > z*}, z* = m^(1/(1-rho)), m = max(1, c); con los momentos Pareto cerrados (Lema 1 (4.5)):
    x = A/Bpot <= m^(-β),  w = κ̃ W/Bpot <= κq m^(-(β+1)),  β = (a-1)/(1-rho),  κq = κ̃ (a-1)/(a-rho);
  y con E0 <= 0:  R/Bpot <= Φ := m^(-β) [ D(τ_d) + κq Q(τ_f)/m ],  D = τ_d (1-τ_d)^η_d,  Q = τ_f (1-τ_f)^(η_f-φ).
  Φ es no creciente en m (m >= 1); como t̃_f >= Q (ocultación >= 0), basta c >= κ̃(1+φ Q)/(1-t̃_d): NO se usa el término de ocultación.
  Para c <= 1 (adopción total posible) m = 1 y Φ = D + κq Q: se trata explícitamente.
Verificación: subdivisión adaptativa por intervalos del rectángulo de tasas [0,3/5]^2 (monotonía de D, t̃_d, Q en cada caja), por cada nodo
(rho, a) del bloque pendiente; se detiene cuando toda caja tiene cota < OBJETIVO o al alcanzar el máximo de cajas (entonces: pendiente).
Traslado binary64: cada primitiva es el intervalo [min(decimal, binary64), max(decimal, binary64)]; las potencias con exponente binary64 se
encierran desde el exponente decimal con desigualdades de Bernoulli exactas. Se recalculan también los tres bloques de C5 (N, G rho=1, G rho<1)
con esos intervalos, para que la cota global cubra el universo del plan y no solo los nodos decimales.
Escribe en exclusiva <salida.json>. Uso: python -B -I -X utf8 cota_masa_c5b.py <raiz> <area> <salida.json> [ensayo]"""
import csv
import hashlib
import json
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

R, Y, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
MODO = sys.argv[4] if len(sys.argv) > 4 else "real"
T0 = time.time()
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: sha(Path(p).read_bytes())  # noqa: E731
FALLOS = []
W = Path("@@W_FS@@")


def need(t, c):
    if not t:
        FALLOS.append(c)
    return bool(t)


# ------------------------------------------------------------------------------------------------ A. fuentes autenticadas
A136, A108, A137, A138, A143 = ("paso4_procedencia_cota_desde_rem136", "paso4_conciliacion_portabilidad_desde_rem108",
                                "paso4_emision_lambda_conexion_captura_desde_rem137", "paso4_preparacion_captura_testigo_desde_rem138",
                                "paso4_emision_t8_testigo_desde_rem143")
SELLO = {A136: "16a2e53e21ba1d3615616bc598ea281ec078f55a5bd97b96a4ae9746934a4087", A108: "b6ccab3ded6e957df5ebfd585a5402b5a10948aaa3e0bfa52192165fb6022cf4",
         A137: "59188e65c2d8dd665679f3b47780e2859633505b260127cc435c772431bf92b2", A138: "364bf4725adf4ffffc187cf3950724d1d92f8f63e38b75c556b03de64100220c",
         A143: "0dd9b3d81e120ad685995ce5ba988ddf356c29bce24e1a88505e258c67e1a8da"}
INV = {}
for ar, s in SELLO.items():
    need(HF(R / "tmp" / ar / "audit/entrega.json") == s, "SELLO:" + ar)
    INV[ar] = json.loads((R / "tmp" / ar / "audit/entrega.json").read_bytes())["files"]


def auten(ar, rel, pin=None):
    b = (R / "tmp" / ar / rel).read_bytes()
    if MODO == "ensayo_fuente" and rel.endswith("C5_COTA_NODOS_v2.json"):
        b = b + b" "                                                     # ENSAYO: fuente alterada en memoria; debe rechazarse
    need(INV[ar].get(rel, {}).get("sha256") == sha(b), "NO_AUTENTICO:%s/%s" % (ar, rel))
    if pin:
        need(sha(b) == pin, "PIN:%s/%s" % (ar, rel))
    return b


PINES = {"C5_NOTA": "52559a004067f71be99a2a677b1a9a712823151af03c75c2ebb425ccb59a313a",
         "C5_V2": "a9ce8434330a0009aca13852db6234e76ca89424379cdcb96021100a2b21c247",
         "C5_C2": "25ec15a48479b373352f49090274da00333fd0161dabcd51a0d2b525833f580c",
         "VISTA": "ec6e3929dd6be8dbb56b17493ce51061b95dde7991722832045a1c4411c8fd93",
         "LEDGER144": "7ed13ccf8123e1bce9e013bdbdce56d5df29de37699a192f1aaa32c55555241c",
         "NOTA_U": "cf738de6945a86ffb55ed0994610bc6d8d9d21860a5cd0b7e92a27f0afe0f34a",
         "MODELO": "24af1c4222a25a6e569cb42311406ffeb6d5df0603d3abe15eb34e10bcbaf4d9",
         "DICT138": "84ba70eeb452223179fd86af155badd2b7ffcdf05121c4d83a3c0d6897b7984d",
         "DICT139": "327763d78c1611e74622dbb573c1e3c5cbbe7a8cfa1bb0cca90cdc6778b56d76",
         "DICT140": "c1ba8187ef9e79d2f8f88d9ec5f550308637a3a70ff537fecbd0d6e1b160fa9c"}
auten(A138, "cinco_filas/C5_NOTA.md", PINES["C5_NOTA"])
c5 = json.loads(auten(A138, "cinco_filas/C5_COTA_NODOS_v2.json", PINES["C5_V2"]))
auten(A138, "ejecutado/c5_cota_nodos.C2.py", PINES["C5_C2"])
vista_b = auten(A143, "t8_testigo_vista_T8_TESTIGO/VISTA_T8_CAPTURA.jsonl", PINES["VISTA"])
need(HF(W / "review_20261104_rem144_T8_testigo_aceptado.json") == PINES["LEDGER144"], "LEDGER144")
need(HF(W / "review_20261101_rem137_cota.txt") == PINES["NOTA_U"], "NOTA_U")
for n, p in (("DICT138", "review_20261101_rem138_dictamen.txt"), ("DICT139", "review_20261101_rem139_dictamen.txt"), ("DICT140", "review_20261102_rem140_dictamen.txt")):
    need(HF(W / p) == PINES[n], n)
ledger = json.loads((W / "review_20261104_rem144_T8_testigo_aceptado.json").read_bytes())
resto = {t["fila"]: t for t in json.loads(auten(A136, "c_cota/RESTO_C3.json"))["filas"]}
anexo = json.loads(auten(A108, "conciliacion/ensamblajes/T8_anexo.json"))["filas"]
fuentes = json.loads(auten(A137, "c2_conexion/candidato_v3/FUENTES_CAPTURA.json"))
need(fuentes["modelo"]["sha256"] == PINES["MODELO"] and HF(R / fuentes["modelo"]["ruta"]) == PINES["MODELO"], "MODELO")
need(fuentes["plan_sha256"] == "6cec0a6d662104dab6a490cea647cd24ae995819a416eaf3cfd4fd9f3c060e42", "PLAN")
BANDA = Fr(fuentes["cota_U"]["banda"])
need(BANDA == Fr(1e-07) == Fr(fuentes["banda_tol_converge"]), "BANDA")
U_ACEPTADA = Fr(fuentes["cota_U"]["U"])
K = Fr(fuentes["cota_U"]["K_binary64_0.2"])
need(K == Fr(0.2), "K")

# ------------------------------------------------------------------------------------------------ B. las cinco filas (vigente y ledger)
FILAS = [7028, 7208, 8144, 8186, 9578]
lineas = vista_b.split(b"\n")
pend = {p["row"]: p for p in ledger["pending_rows"]}
need(sorted(pend) == FILAS and ledger["accepted_counts"] is not None, "LEDGER_CINCO")
filas = []
for f in FILAS:
    t, an, p = resto[f], anexo[f], pend[f]
    v = Fr(t["v_exacto"])
    fila = json.loads(lineas[f])
    ok = (an["cell_id"] == t["cell_id"] == fila["cell_id"] and Fr(an["C_2_required"]) == v == Fr(p["required_exact"]) and an["pais"] == t["pais"]
          and an["inversion_id"] == fila["inversion_id"] == "capture_required" and fila["clave_fila"] == p["row_key"] and fila["run_id"] == p["destination_run"] == t["run"]
          and sha(lineas[f] + b"\n") == p["product_line_sha256"] and fila["estado_sucesor"] == "pendiente_soporte_global" and p["classification"] == "pendiente"
          and t["grupo"] == "EQ-TECHO-T8-1")
    need(ok, "FILA_NO_COINCIDE:%d" % f)
    filas.append({"fila": f, "clave_fila": fila["clave_fila"], "cell_id": fila["cell_id"], "run": fila["run_id"], "pais": an["pais"], "conjunto": an["conjunto"],
                  "unidad": an["unidad_primera"], "v": float(v), "v_exacto": t["v_exacto"], "estado_vigente": fila["estado_sucesor"],
                  "causa_pendiente_vigente": fila.get("causa_pendiente"), "captura_c2_vigente": fila.get("captura_c2"),
                  "estado_historico_outside_support": fila["estado_historico"], "ledger_rem144": p["classification"], "linea_sha256": sha(lineas[f] + b"\n"), "autenticada": ok})

# ------------------------------------------------------------------------------------------------ C. nodos L0: decimal y binary64
D7 = R / "fase2_datos/d7_calibracion/versions/10a0bd5bb8ea48d54d1bd0916b072afcf8cd5a4eed9c5ec16a90a728f021b739"
for nombre, fa in fuentes["d7"]["archivos"].items():
    need(HF(R / fa["ruta"]) == fa["sha256"], "D7_ARCHIVO:" + nombre)
with open(D7 / "support_set.csv", encoding="utf-8", newline="") as fh:
    sup = list(csv.DictReader(fh))
STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
BASE = ["CMP-E1.macro", "CMP-E1.micro", "COL-E2-2023.2023p.macro", "COL-E2-2023.2023p.micro", "COL-E2-2023.2024p.macro", "COL-E2-2023.2024p.micro",
        "PER-E0E3.macro", "PER-E0E3.micro", "PER-E1.macro", "PER-E1.micro"]
txt = {}
for s in BASE:
    for p in STRUCT:
        rows = [r for r in sup if r["support_set_id"] == s and r["parameter_id"] == p and r["variant_id"] == "primary"]
        need(len(rows) == 1, "SOPORTE:%s/%s" % (s, p))
        txt[(s, p)] = rows[0]["level0_nodes"]
need(all(txt[(s, p)] == txt[(BASE[0], p)] for s in BASE for p in STRUCT), "NODOS_DISTINTOS_ENTRE_CONJUNTOS")
need({f["conjunto"] for f in filas} <= set(BASE), "FILA_FUERA_DE_LOS_CONJUNTOS_BASE")
NODOS = {}
for p in STRUCT:
    vals = json.loads(txt[(BASE[0], p)])
    if MODO == "ensayo_premisa" and p == "kappa_tilde":
        vals = vals + [0.25]                                            # ENSAYO: altera una premisa (κ̃ > K): debe rechazar
    NODOS[p] = [(Fr(Decimal(repr(x))), Fr(x)) for x in vals]            # (decimal del texto, binary64 que recibe el motor)
B = Fr(3, 5)
need(Fr(0.6) < B, "DOMINIO_B64")
# premisas H4 de la nota U, sobre texto y binary64
need(all(d > 1 and b > 1 for d, b in NODOS["a"]), "PREMISA_A")
need(all(0 < d <= 1 and 0 < b <= 1 for d, b in NODOS["rho"]), "PREMISA_RHO")
need(all(d >= Fr(1, 10) and b >= Fr(1, 10) for d, b in NODOS["eta_d"] + NODOS["eta_f"]), "PREMISA_ETA")
need(all(0 <= d <= 1 and 0 <= b <= 1 for d, b in NODOS["phi"]), "PREMISA_PHI")
need(all(0 < d <= K and 0 < b <= K for d, b in NODOS["kappa_tilde"]), "PREMISA_KAPPA")
need(all(r[1] < a[0] for r in NODOS["rho"] for a in NODOS["a"]), "PREMISA_RHO_LT_A")


def iv(par):
    return (min(par), max(par))


# ------------------------------------------------------------------------------------------------ D. encierros dirigidos exactos
getcontext().prec = 100
EPS = Fr(1, 10 ** 50)
GRID = 10 ** 60


def ro(lo, hi):
    """redondeo hacia fuera a la rejilla 10^-60 (acota el tamaño de las fracciones; nunca estrecha)."""
    return (Fr((lo.numerator * GRID) // lo.denominator, GRID), Fr(-((-hi.numerator * GRID) // hi.denominator), GRID))


POT_CACHE = {}


def pot(x, e):
    """encierro verificado de x^e, x > 0 racional, e racional de denominador pequeño: lo^n <= x^m <= hi^n con enteros exactos."""
    key = (x, e)
    if key in POT_CACHE:
        return POT_CACHE[key]
    if e == 0:
        return (Fr(1), Fr(1))
    m, n = e.numerator, e.denominator
    need(n <= 1000, "EXPONENTE_GRANDE")
    base = x if m >= 0 else 1 / x
    t = base ** abs(m)
    if n == 1:
        res = (t, t) if t.denominator < 10 ** 80 else ro(t, t)
    else:
        a = Fr(((Decimal(base.numerator) / Decimal(base.denominator)).ln() * Decimal(abs(m)) / Decimal(n)).exp())   # candidato, no prueba
        lo, hi = ro(a - EPS, a + EPS)
        if not (lo > 0 and lo ** n <= t <= hi ** n):
            raise ArithmeticError("ENCIERRO_NO_VERIFICADO")
        res = (lo, hi)
    POT_CACHE[key] = res
    return res


def xy(x, y):
    """encierro racional de x^y para |y| <= 1/2 (Bernoulli): base b >= 1 ⇒ b^t ∈ [1, 1+t(b-1)]; b < 1 ⇒ b^t ∈ [1-t(1-b)/b, 1]."""
    if y == 0:
        return (Fr(1), Fr(1))
    need(abs(y) <= Fr(1, 2), "PERTURBACION_GRANDE")
    b, t = (x, y) if y > 0 else (1 / x, -y)
    return (Fr(1), 1 + t * (b - 1)) if b >= 1 else (1 - t * (1 - b) / b, Fr(1))


def mul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return ro(min(ps), max(ps))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def div(a, b):
    assert b[0] > 0
    return mul(a, (1 / b[1], 1 / b[0]))


def k(c):
    return (Fr(c), Fr(c))


def imax(*xs):
    return (max(x[0] for x in xs), max(x[1] for x in xs))


def imin(*xs):
    return (min(x[0] for x in xs), min(x[1] for x in xs))


def hull(*xs):
    return (min(x[0] for x in xs), max(x[1] for x in xs))


def potx(x, epar):
    """x^e para x > 0 punto y e en el par (decimal, binary64): monótona en e ⇒ envolvente de los dos extremos."""
    ed, eb = epar
    pd = pot(x, ed)
    if eb == ed:
        return pd
    return hull(pd, mul(pd, xy(x, eb - ed)))


def par_suma(p, c):           # exponente 1 + η: (decimal + c, binary64 + c)
    return (p[0] + c, p[1] + c)


def par_resta(p, q):           # η_f - φ como par extremo (decimal-decimal, y la peor combinación binary64)
    cands = [p[i] - q[j] for i in (0, 1) for j in (0, 1)]
    return (p[0] - q[0], min(cands) if min(cands) != p[0] - q[0] else max(cands))


# funciones del modelo en un punto τ (racional) con primitivas en intervalo (par decimal/binary64)
def D(t, eta):                 # τ (1-τ)^η, decreciente en η
    return mul(k(t), potx(1 - t, eta)) if t > 0 else (Fr(0), Fr(0))


def td(t, eta):                # t̃_d = (1 - (1-τ)^(1+η))/(1+η) = ∫0^τ (1-s)^η ds, decreciente en η
    if t == 0:
        return (Fr(0), Fr(0))
    out = []
    for e in set(eta):
        p = potx(1 - t, (eta[0] + 1, e + 1)) if e != eta[0] else pot(1 - t, e + 1)
        out.append(mul(sub(k(1), p), k(1 / (1 + e))))
    return hull(*out)


def alfa(ef, ph):
    """todas las combinaciones (η_f, φ) extremas: α = η_f - φ como par (decimal, peor binary64)."""
    return [(ef[0] - ph[0], ef[i] - ph[j]) for i in (0, 1) for j in (0, 1)]


def Q(t, ef, ph):              # τ (1-τ)^(η_f-φ), decreciente en α
    if t == 0:
        return (Fr(0), Fr(0))
    return hull(*[mul(k(t), potx(1 - t, ap)) for ap in alfa(ef, ph)])


def Dmax(eta):                 # sup_{τ∈[0,B]} D: D crece en [0, 1/(1+η)]; decreciente en η ⇒ extremo superior con η mínimo
    lo_e, hi_e = min(eta), max(eta)
    up = D(min(B, 1 / (1 + lo_e)), (eta[0], lo_e) if lo_e != eta[0] else (eta[0], eta[0]))[1]
    dn = D(min(B, 1 / (1 + hi_e)), (eta[0], hi_e) if hi_e != eta[0] else (eta[0], eta[0]))[0]
    return (dn, up)


def Qmax(ef, ph):              # sup Q: crece en [0,1) si α <= 0, en [0, 1/(1+α)] si α > 0; decreciente en α
    vals = []
    for ap in alfa(ef, ph):
        for a_ in set(ap):
            tq = B if a_ <= 0 else min(B, 1 / (1 + a_))
            vals.append(mul(k(tq), potx(1 - tq, (ap[0], a_) if a_ != ap[0] else (ap[0], ap[0]))))
    return hull(*vals)


# ------------------------------------------------------------------------------------------------ E. bloques de C5 con primitivas en intervalo
def caso_N(kap, ph, ed, ef):
    Ds, Qm = Dmax(ed), Qmax(ef, ph)
    kp, pp = iv(kap), iv(ph)
    t1 = add(mul(Ds, sub(k(1), kp)), mul(mul(kp, Qm), sub(k(1), mul(pp, Ds))))
    t2 = (Qm[0] / (1 + pp[1] * Qm[0]), Qm[1] / (1 + pp[0] * Qm[1]))       # q/(1+φq) crece en q y decrece en φ
    need(Ds[1] * pp[1] < 1, "N_MONOTONIA")
    return imax(Ds, imin(t1, t2))


def caso_G1(kap, ph, ed, ef):
    Ds, Qm = Dmax(ed), Qmax(ef, ph)
    kp, pp = iv(kap), iv(ph)
    if pp[1] == 0:
        return add(Ds, mul(kp, Qm)), None
    need(pp[0] > 0 and pp[1] <= 1, "G1_PHI")
    Tm = 1 - kp[0] - pp[0] * kp[0] * (Qm[0] + Qm[1]) / 2                 # el corte τc es cualquiera en [0,B]: la prueba no depende de él
    base = 1 - (1 + ed[0]) * Tm
    tc = B
    if base > 0:
        c = Fr(float((Decimal(base.numerator) / Decimal(base.denominator)) ** (Decimal(1) / (1 + Decimal(ed[0].numerator) / Decimal(ed[0].denominator)))))
        tc = min(B, max(Fr(0), (1 - c).limit_denominator(10 ** 9)))
    if ed[0] == ed[1]:
        tq = min(tc, 1 / (1 + ed[0]))
    else:                                                                # η inexacto: el argmax de D en [0,τc] es τc para todo η del intervalo
        need(tc <= 1 / (1 + max(ed)), "G1_TC")
        tq = tc
    g1 = add(D(tq, ed), mul(kp, Qm))
    g1B = add(Ds, mul(kp, Qm))
    g2 = add(D(tc, ed), mul(sub(sub(k(1), td(tc, ed)), kp), (1 / pp[1], 1 / pp[0])))
    return imax(Ds, g1, imin(g1B, g2)), str(tc)


def caso_Gr(kap, ph, ed, ef):
    Ds, Qm = Dmax(ed), Qmax(ef, ph)
    kp, pp = iv(kap), iv(ph)
    cm = (Qm[0] / (1 + pp[1] * Qm[0]), Qm[1] / (1 + pp[0] * Qm[1]))
    crece_D = B <= 1 / (1 + max(ed))
    crece_g2 = cm[1] < 1 and B <= (1 - cm[1]) / (1 - cm[1] + max(ed))
    if crece_D and crece_g2:
        return add(D(B, ed), imin(mul(kp, Qm), mul(sub(k(1), td(B, ed)), cm))), "esquina (D y g2 crecientes)"
    return add(Ds, mul(kp, Qm)), "sin acoplar (D* + κ̃ Qm)"


# ------------------------------------------------------------------------------------------------ F. L-MASA: G con rho < 1, por nodo (rho, a)
OBJETIVO = Fr(78, 100)          # < min v - banda (0,78288536…): toda caja debe quedar por debajo
MAX_CAJAS = 20000


def beta_par(a, r):
    """(β decimal, β mínimo sobre la caja de primitivas): β = (a-1)/(1-rho) crece en a y en rho."""
    return ((a[0] - 1) / (1 - r[0]), (min(a) - 1) / (1 - min(r)))


def kq_hi(kap, a, r):
    return max(kv * (av - 1) / (av - rv) for kv in kap for av in a for rv in r)


def m_pot_hi(m, bpar):
    """cota superior de m^(-β), m >= 1, β ∈ {decimal, binary64}: no creciente en β ⇒ β mínimo; si β_b64 < β_dec, Bernoulli exacto."""
    if m == 1:
        return Fr(1)
    bd, bb = bpar
    hi = pot(m, -bd)[1]
    if bb < bd:
        hi = hi * (1 + (bd - bb) * (m - 1))                             # m^δ <= 1 + δ (m-1), 0 <= δ <= 1
    return hi


def phi_caja(d0, d1, f0, f1, kap, ph, ed, ef, bpar, kqh, sin_masa=False):
    """cota de Φ en la caja [d0,d1]×[f0,f1]: Φ crece en D y Q y no crece en m ⇒ D(d1), Q(f1) y m0 = max(1, c(d0, f0)) por defecto."""
    Dh = D(d1, ed)[1]
    Qh = Q(f1, ef, ph)[1]
    Ql = Q(f0, ef, ph)[0]
    tl = td(d0, ed)[0]
    if sin_masa:                 # ENSAYO: sin la reducción por masa (β = 0, κq = κ̃): relajación de C5 en la caja; NO debe resolver
        return Dh + min(max(kap) * Qh, (1 - tl) * Qh / (1 + min(ph) * Qh)), None
    c_lo = ro(min(kap) * (1 + min(ph) * Ql) / (1 - tl), Fr(0))[0]       # redondeo hacia abajo: m menor ⇒ cota mayor (válida)
    m0 = max(Fr(1), c_lo)
    mp = m_pot_hi(m0, bpar)
    return mp * (Dh + kqh * Qh / m0), m0


def verificar_nodo(kap, ph, ed, ef, r, a, sin_masa=False, max_cajas=MAX_CAJAS):
    need(max(ed) <= Fr(1, 2) and B <= 1 / (1 + max(ed)), "MASA_D_CRECE")
    need(all(ap[0] <= 0 and max(ap) <= 0 for ap in alfa(ef, ph)), "MASA_Q_CRECE")   # α <= 0: Q crece en [0,B]
    need(max(r) < 1, "MASA_RHO_MENOR_1")
    bpar, kqh = beta_par(a, r), kq_hi(kap, a, r)
    cajas = [(Fr(0), B, Fr(0), B)]
    finales, n_eval, peor, en_c1 = [], 0, Fr(0), 0
    while cajas:
        d0, d1, f0, f1 = cajas.pop()
        n_eval += 1
        val, m0 = phi_caja(d0, d1, f0, f1, kap, ph, ed, ef, bpar, kqh, sin_masa)
        if val < OBJETIVO:
            finales.append(val)
            peor = max(peor, val)
            en_c1 += 1 if m0 == 1 else 0
            continue
        if n_eval >= max_cajas or (d1 - d0) < Fr(1, 2 ** 20):
            return {"resuelto": False, "cajas_evaluadas": n_eval, "motivo": "MAX_CAJAS o caja mínima con cota >= objetivo", "valor_caja": str(val), "caja": [str(d0), str(d1), str(f0), str(f1)]}
        dm, fm = (d0 + d1) / 2, (f0 + f1) / 2
        cajas += [(d0, dm, f0, fm), (dm, d1, f0, fm), (d0, dm, fm, f1), (dm, d1, fm, f1)]
    return {"resuelto": True, "cajas_evaluadas": n_eval, "cajas_finales": len(finales), "cajas_finales_con_m_1": en_c1,
            "cota_hi": str(peor), "cota": float(peor), "beta": [str(x) for x in bpar], "kappa_q_hi": str(kqh)}


# ------------------------------------------------------------------------------------------------ G. recálculo de C5 con intervalos + L-MASA
P = {p: NODOS[p] for p in STRUCT}
res = {"N_todo_rho": [], "G_rho_1": [], "G_rho_menor_1": []}
pendientes_gr = []
for kap, ph, ed, ef in product(P["kappa_tilde"], P["phi"], P["eta_d"], P["eta_f"]):
    base = {"kappa_tilde": str(kap[0]), "phi": str(ph[0]), "eta_d": str(ed[0]), "eta_f": str(ef[0])}
    bn = caso_N(kap, ph, ed, ef)
    res["N_todo_rho"].append(dict(base, cota_hi=str(bn[1]), cota=float(bn[1])))
    br, modo = caso_Gr(kap, ph, ed, ef)
    bg, tc = caso_G1(kap, ph, ed, ef)
    bg = imin(bg, br)
    res["G_rho_1"].append(dict(base, cota_hi=str(bg[1]), cota=float(bg[1]), tau_c=tc))
    res["G_rho_menor_1"].append(dict(base, cota_hi=str(br[1]), cota=float(br[1]), via=modo))
    if br[1] >= OBJETIVO:
        pendientes_gr.append((kap, ph, ed, ef, base))
masa = []
for kap, ph, ed, ef, base in pendientes_gr:
    for r in [x for x in P["rho"] if x[0] < 1]:
        for a in P["a"]:
            out = verificar_nodo(kap, ph, ed, ef, r, a)
            masa.append(dict(base, rho=str(r[0]), a=str(a[0]), rho_b64=str(r[1]), a_b64=str(a[1]), **out))
# casos dirigidos (ensayos del argumento)
ensayos = {}
if pendientes_gr:
    kap, ph, ed, ef, base = pendientes_gr[0]
    r9, a25 = [x for x in P["rho"] if x[0] == Fr(9, 10)][0], [x for x in P["a"] if x[0] == Fr(5, 2)][0]
    # 1 interior: caja degenerada en un punto interior; su valor no supera la cota certificada del nodo
    bpar, kqh = beta_par(a25, r9), kq_hi(kap, a25, r9)
    vi, mi = phi_caja(Fr(3, 10), Fr(3, 10), Fr(3, 10), Fr(3, 10), kap, ph, ed, ef, bpar, kqh)
    nodo = [m for m in masa if m["rho"] == "9/10" and m["a"] == "5/2"][0]
    ensayos["interior_(3/10,3/10)_rho_9/10_a_5/2"] = {"valor": float(vi), "m": float(mi), "<=_cota_nodo": vi <= Fr(nodo["cota_hi"])}
    # 2 frontera: esquina (3/5,3/5) y origen
    ve, me = phi_caja(B, B, B, B, kap, ph, ed, ef, bpar, kqh)
    vo, mo = phi_caja(Fr(0), Fr(0), Fr(0), Fr(0), kap, ph, ed, ef, bpar, kqh)
    ensayos["frontera_esquina"] = {"valor": float(ve), "m": float(me), "c_mayor_1": me > 1, "<=_cota_nodo": ve <= Fr(nodo["cota_hi"])}
    ensayos["frontera_origen"] = {"valor": float(vo), "m": float(mo), "igual_0": vo == 0}
    # 3 transición de adopción: τ_f = B; τ_d a ambos lados de c = 1 (c <= 1 ⇒ m = 1, adopción total posible; c > 1 ⇒ masa parcial)
    lado = {}
    for td_ in (Fr(52, 100), Fr(56, 100)):
        vv, mm = phi_caja(td_, td_, B, B, kap, ph, ed, ef, bpar, kqh)
        lado[str(td_)] = {"valor": float(vv), "m": float(mm), "adopcion": "total posible (m = 1)" if mm == 1 else "parcial (m > 1)"}
    ensayos["transicion_adopcion"] = lado
    ensayos["transicion_adopcion_ok"] = lado["13/25"]["m"] == 1.0 and lado["14/25"]["m"] > 1.0
    # 4 caso no cubierto: el mismo nodo SIN la reducción por masa (β = 0, κq = κ̃) reproduce la relajación de C5 y no resuelve
    # 5 punto exacto (falsación, no prueba): celda del plan G, rho = 9/10, a = 2, β̃ = 1/4, z_cost = 1 (δ = 1) en τ = (13/25, 3/5).
    #   Si F0-I0 > 0, (1-t̃_d) > k_F (c < 1 con t̃_f COMPLETO) y 1 - τ_dβ - t̃_d - κ̃φ t̃_f >= 0, toda la población es F con prior F:
    #   E0 = 0, A = E[z], W = E[z^rho] y R/Bpot = D + κ̃ (a-1)/(a-rho) Q EXACTAMENTE. L-MASA (m = 1) debe coincidir y no superar la cota del nodo.
    a2 = [x for x in P["a"] if x[0] == 2][0]
    bt = [x for x in P["beta_tilde"] if x[0] == Fr(1, 4)][0]
    tdp, tfp = Fr(13, 25), B
    tdi, Qi = td(tdp, ed), Q(tfp, ef, ph)
    al = (ef[0] - ph[0], max(ef) - ph[0])                                  # α = -9/10 (φ = 1 exacto)
    x = 1 - tfp
    hid = []
    for a_ in set(al):
        pa = potx(x, (al[0], a_)) if a_ != al[0] else pot(x, a_)
        pa1 = potx(x, (al[0] + 1, a_ + 1)) if a_ != al[0] else pot(x, a_ + 1)
        h_ = sub(mul(sub(k(1), pa), k(1 / a_)), mul(sub(k(1), pa1), k(1 / (a_ + 1))))
        hid.append(mul(h_, (min(ef), max(ef))))
    tfi = add(Qi, hull(*hid))                                              # t̃_f = Q + ocultación (encierro)
    priorF = tdp * max(bt) < 1
    f1f0 = (1 - tdi[1]) > max(kap) * (1 + max(ph) * tfi[1])
    f1i1 = 1 - tdp * max(bt) - tdi[1] - max(kap) * max(ph) * tfi[1] >= 0
    exacto = add(D(tdp, ed), mul((min(kap) * (min(a2) - 1) / (min(a2) - min(r9)), kq_hi(kap, a2, r9)), Qi))
    vpt, mpt = phi_caja(tdp, tdp, tfp, tfp, kap, ph, ed, ef, beta_par(a2, r9), kq_hi(kap, a2, r9))
    nodo2 = [m for m in masa if m["rho"] == "9/10" and m["a"] == "2"][0]
    ensayos["punto_exacto_todo_F"] = {"todo_F_demostrado": priorF and f1f0 and f1i1, "R_sobre_Bpot_exacto": [float(exacto[0]), float(exacto[1])],
                                      "L_MASA_en_el_punto": float(vpt), "m": float(mpt), "coincide": exacto[0] <= vpt and vpt - exacto[1] < Fr(1, 10 ** 12),
                                      "<=_cota_nodo": exacto[1] <= Fr(nodo2["cota_hi"]), "cota_nodo": nodo2["cota"]}
    sm = verificar_nodo(kap, ph, ed, ef, r9, a25, sin_masa=True, max_cajas=1500)
    ensayos["sin_masa_no_resuelve"] = {"resuelto": sm["resuelto"], "cajas_evaluadas": sm["cajas_evaluadas"], "valor_caja": sm.get("valor_caja"), "esperado": "no resuelto"}
ensayos["premisa_alterada"] = "ver modo ensayo_premisa (κ̃ = 0,25 > K debe dar PREMISA_KAPPA)" if MODO == "real" else MODO

# ------------------------------------------------------------------------------------------------ H. cota global y decisión por fila
def peor(lst):
    return max(Fr(c["cota_hi"]) for c in lst)


gr_resueltos = [c for c in res["G_rho_menor_1"] if Fr(c["cota_hi"]) < OBJETIVO]
masa_ok = all(m["resuelto"] for m in masa) and len(masa) == len(pendientes_gr) * 20
cotas = {"N_todo_rho": peor(res["N_todo_rho"]), "G_rho_1": peor(res["G_rho_1"]),
         "G_rho_menor_1_por_C5": peor(gr_resueltos) if gr_resueltos else None,
         "G_rho_menor_1_por_masa": max(Fr(m["cota_hi"]) for m in masa) if masa_ok and masa else None}
U_GLOBAL = max(v for v in cotas.values() if v is not None) if masa_ok else None
decision = []
for f in filas:
    v = Fr(f["v_exacto"])
    sufic = U_GLOBAL is not None and v > U_GLOBAL + BANDA and not FALLOS
    decision.append({"fila": f["fila"], "clave_fila": f["clave_fila"], "v_exacto": f["v_exacto"], "v": f["v"],
                     "cota_global_hi": str(U_GLOBAL) if U_GLOBAL is not None else None, "banda": str(BANDA),
                     "holgura_exacta": str(v - U_GLOBAL - BANDA) if U_GLOBAL is not None else None,
                     "holgura": float(v - U_GLOBAL - BANDA) if U_GLOBAL is not None else None,
                     "desigualdad": "Fraction(v) > U_global + banda  =>  outside_support (exclusión; nunca pertenencia)",
                     "estado": "demostracion_candidata_suficiente_exclusion" if sufic else "pendiente",
                     "causa": None if sufic else ("FALLOS:" + ",".join(FALLOS) if FALLOS else "cota global no inferior a v - banda")})
doc = {"kind": "c5b-cota-masa-adoptante-rem144", "experimental": True, "productivo": False, "candidato_separado": True, "modo": MODO,
       "no_se_aplica_a_T8_ni_a_la_vista_vigente": True, "filas": filas,
       "premisas": {"P1": "E0 <= 0 y U (nota rem137 cf738de6…)", "P2": "acoplamiento por adopción (C3_ACOPLADA §1, aceptado en rem138 §4)",
                    "H3": "signos verdaderos (nota rem137 §5)", "L-MASA": "nuevo: F ⊆ {z^(1-rho) > c}; momentos Pareto cerrados; Φ no creciente en m",
                    "ocultacion": "no usada: basta t̃_f >= Q (ocultación >= 0)",
                    "universo": "plan 6cec0a6d… = retícula L0 completa de los diez conjuntos base (843.750 puntos por conjunto), menús d/f/df (rectángulo), G/N"},
       "dominio_tau": "[0, 3/5]^2 ⊇ [0, binary64(0.6)]^2", "banda": str(BANDA), "U_aceptada": str(U_ACEPTADA),
       "nodos": {p: [[str(d), str(b)] for d, b in v] for p, v in NODOS.items()},
       "c5_original_peores": {k_: c5["resumen"][k_]["peor_cota"] for k_ in c5["resumen"]},
       "recalculo_intervalos_peores": {k_: float(peor(v)) for k_, v in res.items()},
       "casos_c5_pendientes_tras_intervalos": [b for *_, b in pendientes_gr], "masa_adoptante": masa, "masa_ok": masa_ok,
       "cotas_por_bloque": {k_: (str(v) if v is not None else None) for k_, v in cotas.items()},
       "cotas_por_bloque_float": {k_: (float(v) if v is not None else None) for k_, v in cotas.items()},
       "U_global_hi": str(U_GLOBAL) if U_GLOBAL is not None else None, "U_global": float(U_GLOBAL) if U_GLOBAL is not None else None,
       "objetivo_cajas": str(OBJETIVO), "decision_por_fila": decision, "ensayos": ensayos,
       "detalle_c5_intervalos": res, "fallos": FALLOS, "conforme": not FALLOS, "segundos": round(time.time() - T0, 2)}
with OUT.open("x", encoding="utf-8") as fh:
    fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"conforme": doc["conforme"], "fallos": FALLOS, "pendientes_gr": len(pendientes_gr), "masa_ok": masa_ok,
                  "cotas": doc["cotas_por_bloque_float"], "U_global": doc["U_global"],
                  "decision": [(d["fila"], d["estado"], d["holgura"]) for d in decision], "ensayos": ensayos,
                  "masa": [(m["rho"], m["a"], m.get("cota"), m["cajas_evaluadas"]) for m in masa], "segundos": doc["segundos"]}, ensure_ascii=False))
raise SystemExit(0 if doc["conforme"] else 4)
