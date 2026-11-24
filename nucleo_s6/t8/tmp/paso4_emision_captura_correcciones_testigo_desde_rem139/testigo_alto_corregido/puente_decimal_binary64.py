"""rem139 — PUENTE DECIMAL → BINARY64 de la cota inferior del testigo alto (P4-T8-TESTIGO-GARANTIA, parte C). Sin modelo y sin motor.
Reutiliza EXACTAMENTE la fórmula de los controles sellados de rem138 (evaluar_punto, pot, iadd, isub, imul, k_ y dec de
testigo_alto/controles_testigo.py, extraídos por AST de los bytes autenticados contra el inventario sellado 364bf472…) y el MISMO punto
interior τ = (19/32, 19/32), y la evalúa dos veces:
  1. con las primitivas DECIMALES de la celda (regresión: debe reproducir la cota de rem138, 0,7558681452598683547908…);
  2. con las primitivas BINARY64 que usa el motor (Fr(float(Decimal(d))): η_d, η_f, κ̃ = binary64(0,1), binary64(0,2); φ = 0,75 y β̃ = 0,25
     exactas), con aritmética racional exacta en todo salvo las potencias de exponente binary64, que se ENCIERRAN así:
       x^e con e = e_d + δ, e_d = e.limit_denominator(10**4) racional (pot verificado de rem138) y |δ| <= 1e-15:
       para x >= 3/8 se cumple ln x >= -1 (x·e >= (3/8)(8/3) = 1, con e >= 8/3), luego x^δ = exp(δ ln x) y
         δ >= 0: x^e ∈ [x^{e_d}(1 - δ), x^{e_d}]        (exp(y) >= 1 + y,  y = δ ln x ∈ [-δ, 0])
         δ <  0: x^e ∈ [x^{e_d}, x^{e_d}(1 + 2|δ|)]     (exp(y) <= 1 + 2y, y = |δ||ln x| ∈ [0, 1])
     En τ = 19/32 la base es x = 13/32 >= 3/8 (comprobado en exacto).
Alcance preciso: L_b64 es una cota inferior DEMOSTRADA de R/B_pot del modelo EXACTO (real) con las primitivas binary64 en el punto
τ = (19/32, 19/32), que pertenece al dominio [0, binary64(0,6)]² y donde todo_F queda demostrado con esas mismas primitivas. No dice nada
del redondeo del motor ni de su supremo; el validador solo exige C2 + err >= L_b64 (comparación Fraction exacta, sin holgura).
Escribe en exclusiva <salida.json>. Uso: python -B -I -X utf8 puente_decimal_binary64.py <raiz> <salida.json>"""
import ast
import hashlib
import json
import sys
from decimal import Decimal
from fractions import Fraction as Fr
from pathlib import Path

R, OUT = Path(sys.argv[1]), Path(sys.argv[2])
HF = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
A = R / "tmp/paso4_preparacion_captura_testigo_desde_rem138"
SELLO_A = "364bf4725adf4ffffc187cf3950724d1d92f8f63e38b75c556b03de64100220c"
CTRL = A / "testigo_alto/controles_testigo.py"
CTRL_JSON = A / "testigo_alto/controles_T2/CONTROLES_TESTIGO.json"
assert HF(A / "audit/entrega.json") == SELLO_A
inv = json.loads((A / "audit/entrega.json").read_bytes())["files"]
assert inv["testigo_alto/controles_testigo.py"]["sha256"] == HF(CTRL)
assert inv["testigo_alto/controles_T2/CONTROLES_TESTIGO.json"]["sha256"] == HF(CTRL_JSON)
src = CTRL.read_text(encoding="utf-8")
FUNCS = ("pot", "iadd", "isub", "imul", "k_", "dec", "evaluar_punto")
segs = {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name in FUNCS}
assert set(segs) == set(FUNCS)


def entorno():
    ns = {"Fr": Fr, "Decimal": Decimal}
    exec("from decimal import getcontext\ngetcontext().prec = 90\nEPS = Fr(1, 10 ** 60)\n", ns)   # mismas constantes que los controles
    for n in FUNCS:
        exec(segs[n], ns)
    return ns


DEC = entorno()
B64 = entorno()
POT_DEC = B64["pot"]
X_MIN = Fr(3, 8)


def pot_b64(x, e):
    """Encierro de x^e para un exponente racional binary64 e (ver docstring); usa el pot VERIFICADO de rem138 en e_d."""
    e_d = e.limit_denominator(10 ** 4)
    d = e - e_d
    assert abs(d) <= Fr(1, 10 ** 15) and x >= X_MIN and x * Fr(8, 3) >= 1 and x < 1
    lo, hi = POT_DEC(x, e_d)
    PASOS.append({"x": str(x), "e": str(e), "e_d": str(e_d), "delta": str(d)})
    return (lo * (1 - d), hi) if d >= 0 else (lo, hi * (1 + 2 * abs(d)))


PASOS = []
B64["pot"] = pot_b64
CELDA_DEC = {"eta_d": Fr(1, 10), "eta_f": Fr(1, 10), "phi": Fr(3, 4), "kappa_tilde": Fr(1, 5), "beta_tilde": Fr(1, 4)}
TXT = {"eta_d": "0.1", "eta_f": "0.1", "phi": "0.75", "kappa_tilde": "0.2", "beta_tilde": "0.25"}
CELDA_B64 = {k: Fr(float(Decimal(v))) for k, v in TXT.items()}
TAU = Fr(19, 32)
assert Fr(float(TAU)) == TAU and TAU <= Fr(0.6) and 1 - TAU == Fr(13, 32)
args = lambda c: (TAU, TAU, c["eta_d"], c["eta_f"], c["phi"], c["kappa_tilde"], c["beta_tilde"])  # noqa: E731
info_dec, val_dec, F_dec = DEC["evaluar_punto"](*args(CELDA_DEC))
info_b64, val_b64, F_b64 = B64["evaluar_punto"](*args(CELDA_B64))
ctrl = json.loads(CTRL_JSON.read_bytes())
L138 = ctrl["c_dominio"]["puntos"]["interior_19_32"]["R_sobre_Bpot"]["lo"]
regresion = DEC["dec"](val_dec[0]) == L138
doc = {"kind": "puente-decimal-binary64-testigo-rem139", "productivo": False,
       "formula": {"origen": str(CTRL.relative_to(R).as_posix()), "sha256": HF(CTRL), "funciones": list(FUNCS),
                   "funciones_sha256": {n: hashlib.sha256(segs[n].encode("utf-8")).hexdigest() for n in FUNCS},
                   "inventario_sellado": SELLO_A},
       "punto": {"tau_d": "19/32", "tau_f": "19/32", "base_x": "13/32", "en_dominio_b64": True},
       "primitivas_decimales": TXT,
       "primitivas_binary64": {k: {"racional": str(v), "repr": repr(float(v)), "delta_vs_decimal": str(v - CELDA_DEC[k])} for k, v in CELDA_B64.items()},
       "encierro_exponente": {"regla": "x^(e_d+δ): δ>=0 → [x^e_d (1-δ), x^e_d]; δ<0 → [x^e_d, x^e_d (1+2|δ|)]; válido para x >= 3/8 (ln x >= -1) y |δ| <= 1",
                              "pasos": PASOS},
       "decimal": {"todo_F_demostrado": F_dec, "R_sobre_Bpot": info_dec["R_sobre_Bpot"], "L_dec": DEC["dec"](val_dec[0]), "L_rem138": L138,
                   "regresion_igual_rem138": regresion},
       "binary64": {"todo_F_demostrado": F_b64, "margenes": {k: info_b64[k] for k in ("margen_F0_I0", "margen_F1_F0", "margen_F1_I1")},
                    "R_sobre_Bpot": info_b64["R_sobre_Bpot"], "L_b64": DEC["dec"](val_b64[0]), "L_b64_racional": str(val_b64[0])},
       "diferencia_L_b64_menos_L_dec": float(val_b64[0] - val_dec[0]),
       "alcance": ("L_b64 es cota inferior demostrada de R/B_pot del modelo exacto con primitivas binary64 en τ = (19/32, 19/32); no certifica el "
                   "redondeo del motor ni su supremo. El validador exige C2 + err >= L_b64 sin holgura; ninguna fila se garantiza por esta cota sola."),
       "no_hace": ["llamar a capture_ceiling, sup_bound, model.evaluate o bridge", "cargar paper2b", "mallas o barridos"]}
doc["conforme"] = bool(regresion and F_dec and F_b64 and val_b64[0] > 0 and len(PASOS) == 4)
with OUT.open("x", encoding="utf-8") as fh:
    fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"conforme": doc["conforme"], "L_dec": doc["decimal"]["L_dec"][:24], "L_b64": doc["binary64"]["L_b64"][:24],
                  "dif": doc["diferencia_L_b64_menos_L_dec"], "todo_F_b64": F_b64, "regresion": regresion}, ensure_ascii=False))
raise SystemExit(0 if doc["conforme"] else 4)
