"""REGISTRO DE VALIDACIÓN PRODUCTIVA generado por la RUTA del paso 4 (candidato S6; NO OFICIAL; nunca escrito a mano) y ENSAMBLAJE POR
UNIDAD del paquete nuevo hacia el comparador.

Ejecuta el validador productivo INSTALADO (paquete_seleccion.verificar_paquete en modo «validar»: la misma ruta común que usa
`seleccion_paso4 validar`, con el contexto S6 de la corrida y su modelo) sobre los BYTES FINALES de un paquete de la corrida nueva y
escribe el registro que exige el comparador (comparar_reproduccion.estado_productivo):
  {"validador": {"archivo", "sha256"}, "generado_por": {"modulo", "sha256", "contexto_identidad_sha256", "paquete", "dictamen_sha256"},
   "verificacion": {cumple, codigos, productor, contrato, hechos_verificados}, "unidades": {<unidad>: {documento_sha256, filas_sha256, estado}}}

rem40 (observación de registro_productivo.generar): la relación unidad -> celda -> documento/filas -> clase numérica ya NO viene del mapa
del llamante. Se DERIVA del paquete validado: la selección sellada (fila con «unidad» y clave_celda), el plan (lote de esa clave), los
resultados del lote (celda con esa clave: cell_id, estado ok / no_aplicable) y sus tablas E12. El documento y las filas por unidad los
produce `ensamblar` desde esos bytes; si el llamante aporta rutas, sus bytes deben ser EXACTAMENTE los ensamblados (si no, «rechazada»);
si declara clave o clase, deben coincidir con las derivadas. Cobertura: las unidades pedidas = las filas de la selección del paquete.
Estados: «completa_validada» (celda ok) o «no_aplicable_validada» (celda no_aplicable) SOLO si el paquete CUMPLE y su lote está en los
hechos verificados; si no, «rechazada». El dictamen se escribe como archivo propio (bytes = forma canónica; su sha256 = dictamen_sha256).

No acepta dobles: el verificador debe ser una instancia de la clase Verificador del validador instalado junto a este módulo.
  ensamblar(pdir, unidad, fila=None, contrato="v3") -> (documento, filas)   (sin modelo; solo bytes del paquete; tablas del contrato)
  generar(V, pdir, raiz, unidades=None, salida=None, dictamen=None) -> registro
    unidades (opcional): {<unidad>: {"doc": <rel a raiz>, "filas": <rel a raiz>, ["clave_celda"], ["numerico"]}}; si se omite, ensambla
    cada unidad de la selección en <raiz>/unidades/<unidad>.json y <unidad>_filas.json (':' -> '_').
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
VALIDADOR = "herramientas/s3/validadores/paquete_seleccion.py"
MODULO = "herramientas/b/registro_productivo.py"


class RegistroError(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def need(t, c):
    if not t:
        raise RegistroError(c)


def _validador_instalado(V):
    mod = sys.modules.get(type(V).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR).resolve(), "VERIFICADOR_NO_INSTALADO")
    need(type(V) is getattr(mod, "Verificador", None), "VERIFICADOR_NO_INSTALADO")
    return mod


def _paquete(pdir: Path):
    sel = json.loads((pdir / "seleccion.json").read_bytes())
    plan = json.loads((pdir / "plan.json").read_bytes())
    por_clave = {c: l["lote_id"] for l in plan.get("lotes", []) for c in l.get("celdas", [])}
    filas = {f["unidad"]: f for f in sel.get("filas", []) if isinstance(f, dict) and "unidad" in f}
    need(len(filas) == len([f for f in sel.get("filas", []) if "unidad" in f]), "SELECCION_CON_UNIDADES_REPETIDAS")
    return sel, plan, por_clave, filas


def _celda(pdir: Path, lote: str, clave: str):
    res = json.loads((pdir / "lotes" / lote / "resultados.json").read_bytes())
    c = [x for x in res.get("celdas", []) if x.get("clave_celda") == clave]
    need(len(c) == 1, "CELDA_DEL_LOTE_NO_UNICA")
    return c[0]


def ensamblar(pdir, unidad, fila=None, contrato="v3"):
    """(documento, filas) de UNA unidad desde los bytes del paquete, sin modelo: la celda de su clave en los resultados de su lote (el
    documento lleva la celda COMPLETA como «resultado») y, por tabla E12 del lote, el cierre relacional de esa celda: filas con su
    cell_id (si la tabla tiene cell_id, SOLO esas), con su frontier_id (si la tabla tiene frontier_id y no cell_id), y las ligadas por
    ceiling_id / macro_id / evidence_ref / record_pk o por quantity_id/result_ref que citan sus ids, alcanzadas desde filas ya incluidas."""
    pdir = Path(pdir)
    _, _, por_clave, filas = _paquete(pdir)
    f = fila or filas.get(unidad)
    need(f is not None, "UNIDAD_FUERA_DE_LA_SELECCION_DEL_PAQUETE")
    lote = por_clave.get(f["clave_celda"])
    need(lote is not None, "CLAVE_SIN_LOTE_EN_EL_PLAN")
    c = _celda(pdir, lote, f["clave_celda"])
    cid, fid = c.get("cell_id"), c.get("frontier_id")
    need(isinstance(cid, str) and cid, "CELDA_SIN_CELL_ID")
    tablas = {q.stem: [json.loads(x) for x in q.read_text(encoding="utf-8").splitlines() if x.strip()] for q in sorted((pdir / "lotes" / lote).glob("*.jsonl"))}
    ids = {cid} | ({fid, "CEI:" + fid.split(":", 1)[1]} if isinstance(fid, str) and ":" in fid else set())
    dentro = {t: [False] * len(rows) for t, rows in tablas.items()}
    for _ in range(4):
        nuevo = False
        for t, rows in tablas.items():
            for i, r in enumerate(rows):
                if dentro[t][i]:
                    continue
                if "cell_id" in r:
                    ok = r["cell_id"] == cid
                elif "frontier_id" in r:
                    ok = r["frontier_id"] in ids
                else:
                    pk = r.get("record_pk") if isinstance(r.get("record_pk"), dict) else {}
                    ok = (any(r.get(k) in ids for k in ("ceiling_id", "macro_id", "evidence_ref")) or any(v in ids for v in pk.values())
                          or any(isinstance(r.get(k), str) and any(x in r[k] for x in ids) for k in ("quantity_id", "result_ref")))
                if ok:
                    dentro[t][i] = nuevo = True
                    for k in ("macro_id", "ceiling_id", "frontier_id", "evidence_ref"):
                        if isinstance(r.get(k), str) and r[k][:4] in ("MAC:", "CEI:", "FRN:", "NEV:"):
                            ids.add(r[k])
        if not nuevo:
            break
    from paper2b import contrato_paquete as CP
    esperadas = list(CP.TABLAS[contrato])
    F = {t: [r for i, r in enumerate(rows) if dentro[t][i]] for t, rows in tablas.items()}
    fuera = sorted(t for t, rs in F.items() if rs and t not in esperadas)
    need(not fuera, "FILAS_EN_TABLAS_FUERA_DEL_CONTRATO_%s:%s" % (contrato, ",".join(fuera)))      # nunca se descartan en silencio
    F = {t: F.get(t, []) for t in esperadas}                                                    # tablas del contrato; vacías = []
    res = {k: v for k, v in c.items() if k != "clave_celda"}
    doc = {"id": unidad, "estado_final": "no_aplicable" if c.get("estado") == "no_aplicable" else c.get("estado"), "contrato_exportado": contrato, "resultado": res,
           "ensamblado": {"paquete_lote": lote, "clave_celda": f["clave_celda"], "regla": "cierre relacional de la celda en el lote (rem40)"}}
    return doc, F


def generar(V, pdir, raiz, unidades=None, salida=None, dictamen=None, contrato="v3") -> dict:
    PS = _validador_instalado(V)
    pdir, raiz = Path(pdir).resolve(), Path(raiz).resolve()
    r = PS.verificar_paquete(V, pdir, "validar")              # el validador REAL sobre los bytes finales (nunca lanza)
    sel, plan, por_clave, filas = _paquete(pdir)
    need(filas, "SELECCION_SIN_UNIDADES")
    if unidades is not None:
        need(isinstance(unidades, dict) and sorted(unidades) == sorted(filas), "UNIDADES_DISTINTAS_DE_LA_SELECCION_DEL_PAQUETE")
    hechos = set(r.get("hechos_verificados") or [])
    out = {}
    for u in sorted(filas):
        f = filas[u]
        doc, F = ensamblar(pdir, u, f, contrato=contrato)
        db, fb = canon(doc) + b"\n", canon(F) + b"\n"
        m = (unidades or {}).get(u)
        codigos = []
        if m is None:
            n = u.replace(":", "_")
            rel_d, rel_f = "unidades/%s.json" % n, "unidades/%s_filas.json" % n
            (raiz / "unidades").mkdir(parents=True, exist_ok=True)
            (raiz / rel_d).write_bytes(db)
            (raiz / rel_f).write_bytes(fb)
        else:
            need(isinstance(m, dict) and isinstance(m.get("doc"), str) and isinstance(m.get("filas"), str), "UNIDAD_SIN_RUTAS:" + str(u))
            rel_d, rel_f = m["doc"], m["filas"]
            if ((raiz / rel_d).read_bytes(), (raiz / rel_f).read_bytes()) != (db, fb):
                codigos.append("PRODUCTO_NO_DERIVADO_DEL_PAQUETE")
            if "clave_celda" in m and m["clave_celda"] != f["clave_celda"]:
                codigos.append("CLAVE_DECLARADA_DISTINTA_DE_LA_DERIVADA")
        estado_celda = doc["estado_final"]
        numerico = {"ok": True, "no_aplicable": False}.get(estado_celda)
        if numerico is None:
            codigos.append("CELDA_SIN_ESTADO_ADMITIDO")
        if m is not None and "numerico" in m and m["numerico"] is not numerico:
            codigos.append("CLASE_DECLARADA_DISTINTA_DE_LA_DERIVADA")
        if not r.get("cumple") or por_clave.get(f["clave_celda"]) not in hechos:
            codigos.extend(r.get("codigos") or ["CELDA_NO_VALIDADA_EN_EL_PAQUETE"])
        est = ("completa_validada" if numerico else "no_aplicable_validada") if not codigos else "rechazada"
        out[str(u)] = {"documento_sha256": sha((raiz / rel_d).read_bytes()), "filas_sha256": sha((raiz / rel_f).read_bytes()), "estado": est,
                       "documento": rel_d, "filas": rel_f, "clave_celda": f["clave_celda"], "numerico_derivado": numerico, "codigos": codigos}
    verif = {k: r.get(k) for k in ("cumple", "codigos", "productor", "contrato", "hechos_verificados", "dictamen")}
    reg = {"validador": {"archivo": VALIDADOR, "sha256": sha((INSTALACION / VALIDADOR).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(V.ctx.identity)),
                            "autoridad": getattr(V.ctx.authority, "kind", None), "paquete": str(pdir), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": out}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg


# ---------------------------------------------------------------------------------------------------------- R3 (rem42)
VALIDADOR_R3 = "herramientas/b/validador_r3.py"


def _validador_r3_instalado(VR):
    mod = sys.modules.get(type(VR).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_R3).resolve(), "VALIDADOR_R3_NO_INSTALADO")
    need(type(VR) is getattr(mod, "ValidadorR3S6", None), "VALIDADOR_R3_NO_INSTALADO")
    return mod


def generar_r3(VR, raiz, productos, definiciones, salida=None, dictamen=None, contrato="v3") -> dict:
    """R3 (S2/S3; rem42): VALIDACIÓN PRODUCTIVA con el validador R3 INSTALADO (validador_r3.ValidadorR3S6: comprobaciones históricas de los
    lotes R3 sin cambios, con el contexto S6 de la corrida) sobre los BYTES FINALES de cada unidad (documento y filas leídos de disco).
    productos: {<unidad>: {"documento": <rel a raiz>, "filas": <rel a raiz>}}; definiciones: {<unidad>: definición VINCULADA (vinculo_paso4)}.
    Estados por unidad = clasificación del validador («completa_validada» / «no_aplicable_validada» / «rechazada»); el dictamen CUMPLE solo si
    todas las unidades están validadas. No acepta dobles: VR debe ser instancia de la clase del validador instalado junto a este módulo."""
    mod = _validador_r3_instalado(VR)
    raiz = Path(raiz).resolve()
    need(isinstance(productos, dict) and productos and sorted(productos) == sorted(definiciones), "UNIDADES_R3_SIN_DEFINICION")
    out, val = {}, {}
    for u in sorted(productos):
        rel_d, rel_f = productos[u]["documento"], productos[u]["filas"]
        db, fb = (raiz / rel_d).read_bytes(), (raiz / rel_f).read_bytes()
        try:
            v = VR.celda(definiciones[u], json.loads(db), json.loads(fb), contrato_exigido=contrato)
        except Exception as ex:  # noqa: BLE001  (el validador no lanza; defensa: todo defecto es un rechazo con motivo)
            v = {"clasificacion": "rechazada", "ok": False, "motivos": ["validador: %s: %s" % (type(ex).__name__, str(ex)[:300])]}
        est = v["clasificacion"] if v.get("clasificacion") in ("completa_validada", "no_aplicable_validada") and not v.get("motivos") else "rechazada"
        out[str(u)] = {"documento_sha256": sha(db), "filas_sha256": sha(fb), "estado": est, "documento": rel_d, "filas": rel_f,
                       "codigos": [] if est != "rechazada" else ["UNIDAD_R3_RECHAZADA_POR_EL_VALIDADOR"], "motivos": list(v.get("motivos") or [])[:20]}
        val[str(u)] = {"clasificacion": est, "motivos": list(v.get("motivos") or [])[:20]}
    cumple = all(e["estado"] in ("completa_validada", "no_aplicable_validada") for e in out.values())
    verif = {"cumple": cumple, "codigos": [] if cumple else ["UNIDADES_R3_RECHAZADAS"], "productor": getattr(VR.ctx, "identity_sha256", None), "contrato": contrato,
             "hechos_verificados": sorted(u for u, e in out.items() if e["estado"] != "rechazada"), "dictamen": val}
    reg = {"validador": {"archivo": VALIDADOR_R3, "sha256": sha((INSTALACION / VALIDADOR_R3).read_bytes()), "historico": {"archivo": mod.HISTORICO[0], "sha256": mod.HISTORICO[1]}},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(VR.ctx.identity)),
                            "autoridad": getattr(VR.ctx.authority, "kind", None), "paquete": str(raiz), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": out}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg


# ---------------------------------------------------------------------------------------------------------- R1 (rem43)
VALIDADOR_R1 = "herramientas/b/r1_s6.py"


def generar_r1(P, sal, tarea, corrida_rel, verificacion_rel, salida=None, dictamen=None, rc_productor=None) -> dict:
    """R1 (rem43): registro de una tarea R1 producida por la pila histórica bajo S6 (r1_s6.PilaR1S6 INSTALADA; sin dobles). Documento =
    manifiesto (sha256 de cada archivo) de la corrida del orquestador; filas = la VERIFICACIÓN del orquestador (reproducción frente a
    las mediciones históricas autenticadas y coherencia de agregados). Cumple solo si el productor terminó con 0 y la verificación
    declara reproduccion_y_coherencia=True con al menos un resultado comparable."""
    mod = sys.modules.get(type(P).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_R1).resolve() and type(P) is getattr(mod, "PilaR1S6", None), "PILA_R1_NO_INSTALADA")
    sal = Path(sal).resolve()
    cd = sal / corrida_rel
    man = {q.relative_to(cd).as_posix(): sha(q.read_bytes()) for q in sorted(cd.rglob("*")) if q.is_file()} if cd.exists() else {}
    (sal / "r1_productos.json").write_bytes(canon({"tarea": tarea, "corrida": corrida_rel, "archivos": man}) + b"\n")
    vb = (sal / verificacion_rel).read_bytes() if (sal / verificacion_rel).exists() else b""
    v = json.loads(vb) if vb else {}
    # rem44 P4-R1-COBERTURA: la aceptación exige la COBERTURA EXACTA de la asignación (requeridos derivados de la cobertura AUTENTICADA y
    # del registro v4, nunca del nombre de la tarea ni de comparables>0): presencia, unicidad, pertenencia, estado y validación de CADA
    # requerido e identidad de la muestra; el dictamen histórico (reproduccion_y_coherencia) se exige además, sin cambiar sus criterios.
    req = P.requeridos_orquestador(tarea)
    cob = P.cobertura_orquestador(cd, sal / verificacion_rel, req, sal / "paquete/muestra.json", P.referencia_cobertura(tarea))
    cumple = rc_productor == 0 and v.get("reproduccion_y_coherencia") is True and bool(man) and cob["cumple"]
    cods = ([] if rc_productor == 0 else ["PRODUCTOR_NO_TERMINO"]) + ([] if v.get("reproduccion_y_coherencia") is True else ["R1_NO_REPRODUCIDA_O_INCOHERENTE"]) + cob["codigos"]
    verif = {"cumple": cumple, "codigos": [] if cumple else (cods or ["R1_NO_REPRODUCIDA_O_INCOHERENTE"]), "productor": getattr(P.ctx, "identity_sha256", None),
             "rc_productor": rc_productor, "comparables": v.get("comparables"), "verificados_ok": v.get("verificados_ok"), "por_ruta": v.get("por_ruta"),
             "cobertura": cob}
    u = "R1:" + tarea
    ent = {u: {"documento_sha256": sha((sal / "r1_productos.json").read_bytes()), "filas_sha256": sha(vb), "estado": "completa_validada" if cumple else "rechazada",
               "documento": "r1_productos.json", "filas": verificacion_rel}}
    reg = {"validador": {"archivo": VALIDADOR_R1, "sha256": sha((INSTALACION / VALIDADOR_R1).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(P.ctx.identity)),
                            "autoridad": getattr(P.ctx.authority, "kind", None), "paquete": str(sal / "paquete"), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": ent}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg



def generar_r1_ruta(P, sal, tarea, plan_ruta, rcs, salida=None, dictamen=None) -> dict:
    """R1 por COMANDO HISTÓRICO (rem44; A*, B*, F): registro con el validador de la fase R1 (r1_s6.py) y la validación de r1_rutas
    (salidas iguales a las históricas del mismo comando; cobertura por id; derivación sin observaciones pendientes). Sin dobles en la
    PILA: P debe ser la PilaR1S6 instalada (su contexto es el de la corrida)."""
    mod = sys.modules.get(type(P).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_R1).resolve() and type(P) is getattr(mod, "PilaR1S6", None), "PILA_R1_NO_INSTALADA")
    import r1_rutas as RR
    sal = Path(sal).resolve()
    v = RR.validar(plan_ruta, Path(P.d["raiz_fuentes"]), sal / "paquete", rcs)
    man = {q.relative_to(sal / "paquete").as_posix(): sha(q.read_bytes()) for q in sorted((sal / "paquete").rglob("*")) if q.is_file()}
    (sal / "r1_productos.json").write_bytes(canon({"tarea": tarea, "paquete": "paquete", "archivos": man, "plan_ruta_sha256": sha(canon(plan_ruta))}) + b"\n")
    (sal / "validacion_ruta.json").write_bytes(canon(v) + b"\n")
    verif = {"cumple": bool(v["cumple"]), "codigos": v["codigos"], "productor": getattr(P.ctx, "identity_sha256", None), "validacion_ruta": v,
             "plan_ruta_sha256": sha(canon(plan_ruta)), "r1_rutas_sha256": sha((INSTALACION / "herramientas/b/r1_rutas.py").read_bytes())}
    u = "R1:" + tarea
    ent = {u: {"documento_sha256": sha((sal / "r1_productos.json").read_bytes()), "filas_sha256": sha((sal / "validacion_ruta.json").read_bytes()),
               "estado": "completa_validada" if v["cumple"] else "rechazada", "documento": "r1_productos.json", "filas": "validacion_ruta.json"}}
    reg = {"validador": {"archivo": VALIDADOR_R1, "sha256": sha((INSTALACION / VALIDADOR_R1).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(getattr(P.ctx, "identity", {}))),
                            "autoridad": getattr(getattr(P.ctx, "authority", None), "kind", None), "paquete": str(sal / "paquete"), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": ent}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg


def generar_r1_opcion(P, sal, tarea, evidencia, salida=None, dictamen=None) -> dict:
    """rem49: R1 con una OPCIÓN candidata ACTIVA (B3/A1A2/A3; activa solo si la autorización reconstruida la declara: opciones_p1.opciones_
    autorizadas). Mismo validador de fase (r1_s6.py) y misma pila instalada que generar_r1_ruta; la verificación es la EVIDENCIA de la opción
    (validación inicial de la ruta o intercambio auténtico), escrita como filas y ligada a los bytes del paquete validado."""
    mod = sys.modules.get(type(P).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_R1).resolve() and type(P) is getattr(mod, "PilaR1S6", None), "PILA_R1_NO_INSTALADA")
    need(isinstance(evidencia, dict) and evidencia.get("opcion") and isinstance(evidencia.get("cumple"), bool), "EVIDENCIA_DE_OPCION_INVALIDA")
    sal = Path(sal).resolve()
    (sal / "paquete").mkdir(parents=True, exist_ok=True)
    man = {q.relative_to(sal / "paquete").as_posix(): sha(q.read_bytes()) for q in sorted((sal / "paquete").rglob("*")) if q.is_file()}
    (sal / "r1_productos.json").write_bytes(canon({"tarea": tarea, "paquete": "paquete", "archivos": man, "opcion": evidencia["opcion"]}) + b"\n")
    (sal / "validacion_opcion.json").write_bytes(canon(evidencia) + b"\n")
    verif = {"cumple": evidencia["cumple"], "codigos": list(evidencia.get("codigos") or []), "opcion": evidencia["opcion"], "productor": getattr(P.ctx, "identity_sha256", None),
             "autorizacion_de_la_opcion": evidencia.get("autorizacion"), "evidencia_sha256": sha((sal / "validacion_opcion.json").read_bytes()),
             "opciones_p1_sha256": sha((INSTALACION / "herramientas/b/opciones_p1.py").read_bytes())}
    u = "R1:" + tarea
    ent = {u: {"documento_sha256": sha((sal / "r1_productos.json").read_bytes()), "filas_sha256": sha((sal / "validacion_opcion.json").read_bytes()),
               "estado": "completa_validada" if evidencia["cumple"] else "rechazada", "documento": "r1_productos.json", "filas": "validacion_opcion.json"}}
    reg = {"validador": {"archivo": VALIDADOR_R1, "sha256": sha((INSTALACION / VALIDADOR_R1).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(getattr(P.ctx, "identity", {}))),
                            "autoridad": getattr(getattr(P.ctx, "authority", None), "kind", None), "paquete": str(sal / "paquete"), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": ent}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg


ESTADOS_ADMISIBLES = ("completa_validada", "no_aplicable_validada")


def generar_r1_global(P, sal, tarea, fuentes, tareas_del_plan, consumos=None, artefactos=None, salida=None, dictamen=None) -> dict:
    """rem51 (P4-R1-V-REGISTRO-GLOBAL): registro de la VALIDACIÓN GLOBAL de R1-V con el validador de la fase R1 (r1_s6.py) y la pila
    instalada (sin dobles), en lugar de la ruta por comando (que la rechazaba siempre: SIN_COMANDOS y archivo ajeno). El generador no recibe
    ningún «cumple»:
      - `fuentes` {tarea: procedencia} son las que la RUTA COMÚN entregó (tarea_r1.productos_aceptados: aceptación en esta corrida con su
        árbol, o en una corrida previa con su autoridad RECONSTRUIDA por corrida_paso4.aceptaciones_previas);
      - de cada fuente re-lee el árbol ACTUAL (= el aceptado), su registro (del registro instalado y del validador de su fase), su dictamen
        (= la verificación del registro) y su ÚNICA unidad R1:<tarea> (estado admisible, ligada a los sha256 de sus productos);
      - ejecuta él mismo P.validar_global sobre esos registros (cobertura autenticada exacta, sin duplicados, cada registro cumple);
      - exige que las tareas del plan (cierre de las dependencias de la tarea) sean EXACTAMENTE las que espera la cobertura, que no haya
        fuentes ajenas y, para cada tarea de `consumos` ({tarea: dependencias}), que las fuentes que ELLA consumió (su registro de consumo
        paquete/dependencias_consumidas.json, dentro de su árbol aceptado) sean exactamente las validadas aquí (enlace R1-D -> R1-V);
      - el paquete solo contiene los artefactos DECLARADOS del trabajador (r1_rutas._artefactos); cualquier otro archivo es ajeno.
    Las fuentes quedan LIGADAS en la verificación (salida, raíz, árbol, registro, dictamen, unidad y autoridad): corrida_paso4 vuelve a
    comprobarlas al reutilizar la aceptación (fuentes_ligadas_vigentes)."""
    mod = sys.modules.get(type(P).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_R1).resolve() and type(P) is getattr(mod, "PilaR1S6", None), "PILA_R1_NO_INSTALADA")
    import r1_rutas as RR
    sal = Path(sal).resolve()
    (sal / "paquete").mkdir(parents=True, exist_ok=True)
    T = Path(P.d["raiz_fuentes"])
    adm, inf_art, cods = RR._artefactos({"artefactos_del_trabajador": dict(artefactos or {})}, T, sal / "paquete")
    cods = sorted(set(cods))
    man = {q.relative_to(sal / "paquete").as_posix(): sha(q.read_bytes()) for q in sorted((sal / "paquete").rglob("*")) if q.is_file()}
    ajenos = sorted(set(man) - set(adm))
    if ajenos:
        cods.append("ARCHIVO_AJENO_EN_EL_PAQUETE")
    regs, lig, rech = {}, {}, []
    for x, pv in sorted((fuentes or {}).items()):
        s = Path(str(pv.get("salida", "")))
        arbol = {q.relative_to(s).as_posix(): sha(q.read_bytes()) for q in sorted(s.rglob("*")) if q.is_file()} if s.is_dir() else {}
        try:
            rb, db = (s / "registro_productivo.json").read_bytes(), (s / "dictamen_validacion.json").read_bytes()
            reg, ver = json.loads(rb), json.loads(db)
        except (OSError, ValueError):
            rech.append({"tarea": x, "motivo": "REGISTRO_DE_LA_FUENTE_AUSENTE_O_ILEGIBLE"})
            continue
        g, vd = reg.get("generado_por") or {}, reg.get("validador") or {}
        us = reg.get("unidades") or {}
        e = us.get("R1:" + x) or {}
        mot = ("FUENTE_ALTERADA_TRAS_SU_ACEPTACION" if not arbol or sha(canon(arbol)) != pv.get("arbol_sha256") else
               "REGISTRO_DE_LA_FUENTE_NO_GENERADO_POR_LA_RUTA" if (g.get("modulo"), g.get("sha256")) != (MODULO, sha(Path(__file__).read_bytes())) else
               "REGISTRO_DE_LA_FUENTE_DE_OTRO_VALIDADOR" if (vd.get("archivo"), vd.get("sha256")) != (VALIDADOR_R1, sha((INSTALACION / VALIDADOR_R1).read_bytes())) else
               "DICTAMEN_DE_LA_FUENTE_DISTINTO" if g.get("dictamen_sha256") != sha(db) or reg.get("verificacion") != ver else
               "UNIDADES_AJENAS_O_DUPLICADAS_EN_LA_FUENTE" if sorted(us) != ["R1:" + x] else
               "ESTADO_NO_ADMISIBLE_EN_LA_FUENTE" if e.get("estado") not in ESTADOS_ADMISIBLES or ver.get("cumple") is not True else
               "UNIDAD_DE_LA_FUENTE_NO_LIGADA_A_SUS_PRODUCTOS" if (e.get("documento_sha256"), e.get("filas_sha256")) != (arbol.get(e.get("documento")), arbol.get(e.get("filas"))) else
               None)
        if mot:
            rech.append({"tarea": x, "motivo": mot})
            continue
        regs[x] = reg
        lig[x] = {"origen": pv.get("origen"), "raiz": pv.get("raiz"), "salida": str(s), "arbol_sha256": pv["arbol_sha256"], "identidad_sha256": pv.get("identidad_sha256"),
                  "autorizacion_sha256": pv.get("autorizacion_sha256"), "acto_mensaje_sha256": pv.get("acto_mensaje_sha256"), "modo_arnes": pv.get("modo_arnes"),
                  "registro_sha256": sha(rb), "dictamen_sha256": sha(db), "unidad": {"estado": e["estado"], "documento_sha256": e["documento_sha256"], "filas_sha256": e["filas_sha256"]}}
    v = P.validar_global(regs)
    ajenas = sorted(set(fuentes or {}) - set(v["tareas_esperadas"]))
    no_consumidas = []
    for x, deps in sorted((consumos or {}).items()):
        if x not in lig:
            continue
        try:
            dc = json.loads((Path(lig[x]["salida"]) / "paquete/dependencias_consumidas.json").read_bytes())
        except (OSError, ValueError):
            no_consumidas.append({"tarea": x, "motivo": "SIN_REGISTRO_DE_CONSUMO"})
            continue
        dif = sorted(d_ for d_ in set(deps) | set(dc) if d_ not in dc or d_ not in lig or (dc[d_].get("salida"), dc[d_].get("arbol_sha256")) !=
                     (lig[d_]["salida"], lig[d_]["arbol_sha256"]))
        if dif:
            no_consumidas.append({"tarea": x, "motivo": "FUENTES_DISTINTAS_DE_LAS_CONSUMIDAS", "dependencias": dif[:10]})
    cods += [c for c, w in (("FUENTE_RECHAZADA", rech), ("FUENTE_AJENA_A_LA_COBERTURA", ajenas), ("ENLACE_DE_CONSUMO_DISTINTO", no_consumidas),
                            ("TAREAS_DEL_PLAN_DISTINTAS_DE_LA_COBERTURA", sorted(tareas_del_plan or []) != v["tareas_esperadas"])) if w] + list(v["codigos"])
    cumple = not cods
    glob_ = {"validacion_global": v, "fuentes": lig, "fuentes_rechazadas": rech, "fuentes_ajenas": ajenas, "enlace_de_consumo": no_consumidas,
             "tareas_del_plan": sorted(tareas_del_plan or []), "artefactos_del_trabajador": inf_art, "ajenos": ajenos}
    (sal / "validacion_global.json").write_bytes(canon(glob_) + b"\n")
    (sal / "r1_productos.json").write_bytes(canon({"tarea": tarea, "paquete": "paquete", "archivos": man, "fuentes_sha256": sha(canon(lig))}) + b"\n")
    verif = {"cumple": cumple, "codigos": cods, "productor": getattr(P.ctx, "identity_sha256", None), "fuentes": lig, "validacion_global_sha256": sha((sal / "validacion_global.json").read_bytes()),
             "r1_s6_sha256": sha((INSTALACION / VALIDADOR_R1).read_bytes())}
    u = "R1:" + tarea
    ent = {u: {"documento_sha256": sha((sal / "r1_productos.json").read_bytes()), "filas_sha256": sha((sal / "validacion_global.json").read_bytes()),
               "estado": "completa_validada" if cumple else "rechazada", "documento": "r1_productos.json", "filas": "validacion_global.json"}}
    reg = {"validador": {"archivo": VALIDADOR_R1, "sha256": sha((INSTALACION / VALIDADOR_R1).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(getattr(P.ctx, "identity", {}))),
                            "autoridad": getattr(getattr(P.ctx, "authority", None), "kind", None), "paquete": str(sal / "paquete"), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": ent}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg


# ---------------------------------------------------------------------------------------------------------- PRODUCCIÓN (rem56)
VALIDADOR_PROD = "herramientas/b/validador_prod.py"


def generar_prod(VR, raiz, productos, especificaciones, salida=None, dictamen=None, d4=False) -> dict:
    """PROD1/PROD2/PROD3 (rem56): VALIDACIÓN PRODUCTIVA con el validador de producción INSTALADO (validador_prod.ValidadorProdS6, que reutiliza
    paper2b.rules.Checker) sobre los BYTES FINALES de cada unidad. Misma forma que generar_r3: estados por unidad del validador; CUMPLE solo si
    todas están validadas. No acepta dobles: VR debe ser instancia de la clase del validador instalado junto a este módulo."""
    mod = sys.modules.get(type(VR).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INSTALACION / VALIDADOR_PROD).resolve() and type(VR) is getattr(mod, "ValidadorProdS6", None),
         "VALIDADOR_PROD_NO_INSTALADO")
    raiz = Path(raiz).resolve()
    need(isinstance(productos, dict) and productos and sorted(productos) == sorted(especificaciones), "UNIDADES_PROD_SIN_ESPECIFICACION")
    out, val = {}, {}
    for u in sorted(productos):
        rel_d, rel_f = productos[u]["documento"], productos[u]["filas"]
        db, fb = (raiz / rel_d).read_bytes(), (raiz / rel_f).read_bytes()
        try:
            v = VR.unidad(especificaciones[u], json.loads(db), json.loads(fb))
        except Exception as ex:  # noqa: BLE001
            v = {"clasificacion": "rechazada", "motivos": ["validador: %s: %s" % (type(ex).__name__, str(ex)[:300])]}
        est = v.get("clasificacion") if v.get("clasificacion") in ("completa_validada", "no_aplicable_validada", "incompleta_validada", "fallida_validada") and not v.get("motivos") else "rechazada"
        out[str(u)] = {"documento_sha256": sha(db), "filas_sha256": sha(fb), "estado": est, "documento": rel_d, "filas": rel_f,
                       "codigos": [] if est != "rechazada" else ["UNIDAD_PROD_RECHAZADA_POR_EL_VALIDADOR"], "motivos": list(v.get("motivos") or [])[:20]}
        val[str(u)] = {"clasificacion": est, "motivos": list(v.get("motivos") or [])[:20]}
        if d4 and est == "incompleta_validada":       # rem66 (QUIEBRES-D4 sellada): incompleta CONSERVADA como declarada, nunca completa
            if str(Path(__file__).resolve().parent) not in sys.path:
                sys.path.insert(0, str(Path(__file__).resolve().parent))
            import decision_d4 as D4
            fil = json.loads(fb)
            if D4.elegible(fil):
                out[str(u)].update(declarada_D4=True, nota_D4=D4.nota(fil)); val[str(u)]["declarada_D4"] = True
    cumple = all(e["estado"] in ("completa_validada", "no_aplicable_validada") or e.get("declarada_D4") for e in out.values())
    verif = {"cumple": cumple, "codigos": [] if cumple else ["UNIDADES_PROD_RECHAZADAS"], "productor": getattr(VR.ctx, "identity_sha256", None),
             "hechos_verificados": sorted(u for u, e in out.items() if e["estado"] != "rechazada"), "dictamen": val}
    reg = {"validador": {"archivo": VALIDADOR_PROD, "sha256": sha((INSTALACION / VALIDADOR_PROD).read_bytes())},
           "generado_por": {"modulo": MODULO, "sha256": sha(Path(__file__).read_bytes()), "contexto_identidad_sha256": sha(canon(getattr(VR.ctx, "identity", {}))),
                            "autoridad": getattr(getattr(VR.ctx, "authority", None), "kind", None), "paquete": str(raiz), "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": out}
    if dictamen is not None:
        Path(dictamen).write_bytes(canon(verif))
    if salida is not None:
        Path(salida).write_bytes(canon(reg) + b"\n")
    return reg
