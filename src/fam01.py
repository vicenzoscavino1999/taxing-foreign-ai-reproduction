"""FAM01 (base detallada S1/S2/S3/C2; selecciones R2 y R3): contexto S6, recorrido de una tarea (cálculo -> validación productiva ->
productos), comprobación documental de las listas, del marco R3 y de las NA, y comparación con el original.

El cálculo científico es el del núcleo S6 copiado sin cambios en nucleo_s6/ (raiz = árbol del proyecto con sus rutas relativas;
instalacion = paso4/instalacion). Este módulo solo conecta piezas. Adaptaciones de interfaz (sin cambiar el algoritmo ni las tolerancias):

- Contexto: la misma construcción de RunInputs que herramientas/b/contexto_s6.ContextoS6 (fb4a4b1e…), sin la capa administrativa
  (autoridad viva con ancla, encargo y procedencia). Los valores que aportaba la autoridad (paquete S6, raíz y hash del contrato,
  D7) están fijados en datos/fam01/contexto_s6.json y se comprueban por hash al cargar. La conformidad del entorno se REGISTRA en
  vez de exigirse; su huella entra igual en las claves técnicas. El contrato G-NA-1 es su copia pública (SAN-RUTAS-v1, huella
  real f3dd49eb…); la histórica (7bde9f15…) queda como referencia y solo correspondencia_saneamiento la relaciona con la pública.
- R2: como tarea_paso4 (rama R2): selección SEL-PASO4-REPRO-v1 con el Verificador S6 instalado (paquete_seleccion.py, a70cf904…,
  con las adaptaciones de ADAPTACIONES_VERIFICADOR), plan por grupos CA2 y unidades.EjecutorSeleccion; validación productiva por
  registro_productivo.generar (verificar_paquete del mismo Verificador). Documento NATIVO (registro_productivo.ensamblar) y
  documento COMPARABLE (FMT_R2), con su relación en comparables/relacion.json.
- R3: productor_r3.ProductorR3 (previas y celda) y documento como tarea_paso4 (R3); validación productiva por validador_r3
  (ValidadorR3S6, d2a5cbb6…) y registro_productivo.generar_r3.
- Comparación: comparar_reproduccion v3-S6 (c90fd220…) con su caché nucleo() rellenada desde la copia; el original se lee de
  referencias/fam01 (copias exactas comprobadas contra el índice de paquetes de autoridad) en vez del árbol histórico; los
  originales se validan con la copia pública del contrato CA2-4 solo si su correspondencia con el histórico se comprueba.
  Pasadas separadas:
  - HISTÓRICA: reglas vigentes y selladas, DR-1 tal cual (comparacion_historica);
  - LIMPIA: además E2E3-NIVEL-R1-v1 (k = r1_level de la unidad), HIST-OPERATIVO-v1 (solo las rutas de primer nivel
    tramo_anterior y recuperacion_de, como procedencia) y SAN-RUTAS-v1 (contrato público = histórico si la correspondencia se
    comprueba); entorno estricto (comparacion_limpia);
  - LIMPIA + F2 (REGLA_F2; adoptada por el autor para FAM01 el 2026-11-16, ADOPCION_F2) (comparacion_limpia_f2).
  Las reglas históricas no se editan; la reproducción dice con qué criterio se acepta.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAIZ = BASE / "nucleo_s6" / "raiz"
INST = BASE / "nucleo_s6" / "instalacion"
DATOS = BASE / "datos" / "fam01"
REFS = BASE / "referencias" / "fam01"
LISTAS = {"R2": ("datos/paso4/lista_R2_testigos.json", "519ec91924cad7ce8b8cf29c407894926c912c9cb9196de3c626514303ae066f"),
          "R3": ("datos/paso4/lista_R3_candidata_B_NA.json", "7f8fed89a8d678fc18ec629b1e9326c8c776d03c566533f7b4a2a2c2a94853b2")}
MARCO = ("marco_R3_identidad_r3.json", "9d8f02c7c6b69b012b17c80b420744f2794acb379218fc43c8b1dc9ab53a3801")
PROPUESTA_B = ("propuesta_r3_b.json", "00c3f3684777d3b99c9b280d4b7224c0c1cb6961574accee084229be27edee73")
REGLA_B = ("herramientas/b/regla_b_v2.py", "b138dec4e9daaff5b226f4fca87dd3ff3d51ab9586b401a00074aed9e00a4790")   # = productor_r3.FIJADOS
REGLAS_SELLADAS = {"R2": "datos/paso4/reglas_selladas_lote1_R2.json", "R3": "datos/paso4/reglas_selladas_R3.json"}


class Fam01Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam01Error(codigo)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> bytes:
    """Serialización de corrida_paso4.canon / registro_productivo.canon (la de los documentos y filas de la ruta S6)."""
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def leer_json(p: Path, h: str | None = None):
    raw = Path(p).read_bytes()
    if h is not None:
        need(sha(raw) == h, "SHA256_DISTINTO:%s" % Path(p).name)
    return json.loads(raw)


def parametros():
    return leer_json(DATOS / "contexto_s6.json")


# ================================================================================================ entorno: F2 (adoptada para FAM01)
HILOS = ("BLIS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
LANZADOR = re.compile(r"^\.\./\.\./Scripts/[^,/\\]+\.exe,")
CAMPOS_UBICACION_F2 = ("fingerprint.executable.path", "fingerprint.executable.base_path",
                       "fingerprint.packages.*.record_sha256 -> record_sin_lanzadores_sha256 (RECORD sin las líneas ../../Scripts/*.exe)",
                       "fingerprint_sha256 (derivado del fingerprint completo)")
REGLA_F2 = ("F2-ENTORNO-PORTABLE-v1 (adoptada por el autor para FAM01 el 2026-11-16: es F2-CANDIDATA-ENTORNO-PORTABLE-v1 sin cambios de "
            "contenido; no sustituye DR-1). Un entorno nuevo E' es equivalente al entorno E "
            "de la tupla S6 admitida si: (1) entorno.assessment de E' con el perfil aprobado da conforms = true y mismatches = [] (Python, "
            "plataforma validada, arquitectura, pip, BLAS/LAPACK, hilos, locale, zona horaria, semilla, versión y sha256 de archivo de cada "
            "paquete del lock y ningún paquete fuera de él); y (2) su documento de entorno es IDÉNTICO al de E salvo los campos de ubicación: "
            "rutas del intérprete del venv y del intérprete base (sus sha256 se conservan) y, en el RECORD de cada paquete, las líneas de los "
            "lanzadores Scripts/*.exe, que contienen la ruta absoluta del intérprete. Se exige la huella real de E' (environment_sha256 de su "
            "ejecución, sin copiar la de E) y no cambia ninguna tolerancia ni otro requisito de DR-1.")
ADOPCION_F2 = {
    "regla": "F2-ENTORNO-PORTABLE-v1",
    "contenido": "el de F2-CANDIDATA-ENTORNO-PORTABLE-v1 revisada en RESULTADO_FAM01.md, sin cambios: mismos campos de ubicación "
                 "(CAMPOS_UBICACION_F2) y misma proyección de referencia (datos/fam01/entorno_f2_referencia.json, b6db2964…)",
    "estado": "adoptada por el autor para FAM01",
    "fecha": "2026-11-16",
    "decision": "Adopto F2 para FAM01 conforme a la propuesta revisada en RESULTADO_FAM01.md, sin modificar criterios científicos ni "
                "autorizar todavía el lote completo.",
    "alcance": "FAM01. Probada en Windows con CPython 3.12.4 oficial, dos ubicaciones de venv y una máquina; no acredita otra plataforma "
               "ni una instalación aislada. Cualquier diferencia en las propiedades conservadas rechaza la equivalencia.",
    "no_cubre": "cambios de código, contrato, configuración, tolerancias o criterios científicos (el saneamiento tiene su propia "
                "correspondencia, SAN-RUTAS-v1)",
    "no_autoriza": "el lote completo de FAM01 ni su tiempo de máquina (Paso 3)"}


def records_sin_lanzadores() -> dict:
    """sha256 del RECORD de cada distribución instalada sin las líneas de los lanzadores Scripts/*.exe (mismo recorrido y lectura que
    entorno.observe; el RECORD completo sigue en el documento de entorno)."""
    import importlib.metadata as md
    out = {}
    for d in md.distributions():
        rec = d.read_text("RECORD")
        out[d.metadata["Name"].lower()] = (sha("".join(x for x in rec.splitlines(keepends=True) if not LANZADOR.match(x)).encode("utf-8"))
                                          if rec else None)
    return dict(sorted(out.items()))


def proyeccion_f2(doc: dict, rec: dict) -> dict:
    """Documento de entorno sin los campos de ubicación (CAMPOS_UBICACION_F2); todo lo demás, incluidos conforms y mismatches, se conserva."""
    d = json.loads(json.dumps(doc))
    fp = d["fingerprint"]
    fp["executable"] = {k: v for k, v in fp["executable"].items() if k not in ("path", "base_path")}
    for n, p in fp["packages"].items():
        p.pop("record_sha256", None)
        p["record_sin_lanzadores_sha256"] = rec.get(n)
    d.pop("fingerprint_sha256", None)
    return d


def equivalencia_f2(doc: dict, rec: dict, environment_sha256: str) -> dict:
    """Comprobación F2 (ADOPCION_F2) de un entorno ya registrado: su documento es el de la huella declarada, cumple el perfil y su proyección
    es la de la tupla S6 admitida (datos/fam01/entorno_f2_referencia.json)."""
    ref = leer_json(DATOS / "entorno_f2_referencia.json")
    mot = []
    if sha(canon(doc) + b"\n") != environment_sha256:
        mot.append("documento de entorno distinto del de la huella declarada")
    if doc.get("conforms") is not True or doc.get("mismatches"):
        mot.append("no cumple el perfil aprobado: %s" % (doc.get("mismatches") or ["conforms != true"])[:6])
    pr = proyeccion_f2(doc, rec)
    if sha(canon(pr)) != ref["proyeccion_sha256"] or sha(canon(ref["proyeccion"])) != ref["proyeccion_sha256"]:
        a, b = ref["proyeccion"], pr
        dif = sorted({"%s.%s" % (s, k) for s in ("fingerprint",) for k in set(a[s]) | set(b[s]) if a[s].get(k) != b[s].get(k)}
                     | {k for k in set(a) | set(b) if k != "fingerprint" and a.get(k) != b.get(k)})
        mot.append("proyección distinta de la de la tupla admitida en: %s" % dif[:8])
    return {"regla": REGLA_F2.split(" ")[0], "adopcion": "%s el %s" % (ADOPCION_F2["estado"], ADOPCION_F2["fecha"]),
            "equivalente": not mot, "motivos": mot, "environment_sha256": environment_sha256,
            "referencia_environment_sha256": ref["environment_sha256_admitido"]}


# ================================================================================================ paquete público: SAN-RUTAS-v1
REGLA_SAN = ("SAN-RUTAS-v1 (saneamiento del paquete público; no es una regla científica). Una copia pública es su original con el prefijo "
             "absoluto de la raíz del proyecto sustituido por nada (ruta relativa) y el de la carpeta de descargas del usuario por "
             "«<descargas>»; nada más cambia (extraccion/extraer_fam01.sanear lo comprueba contra el original, que no se distribuye). Un "
             "manifiesto que lista copias saneadas se publica DERIVADO: el histórico (intacto en referencias/fam01/manifiestos_historicos/) "
             "con solo «bytes» y «sha256» de esas entradas cambiados a los de la copia pública y, si lo tiene, su árbol derivado recalculado. "
             "La huella pública de un manifiesto corresponde a la histórica solo si esta comprobación pasa; nunca se le asigna la histórica.")
SANEAMIENTO = {"G-NA-1": ("herramientas/bloque2/contratos_g_na_1/", "contratos/contract_manifest.json", "contrato_G-NA-1.json"),
               "CA2-4": ("fase6_planes/integracion_s4/versions/560026466c07259d759cdd435a80e37561b0226228383a5a2c1fef5d501fa4d2/contratos_enmienda/",
                         "contratos/contract_manifest.json", "contrato_CA2-4.json"),
               "recepcion": ("fase2_datos/recepcion_nacional/versions/866aa139fb50578cae1ec5d77e1f98e6a5b87b56780aa1d95a118dffc5644984/",
                             "recepcion_manifest.json", "recepcion_866aa139.json")}


def correspondencia_saneamiento() -> dict:
    """Por manifiesto (contratos G-NA-1 y CA2-4, recepción nacional): identidad HISTÓRICA (sha256 del manifiesto de referencia y, en la
    recepción, su árbol) e identidad REAL del paquete público, y si el público es el histórico con SOLO los cambios de SAN-RUTAS-v1: cada
    entrada distinta es una copia declarada en fuentes_fam01.json como saneada, con sha256_origen = la huella histórica de la entrada y
    bytes/sha256 = los del archivo presente; nada más del manifiesto cambia (salvo el árbol, que debe derivar de sus archivos)."""
    rel = {r["archivo"]: r for r in leer_json(BASE / "fuentes_fam01.json")["archivos"]}
    out = {}
    for clave, (raiz, nombre, ref) in SANEAMIENTO.items():
        pb, hb = (RAIZ / raiz / nombre).read_bytes(), (REFS / "manifiestos_historicos" / ref).read_bytes()
        p, h = json.loads(pb), json.loads(hb)
        lista = isinstance(h.get("files"), list)
        eh = {x["path"]: x for x in h["files"]} if lista else dict(h["files"])
        ep = {x["path"]: x for x in p.get("files") or []} if lista else dict(p.get("files") or {})
        mot, saneadas = [], []
        if list(eh) != list(ep):
            mot.append("entradas distintas o en otro orden")
        for k in eh:
            if eh[k] == ep.get(k):
                continue
            saneadas.append(k)
            f, q = rel.get("nucleo_s6/raiz/" + raiz + k), RAIZ / raiz / k
            data = q.read_bytes() if q.is_file() else b""
            if not (f is not None and str(f.get("copia", "")).startswith("procedencia saneada") and f.get("sha256_origen") == eh[k].get("sha256")
                    and f.get("sha256") == sha(data) == (ep.get(k) or {}).get("sha256") and (ep.get(k) or {}).get("bytes") == len(data)
                    and set(ep.get(k) or {}) == set(eh[k])):
                mot.append("entrada %s cambiada sin ser una copia saneada declarada" % k)
        if {k: v for k, v in p.items() if k not in ("files", "tree_sha256")} != {k: v for k, v in h.items() if k not in ("files", "tree_sha256")}:
            mot.append("cambia algo del manifiesto fuera de sus entradas")
        arboles = {}
        if "tree_sha256" in h:
            arbol = lambda m: sha(json.dumps(m["files"], sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))  # noqa: E731
            arboles = {"arbol_historico": h["tree_sha256"], "arbol_publico": p.get("tree_sha256")}
            if h["tree_sha256"] != arbol(h) or p.get("tree_sha256") != arbol(p):
                mot.append("árbol que no deriva de sus archivos")
        out[clave] = dict({"manifiesto_publico": "nucleo_s6/raiz/" + raiz + nombre, "manifiesto_historico": "referencias/fam01/manifiestos_historicos/" + ref,
                           "sha256_historico": sha(hb), "sha256_publico": sha(pb), "entradas_saneadas": saneadas,
                           "correspondencia_comprobada": not mot and bool(saneadas), "motivos": mot}, **arboles)
    return out


def preparar(raiz: Path | None = None):
    """sys.path con el núcleo copiado delante (src/paper2b y el paquete herramientas de la raíz)."""
    raiz = Path(raiz or RAIZ)
    for p in (str(raiz), str(raiz / "src")):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    import paper2b
    need(Path(paper2b.__file__).resolve().parents[1] == (Path(raiz) / "src").resolve(), "NUCLEO_NO_COPIADO:" + paper2b.__file__)


def cargar(nombre: str, ruta: Path):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


# ================================================================================================ contexto S6
class Contexto:
    """Interfaz de contexto_s6.ContextoS6 (C, view, cfg, inp, prov, claims, technical, identity, run()); construcción idéntica de
    RunInputs, sin autoridad viva, encargo ni exigencia de conformidad del entorno (ver cabecera)."""

    def __init__(self, p: dict, raiz: Path | None = None, inst: Path | None = None):
        from herramientas.bloque2 import entorno as E
        from herramientas.bloque2 import familias as FAM
        from herramientas.b import ejecutar_b as EB
        from herramientas.b import nacional as NAT
        from herramientas.s3.validadores.core import Contracts
        from paper2b import claims as CL
        from paper2b import external as X
        from paper2b import keys as K
        from paper2b import run as RUN
        from paper2b.d7view import D7View
        E.set_runtime_conventions()
        self.RUN, self.EB = RUN, EB
        self.authority = None              # sin autoridad viva: los registros lo declaran («autoridad»: null)
        t0 = time.time()
        ROOT, inst = Path(raiz or RAIZ), Path(inst or INST)
        self.C = Contracts.load(ROOT / p["contract_root"], p["contract_sha256"])
        self.d7_dir = ROOT / p["d7_dir"] / "versions" / p["d7_tree"]
        self.d7info = FAM.verify_version(self.d7_dir, "D7", expected_tree=p["d7_tree"])
        need(self.d7info["manifest"]["authority_package_sha256"] == p["s6_package"], "D7_NOT_UNDER_S6")
        self.view = D7View.load(self.C, self.d7_dir)
        need(self.view.phase["phase_status"] == "complete" and self.view.phase["ready_for_b"] is True, "D7_NOT_READY")
        probe = NAT.Providers(ROOT, self.C, self.view, protocol_sha256="0" * 64, technical={})
        set_index = {}
        for sid, (entry, ed, block) in probe.set_case.items():
            set_index.setdefault(entry["preregistration_id"], {}).setdefault(ed, {})[block] = sid
        self.set_index = set_index
        self.cfg = EB.final_config(replace(RUN.RunConfig(), run_class=p["run_class"]), set_index, p["run_class"])
        ea = p["entorno_aprobado"]
        self.env_doc = E.assessment(ROOT, manifest_path=ea["manifest_path"], manifest_sha256=ea["manifest_sha256"],
                                    lock_path=ea["lock_path"], lock_sha256=ea["lock_sha256"])   # = EB.environment_document con ese perfil
        self.env_rec = records_sin_lanzadores()                                            # solo para la comprobación F2
        ddeps = {d["role"]: d for d in self.d7info["manifest"]["input_dependencies"]}
        gdep, mdep = ddeps["external_grid"], ddeps["d4_model_case_map"]
        grid_raw = (ROOT / gdep["path"]).read_bytes()
        need(sha(grid_raw) == gdep["sha256"], "GRID_HASH")
        mraw = (ROOT / mdep["path"]).read_bytes()
        need(sha(mraw) == mdep["sha256"], "D4_MAP_HASH")
        import csv
        import io
        self.mcm = list(csv.DictReader(io.StringIO(mraw.decode("utf-8"))))
        need(sha((ROOT / (p["contract_root"] + "contratos/contract_manifest.json")).read_bytes()) == p["contract_sha256"], "CONTRACT")
        theory_path = "fase4_teoria/baseline_model_v2_2.md"
        proto_path = p["contract_root"] + "contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md"
        self.theory = ("v2_2", theory_path, sha((ROOT / theory_path).read_bytes()))
        self.protocol = ("S2", proto_path, sha((ROOT / proto_path).read_bytes()))
        code = EB.code_manifest(ROOT)
        docs = {"configuration": self.cfg.as_dict(), "tolerances": EB.TOLERANCES, "method": EB.method_manifest(self.cfg), "code": code,
                "environment": self.env_doc}
        self.technical = {role + "_sha256": sha(K.canon(obj) + b"\n") for role, obj in sorted(docs.items())}
        self.technical["contract_sha256"] = p["contract_sha256"]
        self.technical = dict(sorted(self.technical.items()))
        self.prov = NAT.Providers(ROOT, self.C, self.view, protocol_sha256=self.protocol[2], technical=self.technical)
        ev = {r["evidence_id"]: r for r in self.view.tables["source_evidence"]}
        d7m = (self.d7_dir / "d7_manifest.json").resolve().relative_to(ROOT.resolve()).as_posix()
        grid_dep = {"role": "external_grid", "manifest_path": d7m, "manifest_sha256": self.d7info["manifest_sha256"],
                    "artifact_path": gdep["path"], "artifact_sha256": gdep["sha256"], "record_pk": {"table": "grid"}}
        productor = Path(inst) / p["productor"]
        self.inp = RUN.RunInputs(contracts=self.C, d7=self.view, registry=self.prov.registry, grid_cells=X.read_grid(grid_raw),
                                 grid_sha256=gdep["sha256"], grid_dependency=grid_dep, model_case_map=self.mcm,
                                 availability_matrix_hash=ev["EV.D4.MATRIX"]["payload_sha256"], national=self.prov.national,
                                 conditional_key=self.prov.conditional_key, technical=self.technical, theory=self.theory,
                                 protocol=self.protocol, manifest_hash=p["manifest_sha256"], contract_sha256=p["contract_sha256"],
                                 producer_sha256=sha(productor.read_bytes()),
                                 environment_manifest_sha256=self.technical["environment_sha256"],
                                 algorithm_config_sha256=self.technical["configuration_sha256"],
                                 crosswalk_sha256=ev["EV.CROSSWALK"]["payload_sha256"], dme_gai=0.0, set_index=set_index,
                                 created_at="", tolerances=dict(EB.TOLERANCES))
        self.claims = CL.derive(self.prov.registry, self.mcm, set_index)
        self.identity = {"etiqueta": p["etiqueta"], "run_class": p["run_class"], "s6": p["s6_package"], "d7": p["d7_tree"],
                         "grilla_sha256": gdep["sha256"], "mapa_d4_sha256": mdep["sha256"], "registro_sha256": sha(K.canon(self.prov.registry)),
                         "contrato_sha256": p["contract_sha256"], "tecnicas": self.technical,
                         "huella_entorno_sha256": self.env_doc["fingerprint_sha256"]}
        self.identity_sha256 = sha(K.canon(self.identity))
        self.setup_seconds = round(time.time() - t0, 2)

    def run(self, set_id: str, unit_id: str):
        r = self.RUN.Run(self.inp, self.cfg, unit={"unit_id": unit_id, "set_id": set_id, "prefix": {p: 0 for p in self.RUN.STRUCT}})
        need(r.model.kind == "modelo_teorico_v2_2" and r.model.certified, "PROVIDER_NOT_CERTIFIED")
        return r


def referencia_calculo(ctx, GE):
    """GE.Referencia sin cargar las fuentes históricas: el cálculo (Generador.previas) solo usa ctx_key y K1, métodos originales
    sin cambios; se fija el mismo estado que su __init__ deja para ellos (incluido COV.q_pot = q_pot_exact)."""
    from paper2b import cobertura as COV
    from paper2b.intervalos import Iv
    ref = object.__new__(GE.Referencia)
    ref.ctx, ref.COV, ref.Iv, ref.qpe = ctx, COV, Iv, GE.q_pot_exact
    COV.q_pot = GE.q_pot_exact
    return ref


def modulos(inst: Path | None = None):
    GC = cargar("cand_generador_seleccion", Path(inst or INST) / "herramientas/b/generador_seleccion.py")
    return GC, GC.GE


def modulos_ruta():
    """Piezas instaladas de la ruta S6 (copias exactas): ejecutor por lotes, Verificador S6 (validador productivo R2), generador del registro
    productivo, productor y validador R3. Mismos nombres de módulo que tarea_paso4 donde los validadores los exigen."""
    U = cargar("cand_unidades", INST / "herramientas/b/unidades.py")
    P2 = cargar("cand_paquete_seleccion", INST / "herramientas/s3/validadores/paquete_seleccion.py")
    RP = cargar("registro_productivo", INST / "herramientas/b/registro_productivo.py")
    return U, P2, RP


def definiciones() -> dict:
    return {d["unidad"]: d for d in (json.loads(x) for x in (DATOS / "definiciones.jsonl").read_text(encoding="utf-8").splitlines() if x.strip())}


def definicion(unidad: str) -> dict:
    """Definición vinculada de la unidad (datos/fam01/definiciones.jsonl, extraída con vinculo_paso4 de su fuente histórica)."""
    d = definiciones().get(unidad)
    need(d is not None, "UNIDAD_SIN_DEFINICION:" + unidad)
    return d


def unidad_de_lista(seleccion: str, unidad: str, inst: Path | None = None) -> dict:
    need(seleccion in LISTAS, "SELECCION_DESCONOCIDA")
    rel, h = LISTAS[seleccion]
    us = [u for u in leer_json(Path(inst or INST) / rel, h)["unidades"] if u["unidad"] == unidad]
    need(len(us) == 1, "UNIDAD_FUERA_DE_LA_LISTA_%s:%s" % (seleccion, unidad))
    return us[0]


# ================================================================================================ ruta S6 sin capa administrativa
def _constantes_productor() -> dict:
    """SCHEMA, CODIGO y PREFIJO_LOGICO del productor S6 instalado (seleccion_paso4.py), leídos de su texto sin importarlo: su importación
    exige el núcleo bajo la instalación, y aquí el núcleo cargado es el de la raíz (idéntico byte a byte; lo comprueba extraer_fam01)."""
    import ast
    out = {}
    for n in ast.parse((INST / "herramientas/b/seleccion_paso4.py").read_text(encoding="utf-8")).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and getattr(n.targets[0], "id", None) in ("SCHEMA", "CODIGO", "PREFIJO_LOGICO"):
            out[n.targets[0].id] = ast.literal_eval(n.value)
    need(len(out) == 3, "CONSTANTES_DEL_PRODUCTOR")
    return out


class Flujo:
    """El módulo-flujo F que el Verificador y el Ejecutor reciben del productor S6 (seleccion_paso4): sus constantes, plan =
    unidades.plan_selection y el manifiesto de código con su misma fórmula. Sin despliegue, autoridad ni oficial()."""

    def __init__(self, U):
        c = _constantes_productor()
        self.SCHEMA, self.CODIGO, self.PREFIJO_LOGICO = c["SCHEMA"], c["CODIGO"], c["PREFIJO_LOGICO"]
        self.CAND, self.AREA = INST, INST.parent
        self.planificar = U.plan_selection
        self.sha, self.canon = sha, canon

    @staticmethod
    def testigo_dict(w):
        return json.loads(json.dumps({k: (dict(v) if hasattr(v, "keys") else v) for k, v in dict(w).items()}, default=list))

    def codigo_manifiesto(self):
        fs = sorted((RAIZ / "src/paper2b").glob("*.py"))
        nuc = sha(b"".join(f.name.encode() + b"\0" + f.read_bytes() for f in fs))
        return {"nucleo_candidato_sha256": nuc, "archivos": {r: sha((INST / r[len(self.PREFIJO_LOGICO):]).read_bytes()) for r in self.CODIGO}}


KIND_LISTA = "lista-reproduccion-fam01-v1"


def entrada_lista(u: dict, d: dict) -> dict:
    """Fila de la lista de una tarea (forma de corrida_paso4.lista_tarea): identidad de la lista R2 fijada y fuente del testigo."""
    return {"unidad": u["unidad"], "cell_id_contractual": u.get("cell_id_contractual"), "familia": u.get("familia"), "contrato": u.get("contrato"),
            "numerico": u.get("numerico"), "witness_of": u.get("witness_of"), "fuente": dict(d["fuente"], tipo=d["tipo"])}


def lista_r2(unidades: list, tarea: str) -> dict:
    ref = {u["unidad"]: u for u in leer_json(INST / LISTAS["R2"][0], LISTAS["R2"][1])["unidades"]}
    defs = definiciones()
    return {"kind": KIND_LISTA, "seleccion": "R2", "tarea": tarea, "plan_sha256": None,
            "unidades": [entrada_lista(ref[u], defs[u]) for u in unidades]}


def _lista_local(self, lista):
    """En lugar de Verificador.validar_lista_reproduccion (su vínculo lee las entregas históricas): cada fila debe ser la de su unidad en la
    lista R2 fijada (sha256) con la fuente de su testigo; el testigo es el de datos/fam01/definiciones.jsonl, extraído y vinculado con
    vinculo_paso4 desde esas fuentes. Misma salida; nunca lanza."""
    cod, test = [], {}
    try:
        need(isinstance(lista, dict) and lista.get("kind") == KIND_LISTA and lista.get("seleccion") == "R2", "LISTA_NO_R2")
        ref = {u["unidad"]: u for u in leer_json(INST / LISTAS["R2"][0], LISTAS["R2"][1])["unidades"]}
        defs = definiciones()
        us = lista["unidades"]
        need(us and len({x["unidad"] for x in us}) == len(us), "LISTA_CON_UNIDADES_REPETIDAS")
        for x in us:
            u = x["unidad"]
            need(u in ref and u in defs, "UNIDAD_FUERA_DE_LA_LISTA_R2")
            need(defs[u]["tipo"] == "testigo" and defs[u]["seleccion"] == "R2", "UNIDAD_SIN_TESTIGO")
            need(x == entrada_lista(ref[u], defs[u]), "FILA_DISTINTA_DE_LA_LISTA_FIJADA")
            test[u] = json.loads(json.dumps(defs[u]["definicion"]))
    except Fam01Error as e:
        cod.append(str(e))
    except (OSError, ValueError, KeyError, TypeError):
        cod.append("LISTA_ILEGIBLE")
    return {"cumple": not cod, "codigos": cod, "unidades": test, "definiciones": {}}


def _identidad_local(self, ident, sel, plan):
    """En lugar de Verificador.verificar_identidad: el productor es el de ESTA corrida (sin entregas anteriores ni autoridad viva). Mismas
    exigencias sobre el checkpoint (más estrictas: identidad completa del contexto), mismas derivaciones de configuración y método y
    MISMA fórmula del run_id."""
    from dataclasses import replace
    from herramientas.b import ejecutar_b as EB
    P2 = sys.modules[type(self).__module__]
    n = P2.need
    j = lambda o: json.loads(canon(o))  # noqa: E731
    n(isinstance(ident, dict), "ESQUEMA", "identidad no es objeto")
    n(set(ident) == {"autoridad", "tabla_sha256", "sello_seleccion", "plan_sha256", "codigo", "sup", "run_class"}, "IDENTIDAD", "claves de identidad")
    rc, inp = self.ctx.identity["run_class"], self.ctx.inp
    cfg_sha = sha(self.K.canon(replace(self.cfg, run_class=rc).as_dict()) + b"\n")
    met_sha = sha(self.K.canon(EB.method_manifest(replace(self.cfg, run_class=rc))) + b"\n")
    n(cfg_sha == self.ctx.technical["configuration_sha256"] == inp.algorithm_config_sha256, "DERIVACION", "la configuración no se reproduce")
    n(met_sha == self.ctx.technical["method_sha256"], "DERIVACION", "el método no se reproduce")
    n(j(ident["autoridad"]) == j(self.ctx.identity), "IDENTIDAD", "identidad del contexto distinta")
    n(j(ident["codigo"]) == j(self.F.codigo_manifiesto()), "IDENTIDAD", "código productor distinto")
    n(j(ident["sup"]) == j(self.cfg.sup.as_dict()), "IDENTIDAD", "SupConfig")
    n(ident["run_class"] == rc, "IDENTIDAD", "run_class")
    n(ident["tabla_sha256"] == sel["tabla"]["sha256"] and ident["sello_seleccion"] == sel["sello_sha256"] and ident["plan_sha256"] == plan["plan_sha256"],
      "IDENTIDAD", "tabla, sello o plan")
    self._tec_prod = {"configuration_sha256": cfg_sha, "method_sha256": met_sha}
    run_id = "BRUN-" + self.K.H({"d7": inp.d7.manifest["tree_sha256"], "config": cfg_sha, "producer": inp.producer_sha256, "contract": inp.contract_sha256})[:24]
    return "actual", run_id, "v3"


ADAPTACIONES_VERIFICADOR = ("Verificador.__init__ del validador instalado SIN puerta_autoridad (no hay autoridad viva) ni puerta_dependencias (exige "
                            "nombres lógicos del despliegue); las dependencias se registran por ruta y sha256",
                            "validar_lista_reproduccion -> _lista_local (lista R2 fijada + definiciones.jsonl en vez de las entregas históricas)",
                            "verificar_identidad -> _identidad_local (productor de esta corrida; misma fórmula del run_id)",
                            "todo lo demás (selección canónica, plan, lotes, clave E12, techo, λ_π, K1, C2, G, inversiones, geometría, evidencia, "
                            "Checker, R1/R2, resumen canónico, filas ajenas) es el código instalado sin cambios")


def verificador(ctx, ref, GC, U, P2):
    """Instancia de la clase Verificador INSTALADA (registro_productivo exige esa clase) con las adaptaciones de ADAPTACIONES_VERIFICADOR."""
    import types
    F = Flujo(U)
    deps = {Path(m.__file__).resolve().relative_to(BASE).as_posix(): sha(Path(m.__file__).read_bytes())
            for m in (GC, GC.GE, P2, sys.modules[__name__]) + tuple(sys.modules["paper2b." + x] for x in ("contrato_paquete", "rules", "seleccion_valores")
                                                                      if "paper2b." + x in sys.modules)}
    pa, pd = P2.puerta_autoridad, P2.puerta_dependencias
    P2.puerta_autoridad = lambda c: None
    P2.puerta_dependencias = lambda *a, **k: deps
    try:
        V = P2.Verificador(ctx, ref, F, GC, raiz_fuentes=None)
    finally:
        P2.puerta_autoridad, P2.puerta_dependencias = pa, pd
    V.validar_lista_reproduccion = types.MethodType(_lista_local, V)
    V.verificar_identidad = types.MethodType(_identidad_local, V)
    return V, F


# ------------------------------------------------------------------------------------------------ formato R2 (adaptador)
FINAL_C = {"ok": "completo", "incompleta": "incompleto", "error": "error", "no_aplicable": "no_aplicable"}   # bloque_s1 c1.1 (y tarea_paso4 R3)
FMT_R2 = ("FMT-R2-v1 (correspondencia de FORMATO del adaptador; no es una regla del comparador). El documento COMPARABLE de una unidad R2 se "
          "deriva del documento NATIVO validado (registro_productivo.ensamblar) y cambia solo: familia, ruta (si existe) y estrato, y en las 6 "
          "unidades del productor piloto clave_estructural_lima1913, copiados de la entrada del manifiesto de bloque de la unidad "
          "(datos/fam01/clasificacion_manifiesto.json), como hacían los productores históricos; estado_generador = resultado.estado; "
          "estado_final = FINAL_C[resultado.estado] de los trabajadores históricos («completo» = cálculo del generador terminado con estado ok; "
          "NO significa validado: la validación es el registro productivo); resultado.etiqueta = id[:16] (rótulo que el trabajador histórico "
          "pasaba a Generador.celda; el S6 «<lote>:<diseño>-<menú>-<país>» queda en el nativo); filas = {archivo, sha256, tablas}; "
          "«ensamblado» queda solo en el nativo. Ningún valor, estado de celda ni fila cambia; las filas son los mismos bytes.")


def documento_compatible_r2(nativo: dict, fb: bytes, clas: dict, archivo_filas: str) -> dict:
    res = dict(nativo["resultado"], etiqueta=str(nativo["id"])[:16])
    doc = {"id": nativo["id"], **clas, "estado_generador": res.get("estado"), "estado_final": FINAL_C.get(res.get("estado"), "rechazado"),
           "contrato_exportado": nativo["contrato_exportado"], "resultado": res,
           "filas": {"archivo": archivo_filas, "sha256": sha(fb), "tablas": {k: len(v) for k, v in json.loads(fb).items() if isinstance(v, list)}}}
    return doc


def clasificacion(unidad: str) -> dict:
    c = leer_json(DATOS / "clasificacion_manifiesto.json")["unidades"].get(unidad)
    need(c is not None, "UNIDAD_SIN_CLASIFICACION:" + unidad)
    return c


# ------------------------------------------------------------------------------------------------ rastro de lecturas
class Rastro:
    """Archivos abiertos durante la ejecución (gancho de auditoría «open»): dentro del paquete (ruta relativa), del intérprete (solo número)
    y FUERA de ambos (ruta completa: debe quedar vacío). No altera nada."""

    def __init__(self):
        import os
        self.dentro, self.interprete, self.fuera, self.activo = set(), 0, set(), True
        base = str(BASE.resolve()).lower()
        py = tuple({str(Path(p).resolve()).lower() for p in (sys.base_prefix, sys.prefix, sys.exec_prefix)})

        def gancho(ev, args):
            if ev != "open" or not self.activo or not isinstance(args[0], (str, bytes, os.PathLike)):
                return
            p = os.path.abspath(os.fsdecode(args[0]))
            pl = p.lower()
            if pl.startswith(base):
                self.dentro.add(p[len(base):].lstrip("\\/").replace("\\", "/"))
            elif pl.startswith(py):
                self.interprete += 1
            elif not pl.startswith(("nul", "\\\\.\\")):
                self.fuera.add(p)
        sys.addaudithook(gancho)

    def informe(self):
        """Solo archivos que existen (la importación también intenta abrir .pyc ausentes con -B; no se cuentan)."""
        import os
        self.activo = False
        return {"en_el_paquete": sorted(x for x in self.dentro if not x.startswith("salidas/") and (BASE / x).is_file()),
                "aperturas_del_interprete": self.interprete, "fuera_del_paquete_y_del_interprete": sorted(x for x in self.fuera if os.path.isfile(x))}


# ------------------------------------------------------------------------------------------------ cálculo y validación
def calcular_r2(ctx, ref, V, F, GC, GE, U, P2, unidades: list, sal: Path, tarea: str):
    """[CÁLCULO] tarea R2 como tarea_paso4 (rama R2): selección SEL-PASO4-REPRO-v1 con el Verificador del MISMO contexto -> plan
    (unidades.plan_selection, lotes por grupo CA2) -> unidades.EjecutorSeleccion (techos compartidos entre los Run del proceso)."""
    pdir = sal / "paquete"
    raw = canon(lista_r2(unidades, tarea))
    sel = V.seleccion_esperada(raw, P2.REGLA_REPRO)
    sel["sello_sha256"] = sha(canon({k: v for k, v in sel.items() if k != "sello_sha256"}))
    pdir.mkdir(parents=True)
    (pdir / "seleccion.json").write_bytes(canon(sel))
    (pdir / "entrada").mkdir()
    (pdir / "entrada/global_extreme_v3.json").write_bytes(raw)
    (pdir / "plan.json").write_bytes(canon(U.plan_selection(sel)))
    U.EjecutorSeleccion(pdir, ctx, ref, V, GC=GC, GE=GE, schema=F.SCHEMA, codigo=F.codigo_manifiesto(), error=Fam01Error).ejecutar(reanudar=False)
    return pdir


def validar_r2(V, RP, pdir: Path, sal: Path) -> dict:
    """[VALIDACIÓN] registro_productivo.generar: verificar_paquete del Verificador S6 sobre los bytes finales del paquete y ensamblaje por
    unidad (documento NATIVO + filas en unidades/); escribe registro_productivo.json y dictamen_validacion.json."""
    return RP.generar(V, pdir, sal, salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json")


def comparables_r2(sal: Path, reg: dict) -> dict:
    """Documento COMPARABLE (FMT_R2) de cada unidad, junto al nativo, y la relación entre ambos (comparables/relacion.json)."""
    (sal / "comparables").mkdir()
    rel = {}
    for u, e in sorted(reg["unidades"].items()):
        db, fb = (sal / e["documento"]).read_bytes(), (sal / e["filas"]).read_bytes()
        n = u.replace(":", "_")
        doc = documento_compatible_r2(json.loads(db), fb, clasificacion(u), Path(e["filas"]).name)
        cb = canon(doc) + b"\n"
        (sal / "comparables" / (n + ".json")).write_bytes(cb)
        rel[u] = {"nativo": {"documento": e["documento"], "sha256": sha(db)}, "comparable": {"documento": "comparables/%s.json" % n, "sha256": sha(cb)},
                  "filas": {"archivo": e["filas"], "sha256": sha(fb)}}
    r = {"regla": FMT_R2, "unidades": rel}
    (sal / "comparables" / "relacion.json").write_bytes(canon(r) + b"\n")
    return r


def doc_r3(ctx, u: str, rep: dict, res: dict, fb: bytes, n: str) -> dict:
    """Documento de una unidad R3 como tarea_paso4 (rama R3)."""
    return {"id": u, "familia": rep["familia"], "ruta": rep.get("ruta"), "estrato": rep.get("estrato"),
            "estado_final": {"ok": "completo", "no_aplicable": "no_aplicable"}.get(res.get("estado"), "rechazado"),
            "estado_generador": res.get("estado"), "resultado": res, "contrato_exportado": "v3",
            "filas": {"archivo": n + "_filas.json", "sha256": sha(fb), "tablas": {k: len(v) for k, v in json.loads(fb).items() if isinstance(v, list)}},
            "identidad_productor_sha256": getattr(ctx, "identity_sha256", None), "run_class": ctx.identity["run_class"]}


def dependencias_cargadas():
    """Paquetes de terceros realmente importados: distribución -> versión (site-packages) o ruta del
    vendorizado dentro del núcleo. La biblioteca estándar (Lib y DLLs del intérprete) y el código del
    proyecto no se listan."""
    import importlib.metadata as md
    dist = md.packages_distributions()
    base = BASE.resolve()
    fuera = {}
    for nombre, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        pf = Path(f).resolve()
        top = nombre.split(".")[0]
        if "site-packages" in pf.parts:
            for dn in dist.get(top, [top]):
                try:
                    fuera[dn] = md.version(dn)
                except md.PackageNotFoundError:
                    fuera[dn] = None
        elif base in pf.parents and "vendor" in pf.parts:
            rel = pf.relative_to(base).parts
            fuera[top] = "vendorizado: " + "/".join(rel[: rel.index("vendor") + 2])
    return dict(sorted(fuera.items()))


ESTADOS_VALIDADOS = ("completa_validada", "no_aplicable_validada")


def exito_global(por: dict, cumple) -> bool:
    """Éxito de una tarea: TODAS sus unidades calculadas y validadas por el validador productivo, y su dictamen cumple. Una validación
    ausente (cumple None) o pendiente nunca da éxito."""
    return bool(por) and all(x.get("calculo") == "terminado" and x.get("validacion") in ESTADOS_VALIDADOS for x in por.values()) and cumple is True


def correr(seleccion: str, unidades: list, salida: Path) -> dict:
    """Recorrido de una TAREA (una o varias unidades numéricas de la misma lista), en la carpeta NUEVA `salida`:
    contexto S6 -> [cálculo] -> [validación productiva] -> productos por unidad (y, en R2, documento comparable). Tiempos separados.
    La comparación con el original es otro paso (comparar). Ninguna unidad queda «validada» sin su registro productivo."""
    import os
    import platform
    t0, c0 = time.time(), time.process_time()
    need(unidades and len(set(unidades)) == len(unidades), "UNIDADES_VACIAS_O_REPETIDAS")
    us = [unidad_de_lista(seleccion, u) for u in unidades]
    defs = {u: definicion(u) for u in unidades}
    need(all(d["seleccion"] == seleccion for d in defs.values()), "DEFINICION_DE_OTRA_SELECCION")
    need(all(x["numerico"] is True for x in us), "UNIDAD_NA: las NA se comprueban documentalmente (fam01-na), no se calculan")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    rastro = Rastro()
    preparar()
    ctx = Contexto(parametros())
    GC, GE = modulos()
    U, P2, RP = modulos_ruta()
    ref = referencia_calculo(ctx, GE)
    t_ctx = round(time.time() - t0, 2)
    tarea = "fam01-%s-%s" % (seleccion, sha(canon(sorted(unidades)))[:12])
    if seleccion == "R2":
        V, F = verificador(ctx, ref, GC, U, P2)
        t1 = time.time()
        pdir = calcular_r2(ctx, ref, V, F, GC, GE, U, P2, unidades, salida, tarea)
        t_calc = round(time.time() - t1, 2)
        t2 = time.time()
        reg = validar_r2(V, RP, pdir, salida)
        t_val = round(time.time() - t2, 2)
        rel = comparables_r2(salida, reg)
        adapt = list(ADAPTACIONES_VERIFICADOR)
    else:
        PR = cargar("productor_r3", INST / "herramientas/b/productor_r3.py")
        VR3 = cargar("validador_r3", INST / "herramientas/b/validador_r3.py")
        import types
        SPn = types.SimpleNamespace(GC=GC, GE=GE, P2=P2)     # lo que ValidadorR3S6 usa del módulo seleccion_paso4
        VR = VR3.ValidadorR3S6(ctx, ref, SPn, RAIZ)           # ANTES de previas y cálculo, como tarea_paso4
        prod = PR.ProductorR3(ctx, ref, GC, RAIZ, almacen=None)
        pre = {}
        for u in unidades:
            ok, pr, _ = prod.previas(defs[u]["definicion"])
            pre[u] = dict(pr, ok=bool(ok))
        need(all(x["ok"] for x in pre.values()), "PREVIAS_R3_FALLAN:%s" % sorted(u for u, x in pre.items() if not x["ok"]))
        (salida / "unidades").mkdir()
        productos, t1 = {}, time.time()
        for u in unidades:                                    # [CÁLCULO] (techos compartidos entre unidades por prod.store)
            rep = defs[u]["definicion"]
            res, filas, _ = prod.celda(rep)
            n = u.replace(":", "_")
            fb = canon(filas or {}) + b"\n"
            (salida / "unidades" / (n + "_filas.json")).write_bytes(fb)
            (salida / "unidades" / (n + ".json")).write_bytes(canon(doc_r3(ctx, u, rep, res, fb, n)) + b"\n")
            productos[u] = {"documento": "unidades/%s.json" % n, "filas": "unidades/%s_filas.json" % n}
        t_calc = round(time.time() - t1, 2)
        t2 = time.time()                                      # [VALIDACIÓN] validador R3 instalado sobre los bytes finales
        reg = RP.generar_r3(VR, salida, productos, {u: defs[u]["definicion"] for u in unidades}, salida=salida / "registro_productivo.json",
                            dictamen=salida / "dictamen_validacion.json")
        t_val = round(time.time() - t2, 2)
        rel, adapt = None, ["ValidadorR3S6 recibe GC, GE y P2 (lo que usa de seleccion_paso4); por lo demás, validador instalado sin cambios"]
    ent = {"documento": ctx.env_doc, "records_sin_lanzadores": ctx.env_rec, "environment_sha256": ctx.technical["environment_sha256"]}
    (salida / "entorno.json").write_bytes(canon(ent) + b"\n")
    eq = equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"])
    por = {}
    for u in unidades:
        e = reg["unidades"][u]
        n = u.replace(":", "_")
        db = (salida / e["documento"]).read_bytes()
        est_gen = (json.loads(db).get("resultado") or {}).get("estado")
        ccu = json.loads((salida / e["filas"]).read_bytes()).get("cell_context") or [{}]
        por[u] = {"calculo": "terminado" if est_gen in ("ok", "no_aplicable") else "rechazado", "estado_generador": est_gen, "run_id": ccu[0].get("run_id"),
                  "validacion": e["estado"], "validacion_codigos": e.get("codigos") or [], "documento": e["documento"], "documento_sha256": e["documento_sha256"],
                  "filas": e["filas"], "filas_sha256": e["filas_sha256"],
                  "comparable": (rel["unidades"][u]["comparable"] if rel else {"documento": e["documento"], "sha256": e["documento_sha256"]})}
    cc = json.loads((salida / por[unidades[0]]["filas"]).read_bytes()).get("cell_context") or [{}]
    ej = {"seleccion": seleccion, "unidades": unidades, "tarea": tarea, "por_unidad": por, "run_id": cc[0].get("run_id"),
          "validacion": {"cumple": reg["verificacion"].get("cumple"), "codigos": reg["verificacion"].get("codigos"), "registro": "registro_productivo.json",
                         "registro_sha256": sha((salida / "registro_productivo.json").read_bytes()), "adaptaciones": adapt},
          "tecnicas": ctx.technical,
          "contrato": {"sha256_publico": ctx.technical["contract_sha256"], "sha256_historico": parametros()["contract_sha256_historico"],
                       "nota": "contrato G-NA-1 en su copia pública (SAN-RUTAS-v1); la correspondencia con el histórico la comprueba fam01-comparar"},
          "entorno": {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"), "documento": "entorno.json",
                      "f2": eq, "python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"),
                      "hash_randomization": sys.flags.hash_randomization, "hilos": {k: os.environ.get(k) for k in HILOS}, "TZ": os.environ.get("TZ")},
          "tiempos_s": {"contexto": t_ctx, "calculo": t_calc, "validacion": t_val, "total": round(time.time() - t0, 2), "cpu": round(time.process_time() - c0, 2)},
          "dependencias_fuera_de_la_biblioteca_estandar": dependencias_cargadas()}
    ej["exito"] = exito_global(por, ej["validacion"]["cumple"])
    (salida / "archivos_leidos.json").write_bytes((json.dumps(rastro.informe(), ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ listas y marco (documental)
def _rb():
    raw = (RAIZ / REGLA_B[0]).read_bytes()
    need(sha(raw) == REGLA_B[1], "REGLA_B_DISTINTA_DE_LA_FIJADA")
    return cargar("fam01_regla_b_v2", RAIZ / REGLA_B[0])


def comprobar_listas() -> dict:
    """Integridad documental de R2 (1.740), del marco R3 (536) y de la muestra R3 (27, 5 NA): unicidad, pertenencia, recuentos,
    identidad B, separación R2/marco, definiciones e índice de originales. Sin cálculo científico."""
    RB = _rb()
    r2 = leer_json(INST / LISTAS["R2"][0], LISTAS["R2"][1])
    r3 = leer_json(INST / LISTAS["R3"][0], LISTAS["R3"][1])
    marco = leer_json(DATOS / MARCO[0], MARCO[1])
    prop = leer_json(DATOS / PROPUESTA_B[0], PROPUESTA_B[1])
    defs = {json.loads(x)["unidad"]: json.loads(x) for x in (DATOS / "definiciones.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()}
    idx = leer_json(REFS / "indice_originales.json")["unidades"]
    ok, c = [], {}

    def chk(nombre, cond, detalle=None):
        ok.append((nombre, bool(cond)))
        if detalle is not None:
            c[nombre] = detalle

    U2, U3, M = r2["unidades"], r3["unidades"], marco["celdas"]
    # ---- R2
    ids2 = [u["unidad"] for u in U2]
    chk("R2: 1.740 unidades distintas", len(U2) == 1740 == len(set(ids2)))
    chk("R2: cell_id contractual y E12 únicos", len({u["cell_id_contractual"] for u in U2}) == len({u["cell_id_e12"] for u in U2}) == 1740)
    fam2 = Counter(u["familia"] for u in U2)
    chk("R2: S1 1.728 (576 por menú) + C2 12", fam2 == Counter({"S1-d": 576, "S1-f": 576, "S1-df": 576, "C2": 12}), dict(fam2))
    chk("R2: contratos v3 1.159 / v2 581", Counter(u["contrato"] for u in U2) == Counter({"v3": 1159, "v2": 581}), dict(Counter(u["contrato"] for u in U2)))
    c["R2: motivos"] = dict(Counter(m for u in U2 for m in u["motivos"]))
    c["R2: clasificacion"] = dict(Counter(u.get("clasificacion") for u in U2))
    chk("R2: todas numéricas", all(u["numerico"] is True for u in U2))
    # ---- marco R3
    filas_m = [x["fila"] for x in M]
    chk("marco: 536 celdas, filas únicas", len(M) == 536 == len(set(filas_m)))
    chk("marco: cell_id_B, cell_id_A y E12 únicos", len({x["cell_id_B"] for x in M}) == len({x["cell_id_A"] for x in M}) == len({x["cell_id_e12"] for x in M}) == 536)
    num = Counter(x["numerico"] for x in M)
    chk("marco: 371 numéricas + 165 NA", num == Counter({True: 371, False: 165}), {"numericas": num[True], "NA": num[False]})
    estr = Counter(x["estrato"] for x in M)
    chk("marco: 169 estratos", len(estr) == 169, len(estr))
    c["marco: familias"] = dict(Counter(x["familia"] for x in M))
    c["marco: contratos"] = dict(Counter(x["contrato"] for x in M))
    chk("marco: identidad B = sha256(canon(preimagen_B)) en las 536", all(RB.cell_id(x["preimagen_B"]) == x["cell_id_B"] for x in M))
    chk("propuesta B cita este marco y está comprobada", prop["fuentes"]["identidad"]["sha256"] == MARCO[1] and prop.get("todas_ok") is True
        and prop["C3_correspondencia_E12"]["cell_id_B_distintos"] == 536 and prop["C3_correspondencia_E12"]["biunivoca_B_E12"] is True)
    # ---- muestra R3
    por_fila = {x["fila"]: x for x in M}
    chk("R3: 27 unidades distintas", len(U3) == 27 == len({u["unidad"] for u in U3}))
    chk("R3: todas en el marco", all(u["fila"] in por_fila and u["unidad"] == u["fila"] for u in U3))
    campos = ("familia", "estrato", "cell_id_B", "cell_id_A", "cell_id_e12", "numerico", "contrato")
    chk("R3: identidad igual a la del marco", all(all(u[k] == por_fila[u["fila"]][k] for k in campos) for u in U3))
    chk("R3: 5 NA", sum(1 for u in U3 if u["numerico"] is False) == 5)
    chk("R3: S2 25 + S3 2, contrato v3", Counter(u["familia"] for u in U3) == Counter({"S2": 25, "S3": 2}) and all(u["contrato"] == "v3" for u in U3))
    chk("R3: hash_de_orden B de cada unidad", all(u["hash_de_orden"] == sha(("SEL-PASO4-B-v2|repro|%s|%s" % (u["estrato"], u["cell_id_B"])).encode()) for u in U3))
    rep = RB.reparto_r3(dict(estr))
    muestra = []
    for h, nh in rep["n_h"].items():
        orden = sorted((x for x in M if x["estrato"] == h), key=lambda x: sha(("SEL-PASO4-B-v2|repro|%s|%s" % (h, x["cell_id_B"])).encode()))
        muestra += [(x["fila"], i) for i, x in enumerate(orden[:nh])]
    chk("R3: muestra recalculada desde el marco (§2.7, NA en N_h) = la lista", rep["n"] == 27 and sorted(muestra) == sorted((u["fila"], u["rango_en_el_estrato"]) for u in U3),
        {"n": rep["n"], "estratos_con_muestra": sum(1 for v in rep["n_h"].values() if v)})
    # ---- separación R2 / marco R3
    ids_r2 = {u["unidad"] for u in U2} | {u["cell_id_contractual"] for u in U2} | {u["cell_id_e12"] for u in U2}
    ids_m = set(filas_m) | {x["cell_id_B"] for x in M} | {x["cell_id_A"] for x in M} | {x["cell_id_e12"] for x in M}
    chk("separación: R2 y marco R3 sin identificadores comunes", not (ids_r2 & ids_m), len(ids_r2 & ids_m))
    # ---- definiciones e índice de originales
    chk("definiciones: 1.767 = R2 + R3, testigo en R2 y definición en R3",
        set(defs) == set(ids2) | {u["unidad"] for u in U3} and all(defs[u]["tipo"] == "testigo" for u in ids2)
        and all(defs[u["unidad"]]["tipo"] == "definicion" for u in U3))
    chk("originales: contrato y E12 de la lista = índice de autoridad",
        all(idx[u["unidad"]]["contrato"] == u["contrato"] and idx[u["unidad"]]["cell_id_e12"] == u["cell_id_e12"] for u in U2 + U3))
    # ---- unidades del piloto (regla: primera por identificador estable)
    piloto = {"R2_numerica": sorted(u["unidad"] for u in U2 if u["numerico"])[0], "R3_numerica": sorted(u["unidad"] for u in U3 if u["numerico"])[0],
              "R3_NA": sorted(u["unidad"] for u in U3 if not u["numerico"])[0]}
    return {"cumple": all(v for _, v in ok), "comprobaciones": dict(ok), "detalles": c, "piloto": piloto}


# ================================================================================================ comparador
def comparador():
    """comparar_reproduccion v3-S6 copiado, con su caché nucleo() rellenada como la rellena nucleo() pero desde la copia (contratos
    vivo e histórico autenticados por hash, D7 vivo bajo S6 y D7 de los originales bajo su S5). Los contratos son las copias PÚBLICAS
    (SAN-RUTAS-v1) con su huella real; su correspondencia con la histórica se comprueba aquí y queda en _CACHE["saneamiento"]."""
    preparar()
    CR = cargar("fam01_comparar_reproduccion", INST / "herramientas/b/comparar_reproduccion.py")
    if "C" not in CR._CACHE:
        from herramientas.b import ejecutar_b as EB
        from herramientas.bloque2 import familias as FAM
        from herramientas.s3.validadores.core import Contracts
        from paper2b import contrato_paquete as CP
        from paper2b import convergencia as CV
        from paper2b import inversion as INV
        from paper2b import keys as K
        from paper2b import run as RUN
        from paper2b.d7view import D7View
        from paper2b.numeric import canon_dec
        p = parametros()
        san = correspondencia_saneamiento()                  # contratos públicos (SAN-RUTAS-v1) frente a sus manifiestos históricos
        o = p["originales"]
        need(san["G-NA-1"]["sha256_publico"] == p["contract_sha256"] and san["G-NA-1"]["sha256_historico"] == p["contract_sha256_historico"]
             and san["CA2-4"]["sha256_publico"] == o["contract_publico_sha256"] and san["CA2-4"]["sha256_historico"] == o["contract_sha256"],
             "CONTRATOS_PUBLICOS_DISTINTOS_DE_LOS_DECLARADOS")
        need(san["CA2-4"]["correspondencia_comprobada"], "CA2-4_PUBLICO_SIN_CORRESPONDENCIA:%s" % san["CA2-4"]["motivos"][:3])
        C = Contracts.load(RAIZ / p["contract_root"], p["contract_sha256"])
        d7_dir = RAIZ / p["d7_dir"] / "versions" / p["d7_tree"]
        need(FAM.verify_version(d7_dir, "D7", expected_tree=p["d7_tree"])["manifest"]["authority_package_sha256"] == p["s6_package"], "D7_NO_S6")
        cfg = RUN.RunConfig()
        need(float(cfg.sup.tol_converge) == CR.TOL_CONVERGE, "TOL_CONVERGE")
        need(o["d7_tree"] == CR.D7_ORIGINALES, "D7_ORIGINALES")
        C_hist = Contracts.load(RAIZ / o["contract_root"], o["contract_publico_sha256"])   # copia pública del contrato CA2-4 (4d7e676a…)
        CR._CACHE["saneamiento"] = san
        d7h_dir = RAIZ / "fase2_datos/d7_calibracion/versions" / o["d7_tree"]
        need(FAM.verify_version(d7h_dir, "D7", expected_tree=o["d7_tree"])["manifest"]["authority_package_sha256"] == o["s5_package"], "D7_ORIGINALES_NO_S5")
        CR._CACHE.update(C_hist=C_hist, d7_hist=D7View.load(C_hist, d7h_dir),
                         originales={"contract_sha256": o["contract_sha256"], "contract_root": o["contract_root"], "d7_tree": o["d7_tree"], "s5_package": o["s5_package"]})
        CR._CACHE.update(CV=CV, RUN=RUN, d7=D7View.load(C, d7_dir), TOL=dict(EB.TOLERANCES), tol_root=float(EB.TOLERANCES["T_root_residual"]),
                         xtol=float(cfg.endogenous_xtol), certificado=bool(RUN.provider_for(cfg).certified), tolc=float(cfg.sup.tol_converge))
        CR._CACHE.update(C=C, CP=CP, INV=INV, K=K, dec=canon_dec,
                         autoridad={"s6_package": p["s6_package"], "d7_tree": p["d7_tree"], "contract_root": p["contract_root"], "contract_sha256": p["contract_sha256"]})
    return CR


def original(CR, seleccion: str, unidad: str):
    """(sel, doc, filas, contrato, fuente) del ORIGINAL desde referencias/fam01, con las comprobaciones de original_autenticado."""
    s = CR.seleccion(seleccion)
    ks = [k for k, v in s.items() if v["unidad"] == unidad]
    need(len(ks) == 1, "UNIDAD_FUERA_DE_LA_SELECCION")
    sel = s[ks[0]]
    e = leer_json(REFS / "indice_originales.json")["unidades"][unidad]
    n = unidad.replace(":", "_")
    db = (REFS / "originales" / (n + ".json")).read_bytes()
    need(sha(db) == e["documento_sha256"], "DOCUMENTO_ORIGINAL_DISTINTO_DEL_INDICE")
    doc = CR.leer_bytes(db)
    fa = ((doc.get("filas") or {}).get("archivo") if isinstance(doc.get("filas"), dict) else None) or n + "_filas.json"
    fb = (REFS / "originales" / fa).read_bytes()
    need(sha(fb) == e["filas_sha256"], "FILAS_ORIGINALES_DISTINTAS_DEL_INDICE")
    need(not sel.get("entrega_original") or sel["entrega_original"] == e["paquete_entrega"], "ENTREGA_DISTINTA")
    need(not sel.get("contrato") or sel["contrato"] == e["contrato"], "CONTRATO_DISTINTO")
    fuente = {"entrega": e["paquete_entrega"], "doc": "referencias/fam01/originales/" + n + ".json", "filas": "referencias/fam01/originales/" + fa,
              "doc_sha256": sha(db), "filas_sha256": sha(fb)}
    return sel, doc, CR.leer_bytes(fb), e["contrato"], fuente


def _resumen_valores(doc, F):
    t = lambda n: (F.get(n) or [{}])[0]  # noqa: E731
    ce, cf = t("capture_ceiling_result"), t("confrontation_result")
    return {"estado_final": doc.get("estado_final"), "C_2": ce.get("C_2"), "numerical_error": ce.get("numerical_error"), "G": cf.get("G"),
            "K_comp_1": cf.get("K_comp_1"), "verdict": cf.get("verdict"), "computation_status": cf.get("computation_status"),
            "filas_por_tabla": {k: len(v) for k, v in sorted(F.items()) if isinstance(v, list)}}


def _identidad(CR, sel, do, Fo, dn, Fn):
    """Las diferencias de identidad que comparar_cargados evalúa en su capa 1 (misma lista de campos)."""
    cco, ccn = Fo["cell_context"][0], Fn["cell_context"][0]
    malos = [k for k in CR.IDENT if cco[k] != ccn[k]]
    fo, fn = Fo["frontier_context"][0], Fn["frontier_context"][0]
    malos += ["frontera." + k for k in fo if k not in ("frontier_id", "run_id") and fo[k] != fn.get(k)]
    ma, mb = Fo["lambda_pi_envelope"][0], Fn["lambda_pi_envelope"][0]
    malos += ["macro." + k for k in ("country_id", "omega_id", "eta_w_block", "macro_key_sha256", "national_state_sha256") if ma[k] != mb[k]]
    for k in ("extreme_id", "claim_id_hoja", "indice_contexto", "set_id", "omega_id", "pais", "diseno", "instrumento", "caso", "clave_estructural",
              "celda_externa", "estado_nacional", "macro"):
        if do["resultado"].get(k) != dn["resultado"].get(k):
            malos.append("resultado." + k)
    if do.get("id") != dn.get("id") or str(do.get("id")) != str(sel.get("unidad")):
        malos.append("id de la unidad")
    return malos


# Rótulo libre que el llamante pasa a Generador.celda (S6: "<lote>:<diseño>-<instrumento>-<país>"; histórico: prefijo del id).
# Se informa en su propio grupo; el comparador lo sigue contando como diferencia sin regla.
ETIQUETA_LLAMANTE = "documento: resultado.etiqueta distinto sin regla que lo cubra"


def registro_autenticado(CR, seleccion: str, reg: dict):
    """Las comprobaciones que el comparador v3-S6 (_comparar) hace al registro productivo: validador fijado por selección (y su histórico en
    R3), generado por registro_productivo instalado, dictamen íntegro y coherente. None si se acepta; si no, el motivo."""
    try:
        v_ = reg.get("validador") or {}
        vf = CR.VALIDADORES.get(seleccion)
        need(vf is not None and (v_.get("archivo"), v_.get("sha256")) == vf and sha((CR.A / vf[0]).read_bytes()) == vf[1],
             "registro productivo de un validador distinto del fijado")
        if vf is CR.VALIDADOR_R3:
            need((v_.get("historico") or {}).get("sha256") == CR.VALIDADOR_R3_HISTORICO[1]
                 and sha((CR.A / "herramientas/b" / CR.VALIDADOR_R3_HISTORICO[0]).read_bytes()) == CR.VALIDADOR_R3_HISTORICO[1],
                 "registro productivo R3 con un validador histórico distinto del fijado")
        g_ = reg.get("generado_por") or {}
        need(g_.get("modulo") == CR.GENERADOR_REGISTRO and g_.get("sha256") == sha((CR.A / CR.GENERADOR_REGISTRO).read_bytes())
             and g_.get("dictamen_sha256") == sha(canon(reg.get("verificacion"))), "registro productivo no generado por la ruta o con dictamen alterado")
        need(not any(isinstance(e, dict) and e.get("estado") in ESTADOS_VALIDADOS for e in (reg.get("unidades") or {}).values())
             or (reg.get("verificacion") or {}).get("cumple") is True, "registro productivo incoherente")
        need(isinstance(reg.get("unidades"), dict), "registro productivo sin unidades")
    except Fam01Error as e:
        return str(e)
    return None


# ------------------------------------------------------------------------------------------------ comparación LIMPIA
# Correcciones del comparador limpio (encargo de ajustes finales de FAM01). La regla histórica (regla_dr1.py, R-SUCESION-S6 v2) y sus
# resultados no se editan: la comparación histórica se sigue informando tal cual, aparte.
REGLA_E23 = ("E2E3-NIVEL-R1-v1 (corrección del comparador limpio). En las sustituciones E2 (R1 certificado: sufijo «; nivel configurado=6, "
             "efectivo=k») y E3 (R1 incompleto: «al nivel máximo 6» -> «; nivel configurado=6, efectivo=k») de DR-1, k debe ser EXACTAMENTE "
             "el nivel que run.Run.r1_level (idéntica en el núcleo histórico lima1738 y en S6) da para las entradas de la unidad: menú y "
             "barras tau_d_upper/tau_f_upper del tau_domain de su carga estructural, iguales en ambos lados, con r1_n, r1_geometry_tol y "
             "r1_max_level de la configuración fijada. Sustituye el rango 0<=k<=6 del texto de E2/E3, que no describe esa función (6<=k<=10). "
             "El resto del texto debe coincidir; método, estado, cobertura, cotas y valores de la evidencia se siguen comparando sin regla: "
             "una evidencia incompleta no pasa a certificada.")
HISTORIAL_OPERATIVO = ("tramo_anterior", "recuperacion_de")
REGLA_HISTORIAL = ("HIST-OPERATIVO-v1 (corrección del comparador limpio). Las claves de PRIMER NIVEL «tramo_anterior» (183 originales R2) y "
                   "«recuperacion_de» (12) del documento describen intentos históricos de la corrida (parada del tramo 1, recuperación tras el "
                   "límite de la suite): se comparan como procedencia operativa (como los OPERATIVOS del comparador) y sus diferencias se "
                   "informan aparte. Solo esas dos rutas de primer nivel; cualquier otra clave, también con el mismo nombre dentro de "
                   "«resultado» o de las filas, y el estado, la validación, las cifras y los veredictos de la corrida se comparan igual.")
HISTORIAL_ORIGINAL = tuple("documento: %s distinto" % k for k in HISTORIAL_OPERATIVO)


def nivel_r1_esperado(F) -> int | None:
    """k de run.Run.r1_level (la función autenticada del núcleo, sin copiarla) para las entradas de la unidad en sus filas: menú
    (instrument_j) y barras del tau_domain de la carga estructural de su única frontera; configuración R1 fijada (RunConfig: r1_n,
    r1_geometry_tol, r1_max_level, iguales en las 12 clases y en S6). None si la unidad no tiene una frontera única con esos datos."""
    import types
    from paper2b import run as RUN
    fr = F.get("frontier_context") or []
    if len(fr) != 1:
        return None
    dom, j = (fr[0].get("structural_key_payload") or {}).get("tau_domain"), fr[0].get("instrument_j")
    if not isinstance(dom, dict) or j not in ("d", "f", "df"):
        return None
    return int(RUN.Run.r1_level(types.SimpleNamespace(cfg=RUN.RunConfig()), j, float(dom["tau_d_upper"]), float(dom["tau_f_upper"])))


def niveles_r1_declarados(RD1, F) -> list:
    """(texto E2/E3, nivel configurado, nivel efectivo) de las definiciones de evidencia R1 de una unidad nueva."""
    out = []
    for r in F.get("numerical_evidence") or []:
        d = r.get("definition")
        m = (RD1.R1_SUF.search(d) or RD1.R1_INC_NUE.search(d)) if isinstance(d, str) else None
        if m:
            out.append({"forma": "E2 (certificado)" if d.startswith("R1 CERTIFICADO: ") else "E3 (incompleto)",
                        "configurado": int(m.group(1)), "efectivo": int(m.group(2)), "method_id": r.get("method_id"), "status": r.get("status")})
    return out


def _rd1_limpia(RD1, eq: dict, san: dict, f2: bool, k: int | None):
    """regla_dr1 para la comparación LIMPIA (no la sustituye):
    - condiciones(): DR-1 tal cual; si falla, sus motivos «técnica nueva no admitida» y «environment/tolerances distintos» se evalúan de
      nuevo sobre la técnica nueva con sus correspondencias comprobadas: SAN-RUTAS-v1 (contrato público -> histórico, solo si
      correspondencia_saneamiento lo comprueba) y, solo si f2, F2 (entorno equivalente -> huella de referencia). Cualquier
      otro motivo sigue rechazando; ninguna tolerancia cambia.
    - definicion_equivalente(): E1 sin cambios; E2/E3 con el nivel efectivo EXACTO de la unidad (REGLA_E23)."""
    import types
    adm = [x["technical"] for x in RD1.DATOS["nuevas"]]
    sg = san.get("G-NA-1") or {}

    def condiciones(Fo, Fn, do, dn, K):
        r = RD1.condiciones(Fo, Fn, do, dn, K)
        if r["ok"]:
            return dict(r, correspondencias={"aplicadas": [], "motivo": "DR-1 ya se cumple"})
        try:
            to = Fo["frontier_context"][0]["structural_key_payload"]["technical"]
            tn = Fn["frontier_context"][0]["structural_key_payload"]["technical"]
        except (KeyError, IndexError, TypeError):
            return dict(r, correspondencias={"aplicadas": [], "motivo": "estructura inesperada"})
        tm, aplicadas, cond = dict(tn), [], {}
        if sg.get("correspondencia_comprobada") is True and tn.get("contract_sha256") == sg.get("sha256_publico"):
            tm["contract_sha256"] = sg["sha256_historico"]
            aplicadas.append("SAN-RUTAS-v1: contrato público %s… = G-NA-1 histórico %s…" % (sg["sha256_publico"][:8], sg["sha256_historico"][:8]))
        if f2:
            cond = {"entorno_equivalente_F2": eq.get("equivalente") is True,
                    "huella_nueva_es_la_comprobada": tn.get("environment_sha256") == eq.get("environment_sha256"),
                    "huella_original_es_la_de_referencia": to.get("environment_sha256") == eq.get("referencia_environment_sha256")}
            if all(cond.values()):
                tm["environment_sha256"] = to["environment_sha256"]
                aplicadas.append("%s: entorno equivalente %s… -> %s…" % (REGLA_F2.split(" ")[0], tn["environment_sha256"][:8], to["environment_sha256"][:8]))
        cubiertos = []
        if "técnica nueva no admitida" in r["motivos"] and tm in adm:
            cubiertos.append("técnica nueva no admitida")
        if "environment/tolerances distintos" in r["motivos"] and all(to.get(x) == tm.get(x) for x in RD1.IGUALES):
            cubiertos.append("environment/tolerances distintos")
        mot = [m for m in r["motivos"] if m not in cubiertos]
        return {"ok": not mot, "motivos": mot, "correspondencias": {"aplicadas": aplicadas, "condiciones_f2": cond, "motivos_dr1_cubiertos": cubiertos}}

    def definicion_equivalente(a, b) -> bool:
        if not isinstance(a, str) or not isinstance(b, str):
            return False
        if a.startswith(RD1.G_ANT) and b.startswith(RD1.G_NUE) and a[len(RD1.G_ANT):] == b[len(RD1.G_NUE):]:
            return True                                                                   # E1 (sin cambios)
        m = RD1.R1_SUF.search(b)
        if a.startswith("R1 CERTIFICADO: ") and m and b[:m.start()] == a:                 # E2 con el nivel exacto
            return int(m.group(1)) == RD1.R1_MAX_LEVEL and k is not None and int(m.group(2)) == k
        ma, mb = RD1.R1_INC_ANT.search(a), RD1.R1_INC_NUE.search(b)
        if ma and mb:                                                                     # E3 con el nivel exacto
            return (int(ma.group(1)) == int(mb.group(1)) == RD1.R1_MAX_LEVEL and k is not None and int(mb.group(2)) == k
                    and a[:ma.start()] == b[:mb.start()] and a[ma.end():] == b[mb.end():])
        return False
    ns = types.SimpleNamespace(**{x: getattr(RD1, x) for x in dir(RD1) if not x.startswith("__")})
    ns.condiciones, ns.definicion_equivalente = condiciones, definicion_equivalente
    return ns


ACEPTADAS = ("aceptada", "aceptada_comparacion_limpia", "aceptada_comparacion_limpia_con_F2")


def comparar(seleccion: str, unidad: str, nueva: Path) -> dict:
    """Comparación de UNA unidad de una salida de fam01-unidad con su original. Estados separados: cálculo, validación productiva (registro
    autenticado y ligado a los bytes nativos), comparación HISTÓRICA (comparador v3-S6, reglas vigentes y selladas del plan, DR-1 tal cual),
    comparación LIMPIA (la misma con REGLA_E23, REGLA_HISTORIAL y la correspondencia SAN-RUTAS-v1 del contrato; entorno de DR-1 tal cual)
    y comparación LIMPIA con F2 (adoptada para FAM01). La reproducción dice con qué criterio se acepta. Sin registro productivo válido
    ninguna comparación puede quedar «aceptada»."""
    rastro = Rastro()
    CR = comparador()
    nueva = Path(nueva)
    ej = leer_json(nueva / "ejecucion.json")
    need(ej.get("seleccion") == seleccion, "SALIDA_DE_OTRA_SELECCION")
    if "por_unidad" in ej:
        need(unidad in ej["por_unidad"], "UNIDAD_FUERA_DE_LA_SALIDA")
        pu = ej["por_unidad"][unidad]
        rel_doc, rel_fil, rel_cmp, h_doc, h_fil = pu["documento"], pu["filas"], pu["comparable"]["documento"], pu["documento_sha256"], pu["filas_sha256"]
        reg_p, calculo, reg_h = nueva / ej["validacion"]["registro"], pu["calculo"], ej["validacion"].get("registro_sha256")
        run_id = pu.get("run_id", ej.get("run_id"))
        need(sha((nueva / rel_cmp).read_bytes()) == pu["comparable"]["sha256"], "COMPARABLE_ALTERADO")
    else:                                                  # salida de la versión anterior del adaptador (sin validación productiva)
        need(ej.get("unidad") == unidad, "UNIDAD_FUERA_DE_LA_SALIDA")
        rel_doc = rel_cmp = ej["documento"]
        rel_fil, h_doc, h_fil, reg_p, reg_h, run_id = ej["filas"], ej["documento_sha256"], ej["filas_sha256"], None, None, ej.get("run_id")
        calculo = "terminado" if ej.get("estado_generador") in ("ok", "no_aplicable") else "rechazado"
    db, fb, cb = (nueva / rel_doc).read_bytes(), (nueva / rel_fil).read_bytes(), (nueva / rel_cmp).read_bytes()
    need(sha(db) == h_doc and sha(fb) == h_fil, "SALIDA_ALTERADA")
    formato = None
    if rel_cmp != rel_doc:                                 # R2: el comparable debe derivar EXACTAMENTE del nativo por FMT_R2
        esperado = canon(documento_compatible_r2(json.loads(db), fb, clasificacion(unidad), Path(rel_fil).name)) + b"\n"
        formato = {"regla": FMT_R2.split(" ")[0], "comparable": rel_cmp, "nativo": rel_doc, "comparable_derivado_del_nativo": esperado == cb}
        need(esperado == cb, "COMPARABLE_NO_DERIVA_DEL_NATIVO")
    dn, Fn = CR.leer_bytes(cb), CR.leer_bytes(fb)
    registro, reg_mot = None, "la salida no tiene registro de validación productiva"
    if reg_p is not None and reg_p.is_file():
        rb = reg_p.read_bytes()
        reg = CR.leer_bytes(rb)
        # en lugar del inventario audit/entrega.json de la ruta administrativa (no reconstruida), el sha256 que ejecucion.json declara
        reg_mot = "registro productivo distinto del declarado en ejecucion.json" if sha(rb) != reg_h else registro_autenticado(CR, seleccion, reg)
        registro = reg if reg_mot is None else None
    bytes_nuevos = (sha(db), sha(fb))                      # la validación liga los bytes NATIVOS (el comparable es su representación)
    ent_p = nueva / "entorno.json"
    tn_env = ((Fn.get("frontier_context") or [{}])[0].get("structural_key_payload") or {}).get("technical", {}).get("environment_sha256")
    if ent_p.is_file():
        ent = leer_json(ent_p)
        eq = equivalencia_f2(ent["documento"], ent["records_sin_lanzadores"], tn_env)
        if ent.get("environment_sha256") != tn_env:
            eq = dict(eq, equivalente=False, motivos=eq["motivos"] + ["entorno.json de otra huella"])
    else:
        eq = {"regla": REGLA_F2.split(" ")[0], "equivalente": False, "motivos": ["la salida no registra su documento de entorno"],
              "environment_sha256": tn_env}
    sel, do, Fo, contrato_o, fuente = original(CR, seleccion, unidad)
    numerico = bool(sel.get("numerico", True))
    vo_det = CR.validar_detalle(do, Fo, contrato_o, numerico, "original")
    need(not vo_det["motivos"], "ORIGINAL_NO_VALIDO:%s" % vo_det["motivos"][:3])
    need(Fo["cell_context"][0]["cell_id"] == sel.get("cell_id_e12"), "E12_ORIGINAL_DISTINTO_DE_LA_SELECCION")
    vig = [r for r, v in CR.REGLAS.items() if v["estado"] == "vigente"]
    sell = leer_json(INST / REGLAS_SELLADAS[seleccion])
    selladas = []
    for r in sell["reglas"]:
        need(r["id"] in CR.REGLAS and CR.REGLAS[r["id"]]["estado"] == "propuesta" and r["sha256"] == CR.sha_regla(r["id"]), "REGLA_SELLADA_DISTINTA:" + r["id"])
        selladas.append(r["id"])
    N = CR.nucleo()
    out ={"seleccion": seleccion, "unidad": unidad, "fuente_original": fuente, "contrato_original": contrato_o,
           "nueva": {"documento": rel_doc, "documento_sha256": h_doc, "comparable": rel_cmp, "comparable_sha256": sha(cb), "filas_sha256": h_fil, "run_id": run_id},
           "formato": formato, "registro_productivo": {"aceptado": registro is not None, "motivo_rechazo": reg_mot if registro is None else None},
           "entorno_f2": eq, "f2_adopcion": ADOPCION_F2, "valores": {"original": _resumen_valores(do, Fo), "nueva": _resumen_valores(dn, Fn)},
           "reglas_selladas_del_plan": {"archivo": REGLAS_SELLADAS[seleccion], "estado": sell.get("estado"), "reglas": selladas}}
    out["valores"]["iguales"] = {k: out["valores"]["original"][k] == out["valores"]["nueva"][k] for k in out["valores"]["original"]}
    out["capa1_identidad_distinta"] = _identidad(CR, sel, do, Fo, dn, Fn)
    tecnicos = {campo for _, campo in CR.RD1.CAMPOS_REGLA} | {"clave_estructural"}
    rd1_hist, op_hist = CR.RD1, CR.OPERATIVOS
    k_o, k_n = nivel_r1_esperado(Fo), nivel_r1_esperado(Fn)
    k = k_n if k_n is not None and k_n == k_o else None
    out["nivel_r1"] = {"regla": REGLA_E23.split(" ")[0], "esperado_original": k_o, "esperado_nueva": k_n, "esperado": k,
                       "declarado_nueva": niveles_r1_declarados(rd1_hist, Fn)}
    san = CR._CACHE.get("saneamiento") or {}
    out["saneamiento"] = {c: {x: san[c][x] for x in ("sha256_historico", "sha256_publico", "correspondencia_comprobada")} for c in san}
    out["procedencia_operativa_del_original"] = {x: do[x] for x in HISTORIAL_OPERATIVO if x in do}
    for nombre, activas, f2 in (("historico_vigentes", vig, None), ("historico_vigentes_y_selladas", vig + selladas, None),
                                ("limpia", vig + selladas, False), ("limpia_f2", vig + selladas, True)):
        limpia = f2 is not None
        CR.RD1 = _rd1_limpia(rd1_hist, eq, san, f2, k) if limpia else rd1_hist
        CR.OPERATIVOS = op_hist + HISTORIAL_OPERATIVO if limpia else op_hist
        try:
            r = CR.comparar_cargados(sel, do, Fo, contrato_o, fuente, dn, Fn, run_id, activas, registro=registro, bytes_nuevos=bytes_nuevos, vo_det=vo_det)
            mo, mn = CR.mapa_ids(Fo, "original"), CR.mapa_ids(Fn, "nueva")
            ctx = CR._ctx_reglas(Fo, Fn)
            dr1 = CR.RD1.condiciones(Fo, Fn, do, dn, N["K"]) if "R-SUCESION-S6" in activas else {"ok": False, "motivos": ["no sellada"]}
            ctx["_DR1"] = dr1
            ex_t, ci_t, cu_t, nuevas = CR.comparar_tablas(Fo, Fn, mo, mn, contrato_o, ctx, activas, N["C"])
            ex_d, ci_d, cu_d, op = CR.comparar_doc(do, dn, mo, mn, contrato_o, ctx, activas, N["CP"])
        finally:
            CR.RD1, CR.OPERATIVOS = rd1_hist, op_hist
        sin = ci_t + ci_d
        grupo = {"identidad_tecnica_DR1": [m for m in sin if any(("." + f) in m or (" " + f) in m or m.startswith(f) for f in tecnicos)],
                 "formato_documento": [m for m in ci_d if m.startswith("documento: ") and not m.startswith("documento: resultado.") and m not in HISTORIAL_ORIGINAL],
                 "etiqueta_del_llamante": [m for m in sin if m == ETIQUETA_LLAMANTE],
                 "historial_de_ejecucion_del_original": [m for m in sin if m in HISTORIAL_ORIGINAL]}
        grupo["valores_y_resto"] = [m for m in sin if not any(m in g for g in grupo.values())]
        out[nombre] = {"reglas_activas": activas + ([REGLA_E23.split(" ")[0], REGLA_HISTORIAL.split(" ")[0], REGLA_SAN.split(" ")[0] + " (contrato)"]
                                                    if limpia else []) + ([REGLA_F2.split(" ")[0] + " (adoptada para FAM01)"] if f2 else []),
                       "dictamen_comparador": r.get("dictamen"),
                       "motivos_comparador": r.get("motivos"), "validacion": r.get("validacion"), "dr1": dr1,
                       "diagnostico": {"tablas_con_diferencias": sorted(ex_t), "doc_con_diferencias": ex_d, "reglas_aplicadas": cu_t + cu_d,
                                       "operativos_distintos": op, "procedencia_operativa_distinta": [x for x in op if x in HISTORIAL_OPERATIVO],
                                       "evidencia_nueva": nuevas, "sin_regla_por_grupo": grupo, "sin_regla_total": len(sin)}}
    prod = (((out["historico_vigentes_y_selladas"].get("validacion") or {}).get("nueva") or {}).get("productiva"))
    h, lim, c = (out[x]["dictamen_comparador"] for x in ("historico_vigentes_y_selladas", "limpia", "limpia_f2"))
    out["estado"] = {"calculo": calculo, "validacion_productiva": prod or "invalida", "comparacion_historica": h, "comparacion_limpia": lim,
                     "comparacion_limpia_f2": c,
                     "reproduccion": ("aceptada" if h == "aceptada" else "aceptada_comparacion_limpia" if lim == "aceptada"
                                      else "aceptada_comparacion_limpia_con_F2" if c == "aceptada"
                                      else "pendiente_validacion" if "pendiente_validacion_productiva" in (h, lim, c) else "no_aceptada")}
    need(out["estado"]["reproduccion"] not in ACEPTADAS or prod == "verificada", "ACEPTADA_SIN_VALIDACION")
    out["archivos_leidos"] = rastro.informe()
    return out


# ================================================================================================ NA (documental)
def comprobar_na(unidad: str) -> dict:
    """Reproducir una NA = comprobar su clasificación y su fundamento (DEC-S6R36-3), sin cálculo: pertenencia y clase en la lista y
    el marco, documento y filas del original (estado, causa, disponibilidad), validación propia del original por el comparador v3-S6
    y la fila del caso D4 que la fundamenta."""
    CR = comparador()
    u = unidad_de_lista("R3", unidad)
    M = {x["fila"]: x for x in leer_json(DATOS / MARCO[0], MARCO[1])["celdas"]}
    d = definicion(unidad)
    sel, do, Fo, contrato_o, fuente = original(CR, "R3", unidad)
    ok = []
    chk = lambda n, v: ok.append((n, bool(v)))  # noqa: E731
    chk("lista R3: NA (numerico = false)", u["numerico"] is False)
    chk("marco: misma celda y NA", unidad in M and M[unidad]["numerico"] is False and M[unidad]["cell_id_e12"] == u["cell_id_e12"])
    chk("definición vinculada del tipo «definicion»", d["tipo"] == "definicion" and d["definicion"]["familia"] == u["familia"])
    cc, ce, cf = Fo["cell_context"][0], Fo["capture_ceiling_result"][0], Fo["confrontation_result"][0]
    chk("original: estado_final no_aplicable", do.get("estado_final") == "no_aplicable" and (do.get("resultado") or {}).get("estado") == "no_aplicable")
    chk("original: techo y confrontación not_applicable por INSTRUMENT_NOT_AVAILABLE",
        all(x.get("computation_status") == "not_applicable" and x.get("reason_code") == "INSTRUMENT_NOT_AVAILABLE" for x in (ce, cf)))
    chk("original: instrumento no disponible en contexto y techo", cc.get("instrument_available") is False and ce.get("instrument_available") is False)
    chk("original: sin valores numéricos (C_2, G, K_comp_1 nulos)", ce.get("C_2") is None and cf.get("G") is None and cf.get("K_comp_1") is None)
    vd = CR.validar_detalle(do, Fo, contrato_o, False, "original")
    chk("validación propia del comparador v3-S6 (contrato del original)", not vd["motivos"])
    mcm = [r for r in csv_filas(RAIZ / "fase2_datos/d4_disponibilidad/versions/cb5446f861610c767c7200a2a46c637c9c46c64ecb99fef05a132ef3f8534006/model_case_map.csv")
           if (r.get("country_id"), r.get("model_menu"), r.get("case_id")) == (cc.get("country_id"), "j_%s" % cc.get("instrument_j"), cc.get("availability_case_id"))]
    chk("mapa D4: una fila para (país, menú, caso) con el mismo uso que el original",
        len(mcm) == 1 and mcm[0].get("quantitative_use") == cc.get("availability_source"))
    g = [r for r in Fo.get("convergence_result", []) if str(r.get("quantity_id", "")).startswith("G:")]
    return {"unidad": unidad, "cumple": all(v for _, v in ok), "comprobaciones": dict(ok), "fuente_original": fuente,
            "fundamento": {"availability_case_id": cc.get("availability_case_id"), "availability_source": cc.get("availability_source"),
                           "instrumento": cc.get("instrument_j"), "pais": cc.get("country_id"), "motivo": ce.get("reason_code"),
                           "filas_del_caso_en_el_mapa_D4": mcm,
                           "completitud_original": {k: (do.get("resultado") or {}).get("completitud", {}).get(k) for k in ("estado", "motivo_celda")},
                           "fila_G_de_convergencia_original": [{k: r.get(k) for k in ("status", "method_id", "coverage_complete")} for r in g]},
            "validacion_original": {"motivos": vd["motivos"], "no_aplicables": vd["no_aplicables"]}}


def csv_filas(p: Path):
    import csv
    import io
    return list(csv.DictReader(io.StringIO(Path(p).read_bytes().decode("utf-8"))))


# ================================================================================================ carga (traslado, sin ciencia)
def comprobar_carga() -> dict:
    """Comprobación de carga SIN cálculo científico: archivos de fuentes_fam01.json presentes con su sha256, contexto S6 construido
    (técnicas frente a la tupla S6 admitida), módulos del productor y del comparador cargados, y la ruta de datos nacionales que usa la
    clave condicional (build_bundle + CA2Validator por preregistro), que lee la recepción nacional."""
    rel = leer_json(BASE / "fuentes_fam01.json")
    malos = [r["archivo"] for r in rel["archivos"] if not (BASE / r["archivo"]).is_file() or sha((BASE / r["archivo"]).read_bytes()) != r["sha256"]]
    san = correspondencia_saneamiento()
    preparar()
    t0 = time.time()
    ctx = Contexto(parametros())
    adm = leer_json(INST / "datos/paso4/dr1_tecnicas_admitidas.json")["nuevas"]
    GC, GE = modulos()
    U, P2, RP = modulos_ruta()                                   # ejecutor, Verificador S6 (validador R2) y generador del registro
    PR = cargar("productor_r3", INST / "herramientas/b/productor_r3.py")
    PR.ProductorR3(ctx, None, GC, RAIZ)                          # comprueba los sha256 fijados de regla_b_v2 y e12_celda
    cargar("validador_r3", INST / "herramientas/b/validador_r3.py")
    CR = comparador()
    validadores = {s: {"archivo": v[0], "sha256_fijado": v[1], "sha256_copia": sha((CR.A / v[0]).read_bytes())} for s, v in CR.VALIDADORES.items()}
    from herramientas.ca2_bundles.construir_bundles import build_bundle
    from herramientas.nacionales.adaptadores_ca2 import contracts as national_contracts
    from herramientas.s3.validadores.ca2 import CA2Validator
    prov = ctx.prov
    idx = json.loads(prov._artifact(prov.idx_dep["path"], prov.idx_dep["sha256"]))
    nc = national_contracts()
    bundles = []
    for entry in prov.registry["entries"]:
        cx = {k: [dict(x, context=None) for x in idx["contexts"][k]] for k in entry["country_set"]}
        _, adapters = build_bundle(entry, nc, cx, f"fase2_datos/recepcion_nacional/versions/{idx['reception_tree_sha256']}/")
        CA2Validator(nc, RAIZ, adapters)
        bundles.append(entry["preregistration_id"])
    return {"archivos_fuentes_fam01": len(rel["archivos"]), "archivos_ausentes_o_distintos": malos,
            "tecnicas": ctx.technical, "tecnica_distinta_de_la_tupla_S6_admitida": sorted(k for k in adm[0]["technical"] if adm[0]["technical"][k] != ctx.technical.get(k)),
            "entorno": {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"),
                        "f2": equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"])},
            "saneamiento": san,
            "validadores_fijados": validadores, "preregistros_con_datos_nacionales_cargados": bundles, "segundos_contexto_y_carga": round(time.time() - t0, 2),
            "dependencias_fuera_de_la_biblioteca_estandar": dependencias_cargadas(),
            "cumple": not malos and all(v["sha256_fijado"] == v["sha256_copia"] for v in validadores.values())
                      and all(v["correspondencia_comprobada"] for v in san.values())}
