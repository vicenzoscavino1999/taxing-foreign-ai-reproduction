"""rem137 — CONEXIÓN DE CAPTURA POR FILA de T8 (P4-T8-CAPTURA-CONEXION; candidato aislado, NO habilitado; ninguna emisión ni alcance de captura).
Mismo patrón que el núcleo de emisión λ aceptado (rem136 validar_emision_lambda 75ab…: puerta → contexto autenticado → cargar por ruta + sha256
del manifiesto → construir → única verificar con procedencia), aplicado a una VISTA de captura sobre el producto λ:
  puerta(...)             — antes de leer fuentes o escribir: produccion exige manifiesto real + alcance v3 CAPTURA_T8_POR_FILA verificado por C0
                            (verificar_documento) y ligado a ESTE manifiesto, índice, código, instalación, límites y plan + decisión humana nativa
                            (decision_humana de C0); candidata: manifiesto real sin alcance (vista CANDIDATA, nunca productiva); ensayo:
                            manifiesto -ENSAYO sin alcance (vista ENSAYO).
  cargar(...)             — certificación por fila (candidato_v3/certificacion_fila.py), finalizador instalado (_finalize de unidades.py,
                            a8aded1d…), base λ y pruebas: SOLO por ruta + sha256 del manifiesto; la base λ, además, contra su inventario sellado.
  construir_vista(...)    — 13.656 filas: las no-captura se copian SIN cambios de la base λ; cada fila de captura conserva todos sus campos y
                            añade «captura_c2» (clasificación derivada, marca de finalización candidata, prueba, adaptador y procedencia).
                            La clasificación sale de la ÚNICA validación certificacion_fila.validar (vía construir) y se reproduce con
                            _finalize SIN alterar su regla mediante el ADAPTADOR (equivalencia explícita en adaptar()).
  verificar(...)          — ÚNICA validación de la vista (la usan el verificador de la receta y las pruebas): contexto re-autenticado, sello,
                            procedencia, recomputación desde los mismos bytes, universo, claves, duplicados/faltantes/ajenas, preservación de
                            las no-captura y de los campos de captura de la base, recuentos y corridas.
cerrar queda interno: ninguna función acepta filas, callbacks ni hashes del llamador; una fila sin prueba válida queda pendiente (nunca NA)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
PIEZAS = ("conexion_captura.py", "certificacion_fila.py", "FUENTES_CAPTURA.json", "materializar_captura.py", "verificar_captura.py",
          "admision_integracion.py", "receta_captura.sh")
TAREAS = ("CAPTURA-T8-MATERIALIZAR", "CAPTURA-T8-VERIFICAR")
OPERACION = "CAPTURA_T8_POR_FILA"
LIMITES = {"procesos": 3, "tope_s": 2400.0, "suite_s": 3600.0, "union_s": 10800.0}
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
PRODUCTO, RESUMEN, SELLO = "VISTA_T8_CAPTURA.jsonl", "VISTA_RESUMEN.json", "VISTA.sha256"
KIND_PRODUCTO = {"produccion": "vista-t8-captura-PRODUCCION", "candidata": "vista-t8-captura-CANDIDATA", "ensayo": "vista-t8-captura-ENSAYO"}
COMPARTIDOS = ("modo", "manifiesto_captura_sha256", "indice_sha256", "alcance_sha256", "decision")
DERIVADOS_DEL_MODO = ("kind", "productivo")
POR_OPERACION = ("tarea", "entradas")
DUPLICADOS_DEL_RESUMEN = ("modo", "manifiesto_captura_sha256")
TIPO_CAPTURA = "captura_pendiente_sin_soporte_C2"
REGLAS = {"pertenencia_misma_corrida": "C2_inf + err_inf <= v <= C2_sup - err_sup  =>  computed (testigos de la misma corrida)",
          "pertenencia_transferida": "C2_inf + err_inf <= v <= C2_sup - err_sup  =>  computed (testigos de corrida equivalente)",
          "exclusion_cota_33_10": "Fraction(v) > 33/10 + banda  =>  outside_support (nota rem135)"}
SEMANTICA = {"pertenencia_misma_corrida": "encierro_interior_certificado", "pertenencia_transferida": "encierro_interior_certificado",
             "exclusion_cota_33_10": "encierro_exterior_por_cota_33_10", "exclusion_cota_U": "encierro_exterior_por_cota_U"}


class Rechazo(Exception):
    pass


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def autenticar_paquete():
    p = AQUI / "PAQUETE_CAPTURA_C2_v3.json"
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
        return False, {"motivo": "MANIFIESTO_DE_ENSAYO_EN_%s" % str(modo).upper()}
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
                        (al.get("lote_manifiesto_sha256") == ent.get("manifiesto_captura") == H(me_raw), "ALCANCE_DE_OTRO_MANIFIESTO"),
                        (ent.get("paquete_captura") == idx_sha and ent.get("codigo_captura") == codigo, "ALCANCE_DE_OTRO_CODIGO"),
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
    """Puerta de cada invocación; si admite, devuelve el CONTEXTO AUTENTICADO (COMPARTIDOS + POR_OPERACION) de esa invocación."""
    ok, p = _puerta_invocacion(R, me_raw, me, modo, alcance, decision, tarea)
    if not ok:
        return ok, p
    return True, {"modo": modo, "manifiesto_captura_sha256": H(me_raw), "indice_sha256": p["indice_sha256"], "alcance_sha256": p.get("alcance_sha256"),
                  "decision": p.get("decision"), "tarea": tarea,
                  "entradas": {"alcance": str(alcance) if alcance else None, "decision": str(decision) if decision else None}}


def contexto_autentico(R, me_raw, me, contexto):
    if not isinstance(contexto, dict) or not isinstance(contexto.get("entradas"), dict) or contexto.get("tarea") not in TAREAS:
        return ["CONTEXTO_AUSENTE_O_MAL_FORMADO"]
    ent = contexto["entradas"]
    ok, p = puerta(R, me_raw, me, contexto.get("modo"), ent.get("alcance"), ent.get("decision"), contexto["tarea"])
    if not ok:
        return ["CONTEXTO_NO_AUTENTICO:%s" % p.get("motivo")]
    return [] if canon(p) == canon(contexto) else ["CONTEXTO_NO_AUTENTICO:DISTINTO_DE_SU_PUERTA"]


def cotejar_procedencia(res, contexto):
    pu = res.get("puerta")
    if not isinstance(pu, dict):
        return ["PROCEDENCIA_AUSENTE:puerta"]
    fallos = ["PROCEDENCIA_AUSENTE:puerta.%s" % k for k in COMPARTIDOS + ("tarea",) if k not in pu]
    fallos += ["PROCEDENCIA_AUSENTE:%s" % k for k in DUPLICADOS_DEL_RESUMEN + DERIVADOS_DEL_MODO if k not in res]
    if fallos:
        return fallos
    fallos += ["PROCEDENCIA_CONTRADICTORIA:%s" % k for k in DUPLICADOS_DEL_RESUMEN if canon(res[k]) != canon(pu[k])]
    if pu["tarea"] != "CAPTURA-T8-MATERIALIZAR":
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
        raise Rechazo("PIEZA_NO_AUTENTICA:%s" % nombre)
    sp = importlib.util.spec_from_loader(nombre, loader=None, origin=str(ruta))
    m = importlib.util.module_from_spec(sp)
    m.__file__ = str(ruta)
    sys.modules[nombre] = m
    exec(compile(b, str(ruta), "exec"), m.__dict__)
    return m


def _bytes_inventariados(R, x):
    """Bytes de una fuente sellada: inventario fijado → archivo listado → sha256 fijado (los mismos bytes se usan)."""
    R = Path(R)
    ib = (R / x["inventario"]["ruta"]).read_bytes()
    if H(ib) != x["inventario"]["sha256"]:
        raise Rechazo("INVENTARIO_NO_AUTENTICO:%s" % x["inventario"]["ruta"])
    b = (R / "tmp" / x["area"] / x["rel"]).read_bytes()
    if H(b) != x["sha256"] or json.loads(ib)["files"].get(x["rel"], {}).get("sha256") != x["sha256"]:
        raise Rechazo("FUENTE_NO_AUTENTICA:%s" % x["rel"])
    return b


def cargar(R, me):
    """Certificación, finalizador, base λ y pruebas SOLO por ruta + sha256 del manifiesto (los mismos bytes autenticados se usan)."""
    R = Path(R)
    fin = me["finalizador"]
    for p in fin.get("sys_path", []):
        if str(R / p) not in sys.path:
            sys.path.insert(0, str(R / p))
    UN = _modulo("unidades_finalizador_captura", R / fin["ruta"], fin["sha256"])
    CF = _modulo("certificacion_fila_v3_captura", AQUI / me["certificacion"]["rel"], me["certificacion"]["sha256"])
    if CF.FUENTES_SHA256 != me["fuentes_sha256"] or HF(AQUI / "FUENTES_CAPTURA.json") != me["fuentes_sha256"]:
        raise Rechazo("FUENTES_DISTINTAS_DEL_MANIFIESTO")
    ctx = CF.Contexto(R)
    base_raw = _bytes_inventariados(R, me["base_lambda"])
    pb = (AQUI / me["pruebas"]["rel"]).read_bytes()
    if H(pb) != me["pruebas"]["sha256"]:
        raise Rechazo("PRUEBAS_NO_AUTENTICAS")
    return {"CF": CF, "ctx": ctx, "finalizar": UN._finalize, "base_raw": base_raw, "pruebas_raw": pb}


def adaptar(CF, ctx, c, prueba, f, finalizar, me):
    """ADAPTADOR al finalizador instalado, sin alterar su regla ni inventar extremos del soporte. _finalize(row, fin, lam, c2) declara
    outside_support si NO (c2[0] <= v <= c2[1]) para fin.k != lambda con c2_defined. Equivalencia (solo con prueba válida por validar):
      pertenencia: c2 = [C2_inf + err_inf, C2_sup - err_sup] es un ENCIERRO INTERIOR certificado del soporte S (⊆ S); v ∈ c2 ⇒ v ∈ S, y
                   _finalize(v, c2) = _finalize(v, S) = computed;
      exclusión:   c2 = (-inf, cota + banda] es un ENCIERRO EXTERIOR (S ⊆ c2 por la nota); v > cota + banda ⇒ v ∉ S, y
                   _finalize(v, c2) = _finalize(v, S) = outside_support.
    Fuera de esas condiciones el adaptador no se usa (la fila queda pendiente). Si su salida difiriera de validar, es un rechazo."""
    if c["estado_candidato"] == "pendiente":
        return {"estado_candidato": "pendiente", "clasificacion_derivada": None, "finalizacion_candidata": False, "causa_pendiente": c["causa_pendiente"],
                "tipo_prueba": c["tipo_prueba"], "prueba_sha256": c["prueba_sha256"], "cambio": False, "adaptador": None}
    t = prueba["tipo"]
    fin = f["historico"]["fin_por_unidad"]
    if t in ("pertenencia_misma_corrida", "pertenencia_transferida"):
        wi, ws = prueba["testigo_inferior"], prueba["testigo_superior"]
        lo = Fraction(wi["C_2"]) + Fraction(wi["numerical_error"])
        hi = Fraction(ws["C_2"]) - Fraction(ws["numerical_error"])
    elif t == "exclusion_cota_33_10":
        lo, hi = float("-inf"), CF.COTA + ctx.banda
    else:
        lo, hi = float("-inf"), CF.U + ctx.banda
    fila = {}
    finalizar(fila, fin, {}, (lo, hi))
    if fila.get("result_status") != c["estado_candidato"]:
        raise Rechazo("ADAPTADOR_DISCREPA_DE_VALIDAR:%s" % c["fila"])
    return {"estado_candidato": c["estado_candidato"], "clasificacion_derivada": c["estado_candidato"], "finalizacion_candidata": True,
            "causa_pendiente": None, "tipo_prueba": t, "prueba_sha256": c["prueba_sha256"], "cambio": c["estado_candidato"] != f["estado_historico"],
            "adaptador": {"finalizador_sha256": me["finalizador"]["sha256"], "c2": [str(lo), str(hi)], "semantica": SEMANTICA[t], "salida": fila,
                          "regla": CF.REGLA_U if t == "exclusion_cota_U" else REGLAS[t]}}


def construir_vista(carga, me):
    CF, ctx = carga["CF"], carga["ctx"]
    base = [json.loads(x) for x in carga["base_raw"].decode("utf-8").splitlines() if x.strip()]
    pruebas = json.loads(carga["pruebas_raw"])
    cand = CF.construir(ctx, pruebas)                         # ÚNICA validación por fila (validar), una prueba como máximo por fila
    por_clave = {c["clave_fila"]: c for c in cand}
    por_fila = {p["fila"]: p for p in pruebas}
    cap = [f for f in base if f.get("tipo") == TIPO_CAPTURA]
    if sorted(f["fila_anexo"] for f in cap) != sorted(ctx.captura) or len(cap) != len(por_clave):
        raise Rechazo("BASE_INCOHERENTE_CON_EL_UNIVERSO_DE_CAPTURA")
    proc = {"base_lambda_sha256": H(carga["base_raw"]), "pruebas_sha256": H(carga["pruebas_raw"]), "fuentes_sha256": CF.FUENTES_SHA256,
            "certificacion_sha256": me["certificacion"]["sha256"], "plan_sha256": me["plan_sha256"]}
    filas = []
    for f in base:
        if f.get("tipo") != TIPO_CAPTURA:
            filas.append(f)
            continue
        c = por_clave.get(f["clave_fila"])
        if c is None or c["fila"] != f["fila_anexo"] or canon(f["historico"]) != canon(ctx.anexo[c["fila"]]) or c["run_id"] != f["run_id"]:
            raise Rechazo("FILA_DE_CAPTURA_INCOHERENTE:%s" % f.get("fila_anexo"))
        g = dict(f)
        g["captura_c2"] = dict(adaptar(CF, ctx, c, por_fila.get(c["fila"]), f, carga["finalizar"], me), procedencia=proc)
        filas.append(g)
    return filas


def resumen_de(filas, me):
    cap = [f["captura_c2"] for f in filas if f.get("tipo") == TIPO_CAPTURA]
    return {"filas": len(filas), "definitivas_preservadas": sum(f.get("tipo") == "definitivo_almacenado" for f in filas),
            "lambda_finalizadas": sum(f.get("tipo") == "lambda_candidato_por_demostracion" for f in filas), "captura_filas": len(cap),
            "captura_computed": sum(c["estado_candidato"] == "computed" for c in cap),
            "captura_outside_support": sum(c["estado_candidato"] == "outside_support" for c in cap),
            "captura_pendiente": sum(c["estado_candidato"] == "pendiente" for c in cap),
            "captura_por_tipo": dict(sorted(Counter(c["tipo_prueba"] for c in cap if c["finalizacion_candidata"]).items())),
            "captura_pendientes_por_causa": dict(sorted(Counter(c["causa_pendiente"] for c in cap if c["causa_pendiente"]).items())),
            "captura_cambios": sum(bool(c["cambio"]) for c in cap), "corridas": sorted({f["run_id"] for f in filas}), "plan_sha256": me["plan_sha256"]}


def verificar(R, me_raw, prod_dir, contexto, carga=None):
    """ÚNICA validación de la vista: contenido Y procedencia, sobre los bytes leídos una vez (manifiesto, vista, base, pruebas)."""
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
        return False, ["VISTA_ILEGIBLE:%s" % type(ex).__name__], None
    if not isinstance(res, dict):
        return False, ["RESUMEN_MAL_FORMADO"], None
    if H(raw) != sello or res.get("producto_sha256") != sello:
        fallos.append("VISTA_NO_COINCIDE_CON_SU_SELLO")
    fallos += cotejar_procedencia(res, contexto)
    try:
        filas = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    except ValueError:
        return False, fallos + ["VISTA_MAL_FORMADA"], None
    try:
        if carga is None:
            carga = cargar(R, me)
        esperado = construir_vista(carga, me)
    except Exception as ex:  # noqa: BLE001 — una fuente o prueba no auténtica nunca es conformidad
        return False, fallos + ["RECALCULO_RECHAZADO:%s" % (str(ex) or type(ex).__name__)[:200]], None
    base = [json.loads(x) for x in carga["base_raw"].decode("utf-8").splitlines() if x.strip()]
    if len(filas) != len(esperado):
        fallos.append("UNIVERSO_DISTINTO:%d!=%d" % (len(filas), len(esperado)))
    claves = [f.get("clave_fila") for f in filas]
    if len(set(claves)) != len(claves):
        fallos.append("CLAVES_DUPLICADAS")
    ref = {f["clave_fila"]: f for f in esperado}
    if set(claves) != set(ref):
        fallos.append("CLAVES_FALTANTES_O_AJENAS:%d" % len(set(ref) ^ set(claves)))
    por = {}
    for f in filas:
        por.setdefault(f.get("clave_fila"), f)
    distintas = [k for k, f in ref.items() if k in por and canon(f) != canon(por[k])]
    if distintas:
        fallos.append("FILAS_DISTINTAS_DEL_RECALCULO:%d" % len(distintas))
    bpor = {f["clave_fila"]: f for f in base}
    reescritas = [k for k, f in por.items() if k in bpor and canon({x: y for x, y in f.items() if x != "captura_c2"}) != canon(bpor[k])]
    no_cap_con_c2 = [k for k, f in por.items() if f.get("tipo") != TIPO_CAPTURA and "captura_c2" in f]
    if reescritas or no_cap_con_c2:
        fallos.append("BASE_REESCRITA:%d" % (len(reescritas) + len(no_cap_con_c2)))
    promo = [k for k, f in por.items() if f.get("tipo") == TIPO_CAPTURA and (f.get("captura_c2") or {}).get("estado_candidato") != "pendiente"
             and (ref.get(k, {}).get("captura_c2") or {}).get("estado_candidato") == "pendiente"]
    if promo:
        fallos.append("PROMOCION_INDEBIDA:%d" % len(promo))
    try:
        rs_vista = resumen_de(filas, me)
    except (KeyError, TypeError, AttributeError):
        rs_vista = None
        fallos.append("VISTA_SIN_CAMPOS_REQUERIDOS")
    rs = rs_vista if rs_vista is not None else resumen_de(esperado, me)
    for k_, v_ in (me.get("esperado") or {}).items():
        if rs.get(k_) != v_:
            fallos.append("RECUENTO_%s:%s!=%s" % (k_, rs.get(k_), v_))
    if rs["corridas"] != sorted(me["corridas"]):
        fallos.append("CORRIDAS_DISTINTAS")
    if res.get("resumen") != rs_vista:
        fallos.append("RESUMEN_NO_COINCIDE")
    return not fallos, fallos, {"resumen": rs, "producto_sha256": H(raw), "filas_distintas": len(distintas), "base_lambda_sha256": H(carga["base_raw"]),
                                "procedencia": {"cotejados": list(COMPARTIDOS + DERIVADOS_DEL_MODO + DUPLICADOS_DEL_RESUMEN),
                                                "contexto": {k: contexto[k] for k in COMPARTIDOS}}}
