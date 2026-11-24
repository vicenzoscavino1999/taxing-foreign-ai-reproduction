"""TRABAJADOR REAL de UNA tarea R2 o R3 del plan (candidato S6; NO OFICIAL), lanzado por el EjecutorSupervisado dentro de un cupo.
rem41/rem42: (a) contrasta ANTES de usar sus archivos las identidades efectivas que admitió el coordinador (--despliegue-sha256,
--fuentes-sha256); (b) construye contexto S6 y Referencia UNA sola vez (la identidad es inmutable dentro del proceso: el despliegue
verificado por sus bytes y el contexto autenticado por ContextoS6) y los reutiliza en selección, cálculo y validación; (c) R3 por lista.
  R2: lista (corrida_paso4.lista_tarea) -> vínculo (vinculo_paso4) -> selección SEL-PASO4-REPRO-v1 con el Verificador del MISMO contexto
      (misma lógica que seleccion_paso4.seleccionar) -> [CÁLCULO] seleccion_paso4.Ejecutor -> registro productivo (validación del paquete
      con el validador instalado) + ensamblaje por unidad -> manifiesto.
  R3: lista -> vínculo (definiciones S2/S3) -> productor_r3.previas de TODAS las unidades (ω exacto; sin cálculo) -> [CÁLCULO]
      productor_r3.celda por unidad (contrato v3) -> documento y filas por unidad -> VALIDACIÓN PRODUCTIVA (rem42): validador_r3.
      ValidadorR3S6 (comprobaciones históricas de los lotes R3, lima1533 871b1d7f…, con el MISMO contexto S6 del productor) sobre los
      bytes finales, por registro_productivo.generar_r3. El validador se construye ANTES de las previas: si falta una dependencia
      (histórico distinto del fijado, regla_b_v2/e12_celda, contexto) la tarea se RECHAZA antes del cálculo (VALIDADOR_R3_NO_DISPONIBLE).
  --hasta-seleccion: se detiene ANTES del cálculo (R2: tras la selección; R3: tras validador y previas). Sin productos.
  python -B herramientas/b/tarea_paso4.py --despliegue <d.json> --despliegue-sha256 <h> --plan <plan.json> --tarea <id> --fuentes <f.json>
         --fuentes-sha256 <h> --salida <dir> --resultado <r.json> [--almacen-techos <dir>] [--hasta-seleccion]"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(INSTALACION / "herramientas/b"))


def _carga(nombre, rel):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, INSTALACION / rel)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    o = {k: a[a.index(k) + 1] for k in ("--despliegue", "--despliegue-sha256", "--plan", "--tarea", "--fuentes", "--fuentes-sha256", "--salida", "--resultado",
                                        "--almacen-techos") if k in a}
    hasta_sel = "--hasta-seleccion" in a
    t0 = time.time()
    res_p, sal = Path(o["--resultado"]), Path(o["--salida"])

    def fin(**x):
        x["segundos"] = round(time.time() - t0, 1)
        res_p.write_text(json.dumps(x, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        return 0

    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
    for k, kh in (("--despliegue", "--despliegue-sha256"), ("--fuentes", "--fuentes-sha256")):     # (a) identidades efectivas admitidas
        if not o.get(kh) or sha(o[k]) != o[kh]:
            return fin(estado="rechazada", motivo="IDENTIDAD_EFECTIVA_DISTINTA_DE_LA_ADMITIDA: %s" % k)
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    VP = _carga("vinculo_paso4", "herramientas/b/vinculo_paso4.py")
    SP = _carga("seleccion_paso4", "herramientas/b/seleccion_paso4.py")
    RP = _carga("registro_productivo", "herramientas/b/registro_productivo.py")
    plan = CO.verificar_plan(json.loads(Path(o["--plan"]).read_bytes()))
    t = {x["id"]: x for x in plan["tareas"]}.get(o["--tarea"])
    if t is None:
        return fin(estado="rechazada", motivo="TAREA_FUERA_DEL_PLAN")
    fu = json.loads(Path(o["--fuentes"]).read_bytes())
    lista = CO.lista_tarea(plan, t["id"], fu.get("fuentes", fu))
    lp = res_p.with_suffix(".lista.json")
    lp.write_bytes(CO.canon(lista))
    d = SP.configurar(o["--despliegue"])
    try:
        _, vin = VP.Vinculo(d["raiz_fuentes"]).lista_valida(lista)
    except VP.VinculoError as ex:
        return fin(estado="rechazada", motivo="VINCULO: %s" % ex.codigo, detalle=ex.detalle)
    a0 = time.time()
    ctx = SP.contexto()                                                   # (b) UNA sola construcción por proceso
    ref = SP.referencia(ctx)
    V = SP.verificador(ctx, ref)
    t_ctx = round(time.time() - a0, 1)
    pdir = sal / "paquete"
    if t["fase"] == "R3":
        PR = _carga("productor_r3", "herramientas/b/productor_r3.py")
        try:                                                              # rem42: validador productivo R3 ANTES del cálculo
            VR3 = _carga("validador_r3", "herramientas/b/validador_r3.py")
            VR = VR3.ValidadorR3S6(ctx, ref, SP, d["raiz_proyecto"])
        except Exception as ex:  # noqa: BLE001
            return fin(estado="rechazada", motivo="VALIDADOR_R3_NO_DISPONIBLE: %s: %s" % (type(ex).__name__, str(ex)[:300]), contexto_s=t_ctx)
        alm = SP.almacen_techos(o["--almacen-techos"]) if "--almacen-techos" in o else None
        prod = PR.ProductorR3(ctx, ref, SP.GC, d["raiz_proyecto"], almacen=None)
        pre = {}
        for u in t["unidades"]:
            ok, pr, _ = prod.previas(vin[u]["definicion"])
            pre[u] = dict(pr, ok=bool(ok))
        if not all(x["ok"] for x in pre.values()):
            return fin(estado="rechazada", motivo="PREVIAS_R3_FALLAN", previas=pre, contexto_s=t_ctx)
        if hasta_sel:
            return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CALCULO (R3: validador R3 construido y previas del productor S2/S3; sin productos)",
                       previas=pre, contexto_s=t_ctx, validador_r3=VR3.identidad())
        if alm is not None:                                               # el almacén de techos de la corrida solo para calcular
            prod.store = alm({"autoridad": ctx.identity, "uso": "R3 por lista", "run_class": ctx.identity["run_class"]})
        (sal / "unidades").mkdir(parents=True, exist_ok=True)
        productos = {}
        for u in t["unidades"]:                                           # CÁLCULO CIENTÍFICO (solo con autorización)
            res, filas, _ = prod.celda(vin[u]["definicion"])
            n = u.replace(":", "_")
            final = {"ok": "completo", "no_aplicable": "no_aplicable"}.get(res.get("estado"), "rechazado")
            fb = CO.canon(filas or {}) + b"\n"
            (sal / "unidades" / (n + "_filas.json")).write_bytes(fb)
            doc = {"id": u, "familia": vin[u]["definicion"]["familia"], "ruta": vin[u]["definicion"].get("ruta"), "estrato": vin[u]["definicion"].get("estrato"),
                   "estado_final": final, "estado_generador": res.get("estado"), "resultado": res, "contrato_exportado": "v3",
                   "filas": {"archivo": n + "_filas.json", "sha256": hashlib.sha256(fb).hexdigest(), "tablas": {k: len(v) for k, v in (filas or {}).items() if isinstance(v, list)}},
                   "identidad_productor_sha256": getattr(ctx, "identity_sha256", None), "run_class": ctx.identity["run_class"]}
            (sal / "unidades" / (n + ".json")).write_bytes(CO.canon(doc) + b"\n")
            productos[u] = {"documento": "unidades/%s.json" % n, "filas": "unidades/%s_filas.json" % n}
        reg = RP.generar_r3(VR, sal, productos, {u: vin[u]["definicion"] for u in t["unidades"]}, salida=sal / CO.REGISTRO, dictamen=sal / CO.DICTAMEN)
        ok = reg["verificacion"].get("cumple") is True and all(e["estado"] in ("completa_validada", "no_aplicable_validada") for e in reg["unidades"].values())
        return fin(estado="completa" if ok else "rechazada", productos=productos, motivo=None if ok else reg["verificacion"].get("codigos"), contexto_s=t_ctx)
    # ---- R2: selección con el Verificador del MISMO contexto (misma lógica que seleccion_paso4.seleccionar, sin reconstruir contexto)
    raw = lp.read_bytes()
    sel = V.seleccion_esperada(raw, SP.P2.REGLA_REPRO)
    sel["sello_sha256"] = SP.sha(SP.canon({k: v for k, v in sel.items() if k != "sello_sha256"}))
    pdir.mkdir(parents=True, exist_ok=False)
    SP.escribir_atomico(pdir / "seleccion.json", SP.canon(sel))
    (pdir / "entrada").mkdir()
    (pdir / "entrada/global_extreme_v3.json").write_bytes(raw)
    SP.escribir_atomico(pdir / "plan.json", SP.canon(SP.planificar(sel)))
    if hasta_sel:
        return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CALCULO (prueba de conexión; sin productos)", contexto_s=t_ctx,
                   seleccion_sha256=sha(pdir / "seleccion.json"), plan_paquete_sha256=sha(pdir / "plan.json"))
    alm = SP.almacen_techos(o["--almacen-techos"]) if "--almacen-techos" in o else None
    SP.Ejecutor(pdir, ctx, ref, V=V, almacen_techos=alm).ejecutar(reanudar=False)          # CÁLCULO CIENTÍFICO (solo con autorización)
    reg = RP.generar(V, pdir, sal, salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json")
    prod = {u: {"documento": e["documento"], "filas": e["filas"]} for u, e in reg["unidades"].items()}
    ok = reg["verificacion"].get("cumple") is True and all(e["estado"] in ("completa_validada", "no_aplicable_validada") for e in reg["unidades"].values())
    return fin(estado="completa" if ok else "rechazada", productos=prod, motivo=None if ok else reg["verificacion"].get("codigos"), contexto_s=t_ctx)


if __name__ == "__main__":
    raise SystemExit(main())
