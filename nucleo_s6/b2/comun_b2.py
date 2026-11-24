"""rem167 — PIEZA COMÚN del paquete B2 (PROD4.5.6, doce COV, seis grupos K1). Derivada de A/paquete_b1/comun_b1.py (rem165, 25bf92ff…,
índice 9244a279…, aceptado por el dictamen rem166 y usado en la producción B1 aceptada por el dictamen rem167). Contiene:
- FUENTES fijadas por ruta y sha256 (leer() autentica los bytes que entrega);
- fuente_b1(): la cota B1 ACEPTADA (U_C2) desde el libro 19 y la evidencia original de rem166 (no es un máximo puntual);
- q_exterior(): rango de q = kappa(a-1)/(a-rho) por monotonía, EXACTO sobre los extremos de la raíz BINARIA y redondeado hacia afuera
  (q_pot ingenuo de C0 da q.hi = 3 y no se usa);
- construir_manifiesto() / validar_manifiesto(): manifiesto B2 reconstruido desde el censo rem162, el manifiesto B1, D7, la grilla y el
  libro B1; cadena afirmación → grupo → conjunto/kind/edición → estado nacional → vértices/nodo → cota/celdas Q;
- cobertura_esperada() / validar_cobertura(): autoridad de cobertura reconstruida desde el censo CRUDO y el mapa derivado rem162 (igualdad
  EXACTA de conjuntos, deduplicación por clave_entrada_efectiva, inclusiones K5 ⊂ K1∩K3 y K6 ⊂ K2∩K4, 2024p, 9/8 filas);
- cargar_cierre_c0(): cierre de importación REAL de B2 en C0 (__init__, intervalos, macro, external; cobertura solo para la prueba de
  equivalencia) cargado desde sus bytes autenticados, sin __path__;
- evaluar(): núcleo B2 (forma acoplada K1 = n_min(1-q)/(s_Pi gain) en el orden de cobertura.g_enclosure; n_min intervalar; P7, s_T,
  gain, eta_H, 1-q comprobados; un fallo deja PENDIENTE el estado afectado, nunca se descarta un vértice);
- validar_evidencia(): VALIDACIÓN ÚNICA (recalcula s_Pi y Q exactos, n_min, K1 intervalar y referencia exacta independiente; cero
  llamadas a bridge/GridCell.Q). rem168 (P4-B2-VALIDACION-CAMPOS-NUMERICOS, única pieza de ciencia/validación que cambia): estructura
  exacta, tipos estrictos, finitud, orden y concordancia bit a bit número/hex/reconstrucción de k1_lo, k1_hi y Q_float; igualdad canónica
  en las demás representaciones duplicadas; rechazo controlado de toda forma inesperada (sin tolerancias; eps, redondeo y forma acoplada
  sin cambio); lectura()/conciliacion(): regla G_hi = U_C2 - L_K1 <= -1/100 exacta, seis grupos y doce afirmaciones;
- procedencia(): ÚNICA comprobación de origen (solo «lanzamiento»: B2 no implementa continuación entre rondas y la rechaza).
Importable; no escribe nada."""
import csv
import datetime as dt
import hashlib
import importlib.machinery
import io
import json
import math
import sys
import types
from fractions import Fraction
from itertools import product
from pathlib import Path

AQUI = Path(__file__).resolve().parent
Y = AQUI.parent
R = AQUI.parents[2]
T = R / "tmp"
W = Path(r"@@W_WIN@@")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


C0 = T / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
C0_SRC = C0 / "src"
C0_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
C0_INVENTARIO_SHA = "609c6e4dc98cbb8e900e9fe5441feeaf506e22957947c927fb6073cec1cdba4a"
AA_SHA = "631003ca87989ccd0189b33c9bd35e338a6f16fe4a0d50cbc2ccef0ee6f96467"      # C0 herramientas/b/aprobacion_alcance.py
P3CTL_SHA = "546271b057a9635ab39ca3f94e0fd79da46cc7091a4bff873ab8c54e6d875841"
A165 = T / "paso4_invocacion_procedencia_b1_desde_rem165"
PB1 = A165 / "paquete_b1"
X166 = T / "paso4_produccion_b1_doce_cov_desde_rem166"
B1D = X166 / "b1_B1PROD166"
X162 = T / "paso4_preparacion_precisa_doce_cov_desde_rem162"
X161 = T / "paso4_dimensionamiento_doce_cov_desde_rem161"
D7 = R / "salidas_s6/d7/versions/2a25893b09c097b2af22ed2e5be9a4014851faf55bbaaf380c7a078f1a740591"
GRILLA = R / "fase5_cuantificacion/extraccion_grilla/grilla_efectiva.csv"
D6_TAX = R / "fase2_datos/d6_tax_shares_v2/versions/8cea18486cdc83d6a2d25fd7060670cc229b80de2d61de4477ddb57613779441/tax_shares_marg.csv"
BUNDLES = R / "fase2_datos/ca2_bundles/bundles"
# Cierre de importación REAL de B2 en C0 (inventario rem116 609c6e4d…): solo biblioteca estándar; ni model, ni c2_normalizado, ni supremos.
CIERRE_C0 = {
    "__init__.py": "89f7210e7c118c83eec9d73323491e0d8c778b76d1297f703dfca2b86069c72a",
    "intervalos.py": "2607d0cf3f879316c699ec4cd73021bff9ae8f680f7c7c01facb84dfb65aa891",
    "macro.py": "4a94661d1cd0f3fe654f2cf7ecaa740b860e1c735b1585d51fda8f56dd068b98",
    "external.py": "0b14fc0ee0fe4b0bc6d28aebad717dc0e02af03d8b53007be00d7295b72c4a6b",
}
ORDEN_CARGA = ("intervalos", "macro", "external")
# Solo para la prueba de equivalencia con cobertura.g_enclosure/q_pot (ensayos): cobertura importa .intervalos y nada más al cargarse.
COBERTURA_SHA = "d6be53db849fbfaa1d11c3213cc25a0f86a990ef6b3198e36e6b56607f5d9381"
FUENTES = {
    "dictamen_rem167": (W / "review_20261108_rem167_dictamen.txt", "516e65f9b44032584d8cba712d5ca648eaf28d07d39a583ec7b88afa7ac74cb0"),
    "hallazgos_rem167": (W / "review_20261108_rem167_findings.json", "005743341131d56daebe20137c3c15c6bd2b6c6384f1f81fedbdac20cc861b6b"),
    "libro_B1_rem167": (W / "review_20261108_rem167_B1_aceptada.json", "649457712e6f3d33ca596021e5c4878782558579971c4f60a5048455cb1b4535"),
    "x166_inventario": (X166 / "audit/entrega.json", "af7678fda72eca202a3fa0e369c35279f13cbc2241c84e702aadcbf4267b6f4c"),
    "b1_estado": (B1D / "estado_b1.json", "e01f4cf096d105728c67cd04db2bde6ae340aa5379b65a2e58dd4929311f81c6"),
    "b1_evidencia": (B1D / "TRABAJO/EVIDENCIA_B1.json", "8bb0b86e213f88cd902a9a5f8ad6c4ea2f979ee8d948717362d9dc6c66f808c5"),
    "b1_validacion": (B1D / "VALIDACION/VALIDACION_B1.json", "a6806885bfcd47d399564080efe230269f04fd8ca485aa574f4d7b4fdc8d3540"),
    "b1_lectura": (B1D / "VALIDACION/LECTURA_B1.json", "ec3db4e494caeb413407157ae0027c39da5e49f712bf83468d63c5c7e35df960"),
    "a165_inventario": (A165 / "audit/entrega.json", "80d1b2cb1cd7187f8d767b928ac9f4994711a67a9d1ac4931fe499931bf9acf1"),
    "b1_indice": (PB1 / "PAQUETE_B1.json", "9244a279c4b5ede08b9a48b9f2f0ebe99a22ed91cd137b8ae24aa7ae4aa3f13d"),
    "b1_manifiesto": (PB1 / "MANIFIESTO_B1.json", "1194923c273da998db23a83700dac1669693490d01f7fc52668ae39c105fe33e"),
    "x162_inventario": (X162 / "audit/entrega.json", "0ac16b19b91deda3c302f9c82b3be08a653576af20e998a07230cc0b2b026ab7"),
    "x162_contexto_col": (X162 / "soporte/CONTEXTO_COL_POR_GRUPO.json", "5821bb3dae7d4c4dc93e8e956da8984dfeec931587b16b8e7329231c8819d810"),
    "x162_ligadura": (X162 / "soporte/LIGADURA_SOPORTE.md", "bc40c57d0e857ff0dc03229a03d1ea65f732b10f232b22e8bad796f0c516ed64"),
    "x162_enumerador": (X162 / "soporte/enumerar_contextos_rem162.py", "0c57d9a922598a30fc6b09ccec9e21391a27249637cc6dad50cb18969a235c0c"),
    "x162_mapa_derivado": (X162 / "correcciones/MAPA_SOPORTE_REUTILIZACION.derivado.jsonl",
                           "92d5e082aa6d28e113fc16748998146bf999f3dcf07bf2a1184d6f68041eb502"),
    "x162_preparacion_b1_b2": (X162 / "preparacion/PREPARACION_B1_B2.json", "cc73465290d490f14a2b896ad89f6e4e42ca24480c182ea25958d4a2db0dd416"),
    "x162_presupuesto": (X162 / "preparacion/PRESUPUESTO_Y_PARADA.md", "b3f19d73f22123681035f694ccde6aa74f1040cbf3028693ffd3d3435a8644c1"),
    "x162_manifiesto_preparacion": (X162 / "fuentes/MANIFIESTO_PREPARACION.json", "a4c4ab04b19b62a3f80b351933e9c6d767229725db7d00912da39dc8bef97089"),
    "d7_manifest": (D7 / "d7_manifest.json", "9faf63c3ce96ec0e18b7cbf6235bdf21fc6e8bd18ce2ed054e3eb7f7b3a04ff9"),
    "d7_support_set": (D7 / "support_set.csv", "91716f572a85dae4e57290efb3dad03ada588d7a6cfe037fd2e1ae5d40bd61c6"),
    "grilla": (GRILLA, "b94b9eedeea87d08071366e2bd8a5b7cd9662ce6f9fd9d7bee42848d6c4c5f90"),
    "ca2_bundle_E2": (BUNDLES / "73cf4e4499eb2e3327a27e01f9e87e1fd6b14a160bee4718fc945636420ae48e.json",
                      "73cf4e4499eb2e3327a27e01f9e87e1fd6b14a160bee4718fc945636420ae48e"),
    "ca2_bundle_E1": (BUNDLES / "b2a90d7d89f12d4fd2b48a8af1b6e0fed5aca2cb46ee8d3a3db88cd742489151.json",
                      "b2a90d7d89f12d4fd2b48a8af1b6e0fed5aca2cb46ee8d3a3db88cd742489151"),
    "d6_tax_marg": (D6_TAX, "83cb6b5659ec484de356b6d945b37668dd32bbaa401e59d49275af6cb8bdef88"),
    "c0_inventario_rem116": (T / "paso4_raices_impacto_desde_rem116/audit/entrega.json", C0_INVENTARIO_SHA),
    "c0_run_py": (C0_SRC / "paper2b/run.py", "18abae7000d727c88dc7693db59c75a20ea79db7031b0c2e510d2b3af0058360"),
    "c0_contexto_s6": (C0 / "herramientas/b/contexto_s6.py", "618463864db1268678bdfd2d018aded56358411cda80f103dafc7cf1a648e107"),
    "c0_cobertura": (C0_SRC / "paper2b/cobertura.py", COBERTURA_SHA),
    "nacional_instalacion": (R / "herramientas/b/nacional.py", "8b12df28cf317ed2d9f93ce48f1fa236e3c65edbc78c4a1df82490415828422b"),
}
BUNDLE_POR_PREG = {"PREG-COL-E2-2023": "ca2_bundle_E2", "PREG-COMPARACION-E1": "ca2_bundle_E1"}
CONJUNTOS_COV = ("CMP-E1.macro.ABL-COV", "COL-E2-2023.2023p.macro.ABL-COV", "COL-E2-2023.2024p.macro.ABL-COV")
STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
MACRO = ("eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion")
PUENTE = ("eta_w", "pi_iva", "pi_otros_productos", "pi_produccion")
PI_KEYS = ("pi_iva", "pi_otros_productos", "pi_produccion")
SHARE_KEYS = ("s_L_bar", "s_bar_iva", "s_bar_otros_productos", "s_bar_produccion")
SHARE_OF_PI = {"pi_iva": "s_bar_iva", "pi_otros_productos": "s_bar_otros_productos", "pi_produccion": "s_bar_produccion"}
COMPONENT_SHARE = {"iva": "s_bar_iva", "otros_productos": "s_bar_otros_productos", "produccion": "s_bar_produccion"}
COTAS = ("addback_completo", "sin_addback")
CAPA, PAIS = "guardrail_deuda", "COL"
GRUPOS = ("K1", "K2", "K3", "K4", "K5", "K6")
EPS = Fraction(1, 100)
TAREA_TRABAJO, TAREA_VALIDACION = "B2-TRABAJO", "B2-VALIDACION"
KIND_MAN = "manifiesto-b2-doce-cov-rem167"
KIND_EVIDENCIA = "evidencia-b2-rem167"
INDICE = "PAQUETE_B2.json"
RECUENTOS_ESPERADOS = {"afirmaciones": 12, "grupos": 6, "contextos_antes_dedup": 4608, "antes_dedup_por_kind": {"E2_primary": 192,
                       "E1_historical_anchor": 864, "E1_primary": 96}, "contextos_efectivos": 1920, "entradas_puente": 480,
                       "entradas_Q": 60, "entradas_nacionales": 10, "vertices_macro": 32, "vertices_puente": 16, "nodos_eta_H": 3,
                       "celdas_por_cota": 30, "solicitudes_C2_nuevas": 0}
LIMITES_POR_GRUPO = {"K1": 192, "K2": 192, "K3": 864, "K4": 864, "K5": 96, "K6": 96}


class B2Error(RuntimeError):
    pass


def leer(nombre):
    p, h = FUENTES[nombre]
    b = Path(p).read_bytes()
    if H(b) != h:
        raise B2Error("FUENTE_NO_AUTENTICA:%s:%s" % (nombre, H(b)[:16]))
    return b, h


def jsonl(b):
    return [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]


def fs(q):
    """Fracción exacta como texto canónico n/d (n entero si d = 1)."""
    q = Fraction(q)
    return str(q.numerator) if q.denominator == 1 else "%d/%d" % (q.numerator, q.denominator)


# ------------------------------------------------------------------------------------------------ redondeo dirigido (Fraction → binary64)
def binario_afuera(x, lado):
    """'lo' → mayor binary64 <= x; 'hi' → menor binary64 >= x (x decimal en texto o Fraction). Un valor representable queda igual."""
    q = Fraction(x)
    f = float(q)
    if lado == "lo" and Fraction(f) > q:
        f = math.nextafter(f, -math.inf)
    if lado == "hi" and Fraction(f) < q:
        f = math.nextafter(f, math.inf)
    assert (Fraction(f) <= q) if lado == "lo" else (Fraction(f) >= q)
    return f


def iguales_bits(a, b):
    return isinstance(a, float) and isinstance(b, float) and float.hex(a) == float.hex(b)


# ------------------------------------------------------------------------------------------------ q exterior sobre la raíz binaria
def q_exterior(rb):
    """rb = {p: [lo, hi]} binario. q = kappa(a-1)/(a-rho) es creciente en kappa ((a-1)/(a-rho) > 0), en a (dq/da = kappa(1-rho)/(a-rho)^2
    >= 0 con rho <= 1) y en rho (dq/drho = kappa(a-1)/(a-rho)^2 > 0) sobre la caja con a.lo > 1, a.lo > rho.hi, rho.lo > 0, kappa.lo > 0:
    q.lo = q(kappa.lo, a.lo, rho.lo) y q.hi = q(kappa.hi, a.hi, rho.hi), EXACTOS sobre los extremos binarios y redondeados hacia afuera."""
    a, rho, k = ((Fraction(rb[p][0]), Fraction(rb[p][1])) for p in ("a", "rho", "kappa_tilde"))
    prem = {"a_lo_mayor_1": a[0] > 1, "rho_lo_positivo": rho[0] > 0, "rho_hi_le_1": rho[1] <= 1, "a_lo_mayor_rho_hi": a[0] > rho[1],
            "kappa_lo_positivo": k[0] > 0}
    if not all(prem.values()):
        raise B2Error("PREMISAS_DE_Q_NO_SE_CUMPLEN:%s" % sorted(x for x, v in prem.items() if not v))
    qlo = k[0] * (a[0] - 1) / (a[0] - rho[0])
    qhi = k[1] * (a[1] - 1) / (a[1] - rho[1])
    if not (0 < qlo <= qhi < 1):
        raise B2Error("RANGO_DE_Q_FUERA_DE_(0,1)")
    lo, hi = binario_afuera(qlo, "lo"), binario_afuera(qhi, "hi")
    return {"lo": lo, "hi": hi, "lo_hex": float.hex(lo), "hi_hex": float.hex(hi), "lo_exacto": fs(qlo), "hi_exacto": fs(qhi),
            "premisas": prem, "uno_menos_q_hi_positivo": Fraction(hi) < 1,
            "metodo": "monotonia en kappa, a y rho; extremos exactos sobre la raiz BINARIA; redondeo hacia afuera"}


# ------------------------------------------------------------------------------------------------ fuente B1 aceptada (libro 19 + evidencia)
def fuente_b1(datos=None):
    """U_C2 ACEPTADO por el libro 19 (review_20261108_rem167_B1_aceptada.json) y COHERENTE con la evidencia original de rem166 (estado,
    evidencia, validación y lectura con las huellas que fija el propio libro). datos = {nombre: bytes} solo en ensayos de manipulación."""
    def b(n):
        if datos is not None and n in datos:
            return datos[n], H(datos[n])
        return leer(n)
    lb, lh = b("libro_B1_rem167")
    if lh != FUENTES["libro_B1_rem167"][1]:
        raise B2Error("LIBRO_B1_NO_AUTENTICO")
    lib = json.loads(lb)
    need = {"kind": "B1-doce-COV-aceptada-rem167", "accepted": True, "execution_accepted": True, "bound_accepted": True, "reading_accepted": True,
            "inventory_sha256": FUENTES["x166_inventario"][1], "package_index_sha256": FUENTES["b1_indice"][1],
            "manifest_sha256": FUENTES["b1_manifiesto"][1], "producer_installation": C0_IDENTIDAD, "B2_executed": False, "B2_authorized": False}
    for k, v in need.items():
        if lib.get(k) != v:
            raise B2Error("LIBRO_B1_CAMPO_DISTINTO:" + k)
    U = lib.get("U_C2")
    if not (isinstance(U, float) and math.isfinite(U) and lib.get("U_C2_hex") == float.hex(U) and Fraction(lib.get("U_C2_exact")) == Fraction(U)):
        raise B2Error("U_C2_DEL_LIBRO_INCOHERENTE")
    prods = {Path(k).name: v for k, v in (lib.get("products") or {}).items()}
    for n, f in (("estado_b1.json", "b1_estado"), ("EVIDENCIA_B1.json", "b1_evidencia"), ("VALIDACION_B1.json", "b1_validacion"),
                 ("LECTURA_B1.json", "b1_lectura")):
        if prods.get(n) != FUENTES[f][1]:
            raise B2Error("PRODUCTO_B1_NO_FIJADO_POR_EL_LIBRO:" + n)
    eb, eh = b("b1_evidencia")
    vb, vh = b("b1_validacion")
    rb_, rh = b("b1_lectura")
    sb, sh = b("b1_estado")
    for h_, f in ((eh, "b1_evidencia"), (vh, "b1_validacion"), (rh, "b1_lectura"), (sh, "b1_estado")):
        if h_ != prods[Path(FUENTES[f][0]).name]:
            raise B2Error("PRODUCTO_B1_DISTINTO_DEL_LIBRO:" + f)
    ev, va, le, st = json.loads(eb), json.loads(vb), json.loads(rb_), json.loads(sb)
    hi = (ev.get("intervalo_normalizado") or {}).get("hi")
    if not (ev.get("estado") == "complete" and iguales_bits(ev.get("U_C2"), U) and iguales_bits(hi, U)):
        raise B2Error("EVIDENCIA_B1_NO_DA_EL_U_C2_DEL_LIBRO")
    if not (va.get("aceptada") is True and va.get("evidencia_sha256") == eh and iguales_bits((va.get("datos") or {}).get("U_C2"), U)
            and va.get("lectura_sha256") == rh):
        raise B2Error("VALIDACION_B1_INCOHERENTE")
    if not (iguales_bits((le.get("lectura") or {}).get("U_C2"), U) and le.get("evidencia_sha256") == eh):
        raise B2Error("LECTURA_B1_INCOHERENTE")
    if not (st.get("estado_final") == "completo" and st.get("evidencia_sha256") == eh and st.get("validacion_sha256") == vh):
        raise B2Error("ESTADO_B1_INCOHERENTE")
    lec = {g["grupo"]: g for g in lib.get("group_reading") or []}
    claims = {c["afirmacion"]: c["grupo"] for c in lib.get("claims") or []}
    if sorted(lec) != list(GRUPOS) or len(claims) != 12 or any(c.get("lectura") != "candidato_B2" for c in lib["claims"]):
        raise B2Error("LECTURA_B1_DEL_LIBRO_NO_SON_SEIS_CANDIDATOS")
    return {"U_C2": U, "U_C2_hex": float.hex(U), "U_C2_exacto": fs(Fraction(U)), "libro_sha256": lh, "evidencia_sha256": eh,
            "validacion_sha256": vh, "lectura_sha256": rh, "estado_sha256": sh, "acto_B1": lib.get("native_act"),
            "alcance_B1_sha256": lib.get("scope_sha256"), "afirmacion_grupo": dict(sorted(claims.items())),
            "naturaleza": "cota superior certificada sobre la raiz fija; NO es maximo puntual, argmax ni prueba de alcanzabilidad"}


# ------------------------------------------------------------------------------------------------ manifiesto desde fuentes
def _lineas(nombre, esperadas):
    b, h = leer(nombre)
    ls = b.decode("utf-8").splitlines()
    ev = {}
    for n, txt in esperadas.items():
        if ls[n - 1].strip() != txt:
            raise B2Error("LINEA_DE_FUENTE_DISTINTA:%s:%d" % (nombre, n))
        ev[str(n)] = txt
    return {"fuente": nombre, "sha256": h, "lineas": ev}


def _fila_grilla(r):
    return {k: r[k] for k in ("country_id", "policy_id", "policy_variant_id", "gmi_version", "regime_id", "requirement_basis", "xi",
                              "cost_gross_gdp", "F_admin", "F_trans", "F_leak", "F_fix", "F_fix_perp", "s_PB", "Q")}


def id_celda(r):
    return "EXT:%s:%s:%s:%s:%s" % (r["country_id"], r["policy_variant_id"], r["regime_id"], r["requirement_basis"], r["xi"])


def capa_de(basis, xi):
    x = Fraction(xi)
    if x == 0 and basis == "debt_consistent":
        return "guardrail_deuda"
    if x == 0 and basis == "baseline":
        return "nucleo_contable"
    return "otra"


def vertices(ejes):
    """32 vértices macro (eta_w, gain_share, pi_*) en el orden de product sobre MACRO, con sus índices de puente (16, sin gain)."""
    vs, vp = [], []
    for combo in product(*[ejes[p] for p in MACRO]):
        v = dict(zip(MACRO, combo))
        vs.append(v)
        k = {p: v[p] for p in PUENTE}
        if k not in vp:
            vp.append(k)
    idx = [vp.index({p: v[p] for p in PUENTE}) for v in vs]
    return vs, vp, idx


def construir_manifiesto():
    """Manifiesto B2 REAL reconstruido desde las fuentes fijadas. Lanza B2Error si una fuente no es auténtica o no concuerda."""
    fuentes = {k: {"ruta": str(p), "sha256": h} for k, (p, h) in sorted(FUENTES.items())}
    for k in FUENTES:
        leer(k)
    b1 = fuente_b1()
    m1 = json.loads(leer("b1_manifiesto")[0])
    lib = json.loads(leer("libro_B1_rem167")[0])
    rb = {p: [m1["raiz"]["binario"][p]["lo"], m1["raiz"]["binario"][p]["hi"]] for p in STRUCT}
    if any(not (iguales_bits(rb[p][0], lib["domain"]["root_binary"][p][0]) and iguales_bits(rb[p][1], lib["domain"]["root_binary"][p][1]))
           for p in STRUCT):
        raise B2Error("RAIZ_BINARIA_B1_DISTINTA_DEL_LIBRO")
    q = q_exterior(rb)
    ctx = json.loads(leer("x162_contexto_col")[0])
    if ctx.get("kind") != "contexto-col-por-grupo-rem162" or ctx.get("s6_construido") is not False \
            or any(v for v in ctx["bloqueadores"]["llamadas_cientificas"].values()):
        raise B2Error("CENSO_REM162_NO_ES_EL_ACEPTADO")
    # ejes macro y eta_H: iguales en todos los conjuntos del censo y en las filas D7 de los tres conjuntos ABL-COV
    ejes, eta_h, variantes = None, None, None
    entradas, afirmaciones = {}, []
    for a in ctx["por_afirmacion"]:
        conj = []
        for cj in a["conjuntos"]:
            e = {p: [cj["ejes"][p]["lower"], cj["ejes"][p]["upper"]] for p in MACRO}
            vv = {p: cj["ejes"][p]["variant_id"] for p in MACRO + ("eta_H",)}
            h = [repr(float(x)) for x in cj["eta_H_nodos"]]
            if ejes is None:
                ejes, eta_h, variantes = e, h, vv
            if e != ejes or h != eta_h or vv != variantes or cj["vertices_macro"] != 32 or cj["vertices_macro_en_bloque"] != 32:
                raise B2Error("EJES_MACRO_DISTINTOS_ENTRE_CONJUNTOS:" + cj["conjunto_COV"])
            if (cj.get("celdas_capa") or {}).get("capa") != CAPA or len(cj["celdas_capa"]["ids"]) != 30:
                raise B2Error("CELDAS_DE_CAPA_NO_SON_30:" + cj["conjunto_COV"])
            claves = []
            for s in cj["estados"]:
                k = s["clave_entrada_efectiva"]
                uso = {x: s[x] for x in ("preregistration_id", "edicion", "d6_edicion", "anchor_year", "d2_vector_id", "d6_vector_id",
                                         "d2_vector_sha256", "d6_vector_sha256", "d2_snapshot_sha256", "bundle_sha256", "d6_component_sign_status",
                                         "national_state_sha256_ligados_T7")}
                if s["bundle_sha256"] != FUENTES[BUNDLE_POR_PREG[s["preregistration_id"]]][1]:
                    raise B2Error("BUNDLE_DEL_ESTADO_NO_FIJADO:" + k)
                entradas.setdefault(k, {"usos": []})
                if uso not in entradas[k]["usos"]:
                    entradas[k]["usos"].append(uso)
                claves.append(k)
            conj.append({"conjunto_COV": cj["conjunto_COV"], "edicion": cj["edicion"], "claves": claves, "celdas": sorted(cj["celdas_capa"]["ids"]),
                         "anios_estados": sorted(s["anchor_year"] for s in cj["estados"]), "descartados_por_anio": list(cj["estados_descartados_por_anio"])})
        afirmaciones.append({"afirmacion": a["afirmacion"], "grupo": a["grupo_X"], "diseno": a["diseno"], "cota": a["cota"], "capa": a["capa"],
                             "pais": a["pais"], "kind": a["kind"], "pid": a["pid"], "anios": list(a["anios"]), "bloque": a["bloque"], "j": a["j"],
                             "ediciones": list(a.get("ediciones") or []), "conjuntos": conj})
    afirmaciones.sort(key=lambda x: x["afirmacion"])
    sup = {}
    for r in csv.DictReader(io.StringIO(leer("d7_support_set")[0].decode("utf-8"))):
        if r["support_set_id"] in CONJUNTOS_COV and r["parameter_id"] in MACRO + ("eta_H",) and r["variant_id"] == variantes[r["parameter_id"]]:
            sup.setdefault((r["support_set_id"], r["parameter_id"]), []).append(r)
    for cj in CONJUNTOS_COV:
        for p in MACRO:
            rs = sup.get((cj, p), [])
            if len(rs) != 1 or [rs[0]["lower"], rs[0]["upper"]] != ejes[p] or rs[0]["lower_closed"] != "true" or rs[0]["upper_closed"] != "true":
                raise B2Error("EJE_MACRO_D7_DISTINTO:%s:%s" % (cj, p))
        rs = sup.get((cj, "eta_H"), [])
        if len(rs) != 1 or [repr(float(x)) for x in json.loads(rs[0]["level0_nodes"])] != eta_h:
            raise B2Error("NODOS_ETA_H_D7_DISTINTOS:" + cj)
    vs, vp, idx = vertices(ejes)
    # celdas: las 30 de la capa guardrail_deuda de COL en la grilla, por identidad y huella de fila (Q no se calcula aquí)
    filas = {}
    for r in csv.DictReader(io.StringIO(leer("grilla")[0].decode("utf-8"), newline="")):
        if r["country_id"] == PAIS and capa_de(r["requirement_basis"], r["xi"]) == CAPA:
            filas[id_celda(r)] = H(canon(_fila_grilla(r)))
    ids = sorted({c for a in afirmaciones for cj in a["conjuntos"] for c in cj["celdas"]})
    if sorted(filas) != ids or len(ids) != 30:
        raise B2Error("CELDAS_DEL_CENSO_DISTINTAS_DE_LA_GRILLA")
    grupos = []
    for g in GRUPOS:
        afs = [a for a in afirmaciones if a["grupo"] == g]
        cotas = {a["cota"] for a in afs}
        claves = sorted({k for a in afs for cj in a["conjuntos"] for k in cj["claves"]})
        if len(afs) != 2 or len(cotas) != 1 or sorted(a["diseno"] for a in afs) != ["G", "N"]:
            raise B2Error("GRUPO_NO_UNIVOCO:" + g)
        grupos.append({"grupo": g, "afirmaciones": sorted(a["afirmacion"] for a in afs), "cota": cotas.pop(), "claves": claves,
                       "contextos_efectivos": len(claves) * 32 * len(eta_h)})
    dme = [_lineas("c0_contexto_s6", {127: "crosswalk_sha256=ev[\"EV.CROSSWALK\"][\"payload_sha256\"], dme_gai=0.0, set_index=set_index,"}),
           _lineas("c0_run_py", {163: "dme_gai: float = 0.0", 1211: "min(ks) + self.inp.dme_gai))"})]
    man = {
        "kind": KIND_MAN, "modo": "produccion",
        "naturaleza": "MANIFIESTO REAL DOCUMENTAL del paquete B2 (rem167): fija la FUTURA evaluacion B2; no es un alcance ni una autorizacion",
        "operacion": "B2",
        "b1": b1,
        "regla": {"eps": "1/100", "G_hi": "U_C2 - L_K1 (racionales exactos)", "certifica": "G_hi <= -1/100 (borde incluido, como cobertura.classify)",
                  "no_certifica": "G_hi > -1/100: la afirmacion sigue desconocida", "pendiente": "una premisa fallida o un contexto sin cota",
                  "prohibido": "usar K1_testigo como L_K1"},
        "afirmaciones": afirmaciones, "grupos": grupos,
        "entradas_nacionales": dict(sorted(entradas.items())),
        "macro": {"ejes": ejes, "eta_H": eta_h, "vertices": vs, "vertices_puente": vp, "indice_puente": idx,
                  "orden": "itertools.product sobre %s; puente = vertice sin gain_share" % (list(MACRO),)},
        "celdas": {"capa": CAPA, "pais": PAIS, "ids": ids, "filas_sha256": {i: filas[i] for i in ids}, "cotas": list(COTAS)},
        "dme_gai": {"valor": "0.0", "por_cota": {c: "0.0" for c in COTAS}, "evidencia": dme,
                    "regla": "n_min = min_celda Q(cota) + DME_gAI (run.claim_contexts:1211); DME_gAI es el literal de ContextoS6 (contexto_s6.py:127), "
                             "autenticado por bytes; el codigo lo trata como dato y no supone su valor"},
        "q": q, "raiz_binaria": rb,
        "forma": {"k1": "K1 = n_min / ((s_Pi / (1 - q)) * gain) = n_min (1 - q) / (s_Pi gain), mismo orden que cobertura.g_enclosure:93-96",
                  "s_Pi": "macro.bridge (exacto): 1 - s_L_bar theta_W(eta_w, eta_H) - sum_j pi_j s_bar_j",
                  "n_min": "intervalo que contiene min Q exacto (literales) + DME y min GridCell.Q (float C0) + DME",
                  "gain": "gain_share decimal exacto, encerrado hacia afuera", "reduccion": "s_Pi afin y gain lineal: s_Pi*gain multilineal; con P7 "
                  "(s_Pi > 0 en los 16 vertices de puente por estado y nodo) s_Pi*gain > 0 en la caja y sus extremos estan en los 32 vertices; "
                  "K1 es monotono en s_Pi*gain y en q para cualquier signo de n_min(1-q): inf K1 >= min de k1.lo en los vertices"},
        "premisas": {"P1_a_mayor_1": q["premisas"]["a_lo_mayor_1"], "P2_rho_en_0_1": q["premisas"]["rho_lo_positivo"] and q["premisas"]["rho_hi_le_1"],
                     "P3_kappa_binario": "kappa.hi binario = 0.2 > 1/5: q.hi = %s" % q["hi_exacto"], "P4_a_mayor_rho": q["premisas"]["a_lo_mayor_rho_hi"],
                     "P5_eta_H_mayor_menos_1": all(Fraction(x) > -1 for x in eta_h), "P6_gain_positivo": Fraction(ejes["gain_share"][0]) > 0,
                     "P7_s_Pi_positivo": "PENDIENTE: obligatorio en el trabajo por estado y nodo; un fallo deja pendiente el estado",
                     "P8_s_T_no_negativo": "comprobado en el trabajo (documental: D6 positive_admissible)",
                     "P9_signo_n_min": "no autenticado: forma intervalar, sin factor 4/5", "P10_afinidad_bridge": "macro.bridge exacto y afin"},
        "recuentos": dict(RECUENTOS_ESPERADOS),
        "c0": {"ruta": str(C0), "identidad": C0_IDENTIDAD, "inventario_rem116_sha256": C0_INVENTARIO_SHA, "cierre": dict(CIERRE_C0),
               "orden_carga": list(ORDEN_CARGA), "lector_aprobacion_sha256": AA_SHA,
               "fuera_del_cierre": "model, modelos, c2_normalizado, encierros_modelo, supremum, frontier, cobertura, run, claims, nacional, S6"},
        "proveedor_nacional": {"produccion": "literales de los bundles CA2 y D6 tax_shares_marg fijados; clave_entrada_efectiva recomputada "
                                             "(enumerar_contextos_rem162.py:220-228) y shares exactos como nacional.conditional_states "
                                             "(s_L_bar = COE/PIB; s_bar_j = share_exact_json)", "claim_contexts": "NO se llama"},
        "prohibido": ["C2 nuevo", "modelo", "supremos", "claim_contexts", "S6", "cobertura M4/M5", "busqueda de testigos", "subdivision",
                      "K1_testigo como L_K1", "D-EXP8", "N3"],
        "fuentes": fuentes,
    }
    return man


_CONSTRUIDO = {}


def diferencias(a, b, ruta="", n=12):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(ruta + "/" + str(k))
            else:
                out += diferencias(a[k], b[k], ruta + "/" + str(k), n)
            if len(out) >= n:
                break
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diferencias(x, y, "%s[%d]" % (ruta, i), n)
            if len(out) >= n:
                break
    elif a != b or type(a) is not type(b):
        out.append(ruta or "/")
    return out[:n]


def es_fixture(man):
    k = str(man.get("kind", ""))
    return k.endswith("-SINTETICO") or "FIXTURE" in k


def validar_manifiesto(man):
    """Lista de fallos (vacía = conforme). Producción: igualdad canónica EXACTA con construir_manifiesto(). Sintético: kind …-SINTETICO, modo
    sintetico, doble declarado y el MISMO contenido documental que el real. Puerta (kind con FIXTURE, modo producción): solo estructura."""
    f = []
    k = str(man.get("kind", ""))
    sint = k.endswith("-SINTETICO")
    if (man.get("modo") == "sintetico") != sint or man.get("modo") not in ("produccion", "sintetico"):
        return ["MANIFIESTO_MEZCLA_REAL_SINTETICO"]
    try:
        if "doc" not in _CONSTRUIDO:
            _CONSTRUIDO["doc"] = construir_manifiesto()
        exp = _CONSTRUIDO["doc"]
    except (B2Error, OSError, KeyError, ValueError, TypeError, AssertionError) as ex:
        return ["FUENTES_DEL_MANIFIESTO_NO_AUTENTICAS: %s" % str(ex)[:160]]
    if not sint and "FIXTURE" not in k:
        if canon(man) != canon(exp):
            f.append(("PROCEDENCIA_DISTINTA_DE_LAS_FUENTES", diferencias(man, exp)))
        return f
    for x, v in exp.items():
        if x not in ("kind", "modo", "naturaleza") and canon(man.get(x)) != canon(v):
            f.append(("CONTENIDO_DISTINTO_DEL_REAL", x))
    extra = sorted(set(man) - set(exp) - {"doble"})
    if extra:
        f.append(("CAMPO_INESPERADO", extra))
    if sint:
        d = man.get("doble") or {}
        if not (k == KIND_MAN + "-SINTETICO" and isinstance(d.get("sha256"), str) and d.get("ruta") == "pruebas/doble_b2.py"
                and isinstance(d.get("comportamiento"), str)):
            f.append("DOBLE_NO_DECLARADO")
    elif "doble" in man:
        f.append("DOBLE_EN_MANIFIESTO_DE_PUERTA")
    return f


# ------------------------------------------------------------------------------------------------ plan y autoridad de cobertura
def plan(man):
    """Entradas del trabajo derivadas del manifiesto: contextos por grupo (cota, clave, eta_H, vértice 0..31), puentes (clave, eta_H, 0..15),
    celdas (cota, id). La unión deduplica por clave_entrada_efectiva (el diseño G/N no entra en la clave)."""
    eh, nv, idx = man["macro"]["eta_H"], len(man["macro"]["vertices"]), man["macro"]["indice_puente"]
    por = {g["grupo"]: {(g["cota"], k, h, v) for k in g["claves"] for h in eh for v in range(nv)} for g in man["grupos"]}
    union = set().union(*por.values())
    puentes = {(k, h, idx[v]) for (_c, k, h, v) in union}
    celdas = {(c, i) for c in sorted({g["cota"] for g in man["grupos"]}) for i in man["celdas"]["ids"]}
    return {"por_grupo": por, "union": union, "puentes": puentes, "celdas": celdas}


def cobertura_esperada(ctx=None, mapa=None):
    """Autoridad INDEPENDIENTE del manifiesto: reconstruye desde el censo CRUDO rem162 (claims.derive: ediciones y años; nacional.
    conditional_states: un estado por año ancla con D6 de la edición; run.claim_contexts: vértices x nodos x estados con año en cl.years)."""
    ctx = ctx if ctx is not None else json.loads(leer("x162_contexto_col")[0])
    mapa = mapa if mapa is not None else jsonl(leer("x162_mapa_derivado")[0])
    por_g, antes, por_kind = {}, {}, {}
    for a in ctx["por_afirmacion"]:
        n = 0
        for cj in a["conjuntos"]:
            todos = [s["anchor_year"] for s in cj["estados"]] + list(cj["estados_descartados_por_anio"])
            dentro = [s for s in cj["estados"] if s["anchor_year"] in a["anios"]]
            if len(dentro) != len(cj["estados"]) or any(y in a["anios"] for y in cj["estados_descartados_por_anio"]) or len(set(todos)) != len(todos):
                raise B2Error("FILTRO_DE_ANIOS_INCOHERENTE:" + cj["conjunto_COV"])
            nodos = [repr(float(x)) for x in cj["eta_H_nodos"]]
            n += len(dentro) * cj["vertices_macro_en_bloque"] * len(nodos)
            for s in dentro:
                for h in nodos:
                    for v in range(cj["vertices_macro_en_bloque"]):
                        por_g.setdefault(a["grupo_X"], set()).add((a["cota"], s["clave_entrada_efectiva"], h, v))
        antes[a["afirmacion"]] = n
        por_kind.setdefault(("E2" if "E2" in a["pid"] else "E1") + "_" + a["kind"], set()).add(n)
    incl = {}
    for g1 in sorted(por_g):
        for g2 in sorted(por_g):
            if g1 != g2 and por_g[g1] <= {(c, k, h, v) for (c, k, h, v) in por_g[g2]}:
                incl.setdefault(g1, []).append(g2)
    # 17 filas «celda_estado_nacional_no_ligado» de rem161 (mapa derivado rem162): pertenencia por estado ligado T7 y años de la afirmación
    lig = ctx["ligadura_estados_T7"]
    anios = {a["afirmacion"]: a["anios"] for a in ctx["por_afirmacion"]}
    pid = {a["afirmacion"]: a["pid"] for a in ctx["por_afirmacion"]}
    filas = [r for r in mapa if r.get("tipo") == "celda_estado_nacional_no_ligado"]
    pert, fuera = 0, 0
    detalle = []
    for r in filas:
        (preg, anio, _ed, _d2, _d6), = [tuple(x) for x in lig[r["estado_nacional"]]]
        for af in r["afirmaciones"]:
            ok = preg == pid[af] and anio in anios[af]
            pert, fuera = pert + ok, fuera + (not ok)
            detalle.append({"fila": r["id"], "afirmacion": af, "estado": r["estado_nacional"][:16], "anio": anio, "pertenece": ok})
    return {"por_grupo": por_g, "antes_dedup": antes, "por_kind": {k: sorted(v) for k, v in por_kind.items()}, "inclusiones": incl,
            "filas_no_ligadas": {"n": len(filas), "pertenecen": pert, "fuera": fuera, "detalle": detalle},
            "union": set().union(*por_g.values())}


def validar_cobertura(man, esperado=None):
    """Igualdad EXACTA de conjuntos manifiesto ↔ autoridad, recuentos, inclusiones, 2024p y 9/8 filas. Lista de fallos (vacía = conforme)."""
    f = []
    try:
        e = esperado or cobertura_esperada()
        p = plan(man)
    except (B2Error, KeyError, ValueError, TypeError) as ex:
        return ["COBERTURA_NO_RECONSTRUIBLE: %s" % str(ex)[:160]]
    if sorted(p["por_grupo"]) != list(GRUPOS) or sorted(e["por_grupo"]) != list(GRUPOS):
        f.append("GRUPOS_DISTINTOS")
    for g in GRUPOS:
        if p["por_grupo"].get(g) != e["por_grupo"].get(g):
            f.append(("CONTEXTOS_DE_GRUPO_DISTINTOS", g, len(p["por_grupo"].get(g) or ()), len(e["por_grupo"].get(g) or ())))
        if len(p["por_grupo"].get(g) or ()) != LIMITES_POR_GRUPO[g]:
            f.append(("RECUENTO_DE_GRUPO_DISTINTO", g))
    if p["union"] != e["union"] or len(p["union"]) != RECUENTOS_ESPERADOS["contextos_efectivos"]:
        f.append(("UNION_DISTINTA", len(p["union"])))
    if sum(e["antes_dedup"].values()) != RECUENTOS_ESPERADOS["contextos_antes_dedup"] or len(e["antes_dedup"]) != 12:
        f.append(("ANTES_DEDUP_DISTINTO", sum(e["antes_dedup"].values())))
    if e["por_kind"] != {k: [v] for k, v in RECUENTOS_ESPERADOS["antes_dedup_por_kind"].items()}:
        f.append(("ANTES_DEDUP_POR_KIND_DISTINTO", e["por_kind"]))
    if len(p["puentes"]) != RECUENTOS_ESPERADOS["entradas_puente"] or len(p["celdas"]) != RECUENTOS_ESPERADOS["entradas_Q"]:
        f.append(("ENTRADAS_PUENTE_O_Q_DISTINTAS", len(p["puentes"]), len(p["celdas"])))
    if len({k for (_c, k, _h, _v) in p["union"]}) != RECUENTOS_ESPERADOS["entradas_nacionales"] or len(man["entradas_nacionales"]) != 10:
        f.append("ENTRADAS_NACIONALES_NO_SON_DIEZ")
    if e["inclusiones"] != {"K5": ["K1", "K3"], "K6": ["K2", "K4"]}:
        f.append(("INCLUSIONES_DISTINTAS", e["inclusiones"]))
    for sub, sups in (("K5", ("K1", "K3")), ("K6", ("K2", "K4"))):
        for s in sups:
            if not p["por_grupo"].get(sub, set()) <= p["por_grupo"].get(s, set()):
                f.append(("INCLUSION_ROTA_EN_EL_MANIFIESTO", sub, s))
    e24 = {k for k, v in man["entradas_nacionales"].items() if any(u["edicion"] == "2024p" for u in v["usos"])}
    for g in ("K1", "K2"):
        if not e24 or not e24 <= {k for (_c, k, _h, _v) in p["por_grupo"].get(g, set())}:
            f.append(("2024P_FUERA_DEL_GRUPO", g))
    fl = e["filas_no_ligadas"]
    if (fl["n"], fl["pertenecen"], fl["fuera"]) != (17, 9, 8):
        f.append(("FILAS_NO_LIGADAS_DISTINTAS_DE_9_Y_8", fl["n"], fl["pertenecen"], fl["fuera"]))
    if not all(d["anio"] == 2023 for d in fl["detalle"] if d["pertenece"]) or not all(d["anio"] == 2020 for d in fl["detalle"] if not d["pertenece"]):
        f.append("FILAS_NO_LIGADAS_CON_ANIO_INESPERADO")
    return f


# ------------------------------------------------------------------------------------------------ cierre C0 con identidad de módulos
def cargar_cierre_c0(src=None, cierre=None, orden=None):
    """Carga paper2b desde los bytes AUTENTICADOS del cierre (src/paper2b), sin sys.path ni __path__. Devuelve (modulos, identidad)."""
    src = Path(src or C0_SRC) / "paper2b"
    cierre = dict(cierre or CIERRE_C0)
    orden = tuple(orden or ORDEN_CARGA)
    pre = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if pre:
        raise B2Error("MODULO_PRECARGADO:%s" % pre[:4])
    mp = [getattr(x, "__name__", type(x).__name__) for x in sys.meta_path]
    if not set(mp) <= {"BuiltinImporter", "FrozenImporter", "PathFinder"}:
        raise B2Error("META_PATH_AJENO:%s" % mp)
    if sorted(cierre) != sorted([n + ".py" for n in orden] + ["__init__.py"]):
        raise B2Error("CIERRE_INCOMPLETO")
    datos = {}
    for n, h in cierre.items():
        b = (src / n).read_bytes()
        if H(b) != h:
            raise B2Error("CIERRE_C0_DISTINTO:%s" % n)
        datos[n] = b
    creados = {}

    def nuevo(nombre, archivo, paquete):
        m = types.ModuleType(nombre)
        m.__file__ = str(src / archivo)
        m.__package__ = "paper2b"
        m.__spec__ = importlib.machinery.ModuleSpec(nombre, None, origin=str(src / archivo), is_package=paquete)
        if paquete:
            m.__path__ = []
            m.__spec__.submodule_search_locations = []
        sys.modules[nombre] = m
        creados[nombre] = m
        exec(compile(datos[archivo], str(src / archivo), "exec", dont_inherit=True), m.__dict__)
        return m
    try:
        pkg = nuevo("paper2b", "__init__.py", True)
        for n in orden:
            setattr(pkg, n, nuevo("paper2b." + n, n + ".py", False))
    except Exception:
        for k in creados:
            sys.modules.pop(k, None)
        raise
    actuales = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if actuales != sorted(creados) or any(sys.modules[k] is not v for k, v in creados.items()):
        raise B2Error("IDENTIDAD_DE_MODULOS_DISTINTA")
    ident = {k: {"archivo": "src/paper2b/" + Path(v.__file__).name, "sha256": cierre[Path(v.__file__).name], "registrado_es_el_cargado": True}
             for k, v in sorted(creados.items())}
    return {k.split(".")[-1] if "." in k else k: v for k, v in creados.items()}, {"modulos": ident, "meta_path": mp, "precargados": pre}


def comprobar_identidad(ident):
    f = []
    act = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if act != sorted(ident["modulos"]):
        f.append(("MODULOS_PAPER2B_DISTINTOS", act))
    for k, v in ident["modulos"].items():
        if sys.modules.get(k) is None or Path(sys.modules[k].__file__).name != Path(v["archivo"]).name:
            f.append(("MODULO_SUSTITUIDO", k))
    return f


class Bloqueo(RuntimeError):
    pass


def espias(mods, permitir=True):
    """Contadores de macro.bridge y GridCell.Q (pasan sin cambiar argumentos ni resultado) y bloqueadores de toda otra entrada científica
    del cierre (external.K1, external.identities, macro.shares_from_terms…). permitir=False bloquea también bridge y Q (preflight/validación)."""
    reg = {"bridge": 0, "GridCell.Q": 0, "bloqueadas": {}}
    MC, X = mods["macro"], mods["external"]

    def bloq(nombre):
        def f(*a, **k):
            reg["bloqueadas"][nombre] = reg["bloqueadas"].get(nombre, 0) + 1
            raise Bloqueo("ENTRADA_CIENTIFICA_BLOQUEADA:" + nombre)
        return f
    for n in ("K1", "identities"):
        setattr(X, n, bloq("external." + n))
    for n in [x for x in vars(MC) if not x.startswith("_")]:
        v = getattr(MC, n)
        if callable(v) and not isinstance(v, type) and getattr(v, "__module__", "") == MC.__name__ and n not in ("bridge", "theta_W", "q_pot", "F"):
            setattr(MC, n, bloq("macro." + n))
    b0, q0 = MC.bridge, X.GridCell.Q
    if not permitir:
        MC.bridge = bloq("macro.bridge")
        X.GridCell.Q = bloq("GridCell.Q")
        return reg

    def bridge(shares, omega):
        reg["bridge"] += 1
        return b0(shares, omega)

    def q(self, bound):
        reg["GridCell.Q"] += 1
        return q0(self, bound)
    MC.bridge = bridge
    X.GridCell.Q = q
    return reg


# ------------------------------------------------------------------------------------------------ insumos: literales, shares y Q
def clave_de(lit):
    """clave_entrada_efectiva de rem162 (enumerar_contextos_rem162.py:220-228): hash de los literales guardados (json.dumps sort_keys)."""
    return H(json.dumps({"d2_COE": lit["d2_COE"], "d2_PIB": lit["d2_PIB"], "d6_shares_exact_json": lit["d6_shares_exact_json"]},
                        sort_keys=True).encode("utf-8"))


def exact_fraction(text):
    obj = json.loads(text)
    if not (isinstance(obj, dict) and set(obj) == {"numerator", "denominator"}):
        raise B2Error("D6_EXACT_SHARE_FORMAT")
    return Fraction(int(obj["numerator"]), int(obj["denominator"]))


def shares_de(lit):
    """Como nacional.conditional_states: s_L_bar = COE/PIB (Fraction de los literales) y s_bar_j = share_exact_json de D6."""
    sh = {COMPONENT_SHARE[k]: exact_fraction(v) for k, v in lit["d6_shares_exact_json"].items()}
    if sorted(sh) != sorted(SHARE_KEYS[1:]):
        raise B2Error("D6_COMPONENTES")
    pib = Fraction(lit["d2_PIB"])
    if pib == 0:
        raise B2Error("PIB_CERO")
    sh["s_L_bar"] = Fraction(lit["d2_COE"]) / pib
    return {k: sh[k] for k in SHARE_KEYS}


def s_pi_exacto(shares, omega):
    """Referencia INDEPENDIENTE de macro.bridge (validación): theta_W = (eta_w+eta_H)/(1+eta_H); s_T = sum pi_j s_bar_j; s_Pi = 1-s_L-s_T."""
    eh = Fraction(omega["eta_H"])
    tw = (Fraction(omega["eta_w"]) + eh) / (1 + eh)
    sT = sum(Fraction(omega[p]) * Fraction(shares[SHARE_OF_PI[p]]) for p in PI_KEYS)
    return 1 - Fraction(shares["s_L_bar"]) * tw - sT, sT


def q_exacto(fila, cota):
    """Q exacto desde los literales de la fila (misma fórmula que external.GridCell.Q, en racionales)."""
    dc = Fraction(fila["s_PB"]) if fila["requirement_basis"] == "debt_consistent" else Fraction(0)
    F = fila["F_fix_perp"] if cota == "sin_addback" else fila["F_fix"] if cota == "addback_completo" else None
    if F is None:
        raise B2Error("COTA_DESCONOCIDA")
    return (1 + Fraction(fila["xi"])) * Fraction(fila["cost_gross_gdp"]) + Fraction(F) + dc


def q_float_referencia(fila, cota):
    """Réplica en float de GridCell.Q (validación; no llama a C0)."""
    dc = float(fila["s_PB"]) if fila["requirement_basis"] == "debt_consistent" else 0.0
    F = float(fila["F_fix_perp"] if cota == "sin_addback" else fila["F_fix"])
    return (1.0 + float(fila["xi"])) * float(fila["cost_gross_gdp"]) + F + dc


def n_min_intervalo(q_ex, q_fl, dme):
    """n_min = min Q + DME como intervalo que contiene la versión exacta (literales) y la de C0 (min(ks) + dme_gai en float)."""
    ne = min(q_ex) + Fraction(dme)
    nf = min(q_fl) + float(dme)
    lo, hi = min(binario_afuera(ne, "lo"), nf), max(binario_afuera(ne, "hi"), nf)
    return {"lo": lo, "hi": hi, "lo_hex": float.hex(lo), "hi_hex": float.hex(hi), "exacto": fs(ne), "float_c0_hex": float.hex(nf),
            "dme": dme, "signo": "positivo" if lo > 0 else "negativo" if hi < 0 else "contiene_cero"}


def iv_de(IV, x):
    """Encierro hacia afuera de un racional exacto (o decimal) con la clase Iv de C0."""
    return IV(binario_afuera(x, "lo"), binario_afuera(x, "hi"))


def k1_intervalo(IV, n, q, s_pi, gain):
    """Forma acoplada en el orden de cobertura.g_enclosure:93-96 (lam = s_pi/(1-q); k1 = n_min/(lam*gain)), con s_Pi, gain, n_min y q como
    intervalos de la clase Iv de C0. Devuelve (Iv | None, motivo). Sin suposición de signo para n_min."""
    if not (s_pi.lo > 0):
        return None, "P7_S_PI_NO_POSITIVO"
    if not (gain.lo > 0):
        return None, "GAIN_NO_POSITIVO"
    uq = 1.0 - q
    if not (uq.lo > 0):
        return None, "Q_NO_MENOR_QUE_1"
    lam = s_pi / uq
    if not (lam.lo > 0):
        return None, "LAMBDA_NO_POSITIVO"
    return n / (lam * gain), None


def k1_referencia_exacta(n_vals, q_vals, s_pi, gain):
    """Referencia EXACTA independiente: min y max de n(1-q)/(s_Pi gain) sobre los extremos (K1 es monótono en n y en q por separado)."""
    vals = [Fraction(n) * (1 - Fraction(qq)) / (Fraction(s_pi) * Fraction(gain)) for n in n_vals for qq in q_vals]
    return min(vals), max(vals)


def regla(U, L):
    """True = certifica G_hi = U - L <= -1/100 (borde incluido); U y L como racionales exactos."""
    return Fraction(U) - Fraction(L) <= -EPS


class ProveedorReal:
    """Proveedor de PRODUCCIÓN: literales de los bundles CA2 y de D6 tax_shares_marg fijados (como nacional.conditional_states y
    enumerar_contextos_rem162.py), con la clave_entrada_efectiva recomputada para CADA uso (todos deben dar la clave del manifiesto), y
    filas de la grilla fijada con su huella. No calcula shares ni Q (eso lo hace evaluar())."""
    origen = "real"

    def __init__(self):
        self._b, self._tax = {}, None

    def _bundle(self, preg):
        if preg not in self._b:
            self._b[preg] = json.loads(leer(BUNDLE_POR_PREG[preg])[0])
        return self._b[preg]

    def _d6(self):
        if self._tax is None:
            self._tax = list(csv.DictReader(io.StringIO(leer("d6_tax_marg")[0].decode("utf-8"))))
        return self._tax

    def literales(self, clave, entrada):
        lits = []
        for u in entrada["usos"]:
            tab = self._bundle(u["preregistration_id"])
            vec = {v["vector_id"]: v for v in tab["ca2_vectors"]}
            mem = {}
            for m in tab["ca2_members"]:
                mem.setdefault(m["vector_id"], {})[m["concept"]] = m["value_literal"]
            if vec[u["d2_vector_id"]].get("vector_sha256") != u["d2_vector_sha256"] or vec[u["d6_vector_id"]].get("vector_sha256") != u["d6_vector_sha256"]:
                raise B2Error("VECTOR_DEL_BUNDLE_DISTINTO:" + clave[:16])
            tax = [r for r in self._d6() if r["preregistration_id"] == u["preregistration_id"] and r["country_id"] == PAIS and r["edition"] == u["d6_edicion"]]
            if sorted(r["component_id"] for r in tax) != sorted(COMPONENT_SHARE):
                raise B2Error("D6_FILAS:" + clave[:16])
            if {r["component_id"]: r["component_sign_status"] for r in tax} != u["d6_component_sign_status"]:
                raise B2Error("D6_SIGNO_DISTINTO:" + clave[:16])
            lit = {"d2_COE": mem[u["d2_vector_id"]].get("COE"), "d2_PIB": mem[u["d2_vector_id"]].get("PIB"),
                   "d6_shares_exact_json": {r["component_id"]: r["share_exact_json"] for r in sorted(tax, key=lambda r: r["component_id"])}}
            if lit["d2_COE"] is None or lit["d2_PIB"] is None or clave_de(lit) != clave:
                raise B2Error("CLAVE_EFECTIVA_NO_REPRODUCIDA:" + clave[:16])
            lits.append(lit)
        if not lits or any(canon(x) != canon(lits[0]) for x in lits):
            raise B2Error("USOS_CON_LITERALES_DISTINTOS:" + clave[:16])
        return lits[0]

    def filas_grilla(self):
        raw = leer("grilla")[0]
        filas = {}
        for r in csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")):
            if r["country_id"] == PAIS and capa_de(r["requirement_basis"], r["xi"]) == CAPA:
                filas[id_celda(r)] = _fila_grilla(r)
        return {"raw": raw, "filas": filas}

    def comprobar_fila(self, i, fila, sha):
        if H(canon(fila)) != sha:
            raise B2Error("FILA_DE_GRILLA_DISTINTA_DE_LA_FIJADA:" + i)


# ------------------------------------------------------------------------------------------------ núcleo B2 (trabajo)
def pendientes_de(sp):
    """Regla ÚNICA de premisas por (estado, nodo) sobre los 16 vértices de puente: P7 (s_Pi > 0), s_T >= 0, eta_H > -1 y bridge evaluable.
    sp = {(clave, eta_H, vértice): (s_Pi, s_T) | None}. Un fallo en un vértice deja PENDIENTE todo el (estado, nodo)."""
    pend = {}
    for (k, h, iv), v in sp.items():
        if v is None:
            mot = ["BRIDGE_NO_EVALUABLE"] + (["ETA_H_NO_MAYOR_QUE_MENOS_1"] if not Fraction(h) > -1 else [])
        else:
            s, t = v
            mot = [m for m, ok in (("P7_S_PI_NO_POSITIVO", s > 0), ("S_T_NEGATIVO", t >= 0), ("ETA_H_NO_MAYOR_QUE_MENOS_1", Fraction(h) > -1)) if not ok]
        if mot:
            pend.setdefault((k, h), set()).update(mot)
    return pend


def evaluar(man, mods, prov, reg):
    """Evalúa el plan con el proveedor dado (producción: fuentes reales autenticadas; sintético: doble). Devuelve el cuerpo de la evidencia.
    Una premisa fallida deja PENDIENTE el (estado, nodo) y todos sus contextos; ningún vértice se descarta."""
    MC, X, IV = mods["macro"], mods["external"], mods["intervalos"].Iv
    p = plan(man)
    q = man["q"]
    qiv = IV(q["lo"], q["hi"])
    out = {"literales": {}, "puentes": [], "celdas": [], "n_min": {}, "contextos": [], "pendientes": [], "grupos": {}}
    shares = {}
    for k in sorted({k for (k, _h, _v) in p["puentes"]}):
        lit = prov.literales(k, man["entradas_nacionales"][k])
        sh = shares_de(lit)
        shares[k] = sh
        out["literales"][k] = {"shares": {x: fs(v) for x, v in sh.items()}, "origen": prov.origen}
    sp = {}
    corner = {"kappa_tilde": "0.005", "a": "1.1", "rho": "0.4"}   # bridge exige la estructura para q_pot; s_Pi y s_T no dependen de ella
    for (k, h, iv) in sorted(p["puentes"]):
        om = dict(man["macro"]["vertices_puente"][iv], eta_H=h, **corner)
        try:
            m = MC.bridge(dict(shares[k]), om)
        except (ValueError, ZeroDivisionError) as ex:    # p. ej. ETA_H_GT_MINUS1 de theta_W: la entrada queda pendiente, no se descarta
            sp[(k, h, iv)] = None
            out["puentes"].append({"clave": k, "eta_H": h, "vertice_puente": iv, "s_Pi": None, "s_T": None,
                                   "razones": ["BRIDGE_NO_EVALUABLE:%s:%s" % (type(ex).__name__, str(ex)[:60])]})
            continue
        razones = [r for r in m.reasons if r != "Q_POT_GE_1"]
        sp[(k, h, iv)] = (Fraction(m.s_Pi_marg), Fraction(m.s_T_marg))
        out["puentes"].append({"clave": k, "eta_H": h, "vertice_puente": iv, "s_Pi": fs(m.s_Pi_marg), "s_T": fs(m.s_T_marg), "razones": razones})
    filas = prov.filas_grilla()
    celdas = {c.external_cell_id: c for c in X.read_grid(filas["raw"])}
    nmin = {}
    for cota in sorted({c for (c, _i) in p["celdas"]}):
        qe, qf = [], []
        for i in man["celdas"]["ids"]:
            c = celdas[i]
            if c.layer != CAPA or c.country_id != PAIS:
                raise B2Error("CELDA_DE_OTRA_CAPA:" + i)
            prov.comprobar_fila(i, filas["filas"][i], man["celdas"]["filas_sha256"][i])
            qv = c.Q(cota)
            qx = q_exacto(filas["filas"][i], cota)
            qe.append(qx)
            qf.append(qv)
            out["celdas"].append({"cota": cota, "cell_id": i, "Q_float": qv, "Q_float_hex": float.hex(qv), "Q_exacto": fs(qx),
                                  "literales": {x: filas["filas"][i][x] for x in ("xi", "cost_gross_gdp", "F_fix", "F_fix_perp", "s_PB", "requirement_basis")}})
        nmin[cota] = n_min_intervalo(qe, qf, man["dme_gai"]["por_cota"][cota])
        out["n_min"][cota] = nmin[cota]
    # premisas por (estado, nodo): P7 y s_T en los 16 vértices de puente, eta_H > -1
    pend = pendientes_de(sp)
    out["pendientes"] = [{"clave": k, "eta_H": h, "motivos": sorted(v)} for (k, h), v in sorted(pend.items())]
    cache = {}
    for (cota, k, h, v) in sorted(p["union"]):
        vert = man["macro"]["vertices"][v]
        iv = man["macro"]["indice_puente"][v]
        if (k, h) in pend:
            out["contextos"].append({"cota": cota, "clave": k, "eta_H": h, "v": v, "estado": "pendiente", "motivo": sorted(pend[(k, h)])})
            continue
        s, _t = sp[(k, h, iv)]
        key = (cota, k, h, v)
        r, mot = k1_intervalo(IV, IV(nmin[cota]["lo"], nmin[cota]["hi"]), qiv, iv_de(IV, s), iv_de(IV, vert["gain_share"]))
        if r is None:
            out["contextos"].append({"cota": cota, "clave": k, "eta_H": h, "v": v, "estado": "pendiente", "motivo": [mot]})
            continue
        cache[key] = r
        out["contextos"].append({"cota": cota, "clave": k, "eta_H": h, "v": v, "estado": "acotado", "k1_lo": r.lo, "k1_hi": r.hi,
                                 "k1_lo_hex": float.hex(r.lo), "k1_hi_hex": float.hex(r.hi)})
    est = {(c["cota"], c["clave"], c["eta_H"], c["v"]): c for c in out["contextos"]}
    for g in man["grupos"]:
        ks = p["por_grupo"][g["grupo"]]
        pc = [x for x in ks if est[x]["estado"] != "acotado"]
        L = min(est[x]["k1_lo"] for x in ks if est[x]["estado"] == "acotado") if len(pc) < len(ks) else None
        out["grupos"][g["grupo"]] = {"contextos": len(ks), "pendientes": len(pc), "L_K1": L if not pc else None,
                                     "L_K1_hex": float.hex(L) if (L is not None and not pc) else None,
                                     "minimo_parcial_hex": float.hex(L) if L is not None else None}
    out["llamadas_trabajo"] = {"macro.bridge": reg["bridge"], "GridCell.Q": reg["GridCell.Q"], "Q_exacto": len(out["celdas"]),
                               "k1_intervalar": len(cache), "contextos_pendientes": sum(1 for c in out["contextos"] if c["estado"] != "acotado"),
                               "C2": 0, "modelo": 0, "supremos": 0, "claim_contexts": 0}
    return out


# ------------------------------------------------------------------------------------------------ validación única, lectura y conciliación
CAMPOS_EVIDENCIA = {"kind", "tarea", "modo", "sintetico", "manifiesto_sha256", "alcance_sha256", "puerta_nativa", "indice_sha256", "inicio_utc",
                    "pieza", "q", "b1", "dme_gai", "literales", "puentes", "celdas", "n_min", "contextos", "pendientes", "grupos",
                    "llamadas_trabajo", "bloqueadas", "prohibidas_cargadas", "estado", "motivo", "fin_utc", "no_medido"}


def piezas_cambiadas(idx_p=None):
    idx_p = Path(idx_p or AQUI / INDICE)
    try:
        idx = json.loads(idx_p.read_bytes())
        return [n for n, h in idx["piezas"].items() if HF(AQUI / n) != h]
    except (OSError, ValueError, KeyError, TypeError) as ex:
        return ["INDICE_ILEGIBLE:%r" % (ex,)]


# rem168 (P4-B2-VALIDACION-CAMPOS-NUMERICOS): ESTRUCTURA EXACTA de cada registro, tal como la escribe evaluar() (sin campos de más ni de menos).
CAMPOS_CONTEXTO = {"acotado": frozenset({"cota", "clave", "eta_H", "v", "estado", "k1_lo", "k1_hi", "k1_lo_hex", "k1_hi_hex"}),
                   "pendiente": frozenset({"cota", "clave", "eta_H", "v", "estado", "motivo"})}
CAMPOS_CELDA = frozenset({"cota", "cell_id", "Q_float", "Q_float_hex", "Q_exacto", "literales"})
LITERALES_CELDA = ("xi", "cost_gross_gdp", "F_fix", "F_fix_perp", "s_PB", "requirement_basis")
CAMPOS_PUENTE = frozenset({"clave", "eta_H", "vertice_puente", "s_Pi", "s_T", "razones"})
CAMPOS_LITERALES = frozenset({"shares", "origen"})
CAMPOS_LLAMADAS = frozenset({"macro.bridge", "GridCell.Q", "Q_exacto", "k1_intervalar", "contextos_pendientes", "C2", "modelo", "supremos",
                             "claim_contexts"})
ORIGEN_POR_MODO = {"produccion": "real", "sintetico": "doble_inerte"}      # ProveedorReal.origen / pruebas/doble_b2.Doble.origen
EXCEPCIONES_DE_FORMA = (B2Error, TypeError, ValueError, KeyError, AttributeError, IndexError, ArithmeticError)


def _constante_no_json(x):
    """json.loads acepta NaN/Infinity/-Infinity, que NO son JSON (RFC 8259) y nunca los escribe el productor: se rechazan al leer."""
    raise ValueError("CONSTANTE_NO_FINITA_EN_JSON:%s" % x)


def binario_registrado(num, hx):
    """Un binary64 registrado DOS veces (número JSON y float.hex). Exige num de tipo float (no bool, int, str ni None), finito, y hx texto
    IGUAL a float.hex(num) (forma canónica del productor; sin normalizar ni tolerar). float.hex distingue -0.0 de 0.0. None = conforme."""
    if type(num) is not float:
        return "TIPO_NO_FLOAT:%s" % type(num).__name__
    if not math.isfinite(num):
        return "NO_FINITO"
    if type(hx) is not str:
        return "HEX_NO_TEXTO:%s" % type(hx).__name__
    if hx != float.hex(num):
        return "NUMERO_DISTINTO_DE_SU_HEX"
    return None


def par_binario(num, hx, ref):
    """binario_registrado y además bits IGUALES al valor reconstruido por la validación (float.hex(ref) == hx). None = conforme."""
    d = binario_registrado(num, hx)
    if d:
        return d
    if type(ref) is not float or float.hex(ref) != hx:
        return "DISTINTO_DE_LA_RECONSTRUCCION"
    return None


def intervalo_registrado(c):
    """Los dos extremos K1 de un contexto acotado (binario_registrado) y su orden k1_lo <= k1_hi. None = conforme."""
    for lado in ("k1_lo", "k1_hi"):
        d = binario_registrado(c[lado], c[lado + "_hex"])
        if d:
            return "%s:%s" % (lado, d)
    if not c["k1_lo"] <= c["k1_hi"]:
        return "INTERVALO_INVERTIDO"
    return None


def texto_fraccion(x):
    """Racional exacto registrado como el texto canónico fs (n o n/d reducido): ni números, ni decimales, ni espacios ni otras formas."""
    if type(x) is not str:
        return False
    try:
        return fs(Fraction(x)) == x
    except (ValueError, ZeroDivisionError):
        return False


def validar_evidencia(man, man_sha, ev_raw, modo, alcance_sha=None, indice_sha=None, puerta=None, IV=None):
    """VALIDACIÓN ÚNICA de EVIDENCIA_B2.json. Recalcula, sin bridge ni GridCell.Q: s_Pi y s_T exactos desde los shares registrados, Q exacto
    y su réplica float desde los literales, n_min, cada K1 intervalar (misma clase Iv) y una referencia EXACTA independiente por contexto
    (exige k1.lo <= mínimo exacto y k1.hi >= máximo exacto). rem168: exige además la estructura exacta de cada registro, tipos estrictos,
    finitud, k1_lo <= k1_hi y la concordancia BIT A BIT número / hexadecimal / reconstrucción de k1_lo, k1_hi y Q_float; las demás
    representaciones duplicadas (n_min, grupos, pendientes, q, b1, DME, recuentos) se comparan por igualdad canónica (canon distingue tipo y
    signo de cero). Toda forma inesperada se rechaza de modo controlado (EVIDENCIA_MAL_FORMADA), sin excepción. Sin tolerancias.
    Devuelve (fallos, datos, recuentos_validacion)."""
    rv = {"s_Pi_exacto": 0, "Q_exacto": 0, "Q_float_replica": 0, "k1_intervalar": 0, "k1_referencia_exacta": 0, "macro.bridge": 0, "GridCell.Q": 0}
    try:
        return _validar_evidencia(man, man_sha, ev_raw, modo, alcance_sha, indice_sha, puerta, IV, rv)
    except EXCEPCIONES_DE_FORMA as ex:
        return [("EVIDENCIA_MAL_FORMADA", "%s:%s" % (type(ex).__name__, str(ex)[:160]))], None, rv


def _validar_evidencia(man, man_sha, ev_raw, modo, alcance_sha, indice_sha, puerta, IV, rv):
    f = []
    try:
        e = json.loads(ev_raw, parse_constant=_constante_no_json)
    except (ValueError, TypeError) as ex:
        return [("EVIDENCIA_JSON_INVALIDA", str(ex)[:120])], None, rv
    if not isinstance(e, dict) or e.get("kind") != KIND_EVIDENCIA:
        return ["EVIDENCIA_DE_OTRO_TIPO"], None, rv
    if set(e) - CAMPOS_EVIDENCIA:
        return [("CAMPO_NO_PREVISTO_EN_LA_EVIDENCIA", sorted(set(e) - CAMPOS_EVIDENCIA))], None, rv
    sint = modo == "sintetico"
    if modo not in ("produccion", "sintetico") or man.get("modo") != modo or e.get("modo") != modo or e.get("sintetico") is not sint:
        return ["MODO_DISTINTO"], None, rv
    fm = validar_manifiesto(man)
    if fm:
        return ["MANIFIESTO_NO_VALIDO"] + [str(x)[:120] for x in fm[:4]], None, rv
    if e.get("tarea") != TAREA_TRABAJO:
        f.append("EVIDENCIA_DE_OTRA_TAREA")
    if e.get("manifiesto_sha256") != man_sha:
        f.append("MANIFIESTO_AJENO")
    if (modo == "produccion" and alcance_sha is None) or e.get("alcance_sha256") != alcance_sha:
        f.append("ALCANCE_AJENO_O_AUSENTE")
    if indice_sha is not None and e.get("indice_sha256") != indice_sha:
        f.append("INDICE_AJENO")
    if modo == "produccion":
        pe, pv = e.get("puerta_nativa") or {}, puerta or {}
        if not pe or pe.get("modo_arnes") is not False or any(pe.get(k) != pv.get(k) for k in ("uuid", "linea", "alcance_sha256", "registro_sha256")):
            f.append("PUERTA_NATIVA_DISTINTA_O_AUSENTE")
    pz = e.get("pieza") or {}
    mods_ev = (pz.get("identidad") or {}).get("modulos") or {}
    esperado = {("paper2b" if n == "__init__.py" else "paper2b." + n[:-3]): h for n, h in CIERRE_C0.items()}
    if {k: v.get("sha256") for k, v in mods_ev.items()} != esperado or pz.get("identidad_posterior"):
        f.append("PIEZA_O_MODULOS_NO_SON_EL_CIERRE_C0")
    if modo == "produccion" and pz.get("proveedor") != "real":
        f.append("PROVEEDOR_NO_REAL_EN_PRODUCCION")
    if sint and (pz.get("proveedor") != "doble_inerte" or pz.get("doble_sha256") != (man.get("doble") or {}).get("sha256")):
        f.append("DOBLE_NO_DECLARADO_O_AJENO")
    if canon(e.get("q")) != canon(man["q"]) or canon(e.get("b1")) != canon(man["b1"]) or canon(e.get("dme_gai")) != canon(man["dme_gai"]["por_cota"]):
        f.append("Q_B1_O_DME_DISTINTOS_DEL_MANIFIESTO")
    if canon(e.get("bloqueadas")) != canon({}) or canon(e.get("prohibidas_cargadas")) != canon([]):
        f.append("LLAMADAS_O_MODULOS_PROHIBIDOS")
    if e.get("estado") != "complete":
        f.append("TRABAJO_INCOMPLETO")
    if f:
        return f, None, rv
    p = plan(man)
    lt = e.get("llamadas_trabajo")
    if not (isinstance(lt, dict) and set(lt) == CAMPOS_LLAMADAS and all(type(x) is int for x in lt.values())):
        return f + [("LLAMADAS_DE_TRABAJO_DISTINTAS_DEL_PLAN", "FORMA_O_TIPO")], None, rv
    if lt["macro.bridge"] != len(p["puentes"]) or lt["GridCell.Q"] != len(p["celdas"]) or lt["Q_exacto"] != len(p["celdas"]) \
            or any(lt[k] != 0 for k in ("C2", "modelo", "supremos", "claim_contexts")):
        f.append(("LLAMADAS_DE_TRABAJO_DISTINTAS_DEL_PLAN", {k: lt[k] for k in ("macro.bridge", "GridCell.Q", "Q_exacto")}))
    # 1. literales (shares exactos en texto canónico) y s_Pi exacto desde los shares registrados (referencia independiente de bridge)
    lits = e.get("literales")
    claves = sorted({k for (k, _h, _v) in p["puentes"]})
    if not isinstance(lits, dict) or sorted(lits) != claves:
        return f + ["LITERALES_NO_CUBREN_LAS_DIEZ_ENTRADAS"], None, rv
    for k in claves:
        lk = lits[k]
        if not (isinstance(lk, dict) and set(lk) == CAMPOS_LITERALES and lk["origen"] == ORIGEN_POR_MODO[modo] and isinstance(lk["shares"], dict)
                and set(lk["shares"]) == set(SHARE_KEYS) and all(texto_fraccion(x) for x in lk["shares"].values())):
            return f + [("LITERALES_MAL_FORMADOS", k[:16])], None, rv
    if not isinstance(e.get("puentes"), list):
        return f + ["PUENTES_NO_CUBREN_EL_PLAN"], None, rv
    sp = {}
    for r in e["puentes"]:
        if not (isinstance(r, dict) and set(r) == CAMPOS_PUENTE):
            return f + [("PUENTE_MAL_FORMADO", str(sorted(r) if isinstance(r, dict) else type(r).__name__)[:120])], None, rv
        key = (r["clave"], r["eta_H"], r["vertice_puente"])
        if not (type(key[0]) is str and type(key[1]) is str and type(key[2]) is int) or key not in p["puentes"] or key in sp:
            return f + [("PUENTE_FUERA_DEL_PLAN_O_REPETIDO", str(key)[:80])], None, rv
        if not (isinstance(r["razones"], list) and all(type(x) is str for x in r["razones"])):
            return f + [("PUENTE_MAL_FORMADO", "razones", str(key)[:80])], None, rv
        om = dict(man["macro"]["vertices_puente"][key[2]], eta_H=key[1])
        if not Fraction(key[1]) > -1:      # theta_W no está definido: el trabajo tuvo que dejar la entrada sin valor (pendiente)
            if r["s_Pi"] is not None or r["s_T"] is not None:
                return f + [("PUENTE_CON_ETA_H_INVALIDO_CON_VALOR", str(key)[:80])], None, rv
            sp[key] = None
            continue
        s, t = s_pi_exacto(lits[key[0]]["shares"], om)
        rv["s_Pi_exacto"] += 1
        if fs(s) != r["s_Pi"] or fs(t) != r["s_T"]:
            return f + [("S_PI_O_S_T_NO_REPRODUCIDO", str(key)[:80])], None, rv
        sp[key] = (s, t)
    if set(sp) != p["puentes"]:
        return f + ["PUENTES_NO_CUBREN_EL_PLAN"], None, rv
    # 2. Q exacto y réplica float (número, hexadecimal y reconstrucción bit a bit); n_min
    if not isinstance(e.get("celdas"), list):
        return f + ["CELDAS_NO_CUBREN_EL_PLAN"], None, rv
    porc = {}
    for c in e["celdas"]:
        if not (isinstance(c, dict) and set(c) == CAMPOS_CELDA):
            return f + [("CELDA_MAL_FORMADA", str(sorted(c) if isinstance(c, dict) else type(c).__name__)[:120])], None, rv
        key = (c["cota"], c["cell_id"])
        if not (type(key[0]) is str and type(key[1]) is str) or key not in p["celdas"] or key in porc:
            return f + [("CELDA_FUERA_DEL_PLAN_O_REPETIDA", str(key)[:80])], None, rv
        fila = c["literales"]
        if not (isinstance(fila, dict) and set(fila) == set(LITERALES_CELDA) and all(type(x) is str for x in fila.values())):
            return f + [("CELDA_MAL_FORMADA", "literales", key[1])], None, rv
        qx, qf = q_exacto(fila, key[0]), q_float_referencia(fila, key[0])
        rv["Q_exacto"] += 1
        rv["Q_float_replica"] += 1
        if type(c["Q_exacto"]) is not str or fs(qx) != c["Q_exacto"]:
            return f + [("Q_NO_REPRODUCIDO", "Q_exacto", key[1])], None, rv
        d = par_binario(c["Q_float"], c["Q_float_hex"], qf)
        if d:
            return f + [("Q_NO_REPRODUCIDO", "Q_float:" + d, key[1])], None, rv
        porc[key] = (qx, qf)
    if set(porc) != p["celdas"]:
        return f + ["CELDAS_NO_CUBREN_EL_PLAN"], None, rv
    nev = e.get("n_min")
    cotas = sorted({c for (c, _i) in p["celdas"]})
    if not isinstance(nev, dict) or sorted(nev) != cotas:
        return f + [("N_MIN_NO_REPRODUCIDO", "COTAS")], None, rv
    nmin = {}
    for cota in cotas:
        n = n_min_intervalo([porc[(cota, i)][0] for i in man["celdas"]["ids"]], [porc[(cota, i)][1] for i in man["celdas"]["ids"]],
                            man["dme_gai"]["por_cota"][cota])
        if canon(n) != canon(nev[cota]):
            return f + [("N_MIN_NO_REPRODUCIDO", cota)], None, rv
        nmin[cota] = n
    # 3. premisas, K1 intervalar (misma clase Iv) y referencia exacta independiente por contexto
    pend = pendientes_de(sp)
    if canon([{"clave": k, "eta_H": h, "motivos": sorted(v)} for (k, h), v in sorted(pend.items())]) != canon(e.get("pendientes")):
        return f + ["PENDIENTES_NO_REPRODUCIDOS"], None, rv
    q = man["q"]
    qiv = IV(q["lo"], q["hi"])
    if not isinstance(e.get("contextos"), list):
        return f + [("CONTEXTOS_NO_CUBREN_EL_PLAN", 0)], None, rv
    ctxs = {}
    for c in e["contextos"]:
        est = c.get("estado") if isinstance(c, dict) else None
        if not (type(est) is str and est in CAMPOS_CONTEXTO and set(c) == CAMPOS_CONTEXTO[est]):
            return f + [("CONTEXTO_MAL_FORMADO", str(sorted(c) if isinstance(c, dict) else type(c).__name__)[:120])], None, rv
        key = (c["cota"], c["clave"], c["eta_H"], c["v"])
        if not (type(key[0]) is str and type(key[1]) is str and type(key[2]) is str and type(key[3]) is int) or key not in p["union"] or key in ctxs:
            return f + [("CONTEXTO_FUERA_DEL_PLAN_O_REPETIDO", str(key)[:80])], None, rv
        if est == "acotado":
            d = intervalo_registrado(c)
            if d:
                return f + [("K1_NO_REPRODUCIDO", d, str(key)[:80])], None, rv
        elif not (isinstance(c["motivo"], list) and c["motivo"] and all(type(x) is str for x in c["motivo"])):
            return f + [("CONTEXTO_MAL_FORMADO", "motivo", str(key)[:80])], None, rv
        ctxs[key] = c
    if set(ctxs) != p["union"]:
        return f + [("CONTEXTOS_NO_CUBREN_EL_PLAN", len(ctxs))], None, rv
    peor = Fraction(0)
    for key, c in ctxs.items():
        cota, k, h, v = key
        if (k, h) in pend:
            if c["estado"] != "pendiente":
                return f + [("CONTEXTO_CON_PREMISA_FALLIDA_NO_PENDIENTE", str(key)[:80])], None, rv
            if c["motivo"] != sorted(pend[(k, h)]):
                return f + [("PENDIENTE_NO_REPRODUCIDO", "motivo", str(key)[:80])], None, rv
            continue
        s = sp[(k, h, man["macro"]["indice_puente"][v])][0]
        g = man["macro"]["vertices"][v]["gain_share"]
        r, mot = k1_intervalo(IV, IV(nmin[cota]["lo"], nmin[cota]["hi"]), qiv, iv_de(IV, s), iv_de(IV, g))
        rv["k1_intervalar"] += 1
        if r is None:
            if c["estado"] != "pendiente" or c["motivo"] != [mot]:
                return f + [("PENDIENTE_NO_REPRODUCIDO", str(key)[:80])], None, rv
            continue
        if c["estado"] != "acotado":
            return f + [("K1_NO_REPRODUCIDO", "ESTADO_NO_ACOTADO", str(key)[:80])], None, rv
        for lado, ref in (("k1_lo", r.lo), ("k1_hi", r.hi)):
            d = par_binario(c[lado], c[lado + "_hex"], ref)
            if d:
                return f + [("K1_NO_REPRODUCIDO", "%s:%s" % (lado, d), str(key)[:80])], None, rv
        nv = [Fraction(nmin[cota]["exacto"]), Fraction(float.fromhex(nmin[cota]["float_c0_hex"]))]
        mn, mx = k1_referencia_exacta(nv, [Fraction(q["lo_exacto"]), Fraction(q["hi_exacto"])], s, Fraction(g))
        rv["k1_referencia_exacta"] += 1
        if not (Fraction(r.lo) <= mn and Fraction(r.hi) >= mx):
            return f + [("K1_NO_ENCIERRA_LA_REFERENCIA_EXACTA", str(key)[:80])], None, rv
        if mn != 0:
            peor = max(peor, (mn - Fraction(r.lo)) / abs(mn))
    gev = e.get("grupos")
    if not isinstance(gev, dict) or sorted(gev) != sorted(g["grupo"] for g in man["grupos"]):
        return f + [("GRUPO_NO_REPRODUCIDO", "CONJUNTO_DE_GRUPOS")], None, rv
    grupos = {}
    for g in man["grupos"]:
        ks = p["por_grupo"][g["grupo"]]
        ac = [ctxs[x]["k1_lo"] for x in ks if ctxs[x]["estado"] == "acotado"]
        pc = len(ks) - len(ac)
        L = min(ac) if ac else None
        reg_g = {"contextos": len(ks), "pendientes": pc, "L_K1": L if not pc else None, "L_K1_hex": float.hex(L) if (L is not None and not pc) else None,
                 "minimo_parcial_hex": float.hex(L) if L is not None else None}
        if canon(reg_g) != canon(gev[g["grupo"]]):
            return f + [("GRUPO_NO_REPRODUCIDO", g["grupo"])], None, rv
        grupos[g["grupo"]] = reg_g
    na = sum(1 for c in ctxs.values() if c["estado"] == "acotado")
    if lt["k1_intervalar"] != na or lt["contextos_pendientes"] != len(ctxs) - na:
        f.append(("LLAMADAS_DE_TRABAJO_DISTINTAS_DEL_PLAN", {"k1_intervalar": lt["k1_intervalar"], "contextos_pendientes": lt["contextos_pendientes"]}))
    if f:
        return f, None, rv
    return [], {"grupos": grupos, "U_C2": man["b1"]["U_C2"], "holgura_relativa_max_k1": float(peor),
                "contextos_acotados": sum(1 for c in ctxs.values() if c["estado"] == "acotado"),
                "contextos_pendientes": sum(1 for c in ctxs.values() if c["estado"] != "acotado"), "n_min": nmin}, rv


def lectura(man, datos):
    """Una fila por grupo (6) y correspondencia con las doce. datos None → sin lectura científica válida. No clasifica: propone."""
    if datos is None:
        return {"valida": False, "motivo": "RESULTADO_INVALIDO_O_INCOMPLETO", "grupos": [], "afirmaciones": []}
    U = Fraction(man["b1"]["U_C2"])
    filas, por = [], []
    for g in man["grupos"]:
        d = datos["grupos"][g["grupo"]]
        if d["pendientes"] or d["L_K1"] is None:
            lec, Gh = "pendiente", None
        else:
            Gh = U - Fraction(d["L_K1"])
            lec = "certifica_G_negativo" if Gh <= -EPS else "desconocida"
        filas.append({"grupo": g["grupo"], "cota": g["cota"], "L_K1": d["L_K1"], "L_K1_hex": d["L_K1_hex"], "U_C2": man["b1"]["U_C2"],
                      "U_C2_hex": man["b1"]["U_C2_hex"], "G_hi_exacto": fs(Gh) if Gh is not None else None,
                      "comparacion": None if Gh is None else ("<=" if Gh <= -EPS else ">"), "lectura": lec, "pendientes": d["pendientes"],
                      "significado": {"certifica_G_negativo": "U_C2 - L_K1 <= -1/100: g.hi <= -eps en todo el dominio COV del grupo (lectura "
                                                              "'infeasible' de cobertura.classify); la categoria la decide el revisor",
                                      "desconocida": "G_hi > -1/100: no certifica; la afirmacion sigue desconocida",
                                      "pendiente": "premisa fallida o contexto sin cota: el grupo queda pendiente"}[lec],
                      "afirmaciones": list(g["afirmaciones"])})
        for a in g["afirmaciones"]:
            por.append({"afirmacion": a, "grupo": g["grupo"], "lectura": lec, "estado_cientifico": "desconocida (sin cambio)"})
    return {"valida": True, "eps": "1/100", "U_C2": man["b1"]["U_C2"], "grupos": filas, "afirmaciones": sorted(por, key=lambda x: x["afirmacion"]),
            "no_clasifica": True, "no_robustez": True, "K1_testigo_no_usado": True, "N3A_no_adoptada": True}


def conciliacion(man, datos, lec):
    """Conciliación: inclusiones (un subconjunto de contextos no puede tener L menor), 12 ↔ 6, G/N comparten grupo, lectura coherente."""
    f = []
    if datos is None:
        return {"conforme": False, "fallos": ["SIN_DATOS"]}
    g = datos["grupos"]
    for sub, sups in (("K5", ("K1", "K3")), ("K6", ("K2", "K4"))):
        for s in sups:
            if g[sub]["L_K1"] is not None and g[s]["L_K1"] is not None and not g[sub]["L_K1"] >= g[s]["L_K1"]:
                f.append(("INCLUSION_VIOLADA", sub, s))
    afs = {a["afirmacion"]: a["grupo"] for a in lec["afirmaciones"]}
    if len(afs) != 12 or {a["afirmacion"]: a["grupo"] for a in man["afirmaciones"]} != afs or afs != man["b1"]["afirmacion_grupo"]:
        f.append("DOCE_AFIRMACIONES_NO_CONCILIAN")
    for x in lec["grupos"]:
        if sorted(a.split(":")[7] for a in x["afirmaciones"]) != ["G", "N"]:
            f.append(("GRUPO_SIN_PAR_G_N", x["grupo"]))
    return {"conforme": not f, "fallos": f, "comprobaciones": {"inclusiones": 4, "afirmaciones": 12, "grupos": 6}}


# ------------------------------------------------------------------------------------------------ procedencia (derivada de comun_b1 rem165)
INTERPRETE_AUTORIZADO = Path(r"@@R_WIN@@\tmp\pilotos_b36_b37_2026-10-02\entorno\cpython-3.12.4-amd64\python.exe")
INTERPRETE_SHA256 = "fd5c46d73d29ba21b04c844bbaf9096066136526911230645a2a040d23fb612b"
OPCIONES_INTERPRETE = ("-B", "-I", "-X", "utf8")
ARGS_TRABAJO = ("--modo", "--manifiesto", "--salida", "--alcance", "--decision")
_PROHIBIDOS_RUTA = '"<>|?*'
CONTINUACION = None     # B2 no implementa continuación entre rondas: el conductor la rechaza (CONTINUACION_NO_IMPLEMENTADA_EN_B2)


def ruta_windows(x, base=None):
    """Normalización DECLARADA (idéntica a comun_b1.ruta_windows rem165): léxica, determinista, sin tocar el disco. None = no admitida."""
    if not isinstance(x, str) or not x or any(ord(c) < 32 for c in x) or any(c in _PROHIBIDOS_RUTA for c in x):
        return None
    s = x.replace("/", "\\")
    if s.startswith("\\\\"):
        return None
    if len(s) >= 2 and s[1] == ":":
        if not ("A" <= s[0].upper() <= "Z") or len(s) < 3 or s[2] != "\\":
            return None
        unidad, resto = s[0].upper() + ":", s[3:]
    elif s.startswith("\\") or base is None:
        return None
    else:
        unidad, resto = base[:2], base[3:] + "\\" + s
    if ":" in resto:
        return None
    partes = []
    for c in resto.split("\\"):
        if c in ("", "."):
            continue
        if c == "..":
            if not partes:
                return None
            partes.pop()
            continue
        if c[-1] in ". ":
            return None
        partes.append(c)
    return unidad + "\\" + "\\".join(partes)


def _invocacion(av, cwd, script):
    """Orden COMPLETA registrada por p3ctl frente a la admitida de `script` (mismo criterio que comun_b1._invocacion rem165)."""
    if not isinstance(av, list) or not all(isinstance(x, str) for x in av):
        return "ARGV_NO_ES_LISTA_DE_TEXTO", None
    base = ruta_windows(cwd) if isinstance(cwd, str) else None
    if base is None or base != ruta_windows(str(R)):
        return "CWD_NO_AUTENTICADO", None
    n = len(OPCIONES_INTERPRETE)
    if len(av) < n + 2:
        return "INVOCACION_INCOMPLETA", None
    if ruta_windows(av[0], base) != ruta_windows(str(INTERPRETE_AUTORIZADO)):
        return "INTERPRETE_NO_AUTORIZADO", None
    if HF(INTERPRETE_AUTORIZADO) != INTERPRETE_SHA256:
        return "INTERPRETE_DE_OTRA_IDENTIDAD", None
    if tuple(av[1:n + 1]) != OPCIONES_INTERPRETE:
        return "OPCIONES_DEL_INTERPRETE_NO_PREVISTAS", None
    if ruta_windows(av[n + 1], base) != ruta_windows(str(AQUI / script)):
        return "PROGRAMA_DISTINTO_DEL_SCRIPT_FIJADO", None
    if HF(AQUI / script) != json.loads((AQUI / INDICE).read_bytes())["piezas"][script]:
        return "SCRIPT_DISTINTO_DEL_INDICE", None
    return None, av[n + 2:]


def _utc(s):
    t = dt.datetime.fromisoformat(str(s))
    return t if t.tzinfo else None


def procedencia(fuente, modo, man_sha, alcance_sha, propia=None):
    """ÚNICA comprobación de procedencia. fuente = {"tipo": "lanzamiento", "area": A, "lanzamiento": L[, "evidencia_sha256": h]}; cualquier
    otro tipo (continuación) se rechaza. Devuelve (fallos, bytes_evidencia, info)."""
    info = {"tipo": (fuente or {}).get("tipo"), "modo": modo}
    try:
        return _procedencia(fuente or {}, modo, man_sha, alcance_sha, propia, info)
    except (B2Error, OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as ex:
        return ["PROCEDENCIA_NO_AUTENTICA: %s" % str(ex)[:200]], None, info


def _procedencia(fuente, modo, man_sha, alcance_sha, propia, info):
    if modo not in ("produccion", "sintetico"):
        return ["MODO_DESCONOCIDO"], None, info
    if fuente.get("tipo") != "lanzamiento":
        return ["CONTINUACION_NO_IMPLEMENTADA_EN_B2"], None, info
    area, lanz = Path(fuente["area"]), str(fuente["lanzamiento"])
    if HF(area / "codigo/p3ctl.py") != P3CTL_SHA or not (area / "audit/recepcion.json").is_file():
        return ["AREA_DE_ORIGEN_SIN_CONTENCION"], None, info
    evb = (area / "audit/p3ctl/eventos.jsonl").read_bytes()
    evs = jsonl(evb)
    info.update(area=str(area), lanzamiento=lanz, eventos_sha256=H(evb))
    tid = "%s_TRABAJO" % lanz
    ini = [x for x in evs if x.get("evento") == "directa_inicio" and x.get("id") == tid]
    fin = [x for x in evs if x.get("evento") == "directa_fin" and x.get("id") == tid]
    if len(ini) != 1 or len(fin) != 1:
        return ["EJECUCION_DE_TRABAJO_AUSENTE_O_REPETIDA"], None, info
    ini, fin = ini[0], fin[0]
    info.update(evento_inicio_sha256=H(canon(ini)), evento_fin_sha256=H(canon(fin)))
    if not (fin.get("conforme") is True and fin.get("estado") == "TERMINO" and fin.get("codigo_salida") == 0):
        return ["EJECUCION_DE_TRABAJO_NO_CONFORME"], None, info
    mot, resto = _invocacion(ini.get("argv"), ini.get("cwd"), "b2_trabajo.py")
    if mot:
        return ["INVOCACION_DE_TRABAJO_NO_AUTORIZADA:" + mot], None, info
    op = {resto[j]: resto[j + 1] for j in range(0, len(resto) - 1, 2)}
    if len(resto) % 2 or set(op) - set(ARGS_TRABAJO) or len(op) * 2 != len(resto):
        return ["ARGUMENTOS_DE_TRABAJO_NO_PREVISTOS"], None, info
    cwd = Path(ini.get("cwd") or ".")
    absol = lambda x: Path(x) if Path(x).is_absolute() else cwd / x  # noqa: E731
    if op.get("--modo") != modo:
        return ["EJECUCION_DE_OTRO_MODO"], None, info
    if HF(absol(op["--manifiesto"])) != man_sha:
        return ["EJECUCION_DE_OTRO_MANIFIESTO"], None, info
    if (HF(absol(op["--alcance"])) if op.get("--alcance") else None) != alcance_sha:
        return ["EJECUCION_DE_OTRO_ALCANCE"], None, info
    dT = absol(op["--salida"])
    so = (area / "logs/p3_directas" / (tid + ".stdout.log")).read_bytes()
    if fin.get("salida_bytes") != len(so):
        return ["SALIDA_DEL_TRABAJADOR_DISTINTA_DE_LA_REGISTRADA"], None, info
    try:
        rw = json.loads(so.decode("utf-8").strip().splitlines()[-1])
    except (ValueError, IndexError):
        return ["SALIDA_DEL_TRABAJADOR_ILEGIBLE"], None, info
    if rw.get("tarea") != TAREA_TRABAJO or rw.get("estado") != "complete" or not isinstance(rw.get("evidencia_sha256"), str):
        return ["TRABAJADOR_SIN_RESULTADO_COMPLETO"], None, info
    h_rec = rw["evidencia_sha256"]
    info.update(trabajo_id=tid, trabajo_dir=str(dT), salida_trabajador_sha256=H(so), evidencia_sha256=h_rec)
    if fuente.get("evidencia_sha256") is not None and fuente["evidencia_sha256"] != h_rec:
        return ["EVIDENCIA_DISTINTA_DE_LA_DEL_CONDUCTOR"], None, info
    raw = (dT / "EVIDENCIA_B2.json").read_bytes()
    if H(raw) != h_rec:
        return ["EVIDENCIA_DISTINTA_DE_LA_EJECUCION"], None, info
    e = json.loads(raw)
    t_ini, t_fin, e_ini, e_fin = _utc(ini.get("utc")), _utc(fin.get("utc")), _utc(e.get("inicio_utc")), _utc(e.get("fin_utc"))
    if None in (t_ini, t_fin, e_ini, e_fin) or not (t_ini <= e_ini <= e_fin <= t_fin):
        return ["EVIDENCIA_FUERA_DE_SU_EJECUCION"], None, info
    if propia is not None:
        pa = Path(propia["area"])
        if HF(pa / "codigo/p3ctl.py") != P3CTL_SHA:
            return ["VALIDACION_FUERA_DE_UN_AREA_CONTENIDA"], None, info
        pevs = jsonl((pa / "audit/p3ctl/eventos.jsonl").read_bytes())
        tv = "%s_VALIDACION" % propia["lanzamiento"]
        pi = [x for x in pevs if x.get("evento") == "directa_inicio" and x.get("id") == tv]
        pf = [x for x in pevs if x.get("evento") == "directa_fin" and x.get("id") == tv]
        if len(pi) != 1 or pf:
            return ["VALIDACION_FUERA_DE_SU_DIRECTA"], None, info
        mot, presto = _invocacion(pi[0].get("argv"), pi[0].get("cwd"), "validar_b2.py")
        if mot:
            return ["INVOCACION_DE_VALIDACION_NO_AUTORIZADA:" + mot], None, info
        if presto != [str(x) for x in propia["argv"]]:
            return ["VALIDACION_FUERA_DE_SU_DIRECTA"], None, info
        if pa.resolve() != area.resolve() or str(propia["lanzamiento"]) != lanz:
            return ["VALIDACION_DE_OTRO_LANZAMIENTO"], None, info
        info["validacion_id"] = tv
    return [], raw, info
