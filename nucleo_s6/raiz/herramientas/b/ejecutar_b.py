"""Paquete B (bloque 2): ejecución contratada, entradas técnicas autenticadas y familia versionada B.

Clases de corrida (run_manifest.run_class):
- synthetic_validation: mundo sintético (herramientas/bloque2/sintetico.py) o D7 sintético; nunca datos nacionales;
  exige autoridad con b_synthetic_validation_authorized (FICTICIA en pruebas). No habilita exportación oficial.
- official: exige autoridad REAL con b_official_run_authorized y freeze_run_authorized, un freeze-run sellado que
  coincide byte a byte con la selección ejecutada (herramientas/bloque2/freeze_run.py: autoridad, D7, D8_pre PASS,
  código, contrato, configuración, entorno aprobado RE-03 + lock, casos y fuentes). En el bloque 2 SIEMPRE se rechaza.
- trial_frozen: la MISMA ruta (freeze-run verificado, D8_pre PASS) bajo perfil de ENSAYO (raíz aislada, autoridad
  ficticia, mundo sintético). Existe para demostrar la ruta válida con fixtures; ningún consumidor oficial la acepta.
Entradas técnicas (CLAVES 'technical'): contrato, código, método, tolerancias, configuración y entorno se escriben
como archivos direccionados por contenido y se referencian por rol en b_manifest.input_dependencies; las claves
estructurales/macro llevan sus seis huellas (Contracts.technical las resuelve por rol y bytes).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from paper2b import external as X  # noqa: E402
from paper2b import keys as K  # noqa: E402
from paper2b import run as RUN  # noqa: E402
from paper2b import tables as T  # noqa: E402
from paper2b import rules as RULES  # noqa: E402
from paper2b.d7view import D7View  # noqa: E402
from paper2b.supremum import SupConfig  # noqa: E402
from herramientas.bloque2 import autoridad as A  # noqa: E402
from herramientas.bloque2 import familias as FAM  # noqa: E402

B_TABLES = ["omega", "omega_values", "cell_context", "frontier_context", "frontier_result", "capture_ceiling_result",
            "sup_witness", "lambda_pi_envelope", "confrontation_result", "inversion_result", "inversion_targets", "r1_summary",
            "r1_components", "r1_vertices", "r1_edges", "r1_rejected_crossings", "r2_sections", "r2_roots", "claims",
            "support_breakdown_result", "breakdown_witnesses", "external_requirement_sensitivity_result",
            "convergence_result", "computation_coverage", "witness_sets", "scalar_inversion_roots",
            "scalar_inversion_intervals", "numerical_evidence"]
CODE_GLOBS = ("src/paper2b/*.py", "herramientas/b/*.py", "herramientas/d7/construir_d7.py", "herramientas/d8/*.py",
              "herramientas/bloque2/*.py", "herramientas/s3/validadores/*.py", "herramientas/s4/validadores/*.py",
              "herramientas/ca2_bundles/*.py", "herramientas/congelamiento/s3_publicador.py",
              "herramientas/congelamiento/s4_publicador.py")
SUITE_GLOBS = ("herramientas/bloque2/run_suite.py", "herramientas/bloque2/pruebas/*.py")
TOLERANCES = {"T1_accounting": "1e-12", "T2_target_capture_share": "1e-4", "epsilon_econ": "0.01",
              "T_root_residual": "1e-9",
              "note": "T2 se mide por familia de algoritmo sobre problemas con solución conocida (diseño §19.4); no por decreto. "
                      "T_root_residual: residuo máximo |C2 - K1| (o |f|) de una raíz publicada; un cambio de signo sin residuo "
                      "bajo esta tolerancia es un salto, no una raíz"}


# Familias cuyo estado incompleto/fallido deja la corrida 'incomplete' (ninguna cifra de esas filas es concluyente).
STATUS_FAMILIES = ("capture_ceiling_result", "confrontation_result", "r1_summary", "r2_sections", "inversion_result",
                   "support_breakdown_result", "external_requirement_sensitivity_result", "computation_coverage")


class BError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise BError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def environment_document(root: Path, profile: dict | None = None) -> dict:
    """Evaluación RE-03 del entorno que ejecuta, contra el manifiesto+lock aprobados por el perfil (oficial por
    defecto). Documento completo (huella, discrepancias, conforms); se escribe como JSON direccionado por contenido."""
    from herramientas.bloque2 import perfiles as P
    return P.environment(root, profile or P.official(root))


def code_manifest(root: Path, globs=CODE_GLOBS) -> dict:
    files = {}
    for g in globs:
        for q in sorted(Path(root).glob(g)):
            files[q.relative_to(root).as_posix()] = sha(q.read_bytes())
    return {"files": dict(sorted(files.items()))}


def code_manifest_sha256(root: Path = ROOT, globs=CODE_GLOBS) -> str:
    return sha(K.canon(code_manifest(root, globs)) + b"\n")


MODEL_DEFAULT = "modelo_teorico_v2_2"


def method_manifest(cfg: RUN.RunConfig, model_kind: str = MODEL_DEFAULT) -> dict:
    from paper2b import elementales as EL
    return {"model_provider": model_kind,
            "elementales": ("cotas demostradas de exp/log/log1p/E/E'/potencias con aritmética IEEE 754 binary64 y redondeo "
                            "al más cercano (paper2b.elementales); sin supuesto sobre libm. Plataforma: %s"
                            % (EL.GARANTIA or "NO CONFORME: el proveedor con encierros no certifica")),
            "supremum": "mallas anidadas + perfiles globales + pulido local + laterales Richardson (ESTIMACIÓN de convergencia); "
                        "con encierros del proveedor: rama y cota certificada (cota de error demostrada)",
            "partition": "raíces exactas de trinomios generalizados en u=z^(1-rho); signos por conteo de raíces",
            "r1": "con encierros: refinamiento uniforme certificado (cajas vacías/monótonas, cruces 1-D certificados); sin "
                  "ellos: marching squares n y 2n como HALLAZGOS, estado incomplete",
            "r2": "raices.find_roots: existencia por cambio de signo + residuo, cobertura solo con encierros; saltos no son raíces",
            "endogenous": "raices.find_roots sobre C2(x) - K1 (perfil compartido); identidad solo con prueba de invarianza",
            "inversion_budget": ("presupuesto por inversión inversion_budget_seconds=%r s (pared de la evidencia C2(phi) de "
                                 "UNA búsqueda de raíces; se aplica al proveedor por defecto y se exige igual en un "
                                 "proveedor explícito); agotado -> inversión incomplete EVIDENCE_BUDGET_EXHAUSTED con "
                                 "pendientes. Distinto de budget_seconds (corrida) y de los presupuestos por unidades"
                                 % cfg.inversion_budget_seconds),
            "robustness": "escalera declarada de r + bisección; vértices macro (reducción demostrada)",
            "coverage": "cajas estructurales entre nudos: certified_pruned solo con encierro de G; si no, pending",
            "config": cfg.as_dict()}


def write_inputs(root: Path, cfg: RUN.RunConfig, contract_path: str, contract_sha256: str = A.CONTRACT,
                 env_doc: dict | None = None, model_kind: str = MODEL_DEFAULT, *, authority=None) -> tuple[dict, list]:
    """Archivos técnicos direccionados por contenido en <root>/fase2_datos/b_frontera/entradas/ (o raíz de prueba); con autoridad S6,
    en <root>/salidas_s6/b_frontera/entradas/ (s6r35, familias.ubicacion).
    'environment' es la evaluación RE-03 completa (huella + discrepancias contra lo aprobado), no una cadena de versión."""
    root = Path(root)
    b_root = FAM.ubicacion(FAM.FAMILY_ROOT["B"], authority)
    out_dir = root / b_root / "entradas"
    out_dir.mkdir(parents=True, exist_ok=True)
    docs = {"configuration": cfg.as_dict(), "tolerances": TOLERANCES, "method": method_manifest(cfg, model_kind),
            "code": code_manifest(ROOT), "environment": env_doc or environment_document(root)}
    tech, deps = {}, []
    for role, obj in sorted(docs.items()):
        raw = K.canon(obj) + b"\n"
        rel = f"{b_root}/entradas/{role}_{sha(raw)[:16]}.json"
        q = root / rel
        if not q.exists():
            q.write_bytes(raw)
        need(q.read_bytes() == raw, "B_INPUT_WRITE:" + role)
        tech[role + "_sha256"] = sha(raw)
        deps.append({"role": role, "path": rel, "sha256": sha(raw), "tree_sha256": None, "version": role, "authority_package_sha256": None})
    craw = (root / contract_path).read_bytes()
    need(sha(craw) == contract_sha256, "B_CONTRACT_MANIFEST")
    tech["contract_sha256"] = contract_sha256
    deps.append({"role": "contract", "path": contract_path, "sha256": contract_sha256, "tree_sha256": None, "version": "CA2-4",
                 "authority_package_sha256": None})
    return dict(sorted(tech.items())), deps


def run_manifest(r: RUN.Run, inp: RUN.RunInputs, cfg: RUN.RunConfig, created_at: str) -> dict:
    cases = sorted({c["availability_case_id"] for c in r.rows["cell_context"]})
    by = {k: sum(1 for c in r.rows["cell_context"] if c["availability_case_id"] == k) for k in cases}
    incomplete = any(x.get("computation_status", x.get("status")) in ("incomplete", "failed") for t in STATUS_FAMILIES for x in r.rows[t])
    return {"run_id": r.run_id, "theory_version": inp.theory[0], "theory_path": inp.theory[1], "theory_sha256": inp.theory[2],
            "protocol_version": inp.protocol[0], "protocol_path": inp.protocol[1], "protocol_sha256": inp.protocol[2],
            "manifest_hash": inp.manifest_hash, "support_set_ids": sorted(set(r.evaluated_sets())),
            "external_grid_sha256": inp.grid_sha256, "availability_matrix_hash": inp.availability_matrix_hash,
            "availability_case_set": cases, "n_omega": len(r.rows["omega"]), "n_cells": len(r.rows["cell_context"]),
            "n_cells_by_availability_case": by, "n_inadmissible": sum(1 for o in r.rows["omega"] if o["domain_status"] == "excluded"),
            "run_readiness_flag": False, "created_at": created_at, "producer_sha256": inp.producer_sha256,
            "environment_manifest_sha256": inp.environment_manifest_sha256, "contract_sha256": inp.contract_sha256,
            "algorithm_config_sha256": inp.algorithm_config_sha256, "run_class": cfg.run_class,
            "status": "incomplete" if (incomplete or r.incomplete_reasons) else "complete"}


def emit(root: Path, contracts, d7: D7View, r: RUN.Run, inp: RUN.RunInputs, cfg: RUN.RunConfig, authority: A.AuthorityContext,
         deps: list, *, producer_path: str, producer_bytes: bytes, created_at: str, resolver=None) -> dict:
    """Valida TODO (esquema, PK/FK con D7, reglas contratadas) y escribe la versión B inmutable (sin puntero)."""
    files = {}
    tables = {}
    for name in B_TABLES:
        tables[name] = T.sort_rows(contracts, name, [T.normalize_row(contracts, name, x) for x in r.rows[name]])
    joint = dict(tables, **d7.tables)
    contracts.references(joint)
    errors = RULES.check_b(tables, contracts, d7, technical=inp.technical, protocol_sha256=inp.protocol[2],
                           grid_cells=inp.grid_cells, resolver=resolver, tolerances=inp.tolerances or TOLERANCES)
    need(not errors, "B_RULES:" + "; ".join(errors[:5]))
    for name in B_TABLES:
        data = T.table_bytes(contracts, name, r.rows[name])
        files[contracts.C["tables"][name]["file"].split("/", 1)[1]] = (data, T.csv_rows(data))
    rm = run_manifest(r, inp, cfg, created_at)
    files["run_manifest.json"] = (T.json_doc_bytes(contracts, "run_manifest", rm), None)
    entries = FAM.entries_for(files)
    mbytes = FAM.manifest(contracts, "B", run_id=r.run_id, producer_path=producer_path, producer_sha256=sha(producer_bytes),
                          authority_package=authority.package_sha256, authority_manifest=authority.manifest_sha256,
                          contract_sha256=authority.contract_sha256, dependencies=deps, entries=entries, phase_status=rm["status"],
                          created_at=created_at)
    info = FAM.write_version(Path(root) / FAM.ubicacion(FAM.FAMILY_ROOT["B"], authority), "B", files, mbytes)
    return dict(info, run_manifest=rm, run_id=r.run_id)


def synthetic_inputs(root: Path, world: dict, *, grid_kwargs: dict | None = None) -> dict:
    """Escribe (direccionados por contenido) los insumos sintéticos que D7/B/D8 consumen por ruta y hash explícitos."""
    from herramientas.bloque2 import sintetico as SY
    countries = sorted({c for e in world["registry"]["entries"] for c in e["country_set"]})
    grid_raw, cells = SY.grid(countries, **(grid_kwargs or {}))
    desc = {"tag": SY.SYN_TAG, "shares": {c: {k: str(v) for k, v in sh.items()} for c, sh in sorted(world["shares"].items())},
            "formulas_parameters_sha256": K.H(world["formulas"]["parameters"]), "countries": countries}
    nl = b"\n"
    docs = {"mundo.json": K.canon(desc) + nl, "registro.json": K.canon(world["registry"]) + nl,
            "model_case_map.json": K.canon(world["d4"]["model_case_map"]) + nl, "grilla.csv": grid_raw,
            "dominio_conjunto.json": K.canon(SY.joint_domain(countries, world["shares"])) + nl}
    docs["availability_matrix.json"] = K.canon(world["d4"]["matrix_payload"])
    bundle, contexts = SY.synthetic_bundle(world)
    docs["bundle.json"] = K.canon(bundle) + nl
    for name, raw in sorted(contexts.items()):
        docs["contextos/" + name] = raw
    tag = K.H({k: sha(v) for k, v in docs.items()})[:16]
    out = {}
    for name, raw in docs.items():
        rel = f"sintetico/{tag}/{name}"
        q = Path(root) / rel
        q.parent.mkdir(parents=True, exist_ok=True)
        if not q.exists():
            q.write_bytes(raw)
        need(q.read_bytes() == raw, "B_SYNTHETIC_INPUT_WRITE:" + name)
        out[name] = (rel, sha(raw))
    for e in world["evidence"]:
        name = {"EV.D4.MAP": "model_case_map.json", "EV.D4.MATRIX": "availability_matrix.json"}.get(e["evidence_id"])
        if name:
            e["source_path"], e["payload_sha256"] = out[name]
    base = f"sintetico/{tag}/"
    return {"paths": out, "grid_raw": grid_raw, "cells": cells, "countries": countries, "bundle": json.loads(docs["bundle.json"]),
            "bundle_sha256": sha(docs["bundle.json"]), "bundle_path": out["bundle.json"][0], "base": base}


def synthetic_dependencies(si: dict) -> list:
    roles = {"mundo.json": "sintetico_mundo", "registro.json": "registro_casos", "model_case_map.json": "d4_model_case_map",
             "availability_matrix.json": "d4_availability_matrix", "grilla.csv": "external_grid", "dominio_conjunto.json": "sintetico_dominio_conjunto", "bundle.json": "ca2_bundle"}
    return [{"role": roles[n], "path": p, "sha256": h, "tree_sha256": None, "version": "SYN", "authority_package_sha256": None}
            for n, (p, h) in sorted(si["paths"].items()) if n in roles]


def set_index_for(registry: dict) -> dict:
    from paper2b.d7build import base_set_id, editions
    out = {}
    for entry in registry["entries"]:
        for ed in editions(entry):
            for block in ("macro", "micro"):
                out.setdefault(entry["preregistration_id"], {}).setdefault(ed or "pub", {})[block] = base_set_id(entry, ed, block)
    return out


def final_config(cfg: RUN.RunConfig, set_index: dict, run_class: str) -> RUN.RunConfig:
    """Configuración EXACTA de la corrida (clase + sets base derivados del registro): la misma que sella el freeze-run."""
    from dataclasses import replace
    return replace(cfg, run_class=run_class,
                   base_sets=tuple(sorted(s for e in set_index.values() for ed in e.values() for s in ed.values())))


def _synthetic_run_inputs(root: Path, contracts, world: dict, si: dict, view: D7View, d7_manifest_rel: str, d7_manifest_sha: str,
                          d7_tree: str, d7_run_id: str, set_index: dict, cfg: RUN.RunConfig, authority, created_at: str,
                          env_doc: dict | None, external_factor_mapping=None, supplier_targets=None):
    from herramientas.bloque2 import sintetico as SY
    grid_raw, cells = si["grid_raw"], si["cells"]
    grid_rel = si["paths"]["grilla.csv"][0]
    contract_path = authority.contract_root + "contratos/contract_manifest.json"
    model = world.get("model")
    tech, deps = write_inputs(root, cfg, contract_path, authority.contract_sha256, env_doc,
                              model.kind if model is not None else MODEL_DEFAULT, authority=authority)
    theory_path = "fase4_teoria/baseline_model_v2_2.md"
    proto_path = authority.contract_root + "contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md"
    theory = ("v2_2", theory_path, sha((Path(root) / theory_path).read_bytes()))
    protocol = ("S2", proto_path, sha((Path(root) / proto_path).read_bytes()))
    deps += [{"role": "d7_version", "path": d7_manifest_rel, "sha256": d7_manifest_sha, "tree_sha256": d7_tree,
              "version": d7_run_id, "authority_package_sha256": authority.package_sha256},
             {"role": "external_grid", "path": grid_rel, "sha256": sha(grid_raw), "tree_sha256": None, "version": "SYN",
              "authority_package_sha256": None},
             {"role": "theory", "path": theory_path, "sha256": theory[2], "tree_sha256": None, "version": theory[0],
              "authority_package_sha256": None},
             {"role": "protocol", "path": proto_path, "sha256": protocol[2], "tree_sha256": None, "version": protocol[0],
              "authority_package_sha256": None}]
    grid_dep = {"role": "external_grid", "manifest_path": d7_manifest_rel, "manifest_sha256": d7_manifest_sha,
                "artifact_path": grid_rel, "artifact_sha256": sha(grid_raw), "record_pk": {"table": "grid"}}
    env = next(d for d in deps if d["role"] == "environment")
    inp = RUN.RunInputs(contracts=contracts, d7=view, registry=world["registry"], grid_cells=cells, grid_sha256=sha(grid_raw),
                        grid_dependency=grid_dep, model_case_map=world["d4"]["model_case_map"],
                        availability_matrix_hash=world["d4"]["matrix_sha256"],
                        national=(SY.strict_national_provider(world, si["paths"], root) if world.get("national_mode") == "strict"
                                  else SY.national_provider(world, si["bundle"], si["bundle_sha256"])),
                        conditional_key=SY.conditional_key_provider(world, contracts, tech, protocol[2], si["bundle"],
                                                                    si["bundle_sha256"]), technical=tech,
                        theory=theory, protocol=protocol, manifest_hash=authority.manifest_sha256, contract_sha256=authority.contract_sha256,
                        producer_sha256=sha(Path(__file__).read_bytes()), environment_manifest_sha256=env["sha256"],
                        algorithm_config_sha256=tech["configuration_sha256"], crosswalk_sha256=K.H(["syn-crosswalk"]),
                        supplier_targets=supplier_targets or {}, external_factor_mapping=external_factor_mapping,
                        set_index=set_index, created_at=created_at, model=world.get("model"),
                        tolerances=dict(TOLERANCES))
    return inp, deps


def synthetic_validation(root: Path, contracts, world: dict, *, d7_out: Path, cfg: RUN.RunConfig, created_at: str,
                         external_factor_mapping=None, supplier_targets=None, grid_kwargs: dict | None = None,
                         env_doc: dict | None = None) -> dict:
    """Mundo sintético -> D7 sintético -> B synthetic_validation en root (raíz de prueba, nunca el original)."""
    sys.path.insert(0, str(ROOT / "herramientas/d7"))
    import construir_d7 as D7
    from paper2b import claves_condicionales as CK
    authority = world["authority"]
    authority.require("b_synthetic_validation_authorized")
    need(world["data_class"] == "synthetic", "B_SYNTHETIC_REQUIRES_SYNTHETIC_WORLD")
    si = synthetic_inputs(root, world, grid_kwargs=grid_kwargs)
    d7res = D7.produce(world, contracts, authority, d7_out, producer_path="herramientas/d7/construir_d7.py",
                       producer_bytes=(ROOT / "herramientas/d7/construir_d7.py").read_bytes(),
                       dependencies=synthetic_dependencies(si), created_at=created_at)
    view = D7View.load(contracts, Path(d7_out) / "versions" / d7res["tree_sha256"])
    need(view.phase["ready_for_b"] is True, "B_D7_NOT_READY")
    cfg = final_config(cfg, d7res["set_index"], cfg.run_class)
    d7_manifest_rel = (Path(d7_out) / "versions" / d7res["tree_sha256"] / "d7_manifest.json").resolve().relative_to(
        Path(root).resolve()).as_posix()
    inp, deps = _synthetic_run_inputs(root, contracts, world, si, view, d7_manifest_rel, d7res["manifest_sha256"],
                                      d7res["tree_sha256"], d7res["run_id"], d7res["set_index"], cfg, authority, created_at,
                                      env_doc, external_factor_mapping, supplier_targets)
    r = RUN.Run(inp, cfg)
    r.execute()
    for row in r.rows["frontier_context"]:
        contracts.key("structural", row["structural_key_payload"], row["structural_key_sha256"])
        contracts.technical(row["structural_key_payload"]["technical"], root, deps)
    resolver = CK.BundleResolver(root, {si["bundle_sha256"]: si["bundle_path"]})
    out = emit(root, contracts, view, r, inp, cfg, authority, deps, producer_path="herramientas/b/ejecutar_b.py",
               producer_bytes=Path(__file__).read_bytes(), created_at=created_at, resolver=resolver)
    return dict(out, d7=d7res, d7_view=view, run=r, inputs=inp, deps=deps, synthetic_inputs=si, cfg=cfg, resolver=resolver)


def emit_units(root: Path, contracts, ex, state: dict, inp: RUN.RunInputs, cfg: RUN.RunConfig, authority: A.AuthorityContext,
               deps: list, *, producer_path: str, producer_bytes: bytes, created_at: str) -> dict:
    """Emisión en FLUJO desde un checkpoint completo por unidades: mezcla externa -> staging -> versión B atómica."""
    import uuid
    root = Path(root)
    fam_root = root / FAM.ubicacion(FAM.FAMILY_ROOT["B"], authority)
    stage = fam_root / ".staging" / uuid.uuid4().hex
    stage.mkdir(parents=True)
    try:
        asm = ex.assemble(state, stage)
        st = asm["stats"]
        rm = {"run_id": asm["run_id"], "theory_version": inp.theory[0], "theory_path": inp.theory[1], "theory_sha256": inp.theory[2],
              "protocol_version": inp.protocol[0], "protocol_path": inp.protocol[1], "protocol_sha256": inp.protocol[2],
              "manifest_hash": inp.manifest_hash, "support_set_ids": sorted(set(RUN.Run(inp, cfg).evaluated_sets())),
              "external_grid_sha256": inp.grid_sha256, "availability_matrix_hash": inp.availability_matrix_hash,
              "availability_case_set": sorted(st["by_case"]), "n_omega": st["n_omega"], "n_cells": st["n_cells"],
              "n_cells_by_availability_case": dict(sorted(st["by_case"].items())), "n_inadmissible": st["n_inadmissible"],
              "run_readiness_flag": False, "created_at": created_at, "producer_sha256": inp.producer_sha256,
              "environment_manifest_sha256": inp.environment_manifest_sha256, "contract_sha256": inp.contract_sha256,
              "algorithm_config_sha256": inp.algorithm_config_sha256, "run_class": cfg.run_class,
              "status": "incomplete" if st["incomplete"] else "complete"}
        (stage / "run_manifest.json").write_bytes(T.json_doc_bytes(contracts, "run_manifest", rm))
        entries = FAM.entries_for_dir(stage)
        mbytes = FAM.manifest(contracts, "B", run_id=asm["run_id"], producer_path=producer_path, producer_sha256=sha(producer_bytes),
                              authority_package=authority.package_sha256, authority_manifest=authority.manifest_sha256,
                              contract_sha256=authority.contract_sha256, dependencies=deps, entries=entries, phase_status=rm["status"],
                              created_at=created_at)
        info = FAM.write_version_staged(fam_root, "B", stage, mbytes)
    finally:
        if stage.exists():
            import shutil
            shutil.rmtree(stage)
    return dict(info, run_manifest=rm, run_id=asm["run_id"], table_info=asm["files"])


def synthetic_validation_units(root: Path, contracts, world: dict, *, d7_out: Path, cfg: RUN.RunConfig, created_at: str,
                               checkpoint_dir: Path, budgets=None, resume: bool = False, grid_kwargs: dict | None = None,
                               env_doc: dict | None = None, emit_version: bool = True) -> dict:
    """Validación sintética ejecutada POR UNIDADES con checkpoint reanudable; emite B solo si el checkpoint está completo."""
    sys.path.insert(0, str(ROOT / "herramientas/d7"))
    import construir_d7 as D7
    from herramientas.b import unidades as U
    from paper2b import claves_condicionales as CK
    authority = world["authority"]
    authority.require("b_synthetic_validation_authorized")
    need(world["data_class"] == "synthetic", "B_SYNTHETIC_REQUIRES_SYNTHETIC_WORLD")
    si = synthetic_inputs(root, world, grid_kwargs=grid_kwargs)
    d7res = D7.produce(world, contracts, authority, d7_out, producer_path="herramientas/d7/construir_d7.py",
                       producer_bytes=(ROOT / "herramientas/d7/construir_d7.py").read_bytes(),
                       dependencies=synthetic_dependencies(si), created_at=created_at)
    view = D7View.load(contracts, Path(d7_out) / "versions" / d7res["tree_sha256"])
    need(view.phase["ready_for_b"] is True, "B_D7_NOT_READY")
    cfg = final_config(cfg, d7res["set_index"], cfg.run_class)
    d7_manifest_rel = (Path(d7_out) / "versions" / d7res["tree_sha256"] / "d7_manifest.json").resolve().relative_to(
        Path(root).resolve()).as_posix()
    inp, deps = _synthetic_run_inputs(root, contracts, world, si, view, d7_manifest_rel, d7res["manifest_sha256"],
                                      d7res["tree_sha256"], d7res["run_id"], d7res["set_index"], cfg, authority, created_at, env_doc)
    resolver = CK.BundleResolver(root, {si["bundle_sha256"]: si["bundle_path"]})
    ex = U.Executor(inp, cfg, checkpoint_dir, authority=authority, code_manifest_sha256=code_manifest_sha256(),
                    budgets=budgets or U.Budgets(), resolver=resolver)
    state = ex.run(resume=resume)
    out = {"state": state, "executor": ex, "inputs": inp, "deps": deps, "cfg": cfg, "d7": d7res, "d7_view": view,
           "synthetic_inputs": si, "resolver": resolver}
    if state["status"] == "complete" and emit_version:
        out.update(emit_units(root, contracts, ex, state, inp, cfg, authority, deps, producer_path="herramientas/b/ejecutar_b.py",
                              producer_bytes=Path(__file__).read_bytes(), created_at=created_at))
    return out


def _preconditions(root: Path, contracts, authority: A.AuthorityContext, profile: dict, *, freeze_sha: str | None, d7_dir: Path,
                   d7_tree: str, d8_pre_dir: Path, d8_pre_tree: str, cfg: RUN.RunConfig) -> dict:
    """Precondiciones COMUNES de la corrida congelada (oficial y ensayo): la misma lógica en ambos perfiles."""
    from herramientas.bloque2 import freeze_run as FR
    from herramientas.bloque2 import perfiles as P
    authority.require("b_official_run_authorized")
    authority.require("freeze_run_authorized")
    try:
        P.require_authority(profile, authority)
    except P.ProfileError as exc:
        raise BError("B_" + str(exc))
    env_doc = environment_document(root, profile)
    try:
        fr = FR.verify(root, freeze_sha, authority.contract_sha256, authority.contract_root, authority, profile, d7_dir=d7_dir,
                       d7_tree=d7_tree, d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree, cfg_dict=cfg.as_dict(),
                       code_manifest=code_manifest(ROOT), env_doc=env_doc)
    except FR.FreezeError as exc:
        raise BError("B_" + str(exc))
    need(env_doc["conforms"], "B_OFFICIAL_ENVIRONMENT_NOT_APPROVED")
    pre = FAM.verify_version(d8_pre_dir, "D8_pre", expected_tree=d8_pre_tree)
    phase = json.loads((Path(d8_pre_dir) / "d8_pre_phase_report.json").read_bytes())
    need(phase["status"] == "pass" and phase["ready_for_freeze_run"] is True, "B_OFFICIAL_REQUIRES_D8_PRE_PASS")
    pdeps = {d["role"]: d for d in pre["manifest"]["input_dependencies"]}
    need(pdeps.get("d7_version", {}).get("tree_sha256") == d7_tree, "B_OFFICIAL_D7_NOT_AUDITED_BY_D8_PRE")
    d7info = FAM.verify_version(d7_dir, "D7", expected_tree=d7_tree)
    view = D7View.load(contracts, d7_dir)
    need(view.phase["ready_for_b"] is True, "B_D7_NOT_READY")
    d7m = (Path(d7_dir) / "d7_manifest.json").resolve().relative_to(Path(root).resolve()).as_posix()
    d8m = (Path(d8_pre_dir) / "d8_pre_manifest.json").resolve().relative_to(Path(root).resolve()).as_posix()
    extra = [FR.dependency(root, fr),
             {"role": "d8_pre_version", "path": d8m, "sha256": pre["manifest_sha256"], "tree_sha256": d8_pre_tree,
              "version": pre["manifest"]["run_id"], "authority_package_sha256": pre["manifest"]["authority_package_sha256"]}]
    if profile["kind"] == "ensayo":
        extra.append({"role": "perfil_ensayo", "path": profile["path"], "sha256": profile["sha256"], "tree_sha256": None,
                      "version": "FICTICIO", "authority_package_sha256": None})
    return {"freeze": fr, "env_doc": env_doc, "d7info": d7info, "view": view, "d7m": d7m, "extra_deps": extra}


def official(root: Path, contracts, authority: A.AuthorityContext, *, d7_dir: Path, d7_tree: str, d8_pre_dir: Path,
             d8_pre_tree: str, cfg: RUN.RunConfig, created_at: str, freeze_sha: str | None = None) -> dict:
    """Corrida OFICIAL nacional. Precondiciones (ninguna se cumple en el bloque 2): autoridad REAL con corrida oficial y
    freeze-run, freeze-run sellado que coincide con esta selección (D7, D8_pre PASS, código, contrato, configuración,
    entorno RE-03 + lock, casos, fuentes). Las entradas nacionales salen de herramientas/b/nacional.py."""
    import csv
    import io
    from herramientas.b import nacional as NAT
    from herramientas.bloque2 import perfiles as P
    root = Path(root)
    authority.require("b_official_run_authorized")
    authority.require("freeze_run_authorized")
    need(not authority.fictitious, "B_OFFICIAL_FICTITIOUS_AUTHORITY")
    d7info0 = FAM.verify_version(d7_dir, "D7", expected_tree=d7_tree)
    view0 = D7View.load(contracts, d7_dir)
    probe = NAT.Providers(root, contracts, view0, protocol_sha256="0" * 64, technical={})
    set_index = {}
    for sid, (entry, ed, block) in probe.set_case.items():
        set_index.setdefault(entry["preregistration_id"], {}).setdefault(ed, {})[block] = sid
    cfg = final_config(cfg, set_index, "official")
    pc = _preconditions(root, contracts, authority, P.official(root, anclas=authority.anclas_externas or None), freeze_sha=freeze_sha, d7_dir=d7_dir, d7_tree=d7_tree,
                        d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree, cfg=cfg)
    view, d7info = pc["view"], pc["d7info"]
    need(d7info["manifest_sha256"] == d7info0["manifest_sha256"], "B_D7_CHANGED_DURING_PRECONDITIONS")
    ddeps = {d["role"]: d for d in d7info["manifest"]["input_dependencies"]}
    gdep, mdep = ddeps["external_grid"], ddeps["d4_model_case_map"]
    grid_raw = (root / gdep["path"]).read_bytes()
    need(sha(grid_raw) == gdep["sha256"], "B_GRID_HASH")
    mraw = (root / mdep["path"]).read_bytes()
    need(sha(mraw) == mdep["sha256"], "B_D4_MAP_HASH")
    mcm = list(csv.DictReader(io.StringIO(mraw.decode("utf-8"))))
    contract_path = authority.contract_root + "contratos/contract_manifest.json"
    theory_path = "fase4_teoria/baseline_model_v2_2.md"
    proto_path = authority.contract_root + "contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md"
    theory = ("v2_2", theory_path, sha((root / theory_path).read_bytes()))
    protocol = ("S2", proto_path, sha((root / proto_path).read_bytes()))
    tech, deps = write_inputs(root, cfg, contract_path, authority.contract_sha256, pc["env_doc"], authority=authority)
    prov = NAT.Providers(root, contracts, view, protocol_sha256=protocol[2], technical=tech)
    d7m = pc["d7m"]
    deps += [{"role": "d7_version", "path": d7m, "sha256": d7info["manifest_sha256"], "tree_sha256": d7_tree,
              "version": d7info["manifest"]["run_id"], "authority_package_sha256": d7info["manifest"]["authority_package_sha256"]},
             {"role": "external_grid", "path": gdep["path"], "sha256": gdep["sha256"], "tree_sha256": None, "version": gdep["version"],
              "authority_package_sha256": None},
             {"role": "theory", "path": theory_path, "sha256": theory[2], "tree_sha256": None, "version": theory[0],
              "authority_package_sha256": None},
             {"role": "protocol", "path": proto_path, "sha256": protocol[2], "tree_sha256": None, "version": protocol[0],
              "authority_package_sha256": None}] + pc["extra_deps"]
    env = next(d for d in deps if d["role"] == "environment")
    ev = {r["evidence_id"]: r for r in view.tables["source_evidence"]}
    grid_dep = {"role": "external_grid", "manifest_path": d7m, "manifest_sha256": d7info["manifest_sha256"],
                "artifact_path": gdep["path"], "artifact_sha256": gdep["sha256"], "record_pk": {"table": "grid"}}
    inp = RUN.RunInputs(contracts=contracts, d7=view, registry=prov.registry, grid_cells=X.read_grid(grid_raw),
                        grid_sha256=gdep["sha256"], grid_dependency=grid_dep, model_case_map=mcm,
                        availability_matrix_hash=ev["EV.D4.MATRIX"]["payload_sha256"], national=prov.national,
                        conditional_key=prov.conditional_key, technical=tech, theory=theory, protocol=protocol,
                        manifest_hash=authority.manifest_sha256, contract_sha256=authority.contract_sha256,
                        producer_sha256=sha(Path(__file__).read_bytes()), environment_manifest_sha256=env["sha256"],
                        algorithm_config_sha256=tech["configuration_sha256"], crosswalk_sha256=ev["EV.CROSSWALK"]["payload_sha256"],
                        dme_gai=0.0, set_index=set_index, created_at=created_at, tolerances=dict(TOLERANCES))
    r = RUN.Run(inp, cfg)
    r.execute()
    return emit(root, contracts, view, r, inp, cfg, authority, deps, producer_path="herramientas/b/ejecutar_b.py",
                producer_bytes=Path(__file__).read_bytes(), created_at=created_at, resolver=prov.resolver())


def trial_frozen(root: Path, contracts, authority: A.AuthorityContext, world: dict, *, profile_path: str, profile_sha: str,
                 freeze_sha: str | None, d7_dir: Path, d7_tree: str, d8_pre_dir: Path, d8_pre_tree: str, cfg: RUN.RunConfig,
                 created_at: str, grid_kwargs: dict | None = None, external_factor_mapping=None, supplier_targets=None) -> dict:
    """ENSAYO de la ruta congelada con fixtures: mismas precondiciones que official() (freeze-run verificado, D8_pre PASS,
    entorno conforme a lo aprobado POR EL PERFIL de ensayo) en raíz aislada con autoridad FICTICIA y mundo sintético.
    run_class='trial_frozen' + dependencias freeze_run y perfil_ensayo: ningún consumidor oficial lo acepta."""
    from herramientas.bloque2 import perfiles as P
    from paper2b import claves_condicionales as CK
    root = Path(root)
    try:
        profile = P.load(root, profile_path, profile_sha, anclas=authority.anclas_externas or None)
    except (P.ProfileError, OSError) as exc:
        raise BError("B_TRIAL_PROFILE:" + str(exc))
    need(profile["kind"] == "ensayo", "B_TRIAL_REQUIRES_TRIAL_PROFILE")
    need(world.get("data_class") == "synthetic", "B_TRIAL_REQUIRES_SYNTHETIC_WORLD")
    set_index = set_index_for(world["registry"])
    cfg = final_config(cfg, set_index, "trial_frozen")
    pc = _preconditions(root, contracts, authority, profile, freeze_sha=freeze_sha, d7_dir=d7_dir, d7_tree=d7_tree,
                        d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree, cfg=cfg)
    si = synthetic_inputs(root, world, grid_kwargs=grid_kwargs)
    ddeps = {d["role"]: d for d in pc["d7info"]["manifest"]["input_dependencies"]}
    for d in synthetic_dependencies(si):
        need(ddeps.get(d["role"], {}).get("sha256") == d["sha256"], "B_TRIAL_WORLD_IS_NOT_THE_D7_WORLD:" + d["role"])
    inp, deps = _synthetic_run_inputs(root, contracts, world, si, pc["view"], pc["d7m"], pc["d7info"]["manifest_sha256"], d7_tree,
                                      pc["d7info"]["manifest"]["run_id"], set_index, cfg, authority, created_at, pc["env_doc"],
                                      external_factor_mapping, supplier_targets)
    deps += pc["extra_deps"]
    r = RUN.Run(inp, cfg)
    r.execute()
    resolver = CK.BundleResolver(root, {si["bundle_sha256"]: si["bundle_path"]})
    out = emit(root, contracts, pc["view"], r, inp, cfg, authority, deps, producer_path="herramientas/b/ejecutar_b.py",
               producer_bytes=Path(__file__).read_bytes(), created_at=created_at, resolver=resolver)
    return dict(out, run=r, inputs=inp, deps=deps, synthetic_inputs=si, cfg=cfg, freeze=pc["freeze"], resolver=resolver)


def cli_config(inversion_budget_s: str | None) -> RUN.RunConfig:
    """Configuración de la corrida oficial desde la CLI. El texto del presupuesto por inversión se convierte con float()
    y lo valida RunConfig (finito, dentro de los límites); 'nan', 'inf', '0' o negativos -> ValueError (rechazo)."""
    kw = {}
    if inversion_budget_s is not None:
        try:
            kw["inversion_budget_seconds"] = float(inversion_budget_s)
        except ValueError:
            raise ValueError("RUNCONFIG_INVERSION_BUDGET_TYPE:%r" % inversion_budget_s)
    return RUN.RunConfig(run_class="official", **kw)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Paquete B")
    ap.add_argument("command", choices=["oficial", "verificar", "seleccion-paso4"])
    # CANDIDATO PASO 4 (VALIDACION PAQUETE 3.7, NO OFICIAL; copia aislada): recorrido por selección sellada
    ap.add_argument("--fase", choices=["seleccionar", "ejecutar", "reanudar", "validar", "oficial"]); ap.add_argument("--paquete"); ap.add_argument("--tabla")
    ap.add_argument("--interrumpir-tras", dest="interrumpir_tras", type=int, default=None); ap.add_argument("--salida"); ap.add_argument("--regla", default=None)
    ap.add_argument("--despliegue", default=None, help="despliegue candidato (rutas externas y parámetros de autoridad)")
    ap.add_argument("--s6-lanzamiento-sha256", help="SHA-256 EXTERNO de autorización; volver a aportar tras reubicar; no se deduce del paquete")
    ap.add_argument("--autoridad", choices=["s3", "s4", "s5", "s6"], default="s3")
    ap.add_argument("--policy"); ap.add_argument("--receipt"); ap.add_argument("--author")
    ap.add_argument("--producto"); ap.add_argument("--tree")
    ap.add_argument("--d7"); ap.add_argument("--d7-tree"); ap.add_argument("--d8-pre"); ap.add_argument("--d8-pre-tree")
    ap.add_argument("--freeze-run", help="sha256 de la selección sellada (fase6_planes/freeze_runs/<sha>/; con autoridad S6, "
                                         "salidas_s6/freeze_runs/<sha>/)")
    ap.add_argument("--presupuesto-por-inversion-s", dest="inversion_budget_s", default=None,
                    help="presupuesto por inversión endógena en segundos (RunConfig.inversion_budget_seconds; por defecto "
                         "%r; debe coincidir con la configuración sellada por el freeze-run)" % RUN.INVERSION_BUDGET_DEFAULT_S)
    args = ap.parse_args(argv)
    if args.command == "seleccion-paso4":
        return seleccion_paso4(args)
    try:
        if args.command == "verificar":
            info = FAM.verify_version(Path(args.producto), "B", expected_tree=args.tree)
            print(json.dumps({"status": "verified_B", "tree_sha256": info["tree_sha256"], "phase_status": info["manifest"]["phase_status"]}))
            return 0
        cfg = cli_config(args.inversion_budget_s)
        from herramientas.bloque2 import entorno as E
        E.set_runtime_conventions()
        extra = {"lanzamiento_sha256": args.s6_lanzamiento_sha256} if args.autoridad == "s6" else {}
        if args.s6_lanzamiento_sha256 is not None and args.autoridad != "s6":
            raise A.AuthorityError("ANCLA_S6_CON_OTRA_AUTORIDAD")
        ctx = {"s3": A.from_s3, "s4": A.from_s4, "s5": A.from_s5, "s6": A.from_s6}[args.autoridad](ROOT, args.policy, args.receipt, args.author, **extra)
        ctx.require("b_official_run_authorized")
        from herramientas.s3.validadores.core import Contracts
        out = official(ROOT, Contracts.load(ROOT / ctx.contract_root, ctx.contract_sha256), ctx, d7_dir=Path(args.d7), d7_tree=args.d7_tree,
                       d8_pre_dir=Path(args.d8_pre), d8_pre_tree=args.d8_pre_tree, cfg=cfg,
                       created_at=FAM.now(), freeze_sha=args.freeze_run)
        print(json.dumps({"tree_sha256": out["tree_sha256"], "run_manifest": out["run_manifest"]}, ensure_ascii=False))
        return 0
    except (A.AuthorityError, BError, FAM.FamilyError, ValueError, KeyError, OSError, RuntimeError) as exc:  # noqa: B014
        print("B RECHAZADO: " + type(exc).__name__ + ": " + str(exc))
        return 2


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 (CONTRATO PAQUETE 3.7, NO OFICIAL; copia aislada; no incorporado). Recorrido por selección sellada:
# seleccionar -> ejecutar (lotes; interrupción de prueba) -> reanudar -> validar, con la RUTA COMÚN de verificación.
# Autoridad: contexto S5 autenticado del área (codigo/demo/nucleo_v.Contexto), NO el pipeline `official` (que exige
# freeze-run y la autorización b_official_run_authorized). La lógica vive en los módulos candidatos del área
# (codigo/flujo_paso4_v2.py, codigo/generador_candidato_v2.py) y la ruta común en herramientas/s3/validadores/
# paquete_seleccion.py (con paper2b/contrato_paquete.py); --fase oficial se rechaza siempre; el plan, en
# herramientas/b/unidades.plan_selection (copia candidata), que debe coincidir con el del flujo.
def seleccion_paso4(args) -> int:
    import importlib.util
    import sys as _sys
    import importlib.util as _ilu
    _n = "cand_seleccion_paso4"
    if _n not in _sys.modules:                       # punto de entrada CANDIDATO (hermano de este archivo)
        _sp = _ilu.spec_from_file_location(_n, Path(__file__).with_name("seleccion_paso4.py"))
        _m = _ilu.module_from_spec(_sp)
        _sys.modules[_n] = _m
        _sp.loader.exec_module(_m)
    FP = _sys.modules[_n]
    if FP.DESPLIEGUE is None:
        FP.configurar(args.despliegue)
    if args.fase == "oficial":     # CONTRATO PAQUETE 3.7: puerta del pipeline futuro; en el candidato SIEMPRE rechaza
        try:
            FP.P2.exigir_corrida_oficial(args)
        except FP.P2.Rechazo as exc:
            print("B RECHAZADO: %s: %s" % (exc.codigo, exc.detalle))
            return 2
    pdir = Path(args.paquete)
    if args.fase == "seleccionar":
        FP.seleccionar(args.tabla, pdir, args.regla)
        spec = importlib.util.spec_from_file_location("cand_unidades", Path(__file__).with_name("unidades.py"))
        U = importlib.util.module_from_spec(spec)
        _sys.modules["cand_unidades"] = U
        spec.loader.exec_module(U)
        sel = json.loads((pdir / "seleccion.json").read_bytes())
        if U.plan_selection(sel) != json.loads((pdir / "plan.json").read_bytes()):
            print("B RECHAZADO: PLAN_DE_UNIDADES_DISTINTO_DEL_DEL_FLUJO")
            return 2
        return 0
    ctx = FP.contexto()        # autoridad S5 por herramientas/b/contexto_s5.py (parámetros explícitos)
    try:
        FP.P2.puerta_autoridad(ctx)        # S5 real, banderas oficiales en False, etiqueta NO OFICIAL
    except FP.P2.Rechazo as exc:
        print("B RECHAZADO: %s: %s" % (exc.codigo, exc.detalle))
        return 2
    ref = FP.referencia(ctx)
    if args.fase in ("ejecutar", "reanudar"):
        try:
            FP.Ejecutor(pdir, ctx, ref).ejecutar(reanudar=args.fase == "reanudar", interrumpir_tras=args.interrumpir_tras)
        except FP.FlujoError as exc:
            print("B RECHAZADO: " + str(exc))
            return 2
        return 0
    r = FP.validar(pdir, ref)
    if args.salida:
        Path(args.salida).write_bytes((json.dumps(r, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps({"cumple": r["cumple"], "dictamen": r.get("dictamen"), "codigos": r.get("codigos")}, ensure_ascii=False))
    return 0 if r["cumple"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
