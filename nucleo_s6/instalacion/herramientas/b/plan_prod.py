"""PLAN DE PRODUCCIÓN del paso 4 (PROD1–PROD3) — candidato rem56; NO OFICIAL; planificación separada de ejecución.
Construye, desde la LISTA INSTALADA (datos/paso4/lista_PROD.json, sha256 fijado en el plan), un plan con la MISMA forma que verifica la ruta
común (corrida_paso4.verificar_plan: plan_sha256 del cuerpo canónico, banderas oficiales en false) y que recorre corrida_paso4.ejecutar:
tareas con «unidades» (una búsqueda o un ámbito Q por tarea: el coste por búsqueda bajo el núcleo S6 NO está medido) y r1 vacío.
  - topes: 2400 s por tarea (límite ordinario); calendario por TOPES (peor caso) con unión de ronda <= 10 800 s y una tarea a la vez;
  - resumen_q: entrada de PROD3 (resumen agregado de las unidades de detalle aceptadas) por archivo y sha256, o null (las tareas Q se rechazan
    hasta fijarlo; cambiarlo cambia el plan_sha256 que cita la autorización);
  - piloto: subconjunto declarado para MEDIR coste en la primera ejecución autorizada (mismas búsquedas que los ensayos EQ/EQM).
  python -B herramientas/b/plan_prod.py <salida.json> [<resumen_q.json>]"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
KIND = "plan-corrida-paso4-produccion-v1"
TOPE_S = 2400.0
UNION_RONDA_S = 10800.0
PILOTO = ("PROD1:PREG-COMPARACION-E1:historical_anchor:ci:MEX:f:conditional_full:G:addback_completo:micro:guardrail_deuda:a:superior",
          "PROD1:PREG-COMPARACION-E1:primary:ci:MEX:f:conditional_full:G:sin_addback:micro:guardrail_deuda:rho:inferior",
          "PROD1:PREG-COMPARACION-E1:historical_anchor:ci:MEX:f:conditional_full:G:sin_addback:micro:guardrail_deuda:kappa_tilde:superior",
          "PROD2:PREG-COMPARACION-E1:primary:ci:MEX:f:conditional_full:G:addback_completo:micro:guardrail_deuda:eta_w:inferior",
          "PROD2:PREG-COMPARACION-E1:historical_anchor:ci:MEX:f:conditional_full:G:addback_completo:micro:guardrail_deuda:pi_joint:inferior",
          "PROD2:PREG-COMPARACION-E1:primary:ci:MEX:f:conditional_full:G:addback_completo:micro:guardrail_deuda:eta_H:ladder")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def construir(resumen_q: dict | None = None, contexto_esperado: dict | None = None, decision_q: str | None = None, decisiones: dict | None = None) -> dict:
    """rem64: contexto_esperado = {identidad_sha256, despliegue_sha256, procedencia} (entrada SELLADA como resumen_q: la aceptación común
    contrasta con él cada producto); decision_q = decisión Q sellada (None: PROD3 desactivado)."""
    import decision_d4 as D4                            # rem66: decisiones selladas admitidas: None (D4 desactivada) o {QUIEBRES-D4: sha256 exacto}
    D4.admitida_en_plan(decisiones)
    if contexto_esperado is not None:
        assert all(isinstance(contexto_esperado.get(k), str) and len(contexto_esperado[k]) == 64 for k in ("identidad_sha256", "despliegue_sha256")), "CONTEXTO_ESPERADO_INVALIDO"
    raw = (INSTALACION / "datos/paso4/lista_PROD.json").read_bytes()
    lista = json.loads(raw)
    # rem65: PROD1/PROD2, una búsqueda por tarea (la aceptación de una tarea es conjunta: agrupar búsquedas independientes haría que una
    # incompleta arrastrara a las completas); PROD3, las DOS salidas de una misma afirmación (ámbitos global y país) en UNA tarea: derivan de la
    # MISMA evidencia continua (misma fila numérica) y comparten preparación y Φ* en caché; se amortiza un contexto por afirmación.
    grupos, por_afirmacion = [], {}
    for u in lista["unidades"]:
        if u["familia"] == "PROD3" and u["afirmacion"] in por_afirmacion:
            por_afirmacion[u["afirmacion"]][1].append(u["id"])
            continue
        g = (u, [u["id"]])
        grupos.append(g)
        if u["familia"] == "PROD3":
            por_afirmacion[u["afirmacion"]] = g
    tareas = []
    for k, (u, ids) in enumerate(grupos, 1):
        tareas.append({"id": "%s-T%03d" % (u["familia"], k), "fase": u["fase"], "familia": u["familia"], "carril": 1, "unidades": list(ids),
                       "asignacion_sha256": sha(canon(list(ids))), "tope_s": TOPE_S, "pared_s": None, "cpu_s": None, "requiere_excepcion": False,
                       "condicionada_a": [], "coste": "NO MEDIDO bajo el núcleo S6 (ensayo EQ/EQM con el núcleo demo: ver la lista)"})
    # Una suite por producto. El tope de 2400 incluye preparacion de ContextoS6,
    # busqueda y validacion del trabajador (sin repartir/recortar presupuesto
    # numerico). Comparacion/conciliacion separada, tope vigente de 120 s.
    # Dos margenes de terminacion de 90 s por suite; montaje 120 s por ronda.
    from calendario_paso4 import TOPE_COMPARACION_S, MARGEN_TERMINACION_S
    suite_total = TOPE_S + TOPE_COMPARACION_S
    suite_reservada = suite_total + 2*MARGEN_TERMINACION_S
    montaje = 120.0
    rondas, cur, union = [], [], montaje
    for t in tareas:
        if union + suite_reservada > UNION_RONDA_S:
            rondas.append(cur)
            cur, union = [], montaje
        cur.append(t["id"])
        union += suite_reservada
    if cur:
        rondas.append(cur)
    cal = [{"ronda": n, "suites": [{"tareas": [x], "topes_s": {x: TOPE_S}, "comparaciones": [x], "tope_comparacion_s": TOPE_COMPARACION_S,
                                   "topes_total_s": suite_total, "reserva_con_margenes_s": suite_reservada} for x in r],
            "montaje_tope_s": montaje, "union_topes_s": montaje + suite_total*len(r), "union_con_margenes_s": montaje+suite_reservada*len(r),
            "pared_con_reserva_cierre_s": montaje+suite_reservada*len(r)+2400} for n, r in enumerate(rondas, 1)]
    ids = {u["id"] for u in lista["unidades"]}
    assert set(PILOTO) <= ids, sorted(set(PILOTO) - ids)
    # rem70 (P2-AREA-RA): especificación RELATIVA A LA INSTALACIÓN efectiva (ra/), no al área de preparación
    evaluadores = {"dependencias": {"archivo": "ra/R_A_dependencias.json", "sha256": sha((INSTALACION / "ra/R_A_dependencias.json").read_bytes())},
                   "puerto": {"archivo": "ra/puerto_ra.py", "sha256": sha((INSTALACION / "ra/puerto_ra.py").read_bytes())},
                   "adaptador": {"archivo": "herramientas/b/evaluadores_ra.py", "sha256": sha((INSTALACION / "herramientas/b/evaluadores_ra.py").read_bytes())},
                   # rem63: mismos presupuestos internos POR BÚSQUEDA que el ensayo aceptado i2 (EQ/EQM: 120 s por evaluación, 420 s por búsqueda; Q: 300 s)
                   "parametros": {"EQ": {"seg_por_evaluacion": 120.0, "tope_por_busqueda_s": 420.0}, "EQM": {"seg_por_evaluacion": 120.0, "tope_por_busqueda_s": 420.0},
                                  "QSEN2": {"tope_s": 300.0},
                                  # rem64: reloj GLOBAL por TAREA = inicio del trabajador + tope de la tarea (2400 s) − margen de cierre (validación y escritura)
                                  "margen_cierre_s": 180.0}}
    cuerpo = {"kind": KIND, "lista_prod": {"archivo": "datos/paso4/lista_PROD.json", "sha256": sha(raw)}, "familias": lista["familias"],
              "tareas": tareas, "r1": [], "r1_orden": [], "calendario": cal, "resumen_q": resumen_q, "evaluadores_ra": evaluadores, "decision_q": decision_q, "contexto_esperado": contexto_esperado, "decisiones": decisiones,
              "piloto": {"unidades": list(PILOTO), "tareas": [t["id"] for t in tareas if set(t["unidades"]) & set(PILOTO)],
                         "objeto": "medir pared/CPU por búsqueda bajo el núcleo S6 (mismas búsquedas que los ensayos EQ/EQM) antes de reagrupar"},
              "limites": {"tarea_s": TOPE_S, "suite_s": 3600, "union_ronda_s": UNION_RONDA_S, "pared_ronda_s": 14400,
                          "reserva_cierre_s": 2400, "procesos": 3, "tareas_activas": 1},
              "costes": {"medidos_PROD_S6": None, "referencia_montaje_historico_s": 53.8, "montaje_tope_s": montaje,
                         "comparacion_media_historica_s": 17.6, "comparacion_tope_vigente_s": TOPE_COMPARACION_S,
                         "busqueda_preparacion_validacion": "incluidas en tope de tarea 2400 s; desglose S6 pendiente de ensayo autorizado",
                         "margenes": "90 s por lanzamiento, dos por suite; separados de costes medidos y topes",
                         "advertencia": "Agrupacion conservadora por topes, NO ETA. Si una unidad no cabe, se detiene sin reducir presupuesto numerico ni aumentar limites."},
              "resumen": {"tareas_quiebres": sum(t["fase"] == "quiebres" for t in tareas), "tareas_Q": sum(t["fase"] == "Q" for t in tareas), "rondas_por_topes": len(cal)},
              "autorizacion_cientifica_requerida": True,
              "banderas_oficiales": {"b_official_run_authorized": False, "freeze_run_authorized": False, "official_export_authorized": False}}
    return dict(cuerpo, plan_sha256=sha(canon(cuerpo)))


if __name__ == "__main__":
    rq = None
    if len(sys.argv) > 2:
        q = Path(sys.argv[2])
        rq = {"archivo": str(q), "sha256": sha(q.read_bytes())}
    p = construir(rq)
    Path(sys.argv[1]).write_bytes(canon(p) + b"\n")
    print(json.dumps({"plan_sha256": p["plan_sha256"], **p["resumen"]}))
