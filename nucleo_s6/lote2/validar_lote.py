"""rem119 (P4-SUPLEMENTO-C0-COMPATIBILIDAD, COPIA AISLADA): en las mallas marcadas suplemento_topologia, el validador reconstruye desde el
manifiesto autenticado y los BYTES de la fuente aceptada (sha256 del manifiesto; una lectura) qué filas debían conservarse, y exige que el
producto contenga EXACTAMENTE esas filas (sin omisiones, duplicados ni ajenas), con todos sus campos históricos idénticos en valor y tipo
(incluidos nulos y −0.0) y como único campo añadido «topology». La topología sigue comprobándose con la ruta real del núcleo (igual que en el
resto de filas); además se reconstruye, solo con topologías, la estructura de estencil del núcleo en cada punto (kink, derivadas disponibles
frente a los nulos históricos, régimen) y debe ser compatible con la fila histórica. La procedencia (producto suplemento_procedencia.jsonl)
debe cubrir exactamente esas filas, con la huella canónica de cada fila aceptada, la fuente del manifiesto, origen numérico LOTE1_ACEPTADO,
la topología publicada, la identidad del núcleo fijado y el sha256 de frontier_result.jsonl; una procedencia sin suplemento en el manifiesto
es engañosa. Ya no hay comparación numérica del suplemento con T1 (los campos históricos deben ser exactos); T1 sigue en las identidades.
El núcleo fijado se localiza en su ubicación sellada (tmp/paso4_raices_impacto_desde_rem116/candidato_c0/instalacion, d0bf5cd6…).
rem116 (P4-RAICES-C0-SUBDESBORDAMIENTO, COPIA AISLADA): el núcleo de referencia del validador deja de ser la instalación vigente
(<raiz>/paso4/instalacion/src, que conserva el aislador defectuoso de trinomial_roots con C = 0) y pasa a ser el NÚCLEO CORREGIDO del paquete
(<área>/candidato_c0/instalacion), fijado por su identidad canónica d0bf5cd6… y comprobado ANTES de importar paper2b; identidad distinta o
instalación ilegible ⇒ fallo controlado NUCLEO_DE_OTRA_IDENTIDAD (rc 4), nunca aceptación ni retorno a la instalación vigente. Ninguna regla
cambia: los NA siguen exigiéndose solo donde la regla los pide (los nulos sin motivo siguen siendo fallo) y H_DIFF es el del núcleo.
rem114 (P4-LOTE2-TOPOLOGIA y G-E0E3, COPIA AISLADA): (1) con topologia_requerida, la topología de cada fila debe coincidir con la que el
núcleo asigna a su clave estructural, diseño y punto de tasas (proveedor.evaluate(...).topology; laterales con la del punto, según
frontier.point_rows); (2) un conjunto de dominio estricto exige un anexo de vértices que se reproduzca desde su definición (misma enumeración
estructural que el trabajador), con la definición del manifiesto y la condición de signo. El resto de controles no cambia.
rem113 (COPIA AISLADA para el lote 2): en L1-COORD, un techo marcado como reutilizado debe estar declarado en techos_reutilizados del
manifiesto y coincidir EXACTAMENTE con su valor aceptado (C_2, estado, error, motivo) y con el sha256 de su fuente; un techo reutilizado no
declarado, o declarado y distinto, ⇒ fallo. En L1-ELAST, si el manifiesto declara topologia_requerida, toda fila debe llevar su topología de
adopción; una frontera marcada suplemento_topologia (malla ACEPTADA recalculada solo por su topología) debe reproducir fila a fila los
valores aceptados de su fuente autenticada (sha256 del manifiesto), dentro de T1. El resto de controles no cambia.
rem111 (P4-LOTE1-COBERTURA-NACIONAL): en L1-LAMBDA la evidencia de cada extremo y variante se contrasta con el ANEXO DE COBERTURA NACIONAL
ligado al manifiesto (estados esperados por conjunto y ω, reconstruidos de la preparación autenticada, nunca de la salida validada): misma
secuencia de huellas shares_sha256 e índices 0..n−1, sin omisiones, ajenos, sustituciones ni duplicados; el testigo nacional es uno de ellos.
Sin anexo, con anexo de otro manifiesto o de otros conjuntos ⇒ fallo.
rem110 — VALIDADOR del lote 1 (P4-LOTE1-VALIDACION). Reconstruye desde el MANIFIESTO AUTENTICADO los conjuntos exactos, la unicidad, las
relaciones y las identidades; el número de filas no basta. Una tarea solo es «completa_validada» si no hay ningún fallo:
  L1-LAMBDA  filas exactamente {conjunto del manifiesto} × {con, sin}, sin duplicados; estado ok (pendiente_no_cubierto, dominio_vacio… ⇒ fallo);
             K1/Q_min = 1/(λ_max·g_máx) y K1/Q_max = 1/(λ_min·g_mín) en aritmética EXACTA con los extremos de gain_share del manifiesto;
             λ_max ≥ λ_min > 0; testigos ω dentro de su dominio (continuo con sus cierres o discreto), θ_W = macro.theta_W del testigo y ≥ 0 en la
             variante «sin»; si el manifiesto fija testigos por variante, deben coincidir; testigo nacional y evidencia admisible de cada estado.
  L1-ELAST   solo fronteras del manifiesto; en cada una, EXACTAMENTE los nodos de la malla del núcleo (supremum.axes/nodes con el instrumento j y
             frontier_n de RunConfig) con su point_id, UNA fila «point» y, si y solo si hay kink, sus filas left_limit/right_limit;
             computation_status=complete; audit_status y reason_code iguales a los que fija point_rows (limitation/KINK_NO_DERIVATIVE en el kink,
             LATERAL_DERIVATIVE en los laterales, BASE_NONPOSITIVE, SP_LIMIT_AT_ZERO_RATE en τ_f=0); NA solo donde la regla los exige (elasticidad
             con base B ≤ 0 o fila «point» con kink; s_P nula si y solo si τ_f=0); valores finitos; R = τ_d·B_d + τ_f·B_f, CS = R/B_pot y
             s_P = model.provider_share (T1).
  L1-COORD   techos con EXACTAMENTE las claves transformadas del manifiesto (sin ajenas ni duplicadas), estado complete, C_2 y error finitos y
             motivo conservado; una comparación por celda padre del manifiesto (sin faltantes, ajenas ni duplicadas) con su cell_id, K1 reutilizado
             y G padre del manifiesto; C2_COORD = C_2 del techo de SU clave del manifiesto y G_COORD = C2_COORD − K1 del manifiesto (T1).
Además: productos con su sha256, manifiesto idéntico, coherencia sintético/real, esquema completo. Esquema inválido o valores no finitos ⇒
fallo controlado (nunca aceptación por omisión).
Uso: python -B -I -X utf8 validar_lote.py <raiz> <manifiesto> <resultado.json> <salida_dir> [<cobertura_nacional.json> (obligatorio en L1-LAMBDA)]"""
import hashlib
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

R, MAN, RES, SAL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
COB = Path(sys.argv[5]) if len(sys.argv) > 5 else None
NUCLEO = Path(__file__).resolve().parents[2] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"   # rem119: C0 en su ubicación sellada
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
sys.path.insert(0, str(NUCLEO / "herramientas/b"))
try:
    import aprobacion_alcance as _AA  # noqa: E402  (solo la identidad canónica de la instalación)
    _ident = _AA.identidad_instalacion(NUCLEO)
except (ImportError, OSError) as _ex:
    _ident = "ILEGIBLE (%s)" % _ex
del sys.path[0]
if _ident != NUCLEO_IDENTIDAD:
    print(json.dumps({"aceptada": False, "fallos": ["NUCLEO_DE_OTRA_IDENTIDAD (%s ≠ %s)" % (_ident, NUCLEO_IDENTIDAD)], "n_fallos": 1,
                      "dictamen": "incompleta (no se publica como terminada)"}, ensure_ascii=False))
    raise SystemExit(4)
sys.path.insert(0, str(NUCLEO / "src"))
from paper2b import macro as MC  # noqa: E402
from paper2b import model as M  # noqa: E402
from paper2b.run import RunConfig  # noqa: E402
from paper2b.supremum import axes, nodes  # noqa: E402
from paper2b.run import provider_for, _to_state_prim  # noqa: E402  (rem114: misma construcción de estado que conexion_frontera)
from paper2b import frontier as FRV  # noqa: E402  (rem119: H_DIFF y location del núcleo para la estructura del suplemento)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import conexion_lambda as CLX  # noqa: E402  (rem114: misma enumeración estructural de dominios estrictos que el trabajador)

H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
T1 = 1e-12
CAMPOS_FRONTERA = ("frontier_id", "point_id", "side", "tau_d", "tau_f", "B_d", "B_f", "R", "B_pot", "CS", "eps_dd", "eps_df", "eps_fd", "eps_ff", "s_P",
                   "regime", "kink_adjacent", "audit_status", "computation_status", "reason_code")
BASE_EPS = {"eps_dd": "B_d", "eps_df": "B_d", "eps_fd": "B_f", "eps_ff": "B_f"}     # denominador de cada elasticidad en frontier._elasticities
OMEGA = ("eta_w", "eta_H", "pi_iva", "pi_otros_productos", "pi_produccion", "a", "rho", "kappa_tilde")
fallos = []


def falla(c):
    fallos.append(c)


def finito(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def fr(x):
    try:
        return Fr(str(x)) if x is not None else None
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def cerrado(x):
    return x in (True, "True", "true")


def dom_ext(d):
    v = sorted(Fr(x) for x in d["valores"]) if d["tipo"] == "discreto" else [Fr(d["lo"]), Fr(d["hi"])]
    return v[0], v[-1]


def en_dominio(x, d):
    if d["tipo"] == "discreto":
        return x in {Fr(v) for v in d["valores"]}
    lo, hi = Fr(d["lo"]), Fr(d["hi"])
    return (lo < x or (cerrado(d["lo_cerrado"]) and x == lo)) and (x < hi or (cerrado(d["hi_cerrado"]) and x == hi))


def theta_extremo(dw, dh, variante, lado):
    """θ_W mínimo (lado max) o máximo (lado min) sobre el cierre del dominio; θ_W crece en η_w para cada η_H > −1; «sin» corta en θ_W ≥ 0."""
    lo, hi = dom_ext(dw)
    vals = []
    for h in (Fr(x) for x in dh["valores"]):
        a, b = (lo + h) / (1 + h), (hi + h) / (1 + h)
        if variante == "sin":
            if b < 0:
                continue
            a = max(a, Fr(0))
        vals.append(a if lado == "max" else b)
    return min(vals) if lado == "max" else max(vals)


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False))
    raise SystemExit(rc)


try:
    raw = MAN.read_bytes()
    man, res = json.loads(raw), json.loads(RES.read_bytes())
    t = res["tarea"]
except (ValueError, OSError, KeyError, TypeError) as ex:
    salir({"aceptada": False, "fallos": ["ESQUEMA_ILEGIBLE: %s" % ex], "n_fallos": 1, "dictamen": "incompleta (no se publica como terminada)"}, 4)
SINT = str(man.get("kind", "")).endswith("-SINTETICO")
if res.get("manifiesto_sha256") != H(raw):
    falla("MANIFIESTO_DISTINTO")
if res.get("sintetico") is not SINT or res.get("modo") != ("sintetico" if SINT else "produccion"):
    falla("SINTETICO_O_MODO_INCOHERENTE (sintetico=%s, modo=%s, manifiesto sintético=%s)" % (res.get("sintetico"), res.get("modo"), SINT))
if res.get("estado") != "completa":
    falla("TAREA_NO_COMPLETA:%s" % res.get("estado"))
prods = {}
for p in res.get("productos") or []:
    f = SAL / str(p.get("archivo"))
    if not f.is_file() or H(f.read_bytes()) != p.get("sha256"):
        falla("PRODUCTO_ALTERADO_O_AUSENTE:%s" % p.get("archivo"))
        continue
    try:
        filas = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    except ValueError:
        falla("PRODUCTO_NO_JSONL:%s" % p["archivo"])
        continue
    if not all(isinstance(x, dict) for x in filas) or len(filas) != p.get("filas"):
        falla("PRODUCTO_ESQUEMA_O_RECUENTO:%s" % p["archivo"])
        continue
    if any(x.get("sintetico") is not SINT for x in filas):
        falla("FILA_SINTETICO_INCOHERENTE:%s" % p["archivo"])
    prods[p["archivo"]] = filas


def anexo_cobertura(ml):
    """rem111: estados nacionales ESPERADOS por conjunto (y ω), del anexo ligado al manifiesto; None si no hay anexo válido."""
    if COB is None or not COB.is_file():
        falla("COBERTURA_NACIONAL_SIN_ANEXO")
        return None
    an = json.loads(COB.read_bytes())
    if an.get("kind") != "cobertura-nacional-lote1" or an.get("manifiesto_sha256") != H(raw):
        falla("ANEXO_DE_COBERTURA_DE_OTRO_MANIFIESTO_O_INVALIDO")
        return None
    if set(an.get("conjuntos") or {}) != set(ml):
        falla("ANEXO_DE_COBERTURA_CON_OTROS_CONJUNTOS")
        return None
    for s, c in an["conjuntos"].items():
        listas = [c["estados"]] if c.get("independiente_de_omega") is True else list((c.get("por_omega") or {}).values())
        for est in listas:
            hs = [e["shares_sha256"] for e in est]
            if not hs or len(set(hs)) != len(hs) or [e["orden"] for e in est] != list(range(len(est))) or (c.get("independiente_de_omega") is True and c.get("n_estados") != len(est)):
                falla("ANEXO_DE_COBERTURA_INCONSISTENTE:" + s)
                return None
    # rem114 (G-E0E3): un conjunto de dominio estricto exige un anexo de VÉRTICES que se REPRODUZCA desde su definición (misma enumeración
    # estructural que el trabajador, sin bridge), con la definición del manifiesto y la condición de signo; si no, no hay cobertura.
    for s, v in ml.items():
        c = an["conjuntos"][s]
        estricto_m, estricto_a = v.get("dominio_nacional") == "estricto", c.get("tipo_dominio") == "estricto"
        if estricto_m != estricto_a:
            falla("ANEXO_Y_MANIFIESTO_DISCREPAN_EN_EL_TIPO_DE_DOMINIO:" + s)
            return None
        if not estricto_m:
            continue
        df = c.get("definicion")
        if not isinstance(df, dict) or CLX.definicion_sha256(df) != v.get("definicion_sha256") or c.get("definicion_sha256") != v.get("definicion_sha256"):
            falla("ANEXO_ESTRICTO_DE_OTRA_DEFINICION:" + s)
            return None
        try:
            cand, n, signo = CLX.vertices_estrictos(MC, df)
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as ex:
            falla("ANEXO_ESTRICTO_NO_ENUMERABLE:%s:%s" % (s, ex))
            return None
        if [x["huella"] for x in cand] != [e["shares_sha256"] for e in c["estados"]] or c.get("vertices_caja") != n or c.get("independiente_de_omega") is not True:
            falla("ANEXO_ESTRICTO_NO_REPRODUCIBLE:" + s)
            return None
        if not signo or c.get("signo_no_negativo") is not True:
            falla("ANEXO_ESTRICTO_SIN_CONDICION_DE_SIGNO:" + s)
            return None
    return an


def esperados(an, s, w):
    """Secuencia de huellas esperada para el conjunto s en el ω testigo w (independiente de ω si el anexo lo declara: solo NationalState)."""
    c = an["conjuntos"][s]
    if c.get("independiente_de_omega") is True:
        return [e["shares_sha256"] for e in c["estados"]]
    est = (c.get("por_omega") or {}).get(json.dumps({p: str(Fr(w[p])) for p in OMEGA}, sort_keys=True, separators=(",", ":")))
    return None if est is None else [e["shares_sha256"] for e in est]


def lambda_():
    ml = man["L1-LAMBDA"]
    an = anexo_cobertura(ml)
    filas = prods.get("lambda_envolvente.jsonl", [])
    claves = [(f.get("conjunto"), f.get("variante")) for f in filas]
    esperado = {(s, v) for s in ml for v in ("con", "sin")}
    if set(claves) != esperado or len(claves) != len(set(claves)):
        falla("COBERTURA_LAMBDA (faltan %s; ajenas %s; duplicadas %d)" % (sorted(esperado - set(claves)), sorted(set(claves) - esperado, key=str), len(claves) - len(set(claves))))
    for f in filas:
        if (f.get("conjunto"), f.get("variante")) not in esperado:
            continue
        k = "%s|%s" % (f["conjunto"], f["variante"])
        v = ml[f["conjunto"]]
        dom = v["dominios"]
        if f.get("pais") != v.get("pais"):
            falla("PAIS_DISTINTO:" + k)
        if f.get("estado") != "ok":
            falla("ENVOLVENTE_NO_CUBIERTA:%s:%s" % (k, f.get("estado")))
            continue
        lmax, lmin, kmin, kmax = (fr(f.get(x)) for x in ("lambda_max", "lambda_min", "K1_sobre_Q_min", "K1_sobre_Q_max"))
        if None in (lmax, lmin, kmin, kmax):
            falla("ESQUEMA_LAMBDA:" + k)
            continue
        g_lo, g_hi = dom_ext(dom["gain_share"])
        if not (lmax >= lmin > 0 and g_lo > 0):
            falla("ORDEN_O_SIGNO_LAMBDA:" + k)
            continue
        if kmin != 1 / (lmax * g_hi) or kmax != 1 / (lmin * g_lo):
            falla("IDENTIDAD_K1Q (K1/Q ≠ 1/(λ·g) con el extremo de g del manifiesto):" + k)
        fij = (v.get("variantes") or {}).get(f["variante"]) or {}
        for lado in ("max", "min"):
            w = f.get("testigo_" + lado)
            try:
                om = {p: Fr(w[p]) for p in OMEGA}
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                falla("ESQUEMA_TESTIGO:%s:%s" % (k, lado))
                continue
            if set(w) != set(OMEGA):
                falla("TESTIGO_CON_COORDENADAS_AJENAS:%s:%s" % (k, lado))
            if any(not (dom_ext(dom[p])[0] <= om[p] <= dom_ext(dom[p])[1]) for p in OMEGA):
                falla("TESTIGO_FUERA_DEL_CIERRE_DEL_DOMINIO:%s:%s" % (k, lado))
            if f.get("lambda_%s_alcanzado" % lado) is not all(en_dominio(om[p], dom[p]) for p in OMEGA):
                falla("ALCANZADO_INCOHERENTE_CON_LOS_CIERRES:%s:%s" % (k, lado))      # extremo abierto: límite no alcanzado, nunca «alcanzado»
            sube, baja = (0, 1) if lado == "max" else (1, 0)                         # λπ_max: π mínimos, a/ρ/κ máximos; λπ_min: al revés
            if any(om[p] != dom_ext(dom[p])[sube] for p in ("pi_iva", "pi_otros_productos", "pi_produccion")) or \
                    any(om[p] != dom_ext(dom[p])[baja] for p in ("a", "rho", "kappa_tilde")):
                falla("TESTIGO_NO_ES_EL_VERTICE_DEL_DOMINIO:%s:%s" % (k, lado))
            th = MC.theta_W(om["eta_w"], om["eta_H"])
            if fr(f.get("theta_W_en_" + lado)) != th:
                falla("THETA_W_DEL_TESTIGO:%s:%s" % (k, lado))
            if th != theta_extremo(dom["eta_w"], dom["eta_H"], f["variante"], lado):
                falla("THETA_W_NO_EXTREMO_EN_LA_VARIANTE:%s:%s" % (k, lado))
            if f["variante"] == "sin" and th < 0:
                falla("THETA_W_NEGATIVO_EN_VARIANTE_SIN:%s:%s" % (k, lado))
            if "testigo_lambda_" + lado in fij and fij["testigo_lambda_" + lado] != w:
                falla("TESTIGO_DISTINTO_DEL_MANIFIESTO:%s:%s" % (k, lado))
            ev = (f.get("evidencia_por_estado") or {}).get(lado)
            i = f.get("testigo_nacional_" + lado)
            esp = esperados(an, f["conjunto"], w) if an is not None else None
            rec = [e.get("shares_sha256") for e in ev] if isinstance(ev, list) and all(isinstance(e, dict) for e in ev) else None
            if an is not None and esp is None:
                falla("COBERTURA_SIN_ESTADOS_ESPERADOS_PARA_ESTE_OMEGA:%s:%s" % (k, lado))
            elif esp is not None and (rec != esp or [e.get("estado_nacional") for e in ev] != list(range(len(esp)))):
                falla("COBERTURA_NACIONAL_INEXACTA (esperados %d, recibidos %s; faltan %d, ajenos %d, duplicados %d):%s:%s"
                      % (len(esp), len(rec) if rec is not None else "?", len(set(esp) - set(rec or [])), len(set(rec or []) - set(esp)),
                         len(rec or []) - len(set(rec or [])), k, lado))
            if not ev or not all(e.get("admisible") is True for e in ev) or [e.get("estado_nacional") for e in ev] != list(range(len(ev))):
                falla("EVIDENCIA_DE_ADMISIBILIDAD:%s:%s" % (k, lado))
            elif not (isinstance(i, int) and not isinstance(i, bool) and 0 <= i < len(ev)) or fr(ev[i].get("lambda")) != (lmax if lado == "max" else lmin):
                falla("TESTIGO_NACIONAL:%s:%s" % (k, lado))
            elif any((fr(e.get("lambda")) > lmax) if lado == "max" else (fr(e.get("lambda")) < lmin) for e in ev):
                falla("EXTREMO_NO_ES_ENVOLVENTE_DE_LA_EVIDENCIA:%s:%s" % (k, lado))


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def exacto(a, b):
    """Igualdad EXACTA de un campo histórico: mismo tipo y misma serialización (distingue −0.0, 1 frente a 1.0 y nulos)."""
    return type(a) is type(b) and json.dumps(a) == json.dumps(b)


def estructura_nucleo(prov, st, d, td, tf):
    """Reconstrucción independiente (solo topologías) de la estructura de estencil de frontier.point_rows en el núcleo fijado."""
    h = FRV.H_DIFF

    def topo(x, y):
        try:
            return prov.evaluate(st, x, y, d).topology
        except (M.DomainError, ValueError):
            return ""
    t0, kink, disp = topo(td, tf), False, {}
    for eje, t in (("d", td), ("f", tf)):
        a, b = ((td - h, tf), (td + h, tf)) if eje == "d" else ((td, tf - h), (td, tf + h))
        if t - h >= 0.0:
            disp[eje] = topo(*a) == t0 and topo(*b) == t0
            kink = kink or not disp[eje]
        else:
            disp[eje] = topo(*b) == t0
    return t0, kink, disp


def suplemento(fr_man, filas):
    """rem119: filas aceptadas conservadas exactamente + topología; estructura compatible; procedencia ligada (ver cabecera)."""
    sup_ids = {v["frontier_id"]: (k.split("|")[0], v) for k, v in fr_man.items() if v.get("suplemento_topologia")}
    pr = prods.get("suplemento_procedencia.jsonl")
    if not sup_ids:
        if pr is not None:
            falla("PROCEDENCIA_DE_SUPLEMENTO_SIN_SUPLEMENTO_EN_EL_MANIFIESTO")
        return
    sf = man["L1-ELAST"].get("suplemento_fuente") or {}
    p = R / str(sf.get("ruta"))
    b = p.read_bytes() if sf and p.is_file() else None
    if b is None or H(b) != sf.get("sha256"):
        falla("SUPLEMENTO_SIN_FUENTE_ACEPTADA_AUTENTICA")
        return
    acept = {}
    for y in (json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()):
        if y.get("frontier_id") in sup_ids:
            kk = (y["frontier_id"], y["point_id"], y["side"])
            if kk in acept:
                falla("SUPLEMENTO_FUENTE_CON_FILAS_DUPLICADAS:%s:%s" % kk[:2])
            acept[kk] = y
    if len(acept) != sf.get("filas"):
        falla("SUPLEMENTO_FILAS_DISTINTAS_DEL_MANIFIESTO (%d, manifiesto %s)" % (len(acept), sf.get("filas")))
    vistos, prov, estados = {}, provider_for(RunConfig()), {}
    for f in filas:
        if f.get("frontier_id") not in sup_ids:
            continue
        kk = (f.get("frontier_id"), f.get("point_id"), f.get("side"))
        vistos[kk] = vistos.get(kk, 0) + 1
        y = acept.get(kk)
        if y is None:
            falla("SUPLEMENTO_FILA_AJENA_A_LA_FUENTE:%s:%s:%s" % kk)
            continue
        if set(f) - set(y) != {"topology"} or "topology" in y:
            falla("SUPLEMENTO_ESQUEMA_DISTINTO:%s:%s:%s (añadidos %s)" % (kk + (sorted(set(f) - set(y)),)))
        dist = [c for c in y if c not in f or not exacto(f[c], y[c])]
        if dist:
            falla("SUPLEMENTO_CAMPO_HISTORICO_ALTERADO:%s:%s:%s:%s" % (kk + (dist[:4],)))
            continue
        d, v = sup_ids[kk[0]]
        if kk[0] not in estados:
            estados[kk[0]] = prov.state(_to_state_prim(v["clave_estructural"]))
        t0, kink, disp = estructura_nucleo(prov, estados[kk[0]], d, y["tau_d"], y["tau_f"])
        malas = []
        if y.get("kink_adjacent") is not kink:
            malas.append("KINK")
        if y.get("regime") != FRV.location(y["tau_d"], y["tau_f"], float(v["dominio_tau"]["tau_d_upper"]), float(v["dominio_tau"]["tau_f_upper"])):
            malas.append("REGIMEN")
        if y.get("side") == "point" and not kink:
            for eje, pares in (("d", (("eps_dd", "B_d"), ("eps_fd", "B_f"))), ("f", (("eps_df", "B_d"), ("eps_ff", "B_f")))):
                for c, bb in pares:
                    if (y.get(c) is not None) != (bool(disp[eje]) and finito(y.get(bb)) and y[bb] > 0):
                        malas.append("DERIVADA_" + c)
        if malas:
            falla("SUPLEMENTO_INCOMPATIBLE_CON_EL_NUCLEO:%s:%s:%s:%s" % (kk + (malas,)))
    if set(acept) - set(vistos):
        falla("SUPLEMENTO_FILAS_OMITIDAS (%d): %s" % (len(set(acept) - set(vistos)), sorted(set(acept) - set(vistos))[:3]))
    dup = sorted(k for k, n_ in vistos.items() if n_ > 1)
    if dup:
        falla("SUPLEMENTO_FILAS_DUPLICADAS (%d): %s" % (len(dup), dup[:3]))
    if pr is None:
        falla("SUPLEMENTO_SIN_PROCEDENCIA")
        return
    sha_fr = next((q.get("sha256") for q in res.get("productos") or [] if q.get("archivo") == "frontier_result.jsonl"), None)
    topo_prod = {(f.get("frontier_id"), f.get("point_id"), f.get("side")): f.get("topology") for f in filas if f.get("frontier_id") in sup_ids}
    claves_pr = [(q.get("frontier_id"), q.get("point_id"), q.get("side")) for q in pr]
    if sorted(claves_pr) != sorted(acept) or len(set(claves_pr)) != len(claves_pr):
        falla("SUPLEMENTO_PROCEDENCIA_NO_CUBRE_EXACTAMENTE_LA_FUENTE")
    malas = []
    for q in pr:
        kk = (q.get("frontier_id"), q.get("point_id"), q.get("side"))
        ok = (kk in acept and q.get("sha256_fila_aceptada") == H(canon(acept[kk])) and q.get("origen_numerico") == "LOTE1_ACEPTADO"
              and q.get("fuente_ruta") == sf.get("ruta") and q.get("fuente_sha256") == sf.get("sha256") and q.get("instalacion_identidad") == NUCLEO_IDENTIDAD
              and q.get("frontier_result_sha256") == sha_fr and q.get("topology") == topo_prod.get(kk))
        if not ok:
            malas.append("%s:%s:%s" % kk)
    if malas:
        falla("SUPLEMENTO_PROCEDENCIA_INCOHERENTE (%d filas): %s" % (len(malas), malas[:3]))


def elast():
    fr_man = man["L1-ELAST"]["fronteras"]
    filas = prods.get("frontier_result.jsonl", [])
    n = RunConfig().frontier_n
    ids = {}
    for key, v in fr_man.items():
        ids[v["frontier_id"]] = (key.split("|")[1], v)
    ajenas = sorted({str(f.get("frontier_id")) for f in filas} - set(ids))
    if ajenas:
        falla("FRONTERAS_AJENAS:%s" % ajenas[:3])
    if man["L1-ELAST"].get("topologia_requerida") is True:           # rem113: E4 exige la topología de adopción de cada fila
        sin = [f.get("frontier_id") for f in filas if not (isinstance(f.get("topology"), str) and f["topology"])]
        if sin:
            falla("TOPOLOGIA_AUSENTE:%s" % sorted(set(map(str, sin)))[:3])
        # rem114 (P4-LOTE2-TOPOLOGIA): la topología de CADA fila (punto y laterales) debe ser la que el NÚCLEO asigna a ESA clave estructural,
        # diseño y punto de tasas: proveedor.evaluate(estado, τ_d, τ_f, diseño).topology (frontier.point_rows la copia a las filas laterales
        # del mismo punto; una evaluación fallida no tiene topología, ""). No basta una cadena no vacía ni un catálogo de etiquetas.
        prov, estados, malas = provider_for(RunConfig()), {}, []
        for key, v in fr_man.items():
            estados[v["frontier_id"]] = (key.split("|")[0], prov.state(_to_state_prim(v["clave_estructural"])))
        for f in filas:
            if f.get("frontier_id") not in estados or not finito(f.get("tau_d")) or not finito(f.get("tau_f")):
                continue
            d, st = estados[f["frontier_id"]]
            try:
                esperada = prov.evaluate(st, f["tau_d"], f["tau_f"], d).topology
            except (M.DomainError, ValueError):
                esperada = ""
            if f.get("topology") != esperada:
                malas.append("%s:%s:%s" % (f["frontier_id"], f.get("point_id"), f.get("side")))
        if malas:
            falla("TOPOLOGIA_DISTINTA_DE_LA_DEL_NUCLEO (%d filas): %s" % (len(malas), malas[:3]))
    suplemento(fr_man, filas)
    total = 0
    for fid, (j, v) in ids.items():
        bd, bf = float(v["dominio_tau"]["tau_d_upper"]), float(v["dominio_tau"]["tau_f_upper"])
        (dl, dh), (fl, fh) = axes(j, bd, bf)
        dn, fn = (nodes(dl, dh, n) if dh > dl else [dl]), (nodes(fl, fh, n) if fh > fl else [fl])
        esperados = {(dn[a], fn[b]): "P%04d_%04d" % (a, b) for a in range(len(dn)) for b in range(len(fn))}
        total += len(esperados)
        if "puntos_frontier_n4" in v and v["puntos_frontier_n4"] != len(esperados):
            falla("MANIFIESTO_PUNTOS_DISTINTOS_DE_LA_MALLA:" + fid)
        puntos = {}
        for f in filas:
            if f.get("frontier_id") == fid:
                puntos.setdefault((f.get("tau_d"), f.get("tau_f")), []).append(f)
        if set(puntos) != set(esperados):
            falla("COBERTURA_FRONTERA:%s (faltan %d, ajenos %d)" % (fid, len(set(esperados) - set(puntos)), len(set(puntos) - set(esperados))))
        phi = float(v["clave_estructural"]["phi"])
        for pt, rows in puntos.items():
            if pt not in esperados:
                continue
            pid0 = "%s:%s" % (fid, esperados[pt])
            if any(set(CAMPOS_FRONTERA) - set(r) for r in rows):
                falla("ESQUEMA_FRONTERA:" + pid0)
                continue
            if any(r["point_id"] != esperados[pt] for r in rows):
                falla("POINT_ID_DISTINTO_DE_LA_MALLA:" + pid0)
            pr = [r for r in rows if r["side"] == "point"]
            if len(pr) != 1:
                falla("FILA_POINT_NO_UNICA:" + pid0)
                continue
            kink = pr[0]["kink_adjacent"] is True
            if sorted(r["side"] for r in rows) != (["left_limit", "point", "right_limit"] if kink else ["point"]):
                falla("LADOS_INCOMPATIBLES_CON_EL_CONTRATO:%s:%s" % (pid0, sorted(str(r["side"]) for r in rows)))
            for r in rows:
                pid = "%s:%s" % (pid0, r["side"])
                if r["computation_status"] != "complete":
                    falla("CALCULO_FALLIDO:" + pid)
                    continue
                if not all(finito(r[c]) for c in ("tau_d", "tau_f", "B_d", "B_f", "R", "B_pot", "CS")) or r["B_pot"] <= 0:
                    falla("NO_FINITO_O_AUSENTE:" + pid)
                    continue
                if r["kink_adjacent"] is not kink:
                    falla("KINK_INCOHERENTE:" + pid)
                nulas = [c for c in BASE_EPS if r[c] is None]
                for c in BASE_EPS:
                    if r[c] is not None and not finito(r[c]):
                        falla("ELASTICIDAD_NO_FINITA:%s:%s" % (pid, c))
                    elif r[c] is None and r[BASE_EPS[c]] > 0 and not (kink and r["side"] == "point"):
                        falla("ELASTICIDAD_NULA_SIN_REGLA:%s:%s" % (pid, c))
                if r["side"] == "point":
                    motivo = ("KINK_NO_DERIVATIVE" if kink else "BASE_NONPOSITIVE" if nulas and (r["B_d"] <= 0 or r["B_f"] <= 0)
                              else "SP_LIMIT_AT_ZERO_RATE" if r["tau_f"] == 0.0 else None)
                    auditoria = "limitation" if kink else "pass"
                else:
                    motivo, auditoria = "LATERAL_DERIVATIVE", "pass"
                if r["audit_status"] != auditoria or r["reason_code"] != motivo:
                    falla("AUDITORIA_O_MOTIVO_DISTINTOS_DEL_CONTRATO:%s:%s/%s" % (pid, r["audit_status"], r["reason_code"]))
                if abs(r["R"] - (r["tau_d"] * r["B_d"] + r["tau_f"] * r["B_f"])) > T1 * max(1, abs(r["R"])):
                    falla("IDENTIDAD_R:" + pid)
                if abs(r["CS"] - r["R"] / r["B_pot"]) > T1 * max(1, abs(r["CS"])):
                    falla("IDENTIDAD_CS:" + pid)
                if r["tau_f"] == 0.0:
                    if r["s_P"] is not None:
                        falla("SP_DEBE_SER_NA_EN_TASA_CERO:" + pid)
                elif not finito(r["s_P"]) or abs(r["s_P"] - M.provider_share(r["tau_f"], phi)) > T1:
                    falla("IDENTIDAD_SP:" + pid)
    if "puntos_totales_frontier_n4" in man["L1-ELAST"] and man["L1-ELAST"]["puntos_totales_frontier_n4"] != total:
        falla("MANIFIESTO_TOTAL_DE_PUNTOS_DISTINTO_DE_LA_MALLA")


def coord():
    co = man["L1-COORD"]
    techos, comp = prods.get("coord_techos.jsonl", []), prods.get("coord_comparacion.jsonl", [])
    tk = [x.get("clave_transformada_sha256") for x in techos]
    sel = set(co["claves_transformadas"])
    if set(tk) != sel or len(tk) != len(set(tk)):
        falla("TECHOS_NO_CORRESPONDEN_A_LA_SELECCION (faltan %s; ajenas %s; duplicadas %d)" % (sorted(sel - set(tk))[:3], sorted(set(map(str, tk)) - sel)[:3], len(tk) - len(set(tk))))
    if "techos_nuevos_unicos" in co and co["techos_nuevos_unicos"] != len(sel):
        falla("MANIFIESTO_TECHOS_NUEVOS_DISTINTO")
    por_clave = {x.get("clave_transformada_sha256"): x for x in techos if x.get("clave_transformada_sha256") in sel}
    for k, x in por_clave.items():
        if not {"C_2", "estado", "error", "motivo"} <= set(x):
            falla("ESQUEMA_TECHO:%s" % k)
        elif x["estado"] != "complete" or not finito(x["C_2"]) or not finito(x["error"]) or x["error"] < 0:
            falla("TECHO_INCOMPLETO_O_SIN_ERROR:%s" % k)
    reu = co.get("techos_reutilizados") or {}
    for k, r in reu.items():
        x = por_clave.get(k)
        if k not in sel or x is None or any(x.get(f) != r[f] for f in ("C_2", "estado", "error", "motivo")) or x.get("reutilizado_sha256") != r["fuente_sha256"]:
            falla("TECHO_REUTILIZADO_DISTINTO_DEL_ACEPTADO:%s" % k)
    for k, x in por_clave.items():
        if ("reutilizado_de" in x or "reutilizado_sha256" in x) and k not in reu:
            falla("TECHO_REUTILIZADO_NO_DECLARADO:%s" % k)
    cel = {c["unidad"]: c for c in co["celdas"]}
    un = [x.get("unidad") for x in comp]
    if set(un) != set(cel) or len(un) != len(set(un)):
        falla("COMPARACIONES_NO_CORRESPONDEN (faltan %s; ajenas %s; duplicadas %d)" % (sorted(set(cel) - set(un))[:3], sorted(set(map(str, un)) - set(cel))[:3], len(un) - len(set(un))))
    for x in comp:
        c = cel.get(x.get("unidad"))
        if c is None:
            continue
        u = c["unidad"]
        if x.get("cell_id") != c["cell_id"] or x.get("K1_reutilizado") != c["K1_reutilizado"] or x.get("G_padre") != c["G_padre"]:
            falla("CELDA_PADRE_DISTINTA_DEL_MANIFIESTO:" + u)
        tch = por_clave.get(c["clave_transformada_sha256"])
        if tch is None or x.get("C2_coord") != tch.get("C_2") or x.get("estado_techo") != tch.get("estado"):
            falla("TECHO_DE_OTRA_CLAVE_O_AUSENTE:" + u)
            continue
        if not finito(x.get("G_coord")) or not finito(c["K1_reutilizado"]) or abs(x["G_coord"] - (tch["C_2"] - c["K1_reutilizado"])) > T1 * max(1, abs(x["G_coord"])):
            falla("IDENTIDAD_G_COORD:" + u)


try:
    {"L1-LAMBDA": lambda_, "L1-ELAST": elast, "L1-COORD": coord}.get(t, lambda: falla("TAREA_NO_ADMITIDA:%s" % t))()
except (KeyError, TypeError, ValueError, AttributeError, ZeroDivisionError) as ex:     # esquema inválido → fallo controlado, nunca aceptación
    falla("ESQUEMA_INVALIDO:%s:%s" % (type(ex).__name__, ex))
v = {"tarea": t, "sintetico": SINT, "fallos": sorted(set(fallos))[:20], "n_fallos": len(fallos), "aceptada": not fallos,
     "dictamen": "completa_validada" if not fallos else "incompleta (no se publica como terminada)"}
salir(v, 0 if v["aceptada"] else 4)
