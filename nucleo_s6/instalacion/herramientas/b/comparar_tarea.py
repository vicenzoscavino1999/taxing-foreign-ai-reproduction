"""COMPARACIÓN de UNA tarea ACEPTADA de la corrida con sus originales (candidato S6; NO OFICIAL). Distinta de la VALIDACIÓN del paquete:
  - validación (registro_productivo, en la ruta de la tarea): el validador instalado sobre los bytes finales; da el registro y el dictamen
    de validación que forman parte del árbol ACEPTADO;
  - comparación (este módulo, después): cada unidad nueva frente a SU original por la autoridad histórica (comparar_reproduccion), con la
    validación común de ambos lados y el registro productivo ligado a los bytes nuevos.
Entradas: plan sellado, raíz de la corrida, tarea, despliegue S6 (el MISMO de la corrida: se exige su sha256 = el de corrida.json),
reglas propuestas selladas (opcional; DR-1/DR-2 solo con su sha256 y solo si su activación fue aprobada — en el arnés, fixtures).
Requisitos: la tarea tiene UNA aceptación en el diario y su árbol sigue byte a byte (si no: rechazo, no se compara).
Productos: <raíz>/comparaciones/<tarea>/ (FUERA del árbol aceptado): audit/entrega.json (inventario de los bytes aceptados que se
comparan, con rutas relativas a esta carpeta), correspondencia.json y dictamen.json; el diario de la corrida registra op «comparacion»
con los sha256. Una tarea ya comparada con la misma correspondencia no se recompara: se DEVUELVE el dictamen guardado (estado,
conteos, error) con el mismo código de salida (rem42); un dictamen guardado alterado o eliminado se retira (evidencia) y se recompara.
R1 (rem49): solo tareas con OPCIÓN activa por la autorización reconstruida (opciones_p1.comparar_r1: B3 por unidad; par A3 en su tarea L); exige --fuentes.
Reglas propuestas (rem46): solo desde un archivo «reglas-selladas-paso4-v1» cuyo CONTENIDO es el instalado y cuyo sha256 declara la AUTORIZACIÓN RECONSTRUIDA (bytes + acto) de la admisión que cubrió la tarea.
  python -B herramientas/b/comparar_tarea.py --plan <plan.json> --raiz-corrida <dir> --tarea <id> --despliegue <d.json> [--reglas-selladas <json>]
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]


def _carga(nombre, rel):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, INSTALACION / rel)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def _resumen(out, db_sha, tarea, ya):
    """Estado ESENCIAL del dictamen (igual en la primera ejecución y en la reutilización): «ya_comparada» indica reutilización, no aceptación."""
    return {"tarea": tarea, "ya_comparada": ya, "conteo": out.get("conteo"), "aceptado_global": out.get("aceptado_global"), "error": out.get("error_controlado"),
            "dictamen_sha256": db_sha, "estado": "error" if out.get("error_controlado") else ("aceptada" if out.get("aceptado_global") is True else "rechazada")}


def codigo_salida(r) -> int:
    """0 SOLO si el dictamen (nuevo o reutilizado) acepta; 3 error controlado; 2 rechazo (discrepancia, correspondencia incorrecta...);
    6 (rem47, --solo-reutilizar): no hay dictamen VÁLIDO para la correspondencia actual."""
    return 0 if r.get("estado") == "aceptada" else 3 if r.get("estado") == "error" else 6 if r.get("estado") == "sin_dictamen_valido" else 2


KIND_REGLAS = "reglas-selladas-paso4-v1"
# rem46: reglas que una autorización puede sellar en la comparación de cada fase (DR-1 para R2; DR-2 solo con R3 y por separado)
ADMISIBLES_POR_FASE = {"R2": ("R-SUCESION-S6",), "R3": ("R-SUCESION-S6", "R-NA-GNA1")}


class ReglasError(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle) if detalle else codigo)
        self.codigo = codigo


def validar_reglas(doc, fase, CR) -> list:
    """rem46: CONTENIDO del archivo de reglas selladas frente a lo INSTALADO (nunca frente a lo declarado): formato, fase, cada regla
    del catálogo del comparador en estado «propuesta», sha256 = sha256 de SU texto instalado, texto IDÉNTICO y, para DR-1, sus datos
    (valores admitidos) con el sha256 del archivo instalado. Devuelve la lista {id, sha256} que recibe el comparador."""
    if not isinstance(doc, dict) or doc.get("kind") != KIND_REGLAS or not isinstance(doc.get("reglas"), list) or not doc["reglas"]:
        raise ReglasError("REGLAS_SELLADAS_FORMATO", "se exige el formato %s con su lista de reglas" % KIND_REGLAS)
    if fase not in (doc.get("fases") or []):
        raise ReglasError("REGLAS_DE_OTRA_FASE", "%s no está en %s" % (fase, doc.get("fases")))
    out = []
    for r in doc["reglas"]:
        rid = r.get("id") if isinstance(r, dict) else None
        if rid not in ADMISIBLES_POR_FASE.get(fase, ()):
            raise ReglasError("REGLA_NO_ADMISIBLE_EN_LA_FASE", "%s en %s" % (rid, fase))
        cat = CR.REGLAS.get(rid)
        if cat is None or cat["estado"] != "propuesta" or r.get("sha256") != CR.sha_regla(rid) or r.get("texto") != cat["texto"]:
            raise ReglasError("REGLA_AJENA_O_ALTERADA", str(rid))
        if rid == "R-SUCESION-S6":
            dat = r.get("datos") or {}
            q = INSTALACION / "datos/paso4/dr1_tecnicas_admitidas.json"
            if dat.get("archivo") != "datos/paso4/dr1_tecnicas_admitidas.json" or dat.get("sha256") != CR.RD1.DATOS_SHA256 or \
                    hashlib.sha256(q.read_bytes()).hexdigest() != CR.RD1.DATOS_SHA256:
                raise ReglasError("DATOS_DE_LA_REGLA_DISTINTOS", "valores admitidos de DR-1")
        out.append({"id": rid, "sha256": r["sha256"]})
    if len({x["id"] for x in out}) != len(out):
        raise ReglasError("REGLA_REPETIDA")
    return out


def reglas_autorizadas(plan, raiz, t, reglas_path, modo_arnes):
    """rem46 (vinculación DR-1): un archivo de reglas solo ACTIVA reglas si (1) su contenido es exactamente el instalado
    (validar_reglas), (2) la AUTORIZACIÓN de la admisión que cubrió la tarea se RECONSTRUYE con sus bytes y su acto dedicado
    (corrida_paso4.reconstruir_admision: autorización conservada en <raíz>/autoridad, encargo y acto auténticos, en el modo de la corrida;
    una fuente de arnés solo vale en el arnés) y (3) ESA autorización declara reglas_selladas_sha256 = sha256 de este archivo. El campo del
    diario no basta: se lee la autorización. Sin archivo: ninguna regla propuesta (la comparación queda con las vigentes)."""
    if reglas_path is None:
        return [], None
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    CR = _carga("comparar_reproduccion", "herramientas/b/comparar_reproduccion.py")
    raw = Path(reglas_path).read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    try:
        doc = json.loads(raw)
    except ValueError:
        raise ReglasError("REGLAS_SELLADAS_FORMATO", "archivo ilegible")
    lista = validar_reglas(doc, t["fase"], CR)
    ev = CO.Diario(Path(raiz) / "diario_corrida.jsonl").leer()
    ini = [e for e in ev if e.get("op") == "inicio" and e.get("tarea") == t["id"]]
    adm = [e for e in ev if e.get("op") == "admision" and t["id"] in (e.get("tareas") or []) and (not ini or e.get("t", 0) <= ini[-1].get("t", 0))]
    if not adm:
        raise ReglasError("REGLAS_SIN_ADMISION", t["id"])
    try:
        aut = CO.reconstruir_admision(plan, Path(raiz), adm[-1], t, modo_arnes)
    except CO.CorridaError as ex:
        raise ReglasError("REGLAS_SIN_AUTORIDAD_RECONSTRUIDA", ex.codigo)
    ab = json.loads((Path(raiz) / CO.AUTORIDAD_DIR / ("autorizacion_%s.json" % aut["autorizacion_sha256"])).read_bytes())
    if ab.get("reglas_selladas_sha256") != h:
        raise ReglasError("REGLAS_SELLADAS_NO_AUTORIZADAS", "el archivo %s (sha256 %s) no es el declarado por la autorización %s" % (reglas_path, h, aut["autorizacion_sha256"][:16]))
    return lista, {"archivo": str(reglas_path), "sha256": h, "autorizadas_por_la_corrida": True, "autorizacion_sha256": aut["autorizacion_sha256"],
                   "acto_mensaje_sha256": aut["acto"]["mensaje_sha256"], "arnes": bool(aut["modo_arnes"])}


def comparar_tarea(plan, raiz_corrida, tarea, despliegue, reglas_selladas=None, reglas_path=None, modo_arnes=False, solo_reutilizar=False, fuentes=None, previas=None) -> dict:
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    CR = _carga("comparar_reproduccion", "herramientas/b/comparar_reproduccion.py")
    CO.verificar_plan(plan)
    t1 = {x["id"]: x for x in plan.get("r1") or []}.get(tarea)
    if t1 is not None:                              # rem49: R1 con OPCIÓN activa (B3 por unidad; A3 en la tarea L del par): opciones_p1.comparar_r1
        CO.need(fuentes is not None, "COMPARACION_R1_SIN_FUENTES")
        CO.need(reglas_path is None and not reglas_selladas, "REGLAS_NO_APLICAN_A_R1")
        OP = _carga("opciones_p1", "herramientas/b/opciones_p1.py")
        return OP.comparar_r1(plan, raiz_corrida, t1, despliegue, fuentes, modo_arnes=modo_arnes, previas=previas or (), solo_reutilizar=solo_reutilizar)
    raiz = Path(raiz_corrida)
    t = {x["id"]: x for x in plan["tareas"]}.get(tarea)
    CO.need(t is not None and t["fase"] in ("R2", "R3"), "TAREA_SIN_COMPARACION_R2_R3", tarea)
    if reglas_path is not None:                     # rem46: reglas desde ARCHIVO ligado a la AUTORIZACIÓN RECONSTRUIDA; nunca ambas vías
        CO.need(reglas_selladas is None, "REGLAS_POR_DOS_VIAS")
        reglas_selladas, reglas_info = reglas_autorizadas(plan, raiz, t, reglas_path, modo_arnes)
    else:
        CO.need(not reglas_selladas or modo_arnes, "REGLAS_SELLADAS_SIN_ARCHIVO_AUTORIZADO")
        reglas_info = {"arnes": True, "lista_directa_de_prueba": True} if reglas_selladas else None
    c = json.loads((raiz / "corrida.json").read_bytes())
    dsha = hashlib.sha256(Path(despliegue).read_bytes()).hexdigest()
    CO.need(c.get("plan_sha256") == plan["plan_sha256"] and c.get("despliegue_sha256") == dsha, "COMPARACION_CON_OTRA_IDENTIDAD_DE_CORRIDA")
    d = CO.Diario(raiz / "diario_corrida.jsonl")
    hist = CO.estado_tareas(d).get(tarea, [])
    acept = [e for e in hist if e["op"] == "fin" and e["estado"] == "completa_verificada"]
    CO.need(len(acept) == 1, "TAREA_NO_ACEPTADA", tarea)
    a = acept[0]
    sal = raiz / "salidas" / tarea
    CO.need(CO._arbol(sal) == a["arbol"], "SALIDA_ACEPTADA_ALTERADA", tarea)
    prod = a.get("productos") or {}
    CO.need(sorted(prod) == sorted(t["unidades"]), "PRODUCTOS_DISTINTOS_DE_LA_ASIGNACION", tarea)
    reg = json.loads((sal / CO.REGISTRO).read_bytes())
    cdir = raiz / "comparaciones" / tarea
    rel = lambda p: "../../salidas/%s/%s" % (tarea, p)  # noqa: E731
    files = {rel(p): {"sha256": h} for p, h in a["arbol"].items()}
    inv = {"files": files, "nota": "bytes ACEPTADOS de la tarea %s (árbol del diario); comparación fuera del árbol aceptado" % tarea}
    run_ids = set()
    for u in t["unidades"]:
        F = json.loads((sal / prod[u]["filas"]).read_bytes())
        run_ids.add((F.get("cell_context") or [{}])[0].get("run_id"))
    CO.need(len(run_ids) == 1 and None not in run_ids, "RUN_ID_NO_UNICO_EN_LOS_PRODUCTOS", str(sorted(map(str, run_ids)))[:120])
    clave = {x["unidad"]: k for k, x in CR.seleccion(t["fase"]).items()}       # clave contractual de la selección (R2: cell_id_contractual)
    CO.need(all(u in clave for u in t["unidades"]), "UNIDAD_FUERA_DE_LA_SELECCION_DEL_COMPARADOR", tarea)
    cor = {"seleccion": t["fase"], "alcance": {"tipo": "parcial", "contractuales": [clave[u] for u in t["unidades"]]},
           "corrida_nueva": {"raiz": str(cdir), "inventario_sha256": None, "run_id": run_ids.pop()},
           "unidades": [{"contractual": clave[u], "nuevo": {"doc": rel(prod[u]["documento"]), "filas": rel(prod[u]["filas"])}} for u in t["unidades"]],
           "reglas_selladas": list(reglas_selladas or []), "validacion_productiva": {"archivo": rel(CO.REGISTRO)}}
    ib = CO.canon(inv) + b"\n"
    cor["corrida_nueva"]["inventario_sha256"] = CO.sha(ib)
    cb = CO.canon(cor) + b"\n"
    prev = [e for e in d.leer() if e.get("op") == "comparacion" and e.get("tarea") == tarea and e.get("correspondencia_sha256") == CO.sha(cb)]
    if solo_reutilizar:                             # rem47 (P4-LOTE1-REANUDACION): SOLO devolver un dictamen guardado VÁLIDO para la correspondencia
        dp = cdir / "dictamen.json"                 # ACTUAL (tarea aceptada, árbol, reglas autorizadas, inventario); nunca compara ni escribe
        if prev and dp.is_file() and CO.sha(dp.read_bytes()) == prev[-1]["dictamen_sha256"]:
            return _resumen(json.loads(dp.read_bytes()), prev[-1]["dictamen_sha256"], tarea, True)
        return {"tarea": tarea, "ya_comparada": False, "estado": "sin_dictamen_valido", "conteo": None, "aceptado_global": None, "error": None, "dictamen_sha256": None,
                "motivo": "DICTAMEN_ALTERADO" if prev and dp.is_file() else "DICTAMEN_AUSENTE" if prev else "SIN_COMPARACION_PARA_LA_CORRESPONDENCIA_ACTUAL"}
    (cdir / "audit").mkdir(parents=True, exist_ok=True)
    (cdir / "audit/entrega.json").write_bytes(ib)
    if prev:                                        # rem42 P4-COMPARACION-IDEMPOTENCIA: reutilizar = devolver el MISMO dictamen y su estado
        dp = cdir / "dictamen.json"
        if dp.is_file() and CO.sha(dp.read_bytes()) == prev[-1]["dictamen_sha256"]:
            return _resumen(json.loads(dp.read_bytes()), prev[-1]["dictamen_sha256"], tarea, True)
        n = sum(1 for e in d.leer() if e.get("op") == "dictamen_retirado" and e.get("tarea") == tarea)
        destino = None
        if dp.is_file():                            # alterado: se conserva como evidencia, nunca se reutiliza
            destino = dp.with_name("dictamen.alterado-%d.json" % n)
            dp.replace(destino)
        d(op="dictamen_retirado", tarea=tarea, motivo="alterado" if destino else "eliminado", destino=str(destino) if destino else None,
          dictamen_sha256_registrado=prev[-1]["dictamen_sha256"])
    (cdir / "correspondencia.json").write_bytes(cb)
    CR.configurar(str(despliegue))
    out = CR.comparar(json.loads(cb))
    db = (json.dumps(out, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    (cdir / "dictamen.json").write_bytes(db)
    conteo = out.get("conteo")
    d(op="comparacion", tarea=tarea, correspondencia_sha256=CO.sha(cb), dictamen_sha256=CO.sha(db), conteo=conteo, aceptado_global=out.get("aceptado_global"),
      error=out.get("error_controlado"),
      reglas_selladas=[s.get("id") for s in (reglas_selladas or [])], reglas_info=reglas_info, registro_validacion_sha256=a["arbol"].get(CO.REGISTRO))
    return _resumen(out, CO.sha(db), tarea, False)


if __name__ == "__main__":
    a = sys.argv[1:]
    o = {k: a[a.index(k) + 1] for k in ("--plan", "--raiz-corrida", "--tarea", "--despliegue", "--reglas-selladas", "--fuentes", "--corridas-previas") if k in a}
    try:
        r = comparar_tarea(json.loads(Path(o["--plan"]).read_bytes()), o["--raiz-corrida"], o["--tarea"], o["--despliegue"], reglas_path=o.get("--reglas-selladas"),
                           modo_arnes="--modo-arnes" in a, solo_reutilizar="--solo-reutilizar" in a, fuentes=o.get("--fuentes"),
                           previas=[x for x in o.get("--corridas-previas", "").split(",") if x])
    except Exception as ex:  # noqa: BLE001  (rechazo de entrada: no hay dictamen)
        print(json.dumps({"rechazo": "%s: %s" % (type(ex).__name__, str(ex)[:300])}, ensure_ascii=False))
        raise SystemExit(4)
    print(json.dumps(r, ensure_ascii=False))
    raise SystemExit(codigo_salida(r))      # rem42: «ya_comparada» NO es éxito; el código sigue al estado del dictamen
