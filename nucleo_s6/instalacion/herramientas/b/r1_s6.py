"""ADAPTADOR R1 / ORQUESTADOR B BAJO S6 (rem43; candidato; NO OFICIAL). Ejecuta la pila HISTÓRICA del método v5 (lima1351 codigo/:
orquestador_b, extremos_G_df_v5, extremos_G, extremos_dfd, inf_df_bb_v3, cota_un_umbral_v2, c2_extremos, certificar_inf_df,
sensibilidad_q y codigo/demo/*) SIN copiarla ni editarla en su sitio: un importador propio carga cada módulo de `codigo.*` desde los
BYTES autenticados por el inventario de lima1351 (ba473a76…) y aplica SOLO las sustituciones textuales EXACTAS de SUSTITUCIONES (cada una
debe aparecer exactamente una vez; se registran antes/después). Esas sustituciones únicamente:
  (1) quitan la inserción del paper2b AISLADO del área (integracion/src) y de la raíz ORIGINAL en sys.path, e imponen que paper2b sea el
      NÚCLEO S6 autenticado de la instalación (src/paper2b, = raíz S6 archivo por archivo);
  (2) toman la identidad del despliegue S6 en lugar del candidato S5 del área (identidad de reanudación del orquestador);
y el adaptador sustituye `nucleo_v.Contexto` por el ContextoS6 ya autenticado de la corrida (misma interfaz: claims, run, view, cfg, inp).
Fórmulas, parámetros, tolerancias (T2_G, topes por afirmación), selección del diseño, fuentes históricas autenticadas (XDD, CAN, PRV,
puntos U, SRED) y el registro v4 NO cambian. Guarda: cualquier `paper2b` cargado fuera del núcleo S6 -> NUCLEO_HISTORICO_INTRODUCIDO.
Diferencias de núcleo (comparar_nucleos): el aislado de lima1351 = S6 salvo run.py (caché de techos opcional desactivada por defecto,
NA G-NA-1 solo para instrumentos no disponibles, textos E1–E3) y rules.py (verificador de tablas; la pila R1 no lo importa), y S6 añade
aplicabilidad.py, contrato_paquete.py y seleccion_valores.py: cambios de identidad técnica, contrato y NA; ninguna fórmula usada por R1.
  P = PilaR1S6(ctx, despliegue); P.preflight(tarea, ids) (sin cálculo); P.producir(...) (CÁLCULO: solo con autorización)"""
from __future__ import annotations

import hashlib
import importlib.abc
import importlib.util
import json
import sys
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
NUCLEO_S6 = (INSTALACION / "src/paper2b").resolve()
HISTORICO = ("p0_completo_h4_paso4_3_7_2026-10-09_lima1351", "ba473a76059faa9719e0f2a0638ce51878a872e74fccf6c680b9d9d73fb14743")
_SRC = 'sys.path.insert(0, str(AREA / "integracion/src"))'
_AISL = '(AREA / "integracion/src/paper2b").resolve()'
SUSTITUCIONES = {      # módulo -> [(texto histórico EXACTO, texto en el puerto)]; cada original debe aparecer exactamente una vez
    "codigo.extremos_G_df_v5": [(_SRC, "pass  # rem43 r1_s6: núcleo S6 impuesto por el adaptador"), (_AISL, "NUCLEO_S6")],
    "codigo.inf_df_bb_v3": [(_SRC, "pass  # rem43 r1_s6: núcleo S6 impuesto por el adaptador"), (_AISL, "NUCLEO_S6")],
    "codigo.certificar_inf_df": [(_SRC, "pass  # rem43 r1_s6: núcleo S6 impuesto por el adaptador"), (_AISL, "NUCLEO_S6")],
    "codigo.extremos_dfd": [(_SRC + "     # paper2b de la INTEGRACIÓN CANDIDATA (bytes probados)", "pass  # rem43 r1_s6: núcleo S6 impuesto por el adaptador"),
                            ('_INT, _CAN = (AREA / "integracion/src/paper2b").resolve(), (AREA / "candidato/src/paper2b").resolve()',
                             '_INT, _CAN = NUCLEO_S6, Path("__rem43_sin_candidato_historico__")')],
    "codigo.demo.nucleo_v": [("for p in (ROOT, ROOT / \"src\"):", "for p in ():  # rem43 r1_s6: el candidato S6 ya está en sys.path (nunca la raíz original)")],
    "codigo.orquestador_b": [('dep = json.loads((A / "autorizacion/despliegue_candidato.json").read_bytes())', "dep = DESPLIEGUE_S6"),
                             ('{k: dep[k] for k in ("s5_package", "d7_tree", "run_class")}', '{k: dep.get(k) for k in ("s6_package", "ancla", "d7_tree", "run_class")}'),
                             ('"Claim del contexto S5 (', '"Claim del contexto S6 (')],
}
R1_RUTAS = ("herramientas/b/r1_rutas.py", "e6f922fb78d4d5a54b3fadad555d290bb481740ed17f3dcd901e41c5db125f55")        # sha256 fijado al congelar (el validador R1 cubre también las rutas por comando); rem50: artefacto del preflight declarado
COBERTURA = ("validacion_evidencia_comparador_paso4_3_7_2026-10-12_lima1857", "369beaa07cc56fffc966112b6d1faaebac60d072529dc299e761eebf523bca42",
             "demo/plan15/cobertura_r1.json")
ESTADOS_NO_ADMISIBLES = ("no_ejecutado", "error")
# Equivalencia de ETIQUETAS (no de criterio): las mediciones históricas de lima0754/lima0003 escriben «convergida»; el orquestador escribe
# «convergido» (TERMINALES). Es el mismo estado.
ESTADO_EQUIVALENTE = {"convergida": "convergido"}
PILA_ORQUESTADOR = ("R1-B1", "R1-B2", "R1-B3", "R1-C1", "R1-C2", "R1-C3", "R1-C4", "R1-C5", "R1-C6", "R1-D", "R1-V")
PRODUCTOR_MODULO = {"R1-A1": "codigo.c2_extremos", "R1-A2": "codigo.c2_extremos", "R1-A3-G-U": "codigo.certificar_inf_df", "R1-A3-N-U": "codigo.certificar_inf_df",
                    "R1-A3-G-L": "codigo.inf_df_bb_v3", "R1-A3-N-L": "codigo.inf_df_bb_v3", "R1-F": "codigo.sensibilidad_q",
                    **{k: "codigo.orquestador_b" for k in PILA_ORQUESTADOR}}


class R1S6Error(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle) if detalle else codigo)
        self.codigo, self.detalle = codigo, detalle


def need(t, c, d=""):
    if not t:
        raise R1S6Error(c, d)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def comparar_nucleos(raiz_fuentes) -> dict:
    """Comparación CONCRETA archivo por archivo: paper2b aislado de lima1351 frente al núcleo S6 de la instalación."""
    h = Path(raiz_fuentes) / HISTORICO[0] / "integracion/src/paper2b"
    fs = sorted({p.name for d in (h, NUCLEO_S6) for p in d.glob("*.py")})
    out = {"iguales": [], "distintos": {}, "solo_historico": [], "solo_s6": []}
    for f in fs:
        a, b = h / f, NUCLEO_S6 / f
        if not a.exists():
            out["solo_s6"].append(f)
        elif not b.exists():
            out["solo_historico"].append(f)
        elif a.read_bytes() == b.read_bytes():
            out["iguales"].append(f)
        else:
            out["distintos"][f] = {"historico": sha(a.read_bytes()), "s6": sha(b.read_bytes())}
    return out


def guarda_nucleo():
    """Todo paper2b cargado debe venir del núcleo S6 (nunca del aislado histórico ni de la raíz original)."""
    malos = sorted(n for n, m in list(sys.modules.items()) if (n == "paper2b" or n.startswith("paper2b.")) and getattr(m, "__file__", None)
                   and not Path(m.__file__).resolve().is_relative_to(NUCLEO_S6))
    need(not malos, "NUCLEO_HISTORICO_INTRODUCIDO", str(malos[:3]))
    need(not any(Path(p).resolve() == (_raiz_hist / "integracion/src").resolve() for p in sys.path if p), "NUCLEO_HISTORICO_EN_SYS_PATH")


_raiz_hist = Path(".")


class _Importador(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """`codigo` y `codigo.*` desde los bytes AUTENTICADOS de lima1351 con las SUSTITUCIONES registradas."""

    def __init__(self, area, inv, extra):
        self.area, self.inv, self.extra, self.registro = area, inv, extra, {}

    def find_spec(self, fullname, path=None, target=None):
        if fullname != "codigo" and not fullname.startswith("codigo."):
            return None
        rel = fullname.replace(".", "/")
        pkg = (self.area / rel / "__init__.py")
        f = pkg if pkg.is_file() else self.area / (rel + ".py")
        if not f.is_file():
            return None
        return importlib.util.spec_from_file_location(fullname, f, loader=self, submodule_search_locations=[str(f.parent)] if f == pkg else None)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        f = Path(module.__spec__.origin)
        rel = f.relative_to(self.area).as_posix()
        raw = f.read_bytes()
        x = self.inv.get(rel)
        need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "PILA_HISTORICA_NO_AUTENTICADA", rel)
        src = raw.decode("utf-8")
        hechas = []
        for a, b in SUSTITUCIONES.get(module.__name__, []):
            need(src.count(a) == 1, "SUSTITUCION_NO_UNICA", "%s: %r (%d)" % (module.__name__, a[:60], src.count(a)))
            src = src.replace(a, b)
            hechas.append({"original": a, "puerto": b})
        module.__dict__.update(self.extra)
        self.registro[module.__name__] = {"archivo": rel, "sha256_historico": sha(raw), "sha256_puerto": sha(src.encode("utf-8")), "sustituciones": hechas}
        exec(compile(src, str(f), "exec"), module.__dict__)
        guarda_nucleo()


class PilaR1S6:
    """Pila R1 histórica con el ContextoS6 de la corrida y el núcleo S6. Una por proceso (la identidad no cambia dentro del proceso)."""

    def __init__(self, ctx, despliegue: dict):
        global _raiz_hist
        T = Path(despliegue["raiz_fuentes"])
        _raiz_hist = T / HISTORICO[0]
        inv_raw = (_raiz_hist / "audit/entrega.json").read_bytes()
        need(sha(inv_raw) == HISTORICO[1], "INVENTARIO_HISTORICO_R1_ALTERADO")
        import paper2b
        need(Path(paper2b.__file__).resolve().parent == NUCLEO_S6, "PAPER2B_NO_ES_EL_NUCLEO_S6", paper2b.__file__)
        need("codigo" not in sys.modules, "OTRO_PAQUETE_CODIGO_CARGADO", str(getattr(sys.modules.get("codigo"), "__file__", "")))
        need(sha((INSTALACION / R1_RUTAS[0]).read_bytes()) == R1_RUTAS[1], "R1_RUTAS_DISTINTO_DEL_FIJADO")   # el validador R1 fija las rutas
        self.ctx, self.d = ctx, despliegue
        self.imp = _Importador(_raiz_hist, json.loads(inv_raw)["files"], {"NUCLEO_S6": NUCLEO_S6, "DESPLIEGUE_S6": despliegue})
        sys.meta_path.insert(0, self.imp)
        guarda_nucleo()
        import importlib
        self.N = importlib.import_module("codigo.demo.nucleo_v")
        self.N.Contexto = lambda *a, **k: ctx             # ContextoS6 de la corrida (misma interfaz que nucleo_v.Contexto)
        self.OB = importlib.import_module("codigo.orquestador_b")
        guarda_nucleo()

    def modulo(self, nombre):
        import importlib
        m = importlib.import_module(nombre)
        guarda_nucleo()
        return m

    def preflight(self, tarea: str, ids: list) -> dict:
        """SIN CÁLCULO: registro v4 autenticado = afirmaciones del ContextoS6; dependencias derivadas de la autoridad; cierre y rutas de
        la muestra de la tarea; módulo productor cargado con el núcleo S6. Lanza R1S6Error si algo no conecta."""
        OB = self.OB
        reg = set(json.loads(OB.registro())["afirmaciones"])
        mias = {c.claim_id for c in self.ctx.claims}
        need(mias == reg, "REGISTRO_Y_CONTEXTO_S6_DISTINTOS", "%d vs %d (sim. %d)" % (len(mias), len(reg), len(mias ^ reg)))
        deps = OB.dependencias(self.ctx.claims)
        out = {"registro_v4_igual_a_afirmaciones_s6": True, "afirmaciones": len(reg), "dependencias_derivadas": len(deps)}
        mod = PRODUCTOR_MODULO.get(tarea)
        need(mod is not None, "TAREA_R1_SIN_PRODUCTOR", tarea)
        self.modulo(mod)
        out["productor"] = mod
        # ids de cobertura_r1 = extreme_id = sha256(afirmación|sentido)[:16] (global_extreme_v4.eid): se RESUELVEN contra las afirmaciones S6
        eid = {sha((c.claim_id + "|" + s).encode("utf-8"))[:16]: (c.claim_id, s) for c in self.ctx.claims for s in ("sup", "inf")}
        res_ids = [eid[x] for x in ids or [] if x in eid]
        sin = [x for x in ids or [] if x not in eid]
        out.update(ids=len(ids or []), extremos_resueltos=len(res_ids), ids_no_resueltos=len(sin))
        if tarea in PILA_ORQUESTADOR and res_ids:
            from collections import Counter
            afs = sorted({c for c, _ in res_ids})
            if tarea.startswith(("R1-B", "R1-C")):
                need(not sin, "EXTREMO_FUERA_DE_LA_AUTORIDAD", str(sin[:4]))
            orden = OB.cierre(afs, deps)                      # lanza RutaNoSoportada si una afirmación o dependencia no es de la autoridad
            externas = sorted(set(orden) - set(afs))
            if tarea.startswith(("R1-B", "R1-C")):             # hojas: la muestra se cierra sola (las hojas no tienen dependencias)
                need(not externas, "MUESTRA_NO_CERRADA_POR_DEPENDENCIAS", str(externas[:4]))
            out.update(afirmaciones_muestra=afs, sentidos=dict(Counter(s for _, s in res_ids)), cierre=len(orden), dependencias_en_otras_tareas=len(externas),
                       rutas=dict(Counter(OB.ruta_de(c) for c in orden)))
        else:
            out.update(nota="sin extremos de afirmaciones del orquestador en la muestra (C2/Q/validación): sin cierre de dependencias")
        out["modulos_cargados"] = self.imp.registro
        return out

    # ------------------------------------------------------------------ rem43/rem44: ACEPTACIÓN POR COBERTURA EXACTA (P4-R1-COBERTURA)
    def _cobertura(self) -> dict:
        """rem51: la cobertura R1 AUTENTICADA (inventario fijado de lima1857 y sha256 del archivo en él)."""
        T = Path(self.d["raiz_fuentes"])
        ent, h, rel = COBERTURA
        inv_raw = (T / ent / "audit/entrega.json").read_bytes()
        need(sha(inv_raw) == h, "COBERTURA_R1_NO_AUTENTICADA", "inventario")
        raw = (T / ent / rel).read_bytes()
        x = json.loads(inv_raw)["files"].get(rel)
        need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "COBERTURA_R1_NO_AUTENTICADA", rel)
        return json.loads(raw)

    def requeridos(self, tarea: str, exacta: bool = False) -> list:
        """ids EXACTOS asignados a la tarea por la cobertura R1 AUTENTICADA (lima1857, inventario fijado); nunca deducidos del nombre."""
        T = Path(self.d["raiz_fuentes"])
        ent, h, rel = COBERTURA
        inv_raw = (T / ent / "audit/entrega.json").read_bytes()
        need(sha(inv_raw) == h, "COBERTURA_R1_NO_AUTENTICADA", "inventario")
        raw = (T / ent / rel).read_bytes()
        x = json.loads(inv_raw)["files"].get(rel)
        need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "COBERTURA_R1_NO_AUTENTICADA", rel)
        cob = {t["tarea"]: t for t in json.loads(raw)["tareas"]}
        ids = [i for k, v in cob.items() if k == tarea or (not exacta and k.startswith(tarea + "-")) for i in (v.get("ids") or [])]
        need(ids, "TAREA_SIN_COBERTURA", tarea)
        need(len(ids) == len(set(ids)), "COBERTURA_CON_DUPLICADOS", tarea)
        return ids

    def requeridos_orquestador(self, tarea: str) -> list:
        """[(afirmación, sentido)] requeridos: ids de la cobertura = sha256(afirmación|sentido)[:16] RESUELTOS contra el registro v4
        autenticado (= afirmaciones del ContextoS6, comprobado en el preflight). Un id que no resuelve -> EXTREMO_FUERA_DE_LA_AUTORIDAD."""
        ids = self.requeridos(tarea, exacta=True)                      # solo los extremos de ESTA tarea (no sus subtareas de censo/testigos)
        afs = json.loads(self.OB.registro())["afirmaciones"]
        eid = {sha((c + "|" + s_).encode("utf-8"))[:16]: (c, s_) for c in afs for s_ in ("sup", "inf")}
        sin = [i for i in ids if i not in eid]
        need(not sin, "EXTREMO_FUERA_DE_LA_AUTORIDAD", str(sin[:4]))
        return sorted(eid[i] for i in ids)

    def referencia_cobertura(self, tarea: str) -> dict:
        """Referencia AUTENTICADA que la cobertura R1 cita para la tarea (entrega, inventario, archivo y sha256 de la cita): filas por
        (hoja, sentido). Es la referencia de TODOS los requeridos (la verificación histórica del orquestador solo mide una parte)."""
        T = Path(self.d["raiz_fuentes"])
        ent, h, rel = COBERTURA
        cob = {t["tarea"]: t for t in json.loads((T / ent / rel).read_bytes())["tareas"]}
        c = ((cob.get(tarea) or {}).get("referencia") or {}).get("cita")
        need(c is not None, "TAREA_SIN_REFERENCIA_CITADA", tarea)
        inv_raw = (T / c["entrega"] / "audit/entrega.json").read_bytes()
        raw = (T / c["entrega"] / c["archivo"]).read_bytes()
        x = json.loads(inv_raw)["files"].get(c["archivo"])
        need(sha(inv_raw) == c["inventario_sha256"] and sha(raw) == c["sha256"] and x is not None and (x["sha256"] if isinstance(x, dict) else x) == c["sha256"],
             "REFERENCIA_R1_NO_AUTENTICADA", c["archivo"])
        return {"cita": c, "filas": {(f["hoja"], f["sentido"]): f for f in json.loads(raw).get("filas", [])}}

    @staticmethod
    def igual_a_referencia(r: dict, f: dict) -> bool:
        """Mismo criterio de igualdad que la verificación histórica (G y testigo iguales) frente a la fila de la referencia citada."""
        import ast
        try:
            punto = f["punto"] if isinstance(f["punto"], dict) else ast.literal_eval(f["punto"])
            G = [float(f["L"]), float(f["U"])]
            tp = {k: float(v) for k, v in r["testigo"]["punto"].items() if k in punto}
            return (list(r["G"]) == G and tp == {k: float(v) for k, v in punto.items()} and int(r["testigo"]["indice_contexto"]) == int(f["indice_contexto"])
                    and f.get("testigo") == "definitivo")
        except (KeyError, TypeError, ValueError, SyntaxError):
            return False

    def cobertura_orquestador(self, cd, verificacion_p, requeridos, muestra_p, referencia: dict | None = None) -> dict:
        """Contrato de ACEPTACIÓN de una tarea R1 del orquestador (no cambia ningún criterio científico histórico: la verificación histórica
        sigue juzgando G/testigo/agregados; esto exige que TODO lo asignado esté presente, sea único, terminal admisible y verificado):
          - archivos de resultados con nombre canónico (Corrida.f) e integridad de checkpoint (Corrida.leer);
          - unicidad por (afirmación, sentido); AJENOS (afirmaciones fuera de la asignación) -> rechazo; el OTRO sentido de una afirmación
            asignada (el productor histórico calcula ambos) es SUBPRODUCTO: se conserva, no cuenta para la tarea ni para dependientes;
          - cobertura: cada requerido presente; estado terminal, nunca no_ejecutado/error, e igual al histórico cuando la verificación lo da;
          - validación: fila de verificación comparable y ok para CADA requerido;
          - identidad de la muestra: muestra.json = afirmaciones requeridas y identidad.json del orquestador ligada a esos bytes."""
        cd = Path(cd)
        C = object.__new__(self.OB.Corrida)
        C.d = cd
        req = {tuple(x) for x in requeridos}
        afs_req = {c for c, _ in req}
        recs, dup, malos = {}, [], []
        for f in sorted((cd / "resultados").glob("*.json")) if (cd / "resultados").exists() else []:
            try:
                r = json.loads(f.read_bytes())
                k = (r.get("afirmacion"), r.get("sentido"))
                if f.resolve() != C.f(*k).resolve():
                    malos.append(f.name)
                    continue
                C.leer(*k)
            except (ValueError, SystemExit, TypeError) as ex:
                malos.append("%s: %s" % (f.name, str(ex)[:80]))
                continue
            if k in recs:
                dup.append(k)
            recs[k] = r
        ajenos = sorted(k for k in recs if k[0] not in afs_req)
        subproductos = sorted(k for k in recs if k[0] in afs_req and k not in req)
        faltan = sorted(req - set(recs))
        vb = Path(verificacion_p).read_bytes() if Path(verificacion_p).exists() else b"{}"
        filas = {(x.get("afirmacion"), x.get("sentido")): x for x in json.loads(vb).get("filas", [])}
        no_adm, no_val = [], []
        ref = (referencia or {}).get("filas") or {}
        por_ref, por_ver = 0, 0
        for k in sorted(req & set(recs)):
            r, f, fr = recs[k], filas.get(k) or {}, ref.get(k)
            h = f.get("estado_historico", (fr or {}).get("estado"))
            h = ESTADO_EQUIVALENTE.get(h, h)
            if r.get("estado") in ESTADOS_NO_ADMISIBLES or r.get("estado") not in self.OB.TERMINALES or (h is not None and r.get("estado") != h):
                no_adm.append(k)
            v_orq = f.get("comparable") is True and f.get("ok") is True
            v_ref = fr is not None and self.igual_a_referencia(r, fr)
            if f.get("comparable") is True and not v_orq:            # la verificación histórica, cuando juzga, no se puede contradecir
                no_val.append(k)
            elif not (v_orq or v_ref):
                no_val.append(k)
            else:
                por_ver += v_orq
                por_ref += v_ref
        mraw = Path(muestra_p).read_bytes() if Path(muestra_p).exists() else b""
        muestra_ok = bool(mraw) and json.loads(mraw).get("afirmaciones") == sorted(afs_req)
        ident = json.loads((cd / "identidad.json").read_bytes()) if (cd / "identidad.json").exists() else {}
        ident_ok = bool(mraw) and ident.get("muestra_sha256") == sha(mraw)
        cods = [c for c, v in (("SIN_REQUERIDOS", not req), ("RESULTADO_NO_CANONICO_O_ALTERADO", malos), ("RESULTADO_DUPLICADO", dup), ("RESULTADO_AJENO", ajenos),
                                ("REQUERIDO_FALTANTE", faltan), ("ESTADO_NO_ADMISIBLE", no_adm), ("REQUERIDO_NO_VALIDADO", no_val),
                                ("MUESTRA_DISTINTA_DE_LA_ASIGNACION", not muestra_ok), ("IDENTIDAD_DE_MUESTRA_DISTINTA", not ident_ok)) if v]
        return {"cumple": not cods, "codigos": cods, "requeridos": len(req), "presentes": len(req & set(recs)), "faltan": [list(x) for x in faltan[:20]],
                "n_faltan": len(faltan), "ajenos": [list(x) for x in ajenos[:20]], "duplicados": [list(x) for x in dup[:20]], "no_canonicos": malos[:20],
                "no_admisibles": [list(x) for x in no_adm[:20]], "no_validados": [list(x) for x in no_val[:20]], "subproductos": len(subproductos),
                "muestra_ok": muestra_ok, "identidad_muestra_ok": ident_ok, "validados_por_verificacion_historica": por_ver, "validados_por_referencia_citada": por_ref,
                "referencia": (referencia or {}).get("cita")}

    # ------------------------------------------------------------------ rem44: INTERCAMBIO DE PRODUCTOS ACEPTADOS (R1-D) y VALIDACIÓN GLOBAL (R1-V)
    FUENTES_D = {"PRV": "cierre_df_paso4_3_7_2026-10-05_lima1958", "XDD": "extremos_df_d_3_7_2026-10-05_lima0738", "CAN": "cierre_candidato_3_7_2026-10-04_lima2103"}

    def componentes_de(self, afirmaciones: list, deps: dict | None = None) -> dict:
        """Componentes AUTORIZADOS de los agregados de una muestra: cierre por las dependencias de la autoridad (las del ContextoS6 o las
        del plan del orquestador regenerado bajo S6, idéntico al histórico final)."""
        deps = deps if deps is not None else (self.OB.dependencias(self.ctx.claims) if hasattr(self.ctx, "claims") else None)
        need(deps is not None, "CONTEXTO_SIN_AFIRMACIONES")
        orden = self.OB.cierre(list(afirmaciones), deps)
        return {"hojas": sorted(c for c in orden if self.OB.campos(c)["fam"] == "ci"), "agregados": sorted(c for c in orden if self.OB.campos(c)["fam"] != "ci")}

    def intercambio(self, cd, hojas_aceptadas: dict, fuentes_aceptadas: dict, requeridas: set) -> dict:
        """Prepara la corrida del orquestador de R1-D con los PRODUCTOS ACEPTADOS (nunca recalcula hojas aceptadas ni recupera productos
        ajenos en silencio):
          - hojas_aceptadas {(afirmación, sentido): registro del checkpoint aceptado (con contenido_sha256)}: se SIEMBRAN en resultados/
            exactamente las `requeridas` (componentes autorizados); una ausente, ajena o alterada -> rechazo;
          - fuentes_aceptadas {(clave, rel): ruta del producto aceptado}: E5.auth(clave, rel) devuelve ESE producto (B1/B2/B3/A1) en lugar
            del histórico; se registra el sha256 de cada uno.
        Devuelve la evidencia del intercambio."""
        cd = Path(cd)
        need(set(hojas_aceptadas) == set(requeridas), "COMPONENTES_DISTINTOS_DE_LOS_AUTORIZADOS",
             "faltan %d, sobran %d" % (len(set(requeridas) - set(hojas_aceptadas)), len(set(hojas_aceptadas) - set(requeridas))))
        C = self.OB.Corrida(cd)
        sembradas = {}
        for (cid, s_), r in sorted(hojas_aceptadas.items()):
            need(r.get("afirmacion") == cid and r.get("sentido") == s_ and r.get("contenido_sha256") == self.OB.sha(self.OB.canon({k: v for k, v in r.items() if k != "contenido_sha256"})),
                 "HOJA_ACEPTADA_ALTERADA", "%s:%s" % (cid, s_))
            need(r.get("estado") in self.OB.TERMINALES and r.get("estado") not in ESTADOS_NO_ADMISIBLES, "HOJA_ACEPTADA_NO_TERMINAL", "%s:%s" % (cid, s_))
            self.OB.atomico(C.f(cid, s_), (json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8"))
            sembradas[cid + "|" + s_] = r["contenido_sha256"]
        import importlib
        E5 = importlib.import_module("codigo.extremos_G_df_v5")
        orig = getattr(E5, "_auth_historico", E5.auth)
        inyectadas = {}
        for (clave, rel), ruta in sorted(fuentes_aceptadas.items()):
            need(clave in self.FUENTES_D, "FUENTE_NO_INTERCAMBIABLE", clave)
            inyectadas["%s:%s" % (clave, rel)] = sha(Path(ruta).read_bytes())

        def auth(clave, rel):
            if (clave, rel) in fuentes_aceptadas:
                b = Path(fuentes_aceptadas[(clave, rel)]).read_bytes()
                need(sha(b) == inyectadas["%s:%s" % (clave, rel)], "PRODUCTO_ACEPTADO_ALTERADO", rel)
                return json.loads(b)
            return orig(clave, rel)
        E5._auth_historico = orig
        E5.auth = auth
        return {"hojas_sembradas": len(sembradas), "hojas_sembradas_sha256": sha(json.dumps(sembradas, sort_keys=True).encode()), "fuentes_inyectadas": inyectadas}

    def hojas_intactas(self, cd, evidencia: dict, hojas_aceptadas: dict) -> bool:
        """Tras producir: las hojas sembradas siguen idénticas (el orquestador las REUTILIZA como terminales; nunca las recalcula)."""
        C = object.__new__(self.OB.Corrida)
        C.d = Path(cd)
        return all((C.leer(cid, s_) or {}).get("contenido_sha256") == r["contenido_sha256"] for (cid, s_), r in hojas_aceptadas.items())

    def validar_global(self, aceptadas: dict) -> dict:
        """R1-V: sobre los registros ACEPTADOS de las demás tareas R1 ({tarea: registro}), cada uno cumple y la unión de sus ids requeridos
        es EXACTAMENTE la cobertura R1 autenticada (sin faltantes ni duplicados entre tareas). rem51: la cobertura se lee AUTENTICADA (inventario
        fijado de lima1857 y sha256 del archivo, como en requeridos); criterios sin cambios."""
        cob = self._cobertura()
        esperadas = sorted({"R1-D" if t["tarea"].startswith("R1-D-") else t["tarea"] for t in cob["tareas"]} - {"R1-V"})
        # cobertura por (subtarea de cobertura, id): un mismo identificador puede tener PAPELES distintos (p. ej. las 3 afirmaciones del ensayo
        # R1-F también se clasifican en R1-D-clasificacion); la UNICIDAD se exige entre las tareas de EXTREMOS (A*, B*, C*, D principal)
        papel_no_extremo = ("R1-F", "R1-D-clasificacion", "R1-D-testigos")
        vistos, extremos, dup, no_cumplen = set(), {}, [], []
        for t in esperadas:
            r = aceptadas.get(t)
            if r is not None and (r.get("verificacion") or {}).get("cumple") is not True:
                no_cumplen.append(t)
        for x in cob["tareas"]:
            t = "R1-D" if x["tarea"].startswith("R1-D-") else x["tarea"]
            if t not in aceptadas or t == "R1-V":
                continue
            for i_ in x.get("ids") or []:
                vistos.add((x["tarea"], i_))
                if x["tarea"] not in papel_no_extremo:
                    if i_ in extremos and extremos[i_] != x["tarea"]:
                        dup.append(i_)
                    extremos[i_] = x["tarea"]
        total = sum(len(x.get("ids") or []) for x in cob["tareas"] if x["tarea"] != "R1-V")
        faltan = sorted(set(esperadas) - set(aceptadas))
        cods = [c for c, v in (("TAREAS_R1_SIN_ACEPTAR", faltan), ("REGISTRO_QUE_NO_CUMPLE", no_cumplen), ("IDS_DUPLICADOS_ENTRE_TAREAS", dup),
                                ("COBERTURA_GLOBAL_INCOMPLETA", len(vistos) != total)) if v]
        return {"cumple": not cods, "codigos": cods, "tareas_esperadas": esperadas, "faltan": faltan, "ids_cubiertos": len(vistos), "ids_cobertura": total, "duplicados": dup[:10]}

    def producir(self, dirc, muestra_p, opts):
        """CÁLCULO CIENTÍFICO (solo con autorización): orquestador_b.ejecutar con el ContextoS6 (mismo método v5, mismas opciones)."""
        return self.OB.ejecutar(str(dirc), str(muestra_p), list(opts))

    def verificar(self, dirc, hojas_p, plan_p, out):
        """VALIDACIÓN y COMPARACIÓN del orquestador (reproducción frente a las mediciones históricas autenticadas y agregados recalculados)."""
        return self.OB.verificar(str(dirc), str(hojas_p), str(plan_p), str(out))
