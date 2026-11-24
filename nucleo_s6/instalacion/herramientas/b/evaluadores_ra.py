"""EVALUADORES R-A (EQ / EQM / QSEN2) para el TRABAJADOR DE PRODUCCIÓN — rem63; NO OFICIAL; candidato.
Carga los módulos históricos PORTADOS que ejecutó el ensayo aceptado i2 (trabajo/R_A del paquete R-A, cierre de dependencias
audit/R_A_dependencias.json) con el MISMO importador revisado (codigo/puerto_ra.ImportadorRA: bytes verificados, ContextoS6 inyectado,
guarda del núcleo S6) y ejecuta UNA unidad por llamada con la afirmación, parámetro, dirección y ámbito de la ESPECIFICACIÓN sellada.
Los cuerpos de búsqueda son los de los bucles ensayados (codigo.ensayo_quiebres, codigo.ensayo_quiebres_macro, codigo.sensibilidad_q):
mismas llamadas y argumentos a RB.search / RB.ladder_search / cobertura M4 / sondeo / phi_star / RB.q_sensitivity
(pruebas/conexion.py compara las llamadas con el AST de los originales). Solo se AÑADE:
  - captura de evidencia ya calculada: registros de testigo de la cobertura M4 (llegan por su `log`) y, en el sondeo macro, el contexto
    que fija el máximo de G (índice de base -> vértice macro por Universo.meta);
  - conversión de testigos al contrato productivo ({parameter_id, value} en la dirección buscada) SIN inventar puntos: si la evidencia
    capturada no contiene el valor, la unidad no se publica con testigo (TestigoNoSerializable).
No cambia algoritmos, q_pot_exact, omega, datos, tolerancias, presupuestos ni la selección."""
from __future__ import annotations

import hashlib
import importlib
import sys
import time
from decimal import Decimal
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
AREA_RA = INSTALACION      # rem70 (P2-AREA-RA): puerto, manifiesto y módulos R-A viven DENTRO de la instalación efectiva (ra/); sin área de preparación
ENTRADAS = {"EQ": "codigo.ensayo_quiebres", "EQM": "codigo.ensayo_quiebres_macro", "QSEN2": "codigo.sensibilidad_q"}
PI = ("pi_iva", "pi_otros_productos", "pi_produccion")


BORDES_BRIDGE = {"Q_POT_GE_1": "q_pot", "S_T_MARG_NEGATIVE": "s_T_marg", "S_PI_MARG_NONPOSITIVE": "s_Pi_marg", "LAMBDA_NONPOSITIVE": "lambda_pi"}


def borde_contractual(razones):
    """rem64 (P4-P2-EQM-BORDE-CONTRACTUAL): borde de rules.EDGES de una inadmisibilidad de MC.bridge con la MISMA tabla explícita que
    paper2b.run._edge (la que usa Run.claim_holds para esta misma condición) pero SIN su valor por defecto: una razón desconocida o ausente
    no se clasifica (None) y el producto queda pendiente con su detalle original."""
    return BORDES_BRIDGE.get(razones[0]) if razones else None


def limite_busqueda(tb, tope_b, limite_global):
    """rem64 (P4-P2-RELOJ-RA): presupuesto POR BÚSQUEDA de tope_b segundos desde tb (inicio de la búsqueda, DESPUÉS de la preparación), como
    en el ensayo, acotado por el límite GLOBAL de la tarea; la preparación no descuenta del presupuesto de búsqueda."""
    return min(tb + tope_b, limite_global)


def limite_global_tarea(t_inicio, tope_tarea_s, margen_cierre_s):
    """Límite GLOBAL en producción: UNA tarea del plan con su tope externo admitido (tarea_con_cupo), desde el inicio del trabajador y menos el
    margen para validar y escribir productos. Granularidad: la tarea (no la unidad ni el bloque del ensayo); no se reinicia por unidad."""
    return t_inicio + tope_tarea_s - margen_cierre_s


def reloj_ev(tb, tope_b, limite_global):
    return {"inicio_busqueda_t": tb, "tope_busqueda_s": tope_b, "limite_global_t": limite_global, "limite_efectivo_t": limite_busqueda(tb, tope_b, limite_global),
            "limitada_por_global": limite_global < tb + tope_b}


class TestigoNoSerializable(ValueError):
    pass


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cargar(ctx, salida, espec):
    """Módulos R-A con el importador revisado, tras verificar dependencias y puerto contra la especificación SELLADA del plan."""
    for k in ("dependencias", "puerto"):
        f = AREA_RA / espec[k]["archivo"]
        if not f.resolve().is_relative_to(INSTALACION.resolve()):                 # rem70: nunca fuera de la instalación efectiva
            raise ValueError("EVALUADORES_RA_FUERA_DE_LA_INSTALACION: " + k)
        if not f.is_file():
            raise ValueError("EVALUADORES_RA_AUSENTES: " + k)
        if _sha(f) != espec[k]["sha256"]:
            raise ValueError("EVALUADORES_RA_DISTINTOS_DEL_PLAN: " + k)
    puerto = (AREA_RA / espec["puerto"]["archivo"]).resolve()
    pre = sys.modules.get("puerto_ra")                                           # rem70: un puerto precargado de otra ruta no se reutiliza
    if pre is not None and Path(getattr(pre, "__file__", "")).resolve() != puerto:
        raise ValueError("PUERTO_RA_DE_OTRA_RUTA")
    if str(puerto.parent) not in sys.path:
        sys.path.insert(0, str(puerto.parent))
    import puerto_ra as PRA
    if Path(PRA.__file__).resolve() != (AREA_RA / espec["puerto"]["archivo"]).resolve():
        raise ValueError("PUERTO_RA_DE_OTRA_RUTA")
    imp = PRA.ImportadorRA(ctx, salida)
    imp.instalar()
    M = {c: importlib.import_module(m) for c, m in ENTRADAS.items()}
    imp.guarda()
    if importlib.import_module("codigo.demo.nucleo_v").Contexto() is not ctx:
        raise ValueError("CONTEXTO_R_A_NO_INYECTADO")
    for m in M.values():
        m.COV.q_pot = m.q_pot_exact                 # como hacen los main ensayados (COV.q_pot = q_pot_exact)
    return M, imp


class Captura:
    """`log` de los cuerpos ensayados: conserva en memoria los registros de testigo (y cuenta los demás eventos)."""

    def __init__(self):
        self.testigos, self.eventos = [], {}

    def __call__(self, **kw):
        if "tipo" in kw and ("caja" in kw or "punto" in kw):
            self.testigos.append(kw)
        e = kw.get("evento", "testigo_m4" if "tipo" in kw else "otro")
        self.eventos[e] = self.eventos.get(e, 0) + 1


def estructural(EQ, ctx, prep, cid, pid, dirn, seg, tope_b, memo, limite_global):
    """PROD1: cuerpo del bucle de codigo.ensayo_quiebres.main para (cid, pid, dirn) de la especificación. Devuelve (bk, evidencia)."""
    C4, T, C2N, N, COV, RB, RUNMOD, COV_EPS = EQ.C4, EQ.T, EQ.C2N, EQ.N, EQ.COV, EQ.RB, EQ.RUNMOD, EQ.COV_EPS
    cfg = RUNMOD.RunConfig()
    nulo = lambda **kw: None  # noqa: E731
    log = Captura()
    tp = time.time()
    if cid not in prep and tp + tope_b > limite_global:          # rem65: ni la búsqueda sola cabe: no se prepara (nada se recorta)
        return None, {"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_limite_global", "momento": "antes_de_preparar",
                      "reloj": reloj_ev(tp, tope_b, limite_global)}
    if cid not in prep:
        try:
            prep[cid] = T.preparar(ctx, "G", [cid])
        except N.DemoError as e:
            prep[cid] = e
    st = prep[cid]
    if isinstance(st, N.DemoError):
        return None, {"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "preparacion_fallida", "error": str(st)}
    prep_s = round(time.time() - tp, 1)
    axes, fx = st["axes"], st["fixed"]
    root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
    sid = st["claims"][cid].support_sets[0]
    r = ctx.run(sid, "ensayo_quiebres:" + sid)
    lo, hi = (float(x) for x in r.inp.d7.interval(sid, pid))
    scale = r.inp.d7.support(sid, pid)["scale"] or "arithmetic"
    sts = {"G": dict(st, cand=[cid]), "N": dict(st, cand=[])}
    tb = time.time()
    if tb + tope_b > limite_global:          # rem64: la búsqueda ENTERA (tope_b desde tb) no cabe en el límite global de la tarea: no se recorta
        return None, {"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_limite_global", "preparacion_s": prep_s,
                      "reloj": reloj_ev(tb, tope_b, limite_global)}
    limite = limite_busqueda(tb, tope_b, limite_global)
    evals = []

    def claim_holds(iv, cid=cid, pid=pid, dirn=dirn, root=root, fx=fx, st=st, sts=sts, limite=limite, evals=evals, tb=tb):
        a, b = float(iv[0]), float(iv[1])
        box = dict(root, **{pid: (a, b)})
        te = time.time()
        res = None
        if te > limite:
            res = ("incomplete", None)
        elif not COV.box_admissible(box, fx):
            res = ("inadmissible", "box_admissible")
        else:
            nuevo = b if dirn == "superior" else a
            for av in ((nuevo,) if pid == "a" else (1.1, 1.3, 1.5, 2.0, 2.5)):
                pt = {p: ((v[0] + v[1]) / 2,) * 2 for p, v in box.items()}
                pt.update(a=(av, av), kappa_tilde=(box["kappa_tilde"][1],) * 2, rho=(box["rho"][1],) * 2, phi=(box["phi"][1],) * 2,
                          eta_f=(box["eta_f"][0],) * 2, z_cost=(box["z_cost"][0],) * 2, beta_tilde=(2.125, 2.125),
                          eta_d=(2.05, 2.05), u_theta=(0.5, 0.5))
                pt[pid] = (nuevo, nuevo)
                if not COV.box_admissible(pt, fx):
                    continue
                c2p = C2N.c2_normalizado(st["model"], pt, "G", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
                glo = max(COV.g_enclosure(st["model"], pt, cx, fx, c2p).lo for cx in st["univ"][cid])
                log(evento="sondeo", afirmacion=cid, eje=pid, direccion=dirn, intervalo=[a, b], a=av, C2=[c2p.lo, c2p.hi], G_lo=glo)
                if glo > -COV_EPS:
                    res = ("fails", [{"punto": {p: v[0] for p, v in pt.items()}, "G_lo": glo, "C2": [c2p.lo, c2p.hi]}])
                    break
            if res is None:
                resto = max(1.0, min(seg, limite - time.time()))
                n0 = len(log.testigos)
                rr = C4.cubrir_m4(sts, box, memo, ctx.identity_sha256, log, nulo, "%s %s %r" % (pid, dirn, [a, b]), resto, 400)
                est = rr["por_afirmacion"]["G|" + cid]["estado"]
                res = {"cerrada": ("holds", None), "testigo": ("fails", [{pid: [a, b], "registro_m4": log.testigos[n0:]}])}.get(est, ("incomplete", None))
        evals.append({"intervalo": [a, b], "resultado": res[0], "segundos": round(time.time() - te, 2), "acumulado_s": round(time.time() - tb, 1)})
        log(evento="evaluacion", afirmacion=cid, eje=pid, direccion=dirn, intervalo=[a, b], resultado=res[0])
        return res
    bk = RB.search("tecnologia", pid, None, dirn, lo, hi, scale, claim_holds, ladder=cfg.robustness_ladder,
                   bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified")
    return bk, {"reloj": reloj_ev(tb, tope_b, limite_global), "afirmacion": cid, "eje": pid, "direccion": dirn, "soporte_primario": [lo, hi], "escala": scale, "preparacion_s": prep_s,
                "busqueda_s": round(time.time() - tb, 1), "evaluaciones": evals, "status": bk.status, "computation_status": bk.computation_status,
                "reason": bk.reason, "r_critical": bk.r_critical, "bracket": bk.bracket, "reached_expansion_factor": bk.reached_expansion_factor,
                "evaluated_domain": bk.evaluated_domain, "witnesses": bk.witnesses, "eventos": dict(log.eventos)}


def _macro(EQM, ctx, prep, cid, pid, dirn, seg, tope_b, memo, limite_global, capt, causas):
    """PROD2: cuerpo del bucle de codigo.ensayo_quiebres_macro.main para (cid, pid, dirn). CAPTURA añadida: el contexto (índice de base y
    conjunto) que fija max G en el sondeo, y su vértice macro por Universo.meta; el valor de G no cambia (mismo máximo)."""
    C4, T, C2N, N, COV, RB, RUNMOD, COV_EPS = EQM.C4, EQM.T, EQM.C2N, EQM.N, EQM.COV, EQM.RB, EQM.RUNMOD, EQM.COV_EPS
    UniversoAmpliado, Inadmisible = EQM.UniversoAmpliado, EQM.Inadmisible
    cfg = RUNMOD.RunConfig()
    nulo = lambda **kw: None  # noqa: E731
    log = Captura()
    tp = time.time()
    if (cid, "G") not in prep and tp + tope_b > limite_global:   # rem65: ni la búsqueda sola cabe: no se prepara (nada se recorta)
        return None, {"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_limite_global", "momento": "antes_de_preparar",
                      "reloj": reloj_ev(tp, tope_b, limite_global)}
    if (cid, "G") not in prep:
        prep[(cid, "G")] = T.preparar(ctx, "G", [cid])
    st = prep[(cid, "G")]
    prep_s = round(time.time() - tp, 1)
    cl = st["claims"][cid]
    axes, fx = st["axes"], st["fixed"]
    root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
    s0 = cl.support_sets[0]
    r0 = st["runs"][s0]
    tb = time.time()
    if tb + tope_b > limite_global:          # rem64: la búsqueda ENTERA (tope_b desde tb) no cabe en el límite global de la tarea: no se recorta
        return None, {"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_limite_global", "preparacion_s": prep_s,
                      "reloj": reloj_ev(tb, tope_b, limite_global)}
    limite = limite_busqueda(tb, tope_b, limite_global)
    evals = []

    def claim_holds_ov(ov, etiqueta, cid=cid, cl=cl, st=st, fx=fx, root=root, limite=limite, evals=evals, tb=tb):
        te = time.time()
        res = None
        if te > limite:
            res = ("incomplete", None)
        else:
            U2 = UniversoAmpliado(st["U"], ov)
            capt.clear()
            try:
                cx, origen = [], []                                      # CAPTURA: (conjunto, índice de base) de cada contexto
                for sid in cl.support_sets:
                    c_, _ = U2.contexts(cl, sid, st["corner"])
                    cx += [x for x, _ in c_]
                    origen += [(sid, bi) for _, bi in c_]
            except Inadmisible as e:
                razones = list(capt.get("razones") or [])          # rem64: causa AUTÉNTICA capturada de MC.bridge; detalle original conservado
                res = ("inadmissible", borde_contractual(razones) or "PENDIENTE_SIN_CAUSA_CONTRACTUAL")
                causas.append({"sustitucion": etiqueta, "texto": "bridge:" + str(e)[:60], "razones": razones, "borde": res[1]})
            if res is None and not cx:
                res = ("incomplete", None)
            if res is None:
                for av in (1.1, 1.3, 1.5, 2.0, 2.5):          # sondeo de testigos de fallo (C2 alto, K1 bajo)
                    pt = {p: ((v[0] + v[1]) / 2,) * 2 for p, v in root.items()}
                    pt.update(a=(av, av), kappa_tilde=(root["kappa_tilde"][1],) * 2, rho=(root["rho"][1],) * 2, phi=(root["phi"][1],) * 2,
                              eta_f=(root["eta_f"][0],) * 2, z_cost=(root["z_cost"][0],) * 2, beta_tilde=(2.125, 2.125),
                              eta_d=(2.05, 2.05), u_theta=(0.5, 0.5))
                    if not COV.box_admissible(pt, fx):
                        continue
                    c2p = C2N.c2_normalizado(st["model"], pt, "G", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
                    gs = [COV.g_enclosure(st["model"], pt, c, fx, c2p).lo for c in cx]          # = max(... for c in cx), con su índice
                    k = max(range(len(gs)), key=gs.__getitem__)
                    glo = gs[k]
                    if glo > -COV_EPS:
                        sid_k, bi_k = origen[k]
                        res = ("fails", [{"punto": {p: v[0] for p, v in pt.items()}, "G_lo": glo, "C2": [c2p.lo, c2p.hi], "sustitucion": etiqueta,
                                          "contexto": {"conjunto": sid_k, "indice_base": bi_k, "meta": U2.meta(cl, sid_k, st["corner"], bi_k)}}])
                        break
            if res is None:
                resto = max(1.0, min(seg, limite - time.time()))
                sts = {"G": dict(st, cand=[cid], univ={cid: cx}), "N": dict(st, cand=[])}
                n0 = len(log.testigos)
                rr = C4.cubrir_m4(sts, root, memo, ctx.identity_sha256, log, nulo, "%s %s" % (pid, etiqueta), resto, 400)
                est = rr["por_afirmacion"]["G|" + cid]["estado"]
                res = {"cerrada": ("holds", None), "testigo": ("fails", [{pid: etiqueta, "registro_m4": log.testigos[n0:], "ov": {p: [str(x) for x in v] for p, v in ov.items()}}])}.get(est, ("incomplete", None))
        evals.append({"sustitucion": etiqueta, "resultado": res[0], "segundos": round(time.time() - te, 2), "acumulado_s": round(time.time() - tb, 1)})
        log(evento="evaluacion", afirmacion=cid, eje=pid, direccion=dirn, sustitucion=etiqueta, resultado=res[0])
        return res
    if pid == "eta_H":
        ladders = ctx.C.F["parameters"]["eta_H"]["sensitivity_ladders"]
        bk = RB.ladder_search("incidencia_laboral", "eta_H", ladders,
                              lambda lv: claim_holds_ov({"eta_H": [Decimal(str(x)) for x in lv]}, "eta_H=%s" % list(lv)), baseline_status="verified")
        dom = None
    else:
        p0 = "pi_iva" if pid == "pi_joint" else pid
        lo, hi = (float(x) for x in r0.inp.d7.interval(s0, p0))
        scale = "arithmetic" if pid == "pi_joint" else (r0.inp.d7.support(s0, p0)["scale"] or "arithmetic")
        sust = PI if pid == "pi_joint" else (pid,)
        comp = (cl.eta_w_block if pid == "eta_w" else p0.split("_", 1)[1]) if pid != "pi_joint" else None
        block = "incidencia_laboral" if pid == "eta_w" else "cuna_tributaria"
        bk = RB.search(block, None if pid == "pi_joint" else pid, comp, dirn, lo, hi, scale,
                       lambda iv: claim_holds_ov({p: [Decimal(repr(float(iv[0]))), Decimal(repr(float(iv[1])))] for p in sust}, "%r" % (list(iv),)),
                       ladder=cfg.robustness_ladder, bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified", joint=pid == "pi_joint")
        dom = [lo, hi]
    return bk, {"reloj": reloj_ev(tb, tope_b, limite_global), "afirmacion": cid, "eje": pid, "direccion": dirn, "soporte_primario": dom, "preparacion_s": prep_s, "busqueda_s": round(time.time() - tb, 1),
                "evaluaciones": evals, "status": bk.status, "computation_status": bk.computation_status, "reason": bk.reason,
                "r_critical": getattr(bk, "r_critical", None), "reached_expansion_factor": getattr(bk, "reached_expansion_factor", None),
                "evaluated_domain": getattr(bk, "evaluated_domain", None), "witnesses": bk.witnesses, "eventos": dict(log.eventos),
                "domain_edge_reached": getattr(bk, "domain_edge_reached", None), "boundary_kind": getattr(bk, "boundary_kind", None)}


def macro(EQM, ctx, prep, cid, pid, dirn, seg, tope_b, memo, limite_global):
    """PROD2: _macro con CAPTURA (rem64) de las razones auténticas de inadmisibilidad: MC.bridge se envuelve SOLO durante la unidad (misma
    llamada y misma respuesta) y se restaura siempre; las causas quedan en la evidencia junto al borde contractual derivado."""
    RUNMOD = EQM.RUNMOD
    capt, causas, puente = {}, [], RUNMOD.MC.bridge

    def puente_capturado(*a, **k):
        m = puente(*a, **k)
        if not m.admissible:
            capt["razones"] = list(getattr(m, "reasons", None) or [])
        return m
    RUNMOD.MC.bridge = puente_capturado
    try:
        bk, ev = _macro(EQM, ctx, prep, cid, pid, dirn, seg, tope_b, memo, limite_global, capt, causas)
    finally:
        RUNMOD.MC.bridge = puente
    ev["causas_inadmisibilidad"] = causas
    return bk, ev


def q_afirmacion(QS, ctx, cid, tope, phi_cache, reg, limite_global=float("inf")):
    """PROD3 (evidencia): cuerpo por afirmación de codigo.sensibilidad_q.main (Φ* continuo por rama y cota, m* = [mL, mU], comprobaciones
    código/fórmula/nudos/G-N). El paso a la fila contractual m_Q_critical por ámbito es una DECISIÓN pendiente (ver mapear_q)."""
    T, C2N, N, COV, RB, EPS_ECON, q_pot_exact, hashlib_ = QS.T, QS.C2N, QS.N, QS.COV, QS.RB, QS.EPS_ECON, QS.q_pot_exact, QS.hashlib
    phi_star = QS.phi_star
    t_ini = time.time()
    # rem64/rem65 (P4-P2-RELOJ-RA): la rama y cota entera (tope) debe caber en el límite global; nunca se recorta. Sin ninguna Φ* en caché no
    # puede haber acierto: se comprueba antes de preparar; con caché, la decisión se toma tras preparar, cuando se conoce la clave.
    if t_ini >= limite_global or (not phi_cache and t_ini + tope > limite_global):
        return {"estado": "no_iniciada_por_limite_global", "afirmacion": cid, "momento": "antes_de_preparar", "reloj": reloj_ev(t_ini, tope, limite_global)}
    D = float(ctx.inp.dme_gai)
    N.need(reg[cid]["categoria"] == "robusta_infactible_certificada", "NO_ROBUSTA")
    dis = cid.split(":")[-4]
    tp = time.time()
    st = T.preparar(ctx, dis, [cid])
    prep_s = round(time.time() - tp, 1)
    fx, axes = st["fixed"], st["axes"]
    root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
    cx = st["univ"][cid]
    import json
    clave = json.dumps({p: list(v) for p, v in root.items()}, sort_keys=True)
    tp = time.time()
    if clave not in phi_cache and tp + tope > limite_global:     # rem65: tras preparar, justo antes del cálculo NO cacheado
        return {"estado": "no_iniciada_por_limite_global", "afirmacion": cid, "momento": "tras_preparar", "preparacion_s": prep_s,
                "reloj": reloj_ev(tp, tope, limite_global)}
    cache_phi = clave in phi_cache
    if not cache_phi:
        phi_cache[clave] = phi_star(st["model"], root, fx, "G", tope, EPS_ECON)
    ph = phi_cache[clave]
    bb_s = round(time.time() - tp, 1)
    tp = time.time()
    filas = []
    for c in cx:
        Q = c.n_min - D
        filas.append({"Q": Q, "s_pi": c.s_pi, "gain": c.gain, "m_L": (ph["L"] * c.s_pi * c.gain - D) / Q, "m_U": (ph["U"] * c.s_pi * c.gain - D) / Q})
    mL = max(f["m_L"] for f in filas)
    mU = max(f["m_U"] for f in filas)
    ctx_s = round(time.time() - tp, 3)
    pt = ph["punto"]
    bpt = {p: (v, v) for p, v in pt.items()}
    c2pt = C2N.c2_normalizado(st["model"], bpt, dis, "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
    s_pt = q_pot_exact(bpt)
    uni = [{"C2": c2pt.lo, "err": c2pt.hi - c2pt.lo, "lambda": c.s_pi / (1.0 - s_pt.lo), "gain": c.gain, "D": D, "Qs": [c.n_min - D], "key": (i,)} for i, c in enumerate(cx)]
    r_cont = RB.q_sensitivity("robust_infeasible", uni)
    uni0 = [dict(u, err=0.0) for u in uni]
    r_cont0 = RB.q_sensitivity("robust_infeasible", uni0)
    phi_pt = (c2pt.lo + EPS_ECON) / (1.0 - s_pt.lo)
    m_pt = max((phi_pt * c.s_pi * c.gain - D) / (c.n_min - D) for c in cx)
    err_pt = c2pt.hi - c2pt.lo
    sid = st["claims"][cid].support_sets[0]
    nodos = N.axes_nodes(ctx, sid)
    uni_n = []
    tp = time.time()
    for i in range(60):
        vb = {}
        for p in COV.STRUCT:
            xs = [float(x) for x in nodos[p]]
            v = xs[int(hashlib_.sha256(("SEL-Q-NUDOS-v1|%d|%s" % (i, p)).encode()).hexdigest(), 16) % len(xs)]
            vb[p] = (v, v)
        if not COV.box_admissible(vb, fx):
            continue
        c2 = C2N.c2_normalizado(st["model"], vb, dis, "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
        s = q_pot_exact(vb)
        for k, c in enumerate(cx):
            uni_n.append({"C2": c2.lo, "err": c2.hi - c2.lo, "lambda": c.s_pi / (1.0 - s.lo), "gain": c.gain, "D": D, "Qs": [c.n_min - D], "key": (i, k)})
    nod_s = round(time.time() - tp, 1)
    r_nod = RB.q_sensitivity("robust_infeasible", uni_n)
    c2N = C2N.c2_normalizado(st["model"], bpt, "N", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
    a = {"afirmacion": cid, "diseno": dis, "contextos": len(cx), "preparacion_s": prep_s, "rama_y_cota_s": bb_s, "por_contexto_s": ctx_s, "Phi_estrella": ph,
         "m_estrella_continuo": [mL, mU], "estado_formula": "breakdown_found" if 0 < mL and mU < 1 else "ver",
         "codigo_universo_testigo": {"status": r_cont.status, "m_Q_critical": r_cont.m_Q_critical, "m_Q_critical_err0": r_cont0.m_Q_critical,
                                     "formula_en_el_punto": m_pt, "err_encierro_puntual": err_pt},
         "codigo_universo_nudos": {"status": r_nod.status, "m_Q_critical": r_nod.m_Q_critical, "nudos": 60, "filas": len(uni_n), "segundos": nod_s},
         "C2_G_igual_N_en_el_punto": [list((c2pt.lo, c2pt.hi)), list((c2N.lo, c2N.hi))],
         "contexto_argmax": max(range(len(filas)), key=lambda i: filas[i]["m_U"]), "filas_contexto": filas,
         # rem65: CAPTURA de datos ya calculados para la coherencia y la interpretación (D, máximo de m_L; desempate: menor índice)
         "D_dme_gai": D, "contexto_argmax_L": max(range(len(filas)), key=lambda i: filas[i]["m_L"]), "phi_desde_cache": cache_phi}
    a["comprobaciones"] = {
        "formula_igual_codigo_en_testigo_err0": r_cont0.m_Q_critical is not None and abs(r_cont0.m_Q_critical - m_pt) <= 1e-12 * max(1.0, abs(m_pt)),
        "codigo_con_err_conservador": r_cont.m_Q_critical is not None and r_cont.m_Q_critical >= r_cont0.m_Q_critical,
        "punto_testigo_dentro_del_encierro_continuo": mL - 1e-12 <= m_pt <= mU + 1e-12,
        "nudos_no_superan_continuo": r_nod.m_Q_critical is None or r_nod.m_Q_critical <= mU + 1e-12,
        "mismo_estado_nudos_y_continuo": r_nod.status == r_cont.status,
        "C2_G_igual_N": abs(c2pt.lo - c2N.lo) <= 1e-12 and abs(c2pt.hi - c2N.hi) <= 1e-12}
    return a


# ------------------------------------------------------------------------------------------- testigos -> contrato productivo
def testigos_contrato(familia, spec, bk, soporte):
    """[{parameter_id, value}] para Run.breakdown_row a partir de la evidencia R-A, SOLO con valores contenidos en ella:
    - sondeo estructural/macro: el punto evaluado (estructural) y el vértice macro del contexto que fija el máximo (macro, capturado);
    - cobertura M4: punto del registro (tipo centro) o la esquina de la HOJA en la dirección buscada (la hoja está certificada en toda su caja).
    Sin witnesses -> []. Si el valor no está en la evidencia -> TestigoNoSerializable (no se inventa a partir de r crítico)."""
    if not bk.witnesses:
        return []
    pid, d = spec["parametro"], spec["direccion"]
    params = list(PI) if pid == "pi_joint" else [pid]
    out = []
    for w in bk.witnesses:
        vals = {}
        if "punto" in w and familia == "PROD1":
            vals = {p: float(w["punto"][p]) for p in params if p in w["punto"]}
        elif "contexto" in w and familia == "PROD2":
            mv = (w["contexto"].get("meta") or {}).get("macro") or {}
            vals = {p: float(mv[p]) for p in params if p in mv}
        elif "registro_m4" in w:
            for rec in w["registro_m4"]:
                if "punto" in rec and all(p in rec["punto"] for p in params):
                    vals = {p: float(rec["punto"][p]) for p in params}
                    break
                if "caja" in rec and all(p in rec["caja"] for p in params):
                    vals = {p: float(rec["caja"][p][1] if d == "superior" else rec["caja"][p][0]) for p in params}
                    break
        if sorted(vals) != sorted(params):
            raise TestigoNoSerializable("TESTIGO_SIN_VALOR_EN_LA_EVIDENCIA: %s/%s" % (pid, d))
        out += [{"parameter_id": p, "value": vals[p]} for p in params]
    return out


DECISION_Q_V1 = "Q-CONTINUO-COTA-SUPERIOR-v1"
TEXTO_DECISION_Q_V1 = (
    "Q-CONTINUO-COTA-SUPERIOR-v1 (PROPUESTA; no activa sin sellarla en el plan como decision_q): para cada salida PROD3 (afirmación ci, ámbito "
    "global o país de la afirmación) la fila external_requirement_sensitivity_result se obtiene de la evidencia continua R-A sin nudos ni malla: "
    "(1) solo si Φ* convergió (U − L ≤ 1e-7) y todas las comprobaciones código/fórmula/nudos/G-N son verdaderas; si no, incomplete_search con "
    "motivo; (2) m_Q_critical := mU, cota SUPERIOR certificada del encierro [mL, mU] del m* continuo (análoga conservadora a C2 + err del núcleo); "
    "reduction_from_reported := 1 − mU; si el encierro cruza 0 o 1 no se decide el estado (incomplete_search); (3) testigo := gain_share del "
    "contexto que fija el máximo de m_U, con omega_id nulo (θ* es un punto del continuo, no un omega D7; θ*, Φ*, contextos y comprobaciones se "
    "conservan en la evidencia del documento); (4) el ámbito global y el del país producen la misma fila numérica porque el universo de una "
    "afirmación ci solo contiene su país (q_universe filtra por cl.countries = [país]).")
# rem65: v1 se CONSERVA (texto y sha256 77eeb567…) como historia; su redacción quedó superada por v2 (precisión de garantías y testigo, mismo
# cálculo y mismo contrato). Ninguna de las dos está firmada ni activa; mapear_q solo reconoce v2 y rechaza v1 por superada.
DECISION_Q_V2 = "Q-CONTINUO-COTA-SUPERIOR-v2"
TEXTO_DECISION_Q_V2 = (
    "Q-CONTINUO-COTA-SUPERIOR-v2 (PROPUESTA; sustituye la redacción v1 de sha256 77eeb567a9c183e8c934f67517196152da5f3b864346a35a5cc71adadd48c5ff "
    "sin cambiar el cálculo, el algoritmo ni el contrato; no activa sin sellarla en el plan como decision_q). Para cada salida PROD3 (afirmación ci; "
    "ámbito global o el país de la afirmación) la fila external_requirement_sensitivity_result se deriva de la evidencia continua R-A, sin nudos ni "
    "malla, así: (1) Admisión: la evidencia debe ser coherente (D finito e igual al del contexto cuando este se dispone; Φ* = [L, U] finito, ordenado, "
    "con brecha U − L registrada y no negativa y punto completo de Φ_L; las seis comprobaciones obligatorias con claves exactas, booleanas e iguales a "
    "su recálculo desde los números registrados; filas de contexto completas con Q > 0, s_π > 0, gain > 0 y m_L, m_U reconstruidos como "
    "(Φ_L·s_π·gain − D)/Q y (Φ_U·s_π·gain − D)/Q; [mL, mU] igual al máximo de las filas; índice del máximo de m_U entero, no booleano y con desempate "
    "por el menor índice). Evidencia incoherente: rechazo técnico; sin contextos: pendiente. (2) Convergencia: solo si U − L ≤ 1e-7 y las seis "
    "comprobaciones son verdaderas; si no, incomplete_search (Q_CONTINUO_NO_CONVERGIDO). (3) Interpretación: el umbral continuo m* pertenece a "
    "[mL, mU]; el núcleo describe pérdida de robustez para m < m* y el supremo puede no alcanzarse. Para todo m ≥ mU la infactibilidad robusta "
    "se mantiene; para todo m < mL se pierde, con el punto de Φ_L y el contexto del máximo de m_L como testigo; entre ambos no se decide. "
    "(4) Publicación: m_Q_critical := mU, COTA SUPERIOR de m*; reduction_from_reported := 1 − mU, COTA INFERIOR de la reducción crítica "
    "1 − m* ∈ [1 − mU, 1 − mL]: acota la región robusta (toda reducción ≤ 1 − mU queda sin quiebre) y NO demuestra que una reducción de 1 − mU "
    "baste para producir el quiebre; ni mU ni el punto de Φ_L son un quiebre exacto. breakdown_found significa que 0 < mL ≤ mU < 1, es decir, "
    "que existe m* en (0, 1); su posición solo se acota. Si mU ≤ 0: scale_range_exhausted_no_breakdown; si mL ≥ 1: no_solution "
    "(BASELINE_CONTRADICTION_M_GE_1); si el encierro contiene 0 o 1 sin quedar a un lado: incomplete_search (Q_ENCIERRO_CRUZA_UN_BORDE). "
    "(5) Testigo de la fila: gain_share del contexto que fija mU (primer índice del máximo de m_U), con omega_id nulo; identifica el contexto de "
    "la cota y no es un punto que la alcance. (6) La evidencia del documento conserva [mL, mU], Φ* (L, U, brecha, estado y punto de Φ_L), D, "
    "las filas de contexto, los índices de los máximos de m_U y m_L y las comprobaciones. (7) Ámbito global y del país producen la misma fila "
    "numérica porque el universo de una afirmación ci solo contiene su país.")
DECISIONES_Q = (DECISION_Q_V2,)
QBORDES = {"lo": 0.0, "hi": 1.0}
COMPROBACIONES_Q = ("C2_G_igual_N", "codigo_con_err_conservador", "formula_igual_codigo_en_testigo_err0", "mismo_estado_nudos_y_continuo",
                    "nudos_no_superan_continuo", "punto_testigo_dentro_del_encierro_continuo")
CAMPOS_FILA_Q = ("Q", "gain", "m_L", "m_U", "s_pi")


def _finito(x):
    import math
    return type(x) in (int, float) and math.isfinite(x)


def recalculo_comprobaciones_q(ev, mL, mU):
    """Las seis comprobaciones de q_afirmacion recalculadas con SUS fórmulas desde los números registrados en la evidencia (no desde ciencia
    nueva). Devuelve {clave: bool}; ValueError si faltan los números."""
    cut, nud, c2 = ev.get("codigo_universo_testigo"), ev.get("codigo_universo_nudos"), ev.get("C2_G_igual_N_en_el_punto")
    if not (isinstance(cut, dict) and isinstance(nud, dict) and isinstance(cut.get("status"), str) and isinstance(nud.get("status"), str)):
        raise ValueError("Q_COMPROBACIONES_SIN_NUMEROS: codigo_universo_testigo/nudos")
    m_pt, r0, rc, rn = cut.get("formula_en_el_punto"), cut.get("m_Q_critical_err0"), cut.get("m_Q_critical"), nud.get("m_Q_critical")
    if not (_finito(m_pt) and all(v is None or _finito(v) for v in (r0, rc, rn))):
        raise ValueError("Q_COMPROBACIONES_SIN_NUMEROS: m_Q")
    if not (isinstance(c2, list) and len(c2) == 2 and all(isinstance(x, list) and len(x) == 2 and all(_finito(y) for y in x) for x in c2)):
        raise ValueError("Q_COMPROBACIONES_SIN_NUMEROS: C2_G_igual_N_en_el_punto")
    return {"formula_igual_codigo_en_testigo_err0": r0 is not None and abs(r0 - m_pt) <= 1e-12 * max(1.0, abs(m_pt)),
            "codigo_con_err_conservador": rc is not None and r0 is not None and rc >= r0,
            "punto_testigo_dentro_del_encierro_continuo": mL - 1e-12 <= m_pt <= mU + 1e-12,
            "nudos_no_superan_continuo": rn is None or rn <= mU + 1e-12,
            "mismo_estado_nudos_y_continuo": nud["status"] == cut["status"],
            "C2_G_igual_N": abs(c2[0][0] - c2[1][0]) <= 1e-12 and abs(c2[0][1] - c2[1][1]) <= 1e-12}


def coherencia_q(ev, D_contexto=None):
    """rem65 (P4-P2-Q-VALIDACION-EVIDENCIA): COHERENCIA de la evidencia continua Q, sin recalcular ciencia. Comprueba finitud, orden y brecha de
    Φ*, punto completo de Φ_L (claves = paper2b.run.STRUCT), encierro [mL, mU] ordenado, claves EXACTAS y booleanas de las seis comprobaciones y su
    igualdad con el recálculo desde los números registrados, estado de la fórmula, contextos presentes y en número declarado, dominios (Q > 0,
    s_π > 0, gain > 0), m_L/m_U de cada contexto reconstruidos desde Φ, s_π, gain, D y Q, encierro global = máximo de las filas e índice del máximo
    de m_U (entero no booleano; desempate: menor índice). D se contrasta con el contexto cuando quien valida lo dispone (trabajador); en la
    aceptación común (sin contexto construido) se usa el D registrado en los bytes ligados. Es CONSISTENCIA de la evidencia: no certifica de forma
    independiente la optimización de Φ*. ValueError con la causa; TestigoNoSerializable si faltan los contextos (producto pendiente)."""
    def need(c, m):
        if not c:
            raise ValueError(m)
    D = ev.get("D_dme_gai")
    need(_finito(D), "Q_EVIDENCIA_SIN_D_FINITO")
    if D_contexto is not None:
        need(float(D) == float(D_contexto), "Q_D_DISTINTO_DEL_CONTEXTO")
    ph = ev.get("Phi_estrella")
    need(isinstance(ph, dict) and _finito(ph.get("L")) and _finito(ph.get("U")), "Q_PHI_NO_FINITO")
    L, U = float(ph["L"]), float(ph["U"])
    need(L <= U, "Q_PHI_ENCIERRO_INVERTIDO")
    need(_finito(ph.get("brecha")) and ph["brecha"] >= 0 and ph["brecha"] == U - L, "Q_PHI_BRECHA_INCOHERENTE")
    need(ph.get("estado") in ("convergido", "tope") and (ph["estado"] == "convergido") == (U - L <= 1e-7), "Q_PHI_ESTADO_INCOHERENTE")
    from paper2b.run import STRUCT
    pt = ph.get("punto")
    need(isinstance(pt, dict) and set(pt) == set(STRUCT) and all(_finito(v) for v in pt.values()), "Q_PHI_SIN_PUNTO_COMPLETO")
    me = ev.get("m_estrella_continuo")
    need(isinstance(me, list) and len(me) == 2 and all(_finito(x) for x in me), "Q_NO_FINITO")
    mL, mU = float(me[0]), float(me[1])
    need(mL <= mU, "Q_ENCIERRO_INVERTIDO")
    cm = ev.get("comprobaciones")
    need(isinstance(cm, dict) and set(cm) == set(COMPROBACIONES_Q), "Q_COMPROBACIONES_NO_EXACTAS")
    need(all(type(v) is bool for v in cm.values()), "Q_COMPROBACION_NO_BOOLEANA")
    rec = recalculo_comprobaciones_q(ev, mL, mU)
    mal = sorted(k for k in COMPROBACIONES_Q if cm[k] is not rec[k])
    need(not mal, "Q_COMPROBACION_DISTINTA_DE_SU_RECALCULO: %s" % mal)
    need(ev.get("estado_formula") == ("breakdown_found" if 0 < mL and mU < 1 else "ver"), "Q_ESTADO_FORMULA_INCOHERENTE")
    filas = ev.get("filas_contexto")
    if not isinstance(filas, list) or not filas:
        raise TestigoNoSerializable("TESTIGO_Q_SIN_CONTEXTO_EN_LA_EVIDENCIA")
    need(type(ev.get("contextos")) is int and ev["contextos"] == len(filas), "Q_CONTEXTOS_DISTINTOS_DE_LAS_FILAS")
    for i, f in enumerate(filas):
        need(isinstance(f, dict) and set(f) == set(CAMPOS_FILA_Q) and all(_finito(f[c]) for c in CAMPOS_FILA_Q), "Q_FILA_INCOMPLETA_O_NO_FINITA: %d" % i)
        need(f["Q"] > 0, "Q_DOMINIO_Q_NO_POSITIVO: %d" % i)
        need(f["s_pi"] > 0 and f["gain"] > 0, "Q_DOMINIO_S_PI_O_GAIN: %d" % i)
        for lado, phi in (("m_L", L), ("m_U", U)):
            m = (phi * f["s_pi"] * f["gain"] - D) / f["Q"]
            need(abs(m - f[lado]) <= 1e-12 * max(1.0, abs(m)), "Q_FILA_INCOHERENTE_CON_PHI: %s %d" % (lado, i))
    need(mL == max(f["m_L"] for f in filas) and mU == max(f["m_U"] for f in filas), "Q_ENCIERRO_GLOBAL_DISTINTO_DE_LOS_CONTEXTOS")
    k = ev.get("contexto_argmax")
    need(type(k) is int and 0 <= k < len(filas), "Q_ARGMAX_NO_ES_INDICE_ENTERO")
    need(k == max(range(len(filas)), key=lambda i: filas[i]["m_U"]), "Q_ARGMAX_NO_ES_EL_MAXIMO_DE_m_U")
    if "contexto_argmax_L" in ev:
        kl = ev["contexto_argmax_L"]
        need(type(kl) is int and kl == max(range(len(filas)), key=lambda i: filas[i]["m_L"]), "Q_ARGMAX_L_NO_ES_EL_MAXIMO_DE_m_L")
    return {"L": L, "U": U, "D": float(D), "mL": mL, "mU": mU, "k": k, "filas": filas, "conv": ph["estado"] == "convergido" and all(cm.values())}


def mapear_q(decision, spec, ev, ident, D_contexto=None):
    """PROD3: fila contractual y testigo de UNA salida (afirmación, ámbito) desde la evidencia continua R-A, con la decisión sellada en el plan
    (decision_q, citada en el vínculo). Primero exige la COHERENCIA de la evidencia (coherencia_q). No inventa escalar ni sustituye el
    continuo por nudos o malla."""
    if decision is None:
        raise ValueError("DECISION_Q_PENDIENTE: el paso del encierro continuo [mL, mU] a m_Q_critical por ámbito requiere sellar decision_q (TEXTO_DECISION_Q_V2)")
    if decision == DECISION_Q_V1:
        raise ValueError("DECISION_Q_SUPERADA: la redacción v1 (77eeb567…) se conserva como historia y se sustituye por v2; no se mapea")
    if decision not in DECISIONES_Q:
        raise ValueError("DECISION_Q_DESCONOCIDA: %s" % decision)
    scope, sc = spec["ambito"]
    if not (ident["claim_scope"] == "country_instrument" and ((scope == "global" and sc is None) or (scope == "country" and sc == ident["country_id"]))):
        raise ValueError("AMBITO_Q_NO_REPRESENTABLE: %s/%s" % (scope, sc))
    if ev.get("estado") == "no_iniciada_por_limite_global":
        raise ValueError("Q_NO_INICIADA_POR_LIMITE_GLOBAL")
    c = coherencia_q(ev, D_contexto)
    mL, mU = c["mL"], c["mU"]

    def fila(status, comp, m, motivo):
        return {"fila": {"m_Q_critical": m, "reduction_from_reported": None if m is None else 1 - m, "status": status, "computation_status": comp, "reason_code": motivo},
                "testigo": None}
    if not c["conv"]:
        return fila("incomplete_search", "incomplete", None, "Q_CONTINUO_NO_CONVERGIDO")
    if mU <= QBORDES["lo"]:
        return fila("scale_range_exhausted_no_breakdown", "complete", None, None)
    if mL >= QBORDES["hi"]:
        return fila("no_solution", "failed", None, "BASELINE_CONTRADICTION_M_GE_1")
    if mL <= QBORDES["lo"] or mU >= QBORDES["hi"]:
        return fila("incomplete_search", "incomplete", None, "Q_ENCIERRO_CRUZA_UN_BORDE")
    out = fila("breakdown_found", "complete", mU, None)
    out["testigo"] = {"parameter_id": "gain_share", "value": float(c["filas"][c["k"]]["gain"]), "omega_id": None}
    return out


def replica_arnes(EQm, ctx, spec, b, cl):
    """ARNÉS (NUNCA producción): RB.search / RB.ladder_search con los MISMOS argumentos que estructural/macro y, como claim_holds, los
    RESULTADOS DE EVALUACIÓN registrados en el ensayo i2 (b['evaluaciones']); si la secuencia diverge, error. La evidencia queda marcada
    REPLICA_ARNES y el validador la rechaza fuera del modo arnés. Inadmisibilidad sin causa conservada -> borde pendiente (no se inventa)."""
    RB, cfg = EQm.RB, EQm.RUNMOD.RunConfig()
    pid, d, fam = spec["parametro"], spec["direccion"], spec["familia"]
    s0 = cl.support_sets[0]
    r = ctx.run(s0, "PROD:" + cl.claim_id)
    evs, usados = list(b["evaluaciones"]), []
    testigo = b.get("witnesses") or [{"REPLICA_SIN_TESTIGO_SERIALIZADO_EN_I2": True}]

    def ch(lab):
        ex = evs[len(usados)]
        ref = ex["intervalo"] if fam == "PROD1" else ex["sustitucion"]
        if lab != ref:
            raise ValueError("REPLICA_DIVERGE: %r != %r" % (lab, ref))
        usados.append(lab)
        rr = ex["resultado"]
        if rr == "fails":
            return rr, testigo
        if rr == "inadmissible":
            return rr, ex.get("borde") or ("box_admissible" if fam == "PROD1" else "PENDIENTE_SIN_CAUSA_CONTRACTUAL")
        return rr, None
    if fam == "PROD1":
        lo, hi = (float(x) for x in r.inp.d7.interval(s0, pid))
        scale = r.inp.d7.support(s0, pid)["scale"] or "arithmetic"
        bk = RB.search("tecnologia", pid, None, d, lo, hi, scale, lambda iv: ch([float(iv[0]), float(iv[1])]), ladder=cfg.robustness_ladder,
                       bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified")
    elif pid == "eta_H":
        bk = RB.ladder_search("incidencia_laboral", "eta_H", ctx.C.F["parameters"]["eta_H"]["sensitivity_ladders"], lambda lv: ch("eta_H=%s" % list(lv)),
                              baseline_status="verified")
    else:
        p0 = "pi_iva" if pid == "pi_joint" else pid
        lo, hi = (float(x) for x in r.inp.d7.interval(s0, p0))
        scale = "arithmetic" if pid == "pi_joint" else (r.inp.d7.support(s0, p0)["scale"] or "arithmetic")
        comp = (cl.eta_w_block if pid == "eta_w" else p0.split("_", 1)[1]) if pid != "pi_joint" else None
        bk = RB.search("incidencia_laboral" if pid == "eta_w" else "cuna_tributaria", None if pid == "pi_joint" else pid, comp, d, lo, hi, scale,
                       lambda iv: ch("%r" % (list(iv),)), ladder=cfg.robustness_ladder, bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified",
                       joint=pid == "pi_joint")
    if len(usados) != len(evs):
        raise ValueError("REPLICA_INCOMPLETA: %d de %d" % (len(usados), len(evs)))
    ev = dict(b, origen_evidencia="REPLICA_ARNES", domain_edge_reached=bk.domain_edge_reached, boundary_kind=bk.boundary_kind)
    if fam == "PROD2":
        ev["witnesses"] = bk.witnesses
    return bk, ev


def identidad():
    return {"archivo": "herramientas/b/evaluadores_ra.py", "sha256": _sha(__file__)}
