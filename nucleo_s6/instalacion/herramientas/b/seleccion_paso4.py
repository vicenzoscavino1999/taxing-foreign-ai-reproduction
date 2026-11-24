"""PUNTO DE ENTRADA CANDIDATO del paso 4 por selección (INTEGRACION H4 3.7, NO OFICIAL; copia candidata, no incorporada).

  python -B herramientas/b/seleccion_paso4.py --despliegue <despliegue.json> <fase> [args]
    seleccionar <tabla_v3.json> <dir_paquete> [--regla SEL-PASO4-DEMO-v1|SEL-PASO4-PILOTO-v1]
    ejecutar    <dir_paquete> [--interrumpir-tras N] [--almacen-techos <raiz>]
    reanudar    <dir_paquete> [--interrumpir-tras N] [--almacen-techos <raiz>]
    (--almacen-techos: caché PERSISTENTE de techos de esta corrida, herramientas/b/techos_persistentes.py; sin ella, la
     caché de techos vive solo dentro del proceso, como antes)
    validar     <dir_paquete> <salida.json>
    ensamblar   <salida.json> <dir_paquete> [<dir_paquete> ...]
    oficial     (SIEMPRE rechazada: OFICIAL_NO_AUTORIZADO)

Encadena selección -> plan -> ejecutor por lotes -> interrupción/reanudación -> verificador común -> ensamblaje (soporte
global validado) -> sello CANDIDATO cell_selection, con TODO el código operativo en la estructura candidata:
  herramientas/b/{seleccion_paso4, generador_seleccion, unidades, contexto_s5, soporte_global}.py,
  herramientas/s3/validadores/{paquete_seleccion, e13_referencia}.py y src/paper2b (núcleo candidato).
RELOCALIZABLE: las rutas internas se resuelven desde la ubicación de ESTE archivo; las externas (raíz del proyecto, raíz
de las fuentes históricas autenticadas, encargo y procedencia) vienen del archivo de DESPLIEGUE explícito. Ninguna
autorización oficial se activa: el contexto exige S5 real con banderas en False, `oficial` se rechaza y el sello
candidato lleva freeze_run_authorized = b_official_run_authorized = official_export_authorized = False.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
import uuid
from pathlib import Path

CAND = Path(__file__).resolve().parents[2]       # raíz de la INSTALACIÓN efectiva (…/candidato en el área; la raíz en S6)
AREA = CAND.parent                               # base de las rutas declaradas en CODIGO (relocalizable con la copia)
PREFIJO_LOGICO = "candidato/"                    # nombres LÓGICOS de CODIGO (identidad registrada en los paquetes)


def instalado(logico: str) -> Path:
    """Ruta física de un nombre lógico «candidato/...» en la instalación efectiva (lima0044: destino S6)."""
    need(logico.startswith(PREFIJO_LOGICO), "NOMBRE_LOGICO_FUERA_DEL_CANDIDATO:" + logico)
    return CAND / logico[len(PREFIJO_LOGICO):]


def logico(ruta) -> str:
    """Nombre lógico «candidato/...» de un archivo de la instalación efectiva (ValueError si está fuera)."""
    return PREFIJO_LOGICO + Path(ruta).resolve().relative_to(CAND.resolve()).as_posix()
if str(CAND / "src") not in sys.path:
    sys.path.insert(0, str(CAND / "src"))
import paper2b  # noqa: E402  (núcleo CANDIDATO, antes que cualquier otro import de paper2b)
assert Path(paper2b.__file__).resolve().parents[1] == (CAND / "src").resolve(), "NUCLEO_NO_CANDIDATO:" + paper2b.__file__
from paper2b import contrato_paquete as CP  # noqa: E402

REGLA = "SEL-PASO4-DEMO-v1"
SCHEMA = "paso4-seleccion-checkpoint-candidato-v1"
CODIGO = ("candidato/herramientas/b/seleccion_paso4.py", "candidato/herramientas/b/generador_seleccion.py", "candidato/herramientas/b/unidades.py",
          "candidato/herramientas/b/contexto_s5.py", "candidato/herramientas/b/contexto_s6.py", "candidato/herramientas/b/soporte_global.py",
          "candidato/herramientas/s3/validadores/paquete_seleccion.py", "candidato/herramientas/s3/validadores/e13_referencia.py",
          "candidato/herramientas/b/techos_persistentes.py",      # VALIDACION EFICIENCIA H4: el almacén de techos es código del productor
          "candidato/herramientas/s3/validadores/e13_v4.py")     # CACHE FINAL P0: E13 v4 integrada (catálogo de fuentes)
CLAVES_DESPLIEGUE = ("raiz_proyecto", "raiz_fuentes", "encargo", "procedencia", "politica", "recibo", "autor", "s5_package", "d7_tree", "run_class", "etiqueta")
# paso 4 (candidato): despliegue con la autoridad S6 viva (ancla externa obligatoria; D7 bajo S6 en salidas_s6 con directorio y árbol)
CLAVES_DESPLIEGUE_S6 = ("raiz_proyecto", "raiz_fuentes", "encargo", "procedencia", "politica", "recibo", "autor", "s6_package", "ancla", "d7_dir",
                        "d7_tree", "run_class", "etiqueta")
DESPLIEGUE = None


class FlujoError(RuntimeError):
    pass


def need(t, code):
    if not t:
        raise FlujoError(code)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def escribir_atomico(p: Path, data: bytes):
    tmp = p.with_name("." + p.name + "." + uuid.uuid4().hex)
    tmp.write_bytes(data)
    os.replace(tmp, p)


def testigo_dict(w):
    return json.loads(json.dumps({k: (dict(v) if hasattr(v, "keys") else v) for k, v in dict(w).items()}, default=list))


def _cargar(nombre, rel):
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, CAND / rel)
        m = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = m
        spec.loader.exec_module(m)
    return sys.modules[nombre]


def configurar(ruta_despliegue):
    """Carga el DESPLIEGUE explícito (rutas externas y parámetros de autoridad) y deja accesible el código ORIGINAL del
    proyecto (herramientas/, autoridad y validadores oficiales; solo lectura) sin anteponerlo al núcleo candidato."""
    global DESPLIEGUE
    d = json.loads(Path(ruta_despliegue).read_bytes())
    claves = CLAVES_DESPLIEGUE_S6 if isinstance(d, dict) and "s6_package" in d else CLAVES_DESPLIEGUE
    need(isinstance(d, dict) and set(d) == set(claves), "DESPLIEGUE_ESQUEMA:%s" % sorted(set(d) ^ set(claves)) if isinstance(d, dict) else "DESPLIEGUE_ESQUEMA")
    need("NO OFICIAL" in d["etiqueta"], "DESPLIEGUE_ETIQUETA_OFICIAL")
    for k in ("raiz_proyecto", "raiz_fuentes", "encargo", "procedencia"):
        need(Path(d[k]).exists(), "DESPLIEGUE_RUTA:" + k)
    if str(d["raiz_proyecto"]) not in sys.path:
        sys.path.append(str(d["raiz_proyecto"]))
    DESPLIEGUE = d
    return d


def _modulos():
    U = _cargar("cand_unidades", "herramientas/b/unidades.py")
    CS5 = _cargar("cand_contexto_s5", "herramientas/b/contexto_s5.py")
    P2 = _cargar("cand_paquete_seleccion", "herramientas/s3/validadores/paquete_seleccion.py")
    GC = _cargar("cand_generador_seleccion", "herramientas/b/generador_seleccion.py")
    return U, CS5, P2, GC


U, CS5, P2, GC = _modulos()
CS6 = _cargar("cand_contexto_s6", "herramientas/b/contexto_s6.py")
GE = GC.GE


def planificar(sel):
    return U.plan_selection(sel)


def codigo_manifiesto():
    fs = sorted((CAND / "src/paper2b").glob("*.py"))
    nuc = sha(b"".join(f.name.encode() + b"\0" + f.read_bytes() for f in fs))
    return {"nucleo_candidato_sha256": nuc, "archivos": {r: sha(instalado(r).read_bytes()) for r in CODIGO}}


def contexto():
    need(DESPLIEGUE is not None, "DESPLIEGUE_NO_CONFIGURADO")
    d = DESPLIEGUE
    if "s6_package" in d:
        return CS6.ContextoS6(d["raiz_proyecto"], politica=d["politica"], recibo=d["recibo"], autor=d["autor"], s6_package=d["s6_package"], ancla=d["ancla"],
                              d7_dir=d["d7_dir"], d7_tree=d["d7_tree"], run_class=d["run_class"], etiqueta=d["etiqueta"], encargo=d["encargo"],
                              procedencia=d["procedencia"], code_globs=(), productor=Path(__file__), codigo_productor=codigo_manifiesto())
    return CS5.ContextoS5(d["raiz_proyecto"], politica=d["politica"], recibo=d["recibo"], autor=d["autor"], s5_package=d["s5_package"], d7_tree=d["d7_tree"],
                          run_class=d["run_class"], etiqueta=d["etiqueta"], encargo=d["encargo"], procedencia=d["procedencia"], code_globs=(),
                          productor=Path(__file__), codigo_productor=codigo_manifiesto())


def referencia(ctx):
    return GE.Referencia(ctx, raiz=DESPLIEGUE["raiz_fuentes"])


def referencia_v4(ctx, catalogo):
    """CACHE FINAL P0: Referencia E13 v4 (herramientas/s3/validadores/e13_v4.py) con un catálogo EXPLÍCITO
    (CATALOGO_PROPAGACION, CATALOGO_MUESTRA o CATALOGO_CENSO). Las selecciones vigentes siguen usando referencia() (v3)."""
    E4 = _cargar("cand_e13_v4", "herramientas/s3/validadores/e13_v4.py")
    return E4.Referencia(ctx, DESPLIEGUE["raiz_fuentes"], getattr(E4, catalogo) if isinstance(catalogo, str) else catalogo)


def verificador(ctx, ref):
    return P2.Verificador(ctx, ref, sys.modules[__name__], GC, raiz_fuentes=DESPLIEGUE["raiz_fuentes"])


def seleccionar(tabla_p, pdir, regla=None):
    pdir = Path(pdir)
    need(not pdir.exists() or not any(pdir.iterdir()), "PAQUETE_NO_VACIO")
    pdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ctx = contexto()
    ref = referencia(ctx)
    raw = Path(tabla_p).read_bytes()
    doc = verificador(ctx, ref).seleccion_esperada(raw, regla or P2.REGLA_DEMO)       # LA MISMA regla que verifica el validador
    doc["sello_sha256"] = sha(canon({k: v for k, v in doc.items() if k != "sello_sha256"}))
    escribir_atomico(pdir / "seleccion.json", canon(doc))
    (pdir / "entrada").mkdir()
    (pdir / "entrada/global_extreme_v3.json").write_bytes(raw)
    plan = planificar(doc)
    escribir_atomico(pdir / "plan.json", canon(plan))
    print(json.dumps({"filas": len(doc["filas"]), "lotes": [l["lote_id"] for l in plan["lotes"]], "sello": doc["sello_sha256"][:16], "s": round(time.time() - t0, 1)}))


class Ejecutor(U.EjecutorSeleccion):
    """Ejecutor por lotes (unidades.EjecutorSeleccion) con sus dependencias explícitas de la estructura candidata."""

    def __init__(self, pdir, ctx, ref, V=None, almacen_techos=None):
        super().__init__(pdir, ctx, ref, V or verificador(ctx, ref), GC=GC, GE=GE, schema=SCHEMA, codigo=codigo_manifiesto(), error=FlujoError,
                         almacen_techos=almacen_techos)


def almacen_techos(raiz, espera_max_s=1800.0):
    """Fábrica EXPLÍCITA del almacén persistente de techos de UNA corrida (herramientas/b/techos_persistentes.py, esquema
    v2), solo para ejecutar/reanudar con --almacen-techos <raiz> [--espera-techo-s <s>]. La validación no lo carga."""
    TP = _cargar("cand_techos_persistentes", "herramientas/b/techos_persistentes.py")
    return TP.fabrica(raiz, espera_max_s=float(espera_max_s))


def validar(pdir, ref=None, V=None):
    if V is None and ref is not None:
        V = verificador(ref.ctx, ref)
    return P2.validar(pdir, ref, V)


def ensamblar(V, paquetes, salida=None):
    """Ensamblaje CANDIDATO de un universo de prueba ACOTADO (no la fase global del estudio): cada paquete validado es una
    unidad; el soporte global se CONSTRUYE desde los resúmenes por unidad (λ_π de macros admisibles por conjunto|país y
    C_2 de techos, como Run.unit_summary) y se re-valida al cerrar los provisionales; sello cell_selection sin
    autorizaciones por paquete. Devuelve el informe; no escribe nada fuera de `salida`."""
    t0 = time.time()
    unidades, filas, contenidos, sellos, run_ids = [], [], [], {}, set()
    for p in paquetes:
        p = Path(p)
        r = P2.verificar_paquete(V, p, "validar")
        need(r["cumple"], "ENSAMBLAJE_PAQUETE_NO_VALIDO:%s:%s" % (p.name, r["codigos"]))
        rows = {}
        for q in sorted(p.glob("lotes/*/*.jsonl")):
            rows.setdefault(q.stem, []).extend(json.loads(x) for x in q.read_text(encoding="utf-8").splitlines() if x.strip())
        inv = rows.get("inversion_result", [])
        conjunto = {x["cell_id"]: x["_fin"]["set"] for x in inv if "_fin" in x}       # conjunto de CADA celda
        macros = {m["macro_id"]: m for m in rows.get("lambda_pi_envelope", [])}
        lam = {}
        for cf in rows.get("confrontation_result", []):                          # λ_π de la macro de cada celda
            m = macros.get(cf["macro_id"])
            if m is not None and m["admissible"] and m["lambda_pi"] is not None and cf["cell_id"] in conjunto:
                k = conjunto[cf["cell_id"]] + "|" + m["country_id"]
                lo, hi = lam.get(k, (float("inf"), float("-inf")))
                lam[k] = (min(lo, m["lambda_pi"]), max(hi, m["lambda_pi"]))
                contenidos.append(("lambda", k, m["lambda_pi"]))
        c2s = [t["C_2"] for t in rows.get("capture_ceiling_result", []) if t["C_2"] is not None]
        contenidos += [("C2", c) for c in c2s]
        rid = {x["run_id"] for x in rows.get("cell_context", [])}
        need(len(rid) == 1, "ENSAMBLAJE_RUN_ID:%s" % p.name)
        run_ids |= rid
        unidades.append({"unit_id": p.name, "run_id": "UNIVERSO-PRUEBA", "lambda": {k: list(v) for k, v in sorted(lam.items())},
                         "c2": [min(c2s), max(c2s)] if c2s else None})
        filas += inv
        sellos[p.name] = U.sello_cell_selection(json.loads((p / "seleccion.json").read_bytes()), json.loads((p / "plan.json").read_bytes()),
                                                json.loads((p / "checkpoint.json").read_bytes())["identidad"]["autoridad"])
    plan_u = sorted(u["unit_id"] for u in unidades)
    plan_sha = sha(canon({"universo_de_prueba": plan_u, "run_ids_de_los_paquetes": sorted(run_ids)}))
    soporte = U.construir_soporte_global(unidades, plan_u, "UNIVERSO-PRUEBA", plan_sha)
    cerradas = U.cerrar_provisionales_con_soporte(filas, soporte, run_id="UNIVERSO-PRUEBA", plan_unidades=plan_u, plan_sha256=plan_sha, contenidos=contenidos)
    inf = {"alcance": "universo de PRUEBA acotado (paquetes dados); NO es la fase global del estudio ni habilita resultados oficiales",
           "paquetes": plan_u, "soporte_sha256": soporte["sha256"], "c2_estado": soporte["c2_estado"], "claves_lambda": sorted(soporte["lambda"]),
           "filas_cerradas": len(cerradas), "computed": sum(1 for x in cerradas if x["inversion_id"] in ("lambda_required", "capture_required") and x["result_status"] == "computed"),
           "outside_support": sum(1 for x in cerradas if x["inversion_id"] in ("lambda_required", "capture_required") and x["result_status"] == "outside_support"),
           "sellos_cell_selection": {k: v["sello_sha256"] for k, v in sellos.items()},
           "autorizaciones": {k: [v[f] for f in ("freeze_run_authorized", "b_official_run_authorized", "official_export_authorized")] for k, v in sellos.items()},
           "segundos": round(time.time() - t0, 2)}
    if salida:
        Path(salida).write_bytes((json.dumps({"informe": inf, "soporte": soporte}, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return inf


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    need("--despliegue" in a, "FALTA --despliegue")
    i = a.index("--despliegue")
    configurar(a[i + 1])
    del a[i:i + 2]
    fase = a[0]
    if fase == "oficial":
        try:
            P2.exigir_corrida_oficial()
        except P2.Rechazo as e:
            print("RECHAZADO: %s: %s" % (e.codigo, e.detalle))
            return 2
    if fase == "seleccionar":
        regla = a[a.index("--regla") + 1] if "--regla" in a else None
        seleccionar(a[1], a[2], regla)
        sel = json.loads((Path(a[2]) / "seleccion.json").read_bytes())
        return 0 if planificar(sel) == json.loads((Path(a[2]) / "plan.json").read_bytes()) else 2
    ctx = contexto()
    try:
        P2.puerta_autoridad(ctx)
    except P2.Rechazo as e:
        print("RECHAZADO: %s: %s" % (e.codigo, e.detalle))
        return 2
    ref = referencia(ctx)
    if fase in ("ejecutar", "reanudar"):
        it = int(a[a.index("--interrumpir-tras") + 1]) if "--interrumpir-tras" in a else None
        esp = float(a[a.index("--espera-techo-s") + 1]) if "--espera-techo-s" in a else 1800.0
        alm = almacen_techos(a[a.index("--almacen-techos") + 1], esp) if "--almacen-techos" in a else None
        try:
            Ejecutor(a[1], ctx, ref, almacen_techos=alm).ejecutar(reanudar=fase == "reanudar", interrumpir_tras=it)
        except FlujoError as e:
            print("RECHAZADO: %s" % e)
            return 2
        except Exception as e:  # noqa: BLE001 — solo la espera agotada del almacén es un estado controlado (76)
            TP = sys.modules.get("cand_techos_persistentes")
            if TP is not None and isinstance(e, TP.EsperaAgotada):
                print("ESPERA_TECHO_AGOTADA: %s" % e)
                return 76
            raise
        return 0
    V = verificador(ctx, ref)
    if fase == "validar":
        r = validar(a[1], V=V)
        Path(a[2]).write_bytes((json.dumps(r, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
        print(json.dumps({"cumple": r["cumple"], "productor": r.get("productor"), "contrato": r.get("contrato"), "codigos": r.get("codigos")}, ensure_ascii=False))
        return 0 if r["cumple"] else 2
    if fase == "ensamblar":
        print(json.dumps(ensamblar(V, a[2:], a[1]), ensure_ascii=False))
        return 0
    raise FlujoError("FASE_DESCONOCIDA:" + fase)


if __name__ == "__main__":
    raise SystemExit(main())
