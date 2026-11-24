"""rem122 — TRABAJADOR CONTENIDO DE LA RECUPERACIÓN COORD (paquete lote_rec; derivado de tarea_lote.py rem119 dca9d79b…). La puerta de alcance +
decisión humana nativa es la misma, con las mismas comprobaciones y en el mismo orden, antes de cualquier entrada de cálculo. Cambian las tareas
(lista CERRADA de la partición: L1-COORD-R1, L1-COORD-R2, L1-COORD-R3, cada una con sus claves en la sección L1-COORD-REC del manifiesto) y
el cálculo del techo: conexion_coord_cert.techo con model = RUN.provider_for(cfg) (ModeloTeorico certificado, configuración del manifiesto);
nunca frontier.capture_ceiling (se sustituye por una función que falla). Cada techo se persiste en coord_techos_rec.jsonl en cuanto termina
(identidad, parámetros, método/configuración, valor, testigo, error_kind, errores en ambas escalas, cotas, valores por nivel y estado), con
la tarea, el sha256 del manifiesto y, en producción, el del alcance. Una interrupción deja los parciales en ese archivo SIN registrarlos como
producto ni publicar la tarea como completa; no hay reintentos. Antes de calcular, el motor de C0 debe tener la identidad de código del
manifiesto y la configuración declarada.
Modos (lista cerrada):
  hasta-seleccion  autentica por sus bytes el manifiesto LOTE2, las fuentes reutilizadas y las filas padre de las celdas afectadas (sha256) y
                   comprueba K1/G; no construye estados ni llama a ningún supremo. Estado «detenida_antes_del_calculo».
  sintetico        exige un manifiesto SINTÉTICO (kind …-SINTETICO): recorre la MISMA ruta (estado, Engine, capture_ceiling real de C0) con
                   encierros_modelo.sup_bound sustituido por el DOBLE DECLARADO del manifiesto (SupBound sintético por clave). Nunca producción.
  produccion       exige --instalacion, --alcance (v3 verificado que fija este manifiesto, tarea, código e instalación) y --decision
                   (decisión humana nativa sobre el sha256 del alcance); si no, «rechazada» antes de calcular. NO autorizado en rem122.
Estados: completa · incompleta · rechazada · detenida_antes_del_calculo.
Uso: tarea_lote.py --tarea <L1-COORD-R…> --modo <…> --manifiesto <json> --manifiesto-sha256 <sha> --salida <dir> --resultado <json>
     --tope-efectivo <s> [--instalacion <C0>] [--despliegue <json>] [--alcance <json> --decision <json>]"""
import hashlib
import json
import sys
import time
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
       "codigo_sha256": {p.name: H(p.read_bytes()) for p in (Path(__file__), AQUI / "conexion_coord_cert.py")}, "productos": []}


def fin(estado, motivo=None, **k):
    out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2), **k)
    RES.parent.mkdir(parents=True, exist_ok=True)
    RES.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("tarea", "modo", "estado", "motivo", "pared_s")}, ensure_ascii=False))
    raise SystemExit(0 if estado in ("completa", "detenida_antes_del_calculo") else 4)


def producto(nombre, filas=None):
    SAL.mkdir(parents=True, exist_ok=True)
    p = SAL / nombre
    if filas is not None:
        with p.open("x", encoding="utf-8") as f:
            f.write("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in filas))
    b = p.read_bytes()
    out["productos"].append({"archivo": nombre, "sha256": H(b), "filas": len([x for x in b.splitlines() if x.strip()])})


def tope():
    if time.time() - T0 > TOPE:
        fin("incompleta", "TOPE_ALCANZADO (lo parcial no se publica como terminado)")


if H(raw) != o["--manifiesto-sha256"]:
    fin("rechazada", "MANIFIESTO_DISTINTO")
man = json.loads(raw)
SINT = str(man.get("kind", "")).endswith("-SINTETICO")
tarea, modo = o["--tarea"], o["--modo"]
MODOS, TAREAS = ("hasta-seleccion", "sintetico", "produccion"), ("L1-COORD-R1", "L1-COORD-R2", "L1-COORD-R3")   # listas CERRADAS
if modo not in MODOS or tarea not in TAREAS:
    fin("rechazada", "MODO_O_TAREA_NO_ADMITIDOS (%s, %s): rechazo antes de cualquier entrada de cálculo" % (modo, tarea))
CALCULA = modo in ("sintetico", "produccion")
if (modo == "sintetico") != SINT:
    fin("rechazada", "MODO_Y_MANIFIESTO_INCOMPATIBLES (el modo sintético exige un manifiesto sintético y viceversa)")
if "--instalacion" not in o:
    fin("rechazada", "SIN_INSTALACION (el motor certificado es el de C0, fijado por identidad)")
NUCLEO = Path(o["--instalacion"]) / "src"
sys.path[:0] = [str(AQUI), str(NUCLEO)]
import conexion_coord_cert as CX  # noqa: E402
import validar_coord_rec as VC  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import frontier as FR  # noqa: E402
from paper2b import run as RUN  # noqa: E402

if CALCULA and not SINT and modo != "produccion":                  # no hay rama de cálculo real fuera de la puerta
    fin("rechazada", "CALCULO_REAL_SIN_PUERTA")
if modo == "produccion":
    if not ("--alcance" in o and "--decision" in o and "--instalacion" in o):
        fin("rechazada", "PRODUCCION_SIN_ALCANCE_NI_DECISION (no autorizada en rem122)")
    sys.path.insert(0, str(Path(o["--instalacion"]) / "herramientas/b"))
    import aprobacion_alcance as AA  # noqa: E402
    ab = Path(o["--alcance"]).read_bytes()
    al = json.loads(ab)
    try:
        AA.verificar_documento(al)                                       # documento de alcance v3 completo y no oficial
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
    out["alcance_sha256"] = H(ab)

co = man.get("L1-COORD-REC") or {}
claves = (co.get("tareas") or {}).get(tarea)
if not claves:
    fin("rechazada", "TAREA_SIN_CLAVES_EN_LA_PARTICION_DEL_MANIFIESTO")
if modo == "hasta-seleccion":
    malos = []
    if VC.celdas_del_lote(R, co)[2]:
        malos.append(VC.celdas_del_lote(R, co)[2])
    malos += VC.reutilizados_autenticados(R, co)[1]
    for c in co["celdas_afectadas"]:
        p = R / "tmp" / c["ref"]
        b = p.read_bytes() if p.is_file() else b""
        if H(b) != c["filas_sha256"]:
            malos.append("CELDA_PADRE_NO_AUTENTICA:" + c["unidad"])
            continue
        cr = (json.loads(b).get("confrontation_result") or [{}])[0]
        if cr.get("K_comp_1") != c["K1_reutilizado"] or cr.get("G") != c["G_padre"]:
            malos.append("K1_O_G_PADRE_DISTINTO:" + c["unidad"])
    fin("detenida_antes_del_calculo" if not malos else "rechazada", "FUENTES_Y_CELDAS_AUTENTICADAS" if not malos else "PREPARACION_NO_AUTENTICA",
        claves=claves, celdas_afectadas=sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in claves), malos=malos[:5])

# ------------------------------------------------ cálculo (sintético con doble declarado o producción tras la puerta)
FR.capture_ceiling = lambda *a_, **k_: (_ for _ in ()).throw(AssertionError("RUTA_FLOTANTE_PROHIBIDA"))   # sin respaldo flotante
cfg = RUN.RunConfig()
model = RUN.provider_for(cfg)
ident = CX.identidad_codigo(NUCLEO / "paper2b")
if ident != co["motor"]["codigo"]:
    fin("rechazada", "MOTOR_DE_OTRA_IDENTIDAD")
actual = {"k": None}
if SINT:
    dobles = co["sintetico"]["supbound"]

    def doble(eng, j, bd, bf, **kw):                                  # DOBLE DECLARADO: SupBound sintético del manifiesto; ninguna rama y cota
        d = dobles[actual["k"]]
        return EM.SupBound(d["approx"], d["lower"], d["upper"], tuple(d["punto"]), [], d["cajas"], d["salto_vivo"])
    EM.sup_bound = doble
ruta = SAL / "coord_techos_rec.jsonl"
SAL.mkdir(parents=True, exist_ok=True)
if ruta.exists():
    fin("rechazada", "SALIDA_DE_TECHOS_YA_EXISTE")
por_clave = {}
for k in claves:
    tope()
    actual["k"] = k
    fila = CX.techo(model, co["claves_recalculadas"][k], cfg.sup, k, ident, co["motor"]["configuracion"])
    fila.update(tarea=tarea, manifiesto_sha256=H(raw), alcance_sha256=out.get("alcance_sha256"), sintetico=SINT)
    CX.persistir(fila, ruta)
    por_clave[k] = fila
producto("coord_techos_rec.jsonl")
celdas = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in claves]
producto("coord_comparacion_rec.jsonl", [dict(x, tarea=tarea, sintetico=SINT) for x in CX.comparaciones(celdas, por_clave)])
malos = [k for k, t in por_clave.items() if t["estado"] != "complete"]
fin("completa" if not malos else "incompleta", ("SINTETICO_NO_PRODUCCION" if SINT else None) if not malos else "TECHOS_INCOMPLETOS: %s" % malos)
