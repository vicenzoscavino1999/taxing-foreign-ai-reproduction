"""FAM03 (quiebres históricos PROD1/PROD2: 120 tareas = 120 unidades; Q histórica PROD3: 16 tareas = 32 salidas Q): plan de producción
limpio derivado por plan_prod.construir y comparado con el histórico, comprobación sin cálculo de entradas, referencias y cobertura, cálculo y
validación de UNA tarea del plan (los pasos de tarea_prod.main con evaluadores_ra), revalidación sin cálculo de bytes guardados, comparación
con el árbol aceptado de la tarea y receta completa (sin ejecutarla).

Piezas (copias exactas salvo lo declarado; ver fuentes_fam03.json):
- ruta PROD instalada (nucleo_s6/instalacion/herramientas/b): tarea_prod.py U08 (3204ebe5…), validador_prod.py U09 (88918191…),
  evaluadores_ra.py (db962e34…), plan_prod.py, decision_d4.py, calendario_paso4.py, registro_productivo.py (d9addec6…, FAM01) y
  datos/paso4/lista_PROD.json (42fe8914…: 152 unidades = 40 PROD1 + 80 PROD2 + 32 PROD3);
- área R-A (nucleo_s6/instalacion/ra): puerto_ra.py (ImportadorRA), R_A_dependencias.json (copia pública) y los 17 módulos históricos y
  portados de EQ/EQM/QSEN2 (codigo.ensayo_quiebres, codigo.ensayo_quiebres_macro, codigo.sensibilidad_q y su cierre), más su entrega
  lima1958 (nucleo_s6/raiz/tmp/cierre_df_paso4_3_7_2026-10-05_lima1958, inventario anclado en r1_rutas.ENTREGAS);
- núcleo S6 y contexto: los de FAM01/FAM02 (fam01.Contexto, nucleo_s6/instalacion/src/paper2b);
- referencias (solo para comparar): los 136 árboles aceptados del catálogo (referencias/fam03/paquete) y el plan histórico (copia pública).

Lo ejecutado históricamente es evaluadores_ra (estructural / macro / q_afirmacion), no tarea_prod.buscar()/q_ambito() (ruta anterior que main ya
no llama). La Q de PROD3 es la de codigo.sensibilidad_q con la decisión sellada Q-CONTINUO-COTA-SUPERIOR-v2 (no es R1-F de FAM02 ni la Q local
m=1/2 de FAM12). El plan histórico tiene resumen_q = null: la ruta efectiva no consume un resumen de detalle (solo q_ambito, no ejecutada, lo hacía).

Adaptaciones de interfaz (no cambian fórmulas, tolerancias, topes, presupuestos ni criterios):
- contexto: fam01.Contexto (misma construcción que ContextoS6, sin autoridad viva) con run_class = paso4_operativo_s6 (el del despliegue de la
  producción; lo registra cada documento de unidad histórico) y etiqueta FAM03; despliegue = datos/fam03/despliegue.json (sin rutas privadas);
- plan: plan_prod.construir(None, contexto_esperado, decision_q, decisiones) con las decisiones del plan histórico (Q-CONTINUO-COTA-SUPERIOR-v2 y
  QUIEBRES-D4 0494f042…) y el contexto esperado de esta base (datos/fam03/contexto_esperado.json, fijado por fam03-preparar sin cálculo); se
  verifica con la rama de producción de corrida_paso4.verificar_plan y se compara con el plan histórico (iguales salvo contexto esperado,
  huella pública de R_A_dependencias y plan_sha256);
- CO-CANON-v1: corrida_paso4 (coordinador histórico con autorización y rutas privadas) no se copia; tarea_prod solo usa de él canon (misma
  serialización: fam01.canon), REGISTRO y DICTAMEN, que se exponen con ese nombre de módulo;
- RA-AREA-v1: la copia pública de R_A_dependencias.json declara el área R-A por su ruta relativa a la raíz; puerto_ra la resuelve en
  nucleo_s6/raiz al cargarse (en el original era una ruta absoluta del equipo de origen);
- RAIZ-CONTRATOS-v1: validador_prod.raiz_contratos busca la raíz del proyecto entre los PADRES de la instalación; en el paquete la raíz copiada
  es nucleo_s6/raiz (hermana): se devuelve esa raíz, con la misma inserción en sys.path;
- RELOJ-PILOTO-v1: el reloj interno de la tarea usa el tope del plan (2400 s, el de la producción); el límite externo de una invocación lo pone
  el supervisor (600 s en los pilotos): si se agota, el árbol de procesos termina y la tarea queda incompleta; ningún presupuesto se reduce;
- identidades del vínculo (contexto, despliegue, plan, dependencias R-A) son las de esta base; el validador instalado las exige iguales a las
  de quien valida, como en la producción;
- F2-ENTORNO-PORTABLE-v1 extendida a FAM03 (el autor, 2026-11-20): la identidad del contexto S6 se admite si es la esperada del plan sellado
  (496135b0…) o si solo difiere en sus dos campos de entorno (huella_entorno_sha256 y tecnicas.environment_sha256) y el entorno cumple F2
  frente al del plan: perfil aprobado (conforms, sin desajustes) y proyección F2 igual a la del entorno con que fam03-preparar fijó la
  identidad (datos/fam03/entorno_f2_referencia.json); con esos dos campos sustituidos por los del entorno del plan, la identidad es
  exactamente la esperada. Lo exigen fam03-comprobar (antes de lanzar las tareas), fam03-unidad y fam03-validar (admision_contexto). El plan,
  los presupuestos, las tolerancias y COMPARACION-FAM03-v1 no cambian.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
import types
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAIZ = BASE / "nucleo_s6" / "raiz"
INST = BASE / "nucleo_s6" / "instalacion"
T = RAIZ / "tmp"
DATOS = BASE / "datos" / "fam03"
REF = BASE / "referencias" / "fam03"
ETIQUETA = "REPRODUCCION LIMPIA FAM03 NO OFICIAL"
RUN_CLASS = "paso4_operativo_s6"
ENTREGA_RA = "cierre_df_paso4_3_7_2026-10-05_lima1958"
KIND_PLAN = "plan-corrida-paso4-produccion-v1"
REGISTRO, DICTAMEN = "registro_productivo.json", "dictamen_validacion.json"
FAMILIAS = {"PROD1": ("F03-QUIEBRES", "evaluadores_ra.estructural (cuerpo de codigo.ensayo_quiebres)"),
            "PROD2": ("F03-QUIEBRES", "evaluadores_ra.macro (cuerpo de codigo.ensayo_quiebres_macro)"),
            "PROD3": ("F03-Q", "evaluadores_ra.q_afirmacion (cuerpo de codigo.sensibilidad_q) + mapear_q (decision_q sellada)")}
ESTADOS_ADMISIBLES = ("completa_validada", "no_aplicable_validada")
ADAPTACIONES = ("contexto FAM03 (fam01.Contexto, run_class paso4_operativo_s6)", "plan limpio (plan_prod.construir) comparado con el histórico",
                "CO-CANON-v1", "RA-AREA-v1", "RAIZ-CONTRATOS-v1", "RELOJ-PILOTO-v1",
                "F2-ENTORNO-PORTABLE-v1 extendida a FAM03 (identidad del contexto S6)")


class Fam03Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam03Error(codigo)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_archivo(p: Path):
    """Huella del archivo, o None si falta (las comprobaciones informan la ausencia en lugar de detenerse)."""
    return sha(Path(p).read_bytes()) if Path(p).is_file() else None


def cargar(nombre: str, ruta: Path):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def F1():
    return cargar("fam01", BASE / "src" / "fam01.py")


def canon(o) -> bytes:
    return F1().canon(o)


def leer(p: Path):
    return json.loads(Path(p).read_bytes())


def rel(p: Path) -> str:
    p = Path(p).resolve()
    return p.relative_to(BASE.resolve()).as_posix() if p.is_relative_to(BASE.resolve()) else p.name


# ================================================================================================ entorno: F2 extendida a FAM03
# F2-ENTORNO-PORTABLE-v1 (src/fam01.py: REGLA_F2, CAMPOS_UBICACION_F2, proyeccion_f2), sin cambios de contenido, aplicada a la identidad del
# contexto S6 de FAM03. La identidad esperada (plan sellado: contexto_esperado.identidad_sha256 = datos/fam03/contexto_identidad.json) se fijó
# con el entorno del 2026-11-16; otro entorno solo puede diferir de él en la ubicación. Se exige: (1) la referencia sellada intacta (identidad
# esperada y proyección F2 del entorno del plan, datos/fam03/entorno_f2_referencia.json); (2) el documento de entorno es el de la identidad
# calculada (environment_sha256 y huella); (3) fuera de sus dos campos de entorno, la identidad es la esperada componente a componente; (4) el
# entorno cumple el perfil aprobado; (5) su proyección F2 es la del entorno del plan; (6) con los dos campos de entorno del plan, la identidad
# calculada da exactamente la esperada. Cualquier otra diferencia (código, contrato, configuración, datos, tolerancias, paquetes, intérprete,
# BLAS, hilos, semilla...) rechaza la identidad y se informa el campo exacto.
CAMPOS_ENTORNO_DE_LA_IDENTIDAD = ("huella_entorno_sha256", "tecnicas.environment_sha256")
ADOPCION_F2_FAM03 = {
    "regla": "F2-ENTORNO-PORTABLE-v1",
    "estado": "extendida por el autor a FAM03",
    "fecha": "2026-11-20",
    "decision": ("Elijo la opción 1 para FAM03, condicionada a que demuestres que el entorno con que se fijó el plan y el entorno público "
                 "cumplen el mismo perfil y solo difieren en los campos de ubicación admitidos por F2."),
    "condicion_demostrada": "datos/fam03/entorno_f2_referencia.json (entorno_del_plan, entorno_publico_comprobado, campos_que_difieren)",
    "alcance": ("identidad del contexto S6 de FAM03 en fam03-comprobar, fam03-unidad y fam03-validar; el plan sellado (contexto_esperado), "
                "los presupuestos, las tolerancias y COMPARACION-FAM03-v1 no cambian"),
    "no_cubre": "cambios de código, contrato, configuración, datos, tolerancias o criterios científicos, ni otro perfil de entorno"}


def _plano(o, pre: str = "") -> dict:
    """{ruta.con.puntos: valor} de los diccionarios anidados (las listas son valores)."""
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            out.update(_plano(v, pre + "." + k if pre else k))
        return out
    return {pre: o}


def admision_contexto(identidad: dict, identidad_sha256: str, doc: dict, rec: dict, esperada: dict, ref: dict, ce: dict,
                      no_registradas: list = ()) -> dict:
    """Admisión de la identidad del contexto S6 de FAM03 (F2 extendida a FAM03; ver la cabecera de la sección). Función pura de: identidad y
    documento de entorno calculados (y RECORD sin lanzadores), identidad esperada (contexto_identidad.json), referencia F2
    (entorno_f2_referencia.json), contexto_esperado del plan y los archivos de referencia que no coinciden con fuentes_fam03.json.
    «admitido» solo si no hay motivos."""
    preparar()
    from paper2b import keys as K
    f = F1()
    h = lambda o: sha(K.canon(o))
    mot = []
    esp_id = esperada.get("identity") or {}
    pe = _plano(json.loads(K.canon(esp_id)))
    ref_plan = ref.get("entorno_del_plan") or {}
    # (1) referencia sellada
    if no_registradas:
        mot.append("REFERENCIA_DISTINTA_DE_SU_REGISTRO_EN_FUENTES: %s" % sorted(no_registradas))
    if not (h(esp_id) == esperada.get("identity_sha256") == ce.get("identidad_sha256")):
        mot.append("IDENTIDAD_ESPERADA_DISTINTA_DE_LA_DEL_PLAN")
    if sha(f.canon(ref.get("proyeccion"))) != ref.get("proyeccion_sha256"):
        mot.append("REFERENCIA_F2_ALTERADA")
    if (ref_plan.get("fingerprint_sha256"), ref_plan.get("environment_sha256")) != (pe.get("huella_entorno_sha256"), pe.get("tecnicas.environment_sha256")):
        mot.append("REFERENCIA_F2_NO_ES_LA_DEL_ENTORNO_DEL_PLAN")
    # (2) documento de entorno de la identidad calculada
    pa = _plano(json.loads(K.canon(identidad)))
    if h(identidad) != identidad_sha256:
        mot.append("IDENTIDAD_CALCULADA_INCOHERENTE")
    env = sha(f.canon(doc) + b"\n")
    if env != pa.get("tecnicas.environment_sha256"):
        mot.append("DOCUMENTO_DE_ENTORNO_DISTINTO_DEL_DE_LA_IDENTIDAD")
    if doc.get("fingerprint_sha256") != pa.get("huella_entorno_sha256"):
        mot.append("HUELLA_DE_ENTORNO_DISTINTA_DE_LA_DEL_DOCUMENTO")
    # (3) resto de la identidad, componente a componente
    otros = sorted(k for k in set(pa) | set(pe) if k not in CAMPOS_ENTORNO_DE_LA_IDENTIDAD and pa.get(k, "<falta>") != pe.get(k, "<falta>"))
    if otros:
        mot.append("IDENTIDAD_DISTINTA_FUERA_DEL_ENTORNO: %s" % otros[:12])
    # (4) perfil aprobado
    if doc.get("conforms") is not True or doc.get("mismatches"):
        mot.append("PERFIL_NO_CUMPLE: %s" % (doc.get("mismatches") or ["conforms != true"])[:8])
    # (5) proyección F2 = la del entorno del plan
    pr = f.proyeccion_f2(doc, rec)
    campos_f2 = []
    if sha(f.canon(pr)) != ref.get("proyeccion_sha256"):
        a, b = _plano(json.loads(f.canon(pr))), _plano(json.loads(f.canon(ref.get("proyeccion") or {})))
        campos_f2 = sorted(k for k in set(a) | set(b) if a.get(k, "<falta>") != b.get(k, "<falta>"))
        mot.append("ENTORNO_DISTINTO_FUERA_DE_LA_UBICACION: %s" % campos_f2[:12])
    # (6) con los dos campos de entorno del plan, la identidad es exactamente la esperada
    s = json.loads(K.canon(identidad))
    if isinstance(s.get("tecnicas"), dict):
        s["huella_entorno_sha256"], s["tecnicas"]["environment_sha256"] = ref_plan.get("fingerprint_sha256"), ref_plan.get("environment_sha256")
    if h(s) != ce.get("identidad_sha256"):
        mot.append("IDENTIDAD_CON_EL_ENTORNO_DEL_PLAN_DISTINTA_DE_LA_ESPERADA")
    return {"regla": ADOPCION_F2_FAM03["regla"], "adopcion": "%s el %s" % (ADOPCION_F2_FAM03["estado"], ADOPCION_F2_FAM03["fecha"]),
            "admitido": not mot, "via": "identica" if identidad_sha256 == ce.get("identidad_sha256") else "F2", "motivos": mot,
            "identidad_sha256": identidad_sha256, "identidad_esperada_sha256": ce.get("identidad_sha256"),
            "environment_sha256": env, "environment_sha256_del_plan": ref_plan.get("environment_sha256"),
            "campos_de_entorno_distintos": [c for c in CAMPOS_ENTORNO_DE_LA_IDENTIDAD if pa.get(c) != pe.get(c)],
            "otros_campos_distintos": otros, "campos_f2_distintos": campos_f2}


def contexto_admitido(ctx, plan: dict) -> dict:
    """admision_contexto del contexto construido frente al plan sellado y a los datos de la base (registrados en fuentes_fam03.json)."""
    fu = {x["archivo"]: x["sha256"] for x in leer(BASE / "fuentes_fam03.json")["archivos"]}
    refs = ("datos/fam03/contexto_identidad.json", "datos/fam03/entorno_f2_referencia.json")
    no_reg = [r for r in refs if not (BASE / r).is_file() or sha((BASE / r).read_bytes()) != fu.get(r)]
    return admision_contexto(ctx.identity, ctx.identity_sha256, ctx.env_doc, ctx.env_rec, leer(DATOS / "contexto_identidad.json"),
                             leer(DATOS / "entorno_f2_referencia.json"), plan.get("contexto_esperado") or {}, no_reg)


def exigir_contexto(ctx, plan: dict) -> dict:
    """fam03-unidad y fam03-validar: el contexto debe quedar admitido (mismo criterio que fam03-comprobar)."""
    a = contexto_admitido(ctx, plan)
    need(a["admitido"], "CONTEXTO_DISTINTO_DEL_ESPERADO_POR_EL_PLAN: %s" % "; ".join(a["motivos"])[:800])
    return a


# ================================================================================================ entorno de módulos
def preparar():
    """sys.path como seleccion_paso4.configurar (= fam02.preparar): núcleo S6 de la instalación delante y la raíz copiada después; la carpeta
    herramientas/b de la instalación al final (tarea_prod se lanzaba como guion desde ella: decision_d4, plan_prod por nombre)."""
    for p in (str(RAIZ / "src"), str(RAIZ), str(INST / "src")):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(INST / "src"))
    hb = str(INST / "herramientas" / "b")
    if hb not in sys.path:
        sys.path.append(hb)
    import paper2b
    need(Path(paper2b.__file__).resolve().parent == (INST / "src" / "paper2b").resolve(), "NUCLEO_S6_NO_ES_EL_DE_LA_INSTALACION:" + paper2b.__file__)


def co_canon():
    """CO-CANON-v1: lo que tarea_prod usa de corrida_paso4 (canon, REGISTRO, DICTAMEN), con el mismo código de serialización."""
    m = sys.modules.get("corrida_paso4")
    if m is None:
        m = types.ModuleType("corrida_paso4", "FAM03 CO-CANON-v1: canon/REGISTRO/DICTAMEN de corrida_paso4 (el coordinador histórico no se copia)")
        m.canon, m.REGISTRO, m.DICTAMEN, m.FAM03_CO_CANON = F1().canon, REGISTRO, DICTAMEN, True
        sys.modules["corrida_paso4"] = m
    need(getattr(m, "FAM03_CO_CANON", False), "CORRIDA_PASO4_AJENA_CARGADA")
    return m


def adaptar_raiz_contratos(VPm) -> None:
    """RAIZ-CONTRATOS-v1 (ver cabecera)."""
    def raiz_contratos():
        need((RAIZ / "herramientas/bloque2/contratos_g_na_1").is_dir(), "RAIZ_SIN_CONTRATOS_G_NA_1")
        if str(RAIZ) not in sys.path:
            sys.path.append(str(RAIZ))
        return RAIZ
    VPm.raiz_contratos = raiz_contratos


def adaptar_area_ra(PRA) -> None:
    """RA-AREA-v1 (ver cabecera)."""
    h = PRA.DEP["historico"]
    if Path(h).is_absolute():
        need(Path(h).resolve() == (T / ENTREGA_RA).resolve(), "AREA_RA_FUERA_DEL_PAQUETE")
    else:
        need(h == "tmp/" + ENTREGA_RA, "AREA_RA_DISTINTA")
        PRA.DEP["historico"] = str(RAIZ / h)


def pila() -> types.SimpleNamespace:
    """Módulos PROD de la instalación copiada con las adaptaciones; sin contexto ni cálculo."""
    preparar()
    co_canon()
    TP = cargar("tarea_prod", INST / "herramientas/b/tarea_prod.py")
    need(sha((INST / "herramientas/b/tarea_prod.py").read_bytes()) == "3204ebe5c13f856a8fd38e4ce55da7c1b90489a3ba25c9b105208f815b9d3d9f", "TAREA_PROD_DISTINTA")
    RP = TP._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    VPm = TP._carga("validador_prod", "herramientas/b/validador_prod.py")
    adaptar_raiz_contratos(VPm)
    ER = TP._carga("evaluadores_ra", TP.ER_REL)
    PL = TP._carga("plan_prod", "herramientas/b/plan_prod.py")
    D4 = TP._carga("decision_d4", "herramientas/b/decision_d4.py")
    RR = TP._carga("r1_rutas", "herramientas/b/r1_rutas.py")
    PRA = cargar("puerto_ra", INST / "ra" / "puerto_ra.py")
    adaptar_area_ra(PRA)
    return types.SimpleNamespace(TP=TP, RP=RP, VPm=VPm, ER=ER, PL=PL, D4=D4, RR=RR, PRA=PRA)


def contexto():
    preparar()
    f = F1()
    return f.Contexto(dict(f.parametros(), etiqueta=ETIQUETA, run_class=RUN_CLASS), raiz=RAIZ, inst=INST)


# ================================================================================================ datos de la base limpia (sin cálculo)
def despliegue_doc() -> dict:
    p = F1().parametros()
    return {"descripcion": ("Despliegue de FAM03 en la base limpia (sustituye a despliegue_operativo.json de la producción, f293a0a6…, que contiene "
                            "rutas, autor y anclas de autorización del equipo de origen). Solo lo que usa la ruta: raíz copiada, paquete S6 y D7 de "
                            "FAM01, run_class de la producción (paso4_operativo_s6, el que registra cada documento de unidad histórico) y etiqueta NO "
                            "OFICIAL. Sin acto de autorización (ancla = null)."),
            "raiz_proyecto": "nucleo_s6/raiz", "raiz_fuentes": "nucleo_s6/raiz/tmp", "s6_package": p["s6_package"], "ancla": None, "d7_dir": p["d7_dir"],
            "d7_tree": p["d7_tree"], "run_class": RUN_CLASS, "etiqueta": ETIQUETA}


def lista_bytes() -> bytes:
    return (INST / "datos/paso4/lista_PROD.json").read_bytes()


def plan_historico() -> dict:
    return leer(REF / "plan_prod_historico.json")


def plan_limpio() -> dict:
    return leer(DATOS / "plan_prod.json")


def regla_pilotos(plan: dict) -> dict:
    prim = {}
    for t in plan["tareas"]:
        prim.setdefault(t["familia"], t)
    return {"regla": ("primera tarea de cada familia (PROD1, PROD2, PROD3) en el orden del plan de producción (plan_prod.construir, igual al "
                      "histórico); fijada por identificador antes de calcular, sin mirar resultados"),
            "pilotos": [{"tarea": t["id"], "familia": f, "ruta": FAMILIAS[f][1], "unidades": list(t["unidades"]),
                         "cobertura": "tarea mínima del plan: %d unidad(es) (%s)" % (len(t["unidades"]), "2 salidas Q: global y país" if f == "PROD3" else
                                                                                     "1 búsqueda de quiebre")} for f, t in sorted(prim.items())],
            "nota": "PROD1 y PROD2 recorren rutas distintas (EQ estructural / EQM macro): un piloto por familia"}


def preparar_datos() -> dict:
    """fam03-preparar (SIN CÁLCULO): despliegue, contexto esperado (construye el contexto S6 una vez; ninguna búsqueda), plan limpio y
    selección de pilotos en datos/fam03. No sobrescribe un dato existente con otro contenido."""
    t0 = time.time()
    DATOS.mkdir(parents=True, exist_ok=True)

    def fijar(nombre, doc):
        raw = (json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
        p = DATOS / nombre
        if p.exists():
            need(p.read_bytes() == raw, "DATO_EXISTENTE_DISTINTO: datos/fam03/%s" % nombre)
        else:
            p.write_bytes(raw)
        return raw
    dr = fijar("despliegue.json", despliegue_doc())
    ctx = contexto()
    t_ctx = round(time.time() - t0, 2)
    fijar("contexto_identidad.json", {"identity": ctx.identity, "identity_sha256": ctx.identity_sha256,
                                      "descripcion": "identidad del contexto S6 limpio de FAM03 (fam01.Contexto con run_class paso4_operativo_s6)"})
    ce = {"identidad_sha256": ctx.identity_sha256, "despliegue_sha256": sha(dr),
          "procedencia": {"contexto": "datos/fam03/contexto_identidad.json", "despliegue": "datos/fam03/despliegue.json"}}
    fijar("contexto_esperado.json", ce)
    S = pila()
    ph = plan_historico()
    plan = S.PL.construir(None, ce, ph["decision_q"], ph["decisiones"])
    fijar("plan_prod.json", plan)
    fijar("pilotos.json", regla_pilotos(plan))
    return {"contexto_s": t_ctx, "identidad_sha256": ctx.identity_sha256, "plan_sha256": plan["plan_sha256"], "pilotos": regla_pilotos(plan)["pilotos"],
            "segundos": round(time.time() - t0, 2), "calculo": "ninguno (solo construcción del contexto)"}


# ================================================================================================ plan
def verificar_plan(plan: dict, S) -> dict:
    """Rama de producción de corrida_paso4.verificar_plan (CO-CANON-v1), sin cambios de criterio."""
    cuerpo = {k: v for k, v in plan.items() if k not in ("plan_sha256", "anexo_comandos")}
    need(plan.get("plan_sha256") == sha(canon(cuerpo)), "PLAN_ALTERADO")
    need(all(v is False for v in plan["banderas_oficiales"].values()), "PLAN_OFICIAL_NO_AUTORIZADO")
    need(plan.get("kind") == KIND_PLAN, "PLAN_NO_ES_DE_PRODUCCION")
    try:
        S.D4.admitida_en_plan(plan.get("decisiones"))
    except ValueError as ex:
        raise Fam03Error("DECISION_DEL_PLAN_NO_ADMITIDA: %s" % ex)
    need(cuerpo == {k: v for k, v in S.PL.construir(plan.get("resumen_q"), plan.get("contexto_esperado"), plan.get("decision_q"),
                                                    plan.get("decisiones")).items() if k != "plan_sha256"}, "PLAN_PROD_NO_DERIVADO_DE_SELECCION_Y_CALENDARIO_VIGENTES")
    ax = plan.get("anexo_comandos")
    if ax is not None:
        need(ax.get("plan_sha256") == plan["plan_sha256"] and ax.get("anexo_sha256") == sha(canon({k: v for k, v in ax.items() if k != "anexo_sha256"})),
             "ANEXO_DE_COMANDOS_ALTERADO")
    return plan


def hojas(v, pref=""):
    """{puntero: valor hoja} (listas por índice)."""
    if isinstance(v, dict):
        out = {}
        for k in sorted(v):
            out.update(hojas(v[k], pref + "/" + str(k)))
        return out or {pref: {}}
    if isinstance(v, list):
        out = {}
        for i, x in enumerate(v):
            out.update(hojas(x, "%s/%d" % (pref, i)))
        return out or {pref: []}
    return {pref: v}


def casa(patron: str, ptr: str) -> bool:
    a, b = patron.split("/"), ptr.split("/")
    return len(a) == len(b) and all(x == "*" or x == y for x, y in zip(a, b))


def diferencias(a, b) -> list:
    ha, hb = hojas(a), hojas(b)
    out = []
    for k in sorted(set(ha) | set(hb)):
        va, vb = ha.get(k, "<ausente>"), hb.get(k, "<ausente>")
        if type(va) is not type(vb) or va != vb:
            out.append({"puntero": k, "nueva": va, "referencia": vb})
    return out


def comparar_plan(plan: dict, ph: dict, fuentes: dict | None = None) -> dict:
    """Plan limpio frente al histórico: iguales salvo las diferencias DECLARADAS (contexto esperado de esta base, huella pública de
    R_A_dependencias.json con su huella de origen = la del plan histórico, y plan_sha256 que deriva de ellas)."""
    fu = fuentes or leer(BASE / "fuentes_fam03.json")
    dep = next(x for x in fu["archivos"] if x["archivo"] == "nucleo_s6/instalacion/ra/R_A_dependencias.json")
    dif = diferencias(plan, ph)
    declaradas = ("/plan_sha256", "/contexto_esperado/*", "/contexto_esperado/procedencia/*", "/evaluadores_ra/dependencias/sha256")
    otras = [d for d in dif if not any(casa(p, d["puntero"]) for p in declaradas)]
    dep_ok = (plan["evaluadores_ra"]["dependencias"]["sha256"] == dep["sha256"] and ph["evaluadores_ra"]["dependencias"]["sha256"] == dep["sha256_origen"])
    return {"igual_salvo_lo_declarado": not otras and dep_ok, "diferencias_declaradas": [d for d in dif if d not in otras],
            "diferencias_no_declaradas": otras[:20], "dependencias_ra_correspondencia": dep_ok,
            "tareas": len(plan["tareas"]), "tareas_iguales": plan["tareas"] == ph["tareas"], "decision_q": plan["decision_q"], "decisiones": plan["decisiones"],
            "resumen_q": plan["resumen_q"]}


# ================================================================================================ referencias y cobertura (sin cálculo)
def productos_catalogo() -> dict:
    c = leer(BASE / "catalogo.json")
    return {p["id"]: dict(p, clave=op["clave"]) for op in c["operaciones"] if op["clave"] in ("F03-QUIEBRES", "F03-Q") for p in op["productos"]}


def nombre_unidad(u: str) -> str:
    return u.replace(":", "_").replace("|", "_")


def arbol_referencia(tarea: str) -> tuple:
    """(manifiesto, {rel: bytes}) del árbol aceptado de la tarea, autenticado: manifiesto = el del catálogo (tree_sha256) y miembros por huella."""
    p = productos_catalogo().get(tarea)
    need(p is not None, "TAREA_SIN_ARBOL_EN_EL_CATALOGO: %s" % tarea)
    need((REF / "paquete" / p["objeto"]).is_file(), "ARBOL_DE_REFERENCIA_AUSENTE: %s" % tarea)
    man = leer(REF / "paquete" / p["objeto"])
    arbol = sha(canon({k: v["sha256"] for k, v in man["archivos"].items()}))
    need(man.get("tarea") == tarea and man.get("tree_sha256") == p["sha256_aceptado"] == arbol, "ARBOL_DE_REFERENCIA_ALTERADO: %s" % tarea)
    out = {}
    for r, x in man["archivos"].items():
        need((REF / "paquete" / x["objeto"]).is_file(), "MIEMBRO_DE_REFERENCIA_AUSENTE: %s %s" % (tarea, r))
        raw = (REF / "paquete" / x["objeto"]).read_bytes()
        if x["tipo"] == "copia_exacta":
            need(sha(raw) == x["sha256"], "MIEMBRO_DE_REFERENCIA_ALTERADO: %s %s" % (tarea, r))
        else:
            need(Path(x["objeto"]).parent.name == sha(raw), "PROYECCION_DE_REFERENCIA_ALTERADA: %s %s" % (tarea, r))
        out[r] = raw
    return man, out


def fuentes_alteradas() -> list:
    fu = leer(BASE / "fuentes_fam03.json")
    return [x["archivo"] for x in fu["archivos"] if not (BASE / x["archivo"]).is_file() or sha((BASE / x["archivo"]).read_bytes()) != x["sha256"]]


def cobertura(plan: dict) -> dict:
    """Unidades (lista), tareas (plan) y árboles (catálogo/referencias): no se confunden. 152 unidades = 120 quiebres + 32 Q; 136 tareas = 120 + 16;
    136 árboles, uno por tarea, con un documento y unas filas por unidad."""
    lst = json.loads(lista_bytes())
    por_id = {u["id"]: u for u in lst["unidades"]}
    tareas = {t["id"]: t for t in plan["tareas"]}
    asign = Counter(u for t in plan["tareas"] for u in t["unidades"])
    prods = productos_catalogo()
    mot = []
    if sorted(asign) != sorted(por_id) or any(n != 1 for n in asign.values()):
        mot.append("UNIDADES_DE_LA_LISTA_SIN_TAREA_UNICA")
    if sorted(prods) != sorted(tareas):
        mot.append("ARBOLES_DISTINTOS_DE_LAS_TAREAS")
    estados, d4, por_fam = Counter(), Counter(), Counter()
    for tid, t in sorted(tareas.items()):
        if any(por_id[u]["familia"] != t["familia"] or por_id[u]["fase"] != t["fase"] for u in t["unidades"]):
            mot.append("UNIDAD_DE_OTRA_FAMILIA: %s" % tid)
        if t["familia"] == "PROD3":
            if not (len(t["unidades"]) == 2 and len({por_id[u]["afirmacion"] for u in t["unidades"]}) == 1
                    and sorted(por_id[u]["ambito"][0] for u in t["unidades"]) == ["country", "global"]):
                mot.append("TAREA_Q_SIN_LOS_DOS_AMBITOS: %s" % tid)
        elif len(t["unidades"]) != 1:
            mot.append("TAREA_DE_QUIEBRES_CON_VARIAS_UNIDADES: %s" % tid)
        if tid not in prods:
            continue
        try:
            man, b = arbol_referencia(tid)
        except Fam03Error as ex:
            mot.append(str(ex))
            continue
        esperados = {DICTAMEN, REGISTRO} | {"unidades/%s%s.json" % (nombre_unidad(u), s) for u in t["unidades"] for s in ("", "_filas")}
        if set(b) != esperados:
            mot.append("ARBOL_CON_OTROS_MIEMBROS: %s" % tid)
            continue
        reg = json.loads(b[REGISTRO])
        for u in t["unidades"]:
            doc = json.loads(b["unidades/%s.json" % nombre_unidad(u)])
            if doc.get("especificacion") != por_id[u] or doc.get("vinculo", {}).get("tarea") != tid:
                mot.append("DOCUMENTO_DE_REFERENCIA_DE_OTRA_UNIDAD: %s" % u)
            e = reg["unidades"][u]
            estados[e["estado"]] += 1
            por_fam[(t["familia"], e["estado"], bool(e.get("declarada_D4")))] += 1
            d4[bool(e.get("declarada_D4"))] += 1
    return {"unidades_lista": len(por_id), "unidades_por_familia": dict(Counter(u["familia"] for u in lst["unidades"])),
            "tareas_plan": len(tareas), "tareas_por_familia": dict(Counter(t["familia"] for t in plan["tareas"])), "arboles_catalogo": len(prods),
            "estados_en_las_referencias": dict(estados), "declaradas_D4_en_las_referencias": d4.get(True, 0),
            "por_familia_estado_D4": {"%s|%s|D4=%s" % k: n for k, n in sorted(por_fam.items())}, "cumple": not mot, "motivos": mot[:20]}


def comprobar() -> dict:
    """fam03-comprobar: SIN CÁLCULO. Construye el contexto S6 (sin búsquedas) solo para comprobar su identidad frente al plan sellado con el
    criterio de fam03-unidad y fam03-validar (admision_contexto: F2 extendida a FAM03), antes de lanzar las tareas."""
    S = pila()
    r = {"comando": "fam03-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    r["fuentes"] = {"archivos": len(leer(BASE / "fuentes_fam03.json")["archivos"]), "ausentes_o_distintos": malos[:20]}
    plan, ph = plan_limpio(), plan_historico()
    try:
        verificar_plan(plan, S)
        r["plan"] = {"verificado": True, "plan_sha256": plan["plan_sha256"], **comparar_plan(plan, ph)}
    except Fam03Error as ex:
        r["plan"] = {"verificado": False, "motivo": str(ex)}
    ce = leer(DATOS / "contexto_esperado.json")
    r["contexto_esperado"] = {"igual_al_del_plan": plan.get("contexto_esperado") == ce,
                              "despliegue_igual": ce["despliegue_sha256"] == sha((DATOS / "despliegue.json").read_bytes())}
    r["cobertura"] = cobertura(plan)
    dep = S.PRA.DEP
    ra_mal = [x["archivo"] for x in dep["codigo"].values() if not (
        sha_archivo(INST / "ra/historico" / x["archivo"]) == x["sha256"] == sha_archivo(T / ENTREGA_RA / x["archivo"])
        and sha_archivo(INST / "ra/puerto" / x["archivo"]) == x["puerto"]["sha256"])]
    inv_ok = sha_archivo(T / ENTREGA_RA / "audit/entrega.json") == S.RR.ENTREGAS.get(ENTREGA_RA) == dep["inventario_sha256"]
    r["evaluadores_ra"] = {"modulos": len(dep["codigo"]), "distintos": ra_mal, "inventario_anclado": inv_ok, "area": rel(Path(dep["historico"])),
                           "adaptador_igual_al_plan": sha((INST / S.TP.ER_REL).read_bytes()) == plan["evaluadores_ra"]["adaptador"]["sha256"]}
    pil = leer(DATOS / "pilotos.json")
    r["pilotos"] = {"fijados": [p["tarea"] for p in pil["pilotos"]], "iguales_a_la_regla": pil == regla_pilotos(plan)}
    try:
        r["contexto"] = contexto_admitido(contexto(), plan)
    except Exception as ex:
        r["contexto"] = {"admitido": False, "motivos": ["CONTEXTO_NO_CONSTRUIBLE: %s" % str(ex)[:300]]}
    r["cumple"] = (not malos and r["plan"].get("verificado") and r["plan"].get("igual_salvo_lo_declarado") and all(r["contexto_esperado"].values())
                   and r["contexto"].get("admitido") is True
                   and r["cobertura"]["cumple"] and not ra_mal and inv_ok and r["evaluadores_ra"]["adaptador_igual_al_plan"] and r["pilotos"]["iguales_a_la_regla"])
    return r


def listar() -> dict:
    plan = plan_limpio()
    prods = productos_catalogo()
    return {"comando": "fam03-listar", "calculo": "ninguno", "plan_sha256": plan["plan_sha256"],
            "tareas": [{"tarea": t["id"], "familia": t["familia"], "fase": t["fase"], "unidades": t["unidades"], "tope_s": t["tope_s"],
                        "referencia": prods[t["id"]]["objeto"] if t["id"] in prods else None} for t in plan["tareas"]],
            "pilotos": leer(DATOS / "pilotos.json")}


# ================================================================================================ cálculo de UNA tarea
def identidades_admitidas() -> dict:
    """Lo que el coordinador transportaba en el comando (--despliegue-sha256, --fuentes-sha256): huellas de los bytes que usa esta base."""
    return {"--despliegue-sha256": sha((DATOS / "despliegue.json").read_bytes()), "--fuentes-sha256": sha(lista_bytes())}


def _entorno(ctx) -> dict:
    import platform
    f = F1()
    return {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"), "environment_sha256": ctx.technical["environment_sha256"],
            "f2": f.equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"]),
            "f2_alcance": "adoptada solo para FAM01; aquí se informa y no es requisito de FAM03", "python": platform.python_version(),
            "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in f.HILOS}, "TZ": os.environ.get("TZ")}


def declarados() -> set:
    out = set()
    for n in ("fuentes_fam01.json", "fuentes_fam02.json", "fuentes_fam03.json"):
        p = BASE / n
        if p.is_file():
            out |= {x["archivo"] for x in leer(p).get("archivos", [])}
    return out


def lecturas(informe: dict) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam03/", "fuentes_fam0")
    sin = [x for x in informe["en_el_paquete"] if x not in dec and not x.startswith(".venv-fam01/") and not x.startswith(propios)]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(informe["en_el_paquete"]),
            "del_entorno_venv": sum(1 for x in informe["en_el_paquete"] if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": sin, "referencias_leidas": [x for x in informe["en_el_paquete"] if x.startswith("referencias/")]}


def correr(tarea: str, salida: Path, tope_efectivo: float = 2400.0) -> dict:
    """fam03-unidad: los pasos de tarea_prod.main para UNA tarea del plan limpio, en la carpeta NUEVA `salida` (el árbol de la tarea:
    unidades/, registro_productivo.json, dictamen_validacion.json) más resultado.json (lo que tarea_prod escribe en --resultado),
    ejecucion.json y archivos_leidos.json. La comparación es otro paso."""
    f = F1()
    t0, c0 = time.time(), time.process_time()
    S = pila()
    TP, RP, VPm, ER, D4 = S.TP, S.RP, S.VPm, S.ER, S.D4
    plan = verificar_plan(plan_limpio(), S)
    t = {x["id"]: x for x in plan["tareas"]}.get(tarea)
    need(t is not None and t.get("fase") in ("quiebres", "Q"), "TAREA_FUERA_DEL_PLAN_DE_PRODUCCION")
    malos = fuentes_alteradas()
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam03.json; no se calcula): %s" % malos[:5])
    try:
        esp = TP.especificaciones(plan, t)
    except ValueError as ex:
        raise Fam03Error(str(ex))
    era = plan["evaluadores_ra"]
    need(sha((INST / TP.ER_REL).read_bytes()) == era["adaptador"]["sha256"], "ADAPTADOR_RA_DISTINTO_DEL_PLAN")
    tope_ef = float(tope_efectivo)
    need(float(era["parametros"]["margen_cierre_s"]) < tope_ef <= float(t["tope_s"]), "TOPE_EFECTIVO_INCOHERENTE_CON_EL_PLAN")
    need(not (t["fase"] == "Q" and plan.get("decision_q") is None), "DECISION_Q_PENDIENTE")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    rastro = f.Rastro()
    from paper2b import claims as CL
    from paper2b import keys as K
    a0 = time.time()
    ctx = contexto()
    ce = plan.get("contexto_esperado") or {}
    o = identidades_admitidas()
    need(ce.get("despliegue_sha256") == o["--despliegue-sha256"], "CONTEXTO_DISTINTO_DEL_ESPERADO_POR_EL_PLAN: DESPLIEGUE")
    adm = exigir_contexto(ctx, plan)                                    # antes de cualquier cálculo (F2 extendida a FAM03)
    afirm = sorted({v["afirmacion"] for v in esp.values()})
    base = {c: CL.Verdict("verified", "robust_infeasible", None, None, 0, None) for c in afirm}
    runs, cls = {}, {}
    derivadas = CL.derive(ctx.inp.registry, ctx.inp.model_case_map, dict(ctx.inp.set_index.items()))
    for c in afirm:
        cl = next((x for x in derivadas if x.claim_id == c), None)
        need(cl is not None, "AFIRMACION_NO_DERIVABLE_BAJO_S6: %s" % c)
        cls[c] = cl
        runs[c] = ctx.run(cl.support_sets[0], "PROD:" + c)
        runs[c].verdicts = {c: base[c]}
    t_ctx = round(time.time() - a0, 1)
    need(sha(canon(list(t["unidades"]))) == t.get("asignacion_sha256"), "ASIGNACION_DISTINTA_DEL_PLAN")
    a1 = time.time()
    M, imp = ER.cargar(ctx, sal / "ra_importaciones", era)
    vinc = TP.vinculo(ctx, o, plan, t, era, imp)
    t_ra = round(time.time() - a1, 2)
    (sal / "unidades").mkdir(parents=True, exist_ok=True)
    productos, prep, memo, phi_cache, t_u = {}, {}, None, {}, {}
    par = era["parametros"]
    limite_global = ER.limite_global_tarea(t0, tope_ef, float(par["margen_cierre_s"]))
    for u, e in esp.items():                                              # CÁLCULO CIENTÍFICO
        tu = time.time()
        r, cl, vd = runs[e["afirmacion"]], cls[e["afirmacion"]], base[e["afirmacion"]]
        if e["familia"] == "PROD3":
            reg_q = M["QSEN2"].autenticado("demo/registro/registro_candidato_v4.json")["afirmaciones"]
            ev = ER.q_afirmacion(M["QSEN2"], ctx, e["afirmacion"], par["QSEN2"]["tope_s"], phi_cache, reg_q, limite_global)
            imp.guarda()
            productos[u] = TP.ensamblar_q(sal, u, e, r, cl, vd, ev, ctx, vinc, K, ER, plan.get("decision_q"))
        else:
            caso = "EQ" if e["familia"] == "PROD1" else "EQM"
            if memo is None:
                memo = M["EQ"].MEMO.Memo(True)
            fn = ER.estructural if caso == "EQ" else ER.macro
            bk, ev = fn(M[caso], ctx, prep, e["afirmacion"], e["parametro"], e["direccion"], par[caso]["seg_por_evaluacion"], par[caso]["tope_por_busqueda_s"],
                        memo, limite_global)
            imp.guarda()
            productos[u] = TP.ensamblar_quiebre(sal, u, e, r, cl, vd, bk, ev, ctx, vinc, K, ER, o)
        t_u[u] = round(time.time() - tu, 2)
    a2 = time.time()
    VR = VPm.ValidadorProdS6(ctx, esperado=TP.vinculo_esperado(vinc), modo_arnes=False)
    d4 = t["fase"] == "quiebres" and D4.activa(plan)
    reg = RP.generar_prod(VR, sal, productos, esp, salida=sal / REGISTRO, dictamen=sal / DICTAMEN, d4=d4)
    t_val = round(time.time() - a2, 2)
    ok = reg["verificacion"].get("cumple") is True and all(x["estado"] in ESTADOS_ADMISIBLES or x.get("declarada_D4") for x in reg["unidades"].values())
    res = {"estado": "completa" if ok else "rechazada", "productos": productos, "motivo": None if ok else reg["verificacion"].get("codigos"), "contexto_s": t_ctx,
           "unidades": {x: v["estado"] for x, v in reg["unidades"].items()}, "replica_arnes": False, "tope_efectivo_s": tope_ef,
           "segundos": round(time.time() - t0, 1)}
    (sal / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej = {"tarea": tarea, "familia": t["familia"], "fase": t["fase"], "unidades": list(t["unidades"]), "plan_sha256": plan["plan_sha256"],
          "naturaleza": "cálculo: pasos de tarea_prod.main con evaluadores_ra en la base limpia (etiqueta NO OFICIAL)", "adaptaciones": list(ADAPTACIONES),
          "tope_efectivo_s": tope_ef, "reloj": "RELOJ-PILOTO-v1: tope interno = tope de la tarea en el plan; el límite externo lo pone el supervisor",
          "vinculo": vinc, "contexto": {"identity_sha256": ctx.identity_sha256, "run_class": ctx.identity["run_class"]}, "entorno_f2": adm,
          "run_id": {r.run_id for r in runs.values()}, "run_id_entradas": {"d7": ctx.inp.d7.manifest["tree_sha256"], "config": ctx.inp.algorithm_config_sha256,
                                                                          "producer": ctx.inp.producer_sha256, "contract": ctx.inp.contract_sha256},
          "calculo": {"estado": "terminado", "por_unidad_s": t_u}, "validacion": {"cumple": reg["verificacion"].get("cumple"), "codigos": reg["verificacion"].get("codigos"),
                                                                                  "estados": res["unidades"], "declaradas_D4": sorted(x for x, v in reg["unidades"].items() if v.get("declarada_D4"))},
          "resultado": res["estado"], "tiempos_s": {"contexto": t_ctx, "carga_ra": t_ra, "calculo": round(sum(t_u.values()), 2), "validacion": t_val,
                                                   "total": round(time.time() - t0, 2), "cpu": round(time.process_time() - c0, 2)},
          "entorno": _entorno(ctx), "lecturas": lecturas(informe), "dependencias_fuera_de_la_biblioteca_estandar": f.dependencias_cargadas()}
    ej["run_id"] = sorted(ej["run_id"])
    ej["exito"] = ok
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=list).encode("utf-8") + b"\n")
    return ej


def validar(origen: Path, salida: Path) -> dict:
    """fam03-validar: SIN CÁLCULO. Copia los documentos y filas de `origen` (bytes exactos) a la carpeta NUEVA `salida` y repite la validación
    productiva (ValidadorProdS6 + generar_prod) con el contexto y el vínculo de quien valida."""
    t0 = time.time()
    origen = Path(origen).resolve()
    ej0 = leer(origen / "ejecucion.json")
    S = pila()
    plan = verificar_plan(plan_limpio(), S)
    t = {x["id"]: x for x in plan["tareas"]}[ej0["tarea"]]
    esp = S.TP.especificaciones(plan, t)
    ctx = contexto()
    adm = exigir_contexto(ctx, plan)                                    # mismo criterio que fam03-unidad (F2 extendida a FAM03)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    (sal / "unidades").mkdir()
    productos = {}
    for u in t["unidades"]:
        n = nombre_unidad(u)
        for s in ("", "_filas"):
            src = origen / "unidades" / (n + s + ".json")
            need(src.is_file(), "PRODUCTO_AUSENTE: %s" % src.name)
            shutil.copyfile(src, sal / "unidades" / (n + s + ".json"))
        productos[u] = {"documento": "unidades/%s.json" % n, "filas": "unidades/%s_filas.json" % n}
    VR = S.VPm.ValidadorProdS6(ctx, esperado=S.TP.vinculo_esperado(S.TP.vinculo(ctx, identidades_admitidas(), plan, t, plan["evaluadores_ra"], None)),
                               modo_arnes=False)
    d4 = t["fase"] == "quiebres" and S.D4.activa(plan)
    reg = S.RP.generar_prod(VR, sal, productos, esp, salida=sal / REGISTRO, dictamen=sal / DICTAMEN, d4=d4)
    ok = reg["verificacion"].get("cumple") is True and all(x["estado"] in ESTADOS_ADMISIBLES or x.get("declarada_D4") for x in reg["unidades"].values())
    rv = {"naturaleza": "REVALIDACIÓN SIN CÁLCULO de bytes guardados", "origen": rel(origen), "tarea": t["id"],
          "origen_ejecucion_sha256": sha((origen / "ejecucion.json").read_bytes()),
          "productos_sha256": {r: sha((sal / r).read_bytes()) for p in productos.values() for r in p.values()},
          "validacion": {"cumple": reg["verificacion"].get("cumple"), "codigos": reg["verificacion"].get("codigos"),
                         "estados": {x: v["estado"] for x, v in reg["unidades"].items()}, "motivos": {x: v["motivos"] for x, v in reg["unidades"].items() if v["motivos"]}},
          "exito": ok, "entorno_f2": adm, "segundos": round(time.time() - t0, 2)}
    (sal / "revalidacion.json").write_bytes(json.dumps(rv, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8") + b"\n")
    return rv


# ================================================================================================ comparación con el árbol aceptado
# COMPARACION-FAM03-v1. Criterios del contrato de comparadores (F03-QUIEBRES / F03-Q): CR-HASH-CANONICO (igualdad exacta del contenido
# científico canónico) y CR-DISCRETOS (clasificaciones, estados y conteos exactos; un cambio de clasificación no se compensa). Por OBJETO y por
# PUNTERO exacto (nunca por nombre de clave a cualquier profundidad) se separan:
#   operativos  duraciones y marcas de reloj que escribe evaluadores_ra (se muestran, no se comparan);
#   identidad   identidades de la base limpia (contexto, despliegue, plan, dependencias R-A, autoridad) y rutas: se comprueban contra las
#               propias de cada lado, no entre lados;
#   derivados   huellas de otros miembros (iguales si y solo si lo son esos miembros) y run_id (fórmula de paper2b.run con las entradas de
#               cada lado: solo cambia la huella del contrato público, FAM01).
# Todo lo demás (filas, evidencia, testigos, soporte, estados, clasificación, D4) se compara con igualdad exacta.
OPERATIVOS = {"documento_quiebre": ("/evidencia_ra/reloj/inicio_busqueda_t", "/evidencia_ra/reloj/limite_efectivo_t", "/evidencia_ra/reloj/limite_global_t",
                                    "/evidencia_ra/preparacion_s", "/evidencia_ra/busqueda_s", "/evidencia_ra/evaluaciones/*/segundos",
                                    "/evidencia_ra/evaluaciones/*/acumulado_s"),
              "documento_q": ("/evidencia_ra/preparacion_s", "/evidencia_ra/rama_y_cota_s", "/evidencia_ra/por_contexto_s", "/evidencia_ra/Phi_estrella/segundos",
                              "/evidencia_ra/codigo_universo_nudos/segundos"),
              "filas": (), "dictamen": (), "registro": ()}
IDENTIDAD = {"documento_quiebre": ("/identidad_productor_sha256", "/vinculo/contexto_identidad_sha256", "/vinculo/encargo_procedencia_sha256",
                                   "/vinculo/despliegue_sha256", "/vinculo/plan_sha256", "/vinculo/dependencias_ra_sha256"),
             "filas": (), "dictamen": ("/productor",),
             "registro": ("/generado_por/paquete", "/generado_por/contexto_identidad_sha256", "/generado_por/autoridad", "/verificacion/productor")}
IDENTIDAD["documento_q"] = IDENTIDAD["documento_quiebre"]
DERIVADOS = {"documento_quiebre": ("/filas/sha256",), "documento_q": ("/filas/sha256",),
             "filas": ("/support_breakdown_result/*/run_id", "/external_requirement_sensitivity_result/*/run_id"), "dictamen": (),
             "registro": ("/generado_por/dictamen_sha256", "/unidades/*/documento_sha256", "/unidades/*/filas_sha256")}


def _clase(ptr: str, tipo: str) -> str:
    for nombre, tabla in (("operativo", OPERATIVOS), ("identidad", IDENTIDAD), ("derivado", DERIVADOS)):
        if any(casa(p, ptr) for p in tabla[tipo]):
            return nombre
    return "cientifico"


def _tipo(r: str, doc) -> str:
    if r == DICTAMEN:
        return "dictamen"
    if r == REGISTRO:
        return "registro"
    if r.endswith("_filas.json"):
        return "filas"
    return "documento_q" if doc.get("familia") == "PROD3" else "documento_quiebre"


def _run_id(K, e: dict, contrato: str) -> str:
    return "BRUN-" + K.H({"d7": e["d7"], "config": e["config"], "producer": e["producer"], "contract": contrato})[:24]


def comparar(tarea: str, nueva: Path) -> dict:
    """fam03-comparar: árbol de `nueva` (carpeta de fam03-unidad o de fam03-validar) frente al árbol aceptado de `tarea`."""
    preparar()
    from paper2b import keys as K
    nueva = Path(nueva).resolve()
    rv = leer(nueva / "revalidacion.json") if (nueva / "revalidacion.json").is_file() else None
    ej_dir = (BASE / rv["origen"]) if rv else nueva
    ej = leer(ej_dir / "ejecucion.json")
    man, ref = arbol_referencia(tarea)
    plan = plan_limpio()
    t = {x["id"]: x for x in plan["tareas"]}.get(tarea)
    need(t is not None, "TAREA_FUERA_DEL_PLAN")
    mot = []
    if ej.get("tarea") != tarea:
        mot.append("SALIDA_DE_OTRA_TAREA: %s" % ej.get("tarea"))
    if not ej.get("exito") or (rv is not None and not rv.get("exito")):
        mot.append("CALCULO_O_VALIDACION_NO_CUMPLE")
    miembros = sorted(ref)
    presentes = sorted(p.relative_to(nueva).as_posix() for p in nueva.rglob("*") if p.is_file())
    faltan = [m for m in miembros if m not in presentes]
    fuera_del_arbol = [p for p in presentes if p not in miembros]
    if faltan:
        mot.append("MIEMBROS_DEL_ARBOL_AUSENTES: %s" % faltan[:4])
    fu = leer(BASE / "fuentes_fam03.json")
    dep = next(x for x in fu["archivos"] if x["archivo"] == "nucleo_s6/instalacion/ra/R_A_dependencias.json")
    ph = plan_historico()
    e_n = ej["run_id_entradas"]
    hist_contrato = F1().parametros()["contract_sha256_historico"]
    objetos, cuentas = {}, Counter()
    for m in miembros:
        if m in faltan:
            continue
        bn, br = (nueva / m).read_bytes(), ref[m]
        dn, dr = json.loads(bn), json.loads(br)
        tipo = _tipo(m, dn)
        o = {"tipo": tipo, "bytes_iguales": bn == br, "cientifico": [], "operativo": [], "identidad": [], "derivado": []}
        for d in diferencias(dn, dr):
            c = _clase(d["puntero"], tipo)
            o[c].append(d)
        chk = []
        if tipo.startswith("documento"):
            fm = "unidades/" + dn.get("filas", {}).get("archivo", "?")
            chk.append(("filas_sha256_nueva", dn["filas"]["sha256"] == sha((nueva / fm).read_bytes()) if (nueva / fm).is_file() else False))
            chk.append(("filas_sha256_referencia", dr["filas"]["sha256"] == sha(ref.get(fm, b""))))
            v_n, v_r = dn.get("vinculo", {}), dr.get("vinculo", {})
            chk += [("vinculo_nueva_es_el_de_esta_ejecucion", {k: v_n.get(k) for k in ej["vinculo"]} == ej["vinculo"]),
                    ("vinculo_referencia_plan_historico", v_r.get("plan_sha256") == ph["plan_sha256"]),
                    ("dependencias_ra_correspondencia", v_n.get("dependencias_ra_sha256") == dep["sha256"] and v_r.get("dependencias_ra_sha256") == dep["sha256_origen"]),
                    ("identidad_productor_nueva", dn.get("identidad_productor_sha256") == ej["contexto"]["identity_sha256"] == v_n.get("contexto_identidad_sha256"))]
        elif tipo == "filas":
            for tb in ("support_breakdown_result", "external_requirement_sensitivity_result"):
                for x, y in zip(dn.get(tb, []), dr.get(tb, [])):
                    chk += [("run_id_nueva_formula", x["run_id"] == _run_id(K, e_n, e_n["contract"])),
                            ("run_id_referencia_formula_con_contrato_historico", y["run_id"] == _run_id(K, e_n, hist_contrato))]
        elif tipo == "registro":
            for u, x in dn.get("unidades", {}).items():
                chk += [("registro_documento_sha256_nueva", x["documento_sha256"] == sha((nueva / x["documento"]).read_bytes())),
                        ("registro_filas_sha256_nueva", x["filas_sha256"] == sha((nueva / x["filas"]).read_bytes()))]
            for u, x in dr.get("unidades", {}).items():
                chk += [("registro_documento_sha256_referencia", x["documento_sha256"] == sha(ref.get(x["documento"], b""))),
                        ("registro_filas_sha256_referencia", x["filas_sha256"] == sha(ref.get(x["filas"], b"")))]
            chk += [("dictamen_sha256_nueva", dn["generado_por"]["dictamen_sha256"] == sha((nueva / DICTAMEN).read_bytes())),
                    ("dictamen_sha256_referencia", dr["generado_por"]["dictamen_sha256"] == sha(ref[DICTAMEN]))]
        o["comprobaciones"] = {k: all(v for kk, v in chk if kk == k) for k in dict(chk)}
        if o["cientifico"]:
            mot.append("DIFERENCIA_CIENTIFICA: %s %s" % (m, [d["puntero"] for d in o["cientifico"][:4]]))
        if not all(o["comprobaciones"].values()):
            mot.append("COMPROBACION_DE_IDENTIDAD_O_DERIVACION: %s %s" % (m, [k for k, v in o["comprobaciones"].items() if not v]))
        for c in ("cientifico", "operativo", "identidad", "derivado"):
            cuentas[c] += len(o[c])
            o["n_" + c] = len(o[c])
            o[c] = o[c][:40]
        objetos[m] = o
    reg_n = leer(nueva / REGISTRO) if (nueva / REGISTRO).is_file() else {}
    reg_r = json.loads(ref[REGISTRO])
    clas = {"nueva": {u: (x["estado"], bool(x.get("declarada_D4"))) for u, x in reg_n.get("unidades", {}).items()},
            "referencia": {u: (x["estado"], bool(x.get("declarada_D4"))) for u, x in reg_r["unidades"].items()}}
    clas["igual"] = clas["nueva"] == clas["referencia"]
    if not clas["igual"]:
        mot.append("CLASIFICACION_DISTINTA (CR-DISCRETOS, precedencia: no se compensa)")
    if (reg_n.get("verificacion") or {}).get("cumple") is not True:
        mot.append("VALIDACION_NUEVA_AUSENTE_O_NO_CUMPLE")
    tiempos = {}
    for m, o in objetos.items():
        for d in o["operativo"]:
            tiempos[m.split("/")[-1][:60] + d["puntero"]] = [d["nueva"], d["referencia"]]
    return {"comando": "fam03-comparar", "tarea": tarea, "familia": t["familia"], "regla": "COMPARACION-FAM03-v1 (src/fam03.py)",
            "criterios": ["CR-HASH-CANONICO (contexto canónico: mismo entorno .venv-fam01; el comparador compara documentos, no certifica el entorno)",
                          "CR-DISCRETOS"],
            "referencia": {"arbol": man["tree_sha256"], "manifiesto": productos_catalogo()[tarea]["objeto"]}, "nueva": rel(nueva),
            "naturaleza_nueva": "revalidación sin cálculo de " + rv["origen"] if rv else "cálculo",
            "cobertura": {"miembros": len(miembros), "faltan": faltan, "fuera_del_arbol": fuera_del_arbol},
            "objetos": objetos, "cuentas": dict(cuentas), "clasificacion": clas, "tiempos_nueva_frente_a_referencia": tiempos,
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    plan = plan_limpio()
    prods = productos_catalogo()
    ordenes = [{"tarea": t["id"], "familia": t["familia"], "fase": t["fase"], "unidades": len(t["unidades"]), "tope_s": t["tope_s"],
                "referencia": prods[t["id"]]["objeto"],
                "ordenes": ["reproducir.py fam03-unidad --tarea %s --salida salidas/fam03/<ejecucion>/%s" % (t["id"], t["id"]),
                            "reproducir.py fam03-comparar --tarea %s --nueva salidas/fam03/<ejecucion>/%s --salida salidas/fam03/<ejecucion>/%s.comparacion.json"
                            % (t["id"], t["id"], t["id"])]} for t in plan["tareas"]]
    return {"comando": "fam03-receta", "estado": "receta completa preparada; NO ejecutada (los lotes pertenecen al Paso 3)", "plan_sha256": plan["plan_sha256"],
            "orden": [t["id"] for t in plan["tareas"]], "tareas": ordenes,
            "cobertura": {"tareas": len(ordenes), "por_familia": dict(Counter(t["familia"] for t in plan["tareas"])),
                          "unidades": sum(len(t["unidades"]) for t in plan["tareas"]), "arboles_de_referencia": len(prods)},
            "previo": ["reproducir.py fam03-comprobar --salida salidas/fam03/<nuevo>.json (sin cálculo)",
                       "datos/fam03 fijado por fam03-preparar (contexto esperado, plan limpio, pilotos); no se regenera en cada ejecución"],
            "ejecucion": {"procesos": "una tarea a la vez (plan: tareas_activas 1)", "limite_externo_por_tarea_s": 2400.0,
                          "reloj_interno": "tope de la tarea en el plan (2400 s); margen de cierre 180 s; presupuestos EQ/EQM 120 s por evaluación y 420 s por "
                                           "búsqueda; QSEN2 300 s por rama y cota (sin cambios)",
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos)",
                          "dependencias_entre_tareas": "ninguna dentro de FAM03 (cada tarea solo lee las entradas instaladas); la conciliación PROD4 es otra familia"},
            "F1": {"reutilizable": ["lista de producción instalada (152 unidades) y plan derivado con las decisiones selladas del plan histórico "
                                    "(Q-CONTINUO-COTA-SUPERIOR-v2, QUIEBRES-D4)", "línea base certificada del registro candidato v4 (lima1941)",
                                    "módulos R-A ensayados (lima1958, puerto y cierre de dependencias)", "núcleo S6, D7 y contratos de FAM01"],
                   "solo_para_comparar": ["los 136 árboles aceptados (referencias/fam03/paquete) y el plan histórico (copia pública)"],
                   "se_genera_en_la_nueva_ejecucion": ["los 136 árboles: documentos y filas de las 152 unidades, registro productivo y dictamen por tarea"],
                   "no_consumido": ["resumen_q (null en el plan efectivo: la ruta q_ambito que lo usaba no se ejecuta)",
                                    "resultados históricos de búsqueda (la réplica de arnés --replica-arnes no forma parte de la receta)"]},
            "pilotos": leer(DATOS / "pilotos.json")}
