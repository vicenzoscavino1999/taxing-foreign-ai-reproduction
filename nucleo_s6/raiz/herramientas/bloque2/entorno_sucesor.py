"""Contrato de entorno CANDIDATO sucesor (bloque 3): perfiles, roles y evaluación separada de la aprobación.

Tres estados que este módulo mantiene distinguibles (nunca se infiere uno de otro):
- conformidad con el contrato APROBADO vigente: entorno.assessment(root) con las constantes aprobadas de entorno.py
  (manifiesto histórico 3bd72cc8…, Windows-11-build-22621, lock 3e81920b…);
- conformidad TÉCNICA con el contrato CANDIDATO: evaluar(root, perfil) contra los manifiestos de
  environment/sucesor_b3/<perfil>/ (estado CANDIDATO_SUCESOR_NO_APROBADO, plataforma validada Windows-11-build-26200);
- aprobación REAL: solo la concede el autor al emitir S4, cuya política fija pins() (campo 'environment'). Ninguna
  etiqueta, hash ni evaluación de este módulo la sustituye; aprobacion_real() la reconoce solo si el S4 vivo VERIFICA
  por completo (herramientas/s4/aprobacion.py, definición única) y es real (la aprobación ficticia nunca cuenta).

Perfiles (separación exigida por los contratos históricos: Paquete A/A-ter aceptan EXACTAMENTE numpy+pip):
- numerico: CPython 3.12.4 oficial + pip 26.1.2 + numpy 2.0.2 (lock aprobado, mismos bytes).
- integracion: numerico + PyMuPDF (fitz) + openpyxl + pandas y dependencias (herramientas documentales y compuerta S4).
ROLES fija qué perfil ejecuta cada proceso; exigir() lo comprueba al arrancar el proceso (y sus hijos heredan el mismo
intérprete: sys.executable), y el resultado registra huella, manifiesto y lock efectivamente comprobados.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from herramientas.bloque2 import entorno as E

ESTADO = "CANDIDATO_SUCESOR_NO_APROBADO"
PLATAFORMA_VALIDADA = "Windows-11-build-26200"
ANTECEDENTE = {"manifest_path": E.APPROVED_MANIFEST_PATH, "manifest_sha256": E.APPROVED_MANIFEST_SHA256,
               "lock_path": E.APPROVED_LOCK_PATH, "lock_sha256": E.APPROVED_LOCK_SHA256}
RECETA = {"path": "environment/sucesor_b3/crear_entorno.ps1",
          "sha256": "373ffc2bd52f90065e4228c5f37e47711a99514d583d9e3b7e08c97849612ca9"}
PERFILES = {
    "numerico": {"manifest_path": "environment/sucesor_b3/numerico/environment_manifest.json",
                 "manifest_sha256": "97b98ebbde49382bf3594fab9cb020e92d850103a1eea4a3e6fefff7ca49ccb0",
                 "lock_path": "environment/sucesor_b3/numerico/requirements.lock",
                 "lock_sha256": "3e81920beac139b7a4d992e3cde7847c44d21253059e5de76703a518806e6521"},
    "integracion": {"manifest_path": "environment/sucesor_b3/integracion/environment_manifest.json",
                    "manifest_sha256": "a44e3c8e93be710e1451bcb72f0920c6a84a1bcb1ee6e4be82ebfad2f0e4b90a",
                    "lock_path": "environment/sucesor_b3/integracion/requirements.lock",
                    "lock_sha256": "942a4138192e12eb149343fbf12e1b0856591094ba0da4e28dfc97d4a1c28a2f"},
}
ROLES = {"paquete_a": "numerico", "paquete_a_ter": "numerico", "b3_3_phi_df": "numerico",
         "compuerta_s4": "integracion", "suites_historicas": "integracion", "suites_s3": "integracion",
         "bateria_bloque2": "integracion", "congelador": "integracion", "d7_b_d8": "integracion"}


class EntornoSucesorError(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pins() -> dict:
    """Lo que la política S4 fija como entorno a aprobar (el autor lo aprueba con S4; aquí solo se declara)."""
    return {"estado": ESTADO, "plataforma_validada": PLATAFORMA_VALIDADA, "antecedente": dict(ANTECEDENTE),
            "receta": dict(RECETA), "perfiles": {k: dict(v) for k, v in PERFILES.items()}, "roles": dict(ROLES)}


def pins_sha256() -> str:
    return sha(json.dumps(pins(), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _manifiesto(root, perfil: str) -> dict:
    if perfil not in PERFILES:
        raise EntornoSucesorError("PERFIL_DESCONOCIDO:" + str(perfil))
    ref = PERFILES[perfil]
    raw = (Path(root) / ref["manifest_path"]).read_bytes()
    if sha(raw) != ref["manifest_sha256"]:
        raise EntornoSucesorError("MANIFIESTO_CANDIDATO_ALTERADO:" + perfil)
    man = json.loads(raw)
    if man.get("status") != ESTADO or man.get("profile") != perfil or man.get("platform") != PLATAFORMA_VALIDADA:
        raise EntornoSucesorError("MANIFIESTO_CANDIDATO_INCOHERENTE:" + perfil)
    if man.get("antecedent", {}).get("manifest_sha256") != ANTECEDENTE["manifest_sha256"]:
        raise EntornoSucesorError("ANTECEDENTE_DISTINTO:" + perfil)
    receta = (Path(root) / RECETA["path"]).read_bytes()
    if sha(receta) != RECETA["sha256"] or man.get("recipe_sha256") != RECETA["sha256"]:
        raise EntornoSucesorError("RECETA_NO_LIGADA:" + perfil)
    return man


def evaluar(root, perfil: str) -> dict:
    """Conformidad TÉCNICA con el perfil candidato (no aprobación)."""
    man = _manifiesto(root, perfil)
    doc = E.assessment(root, **PERFILES[perfil])
    doc = dict(doc, perfil=perfil, estado_contrato=ESTADO, plataforma_validada=man["platform"],
               nota="conformidad técnica con el contrato CANDIDATO; la aprobación real la concede solo S4")
    return doc


def exigir(root, perfil: str) -> dict:
    doc = evaluar(root, perfil)
    if not doc["conforms"]:
        raise EntornoSucesorError("ENTORNO_NO_CONFORME_CON_PERFIL_CANDIDATO:%s:%s" % (perfil, ";".join(doc["mismatches"][:4])))
    return doc


def dictamen(root, perfil: str, *, anclas: dict | None = None) -> dict:
    """Los tres estados, separados, para el proceso en curso."""
    aprobado = E.assessment(root)
    cand = evaluar(root, perfil)
    return {"perfil": perfil, "huella_sha256": cand["fingerprint_sha256"],
            "conformidad_contrato_aprobado_vigente": {"conforms": aprobado["conforms"], "mismatches": aprobado["mismatches"],
                                                      "manifest_sha256": ANTECEDENTE["manifest_sha256"]},
            "conformidad_tecnica_contrato_candidato": {"conforms": cand["conforms"], "mismatches": cand["mismatches"],
                                                       "manifest_sha256": PERFILES[perfil]["manifest_sha256"],
                                                       "lock_sha256": PERFILES[perfil]["lock_sha256"]},
            "aprobacion_real": aprobacion_real(root, anclas=anclas)}


def aprobacion_real(root, *, anclas: dict | None = None) -> dict:
    """Estado de la aprobación real del entorno sucesor (corrección R2).

    APROBADO_POR_S4 solo si herramientas/s4/aprobacion.estado_s4 (definición única, compartida con perfiles.s4_approved)
    clasifica el S4 vivo como VERIFICADO_REAL (s4_publicador.verify completo) y la política instalada fija exactamente
    pins(). Una declaración en el manifiesto nunca basta. Resultados controlados:
    PENDIENTE/SIN_S4, PENDIENTE/S4_FICTICIO, INVALIDO/<motivo>, APROBADO_POR_S4."""
    from herramientas.s4 import aprobacion as AP
    est = AP.estado_s4(root, anclas=anclas)
    if est["estado"] == "SIN_S4":
        return {"estado": "PENDIENTE", "situacion": "SIN_S4",
                "motivo": "S4 no emitido: rige el contrato aprobado histórico (22621). " + est["motivo"]}
    if est["estado"] in ("S4_FICTICIO", "S5_FICTICIO", "S6_FICTICIO"):
        return {"estado": "PENDIENTE", "situacion": est["estado"], "verificado": est.get("verificado"),
                "motivo": est["estado"][:2] + " vigente es FICTICIO (ensayo): no aprueba nada. " + est["motivo"]}
    if est["estado"] != "VERIFICADO_REAL":
        return {"estado": "INVALIDO", "situacion": "S4_INVALIDO", "motivo": est["motivo"]}
    if est.get("environment") != pins():
        return {"estado": "INVALIDO", "situacion": "S4_REAL_CON_OTRO_ENTORNO",
                "motivo": "el S4 real verificado no fija este entorno sucesor (pins distintos)"}
    if est.get("autoridad") == "S6":
        return {"estado": "APROBADO_POR_S6", "situacion": "S6_REAL_VERIFICADO", "package_sha256": est["package_sha256"],
                "policy_sha256": est["policy_sha256"], "receipt_sha256": est["receipt_sha256"], "author": est["author"]}
    if est.get("autoridad") == "S5":                 # sucesora S5 (B3-5): misma exigencia, otra autoridad
        return {"estado": "APROBADO_POR_S5", "situacion": "S5_REAL_VERIFICADO", "package_sha256": est["package_sha256"],
                "policy_sha256": est["policy_sha256"], "receipt_sha256": est["receipt_sha256"], "author": est["author"]}
    return {"estado": "APROBADO_POR_S4", "situacion": "S4_REAL_VERIFICADO", "package_sha256": est["package_sha256"],
            "policy_sha256": est["policy_sha256"], "receipt_sha256": est["receipt_sha256"], "author": est["author"]}
