"""rem167 — PUERTA NATIVA COMÚN del paquete B2 (derivada de A/paquete_b1/puerta_b1.py, a24bdb76…). La usan IGUAL el trabajador (b2_trabajo),
el validador (validar_b2) y el conductor (conducir_b2) ANTES de cualquier operación científica o escritura productiva:
- modo ∈ {produccion, sintetico} y coherente con el manifiesto (…-SINTETICO ⇔ sintético);
- producción: alcance Y decisión obligatorios; alcance_b2.verificar (verificar_documento del C0 + comparación campo a campo con
  alcance_b2.esperado) y aprobacion_alcance.decision_humana del C0 SIN modo_arnes sobre la decisión ORIGINAL ligada al sha256 de esos MISMOS
  bytes. El acto de B1 (150d4b71…) no liga este alcance y el lector C0 lo rechaza; un FIXTURE nunca habilita producción;
- sintético: sin alcance o con alcance FIXTURE verificado igual; la decisión no se comprueba ni se fabrica.
Diferencial frente a puerta_b1: nombres B2 e índice PAQUETE_B2.json. Devuelve (alcance_sha256, evidencia). Importable; no escribe nada."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun_b2 as C  # noqa: E402


def puerta_comun(modo, man, man_sha, tarea, alcance_p=None, decision_p=None):
    import alcance_b2 as AP
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
    AP.verificar(doc, man, man_sha, C.HF(C.AQUI / C.INDICE), tarea, AA)
    if modo != "produccion":
        return s, None
    ev = AA.decision_humana(json.loads(Path(decision_p).read_bytes()), s, doc["emitida_utc"])
    AA.need("FIXTURE" not in str(man.get("kind", "")) and "FIXTURE" not in str(doc.get("etiqueta", "")), "FIXTURE_NO_HABILITA_PRODUCCION")
    AA.need(ev.get("modo_arnes") is False, "MODO_ARNES_NO_ADMITIDO")
    return s, ev
