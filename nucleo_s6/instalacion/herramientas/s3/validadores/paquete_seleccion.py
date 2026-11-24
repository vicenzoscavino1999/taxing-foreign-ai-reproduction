"""E14 CANDIDATO (CONTRATO PAQUETE 3.7, NO OFICIAL; copia aislada, no incorporada): RUTA COMÚN de verificación del
paquete por selección del paso 4. La usan el VALIDADOR (core.validar_paquete_seleccion), la REANUDACIÓN
(Ejecutor.cargar del flujo) y el subcomando `seleccion-paso4` de ejecutar_b.py. codigo/paquete_v2.py del área solo
reexporta este módulo (una sola ruta).

DEPENDENCIAS (explícitas):
  - núcleo candidato paper2b: contrato_paquete (reglas de contenido y matriz), rules (E12), convergencia, inversion,
    keys, external, model, supremum, tables;
  - INYECTADAS y AUTENTICADAS por sha256 al construir el Verificador (puerta `dependencias`): el flujo F
    (REGLA, SCHEMA, planificar, testigo_dict, codigo_manifiesto, CODIGO), el generador GC (derivación de la celda), el
    validador de la tabla v3 GE y el contexto S5 del área (ctx, ref). Cada módulo inyectado debe ser un archivo
    declarado en F.CODIGO del área, con el sha256 del manifiesto del productor actual; si no, DEPENDENCIA_NO_DECLARADA.
  - AUTORIDAD (puerta `autoridad`): S5 real no ficticio con las banderas oficiales en False; etiqueta NO OFICIAL. Esta
    ruta no emite freeze-run, no activa official() y rechaza (OFICIAL_NO_AUTORIZADO) cualquier petición oficial.

Lo que verifica (contrato por campo en paper2b.contrato_paquete.MATRIZ):
  1. ESQUEMA estricto antes de consumir; esquema del CONTRATO DE LA AUTORIDAD (Contracts.table) en cada tabla exportada.
  2. SELECCIÓN = salida exacta de su regla sobre testigos canónicos; plan = función pura de la selección.
  3. IDENTIDAD del productor AUTENTICADA (actual, o entrega anterior por su inventario) y su CONTRATO (v2 | v3).
  4. CLAVE E12 DERIVADA y cell_id recalculado; presencia por rules.e12_verificar_celda.
  5. CONTENIDO: techo (dominio del punto, valor del modelo en el punto, laterales/testigos, fila C2), λ_π, estado y
     valores de la confrontación, G, las 6 inversiones (filas del núcleo recalculadas; endógenas costosas por coherencia
     con hijas y convergencia), R1/R2.
  6. RESUMEN resultados.json = resumen canónico derivado de filas y autoridad; diagnósticos declarados.
  7. INVENTARIO de lote con cobertura exacta; filas ajenas; dictamen COMPLETO solo con referencia autenticada.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from paper2b import contrato_paquete as CP
from paper2b import rules as RULES

CIENTIFICOS = ("s5", "d7", "politica", "recibo", "grilla_sha256", "mapa_d4_sha256", "registro_sha256", "contrato_sha256", "tecnicas", "huella_entorno_sha256")
# paso 4 (candidato): con la autoridad S6 viva la identidad científica lleva el paquete S6 y su ANCLA externa en lugar del S5
CIENTIFICOS_S6 = ("s6", "ancla") + CIENTIFICOS[1:]
AUTORIDADES_ADMITIDAS = ("S5", "S6")


def cientificos(ctx):
    return CIENTIFICOS_S6 if getattr(getattr(ctx, "authority", None), "kind", None) == "S6" else CIENTIFICOS
DE_RONDA = ("etiqueta", "run_class", "codigo_demo_sha256", "autorizacion_sha256")
UK = ("run_id", "design_v", "country_id", "instrument_j", "availability_case_id", "omega_id", "eta_w_block", "policy_variant_id", "regime_id",
      "requirement_basis", "xi", "layer", "bound_variant", "external_cell_id", "national_state_sha256", "expected_macro_key_sha256")
CLAVE_E12 = ("cell_id", "frontier_id", "instrumento", "barras", "tasa", "run_geometry", "con_unidad", "omega_id")
EXPORTABLES = CP.TABLAS["v3"]
# Productores ANTERIORES autenticados por su inventario (paquetes inmutables; contrato v2: sin hijas ni fila C2).
PRODUCTORES_ANTERIORES = (
    {"area": "integracion_e12_paso4_3_7_2026-10-07_lima0746", "inventario": "fb9d1bc7d8996b9c0ac27d33e2877b98b201b701fe94fdb57887498c53013e68",
     "codigo": ("codigo/flujo_paso4.py", "codigo/generador_candidato_v2.py", "codigo/completitud_e12.py", "codigo/global_extreme_v3.py",
                "codigo/demo/celdas.py", "codigo/demo/nucleo_v.py", "codigo/demo/universo.py"),
     "run_class": "integration_e12_3_7", "etiqueta": "INTEGRACION E12 3.7 NO OFICIAL", "encargo": "autorizacion/ENCARGO_3_7_INTEGRACION_E12.txt", "contrato": "v2"},
    {"area": "validacion_paquete_paso4_3_7_2026-10-07_lima1045", "inventario": "088262423a9c2426810260fa50aec5118cd500023328c1ff85a7997acbb536b0",
     "codigo": ("codigo/flujo_paso4_v2.py", "codigo/flujo_paso4.py", "codigo/paquete_v2.py", "codigo/generador_candidato_v2.py", "codigo/completitud_e12.py",
                "codigo/global_extreme_v3.py", "codigo/demo/celdas.py", "codigo/demo/nucleo_v.py", "codigo/demo/universo.py"),
     "run_class": "package_validation_3_7", "etiqueta": "VALIDACION PAQUETE 3.7 NO OFICIAL", "encargo": "autorizacion/ENCARGO_3_7_VALIDACION_PAQUETE.txt", "contrato": "v2"},
    {"area": "contrato_paquete_paso4_3_7_2026-10-07_lima1210", "inventario": "a0cd00abe29b2ed7a36cea1e05ae4588ae6fd8f841f95460ce2a17ffdd267a82",
     "codigo": ("codigo/flujo_paso4_v2.py", "codigo/flujo_paso4.py", "codigo/paquete_v2.py", "codigo/generador_candidato_v2.py", "codigo/completitud_e12.py",
                "codigo/global_extreme_v3.py", "codigo/demo/celdas.py", "codigo/demo/nucleo_v.py", "codigo/demo/universo.py",
                "candidato/herramientas/s3/validadores/paquete_seleccion.py"),
     "run_class": "package_contract_3_7", "etiqueta": "CONTRATO PAQUETE 3.7 NO OFICIAL", "encargo": "autorizacion/ENCARGO_3_7_CONTRATO_PAQUETE.txt", "contrato": "v3"},
    {"area": "relaciones_contrato_paso4_3_7_2026-10-07_lima1442", "inventario": "27816a755d2a62806b27014929e4e816eb6f12b564b9e32eb41d09e333d61d83",
     "codigo": ("codigo/flujo_paso4_v2.py", "codigo/flujo_paso4.py", "codigo/paquete_v2.py", "codigo/generador_candidato_v2.py", "codigo/completitud_e12.py",
                "codigo/global_extreme_v3.py", "codigo/demo/celdas.py", "codigo/demo/nucleo_v.py", "codigo/demo/universo.py",
                "candidato/herramientas/s3/validadores/paquete_seleccion.py", "candidato/herramientas/b/unidades.py", "candidato/herramientas/b/contexto_s5.py"),
     "run_class": "contract_relations_3_7", "etiqueta": "RELACIONES CONTRATO 3.7 NO OFICIAL", "encargo": "autorizacion/ENCARGO_3_7_RELACIONES_CONTRATO.txt", "contrato": "v3",
     "globs": ("tmp/%s/candidato/herramientas/b/*.py", "tmp/%s/candidato/herramientas/s3/validadores/paquete_seleccion.py"),
     "productor": "candidato/herramientas/b/contexto_s5.py"},
    # VALIDACION EFICIENCIA H4 3.7: la ronda de integración H4 (paquetes A/B del piloto PIL2). Su contexto usó el manifiesto
    # de código POR CONTENIDO (codigo_productor) como código del productor: codigo_demo_sha256 = sha(canon(manifiesto)).
    {"area": "integracion_h4_paso4_3_7_2026-10-08_lima2128", "inventario": "281f05eea93651d9520ae3de111cfcee405d8f8a06dc347f8921ba8553725374",
     "codigo": ("candidato/herramientas/b/contexto_s5.py", "candidato/herramientas/b/generador_seleccion.py", "candidato/herramientas/b/seleccion_paso4.py",
                "candidato/herramientas/b/soporte_global.py", "candidato/herramientas/b/unidades.py",
                "candidato/herramientas/s3/validadores/e13_referencia.py", "candidato/herramientas/s3/validadores/paquete_seleccion.py"),
     "run_class": "integration_h4_3_7", "etiqueta": "INTEGRACION H4 3.7 NO OFICIAL", "encargo": "autorizacion/ENCARGO_3_7_INTEGRACION_H4.txt", "contrato": "v3",
     "demo_es_codigo": True, "productor": "candidato/herramientas/b/seleccion_paso4.py"},
    # CIERRE CACHE CUPOS H4 3.7: la ronda de validación y eficiencia (paquete A3b del piloto PIL3b, caché v1). Mismo tipo de
    # productor que lima2128 (manifiesto de código por contenido), con el almacén de techos v1 en su manifiesto.
    {"area": "validacion_eficiencia_h4_paso4_3_7_2026-10-09_lima0003", "inventario": "36d10e10084ccb86298c132b338fb649e328285cd61421fc671222845940cb04",
     "codigo": ("candidato/herramientas/b/contexto_s5.py", "candidato/herramientas/b/generador_seleccion.py", "candidato/herramientas/b/seleccion_paso4.py",
                "candidato/herramientas/b/soporte_global.py", "candidato/herramientas/b/unidades.py",
                "candidato/herramientas/s3/validadores/e13_referencia.py", "candidato/herramientas/s3/validadores/paquete_seleccion.py",
                "candidato/herramientas/b/techos_persistentes.py"),
     "run_class": "validacion_eficiencia_h4_3_7", "etiqueta": "VALIDACION EFICIENCIA H4 3.7 NO OFICIAL", "encargo": "autorizacion/encargo.txt", "contrato": "v3",
     "demo_es_codigo": True, "productor": "candidato/herramientas/b/seleccion_paso4.py"},
    # CACHE FINAL P0 H4 3.7: la ronda de cierre de caché y cupos (paquete P4, caché v2). Mismo tipo de productor.
    {"area": "cierre_cache_cupos_h4_paso4_3_7_2026-10-09_lima0652", "inventario": "e35a5d7fdcc0ff10614f0a5b0a764453b1a1a495abf0386e6a5bccf0c4d8e22d",
     "codigo": ("candidato/herramientas/b/contexto_s5.py", "candidato/herramientas/b/generador_seleccion.py", "candidato/herramientas/b/seleccion_paso4.py",
                "candidato/herramientas/b/soporte_global.py", "candidato/herramientas/b/unidades.py",
                "candidato/herramientas/s3/validadores/e13_referencia.py", "candidato/herramientas/s3/validadores/paquete_seleccion.py",
                "candidato/herramientas/b/techos_persistentes.py"),
     "run_class": "cierre_cache_cupos_h4_3_7", "etiqueta": "CIERRE CACHE CUPOS H4 3.7 NO OFICIAL", "encargo": "autorizacion/encargo.txt", "contrato": "v3",
     "demo_es_codigo": True, "productor": "candidato/herramientas/b/seleccion_paso4.py"},
)
BANDERAS_OFICIALES = ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")
# Reglas de selección admitidas. PILOTO: estratos país x menú (Perú principal; México y Colombia comparadores; Chile
# excluido), un testigo autenticado por estrato, fuera de la selección de demostración; desempate determinista por hash.
REGLA_DEMO, REGLA_PILOTO = "SEL-PASO4-DEMO-v1", "SEL-PASO4-PILOTO-v1"
# Piloto COMPLEMENTARIO de H4 (familias de costo no medidas): testigos df de a ALTA (los de ínfimo de G, tipos W1/W2 del
# plan v5), fuera de las selecciones DEMO y PILOTO. A: diseño N en PER, MEX y COL (moderados); B: diseño G en COL (exigente).
REGLA_COMP_A, REGLA_COMP_B = "SEL-PASO4-COMPLEMENTO-A-v1", "SEL-PASO4-COMPLEMENTO-B-v1"
REGLAS = (REGLA_DEMO, REGLA_PILOTO, REGLA_COMP_A, REGLA_COMP_B)
# paso 4 (candidato S6): REPRODUCCIÓN POR LISTA. La selección es la de una TAREA del plan de la corrida (unidades de las listas R2/R3
# fijadas por sha256) con los testigos AUTÉNTICOS de los manifiestos de bloque de su entrega original; NO es una regla de selección nueva.
REGLA_REPRO = "SEL-PASO4-REPRO-v1"
REGLAS = REGLAS + (REGLA_REPRO,)
INSTALACION_PS = Path(__file__).resolve().parents[3]
LISTAS_REPRO = {"R2": ("datos/paso4/lista_R2_testigos.json", "519ec91924cad7ce8b8cf29c407894926c912c9cb9196de3c626514303ae066f"),
                "R3": ("datos/paso4/lista_R3_candidata_B_NA.json", "7f8fed89a8d678fc18ec629b1e9326c8c776d03c566533f7b4a2a2c2a94853b2")}
CAMPOS_TESTIGO_REPRO = ("C2_en_punto", "K1_en_punto", "claim_id_hoja", "contexto", "diseno", "extreme_id", "indice_contexto", "instrumento_hoja",
                        "pais_hoja", "punto", "sentido")
COMPLEMENTO_ESTRATOS = {REGLA_COMP_A: (("PER", "N", "df"), ("MEX", "N", "df"), ("COL", "N", "df")), REGLA_COMP_B: (("COL", "G", "df"),)}
A_ALTA = 2.0          # umbral de «a alta» del estrato (los testigos de a = 1,1 ya están medidos)
PILOTO_ESTRATOS = (("PER", "df"), ("PER", "f"), ("MEX", "df"), ("MEX", "f"), ("COL", "df"), ("COL", "f"))
TOL_VALOR = 1e-12      # |R(punto)/B - C_2| relativo: misma evaluación en flotante que el productor (rama y cota)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def _fin(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


class Rechazo(Exception):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo, self.detalle = codigo, str(detalle)[:300]


def need(t, codigo, detalle=""):
    if not t:
        raise Rechazo(codigo, detalle)


def completar_testigo_c2(gen, ref, w):
    """rem40 — REGLA C2 HISTÓRICA (manifiestos de lima1533/lima2201: «K1 a calcular por la Referencia en el contexto del testigo»): el
    testigo C2 conserva punto, índice, afirmación, diseño, menú y país; su contexto y K1 los fija la Referencia en el contexto que
    localiza ese índice. No cambia el testigo: lo completa. (Por construcción, previas.contexto_coincide y K1_coincide son tautológicos
    para C2; el resto de las previas —índice en el universo, diseño/menú, país, ω exacto y admisible— sigue siendo una comprobación.)"""
    if all(c in w for c in CAMPOS_TESTIGO_REPRO) and isinstance(w.get("K1_en_punto"), list):
        return w
    cl = gen.claims[w["claim_id_hoja"]]
    if gen.U is None or any(s not in gen.runs for s in cl.support_sets):
        gen.preparar(sorted(set(getattr(gen, "_hojas_c2", [])) | {w["claim_id_hoja"]}))
    _, _, _, c = gen.localizar(cl, w["indice_contexto"])
    k1 = ref.K1({p: float(x) for p, x in w["punto"].items()}, c)
    return dict(json.loads(json.dumps(w)), contexto=json.loads(json.dumps(ref.ctx_key(c))), K1_en_punto=[k1.lo, k1.hi],
                compleccion="regla C2 histórica: contexto y K1 por la Referencia en el índice del testigo (rem40)")


def cargar_vinculo():
    """rem40: el módulo ÚNICO del vínculo plan/tarea<->unidad<->fuente<->original, desde ESTA instalación (nunca otro del sys.path)."""
    import importlib.util
    import sys as _sys
    p = INSTALACION_PS / "herramientas/b/vinculo_paso4.py"
    m = _sys.modules.get("vinculo_paso4")
    if m is None or Path(getattr(m, "__file__", "")).resolve() != p.resolve():
        spec = importlib.util.spec_from_file_location("vinculo_paso4", p)
        m = importlib.util.module_from_spec(spec)
        _sys.modules["vinculo_paso4"] = m
        spec.loader.exec_module(m)
    return m


# ================================================================================================ puertas
def puerta_autoridad(ctx):
    """Rechazos de la puerta de autoridad para el pipeline futuro: autoridad REAL S5 o S6 (paso 4: la viva es S6, verificada por
    from_s6 con el ancla externa), banderas oficiales en False, etiqueta NO OFICIAL. Esta ruta nunca habilita una corrida, un
    freeze-run ni una exportación oficial."""
    a = getattr(ctx, "authority", None)
    need(a is not None and getattr(a, "kind", None) in AUTORIDADES_ADMITIDAS and not getattr(a, "fictitious", True), "AUTORIDAD_NO_S5_NI_S6")
    for f in BANDERAS_OFICIALES:
        need(a.scope.get(f) is False, "BANDERA_OFICIAL_ACTIVA", f)
    need("NO OFICIAL" in str(ctx.identity.get("etiqueta")), "ETIQUETA_OFICIAL", ctx.identity.get("etiqueta"))


def exigir_corrida_oficial(*_a, **_k):
    """Punto de enganche del pipeline `official()` futuro: en este candidato SIEMPRE rechaza (sin D1–D6, S6, freeze-run
    ni autorización del autor)."""
    raise Rechazo("OFICIAL_NO_AUTORIZADO", "la ruta candidata no habilita corrida, freeze-run ni exportación oficial")


def puerta_dependencias(F, GC, GE, N, area, ctx=None):   # N: compatibilidad (None en la ruta integrada)
    """sha256 de cada dependencia INYECTADA; cada una debe ser un archivo declarado en F.CODIGO del área (el contexto: el
    módulo de la CLASE del contexto inyectado, p. ej. herramientas/b/contexto_s5.py)."""
    import sys as _sys
    out = {}
    mctx = _sys.modules[type(ctx).__module__] if ctx is not None else N
    for nombre, m in (("flujo", F), ("generador", GC), ("tabla_v3", GE), ("contexto", mctx)):
        p = Path(getattr(m, "__file__", "") or "").resolve()
        try:                          # nombre LÓGICO desde la instalación efectiva (área: <área>/candidato; S6: la raíz)
            rel = F.logico(p) if hasattr(F, "logico") else p.relative_to(Path(area).resolve()).as_posix()
        except ValueError:
            raise Rechazo("DEPENDENCIA_NO_DECLARADA", "%s fuera de la instalación: %s" % (nombre, p))
        need(rel in F.CODIGO, "DEPENDENCIA_NO_DECLARADA", "%s: %s no está en F.CODIGO" % (nombre, rel))
        out[rel] = sha(p.read_bytes())
    from paper2b import seleccion_valores as SV
    for nombre, m in (("contrato_paquete", CP), ("rules", RULES), ("seleccion_valores", SV)):
        p = Path(m.__file__).resolve()
        nucleo = (Path(F.CAND) / "src/paper2b") if hasattr(F, "CAND") else (Path(area) / "candidato/src/paper2b")
        need(p.parent == nucleo.resolve(), "DEPENDENCIA_NO_DECLARADA", "%s no es del núcleo candidato: %s" % (nombre, p))
        out["candidato/src/paper2b/" + p.name] = sha(p.read_bytes())
    return out


# ================================================================================================ esquemas
def _esq(x, e, ruta, GE):
    try:
        GE.comprobar(x, e, ruta)
    except GE.Rechazo as r:
        raise Rechazo("ESQUEMA", r.detalle)


def esquemas(F):
    hexr = "hex64"
    sel = ("dict", {"selection_rule_id": ("enum", list(REGLAS)), "alcance": "str", "universo_celdas": "int0", "filas": ("lista", "json", 1, 4004), "sello_sha256": hexr,
                    "tabla": ("dict", {"sha256": hexr, "validacion": "str", "seleccion_autenticada": "str"})})
    plan = ("dict", {"selection_rule_id": ("enum", list(REGLAS)), "sello_seleccion": hexr, "regla_plan": "str", "lotes": ("lista", "json", 1, 4004), "plan_sha256": hexr})
    ck = ("dict", {"schema": ("const", F.SCHEMA), "identidad": "json", "lotes": ("lista", "str", 1, 4004), "hechos": "json", "estado": ("enum", ["en_curso", "completo", "incompleto"]),
                   "historial": "json"})
    clave = ("dict", {"cell_id": "str", "frontier_id": "str", "instrumento": ("enum", ["d", "df", "f"]), "barras": ("intervalo",), "tasa": ("nulo_o", "float"),
                      "run_geometry": "bool", "con_unidad": "bool", "omega_id": "str"})
    return sel, plan, ck, clave


# ================================================================================================ verificador
class Verificador:
    """Autoridad, dependencias y derivaciones compartidas (una por proceso). `ref` = Referencia v3 con el contexto S5."""

    def __init__(self, ctx, ref, F, GC, raiz_fuentes=None):
        self.ctx, self.ref, self.F, self.GC = ctx, ref, F, GC
        self.GE, self.N, self.CE = GC.GE, getattr(GC, "N", None), GC.CE
        self.area = Path(F.AREA)
        # raíz de las entregas anteriores (productores autenticados por su inventario): explícita en la ruta integrada
        self.T = Path(raiz_fuentes) if raiz_fuentes is not None else self.area.parent
        puerta_autoridad(ctx)
        self.dependencias = puerta_dependencias(F, GC, GC.GE, self.N, self.area, ctx)
        from paper2b import convergencia as CV
        from paper2b import external as X
        from paper2b import inversion as INV
        from paper2b import keys as K
        from paper2b import model as M
        self.CV, self.X, self.INV, self.K, self.M = CV, X, INV, K, M
        self.esq = esquemas(F)
        self.cfg = ctx.cfg
        self.C = ctx.C
        self.tol_converge = float(ctx.cfg.sup.tol_converge)
        self.r1_tol = float(ctx.cfg.r1_geometry_tol)
        self.xtol = float(ctx.cfg.endogenous_xtol)
        self.claims = {c.claim_id: c for c in ctx.claims}
        self.gcells = {g.external_cell_id: g for g in ctx.inp.grid_cells}
        self._gen = None
        self._productores = None
        self._estados = {}
        self._tec_prod = None       # técnica del PRODUCTOR autenticado (config/método dependen de su run_class)

    # -------------------------------------------------------------------------------------------- selección y plan
    def seleccion_esperada(self, tabla_raw, regla=REGLA_DEMO):
        """Regla `regla` (la misma que produce) sobre la tabla v3 VALIDADA: DEMO (diseño x menú) o PILOTO (país x menú)."""
        need(regla in REGLAS, "SELECCION_NO_CANONICA", "regla desconocida %r" % regla)
        if regla == REGLA_REPRO:                 # paso 4 (S6): la entrada es la lista autenticada de una tarea de reproducción
            return self.seleccion_reproduccion(tabla_raw)
        F, GE, ref = self.F, self.GE, self.ref
        tv = GE.TestigosValidados(ref, json.loads(tabla_raw))
        cand = {}
        for e in tv.ids():
            w = F.testigo_dict(tv[e])
            k = json.dumps([w["claim_id_hoja"], sorted(w["punto"].items()), w["indice_contexto"]])
            cand.setdefault(k, {"w": w, "witness_of": []})["witness_of"].append(w["claim_id"] + ":" + w["sentido"])
        hojas_d = sorted({h for c, hs in ref.hojas.items() if GE.campos(c)["fam"] == "c" for h in hs if GE.campos(h)["j"] == "d"})
        for hh in hojas_d:
            for s in ("sup", "inf"):
                t = ref.hoja(hh, s)["testigo"]
                w = {x: t[x] for x in GE.TestigosValidados.CAMPOS}
                w.update(diseno=GE.campos(hh)["dis"], sentido=s, claim_id=hh, extreme_id=None)
                w = json.loads(json.dumps(w))
                k = json.dumps([hh, sorted(w["punto"].items()), w["indice_contexto"]])
                cand.setdefault(k, {"w": w, "witness_of": []})["witness_of"].append(hh + ":" + s)
        filas = []
        if regla == REGLA_DEMO:
            estratos = [(lambda v, dis=dis, j=j: v["w"]["diseno"] == dis and v["w"]["instrumento_hoja"] == j) for dis in ("G", "N") for j in ("d", "df", "f")]
            excluir = set()
        elif regla in COMPLEMENTO_ESTRATOS:
            estratos = [(lambda v, p=p, dis=dis, j=j: v["w"]["pais_hoja"] == p and v["w"]["diseno"] == dis and v["w"]["instrumento_hoja"] == j
                         and float(v["w"]["punto"]["a"]) > A_ALTA) for p, dis, j in COMPLEMENTO_ESTRATOS[regla]]
            excluir = {f["clave_celda"] for r_ in (REGLA_DEMO, REGLA_PILOTO) for f in self.seleccion_esperada(tabla_raw, r_)["filas"]}
        else:
            estratos = [(lambda v, p=p, j=j: v["w"]["pais_hoja"] == p and v["w"]["instrumento_hoja"] == j) for p, j in PILOTO_ESTRATOS]
            excluir = {f["clave_celda"] for f in self.seleccion_esperada(tabla_raw, REGLA_DEMO)["filas"]}
        for estrato in estratos:
            if True:
                cl_ = [(k, v) for k, v in cand.items() if estrato(v) and (v["w"]["instrumento_hoja"] != "df" or v["w"]["sentido"] == "sup" or regla in COMPLEMENTO_ESTRATOS)
                       and k not in excluir]
                if not cl_:
                    continue
                k, v = min(cl_, key=lambda kv: F.sha(("%s|%s" % (regla, kv[0])).encode()))
                cl = self.claims[v["w"]["claim_id_hoja"]]
                filas.append({"clave_celda": k, "reason": "witness_" + ("sup" if v["w"]["sentido"] == "sup" else "inf"), "witness_of": sorted(v["witness_of"]),
                              "testigo": v["w"], "grupo_ca2": {"preregistro": cl.claim_id.split(":")[1], "pais": cl.country_id, "diseno": cl.design,
                                                              "menu": cl.instrument_j, "caso_d4": cl.availability_case_id},
                              "fuente_testigo": "TestigosValidados" if v["w"].get("extreme_id") else "Referencia.hoja (hoja d componente)"})
        alcance = ("DEMOSTRACIÓN del flujo (no es S1 completa ni la selección de las 1728 afirmaciones)" if regla == REGLA_DEMO else
                   "PILOTO COMPLEMENTARIO H4 (%s): testigos df de a alta (familias de costo no medidas); medición técnica, no estimación global" % regla
                   if regla in COMPLEMENTO_ESTRATOS else
                   "PILOTO estratificado país x menú sobre testigos autenticados (Perú, México, Colombia; Chile excluido); fuera de la selección de "
                   "demostración; no es S1 ni estimación global")
        return {"selection_rule_id": regla, "alcance": alcance,
                "tabla": {"sha256": F.sha(tabla_raw), "validacion": "TestigosValidados (validar_tabla completa)", "seleccion_autenticada": GE.SELECCION},
                "universo_celdas": len(cand), "filas": filas}

    def validar_lista_reproduccion(self, lista):
        """Lista de una TAREA de reproducción (paso 4, S6). rem40 P4-VINCULO-TESTIGO: la comprobación es la del módulo ÚNICO
        herramientas/b/vinculo_paso4.py (el mismo de lista, preflight, productor, registro y comparación): plan sellado reproducido desde
        el presupuesto autenticado, tarea del plan, unidades EXACTAMENTE las de su asignación, identidad de la lista R2/R3 fijada y, por
        unidad, original autenticado por la autoridad histórica (su contrato) y fuente del manifiesto de bloque que es la de ESA unidad
        (id o alias de piloto) con testigo/definición igual al original. Nunca lanza."""
        cod, testigos, definiciones = [], {}, {}
        try:
            VP = cargar_vinculo()
            try:
                _, vin = VP.Vinculo(self.T).lista_valida(lista)
            except VP.VinculoError as r:
                raise Rechazo(r.codigo, r.detalle)
            for u, v in vin.items():
                (testigos if v["tipo"] == "testigo" else definiciones)[u] = v["definicion"]
        except Rechazo as r:
            cod.append(r.codigo)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            cod.append("LISTA_ILEGIBLE")
        return {"cumple": not cod, "codigos": cod, "unidades": testigos, "definiciones": definiciones}

    def seleccion_reproduccion(self, raw):
        """Selección canónica de una tarea de reproducción: una fila por unidad, con el testigo autenticado (misma clave de celda que
        las demás reglas) y su grupo CA2 derivado de la afirmación de la hoja."""
        lista = json.loads(raw)
        r = self.validar_lista_reproduccion(lista)
        need(r["cumple"], "LISTA_REPRODUCCION_NO_VALIDA", r["codigos"])
        need(not r["definiciones"], "PRODUCTOR_S2_S3_NO_CONECTADO", "%d unidades con definición estructural (S2/S3): vinculadas, sin productor S6 por lista"
             % len(r["definiciones"]))
        inc = sorted(u for u, w in r["unidades"].items() if not all(c in w for c in CAMPOS_TESTIGO_REPRO) or not isinstance(w.get("K1_en_punto"), list))
        ref_l = {x["unidad"]: x for x in lista["unidades"]}
        need(all(ref_l[u].get("familia") == "C2" for u in inc), "TESTIGO_INCOMPLETO", "%s" % [u for u in inc if ref_l[u].get("familia") != "C2"][:3])
        if inc:
            gc2 = self.GC.Generador(self.ctx, self.ref, self.GC.Compartido(activo=False))
            gc2.preparar(sorted({r["unidades"][u]["claim_id_hoja"] for u in inc}))
            for u in inc:
                r["unidades"][u] = completar_testigo_c2(gc2, self.ref, r["unidades"][u])
        filas = []
        for x in lista["unidades"]:
            w = json.loads(json.dumps(r["unidades"][x["unidad"]]))
            cl = self.claims[w["claim_id_hoja"]]
            filas.append({"clave_celda": json.dumps([w["claim_id_hoja"], sorted(w["punto"].items()), w["indice_contexto"]]), "reason": "reproduccion_" + lista["seleccion"],
                          "witness_of": sorted(x.get("witness_of") or []), "unidad": x["unidad"], "testigo": w,
                          "grupo_ca2": {"preregistro": cl.claim_id.split(":")[1], "pais": cl.country_id, "diseno": cl.design, "menu": cl.instrument_j,
                                        "caso_d4": cl.availability_case_id},
                          "fuente_testigo": "manifiesto de bloque autenticado: %s/%s" % (x["fuente"]["entrega"], x["fuente"]["manifiesto"])})
        need(len({f["clave_celda"] for f in filas}) == len(filas), "LISTA_CON_CELDAS_REPETIDAS")
        return {"selection_rule_id": REGLA_REPRO, "alcance": "REPRODUCCIÓN por lista (%s, tarea %s del plan %s): no es una selección nueva"
                % (lista["seleccion"], lista.get("tarea"), str(lista.get("plan_sha256"))[:16]),
                "tabla": {"sha256": sha(raw), "validacion": "lista de reproducción autenticada (lista fijada + manifiestos de bloque por inventario)",
                          "seleccion_autenticada": lista["seleccion"]}, "universo_celdas": len(filas), "filas": filas}

    def verificar_seleccion(self, pdir):
        sel_esq, plan_esq, _, _ = self.esq
        try:
            sel = json.loads((pdir / "seleccion.json").read_bytes())
            plan = json.loads((pdir / "plan.json").read_bytes())
        except (OSError, ValueError) as e:
            raise Rechazo("ESQUEMA", "selección o plan ilegibles: %s" % e)
        _esq(sel, sel_esq, "$seleccion", self.GE)
        _esq(plan, plan_esq, "$plan", self.GE)
        need(sel["sello_sha256"] == sha(canon({k: v for k, v in sel.items() if k != "sello_sha256"})), "SELECCION_ALTERADA", "sello")
        try:
            raw = (pdir / "entrada/global_extreme_v3.json").read_bytes()
        except OSError as e:
            raise Rechazo("ENTRADA_ALTERADA", e)
        need(sha(raw) == sel["tabla"]["sha256"], "ENTRADA_ALTERADA", "sha256 de la tabla distinto del sellado")
        if sel.get("selection_rule_id") == REGLA_REPRO:      # paso 4 (S6): la entrada es la lista autenticada de la tarea
            r = self.validar_lista_reproduccion(json.loads(raw))
            need(r["cumple"], "LISTA_REPRODUCCION_NO_VALIDA", r["codigos"])
        else:
            r = self.GE.validar_tabla(self.ref, json.loads(raw))
            need(r["cumple"], "E13_TABLA_NO_VALIDA", r["codigos"])
        esperada = self.seleccion_esperada(raw, sel["selection_rule_id"])
        dif = self.GE.diferencias(json.loads(canon(esperada)), json.loads(canon({k: v for k, v in sel.items() if k != "sello_sha256"})))
        need(not dif, "SELECCION_NO_CANONICA", "rutas distintas de la regla sobre testigos canónicos: %s" % dif[:6])
        need(plan == self.F.planificar(sel), "PLAN_NO_DERIVA_DE_LA_SELECCION")
        return sel, plan

    # -------------------------------------------------------------------------------------------- productor e identidad
    def productores(self):
        """{nombre: {codigo, producer_sha256, config_sha256, metodo_sha256, de_ronda, contrato}}: el código ACTUAL
        (contrato v3) y los de las entregas anteriores (contrato v2), autenticados por su inventario."""
        if self._productores is not None:
            return self._productores
        from herramientas.b import ejecutar_b as EB      # código ORIGINAL del proyecto (manifiestos de método y de código)
        F = self.F
        inp = self.ctx.inp
        from dataclasses import replace

        def cfg_sha(rc):
            return sha(self.K.canon(replace(self.cfg, run_class=rc).as_dict()) + bytes([10]))

        def met_sha(rc):
            return sha(self.K.canon(EB.method_manifest(replace(self.cfg, run_class=rc))) + bytes([10]))
        need(cfg_sha(self.ctx.identity["run_class"]) == self.ctx.technical["configuration_sha256"] == inp.algorithm_config_sha256,
             "DERIVACION", "la configuración no se reproduce desde la autenticada")
        need(met_sha(self.ctx.identity["run_class"]) == self.ctx.technical["method_sha256"], "DERIVACION", "el método no se reproduce")
        out = {"actual": {"codigo": F.codigo_manifiesto(), "producer_sha256": inp.producer_sha256, "config_sha256": inp.algorithm_config_sha256,
                          "metodo_sha256": self.ctx.technical["method_sha256"], "de_ronda": {k: self.ctx.identity[k] for k in DE_RONDA}, "contrato": "v3"}}
        T = self.T
        for pa in PRODUCTORES_ANTERIORES:
            base = pa["area"]
            P = T / base
            try:
                inv_raw = (P / "audit/entrega.json").read_bytes()
            except OSError:
                continue
            if sha(inv_raw) != pa["inventario"]:
                continue
            files = json.loads(inv_raw)["files"]

            def autent(rel, files=files, P=P):
                b = (P / rel).read_bytes()
                need(rel in files and files[rel]["sha256"] == sha(b), "PRODUCTOR_NO_AUTENTICADO", rel)
                return b
            fs = sorted((P / "candidato/src/paper2b").glob("*.py"))
            need(sorted("candidato/src/paper2b/" + f.name for f in fs) == sorted(x for x in files if x.startswith("candidato/src/paper2b/") and x.endswith(".py")
                                                                                   and x.count("/") == 3), "PRODUCTOR_NO_AUTENTICADO", "núcleo")
            nuc = sha(b"".join(f.name.encode() + b"\0" + autent("candidato/src/paper2b/" + f.name) for f in fs))
            cod = {"nucleo_candidato_sha256": nuc, "archivos": {r: sha(autent(r)) for r in pa["codigo"]}}
            if pa.get("demo_es_codigo"):         # el «código demo» de la identidad ES el manifiesto por contenido autenticado arriba
                demo_manifest = cod
            else:
                demo_manifest = EB.code_manifest(T.parent, tuple(g % base for g in pa.get("globs", ("tmp/%s/codigo/demo/*.py",))))
                need(all(files.get(k.split(base + "/", 1)[-1], {}).get("sha256") == v for k, v in _hashes_manifiesto(demo_manifest).items()), "PRODUCTOR_NO_AUTENTICADO", "demo")
            out[base] = {"codigo": cod, "producer_sha256": sha(autent(pa.get("productor", "codigo/demo/nucleo_v.py"))), "config_sha256": cfg_sha(pa["run_class"]),
                         "metodo_sha256": met_sha(pa["run_class"]), "contrato": pa["contrato"],
                         "de_ronda": {"etiqueta": pa["etiqueta"], "run_class": pa["run_class"], "codigo_demo_sha256": sha(self.K.canon(demo_manifest)),
                                      "autorizacion_sha256": sha(autent(pa["encargo"]))}}
        self._productores = out
        return out

    def verificar_identidad(self, ident, sel, plan):
        need(isinstance(ident, dict), "ESQUEMA", "identidad no es objeto")
        prods = self.productores()
        prod = next((n for n, p in prods.items() if json.loads(canon(ident.get("codigo"))) == json.loads(canon(p["codigo"]))), None)
        need(prod is not None, "IDENTIDAD", "código productor no autenticado")
        aut = ident.get("autoridad")
        need(isinstance(aut, dict), "IDENTIDAD", "autoridad ausente")
        for k in cientificos(self.ctx):
            esperado = self.ctx.identity[k]
            if k == "tecnicas":       # la configuración incluye run_class: la del PRODUCTOR, derivada (no leída de la salida)
                esperado = dict(esperado, configuration_sha256=prods[prod]["config_sha256"], method_sha256=prods[prod]["metodo_sha256"])
            need(json.loads(canon(aut.get(k))) == json.loads(canon(esperado)), "IDENTIDAD", "autoridad científica distinta: %s" % k)
        for k, v in prods[prod]["de_ronda"].items():
            need(aut.get(k) == v, "IDENTIDAD", "campo de ronda del productor distinto: %s" % k)
        need(set(aut) == set(cientificos(self.ctx)) | set(DE_RONDA), "IDENTIDAD", "claves de la autoridad")
        need(json.loads(canon(ident.get("sup"))) == json.loads(canon(self.cfg.sup.as_dict())), "IDENTIDAD", "SupConfig")
        need(ident.get("run_class") == prods[prod]["de_ronda"]["run_class"], "IDENTIDAD", "run_class")
        need(ident.get("tabla_sha256") == sel["tabla"]["sha256"] and ident.get("sello_seleccion") == sel["sello_sha256"]
             and ident.get("plan_sha256") == plan["plan_sha256"], "IDENTIDAD", "tabla, sello o plan")
        need(set(ident) == {"autoridad", "tabla_sha256", "sello_seleccion", "plan_sha256", "codigo", "sup", "run_class"}, "IDENTIDAD", "claves de identidad")
        self._tec_prod = {"configuration_sha256": prods[prod]["config_sha256"], "method_sha256": prods[prod]["metodo_sha256"]}
        inp = self.ctx.inp
        run_id = "BRUN-" + self.K.H({"d7": inp.d7.manifest["tree_sha256"], "config": prods[prod]["config_sha256"], "producer": prods[prod]["producer_sha256"],
                                      "contract": inp.contract_sha256})[:24]
        return prod, run_id, prods[prod]["contrato"]

    # -------------------------------------------------------------------------------------------- derivación de la celda
    def generador(self, sel):
        if self._gen is None:
            gen = self.GC.Generador(self.ctx, self.ref, self.GC.Compartido(activo=False))
            gen.preparar(sorted({f["testigo"]["claim_id_hoja"] for f in sel["filas"]}))
            self._gen = gen
        return self._gen

    def derivar(self, sel, fila, run_id, lote_id=None):
        """Clave E12, requisitos, entradas de los recálculos y base del resumen canónico de la celda, desde selección +
        autoridad + configuración (no desde la salida)."""
        gen = self.generador(sel)
        w = self.GE.congelar(fila["testigo"])
        ok, pre, dd = gen.previas(w)
        need(ok, "DERIVACION", "previas falsas: %s" % pre)
        cl, sid, meta, oid = dd["cl"], dd["sid"], dd["meta"], dd["oid"]
        r = gen.runs[sid]
        v = r.omegas[oid]["values"]
        j, case, pais, design = cl.instrument_j, cl.availability_case_id, meta["pais"], cl.design
        fid = "FRN:" + self.K.H({"r": run_id, "d": design, "c": pais, "j": j, "a": case, "o": oid, "t": "TAU:%s:%s" % (sid, j)})[:40]
        rate = r.inp.d7.rates.get(pais)
        tasa = float(rate["value"]) if (rate is not None and rate.get("status") == "verified") else None
        g = self.gcells[meta["celda_externa"]["id"]]
        t = fila["testigo"]
        # clave estructural con la técnica del PRODUCTOR (su configuración y su método dependen de su run_class)
        tec = dict(r.inp.technical, **self._tec_prod) if self._tec_prod else r.inp.technical
        payload = self.K.structural(v, r.C.K, r.units, design, j, v["bar_tau_d"], v["bar_tau_f"], r.inp.theory[2], tec)
        skey = r.C.key("structural", payload)
        frontera = {"frontier_id": fid, "run_id": run_id, "design_v": design, "country_id": pais, "instrument_j": j, "availability_case_id": case,
                    "availability_matrix_hash": r.inp.availability_matrix_hash, "omega_id": oid, "structural_key_sha256": skey,
                    "tau_domain_id": "TAU:%s:%s" % (sid, j), "structural_key_payload": payload}
        base = {"clave_celda": fila["clave_celda"], "extreme_id": t["extreme_id"], "claim_id_hoja": t["claim_id_hoja"], "indice_contexto": t["indice_contexto"],
                "precomprobaciones": pre, "set_id": sid, "omega_id": oid, "pais": pais, "diseno": design, "instrumento": j, "caso": case,
                "estado_nacional": meta["estado_nacional"], "macro": meta["macro"], "celda_externa": meta["celda_externa"],
                "clave_estructural": skey, "frontier_id": fid}
        if lote_id is not None:
            base["etiqueta"] = "%s:%s-%s-%s" % (lote_id, t["diseno"], t["instrumento_hoja"], fila["grupo_ca2"]["pais"])
        sts = [x for x in r.states_for(r.omegas[oid], pais) if self.GC.state_meta(x) == meta["estado_nacional"]]
        need(len(sts) == 1, "DERIVACION", "estado nacional no único: %d" % len(sts))
        return {"set": sid, "omega_id": oid, "frontier_id": fid, "ceiling_id": "CEI:" + fid[4:], "instrumento": j, "pais": pais, "diseno": design, "caso": case,
                "estado_nacional": sts[0], "contexto_macro": None if sts[0].channel == "strict" else (design, j, case),
                "barras": [float(v["bar_tau_d"]), float(v["bar_tau_f"])], "tasa": tasa, "run_geometry": bool(self.cfg.run_geometry), "con_unidad": True,
                "run_id": run_id, "gcell": g, "bound": cl.bound_variant, "y": float(v["gain_share"]), "dme_gai": r.inp.dme_gai, "testigo": t,
                "tol_root": float(r.tol_root), "run": r, "valores": v, "base_resumen": base, "frontera": frontera}

    def tecnica_productor(self):
        return dict(self.ctx.technical, **self._tec_prod) if self._tec_prod else dict(self.ctx.technical)

    def payload_condicional(self, st, om, block, context, technical):
        """macro-ca2-v2 desde las tablas del bundle AUTENTICADO del proveedor S5 (herramientas.b.nacional.Providers), con la
        técnica del productor. Misma construcción que Providers.conditional_key SIN validate_key (validación completa del
        bundle, evidencia del productor ya exigida al producir)."""
        prov = self.ctx.prov
        preg, c = st.preregistration_id, st.country_id
        need(context is not None, "DERIVACION", "contexto de celda ausente para la clave condicional")
        b, raw, tab = prov._bundle(preg)
        label = "{}-{}-{}".format(*context)
        _, row0 = prov._key_cache[("row", preg, c, st.anchor_year, st.edition)]
        rows = [r for r in tab["ca2_inputs"] if r["country_id"] == c and r["anchor_year"] == st.anchor_year
                and r["d6_vector_id"] == row0["d6_vector_id"] and r["case_id"].endswith(":" + label)]
        need(len(rows) == 1, "DERIVACION", "fila condicional %s:%s:%s" % (preg, c, label))
        case = next(x for x in tab["ca2_cases"] if x["case_id"] == rows[0]["case_id"])
        vectors = {v["vector_id"]: v for v in tab["ca2_vectors"]}
        return self.K.macro_ca2_v2(b["sha256"], case, c, rows[0], vectors, om["common_sha"], block, prov.protocol, technical)

    def f_en(self, der, K1):
        """f(τ_d, τ_f) = R/B_pot - K1 con el modelo y el estado del productor (Run.cs_function del núcleo)."""
        self.valor_en(der)
        st = self._estados[(id(der["run"]), der["omega_id"], der["diseno"])]
        mod, design = der["run"].model, der["diseno"]
        return lambda td, tf: mod.evaluate(st, td, tf, design).R / st.B_pot - K1

    def valor_en(self, der):
        """C_2 en un punto: R(τ_d, τ_f)/B_pot con el ESTADO del modelo del productor para ω (evaluación puntual)."""
        r, v, design = der["run"], der["valores"], der["diseno"]
        k = (id(r), der["omega_id"], design)
        if k not in self._estados:
            from paper2b.run import _to_state_prim
            self._estados[k] = r.model.state(_to_state_prim(v))
        st = self._estados[k]
        return lambda td, tf: self.M.revenue(st, td, tf, design) / st.B_pot


def _hashes_manifiesto(m):
    out = {}
    fs = m.get("files", m) if isinstance(m, dict) else m
    if isinstance(fs, dict):
        for k, v in fs.items():
            out[k] = v["sha256"] if isinstance(v, dict) else v
    else:
        for e in fs:
            out[e.get("path") or e.get("relative_path")] = e["sha256"]
    return out


# ================================================================================================ contenido de la celda
def verificar_celda(V, rows, der, c, contrato):
    """(estado, motivos) de UNA celda: completa | incompleta | invalida, con presencia (rules.e12_verificar_celda) y
    contenido (paper2b.contrato_paquete)."""
    mot_inv, mot_inc = [], []
    inval, incomp = mot_inv.append, mot_inc.append
    _, _, _, clave_esq = V.esq
    ce = c.get("clave_E12")
    try:
        _esq(ce, clave_esq, "$clave_E12", V.GE)
    except Rechazo as e:
        return "invalida", ["clave_E12: " + e.detalle]
    for k in CLAVE_E12[1:]:
        if json.loads(canon(ce[k])) != json.loads(canon(der[k])):
            inval("clave_E12.%s %r distinta de la derivada %r" % (k, ce[k], der[k]))
    cid, fid = ce["cell_id"], der["frontier_id"]
    comp = RULES.e12_verificar_celda(rows, cid, fid, instrumento=der["instrumento"], barras=tuple(der["barras"]), tasa=der["tasa"],
                                     run_geometry=der["run_geometry"], con_unidad=der["con_unidad"], omega_id=der["omega_id"])
    (mot_inv if comp["estado"] == "invalida" else mot_inc).extend(comp["motivos"])
    if comp["estado"] == "invalida":
        return "invalida", mot_inv
    f1 = lambda t, **k: [x for x in rows.get(t, []) if all(x.get(a) == b for a, b in k.items())]  # noqa: E731
    cx, te, cf = f1("cell_context", cell_id=cid)[0], f1("capture_ceiling_result", frontier_id=fid)[0], f1("confrontation_result", cell_id=cid)[0]
    mac = f1("lambda_pi_envelope", macro_id=cf.get("macro_id"))[0]
    g = der["gcell"]
    # ---- contexto y cell_id recalculado
    uk = {"run_id": der["run_id"], "design_v": der["diseno"], "country_id": der["pais"], "instrument_j": der["instrumento"], "availability_case_id": der["caso"],
          "omega_id": der["omega_id"], "eta_w_block": mac.get("eta_w_block"), "policy_variant_id": g.policy_variant_id, "regime_id": g.regime_id,
          "requirement_basis": g.requirement_basis, "xi": g.xi, "layer": g.layer, "bound_variant": der["bound"], "external_cell_id": g.external_cell_id,
          "national_state_sha256": mac.get("national_state_sha256"), "expected_macro_key_sha256": mac.get("macro_key_sha256")}
    if cid != "CEL:" + V.K.H(uk)[:44]:
        inval("cell_id no se recalcula desde su contexto derivado")
    for k in UK:
        if k != "xi" and cx.get(k) != uk[k]:
            inval("cell_context.%s distinto del derivado" % k)
    # ---- frontera: contexto y clave estructural derivados (técnica del productor)
    fx = f1("frontier_context", frontier_id=fid)
    if len(fx) != 1 or json.loads(canon(fx[0])) != json.loads(canon(der["frontera"])):
        inval("frontier_context distinto del derivado (clave estructural, dominio TAU o contexto)")
    # ---- techo: dominio, valor en el punto, laterales/testigos, fila C2
    if te.get("ceiling_id") != der["ceiling_id"] or te.get("instrument_available") is not True:
        inval("techo: ceiling_id o disponibilidad distintos de los derivados")
    e = {"menu": der["instrumento"], "barras": der["barras"], "tol_converge": V.tol_converge, "contrato": contrato, "certificado": bool(der["run"].model.certified),
         "valor_en": V.valor_en(der), "tol_valor": TOL_VALOR}
    a, b = CP.verificar_techo(te, rows, e)
    mot_inv.extend(a)
    mot_inc.extend(b)
    st = te.get("computation_status")
    # ---- λ_π y confrontación: estado derivado; valores recalculados
    if not (mac.get("omega_id") == der["omega_id"] and mac.get("country_id") == der["pais"] and mac.get("admissible") is True and _fin(mac.get("lambda_pi"))
            and mac.get("computation_status") == "complete"):
        inval("fila λ_π incoherente con la celda derivada")
    r_ = der["run"]
    try:
        esp = CP.macro_esperada(r_, r_.omegas[der["omega_id"]], der["omega_id"], der["pais"], der["estado_nacional"], der["contexto_macro"], der["run_id"],
                                V.tecnica_productor(), V.payload_condicional)
        a, b = CP.verificar_macro(rows, mac, esp, r_, der["omega_id"], V.tecnica_productor())
    except Rechazo as x:
        a, b = ["fila λ_π no derivable: %s" % x.detalle], []
    mot_inv.extend(a)
    mot_inc.extend(b)
    st_cf = "complete" if st == "complete" else "incomplete"     # disponible y admisible (exigidos arriba)
    if cf.get("computation_status") != st_cf:
        inval("confrontación en %r; el estado derivado del techo es %r" % (cf.get("computation_status"), st_cf))
    K1 = None
    try:
        K1 = V.X.K1(g.Q(der["bound"]), der["dme_gai"], mac["lambda_pi"], der["y"])
    except Exception as x:  # noqa: BLE001
        inval("K1 no recalculable: %s" % x)
    if st_cf == "complete" and K1 is not None and not mot_inv:
        if cf.get("K_comp_1") != K1 or cf.get("C_2") != te["C_2"] or cf.get("G") != te["C_2"] - K1:
            inval("confrontación: K1, C2 o G distintos de los recalculados")
        err = te["numerical_error"]
        G = te["C_2"] - K1
        ver = "factible" if G - err >= V.CV.EPS_ECON else ("infactible" if G + err <= -V.CV.EPS_ECON else "inconcluso")
        if cf.get("verdict") != ver:
            inval("veredicto %s distinto del recalculado %s" % (cf.get("verdict"), ver))
        w = der["testigo"]
        if not (w["K1_en_punto"][0] - V.GC.TOL_K1 <= K1 <= w["K1_en_punto"][1] + V.GC.TOL_K1 and te["C_2"] + err >= w["C2_en_punto"][0] and te["C_2"] - err <= w["C2_en_punto"][1]):
            inval("poscomprobación falsa (K1 ∉ testigo o C2 ∩ certificado = ∅)")
        fg = V.CV.fila_G(cid, C2=te["C_2"], err_C2=err, error_kind="certified_bound", ceiling_status=st, K1=K1, evidence_ref=None)
        eg = f1("convergence_result", quantity_id="G:" + cid)[0]
        dif = [k for k in V.CV.COLUMNAS if k != "evidence_ref" and json.loads(canon(eg.get(k))) != json.loads(canon(fg.get(k)))]
        if dif:
            inval("evidencia G distinta de la recalculada en %s" % dif)
        elif fg["status"] != "pass":
            incomp("evidencia G en %s (%s)" % (fg["status"], fg.get("motivo")))
    elif st_cf != "complete":
        if not (cf.get("verdict") == "no_verdict" and cf.get("G") is None and cf.get("C_2") is None and cf.get("K_comp_1") is None and cf.get("reason_code")):
            inval("confrontación no completa con valores o sin motivo")
        incomp("confrontación %s" % cf.get("computation_status"))
    if cf.get("run_readiness_flag") is not False or cf.get("ceiling_id") != der["ceiling_id"] or cf.get("sup_not_attained") != te.get("sup_not_attained"):
        inval("confrontación: readiness, ceiling_id o sup_not_attained distintos")
    # ---- inversiones (filas del núcleo recalculadas; endógenas costosas por coherencia)
    if K1 is not None:
        r = der["run"]
        ei = {"status": st_cf, "N": g.Q(der["bound"]) + der["dme_gai"], "C2": te.get("C_2"), "lam": mac.get("lambda_pi"), "y": der["y"], "K1": K1,
              "gain_support": tuple(float(x) for x in r.inp.d7.interval(der["set"], "gain_share")), "targets": r.inp.supplier_targets.get(der["set"]),
              "mapping": r.inp.external_factor_mapping is not None, "run_endogenous": bool(r.cfg.run_endogenous), "menu": der["instrumento"],
              "set": der["set"], "pais": der["pais"], "con_unidad": der["con_unidad"], "tol_root": der["tol_root"], "xtol": V.xtol, "contrato": contrato,
              "grid_sha256": r.inp.grid_sha256}
        a, b = CP.verificar_inversiones(rows, cid, r, ei)
        mot_inv.extend(a)
        mot_inc.extend(b)
    # ---- GEOMETRÍA (relaciones locales, todas las ramas) y EVIDENCIA (v3)
    if der["run_geometry"] and K1 is not None and st_cf == "complete":
        eg_ = {"menu": der["instrumento"], "barras": der["barras"], "f": V.f_en(der, K1), "tol_root": der["tol_root"], "tasa": der["tasa"], "r1_tol": V.r1_tol,
               "vacio_demostrado": bool(der["run"].model.certified) and _fin(te.get("C_2")) and _fin(te.get("numerical_error"))
               and K1 > te["C_2"] + te["numerical_error"]}
        a, b = CP.verificar_geometria(rows, cid, eg_)
        mot_inv.extend(a)
        mot_inc.extend(b)
        if contrato == "v3":
            a, b = CP.verificar_evidencia(rows, cid, der["ceiling_id"], eg_)
            mot_inv.extend(a)
            mot_inc.extend(b)
    # ---- CHECKER DEL NÚCLEO (v3: con las hijas y la evidencia numérica exportadas)
    if contrato == "v3" and not mot_inv:
        r = der["run"]
        try:
            err_ch = CP.checker_nucleo(V.C, r.inp.d7, CP.filas_de_celda(rows, cid, fid, "v3"), r.inp.tolerances)
        except Exception as x:  # noqa: BLE001
            err_ch = ["Checker no ejecutable: %s: %s" % (type(x).__name__, x)]
        for m in err_ch[:4]:
            inval("Checker del núcleo: " + m)
    # ---- R1 y R2
    if der["run_geometry"]:
        r1 = f1("r1_summary", cell_id=cid)[0]
        if r1.get("computation_status") == "complete":
            gb, rb = r1.get("geometry_error_bound"), r1.get("residual_bound")
            if not (_fin(gb) and 0 <= gb <= V.r1_tol and _fin(rb) and 0 <= rb <= der["tol_root"] and r1.get("topology_stable") is True):
                inval("R1 complete con cotas %r/%r fuera de r1_geometry_tol/tol_root o topología inestable" % (gb, rb))
            ev = f1("convergence_result", quantity_id="R1:" + cid)[0]
            esper = {"method_id": "certified_contour", "topology_before": r1.get("n_components"), "topology_after": r1.get("n_components"), "coverage_complete": True,
                     "status": "pass", "change_bound": gb, "tolerance": V.r1_tol, "unit": "tau", "level_before": 0, "level_after": 1, "verdict_changes": 0,
                     "value_before": None, "value_after": None, "result_ref": "r1_summary:" + json.dumps({"cell_id": cid}, sort_keys=True, separators=(",", ":"))}
            dif = [k for k, x in esper.items() if json.loads(canon(ev.get(k))) != json.loads(canon(x))]
            if dif:
                inval("evidencia R1 distinta de la exigida en %s" % dif)
            for vx in f1("r1_vertices", cell_id=cid):
                if not (_fin(vx.get("residual")) and abs(vx["residual"]) <= der["tol_root"]):
                    inval("vértice R1 con residuo fuera de tol_root")
                    break
        for s in f1("r2_sections", cell_id=cid):
            if s.get("computation_status") == "complete":
                for rt in f1("r2_roots", cell_id=cid, section_id=s.get("section_id")):
                    if not (_fin(rt.get("residual")) and abs(rt["residual"]) <= der["tol_root"]):
                        inval("raíz R2 con residuo fuera de tol_root")
                        break
    if mot_inv:
        return "invalida", mot_inv + mot_inc
    return ("incompleta" if mot_inc else "completa"), mot_inc


def resumen_esperado(V, rows, der, c):
    """Resumen canónico de la celda: E12 sobre las filas exportadas, poscomprobaciones recalculadas y la fórmula de
    estado del productor (E12 + poscomprobaciones)."""
    cid = der["base_resumen"].get("cell_id") or c["clave_E12"]["cell_id"]
    fid = der["frontier_id"]
    comp = RULES.e12_verificar_celda(rows, cid, fid, instrumento=der["instrumento"], barras=tuple(der["barras"]), tasa=der["tasa"],
                                     run_geometry=der["run_geometry"], con_unidad=der["con_unidad"], omega_id=der["omega_id"])
    filas = {t: [x for x in rows.get(t, []) if (x.get("cell_id") == cid if t == "confrontation_result" else x.get("frontier_id") == fid)]
             for t in ("confrontation_result", "capture_ceiling_result")}
    cf = filas["confrontation_result"][0] if len(filas["confrontation_result"]) == 1 else {}
    ce = filas["capture_ceiling_result"][0] if len(filas["capture_ceiling_result"]) == 1 else {}
    w, TOL = der["testigo"], V.GC.TOL_K1
    k1c, c2, err = cf.get("K_comp_1"), ce.get("C_2"), ce.get("numerical_error")
    post = {"K_comp_1_en_K1": k1c is not None and w["K1_en_punto"][0] - TOL <= k1c <= w["K1_en_punto"][1] + TOL,
            "C2_interseca_certificado": c2 is not None and err is not None and c2 + err >= w["C2_en_punto"][0] and c2 - err <= w["C2_en_punto"][1]}
    estado = "salida_invalida" if comp["estado"] == "invalida" else ("incoherente" if not all(post.values()) else ("incompleta" if comp["estado"] == "incompleta" else "ok"))
    motivos = list(comp["motivos"]) + ["poscomprobación falsa: %s" % k for k, v in post.items() if not v]
    clave = {"cell_id": cid, "frontier_id": fid, "instrumento": der["instrumento"], "barras": list(der["barras"]), "tasa": der["tasa"],
             "run_geometry": der["run_geometry"], "con_unidad": der["con_unidad"], "omega_id": der["omega_id"]}
    return CP.resumen_canonico(der["base_resumen"], filas, comp, post, estado, motivos, clave)


# ================================================================================================ lote y paquete
def requeridos(der, rows, cid, contrato):
    req = {"cell_context", "frontier_context", "capture_ceiling_result", "lambda_pi_envelope", "confrontation_result", "inversion_result", "convergence_result"}
    if der["run_geometry"]:
        req |= {"r1_summary", "r2_sections"}
        n = sum(int(x.get("n_components") or 0) for x in rows.get("r1_summary", []) if x.get("cell_id") == cid)
        if n:
            req |= {"r1_components", "r1_vertices"}
        if any(len([v for v in rows.get("r1_vertices", []) if v.get("cell_id") == cid and v.get("component_id") == k]) >= 2
               for k in {x.get("component_id") for x in rows.get("r1_components", []) if x.get("cell_id") == cid}):
            req.add("r1_edges")
        if any((x.get("n_roots_by_section") or 0) > 0 for x in rows.get("r2_sections", []) if x.get("cell_id") == cid):
            req.add("r2_roots")
    if contrato == "v3":
        req.add("inversion_targets")
        inv = [x for x in rows.get("inversion_result", []) if x.get("cell_id") == cid]
        if any(isinstance(x.get("n_scalar_solutions"), int) and x["n_scalar_solutions"] > 0 for x in inv):
            req.add("scalar_inversion_roots")
        if any(isinstance(x.get("n_scalar_intervals"), int) and x["n_scalar_intervals"] > 0 for x in inv):
            req.add("scalar_inversion_intervals")
        if any(x.get("sup_not_attained") is True for x in rows.get("capture_ceiling_result", []) if x.get("frontier_id") == der["frontier_id"]):
            req.add("sup_witness")
        req.add("numerical_evidence")
    return req


def verificar_lote(V, pdir, sel, lote, hecho, run_id, vistas, contrato):
    """[(codigo, detalle)] de UN lote hecho."""
    out = []
    lid = lote["lote_id"]
    if not (isinstance(hecho, dict) and set(hecho) >= {"archivos", "resumen"} and isinstance(hecho["archivos"], dict) and hecho["archivos"]
            and all(isinstance(k, str) and isinstance(v, str) and len(v) == 64 for k, v in hecho["archivos"].items())):
        return [("MANIFIESTO_LOTE", "%s: archivos ausentes, vacíos o mal formados" % lid)]
    ldir = pdir / "lotes" / lid
    presentes = {"lotes/%s/%s" % (lid, q.name) for q in ldir.iterdir() if q.is_file()} if ldir.is_dir() else set()
    reg = set(hecho["archivos"])
    if reg != presentes:
        out.append(("MANIFIESTO_LOTE", "%s: registrados %s ≠ presentes %s" % (lid, sorted(reg - presentes)[:3], sorted(presentes - reg)[:3])))
    for rel, h in hecho["archivos"].items():
        q = pdir / rel
        if not rel.startswith("lotes/%s/" % lid) or ".." in rel or not q.is_file() or sha(q.read_bytes()) != h:
            out.append(("CHECKPOINT_CORRUPT", rel))
    if out:
        return out
    permitidos = {"resultados.json"} | {t + ".jsonl" for t in CP.TABLAS[contrato]}
    raros = sorted(q.name for q in ldir.iterdir() if q.is_file() and q.name not in permitidos)
    vacios = sorted(q.name for q in ldir.glob("*.jsonl") if not q.read_bytes().strip())
    if raros or vacios:
        return out + [("MANIFIESTO_LOTE", "%s: archivos no exportables por el contrato %s %s o vacíos %s" % (lid, contrato, raros[:3], vacios[:3]))]
    rows = {}
    for q in sorted(ldir.glob("*.jsonl")):
        try:
            xs = [json.loads(x) for x in q.read_text(encoding="utf-8").splitlines() if x.strip()]
        except ValueError as e:
            return [("ESQUEMA", "%s ilegible: %s" % (q.name, e))]
        if not all(isinstance(x, dict) for x in xs):
            return [("ESQUEMA", "%s con filas que no son objetos" % q.name)]
        if len({sha(canon(x)) for x in xs}) != len(xs):
            out.append(("FILAS_DUPLICADAS", "%s/%s" % (lid, q.stem)))
        m = CP.esquema(V.C, q.stem, xs)
        if m:
            out.append(("ESQUEMA_CONTRATO", "%s/%s: %s" % (lid, q.stem, m)))
        rows[q.stem] = xs
    if out:
        return out
    try:
        res = json.loads((ldir / "resultados.json").read_bytes())
        V.GE.comprobar(res, ("dict", {"lote_id": ("const", lid), "celdas": ("lista", "json", 1, 4004), "segundos": "float"}), "$resultados")
    except (OSError, ValueError, V.GE.Rechazo) as e:
        return out + [("ESQUEMA", "resultados de %s: %s" % (lid, getattr(e, "detalle", e)))]
    if [c.get("clave_celda") if isinstance(c, dict) else None for c in res["celdas"]] != lote["celdas"]:
        return out + [("LOTE_NO_CORRESPONDE_AL_PLAN", lid)]
    filas_sel = {f["clave_celda"]: f for f in sel["filas"]}
    propias = {t: set() for t in rows}
    for c in res["celdas"]:
        k = c["clave_celda"]
        vistas[k] = vistas.get(k, 0) + 1
        try:
            der = V.derivar(sel, filas_sel[k], run_id, lid)
        except Rechazo as e:
            out.append((e.codigo, e.detalle))
            continue
        if not isinstance(c.get("clave_E12"), dict) or not isinstance(c["clave_E12"].get("cell_id"), str):
            out.append(("E12_CLAVE", "%s: clave_E12 ausente o mal formada" % k[:50]))
            continue
        cid = c["clave_E12"]["cell_id"]
        falt = requeridos(der, rows, cid, contrato) - set(rows)
        if falt:
            out.append(("MANIFIESTO_LOTE", "%s: faltan archivos requeridos %s" % (lid, sorted(falt))))
        try:
            estado, mot = verificar_celda(V, rows, der, c, contrato)
        except (IndexError, KeyError, TypeError) as e:
            estado, mot = "invalida", ["filas de la celda ausentes o mal formadas: %s %s" % (type(e).__name__, e)]
        recalc = {"completa": "ok", "incompleta": "incompleta", "invalida": "salida_invalida"}[estado]
        if c.get("estado") != recalc:
            out.append(("ETIQUETA_INCOHERENTE", "%s: etiqueta %r, recalculado %s (%s)" % (k[:40], c.get("estado"), recalc, mot[:3])))
        if recalc != "ok":
            out.append(("CELDA_NO_OK", "%s: %s %s" % (k[:40], recalc, mot[:3])))
        der["base_resumen"]["cell_id"] = cid
        try:
            mres = CP.comprobar_resumen(c, resumen_esperado(V, rows, der, c))
        except (IndexError, KeyError, TypeError) as e:
            mres = ["resumen no derivable: %s %s" % (type(e).__name__, e)]
        if mres:
            out.append(("RESUMEN_NO_CANONICO", "%s: %s" % (k[:40], mres[:3])))
        q = {"G:" + cid, "R1:" + cid} | {"INV:%s:%s" % (cid, i) for i in V.INV.INVERSIONS} | ({"C2:" + der["ceiling_id"]} if contrato == "v3" else set())
        for t, xs in rows.items():
            for i, x in enumerate(xs):
                if x.get("cell_id") == cid or x.get("frontier_id") == der["frontier_id"] or x.get("quantity_id") in q or \
                        (t == "sup_witness" and x.get("ceiling_id") == der["ceiling_id"]) or \
                        (t == "numerical_evidence" and isinstance(x.get("record_pk"), dict)
                         and (x["record_pk"].get("cell_id") == cid or x["record_pk"].get("ceiling_id") == der["ceiling_id"])):
                    propias[t].add(i)
        for i, x in enumerate(rows.get("lambda_pi_envelope", [])):
            if x.get("macro_id") in {y.get("macro_id") for y in rows.get("confrontation_result", []) if y.get("cell_id") == cid}:
                propias["lambda_pi_envelope"].add(i)
    for t, xs in rows.items():
        if len(propias.get(t, ())) != len(xs):
            out.append(("FILAS_AJENAS", "%s/%s: %d filas sin relación con las celdas del lote" % (lid, t, len(xs) - len(propias.get(t, ())))))
    return out


def verificar_paquete(V, pdir, modo="validar"):
    """Ruta común. modo «validar»: dictamen completo del paquete. modo «reanudar»: lotes hechos verificados (los
    pendientes se permiten). Devuelve {cumple, codigos, violaciones, productor, contrato, hechos}; nunca lanza."""
    pdir = Path(pdir)
    viol = []

    def v(c, d):
        viol.append({"codigo": c, "detalle": str(d)[:300]})
    prod, contrato, hechos = None, None, []
    try:
        sel, plan = V.verificar_seleccion(pdir)
        _, _, ck_esq, _ = V.esq
        st = json.loads((pdir / "checkpoint.json").read_bytes())
        _esq(st, ck_esq, "$checkpoint", V.GE)
        need(isinstance(st["hechos"], dict) and all(isinstance(k, str) for k in st["hechos"]), "ESQUEMA", "hechos")
        need(st["lotes"] == [l["lote_id"] for l in plan["lotes"]], "IDENTIDAD", "lotes del checkpoint distintos del plan")
        prod, run_id, contrato = V.verificar_identidad(st["identidad"], sel, plan)
        fuera = set(st["hechos"]) - set(st["lotes"])
        if fuera:
            v("CHECKPOINT_CORRUPT", "lotes hechos fuera del plan: %s" % sorted(fuera))
        en_disco = {q.name for q in (pdir / "lotes").iterdir() if q.is_dir() and not q.name.startswith(".")} if (pdir / "lotes").is_dir() else set()
        if modo == "validar":
            if st["estado"] != "completo" or sorted(st["hechos"]) != sorted(st["lotes"]):
                v("PAQUETE_INCOMPLETO", "estado %s; hechos %s" % (st["estado"], sorted(st["hechos"])))
            if en_disco - set(st["hechos"]):
                v("MANIFIESTO_PAQUETE", "lotes en disco no registrados: %s" % sorted(en_disco - set(st["hechos"])))
        vistas = {}
        for lote in plan["lotes"]:
            if lote["lote_id"] in st["hechos"]:
                for c, d in verificar_lote(V, pdir, sel, lote, st["hechos"][lote["lote_id"]], run_id, vistas, contrato):
                    v(c, d)
                hechos.append(lote["lote_id"])
        if modo == "validar":
            for f in sel["filas"]:
                if vistas.get(f["clave_celda"], 0) != 1:
                    v("CELDA_FALTANTE_O_DUPLICADA", "%s vista %d veces" % (f["clave_celda"][:50], vistas.get(f["clave_celda"], 0)))
    except Rechazo as e:
        v(e.codigo, e.detalle)
    except Exception as e:  # noqa: BLE001  (rechazo controlado de cualquier forma inesperada)
        v("PAQUETE_ILEGIBLE", "%s: %s" % (type(e).__name__, e))
    return {"cumple": not viol, "completa": True, "dictamen": "completo" if not viol else "rechazado", "productor": prod, "contrato": contrato,
            "hechos_verificados": hechos, "violaciones": viol, "codigos": sorted({x["codigo"] for x in viol}),
            "campos_diagnosticos_no_consumibles": list(CP.DIAGNOSTICO), "dependencias": V.dependencias}


def validar(pdir, ref=None, V=None):
    """Validación E13/E14. Sin referencia autenticada NO hay dictamen completo: «parcial», cumple = False."""
    if V is None and ref is None:
        return {"cumple": False, "completa": False, "dictamen": "parcial_sin_referencia_autenticada", "codigos": ["SIN_REFERENCIA_AUTENTICADA"],
                "violaciones": [{"codigo": "SIN_REFERENCIA_AUTENTICADA", "detalle": "la validación completa exige el contexto S5 autenticado (Referencia)"}]}
    return verificar_paquete(V, pdir, "validar")


def consumir(V, pdir):
    """Lo ÚNICO consumible de un paquete: celdas validadas sin campos diagnósticos. Rechaza si la validación no cumple."""
    r = verificar_paquete(V, pdir, "validar")
    need(r["cumple"], "PAQUETE_NO_VALIDO", r["codigos"])
    out = []
    for lote in json.loads((Path(pdir) / "plan.json").read_bytes())["lotes"]:
        res = json.loads((Path(pdir) / "lotes" / lote["lote_id"] / "resultados.json").read_bytes())
        out.extend(CP.consumir_celda(c) for c in res["celdas"])
    return out


__all__ = ["Rechazo", "Verificador", "verificar_paquete", "validar", "consumir", "puerta_autoridad", "exigir_corrida_oficial", "EXPORTABLES"]


# ======================================================================================================================
# ENTRADA POR PROCEDENCIA (lima1009; SOLO en la COPIA DE INTEGRACIÓN integracion_consumidor/, NO en el candidato congelado).
# Paquetes de celdas detalladas por procedencia (alternativa A): el consumidor REAL (este módulo y su Verificador) registra el
# productor AUTENTICADO, exige la entrada común corregida (ensamblaje/paquetes_procedencia.verificar: PK1 + índice global A +
# tipos B) y valida el CONTENIDO de cada unidad con SUS reglas (paper2b.contrato_paquete y rules del núcleo candidato):
#   C1 esquema del contrato de la autoridad en cada tabla exigida por el contrato del productor (v2: E12; v3: E12 + hijas + C2);
#   C2 presencia E12 (rules.e12_verificar_celda) con la clave E12 del documento: «completa» para las numéricas;
#   C3 v3 numéricas: checker del núcleo (rules.Checker: ceilings, inversions, geometry, audit) sin errores;
#   C4 v2: garantías menores DECLARADAS (evidencia ausente: las 5 hijas y la fila C2); NUNCA se equiparan a v3.
# Cada unidad queda «aceptada_por_el_consumidor» o «rechazada» con motivos; las no comprobables se declaran (nunca aceptadas).
# ======================================================================================================================
# lima1324 (v2): instantánea única verificada y consumida, identidades/cantidades por lote y globales contra la autoridad, productores
# por identidad completa con cobertura (correcciones A y B del dictamen rem7). La v1 (lima1009) está en demo/pk3/versiones_previas.
RUTA_PROCEDENCIA = "consumidor-procedencia-v2 (lima1324, copia de integración)"
# lima0845 (procedencia de VARIANTE; misma ruta v2): un paquete con `procedencia_variante` (hoy solo rem-lima2330) se registra con la VARIANTE en
# la identidad de su productor. El consumidor la AUTENTICA por el inventario de la entrega del lote (entrada, archivos, congelación,
# declaración, procedencia de ejecución, resumen del trabajador y evidencias), RECALCULA la identidad (sha256(canon(autoridad del
# contexto del trabajador)); su manifiesto de código enlazado por codigo_demo_sha256 contiene la variante), exige alcance = unidades del
# paquete, productor original = el autenticado, limitación DERIVADA presente (instantánea final ausente), aceptación SOLO técnica (sin firma
# científica, NA científico, incorporación ni adopción para otras inversiones) y documentos del lote con esa identidad. Sin variante: ningún
# resumen de variante en la propuesta y ningún resumen de trabajador autenticado del lote con variante (VARIANTE_NO_DECLARADA).
# CORRECCIÓN DE ALCANCE (lima1018, observación PV12 del dictamen rem12): en lima0845 estas comprobaciones NO cubrían todo el bloque (con una
# entrada común deliberadamente permisiva pasaban entrada distinta de la declarada, método o evidencias vacíos, limitación con contenido
# falso y referencia de aceptación sustituida); la entrada común REAL sí las rechazaba. lima1018 cierra esas relaciones (ver abajo).
# Versiones previas exactas: demo/pk7/versiones_previas/ (lima0845) y demo/pk8/versiones_previas/ (lima1018).
LIM_SIN_INSTANTANEA_FINAL = "SIN_INSTANTANEA_FINAL_DE_MODULOS_DEL_INTENTO"

# lima1018 (PV12): la defensa PROPIA del consumidor sobre el bloque `procedencia_variante` no depende de la entrada común. El bloque tiene un
# ESQUEMA CERRADO (todo campo obligatorio, sin campos extra, tipos y no vacíos) y CADA valor se resuelve contra fuentes autenticadas por el
# inventario de la entrega del lote o contra la autoridad FIJADA en este código (aceptación técnica): entrada = la de la declaración
# autenticada y la del módulo lanzado según la supervisión; método completo = manifiesto de la identidad; evidencias = conjunto pertinente,
# cada una con su relación (declaración, identidad, variante, unidad); limitación = la DERIVADA de la procedencia auténtica (contenido
# íntegro, no solo el código); aceptación = nombre y sha256 fijados aquí y bytes de la copia verificable. Los textos del contrato son los
# del ensamblador. Alcance de esta garantía: el bloque de variante y su resumen de registro; las identidades y cantidades esperadas por lote
# y los demás campos derivados del paquete siguen dependiendo de la verificación de la entrada común REAL.
CAMPOS_METODO = ("tipo", "metodo", "metodo_original_sha256", "fuente_corregida_sha256", "parche_diff_sha256", "modelos_py_sha256")
EVIDENCIAS_VARIANTE = ("validacion_lote_en_contexto_de_la_variante", "control_negativo_validador_original", "puerta_del_intento", "ensayo_parcial",
                       "supervision_del_intento", "procedencia_validacion_lote", "procedencia_validacion_final")
TIPO_BLOQUE_VARIANTE = 'VARIANTE DECLARADA (aislada; NO incorporada; no se adopta para otras inversiones)'
PAPEL_PRODUCTOR_ORIGINAL = 'escribe y exporta el contrato v3 (codigo/bloque_s1.trabajador_c SIN cambios)'
REGLA_IDENTIDAD_VARIANTE = 'identidad = sha256(canon(identidad_almacen.autoridad)); codigo_demo_sha256 = sha256(canon(identidad_almacen.codigo)), que contiene la variante'
TEXTO_LIMITACION_VARIANTE = {LIM_SIN_INSTANTANEA_FINAL: 'el intento completo tiene instantánea INICIAL de {n} módulos (al instalar la variante) pero NO FINAL: el trabajador (codigo/bloque_s1.trabajador_c) termina con os._exit(0) y atexit no se ejecuta; no se reconstruye retrospectivamente ni se repite la celda para obtenerla'}
MOTIVO_CONTROL_NEGATIVO = "procedencia falsa: identidad_del_productor"
# autoridad FIJADA de la aceptación técnica por identidad de variante (el paquete no la aporta: solo puede citarla igual). La copia verificable
# de sus bytes se INSTALA junto a este validador, en el destino estable y declarado DESTINO_ACEPTACIONES (procedencia, tamaño y sha256 en
# procedencia_aceptaciones.json y en la composición del código S6). La ruta se resuelve desde la instalación efectiva de este módulo
# (lima0044: antes, parents[4]/aceptaciones, válido solo en la copia de integración de lima1018, apuntaba fuera de una raíz instalada).
DESTINO_ACEPTACIONES = "herramientas/s3/validadores/aceptaciones"
DIR_ACEPTACIONES = Path(__file__).resolve().parent / "aceptaciones"
ACEPTACIONES_TECNICAS = {
    "dd9463df93293785b7ec1b1a08045b6046b856bd17c88c650a006fdbaec77ae7": {
        "tipo": 'ACEPTACIÓN TÉCNICA del revisor independiente: SOLO esta unidad, en el alcance de la variante aislada autenticada',
        "dictamen": "review_20261012_rem11_dictamen.txt",
        "sha256": "7d1e8a7a5bf7a738344c47672e63cdabfcb80aeba28c1672347e0ee20e811910",
        "alcance": ("S2:e6a4f7a3e323199a:0",),
        "frase": "se acepta técnicamente"},
}
_HEX = set("0123456789abcdef")
_FLAGS_ACEPTACION = ("firma_cientifica", "aceptacion_cientifica_v2_na", "autorizacion_de_incorporacion", "adopcion_para_otras_inversiones")
_REF = {"archivo": "texto", "sha256": "hex64"}
_FUENTE_LIM = {"archivo": "texto", "sha256": "hex64", "etapa": "texto", "instantanea_inicial_modulos": "entero", "instantanea_final_modulos": "entero_o_nulo"}
ESQUEMA_VARIANTE = {
    "tipo": "texto", "identidad": "hex64", "alcance": "lista_unidades",
    "productor_original": {"archivo": "texto", "sha256": "hex64", "papel": "texto", "identidad_del_validador_original": "hex64"},
    "entrada_variante": _REF, "archivos_variante": "mapa_hex64",
    "metodo": {k: ("hex64" if k.endswith("_sha256") else "texto") for k in CAMPOS_METODO},
    "identidad_recalculada": {"resumen_trabajador": _REF, "regla": "texto"},
    "congelacion": {"archivo": "texto", "sha256": "hex64", "archivos": "entero"},
    "declaracion": _REF,
    "procedencia_ejecucion": dict(_FUENTE_LIM),
    "evidencias": {k: _REF for k in EVIDENCIAS_VARIANTE},
    "limitaciones": ("lista", {"codigo": "texto", "detalle": "texto", "fuente": _FUENTE_LIM}),
    "aceptacion": dict({"tipo": "texto", "dictamen": "texto", "dictamen_sha256": "hex64"}, **{k: "booleano" for k in _FLAGS_ACEPTACION}),
}


def _esquema(x, e, ruta="procedencia_variante"):
    """Esquema CERRADO: Rechazo VARIANTE_ESQUEMA ante un campo ausente, extra, vacío o de tipo inválido."""
    if isinstance(e, dict):
        need(isinstance(x, dict), "VARIANTE_ESQUEMA", "%s: se esperaba un objeto" % ruta)
        falta, sobra = sorted(set(e) - set(x)), sorted(set(x) - set(e))
        need(not falta and not sobra, "VARIANTE_ESQUEMA", "%s: ausentes %s; no esperados %s" % (ruta, falta, sobra))
        for k, sub in e.items():
            _esquema(x[k], sub, "%s.%s" % (ruta, k))
        return
    if isinstance(e, tuple):            # ("lista", esquema_del_elemento)
        need(isinstance(x, list), "VARIANTE_ESQUEMA", "%s: se esperaba una lista" % ruta)
        for i, y in enumerate(x):
            _esquema(y, e[1], "%s[%d]" % (ruta, i))
        return
    ok = {"texto": lambda v: isinstance(v, str) and v.strip() != "",
          "hex64": lambda v: isinstance(v, str) and len(v) == 64 and set(v) <= _HEX,
          "entero": lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0,
          "entero_o_nulo": lambda v: v is None or (isinstance(v, int) and not isinstance(v, bool) and v >= 0),
          "booleano": lambda v: isinstance(v, bool),
          "lista_unidades": lambda v: isinstance(v, list) and len(v) > 0 and all(isinstance(u, str) and u for u in v) and len(set(v)) == len(v),
          "mapa_hex64": lambda v: isinstance(v, dict) and len(v) > 0 and all(isinstance(k, str) and k and isinstance(h, str) and len(h) == 64 and set(h) <= _HEX
                                                                           for k, h in v.items())}[e]
    need(ok(x), "VARIANTE_ESQUEMA", "%s: tipo inválido o vacío (%s)" % (ruta, e))


def _modulo_de(rel):
    return rel[:-3].replace("/", ".") if rel.endswith(".py") else None


def _canon_json(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _resumen_variante(v):
    return {"identidad": v["identidad"], "alcance": list(v["alcance"]), "entrada": dict(v["entrada_variante"]), "archivos": dict(v["archivos_variante"]),
            "congelacion": {"archivo": v["congelacion"]["archivo"], "sha256": v["congelacion"]["sha256"]},
            "declaracion": dict(v["declaracion"]), "limitaciones": [x["codigo"] for x in v["limitaciones"]]}


def _variante_autenticada(p, prop, autent, prod_rel, prod_b, files=None):
    """Resumen de la variante del paquete, comprobado contra las fuentes autenticadas (Rechazo si algo no coincide); None sin variante.
    Sin variante declarada, ningún resumen de trabajador autenticado de la carpeta del lote puede mostrar una variante en su manifiesto
    de código (VARIANTE_NO_DECLARADA): el resultado nunca se atribuye en silencio al productor original."""
    pv = p.get("procedencia_variante")
    if pv is None:
        need(prop.get("variante") is None, "VARIANTE_INCOHERENTE", "la propuesta declara una variante que el paquete no lleva")
        pref = str(p.get("carpeta_resultados") or "") + "/"
        for r in sorted(x for x in (files or {}) if x.startswith(pref) and x.rsplit("/", 1)[-1].startswith("trabajador_") and x.endswith(".json")):
            man = ((json.loads(autent(r)).get("identidad_almacen") or {}).get("codigo") or {})
            need(not any(isinstance(k, str) and k.startswith("variante") for k in man), "VARIANTE_NO_DECLARADA",
                 "%s muestra una variante que el paquete no declara" % r)
        return None
    _esquema(pv, ESQUEMA_VARIANTE)                         # lima1018: esquema cerrado ANTES de leer ningún valor
    res = _resumen_variante(pv)
    need(prop.get("variante") == res, "VARIANTE_INCOHERENTE", "la propuesta de registro declara otra variante")
    ident, alc = pv["identidad"], list(pv["alcance"])

    def av(rel):
        try:
            return autent(rel)
        except (OSError, Rechazo) as ex:
            raise Rechazo("VARIANTE_NO_AUTENTICADA", "%s no autenticado por el inventario de la entrega del lote: %s" % (rel, getattr(ex, "detalle", ex)))

    def aj(rel, codigo):
        try:
            return json.loads(av(rel))
        except ValueError as ex:
            raise Rechazo(codigo, "%s no es JSON: %s" % (rel, ex))
    # 1. textos del contrato, productor ORIGINAL y alcance (una celda: las unidades del paquete)
    need(pv["tipo"] == TIPO_BLOQUE_VARIANTE and pv["productor_original"]["papel"] == PAPEL_PRODUCTOR_ORIGINAL
         and pv["identidad_recalculada"]["regla"] == REGLA_IDENTIDAD_VARIANTE, "VARIANTE_ESQUEMA", "texto de contrato distinto del del ensamblador")
    po = pv["productor_original"]
    need(po["archivo"] == prod_rel and po["sha256"] == sha(prod_b), "VARIANTE_PRODUCTOR_ORIGINAL", "productor original distinto del autenticado")
    need(sorted(alc) == sorted(u.get("unidad") for u in p.get("unidades") or []), "VARIANTE_ALCANCE", "alcance de la variante distinto de las unidades del paquete")
    # 2. bytes de la variante, su entrada y la congelación que los fija
    ent = pv["entrada_variante"]
    for r, h in list(pv["archivos_variante"].items()) + [(ent["archivo"], ent["sha256"])]:
        need(sha(av(r)) == h, "VARIANTE_HASH", r)
    cg_b = av(pv["congelacion"]["archivo"])
    need(sha(cg_b) == pv["congelacion"]["sha256"], "VARIANTE_HASH", "congelación")
    cg = json.loads(cg_b)
    cga = cg.get("archivos") if isinstance(cg.get("archivos"), dict) else {}
    need(all(cga.get(r) == h for r, h in list(pv["archivos_variante"].items()) + [(ent["archivo"], ent["sha256"])]) and pv["congelacion"]["archivos"] == len(cga),
         "VARIANTE_HASH", "la congelación no fija los bytes de la variante o su recuento no coincide")
    # 3. identidad RECALCULADA y manifiesto de código enlazado que contiene EXACTAMENTE esta variante
    rt_ref = pv["identidad_recalculada"]["resumen_trabajador"]
    rt_b = av(rt_ref["archivo"])
    need(sha(rt_b) == rt_ref["sha256"], "VARIANTE_HASH", "resumen del trabajador")
    rt = json.loads(rt_b)
    ia = rt.get("identidad_almacen") if isinstance(rt.get("identidad_almacen"), dict) else {}
    autoridad_ctx = ia.get("autoridad") if isinstance(ia.get("autoridad"), dict) else {}
    man = ia.get("codigo") if isinstance(ia.get("codigo"), dict) else {}
    need(sha(_canon_json(autoridad_ctx)) == ident and rt.get("identidad_productor_sha256") == ident, "VARIANTE_IDENTIDAD", "identidad recalculada distinta de la declarada")
    need(autoridad_ctx.get("codigo_demo_sha256") == sha(_canon_json(man)), "VARIANTE_IDENTIDAD", "manifiesto de código no enlazado a la identidad")
    mvs = [v for k, v in man.items() if isinstance(k, str) and k.startswith("variante")]
    need(len(mvs) == 1 and isinstance(mvs[0], dict), "VARIANTE_IDENTIDAD", "el manifiesto de la identidad no contiene exactamente una variante")
    mv = mvs[0]
    mcg = mv.get("congelacion") if isinstance(mv.get("congelacion"), dict) else {}
    need(mv.get("archivos") == pv["archivos_variante"] and mcg.get("sha256") == pv["congelacion"]["sha256"]
         and str(mcg.get("archivo") or "").replace(chr(92), "/") == pv["congelacion"]["archivo"], "VARIANTE_IDENTIDAD", "el manifiesto de la identidad no contiene esta variante")
    # 4. MÉTODO completo: todos los campos obligatorios, iguales a los del manifiesto autenticado (nunca solo las claves aportadas)
    need(all(isinstance(mv.get(k), str) and mv.get(k) for k in CAMPOS_METODO) and pv["metodo"] == {k: mv[k] for k in CAMPOS_METODO},
         "VARIANTE_METODO", "método distinto del manifiesto autenticado o incompleto")
    # 5. DECLARACIÓN autenticada: lote, unidad, identidad, productor, variante, ENTRADA, procedencia de ejecución y validación final
    de_b = av(pv["declaracion"]["archivo"])
    need(sha(de_b) == pv["declaracion"]["sha256"], "VARIANTE_HASH", "declaración")
    de = json.loads(de_b)
    dpq = de.get("productor_que_escribe_y_exporta_v3") if isinstance(de.get("productor_que_escribe_y_exporta_v3"), dict) else {}
    need(de.get("identidad_del_productor_de_los_documentos") == ident and [de.get("unidad")] == alc and de.get("lote") == p.get("lote")
         and dpq.get("archivo") == prod_rel and dpq.get("sha256") == sha(prod_b) and de.get("variante") == mv, "VARIANTE_DECLARACION", "declaración del lote incompatible")
    dent = de.get("entrada_de_la_variante") if isinstance(de.get("entrada_de_la_variante"), dict) else {}
    need({"archivo": dent.get("archivo"), "sha256": dent.get("sha256")} == ent, "VARIANTE_ENTRADA",
         "la entrada declarada no es la identificada en la declaración autenticada (ruta e identidad de bytes)")
    pe_ref = pv["procedencia_ejecucion"]
    dpe = de.get("procedencia_de_ejecucion") if isinstance(de.get("procedencia_de_ejecucion"), dict) else {}
    vctx = de.get("validacion_en_contexto_de_la_variante") if isinstance(de.get("validacion_en_contexto_de_la_variante"), dict) else {}
    vfin, vlote = vctx.get("final") or {}, vctx.get("lote") or {}
    pval = p.get("validacion") if isinstance(p.get("validacion"), dict) else {}
    need(dpe.get("archivo") == pe_ref["archivo"] and dpe.get("sha256") == pe_ref["sha256"]
         and pval.get("entrega") == p.get("entrega") and (vfin.get("archivo"), vfin.get("sha256")) == (pval.get("archivo"), pval.get("sha256")),
         "VARIANTE_DECLARACION", "la declaración no enlaza esta procedencia de ejecución o la validación del paquete")
    # 6. procedencia de EJECUCIÓN: misma variante; recuentos de las instantáneas DERIVADOS (la final ausente no se reconstruye)
    pe_b = av(pe_ref["archivo"])
    need(sha(pe_b) == pe_ref["sha256"], "VARIANTE_HASH", "procedencia de ejecución")
    pe = json.loads(pe_b)
    need(pe.get("variante") == mv, "VARIANTE_IDENTIDAD", "procedencia de ejecución con otra variante")
    n_ini = len(pe.get("cargados") or {}) if isinstance(pe.get("cargados") or {}, dict) else -1
    n_fin = len(pe.get("cargados_al_final") or {}) if isinstance(pe.get("cargados_al_final") or {}, dict) else -1
    need(n_ini >= 0 and n_fin >= 0 and pe_ref["etapa"] == pe.get("etapa") and pe_ref["instantanea_inicial_modulos"] == n_ini
         and pe_ref["instantanea_final_modulos"] == (n_fin or None), "VARIANTE_PROCEDENCIA", "instantáneas declaradas distintas de la procedencia auténtica")
    need(dpe.get("etapa") == pe.get("etapa") and dpe.get("modulos_cargados_registrados") == n_ini and dpe.get("modulos_al_final") == n_fin,
         "VARIANTE_DECLARACION", "la declaración describe otras instantáneas que la procedencia auténtica")
    # 7. LIMITACIONES: iguales ÍNTEGRAMENTE (código, texto y fuente estructurada) a las DERIVADAS de la procedencia auténtica
    fuente = {"archivo": pe_ref["archivo"], "sha256": sha(pe_b), "etapa": pe.get("etapa"), "instantanea_inicial_modulos": n_ini, "instantanea_final_modulos": None}
    derivadas = ([{"codigo": LIM_SIN_INSTANTANEA_FINAL, "detalle": TEXTO_LIMITACION_VARIANTE[LIM_SIN_INSTANTANEA_FINAL].format(n=n_ini), "fuente": fuente}]
                 if n_ini and not n_fin else [])
    need(pv["limitaciones"] == derivadas, "VARIANTE_LIMITACION", "limitaciones distintas de las derivadas de la procedencia auténtica (código, texto o fuente)")
    linea = ("producida con la VARIANTE %s (identidad %s; entrada %s); alcance aceptado: SOLO %s; aceptación técnica, no firma científica ni incorporación"
             % (pv["metodo"]["tipo"], ident, ent["archivo"], ", ".join(alc)))
    need(all(isinstance(u.get("limitaciones"), list) and linea in u["limitaciones"] and all(x["detalle"] in u["limitaciones"] for x in derivadas)
             for u in p.get("unidades") or []), "VARIANTE_LIMITACION", "unidad sin la declaración de la variante o sin su limitación")
    # 8. EVIDENCIAS pertinentes (conjunto completo por esquema), autenticadas, distintas y con su relación con la autoridad
    ev = pv["evidencias"]
    rutas = [x["archivo"] for x in ev.values()] + [pv["declaracion"]["archivo"], pe_ref["archivo"]]
    need(len(set(rutas)) == len(rutas), "VARIANTE_EVIDENCIA", "una misma fuente usada para dos papeles")
    for k, ref in ev.items():
        need(sha(av(ref["archivo"])) == ref["sha256"], "VARIANTE_EVIDENCIA", "evidencia %s con otro sha256" % k)
    vl, cn = ev["validacion_lote_en_contexto_de_la_variante"], ev["control_negativo_validador_original"]
    dcn = de.get("control_negativo_validador_original") if isinstance(de.get("control_negativo_validador_original"), dict) else {}
    need((vl["archivo"], vl["sha256"]) == (vlote.get("archivo"), vlote.get("sha256")) and (cn["archivo"], cn["sha256"]) == (dcn.get("archivo"), dcn.get("sha256")),
         "VARIANTE_EVIDENCIA", "validación del lote o control negativo distintos de los de la declaración")
    d_vl = aj(vl["archivo"], "VARIANTE_EVIDENCIA")
    need(d_vl.get("identidad_validador_sha256") == ident and d_vl.get("conteo") == {"completa_validada": len(alc)}
         and sorted(str(c.get("id")) for c in d_vl.get("celdas") or [] if isinstance(c, dict)) == sorted(alc), "VARIANTE_EVIDENCIA",
         "la validación del lote no acepta esta unidad en el contexto de la variante")
    d_cn = aj(cn["archivo"], "VARIANTE_EVIDENCIA")
    need(d_cn.get("conteo") == {"rechazada": len(alc)} and d_cn.get("identidad_validador_sha256") not in (None, ident)
         and d_cn.get("identidad_validador_sha256") == po["identidad_del_validador_original"]
         and all(isinstance(c, dict) and c.get("motivos") == [MOTIVO_CONTROL_NEGATIVO] for c in d_cn.get("celdas") or [None]), "VARIANTE_EVIDENCIA",
         "el control negativo no muestra el rechazo del validador original solo por identidad")
    d_su = aj(ev["supervision_del_intento"]["archivo"], "VARIANTE_EVIDENCIA")
    need(d_su.get("tarea") == de.get("tarea") and de.get("tarea"), "VARIANTE_EVIDENCIA", "supervisión de otra tarea que la declarada")
    need(d_su.get("modulo_trabajador") == _modulo_de(ent["archivo"]), "VARIANTE_ENTRADA", "el módulo lanzado según la supervisión no es la entrada declarada")
    d_pu = aj(ev["puerta_del_intento"]["archivo"], "VARIANTE_EVIDENCIA")
    need(d_pu.get("pasa") is True and all(u in str(d_pu.get("puerta") or "") for u in alc), "VARIANTE_EVIDENCIA", "puerta del intento no superada o de otra unidad")
    d_en = aj(ev["ensayo_parcial"]["archivo"], "VARIANTE_EVIDENCIA")
    vc = d_en.get("version_corregida") if isinstance(d_en.get("version_corregida"), dict) else {}
    need({k: vc.get(k) for k in CAMPOS_METODO} == pv["metodo"], "VARIANTE_EVIDENCIA", "el ensayo parcial probó otra versión del método")
    for k in ("procedencia_validacion_lote", "procedencia_validacion_final"):
        d_pv = aj(ev[k]["archivo"], "VARIANTE_EVIDENCIA")
        need(d_pv.get("etapa") == "fin" and d_pv.get("variante") == mv, "VARIANTE_EVIDENCIA", "%s sin la variante o sin etapa final" % k)
    # 9. ACEPTACIÓN técnica: autoridad FIJADA en este consumidor + bytes de la copia verificable; nunca nombre y hash aportados por el paquete
    ac = pv["aceptacion"]
    need(all(ac[k] is False for k in _FLAGS_ACEPTACION), "VARIANTE_ACEPTACION",
         "el paquete declara más que la aceptación técnica de esta unidad (firma, NA científico, incorporación u otras inversiones)")
    fij = ACEPTACIONES_TECNICAS.get(ident)
    need(fij is not None, "VARIANTE_ACEPTACION", "no hay aceptación técnica fijada para esta identidad de variante")
    need((ac["tipo"], ac["dictamen"], ac["dictamen_sha256"]) == (fij["tipo"], fij["dictamen"], fij["sha256"]) and tuple(alc) == fij["alcance"],
         "VARIANTE_ACEPTACION", "referencia de aceptación distinta de la autoridad fijada (nombre, sha256, tipo o alcance)")
    try:
        cb = (DIR_ACEPTACIONES / fij["dictamen"]).read_bytes()
    except OSError as ex:
        raise Rechazo("VARIANTE_ACEPTACION_NO_COMPROBABLE", "copia verificable del dictamen ausente: %s" % ex)
    need(sha(cb) == fij["sha256"], "VARIANTE_ACEPTACION_NO_COMPROBABLE", "copia del dictamen con otro sha256")
    txt = cb.decode("utf-8", errors="replace")
    need(ident in txt and all(u in txt for u in alc) and fij["frase"] in txt, "VARIANTE_ACEPTACION", "el dictamen fijado no acepta esta unidad con esta identidad")
    return res


def registrar_productor_procedencia(V, p, aut):
    """Entrada de registro del productor de un paquete, AUTENTICADA por el inventario de su entrega (la autoridad la da la cadena de
    custodia, `aut`; la propuesta del paquete solo nombra lo que se autentica, nunca se acepta por sí misma)."""
    return _productor_y_inventario(V, p, aut)[0]


def _productor_y_inventario(V, p, aut):
    """(registro, inventario verificado {archivo: sha256}): el inventario sale de los MISMOS bytes cuyo sha256 se comprobó (una lectura)."""
    prop = p.get("propuesta_registro_consumidor")
    need(isinstance(prop, dict), "PRODUCTOR_NO_AUTENTICADO", "sin propuesta de registro")
    area = prop.get("area")
    need(area == p.get("entrega") and area in aut, "PRODUCTOR_NO_AUTENTICADO", "área fuera de la autoridad: %s" % area)
    try:        # el inventario que fija la AUTORIDAD (entrega cerrada: audit/entrega.json; ronda en curso: su pre-inventario provisional)
        inv_raw = (V.T / area / aut[area].get("archivo", "audit/entrega.json")).read_bytes()
    except OSError as e:
        raise Rechazo("PRODUCTOR_NO_AUTENTICADO", "inventario de %s ilegible: %s" % (area, e))
    need(sha(inv_raw) == aut[area]["sha256"] == prop.get("inventario"), "PRODUCTOR_NO_AUTENTICADO", "inventario de %s" % area)
    files = json.loads(inv_raw)["files"]

    def autent(rel):
        b = (V.T / area / rel).read_bytes()
        need(rel in files and files[rel]["sha256"] == sha(b), "PRODUCTOR_NO_AUTENTICADO", rel)
        return b
    need(prop.get("codigo") == [prop.get("productor")], "PRODUCTOR_NO_AUTENTICADO", "código del productor")
    prod = autent(prop["productor"])
    exporta_v3 = b"filas_de_celda(" in prod and b'"v3")' in prod
    need(prop.get("contrato") == p.get("contrato") and (exporta_v3 == (p.get("contrato") == "v3") or p.get("lote") == "S2-G-df-NA"),
         "PRODUCTOR_NO_AUTENTICADO", "contrato incoherente con el productor")
    dep = json.loads(autent("autorizacion/despliegue_ronda.json"))
    need(dep.get("run_class") == prop.get("run_class") == p.get("run_class") and dep.get("etiqueta") == prop.get("etiqueta") == p.get("etiqueta"),
         "PRODUCTOR_NO_AUTENTICADO", "despliegue")
    enc = autent(prop.get("encargo") or "autorizacion/encargo.txt")
    from dataclasses import replace
    cfg_sha = sha(V.K.canon(replace(V.cfg, run_class=dep["run_class"]).as_dict()) + bytes([10]))
    var = _variante_autenticada(p, prop, autent, prop["productor"], prod, files)       # lima0845
    return ({"area": area, "inventario": aut[area]["sha256"], "productor": prop["productor"], "producer_sha256": sha(prod), "contrato": p["contrato"],
             "run_class": dep["run_class"], "etiqueta": dep.get("etiqueta"), "autorizacion_sha256": sha(enc), "config_sha256": cfg_sha,
             "variante": var, "ruta": RUTA_PROCEDENCIA}, {r: (v["sha256"] if isinstance(v, dict) else v) for r, v in files.items()})


def contenido_unidad(V, u, p, inv, T):
    """(estado, motivos) del CONTENIDO de una unidad con las reglas del consumidor (C1–C4); bytes autenticados por el inventario."""
    from paper2b import rules as RULES
    ent, carpeta = p["entrega"], p["carpeta_resultados"]
    n = u["unidad"].replace(":", "_")
    rd = "%s/%s.json" % (carpeta, n)
    db = (T / ent / rd).read_bytes()
    need(inv.get(rd) == sha(db) == u["documento_sha256"], "REFERENCIA_NO_AUTENTICADA", rd)
    doc = json.loads(db)
    pv = p.get("procedencia_variante")
    if pv is not None:      # lima0845: el documento debe ser del productor con la VARIANTE declarada
        need(doc.get("identidad_productor_sha256") == pv.get("identidad"), "VARIANTE_IDENTIDAD", "documento con otra identidad de productor que la variante")
    rf = "%s/%s" % (carpeta, (doc.get("filas") or {}).get("archivo", n + "_filas.json"))
    fb = (T / ent / rf).read_bytes()
    need(inv.get(rf) == sha(fb) == u["filas_sha256"], "REFERENCIA_NO_AUTENTICADA", rf)
    rows = json.loads(fb)
    if not u.get("numerico"):
        # no aplicable: su garantía es la clasificación NA de su validación autenticada (entrada común); el contenido no debe
        # traer una confrontación numérica completa de esa celda
        cfs = [x for x in rows.get("confrontation_result", []) if x.get("cell_id") == u.get("cell_id_e12") and x.get("computation_status") == "complete"]
        return ("rechazada", ["NA con confrontación numérica completa"]) if cfs else ("aceptada_por_el_consumidor", [])
    r = doc.get("resultado") or {}
    ce = r.get("clave_E12") or {}
    cid = ce.get("cell_id") or u.get("cell_id_e12")
    fid = ce.get("frontier_id") or r.get("frontier_id")
    if not (cid and fid and ce.get("instrumento")):
        return "no_comprobable", ["documento sin clave E12 completa (cell_id, frontier_id, instrumento)"]
    if cid != u.get("cell_id_e12"):
        return "rechazada", ["cell_id del documento distinto del del paquete"]
    contrato = p["contrato"]
    mot = []
    sel = CP.filas_de_celda(rows, cid, fid, contrato)
    for t in CP.TABLAS[contrato]:
        e = CP.esquema(V.C, t, sel.get(t, []))
        if e:
            mot.append("C1 esquema %s: %s" % (t, e))
    comp = RULES.e12_verificar_celda(rows, cid, fid, instrumento=ce["instrumento"], barras=tuple(ce.get("barras") or ()), tasa=ce.get("tasa"),
                                     run_geometry=bool(ce.get("run_geometry", True)), con_unidad=bool(ce.get("con_unidad", True)), omega_id=ce.get("omega_id"))
    if comp["estado"] != "completa":
        mot.append("C2 E12 %s: %s" % (comp["estado"], "; ".join(comp["motivos"])[:200]))
    if contrato == "v3":
        err = CP.checker_nucleo(V.C, V.ctx.inp.d7, CP.filas_de_celda(rows, cid, fid, "v3"), V.ctx.inp.tolerances)
        if err:
            mot.append("C3 checker del núcleo: %s" % "; ".join(err)[:300])
    else:
        aus = set(u.get("evidencia_ausente") or [])
        if not (set(CP.HIJAS) | {"convergence_result:C2"}) <= aus:
            mot.append("C4 v2 sin evidencia ausente declarada completa")
        if any(x.get("cell_id") == cid for t in CP.HIJAS for x in rows.get(t, []) if isinstance(x, dict)):
            mot.append("C4 v2 con tablas hijas de la celda (no es v2)")
    return ("rechazada" if mot else "aceptada_por_el_consumidor"), mot


def instantanea_paquetes(dout):
    """lima1324 (corrección A): UNA lectura del índice y de los archivos de paquete que declara (solo nombres simples dentro de dout).
    La entrada común verifica EXACTAMENTE estos bytes y el consumidor consume EXACTAMENTE estos bytes (nunca vuelve a leer dout)."""
    dout = Path(dout)
    snap = {}
    try:
        raw = (dout / "paquetes_indice.json").read_bytes()
    except OSError:
        return snap
    snap["paquetes_indice.json"] = raw
    try:
        ind = json.loads(raw)
    except ValueError:
        return snap
    paq = ind.get("paquetes") if isinstance(ind, dict) else None
    if isinstance(paq, dict):
        for meta in paq.values():
            a = meta.get("archivo") if isinstance(meta, dict) else None
            if isinstance(a, str) and a not in snap and Path(a).name == a and a != "paquetes_indice.json":
                try:
                    snap[a] = (dout / a).read_bytes()
                except OSError:
                    pass        # ausente: la entrada común lo rechaza (archivo fuera de la instantánea)
    return snap


IDENTIDAD_PRODUCTOR = ("area", "inventario", "productor", "producer_sha256", "contrato", "run_class", "etiqueta", "autorizacion_sha256", "config_sha256",
                       "variante")      # lima0845: la variante (resumen autenticado o None) forma parte de la identidad del productor


def clave_productor(reg):
    """lima1324 (corrección B): identidad COMPLETA del productor registrado (no solo la entrega)."""
    return sha(json.dumps({k: reg.get(k) for k in IDENTIDAD_PRODUCTOR}, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def validar_paquetes_procedencia(V, dout, PP, pre=None, salida_entrada=None):
    """Ruta del consumidor REAL para paquetes por procedencia (v2, lima1324):
    1. INSTANTÁNEA: índice y paquetes leídos UNA vez (instantanea_paquetes);
    2. ENTRADA COMÚN sobre esa misma instantánea (PP.verificar(..., instantanea=...)); sin índice global verificado no entra nada;
    3. CONTINUIDAD: cada paquete consumido sale de la instantánea y su sha256 es el que verificó la entrada común;
    4. IDENTIDADES Y CANTIDADES: las unidades de cada lote son EXACTAMENTE las esperadas desde la autoridad (número y sha256 de los
       ids ordenados) y lo consumido globalmente coincide con la identidad global esperada; un lote vacío o incompleto nunca se acepta;
    5. PRODUCTORES: registro por identidad COMPLETA (área, inventario, productor y su sha256, contrato, despliegue, encargo, config y,
       desde lima0845, la VARIANTE autenticada o None), cada lote vinculado a su productor, igual al productor esperado desde la
       autoridad (también en su variante); cobertura completa y sin sobrescrituras;
    6. CONTENIDO por unidad (C1–C4) con bytes autenticados por el inventario verificado de su entrega (una sola lectura);
    7. ORIGEN: al terminar se relee el directorio; si cambió respecto de la instantánea, el dictamen es «rechazado» y nada es
       consumible (ningún subconjunto se acepta en silencio)."""
    import tempfile
    import time as _t
    t0 = _t.time()
    dout = Path(dout)
    snap = instantanea_paquetes(dout)
    huella = {k: sha(v) for k, v in snap.items()}
    with tempfile.TemporaryDirectory() as tmp:
        ent = PP.verificar(dout, pre, salida_entrada or Path(tmp) / "entrada.json", instantanea=snap)
    aut = PP.autoridad(pre)
    res = {"ruta": RUTA_PROCEDENCIA, "entrada_comun": {k: ent.get(k) for k in ("aceptados", "unidades_aceptadas", "lotes_esperados", "unidades_esperadas",
                                                                             "lotes_esperados_ausentes", "indice_global_verificado", "rechazo_indice", "completo",
                                                                             "lectura", "identidad_esperada_global")},
           "instantanea": {"archivos": len(snap), "sha256": huella}, "productores": {}, "productores_por_lote": {}, "lotes": {}, "unidades": {}}

    def cerrar(dictamen, motivos=()):
        us = list(res["unidades"].values())
        res["resumen"] = {"lotes_aceptados": sum(1 for v in res["lotes"].values() if v.get("aceptado")), "lotes": len(res["lotes"]),
                          "unidades_aceptadas": sum(1 for x in us if x["estado"] == "aceptada_por_el_consumidor"),
                          "rechazadas": sum(1 for x in us if x["estado"] == "rechazada"), "no_comprobables": sum(1 for x in us if x["estado"] == "no_comprobable"),
                          "por_contrato": {c: sum(1 for x in us if x["contrato"] == c and x["estado"] == "aceptada_por_el_consumidor") for c in ("v2", "v3")},
                          "no_aplicables_aceptadas": sum(1 for x in us if not x["numerico"] and x["estado"] == "aceptada_por_el_consumidor"),
                          "segundos": round(_t.time() - t0, 1)}
        res["dictamen"] = dictamen
        res["motivos_del_dictamen"] = list(motivos)
        res["consumible"] = dictamen == "aceptado"
        return res
    if not ent.get("indice_global_verificado"):
        return cerrar("rechazado: índice global no verificado por la entrada común")
    bv = ent.get("bytes_verificados") or {}
    discont = sorted(k for k in bv if bv[k] != huella.get(k))
    if discont or bv.get("paquetes_indice.json") != huella.get("paquetes_indice.json"):
        return cerrar("rechazado: los bytes verificados no son los de la instantánea", ["discontinuidad: %s" % ", ".join(discont[:5] or ["paquetes_indice.json"])])
    ind = json.loads(snap["paquetes_indice.json"])
    ide = ent.get("identidad_esperada_por_lote") or {}
    pes = ent.get("productores_esperados") or {}
    aceptadas_ids = []
    for lote, meta in ind["paquetes"].items():
        if not (ent.get("paquetes", {}).get(lote) or {}).get("aceptado"):
            res["lotes"][lote] = {"aceptado": False, "motivo": "rechazado por la entrada común"}
            continue
        try:
            raw = snap[meta["archivo"]]
            need(bv.get(meta["archivo"]) == sha(raw), "CONTINUIDAD", "bytes consumidos distintos de los verificados: %s" % meta["archivo"])
            p = json.loads(raw)
            ids = [u["unidad"] for u in p["unidades"]]
            e = ide.get(lote) or {}
            need(len(ids) == len(set(ids)) == e.get("unidades") and PP.ids_sha(ids) == e.get("ids_sha256") and len(ids) > 0, "IDENTIDAD_DE_UNIDADES",
                 "lote %s: %d unidades (esperadas %s) o identidades distintas de las esperadas desde la autoridad" % (lote, len(ids), e.get("unidades")))
            reg, files = _productor_y_inventario(V, p, aut)
            pe = pes.get(lote) or {}
            need((reg["area"], reg["productor"], reg["producer_sha256"]) == (pe.get("entrega"), pe.get("archivo"), pe.get("sha256")), "PRODUCTOR_NO_AUTENTICADO",
                 "productor del lote %s distinto del esperado desde la autoridad" % lote)
            need(reg.get("variante") == pe.get("variante"), "VARIANTE_INCOHERENTE",
                 "variante del productor del lote %s distinta de la esperada desde la autoridad (omisión, sustitución o atribución al original)" % lote)
            k = clave_productor(reg)
            if k in res["productores"]:
                need({x: res["productores"][k].get(x) for x in IDENTIDAD_PRODUCTOR} == {x: reg.get(x) for x in IDENTIDAD_PRODUCTOR}, "PRODUCTOR_NO_AUTENTICADO", "colisión de identidad")
                res["productores"][k]["lotes"].append(lote)
            else:
                res["productores"][k] = dict(reg, identidad_sha256=k, lotes=[lote])
            res["productores_por_lote"][lote] = k
        except (Rechazo, OSError, ValueError, KeyError, TypeError) as ex:
            res["lotes"][lote] = {"aceptado": False, "motivo": "%s: %s" % (getattr(ex, "codigo", type(ex).__name__), getattr(ex, "detalle", ex))}
            continue
        cuenta = {}
        for u in p["unidades"]:
            try:
                st, mot = contenido_unidad(V, u, p, files, V.T)
            except Rechazo as ex:
                st, mot = "rechazada", ["%s: %s" % (ex.codigo, ex.detalle)]
            except (KeyError, ValueError, TypeError, AttributeError, OSError) as ex:
                st, mot = "rechazada", ["ESQUEMA_O_REFERENCIA: %s: %s" % (type(ex).__name__, ex)]
            res["unidades"][u["unidad"]] = {"lote": lote, "contrato": p["contrato"], "numerico": u["numerico"], "familia": u["familia"], "estado": st, "motivos": mot[:4]}
            cuenta[st] = cuenta.get(st, 0) + 1
            if st == "aceptada_por_el_consumidor":
                aceptadas_ids.append(u["unidad"])
        ok = cuenta.get("aceptada_por_el_consumidor", 0) == e.get("unidades") and cuenta.get("rechazada", 0) == 0 and cuenta.get("no_comprobable", 0) == 0
        res["lotes"][lote] = {"aceptado": ok, "contrato": p["contrato"], "unidades": len(p["unidades"]), "unidades_esperadas": e.get("unidades"), "estados": cuenta,
                              "productor": res["productores_por_lote"][lote]}
    # ---- cobertura global (identidades) y de productores
    ge = ent.get("identidad_esperada_global") or {}
    glob = {"lotes_aceptados": sum(1 for v in res["lotes"].values() if v.get("aceptado")), "lotes_esperados": ge.get("lotes"),
            "unidades_aceptadas": len(aceptadas_ids), "unidades_esperadas": ge.get("unidades"),
            "ids_sha256_aceptadas": PP.ids_sha(aceptadas_ids), "ids_sha256_esperadas": ge.get("ids_sha256")}
    glob["exacta"] = (glob["lotes_aceptados"] == glob["lotes_esperados"] and glob["unidades_aceptadas"] == glob["unidades_esperadas"]
                      and glob["ids_sha256_aceptadas"] == glob["ids_sha256_esperadas"] and len(set(aceptadas_ids)) == len(aceptadas_ids))
    res["cobertura_global"] = glob
    esperados = {(v["entrega"], v["archivo"], v["sha256"], (v.get("variante") or {}).get("identidad")) for v in pes.values()}
    registrados = {(v["area"], v["productor"], v["producer_sha256"], (v.get("variante") or {}).get("identidad")) for v in res["productores"].values()}
    sin_productor = sorted(l for l, v in res["lotes"].items() if v.get("aceptado") and l not in res["productores_por_lote"])
    vinculados = sorted(l for v in res["productores"].values() for l in v["lotes"])
    res["cobertura_productores"] = {"productores_esperados": len(esperados), "productores_registrados": len(res["productores"]),
                                    "identidades_registradas_iguales_a_las_esperadas": registrados == esperados,
                                    "lotes_vinculados": len(vinculados), "lotes_vinculados_una_vez": len(vinculados) == len(set(vinculados)),
                                    "lotes_aceptados_sin_productor": sin_productor, "sobrescrituras": 0}
    res["cobertura_productores"]["completa"] = (res["cobertura_productores"]["identidades_registradas_iguales_a_las_esperadas"]
                                                 and not sin_productor and res["cobertura_productores"]["lotes_vinculados_una_vez"])
    # ---- origen: ¿cambió el directorio tras la instantánea verificada?
    snap2 = instantanea_paquetes(dout)      # comparado con las huellas tomadas ANTES de verificar (no con el objeto en memoria)
    h2 = {k: sha(v) for k, v in snap2.items()}
    cambios = sorted(k for k in set(huella) | set(h2) if huella.get(k) != h2.get(k))
    res["origen_sin_cambios_tras_la_instantanea"] = not cambios
    res["cambios_en_el_origen"] = cambios
    if cambios:
        return cerrar("rechazado: el origen cambió tras la instantánea verificada; nada es consumible", ["archivos cambiados: %s" % ", ".join(cambios[:6])])
    motivos = []
    if not glob["exacta"]:
        motivos.append("cobertura global distinta de la esperada")
    if not res["cobertura_productores"]["completa"]:
        motivos.append("cobertura de productores incompleta")
    if glob["exacta"] and res["cobertura_productores"]["completa"] and glob["lotes_aceptados"] == len(res["lotes"]):
        return cerrar("aceptado")
    return cerrar("parcial o rechazado", motivos)
