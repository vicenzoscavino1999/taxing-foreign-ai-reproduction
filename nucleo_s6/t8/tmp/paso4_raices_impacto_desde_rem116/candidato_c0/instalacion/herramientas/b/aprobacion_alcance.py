"""rem105 (PORTABILIDAD; CANDIDATO NO INCORPORADO) — aprobación de un ALCANCE separada del agente y de la conversación.

Separa tres cosas que la autorización v2 mezclaba:
  (a) procedencia científica y configuración reproducible: plan, operaciones, tareas, asignaciones, entradas (sha256), despliegue técnico
      (sha256 del archivo, el mismo que fijan plan/acta), límites, reglas de repetición/excepciones y versión del código (identidad de la
      instalación). Es el documento de ALCANCE v3; su sha256 es la identidad de lo aprobado.
  (b) aprobación interna de ese alcance: un MENSAJE HUMANO NATIVO dedicado «AUTORIZO ALCANCE PASO4 alcance_sha256=<sha256>» en cualquiera
      de los almacenes nativos configurados (datos/paso4/almacenes_decision.json, parte de la identidad de la instalación), POSTERIOR a la
      emisión del alcance. Se re-lee siempre del registro nativo: un booleano, un hash o una afirmación del ejecutor no es una aprobación.
  (c) identidad del agente o interfaz que ejecuta: NO forma parte del alcance (se rechazan campos de área, recibo, conductor, conversación,
      sesión, ejecutor o agente dentro del alcance). Cambiar de agente o de conversación no invalida un alcance aprobado.
Las autorizaciones v2 y sus actos (misma conversación que el encargo del despliegue) se siguen leyendo con corrida_paso4.acto_dedicado
sin cambios: este módulo no reescribe recibos, actos, inventarios, resultados ni decisiones históricos."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

KIND_ALCANCE = "autorizacion-alcance-paso4-v3"
DECISION_RE = re.compile(r"AUTORIZO ALCANCE PASO4 alcance_sha256=([0-9a-f]{64})")
CAMPOS_ALCANCE = ("kind", "plan_sha256", "operaciones", "tareas", "asignaciones", "despliegue_sha256", "entradas", "limites", "repetir", "excepciones",
                  "instalacion_identidad", "congelamiento_p3_sha256", "emitida_utc", "b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")
PROHIBIDOS_EN_ALCANCE = ("area", "recibo", "conductor", "acto", "decision", "transcripcion", "sesion", "conversacion", "ejecutor", "agente", "interfaz",
                         "ubicaciones", "raiz_corrida", "anclas")          # rem106: la ubicación física y la raíz de ejecución tampoco son alcance
ALMACENES = Path(__file__).resolve().parents[2] / "datos/paso4/almacenes_decision.json"
PROVEEDORES = ("claude", "codex")


class Rechazo(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo, self.detalle = codigo, detalle


def need(c, codigo, detalle=""):
    if not c:
        raise Rechazo(codigo, detalle)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def identidad_instalacion(raiz: Path) -> str:
    """Misma fórmula que la custodia y la guarda: sha256 canónico de {ruta: {sha256, bytes}} de todos los archivos de la instalación."""
    f = {p.relative_to(raiz).as_posix(): {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size} for p in sorted(Path(raiz).rglob("*")) if p.is_file()}
    return sha(json.dumps(dict(sorted(f.items())), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def verificar_documento(a: dict) -> None:
    need(isinstance(a, dict) and a.get("kind") == KIND_ALCANCE, "ALCANCE_KIND_INVALIDO", str(a.get("kind") if isinstance(a, dict) else a)[:80])
    falta = [k for k in CAMPOS_ALCANCE if k not in a]
    need(not falta, "ALCANCE_INCOMPLETO", str(falta))
    sobran = [k for k in a if k in PROHIBIDOS_EN_ALCANCE]
    need(not sobran, "ALCANCE_CON_METADATOS_DE_EJECUTOR", "el alcance no puede ligarse al agente, la conversación ni el área: %s" % sobran)
    need(all(a.get(k) is False for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")), "OFICIAL_NO_AUTORIZADO")
    try:
        t = dt.datetime.fromisoformat(a["emitida_utc"])
    except (TypeError, ValueError):
        t = None
    need(t is not None and t.tzinfo is not None, "ALCANCE_SIN_EMISION_FECHADA")
    ca = a.get("continua_alcance")      # rem106: continuación declarada de un alcance anterior (hereda su historial de intentos; continuidad.py)
    need(ca is None or (isinstance(ca, str) and len(ca) == 64 and all(c in "0123456789abcdef" for c in ca)), "CONTINUA_ALCANCE_INVALIDO")


def almacenes(ruta: Path | None = None) -> dict:
    p = Path(ruta or ALMACENES)
    need(p.is_file(), "ALMACENES_DE_DECISION_AUSENTES", str(p))
    d = json.loads(p.read_bytes())
    need(isinstance(d, dict) and all(isinstance(d.get(k), list) for k in PROVEEDORES), "ALMACENES_DE_DECISION_INVALIDOS")
    return {k: [Path(x).resolve() for x in d[k]] for k in PROVEEDORES}


def _bajo(tp: Path, raices) -> bool:
    return any(tp.is_relative_to(r) for r in raices)


def _claude(ref: dict, raices, modo_arnes: bool):
    need(isinstance(ref.get("linea"), int) and ref["linea"] > 0 and isinstance(ref.get("uuid"), str), "DECISION_REFERENCIA_INVALIDA", str(ref)[:200])
    tp = Path(str(ref.get("transcripcion", ""))).resolve()
    need(modo_arnes or (_bajo(tp, raices) and tp.suffix == ".jsonl"), "DECISION_FUERA_DE_LOS_ALMACENES_NATIVOS", str(tp))
    need(tp.is_file(), "TRANSCRIPCION_AUSENTE", str(tp))
    raw = None
    with tp.open("rb") as fh:
        for n, x in enumerate(fh, 1):
            if n == ref["linea"]:
                raw = x.rstrip(b"\r\n")
                break
    need(raw is not None, "DECISION_LINEA_AUSENTE", str(ref["linea"]))
    m = json.loads(raw)
    msg = m.get("message") or {}
    need(m.get("uuid") == ref["uuid"] and m.get("type") == "user" and msg.get("role") == "user", "DECISION_MENSAJE_DISTINTO_DE_LA_FUENTE", ref["uuid"])
    need(m.get("sessionId") == tp.stem, "DECISION_DE_OTRA_SESION", "%s != %s" % (m.get("sessionId"), tp.stem))
    need(not m.get("isMeta") and not m.get("isSidechain") and not m.get("isCompactSummary") and "toolUseResult" not in m
         and m.get("userType", "external") == "external" and (m.get("origin") or {}).get("kind", "human") == "human", "DECISION_NO_ES_MENSAJE_HUMANO")
    c = msg.get("content")
    if isinstance(c, list):          # forma del cliente de VS Code: UN único bloque de texto; cualquier otra parte se rechaza
        need(len(c) == 1 and isinstance(c[0], dict) and set(c[0]) == {"type", "text"} and c[0]["type"] == "text", "DECISION_CON_PARTES_O_ADJUNTOS")
        c = c[0]["text"]
    need(isinstance(c, str), "DECISION_CON_PARTES_O_ADJUNTOS")
    return c, {"proveedor": "claude", "transcripcion": str(tp), "linea": ref["linea"], "uuid": ref["uuid"], "session_id": m.get("sessionId"),
               "timestamp": m.get("timestamp"), "registro_sha256": sha(raw)}


def _codex(ref: dict, raices, modo_arnes: bool):
    import corrida_paso4 as CO          # adaptador nativo existente (sin cambios); la raíz admitida la fija esta configuración
    tp = Path(str(ref.get("transcripcion", ""))).resolve()
    need(modo_arnes or (_bajo(tp, raices) and tp.suffix == ".jsonl"), "DECISION_FUERA_DE_LOS_ALMACENES_NATIVOS", str(tp))
    try:
        c, src = CO._mensaje_codex(dict(ref, extraccion="texto"), True)
    except CO.CorridaError as ex:
        raise Rechazo(ex.codigo, ex.detalle)
    need(modo_arnes or tp.name.endswith("-" + str(src.get("session_id")) + ".jsonl"), "CODEX_RUTA_DE_OTRA_SESION")
    return c, dict(src, proveedor="codex")


def decision_humana(ref, alcance_sha256: str, emitida_utc: str, modo_arnes: bool = False, ruta_almacenes: Path | None = None) -> dict:
    """Verifica la DECISIÓN humana sobre un alcance re-leyendo su registro nativo. Devuelve la evidencia (reutilizable por la reanudación)."""
    need(ref is not None, "DECISION_REQUERIDA", "la ejecución de un alcance v3 exige la referencia a la decisión humana nativa")
    if isinstance(ref, (str, Path)):
        need(Path(ref).is_file(), "DECISION_REFERENCIA_AUSENTE", str(ref))
        ref = json.loads(Path(ref).read_bytes())
    need(isinstance(ref, dict), "DECISION_REFERENCIA_INVALIDA")
    prov = ref.get("proveedor", "claude")
    need(prov in PROVEEDORES, "PROVEEDOR_NO_ADMITIDO", str(prov))
    need("transcripcion" in ref, "DECISION_SIN_EVIDENCIA_NATIVA", "una afirmación, booleano o hash del ejecutor no es una aprobación")
    raices = almacenes(ruta_almacenes)[prov] if not modo_arnes else []
    texto, src = (_claude if prov == "claude" else _codex)(ref, raices, modo_arnes)
    a = DECISION_RE.fullmatch(texto.strip())
    need(a is not None, "DECISION_NO_DEDICADA", "el contenido completo no es exactamente «AUTORIZO ALCANCE PASO4 alcance_sha256=<sha256>»")
    need(a.group(1) == alcance_sha256, "DECISION_DE_OTRO_ALCANCE", "%s != %s" % (a.group(1)[:16], alcance_sha256[:16]))
    ts = dt.datetime.fromisoformat(str(src["timestamp"]).replace("Z", "+00:00"))
    need(ts > dt.datetime.fromisoformat(emitida_utc), "DECISION_ANTERIOR_A_LA_EMISION", "%s <= %s" % (src["timestamp"], emitida_utc))
    return dict(src, contenido=texto.strip(), mensaje_sha256=src["registro_sha256"], alcance_sha256=alcance_sha256, modo_arnes=bool(modo_arnes))
