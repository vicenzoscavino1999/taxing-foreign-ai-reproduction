"""AUTORIDAD DESDE S6 y RunInputs del paquete por selección (paso 4, NO OFICIAL; candidato derivado de contexto_s5.py con reemplazos
exactos: misma lógica, autoridad S6 viva con ANCLA externa y D7 bajo S6 en la zona salidas_s6). Port PARAMETRIZADO de codigo/demo/nucleo_v.Contexto (misma lógica): ninguna ruta se deduce de la
ubicación de este archivo; la raíz del proyecto, la política, el recibo, el autor, el paquete S5, el árbol D7, la clase
y la etiqueta de la corrida, el encargo y su procedencia, y los patrones del código del productor se pasan
EXPLÍCITAMENTE. Es relocalizable: puede vivir en herramientas/b del proyecto.

Garantías: autoridad REAL S6 verificada (A.from_s6 con lanzamiento_sha256 = ancla externa; sin ancla se niega); banderas
b_official_run/freeze_run/official_export en False o se niega; encargo con hash igual a su procedencia y citas obligatorias
presentes; D7 autenticado (directorio en salidas_s6 y árbol fijados), complete y ready_for_b, bajo el MISMO paquete S6 (la
política S6 decide d7 = reconstruir_bajo_s6: un D7 bajo S5 se rechaza); entorno oficial conforme; grilla y mapa D4 por hash; contrato por hash.
No activa official(), no emite freeze-run y no escribe nada.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from dataclasses import replace
from pathlib import Path

BANDERAS = ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")


class ContextoError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise ContextoError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class ContextoS6:
    """Mismo interfaz que nucleo_v.Contexto (authority, C, view, cfg, inp, prov, claims, technical, identity, run())."""

    def __init__(self, root, *, politica, recibo, autor, s6_package, ancla, d7_dir, d7_tree, run_class, etiqueta, encargo, procedencia, code_globs, productor=None,
                 codigo_productor=None):
        from herramientas.bloque2 import autoridad as A
        from herramientas.bloque2 import entorno as E
        from herramientas.bloque2 import familias as FAM
        from herramientas.bloque2 import perfiles as P
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
        t0 = time.time()
        ROOT = Path(root)
        need("NO OFICIAL" in etiqueta, "ETIQUETA_OFICIAL")
        self.init_info = {"modo": "directa (verificación completa, sin reutilización)"}
        need(isinstance(ancla, str) and len(ancla) == 64, "ANCLA_S6_REQUERIDA")
        self.authority = a = A.from_s6(ROOT, politica, recibo, autor, lanzamiento_sha256=ancla)
        self.init_seconds = round(time.time() - t0, 2)
        need(not a.fictitious and a.kind == "S6" and a.package_sha256 == s6_package, "REQUIRES_REAL_S6")
        for flag in BANDERAS:
            need(a.scope.get(flag) is False, "SCOPE_CHANGED:" + flag)
        proc = json.loads(Path(procedencia).read_bytes())
        self.autorizacion_sha256 = sha(Path(encargo).read_bytes())
        need(proc["sha256"] == self.autorizacion_sha256 and all(proc["citas_obligatorias_presentes"].values()), "AUTHORIZATION_HASH")
        self.C = Contracts.load(ROOT / a.contract_root, a.contract_sha256)
        need(isinstance(d7_dir, str) and d7_dir.startswith("salidas_s6/") and ".." not in Path(d7_dir).parts, "D7_FUERA_DE_SALIDAS_S6")
        self.d7_dir = ROOT / d7_dir / "versions" / d7_tree
        self.d7info = FAM.verify_version(self.d7_dir, "D7", expected_tree=d7_tree)
        need(self.d7info["manifest"]["authority_package_sha256"] == s6_package, "D7_NOT_UNDER_S6")
        self.view = D7View.load(self.C, self.d7_dir)
        need(self.view.phase["phase_status"] == "complete" and self.view.phase["ready_for_b"] is True, "D7_NOT_READY")
        probe = NAT.Providers(ROOT, self.C, self.view, protocol_sha256="0" * 64, technical={})
        set_index = {}
        for sid, (entry, ed, block) in probe.set_case.items():
            set_index.setdefault(entry["preregistration_id"], {}).setdefault(ed, {})[block] = sid
        self.set_index = set_index
        self.cfg = EB.final_config(replace(RUN.RunConfig(), run_class=run_class), set_index, run_class)
        self.env_doc = EB.environment_document(ROOT, P.official(ROOT, anclas=a.anclas_externas or None))   # S6: el perfil exige el ancla
        need(self.env_doc["conforms"], "ENVIRONMENT_NOT_APPROVED:" + ";".join(self.env_doc["mismatches"][:3]))
        ddeps = {d["role"]: d for d in self.d7info["manifest"]["input_dependencies"]}
        gdep, mdep = ddeps["external_grid"], ddeps["d4_model_case_map"]
        grid_raw = (ROOT / gdep["path"]).read_bytes()
        need(sha(grid_raw) == gdep["sha256"], "GRID_HASH")
        mraw = (ROOT / mdep["path"]).read_bytes()
        need(sha(mraw) == mdep["sha256"], "D4_MAP_HASH")
        self.mcm = list(csv.DictReader(io.StringIO(mraw.decode("utf-8"))))
        need(sha((ROOT / (a.contract_root + "contratos/contract_manifest.json")).read_bytes()) == a.contract_sha256, "CONTRACT")
        theory_path = "fase4_teoria/baseline_model_v2_2.md"
        proto_path = a.contract_root + "contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md"
        self.theory = ("v2_2", theory_path, sha((ROOT / theory_path).read_bytes()))
        self.protocol = ("S2", proto_path, sha((ROOT / proto_path).read_bytes()))
        code = EB.code_manifest(ROOT)
        # código del productor: manifiesto por CONTENIDO de la estructura candidata (invariante a la relocalización) si se
        # da; si no, por patrones de ruta (comportamiento anterior)
        demo_code = codigo_productor if codigo_productor is not None else EB.code_manifest(ROOT, tuple(code_globs))
        docs = {"configuration": self.cfg.as_dict(), "tolerances": EB.TOLERANCES, "method": EB.method_manifest(self.cfg), "code": code,
                "environment": self.env_doc}
        self.technical = {role + "_sha256": sha(K.canon(obj) + b"\n") for role, obj in sorted(docs.items())}
        self.technical["contract_sha256"] = a.contract_sha256
        self.technical = dict(sorted(self.technical.items()))
        self.prov = NAT.Providers(ROOT, self.C, self.view, protocol_sha256=self.protocol[2], technical=self.technical)
        ev = {r["evidence_id"]: r for r in self.view.tables["source_evidence"]}
        d7m = (self.d7_dir / "d7_manifest.json").resolve().relative_to(ROOT.resolve()).as_posix()
        grid_dep = {"role": "external_grid", "manifest_path": d7m, "manifest_sha256": self.d7info["manifest_sha256"],
                    "artifact_path": gdep["path"], "artifact_sha256": gdep["sha256"], "record_pk": {"table": "grid"}}
        productor = Path(productor) if productor is not None else Path(__file__)
        self.inp = RUN.RunInputs(contracts=self.C, d7=self.view, registry=self.prov.registry, grid_cells=X.read_grid(grid_raw),
                                 grid_sha256=gdep["sha256"], grid_dependency=grid_dep, model_case_map=self.mcm,
                                 availability_matrix_hash=ev["EV.D4.MATRIX"]["payload_sha256"], national=self.prov.national,
                                 conditional_key=self.prov.conditional_key, technical=self.technical, theory=self.theory,
                                 protocol=self.protocol, manifest_hash=a.manifest_sha256, contract_sha256=a.contract_sha256,
                                 producer_sha256=sha(productor.read_bytes()),
                                 environment_manifest_sha256=self.technical["environment_sha256"],
                                 algorithm_config_sha256=self.technical["configuration_sha256"],
                                 crosswalk_sha256=ev["EV.CROSSWALK"]["payload_sha256"], dme_gai=0.0, set_index=set_index,
                                 created_at="", tolerances=dict(EB.TOLERANCES))
        self.claims = CL.derive(self.prov.registry, self.mcm, set_index)
        self.identity = {"etiqueta": etiqueta, "run_class": run_class, "s6": s6_package, "ancla": ancla, "d7": d7_tree, "politica": politica, "recibo": recibo,
                         "grilla_sha256": gdep["sha256"], "mapa_d4_sha256": mdep["sha256"], "registro_sha256": sha(K.canon(self.prov.registry)),
                         "contrato_sha256": a.contract_sha256, "tecnicas": self.technical, "codigo_demo_sha256": sha(K.canon(demo_code)),
                         "huella_entorno_sha256": self.env_doc["fingerprint_sha256"], "autorizacion_sha256": self.autorizacion_sha256}
        self.identity_sha256 = sha(K.canon(self.identity))
        self.setup_seconds = round(time.time() - t0, 2)

    def run(self, set_id: str, unit_id: str):
        r = self.RUN.Run(self.inp, self.cfg, unit={"unit_id": unit_id, "set_id": set_id, "prefix": {p: 0 for p in self.RUN.STRUCT}})
        need(r.model.kind == "modelo_teorico_v2_2" and r.model.certified, "PROVIDER_NOT_CERTIFIED")
        return r
