"""rem148 — CONCILIACIÓN POR AFIRMACIÓN Y CANAL del contraste ABL-COV (pieza nueva; aritmética sobre productos ya validados; ningún techo,
supremo, bridge ni evaluación del modelo).
Entrada: un ENSAMBLADO del conductor/ensamblador de ESTE paquete y la conciliación ENF ACEPTADA (exp8/ENF_POR_AFIRMACION.jsonl rem147, e0670acc…,
aceptada en rem148), que fija el universo de 1.728 afirmaciones, sus testigos (unidad, cell_id), K1 y el canal eta_f, que NO se recalcula.
1) Validación común: autentica ENSAMBLADO.json frente al manifiesto; para CADA tarea registrada vuelve a aplicar validar_coord_rec.validar_tarea
   (la misma de la tarea y del ensamblado) sobre los bytes de su directorio, exige los mismos sha256 de resultado y productos que registró el
   ensamblado y repite validar_ensamblado; cada producto del ensamblado se autentica por el sha256 que registró y sus filas deben ser idénticas
   a las reconstruidas (i2: comparación de contenido; i1 comparaba bytes con fin de línea LF y rechazó los productos que el ensamblador escribe
   en modo texto, CRLF en Windows). Un ensamblado no aceptado,
   una tarea incompleta, un techo null/ausente/no admisible o de otra clave no pasa nunca a completo: la conciliación se rechaza (rc 4).
2) Cotas en la escala de G (aritmética racional exacta sobre los binary64): C2 ∈ [C_2 − e_n, C_2 + e_n], con e_n = error_normalizado certificado
   de SU clave; K1 es el valor reutilizado del padre aceptado, idéntico al de ENF (K1 no depende de phi, ec. 24), con su garantía declarada
   (GARANTIA_K1: valor binary64 aceptado, sin cota adicional declarada en la fuente; si una fila declara K1_error se suma). Testigo sup:
   G_inf = C2_inf − K1 − eK1; testigo inf: G_sup = C2_sup − K1 + eK1. Sin margen 1e-4: el margen fijo no sustituye la propagación.
3) Regla §17.1 (eps = 1/100 exacto): sup G > −eps demostrado si G_inf(sup) > −eps; inf G < eps demostrado si G_sup(inf) < eps. Si el intervalo
   de un testigo cruza su umbral, queda «no_decidida_por_incertidumbre». Las 16 robustas padre: solo pueden quedar refutadas por el testigo sup
   o no decididas; nunca se declara su robustez bajo COV con testigos. Signo certificado solo si el intervalo de G excluye 0.
Modos: «produccion» (manifiesto real, ensamblado real) o «sintetico» (manifiesto …-SINTETICO; unidades SINT-); cualquier mezcla o modo
desconocido se rechaza antes de leer productos.
Escribe en exclusiva <salida> (directorio nuevo): CONCILIACION_COV.jsonl, CONCILIACION_COV.json; última línea {aceptada, dictamen, fallos}.
Uso: python -B -I -X utf8 conciliar_cov.py <raiz> <manifiesto> <modo> <ENSAMBLADO.json> <ENF_POR_AFIRMACION.jsonl> <salida>"""
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENF_SHA = "e0670acc74ac1aaf92686b4fd207c11da1aa8636833b140e40c0a08ddc30ac3c"
EPS = Fraction(1, 100)
GARANTIA_K1 = "K1_reutilizado = valor binary64 aceptado del padre (mismo que ENF y T7); sin cota numérica adicional declarada en la fuente; K1_error de la fila si existe"
MODOS = ("produccion", "sintetico")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
INC = ("cambio_de_signo_certificado", "inconclusa_por_testigos_en_tolerancia")


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False))
    raise SystemExit(rc)


def cotas_G(c2, e_n, k1, ek1=0.0):
    """Intervalo exacto de G = C2 − K1 a partir de C_2 ± e_n (normalizado) y K1 ± eK1; todo en racionales."""
    c, e, k, ek = Fraction(c2), Fraction(e_n), Fraction(k1), Fraction(ek1)
    assert e >= 0 and ek >= 0
    return c - e - k - ek, c + e - k + ek


def lado(g_lo, g_hi, umbral, sentido):
    """sup: demuestra sup G > −eps si g_lo > −eps; inf: demuestra inf G < eps si g_hi < eps. Devuelve demostrado / cruza / no."""
    if sentido == "sup":
        return "demostrado" if g_lo > -umbral else ("cruza" if g_hi > -umbral else "no")
    return "demostrado" if g_hi < umbral else ("cruza" if g_lo < umbral else "no")


def canal_phi(categoria, s, i):
    """s, i: None (testigo sin filas aceptadas), "sin_evidencia" o dict con g_lo/g_hi. Devuelve (cobertura, canal)."""
    rob = categoria == "robusta_infactible_certificada"
    falta = [n for n, t in (("sup", s), ("inf", i)) if t == "sin_evidencia"]
    if falta:
        return "incompleta", "sin_evidencia_COV_completa:" + ",".join(falta)
    ls, li = isinstance(s, dict), isinstance(i, dict)
    cob = "ambos" if ls and li else "solo_sup" if ls else "solo_inf" if li else "ninguno"
    rs = lado(s["g_lo"], s["g_hi"], EPS, "sup") if ls else None
    ri = lado(i["g_lo"], i["g_hi"], EPS, "inf") if li else None
    if rob:
        c = ("robustez_refutada_por_testigo_sup" if rs == "demostrado" else "no_decidida_por_incertidumbre" if rs == "cruza"
             else "no_decidida_por_testigos" if ls else "sin_cobertura_COV")
    elif cob == "ambos":
        c = ("inconclusa_preservada" if rs == ri == "demostrado" else "no_decidida_por_incertidumbre" if "cruza" in (rs, ri)
             else "no_decidida_por_testigos")
    elif cob == "solo_sup":
        c = "parcial_no_robusta_infactible" if rs == "demostrado" else "no_decidida_por_incertidumbre" if rs == "cruza" else "no_decidida_por_testigos"
    elif cob == "solo_inf":
        c = "parcial_no_robusta_factible" if ri == "demostrado" else "no_decidida_por_incertidumbre" if ri == "cruza" else "no_decidida_por_testigos"
    else:
        c = "sin_cobertura_COV"
    return cob, c


def signo(g_lo, g_hi):
    return 1 if g_lo > 0 else -1 if g_hi < 0 else 0


def validar_entrada(R, raw, modo, ens_p):
    """Validación común sobre los bytes autenticados del ensamblado; devuelve (fallos, techos_por_clave, filas_por_celda)."""
    sys.path.insert(0, str(AQUI))
    import validar_coord_rec as VC  # noqa: E402
    man = json.loads(raw)
    co = man.get("ABL-COV") or {}
    sint = str(man.get("kind", "")).endswith("-SINTETICO")
    if modo not in MODOS:
        return ["MODO_DESCONOCIDO:%s" % modo], {}, {}
    if (modo == "sintetico") != sint:
        return ["MODO_Y_MANIFIESTO_INCOMPATIBLES"], {}, {}
    eb = Path(ens_p).read_bytes() if Path(ens_p).is_file() else b"{}"
    ens = json.loads(eb)
    D = Path(ens_p).parent
    f = [m for c, m in ((ens.get("manifiesto_sha256") == H(raw), "ENSAMBLADO_DE_OTRO_MANIFIESTO"), (ens.get("sintetico") is sint, "ENSAMBLADO_SINTETICO_REAL_MEZCLADO"),
                        (ens.get("aceptada") is True and ens.get("dictamen") == "completa_validada", "ENSAMBLADO_NO_ACEPTADO"),
                        (set(ens.get("tareas") or {}) == set(co.get("tareas") or {}), "ENSAMBLADO_SIN_TODAS_LAS_TAREAS")) if not c]
    if f:
        return f, {}, {}
    techos = []
    for t, o in sorted(ens["tareas"].items()):
        d = Path(o["directorio"])
        v = VC.validar_tarea(raw, d / "resultado.json", d / "salida")
        if not v["aceptada"] or v["tarea"] != t:
            f.append("TAREA_NO_VALIDA_EN_LA_CONCILIACION:%s:%s" % (t, (v["fallos"] or v["incompletos"])[:2]))
        if v["resultado_sha256"] != o.get("resultado_sha256") or v["productos_sha256"] != o.get("productos"):
            f.append("BYTES_DE_TAREA_DISTINTOS_DE_LOS_ENSAMBLADOS:%s" % t)
        if (v["modo"] == "sintetico") != sint:
            f.append("MODO_DE_TAREA_MEZCLADO:%s" % t)
        techos += v["techos"]
    e, filas = VC.validar_ensamblado(R, co, techos)
    f += e["fallos"]
    if e["dictamen"] != "completa_validada" or e.get("con_techo_incompleto"):
        f.append("ENSAMBLADO_REVALIDADO_NO_COMPLETO:%s" % e["dictamen"])
    for nombre, cont in (("cov_techos_ensamblados.jsonl", techos), ("cov_comparacion_ensamblada.jsonl", filas)):
        disco = (D / nombre).read_bytes() if (D / nombre).is_file() else None
        leidas = [json.loads(x) for x in disco.decode("utf-8").splitlines() if x.strip()] if disco is not None else None
        if disco is None or (ens.get("productos") or {}).get(nombre) != H(disco) or leidas != json.loads(json.dumps(cont)):
            f.append("PRODUCTO_DEL_ENSAMBLADO_DISTINTO_DE_LO_REVALIDADO:%s" % nombre)
    por_clave = {}
    for t in techos:
        k = t["clave_transformada_sha256"]
        if k in por_clave:
            f.append("TECHO_DUPLICADO:%s" % k)
        por_clave[k] = t
    por_celda = {}
    for x in filas:
        por_celda.setdefault((x["unidad"], x["cell_id"]), []).append(x)
    return f, por_clave, por_celda


def evidencia(w, pref, por_clave, por_celda, fallos):
    """Cotas COV de un testigo enlazado; None si el testigo no tiene filas aceptadas (fuera de la descomposición)."""
    if not w.get("enlazado"):
        return None
    xs = por_celda.get((pref + w["unidad"], w["cell_id"])) or []
    if len(xs) != 1:
        return "sin_evidencia"
    x = xs[0]
    t = por_clave.get(x.get("clave_transformada_sha256"))
    if (t is None or t.get("estado") != "complete" or x.get("estado_techo") != "complete" or t.get("error_kind") != "certified_bound"
            or not isinstance(t.get("error_normalizado"), float) or t.get("C_2") is None or x.get("C2_coord") != t["C_2"]):
        return "sin_evidencia"
    if x.get("K1_reutilizado") != w["K1_reutilizado"]:
        fallos.append("K1_DISTINTO_DEL_ACEPTADO:%s" % w["cell_id"])
        return "sin_evidencia"
    lo, hi = cotas_G(t["C_2"], t["error_normalizado"], w["K1_reutilizado"], x.get("K1_error") or 0.0)
    return {"unidad": w["unidad"], "cell_id": w["cell_id"], "clave_cov": t["clave_transformada_sha256"], "C2_cov": t["C_2"], "error_normalizado": t["error_normalizado"],
            "error_R": t.get("error_R"), "K1": w["K1_reutilizado"], "g_lo": lo, "g_hi": hi, "G_padre": w["G_padre_ENF"], "signo_padre": w["signo_padre"],
            "signo_cov_certificado": signo(lo, hi)}


def main(R, man_p, modo, ens_p, enf_p, sal):
    R, sal = Path(R), Path(sal)
    raw = Path(man_p).read_bytes()
    eb = Path(enf_p).read_bytes()
    if H(eb) != ENF_SHA:
        salir({"aceptada": False, "dictamen": "rechazada", "fallos": ["CONCILIACION_ENF_NO_AUTENTICA"]}, 4)
    fallos, por_clave, por_celda = validar_entrada(R, raw, modo, ens_p)
    if fallos:
        salir({"aceptada": False, "dictamen": "rechazada", "fallos": fallos[:8]}, 4)
    pref = "SINT-" if modo == "sintetico" else ""
    enf = [json.loads(x) for x in eb.decode("utf-8").splitlines() if x.strip()]
    filas = []
    for a in enf:
        s, i = (evidencia(a[l], pref, por_clave, por_celda, fallos) for l in ("sup", "inf"))
        cob, c = canal_phi(a["categoria_original"], s, i)
        fx = lambda t: ({k: (str(v) if isinstance(v, Fraction) else v) for k, v in t.items()} | {"g_lo_float": float(t["g_lo"]), "g_hi_float": float(t["g_hi"])}  # noqa: E731
                        if isinstance(t, dict) else t)
        filas.append({"afirmacion": a["afirmacion"], "categoria_original": a["categoria_original"], "pais": a["pais"], "inconclusa": a["categoria_original"] in INC,
                      "canal_eta_f_aceptado": a["canal_eta_f"], "cobertura_COV": cob, "canal_phi": c, "sup": fx(s), "inf": fx(i),
                      "cambio_de_signo_certificado_COV": [n for n, t in (("sup", s), ("inf", i)) if isinstance(t, dict) and t["signo_cov_certificado"] not in (0, t["signo_padre"])]})
    if fallos:
        salir({"aceptada": False, "dictamen": "rechazada", "fallos": fallos[:8]}, 4)
    inc = [x for x in filas if x["inconclusa"]]
    rob = [x for x in filas if x["categoria_original"] == "robusta_infactible_certificada"]
    resumen = {"kind": "conciliacion-cov-por-afirmacion-rem148", "modo": modo, "sintetico": modo == "sintetico", "manifiesto_sha256": H(raw),
               "ensamblado_sha256": H(Path(ens_p).read_bytes()), "enf_por_afirmacion_sha256": ENF_SHA, "eps": "1/100", "garantia_K1": GARANTIA_K1,
               "regla": "testigo sup: C2_inf − K1 − eK1 > −eps; testigo inf: C2_sup − K1 + eK1 < eps; cruce del umbral = no decidida; sin margen 1e-4",
               "universo": len(filas), "inconclusas": len(inc), "robustas": len(rob),
               "canal_phi": dict(Counter(x["canal_phi"] for x in filas)), "canal_phi_inconclusas": dict(Counter(x["canal_phi"] for x in inc)),
               "canal_phi_robustas": dict(Counter(x["canal_phi"] for x in rob)),
               "cruce_eta_f_phi": dict(Counter("%s | %s" % (x["canal_eta_f_aceptado"], x["canal_phi"]) for x in filas)),
               "por_pais": {p: dict(Counter(x["canal_phi"] for x in filas if (x["pais"] or "-") == p)) for p in sorted({x["pais"] or "-" for x in filas})},
               "cambios_de_signo_certificados": sum(len(x["cambio_de_signo_certificado_COV"]) for x in filas),
               "nota": "contraste finito del modelo (phi/2, resto fijo); no causalidad, no canal dominante, no ordenación frente a eta_f/2"}
    sal.mkdir()
    with (sal / "CONCILIACION_COV.jsonl").open("x", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in filas))
    resumen["producto_sha256"] = H((sal / "CONCILIACION_COV.jsonl").read_bytes())
    with (sal / "CONCILIACION_COV.json").open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(resumen, ensure_ascii=False, indent=1) + "\n")
    salir({"aceptada": True, "dictamen": "conciliada", "fallos": [], "universo": len(filas), "canal_phi": resumen["canal_phi"]}, 0)


if __name__ == "__main__":
    if len(sys.argv) != 7:
        salir({"aceptada": False, "dictamen": "rechazada", "fallos": ["USO"]}, 3)
    main(*sys.argv[1:7])
