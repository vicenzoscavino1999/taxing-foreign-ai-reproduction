"""ORQUESTADOR CANDIDATO de la fase global B (P0 de H4; CACHE FINAL P0 H4 3.7 y P0 COMPLETO H4 3.7, NO OFICIAL). No es la
fase global completa (P1).

  <py_integracion> -m codigo.orquestador_b plan <salida.json>
  <py_integracion> -m codigo.orquestador_b ejecutar <dir_corrida> <muestra.json> [--reanudar] [--tope-afirmacion s] [--tope-proceso s]
                   [--interrumpir-tras n] [--doble-detencion cid] [--doble-error cid] [--config-alterna]
  <py_integracion> -m codigo.orquestador_b verificar <dir_corrida> <hojas_ci.json> <plan.json> <salida.json>

Integra componentes EXISTENTES (no hay optimización ni método nuevo):
- ci-df: extremos de G por el método v5 (la misma secuencia por afirmación que codigo/muestra_G_df.py y extremos_G_df_v5:
  sup = conjunta en p⁺ con el certificado SRED; inf = rama y cota conjunta con la cota de un umbral sobre los puntos U, con
  tope por afirmación); se CALCULA.
- ci-d y ci-f: producciones COMPLETAS históricas autenticadas por inventario (XDD + PRV para ci-d; CAN para ci-f); se
  RECUPERAN sin recalcular, con su cita.
- country y global, en conditional_full Y conditional_none: AGREGACIÓN PAÍS POR PAÍS con la regla de E13 (sup: [max L, max U];
  inf: [min L, min U]; hoja ganadora la de mayor L (sup) o menor U (inf); desempate d < df < f, país, claim_id).

DEPENDENCIAS (P0 COMPLETO): se DERIVAN de la autoridad autenticada, las afirmaciones del contexto S5 (paper2b.claims.derive,
idéntico al original): una country depende de las hojas ci de SUS instrumentos (Claim.instruments: en conditional_none solo
('d',), hoja domestic_unchanged) y una global de las country de SUS países (Claim.countries) en el MISMO escenario, con igualdad
de preregistro, tipo, diseño, cota, bloque, capa, años, escenarios, ediciones y soportes. Una dependencia ausente, ambigua o de
otro tipo, o una ruta sin implementar, se RECHAZA con código 4 ANTES de cualquier cálculo.

REANUDACIÓN (P0 COMPLETO): los resultados TERMINALES (convergido, detenido, error) se reutilizan y nunca se recalculan ni se
elevan automáticamente; los PENDIENTES (no_ejecutado: dependencias ausentes o tope de proceso) se REEVALÚAN al reanudar. Un
agregado terminal guarda el sha256 de contenido de cada componente; si no coincide con el componente vigente se reevalúa
(agregar es barato). Identidad (registro v4, autoridad del despliegue, bytes del código, fuentes y configuración) comprobada
ANTES de cargar el contexto: una reanudación con otra identidad se rechaza sin cálculo (código 3). Checkpoint ATÓMICO por
afirmación y sentido. Dobles de detención y error rotulados SIMULACION.
Pila: la del método v5 (paper2b AISLADO del área, codigo.demo.nucleo_v.Contexto, codigo.extremos_G.preparar); el módulo no
importa el núcleo candidato (flujo_paso4_v2) porque extremos_G_df_v5 exige su paper2b aislado (PAPER2B_NO_AISLADO).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
import uuid
from collections import Counter
from pathlib import Path

A = Path(__file__).resolve().parents[1]
T = A.parent
L754 = "cierre_G_df_3_7_2026-10-06_lima0754"
RES = ("resolucion_3_7_2026-10-04_lima1941", "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f")
REL_REG = "demo/registro/registro_candidato_v4.json"
CODIGO = ("codigo/orquestador_b.py", "codigo/extremos_G_df_v5.py", "codigo/extremos_dfd.py", "codigo/extremos_G.py",
          "codigo/inf_df_bb_v3.py", "codigo/cota_un_umbral_v2.py", "codigo/demo/nucleo_v.py", "codigo/demo/cobertura_compartida.py",
          "integracion/src/paper2b/claims.py")
ORDEN_J = {"d": 0, "df": 1, "f": 2}
ORDEN_FAM = {"ci": 0, "c": 1, "g": 2}
TERMINALES = ("convergido", "detenido", "error")      # reutilizables; nunca se recalculan ni se elevan automáticamente
PENDIENTES = ("no_ejecutado",)                         # se reevalúan al reanudar
T2_AGREGADO = 1e-4
ATRIBUTOS = ("preregistration_id", "kind", "design", "bound_variant", "eta_w_block", "layer", "years", "scenarios", "editions", "support_sets")
RUTAS = {("ci", "df"): "calculo_v5_ci_df", ("ci", "d"): "recuperacion_historica_XDD_PRV", ("ci", "f"): "recuperacion_historica_CAN",
         ("c", "conditional_full"): "agregacion_country_cf", ("c", "conditional_none"): "agregacion_country_cn",
         ("g", "conditional_full"): "agregacion_global_cf", ("g", "conditional_none"): "agregacion_global_cn"}


class RutaNoSoportada(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def atomico(p: Path, data: bytes):
    tmp = p.with_name("." + p.name + "." + uuid.uuid4().hex + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, p)


def campos(cid):
    """= extremos_G_df_v5.campos (copia literal para no cargar paper2b en el plan y la verificación)."""
    p = cid.split(":")
    if p[3] == "ci":
        return {"pid": p[1], "kind": p[2], "fam": "ci", "pais": p[4], "j": p[5], "avail": p[6], "dis": p[7], "resto": tuple(p[8:])}
    if p[3] == "c":
        return {"pid": p[1], "kind": p[2], "fam": "c", "pais": p[4], "scen": p[5], "dis": p[6], "resto": tuple(p[7:])}
    return {"pid": p[1], "kind": p[2], "fam": "g", "scen": p[4], "dis": p[5], "resto": tuple(p[6:])}


def registro():
    """Registro v4 autenticado por el inventario de lima1941 (mismo vínculo que extremos_G_df_v5.auth('RES'))."""
    inv_raw = (T / RES[0] / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != RES[1]:
        raise SystemExit("INVENTARIO_RES_ALTERADO")
    raw = (T / RES[0] / REL_REG).read_bytes()
    if json.loads(inv_raw)["files"][REL_REG]["sha256"] != sha(raw):
        raise SystemExit("REGISTRO_NO_AUTENTICADO")
    return raw


# ============================================================================================== autoridad de dependencias
def ruta_de(cid):
    f = campos(cid)
    k = (f["fam"], f["j"] if f["fam"] == "ci" else f["scen"])
    if k not in RUTAS:
        raise RutaNoSoportada("RUTA_NO_SOPORTADA:%s:%s" % (cid, k))
    return RUTAS[k]


def dependencias(claims):
    """{claim_id: [dependencias]} derivado de la autoridad (Claim del contexto S5). Lanza RutaNoSoportada si una dependencia
    no existe, no es única o es de otro tipo. Las hojas ci no tienen dependencias."""
    porid = {c.claim_id: c for c in claims}
    clave = lambda c: tuple(getattr(c, a) for a in ATRIBUTOS)  # noqa: E731
    hojas, paises = {}, {}
    for c in claims:
        if c.claim_scope == "country_instrument":
            hojas.setdefault((clave(c), c.country_id, c.instrument_j), []).append(c)
        elif c.claim_scope == "country":
            paises.setdefault((clave(c), c.country_id, c.availability_case_id), []).append(c)
    deps = {}
    for c in claims:
        ruta_de(c.claim_id)
        if c.claim_scope == "country_instrument":
            if c.instruments != (c.instrument_j,) or c.countries != (c.country_id,):
                raise RutaNoSoportada("HOJA_INCOHERENTE:%s" % c.claim_id)
            deps[c.claim_id] = []
        elif c.claim_scope == "country":
            ds = []
            for j in c.instruments:
                xs = hojas.get((clave(c), c.country_id, j), [])
                if c.availability_case_id == "conditional_none":
                    xs = [x for x in xs if x.availability_case_id == "domestic_unchanged"]   # instruments_for: solo domestic_unchanged
                if len(xs) != 1:
                    raise RutaNoSoportada("HOJA_NO_UNICA:%s:%s:%d" % (c.claim_id, j, len(xs)))
                ds.append(xs[0].claim_id)
            if len(set(ds)) != len(ds) or not ds:
                raise RutaNoSoportada("HOJAS_DUPLICADAS_O_VACIAS:%s" % c.claim_id)
            deps[c.claim_id] = ds
        elif c.claim_scope == "global":
            ds = []
            for p in c.countries:
                xs = paises.get((clave(c), p, c.availability_case_id), [])
                if len(xs) != 1:
                    raise RutaNoSoportada("COUNTRY_NO_UNICA:%s:%s:%d" % (c.claim_id, p, len(xs)))
                ds.append(xs[0].claim_id)
            if len(set(ds)) != len(ds) or len(ds) < 2:
                raise RutaNoSoportada("PAISES_DUPLICADOS_O_INSUFICIENTES:%s" % c.claim_id)
            deps[c.claim_id] = ds
        else:
            raise RutaNoSoportada("ALCANCE_DESCONOCIDO:%s:%s" % (c.claim_id, c.claim_scope))
    for cid, ds in deps.items():
        for x in ds:
            if x not in porid:
                raise RutaNoSoportada("DEPENDENCIA_INEXISTENTE:%s:%s" % (cid, x))
            esperado = {"c": "ci", "g": "c"}[campos(cid)["fam"]]
            if campos(x)["fam"] != esperado:
                raise RutaNoSoportada("DEPENDENCIA_DE_OTRO_TIPO:%s:%s" % (cid, x))
    return deps


def cierre(ids, deps):
    """Cierre por dependencias (sin duplicados) en orden topológico: hojas, country, global."""
    vistos, pila = set(), list(ids)
    while pila:
        x = pila.pop()
        if x in vistos:
            continue
        if x not in deps:
            raise RutaNoSoportada("AFIRMACION_FUERA_DE_LA_AUTORIDAD:%s" % x)
        vistos.add(x)
        pila.extend(deps[x])
    return sorted(vistos, key=lambda c: (ORDEN_FAM[campos(c)["fam"]], c))


def puntos_U_de(d):
    """Fuentes de puntos U del método v5 para el diseño d: las que citó la propagación autenticada (lima0754)."""
    prop = json.loads((T / L754 / ("demo/hito2/extremos_G_df_v5_%s.json" % d)).read_bytes())
    return [(L754, f["archivo"], f["sha256"]) for f in prop["puntos_U"]["fuentes"]]


def identidad(muestra_sha, config):
    dep = json.loads((A / "autorizacion/despliegue_candidato.json").read_bytes())
    return {"orquestador": "B-CANDIDATO-v2", "registro_sha256": sha(registro()), "autoridad": {k: dep[k] for k in ("s5_package", "d7_tree", "run_class")},
            "codigo": {p: sha((A / p).read_bytes()) for p in CODIGO}, "puntos_U": {d: puntos_U_de(d) for d in ("G", "N")},
            "sred": {d: sha((T / "cierre_df_paso4_3_7_2026-10-05_lima1958" / ("demo/hito2/sred_%s_df.json" % d)).read_bytes()) for d in ("G", "N")},
            "config": config, "muestra_sha256": muestra_sha}


# ============================================================================================== plan
def plan(out, universos=False):
    """Plan de las 1728 afirmaciones SIN ejecutar: ruta, dependencias derivadas de la autoridad, cierre completo, sin duplicados.
    Con --universos, comprueba además que el universo de contextos de cada country/global es la SUMA (multiconjunto) de los de
    sus dependencias (solo contextos: sin cálculo de extremos)."""
    t0 = time.time()
    from codigo import extremos_G_df_v5 as E5      # paper2b aislado del área
    from codigo.demo import nucleo_v as N
    ctx = N.Contexto()
    reg = json.loads(registro())["afirmaciones"]
    N.need({c.claim_id for c in ctx.claims} == set(reg), "REGISTRO_Y_CONTEXTO_DISTINTOS")
    deps = dependencias(ctx.claims)
    t_ctx = round(time.time() - t0, 1)
    filas, por_ruta = [], Counter()
    for cid in sorted(reg):
        r = ruta_de(cid)
        por_ruta[r] += 1
        f = campos(cid)
        filas.append({"afirmacion": cid, "familia": f["fam"], "diseno": f["dis"], "menu": f.get("j"), "escenario": f.get("scen"),
                      "ruta": r, "dependencias": deps[cid], "sentidos": ["sup", "inf"], "estado": "no_ejecutado"})
    todas = cierre(list(reg), deps)
    usadas = Counter(x for ds in deps.values() for x in ds)
    comprob = {"cierre_igual_al_registro": set(todas) == set(reg), "sin_dependencias_duplicadas": all(len(set(d)) == len(d) for d in deps.values()),
               "hojas_ci_usadas_por_alguna_country": sum(1 for c in reg if campos(c)["fam"] == "ci" and usadas[c] > 0),
               "country_usadas_por_alguna_global": sum(1 for c in reg if campos(c)["fam"] == "c" and usadas[c] > 0),
               "dependencias_por_ruta": {r: dict(Counter(len(x["dependencias"]) for x in filas if x["ruta"] == r)) for r in sorted(por_ruta)},
               "cn_solo_hojas_d_domestic_unchanged": all(campos(h)["j"] == "d" and campos(h)["avail"] == "domestic_unchanged"
                                                         for x in filas if x["ruta"] == "agregacion_country_cn" for h in x["dependencias"]),
               "cf_hojas_d_df_f": all(sorted(campos(h)["j"] for h in x["dependencias"]) == ["d", "df", "f"] for x in filas if x["ruta"] == "agregacion_country_cf")}
    if universos:
        from codigo import extremos_G as EG
        uni = {"comprobadas": 0, "distintas": []}
        for d in ("G", "N"):
            ids = [c for c in reg if campos(c)["dis"] == d]
            st = EG.preparar(ctx, d, ids)
            ck = {c: Counter(E5.ctx_key(x) for x in st["univ"][c]) for c in ids}
            for c in ids:
                if campos(c)["fam"] == "ci":
                    continue
                suma = sum((ck[x] for x in deps[c]), Counter())
                uni["comprobadas"] += 1
                if ck[c] != suma:
                    uni["distintas"].append(c)
        comprob["universos"] = uni
    doc = {"etiqueta": N.ETIQUETA, "autoridad": "Claim del contexto S5 (paper2b.claims.derive; claims.py sha256 %s)" % sha((A / "integracion/src/paper2b/claims.py").read_bytes()),
           "afirmaciones": len(filas), "pares_afirmacion_sentido": 2 * len(filas), "por_ruta": dict(sorted(por_ruta.items())),
           "comprobaciones": comprob, "contexto_s": t_ctx, "segundos": round(time.time() - t0, 1), "filas": filas,
           "nota": "plan registrado SIN ejecutar: P1 (fase global) no está autorizada"}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    atomico(Path(out), (json.dumps(doc, indent=0, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps({k: doc[k] for k in ("afirmaciones", "pares_afirmacion_sentido", "por_ruta", "comprobaciones", "segundos")}, ensure_ascii=False))
    ok = comprob["cierre_igual_al_registro"] and comprob["sin_dependencias_duplicadas"] and comprob["cn_solo_hojas_d_domestic_unchanged"] and comprob["cf_hojas_d_df_f"]
    if universos:
        ok = ok and not comprob["universos"]["distintas"]
    return 0 if ok else 1


# ============================================================================================== checkpoints
class Corrida:
    def __init__(self, d: Path):
        self.d = Path(d)
        (self.d / "resultados").mkdir(parents=True, exist_ok=True)

    def evento(self, **kw):
        kw.update(t_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), pid=os.getpid())
        with open(self.d / "registro.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(kw, ensure_ascii=False) + "\n")

    def f(self, cid, s):
        return self.d / "resultados" / ("%s_%s.json" % (sha(cid.encode())[:24], s))

    def leer(self, cid, s):
        p = self.f(cid, s)
        if not p.exists():
            return None
        r = json.loads(p.read_bytes())
        if r.get("afirmacion") != cid or r.get("sentido") != s or sha(canon({k: v for k, v in r.items() if k != "contenido_sha256"})) != r.get("contenido_sha256"):
            raise SystemExit("CHECKPOINT_ALTERADO:%s:%s" % (cid, s))
        return r

    def terminal(self, cid, s):
        """Resultado REUTILIZABLE (convergido/detenido/error) o None si falta o está pendiente (no_ejecutado: se reevalúa)."""
        r = self.leer(cid, s)
        if r is None:
            return None
        if r["estado"] in TERMINALES:
            return r
        if r["estado"] not in PENDIENTES:
            raise SystemExit("ESTADO_DESCONOCIDO:%s:%s:%s" % (cid, s, r["estado"]))
        self.evento(evento="pendiente_reevaluado", afirmacion=cid, sentido=s, motivo=r.get("motivo"))
        return None

    def escribir(self, cid, s, r):
        r = dict(r, afirmacion=cid, sentido=s)
        r["contenido_sha256"] = sha(canon(r))
        atomico(self.f(cid, s), (json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8"))
        self.evento(evento="resultado", afirmacion=cid, sentido=s, estado=r["estado"])
        return r


def clave_ganador(sentido):
    """Regla de E13 / SEL-PASO4-B-v2: sup, mayor L; inf, menor U; desempate d < df < f, país alfabético, claim_id de la HOJA."""
    if sentido == "sup":
        return lambda x: (-x["L"], ORDEN_J[campos(x["hoja"])["j"]], campos(x["hoja"])["pais"], x["hoja"])
    return lambda x: (x["U"], ORDEN_J[campos(x["hoja"])["j"]], campos(x["hoja"])["pais"], x["hoja"])


def agregado_de(sentido, comps):
    """comps: [(id_componente, registro)] TERMINALES con G. Devuelve el agregado (G, estado, ganador, testigo)."""
    xs = []
    for h, r in comps:
        hoja = h if campos(h)["fam"] == "ci" else r["hoja_ganadora"]
        xs.append({"h": h, "hoja": hoja, "L": r["G"][0], "U": r["G"][1], "conv": r["estado"] == "convergido", "testigo": r.get("testigo")})
    if sentido == "sup":
        L, U = max(x["L"] for x in xs), max(x["U"] for x in xs)
    else:
        L, U = min(x["L"] for x in xs), min(x["U"] for x in xs)
    real = min(xs, key=clave_ganador(sentido))
    estado = "convergido" if (U - L <= T2_AGREGADO and all(x["conv"] for x in xs)) else "detenido"
    return {"G": [L, U], "brecha": U - L, "estado": estado, "componente_ganador": real["h"], "hoja_ganadora": real["hoja"],
            "testigo": real["testigo"]}


def agregar(C, cid, deps, ruta, hecho=lambda: None):
    """Agregado país por país (country sobre sus hojas; global sobre sus country). Reutiliza el terminal vigente; reevalúa el
    pendiente o el obsoleto (componente cambiado). Dependencia sin resultado terminal con G: no_ejecutado (pendiente)."""
    if not deps:
        raise RutaNoSoportada("AGREGADO_SIN_DEPENDENCIAS:%s" % cid)
    for s in ("sup", "inf"):
        comps = [(h, C.terminal(h, s)) for h in deps]
        firma = {h: (r or {}).get("contenido_sha256") for h, r in comps}
        previo = C.terminal(cid, s)
        if previo is not None:
            if previo.get("componentes_sha256") == firma:
                continue
            C.evento(evento="agregado_obsoleto_reevaluado", afirmacion=cid, sentido=s)
        sim = [h for h, r in comps if r is not None and r.get("simulacion")]
        rot = {"simulacion": "SIMULACION: depende de componentes simulados %s" % sim} if sim else {}
        faltan = [h for h, r in comps if r is None or "G" not in r]
        if faltan:
            C.escribir(cid, s, dict(rot, ruta=ruta, estado="no_ejecutado", motivo="dependencias sin resultado terminal con G: %s" % faltan,
                                    componentes=list(deps)))
            continue
        a = agregado_de(s, comps)
        C.escribir(cid, s, dict(a, ruta=ruta, componentes=list(deps), componentes_sha256=firma, **rot))
        hecho()


# ============================================================================================== ejecución
def ejecutar(dirc, muestra_p, opts):
    t0 = time.time()
    muestra_raw = Path(muestra_p).read_bytes()
    muestra = json.loads(muestra_raw)["afirmaciones"]
    tpa = float(opts[opts.index("--tope-afirmacion") + 1]) if "--tope-afirmacion" in opts else 300.0
    tpp = float(opts[opts.index("--tope-proceso") + 1]) if "--tope-proceso" in opts else 2100.0
    config = {"T2_G": 1e-4, "tope_afirmacion_s": tpa, "metodo": "v5 (extremos_G_df_v5 / muestra_G_df)", "politica_reanudacion": "terminales+pendientes v2"}
    if "--config-alterna" in opts:
        config["T2_G"] = 1e-3                     # identidad distinta: debe rechazarse ANTES del cálculo
    ident = identidad(sha(muestra_raw), config)
    C = Corrida(Path(dirc))
    fid = C.d / "identidad.json"
    if fid.exists():
        if "--reanudar" not in opts:
            raise SystemExit("CORRIDA_EXISTE_USE_REANUDAR")
        previa = json.loads(fid.read_bytes())
        if previa != json.loads(canon(ident)):
            C.evento(evento="reanudacion_rechazada", motivo="IDENTIDAD_DISTINTA",
                     diferencias=sorted(k for k in set(previa) | set(ident) if previa.get(k) != json.loads(canon(ident)).get(k)))
            print("RECHAZADO: CORRIDA_INCOMPATIBLE (antes de cualquier cálculo)")
            return 3
        C.evento(evento="reanudacion_compatible")
    else:
        if "--reanudar" in opts:
            raise SystemExit("CORRIDA_AUSENTE")
        atomico(fid, canon(ident))
        C.evento(evento="inicio", muestra=muestra)
    # ---- contexto (solo tras validar la identidad) y AUTORIDAD de dependencias, ANTES de cualquier cálculo
    from codigo import extremos_G_df_v5 as E5      # primero: inserta y comprueba el paper2b aislado del área
    from codigo import extremos_dfd as XD
    from codigo import extremos_G as EG
    from codigo.demo import nucleo_v as N
    from codigo.demo.cobertura_compartida import q_pot_exact
    from paper2b import cobertura as COV
    from paper2b.intervalos import Iv
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    N.need({c.claim_id for c in ctx.claims} == set(json.loads(registro())["afirmaciones"]), "REGISTRO_Y_CONTEXTO_DISTINTOS")
    try:
        deps = dependencias(ctx.claims)
        orden = cierre(muestra, deps)
        fuera = sorted(set(orden) - set(muestra))
        if fuera:
            raise RutaNoSoportada("MUESTRA_NO_CERRADA_POR_DEPENDENCIAS:%s" % fuera[:6])
        rutas = {c: ruta_de(c) for c in orden}
    except RutaNoSoportada as e:
        C.evento(evento="rechazo_antes_del_calculo", motivo=str(e))
        print("RECHAZADO: %s (antes de cualquier cálculo)" % e)
        return 4
    t_ctx = round(time.time() - t0, 1)
    hojas_df = [h for h in orden if campos(h)["fam"] == "ci" and campos(h)["j"] == "df"]
    # universos: country/global = suma (multiconjunto) de los de sus dependencias, ANTES del cálculo
    prep = {}
    for d in ("G", "N"):
        ids = [c for c in orden if campos(c)["dis"] == d]
        if not ids:
            continue
        st = EG.preparar(ctx, d, ids)
        for c in ids:
            if campos(c)["fam"] != "ci":
                u = Counter(E5.ctx_key(x) for x in st["univ"][c])
                v = sum((Counter(E5.ctx_key(x) for x in st["univ"][h]) for h in deps[c]), Counter())
                if u != v:
                    C.evento(evento="rechazo_antes_del_calculo", motivo="UNIVERSO_NO_ES_SUMA:%s" % c)
                    print("RECHAZADO: UNIVERSO_NO_ES_SUMA:%s" % c)
                    return 4
        if not [h for h in hojas_df if campos(h)["dis"] == d]:
            continue
        Gr = XD.grupo(d, "df")
        sred = E5.auth("PRV", "demo/hito2/sred_%s_df.json" % d)
        pplus = {p: float(v) for p, v in sred["punto_cota_inferior"].items() if p in COV.STRUCT}
        bxp = {p: (pplus[p], pplus[p]) for p in COV.STRUCT}
        root = {p: (st["axes"][p][0][0], st["axes"][p][-1][1]) for p in COV.STRUCT}
        puntos = []
        for base, rel, h_ in ident["puntos_U"][d]:
            raw = (T / base / rel).read_bytes()
            if sha(raw) != h_:
                raise SystemExit("PUNTOS_U_ALTERADOS:%s" % rel)
            for fila in json.loads(raw)["filas"]:
                if fila.get("admisible") and "U" in fila and not fila.get("incompatible"):
                    bx = {p: (fila["theta"][p], fila["theta"][p]) for p in COV.STRUCT}
                    puntos.append((fila["theta"], bx, fila["U"], fila["L_punto"], q_pot_exact(bx)))
        prep[d] = {"st": st, "Gr": Gr, "sred": sred, "pplus": pplus, "s_p": q_pot_exact(bxp), "s_max": q_pot_exact(root).hi, "puntos": puntos}
    xdd = E5.auth("XDD", "demo/extremos/extremos_G_d.json")
    can = E5.auth("CAN", "demo/extremos/extremos_G_f.json")
    prod = {d: E5.auth("PRV", "demo/hito2/produccion_inf_G_cid_%s.json" % d) for d in ("G", "N")}
    C.evento(evento="plan_de_la_muestra", orden=orden, dependencias={c: deps[c] for c in orden}, rutas=rutas, contexto_s=t_ctx)
    hechos = [0]
    it = int(opts[opts.index("--interrumpir-tras") + 1]) if "--interrumpir-tras" in opts else None

    def hecho():
        hechos[0] += 1
        if it is not None and hechos[0] >= it:
            C.evento(evento="interrumpido", tras=hechos[0])
            print(json.dumps({"interrumpido_tras": hechos[0]}))
            raise SystemExit(75)

    def ci_df(cid):
        d = campos(cid)["dis"]
        P = prep[d]
        st, Gr = P["st"], P["Gr"]
        cx = st["univ"][cid]
        ks = [(E5.k_iv(x), x) for x in cx]
        k_lo, c_lo = min(ks, key=lambda t_: t_[0].lo)
        k_hi, c_hi = max(ks, key=lambda t_: t_[0].hi)
        if C.terminal(cid, "sup") is None:
            U_sup = (Iv(P["sred"]["U"], P["sred"]["U"]) - k_lo * (1.0 - Iv(P["s_max"], P["s_max"]))).hi
            L_sup = (Iv(P["sred"]["L"], P["sred"]["L"]) - k_lo * (1.0 - P["s_p"])).lo
            C.escribir(cid, "sup", {"ruta": "calculo_v5_ci_df", "G": [L_sup, U_sup], "brecha": U_sup - L_sup,
                                    "estado": "convergido" if U_sup - L_sup <= E5.T2_G else "detenido",
                                    "testigo": {"punto": P["pplus"], "contexto": list(E5.ctx_key(c_lo)), "indice_contexto": cx.index(c_lo)}})
            hecho()
        if C.terminal(cid, "inf") is None:
            if "--doble-error" in opts and opts[opts.index("--doble-error") + 1] == cid:
                C.escribir(cid, "inf", {"ruta": "calculo_v5_ci_df", "estado": "error", "simulacion": "SIMULACION: error del componente forzado (--doble-error)"})
                hecho()
                return
            U_inf, arg = math.inf, None
            for th, bx, u2, l2, s in P["puntos"]:
                u = (Iv(u2, u2) - k_hi * (1.0 - s)).hi
                if u < U_inf:
                    U_inf, arg = u, (th, bx, u2, l2)
            presupuesto = 1e-3 if ("--doble-detencion" in opts and opts[opts.index("--doble-detencion") + 1] == cid) else tpa
            bb = E5.inf_bb(Gr["full"], st["fixed"], d, Gr["bd"], Gr["bf"], k_hi.hi, U_inf, presupuesto)
            conv = U_inf - bb["L"] <= E5.T2_G and bb["estado"] == "convergido"
            r = {"ruta": "calculo_v5_ci_df", "G": [bb["L"], U_inf], "brecha": U_inf - bb["L"], "estado": "convergido" if conv else "detenido",
                 "inf_bb": bb, "testigo": {"punto": arg[0], "contexto": list(E5.ctx_key(c_hi)), "indice_contexto": cx.index(c_hi)}}
            if presupuesto != tpa:
                r["simulacion"] = "SIMULACION: presupuesto del B&B forzado a 1e-3 s (--doble-detencion); ruta REAL de detención"
            C.escribir(cid, "inf", r)
            hecho()

    def ci_hist(h):
        d, j = campos(h)["dis"], campos(h)["j"]
        for s in ("sup", "inf"):
            if C.terminal(h, s) is not None:
                continue
            if j == "d":
                if s == "sup":
                    L, U = xdd["afirmaciones"][h]["sup_G"]
                    est, cita = xdd["afirmaciones"][h]["estado_sup"], "XDD demo/extremos/extremos_G_d.json afirmaciones/%s/sup_G" % h
                    punto = xdd["p_max"]
                else:
                    L, U = prod[d]["afirmaciones"][h]["inf_G"]
                    est, cita = prod[d]["afirmaciones"][h]["estado_inf"], "PRV demo/hito2/produccion_inf_G_cid_%s.json afirmaciones/%s/inf_G" % (d, h)
                    punto = prod[d]["afirmaciones"][h]["punto_cota_superior"]
            else:
                L, U = can["afirmaciones"][h][s + "_G"]
                est, cita = can["afirmaciones"][h]["estado"], "CAN demo/extremos/extremos_G_f.json afirmaciones/%s/%s_G" % (h, s)
                punto = can["puntos"]["sup_C2" if s == "sup" else "inf_C2"]
            C.escribir(h, s, {"ruta": "recuperacion_historica", "G": [L, U], "brecha": U - L, "estado": "convergido" if est == "convergida" else "detenido",
                              "cita": cita, "testigo": {"punto": punto}, "recalculado": False})
            hecho()

    for cid in orden:                                   # topológico: hojas, country, global; cada afirmación UNA vez
        if time.time() - t0 > tpp:
            for s in ("sup", "inf"):
                if C.terminal(cid, s) is None:
                    C.escribir(cid, s, {"ruta": rutas[cid], "estado": "no_ejecutado", "motivo": "tope de proceso (%.0f s)" % tpp})
            continue
        f = campos(cid)
        if f["fam"] == "ci":
            ci_df(cid) if f["j"] == "df" else ci_hist(cid)
        else:
            agregar(C, cid, deps[cid], rutas[cid], hecho)
    est = Counter()
    for cid in orden:
        for s in ("sup", "inf"):
            r = C.leer(cid, s)
            est[r["estado"] if r else "ausente"] += 1
    res = {"estados": dict(est), "afirmaciones": len(orden), "contexto_s": t_ctx, "segundos": round(time.time() - t0, 1)}
    C.evento(evento="fin", **res)
    print(json.dumps(res, ensure_ascii=False))
    return 0


# ============================================================================================== verificación
def historicos():
    """ci-df medidas y agregados cf históricos, autenticados por el inventario de su entrega."""
    hist, agr = {}, {}
    for base, rel_t in ((L754, "demo/hito2/extremos_G_df_v5_%s.json"), (L754, "demo/hito2/muestra_G_df_%s.json"),
                        ("validacion_eficiencia_h4_paso4_3_7_2026-10-09_lima0003", "demo/h4/inf_cidf/muestra_continuada_%s.json")):
        inv = json.loads((T / base / "audit/entrega.json").read_bytes())["files"]
        for d in ("G", "N"):
            rel = rel_t % d
            raw = (T / base / rel).read_bytes()
            if inv[rel]["sha256"] != sha(raw):
                raise SystemExit("HISTORICO_NO_AUTENTICADO:%s" % rel)
            doc = json.loads(raw)
            for cid, v in doc["ci_df"].items():
                hist.setdefault(cid, (base + "/" + rel, v))
            for cid, v in (doc.get("agregadas") or {}).items():
                agr.setdefault(cid, (base + "/" + rel, v))
    return hist, agr


def verificar(dirc, hojas_p, plan_p, out):
    """Reproducción (no copia) y coherencia de TODOS los resultados:
    - ci-df calculadas: G y testigo iguales a la medición histórica autenticada;
    - ci-d/ci-f recuperadas: G y testigo iguales a la hoja validada por E13 v4 (CENSO-v2);
    - agregados (country/global, cf y cn): componentes = dependencias del plan (autoridad); G, ganador y testigo RECALCULADOS
      desde los componentes de la corrida; firma de componentes vigente; y, si existe, G igual al agregado histórico (lima0754).
    Los resultados SIMULACION no cuentan como comparables."""
    hist, agr = historicos()
    hojas = {(x["hoja"], x["sentido"]): x for x in json.loads(Path(hojas_p).read_bytes())["filas"]}
    plan_deps = {x["afirmacion"]: x["dependencias"] for x in json.loads(Path(plan_p).read_bytes())["filas"]}
    C = Corrida(Path(dirc))
    recs = {}
    for p in sorted((Path(dirc) / "resultados").glob("*.json")):
        r = json.loads(p.read_bytes())
        recs[(r["afirmacion"], r["sentido"])] = C.leer(r["afirmacion"], r["sentido"])      # integridad del checkpoint
    filas = []
    for (cid, s), r in sorted(recs.items()):
        f = {"afirmacion": cid, "sentido": s, "ruta": r["ruta"], "estado": r["estado"], "simulacion": r.get("simulacion")}
        fam = campos(cid)["fam"]
        if r.get("simulacion") or "G" not in r:
            f["comparable"] = False
        elif r["ruta"] == "calculo_v5_ci_df":
            if cid in hist:
                fuente, v = hist[cid]
                f.update(comparable=True, fuente_historica=fuente, G_igual=r["G"] == v[s + "_G"],
                         testigo_igual=r["testigo"]["punto"] == v["testigo_" + s]["punto"] and r["testigo"]["indice_contexto"] == v["testigo_" + s]["indice_contexto"],
                         estado_historico=v["estado_" + s])
                f["ok"] = f["G_igual"] and f["testigo_igual"]
            else:
                f.update(comparable=False, motivo="sin medición histórica (no reproducción)")
        elif r["ruta"] == "recuperacion_historica":
            hj = hojas.get((cid, s))
            ok_h = hj is not None and hj["testigo"] == "definitivo"
            f.update(comparable=ok_h, G_igual_a_E13v4=ok_h and r["G"] == [hj["L"], hj["U"]],
                     testigo_igual_a_E13v4=ok_h and {k: float(x) for k, x in r["testigo"]["punto"].items() if k in hj["punto"]} == hj["punto"])
            f["ok"] = f["G_igual_a_E13v4"] and f["testigo_igual_a_E13v4"]
        elif fam in ("c", "g"):
            deps = plan_deps.get(cid)
            comps = [(h, recs.get((h, s))) for h in (deps or [])]
            f["comparable"] = True
            f["componentes_igual_al_plan"] = deps is not None and r.get("componentes") == deps
            f["firma_vigente"] = all(c is not None for _, c in comps) and r.get("componentes_sha256") == {h: c["contenido_sha256"] for h, c in comps}
            try:
                a = agregado_de(s, comps)
                f["G_recalculado_igual"] = a["G"] == r["G"]
                f["ganador_recalculado_igual"] = (a["hoja_ganadora"], a["componente_ganador"]) == (r.get("hoja_ganadora"), r.get("componente_ganador"))
                f["testigo_recalculado_igual"] = a["testigo"] == r.get("testigo")
                f["estado_recalculado_igual"] = a["estado"] == r["estado"]
            except (TypeError, KeyError, ValueError) as e:
                f.update(G_recalculado_igual=False, error_recalculo="%s: %s" % (type(e).__name__, e))
            if cid in agr:
                fuente, v = agr[cid]
                f.update(fuente_historica=fuente, G_igual_al_historico=r["G"] == v[s + "_G"])
            f["ok"] = all(f.get(k, False) for k in ("componentes_igual_al_plan", "firma_vigente", "G_recalculado_igual", "ganador_recalculado_igual",
                                                     "testigo_recalculado_igual", "estado_recalculado_igual")) and f.get("G_igual_al_historico", True)
        filas.append(f)
    comp = [x for x in filas if x.get("comparable")]
    ok = bool(comp) and all(x.get("ok") for x in comp)
    por = Counter((x["ruta"], bool(x.get("comparable")), bool(x.get("ok"))) for x in filas)
    doc = {"filas": filas, "resultados": len(filas), "comparables": len(comp), "verificados_ok": sum(1 for x in comp if x.get("ok")),
           "por_ruta": {"%s|comparable=%s|ok=%s" % k: v for k, v in sorted(por.items())}, "reproduccion_y_coherencia": ok}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    atomico(Path(out), (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps({k: doc[k] for k in ("resultados", "comparables", "verificados_ok", "por_ruta", "reproduccion_y_coherencia")}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "plan":
        raise SystemExit(plan(a[1], "--universos" in a))
    elif a[0] == "ejecutar":
        raise SystemExit(ejecutar(a[1], a[2], a[3:]))
    elif a[0] == "verificar":
        raise SystemExit(verificar(a[1], a[2], a[3], a[4]))
