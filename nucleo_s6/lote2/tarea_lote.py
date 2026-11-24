"""rem119 (P4-SUPLEMENTO-C0-COMPATIBILIDAD, COPIA AISLADA): en L1-ELAST, una malla marcada suplemento_topologia NO se recalcula. Sus filas son
las ACEPTADAS de la fuente del manifiesto (suplemento_fuente: ruta y sha256): se leen UNA vez sus bytes, se verifica su sha256 contra el
manifiesto autenticado y se usan ESOS bytes. Cada fila se conserva exactamente y recibe solo la topología del núcleo para su clave, diseño y
punto (conexion_frontera.enriquecer_suplemento), tras comprobar la compatibilidad de la estructura de estencil; una incompatibilidad deja la
tarea «incompleta» con la evidencia (nunca se combina). La procedencia de esas filas se publica como producto propio
suplemento_procedencia.jsonl, ligado al sha256 de frontier_result.jsonl: origen numérico LOTE1_ACEPTADO, topología del núcleo (identidad de
la instalación). Las demás mallas se calculan como antes con el núcleo (filas_frontera).
rem114 (G-E0E3, COPIA AISLADA): en L1-LAMBDA, un conjunto marcado dominio_nacional=estricto toma como estados TODOS los candidatos de la
enumeración estructural de su definición (conexion_lambda.vertices_estrictos), comprobando que la definición del contexto es la del manifiesto
(sha256); un share negativo deja la envolvente «pendiente_no_cubierto» sin evaluarla. En modo sintético, definicion_sintetica. hasta-seleccion
cuenta macro.bridge y macro.strict_vertices durante la preparación (deben ser 0) e informa la enumeración.
rem113 (COPIA AISLADA para el lote 2; mismas fórmulas, tolerancias, topes, puerta y rechazos): acepta más unidades sin cambiar el algoritmo.
(1) L1-ELAST: la clave del manifiesto es «diseño|j|frontier_id» (varias fronteras por diseño y j); diseño y j son sus dos primeros campos.
(2) L1-LAMBDA: la clave puede ser «conjunto|país»; el conjunto que se consulta en el contexto es v["conjunto"] (por defecto la clave).
(3) L1-COORD: un techo cuya clave transformada figura en techos_reutilizados del manifiesto (valor ACEPTADO de una clave idéntica) no se
    vuelve a buscar: se copia con su fuente; los demás se calculan como antes. La comparación por celda no cambia.
rem110: lista cerrada de modos/tareas antes de calcular; misma puerta de alcance+decisión para todo cálculo no sintético; cierre por estado
de filas/techos/envolventes. rem109 — TRABAJADOR CONTENIDO del lote 1 (L1-LAMBDA, L1-ELAST, L1-COORD). Se lanza por la ruta de contención admitida (p3ctl directa: Job,
límite duro = tope, máx. 3 procesos) y escribe solo en --salida y --resultado. El algoritmo científico es el del núcleo (macro.bridge y
macro.strict_vertices, model.frontier_grid vía conexion_frontera, frontier.capture_ceiling); este trabajador conecta entradas y salidas.
UNA SOLA RUTA DE CÁLCULO por tarea (calc_lambda, calc_elast, calc_coord): el modo «sintetico» la recorre con un manifiesto SINTÉTICO declarado
(kind …-SINTETICO); «produccion» con el manifiesto real, tras la puerta de alcance + decisión humana nativa (lector revisado del candidato).
Modos:
  hasta-seleccion  preparación REAL hasta la frontera anterior al cálculo (manifiesto real por sha256): L1-LAMBDA construye el contexto S6
                   portable (candidato rem107) y obtiene los estados nacionales sin evaluar λπ; L1-ELAST comprueba claves y dominios τ; L1-COORD
                   re-autentica las filas de las celdas padre (sha256) y sus K1/G. Estado «detenida_antes_del_calculo».
  sintetico        exige un manifiesto SINTÉTICO; nunca producción.
  produccion       exige --instalacion, --alcance (documento v3 verificado que fija este manifiesto, tarea, código del lote e instalación)
                   y --decision (decisión humana nativa sobre el sha256 del alcance, aprobacion_alcance.decision_humana); si no,
                   «rechazada» antes de calcular. NO autorizado en rem109 ni en rem110.
Estados: completa · incompleta (tope o cobertura parcial: nunca se publica como terminada) · rechazada · detenida_antes_del_calculo.
Uso: tarea_lote.py --tarea <L1-…> --modo <…> --manifiesto <json> --manifiesto-sha256 <sha> --salida <dir> --resultado <json> --tope-efectivo <s>
     [--instalacion <candidato>] [--despliegue <json>] [--alcance <json> --decision <json>]"""
import hashlib
import json
import sys
import time
from decimal import Decimal
from fractions import Fraction as Fr
from pathlib import Path

T0 = time.time()
a = sys.argv[1:]
o = {a[i]: a[i + 1] for i in range(0, len(a) - 1, 2) if a[i].startswith("--")}
AQUI = Path(__file__).resolve().parent
R = AQUI.parents[2]
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
SAL, RES = Path(o["--salida"]), Path(o["--resultado"])
TOPE = float(o["--tope-efectivo"])
raw = Path(o["--manifiesto"]).read_bytes()
out = {"tarea": o["--tarea"], "modo": o["--modo"], "manifiesto_sha256": H(raw), "tope_efectivo_s": TOPE, "sintetico": o["--modo"] == "sintetico",
       "codigo_sha256": {p.name: H(p.read_bytes()) for p in (Path(__file__), AQUI / "conexion_lambda.py", AQUI / "conexion_frontera.py")}, "productos": []}


def fin(estado, motivo=None, **k):
    out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2), **k)
    RES.parent.mkdir(parents=True, exist_ok=True)
    RES.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("tarea", "modo", "estado", "motivo", "pared_s")}, ensure_ascii=False))
    raise SystemExit(0 if estado in ("completa", "detenida_antes_del_calculo") else 4)


def producto(nombre, filas):
    SAL.mkdir(parents=True, exist_ok=True)
    p = SAL / nombre
    p.write_text("".join(json.dumps(f, ensure_ascii=False, default=str) + "\n" for f in filas), encoding="utf-8")
    out["productos"].append({"archivo": nombre, "sha256": H(p.read_bytes()), "filas": len(filas)})


def tope():
    if time.time() - T0 > TOPE:
        fin("incompleta", "TOPE_ALCANZADO (lo parcial no se publica como terminado)")


if H(raw) != o["--manifiesto-sha256"]:
    fin("rechazada", "MANIFIESTO_DISTINTO")
man = json.loads(raw)
SINT = str(man.get("kind", "")).endswith("-SINTETICO")
tarea, modo = o["--tarea"], o["--modo"]
MODOS, TAREAS = ("hasta-seleccion", "sintetico", "produccion"), ("L1-LAMBDA", "L1-ELAST", "L1-COORD")   # rem110: listas CERRADAS
if modo not in MODOS or tarea not in TAREAS:
    fin("rechazada", "MODO_O_TAREA_NO_ADMITIDOS (%s, %s): rechazo antes de cualquier entrada de cálculo" % (modo, tarea))
CALCULA = modo in ("sintetico", "produccion")
if (modo == "sintetico") != SINT:
    fin("rechazada", "MODO_Y_MANIFIESTO_INCOMPATIBLES (el modo sintético exige un manifiesto sintético y viceversa)")
NUCLEO = (Path(o["--instalacion"]) / "src") if "--instalacion" in o else (R / "paso4/instalacion/src")   # el contexto del candidato exige SU núcleo (mismos bytes de paper2b)
sys.path[:0] = [str(AQUI), str(NUCLEO)]
import conexion_lambda as CLX  # noqa: E402
import conexion_frontera as CFR  # noqa: E402
from paper2b import macro as MC  # noqa: E402
from paper2b import model as M  # noqa: E402
from paper2b import run as RUN  # noqa: E402
from paper2b import frontier as FR  # noqa: E402

if CALCULA and not SINT and modo != "produccion":                  # rem110: no hay rama de cálculo real fuera de la puerta
    fin("rechazada", "CALCULO_REAL_SIN_PUERTA")
if modo == "produccion":
    if not ("--alcance" in o and "--decision" in o and "--instalacion" in o):
        fin("rechazada", "PRODUCCION_SIN_ALCANCE_NI_DECISION (no autorizada en rem109 ni en rem110)")
    sys.path.insert(0, str(Path(o["--instalacion"]) / "herramientas/b"))
    import aprobacion_alcance as AA  # noqa: E402
    ab = Path(o["--alcance"]).read_bytes()
    al = json.loads(ab)
    try:
        AA.verificar_documento(al)                                       # rem110: documento de alcance v3 completo y no oficial
    except AA.Rechazo as ex:
        fin("rechazada", ex.codigo)
    if al.get("lote_manifiesto_sha256") != H(raw) or (al.get("entradas") or {}).get("lote_manifiesto") != H(raw):
        fin("rechazada", "ALCANCE_DE_OTRO_MANIFIESTO")
    if tarea not in (al.get("tareas") or []):
        fin("rechazada", "TAREA_FUERA_DEL_ALCANCE")
    if (al.get("entradas") or {}).get("codigo_lote") != out["codigo_sha256"]:
        fin("rechazada", "ALCANCE_DE_OTRO_CODIGO_DEL_LOTE")
    if al.get("instalacion_identidad") != AA.identidad_instalacion(Path(o["--instalacion"])):
        fin("rechazada", "ALCANCE_DE_OTRA_INSTALACION")
    try:
        AA.decision_humana(o["--decision"], H(ab), al["emitida_utc"])
    except AA.Rechazo as ex:
        fin("rechazada", ex.codigo)


def dom_manifiesto(d):
    """Dominio serializado en el manifiesto → objeto de conexion_lambda.dominio (Fraction y cierres)."""
    if d["tipo"] == "discreto":
        return {"tipo": "discreto", "valores": [Fr(x) for x in d["valores"]]}
    return {"tipo": "continuo", "lo": Fr(d["lo"]), "hi": Fr(d["hi"]), "lo_cerrado": d["lo_cerrado"] in (True, "True", "true"), "hi_cerrado": d["hi_cerrado"] in (True, "True", "true")}


def proveedor_real(ctx, s, pais):
    """Estados nacionales como Run.states_for: dominio estricto → vértices de MC.strict_vertices para las coordenadas macro de ESE ω."""
    estados = ctx.inp.national(s, pais)

    def prov(om):
        lista = []
        for st in estados:
            if isinstance(st, dict) and st.get("kind") == "strict_domain":
                for _, (prim, shares) in sorted(MC.strict_vertices(st["domains"], st["terms"], st["denominator"], om).items()):
                    lista.append(shares)
            else:
                lista.append(st.share_dict())
        return lista
    return prov


def estrictos(ctx, ml):
    """rem114 (G-E0E3): candidatos de los conjuntos de dominio estricto = enumeración estructural de SU definición en el contexto, que debe ser
    exactamente la del manifiesto (sha256). Devuelve {clave: (candidatos, vértices, signo, sha)} o un motivo de rechazo."""
    out = {}
    for s, v in ml.items():
        if v.get("dominio_nacional") != "estricto":
            continue
        if ctx is None:
            st = v["definicion_sintetica"]
        else:
            sts = ctx.inp.national(v.get("conjunto", s), v["pais"])
            if len(sts) != 1 or not (isinstance(sts[0], dict) and sts[0].get("kind") == "strict_domain"):
                return "DOMINIO_ESTRICTO_NO_UNICO_EN_EL_CONTEXTO:" + s
            st = sts[0]
        if CLX.definicion_sha256(st) != v["definicion_sha256"]:
            return "DEFINICION_ESTRICTA_DISTINTA_DEL_MANIFIESTO:" + s
        try:
            cand, n, signo = CLX.vertices_estrictos(MC, st)
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as ex:      # dominio vacío/invertido o denominador no positivo: no hay cobertura
            return "DOMINIO_ESTRICTO_INVALIDO:%s:%s" % (s, ex)
        out[s] = (cand, n, signo, CLX.definicion_sha256(st))
    return out


def calc_lambda(ml, proveedores, est=None):
    filas = []
    for s, v in ml.items():
        dom = {p: dom_manifiesto(d) for p, d in v["dominios"].items()}
        for var in ("con", "sin"):
            tope()
            if est and s in est and not est[s][2]:          # rem114: un share negativo ⇒ el testigo ω no es común a los candidatos: NO cubierto
                filas.append({"variante": var, "estado": "pendiente_no_cubierto", "notas": ["SIGNO_DE_SHARES_NO_UNIFORME: algún candidato del dominio "
                              "estricto tiene un share negativo; la monotonía que fija el testigo ω no vale para todos; no se evalúa"],
                              "conjunto": s, "pais": v["pais"], "sintetico": SINT, "llamadas_bridge": 0})
                continue
            filas.append(dict(CLX.envolvente(MC, proveedores[s], dom, var), conjunto=s, pais=v["pais"], sintetico=SINT))
    return filas


def fuente_suplemento(fr_):
    """rem119: fuente ACEPTADA del suplemento desde el manifiesto autenticado; una sola lectura de bytes, verificación y uso de esos bytes."""
    sf = man["L1-ELAST"].get("suplemento_fuente") or {}
    p = R / str(sf.get("ruta"))
    if not sf or not p.is_file():
        fin("incompleta", "SUPLEMENTO_SIN_FUENTE_ACEPTADA")
    b = p.read_bytes()
    if H(b) != sf.get("sha256"):
        fin("incompleta", "SUPLEMENTO_FUENTE_NO_AUTENTICA (sha256 %s, manifiesto %s)" % (H(b), sf.get("sha256")))
    ids = {v["frontier_id"] for v in fr_.values() if v.get("suplemento_topologia")}
    filas = [y for y in (json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()) if y.get("frontier_id") in ids]
    if len(filas) != sf.get("filas") or len({(y["frontier_id"], y["point_id"], y["side"]) for y in filas}) != len(filas):
        fin("incompleta", "SUPLEMENTO_FILAS_DISTINTAS_DEL_MANIFIESTO (%d, manifiesto %s)" % (len(filas), sf.get("filas")))
    return sf, H(b), filas


def calc_elast(fr_):
    filas, procedencia, bloqueadas = [], [], []
    fuente = fuente_suplemento(fr_) if any(v.get("suplemento_topologia") for v in fr_.values()) else None
    for k, v in fr_.items():
        tope()
        diseno, j = k.split("|")[:2]
        if v.get("suplemento_topologia"):                          # rem119: filas ACEPTADAS + topología del núcleo; nada se recalcula
            acept = [y for y in fuente[2] if y["frontier_id"] == v["frontier_id"]]
            rows, proc, bloq = CFR.enriquecer_suplemento(RUN, M, FR, v["clave_estructural"], v["dominio_tau"], diseno, acept)
            filas += rows
            procedencia += proc
            bloqueadas += bloq
            continue
        _, rows, n = CFR.filas_frontera(RUN, M, v["clave_estructural"], v["dominio_tau"], diseno, j, frontier_id=v["frontier_id"])
        filas += [dict(r, sintetico=SINT) for r in rows]
    return filas, procedencia, bloqueadas, fuente


def calc_coord(co):
    cfg = RUN.RunConfig()
    techos, por_clave = [], {}
    for c in co["celdas"]:
        k = c["clave_transformada_sha256"]
        if k in por_clave:
            continue
        if k in (co.get("techos_reutilizados") or {}):             # rem113: valor ACEPTADO de una clave idéntica; no se repite la búsqueda
            r = co["techos_reutilizados"][k]
            por_clave[k] = {"clave_transformada_sha256": k, "C_2": r["C_2"], "estado": r["estado"], "error": r["error"], "motivo": r["motivo"], "sintetico": SINT,
                            "reutilizado_de": r["fuente"], "reutilizado_sha256": r["fuente_sha256"]}
            techos.append(por_clave[k])
            continue
        tope()
        cl = co["claves_transformadas"][k]
        st = M.state_from_primitives({p: float(x) for p, x in cl["clave"].items()})
        ce = FR.capture_ceiling(st, cl["diseno"], cl["j"], float(cl["tau"]["tau_d_upper"]), float(cl["tau"]["tau_f_upper"]), True, cfg.sup)
        por_clave[k] = {"clave_transformada_sha256": k, "C_2": ce.C2, "estado": ce.status, "error": ce.numerical_error, "motivo": ce.reason, "sintetico": SINT}
        techos.append(por_clave[k])
    comp = []
    for c in co["celdas"]:
        t = por_clave[c["clave_transformada_sha256"]]
        comp.append({"unidad": c["unidad"], "cell_id": c["cell_id"], "K1_reutilizado": c["K1_reutilizado"], "G_padre": c["G_padre"], "C2_coord": t["C_2"],
                     "G_coord": (t["C_2"] - c["K1_reutilizado"]) if t["C_2"] is not None and t["estado"] == "complete" else None, "estado_techo": t["estado"], "sintetico": SINT})
    return techos, comp


# ============================== L1-LAMBDA ==============================
if tarea == "L1-LAMBDA":
    ml = man["L1-LAMBDA"]
    if modo == "hasta-seleccion" or modo == "produccion":
        sys.path.insert(0, str(Path(o["--instalacion"]) / "herramientas/b"))
        import seleccion_paso4 as SP  # noqa: E402
        llamadas = {"macro.bridge": 0, "macro.strict_vertices": 0}
        if modo == "hasta-seleccion":                    # rem114: la preparación debe quedar con CERO llamadas científicas (contadas)
            for _n in ("bridge", "strict_vertices"):
                setattr(MC, _n, (lambda nombre, orig: (lambda *a, **k: (llamadas.__setitem__("macro." + nombre, llamadas["macro." + nombre] + 1), orig(*a, **k))[1]))(_n, getattr(MC, _n)))
        t = time.time()
        SP.configurar(o["--despliegue"], None, True)
        ctx = SP.contexto()
        est = estrictos(ctx, ml)
        if isinstance(est, str):
            fin("incompleta", est)
        if modo == "hasta-seleccion":
            prep = {s: {"estados_nacionales": len(ctx.inp.national(v.get("conjunto", s), v["pais"])),
                        "tipos": sorted({(x.get("kind") if isinstance(x, dict) else "NationalState") for x in ctx.inp.national(v.get("conjunto", s), v["pais"])}),
                        "testigos_omega_unicos": v["testigos_omega_unicos"]} for s, v in ml.items()}
            for s, (cand, n, signo, sha) in est.items():
                prep[s].update(candidatos_estrictos=len(cand), vertices_caja=n, signo_no_negativo=signo, definicion_sha256=sha)
            fin("detenida_antes_del_calculo", "PREPARACION_REAL_COMPLETA_SIN_EVALUAR_LAMBDA", contexto_s=round(time.time() - t, 1), contexto_identidad=ctx.identity_sha256,
                preparacion=prep, llamadas_durante_preparacion=llamadas)
        prov = {s: proveedor_real(ctx, v.get("conjunto", s), v["pais"]) for s, v in ml.items() if s not in est}
        prov.update({s: (lambda c: (lambda om: [x["shares"] for x in c]))(cand) for s, (cand, n, signo, sha) in est.items()})
        filas = calc_lambda(ml, prov, est)
    else:
        est = estrictos(None, ml)
        if isinstance(est, str):
            fin("incompleta", est)
        prov = {s: (lambda sh: (lambda om: [sh]))({k: Fr(x) for k, x in v["shares_sinteticos"].items()}) for s, v in ml.items() if s not in est}
        prov.update({s: (lambda c: (lambda om: [x["shares"] for x in c]))(cand) for s, (cand, n, signo, sha) in est.items()})
        filas = calc_lambda(ml, prov, est)
    producto("lambda_envolvente.jsonl", filas)
    out["llamadas_bridge"] = sum(f.get("llamadas_bridge", 0) for f in filas)
    fin("completa" if filas and all(f["estado"] == "ok" for f in filas) else "incompleta",
        ("SINTETICO_NO_PRODUCCION" if SINT else None) if all(f["estado"] == "ok" for f in filas) else "ENVOLVENTE_NO_CUBIERTA: %s" % [(f["conjunto"], f["variante"], f["estado"]) for f in filas if f["estado"] != "ok"])
# ============================== L1-ELAST ==============================
if tarea == "L1-ELAST":
    fr_ = man["L1-ELAST"]["fronteras"]
    if modo == "hasta-seleccion":
        falt = {k: [p for p in ("a", "beta_tilde", "c_legal", "eta_d", "eta_f", "gamma", "kappa_tilde", "phi", "rho", "t", "u_theta", "z_cost", "z_m") if p not in v["clave_estructural"]]
                for k, v in fr_.items()}
        ok = all(not x for x in falt.values()) and all(v["dominio_tau"] for v in fr_.values())
        sup_ = fuente_suplemento(fr_) if any(v.get("suplemento_topologia") for v in fr_.values()) else None   # rem119: fuente autenticada, sin ciencia
        fin("detenida_antes_del_calculo" if ok else "rechazada", "CLAVES_Y_DOMINIOS_COMPLETOS" if ok else "CLAVE_INCOMPLETA", faltantes=falt,
            puntos_al_calcular=man["L1-ELAST"]["puntos_totales_frontier_n4"], suplemento_filas_aceptadas=len(sup_[2]) if sup_ else 0,
            suplemento_fuente_sha256=sup_[1] if sup_ else None,
            suplemento_mallas=len({y["frontier_id"] for y in sup_[2]}) if sup_ else 0)
    filas, procedencia, bloqueadas, fuente = calc_elast(fr_)
    if bloqueadas:                                                   # rem119: incompatibilidad semántica: no se combina ni se publica
        fin("incompleta", "SUPLEMENTO_INCOMPATIBLE_CON_EL_NUCLEO (%d filas): %s" % (len(bloqueadas), [(b["frontier_id"], b["point_id"], b["discrepancias"]) for b in bloqueadas[:3]]),
            suplemento_bloqueado=bloqueadas)
    producto("frontier_result.jsonl", filas)
    if fuente is not None:
        if "--instalacion" in o:
            sys.path.insert(0, str(Path(o["--instalacion"]) / "herramientas/b"))
            import aprobacion_alcance as AA_  # noqa: E402  (solo la identidad canónica de la instalación que da la topología)
            ident = AA_.identidad_instalacion(Path(o["--instalacion"]))
        else:
            ident = None
        sha_fr = out["productos"][-1]["sha256"]
        producto("suplemento_procedencia.jsonl", [dict(p, origen_numerico="LOTE1_ACEPTADO", origen_topologia="NUCLEO_DE_LA_TAREA", instalacion_identidad=ident,
                                                       fuente_ruta=fuente[0]["ruta"], fuente_sha256=fuente[1], frontier_result_sha256=sha_fr,
                                                       nota="valores numéricos ACEPTADOS copiados sin cambios; solo la topología procede del núcleo",
                                                       sintetico=SINT) for p in procedencia])
    fallidas = [f["frontier_id"] + ":" + f["point_id"] for f in filas if f.get("computation_status") != "complete" or f.get("audit_status") not in ("pass", "limitation")]
    fin("completa" if filas and not fallidas else "incompleta", ("SINTETICO_NO_PRODUCCION" if SINT else None) if not fallidas else "FILAS_CON_CALCULO_FALLIDO: %s" % fallidas[:5])
# ============================== L1-COORD ==============================
if tarea == "L1-COORD":
    co = man["L1-COORD"]
    if modo == "hasta-seleccion":
        malos = []
        for c in co["celdas"]:
            p = R / "tmp" / c["ref"]
            if not p.is_file() or H(p.read_bytes()) != c["filas_sha256"]:
                malos.append(c["unidad"])
                continue
            cr = (json.loads(p.read_bytes()).get("confrontation_result") or [{}])[0]
            if cr.get("K_comp_1") != c["K1_reutilizado"] or cr.get("G") != c["G_padre"]:
                malos.append(c["unidad"])
        fin("detenida_antes_del_calculo" if not malos else "rechazada", "CELDAS_PADRE_AUTENTICADAS" if not malos else "CELDA_PADRE_NO_AUTENTICA",
            celdas=len(co["celdas"]), techos_nuevos_al_calcular=co.get("techos_nuevos_unicos", co.get("techos_a_calcular")),
            techos_reutilizados=len(co.get("techos_reutilizados") or {}), k1_reutilizados=len(co["celdas"]) - len(malos), malos=malos[:5])
    techos, comp = calc_coord(co)
    producto("coord_techos.jsonl", techos)
    producto("coord_comparacion.jsonl", comp)
    import math
    malos = [t["clave_transformada_sha256"] for t in techos if t["estado"] != "complete" or t["C_2"] is None or t["error"] is None or not math.isfinite(t["C_2"]) or not math.isfinite(t["error"])]
    fin("completa" if techos and not malos else "incompleta", ("SINTETICO_NO_PRODUCCION" if SINT else None) if not malos else "TECHOS_INCOMPLETOS: %s" % malos[:5])
fin("rechazada", "TAREA_DESCONOCIDA")
