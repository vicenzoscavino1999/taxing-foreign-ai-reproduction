"""VALIDACIÓN DETALLADA v2 (VALIDACION DETALLADA Y D-S1-d H4 3.7, NO OFICIAL). Sustituye a la validación del piloto
(codigo/piloto_detallado.py:validar v1), que aceptaba K_comp_1/G alterados, un ω falseado en el manifiesto y evidencias de
convergencia fallidas porque confiaba en banderas del productor (omega_exacto, poscomprobaciones) y solo comprobaba la
presencia de filas.

  <py> -B -m codigo.validar_detallado piloto <manifiesto.json> <dir_resultados> <salida.json>      (evidencia HISTÓRICA lima2201)
  <py> -B -m codigo.validar_detallado bloque <preregistro.json> <dir_resultados> <salida.json>     (D-S1-d, esta ronda)

Nada se toma del resultado sin reconstruirlo. Por celda, grupos de comprobaciones (cada uno rechaza por sí solo):
1. PROCEDENCIA: manifiesto y resultados autenticados (histórico: bytes iguales al inventario de su entrega; bloque: sha del
   manifiesto igual al preregistrado y resultado ligado a la identidad del productor preregistrada).
2. MANIFIESTO: la fila del representante se REGENERA desde las fuentes autenticadas (censo, selección, hojas, tareas,
   certificados) y debe ser idéntica a la dada.
3. IDENTIDAD por contenido, en el contexto S5 de la run_class de la evidencia (sin reasignar identidades): ω reconstruido
   (punto del testigo o prefijo L0 + regla de vértice) con valores EXACTOS; contexto y K1 del testigo; cell_id del censo por
   contenido; run_id, frontier_id, ceiling_id, macro_id y cell_id recalculados con las fórmulas del núcleo; clave
   estructural y su carga (contrato) y huellas técnicas; caso D4 y disponibilidad; celda externa de la grilla autenticada;
   estado nacional y su sha.
4. NÚMEROS: λ_π recalculado desde el estado nacional (macro.bridge); K_comp_1 = (Q+dme)/(λ_π·y) desde la grilla y el ω;
   K_comp_1 dentro de K1 de la Referencia E13 en el contexto del testigo (S1/C2); C_2 de la confrontación = C_2 del techo;
   G = C_2 - K_comp_1; veredicto recalculado; techo complete con 0 <= error <= tol_converge (1e-7); C_2 ± error dentro del
   certificado del testigo (S1/C2).
5. EVIDENCIAS: fila de G recalculada (convergencia.fila_G) e idéntica; toda evidencia consumida (G, R1, INV) con estado y
   cobertura coherentes con el resultado que respalda y cambio <= su tolerancia; inversiones sin cifra si su estado no la
   admite; E12 re-verificada (candidato e12_celda: delega en paper2b.rules para instrumentos disponibles) con las claves
   RECONSTRUIDAS y estado "completa".
6. ESQUEMA: cualquier archivo, tabla, campo o tipo inválido -> rechazo controlado con motivo (nunca excepción).
Ruta no aplicable (instrumento no disponible): misma identidad y procedencia; E12 debe dar "no_aplicable" y la celda se
clasifica no_aplicable_validada (NUNCA completo numérico).
"""
import hashlib
import json
import math
import sys
import time
import traceback
from decimal import Decimal
from pathlib import Path

A = Path(__file__).resolve().parents[1]
T = A.parent
TOL_CONVERGE = 1e-7          # tol_converge del techo de celda (NO es T2_G)
T2_G = 1e-4                  # tolerancia de la evidencia de G (convergencia.T2_G); no intercambiables
TOL_REL = 1e-12              # redondeo relativo admitido en relaciones de forma cerrada (G = C2 - K)
L2201 = ("fase_detallada_piloto_h4_paso4_3_7_2026-10-09_lima2201", "1f81beca84009c710fe23a427644f4c15260475fb70052862a89613596ebf3a8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def norm(x):
    return json.loads(json.dumps(x, default=str))


class Rechazo(Exception):
    pass


def leer_json(p, que):
    try:
        raw = Path(p).read_bytes()
    except OSError as ex:
        raise Rechazo("esquema: %s ilegible (%s)" % (que, type(ex).__name__))
    try:
        return raw, json.loads(raw)
    except ValueError:
        raise Rechazo("esquema: %s no es JSON válido" % que)


def autenticado(base, inv_h, rel):
    inv_raw = (T / base / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != inv_h:
        raise SystemExit("INVENTARIO_ALTERADO:%s" % base)
    raw = (T / base / rel).read_bytes()
    if json.loads(inv_raw)["files"][rel]["sha256"] != sha(raw):
        raise SystemExit("NO_AUTENTICADO:%s/%s" % (base, rel))
    return raw


class Validador:
    def __init__(self, run_class, etiqueta):
        from codigo import flujo_paso4_v2 as F
        SP = F.SP
        d = SP.DESPLIEGUE
        t0 = time.time()
        self.ctx = SP.CS5.ContextoS5(d["raiz_proyecto"], politica=d["politica"], recibo=d["recibo"], autor=d["autor"], s5_package=d["s5_package"],
                                     d7_tree=d["d7_tree"], run_class=run_class, etiqueta=etiqueta, encargo=d["encargo"], procedencia=d["procedencia"],
                                     code_globs=(), productor=Path(SP.__file__), codigo_productor=SP.codigo_manifiesto())
        self.t_ctx = round(time.time() - t0, 1)
        a = time.time()
        self.ref = SP.GE.Referencia(self.ctx, raiz=d["raiz_fuentes"])
        self.t_ref = round(time.time() - a, 1)
        self.SP, self.GC = SP, SP.GC
        self.CE = SP.GC.CE
        self.RB = SP._cargar("cand_regla_b_v2", "herramientas/b/regla_b_v2.py")
        self.E12 = SP._cargar("cand_e12_celda", "herramientas/b/e12_celda.py")
        from paper2b import claves_condicionales as CK
        from paper2b import convergencia as CV
        from paper2b import external as X
        from paper2b import inversion as INV
        from paper2b import keys as K
        from paper2b import macro as MC
        from paper2b import run as RUN
        self.CK, self.CV, self.X, self.INV, self.K, self.MC, self.RUN = CK, CV, X, INV, K, MC, RUN
        # v3 (S1-f Y VALIDACION H4 3.7): CONTRATO DE CONTENIDO del núcleo candidato (paper2b.contrato_paquete), el MISMO de la
        # ruta común de verificación del paquete (herramientas/s3/validadores/paquete_seleccion.verificar_celda)
        from paper2b import contrato_paquete as CP
        from paper2b import model as M
        self.CP, self.M = CP, M
        self.P2 = SP.P2
        self.r1_tol = float(self.ctx.cfg.r1_geometry_tol)            # tolerancia AUTORIZADA de la evidencia R1
        self.xtol = float(self.ctx.cfg.endogenous_xtol)              # tolerancia AUTORIZADA de la evidencia INV
        self._estados = {}
        self.gen = self.GC.Generador(self.ctx, self.ref, self.GC.Compartido(activo=False))
        self.runs = {}
        assert abs(float(self.ctx.cfg.sup.tol_converge) - TOL_CONVERGE) == 0.0 and abs(float(CV.T2_G) - T2_G) == 0.0, "TOLERANCIAS"

    # ------------------------------------------------------------------------------------------------ contrato (v3/v4)
    @staticmethod
    def contrato_por_tablas(filas):
        """SOLO DIAGNÓSTICO (nunca decide): versión que sugerirían las tablas presentes. v4 (S1-f REMANENTE H4 3.7): la versión
        EXIGIDA viene de la procedencia autenticada (contrato_exigido_de), no de las tablas ni de la declaración del documento."""
        from paper2b import contrato_paquete as CP
        return "v3" if isinstance(filas, dict) and all(t in filas for t in CP.HIJAS) else "v2"

    def esquema_contrato(self, filas, exigido, doc=None):
        """Antes de cualquier cálculo: (1) el conjunto EXACTO de tablas de la versión EXIGIDA por la procedencia (una tabla
        ausente es pérdida de evidencia: rechazo; nunca se rebaja la versión); (2) la versión declarada por el documento
        (contrato_exportado), si existe, igual a la exigida; (3) los recuentos declarados de filas iguales a los reales; (4) en
        v3, evidencia estructural mínima: cada fila de convergencia con su evidencia numérica exportada y la fila C2 del techo
        de un instrumento disponible completo; (5) tipos, nulabilidad, columnas y PK/UK del CONTRATO DE LA AUTORIDAD."""
        if exigido not in ("v2", "v3"):
            raise Rechazo("procedencia: versión de contrato exigida %r no derivada de la procedencia autenticada" % (exigido,))
        if not isinstance(filas, dict):
            raise Rechazo("esquema: filas no es un objeto")
        req = set(self.CP.TABLAS[exigido])
        falt, extra = sorted(req - set(filas)), sorted(set(filas) - req)
        if falt:
            raise Rechazo("esquema: pérdida de evidencia: faltan tablas exigidas por el contrato %s de la procedencia: %s" % (exigido, falt))
        if extra:
            raise Rechazo("esquema: tablas no previstas por el contrato %s de la procedencia: %s" % (exigido, extra))
        if isinstance(doc, dict):
            dec = doc.get("contrato_exportado")
            if dec is not None and dec != exigido:
                raise Rechazo("procedencia: versión declarada %r distinta de la exigida %r por la procedencia" % (dec, exigido))
            tab = (doc.get("filas") or {}).get("tablas")
            if tab is not None and tab != {t: len(v) for t, v in filas.items() if isinstance(v, list)}:
                raise Rechazo("esquema: recuentos de filas declarados distintos de los exportados")
        for t in self.CP.TABLAS[exigido]:
            xs = filas.get(t)
            if not isinstance(xs, list) or not all(isinstance(f, dict) for f in xs):
                raise Rechazo("esquema: tabla %s mal formada" % t)
        if exigido == "v3":
            refs = {x.get("evidence_ref") for x in filas["numerical_evidence"]}
            sin = sorted(str(z.get("quantity_id"))[:28] for z in filas["convergence_result"] if z.get("evidence_ref") not in refs)
            if sin:
                raise Rechazo("esquema: pérdida de evidencia v3: convergencias sin su evidencia numérica exportada: %s" % sin[:3])
            for ce in filas["capture_ceiling_result"]:
                if ce.get("instrument_available") is True and ce.get("computation_status") == "complete":
                    n = sum(1 for z in filas["convergence_result"] if z.get("quantity_id") == "C2:" + str(ce.get("ceiling_id")))
                    if n != 1:
                        raise Rechazo("esquema: pérdida de evidencia v3: %d filas de convergencia C2 para el techo %s (se exige 1)" % (n, str(ce.get("ceiling_id"))[:16]))
        for t in self.CP.TABLAS[exigido]:
            m = self.CP.esquema(self.ctx.C, t, filas[t])
            if m:
                raise Rechazo("esquema (contrato de la autoridad): %s: %s" % (t, m))
        return exigido

    def estado_modelo(self, r, oid, vals, design):
        k = (id(r), oid, design)
        if k not in self._estados:
            self._estados[k] = r.model.state(self.RUN._to_state_prim(vals))
        return self._estados[k]

    def valor_en(self, r, oid, vals, design):
        """C_2 en un punto: R(τ_d, τ_f)/B_pot con el estado del modelo de ω (misma evaluación que paquete_seleccion.valor_en)."""
        st = self.estado_modelo(r, oid, vals, design)
        return lambda td, tf: self.M.revenue(st, td, tf, design) / st.B_pot

    def f_en(self, r, oid, vals, design, K1):
        st = self.estado_modelo(r, oid, vals, design)
        mod = r.model
        return lambda td, tf: mod.evaluate(st, td, tf, design).R / st.B_pot - K1

    def payload_condicional(self, st, om, block, context, technical):
        """macro-ca2-v2 desde las tablas del bundle AUTENTICADO del proveedor S5 (misma construcción que
        paquete_seleccion.Verificador.payload_condicional y Providers.conditional_key SIN validate_key, que es evidencia del
        productor ya exigida al producir: el productor se detiene con CONDITIONAL_KEY_DIFFERS_FROM_CA2_KEY si difiere)."""
        prov = self.ctx.prov
        preg, c = st.preregistration_id, st.country_id
        if context is None:
            raise Rechazo("identidad: contexto de celda ausente para la clave condicional")
        b, raw, tab = prov._bundle(preg)
        label = "{}-{}-{}".format(*context)
        _, row0 = prov._key_cache[("row", preg, c, st.anchor_year, st.edition)]
        rows = [q for q in tab["ca2_inputs"] if q["country_id"] == c and q["anchor_year"] == st.anchor_year
                and q["d6_vector_id"] == row0["d6_vector_id"] and q["case_id"].endswith(":" + label)]
        if len(rows) != 1:
            raise Rechazo("identidad: fila condicional %s:%s:%s no única en el bundle autenticado" % (preg, c, label))
        case = next(q for q in tab["ca2_cases"] if q["case_id"] == rows[0]["case_id"])
        vectors = {v["vector_id"]: v for v in tab["ca2_vectors"]}
        return self.K.macro_ca2_v2(b["sha256"], case, c, rows[0], vectors, om["common_sha"], block, prov.protocol, technical)

    # ------------------------------------------------------------------------------------------------ runs y universo
    def run(self, sid, prefijo):
        k = (sid, json.dumps(prefijo, sort_keys=True))
        if k not in self.runs:
            r = self.RUN.Run(self.ctx.inp, self.ctx.cfg, unit={"unit_id": "validacion:%s" % sid, "set_id": sid, "prefix": dict(prefijo)})
            if not (r.model.kind == "modelo_teorico_v2_2" and r.model.certified):
                raise SystemExit("PROVEEDOR_NO_CERTIFICADO")
            self.runs[k] = r
        return self.runs[k]

    def localizar(self, claim, idx):
        cl = self.gen.claims[claim]
        nuevo = False
        for sid in cl.support_sets:
            if sid not in self.gen.runs:
                self.gen.runs[sid] = self.run(sid, {p: 0 for p in self.RUN.STRUCT})
                nuevo = True
        if nuevo or getattr(self.gen, "U", None) is None:
            self.gen.U = self.GC.Universo(self.gen.runs, self.GC.qmin_table(self.ctx.inp.grid_cells))
        sid, bi, meta, c = self.gen.localizar(cl, idx)
        return cl, sid, meta, c

    def prefijo_de(self, sid, decl):
        nod = self.CE.axes_nodes(self.ctx.view, self.ctx.cfg, sid)
        pre = {}
        for p in self.RUN.STRUCT:
            v = Decimal(str(decl[p]))
            idx = [i for i, x in enumerate(nod[p]) if Decimal(str(x)) == v]
            if len(idx) != 1:
                raise Rechazo("identidad: ω estructural declarado fuera de L0 en %s (%s)" % (p, decl[p]))
            pre[p] = idx[0]
        return pre

    # ------------------------------------------------------------------------------------------------ esperado por contenido
    def esperado(self, e):
        """Componentes de la celda reconstruidos desde el representante (ya regenerado desde fuentes autenticadas)."""
        GC, CE, RUN = self.GC, self.CE, self.RUN
        x = {"chk": {}}
        chk = x["chk"]
        fam = e["familia"]
        if fam in ("S1", "C2"):
            w = e["testigo"]
            cl, sid, meta, c = self.localizar(w["claim_id_hoja"], int(w["indice_contexto"]))
            punto = {p: float(w["punto"][p]) for p in GC.STRUCT}
            ki = self.ref.K1(punto, c)
            if fam == "S1":
                chk["contexto_del_testigo"] = self.ref.ctx_key(c) == norm(w["contexto"])
                chk["K1_del_testigo_reproducido"] = [ki.lo, ki.hi] == list(w["K1_en_punto"])
            chk["diseno_menu_del_testigo"] = (c.design, c.instrument) == (cl.design, cl.instrument_j)
            r = self.run(sid, {p: 0 for p in RUN.STRUCT})
            oid, ok, _ = CE.omega_por_valores(r, sid, punto, meta["macro"])
            vals = r.omegas[oid]["values"]
            chk["omega_admisible"] = bool(ok)
            chk["omega_exacto_reconstruido"] = all(float(vals[p]) == punto[p] for p in GC.STRUCT)
            cont = {"conjunto": sid, "contexto": self.ref.ctx_key(c), "omega": {k: str(v) for k, v in sorted(vals.items())}, "pais": meta["pais"],
                    "estado_nacional": meta["estado_nacional"], "celda_externa": meta["celda_externa"]["id"], "cota": cl.bound_variant,
                    "diseno": cl.design, "menu": cl.instrument_j, "caso": cl.availability_case_id}
            chk["cell_id_del_censo_por_contenido"] = sha(canon(cont)) == e["cell_id_censo"]
            sts = [s for s in r.states_for(r.omegas[oid], meta["pais"]) if GC.state_meta(s) == meta["estado_nacional"]]
            if len(sts) != 1:
                raise Rechazo("identidad: estado nacional del testigo no único (%d)" % len(sts))
            gcl = [g for g in CE.grid_cells(r, meta["pais"]) if g.external_cell_id == meta["celda_externa"]["id"]]
            x.update(sid=sid, r=r, oid=oid, vals=vals, pais=meta["pais"], d=cl.design, j=cl.instrument_j, case=cl.availability_case_id,
                     bound=cl.bound_variant, st=sts[0], gcell=gcl[0] if len(gcl) == 1 else None, K1_ref=(ki.lo, ki.hi), certificado=w["C2_en_punto"])
        else:
            if fam == "S3":
                tk = e["tarea"]
                pre = self.prefijo_de(e["conjunto"], tk["valores"])
                chk["prefijo_de_la_tarea"] = pre == {p: int(tk["prefix"][p]) for p in RUN.STRUCT}
                decl = tk["valores"]
            else:
                pre = self.prefijo_de(e["conjunto"], e["omega_estructural"])
                decl = e["omega_estructural"]
            sid, pais, d, j, case, bound = e["conjunto"], e["pais"], e["diseno"], e["menu"], e["caso"], e["cota"]
            r = self.run(sid, pre)
            oids = CE.omega_list(r)
            if not oids:
                raise Rechazo("identidad: sin ω admisible en el prefijo")
            if fam == "S3":
                oid = oids[int(tk["sel_omega"]) % len(oids)]
            else:
                oid = oids[self.RB.indice(list(e["estrato"]), int(e["k"]), "omega_vertice", len(oids))]
            vals = r.omegas[oid]["values"]
            chk["omega_exacto_reconstruido"] = all(Decimal(str(vals[p])) == Decimal(str(decl[p])) for p in GC.STRUCT)
            sts = r.states_for(r.omegas[oid], pais)
            if not sts:
                raise Rechazo("identidad: sin estados nacionales")
            # orden de macro_states = orden de states_for (una fila macro por estado; contexto (d, j, caso) o estricto)
            i = int(tk["sel_estado"]) % len(sts) if fam == "S3" else self.RB.indice(list(e["estrato"]), int(e["k"]), "estado_macro", len(sts))
            gcs = CE.grid_cells(r, pais)
            if fam == "S3":
                gcell = gcs[int(tk["sel_celda"])] if int(tk["sel_celda"]) < len(gcs) else None
            else:
                gcl = [g for g in gcs if g.external_cell_id == e["celda_externa"]]
                gcell = gcl[0] if len(gcl) == 1 else None
            x.update(sid=sid, r=r, oid=oid, vals=vals, pais=pais, d=d, j=j, case=case, bound=bound, st=sts[i], gcell=gcell, K1_ref=None, certificado=None)
        if x["gcell"] is None:
            raise Rechazo("identidad: celda externa no única o fuera de la grilla autenticada")
        return x

    # ------------------------------------------------------------------------------------------------ una celda
    def celda(self, e, doc, filas, *, contrato_exigido, esperado_previo=None):
        """-> dict con grupos de comprobaciones, motivos y clasificación. No lanza: todo defecto es un rechazo con motivo.
        contrato_exigido: versión derivada de la PROCEDENCIA autenticada (contrato_exigido_de), obligatoria."""
        out = {"id": e.get("id"), "familia": e.get("familia"), "contrato_exigido": contrato_exigido}
        chk, motivos = {}, []
        try:
            out["contrato_por_tablas_diagnostico"] = self.contrato_por_tablas(filas)
            contrato = self.esquema_contrato(filas, contrato_exigido, doc)   # ANTES de cualquier cálculo costoso
            out["contrato"] = contrato
            x = dict(esperado_previo) if esperado_previo else self.esperado(e)
            x["chk"] = dict(x["chk"])
            x["contrato"] = contrato
            x["detalle_contrato"] = {}
            chk.update(x["chk"])
            try:
                self._filas(x, e, doc, filas, chk)
            finally:
                for grupo, ms in x["detalle_contrato"].items():
                    motivos.extend("contrato %s: %s" % (grupo, m) for m in ms[:4])
                out["detalle_contrato"] = x["detalle_contrato"]
        except Rechazo as ex:
            motivos.append(str(ex))
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, AssertionError) as ex:
            motivos.append("esquema: %s: %s" % (type(ex).__name__, str(ex)[:300]))
            out["traza"] = traceback.format_exc()[-1200:]
        motivos += ["falsa: %s" % k for k, v in chk.items() if v is not True]
        out["comprobaciones"] = chk
        out["motivos"] = motivos
        na = chk.get("ruta_no_aplicable") is True
        out["clasificacion"] = ("rechazada" if motivos else ("no_aplicable_validada" if na else "completa_validada"))
        out["ok"] = not motivos
        return out

    def _filas(self, x, e, doc, filas, chk):
        K, RUN, MC, X, CV, INV = self.K, self.RUN, self.MC, self.X, self.CV, self.INV
        if not isinstance(filas, dict):
            raise Rechazo("esquema: filas no es un objeto")
        for t in ("cell_context", "frontier_context", "capture_ceiling_result", "confrontation_result", "lambda_pi_envelope", "convergence_result",
                  "inversion_result", "r1_summary", "r2_sections"):
            if not isinstance(filas.get(t), list) or not all(isinstance(f, dict) for f in filas[t]):
                raise Rechazo("esquema: tabla %s ausente o mal formada" % t)
        for t in ("cell_context", "frontier_context", "capture_ceiling_result", "confrontation_result", "lambda_pi_envelope"):
            if len(filas[t]) != 1:
                raise Rechazo("referencias: %d filas en %s (se exige 1)" % (len(filas[t]), t))
        r, oid, vals, pais, d, j, case, bound, st, gcell = (x[k] for k in ("r", "oid", "vals", "pais", "d", "j", "case", "bound", "st", "gcell"))
        sid = x["sid"]
        cx, fc, ce, cf, mac = (filas[t][0] for t in ("cell_context", "frontier_context", "capture_ceiling_result", "confrontation_result", "lambda_pi_envelope"))
        # ---- frontera y caso D4
        run_id = r.run_id
        tau_id = "TAU:%s:%s" % (sid, j)
        fid = "FRN:" + K.H({"r": run_id, "d": d, "c": pais, "j": j, "a": case, "o": oid, "t": tau_id})[:40]
        cei = "CEI:" + fid[4:]
        casos = [z for z in r.frontier_cases(pais) if z[0] == j and z[1] == case]
        if len(casos) != 1:
            raise Rechazo("identidad: caso D4 (%s, %s, %s) no está en el mapa autenticado" % (pais, j, case))
        disponible, d4 = casos[0][2], casos[0][3]
        sk, payload = r.structural(vals, d, j)
        chk["frontera_id_recalculado"] = fc.get("frontier_id") == fid and fc.get("run_id") == run_id
        chk["frontera_campos"] = (fc.get("design_v"), fc.get("country_id"), fc.get("instrument_j"), fc.get("availability_case_id"), fc.get("omega_id"),
                                  fc.get("tau_domain_id"), fc.get("availability_matrix_hash")) == (d, pais, j, case, oid, tau_id, self.ctx.inp.availability_matrix_hash)
        chk["clave_estructural_recalculada"] = fc.get("structural_key_sha256") == sk and norm(fc.get("structural_key_payload")) == norm(payload)
        try:
            self.ctx.C.key("structural", fc.get("structural_key_payload"), fc.get("structural_key_sha256"))
            chk["clave_estructural_contrato"] = True
        except Exception:      # noqa: BLE001
            chk["clave_estructural_contrato"] = False
        chk["huellas_tecnicas"] = norm((fc.get("structural_key_payload") or {}).get("technical")) == norm(self.ctx.technical)
        coord = self.ctx.inp.d7.scenarios[self.ctx.inp.d7.layer_scenario(sid)]["coordination_scenario_id"]
        chk["techo_id_y_disponibilidad"] = (ce.get("ceiling_id"), ce.get("frontier_id"), ce.get("instrument_available"), ce.get("availability_status"),
                                            ce.get("availability_source"), ce.get("availability_assumed"), ce.get("coordination_scenario_id")) == \
            (cei, fid, disponible, d4["national_availability_status"], d4["quantitative_use"], d4["availability_assumed"] == "true", coord)
        # ---- estado nacional, λ_π y clave macro
        om = r.omegas[oid]
        m = MC.bridge(st.share_dict(), vals)
        lam = float(m.lambda_pi) if m.lambda_pi is not None else None
        admisible = bool(m.admissible and vals["eta_H"] > -1)
        prim = [{"parameter_id": p.replace("!", "_").replace(":", "_"), "value": RUN.canon_dec(float(v)) if not RUN._finite_dec(v) else RUN.canon_dec(v), "value_unit": u}
                for p, v, u in st.primitive_values]
        nsha = K.H(K.national_state(sorted(prim, key=lambda q: q["parameter_id"]), {k: float(v) for k, v in st.shares}, st.joint_domain_sha256))
        block = om["block"]
        p = mac.get("macro_key_payload") or {}
        if st.channel == "strict":
            try:
                self.ctx.C.key("macro", p, mac.get("macro_key_sha256"))
                clave_ok = True
            except Exception:      # noqa: BLE001
                clave_ok = False
        else:
            clave_ok = (p.get("kind") == "macro-ca2-v2" and K.H(p) == mac.get("macro_key_sha256") and not self.CK.check_shape(p, self.ctx.C)
                        and str(p.get("case_id", "")).endswith(":%s-%s-%s" % (d, j, case)) and p.get("bundle_sha256") == st.joint_domain_sha256)
        chk["clave_macro"] = bool(clave_ok) and p.get("country_id") == pais and p.get("eta_w_block") == block and \
            norm(p.get("technical")) == norm(self.ctx.technical) and p.get("protocol_sha256") == self.ctx.inp.protocol[2]
        mid = "MAC:" + K.H({"r": run_id, "c": pais, "o": oid, "b": block, "m": mac.get("macro_key_sha256")})[:40]
        chk["macro_id_y_estado_nacional"] = (mac.get("macro_id"), mac.get("run_id"), mac.get("country_id"), mac.get("omega_id"), mac.get("national_state_sha256"),
                                             mac.get("eta_w_block")) == (mid, run_id, pais, oid, nsha, block)
        chk["lambda_pi_recalculado"] = mac.get("lambda_pi") == lam and mac.get("admissible") is admisible and \
            mac.get("computation_status") == ("complete" if admisible else "excluded")
        # ---- celda: cell_id por las claves del núcleo (Run.cell)
        uk = {"run_id": run_id, "design_v": d, "country_id": pais, "instrument_j": j, "availability_case_id": case, "omega_id": oid,
              "eta_w_block": mac.get("eta_w_block"), "policy_variant_id": gcell.policy_variant_id, "regime_id": gcell.regime_id,
              "requirement_basis": gcell.requirement_basis, "xi": gcell.xi, "layer": gcell.layer, "bound_variant": bound,
              "external_cell_id": gcell.external_cell_id, "national_state_sha256": nsha, "expected_macro_key_sha256": mac.get("macro_key_sha256")}
        cid = "CEL:" + K.H(uk)[:44]
        chk["cell_id_recalculado"] = cx.get("cell_id") == cid and all(cx.get(k) == v for k, v in uk.items() if k != "xi") and \
            cx.get("xi") == RUN._dec(gcell.xi) and cx.get("instrument_available") is disponible and \
            cx.get("availability_matrix_hash") == self.ctx.inp.availability_matrix_hash and cx.get("coordination_scenario_id") == coord
        chk["confrontacion_referencias"] = (cf.get("cell_id"), cf.get("ceiling_id"), cf.get("macro_id"), cf.get("run_readiness_flag"),
                                            cf.get("sup_not_attained")) == (cid, cei, mid, False, ce.get("sup_not_attained"))
        # ---- E12 con claves reconstruidas (barras del ω; tasa D7)
        rate = self.ctx.inp.d7.rates.get(pais)
        tasa = float(rate["value"]) if (rate is not None and rate.get("status") == "verified") else None
        barras = (float(vals["bar_tau_d"]), float(vals["bar_tau_f"])) if disponible else (None, None)
        comp = self.E12.verificar_celda(filas, cid, fid, instrumento=j, barras=barras, tasa=tasa, run_geometry=bool(self.ctx.cfg.run_geometry),
                                        con_unidad=True, omega_id=oid)
        # v4 (V2): FAMILIA 2 — campos macro, ANTES de cualquier salida (también la no aplicable): el estado macro no depende del
        # instrumento y su fila λ_π se consume siempre; se reconstruye y compara completa con la misma autoridad y definición
        CP, det = self.CP, x["detalle_contrato"]

        def grupo(nombre, resultado):
            inv_, inc_ = resultado
            if inv_ or inc_:
                det[nombre] = list(inv_) + ["(incompleto) " + m for m in inc_]
            chk[nombre] = not inv_ and not inc_
        # FAMILIA 2 — campos macro: la fila λ_π COMPLETA reconstruida desde el estado nacional y ω auténticos (Run.macro_row) e
        # igual campo a campo (q_pot, θ_W, s_T, s_L, banderas, estado, motivo, claves); Checker.omega + Checker.macro del núcleo
        try:
            ctxm = None if st.channel == "strict" else (d, j, case)
            esp = CP.macro_esperada(r, om, oid, pais, st, ctxm, run_id, self.ctx.technical, self.payload_condicional)
            grupo("macro_fila_reconstruida_y_checker", CP.verificar_macro(filas, mac, esp, r, oid, self.ctx.technical))
        except Rechazo as ex:
            grupo("macro_fila_reconstruida_y_checker", (["fila λ_π no derivable: %s" % ex], []))
        g = [z for z in filas["convergence_result"] if z.get("quantity_id") == "G:" + cid]
        if len(g) != 1:
            raise Rechazo("evidencias: %d filas de evidencia de G" % len(g))
        g = g[0]
        if not disponible:
            # ---- RUTA NO APLICABLE: nunca un resultado numérico
            chk["ruta_no_aplicable"] = True
            chk["E12_no_aplicable"] = comp["estado"] == "no_aplicable"
            exp = CV.fila_G(cid, C2=None, err_C2=None, K1=None, error_kind="certified_bound", ceiling_status="not_applicable", evidence_ref=None)
            chk["evidencia_G_recalculada"] = all(norm(g.get(k)) == norm(exp[k]) for k in CV.COLUMNAS if k != "evidence_ref")
            chk["resultado_declarado_no_numerico"] = doc.get("estado_final") == "no_aplicable" and (doc.get("resultado") or {}).get("cell_id") == cid
            x["E12"] = comp
            return
        chk["E12_completa"] = comp["estado"] == "completa"
        x["E12"] = comp
        # ---- techo
        err, c2 = ce.get("numerical_error"), ce.get("C_2")
        num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)  # noqa: E731
        chk["techo_completo_error_<=_tol_converge"] = ce.get("computation_status") == "complete" and ce.get("reason_code") is None and num(c2) and num(err) \
            and 0.0 <= err <= TOL_CONVERGE
        chk["techo_alcance"] = (ce.get("sup_not_attained") is False and num(ce.get("tau_d_at_sup")) and num(ce.get("tau_f_at_sup"))) or \
            (ce.get("sup_not_attained") is True and ce.get("sup_lateral_low") is not None and ce.get("sup_lateral_high") is not None)
        chk["monotonicidad_declarada"] = ce.get("monotonicity_check") in ("pass", "fail", "not_applicable")
        if x["certificado"] is not None:
            cc = x["certificado"]
            chk["C2_dentro_del_certificado_del_testigo"] = num(c2) and num(err) and c2 + err >= float(cc[0]) and c2 - err <= float(cc[1])
        # ---- confrontación y K1
        y = float(vals["gain_share"])
        Q = gcell.Q(bound)
        K1c = X.K1(Q, self.ctx.inp.dme_gai, lam, y) if (admisible and lam is not None) else None
        kc, G = cf.get("K_comp_1"), cf.get("G")
        chk["confrontacion_completa"] = cf.get("computation_status") == "complete" and cf.get("reason_code") is None and num(kc) and num(G) \
            and cf.get("C_2") == c2
        chk["K_comp_1_recalculado_desde_grilla_lambda_y"] = num(kc) and K1c is not None and math.isclose(kc, K1c, rel_tol=TOL_REL, abs_tol=0.0)
        if x["K1_ref"] is not None:
            lo, hi = x["K1_ref"]
            chk["K_comp_1_dentro_de_K1_referencia"] = num(kc) and lo - self.GC.TOL_K1 <= kc <= hi + self.GC.TOL_K1
        chk["G_igual_C2_menos_K"] = num(G) and num(c2) and num(kc) and abs(G - (c2 - kc)) <= TOL_REL * max(1.0, abs(G))
        if num(G) and num(err):
            from paper2b import claims as CL
            eps = CL.EPS_ECON
            want = "factible" if G - err >= eps else ("infactible" if G + err <= -eps else "inconcluso")
            chk["veredicto_recalculado"] = cf.get("verdict") == want
        # ---- evidencias consumidas
        exp = CV.fila_G(cid, C2=c2, err_C2=err, K1=kc, error_kind="certified_bound", ceiling_status=ce.get("computation_status"), evidence_ref=None)
        chk["evidencia_G_recalculada"] = all(norm(g.get(k)) == norm(exp[k]) for k in CV.COLUMNAS if k != "evidence_ref")
        chk["evidencia_G_pasa"] = g.get("status") == "pass" and g.get("coverage_complete") is True and g.get("tolerance") == T2_G and \
            num(g.get("change_bound")) and g.get("change_bound") <= T2_G and g.get("verdict_changes") == 0
        evs_ok, ev_mot = True, []
        r1 = filas["r1_summary"][0] if len(filas["r1_summary"]) == 1 else {}
        # v3: tolerancia AUTORIZADA por tipo de evidencia (configuración de la autoridad, no la que declara el productor),
        # cota finita y NO NEGATIVA, estados y relación con el resultado que respalda; nunca se relaja una tolerancia
        autorizada = {"G": T2_G, "R1": self.r1_tol, "INV": self.xtol, "C2": TOL_CONVERGE}
        for z in filas["convergence_result"]:
            q = str(z.get("quantity_id"))
            tipo = q.split(":", 1)[0]
            if q == "G:" + cid:
                ref_ok = cf.get("computation_status") == "complete"
            elif q == "R1:" + cid:
                ref_ok = r1.get("computation_status") == "complete"
            elif q.startswith("INV:%s:" % cid):
                iv = [f for f in filas["inversion_result"] if f.get("inversion_id") == q.split(":")[-1]]
                ref_ok = len(iv) == 1 and iv[0].get("computation_status") == "complete"
            elif q == "C2:" + cei:
                ref_ok = ce.get("computation_status") == "complete"
            else:
                evs_ok = False                       # evidencia de otra celda u otro producto
                ev_mot.append("evidencia ajena a la celda: %s" % q[:40])
                continue
            cb, tol = z.get("change_bound"), z.get("tolerance")
            if not (num(tol) and tol > 0 and tol == autorizada[tipo]):
                evs_ok = False
                ev_mot.append("%s: tolerancia %r distinta de la autorizada %r" % (tipo, tol, autorizada[tipo]))
            if cb is not None and not (num(cb) and cb >= 0):
                evs_ok = False
                ev_mot.append("%s: cota %r no finita o negativa" % (tipo, cb))
            if z.get("status") not in ("pass", "fail", "incomplete") or not isinstance(z.get("coverage_complete"), bool) or \
                    not (isinstance(z.get("verdict_changes"), int) and not isinstance(z.get("verdict_changes"), bool) and z.get("verdict_changes") >= 0):
                evs_ok = False
                ev_mot.append("%s: estado, cobertura o cambios de veredicto mal formados" % tipo)
            pasa = z.get("status") == "pass" and z.get("coverage_complete") is True and num(cb) and cb >= 0 and num(tol) and cb <= tol \
                and z.get("verdict_changes") == 0 and z.get("topology_before") == z.get("topology_after")
            if z.get("status") == "pass" and not pasa:
                evs_ok = False
                ev_mot.append("%s: pass sin sus condiciones (cobertura, cota <= tolerancia, 0 cambios, topología estable)" % tipo)
            if ref_ok and not pasa:
                evs_ok = False
                ev_mot.append("%s: el resultado está completo pero su evidencia no pasa" % tipo)
            if not ref_ok and z.get("status") == "pass":
                evs_ok = False
                ev_mot.append("%s: evidencia que pasa para un resultado no completo" % tipo)
        chk["evidencias_consumidas_coherentes"] = evs_ok
        if ev_mot:
            x["detalle_contrato"]["evidencias"] = ev_mot
        inv_ok = True
        for f in filas["inversion_result"]:
            iid, rs = f.get("inversion_id"), f.get("result_status")
            vf = INV.VALUE_FIELD.get(iid)
            if vf is None:
                inv_ok = False
                continue
            if rs in ("undefined_denominator", "not_identified") and f.get(vf) is not None:
                inv_ok = False
            if f.get("computation_status") != INV.STATUS_TO_COMPUTATION.get(rs):
                inv_ok = False
        chk["inversiones_estado_y_cifras"] = inv_ok
        # ================= v3: CONTRATO DE CONTENIDO del núcleo (paper2b.contrato_paquete), mismas reglas que la ruta común
        contrato = x["contrato"]
        bd, bf = float(vals["bar_tau_d"]), float(vals["bar_tau_f"])
        # FAMILIA 1 — alcanzabilidad del techo: punto en el dominio auténtico del menú (barras de ω), C_2 igual al valor del
        # modelo en el punto alcanzado; supremo no alcanzado: sin punto, dos laterales finitos, C_2 = máx(laterales) y
        # testigos laterales verificables (v3: sup_witness exportados; v2: no exportados -> no puede ser completo); fila C2 (v3)
        et = {"menu": j, "barras": [bd, bf], "tol_converge": TOL_CONVERGE, "contrato": contrato, "certificado": bool(r.model.certified),
              "valor_en": self.valor_en(r, oid, vals, d), "tol_valor": self.P2.TOL_VALOR}
        grupo("techo_contrato_dominio_valor_y_testigos", CP.verificar_techo(ce, filas, et))
        # inversiones: filas del núcleo recalculadas campo a campo con su convergencia INV (tolerancia del núcleo); las
        # búsquedas costosas, por coherencia con sus hijas (v3) y con la convergencia recalculada desde ellas
        if K1c is not None:
            ei = {"status": "complete" if ce.get("computation_status") == "complete" else "incomplete", "N": Q + self.ctx.inp.dme_gai, "C2": c2,
                  "lam": mac.get("lambda_pi"), "y": y, "K1": K1c, "gain_support": tuple(float(v) for v in r.inp.d7.interval(sid, "gain_share")),
                  "targets": r.inp.supplier_targets.get(sid), "mapping": r.inp.external_factor_mapping is not None,
                  "run_endogenous": bool(r.cfg.run_endogenous), "menu": j, "set": sid, "pais": pais, "con_unidad": True, "tol_root": float(r.tol_root),
                  "xtol": self.xtol, "contrato": contrato, "grid_sha256": r.inp.grid_sha256}
            grupo("inversiones_contrato_y_evidencia_INV", CP.verificar_inversiones(filas, cid, r, ei))
            # geometría: puntos R1/R2 en el dominio del menú, residuos = |f| en el punto, raíces sobre su trayectoria,
            # conteos y vacío demostrado
            eg = {"menu": j, "barras": [bd, bf], "f": self.f_en(r, oid, vals, d, K1c), "tol_root": float(r.tol_root), "tasa": tasa, "r1_tol": self.r1_tol,
                  "vacio_demostrado": bool(r.model.certified) and num(c2) and num(err) and K1c > c2 + err}
            grupo("geometria_contrato_dominio_y_residuos", CP.verificar_geometria(filas, cid, eg))
            if contrato == "v3":
                grupo("evidencia_numerica_contrato", CP.verificar_evidencia(filas, cid, cei, eg))
                try:
                    err_ch = CP.checker_nucleo(self.ctx.C, r.inp.d7, CP.filas_de_celda(filas, cid, fid, "v3"), r.inp.tolerances)
                except Exception as ex:      # noqa: BLE001
                    err_ch = ["Checker no ejecutable: %s: %s" % (type(ex).__name__, ex)]
                grupo("checker_del_nucleo", (["Checker del núcleo: " + m for m in err_ch[:4]], []))
        else:
            grupo("inversiones_contrato_y_evidencia_INV", (["K1 no recalculable con la fila λ_π reconstruida"], []))
        # FAMILIA 3 — evidencia R1: la fila EXIGIDA por el contrato (tolerancia = r1_geometry_tol autorizada, cota = la del
        # resumen R1, topología = sus componentes) y cotas del resumen dentro de r1_geometry_tol y T_root
        if r1.get("computation_status") == "complete":
            gb, rb = r1.get("geometry_error_bound"), r1.get("residual_bound")
            mal = []
            if not (num(gb) and 0 <= gb <= self.r1_tol and num(rb) and 0 <= rb <= float(r.tol_root) and r1.get("topology_stable") is True):
                mal.append("R1 complete con cotas %r/%r fuera de r1_geometry_tol/T_root o topología inestable" % (gb, rb))
            evr = [z for z in filas["convergence_result"] if z.get("quantity_id") == "R1:" + cid]
            esper = {"method_id": "certified_contour", "topology_before": r1.get("n_components"), "topology_after": r1.get("n_components"),
                     "coverage_complete": True, "status": "pass", "change_bound": gb, "tolerance": self.r1_tol, "unit": "tau", "level_before": 0,
                     "level_after": 1, "verdict_changes": 0, "value_before": None, "value_after": None,
                     "result_ref": "r1_summary:" + json.dumps({"cell_id": cid}, sort_keys=True, separators=(",", ":"))}
            if len(evr) != 1:
                mal.append("%d evidencias R1 (se exige 1)" % len(evr))
            else:
                dif = [k for k, v in esper.items() if norm(evr[0].get(k)) != norm(v)]
                if dif:
                    mal.append("evidencia R1 distinta de la exigida por el contrato en %s" % dif)
            for s_ in filas["r2_sections"]:
                if s_.get("computation_status") == "complete":
                    for rt in [q for q in filas.get("r2_roots", []) if q.get("section_id") == s_.get("section_id")]:
                        if not (num(rt.get("residual")) and abs(rt["residual"]) <= float(r.tol_root)):
                            mal.append("raíz R2 con residuo fuera de T_root")
                            break
            grupo("evidencia_R1_y_cotas_autorizadas", (mal, []))
        chk["geometria_resumen"] = r1.get("computation_status") == "complete" and r1.get("cell_id") == cid
        # ---- lo declarado por el productor debe coincidir con lo reconstruido (no se usa como prueba)
        rr = doc.get("resultado") or {}
        chk["resultado_coincide_con_lo_reconstruido"] = doc.get("estado_final") == "completo" and rr.get("omega_id") == oid and rr.get("cell_id") == cid \
            and rr.get("frontier_id") == fid and rr.get("clave_estructural") == sk and norm(rr.get("techo")) == norm({k: ce.get(k) for k in rr.get("techo", {})}) \
            and norm(rr.get("confrontacion")) == norm({k: cf.get(k) for k in rr.get("confrontacion", {})}) and (rr.get("clave_E12") or {}).get("barras") == list(barras)


# ==================================================================================================== versión exigida por la procedencia
# v4 (S1-f REMANENTE H4 3.7): la versión del contrato de exportación la fija el PRODUCTOR AUTENTICADO de cada entrega (su código
# en el inventario de la entrega), nunca las tablas presentes ni la declaración del documento. Histórico v2 legítimo: piloto
# (piloto_detallado: E12.filas_de_celda) y D-S1-d + diagnóstico (bloque_detallado / piloto_detallado). v3: S1-f (bloque_s1 v1.2+:
# contrato_paquete.filas_de_celda(v3)). Esta ronda: el preregistro congelado declara v3 y su productor es bloque_s1 (v1.3).
PRODUCTOR_POR_ENTREGA = {
    "fase_detallada_piloto_h4_paso4_3_7_2026-10-09_lima2201": ("v2", "codigo/piloto_detallado.py"),
    "validacion_detallada_d_s1_d_h4_paso4_3_7_2026-10-09_lima2331": ("v2", "codigo/bloque_detallado.py"),
    "s1f_validacion_h4_paso4_3_7_2026-10-10_lima0800": ("v3", "codigo/bloque_s1.py"),
}
INVENTARIOS = {"fase_detallada_piloto_h4_paso4_3_7_2026-10-09_lima2201": "1f81beca84009c710fe23a427644f4c15260475fb70052862a89613596ebf3a8",
               "validacion_detallada_d_s1_d_h4_paso4_3_7_2026-10-09_lima2331": "4caedd3bb0901bc678193035422d673bd41be6a8abcba6184a982f8638a1b7f1",
               "s1f_validacion_h4_paso4_3_7_2026-10-10_lima0800": "d22952fad5782ff67c0c514a5b2c8d613c089f8cdfb241ebad133fb8903d7dc1"}


def contrato_exigido_de(entrega=None, preregistro=None):
    """Entrega histórica: versión de su productor, comprobando que el archivo productor está en su inventario autenticado
    (y, para v3, que exporta con contrato_paquete.filas_de_celda(..., "v3")). Ronda actual: el preregistro congelado
    (campo contrato_exigido) y el productor congelado en él."""
    if entrega is not None:
        ver, prod = PRODUCTOR_POR_ENTREGA[entrega]
        inv_raw = (T / entrega / "audit/entrega.json").read_bytes()
        if sha(inv_raw) != INVENTARIOS[entrega]:
            raise SystemExit("INVENTARIO_ALTERADO:%s" % entrega)
        raw = (T / entrega / prod).read_bytes()
        if json.loads(inv_raw)["files"][prod]["sha256"] != sha(raw):
            raise SystemExit("PRODUCTOR_NO_AUTENTICADO:%s/%s" % (entrega, prod))
        if (b'filas_de_celda(' in raw and b'"v3")' in raw) != (ver == "v3"):
            raise SystemExit("PRODUCTOR_CONTRATO_INCOHERENTE:%s" % entrega)
        return ver
    pre = json.loads(Path(preregistro).read_bytes())
    ver = pre.get("contrato_exigido")
    if ver not in ("v2", "v3"):
        raise SystemExit("PREREGISTRO_SIN_CONTRATO_EXIGIDO")
    prod = pre["bytes"]["sha256"].get("codigo/bloque_s1.py")
    if prod is None or sha((A / "codigo/bloque_s1.py").read_bytes()) != prod:
        raise SystemExit("PRODUCTOR_DISTINTO_DEL_CONGELADO")
    return ver


# ==================================================================================================== evidencia histórica lima2201
def validar_piloto(man_p, dres, out, *, validador=None):
    """Valida el piloto lima2201 (evidencia HISTÓRICA: run_class fase_detallada_piloto_h4_3_7, sin recalcular celdas)."""
    from codigo import piloto_detallado as P
    base, inv_h = L2201
    inv_raw = (T / base / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != inv_h:
        raise SystemExit("INVENTARIO_ALTERADO")
    inv = json.loads(inv_raw)
    dep = json.loads(autenticado(base, inv_h, "autorizacion/despliegue_ronda.json"))
    t0 = time.time()
    res = {"modo": "evidencia histórica lima2201 (validación, sin cálculo de celdas)", "fuente": {"entrega": base, "inventario_sha256": inv_h,
           "run_class": dep["run_class"]}, "celdas": []}
    man_raw, man = leer_json(man_p, "manifiesto")
    proc_man = inv["files"].get("demo/detallado/manifiesto_detallado.json", {}).get("sha256") == sha(man_raw)
    regen = P.construir_manifiesto()
    V = validador or Validador(dep["run_class"], dep["etiqueta"])
    res["contexto_s"], res["referencia_s"] = V.t_ctx, V.t_ref
    res["manifiesto_autenticado"] = proc_man
    reg = {e["id"]: e for e in regen["representantes"]}
    claves = []
    for e in man.get("representantes", []):
        f = {"id": e.get("id"), "familia": e.get("familia")}
        try:
            proc = {"manifiesto_autenticado": proc_man, "fila_del_manifiesto_regenerada_igual": norm(reg.get(e.get("id"))) == norm(e)}
            p = Path(dres) / ("%s.json" % e["id"])
            doc_raw, doc = leer_json(p, "resultado %s" % e["id"])
            proc["resultado_autenticado"] = inv["files"].get("demo/detallado/resultados/%s.json" % e["id"], {}).get("sha256") == sha(doc_raw)
            if doc.get("estado_final") != "completo" or not doc.get("filas"):
                f.update(estado_final=doc.get("estado_final"), clasificacion="no_terminal_o_error (no cuenta)", ok=None, procedencia=proc)
                res["celdas"].append(f)
                continue
            fr_raw, filas = leer_json(Path(dres) / doc["filas"]["archivo"], "filas %s" % e["id"])
            proc["filas_autenticadas"] = inv["files"].get("demo/detallado/resultados/%s" % doc["filas"]["archivo"], {}).get("sha256") == sha(fr_raw)
            proc["filas_sha_del_resultado"] = doc["filas"].get("sha256") == sha(fr_raw)
            exig = contrato_exigido_de(entrega=base)
            v = V.celda(reg[e["id"]] if e.get("id") in reg else e, doc, filas, contrato_exigido=exig)
            if not proc["fila_del_manifiesto_regenerada_igual"]:
                # la fila DADA no es la autenticada: se valida también tal cual, para registrar qué contradice (sin aceptarla)
                vd = V.celda(e, doc, filas, contrato_exigido=exig)
                v["motivos"] = v["motivos"] + ["manifiesto dado: %s" % m for m in (vd["motivos"] or ["distinto del regenerado desde las fuentes"])]
        except Rechazo as ex:
            f.update(clasificacion="rechazada", ok=False, motivos=[str(ex)])
            res["celdas"].append(f)
            continue
        except (KeyError, TypeError, ValueError, AttributeError) as ex:
            f.update(clasificacion="rechazada", ok=False, motivos=["esquema: %s: %s" % (type(ex).__name__, ex)])
            res["celdas"].append(f)
            continue
        v["procedencia"] = proc
        v["motivos"] = v["motivos"] + ["procedencia falsa: %s" % k for k, b in proc.items() if b is not True]
        v["ok"] = not v["motivos"]
        v["clasificacion"] = v["clasificacion"] if v["ok"] else "rechazada"
        v["estado_final_declarado"] = doc.get("estado_final")
        if v["ok"]:
            claves.append((doc.get("resultado") or {}).get("clave_estructural"))
        res["celdas"].append(v)
    res["completas_validadas"] = sum(1 for f in res["celdas"] if f.get("clasificacion") == "completa_validada")
    res["rechazadas"] = [f["id"] for f in res["celdas"] if f.get("clasificacion") == "rechazada"]
    res["no_cuentan"] = [f["id"] for f in res["celdas"] if f.get("ok") is None]
    res["claves_distintas_validadas"] = len(set(claves))
    res["todas_ok"] = not res["rechazadas"] and not res["no_cuentan"]
    res["segundos"] = round(time.time() - t0, 1)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "piloto":
        r = validar_piloto(a[1], a[2], a[3])
        print(json.dumps({k: v for k, v in r.items() if k != "celdas"}, ensure_ascii=False))
        raise SystemExit(0 if not r["rechazadas"] else 1)
    elif a[0] == "bloque":
        from codigo import bloque_detallado as B
        raise SystemExit(B.validar(a[1], a[2], a[3]))
