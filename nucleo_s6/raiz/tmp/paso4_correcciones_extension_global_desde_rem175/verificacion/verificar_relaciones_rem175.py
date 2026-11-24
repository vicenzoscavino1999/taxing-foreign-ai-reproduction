# -*- coding: utf-8 -*-
"""rem175 — VERIFICADOR v3 (copia de verificar_relaciones_rem174.py, dbd401d4…, con parches declarados en DIFERENCIAL_REM175.md):
la extensión G/N y de localización (13 relaciones rem174) se revalida desde autoridades EXTERNAS a los productos que valida (raíz de fuentes
rem175 ef581a7a…, mapa aceptado por rem118 §3, certificados rem118, conciliación E4 aceptada por L_rem122, manifiestos E4, registros de techo,
UNIVERSOS_POR_CORRIDA, RESUMEN rem132, inventarios de las 14 entregas y partes de búsqueda autenticadas). Los productos candidatos no se aceptan
por su huella ni por booleanos del constructor: se cotejan campo a campo y se reconstruye la biyección de las 391 parejas. Añade la
correspondencia exacta con la matriz candidata rem174 y la comprobación de los textos de ausencia (frases prohibidas y textos base).
Uso: verificar_relaciones_rem175.py <R> <Y> <salida_rel_a_Y> <ejecucion_rel_a_Y>
---- antes (rem173/rem174):
rem173 — VERIFICADOR v2 independiente de la traza obligación → objeto aceptado.

No importa el constructor ni copia sus funciones. Sobre los bytes finales de <salida>:
  R1 raíz: cada autoridad es un archivo review_* de W (o el diseño) fijado por los manifiestos raíz del revisor (rem172 e87f5076…,
     rem173 7f33162b…), con su rol derivado de la sección raíz, no del rol autodeclarado;
  R2 productos: cada producto se autentica por su cadena (libro/inventario/campo/texto) desde autoridades raíz;
  R3 selectores: se reevalúan filtro, clave, unidad, cardinalidad, duplicados, relación 1:1/1:N, grupos, escenario y huella de claves;
  R4 claves y textos: punteros JSON exactos y líneas exactas; ruta inexistente o valor distinto se rechaza;
  R5 garantía: clase derivada por familia de producto y por los datos seleccionados (no por palabras ni por la declaración);
  R6 autoridad aplicable: la de la obligación debe ser exactamente la que acepta sus objetos, claves, textos y decisiones;
  R7 decisiones: anclas exactas en su autoridad y obligación dentro de sus objetos; límites con decisión;
  R8 universo y estados: 76 de rem172 + altas declaradas; cambios de estado solo los declarados; pendiente_real exige revisión documentada;
  R9 enlaces: biyección con las relaciones, cantidades, huellas, escenario y clave de unión;
  R10 coherencia: resumen por estado, remanente, propuesta de cierre, tabla md y controles (32) recalculados aquí.
Después aplica el positivo, los negativos adaptados de rem172, A1–A8 y negativos nuevos, escritos en disco y releídos.
Solo biblioteca estándar. Uso: verificar_relaciones_rem173.py <R> <Y> <salida_rel_a_Y> <ejecucion_rel_a_Y>"""
import copy
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

R, Y = Path(sys.argv[1]), Path(sys.argv[2])
SAL = Y / sys.argv[3]
EJ = Y / sys.argv[4]
EJ.mkdir(parents=False, exist_ok=False)
WD = Path(r"@@W_BS1@@")
XD = R / "tmp/paso4_conciliacion_global_desde_rem172"
DISENO = R / "fase6_planes/PLAN_DISENO_v2_2_30.md"


def sha(b):
    return hashlib.sha256(b).hexdigest()


ARCH = {"matriz": SAL / "MATRIZ_PROD4_GLOBAL_REM175.json", "matriz_md": SAL / "MATRIZ_PROD4_GLOBAL_REM175.md", "enlaces": SAL / "ENLACES_RELACIONES_REM175.jsonl",
        "resumen": SAL / "RESUMEN_PROD4_GLOBAL_REM175.json", "remanente": SAL / "REMANENTE_PROD4_6_REM175.json", "remanente_md": SAL / "REMANENTE_PROD4_6_REM175.md",
        "esquema": Y / "construccion/ESQUEMA_RELACIONES_REM175.json", "constructor": Y / "construccion/construir_relaciones_rem175.py",
        "pruebas": Y / "verificacion/MATRIZ_PRUEBAS_REM175.json", "verificador": Y / "verificacion/verificar_relaciones_rem175.py"}
_E175A = json.loads(ARCH["esquema"].read_bytes())["rem175"]
ARCH.update({k: Y / v for k, v in _E175A["textos"].items()})
BY = {k: p.read_bytes() for k, p in ARCH.items()}
MAT = json.loads(BY["matriz"])
ENL = [json.loads(x) for x in BY["enlaces"].decode("utf-8").splitlines() if x.strip()]
RES = json.loads(BY["resumen"])
REM = json.loads(BY["remanente"])
ESQ = json.loads(BY["esquema"])
PRU = json.loads(BY["pruebas"])
MD = BY["matriz_md"].decode("utf-8")

# ------------------------------------------------------------------ R1 raíz
ROOTS = {"rem172": (WD / "FUENTES_CONCILIACION_GLOBAL_PROD4_6_REM172.json", "e87f50766e85456809c871126b17f5ffd10f3155ce35c33b2ac60036fac750c8"),
         "rem173": (WD / "FUENTES_CORRECCIONES_PROD4_6_REM173.json", "7f33162b3a86e36336dc4415abe0dcfcb2df1fe5116b8f667959f42179a4bbca"),
         "rem174": (WD / "FUENTES_SUPREMOS_GN_AUDITORIA_PROD4_6_REM174.json", "196b4e24750d4bb1234a71d36a672b4056487c96b7300bd23c253c0e4db9e0ea")}
EXCL = {"source_delivery", "administrative_sources", "historical_sources_not_current", "reviewer_evidence_not_scientific_acceptance", "observed", "observed_files",
        "expected", "declared_differences", "current_EXP8_products"}
PIN = {}  # nombre -> (sha, roles)


def recoge(o, sec, raiz):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in EXCL:
                continue
            if k == "accepted_ledgers" and isinstance(v, dict):
                # los libros se fijan por nombre relativo a W
                for nm, hh in v.items():
                    if isinstance(hh, str) and len(hh) == 64 and "/" not in nm and "\\" not in nm:
                        PIN.setdefault(nm, set()).add((hh, "accepted_ledgers"))
                continue
            if isinstance(v, str) and len(v) == 64 and ("\\" in k or "/" in k):
                p = Path(k.replace("\\", "/"))
                if p.parent == Path(str(WD).replace("\\", "/")) or p == Path(str(DISENO).replace("\\", "/")):
                    PIN.setdefault(p.name, set()).add((v, sec if sec else k))
            else:
                recoge(v, k if sec is None else sec, raiz)
    elif isinstance(o, list):
        for v in o:
            if isinstance(v, dict) and "path" in v and "sha256" in v:
                p = Path(v["path"].replace("\\", "/"))
                if p.parent == Path(str(WD).replace("\\", "/")) or p == Path(str(DISENO).replace("\\", "/")):
                    PIN.setdefault(p.name, set()).add((v["sha256"], sec))
            else:
                recoge(v, sec, raiz)


for rk, (rp, rh) in ROOTS.items():
    rb = rp.read_bytes()
    assert sha(rb) == rh, rk
    recoge(json.loads(rb), None, rk)


def rol_raiz(nombre):
    secs = {s for _, s in PIN.get(nombre, set())}
    if "accepted_ledgers" in secs:
        return "libro_aceptado"
    if nombre.endswith("_dictamen.txt"):
        return "dictamen_revisor"
    if nombre == DISENO.name:
        return "contrato"
    return "registro_revisor"


# rutas de las autoridades: nombre declarado en el registro de X (autenticado por el inventario sellado de rem172)
INVX = json.loads((XD / "audit/entrega.json").read_bytes())
assert sha((XD / "audit/entrega.json").read_bytes()) == "9b6a074d10d02fa9bf59b8f00a6568251b35d5cc70de9721538cfcf02dcd9805"
_mb = (XD / "fuentes/MANIFIESTO_CONCILIACION_GLOBAL.json").read_bytes()
assert sha(_mb) == INVX["files"]["fuentes/MANIFIESTO_CONCILIACION_GLOBAL.json"]["sha256"]
MANX = json.loads(_mb)["fuentes"]
_xb = (XD / "conciliacion/MATRIZ_PROD4_GLOBAL.json").read_bytes()
assert sha(_xb) == INVX["files"]["conciliacion/MATRIZ_PROD4_GLOBAL.json"]["sha256"]
XOBS = {o["id"]: o for o in json.loads(_xb)["obligaciones"]}
_rb = (XD / "conciliacion/RESUMEN_PROD4_GLOBAL.json").read_bytes()
assert sha(_rb) == INVX["files"]["conciliacion/RESUMEN_PROD4_GLOBAL.json"]["sha256"]
XCTL = json.loads(_rb)["controles_encargo_4"]
assert len(XCTL) == 32

AUTB0, AUTJ0, AUTL0, AUTINFO = {}, {}, {}, {}
for a in ESQ["autoridades"]:
    p = Path(MANX[a]["ruta"])
    b = p.read_bytes()
    pins = {h for h, _ in PIN.get(p.name, set())}
    AUTINFO[a] = {"nombre": p.name, "sha256": sha(b), "fijada_en_raiz": sha(b) in pins, "rol_raiz": rol_raiz(p.name) if pins else None}
    AUTB0[a] = b
    AUTL0[a] = b.decode("utf-8").splitlines()
    if p.name.endswith(".json"):
        AUTJ0[a] = json.loads(b)
E174 = ESQ["rem174"]
for a, d in E174["autoridades_nuevas"].items():
    p = WD / d["nombre"]
    b = p.read_bytes()
    pins = {h for h, _ in PIN.get(p.name, set())}
    AUTINFO[a] = {"nombre": p.name, "sha256": sha(b), "fijada_en_raiz": sha(b) in pins, "rol_raiz": rol_raiz(p.name) if pins else None}
    AUTB0[a] = b
    AUTL0[a] = b.decode("utf-8").splitlines()


def ptr(o, p):
    if p in ("", "/"):
        return o
    for s in p.split("/")[1:]:
        s = s.replace("~1", "/").replace("~0", "~")
        if isinstance(o, list) and s.startswith("[id=") and s.endswith("]"):
            m = [e for e in o if isinstance(e, dict) and e.get("id") == s[4:-1]]
            if len(m) != 1:
                raise LookupError(p)
            o = m[0]
        elif isinstance(o, list):
            if not s.isdigit() or int(s) >= len(o):
                raise LookupError(p)
            o = o[int(s)]
        elif isinstance(o, dict) and s in o:
            o = o[s]
        else:
            raise LookupError(p)
    return o


# ------------------------------------------------------------------ R2 productos (bytes; la cadena se evalúa dentro de evaluar())
PRB0 = {}
for pid, d in ESQ["productos"].items():
    rp = MANX[d["x"]]["ruta"] if "x" in d else str(R / d["ruta"])
    PRB0[pid] = Path(rp).read_bytes()


def campo(r, path):
    o = r
    for k in path.split("."):
        if isinstance(o, dict) and k in o:
            o = o[k]
        else:
            return ("<AUSENTE>",)
    return o


def ausente(v):
    return v == ("<AUSENTE>",) or v is None


class Ctx:
    def __init__(s, prb, autb):
        s.prb, s.autb = prb, autb
        s.autj = {a: (json.loads(b) if AUTINFO[a]["nombre"].endswith(".json") else None) for a, b in autb.items()}
        s.autl = {a: b.decode("utf-8").splitlines() for a, b in autb.items()}
        s.pj = {p: json.loads(b) for p, b in prb.items() if ESQ["productos"][p]["formato"] == "json"}
        s.rows = {}
        s.selv = {}
        s.acep = {}
        s.fallo_cadena = {}

    def cadena(s, pid, pila=()):
        if pid in s.acep:
            return s.acep[pid]
        d = ESQ["productos"][pid]
        h = sha(s.prb[pid])
        aut, ok = set(), True
        for st in d["cadena"]:
            try:
                if st["t"] == "libro":
                    v = ptr(s.autj[st["aut"]], st["ptr"])
                    ok &= (v == h) or (isinstance(v, dict) and v.get("sha256") == h)
                    aut.add(st["aut"])
                elif st["t"] in ("inventario", "inventario_texto"):
                    ib = (R / st["inv"]).read_bytes()
                    if st["t"] == "inventario":
                        ok &= ptr(s.autj[st["aut"]], st["ptr"]) == sha(ib)
                    else:
                        ok &= sha(ib) in s.autl[st["aut"]][st["linea"] - 1]
                    ok &= json.loads(ib)["files"][st["miembro"]]["sha256"] == h
                    aut.add(st["aut"])
                elif st["t"] == "campo":
                    if st["desde"] in pila:
                        ok = False
                        continue
                    aut |= s.cadena(st["desde"], pila + (pid,))
                    ok &= ptr(s.pj[st["desde"]], st["ptr"]) == h and not s.fallo_cadena.get(st["desde"])
                elif st["t"] == "texto":
                    aut |= s.cadena(st["desde"], pila + (pid,))
                    ok &= h in s.prb[st["desde"]].decode("utf-8").splitlines()[st["linea"] - 1] and not s.fallo_cadena.get(st["desde"])
                else:
                    ok = False
            except (LookupError, KeyError, IndexError, ValueError):
                ok = False
        s.fallo_cadena[pid] = not ok
        s.acep[pid] = aut
        return aut

    def filas(s, pid, fp):
        k = (pid, fp)
        if k not in s.rows:
            fmt = ESQ["productos"][pid]["formato"]
            b = s.prb[pid]
            if fmt == "jsonl":
                s.rows[k] = [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]
            elif fmt == "csv":
                s.rows[k] = [dict(x) for x in csv.DictReader(io.StringIO(b.decode("utf-8")))]
            else:
                o = ptr(s.pj[pid], fp or "")
                if isinstance(o, list):
                    s.rows[k] = o
                elif isinstance(o, dict) and fp and fp.split("/")[-1] == "fronteras":
                    s.rows[k] = [o[x] for x in o]
                else:
                    s.rows[k] = [o]
        return s.rows[k]

    def sel(s, d):
        """Evalúa la declaración d de una relación (filtro/clave/…) sobre los bytes; devuelve hechos derivados."""
        key = json.dumps(d, sort_keys=True, ensure_ascii=False)
        if key in s.selv:
            return s.selv[key]
        rows = s.filas(d["producto"], d.get("filas_puntero"))

        def k_of(r):
            if d["clave"] == ["*"]:
                return [json.dumps(r, sort_keys=True, ensure_ascii=False)]
            return [None if ausente(campo(r, c)) else campo(r, c) for c in d["clave"]]

        keep = []
        for r in rows:
            ok = True
            for f in d.get("filtro") or []:
                if f[0] == "eq":
                    ok = campo(r, f[1]) == f[2]
                elif f[0] == "en":
                    ok = campo(r, f[1]) in f[2]
                elif f[0] == "ne_campos":
                    ok = campo(r, f[1]) != campo(r, f[2])
                elif f[0] == "nulo":
                    ok = ausente(campo(r, f[1]))
                elif f[0] == "no_nulo":
                    ok = not ausente(campo(r, f[1]))
                elif f[0] == "no_vacio":
                    ok = isinstance(campo(r, f[1]), list) and bool(campo(r, f[1]))
                elif f[0] == "algun_lo_negativo":
                    v = campo(r, f[1])
                    ok = isinstance(v, list) and any(Fraction(x["lo"]) < 0 for x in v)
                elif f[0] in ("en_claves_de", "no_en_claves_de"):
                    ref = dict(ESQ["selectores"][f[1]])
                    ref = {"producto": ref["p"], "filas_puntero": ref.get("filas"), "filtro": ref.get("filtro", []), "clave": ref["clave"]}
                    ks = s.sel(ref)["_claves"]
                    ok = (json.dumps(k_of(r), ensure_ascii=False) in ks) == (f[0] == "en_claves_de")
                else:
                    raise ValueError("filtro desconocido " + str(f))
                if not ok:
                    break
            if ok:
                keep.append(r)
        ks = [json.dumps(k_of(r), ensure_ascii=False) for r in keep]
        if d.get("expandir"):
            us = [json.dumps(json.loads(k) + [i], ensure_ascii=False) for r, k in zip(keep, ks) for i in range(len(campo(r, d["expandir"])))]
            card, hu = len(us), sha("\n".join(sorted(us)).encode())
        else:
            uniq = sorted(set(ks))
            card, hu = len(uniq), sha("\n".join(uniq).encode())
        esc = None
        if d.get("escenario_campo"):
            e = sorted({campo(r, d["escenario_campo"]) for r in keep})
            esc = e[0] if len(e) == 1 else ("<MEZCLA>" if e else None)
        out = {"_claves": set(ks), "_filas": keep, "filas": len(keep), "cardinalidad": card, "duplicados": len(ks) - len(set(ks)), "huella": hu, "escenario_derivado": esc}
        s.selv[key] = out
        return out


# ------------------------------------------------------------------ R5 clase de garantía derivada por familia (independiente)
G_ENF = "techos certified_bound; K1 reutilizado (binary64)"
G_COV = "techos certified_bound, escala normalizada (error <= 1e-7)"
G_Q_PREF = "racional exacta sobre binary64 guardados"


def niveles(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "nivel_de_evidencia":
                yield v
            yield from niveles(v)
    elif isinstance(o, list):
        for v in o:
            yield from niveles(v)


def clase_derivada(ctx, rel, hechos):
    p = rel["producto"]
    fs = hechos["_filas"]
    filtro_campos = {f[1].split(".")[0] for f in rel.get("filtro") or [] if isinstance(f[1], str)}
    if p in ("P_elast_lote2", "P_elast_lote1", "P_e4_frontier", "P_conc_e4", "P_enf_pares_puntos"):
        return "dato_puntual_malla"
    if p in ("P_lambda_lote1", "P_lambda_lote2"):
        def racional(v):
            try:
                return isinstance(v, str) and Fraction(v) is not None
            except (ValueError, ZeroDivisionError):
                return False
        return "aritmetica_exacta" if all(racional(r.get("lambda_max")) and racional(r.get("lambda_min")) for r in fs) else "?"
    if p == "P_coord_192":
        j = ctx.autj["L_rem125"]
        # los techos del lote 1 son los de rem112; su garantía original (preservada por rem125) es convergence_estimate
        try:
            rr_ = ptr(j, "/roofs_reused")
            r112 = [v for v in rr_.values() if v.get("fuente") == "rem112_coord_techos"]
            ok = bool(r112) and all(v.get("error_kind_original") == "convergence_estimate" for v in r112)
            return "estimacion_convergencia" if ok and all(r.get("estado_techo") == "complete" for r in fs) else "?"
        except LookupError:
            return "?"
    if p == "P_coord_1532":
        o = {r.get("origen_techo") for r in fs}
        return "cota_certificada_techo" if o == {"recalculado"} else "estimacion_convergencia"
    if p == "P_enf_techos_pares":
        return "cota_certificada_techo"
    if p == "P_t8_vista_C5B":
        if fs and all(not ausente(r.get("captura_c2")) for r in fs):
            return "aritmetica_exacta"
        if fs and all(r.get("tipo") == "lambda_candidato_por_demostracion" for r in fs):
            return "aritmetica_exacta"
        return "dato_puntual_malla"
    if p == "X_exp8_filas":
        if "P7" in filtro_campos:
            return "dato_puntual_malla"
        if "COV" in filtro_campos:
            if fs and all("cota_global" in list(niveles(r["COV"])) for r in fs):
                return "cota_global"
            if rel.get("expandir") == "COV.cambio_de_signo_certificado":
                return "testigo"
            return "cota_certificada_techo" if all(r["garantias"]["COV"] == G_COV for r in fs) else "?"
        if "ENF" in filtro_campos:
            return "cota_certificada_techo" if all(r["garantias"]["ENF"] == G_ENF for r in fs) else "?"
        if "Q" in filtro_campos:
            if fs and all(campo(r, "Q.versiones.contrato.canal") == "robustez_refutada_por_testigo_sup" for r in fs):
                return "testigo"
            return "aritmetica_exacta" if all(r["garantias"]["Q"].startswith(G_Q_PREF) for r in fs) else "?"
        return "?"
    if p == "X_cov12":
        return "cota_global" if fs and all(r.get("conclusion_COV_vigente") == "robust_infeasible" and isinstance(r.get("libro_B2"), dict) for r in fs) else "?"
    if p in ("P_matriz_v4", "P_t1", "P_t2", "P_phi_lote2"):
        return "evidencia_documental"
    if p in ("P_t7_anexo", "P_t7_csv"):
        return "testigo"
    if p in ("P_val_e1235", "P_val_e1i2"):
        return "validacion_sintetica"
    return "?"


# ------------------------------------------------------------------ evaluación
ESTADOS = set(ESQ["estados"])
BLOQ = set(ESQ["estados_que_bloquean_cierre"])


# ------------------------------------------------------------------ rem174: re-derivación INDEPENDIENTE de los hechos GN y §18.7
# Desde los registros de techo crudos (huella contra el inventario de su área), CONCILIACION_E4_REM121 (producto P_conc_e4 del esquema,
# cuya cadena comprueba evaluar()) y el registro §18.7. No usa los recuentos de los productos A/B salvo para compararlos.
TT = R / "tmp"
_CACHE = {}


def _bytes(p):
    k = str(p)
    if k not in _CACHE:
        _CACHE[k] = Path(p).read_bytes()
    return _CACHE[k]


def _inv(area):
    k = "INV:" + area
    if k not in _CACHE:
        b = _bytes(TT / area / "audit/entrega.json")
        _CACHE[k] = (sha(b), json.loads(b)["files"])
    return _CACHE[k]


_i3 = (TT / E174["matriz_rem173"]["area"] / "audit/entrega.json").read_bytes()
assert sha(_i3) == E174["matriz_rem173"]["inventario_sha256"]
_m3 = (TT / E174["matriz_rem173"]["area"] / E174["matriz_rem173"]["miembro"]).read_bytes()
assert sha(_m3) == json.loads(_i3)["files"][E174["matriz_rem173"]["miembro"]]["sha256"]
X3OBS = {o["id"]: o for o in json.loads(_m3)["obligaciones"]}
E175 = ESQ["rem175"]
XA = E175["productos_extension"]["area"]   # rem175: los productos candidatos de la extensión son los de rem174, leídos bajo su área
PRB174 = {k: (TT / XA / v["producto"]).read_bytes() for k, v in E174["especificacion"].items()}
PARES0 = json.loads((TT / XA / E175["productos_extension"]["pares"]).read_bytes())
REG0 = json.loads(PRB174["LOC:18_7"])
COB0 = json.loads(PRB174["GN:cobertura"])
CONC = json.loads((R / ESQ["productos"]["P_conc_e4"]["ruta"]).read_bytes())
PROHIBIDOS = {"mechanism", "where_counted", "where_not_counted", "verified_by", "status"}


def _claves(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(k)
            _claves(v, acc)
    elif isinstance(o, list):
        for v in o:
            _claves(v, acc)
    return acc


def _gn_hechos_rem174(pares, reg, cob):
    """Comprobaciones de rem174, conservadas sin cambio (las 23 G y los 2 válidos siguen ensayándolas)."""
    fl, menus, comp, vistos = [], Counter(), Counter(), set()
    for p in pares["pares"]:
        par = p.get("par")
        if par in vistos:
            fl.append(("GN_CONTRAPARTE", "par duplicado %s" % par))
        vistos.add(par)
        lados = {}
        for dz in ("G", "N"):
            s = p.get(dz)
            if not isinstance(s, dict) or not isinstance(s.get("registro"), dict):
                fl.append(("GN_CONTRAPARTE", "%s sin lado %s" % (par, dz)))
                continue
            if s.get("diseno") != dz:
                fl.append(("GN_EMPAREJAMIENTO", "%s lado %s con diseño %s" % (par, dz, s.get("diseno"))))
            rg = s["registro"]
            try:
                b = _bytes(TT / rg["ruta"])
                hi, files = _inv(rg["area"])
                rel = rg["ruta"].split("/", 1)[1]
                ok = rg["ruta"].split("/", 1)[0] == rg["area"] and sha(b) == rg["sha256"] and hi == rg["inventario_area_sha256"] and files.get(rel, {}).get("sha256") == rg["sha256"]
                doc = json.loads(b)
                c, pl = doc["contenido"]["ceiling"], doc["contenido"]["payload"]
            except (OSError, KeyError, IndexError, ValueError, TypeError):
                ok = False
            if not ok:
                fl.append(("GN_REGISTRO", "%s %s registro no autenticado" % (par, dz)))
                continue
            lados[dz] = (c, pl)
            en = s.get("escala_normalizada") or {}
            if en.get("C2") != c["C2"] or en.get("error_normalizado") != c["numerical_error"] or en.get("B_pot") != c["B_pot"]:
                fl.append(("GN_ESCALA_GARANTIA", "%s %s escala normalizada distinta del registro" % (par, dz)))
            ga = s.get("garantia") or {}
            if ga.get("clase") != "cota_certificada_techo" or ga.get("error_kind") != "certified_bound":
                fl.append(("GN_ESCALA_GARANTIA", "%s %s garantía %s/%s" % (par, dz, ga.get("clase"), ga.get("error_kind"))))
        if len(lados) != 2:
            continue
        (cg, pg), (cn, pn) = lados["G"], lados["N"]
        if pg["values"] != pn["values"] or pg["tau_domain"] != pn["tau_domain"]:
            fl.append(("GN_EMPAREJAMIENTO", "%s primitivas/dominio distintos en los registros" % par))
        sg, sn = p["G"], p["N"]
        if sg.get("menu") != sn.get("menu") or sg.get("menu") != p.get("instrumento"):
            fl.append(("GN_EMPAREJAMIENTO", "%s menú G %s N %s instrumento %s" % (par, sg.get("menu"), sn.get("menu"), p.get("instrumento"))))
        if json.dumps(sg.get("primitivas"), sort_keys=True) != json.dumps(sn.get("primitivas"), sort_keys=True) or sg.get("dominio_tau") != sn.get("dominio_tau"):
            fl.append(("GN_EMPAREJAMIENTO", "%s primitivas/dominio declarados distintos" % par))
        dif = sorted(k for k in pg["technical"] if pg["technical"][k] != pn["technical"].get(k))
        if dif != sorted(p.get("diferencias_tecnicas") or {}) or pg.get("theory_sha256") != pn.get("theory_sha256") or p.get("teoria_igual") is not True:
            fl.append(("GN_IDENTIDAD_TECNICA", "%s declaradas %s, en registros %s" % (par, sorted(p.get("diferencias_tecnicas") or {}), dif)))
        lo = lambda c_: Fraction(c_["C2"]) - Fraction(c_["numerical_error"])  # noqa: E731
        up = lambda c_: Fraction(c_["C2"]) + Fraction(c_["numerical_error"])  # noqa: E731
        if lo(cg) > up(cn):
            rs = "G_sobre_N_certificado"
        elif lo(cn) > up(cg):
            rs = "N_sobre_G_certificado"
        elif cg["C2"] == cn["C2"]:
            rs = "C2_almacenado_igual"
        else:
            rs = "solapados"
        if (p.get("comparacion_normalizada") or {}).get("resultado") != rs:
            fl.append(("GN_COMPARACION", "%s declarado %s, recalculado %s" % (par, (p.get("comparacion_normalizada") or {}).get("resultado"), rs)))
        menus[p.get("instrumento")] += 1
        comp[rs] += 1
    n391 = len(CONC["detalle"])
    ncomp = sum(menus.values())
    rs_ = cob.get("resumen") or {}
    if (rs_.get("pares_E4_conciliados") != n391 or rs_.get("pares_completos") != ncomp or rs_.get("pares_completos_por_menu") != dict(menus)
            or rs_.get("pares_un_lado", -1) + ncomp + rs_.get("pares_sin_lado", -1) != n391 or sum((rs_.get("pares_un_lado_por_menu") or {}).values()) != rs_.get("pares_un_lado")
            or rs_.get("afirmacion_universal") is not False or rs_.get("tabla_391_supremos") is not False or rs_.get("comparaciones") != dict(comp)):
        fl.append(("GN_COBERTURA", "cobertura declarada distinta de la re-derivada (391=%d, completos=%d)" % (n391, ncomp)))
    cobv = {k: rs_.get(k) for k in ("pares_E4_conciliados", "pares_completos", "pares_completos_por_menu", "pares_un_lado", "pares_un_lado_por_menu", "pares_sin_lado",
                                   "afirmacion_universal", "tabla_391_supremos")}
    cobv.update({"pares_E4_conciliados": n391, "pares_completos": ncomp, "pares_completos_por_menu": dict(menus)})
    rc = reg.get("corridas") or []
    ks = _claves(rc, set()) & PROHIBIDOS
    if ks:
        fl.append(("AUD_FABRICADA", "campos de auditoría en el registro de localización: %s" % sorted(ks)))
    if "NO es la auditoría" not in (reg.get("naturaleza") or ""):
        fl.append(("AUD_FABRICADA", "naturaleza del registro"))
    nloc = sum(1 for x in rc if x.get("resultado") != "no localizado en el corpus revisado")
    if len(rc) != 14 or len({x.get("run_id") for x in rc}) != 14:
        fl.append(("AUD_LOCALIZACION", "corridas %d" % len(rc)))
    for x in rc:
        if x.get("resultado") != "no localizado en el corpus revisado" and not x.get("tablas_con_los_seis_campos_de_esta_corrida"):
            fl.append(("AUD_LOCALIZACION", "%s localizada sin tabla de los seis campos" % x.get("run_id")))
    locv = {"corridas": len(rc), "localizadas": nloc, "no_localizadas": len(rc) - nloc}
    return fl, {"pares_completos": (dict(menus), ncomp), "comparacion": (dict(comp), ncomp), "cobertura": (cobv, n391), "localizacion": (locv, len(rc))}


# ------------------------------------------------------------------ rem175: LIGADURA desde autoridades externas a los productos
# Toda fuente se autentica por su huella en la raíz de fuentes rem175 (source_files_sha256) y, si es miembro de un área, por el inventario del
# área. Los productos candidatos (pares, cobertura, registro) NO se autentican por huella: se cotejan con lo derivado aquí.
_RAIZ175 = (WD / E175["raiz_fuentes"]["nombre"]).read_bytes()
assert sha(_RAIZ175) == E175["raiz_fuentes"]["sha256"] == "ef581a7a8493e40264b6f6969f7d41c8a379529a993c18b2ba36d6a77a913952", "RAIZ_REM175"
_RAIZ175J = json.loads(_RAIZ175)
PINF = {Path(k.replace("\\", "/")).as_posix(): v for k, v in _RAIZ175J["source_files_sha256"].items()}
FIJ175 = {}
for _k, _v in _RAIZ175J["diagnostic_inputs_not_scientific_acceptance"].items():
    _q = Path(_k.replace("\\", "/"))
    FIJ175[(_q.parent.name, _q.stem)] = _v
_INVF = {}


def fijada(p):
    b = _bytes(p)
    h = PINF.get(Path(p).as_posix())
    if h is None or sha(b) != h:
        raise ValueError("FUENTE_NO_FIJADA_POR_LA_RAIZ_REM175 %s" % p)
    return b


def inv_fijado(area):
    if area not in _INVF:
        ib = fijada(TT / area / "audit/entrega.json")
        _INVF[area] = (sha(ib), json.loads(ib)["files"])
    return _INVF[area]


def miembro_fijado(area, rel):
    b = fijada(TT / area / rel)
    ih, files = inv_fijado(area)
    e = files.get(rel) or {}
    if e.get("sha256") != sha(b) or e.get("bytes") != len(b):
        raise ValueError("NO_MIEMBRO_DEL_INVENTARIO %s/%s" % (area, rel))
    return b, ih


def _clave_est(valores, dominio, j, d):
    """Identidad exacta: primitivas racionales, dominio τ con bordes, menú y diseño (nunca proximidad numérica)."""
    pv = tuple(sorted((n, str(Fraction(v))) for n, v in valores.items()))
    pd = tuple(sorted((n, v if isinstance(v, bool) else str(Fraction(v))) for n, v in dominio.items()))
    return (pv, pd, j, d)


ORIGEN_HIST = E175["ligadura_gn"]["origen_historico_declarado"]


def _ligadura_gn():
    d118 = fijada(WD / "review_20261029_rem118_dictamen.txt").decode("utf-8").splitlines()
    cert = json.loads(fijada(WD / "review_20261029_rem118_certificates.json"))
    l122 = json.loads(fijada(WD / "review_20261029_rem122_E4_aceptada.json"))
    assert not cert["failures"] and cert["units"] == 2111 and d118[31].startswith("3. CERTIFICADOS: COMPROBACIÓN INDEPENDIENTE 2.111/2.111"), "REM118_SECCION_3"
    mb, ihm = miembro_fijado("paso4_impacto_certificados_desde_rem117", "impacto/MAPA_IMPACTO_REM117.json")
    assert ihm in d118[10], "MAPA_NO_CITADO_POR_D_rem118"
    mapa = json.loads(mb)
    cb, ihc = miembro_fijado("paso4_e4_coord_desde_rem121", "conciliacion/CONCILIACION_E4_REM121.json")
    assert ihc == l122["inventory_sha256"], "CONCILIACION_NO_ACEPTADA_POR_L_rem122"
    conc = json.loads(cb)
    l2 = json.loads(miembro_fijado("paso4_lote2_cobertura_desde_rem114", "lote2/LOTE2_MANIFIESTO.json")[0])
    e4m = json.loads(miembro_fijado("paso4_lote2_cobertura_desde_rem114", "lote2/LOTE2E4_MANIFIESTO.json")[0])
    certf = {r["unit"]: r for r in cert["rows"]}
    regs, porclave, unid = {}, {}, {}
    for fila in mapa["unidades_detalle"]:
        rec = fila["certificado"]["registro"]
        cf = certf[fila["unidad"]]
        assert cf["record"] == rec and all(cf["checks"].values()) and cf["contract"] == fila["contrato"], ("ACEPTACION_REM118", fila["unidad"])
        unid.setdefault(rec, []).append({"unidad": fila["unidad"], "contrato": fila["contrato"], "entrega": fila["entrega"], "j": fila["j"], "diseno": fila["diseno"],
                                         "C2": fila["C2"], "certificado_mapa": {k: fila["certificado"][k] for k in ("error_kind", "estado", "C2", "lower", "upper",
                                                                                                                  "numerical_error", "final_n", "tau_d_testigo", "valido")},
                                         "rem118_comprobaciones": cf["checks"]})
        if rec in regs:
            continue
        area, rel = rec.split("/", 1)
        rb, iha = miembro_fijado(area, rel)
        doc = json.loads(rb)
        c, pl = doc["contenido"]["ceiling"], doc["contenido"]["payload"]
        assert doc["esquema"] == "techo-persistente-v2" and c["status"] == "complete" and c["sup"]["error_kind"] == "certified_bound", ("NO_TECHO", rec)
        k = _clave_est({x["parameter_id"]: x["value"] for x in pl["values"]}, pl["tau_domain"], pl["instrument_j"], pl["design_v"])
        regs[rec] = {"doc": doc, "sha256": sha(rb), "bytes": len(rb), "area": area, "inventario_area_sha256": iha, "clave": k}
        porclave.setdefault(k, []).append(rec)
    for rec, us in unid.items():
        c = regs[rec]["doc"]["contenido"]["ceiling"]
        for u in us:
            cm = u["certificado_mapa"]
            assert (cm["C2"], cm["numerical_error"], cm["lower"], cm["upper"], cm["final_n"], cm["estado"], cm["error_kind"]) == \
                (c["C2"], c["numerical_error"], c["sup"]["lower"], c["sup"]["upper"], c["sup"]["final_n"], c["status"], c["sup"]["error_kind"]), ("MAPA_REGISTRO", rec)
    front = {}
    for nombre, mm in (("LOTE2_MANIFIESTO", l2), ("LOTE2E4_MANIFIESTO", e4m)):
        for et, fila in mm["L1-ELAST"]["fronteras"].items():
            d_, j_ = et.split("|")[:2]
            for fid in {fila["frontier_id"], *fila.get("frontier_ids_equivalentes", [])}:
                front.setdefault(fid, (fila, d_, j_, nombre))
            org = (fila.get("origen") or {}).get("malla_de_origen")
            if org:
                od, oj, of = org.split("|", 2)
                front.setdefault(of, (fila, od, oj, nombre + " (malla_de_origen)"))
    exist = e4m["L1-ELAST"]["pares_existentes"]
    filas, completos, orden = {}, {}, []
    for par in conc["detalle"]:
        j = par["instrumento"]
        lados = {}
        for d in ("G", "N"):
            fila, dd, jj, man = front[par[d]]
            assert dd == d and jj == j, ("FRONTERA_OTRO_DISENO_O_MENU", par["par"], d)
            k = _clave_est(fila["clave_estructural"], fila["dominio_tau"], j, d)
            lados[d] = {"frontera": par[d], "manifiesto": man, "registros": list(porclave.get(k, [])), "clave": k}
        n = sum(1 for d in ("G", "N") if lados[d]["registros"])
        dup = [d for d in ("G", "N") if len(lados[d]["registros"]) > 1]
        filas[par["par"]] = {"par": par["par"], "instrumento": j, "tipo": "existente" if par["par"].startswith("existente:") else "contraparte_E4",
                             "lados": {d: {x: lados[d][x] for x in ("frontera", "manifiesto", "registros")} for d in ("G", "N")},
                             "lados_localizados": n, "lados_con_registro_duplicado": dup}
        orden.append(par["par"])
        if n == 2 and not dup:
            i = int(par["par"].split(":")[1])
            assert par["par"] == "existente:%d" % i and exist[i]["G"] == par["G"] and exist[i]["N"] == par["N"] and exist[i]["j"] == j, ("NO_EXISTENTE", par["par"])
            completos[par["par"]] = {"i": i, "j": j, "G": lados["G"], "N": lados["N"]}
    assert len(orden) == len(set(orden)), "PAREJAS_DUPLICADAS_EN_LA_CONCILIACION"
    return {"regs": regs, "porclave": porclave, "unid": unid, "filas": filas, "orden": orden, "completos": completos,
            "regla": {"regla": e4m["L1-ELAST"].get("regla"), "alternativa_sin_opcion": e4m.get("alternativa_sin_opcion")}}


AG = _ligadura_gn()


def ficha_registro(rec):
    """Lo que el registro auténtico del mapa dice de un lado (todo campo publicado sale de aquí)."""
    r = AG["regs"][rec]
    doc = r["doc"]
    c, pl = doc["contenido"]["ceiling"], doc["contenido"]["payload"]
    s = c["sup"]
    e = Fraction(c["numerical_error"])
    au = doc["identidad_corrida"]["autoridad"]
    us = AG["unid"][rec]
    return {"unidades": us, "contratos": sorted({u["contrato"] for u in us}),
            "registro": {"ruta": rec, "sha256": r["sha256"], "bytes": r["bytes"], "area": r["area"], "inventario_area_sha256": r["inventario_area_sha256"],
                         "esquema": doc["esquema"], "clave_compat": doc["clave_compat"], "contenido_sha256": doc["contenido_sha256"], "corrida_sha256": doc["corrida_sha256"]},
            "identidad_historica": {"run_class": au["run_class"], "etiqueta": au["etiqueta"], "contrato_sha256": au["contrato_sha256"], "tecnica": pl["technical"],
                                    "theory_sha256": pl["theory_sha256"], "payload_kind": pl["kind"], "origen": ORIGEN_HIST},
            "primitivas": pl["values"], "menu": pl["instrument_j"], "diseno": pl["design_v"], "dominio_tau": pl["tau_domain"], "barras": doc["contenido"]["bars"],
            "estado": c["status"], "instrumento_disponible": c["instrument_available"], "razon": c["reason"],
            "garantia": {"error_kind": s["error_kind"], "alcanzado": s["attained"], "convergido": s["converged"], "final_n": s["final_n"], "clase": "cota_certificada_techo"},
            "escala_normalizada": {"C2": c["C2"], "B_pot": c["B_pot"], "error_normalizado": c["numerical_error"], "encierro_exacto": [str(Fraction(c["C2"]) - e), str(Fraction(c["C2"]) + e)]},
            "escala_R": {"sup": s["sup"], "lower": s["lower"], "upper": s["upper"], "error_R": s["numerical_error"], "level_values": s["level_values"]},
            "testigo": {"tau_d": s["tau_d"], "tau_f": s["tau_f"], "witnesses": s["witnesses"], "n_jump_points": s["n_jump_points"],
                        "lateral": {"axis": s["lateral_axis"], "low": s["lateral_low"], "high": s["lateral_high"]}}}


def _intervalo(f_):
    return [Fraction(x) for x in f_["escala_normalizada"]["encierro_exacto"]]


def _resultado(fg, fn):
    gl, gh = _intervalo(fg)
    nl, nh = _intervalo(fn)
    return ("G_sobre_N_certificado" if gl > nh else "N_sobre_G_certificado" if nl > gh else
            "C2_almacenado_igual" if fg["escala_normalizada"]["C2"] == fn["escala_normalizada"]["C2"] else "intervalos_solapados")


def _fila_par_esperada(par):
    """Fila completa esperada de un par completo, desde la conciliación, el manifiesto y los registros del mapa."""
    cp = AG["completos"][par]
    fg, fn = ficha_registro(cp["G"]["registros"][0]), ficha_registro(cp["N"]["registros"][0])
    fg["frontera"], fn["frontera"] = cp["G"]["frontera"], cp["N"]["frontera"]
    return cp, fg, fn


def _resumen_esperado():
    filas = AG["filas"]
    comp = Counter()
    dif_ = []
    for par in AG["orden"]:
        if par in AG["completos"]:
            _, fg, fn = _fila_par_esperada(par)
            comp[_resultado(fg, fn)] += 1
            tg, tn = fg["identidad_historica"]["tecnica"], fn["identidad_historica"]["tecnica"]
            if any(tg.get(k) != tn.get(k) for k in set(tg) | set(tn)):
                dif_.append(par)
    un = Counter(filas[p]["instrumento"] for p in AG["orden"] if filas[p]["lados_localizados"] == 1)
    return {"pares_E4_conciliados": len(AG["orden"]), "pares_completos": len(AG["completos"]),
            "pares_completos_por_menu": dict(sorted(Counter(v["j"] for v in AG["completos"].values()).items())),
            "pares_un_lado": sum(1 for p in AG["orden"] if filas[p]["lados_localizados"] == 1), "pares_un_lado_por_menu": dict(sorted(un.items())),
            "pares_sin_lado": sum(1 for p in AG["orden"] if filas[p]["lados_localizados"] == 0),
            "lados_con_registro_duplicado": sum(len(filas[p]["lados_con_registro_duplicado"]) for p in AG["orden"]),
            "comparaciones": dict(sorted(comp.items())), "pares_con_diferencias_tecnicas": dif_, "registros_distintos_del_mapa": len(AG["regs"]),
            "claves_estructurales_distintas": len(AG["porclave"]), "unidades_historicas": sum(len(v) for v in AG["unid"].values()),
            "afirmacion_universal": False, "tabla_391_supremos": False}


RES_GN = _resumen_esperado()
GRUPOS_LADO = (("registro", "GN_REGISTRO"), ("unidades", "GN_UNIDADES"), ("contratos", "GN_UNIDADES"), ("identidad_historica", "GN_IDENTIDAD_HISTORICA"),
               ("primitivas", "GN_PRIMITIVAS"), ("dominio_tau", "GN_PRIMITIVAS"), ("menu", "GN_PRIMITIVAS"), ("diseno", "GN_DISENO_REGISTRO"),
               ("barras", "GN_PUBLICADO"), ("estado", "GN_PUBLICADO"), ("instrumento_disponible", "GN_PUBLICADO"), ("razon", "GN_PUBLICADO"),
               ("garantia", "GN_ESCALA_GARANTIA"), ("escala_R", "GN_PUBLICADO"), ("testigo", "GN_PUBLICADO"))


def _gn_pares(pares):
    fl = []
    filas = pares.get("pares") if isinstance(pares, dict) else None
    if not isinstance(filas, list):
        return [("GN_PARES", "producto de pares sin filas")]
    decl = Counter(p.get("par") if isinstance(p, dict) else None for p in filas)
    if set(decl) != set(AG["completos"]):
        fl.append(("GN_PARES", "pares declarados %s ≠ completos derivados %s" % (sorted(map(str, set(decl) - set(AG["completos"]))), sorted(set(AG["completos"]) - set(decl)))))
    for p in filas:
        if not isinstance(p, dict):
            fl.append(("GN_PARES", "fila no es objeto"))
            continue
        par = p.get("par")
        cp = AG["completos"].get(par)
        if cp is None:
            fl.append(("GN_PAREJA_FUENTE", "%s no es un par completo de la conciliación E4 aceptada" % par))
        else:
            if p.get("instrumento") != cp["j"] or p.get("indice_pares_existentes") != cp["i"]:
                fl.append(("GN_PAREJA_FUENTE", "%s menú/índice %s/%s ≠ %s/%s" % (par, p.get("instrumento"), p.get("indice_pares_existentes"), cp["j"], cp["i"])))
        fic = {}
        for d in ("G", "N"):
            s = p.get(d)
            if not isinstance(s, dict) or not isinstance(s.get("registro"), dict):
                continue   # ya consta como GN_CONTRAPARTE (rem174)
            rec = s["registro"].get("ruta")
            if cp is not None:
                if s.get("frontera") != cp[d]["frontera"]:
                    fl.append(("GN_PAREJA_FUENTE", "%s %s frontera %s ≠ %s (conciliación E4)" % (par, d, s.get("frontera"), cp[d]["frontera"])))
                if rec != cp[d]["registros"][0]:
                    fl.append(("GN_REGISTRO_MAPA", "%s %s registro %s ≠ el del mapa para su frontera" % (par, d, rec)))
            if rec not in AG["regs"]:
                fl.append(("GN_REGISTRO_MAPA", "%s %s registro fuera del mapa aceptado por rem118" % (par, d)))
                continue
            f_ = ficha_registro(rec)
            fic[d] = f_
            if set(s) != set(f_) | {"frontera"}:
                fl.append(("GN_PUBLICADO", "%s %s campos %s" % (par, d, sorted(set(s) ^ (set(f_) | {"frontera"})))))
            for campo_, regla in GRUPOS_LADO:
                if s.get(campo_) != f_[campo_]:
                    fl.append((regla, "%s %s %s distinto del registro" % (par, d, campo_)))
            en, ef = s.get("escala_normalizada") or {}, f_["escala_normalizada"]
            if any(en.get(k) != ef[k] for k in ("C2", "B_pot", "error_normalizado")):
                fl.append(("GN_ESCALA_GARANTIA", "%s %s escala normalizada distinta del registro" % (par, d)))
            if en.get("encierro_exacto") != ef["encierro_exacto"] or set(en) != set(ef):
                fl.append(("GN_PUBLICADO", "%s %s encierro normalizado publicado distinto del registro" % (par, d)))
            if s.get("diseno") != d or f_["diseno"] != d:
                fl.append(("GN_DISENO_REGISTRO", "%s lado %s: declarado %s, payload.design_v %s" % (par, d, s.get("diseno"), f_["diseno"])))
        if len(fic) != 2:
            continue
        if p["G"]["registro"].get("ruta") == p["N"]["registro"].get("ruta"):
            fl.append(("GN_DISENO_REGISTRO", "%s el mismo registro en ambos lados" % par))
        fg, fn = fic["G"], fic["N"]
        kg, kn = AG["regs"][fg["registro"]["ruta"]]["clave"], AG["regs"][fn["registro"]["ruta"]]["clave"]
        emp = {"primitivas_iguales": kg[0] == kn[0], "dominio_tau_igual": kg[1] == kn[1], "menu_igual": fg["menu"] == fn["menu"] == (cp or {}).get("j", p.get("instrumento")),
               "disenos": [fg["diseno"], fn["diseno"]]}
        pe = p.get("emparejamiento") or {}
        if any(pe.get(k) != v for k, v in emp.items()) or not all(emp[k] for k in ("primitivas_iguales", "dominio_tau_igual", "menu_igual")) or emp["disenos"] != ["G", "N"]:
            fl.append(("GN_EMPAREJAMIENTO", "%s emparejamiento declarado %s, desde registros %s" % (par, {k: pe.get(k) for k in emp}, emp)))
        tg, tn = fg["identidad_historica"]["tecnica"], fn["identidad_historica"]["tecnica"]
        dif = {k: {"G": tg.get(k), "N": tn.get(k)} for k in sorted(set(tg) | set(tn)) if tg.get(k) != tn.get(k)}
        if p.get("diferencias_tecnicas") != dif or p.get("teoria_igual") is not (fg["identidad_historica"]["theory_sha256"] == fn["identidad_historica"]["theory_sha256"]):
            fl.append(("GN_IDENTIDAD_TECNICA", "%s valores de diferencias técnicas o teoría distintos de los registros" % par))
        cn = p.get("comparacion_normalizada") or {}
        esp = {"G": [str(x) for x in _intervalo(fg)], "N": [str(x) for x in _intervalo(fn)], "resultado": _resultado(fg, fn),
               "c2_almacenado_igual": fg["escala_normalizada"]["C2"] == fn["escala_normalizada"]["C2"], "clase": "aritmetica_exacta"}
        if any(cn.get(k) != v for k, v in esp.items()):
            fl.append(("GN_COMPARACION", "%s comparación normalizada distinta de la derivada de los registros" % par))
        cr = p.get("comparacion_R_informativa") or {}
        if cr.get("G") != [fg["escala_R"]["lower"], fg["escala_R"]["upper"]] or cr.get("N") != [fn["escala_R"]["lower"], fn["escala_R"]["upper"]]:
            fl.append(("GN_PUBLICADO", "%s cotas R informativas distintas de los registros" % par))
    rs = pares.get("resumen") or {}
    if any(rs.get(k) != v for k, v in RES_GN.items()):
        fl.append(("GN_REPARTO" if any(rs.get(k) != RES_GN[k] for k in ("pares_un_lado_por_menu", "pares_completos_por_menu")) else "GN_COBERTURA",
                   "resumen del producto de pares distinto del derivado: %s" % sorted(k for k, v in RES_GN.items() if rs.get(k) != v)))
    return fl


def _gn_cobertura(cob):
    fl = []
    filas = cob.get("pares") if isinstance(cob, dict) else None
    if not isinstance(filas, list):
        return [("GN_BIYECCION", "cobertura sin filas")]
    cnt = Counter(f_.get("par") if isinstance(f_, dict) else None for f_ in filas)
    dups = sorted(str(k) for k, v in cnt.items() if v > 1)
    falt = sorted(set(AG["orden"]) - set(cnt))
    sob = sorted(str(k) for k in set(cnt) - set(AG["orden"]))
    if dups or falt or sob or len(filas) != len(AG["orden"]):
        fl.append(("GN_BIYECCION", "391: filas %d, duplicadas %s, omitidas %s, ajenas %s" % (len(filas), dups[:5], falt[:5], sob[:5])))
    vistas = set()
    for f_ in filas:
        if not isinstance(f_, dict) or f_.get("par") not in AG["filas"] or f_.get("par") in vistas:
            continue
        vistas.add(f_["par"])
        e = AG["filas"][f_["par"]]
        if f_ != e:
            fl.append(("GN_BIYECCION", "%s fila distinta de la derivada en %s" % (f_["par"], sorted(k for k in set(e) | set(f_) if f_.get(k) != e.get(k)))))
    # reparto recontado desde las filas declaradas (no desde su resumen)
    try:
        dl = Counter(f_["instrumento"] for f_ in filas if sum(1 for d in ("G", "N") if f_["lados"][d]["registros"]) == 1)
        dc = Counter(f_["instrumento"] for f_ in filas if sum(1 for d in ("G", "N") if f_["lados"][d]["registros"]) == 2)
        if dict(sorted(dl.items())) != RES_GN["pares_un_lado_por_menu"] or dict(sorted(dc.items())) != RES_GN["pares_completos_por_menu"]:
            fl.append(("GN_REPARTO", "reparto recontado de las filas %s/%s ≠ derivado %s/%s" % (dict(dl), dict(dc), RES_GN["pares_un_lado_por_menu"], RES_GN["pares_completos_por_menu"])))
    except (KeyError, TypeError, AttributeError) as ex:
        fl.append(("GN_BIYECCION", "filas no recontables %r" % (ex,)))
    rs = cob.get("resumen") or {}
    malos = sorted(k for k, v in RES_GN.items() if rs.get(k) != v)
    if malos:
        fl.append(("GN_REPARTO" if set(malos) & {"pares_un_lado_por_menu", "pares_completos_por_menu"} else "GN_COBERTURA", "resumen de cobertura distinto del derivado: %s" % malos))
    if cob.get("regla_contrapartes_E4") != AG["regla"]:
        fl.append(("GN_COBERTURA", "regla de contrapartes E4 distinta del manifiesto"))
    return fl


# ---- localización §18.7: corridas, inventarios, partes, corpus y adenda
LIG = E175["ligadura_localizacion"]
CAMPOS_18_7 = ["run_id", "mechanism", "where_counted", "where_not_counted", "verified_by", "status"]
TXT_EXT = (".json", ".jsonl", ".md", ".txt", ".csv")


def _ligadura_loc():
    fl = []
    res132 = json.loads(fijada(R / LIG["resumen_rem132"]))
    uni = json.loads(fijada(R / LIG["universos"]))["corridas"]
    iar = json.loads(fijada(R / LIG["input_audit_report_v4"]))["filas"]
    edu = res132["entregas_de_unidades"]
    assert res132["corridas"] == 14 and len(uni) == 14 and sorted({c["entrega"] for c in uni.values()}) == sorted(edu) and len({c["entrega"] for c in uni.values()}) == 14, "CATORCE"
    corpus, adenda = fijada(TT / XA / LIG["corpus"]), fijada(TT / XA / LIG["adenda"])
    cl = corpus.decode("utf-8").splitlines()
    qn, qc = LIG["consultas_declaradas"]["nombre"], LIG["consultas_declaradas"]["contenido"]
    l2_ = [x for x in cl if x.startswith("| C2 |")]
    l3_ = [x for x in cl if x.startswith("| C3 |")]
    assert len(l2_) == 1 and len(l3_) == 1 and all("`%s`" % q in l2_[0] for q in qn) and all("`%s`" % q in l3_[0] for q in qc), "CONSULTAS_NO_ANCLADAS_EN_EL_CORPUS"
    assert "clasificación v2" in adenda.decode("utf-8"), "ADENDA_V2"
    partes = {Path(p).name: fijada(TT / XA / p) for p in LIG["partes"]}
    runs = sorted(uni)
    dirs_todas = sorted({d.rstrip("/") for c in uni.values() for d in c["seleccion_registrada"]["directorios"]})

    def clase(rel):
        for d in dirs_todas:
            if rel == d or rel.startswith(d + "/"):
                return "resultado_celda"
        if "/almacen_techos/" in "/" + rel:
            return "almacen_techos"
        if rel.endswith(".py"):
            return "codigo"
        if not rel.lower().endswith(TXT_EXT):
            return "otro"
        if rel.startswith("demo/") and len(rel.split("/")) > 3:
            return "demo_profundo"
        return "artefacto_texto"
    der = {}
    for run in runs:
        e = uni[run]["entrega"]
        ib = fijada(TT / e / "audit/entrega.json")
        assert sha(ib) == edu[e], ("INVENTARIO_NO_ES_EL_DE_RESUMEN_REM132", e)
        files = json.loads(ib)["files"]
        cnt = {"resultado_celda": 0, "almacen_techos": 0, "codigo": 0, "artefacto_texto": 0, "otro": 0, "demo_profundo": 0}
        byt = {"codigo": 0, "artefacto_texto": 0}
        nom, leidos = [], {}
        for rel in sorted(files):
            ent = files[rel]
            q = [x for x in qn if x in rel.lower()]
            if q:
                nom.append({"ruta": rel, "sha256": ent["sha256"], "consultas": q})
            k = clase(rel)
            cnt[k] += 1
            if k in byt:
                byt[k] += int(ent["bytes"])
                leidos[rel] = (k, ent["sha256"])
        der[run] = {"entrega": e, "inventario_sha256": sha(ib), "archivos": len(files), "dirs": uni[run]["seleccion_registrada"]["directorios"],
                    "por_clase": cnt, "bytes": byt, "nombres": nom, "leidos": leidos}
    # partes: cada fila de parte se liga a su corrida auténtica; su sello acredita bytes, no identidad
    parte_run = {}
    for nm, b in partes.items():
        d = json.loads(b)
        if d.get("corpus_declarado_sha256") != sha(corpus):
            fl.append(("AUD_EVIDENCIA", "parte %s con otro corpus" % nm))
        i0, i1 = d.get("rango") or [None, None]
        if [c.get("run_id") for c in d.get("corridas", [])] != runs[i0:i1]:
            fl.append(("AUD_EVIDENCIA", "parte %s: corridas distintas de su rango %s" % (nm, d.get("rango"))))
        for c in d.get("corridas", []):
            rid = c.get("run_id")
            if rid in parte_run or rid not in der:
                fl.append(("AUD_EVIDENCIA", "parte %s: corrida %s repetida o ajena" % (nm, rid)))
                continue
            parte_run[rid] = c
            x = der[rid]
            if (c.get("entrega"), c.get("inventario_sha256"), c.get("archivos_inventario"), c.get("directorios_resultados_de_celda")) != (x["entrega"], x["inventario_sha256"], x["archivos"], x["dirs"]):
                fl.append(("AUD_EVIDENCIA", "parte %s: identidad de %s distinta de la auténtica" % (nm, rid)))
            if c.get("por_clase") != x["por_clase"] or c.get("bytes_leidos") != x["bytes"] or c.get("coincidencias_nombre") != x["nombres"]:
                fl.append(("AUD_EVIDENCIA", "parte %s: recuentos de %s distintos de su inventario" % (nm, rid)))
            for h in c.get("coincidencias_contenido_artefactos", []) + c.get("coincidencias_contenido_codigo", []):
                if h.get("ruta") not in x["leidos"] or x["leidos"][h["ruta"]][1] != h.get("sha256"):
                    fl.append(("AUD_EVIDENCIA", "parte %s: coincidencia %s fuera de lo examinado de %s" % (nm, h.get("ruta"), rid)))
            if any(x["leidos"].get(h.get("ruta"), ("",))[0] != "artefacto_texto" for h in c.get("coincidencias_contenido_artefactos", [])) or \
                    any(x["leidos"].get(h.get("ruta"), ("",))[0] != "codigo" for h in c.get("coincidencias_contenido_codigo", [])):
                fl.append(("AUD_EVIDENCIA", "parte %s: coincidencias de %s en una clase equivocada" % (nm, rid)))
            arts = {h["ruta"]: h for h in c.get("coincidencias_contenido_artefactos", []) if "ruta" in h}
            for t in c.get("tablas_con_los_seis_campos", []):
                h = arts.get(t.get("ruta"))
                if h is None or not any(all(t.get(k) == v for k, v in tt.items()) for tt in h.get("tablas_con_los_seis_campos", [])):
                    fl.append(("AUD_EVIDENCIA", "parte %s: tabla %s sin coincidencia de contenido que la sostenga" % (nm, t.get("ruta"))))
    if sorted(parte_run) != runs:
        fl.append(("AUD_EVIDENCIA", "las partes no cubren exactamente las 14 corridas"))
    gates = {}
    for f_ in iar:
        if f_["gate_id"] in ("H7", "H13"):
            gates.setdefault(f_["run_id"], {})[f_["gate_id"]] = {k: f_.get(k) for k in ("level", "decision", "clase_evidencia", "clase_evidencia_v2", "resultado_v2")}
    esp = {}
    for run in runs:
        x, c = der[run], parte_run.get(run, {})
        propias = [t for t in c.get("tablas_con_los_seis_campos", []) if run in t.get("run_ids", [])]
        esp[run] = {"run_id": run, "entrega": x["entrega"], "inventario_sha256": x["inventario_sha256"], "directorios_resultados_de_celda_excluidos": x["dirs"],
                    "examinado": {"nombres_de_archivo": x["archivos"], "artefactos_texto_leidos": x["por_clase"]["artefacto_texto"], "bytes_artefactos": x["bytes"]["artefacto_texto"],
                                  "codigo_py_leido": x["por_clase"]["codigo"], "bytes_codigo": x["bytes"]["codigo"],
                                  "solo_nombre": {k: x["por_clase"][k] for k in ("resultado_celda", "almacen_techos", "demo_profundo", "otro")}},
                    "consultas_nombre": qn, "consultas_contenido": qc, "coincidencias_nombre": x["nombres"],
                    "coincidencias_contenido_artefactos": c.get("coincidencias_contenido_artefactos"), "coincidencias_contenido_codigo": c.get("coincidencias_contenido_codigo"),
                    "copias_auditor_d8_en_la_entrega": c.get("copias_auditor_d8_en_la_entrega"), "tablas_con_los_seis_campos_de_esta_corrida": propias,
                    "filas_input_audit_report_v4": sum(1 for f_ in iar if f_["run_id"] == run), "compuertas_H7_H13_de_insumos_v4": gates.get(run, {}),
                    "resultado": "localizado en el corpus revisado" if propias else "no localizado en el corpus revisado"}
    tot = {"corridas": len(runs), "localizadas": sum(1 for r in runs if esp[r]["resultado"] != "no localizado en el corpus revisado"),
           "artefactos_texto_leidos": sum(esp[r]["examinado"]["artefactos_texto_leidos"] for r in runs), "codigo_py_leido": sum(esp[r]["examinado"]["codigo_py_leido"] for r in runs),
           "nombres_examinados": sum(esp[r]["examinado"]["nombres_de_archivo"] for r in runs),
           "coincidencias_contenido_artefactos": sum(len(esp[r]["coincidencias_contenido_artefactos"] or []) for r in runs),
           "coincidencias_contenido_codigo": sum(len(esp[r]["coincidencias_contenido_codigo"] or []) for r in runs),
           "coincidencias_nombre": sum(len(esp[r]["coincidencias_nombre"]) for r in runs), "copias_auditor_d8": sum(len(esp[r]["copias_auditor_d8_en_la_entrega"] or []) for r in runs)}
    tot["no_localizadas"] = tot["corridas"] - tot["localizadas"]
    ex = LIG["explicitos"]
    if [tot["nombres_examinados"], tot["artefactos_texto_leidos"], tot["codigo_py_leido"], tot["coincidencias_nombre"], tot["coincidencias_contenido_artefactos"], tot["coincidencias_contenido_codigo"]] != \
            [ex["nombres"], ex["textos"], ex["python"], ex["coincidencias_nombre"], ex["coincidencias_documentales"], ex["coincidencias_codigo"]]:
        fl.append(("AUD_EVIDENCIA", "recuentos derivados %s distintos de los explícitos" % tot))
    glob_ = {"corpus_declarado": {"ruta": LIG["corpus"], "sha256": sha(corpus), "adenda": LIG["adenda"], "adenda_sha256": sha(adenda), "clasificacion": LIG["clasificacion"],
                                  "directorios_resultados_de_celda_de_las_14": dirs_todas},
             "partes": {nm: sha(b) for nm, b in partes.items()},
             "objeto_buscado": {"diseno": "fase6_planes/PLAN_DISENO_v2_2_30.md §18.7 (l.2458–2460)", "campos_de_diseno": CAMPOS_18_7}}
    return {"fallos": fl, "runs": runs, "esp": esp, "tot": tot, "glob": glob_}


AL = _ligadura_loc()


def _loc_registro(reg):
    fl = []
    rc = reg.get("corridas") if isinstance(reg, dict) else None
    if not isinstance(rc, list):
        return [("AUD_CORRIDA_IDENTIDAD", "registro sin corridas")]
    ids = Counter(x.get("run_id") if isinstance(x, dict) else None for x in rc)
    if sorted(map(str, ids)) != AL["runs"] or any(v > 1 for v in ids.values()):
        fl.append(("AUD_CORRIDA_IDENTIDAD", "corridas %s ≠ UNIVERSOS_POR_CORRIDA (ajenas %s, ausentes %s)" % (len(rc), sorted(map(str, set(ids) - set(AL["runs"]))), sorted(set(AL["runs"]) - set(ids)))))
    IDENT = ("run_id", "entrega", "inventario_sha256", "directorios_resultados_de_celda_excluidos")
    for x in rc:
        if not isinstance(x, dict):
            continue
        e = AL["esp"].get(x.get("run_id"))
        if e is None:
            continue
        if any(x.get(k) != e[k] for k in IDENT):
            fl.append(("AUD_CORRIDA_IDENTIDAD", "%s identidad/entrega/inventario/directorios distintos de los auténticos" % x.get("run_id")))
        malos = sorted(k for k in e if k not in IDENT and x.get(k) != e[k])
        if malos:
            fl.append(("AUD_EVIDENCIA", "%s evidencia de búsqueda distinta de la derivada: %s" % (x.get("run_id"), malos)))
        tabs = x.get("tablas_con_los_seis_campos_de_esta_corrida") or []
        if (x.get("resultado") == "no localizado en el corpus revisado") == bool(tabs):
            fl.append(("AUD_EVIDENCIA", "%s resultado «%s» contradice sus tablas (%d)" % (x.get("run_id"), x.get("resultado"), len(tabs))))
        if x.get("resultado") not in ("no localizado en el corpus revisado", "localizado en el corpus revisado"):
            fl.append(("AUD_EVIDENCIA", "%s resultado no admitido «%s»" % (x.get("run_id"), x.get("resultado"))))
    for k, v in AL["glob"].items():
        if reg.get(k) != v:
            fl.append(("AUD_EVIDENCIA", "registro: %s distinto de lo autenticado" % k))
    if reg.get("resumen") != AL["tot"]:
        fl.append(("AUD_EVIDENCIA", "resumen del registro distinto del derivado"))
    for pth, h in (reg.get("fuentes_autenticadas") or {}).items():
        try:
            ok = sha(fijada(Path(pth))) == h
        except (OSError, ValueError):
            ok = False
        if not ok:
            fl.append(("AUD_EVIDENCIA", "fuente autenticada no fijada o distinta: %s" % Path(pth).name))
    return fl


GNV_AUT = {"pares_completos": (RES_GN["pares_completos_por_menu"], RES_GN["pares_completos"]),
           "comparacion": (RES_GN["comparaciones"], RES_GN["pares_completos"]),
           "cobertura": ({k: RES_GN[k] for k in ("pares_E4_conciliados", "pares_completos", "pares_completos_por_menu", "pares_un_lado", "pares_un_lado_por_menu",
                                                 "pares_sin_lado", "afirmacion_universal", "tabla_391_supremos")}, RES_GN["pares_E4_conciliados"]),
           "localizacion": ({"corridas": AL["tot"]["corridas"], "localizadas": AL["tot"]["localizadas"], "no_localizadas": AL["tot"]["no_localizadas"]}, AL["tot"]["corridas"])}


def gn_hechos(pares, reg, cob):
    """rem175: comprobaciones de rem174 + ligadura completa; los valores de relación salen de las autoridades (GNV_AUT), no del producto."""
    fl, _ = _gn_hechos_rem174(pares, reg, cob)
    fl = list(fl) + list(AL["fallos"])
    for fn_, arg in ((_gn_pares, pares), (_gn_cobertura, cob), (_loc_registro, reg)):
        try:
            fl += fn_(arg)
        except (KeyError, TypeError, AttributeError, ValueError, IndexError) as ex:
            fl.append(({"_gn_pares": "GN_PARES", "_gn_cobertura": "GN_BIYECCION", "_loc_registro": "AUD_EVIDENCIA"}[fn_.__name__], "no evaluable %r" % (ex,)))
    return fl, dict(GNV_AUT)


# ---- correspondencia con la matriz candidata rem174 (autenticada por el inventario X, fijado por la raíz rem175)
_m4, _ = miembro_fijado(E175["matriz_rem174"]["area"], E175["matriz_rem174"]["miembro"])
assert inv_fijado(E175["matriz_rem174"]["area"])[0] == E175["matriz_rem174"]["inventario_sha256"], "INVENTARIO_REM174"
X4OBS = {o["id"]: o for o in json.loads(_m4)["obligaciones"]}
EXT_IDS = {x for v in E174["relaciones"].values() for x in v}
TXT175 = {k: BY[k].decode("utf-8") for k in E175["textos"]}
TXT_ACT = {"t": TXT175}


def _sin_huella(rels):
    return [{k: v for k, v in r_.items() if not (r_.get("id") in EXT_IDS and k == "sha256_producto")} for r_ in rels]


GN_BASE = gn_hechos(PARES0, REG0, COB0)
GN_ACT = {"h": GN_BASE}
GN_MUT = {}


def evaluar(mat, enl, res, rem, md, prb, autb, autinfo, extra_aut=None):
    F = []

    def f(regla, det):
        F.append({"regla": regla, "detalle": det})
    gn_fl, GNV = GN_ACT["h"]
    for rg_, dt_ in gn_fl:
        f(rg_, dt_)

    ctx = Ctx(prb, autb)

    def selc(sid):
        d = ESQ["selectores"][sid]
        return ctx.sel({"producto": d["p"], "filas_puntero": d.get("filas"), "filtro": d.get("filtro", []), "clave": d["clave"], "expandir": d.get("expandir")})
    for pid in ESQ["productos"]:
        ctx.cadena(pid)
    for pid, bad in ctx.fallo_cadena.items():
        if bad:
            f("PRODUCTO_NO_AUTENTICADO", pid)
    # cada paso de cadena debe apoyarse en una autoridad con el rol que la raíz le da: libro para libro/inventario, dictamen para inventario_texto
    for pid, dd in ESQ["productos"].items():
        for st in dd["cadena"]:
            if st["t"] in ("libro", "inventario", "inventario_texto"):
                rol = (autinfo.get(st["aut"]) or {}).get("rol_raiz")
                req = "libro_aceptado" if st["t"] != "inventario_texto" else "dictamen_revisor"
                if rol != req:
                    f("CADENA_ROL", "%s paso %s en %s con rol %s (exige %s)" % (pid, st["t"], st["aut"], rol, req))
    obs = mat["obligaciones"]
    ids = [o["id"] for o in obs]
    # R8 universo
    altas = {k for k, v in ESQ["obligaciones"].items() if v.get("nueva")}
    if len(ids) != len(set(ids)):
        f("UNIVERSO", "ids duplicados %s" % [k for k, v in Counter(ids).items() if v > 1])
    if set(ids) != set(XOBS) | altas:
        f("UNIVERSO", "faltan %s sobran %s" % (sorted((set(XOBS) | altas) - set(ids)), sorted(set(ids) - set(XOBS) - altas)))
    dl = DISENO.read_bytes().decode("utf-8").splitlines()
    claves_enl = Counter(e["clave_union"] for e in enl)
    if any(v > 1 for v in claves_enl.values()):
        f("CLAVE_UNION", "claves de enlace duplicadas")
    enl_por = {}
    for e in enl:
        enl_por.setdefault((e["obligacion"], e["relacion"]), []).append(e)
    rel_vistas = set()
    for o in obs:
        i = o["id"]
        esq = ESQ["obligaciones"].get(i, {})
        if o["estado"] not in ESTADOS:
            f("ESTADO", "estado desconocido " + i)
        x = XOBS.get(i)
        esperado_estado = esq.get("estado", x["estado"] if x else None)
        if o["estado"] != esperado_estado:
            f("ESTADO_NO_JUSTIFICADO", "%s: %s (declarado/rem172: %s)" % (i, o["estado"], esperado_estado))
        if o["estado"] == "pendiente_real" and not o.get("revision_documentada"):
            f("ESTADO_PENDIENTE_REAL", i)
        c = o["cita"]
        lc = dl if c.get("documento") == "diseno" else ctx.autl.get(c.get("documento"))
        if lc is None or not isinstance(c.get("linea"), int) or not (1 <= c["linea"] <= len(lc)) or not c.get("ancla") or c["ancla"] not in lc[c["linea"] - 1]:
            f("CITA", "%s %s l.%s" % (i, c.get("documento"), c.get("linea")))
        elif "sha256" in c and c["sha256"] != (autinfo.get(c["documento"]) or {}).get("sha256"):
            f("CITA", "%s huella del documento citado" % i)
        if i == "EXP6.margen_robustez_quiebres" and o["estado"] == "satisfecho_en_alcance" and ptr(ctx.autj["L_rem105"], "/counts/PROD1/declared_D4") + ptr(ctx.autj["L_rem105"], "/counts/PROD2/declared_D4") > 0:
            f("ESTADO_NO_JUSTIFICADO", "D4 promovidas")
        rels = o.get("relaciones", [])
        rids = [r["id"] for r in rels]
        if len(rids) != len(set(rids)):
            f("RELACION_DUPLICADA", i)
        # relaciones declaradas por el esquema (cobertura exacta)
        req = {"SEL:" + s for s in esq.get("sel", [])} | {"CLV:%s:%s" % (k[0], k[1]) for k in esq.get("claves", [])} | set(E174["relaciones"].get(i, []))
        tiene = {r for r in rids if not r.startswith("TXT:")}
        if req != tiene:
            f("COBERTURA_RELACIONES", "%s faltan %s sobran %s" % (i, sorted(req - tiene), sorted(tiene - req)))
        if o["estado"] in ("satisfecho_en_alcance", "parcial_con_limite_adoptado") and not rels:
            f("COBERTURA_RELACIONES", "satisfecho sin relaciones " + i)
        aut_esp = set()
        clases = set()
        for r in rels:
            rel_vistas.add((i, r["id"]))
            if r["tipo"] == "selector":
                sid = r["id"][4:]
                d = ESQ["selectores"].get(sid)
                if d is None or r.get("producto") not in ESQ["productos"]:
                    f("PRODUCTO_NO_DECLARADO", "%s %s" % (i, r.get("producto")))
                    continue
                decl = {"producto": d["p"], "filas_puntero": d.get("filas"), "filtro": d.get("filtro", []), "clave": d["clave"], "expandir": d.get("expandir"),
                        "unidad": d["unidad"], "relacion": d["rel"]}
                for k, v in decl.items():
                    if r.get(k) != v:
                        f("SELECTOR_DISTINTO_DEL_ESQUEMA", "%s %s %s" % (i, sid, k))
                if r.get("sha256_producto") != sha(prb[r["producto"]]):
                    f("PRODUCTO_NO_AUTENTICADO", "%s huella de producto %s" % (i, r["producto"]))
                q = {"producto": r.get("producto"), "filas_puntero": r.get("filas_puntero"), "filtro": r.get("filtro") or [], "clave": r.get("clave"),
                     "expandir": r.get("expandir"), "escenario_campo": d.get("escenario_campo")}
                try:
                    hz = ctx.sel(q)
                except (LookupError, KeyError, ValueError, TypeError) as ex:
                    f("SELECTOR_NO_EVALUABLE", "%s %s %r" % (i, sid, ex))
                    continue
                if r.get("cardinalidad") != hz["cardinalidad"]:
                    f("CANTIDAD_NO_DERIVADA", "%s %s declarada %s derivada %s" % (i, sid, r.get("cardinalidad"), hz["cardinalidad"]))
                if r.get("huella_claves") != hz["huella"]:
                    f("HUELLA_CLAVES", "%s %s" % (i, sid))
                if r.get("relacion") == "1:1" and not r.get("expandir") and hz["duplicados"]:
                    f("RELACION_CARDINALIDAD", "%s %s 1:1 con %d duplicados" % (i, sid, hz["duplicados"]))
                if r.get("relacion") == "1:N" and not r.get("expandir") and hz["duplicados"] == 0 and hz["filas"] > 1:
                    f("RELACION_CARDINALIDAD", "%s %s 1:N sin agrupación" % (i, sid))
                if d.get("grupo"):
                    gr = {}
                    for rr in hz["_filas"]:
                        gr.setdefault(json.dumps([campo(rr, c) for c in d["clave"]]), []).append(campo(rr, d["grupo"]["campo"]))
                    if not all(sorted(v) == sorted(d["grupo"]["valores"]) for v in gr.values()):
                        f("RELACION_CARDINALIDAD", "%s %s grupos incompletos" % (i, sid))
                esc_d = hz["escenario_derivado"] if d.get("escenario_campo") else d.get("escenario", "padre (escenario base aceptado)")
                if r.get("escenario") != esc_d:
                    f("ESCENARIO_NO_DERIVADO", "%s %s %s != %s" % (i, sid, r.get("escenario"), esc_d))
                cl = clase_derivada(ctx, r, hz)
                if r.get("clase_garantia") != cl:
                    f("GARANTIA_NO_DERIVADA", "%s %s declarada %s derivada %s" % (i, sid, r.get("clase_garantia"), cl))
                clases.add(cl)
                aut_esp |= ctx.cadena(r["producto"])
            elif r["tipo"] == "clave":
                fu = r.get("fuente")
                try:
                    base = ctx.autj[fu] if fu in ctx.autj and ctx.autj[fu] is not None else ctx.pj[fu]
                    v = ptr(base, r.get("puntero", ""))
                    if r.get("medida") == "longitud":
                        v = len(v)
                except (LookupError, KeyError, TypeError):
                    f("CLAVE_INEXISTENTE", "%s %s %s" % (i, fu, r.get("puntero")))
                    continue
                if v != r.get("valor"):
                    f("CLAVE_DISTINTA", "%s %s %s: %r != %r" % (i, fu, r.get("puntero"), r.get("valor"), v))
                if r.get("clase_garantia") != "evidencia_documental":
                    f("GARANTIA_NO_DERIVADA", "%s clave con clase %s" % (i, r.get("clase_garantia")))
                clases.add("evidencia_documental")
                aut_esp |= ({fu} if fu in ctx.autj else ctx.cadena(fu))
            elif r["tipo"] == "texto":
                fu = r.get("fuente")
                ls = ctx.autl.get(fu)
                if ls is None or not (1 <= r.get("linea", 0) <= len(ls)) or r.get("texto", "\x00") not in ls[r["linea"] - 1]:
                    f("TEXTO_NO_ANCLADO", "%s %s l.%s" % (i, fu, r.get("linea")))
                clases.add("evidencia_documental")
                aut_esp.add(fu)
            elif r["tipo"] in ("gn", "localizacion"):
                sp = E174["especificacion"].get(r["id"])
                if sp is None or r["id"] not in E174["relaciones"].get(i, []) or sp["tipo"] != r["tipo"]:
                    f("RELACION_TIPO", "%s %s" % (i, r["id"]))
                    continue
                val_, card_ = GNV[sp["deriva"]]
                if r.get("producto") != sp["producto"] or r.get("puntero") != sp["puntero"] or r.get("sha256_producto") != sha(PRB174[r["id"]]):
                    f("GN_REGISTRO", "%s %s producto/puntero/huella" % (i, r["id"]))
                if r.get("valor") != val_:
                    f(sp["regla"], "%s %s valor %s ≠ re-derivado %s" % (i, r["id"], r.get("valor"), val_))
                if r.get("cardinalidad") != card_:
                    f("GN_ALCANCE", "%s %s cardinalidad %s ≠ %s" % (i, r["id"], r.get("cardinalidad"), card_))
                if r.get("clase_garantia") != sp["clase_garantia"]:
                    f("GN_ESCALA_GARANTIA", "%s %s clase %s" % (i, r["id"], r.get("clase_garantia")))
                if r.get("aceptado_por") != sp["aceptado_por"]:
                    f("GN_AUTORIDAD", "%s %s aceptado_por %s" % (i, r["id"], r.get("aceptado_por")))
                clases.add(sp["clase_garantia"])
                aut_esp |= set(sp["aceptado_por"])
            else:
                f("RELACION_TIPO", i)
        # uniones exigidas por el esquema, recalculadas aquí y comparadas con las declaradas
        decl_u = {(u.get("de"), u.get("campo"), u.get("a")): u for u in o.get("uniones", [])}
        for de, cam, a_ in esq.get("union", []):
            a = ESQ["selectores"][de]
            b_ = ESQ["selectores"][a_]
            try:
                ha = ctx.sel({"producto": a["p"], "filas_puntero": a.get("filas"), "filtro": a.get("filtro", []), "clave": a["clave"], "expandir": None, "escenario_campo": None})
                hb = ctx.sel({"producto": b_["p"], "filas_puntero": b_.get("filas"), "filtro": b_.get("filtro", []), "clave": b_["clave"], "expandir": None, "escenario_campo": None})
            except (LookupError, KeyError, ValueError, TypeError) as ex:
                f("UNION_INCOMPLETA", "%s %s→%s no evaluable %r" % (i, de, a_, ex))
                continue
            ids_b = set()
            for rr in hb["_filas"]:
                ids_b.add(rr.get("frontier_id"))
                ids_b.update(rr.get("frontier_ids_equivalentes") or [])
            vals = {rr[cam] for rr in ha["_filas"]}
            falt = vals - ids_b
            u = decl_u.pop((de, cam, a_), None)
            if falt or u is None or not u.get("cobertura_total") or u.get("valores_distintos") != len(vals) or u.get("cubiertos") != len(vals) - len(falt):
                f("UNION_INCOMPLETA", "%s %s→%s faltan %d declarada %s" % (i, de, a_, len(falt), None if u is None else (u.get("cubiertos"), u.get("valores_distintos"))))
        if decl_u:
            f("UNION_INCOMPLETA", "%s uniones no exigidas %s" % (i, sorted(decl_u)))
        # partición exigida por el esquema: partes disjuntas que cubren exactamente el total (recalculado aquí)
        pa = esq.get("particion")
        if pa:
            try:
                tot = selc(pa["de"])["_claves"]
                partes = {p_: selc(p_)["_claves"] for p_ in pa["partes"]}
                un = set().union(*partes.values())
                disj = sum(len(v) for v in partes.values()) == len(un)
                esp = {"de": pa["de"], "total": len(tot), "partes": {p_: len(v) for p_, v in partes.items()}, "disjuntas": disj, "cubre_total": un == tot}
                if not disj or un != tot or o.get("particion") != esp:
                    f("PARTICION", "%s declarada %s recalculada %s" % (i, o.get("particion"), esp))
            except (LookupError, KeyError, ValueError, TypeError) as ex:
                f("PARTICION", "%s no evaluable %r" % (i, ex))
        elif "particion" in o:
            f("PARTICION", "%s partición no exigida" % i)
        # textos: cada extracto textual de rem172 debe estar anclado por una relación texto de la misma fuente
        if x:
            txts = {(r.get("fuente"), r.get("texto")) for r in rels if r["tipo"] == "texto"}
            for xt in x.get("extractos", []):
                if xt.get("tipo") == "texto" and (xt.get("fuente"), xt.get("texto")) not in txts:
                    f("TEXTO_NO_ANCLADO", "%s extracto rem172 sin relación %s" % (i, xt.get("fuente")))
        decs = o.get("decision_que_admite", [])
        for dname in decs:
            dd = ESQ["decisiones"].get(dname)
            if dd is None:
                f("DECISION_NO_REGISTRADA", "%s %s" % (i, dname))
                continue
            if i not in dd["objetos"]:
                f("DECISION_FUERA_DE_OBJETO", "%s no es objeto de %s" % (i, dname))
            aut_esp.add(dd["aut"])
        if o["estado"] in ("parcial_con_limite_adoptado", "limitacion_adoptada") and not decs:
            f("LIMITE_SIN_DECISION", i)
        if o["estado"] in ("etapa_posterior", "condicional_no_activado") or (not rels and o["estado"] == "limitacion_adoptada"):
            aut_esp.add("diseno")
            rc = o.get("referencia_contractual")
            an = (rc or {}).get("anclas") or ([rc] if rc else [])
            if not an or not all(1 <= x["linea"] <= len(dl) and x["ancla"] in dl[x["linea"] - 1] for x in an if x.get("documento", "diseno") == "diseno"):
                f("REFERENCIA_CONTRACTUAL", i)
        if o["estado"] in BLOQ and not o.get("busqueda"):
            f("PENDIENTE_SIN_BUSQUEDA", i)
        # R6 autoridad aplicable y raíz
        declarada = set()
        for a in o.get("autoridad", []):
            declarada.add(a["id"])
            info = autinfo.get(a["id"]) if a["id"] in autinfo else (extra_aut or {}).get(a["id"])
            if info is None or not info.get("fijada_en_raiz"):
                f("AUTORIDAD_NO_RAIZ", "%s %s" % (i, a["id"]))
            elif a.get("sha256") != info["sha256"]:
                f("AUTORIDAD_HUELLA", "%s %s" % (i, a["id"]))
            if "rol" in a and info is not None and info.get("rol_raiz") != a["rol"]:
                f("AUTORIDAD_ROL_AUTODECLARADO", "%s %s" % (i, a["id"]))
        if declarada != aut_esp:
            f("AUTORIDAD_NO_APLICABLE", "%s declarada %s esperada %s" % (i, sorted(declarada), sorted(aut_esp)))
        pae = o.get("pais_anio_escenario") or ""
        if "según producto" in pae:
            f("ESCENARIO_NO_DERIVADO", "%s conserva «según producto»" % i)
        elif pae.startswith("por relación"):
            esc_rel = " | ".join(sorted({r.get("escenario") for r in rels if r.get("tipo") == "selector"}))
            if pae != "por relación; escenarios derivados de los selectores: " + esc_rel:
                f("ESCENARIO_NO_DERIVADO", "%s resumen de escenarios distinto de sus relaciones" % i)
        canon = sorted(clases)
        if o.get("garantia_clases") != canon or o.get("garantia") != (" + ".join(canon) if canon else "—"):
            f("GARANTIA_NO_DERIVADA", "%s declarada %s / %s derivada %s" % (i, o.get("garantia_clases"), o.get("garantia"), canon))
    # R7 decisiones del catálogo: anclas
    for dname, dd in ESQ["decisiones"].items():
        try:
            ok = True
            for kk in ("clave", "clave2"):
                if kk in dd:
                    ok &= ptr(ctx.autj[dd["aut"]], dd[kk][0]) == dd[kk][1]
            if "texto_ptr" in dd:
                ok &= str(ptr(ctx.autj[dd["aut"]], dd["texto_ptr"][0])).startswith(dd["texto_ptr"][1])
            if "substr" in dd:
                ok &= (dd["substr"] in ctx.autl[dd["aut"]][dd["linea"] - 1]) if "linea" in dd else (dd["substr"] in autb[dd["aut"]].decode("utf-8"))
        except (LookupError, KeyError, IndexError):
            ok = False
        dres = res.get("decisiones", {}).get(dname)
        if not ok or dres is None or dres.get("objetos") != dd["objetos"]:
            f("DECISION_NO_ANCLADA", dname)
    # R3b derivados aritméticos e igualdades selector ↔ libro, recalculados aquí

    try:
        phi = {}
        for r in selc("S_PHI_LOTE2")["_filas"]:
            for fid in [r["frontier_id"]] + list(r.get("frontier_ids_equivalentes") or []):
                phi[fid] = Fraction(r["clave_estructural"]["phi"])
        lim = sorted("%s|%s" % (r["frontier_id"], 1 - phi[r["frontier_id"]]) for r in selc("S_ELAST2_SP_LIMITE")["_filas"] if r["frontier_id"] in phi)

        def e6(sid):
            gr = {}
            for r in selc(sid)["_filas"]:
                gr.setdefault((r["conjunto"], r["pais"]), {})[r["variante"]] = r
            return sum(1 for v in gr.values() if Fraction(v["con"]["lambda_max"]) >= Fraction(v["sin"]["lambda_max"]) and Fraction(v["con"]["lambda_min"]) <= Fraction(v["sin"]["lambda_min"]))
        c192 = {r["cell_id"] for r in selc("S_COORD192")["_filas"]}
        c1532 = {r["cell_id"] for r in ctx.filas("P_coord_1532", None)}
        der = {"phi_racional_en_0_1": sum(1 for r in selc("S_PHI_LOTE2")["_filas"] if 0 <= Fraction(r["clave_estructural"]["phi"]) <= 1),
               "limite_1_menos_phi_filas": len(lim), "limite_1_menos_phi_huella": sha("\n".join(lim).encode()),
               "E6_pares_con_contiene_sin_lote1": e6("S_LAMBDA1_PARES"), "E6_pares_con_contiene_sin_lote2": e6("S_LAMBDA2_PARES"),
               "coord_disjuntas": c192.isdisjoint(c1532), "coord_union_celdas": len(c192 | c1532),
               "t8_unidades_con_captura": len({r["cell_id"] for r in selc("S_T8_CAPTURA")["_filas"]}),
               "topologia_puntos_distintos": sum(r["puntos"] - r["topologia_igual_en_puntos"] for r in selc("S_E4_PARES_TOPO_DISTINTA")["_filas"])}
        if der["limite_1_menos_phi_filas"] != selc("S_ELAST2_SP_LIMITE")["filas"]:
            f("DERIVADO", "filas límite sin phi de entrada")
        for k, v in der.items():
            if res.get("derivados", {}).get(k) != v:
                f("DERIVADO", "%s declarado %r recalculado %r" % (k, res.get("derivados", {}).get(k), v))
        igu_res = res.get("igualdades", [])
        if len(igu_res) != len(ESQ["igualdades"]):
            f("IGUALDAD", "número de igualdades declaradas")
        for n_, (sel_, fu_, p_) in enumerate(ESQ["igualdades"]):
            izq = selc(sel_)["cardinalidad"] if sel_ in ESQ["selectores"] else der[sel_]
            dr = ptr(ctx.autj[fu_], p_)
            dr = len(dr) if isinstance(dr, list) else dr
            if izq != dr:
                f("IGUALDAD", "%s = %d ≠ %s %s = %r" % (sel_, izq, fu_, p_, dr))
            if n_ < len(igu_res) and (igu_res[n_].get("izquierda") != sel_ or igu_res[n_].get("valor") != izq or igu_res[n_].get("valor_fuente") != dr or igu_res[n_].get("coincide") is not True):
                f("IGUALDAD", "declarada distinta para %s" % sel_)
    except (LookupError, KeyError, ValueError, TypeError, ZeroDivisionError) as ex:
        f("DERIVADO", "no evaluable %r" % (ex,))
    # R9 enlaces
    for (oi, ri), es in enl_por.items():
        if oi not in set(ids):
            f("ENLACE_OBLIGACION_INEXISTENTE", "%s %s" % (oi, ri))
            continue
        if (oi, ri) not in rel_vistas:
            f("ENLACE_RELACION_INEXISTENTE", "%s %s" % (oi, ri))
            continue
        if len(es) > 1:
            f("CLAVE_UNION", "enlace repetido %s %s" % (oi, ri))
    byid = {o["id"]: o for o in obs}
    for (oi, ri) in rel_vistas:
        es = enl_por.get((oi, ri))
        if not es:
            f("COBERTURA_ENLACES", "relación sin enlace %s %s" % (oi, ri))
            continue
        e = es[0]
        r = next(x for x in byid[oi]["relaciones"] if x["id"] == ri)
        fu = r.get("producto") or r.get("fuente")
        obj = r.get("selector") or r.get("puntero") or ("l.%s" % r.get("linea"))
        esc = r.get("escenario") or "—"
        if e.get("clave_union") != "|".join([oi, ri, fu, str(obj), esc]) or e.get("escenario") != esc or e.get("fuente") != fu:
            f("CLAVE_UNION", "%s %s" % (oi, ri))
        if e.get("cantidad") != r.get("cardinalidad"):
            f("CANTIDAD_NO_DERIVADA", "enlace %s %s %s != %s" % (oi, ri, e.get("cantidad"), r.get("cardinalidad")))
        if e.get("clase_garantia") != r.get("clase_garantia") or e.get("huella_claves") != r.get("huella_claves"):
            f("GARANTIA_NO_DERIVADA" if e.get("clase_garantia") != r.get("clase_garantia") else "HUELLA_CLAVES", "enlace %s %s" % (oi, ri))
    # R10 coherencia
    pe = dict(sorted(Counter(o["estado"] for o in obs).items()))
    if res.get("por_estado") != pe or res.get("obligaciones") != len(obs) or res.get("relaciones") != len(enl):
        f("COHERENCIA_RESUMEN", "por_estado/obligaciones/relaciones")
    bl = [o["id"] for o in obs if o["estado"] in BLOQ]
    rmd = rem.get("_md", "")
    if rem.get("busquedas") != ESQ["busquedas"]:
        f("COHERENCIA_REMANENTE", "búsquedas del remanente distintas de las declaradas")
    if ("Propuesta de cierre: **no**." in rmd) != bool(bl) or any(("- `%s` — %s; búsqueda" % (b, byid[b]["estado"])) not in rmd for b in bl):
        f("COHERENCIA_REMANENTE", "REMANENTE.md distinto de la matriz")
    for o in obs:
        if o["id"] in XOBS and (o.get("version_rem172") or {}).get("estado") != XOBS[o["id"]]["estado"]:
            f("VERSION_REM172", "%s estado rem172 declarado %s ≠ X %s" % (o["id"], (o.get("version_rem172") or {}).get("estado"), XOBS[o["id"]]["estado"]))
    # rem174: correspondencia de las 83 con rem173 y ninguna transición de estado no declarada
    if sorted(o["id"] for o in obs) != sorted(X3OBS):
        f("CORRESPONDENCIA_83", "obligaciones distintas de rem173")
    for o in obs:
        x3 = X3OBS.get(o["id"])
        if x3 is None:
            continue
        if o["estado"] != x3["estado"] or (o.get("version_rem173") or {}).get("estado") != x3["estado"]:
            f("TRANSICION_NO_DECLARADA", "%s %s (rem173 %s)" % (o["id"], o["estado"], x3["estado"]))
        ids_ = [r_["id"] for r_ in o.get("relaciones", [])]
        if [r_["id"] for r_ in x3["relaciones"]] != [x_ for x_ in ids_ if x_ not in E174["relaciones"].get(o["id"], [])] or (o.get("version_rem173") or {}).get("relaciones") != len(x3["relaciones"]):
            f("RELACIONES_REM173_ALTERADAS", o["id"])
    # rem175: correspondencia exacta con la matriz candidata rem174 (83 obligaciones, 289 relaciones iguales salvo la huella de producto de la
    # extensión, que se coteja aparte contra los bytes del producto validado), sin transición de estado
    if sorted(o["id"] for o in obs) != sorted(X4OBS):
        f("CORRESPONDENCIA_REM174", "obligaciones distintas de rem174")
    for o in obs:
        x4 = X4OBS.get(o["id"])
        if x4 is None:
            continue
        if o["estado"] != x4["estado"] or (o.get("version_rem174") or {}).get("estado") != x4["estado"]:
            f("TRANSICION_NO_DECLARADA", "%s %s (rem174 %s)" % (o["id"], o["estado"], x4["estado"]))
        if _sin_huella(o.get("relaciones", [])) != _sin_huella(x4["relaciones"]) or (o.get("version_rem174") or {}).get("relaciones") != len(x4["relaciones"]):
            f("RELACIONES_REM174_ALTERADAS", o["id"])
    # rem175: textos de ausencia y de alcance (frases prohibidas; textos base exigidos; marca de propuesta sin adoptar)
    docs = dict(TXT_ACT["t"], remanente_md=rem.get("_md", ""), matriz_md=md)
    for k_, t_ in docs.items():
        for fr in E175["frases_prohibidas"]:
            if fr.lower() in t_.lower():
                f("AUSENCIA_INFERENCIA", "%s contiene «%s»" % (k_, fr))
    for k_, req in E175["exigencias_texto"].items():
        norm = " ".join(docs.get(k_, "").split())
        for rq in req:
            if " ".join(E175[rq].split()) not in norm:
                f("AUSENCIA_INFERENCIA", "%s sin el texto exigido %s" % (k_, rq))
    if E175["marca_sin_adoptar"] not in docs.get("propuestas", ""):
        f("AUSENCIA_INFERENCIA", "propuestas sin la marca «%s»" % E175["marca_sin_adoptar"])
    if res.get("remanente") != bl or res.get("propuesta_de_cierre") != (not bl) or rem.get("propuesta_de_cierre") != (not bl) or [b["id"] for b in rem.get("bloqueantes", [])] != bl:
        f("COHERENCIA_REMANENTE", "remanente declarado %s / %s; bloqueantes %s" % (res.get("remanente"), [b["id"] for b in rem.get("bloqueantes", [])], bl))
    filas_md = {}
    for ln in md.splitlines():
        if ln.startswith("| ") and not ln.startswith("| id ") and not ln.startswith("|---"):
            cs = [c.strip() for c in ln.strip("|").split("|")]
            filas_md[cs[0]] = (cs[1], cs[2])
    if filas_md != {o["id"]: (o["estado"], str(len(o.get("relaciones", [])))) for o in obs}:
        f("COHERENCIA_MD", "tabla md distinta de la matriz")
    # controles (33) recalculados aquí; un producto ilegible los deja sin evaluar (y ya consta como no autenticado)
    try:
        ctl = controles(ctx)
    except (LookupError, KeyError, ValueError, TypeError) as ex:
        f("CONTROL_NO_EVALUABLE", repr(ex)[:200])
        return F, ctx, []
    decl = res.get("controles", [])
    if len(decl) != len(ctl) or any(a["derivado"] != b or a["esperado_encargo"] != c for a, (b, c) in zip(decl, ctl)):
        f("CONTROL", "controles declarados distintos de los recalculados")
    if not all(b == c for b, c in ctl):
        f("CONTROL", "control recalculado distinto del esperado del encargo")
    # los 32 controles de rem172, cada uno cubierto por un control rem173 recalculado aquí
    mapa = res.get("mapa_controles_rem172", {}).get("pares", [])
    if mapa != ESQ["mapa_controles_rem172"]["pares"] or sorted(p["i172"] for p in mapa) != list(range(len(XCTL))):
        f("CONTROL_REM172", "mapa de controles rem172 incompleto o distinto del declarado")
    for p in ESQ["mapa_controles_rem172"]["pares"]:
        e172 = XCTL[p["i172"]]["esperado_encargo"]
        v173 = ctl[p["j173"]][0] if p["j173"] < len(ctl) else None
        if p["tipo"] == "texto":
            ok = isinstance(e172, str) and e172 in ctx.autb[p["fuente"]].decode("utf-8") and v173 is True
        elif p["tipo"] == "salvedad":
            ok = e172 is True and v173 == [True, True, True, True, False]
        else:
            a172 = [e172[k] for k in p["claves"]] if p.get("claves") else e172
            b173 = [v173[k] for k in p["componentes"]] if p.get("componentes") else v173
            if p.get("claves") and len(p["claves"]) == 1 and not isinstance(b173, list):
                b173 = [b173]
            if p.get("componentes") and len(p["componentes"]) == 1 and not isinstance(a172, list):
                b173 = b173[0]
            ok = a172 == b173
        if not ok:
            f("CONTROL_REM172", "rem172[%d] %s → rem173[%d]: %r vs %r" % (p["i172"], XCTL[p["i172"]]["campo"], p["j173"], e172, v173))
    return F, ctx, ctl


def controles(ctx):
    def S(sid):
        d = ESQ["selectores"][sid]
        return ctx.sel({"producto": d["p"], "filas_puntero": d.get("filas"), "filtro": d.get("filtro", []), "clave": d["clave"], "expandir": d.get("expandir")})

    L = lambda a, p: ptr(ctx.autj[a], p)  # noqa: E731
    c = lambda s: S(s)["cardinalidad"]  # noqa: E731
    cap_u = len({r["cell_id"] for r in S("S_T8_CAPTURA")["_filas"]})
    c192 = {r["cell_id"] for r in S("S_COORD192")["_filas"]}
    c1532 = {r["cell_id"] for r in ctx.filas("P_coord_1532", None)}
    v = ctx.pj["P_val_e1235"]
    cx = ptr(ctx.pj["X_resumen_exp8"], "/COV_resolucion_global/contextos")
    return [
        (c("S_T8_UNIDADES"), 2276), (cap_u, 2111), (c("S_T8_UNIDADES") - cap_u, 165), ("587 v2 y 1.689 v3" in ctx.autb["D_rem106"].decode("utf-8"), True),
        ([L("L_rem105", "/counts/PROD1/accepted") + L("L_rem105", "/counts/PROD2/accepted"), L("L_rem105", "/counts/PROD1/complete") + L("L_rem105", "/counts/PROD2/complete"),
          L("L_rem105", "/counts/PROD1/declared_D4") + L("L_rem105", "/counts/PROD2/declared_D4")], [120, 52, 68]),
        ([L("L_rem105", "/counts/PROD3/accepted_tasks"), L("L_rem105", "/counts/PROD3/complete_outputs")], [16, 32]),
        ([L("L_rem147", "/accepted_counts/definitive_total"), L("L_rem147", "/accepted_counts/capture_pending")], [13656, 0]),
        ([L("L_rem147", "/accepted_counts/capture_computed"), L("L_rem147", "/accepted_counts/capture_outside_support")], [963, 1148]),
        (c("S_T8_CAPTURA"), 2111),
        ([ptr(ctx.pj["P_val_e1i2"], "/conforme"), v["E2"]["conforme"], v["E3"]["conforme"], v["E5"]["conforme"], v["E1"]["conforme"]], [True, True, True, True, False]),
        (L("L_rem122", "/E4/parent_universe"), 572),
        ([c("S_ELAST2_TODAS"), c("S_ELAST2_HIST"), c("S_ELAST2_NUEVAS")], [4195, 70, 4125]),
        ([c("S_LAMBDA1_PARES") + c("S_LAMBDA2_PARES"), c("S_LAMBDA1_ENV") + c("S_LAMBDA2_ENV")], [14, 28]),
        ([c("S_E4_MALLAS"), c("S_E4_FILAS"), c("S_E4_PARES")], [383, 4115, 391]),
        ([len(c192), len(c1532), c192.isdisjoint(c1532), len(c192 | c1532)], [192, 1532, True, 1724]),
        ([c("S_COORD1532_REUT"), c("S_COORD1532_RECALC")], [1502, 30]),
        ([c("S_COORD1532_CLAVES"), L("L_rem125", "/assembly/reused_roofs"), L("L_rem125", "/certified_roofs_new_count")], [26, 20, 6]),
        ([c("S_ENF_TECHOS"), c("S_ENF_PUNTOS")], [26, 330]),
        (c("S_EXP8_ENF_INCONCL") + c("S_EXP8_ENF_NODEC"), 1728),
        ([c("S_EXP8_ENF_INCONCL"), c("S_EXP8_ENF_NODEC")], [1712, 16]),
        ([c("S_EXP8_COV_INCONCL"), c("S_EXP8_COV_ROBUST"), c("S_EXP8_COV_NODEC")], [1700, 12, 16]),
        ([c("S_EXP8_Q_INCONCL"), c("S_EXP8_Q_REFUTADA")], [1712, 16]),
        ([c("S_EXP8_PADRE_INCONCL"), c("S_EXP8_PADRE_ROBUSTA")], [1712, 16]),
        ([c("S_EXP8_QCONS_INCONCL"), c("S_EXP8_QCONS_REFUTADA")], [1712, 16]),
        ([c("S_EXP8_P7"), c("S_EXP8_P7_UNIDADES")], [7, 4]),
        ([L("L_rem171", "/counts/P7_claims"), L("L_rem171", "/counts/P7_units")], [7, 4]),
        (c("S_EXP8_DESC_REM108"), 1705),
        (c("S_EXP8_COV_SIGNOS"), 20),
        ([c("S_EXP8_COV_ROBUST"), c("S_COV12")], [12, 12]),
        ([cx.get("antes_dedup_doce"), cx.get("suma_tamanos_grupo"), cx.get("union_efectiva")], [4608, 2304, 1920]),
        (c("S_COV12_GRUPOS"), 6),
        ("2024p pertenece al soporte E2 de la cota global" in ctx.prb["X_matriz_cierre"].decode("utf-8"), True),
        (all("2024p" in k for k in L("L_rem125", "/outside_declared_universe")), True),
    ]


# ------------------------------------------------------------------ positivo
REM = dict(REM, _md=BY["remanente_md"].decode("utf-8"))
F0, CTX0, CTL0 = evaluar(MAT, ENL, RES, REM, MD, PRB0, AUTB0, AUTINFO)
RESULT = {"kind": "verificacion-final-relaciones-rem175", "salida": str(SAL.relative_to(Y)),
          "ligadura": {"raiz_fuentes": E175["raiz_fuentes"]["sha256"], "pares_E4": len(AG["orden"]), "pares_completos": sorted(AG["completos"]),
                       "registros_del_mapa": len(AG["regs"]), "resumen_gn_derivado": RES_GN, "localizacion_derivada": AL["tot"], "fallos_de_ligadura_loc": AL["fallos"],
                       "productos_validados": {k: {"ruta": str(TT / XA / v["producto"]), "sha256": sha(PRB174[k])} for k, v in E174["especificacion"].items()},
                       "pares_validado": {"ruta": str(TT / XA / E175["productos_extension"]["pares"]), "sha256": sha((TT / XA / E175["productos_extension"]["pares"]).read_bytes())}},
          "gn_rederivado": {"fallos_base": GN_BASE[0], "valores": {k: v[0] for k, v in GN_BASE[1].items()}, "cardinalidades": {k: v[1] for k, v in GN_BASE[1].items()}},
          "archivos": {k: {"ruta": str(p), "bytes": len(BY[k]), "sha256": sha(BY[k])} for k, p in ARCH.items()},
          "autoridades": AUTINFO, "productos": {p: {"sha256": sha(b), "aceptado_por": sorted(CTX0.acep[p]), "cadena_conforme": not CTX0.fallo_cadena[p]} for p, b in PRB0.items()},
          "controles_recalculados": [{"derivado": a, "esperado": b, "coincide": a == b} for a, b in CTL0],
          "positivo": {"fallos": F0, "aceptado": not F0}}

# ------------------------------------------------------------------ negativos (parches en disco, releídos)
ND = EJ / "negativos"
ND.mkdir()


def obl(m, i):
    return next(o for o in m["obligaciones"] if o["id"] == i)


def aplicar(pa, m, e, r, rm, md, prb, autb, autinfo):
    extra = None
    for op in pa:
        t = op["op"]
        if t == "set_obl":
            obl(m, op["obl"])[op["campo"]] = op["valor"]
        elif t == "set_rel":
            next(x for x in obl(m, op["obl"])["relaciones"] if x["id"] == op["rel"])[op["campo"]] = op["valor"]
        elif t == "set_enl":
            if not any(x["obligacion"] == op["obl"] and x["relacion"] == op["rel"] for x in e):
                raise SystemExit("parche de enlace sin objetivo %s %s" % (op["obl"], op["rel"]))
            for x in e:
                if x["obligacion"] == op["obl"] and x["relacion"] == op["rel"]:
                    x[op["campo"]] = op["valor"]
                    if op.get("recalcular_clave"):
                        x["clave_union"] = "|".join([x["obligacion"], x["relacion"], x["fuente"], str(x["objeto"]), x["escenario"]])
        elif t == "enl_solo_clase":
            e[:] = [x for x in e if x["clase_garantia"] == op["clase"]]
        elif t == "borrar_obl":
            m["obligaciones"] = [o for o in m["obligaciones"] if o["id"] != op["obl"]]
        elif t == "duplicar_obl":
            dup = copy.deepcopy(obl(m, op["copiar"]))
            m["obligaciones"] = [dup if o["id"] == op["quitar"] else o for o in m["obligaciones"]]
        elif t == "duplicar_rel":
            o = obl(m, op["obl"])
            o["relaciones"].append(copy.deepcopy(next(x for x in o["relaciones"] if x["id"] == op["rel"])))
        elif t == "set_ctrl":
            r["controles"][op["indice"]]["derivado"] = op["valor"]
        elif t == "set_res":
            r[op["campo"]] = op["valor"]
        elif t == "set_res_clave":
            if op["clave"] not in r[op["campo"]]:
                raise SystemExit("parche de resumen sin objetivo " + op["clave"])
            r[op["campo"]][op["clave"]] = op["valor"]
        elif t == "set_rem":
            rm[op["campo"]] = op["valor"]
        elif t == "flip_byte":
            bb = bytearray(prb[op["producto"]])
            bb[op["byte"]] ^= 1
            prb[op["producto"]] = bytes(bb)
        elif t == "autoridad_inventada":
            b = op["bytes"].encode("utf-8")
            with open(ND / Path(op["ruta_rel"]).name, "xb") as fh:
                fh.write(b)
            b = (ND / Path(op["ruta_rel"]).name).read_bytes()
            extra = {op["id"]: {"nombre": Path(op["ruta_rel"]).name, "sha256": sha(b), "fijada_en_raiz": sha(b) in {h for h, _ in PIN.get(Path(op["ruta_rel"]).name, set())}, "rol_raiz": None}}
            obl(m, op["obl"])["autoridad"] = [{"id": op["id"], "sha256": sha(b), "rol": op["rol"]}]
        elif t == "autoridad_copia":
            src = autinfo[op["copia_de"]]
            autinfo[op["id"]] = {"nombre": op["nombre"], "sha256": src["sha256"], "fijada_en_raiz": src["sha256"] in {h for h, _ in PIN.get(op["nombre"], set())}, "rol_raiz": None}
            obl(m, op["obl"])["autoridad"] = [{"id": op["id"], "sha256": src["sha256"]}]
        elif t == "md_reemplaza":
            if op["viejo"] not in md:
                raise SystemExit("parche md sin efecto " + op["viejo"])
            md = md.replace(op["viejo"], op["nuevo"], 1)
        elif t == "rmd_reemplaza":
            if op["viejo"] not in rm["_md"]:
                raise SystemExit("parche REMANENTE.md sin efecto " + op["viejo"])
            rm["_md"] = rm["_md"].replace(op["viejo"], op["nuevo"], 1)
        elif t == "set_version_rem172":
            obl(m, op["obl"])["version_rem172"][op["campo"]] = op["valor"]
        elif t == "set_autoridad_ids":
            obl(m, op["obl"])["autoridad"] = [{"id": a, "sha256": autinfo[a]["sha256"]} for a in op["ids"]]
        elif t == "altera_rol":
            autinfo[op["aut"]] = dict(autinfo[op["aut"]], rol_raiz=op["rol"])
        elif t == "recortar_lista":
            o = obl(m, op["obl"])
            o[op["campo"]] = o[op["campo"]][:op["n"]]
        elif t == "altera_autoridad":
            j = json.loads(autb[op["aut"]])
            cur = j
            ps = op["puntero"].split("/")[1:]
            for s_ in ps[:-1]:
                cur = cur[s_]
            cur[ps[-1]] = op["valor"]
            autb[op["aut"]] = json.dumps(j, ensure_ascii=False).encode("utf-8")
            autinfo[op["aut"]] = dict(autinfo[op["aut"]], sha256=sha(autb[op["aut"]]), fijada_en_raiz=sha(autb[op["aut"]]) in {h for h, _ in PIN.get(autinfo[op["aut"]]["nombre"], set())})
        elif t in ("pares_set", "reg_set", "cob_set"):
            base = {"pares_set": ("pares", PARES0), "reg_set": ("reg", REG0), "cob_set": ("cob", COB0)}[t]
            obj = GN_MUT.setdefault(base[0], copy.deepcopy(base[1]))
            ps = [s_ for s_ in op["puntero"].split("/")[1:]]
            cur = obj
            for s_ in ps[:-1]:
                cur = cur[int(s_)] if isinstance(cur, list) else cur[s_]
            last = int(ps[-1]) if isinstance(cur, list) else ps[-1]
            if op.get("borrar"):
                del cur[last]
            else:
                if isinstance(cur, dict) and last not in cur and not op.get("crear"):
                    raise SystemExit("parche GN sin objetivo " + op["puntero"])
                cur[last] = op["valor"]
        elif t == "pares_duplicar":
            obj = GN_MUT.setdefault("pares", copy.deepcopy(PARES0))
            obj["pares"].append(copy.deepcopy(obj["pares"][op["indice"]]))
        elif t == "pares_invertir":
            obj = GN_MUT.setdefault("pares", copy.deepcopy(PARES0))
            obj["pares"].reverse()
        elif t == "sonda":
            # rem175: entradas en disco de la sonda del revisor (W, solo lectura), autenticadas por el manifiesto rem175; huellas de los
            # productos documentales actualizadas coherentemente, como en review_20261108_rem175_probes.py
            base_ = WD / "review_20261108_rem175_probe_inputs" / op["caso"]
            datos = {}
            for k_ in ("pares", "registro", "cobertura"):
                b_ = (base_ / (k_ + ".json")).read_bytes()
                if sha(b_) != FIJ175.get((op["caso"], k_)):
                    raise SystemExit("entrada de sonda no fijada %s/%s" % (op["caso"], k_))
                datos[k_] = b_
            GN_MUT["pares"], GN_MUT["reg"], GN_MUT["cob"] = (json.loads(datos[k_]) for k_ in ("pares", "registro", "cobertura"))
            upd = {}
            for rid, sp in E174["especificacion"].items():
                PRB174[rid] = datos["registro" if sp["tipo"] == "localizacion" else "cobertura"]
                upd[rid] = sha(PRB174[rid])
            for o_ in m["obligaciones"]:
                for r_ in o_["relaciones"]:
                    if r_["id"] in upd:
                        r_["sha256_producto"] = upd[r_["id"]]
        elif t == "texto_reemplaza":
            tt = dict(TXT_ACT["t"])
            if op["viejo"] not in tt[op["doc"]]:
                raise SystemExit("parche de texto sin efecto " + op["viejo"])
            tt[op["doc"]] = tt[op["doc"]].replace(op["viejo"], op["nuevo"], 1)
            TXT_ACT["t"] = tt
        else:
            raise SystemExit("operación desconocida " + t)
    return md, extra


NEG = []
for t in PRU["negativos"]:
    p = ND / (t["id"] + ".json")
    with open(p, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"nota": "COPIA SINTÉTICA: solo se guarda la mutación", "id": t["id"], "parche": t["parche"]}, ensure_ascii=False, indent=1) + "\n")
    pa = json.loads(p.read_text(encoding="utf-8"))["parche"]
    m, e, r, rm = copy.deepcopy(MAT), copy.deepcopy(ENL), copy.deepcopy(RES), copy.deepcopy(REM)
    prb, autb, ai = dict(PRB0), dict(AUTB0), copy.deepcopy(AUTINFO)
    GN_MUT.clear()
    _prb174_0 = dict(PRB174)
    md2, extra = aplicar(pa, m, e, r, rm, MD, prb, autb, ai)
    GN_ACT["h"] = gn_hechos(GN_MUT.get("pares", PARES0), GN_MUT.get("reg", REG0), GN_MUT.get("cob", COB0)) if GN_MUT else GN_BASE
    fl, _, _ = evaluar(m, e, r, rm, md2, prb, autb, ai, extra)
    GN_ACT["h"] = GN_BASE
    PRB174.clear()
    PRB174.update(_prb174_0)
    TXT_ACT["t"] = TXT175
    reglas = sorted({x["regla"] for x in fl})
    if t.get("valido"):
        NEG.append({"id": t["id"], "origen": t["origen"], "descripcion": t["descripcion"], "parche_sha256": sha(p.read_bytes()), "regla_esperada": None,
                    "valido": True, "reglas_disparadas": reglas, "fallos": fl[:5], "rechazado_por_su_motivo": not fl})
        continue
    esperadas = t.get("reglas_esperadas") or [t["regla_esperada"]]
    NEG.append({"id": t["id"], "origen": t["origen"], "descripcion": t["descripcion"], "parche_sha256": sha(p.read_bytes()), "regla_esperada": t["regla_esperada"],
                "reglas_esperadas": esperadas, "reglas_disparadas": reglas, "fallos": fl[:5], "rechazado_por_su_motivo": all(x in reglas for x in esperadas)})
RESULT["negativos"] = NEG
RESULT["negativos_rechazados_por_su_motivo"] = sum(1 for n in NEG if n["rechazado_por_su_motivo"])
RESULT["negativos_total"] = len(NEG)
RESULT["controles_conformes"] = all(a == b for a, b in CTL0)
RESULT["veredicto"] = "CONFORME" if (not F0 and RESULT["negativos_rechazados_por_su_motivo"] == len(NEG) and RESULT["controles_conformes"]) else "NO_CONFORME"
RESULT["por_origen"] = {o_: {"total": sum(1 for n in NEG if n["origen"] == o_), "por_su_motivo": sum(1 for n in NEG if n["origen"] == o_ and n["rechazado_por_su_motivo"])}
                        for o_ in sorted({n["origen"] for n in NEG})}
with open(EJ / "VERIFICACION_FINAL_REM175.json", "x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(RESULT, ensure_ascii=False, indent=1, default=str) + "\n")
print(RESULT["veredicto"], "positivo", not F0, "negativos", RESULT["negativos_rechazados_por_su_motivo"], "/", len(NEG), "controles", RESULT["controles_conformes"])
for x in F0[:30]:
    print(" FALLO POSITIVO", x)
for n in NEG:
    if not n["rechazado_por_su_motivo"]:
        print(" NEGATIVO NO RECHAZADO POR SU MOTIVO", n["id"], n["reglas_disparadas"])
sys.exit(0 if RESULT["veredicto"] == "CONFORME" else 3)
