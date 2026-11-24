"""Autoridad consumidora de D7/B/D8 (bloque 2).

S3 (vigente) NO autoriza D7/B/D8: su alcance fija source_admission, quantitative_eligibility, scientific_execution y
model_execution en false, y su toolchain cerrada no contiene los módulos del bloque 2. Por eso:
- con S3 todo productor D7/B/D8 se RECHAZA (y la verificación S3 misma falla si hay módulos no fijados);
- con una autoridad sucesora S4 (herramientas/congelamiento/s4_publicador.py) el alcance se lee de su política
  aprobada por recibo separado del autor; los productos D2/D6/D3-D5 siguen autenticándose con S3 como antecedente;
- en pruebas existe un contexto FICTICIO explícito, rotulado en cada salida (nunca utilizable en la raíz original).
- con la sucesora S5 (bloque 3, B3-5, candidata; herramientas/congelamiento/s5_publicador.py) el contexto incluye la
  sucesión: productos nacionales sucesores VERIFICADOS (D2, D6 v2, índice de bundles, idénticos a la adopción S5), mapeo
  A6 y elegibilidad por caso; D3-D5 y sus certificados siguen autenticándose con S3 como antecedente.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

S3_PACKAGE = "8aaa27cf12dfe435512ccd60245cc1ed4c70dbf28421eee5aec7c38814fab7b9"
S3_MANIFEST = "0cc606177b865ec58d5bee1a68fb6143dae7a9be4a3cde5c95eb8df54b103ddc"
S3_POLICY = "1192c3caec215f8419939b175be81a8c963b40c693ffcacc638ebd82a6af03fc"
S3_RECEIPT = "3b03a698105da957b9b86728e61566fe6d39e0f9a7049a2e828ee5bf3e65db50"
CONTRACT_S3 = "eda3d6e5a0c0c0c318bb075c3314f7c927382c955d76e2dcdd3b5c1f4659af32"   # CA2-3, antecedente (S3)
TRIAL_CONTRACT = "7bde9f1549e7c3903a88b41ac1896d81bf8c5eeb1ebee7bd6e960bb5ea2286bb"
CONTRACT = "4d7e676a2156c7f83b231e812fa39afe417fb6057abb35083f80774fe15e3220"      # CA2-4 candidata: contrato de D7/B/D8
TRIAL_CONTRACT_ROOT = "herramientas/bloque2/contratos_g_na_1/"
CONTRACT_ROOT_CANDIDATE = "herramientas/s4/contratos_enmienda/"
S3_PREFIX = f"fase6_planes/integracion_s3/versions/{S3_POLICY}/"
FICTITIOUS_MARK = "FICTICIA_ENSAYO_AISLADO"
SCOPE_FLAGS = ("d7_production_authorized", "quantitative_eligibility_authorized", "b_synthetic_validation_authorized",
               "b_official_run_authorized", "freeze_run_authorized", "d8_pre_authorized", "d8_post_authorized",
               "official_export_authorized", "source_admission_authorized")


class AuthorityError(RuntimeError):
    pass


def need(test, code: str):
    if not test:
        raise AuthorityError(code)


@dataclass
class AuthorityContext:
    kind: str                      # S3 | S4 | FICTICIA_ENSAYO_AISLADO
    package_sha256: str
    manifest_sha256: str
    decision_path: str
    decision_sha256: str
    approval_evidence_sha256: str
    consumer_scope: str
    lineage_manifest_sha256: str
    scope: dict
    products_authority: dict       # autoridad bajo la que se emitieron D2/D6/D3-D5 (S3, antecedente)
    pins: dict = field(default_factory=dict)
    installed_prefix: str = S3_PREFIX            # contratos y productos antecedentes (S3)
    contract_root: str = CONTRACT_ROOT_CANDIDATE  # raíz de entrega del contrato de D7/B/D8 que autentica esta autoridad
    contract_sha256: str = CONTRACT
    succession: dict | None = None               # S5: identidad, adopción, productos verificados, A6 y elegibilidad por caso

    # Copia del contexto EXTERNO aportado por el llamante; nunca se deriva del paquete.
    anclas_externas: dict = field(default_factory=dict)

    @property
    def authority_id(self) -> str:
        return f"AUT:{self.kind}:{self.package_sha256[:16]}"

    @property
    def fictitious(self) -> bool:
        return self.kind == FICTITIOUS_MARK

    def row(self) -> dict:
        return {"authority_id": self.authority_id, "package_sha256": self.package_sha256,
                "manifest_sha256": self.manifest_sha256, "decision_path": self.decision_path,
                "decision_sha256": self.decision_sha256, "approval_evidence_sha256": self.approval_evidence_sha256,
                "consumer_scope": self.consumer_scope, "lineage_manifest_sha256": self.lineage_manifest_sha256}

    def require(self, flag: str) -> None:
        need(flag in SCOPE_FLAGS, "BANDERA_DESCONOCIDA:" + flag)
        need(self.scope.get(flag) is True, f"AUTORIDAD_{self.kind}_NO_AUTORIZA:{flag}")


def from_s3(root: Path, policy: str, receipt: str, author: str) -> AuthorityContext:
    """S3 verificada. Su alcance no contiene ninguna bandera del bloque 2: todo consumidor debe rechazar."""
    from herramientas.congelamiento import s3_publicador as S3P
    a = S3P.verify(Path(root), policy, receipt, author)
    scope = {k: False for k in SCOPE_FLAGS}
    return AuthorityContext("S3", a["package_sha256"], a["manifest_sha256"], a["installed_prefix"] + "compatibilidad_s3.json",
                            policy, receipt, "S3: incorporación de fuentes y reconstrucción de consumidores; sin D7/B/D8",
                            a["manifest_sha256"], scope, {"package_sha256": a["package_sha256"], "manifest_sha256": a["manifest_sha256"],
                                                          "contract_sha256": a["contract_sha256"], "installed_prefix": a["installed_prefix"],
                                                          "adopted": a["adopted"]}, contract_root=a["installed_prefix"],
                            contract_sha256=CONTRACT_S3)


def from_s4(root: Path, policy: str, receipt: str, author: str) -> AuthorityContext:
    from herramientas.congelamiento import s4_publicador as S4P
    a = S4P.verify(Path(root), policy, receipt, author)
    s3 = a["antecedent_s3"]
    kind = FICTITIOUS_MARK if a.get("fictitious_approval") else "S4"
    return AuthorityContext(kind, a["package_sha256"], a["manifest_sha256"], a["decision_path"], a["decision_sha256"], receipt,
                            a["consumer_scope"], a["manifest_sha256"], dict(a["scope"]),
                            {"package_sha256": s3["package_sha256"], "manifest_sha256": s3["manifest_sha256"],
                             "contract_sha256": s3["contract_sha256"], "installed_prefix": s3["installed_prefix"],
                             "adopted": s3["adopted"]}, pins=dict(a["pins"]), installed_prefix=s3["installed_prefix"],
                            contract_root=a["contract_root"], contract_sha256=a["contract_sha256"])


def from_s5(root: Path, policy: str, receipt: str, author: str) -> AuthorityContext:
    """S5 verificada CON sus productos publicados (verify_products): sin productos idénticos a la adopción, se rechaza."""
    from herramientas.congelamiento import s5_publicador as S5P
    vp = S5P.verify_products(Path(root), policy, receipt, author)
    a = vp["s5"]
    s3 = a["antecedent_s4"]["s3"]
    kind = FICTITIOUS_MARK if a.get("fictitious_approval") else "S5"
    return AuthorityContext(kind, a["package_sha256"], a["manifest_sha256"], a["decision_path"], a["decision_sha256"], receipt,
                            a["consumer_scope"], a["manifest_sha256"], dict(a["scope"]),
                            {"package_sha256": s3["package_sha256"], "manifest_sha256": s3["manifest_sha256"],
                             "contract_sha256": s3["contract_sha256"], "installed_prefix": s3["installed_prefix"],
                             "adopted": s3["adopted"]}, pins=dict(a["pins"]), installed_prefix=s3["installed_prefix"],
                            contract_root=a["contract_root"], contract_sha256=a["contract_sha256"],
                            succession={"s5": {k: a[k] for k in ("package_sha256", "manifest_sha256", "policy_sha256", "receipt_sha256")},
                                        "adopcion": dict(a["adopcion"]), "elegibilidad": dict(a["elegibilidad"]),
                                        "a6": dict(a["a6"]), "productos": {"d2": vp["d2"], "d6": vp["d6"], "bundles": vp["bundles"]}})


def from_s6(root: Path, policy: str, receipt: str, author: str, *, lanzamiento_sha256: str | None = None) -> AuthorityContext:
    """S6 (CANDIDATA) verificada: código acumulado con S5 como antecedente archivado y sus productos HEREDADOS verificados
    (s6_publicador.verify). Misma forma de contexto que from_s5; la sucesión registra S6 y su antecedente S5."""
    from herramientas.congelamiento import s6_publicador as S6P
    a = S6P.verify(Path(root), policy, receipt, author, lanzamiento_sha256=lanzamiento_sha256)
    ant = a["antecedent_s5"]
    s3 = ant["s4"]["s3"]
    kind = FICTITIOUS_MARK if a.get("fictitious_approval") else "S6"
    return AuthorityContext(kind, a["package_sha256"], a["manifest_sha256"], a["decision_path"], a["decision_sha256"], receipt,
                            a["consumer_scope"], a["manifest_sha256"], dict(a["scope"]),
                            {"package_sha256": s3["package_sha256"], "manifest_sha256": s3["manifest_sha256"],
                             "contract_sha256": s3["contract_sha256"], "installed_prefix": s3["installed_prefix"],
                             "adopted": s3["adopted"]}, pins=dict(a["pins"]), installed_prefix=s3["installed_prefix"],
                            contract_root=a["contract_root"], contract_sha256=a["contract_sha256"],
                            succession={"s6": {k: a[k] for k in ("package_sha256", "manifest_sha256", "policy_sha256", "receipt_sha256")},
                                        "s5": {k: ant[k] for k in ("package_sha256", "manifest_sha256", "policy_sha256", "receipt_sha256")},
                                        "adopcion": dict(ant["adopcion"]), "elegibilidad": dict(a["elegibilidad"]), "a6": dict(ant["a6"]),
                                        "codigo": dict(a["codigo"]), "d7": dict(a["d7"]), "productos": a["productos_heredados"]},
                            anclas_externas={"policy_sha256": policy, "receipt_sha256": receipt, "author": author,
                                             "lanzamiento_sha256": lanzamiento_sha256})


def autoridad_real_verificada(root: Path, authority: AuthorityContext, *, facultad: str | None = None) -> dict:
    """Reconocimiento de una autoridad REAL en rutas oficiales (D8_pre P01, exportación oficial) por AUTENTICACIÓN y no
    por etiqueta (corrección candidata B3-6/B3-7; sustituye las comparaciones kind == "S4"):
    1. el contexto no es ficticio;
    2. la definición ÚNICA del estado vivo (herramientas/s4/aprobacion.estado_s4, que delega en el verificador completo de
       la autoridad vigente: S4, S5 o una sucesora que registre allí su rama) lo clasifica VERIFICADO_REAL;
    3. el contexto ES esa autoridad: misma clase, paquete, manifiesto, recibo y alcance que el resultado verificado (un
       contexto alterado, de otra autoridad o ya no vigente se rechaza);
    4. si se pide una facultad, el ALCANCE VERIFICADO la concede (no el del contexto).
    Devuelve el resumen verificado; si no, AuthorityError con el motivo específico."""
    need(not authority.fictitious, "AUTORIDAD_FICTICIA_EN_RUTA_OFICIAL")
    from herramientas.s4 import aprobacion as AP
    est = AP.estado_s4(Path(root), anclas=authority.anclas_externas or None)
    need(est.get("estado") == "VERIFICADO_REAL", "AUTORIDAD_VIVA_NO_VERIFICADA:%s:%s" % (est.get("estado"), str(est.get("motivo"))[:160]))
    v = est.get("verificacion") or {}
    viva = est.get("autoridad", "S4")
    need(viva == authority.kind, "AUTORIDAD_INCOMPATIBLE:contexto %s, vigente %s" % (authority.kind, viva))
    need(est.get("package_sha256") == v.get("package_sha256") == authority.package_sha256, "AUTORIDAD_ALTERADA_O_NO_VIGENTE:paquete")
    need(v.get("manifest_sha256") == authority.manifest_sha256, "AUTORIDAD_ALTERADA:manifiesto")
    need(est.get("receipt_sha256") == authority.approval_evidence_sha256, "AUTORIDAD_ALTERADA:recibo")
    alcance = dict(v.get("scope") or {})
    need({k: alcance.get(k) for k in SCOPE_FLAGS} == {k: authority.scope.get(k) for k in SCOPE_FLAGS}, "AUTORIDAD_ALTERADA:alcance")
    if facultad is not None:
        need(facultad in SCOPE_FLAGS, "BANDERA_DESCONOCIDA:" + facultad)
        need(alcance.get(facultad) is True, "AUTORIDAD_%s_NO_AUTORIZA:%s" % (viva, facultad))
    return {"estado": "VERIFICADO_REAL", "autoridad": viva, "package_sha256": authority.package_sha256,
            "manifest_sha256": authority.manifest_sha256, "receipt_sha256": authority.approval_evidence_sha256, "facultad": facultad}


def fictitious(*, scope: dict, pins: dict | None = None, label: str = "pruebas") -> AuthorityContext:
    """Autoridad FICTICIA para pruebas y mundos sintéticos. Rotulada en authority_id y consumer_scope."""
    full = {k: bool(scope.get(k, False)) for k in SCOPE_FLAGS}
    fake = "f" * 64
    return AuthorityContext(FICTITIOUS_MARK, fake, fake, "herramientas/bloque2/autoridad.py", fake, fake,
                            f"{FICTITIOUS_MARK}: {label}; no autoriza nada en la raíz original", fake, full,
                            {"package_sha256": fake, "manifest_sha256": fake, "contract_sha256": CONTRACT_S3,
                             "installed_prefix": S3_PREFIX, "adopted": {}}, pins=dict(pins or {}),
                            contract_root=TRIAL_CONTRACT_ROOT, contract_sha256=TRIAL_CONTRACT)
