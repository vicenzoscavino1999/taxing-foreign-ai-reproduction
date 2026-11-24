"""CORRECCIÓN COTAS Y PASO 4 3.7 NO OFICIAL (copia sin cambios de lógica de extremos_df_d_3_7_2026-10-05_lima0738, antes cierre_candidato_3_7_2026-10-04_lima2103, antes resolucion_3_7_2026-10-04_lima1941, antes consolidacion_3_7_2026-10-04, antes testigos_cobertura_3_7_2026-10-04/codigo/demo/nucleo_v.py, que copiaba certificacion_3_7_2026-10-04/codigo/demo/nucleo_v.py; antes:
copia de verificador_rendimiento_3_7_2026-10-04/codigo/demo/nucleo_v.py, con
la opción de inicialización autenticada reutilizable de init_autenticada.py; copia a su vez de obstaculos_3_7_2026-10-03/codigo/demo/nucleo_v.py): entradas autenticadas (copia de viabilidad_alternativa_2026-10-03/codigo/demo/nucleo_v.py, a su vez
adaptado de codigo/pilotos/nucleo.py de B3-6).

Cambios respecto del núcleo de los pilotos (todo lo demás es idéntico):
- área, rótulo y clase de corrida propios ('national_viability_demo'); escribe SOLO en esta área;
- autorización = encargo literal de esta ronda (autorizacion/ENCARGO_VIABILIDAD.txt, hash comprobado con procedencia.json);
- no construye celdas, inversiones ni geometrías: solo da acceso a Run (afirmaciones, contextos y proveedor certificado).
Garantías conservadas: autoridad REAL S5 verificada; banderas b_official_run/freeze_run/official_export en false o se niega;
D7 autenticado (árbol fijado), complete y ready_for_b; entorno oficial conforme; grilla y mapa D4 por hash.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sys
import time
from dataclasses import replace
from pathlib import Path

AREA = Path(__file__).resolve().parents[2]
ROOT = AREA.parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
sys.dont_write_bytecode = True

from herramientas.bloque2 import entorno as E  # noqa: E402
E.set_runtime_conventions()
from herramientas.bloque2 import autoridad as A  # noqa: E402
from herramientas.bloque2 import familias as FAM  # noqa: E402
from herramientas.bloque2 import perfiles as P  # noqa: E402
from herramientas.b import ejecutar_b as EB  # noqa: E402
from herramientas.b import nacional as NAT  # noqa: E402
from herramientas.s3.validadores.core import Contracts  # noqa: E402
from paper2b import claims as CL  # noqa: E402
from paper2b import external as X  # noqa: E402
from paper2b import keys as K  # noqa: E402
from paper2b import run as RUN  # noqa: E402
from paper2b.d7view import D7View  # noqa: E402

ETIQUETA = "CORRECCION COTAS PASO4 3.7 NO OFICIAL"
RUN_CLASS = "national_bounds_fix_step4_3_7"
POL = "d2694d8f76eb26ac7133923774a5f2808ad601d9203417bd4ea56fffdaaa9ab1"
REC = "5312b9f9322a9cc6bbd6a440760275f72d0fea25fd2771d5969af50cadbe53d2"
AUT = "Vicenzo Scavino"
S5_PKG = "93c625a40772f3d278183cd738f454cc47345c1a52e71dc9f47342352d2aba09"
D7T = "10a0bd5bb8ea48d54d1bd0916b072afcf8cd5a4eed9c5ec16a90a728f021b739"
AUTORIZACION = AREA / "autorizacion/ENCARGO_3_7_CORRECCION_COTAS_PASO4.txt"
CODE_GLOBS = ("tmp/correccion_cotas_paso4_3_7_2026-10-05_lima1259/codigo/demo/*.py",)
# inicialización reutilizable: activa si se pasa `init_dir` o la variable de entorno MEJORAS_INIT_DIR (ruta dentro del área)
INIT_ENV = "MEJORAS_INIT_DIR"


class DemoError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise DemoError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return K.canon(obj)


def write_json_atomic(path: Path, obj) -> str:
    path = Path(path)
    need(path.resolve().is_relative_to(AREA.resolve()), "DEMO_WRITE_OUTSIDE_AREA:" + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True, default=str) + "\n").encode("utf-8")
    tmp = path.with_name(path.name + ".tmp-%d" % os.getpid())
    tmp.write_bytes(raw)
    os.replace(tmp, path)
    return sha(raw)


class Contexto:
    def __init__(self, init_dir=None):
        t0 = time.time()
        init_dir = init_dir or os.environ.get(INIT_ENV)
        self.init_info = {"modo": "directa (verificación completa, sin reutilización)"}
        if init_dir:
            # MISMA función from_s5; solo su llamada interna a verify_products pasa por la reutilización autenticada
            from herramientas.congelamiento import s5_publicador as S5P
            from . import init_autenticada as IA
            init_dir = Path(init_dir) if Path(init_dir).is_absolute() else AREA / init_dir
            need(init_dir.resolve().is_relative_to(AREA.resolve()), "INIT_FUERA_DEL_AREA")
            orig = S5P.verify_products

            def vp_reutilizable(root, pin, rh, author, **kw):
                need(not kw, "INIT_ARGUMENTOS_EXTRA")
                res, info = IA.con_reutilizacion(Path(root), init_dir, lambda r, *a: orig(r, *a), [pin, rh, author],
                                                 etiqueta=ETIQUETA)
                self.init_info = info
                return res
            S5P.verify_products = vp_reutilizable
            try:
                self.authority = A.from_s5(ROOT, POL, REC, AUT)
            finally:
                S5P.verify_products = orig
        else:
            self.authority = A.from_s5(ROOT, POL, REC, AUT)
        self.init_seconds = round(time.time() - t0, 2)
        a = self.authority
        need(not a.fictitious and a.kind == "S5" and a.package_sha256 == S5_PKG, "DEMO_REQUIRES_REAL_S5")
        for flag in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized"):
            need(a.scope.get(flag) is False, "DEMO_SCOPE_CHANGED:" + flag)
        proc = json.loads((AREA / "autorizacion/procedencia.json").read_bytes())
        self.autorizacion_sha256 = sha(AUTORIZACION.read_bytes())
        need(proc["sha256"] == self.autorizacion_sha256 and all(proc["citas_obligatorias_presentes"].values()),
             "DEMO_AUTHORIZATION_HASH")
        self.C = Contracts.load(ROOT / a.contract_root, a.contract_sha256)
        self.d7_dir = ROOT / "fase2_datos/d7_calibracion/versions" / D7T
        self.d7info = FAM.verify_version(self.d7_dir, "D7", expected_tree=D7T)
        need(self.d7info["manifest"]["authority_package_sha256"] == S5_PKG, "DEMO_D7_NOT_UNDER_S5")
        self.view = D7View.load(self.C, self.d7_dir)
        need(self.view.phase["phase_status"] == "complete" and self.view.phase["ready_for_b"] is True, "DEMO_D7_NOT_READY")
        probe = NAT.Providers(ROOT, self.C, self.view, protocol_sha256="0" * 64, technical={})
        set_index = {}
        for sid, (entry, ed, block) in probe.set_case.items():
            set_index.setdefault(entry["preregistration_id"], {}).setdefault(ed, {})[block] = sid
        self.set_index = set_index
        self.cfg = EB.final_config(replace(RUN.RunConfig(), run_class=RUN_CLASS), set_index, RUN_CLASS)
        self.env_doc = EB.environment_document(ROOT, P.official(ROOT))
        need(self.env_doc["conforms"], "DEMO_ENVIRONMENT_NOT_APPROVED:" + ";".join(self.env_doc["mismatches"][:3]))
        ddeps = {d["role"]: d for d in self.d7info["manifest"]["input_dependencies"]}
        gdep, mdep = ddeps["external_grid"], ddeps["d4_model_case_map"]
        grid_raw = (ROOT / gdep["path"]).read_bytes()
        need(sha(grid_raw) == gdep["sha256"], "DEMO_GRID_HASH")
        mraw = (ROOT / mdep["path"]).read_bytes()
        need(sha(mraw) == mdep["sha256"], "DEMO_D4_MAP_HASH")
        self.mcm = list(csv.DictReader(io.StringIO(mraw.decode("utf-8"))))
        need(sha((ROOT / (a.contract_root + "contratos/contract_manifest.json")).read_bytes()) == a.contract_sha256, "DEMO_CONTRACT")
        theory_path = "fase4_teoria/baseline_model_v2_2.md"
        proto_path = a.contract_root + "contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md"
        self.theory = ("v2_2", theory_path, sha((ROOT / theory_path).read_bytes()))
        self.protocol = ("S2", proto_path, sha((ROOT / proto_path).read_bytes()))
        code = EB.code_manifest(ROOT)
        demo_code = EB.code_manifest(ROOT, CODE_GLOBS)
        docs = {"configuration": self.cfg.as_dict(), "tolerances": EB.TOLERANCES, "method": EB.method_manifest(self.cfg),
                "code": code, "environment": self.env_doc}
        self.technical = {role + "_sha256": sha(canon(obj) + b"\n") for role, obj in sorted(docs.items())}
        self.technical["contract_sha256"] = a.contract_sha256
        self.technical = dict(sorted(self.technical.items()))
        self.prov = NAT.Providers(ROOT, self.C, self.view, protocol_sha256=self.protocol[2], technical=self.technical)
        ev = {r["evidence_id"]: r for r in self.view.tables["source_evidence"]}
        d7m = (self.d7_dir / "d7_manifest.json").resolve().relative_to(ROOT.resolve()).as_posix()
        grid_dep = {"role": "external_grid", "manifest_path": d7m, "manifest_sha256": self.d7info["manifest_sha256"],
                    "artifact_path": gdep["path"], "artifact_sha256": gdep["sha256"], "record_pk": {"table": "grid"}}
        self.inp = RUN.RunInputs(contracts=self.C, d7=self.view, registry=self.prov.registry, grid_cells=X.read_grid(grid_raw),
                                 grid_sha256=gdep["sha256"], grid_dependency=grid_dep, model_case_map=self.mcm,
                                 availability_matrix_hash=ev["EV.D4.MATRIX"]["payload_sha256"], national=self.prov.national,
                                 conditional_key=self.prov.conditional_key, technical=self.technical, theory=self.theory,
                                 protocol=self.protocol, manifest_hash=a.manifest_sha256, contract_sha256=a.contract_sha256,
                                 producer_sha256=sha(Path(__file__).read_bytes()),
                                 environment_manifest_sha256=self.technical["environment_sha256"],
                                 algorithm_config_sha256=self.technical["configuration_sha256"],
                                 crosswalk_sha256=ev["EV.CROSSWALK"]["payload_sha256"], dme_gai=0.0, set_index=set_index,
                                 created_at="", tolerances=dict(EB.TOLERANCES))
        self.claims = CL.derive(self.prov.registry, self.mcm, set_index)
        self.identity = {"etiqueta": ETIQUETA, "run_class": RUN_CLASS, "s5": S5_PKG, "d7": D7T, "politica": POL, "recibo": REC,
                         "grilla_sha256": gdep["sha256"], "mapa_d4_sha256": mdep["sha256"], "registro_sha256": sha(canon(self.prov.registry)),
                         "contrato_sha256": a.contract_sha256, "tecnicas": self.technical, "codigo_demo_sha256": sha(canon(demo_code)),
                         "huella_entorno_sha256": self.env_doc["fingerprint_sha256"], "autorizacion_sha256": self.autorizacion_sha256}
        self.identity_sha256 = sha(canon(self.identity))
        self.setup_seconds = round(time.time() - t0, 2)

    def run(self, set_id: str, unit_id: str) -> RUN.Run:
        r = RUN.Run(self.inp, self.cfg, unit={"unit_id": unit_id, "set_id": set_id, "prefix": {p: 0 for p in RUN.STRUCT}})
        need(r.model.kind == "modelo_teorico_v2_2" and r.model.certified, "DEMO_PROVIDER_NOT_CERTIFIED")
        return r


def axes_nodes(ctx: Contexto, set_id: str) -> dict:
    from paper2b.supports import level_nodes
    return {pid: level_nodes(ctx.view.nodes(set_id, pid), ctx.view.support(set_id, pid)["scale"], ctx.cfg.level) for pid in RUN.STRUCT}
