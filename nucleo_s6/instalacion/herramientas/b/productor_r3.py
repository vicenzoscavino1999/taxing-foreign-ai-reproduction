"""PRODUCTOR S2/S3 POR LISTA (R3; candidato S6; NO OFICIAL). Misma secuencia que el productor histórico de las 27 unidades R3
(codigo/piloto_detallado.py 4ef36262… —idéntico en lima1533, lima1855, lima2213, lima0200, lima1009, lima1324 y lima1738—,
Piloto.celda_componentes, usada por bloque_s1.trabajador_c): prefijo del ω
estructural en L0 (S2) o prefijo de la tarea (S3) -> Run -> ω del prefijo elegido por la regla B (S2: regla_b_v2.indice sobre el estrato y
k; S3: sel_omega) -> COMPROBACIÓN de ω exacto -> [CÁLCULO] techo -> frontera -> estados macro -> celda externa -> celda -> E12 (con la
ruta no aplicable para las NA) -> exportación del CONTRATO v3 (contrato_paquete.filas_de_celda(..., "v3")).
La definición de cada unidad es la del manifiesto histórico VINCULADO a su original (vinculo_paso4, tipo «definicion»); nada se
reconstruye con identidad S6. `previas` se detiene ANTES del techo (sin cálculo costoso). `celda` es CÁLCULO CIENTÍFICO: solo tras
la admisión del coordinador con autorización.
regla_b_v2.py y e12_celda.py se cargan de la raíz S6 del despliegue y se exige su sha256 (= el de los lotes históricos y el original).
  P = ProductorR3(ctx, ref, GC, raiz_proyecto, almacen=None); P.previas(definicion) / P.celda(definicion, progreso)
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import time
from decimal import Decimal
from pathlib import Path

FIJADOS = {"regla_b_v2": ("herramientas/b/regla_b_v2.py", "b138dec4e9daaff5b226f4fca87dd3ff3d51ab9586b401a00074aed9e00a4790"),   # = lotes R3 históricos
           "e12_celda": ("herramientas/b/e12_celda.py", "4f30b3f054394e929bac50536ecae67f2ed53b8cf617e5741778e79d0b1a96b0")}    # (lima1533…lima1738)


class ProductorR3Error(RuntimeError):
    pass


class ProductorR3:
    def __init__(self, ctx, ref, GC, raiz_proyecto, almacen=None):
        from paper2b import run as RUN
        self.ctx, self.ref, self.GC, self.RUN, self.store = ctx, ref, GC, RUN, (almacen if almacen is not None else {})
        mods = {}
        for nombre, (rel, h) in FIJADOS.items():
            p = Path(raiz_proyecto) / rel
            if hashlib.sha256(p.read_bytes()).hexdigest() != h:
                raise ProductorR3Error("MODULO_DISTINTO_DEL_FIJADO:" + rel)
            if "r3_" + nombre not in sys.modules:
                sp = importlib.util.spec_from_file_location("r3_" + nombre, p)
                m = importlib.util.module_from_spec(sp)
                sys.modules["r3_" + nombre] = m
                sp.loader.exec_module(m)
            mods[nombre] = sys.modules["r3_" + nombre]
        self.RB, self.E12C = mods["regla_b_v2"], mods["e12_celda"]

    def run(self, sid, prefijo, etq):
        r = self.RUN.Run(self.ctx.inp, self.ctx.cfg, unit={"unit_id": "r3:%s:%s" % (etq[:24], sid), "set_id": sid, "prefix": dict(prefijo)},
                         techos_compartidos=self.store)
        if not (r.model.kind == "modelo_teorico_v2_2" and r.model.certified):
            raise ProductorR3Error("PROVEEDOR_NO_CERTIFICADO")
        if hasattr(self.store, "vincular"):
            self.store.vincular(r)
        return r

    def prefijo_de(self, sid, omega_estructural):
        nod = self.GC.CE.axes_nodes(self.ctx.view, self.ctx.cfg, sid)
        pre = {}
        for p in self.RUN.STRUCT:
            v = Decimal(str(omega_estructural[p]))
            idx = [i for i, x in enumerate(nod[p]) if Decimal(str(x)) == v]
            if len(idx) != 1:
                raise ProductorR3Error("OMEGA_ESTRUCTURAL_FUERA_DE_L0:%s" % p)
            pre[p] = idx[0]
        return pre

    def previas(self, rep):
        """Hasta la frontera del cálculo: prefijo, Run, ω elegido por la regla y ω exacto = declarado. Devuelve (ok, pre, datos)."""
        CE = self.GC.CE
        a = time.time()
        prefijo = rep["tarea"]["prefix"] if rep["familia"] == "S3" else self.prefijo_de(rep["conjunto"], rep["omega_estructural"])
        r = self.run(rep["conjunto"], prefijo, rep["id"])
        oids = CE.omega_list(r)
        if not oids:
            return False, {"omega_en_el_prefijo": False}, {"r": r, "prefijo": prefijo}
        if rep["familia"] == "S3":
            oid = oids[rep["tarea"]["sel_omega"] % len(oids)]
        else:
            oid = oids[self.RB.indice(list(rep["estrato"]), int(rep["k"]), "omega_vertice", len(oids))]
        vals = r.omegas[oid]["values"]
        decl = rep["tarea"]["valores"] if rep["familia"] == "S3" else rep["omega_estructural"]
        exacto = all(Decimal(str(vals[p])) == Decimal(str(decl[p])) for p in self.GC.STRUCT)
        pre = {"omega_en_el_prefijo": True, "omega_exacto": exacto, "n_omegas_del_prefijo": len(oids)}
        return exacto, pre, {"r": r, "oid": oid, "oids": oids, "prefijo": prefijo, "previas_s": round(time.time() - a, 3)}

    def celda(self, rep, progreso=None):
        """CÁLCULO CIENTÍFICO (solo con autorización): la secuencia histórica completa. Devuelve (resultado, filas_v3, run)."""
        from paper2b import contrato_paquete as CP
        GC, RB, CE = self.GC, self.RB, self.GC.CE
        progreso = progreso if progreso is not None else {}
        t = {}
        ok, pre, dd = self.previas(rep)
        r = dd["r"]
        sid, pais, d, j, case, bound = rep["conjunto"], rep["pais"], rep["diseno"], rep["menu"], rep["caso"], rep["cota"]
        t["previas_s"] = dd.get("previas_s")
        res = {"etiqueta": rep["id"], "set_id": sid, "omega_id": dd.get("oid"), "n_omegas_del_prefijo": pre.get("n_omegas_del_prefijo"),
               "omega_exacto": pre.get("omega_exacto"), "pais": pais, "diseno": d, "instrumento": j, "caso": case, "prefijo": dd["prefijo"]}
        if not pre.get("omega_en_el_prefijo"):
            return dict(res, estado="salida_invalida", motivos=["sin ω admisible en el prefijo"]), None, r
        if not ok:
            return dict(res, estado="rechazada_antes_del_calculo", motivos=["ω estructural distinto del declarado"], tiempos_s=t), None, r
        oid = dd["oid"]
        progreso.update(fase="techo", t=time.time())
        b = time.time()
        fr, secs, skey, reuso = GC.Compartido(activo=False).techo(r, oid, pais, d, j, case)
        t["techo_s"] = round(time.time() - b, 3)
        res.update(clave_estructural=skey, frontier_id=fr["frontier_id"], techo_reutilizado_entre_conjuntos=reuso)
        progreso.update(fase="macro", t=time.time())
        b = time.time()
        macs = CE.macro_states(r, oid, pais, d, j, case)
        t["macro_s"] = round(time.time() - b, 3)
        if not macs:
            return dict(res, estado="salida_invalida", motivos=["sin estados macro"], tiempos_s=t), None, r
        if rep["familia"] == "S3":
            tk = rep["tarea"]
            mac = macs[tk["sel_estado"] % len(macs)]
            gcs = CE.grid_cells(r, pais)
            gcell = gcs[tk["sel_celda"]] if tk["sel_celda"] < len(gcs) else None
        else:
            mac = macs[RB.indice(list(rep["estrato"]), int(rep["k"]), "estado_macro", len(macs))]
            gcl = [g for g in CE.grid_cells(r, pais) if g.external_cell_id == rep["celda_externa"]]
            gcell = gcl[0] if len(gcl) == 1 else None
        if gcell is None:
            return dict(res, estado="salida_invalida", motivos=["celda externa no única o fuera de rango"], tiempos_s=t), None, r
        res.update(n_estados_macro=len(macs), macro_id=mac["row"]["macro_id"], estado_macro=GC.state_meta(mac["state"]), celda_externa=gcell.external_cell_id)
        progreso.update(fase="celda", t=time.time())
        b = time.time()
        cid = CE.build_cell(r, oid, pais, d, j, case, fr, mac, gcell, bound)
        t["resto_celda_s"] = round(time.time() - b, 3)
        hit = fr.get("hit") or {}
        rate = r.inp.d7.rates.get(pais)
        tasa = float(rate["value"]) if (rate is not None and rate.get("status") == "verified") else None
        barras = tuple(hit.get("bars") or (None, None))
        # E12 con la ruta NO APLICABLE (e12_celda fijado; delega en paper2b.rules si el instrumento está disponible), como el histórico
        comp = self.E12C.verificar_celda(r.rows, cid, fr["frontier_id"], instrumento=j, barras=barras, tasa=tasa, run_geometry=bool(r.cfg.run_geometry),
                                         con_unidad=r.unit is not None, omega_id=oid)
        estado = {"invalida": "salida_invalida", "incompleta": "incompleta", "no_aplicable": "no_aplicable"}.get(comp["estado"], "ok")
        filas = CP.filas_de_celda(r.rows, cid, fr["frontier_id"], "v3")                     # CONTRATO v3, como el histórico
        ce = filas["capture_ceiling_result"][0] if len(filas.get("capture_ceiling_result") or []) == 1 else {}
        conf = filas["confrontation_result"][0] if len(filas.get("confrontation_result") or []) == 1 else {}
        res.update(estado=estado, motivos=list(comp["motivos"]), completitud=comp, cell_id=cid, tiempos_s=t,
                   techo={k: ce.get(k) for k in ("C_2", "numerical_error", "computation_status", "reason_code", "sup_not_attained")},
                   confrontacion={k: conf.get(k) for k in ("G", "K_comp_1", "verdict", "computation_status", "reason_code")},
                   clave_E12={"cell_id": cid, "frontier_id": fr["frontier_id"], "instrumento": j, "barras": list(barras), "tasa": tasa,
                              "run_geometry": bool(r.cfg.run_geometry), "con_unidad": r.unit is not None, "omega_id": oid})
        return res, filas, r
