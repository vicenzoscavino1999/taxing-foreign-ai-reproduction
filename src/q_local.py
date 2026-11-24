"""Aritmética de Q local (FAM12, F12-QLOCAL): G(m) = C_2 − m·K1 en racionales exactos sobre posiciones guardadas.

Funciones copiadas sin cambios de comun_q.py (rem157, a63cb2a7…, el que usó la producción rem158): cotas, lado_m, afirmaciones,
evaluar y contar, con sus constantes VERSIONES, ORIGENES_PADRE, CONTADOR, CONJUNTOS_CONTEO y REGIONES. La regla (lado, canal_phi,
signo, EPS = 1/100) la aporta el conciliador COV i5 aceptado (src/conciliar_cov.py, fef92f1c…), que se pasa como G.
No se copian las partes del arnés histórico: fuentes con rutas privadas, puerta nativa, bloqueo de importaciones y validación de
tareas. Este módulo solo usa la biblioteca estándar y no importa el modelo, K1, bridge, GridCell.Q ni supremos.

Adaptación de interfaz (no de fórmula): diferencias_entre_versiones y categorias_intactas reproducen las dos comprobaciones de
conciliar_q.py (rem157) sobre las afirmaciones regeneradas."""
from fractions import Fraction

VERSIONES = ("contrato", "conservadora")
CONTADOR = {"evaluar": 0}     # derivaciones Q realizadas en este proceso (los ensayos comprueban 0 tras un rechazo de la puerta)
ORIGENES_PADRE = ("filas_padre_aceptadas", "suplemento_P7_lado_padre_faltante")


def cotas(f, m, version="contrato"):
    """Intervalo exacto de G(m) = C_2 − m·K1 para la posición f."""
    m = Fraction(m)
    assert 0 <= m <= 1, "M_FUERA_DE_DOMINIO"
    k = Fraction(f["K1"])
    assert k > 0, "K1_NO_POSITIVO"
    e = Fraction(f["e_C2"]) if (version == "contrato" or f.get("e_G") is None) else Fraction(f["e_G"])
    assert version in VERSIONES and e >= 0, "VERSION_O_ERROR_INVALIDO"
    c = Fraction(f["C_2"])
    return c - e - m * k, c + e - m * k


def lado_m(f, m, version, G):
    lo, hi = cotas(f, m, version)
    return lo, hi, G.lado(lo, hi, G.EPS, f["lado"])


def afirmaciones(filas):
    af = {}
    for f in filas:
        af.setdefault(f["afirmacion"], {})[f["lado"]] = f
    return af


def evaluar(filas, m, version, G):
    """Filas de producto Q (una por posición) y una por afirmación, para un m racional y una versión de cotas. Solo aritmética."""
    m = Fraction(m)
    CONTADOR["evaluar"] += 1
    pos, porA = [], []
    for a, d in sorted(afirmaciones(filas).items()):
        lados = {}
        for lado in ("sup", "inf"):
            f = d.get(lado)
            if f is None or f.get("cobertura") == "SIN_FUENTE_PADRE" or f.get("origen") not in ORIGENES_PADRE:
                lados[lado] = "sin_evidencia"
                continue
            lo, hi, ld = lado_m(f, m, version, G)
            pos.append({"afirmacion": a, "lado": lado, "unidad": f["unidad"], "origen": f["origen"], "fuente_sha256": f["fuente"]["sha256"],
                        "clave_techo": f["clave_techo"], "m": str(m), "version": version, "g_lo": str(lo), "g_hi": str(hi), "lado_veredicto": ld,
                        "signo": G.signo(lo, hi)})
            lados[lado] = {"g_lo": lo, "g_hi": hi}
        cob, canal = G.canal_phi(d[next(iter(d))]["categoria_original"], lados["sup"], lados["inf"])
        cert = [x for x in ("sup", "inf") if isinstance(lados[x], dict) and G.lado(lados[x]["g_lo"], lados[x]["g_hi"], G.EPS, x) == "demostrado"]
        porA.append({"afirmacion": a, "categoria_original": d[next(iter(d))]["categoria_original"], "conjunto": d[next(iter(d))]["conjunto"],
                     "m": str(m), "version": version, "cobertura": cob, "canal": canal, "lados_demostrados": cert,
                     "region": "ambos" if len(cert) == 2 else "uno" if len(cert) == 1 else "ninguno"})
    return pos, porA


CONJUNTOS_CONTEO = ("inconclusa", "robusta")
REGIONES = ("ambos", "uno", "ninguno")


def contar(porA):
    out = {}
    for conj in CONJUNTOS_CONTEO:
        xs = [a for a in porA if a["conjunto"] == conj]
        out[conj] = {"afirmaciones": len(xs), "region": {r: sum(a["region"] == r for a in xs) for r in REGIONES},
                     "canal": {}}
        for a in xs:
            out[conj]["canal"][a["canal"]] = out[conj]["canal"].get(a["canal"], 0) + 1
    return out


def diferencias_entre_versiones(a_contrato, a_conservadora):
    """conciliar_q.py (rem157): afirmaciones cuyo (canal, region) difiere entre las versiones contrato y conservadora."""
    return [x["afirmacion"] for x, y in zip(a_contrato, a_conservadora) if (x["canal"], x["region"]) != (y["canal"], y["region"])]


def categorias_intactas(filas, *listas):
    """conciliar_q.py (rem157): ninguna afirmación regenerada cambia la categoría original de las posiciones de entrada."""
    cats = {x["afirmacion"]: x["categoria_original"] for x in filas}
    return all(x["categoria_original"] == cats[x["afirmacion"]] for lista in listas for x in lista)
