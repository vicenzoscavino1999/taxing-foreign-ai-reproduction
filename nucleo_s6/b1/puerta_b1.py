"""rem163 — PUERTA NATIVA COMÚN del paquete B1 (derivada de paquete_p7/puerta_p7.py rem153 a88ea602…, copia en antecedente/). La usan IGUAL
el trabajador (b1_trabajo), el validador (validar_b1) y el conductor (conducir_b1, también en continuación) ANTES de cualquier operación
científica o escritura productiva. No es un booleano ni un hash aislado:
- modo ∈ {produccion, sintetico} (otro modo se rechaza) y coherente con el manifiesto (…-SINTETICO ⇔ sintético);
- producción: alcance Y decisión obligatorios; se leen UNA vez los bytes del alcance; alcance_b1.verificar (verificar_documento del C0 +
  comparación campo a campo con alcance_b1.esperado desde autoridad fijada) y aprobacion_alcance.decision_humana del C0 SIN modo_arnes sobre
  la decisión ORIGINAL, que liga su evidencia (mensaje humano dedicado «AUTORIZO ALCANCE PASO4 alcance_sha256=…» del registro nativo) al
  sha256 de esos MISMOS bytes; un manifiesto o una etiqueta FIXTURE nunca habilitan producción;
- sintético: sin alcance o con alcance FIXTURE verificado igual; la decisión no se comprueba ni se fabrica; nunca habilita producción.
Diferencial frente a puerta_p7: nombres B1 y comprobación de FIXTURE también en el alcance (etiqueta) antes de devolver. Devuelve
(alcance_sha256, evidencia); lanza la excepción del lector C0 (Rechazo) o AssertionError. Importable; no escribe nada."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b1 as C  # noqa: E402


def puerta_comun(modo, man, man_sha, tarea, alcance_p=None, decision_p=None):
    import alcance_b1 as AP
    AA = AP.lector()
    AA.need(modo in ("produccion", "sintetico"), "MODO_DESCONOCIDO", str(modo)[:40])
    sint_man = str(man.get("kind", "")).endswith("-SINTETICO")
    AA.need((modo == "sintetico") == sint_man and man.get("modo") == modo, "MEZCLA_REAL_SINTETICO")
    if modo == "produccion":
        AA.need(bool(alcance_p) and bool(decision_p), "SIN_ALCANCE_O_DECISION")
    if not alcance_p:
        return None, None
    raw = Path(alcance_p).read_bytes()
    doc, s = json.loads(raw), C.H(raw)
    AP.verificar(doc, man, man_sha, C.HF(C.AQUI / "PAQUETE_B1.json"), tarea, AA)
    if modo != "produccion":
        return s, None
    ev = AA.decision_humana(json.loads(Path(decision_p).read_bytes()), s, doc["emitida_utc"])
    AA.need("FIXTURE" not in str(man.get("kind", "")) and "FIXTURE" not in str(doc.get("etiqueta", "")), "FIXTURE_NO_HABILITA_PRODUCCION")
    AA.need(ev.get("modo_arnes") is False, "MODO_ARNES_NO_ADMITIDO")
    return s, ev
