"""Verificador CANDIDATO v2 de fichas de testigo (VERIFICADOR Y RENDIMIENTO 3.7, NO OFICIAL).

CORRECCIÓN respecto de v1 (validacion_testigos_3_7_2026-10-03/codigo/demo/verificador_testigos.py) y de la subclase
VerificadorContinuo (obstaculos_3_7_2026-10-03/codigo/demo/fichas_testigos.py), según el hallazgo del revisor:
- v1 registraba NO_ES_NUDO_DE_LA_MALLA en el paso 2 y RETORNABA antes de los pasos 3-8; la subclase filtraba después ese
  mensaje y devolvía [] sin haber ejecutado estado nacional, celda externa, contexto ni reproducción de G.
- v2: admitir puntos del continuo es una OPCIÓN EXPLÍCITA del verificador (`permitir_continuo`), comprobada dentro del
  paso 2: con la opción, un punto que no es nudo NO genera rechazo (se exige igual el soporte cerrado y la
  admisibilidad); sin la opción (evidencia de malla), sigue rechazándose. Nada se filtra al final.
- `verificar_completo` une en un único veredicto los pasos 1-6 y 8, la reproducción de C2 (paso 7) y, si se pide, la
  pertenencia al universo oficial: una ficha solo es válida si TODO pasa. Faltar o fallar C2 la invalida.
- La caché de C2 identifica el cálculo por valores, diseño, menú, cotas, todos los fijos, método y configuración del
  proveedor (struct_max_boxes, struct_tol, sup_max_boxes, jump_budget, tol_converge).

Texto original de v1:
3.7.1 — verificador CANDIDATO de la evidencia de testigos (VALIDACIÓN 3.7, NO OFICIAL; preregistro §3.7.1 V).

  <py_integracion> -m codigo.demo.verificador_testigos <evidencia.json> <salida.json> <tope_cooperativo_s>

No confía en los booleanos del censo ni en la categoría de la evidencia. Para cada ficha usa solo funciones oficiales
del núcleo (Run.states_for, Run.frontier_cases, Run.block_of, Run.ceiling, MC.bridge, la grilla autenticada, el
proveedor certificado y cobertura.g_enclosure) y comprueba:
  1 atributos de la afirmación (conjunto, diseño, instrumento, país, año, capa, cota);
  2 soporte: valores estructurales dentro del soporte y nudos de la malla; punto admisible; macro dentro de sus
    intervalos y en sus vértices; eta_H nudo; bloque de eta_w; fijos iguales a los del conjunto;
  3 estado nacional existente con esos atributos; s_pi y s_t recalculados iguales;
  4 celda externa del país y la capa, con Q de la cota igual y mínimo de (país, capa, cota);
  5 instrumento disponible para el país;
  6 contexto reconstruido igual al de la ficha;
  7 C2 recalculado con el método registrado e igual a la ficha (fase final, con caché por nudo y familia);
  8 G recalculado y desigualdad del rol: A: G.lo > -eps; B: G.hi < eps; pos: G.lo >= eps; neg: G.hi <= -eps;
  9 (muestra estratificada) contexto presente en el universo OFICIAL Run.claim_contexts.
Primero corre las pruebas de rechazo; después los pasos 1-6 y 8 (con el C2 de la ficha) para todas las fichas; luego
la muestra oficial; por último el paso 7. Si el tope corta, lo no verificado queda como tal.
"""
from __future__ import annotations

import copy
import json
import sys
import time
from decimal import Decimal
from pathlib import Path

from . import nucleo_v as N
from paper2b import claims as CL
from paper2b import cobertura as COV
from paper2b import run as RUNMOD
from paper2b.intervalos import Iv

EPS = CL.EPS_ECON
MACRO = ("eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion")


class Verificador:
    def __init__(self, ctx, permitir_continuo: bool = False):
        self.ctx = ctx
        self.permitir_continuo = bool(permitir_continuo)
        self.claims = {c.claim_id: c for c in ctx.claims}
        self.runs = {}
        self.grid = {g.external_cell_id: g for g in ctx.inp.grid_cells}
        self.c2cache = {}

    def run(self, sid):
        if sid not in self.runs:
            self.runs[sid] = self.ctx.run(sid, "verificador:" + sid)
        return self.runs[sid]

    def fixed(self, sid):
        d7 = self.run(sid).inp.d7
        return {pid: d7.nodes(sid, pid)[0] for pid in RUNMOD.FIXED + RUNMOD.BARS}

    def check(self, f: dict, cl, rol: str, c2_override=None) -> list:
        """Lista de motivos de rechazo (vacía = ficha válida para el rol) — pasos 1-6 y 8."""
        bad = []
        sid = f["conjunto"]
        if sid not in cl.support_sets:
            return ["CONJUNTO_FUERA_DE_LA_AFIRMACION"]
        r = self.run(sid)
        d7 = r.inp.d7
        en = f["estado_nacional"]
        ce = f["celda_externa"]
        if f["diseno"] != cl.design:
            bad.append("DISENO_DISTINTO")
        if f["instrumento"] not in cl.instruments:
            bad.append("INSTRUMENTO_FUERA_DE_LA_AFIRMACION")
        if f["pais"] not in cl.countries:
            bad.append("PAIS_FUERA_DE_LA_AFIRMACION")
        if en["anio_ancla"] not in cl.years:
            bad.append("ANIO_FUERA_DE_LA_AFIRMACION")
        if ce["capa"] != cl.layer:
            bad.append("CAPA_DISTINTA")
        if ce["cota"] != cl.bound_variant:
            bad.append("COTA_DISTINTA")
        # 2 soporte
        vals = {p: Decimal(f["valores_estructurales"][p]) for p in RUNMOD.STRUCT}
        from paper2b.supports import level_nodes
        for p in RUNMOD.STRUCT:
            nodes = [Decimal(str(x)) for x in level_nodes(d7.nodes(sid, p), d7.support(sid, p)["scale"], r.cfg.level)]
            if not (nodes[0] <= vals[p] <= nodes[-1]):
                bad.append("FUERA_DEL_SOPORTE:" + p)
            elif vals[p] not in nodes and not self.permitir_continuo:
                bad.append("NO_ES_NUDO_DE_LA_MALLA:" + p)
        fixed = self.fixed(sid)
        if {k: str(v) for k, v in fixed.items()} != f["fijos"]:
            bad.append("FIJOS_DISTINTOS")
        dbox = {p: (float(v), float(v)) for p, v in vals.items()}
        if not COV.box_admissible(dbox, fixed):
            bad.append("PUNTO_NO_ADMISIBLE")
        mv = {}
        for p in MACRO:
            lo, hi = d7.interval(sid, p)
            x = Decimal(f["macro"][p])
            mv[p] = x
            if x not in (Decimal(str(lo)), Decimal(str(hi))):
                bad.append("MACRO_FUERA_DE_VERTICES:" + p)
        mv["eta_H"] = Decimal(f["macro"]["eta_H"])
        if mv["eta_H"] not in [Decimal(str(x)) for x in d7.nodes(sid, "eta_H")]:
            bad.append("ETA_H_NO_ES_NUDO")
        if r.block_of(mv["eta_w"]) != cl.eta_w_block:
            bad.append("BLOQUE_DISTINTO")
        if bad:
            return bad
        # 3 estado nacional
        v = dict(vals, **{k: d7.interval(sid, k)[0] if Decimal(str(d7.interval(sid, k)[0])) == mv[k] else d7.interval(sid, k)[1]
                          for k in MACRO}, **fixed)
        v["eta_H"] = next(x for x in d7.nodes(sid, "eta_H") if Decimal(str(x)) == mv["eta_H"])
        sts = [st for st in r.states_for({"set": sid, "values": v}, f["pais"])
               if (st.preregistration_id, st.channel, st.edition, st.anchor_year, st.label, st.joint_domain_sha256)
               == (en["preregistro"], en["canal"], en["edicion"], en["anio_ancla"], en["etiqueta"], en["dominio_conjunto_sha256"])]
        if len(sts) != 1:
            return bad + ["ESTADO_NACIONAL_NO_ENCONTRADO"]
        m = RUNMOD.MC.bridge(sts[0].share_dict(), v)
        cx = f["contexto"]
        if float(m.s_Pi_marg) != cx["s_pi"] or float(m.s_T_marg) != cx["s_t"]:
            bad.append("S_PI_O_S_T_NO_REPRODUCIDO")
        # 4 celda externa
        g = self.grid.get(ce["id"])
        if g is None or g.country_id != f["pais"] or g.layer != cl.layer:
            bad.append("CELDA_EXTERNA_INVALIDA")
        else:
            qmin = min(x.Q(cl.bound_variant) for x in self.ctx.inp.grid_cells if x.country_id == f["pais"] and x.layer == cl.layer)
            if g.Q(cl.bound_variant) != ce["Q"] or ce["Q"] != qmin:
                bad.append("CELDA_NO_REALIZA_MIN_Q")
            if cx["n_min"] != qmin + r.inp.dme_gai:
                bad.append("N_MIN_NO_REPRODUCIDO")
        # 5 disponibilidad
        if not [c for jj, c, av, _ in r.frontier_cases(f["pais"]) if jj == f["instrumento"] and av]:
            bad.append("INSTRUMENTO_NO_DISPONIBLE")
        # 6 contexto
        c = COV.Context(cl.design, f["instrumento"], (float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])), float(m.s_Pi_marg),
                        float(m.s_T_marg), float(v["eta_H"]), float(v["gain_share"]), cx["n_min"])
        if (c.s_pi, c.s_t, c.eta_h, c.gain, c.n_min) != (cx["s_pi"], cx["s_t"], cx["eta_h"], cx["gain"], cx["n_min"]) \
                or list(c.bars) != f["cotas_fiscales"] or c.instrument != f["instrumento"] or c.design != f["diseno"]:
            bad.append("CONTEXTO_NO_REPRODUCIDO")
        # 8 G y desigualdad
        c2 = c2_override if c2_override is not None else Iv(f["C2"]["lo"], f["C2"]["hi"])
        gg = COV.g_enclosure(r.model, dbox, c, fixed, c2)
        if gg is None:
            return bad + ["G_SIN_ENCIERRO"]
        if c2_override is None and [gg.lo, gg.hi] != f["G"]:
            bad.append("G_NO_REPRODUCIDO")
        ok = {"A": gg.lo > -EPS, "B": gg.hi < EPS, "pos": gg.lo >= EPS, "neg": gg.hi <= -EPS}[rol]
        if not ok:
            bad.append("DESIGUALDAD_NO_RESPALDADA:" + rol)
        f["_ctx"], f["_dbox"], f["_fixed"] = c, dbox, fixed
        return bad

    def c2_key(self, f):
        """Identidad completa del cálculo de C2 (todo lo que lo afecta)."""
        sid = f["conjunto"]
        r = self.run(sid)
        m, sup = r.model, r.cfg.sup
        return (tuple(sorted(f["valores_estructurales"].items())), f["diseno"], f["instrumento"], tuple(f["cotas_fiscales"]),
                tuple(sorted((k, str(v)) for k, v in self.fixed(sid).items())), f["C2"]["metodo"],
                ("struct_max_boxes", m.struct_max_boxes), ("struct_tol", m.struct_tol), ("sup_max_boxes", m.sup_max_boxes),
                ("jump_budget", m.jump_budget), ("tol_converge", getattr(sup, "tol_converge", None)), ("proveedor", m.kind))

    def verificar_completo(self, f, cl, rol, oficial=True):
        """Veredicto único: pasos 1-6 y 8, reproducción de C2 (7) y, si oficial, pertenencia a Run.claim_contexts."""
        g = copy.deepcopy(f)
        motivos = self.check(g, cl, rol)
        e, secs = self.c2(f)
        c2_igual = e is not None and [e.lo, e.hi] == [f["C2"]["lo"], f["C2"]["hi"]]
        if not c2_igual:
            motivos = motivos + ["C2_NO_REPRODUCIDO"]
        en_oficial = None
        if oficial and "_ctx" in g:
            sid = f["conjunto"]
            corner = {p: Decimal(f["valores_estructurales"][p]) for p in RUNMOD.STRUCT}
            ctxs, _ = self.run(sid).claim_contexts(cl, sid, corner)
            en_oficial = g["_ctx"] in ctxs
            if not en_oficial:
                motivos = motivos + ["FUERA_DEL_UNIVERSO_OFICIAL"]
        elif oficial:
            en_oficial = False
        return {"motivos": motivos, "c2_reproducido": c2_igual, "c2_recalculado": None if e is None else [e.lo, e.hi],
                "c2_segundos": secs, "en_universo_oficial": en_oficial, "valida": not motivos}

    def c2(self, f):
        """Paso 7: C2 con el método registrado (caché con identidad completa: c2_key)."""
        sid = f["conjunto"]
        r = self.run(sid)
        vals = {p: Decimal(f["valores_estructurales"][p]) for p in RUNMOD.STRUCT}
        key = self.c2_key(f)
        if key not in self.c2cache:
            a = time.time()
            fixed = self.fixed(sid)
            dbox = {p: (float(v), float(v)) for p, v in vals.items()}
            if f["C2"]["metodo"] == "capture_ceiling_punto":
                _, hit = r.ceiling(dict(vals, **fixed), f["diseno"], f["instrumento"])
                ce = hit["ceiling"]
                e = None if ce.C2 is None or ce.numerical_error is None else Iv.point(ce.C2) + Iv(-float(ce.numerical_error), float(ce.numerical_error))
            else:
                e = r.model.c2_struct_enclosure(dbox, f["diseno"], f["instrumento"], f["cotas_fiscales"][0], f["cotas_fiscales"][1], fixed=fixed)
            self.c2cache[key] = (e, round(time.time() - a, 3))
        return self.c2cache[key]


def fichas_de(s):
    """(rol, ficha) que deciden la afirmación: pos/neg si existen; si no, A/B."""
    out = []
    if s.get("pos") and s.get("neg"):
        out += [("pos", s["pos"]), ("neg", s["neg"])]
    else:
        if s.get("A"):
            out.append(("A", s["A"]))
        if s.get("B"):
            out.append(("B", s["B"]))
    return out


def pruebas_rechazo(V, ev):
    """Cuatro mutaciones de fichas válidas; cada una debe rechazarse con el motivo esperado."""
    claims = V.claims
    dec = [(cid, s) for cid, s in sorted(ev.items()) if s.get("A") and s.get("B")]
    cid, s = dec[0]
    f0 = s["A"]
    out = []
    f1 = copy.deepcopy(f0); f1["valores_estructurales"]["a"] = "2.6"
    out.append(("testigo_fuera_del_soporte", V.check(f1, claims[cid], "A"), "FUERA_DEL_SOPORTE"))
    otro = next(c for c in sorted(claims) if c != cid and claims[c].preregistration_id == claims[cid].preregistration_id
                and claims[c].layer != claims[cid].layer and claims[c].claim_scope == claims[cid].claim_scope)
    out.append(("contexto_de_otra_afirmacion", V.check(copy.deepcopy(f0), claims[otro], "A"), "CAPA_DISTINTA"))
    f3 = copy.deepcopy(f0); f3["C2"]["lo"] -= 0.5; f3["C2"]["hi"] -= 0.5
    out.append(("C2_alterado", V.check(f3, claims[cid], "A"), "G_NO_REPRODUCIDO"))
    fneg = next((x["neg"] for _, x in sorted(ev.items()) if x.get("neg")), None)
    out.append(("desigualdad_no_respaldada", V.check(copy.deepcopy(fneg), claims[next(c for c, x in sorted(ev.items()) if x.get("neg") is fneg)], "A"),
                "DESIGUALDAD_NO_RESPALDADA"))
    return [{"prueba": n, "motivos": m, "esperado": e, "rechazada_como_se_esperaba": any(x.startswith(e) for x in m)} for n, m, e in out]


def main():
    evp, out, budget = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])
    t0 = time.time()
    raw = evp.read_bytes()
    ev = json.loads(raw)["afirmaciones"]
    ctx = N.Contexto()
    V = Verificador(ctx)
    doc = {"etiqueta": N.ETIQUETA, "evidencia_sha256": N.sha(raw), "identidad_sha256": ctx.identity_sha256, "parada": None}
    doc["pruebas_de_rechazo"] = pruebas_rechazo(V, ev)
    N.write_json_atomic(out, doc)
    res = {}
    for cid, s in sorted(ev.items()):
        fs = fichas_de(s)
        if not fs:
            continue
        motivos = {rol: V.check(f, V.claims[cid], rol) for rol, f in fs}
        res[cid] = {"roles": [r for r, _ in fs], "motivos": motivos, "pasos_1_6_8_ok": all(not m for m in motivos.values()),
                    "categoria_evidencia": s.get("categoria")}
    doc["fichas"] = res
    doc["t_pasos_1_6_8_s"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    # 9 muestra oficial: primera afirmación de cada (ruta, alcance, menú, diseño, cota, bloque)
    grupos = {}
    for cid in sorted(res):
        cl = V.claims[cid]
        grupos.setdefault((cl.preregistration_id, cl.claim_scope, cl.instrument_j, cl.design, cl.bound_variant, cl.eta_w_block), cid)
    muestra = {}
    for g, cid in sorted(grupos.items()):
        if time.time() - t0 > budget * 0.5:
            doc["parada"] = "TOPE_EN_MUESTRA_OFICIAL"
            break
        cl = V.claims[cid]
        okr = True
        for rol, f in fichas_de(ev[cid]):
            if "_ctx" not in f:
                V.check(f, cl, rol)
            sid = f["conjunto"]
            corner = {p: Decimal(f["valores_estructurales"][p]) for p in RUNMOD.STRUCT}
            ctxs, _ = V.run(sid).claim_contexts(cl, sid, corner)
            okr = okr and f.get("_ctx") in ctxs
        muestra[cid] = okr
    doc["muestra_universo_oficial"] = {"grupos": len(grupos), "verificadas": len(muestra), "en_universo": sum(muestra.values()),
                                       "detalle": muestra}
    N.write_json_atomic(out, doc)
    # 7 C2 recalculado: primero d y f (baratos), después df
    pend = [(cid, rol, f) for cid, s in sorted(ev.items()) for rol, f in fichas_de(s)]
    pend.sort(key=lambda x: (x[2]["instrumento"] == "df", x[2]["C2"]["metodo"] == "capture_ceiling_punto"))
    c2ok, c2bad, c2no = 0, [], 0
    tiempos = []
    for cid, rol, f in pend:
        if time.time() - t0 > budget:
            doc["parada"] = "TOPE_EN_C2"
            c2no += 1
            continue
        e, secs = V.c2(f)
        tiempos.append(secs)
        if e is not None and [e.lo, e.hi] == [f["C2"]["lo"], f["C2"]["hi"]]:
            c2ok += 1
        else:
            c2bad.append({"afirmacion": cid, "rol": rol, "ficha": [f["C2"]["lo"], f["C2"]["hi"]], "recalculado": None if e is None else [e.lo, e.hi]})
    doc["c2_recalculado"] = {"fichas": len(pend), "iguales": c2ok, "distintos": c2bad[:50], "n_distintos": len(c2bad),
                             "no_verificadas_por_tope": c2no, "encierros_distintos_recalculados": len(V.c2cache),
                             "segundos_por_encierro": sorted(tiempos)[-5:] if tiempos else []}
    ok_total = [cid for cid, x in res.items() if x["pasos_1_6_8_ok"]]
    doc["resumen"] = {"afirmaciones_con_fichas": len(res), "fichas_validas_pasos_1_6_8": len(ok_total),
                      "rechazadas": {cid: x["motivos"] for cid, x in res.items() if not x["pasos_1_6_8_ok"]},
                      "pruebas_de_rechazo_ok": all(x["rechazada_como_se_esperaba"] for x in doc["pruebas_de_rechazo"])}
    doc["consumido_s"] = round(time.time() - t0, 1)
    doc["parada"] = doc["parada"] or "COMPLETO"
    for s in ev.values():
        for k in ("pos", "neg", "A", "B"):
            if s.get(k):
                for z in ("_ctx", "_dbox", "_fixed"):
                    s[k].pop(z, None)
    N.write_json_atomic(out, doc)
    print(json.dumps({"resumen": {k: v for k, v in doc["resumen"].items() if k != "rechazadas"}, "c2": {k: v for k, v in doc["c2_recalculado"].items() if k != "distintos"},
                      "muestra": {k: v for k, v in doc["muestra_universo_oficial"].items() if k != "detalle"}, "parada": doc["parada"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
