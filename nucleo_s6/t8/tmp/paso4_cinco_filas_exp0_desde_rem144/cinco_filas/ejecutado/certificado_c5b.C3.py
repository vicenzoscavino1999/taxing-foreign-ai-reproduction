"""rem144 — CERTIFICADO CANDIDATO de las cinco filas T8 (7028, 7208, 8144, 8186, 9578), SEPARADO de la vista vigente.
Solo lectura y aritmética exacta. No llama al modelo (evaluate, capture_ceiling, sup_bound, bridge), no recorre soportes ni modifica T8, la vista
ni los ledgers. Toma la salida del análisis REM144-M2 (C5B_MASA_M2.json, script cota_masa_c5b.M2.py) por sha256 fijado y:
  1. re-autentica la vista vigente (inventario sellado rem143 + pin), el ledger del revisor rem144 y las fuentes de captura (banda);
  2. comprueba que U_global es exactamente el máximo de las cuatro cotas por bloque y que el bloque L-MASA quedó resuelto en los 20 nodos;
  3. por fila: línea de la vista (sha256 de línea + LF = ledger), valor exacto, magnitud C2/share, y Fraction(v) > U_global + banda;
  4. ENSAYO DE CONEXIÓN con el finalizador INSTALADO (_finalize de paso4/instalacion/herramientas/b/unidades.py, a8aded1d…, cargado por
     ruta + sha256 como en conexion_captura.cargar), sin alterar su regla, sobre COPIAS en memoria de fin_por_unidad:
       C-a  c2 = (-inf, U_global + banda]  -> outside_support   (encierro exterior: la conexión mínima propuesta);
       C-b  c2 = (-inf, U + banda]         -> computed          (la cota U aceptada supera v: NO decide, por eso las filas siguen pendientes);
       C-c  c2 = (-inf, v]                 -> computed          (cota + banda = v: la igualdad no excluye).
     Un «computed» con encierro exterior NO es prueba de pertenencia; el adaptador existente solo usa la exclusión cuando v > cota + banda.
El certificado no lleva tiempos: es determinista y se verifica recomputándolo (modo verificar) y comparando bytes.
Uso: python -B -I -X utf8 certificado_c5b.py <raiz> <area> <salida.json> [verificar <certificado.json> | ensayo_fuente]"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

R, Y, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
MODO = sys.argv[4] if len(sys.argv) > 4 else "emitir"
W = Path("@@W_FS@@")
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
FALLOS = []


def need(t, c):
    if not t:
        FALLOS.append(c)
    return bool(t)


A137, A143 = "paso4_emision_lambda_conexion_captura_desde_rem137", "paso4_emision_t8_testigo_desde_rem143"
SELLO = {A137: "59188e65c2d8dd665679f3b47780e2859633505b260127cc435c772431bf92b2", A143: "0dd9b3d81e120ad685995ce5ba988ddf356c29bce24e1a88505e258c67e1a8da"}
PIN = {"M2_SALIDA": "05c10ea6d2e8f87b96704f66d9c1edb6c188a2d6c528b4d086ab3061d9da4691",
       "M2_SCRIPT": "f725f028ff1fa63281a69d5ff30fa51df988cb9ac4f9654ab62e9a29355b3a1b",
       "VISTA": "ec6e3929dd6be8dbb56b17493ce51061b95dde7991722832045a1c4411c8fd93",
       "LEDGER144": "7ed13ccf8123e1bce9e013bdbdce56d5df29de37699a192f1aaa32c55555241c",
       "NOTA_U": "cf738de6945a86ffb55ed0994610bc6d8d9d21860a5cd0b7e92a27f0afe0f34a",
       "FINALIZADOR": "a8aded1db50f80feffd62bcb655e62e5f93487364a3c4e625f47dcdbd1f17c86",
       "CONEXION": "f7a8d23f5d2558843f4620052b49d20250cf23c67ac8a02d54ea57db1c05dba7",
       "CERTIFICACION": "4741b4ea3b72fc2f754cc2d8c79dd9dd718f8e37205bf3e4ee5c0c539be60f4b"}
INV = {}
for ar, s in SELLO.items():
    e = (R / "tmp" / ar / "audit/entrega.json").read_bytes()
    need(sha(e) == s, "SELLO:" + ar)
    INV[ar] = json.loads(e)["files"]


def auten(ar, rel, pin):
    b = (R / "tmp" / ar / rel).read_bytes()
    need(INV[ar].get(rel, {}).get("sha256") == sha(b), "NO_AUTENTICO:%s/%s" % (ar, rel))
    need(sha(b) == pin, "PIN:%s/%s" % (ar, rel))
    return b


m2_b = (Y / "cinco_filas/salida/C5B_MASA_M2.json").read_bytes()
if MODO == "ensayo_fuente":
    m2_b = m2_b + b" "                                                  # ENSAYO: salida M2 alterada en memoria; debe rechazarse
need(sha(m2_b) == PIN["M2_SALIDA"], "PIN:C5B_MASA_M2.json")
need(sha((Y / "cinco_filas/ejecutado/cota_masa_c5b.M2.py").read_bytes()) == PIN["M2_SCRIPT"], "PIN:cota_masa_c5b.M2.py")
m2 = json.loads(m2_b)
vista = auten(A143, "t8_testigo_vista_T8_TESTIGO/VISTA_T8_CAPTURA.jsonl", PIN["VISTA"])
fuentes = json.loads(auten(A137, "c2_conexion/candidato_v3/FUENTES_CAPTURA.json",
                           INV[A137]["c2_conexion/candidato_v3/FUENTES_CAPTURA.json"]["sha256"]))
auten(A137, "c2_conexion/candidato_v3/conexion_captura.py", PIN["CONEXION"])
auten(A137, "c2_conexion/candidato_v3/certificacion_fila.py", PIN["CERTIFICACION"])
led_b = (W / "review_20261104_rem144_T8_testigo_aceptado.json").read_bytes()
need(sha(led_b) == PIN["LEDGER144"], "LEDGER144")
need(sha((W / "review_20261101_rem137_cota.txt").read_bytes()) == PIN["NOTA_U"], "NOTA_U")
ledger = json.loads(led_b)
BANDA = Fr(fuentes["cota_U"]["banda"])
U = Fr(fuentes["cota_U"]["U"])
need(BANDA == Fr(1e-07) == Fr(m2["banda"]) and U == Fr(m2["U_aceptada"]), "BANDA_O_U")

# ---------------------------------------------------------------------------------------------- 2. coherencia interna de M2
need(m2["kind"] == "c5b-cota-masa-adoptante-rem144" and m2["modo"] == "real" and m2["conforme"] is True and m2["fallos"] == [], "M2_NO_CONFORME")
need(m2["productivo"] is False and m2["no_se_aplica_a_T8_ni_a_la_vista_vigente"] is True, "M2_NATURALEZA")
cotas = {k: Fr(v) for k, v in m2["cotas_por_bloque"].items()}
UG = Fr(m2["U_global_hi"])
need(len(cotas) == 4 and None not in m2["cotas_por_bloque"].values() and UG == max(cotas.values()), "U_GLOBAL_NO_ES_MAXIMO")
masa = m2["masa_adoptante"]
pend_gr = m2["casos_c5_pendientes_tras_intervalos"]
need(m2["masa_ok"] is True and len(pend_gr) == 1 and len(masa) == 20 and all(n["resuelto"] for n in masa)
     and max(Fr(n["cota_hi"]) for n in masa) == cotas["G_rho_menor_1_por_masa"], "MASA_NO_RESUELTA")
need(len({(n["rho"], n["a"]) for n in masa}) == 20, "MASA_NODOS_REPETIDOS")
need(all(Fr(c["cota_hi"]) <= cotas["N_todo_rho"] for c in m2["detalle_c5_intervalos"]["N_todo_rho"])
     and all(Fr(c["cota_hi"]) <= cotas["G_rho_1"] for c in m2["detalle_c5_intervalos"]["G_rho_1"]), "DETALLE_NO_ACOTADO")
gr = m2["detalle_c5_intervalos"]["G_rho_menor_1"]
cubiertos = [c for c in gr if Fr(c["cota_hi"]) <= cotas["G_rho_menor_1_por_C5"]]
resto = [c for c in gr if Fr(c["cota_hi"]) > cotas["G_rho_menor_1_por_C5"]]
need(len(gr) == len(cubiertos) + 1 and [{k: c[k] for k in ("kappa_tilde", "phi", "eta_d", "eta_f")} for c in resto] == pend_gr, "PARTICION_G_RHO_MENOR_1")
need(len(m2["detalle_c5_intervalos"]["N_todo_rho"]) == len(m2["detalle_c5_intervalos"]["G_rho_1"]) == len(gr) == 750, "COMBINACIONES_750")


# ---------------------------------------------------------------------------------------------- 4. finalizador instalado (ruta + sha256)
def finalizador():
    ruta = R / "paso4/instalacion/herramientas/b/unidades.py"
    need(sha(ruta.read_bytes()) == PIN["FINALIZADOR"], "PIN:FINALIZADOR")
    for p in ("paso4/instalacion/src", "paso4/instalacion"):
        if str(R / p) not in sys.path:
            sys.path.insert(0, str(R / p))
    spec = importlib.util.spec_from_file_location("unidades_finalizador_c5b", ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["unidades_finalizador_c5b"] = mod                       # como conexion_captura._modulo (dataclasses lo exige)
    spec.loader.exec_module(mod)
    return mod._finalize


FIN = finalizador()


def finalizar(fin, c2):
    fila = {}
    FIN(fila, dict(fin), {}, c2)
    return fila["result_status"]


# ---------------------------------------------------------------------------------------------- 3. filas
lineas = vista.split(b"\n")
pendientes = {p["row"]: p for p in ledger["pending_rows"]}
dec = {d["fila"]: d for d in m2["decision_por_fila"]}
FILAS = [7028, 7208, 8144, 8186, 9578]
need(sorted(pendientes) == FILAS == sorted(dec), "CINCO_FILAS")
UNIVERSO = ("soporte global C2 (C_2_share, gamma = z_m = 1) de la corrida destino; está contenido en el universo del plan 6cec0a6d… "
            "(retícula L0 completa de los diez conjuntos base, 843.750 puntos estructurales por conjunto; diseños G y N; menús d, f, df; "
            "tasas en [0, binary64(0,6)]^2 ⊆ [0, 3/5]^2), y la cota cubre ese universo entero, de modo que cubre el soporte de cualquier corrida del plan")
filas = []
for f in FILAS:
    p, d = pendientes[f], dec[f]
    ln = lineas[f]
    r = json.loads(ln)
    v = Fr(p["required_exact"])
    fin = r["historico"]["fin_por_unidad"]
    ok = (sha(ln + b"\n") == p["product_line_sha256"] and r["clave_fila"] == p["row_key"] == d["clave_fila"] and r["run_id"] == p["destination_run"]
          and r["estado_sucesor"] == "pendiente_soporte_global" and r["causa_pendiente"] == "SIN_SOPORTE_GLOBAL_C2" and p["classification"] == "pendiente"
          and Fr(d["v_exacto"]) == v == Fr(fin["value"]) and r["inversion_id"] == "capture_required")
    need(ok, "FILA_NO_COINCIDE:%d" % f)
    magn = fin.get("k") == "C2" and r["historico"].get("target_unit") == "share" and fin.get("c2_defined") is True
    need(magn, "MAGNITUD_NO_C2_SHARE:%d" % f)
    supera = v > UG + BANDA
    need(supera, "V_NO_SUPERA_U_GLOBAL_MAS_BANDA:%d" % f)
    need(not v > U + BANDA, "U_ACEPTADA_YA_DECIDIA:%d" % f)
    ca = finalizar(fin, (float("-inf"), UG + BANDA))
    cb = finalizar(fin, (float("-inf"), U + BANDA))
    cc = finalizar(fin, (float("-inf"), v))
    need(ca == "outside_support" and cb == "computed" and cc == "computed", "CONEXION:%d" % f)
    est = "demostracion_candidata_suficiente" if (ok and magn and supera and ca == "outside_support") else "pendiente"
    filas.append({"fila": f, "clave_fila": r["clave_fila"], "cell_id": r["cell_id"], "run_destino": r["run_id"], "pais": fin["country"], "conjunto": fin["set"],
                  "magnitud": {"k": fin["k"], "target_unit": r["historico"]["target_unit"]},
                  "valor_requerido_exacto": p["required_exact"], "valor_requerido": float(v), "linea_vista_sha256": p["product_line_sha256"],
                  "estado_vigente": r["estado_sucesor"], "estado_historico_declarado_aparte": r["estado_historico"],
                  "soporte_a_cubrir": UNIVERSO,
                  "cota": {"U_global_hi": str(UG), "U_global": float(UG), "banda": str(BANDA), "U_global_mas_banda": str(UG + BANDA)},
                  "argumento": "L-MASA (G, rho<1, combinación kappa_tilde=1/5, phi=1, eta_d=eta_f=1/10) + C5 trasladado a binary64 (N, G rho=1, G rho<1 restante)",
                  "garantia_numerica": "aritmética racional exacta (Fraction); binary64 encerrado por intervalos [min, max](decimal, binary64) y Bernoulli exacta; sin coma flotante en la decisión",
                  "desigualdad": "Fraction(v) > U_global + banda  =>  outside_support (la igualdad no excluye; nunca prueba pertenencia)",
                  "holgura_exacta": str(v - UG - BANDA), "holgura": float(v - UG - BANDA),
                  "cota_U_aceptada_no_decide": {"U_mas_banda": str(U + BANDA), "v_menor_o_igual": True},
                  "ensayo_conexion_finalizador": {"C-a_(-inf,U_global+banda]": ca, "C-b_(-inf,U+banda]": cb, "C-c_(-inf,v]": cc},
                  "estado": est, "causa": None if est != "pendiente" else ",".join(FALLOS) or "sin causa registrada"})
if FALLOS:                                                              # C3: cualquier fallo (también global) deja TODAS las filas pendientes
    for x in filas:
        x["estado"], x["causa"] = "pendiente", ",".join(FALLOS)

doc = {"kind": "certificado-candidato-c5b-rem144", "experimental": True, "productivo": False, "candidato_separado_de_la_vista_vigente": True,
       "no_modifica": ["T8", "vista vigente ec6e3929…", "doce ledgers", "original", "instalación", "C0", "D7"],
       "requiere_dictamen": True,
       "tipo_prueba_propuesto": "exclusion_cota_U_global",
       "semantica_propuesta": "encierro_exterior_por_cota_U_global",
       "regla_propuesta": "Fraction(v) > U_global + banda  =>  outside_support (la igualdad no excluye; nunca prueba pertenencia)",
       "fuentes": {"analisis_salida_sha256": PIN["M2_SALIDA"], "analisis_script_sha256": PIN["M2_SCRIPT"], "vista_sha256": PIN["VISTA"],
                   "ledger_rem144_sha256": PIN["LEDGER144"], "nota_U_sha256": PIN["NOTA_U"],
                   "fuentes_captura_sha256": INV[A137]["c2_conexion/candidato_v3/FUENTES_CAPTURA.json"]["sha256"], "finalizador_sha256": PIN["FINALIZADOR"],
                   "conexion_captura_sha256": PIN["CONEXION"], "certificacion_fila_sha256": PIN["CERTIFICACION"],
                   "plan_sha256": fuentes["plan_sha256"]},
       "premisas": m2["premisas"],
       "cotas_por_bloque": m2["cotas_por_bloque"], "cotas_por_bloque_float": m2["cotas_por_bloque_float"],
       "U_global_hi": str(UG), "U_global": float(UG), "U_aceptada": str(U), "banda": str(BANDA),
       "bloque_L_MASA": {"combinacion": pend_gr[0], "nodos": [{k: n[k] for k in ("rho", "a", "cota", "cajas_evaluadas", "cajas_finales")} for n in masa]},
       "particion_G_rho_menor_1": {"por_C5_trasladado": len(cubiertos), "por_L_MASA": len(resto)},
       "filas": filas,
       "conexion_minima_futura": {
           "pieza_existente": "certificacion_fila.py (4741b4ea…) + conexion_captura.adaptar (f7a8d23f…) + _finalize instalado (a8aded1d…)",
           "cambio": ("un tipo de prueba más, «exclusion_cota_U_global», con el mismo esquema que exclusion_cota_U y la cota fija U_global_hi de este "
                      "certificado (y su sha256) en lugar de U; en adaptar, la rama de exclusión usa c2 = (-inf, U_global_hi + banda]; _finalize no cambia"),
           "condiciones": ["dictamen que acepte L-MASA, el traslado binary64 y este certificado", "la misma magnitud C2/share y la misma banda",
                           "una ronda de conexión/emisión con su propio alcance y acto nativo del autor; no se reutilizan actos consumidos"],
           "no_hace": "no se desarrolla otro emisor, no se toca T8 ni la vista vigente en rem144"},
       "fallos": FALLOS, "conforme": not FALLOS and all(x["estado"] == "demostracion_candidata_suficiente" for x in filas)}
texto = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
if MODO == "verificar":
    previo = Path(sys.argv[5]).read_bytes()
    iguales = previo == texto
    with OUT.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps({"kind": "verificacion-certificado-c5b-rem144", "certificado_sha256": sha(previo), "recomputado_sha256": sha(texto),
                             "iguales": iguales, "fallos": FALLOS, "conforme": iguales and doc["conforme"]}, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"iguales": iguales, "certificado_sha256": sha(previo), "fallos": FALLOS}))
    raise SystemExit(0 if iguales and doc["conforme"] else 4)
with OUT.open("xb") as fh:
    fh.write(texto)
print(json.dumps({"conforme": doc["conforme"], "fallos": FALLOS, "sha256": sha(texto),
                  "filas": [(x["fila"], x["estado"], x["holgura"], x["ensayo_conexion_finalizador"]) for x in filas]}, ensure_ascii=False))
raise SystemExit(0 if doc["conforme"] else 4)
