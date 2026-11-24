"""rem136 — NÚCLEO del paquete de EMISIÓN LAMBDA de T8, corrección de PROCEDENCIA (P4-T8-LAMBDA-PROCEDENCIA-EMISION; derivado de rem135
66215f11…; candidato, NO habilitado). Único cambio: la puerta devuelve el contexto autenticado de su invocación y verificar lo recibe, lo
re-autentica con la misma puerta y coteja con él el origen declarado en el resumen del materializador (COMPARTIDOS, DERIVADOS_DEL_MODO;
POR_OPERACION no se coteja). Entrada, manifiesto de fuentes, helper, _finalize, clasificaciones y límites sin cambios.
rem135 — NÚCLEO del paquete de EMISIÓN LAMBDA de T8 (candidato; NO habilitado; ninguna emisión real en rem135).
Reutiliza sin rediseñar la ruta aceptada en el dictamen rem135: EntradaLambda.vista (rem134, 295b13b5…) con su manifiesto de fuentes fijado
(647744d0…), el helper autenticado por ese manifiesto y unidades._finalize instalado (a8aded1d…). cerrar queda interno: aquí no hay vía que
acepte filas, callbacks ni hashes del llamador; el finalizador se carga SOLO desde la ruta y el sha256 del manifiesto de emisión.
  puerta(...)            — antes de leer fuentes o escribir productos (misma regla que la puerta ENF aceptada, rem129/rem130): produccion exige
                           manifiesto real + alcance v3 verificado por C0 (aprobacion_alcance.verificar_documento) y ligado a ESTE manifiesto,
                           índice, código, instalación y límites + decisión humana nativa (decision_humana de C0); al final rechaza alcances
                           etiquetados FIXTURE; ensayo: manifiesto -ENSAYO y sin alcance; candidata: manifiesto real, sin alcance, producto
                           marcado CANDIDATA (nunca productivo).
  cargar(...)            — entrada y finalizador por ruta + sha256 del manifiesto de emisión (los dobles de ensayo, por el manifiesto -ENSAYO).
  construir_producto(...)— filas del producto: clave estable, histórico completo, clasificación derivada, finalización y procedencia.
  verificar(...)         — ÚNICA validación del producto (la usan el verificador y las pruebas): universo, claves, duplicados/faltantes,
                           fuentes, corridas, plan, procedencia, recomputación por la ruta aceptada y preservación de definitivas y captura."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
PIEZAS = ("validar_emision_lambda.py", "materializar_lambda.py", "verificar_producto_lambda.py", "emitir_alcance_emision.py",
          "admision_integracion.py", "receta_emision_lambda.sh")
TAREAS = ("LAMBDA-T8-MATERIALIZAR", "LAMBDA-T8-VERIFICAR")
OPERACION = "EMISION_LAMBDA_T8"
LIMITES = {"procesos": 3, "tope_s": 2400.0, "suite_s": 3600.0, "union_s": 10800.0}
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
PRODUCTO, RESUMEN, SELLO = "PRODUCTO_T8_LAMBDA.jsonl", "PRODUCTO_RESUMEN.json", "PRODUCTO.sha256"
# rem136 — PROCEDENCIA. Materializar y verificar son operaciones DISTINTAS del mismo alcance (sus dos tareas):
KIND_PRODUCTO = {"produccion": "producto-t8-lambda-PRODUCCION", "candidata": "producto-t8-lambda-CANDIDATA", "ensayo": "producto-t8-lambda-ENSAYO"}
COMPARTIDOS = ("modo", "manifiesto_emision_sha256", "indice_sha256", "alcance_sha256", "decision")  # deben coincidir en ambas operaciones
DERIVADOS_DEL_MODO = ("kind", "productivo")  # se derivan del modo compartido (KIND_PRODUCTO; modo == produccion): no son etiquetas libres
POR_OPERACION = ("tarea", "entradas")  # identifican cada invocación (su tarea del alcance y las rutas recibidas): no se cotejan entre sí
DUPLICADOS_DEL_RESUMEN = ("modo", "manifiesto_emision_sha256")  # copias de nivel superior del resumen: deben coincidir con su puerta


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def autenticar_paquete():
    p = AQUI / "PAQUETE_EMISION_LAMBDA.json"
    if not p.is_file():
        return None, ["INDICE_DEL_PAQUETE_AUSENTE"]
    idx = json.loads(p.read_bytes())
    mal = [n for n in PIEZAS if n not in idx.get("piezas", {}) or not (AQUI / n).is_file() or HF(AQUI / n) != idx["piezas"][n]["sha256"]]
    return HF(p), (["CODIGO_DEL_PAQUETE_NO_AUTENTICO:%s" % mal] if mal else [])


def es_ensayo(me):
    return str(me.get("kind", "")).endswith("-ENSAYO")


def _puerta_invocacion(R, me_raw, me, modo, alcance, decision, tarea):
    R = Path(R)
    C0 = R / me["nucleo"]["ruta"]
    sys.path.insert(0, str(C0 / "herramientas/b"))
    import aprobacion_alcance as AA
    if AA.identidad_instalacion(C0) != NUCLEO_IDENTIDAD or me["nucleo"]["identidad"] != NUCLEO_IDENTIDAD:
        return False, {"motivo": "NUCLEO_DE_OTRA_IDENTIDAD"}
    idx_sha, mal = autenticar_paquete()
    if mal:
        return False, {"motivo": mal[0]}
    if tarea not in TAREAS:
        return False, {"motivo": "TAREA_DESCONOCIDA"}
    if modo == "ensayo":
        if not es_ensayo(me):
            return False, {"motivo": "ENSAYO_CON_MANIFIESTO_REAL"}
        if alcance or decision:
            return False, {"motivo": "ENSAYO_NO_ADMITE_ALCANCE"}
        return True, {"modo": modo, "indice_sha256": idx_sha}
    if es_ensayo(me):
        return False, {"motivo": "MANIFIESTO_DE_ENSAYO_EN_%s" % modo.upper()}
    if modo == "candidata":
        if alcance or decision:
            return False, {"motivo": "CANDIDATA_NO_ADMITE_ALCANCE"}
        return True, {"modo": modo, "indice_sha256": idx_sha}
    if modo != "produccion":
        return False, {"motivo": "MODO_NO_ADMITIDO"}
    if not alcance or not decision:
        return False, {"motivo": "PRODUCCION_SIN_ALCANCE_NI_DECISION"}
    ap = Path(alcance)
    if not ap.is_file():
        return False, {"motivo": "ALCANCE_NO_MATERIALIZADO"}
    ab = ap.read_bytes()
    al = json.loads(ab)
    try:
        AA.verificar_documento(al)
    except AA.Rechazo as ex:
        return False, {"motivo": "ALCANCE_NO_VERIFICABLE:%s" % ex.codigo}
    ent = al.get("entradas") or {}
    codigo = {n: HF(AQUI / n) for n in PIEZAS}
    for cond, causa in ((al.get("operaciones") == [OPERACION], "ALCANCE_DE_OTRA_OPERACION"),
                        (tarea in (al.get("tareas") or []), "TAREA_FUERA_DEL_ALCANCE"),
                        (al.get("lote_manifiesto_sha256") == ent.get("manifiesto_emision") == H(me_raw), "ALCANCE_DE_OTRO_MANIFIESTO"),
                        (ent.get("paquete_emision") == idx_sha and ent.get("codigo_emision") == codigo, "ALCANCE_DE_OTRO_CODIGO"),
                        (al.get("instalacion_identidad") == NUCLEO_IDENTIDAD, "ALCANCE_DE_OTRA_INSTALACION"),
                        (al.get("limites") == LIMITES, "ALCANCE_CON_OTROS_LIMITES"),
                        (al.get("plan_sha256") == me["plan_sha256"], "ALCANCE_DE_OTRO_PLAN")):
        if not cond:
            return False, {"motivo": causa}
    try:
        dec = AA.decision_humana(str(decision), H(ab), al["emitida_utc"])
    except AA.Rechazo as ex:
        return False, {"motivo": "DECISION_NO_VALIDA:%s" % ex.codigo}
    if "FIXTURE" in str(al.get("etiqueta", "")).upper():
        return False, {"motivo": "ALCANCE_FIXTURE_EN_PRODUCCION"}
    return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab), "decision": dec}


def puerta(R, me_raw, me, modo, alcance, decision, tarea):
    """Puerta de cada invocación (la regla rem135, sin cambios, en _puerta_invocacion). Si admite, devuelve el CONTEXTO AUTENTICADO de esa
    invocación: COMPARTIDOS (modo, sha256 del manifiesto leído, índice autenticado, alcance y evidencia nativa de decision_humana de C0; ambos
    None fuera de producción) y POR_OPERACION (tarea y entradas recibidas)."""
    ok, p = _puerta_invocacion(R, me_raw, me, modo, alcance, decision, tarea)
    if not ok:
        return ok, p
    return True, {"modo": modo, "manifiesto_emision_sha256": H(me_raw), "indice_sha256": p["indice_sha256"], "alcance_sha256": p.get("alcance_sha256"),
                  "decision": p.get("decision"), "tarea": tarea,
                  "entradas": {"alcance": str(alcance) if alcance else None, "decision": str(decision) if decision else None}}


def contexto_autentico(R, me_raw, me, contexto):
    """El contexto esperado se RE-AUTENTICA con la misma puerta (C0: verificar_documento y decision_humana) desde las entradas de su invocación
    y debe reproducirla exactamente: un contexto fabricado o de otro manifiesto, índice, modo, alcance o decisión no sirve."""
    if not isinstance(contexto, dict) or not isinstance(contexto.get("entradas"), dict) or contexto.get("tarea") not in TAREAS:
        return ["CONTEXTO_AUSENTE_O_MAL_FORMADO"]
    ent = contexto["entradas"]
    ok, p = puerta(R, me_raw, me, contexto.get("modo"), ent.get("alcance"), ent.get("decision"), contexto["tarea"])
    if not ok:
        return ["CONTEXTO_NO_AUTENTICO:%s" % p.get("motivo")]
    return [] if canon(p) == canon(contexto) else ["CONTEXTO_NO_AUTENTICO:DISTINTO_DE_SU_PUERTA"]


def cotejar_procedencia(res, contexto):
    """Origen declarado por el materializador en su resumen frente al contexto autenticado de la invocación que verifica."""
    pu = res.get("puerta")
    if not isinstance(pu, dict):
        return ["PROCEDENCIA_AUSENTE:puerta"]
    fallos = ["PROCEDENCIA_AUSENTE:puerta.%s" % k for k in COMPARTIDOS + ("tarea",) if k not in pu]
    fallos += ["PROCEDENCIA_AUSENTE:%s" % k for k in DUPLICADOS_DEL_RESUMEN + DERIVADOS_DEL_MODO if k not in res]
    if fallos:
        return fallos
    fallos += ["PROCEDENCIA_CONTRADICTORIA:%s" % k for k in DUPLICADOS_DEL_RESUMEN if canon(res[k]) != canon(pu[k])]
    if pu["tarea"] != "LAMBDA-T8-MATERIALIZAR":
        fallos.append("PROCEDENCIA_DE_OTRA_OPERACION:%s" % pu["tarea"])
    fallos += ["PROCEDENCIA_DISTINTA_DEL_CONTEXTO:%s" % k for k in COMPARTIDOS if canon(pu[k]) != canon(contexto[k])]
    if res["kind"] != KIND_PRODUCTO[contexto["modo"]]:
        fallos.append("PROCEDENCIA_KIND_NO_CORRESPONDE_AL_MODO:%s" % res["kind"])
    if res["productivo"] is not (contexto["modo"] == "produccion"):
        fallos.append("PROCEDENCIA_PRODUCTIVO_NO_CORRESPONDE_AL_MODO")
    return fallos


def _modulo(nombre, ruta, sha_esperado):
    b = Path(ruta).read_bytes()
    if H(b) != sha_esperado:
        raise RuntimeError("PIEZA_NO_AUTENTICA:%s" % nombre)
    sp = importlib.util.spec_from_loader(nombre, loader=None, origin=str(ruta))
    m = importlib.util.module_from_spec(sp)
    m.__file__ = str(ruta)
    sys.modules[nombre] = m
    exec(compile(b, str(ruta), "exec"), m.__dict__)
    return m


def cargar(R, me):
    """Entrada y finalizador SOLO por ruta + sha256 del manifiesto de emisión (los mismos bytes autenticados se ejecutan)."""
    R = Path(R)
    fin = me["finalizador"]
    for p in fin.get("sys_path", []):
        if str(R / p) not in sys.path:
            sys.path.insert(0, str(R / p))
    UN = _modulo("unidades_finalizador_emision", R / fin["ruta"], fin["sha256"])
    EM = _modulo("entrada_lambda_emision", R / me["entrada"]["ruta"], me["entrada"]["sha256"])
    if getattr(EM, "MANIFIESTO_SHA256", None) != me["manifiesto_fuentes"]["sha256"]:
        raise RuntimeError("MANIFIESTO_DE_FUENTES_DISTINTO")
    return EM.EntradaLambda(R), UN._finalize


def clave_fila(a):
    return H(canon({"ref": a["ref"], "fila_en_unidad": a["fila_en_unidad"], "inversion_id": a["inversion_id"], "cell_id": a["cell_id"]}))


def construir_producto(E, finalizar, me):
    v = E.vista(finalizar)
    filas = []
    for x in sorted(v, key=lambda r: r["fila"]):
        a = E.anexo[x["fila"]]
        f = {"clave_fila": clave_fila(a), "fila_anexo": x["fila"], "run_id": x["run_id"], "cell_id": a["cell_id"], "inversion_id": a["inversion_id"],
             "tipo": x["tipo"], "estado_historico": a["result_status"], "historico": a}
        if x["tipo"] == "lambda_candidato_por_demostracion":
            fin = a["fin_por_unidad"]
            k = fin["set"] + "|" + fin["country"]
            env = E.eq["por_clave"][k]["envolvente"]
            f.update(clasificacion_derivada=x["estado"], finalizada=True, cambio=x["cambio"],
                     procedencia={"soporte_sha256": x["soporte"], "clave": k, "intervalo": [env["lambda_min"], env["lambda_max"]], "regla": x["regla"],
                                  "manifiesto_fuentes": me["manifiesto_fuentes"]["sha256"], "entrada": me["entrada"]["sha256"],
                                  "finalizador": me["finalizador"]["sha256"], "derivacion": "soporte λ derivado por demostración (equivalencia aceptada)"})
        elif x["tipo"] == "captura_pendiente_sin_soporte_C2":
            f.update(finalizada=False, estado_sucesor="pendiente_soporte_global", causa_pendiente="SIN_SOPORTE_GLOBAL_C2")
        else:
            f.update(finalizada=None, estado_sucesor=a["result_status"], preservada=True)
        filas.append(f)
    return filas


def resumen_de(filas, me):
    lam = [f for f in filas if f["tipo"] == "lambda_candidato_por_demostracion"]
    return {"filas": len(filas), "definitivas_preservadas": sum(f["tipo"] == "definitivo_almacenado" for f in filas),
            "captura_pendiente": sum(f["tipo"] == "captura_pendiente_sin_soporte_C2" for f in filas), "lambda_finalizadas": len(lam),
            "lambda_outside_support": sum(f["clasificacion_derivada"] == "outside_support" for f in lam),
            "lambda_computed": sum(f["clasificacion_derivada"] == "computed" for f in lam), "cambios": sum(f["cambio"] for f in lam),
            "corridas": sorted({f["run_id"] for f in filas}), "plan_sha256": me["plan_sha256"]}


def verificar(R, me_raw, prod_dir, contexto, E=None, finalizar=None):
    """ÚNICA validación del producto: contenido Y procedencia. Lee UNA vez los bytes del manifiesto (me_raw) y del producto, los autentica
    (contexto re-autenticado; sello del materializador) y analiza esos mismos bytes; el origen del resumen se coteja con el contexto."""
    me = json.loads(me_raw)
    fallos = contexto_autentico(R, me_raw, me, contexto)
    if fallos:
        return False, fallos, None
    prod_dir = Path(prod_dir)
    try:
        raw = (prod_dir / PRODUCTO).read_bytes()
        sello = (prod_dir / SELLO).read_text(encoding="utf-8").split()[0]
        res = json.loads((prod_dir / RESUMEN).read_bytes())
    except (OSError, ValueError, IndexError) as ex:
        return False, ["PRODUCTO_ILEGIBLE:%s" % type(ex).__name__], None
    if not isinstance(res, dict):
        return False, ["RESUMEN_MAL_FORMADO"], None
    if H(raw) != sello or res.get("producto_sha256") != sello:
        fallos.append("PRODUCTO_NO_COINCIDE_CON_SU_SELLO")
    fallos += cotejar_procedencia(res, contexto)
    try:
        filas = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    except ValueError:
        return False, fallos + ["PRODUCTO_MAL_FORMADO"], None
    if E is None:
        E, finalizar = cargar(R, me)
    esperado = construir_producto(E, finalizar, me)
    if len(filas) != len(E.anexo):
        fallos.append("UNIVERSO_DISTINTO:%d!=%d" % (len(filas), len(E.anexo)))
    claves = [f.get("clave_fila") for f in filas]
    if len(set(claves)) != len(claves):
        fallos.append("CLAVES_DUPLICADAS")
    ref = {f["clave_fila"]: f for f in esperado}
    if set(claves) != set(ref):
        fallos.append("CLAVES_FALTANTES_O_AJENAS:%d" % len(set(ref) ^ set(claves)))
    por = {}
    for f in filas:
        por.setdefault(f.get("clave_fila"), f)
    distintas = [c for c, f in ref.items() if c in por and canon(f) != canon(por[c])]
    if distintas:
        fallos.append("FILAS_DISTINTAS_DE_LA_RUTA_ACEPTADA:%d" % len(distintas))
    rs = resumen_de(filas, me)
    for k_, v_ in (me.get("esperado") or {}).items():
        if rs.get(k_) != v_:
            fallos.append("RECUENTO_%s:%s!=%s" % (k_, rs.get(k_), v_))
    if rs["corridas"] != sorted(me["corridas"]):
        fallos.append("CORRIDAS_DISTINTAS")
    if res.get("resumen") != rs:
        fallos.append("RESUMEN_NO_COINCIDE")
    return not fallos, fallos, {"resumen": rs, "producto_sha256": H(raw), "filas_distintas": len(distintas),
                                "procedencia": {"cotejados": list(COMPARTIDOS + DERIVADOS_DEL_MODO + DUPLICADOS_DEL_RESUMEN),
                                                "contexto": {k: contexto[k] for k in COMPARTIDOS}}}
