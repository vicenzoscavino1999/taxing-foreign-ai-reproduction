"""Comando general de la reproducción limpia (subpasos 2.2.3 y 2.2.2): las 39 operaciones del catálogo conectadas a llamadas reales.

- plan: lanza las recetas existentes (famXX-receta, sin cálculo), convierte sus órdenes en llamadas de reproducir.py dentro de una carpeta
  de ejecución nueva, las ordena por datos, liga cada clave del catálogo a sus llamadas y a la comparación o verificación de sus productos,
  y escribe plan.json y BALANCE.md. No calcula.
- piloto: las mismas llamadas para la cadena FAM08 + FAM11 + FAM12 -> FAM10. El integral ENF y el ensamblado COV toman las tareas
  guardadas del paquete, como admiten sus recetas (--entrada <tarea>=guardado; ENTRADA-GUARDADA-PILOTO-v1). B1 -> B2, P7 y Q se ejecutan
  enteros, con B2 sobre el B1 validado de esta ejecución.
- completo: todas las llamadas del plan (Paso 3). Solo se ejecuta si se elige expresamente.
- ensayo-fam01: unidades de FAM01 nombradas con --unidad, en un mismo proceso fam01-unidad, con fam01-listas antes y una comparación
  por unidad después (ENSAYO-FAM01-v1). Varias unidades solo si comparten selección y grupo de techo caro (GRUPOS-TECHO-C2-v1).

Cada llamada corre en su propio proceso: el intérprete y las opciones de esta invocación, el entorno del perfil y el límite externo que
fija su receta. Al agotarlo se termina el árbol de procesos. Un paso no se lanza si su productor falló, fue rechazado, o si su entrada
falta o cambió desde que se produjo; queda bloqueado y lo dice el balance. Por omisión, una llamada a la vez. Con procesos_fam01 = N
(1 < N ≤ 12), hasta N llamadas de FAM01 a la vez, cada una cuando sus dependencias quedaron resueltas; las demás familias siguen
una a una, en el orden del plan y sin otra llamada en curso. Ningún cálculo se ejecuta al importar este módulo.

Reanudación (REANUDACION-PASO3-v1): una corrida no se reparte entre dos ejecutores a la vez (cerrojo en <S>/ejecucion.lock). Al empezar se
guardan en <S>/control.json la huella del inventario de ejecución, el entorno y la huella del plan. Cada llamada cerrada queda en
<S>/estado_llamadas.jsonl, forzada a disco: su estado y, si fue aceptada, las huellas de su salida. Con reanudar() se vuelven a comprobar
la versión, el entorno y el plan (reconstruido en <S>/reanudaciones/<k>). Se reutiliza una llamada aceptada si su salida conserva esas
huellas y todo lo que la precede se reutiliza también. Las demás se repiten con la misma orden y el mismo límite: las que quedaron a medias,
las rechazadas y las de insumos cambiados. Lo que dejaron va a <S>/intentos/<k>."""
import contextlib
import hashlib
import heapq
import io
import json
import math
import os
import platform
import re
import shlex
import signal
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parents[1]
FLAGS = ("-B", "-P", "-s", "-X", "utf8")
ENTORNO = {"PYTHONHASHSEED": "0", "TZ": "UTC", **{v: "1" for v in ("BLIS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "OMP_NUM_THREADS",
                                                                    "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}}
LIMITE_ORDINARIO_S = 600.0      # pasos sin cálculo científico (recetas, comprobar, validar, comparar, regenerar)
MAX_PROCESOS_FAM01 = 12         # llamadas de FAM01 simultáneas como máximo (ensayo de concurrencia de 48 unidades, 2026-11-19)
PARALELIZABLES = ("FAM01",)     # familias cuyas llamadas pueden correr a la vez con procesos_fam01 > 1
SONDEO_S = 0.5
REGLA_REANUDACION = "REANUDACION-PASO3-v1"
# Lo que una reanudación no aparta: el control de la corrida, el plan, las recetas, los intentos y las reconstrucciones del plan
# (registro/ se recorre: quedan los de las recetas y los de las llamadas reutilizadas).
CONTROL_DE_LA_CORRIDA = ("plan.json", "recetas", "control.json", "estado_llamadas.jsonl", "ejecucion.lock", "ejecutor.json", "en_curso.json",
                         "intentos", "reanudaciones")
ORDEN_FAMILIAS = ("FAM01", "FAM02", "FAM03", "FAM04", "FAM05", "FAM06", "FAM07", "FAM08", "FAM11", "FAM12", "FAM09", "FAM10", "FAM13", "FAM14")
SIN_RECETA = ("FAM12",)
TIPOS = {"RN": "numérica", "RD": "regeneración", "VI": "integridad"}
ESPERADO = {"claves": 39, "RN": 17, "RD": 12, "VI": 10}  # F13-HISTORICAS pasó de RD a VI (L-F13-VALIDADOR-REM191, decisión del autor, 2026-11-18)

# llamadas que el catálogo nombra y ninguna receta lista (la clave queda ligada a ellas; su comando debe figurar en comando_base_limpia)
DEL_CATALOGO = {
    "FAM01": [(["fam01-listas", "--salida", "{S}/fam01/listas.json"], "F01-R3-MARCO")],
    "FAM02": [(["fam02-comprobar", "--salida", "{S}/fam02/comprobar.json"], "F02-R1")],
    "FAM12": [(["p7-suplemento", "--salida", "{S}/fam12/p7_suplemento.json"], "F12-P7-G"),
              (["q-local", "--salida", "{S}/fam12/q_local"], "F12-QLOCAL")]}
SUBSUMIDAS = {"F12-P7-K1": ("p7-k1", "p7-suplemento",
                            "p7-suplemento recalcula los cuatro K1 con derivar_k1 y los compara en binary64 exacto antes de generar las siete filas "
                            "(reproducir.py: p7_suplemento -> p7_k1); p7-k1 no se lanza aparte para no repetir el cálculo")}

# ligadura llamada -> clave del catálogo (validar, comparar y recuperar heredan la clave del productor que consumen)
DIRECTAS = {"fam01-listas": ("F01-R3-MARCO",), "fam06-unidad": ("F06-MALLAS",), "fam06-conciliar": ("F06-CONCILIACION",),
            "fam07-unidad": ("F07-RECALCULO",), "fam07-ensamblar": ("F07-RECALCULO", "F07-REUTILIZADAS"),
            "fam07-comprobar": ("F07-PREVIAS-192", "F07-REUTILIZADAS"), "fam08-conciliar": ("F08-PARES",), "fam08-integrar": ("F08-INTEGRAL",),
            "fam10-tabla": ("F10-ENF-AFIRMACION", "F10-SINTESIS", "F10-INTEGRACION"), "fam11-ensamblar": ("F11-COV26",),
            "p7-suplemento": ("F12-P7-K1", "F12-P7-G"), "q-local": ("F12-QLOCAL",), "fam13-reproducir": ("F13-HISTORICAS", "F13-S1"),
            "fam14-reproducir": ("F14-GN-REGEN", "F14-GN", "F14-187", "F14-176")}
POR_TAREA = {"fam05-unidad": {"L1-ELAST": ("F05-ELAST-C0", "F05-ELAST-HIST"), "L1-LAMBDA": ("F05-LAMBDA",)},
             "fam08-unidad": {"L1-ELAST": ("F08-MALLAS",), **{"ABL-ENF-T%d" % i: ("F08-TECHOS",) for i in range(1, 7)}},
             "fam09-etapa": {"HIST": ("F09-HIST",), "LAMBDA": ("F09-LAMBDA",), "CAPTURA": ("F09-CAPTURA",), "TESTIGO": ("F09-TESTIGO",),
                             "INCORPORACION": ("F09-TESTIGO",), "C5B": ("F09-C5B",)},
             "fam11-unidad": {**{"ABL-COV-T%d" % i: ("F11-COV26",) for i in range(1, 7)}, "B1": ("F11-B1",), "B2": ("F11-B2",)}}
POR_FAMILIA_FAM03 = {"PROD1": "F03-QUIEBRES", "PROD2": "F03-QUIEBRES", "PROD3": "F03-Q"}
CONSUMIDAS = ("--nueva", "--validacion", "--b1", "--validacion-b1", "--e4", "--lote2", "--validacion-e4", "--validacion-lote2")

# fam10-tabla: cada entrada de la receta se cablea a la llamada que la produce en esta ejecución (y el texto de la receta debe nombrarla)
CABLEADO = {"enf_integral": ("fam08-integrar", None, "fam08-integrar"), "registro_enf_integral": ("fam08-comparar", "INTEGRAL", "fam08-comparar INTEGRAL"),
            "cov": ("fam11-ensamblar", None, "fam11-ensamblar"), "registro_cov": ("fam11-comparar", "ENSAMBLADO", "fam11-comparar ENSAMBLADO"),
            "p7": ("p7-suplemento", None, "p7-suplemento"), "q_local": ("q-local", None, "q-local"),
            "b1": ("fam11-unidad", "B1", "fam11-unidad B1"), "validacion_b1": ("fam11-validar", "B1", "fam11-validar"),
            "b2": ("fam11-unidad", "B2", "fam11-unidad B2"), "validacion_b2": ("fam11-validar", "B2", "fam11-validar")}

# ENTRADA-GUARDADA-PILOTO-v1: en el piloto, el integral ENF y el ensamblado COV toman las tareas guardadas que sus recetas admiten
GUARDABLES = {"fam08-integrar": {"mallas"} | {"ABL-ENF-T%d" % i for i in range(1, 7)}, "fam11-ensamblar": {"ABL-COV-T%d" % i for i in range(1, 7)}}
QUITABLES = {"fam08-integrar": {"certificado": "sin entrada: con la T1 guardada vale su certificado guardado (como regeneracion_02 de FAM08)"}}
PROCEDENCIA_GUARDADA = {"fam08-integrar": "salidas aceptadas rem127 (T1) y rem128 (T2–T6) y producto de mallas aceptado, guardados en datos/fam08 "
                                          "(autenticados por el manifiesto integral)",
                        "fam11-ensamblar": "seis tareas aceptadas rem151 guardadas en datos/fam11 (autenticadas por su manifiesto)"}

HISTORICOS_FIJOS = {
    "FAM01": ["listas R2 (1.740 testigos) y R3 (27 de un marco de 536) fijadas por la selección S6 sellada; núcleo S6, D7 y contratos de "
              "la instalación, en copia exacta o saneada (fuentes_fam01.json)"],
    "FAM09": ["piezas T8 copiadas en nucleo_s6/t8 y datos/fam09 (fuentes_fam09.json): filas preservadas del anexo (HIST) y entradas de λ, "
              "captura y testigo; cada etapa consume la salida nueva validada de la anterior"],
    "FAM10": ["resúmenes de los libros rem148/rem161/rem171 (datos/fam10/autoridad) y U41/U44/U47 del paquete; ENF, COV, P7, Q y B1/B2 "
              "llegan de las llamadas de FAM08, FAM11 y FAM12 de esta ejecución, cada una con su registro aceptado"],
    "FAM12": ["entradas ligadas guardadas de los cuatro K1 (datos/p7.json y datos/p7_k1_reutilizados.json)",
              "techos COV/ENF aceptados de las siete afirmaciones (datos/p7_suplemento.json; no se recalculan)",
              "posiciones Q guardadas (datos/q_local.jsonl; aritmética exacta sobre ellas)"]}
COMPARACION_DE = {"FAM01": "comparador histórico, limpio y limpio con F2 (F2-ENTORNO-PORTABLE-v1, adoptada solo para FAM01)",
                  "FAM02": "igualdad exacta con la referencia (IGUALDAD-R1F-TIEMPOS-v1 solo en R1-F)", "FAM03": "COMPARACION-FAM03-v1",
                  "FAM04": "COMPARACION-FAM04-v1", "FAM05": "COMPARACION-FAM05-v1 (+ VINCULO-PROCEDENCIA-v1)",
                  "FAM06": "COMPARACION-FAM06-MALLAS-v1 / COMPARACION-FAM06-CONCILIACION-v1", "FAM07": "COMPARACION-FAM07-v1",
                  "FAM08": "COMPARACION-FAM08-v1", "FAM09": "comparación por etapa con rem138/rem140/rem141/rem147 (fam09-comparar)",
                  "FAM10": "COMPARACION-FAM10-v1", "FAM11": "COMPARACION-FAM11-v1",
                  "FAM12": "binary64 exacta (K1) e identidad de filas y bytes con la referencia (suplemento y Q)", "FAM13": "COMPARACION-FAM13-v1",
                  "FAM14": "COMPARACION-FAM14-v1"}


class ErrorGeneral(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise ErrorGeneral(msg)


def sha_archivo(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _escribir(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")


def _opt(argv, nombre):
    return next((argv[i + 1] for i in range(1, len(argv) - 1) if argv[i] == nombre), None)


def _entradas(argv):
    return [tuple(argv[i + 1].partition("=")[::2]) for i in range(1, len(argv) - 1) if argv[i] == "--entrada"]


def _consumidas(argv):
    """(opción, ruta) de cada entrada que la llamada lee de otra llamada; «guardado» queda aparte (insumo histórico del paquete)."""
    out = [(o, argv[i + 1]) for i in range(1, len(argv) - 1) for o in CONSUMIDAS if argv[i] == o]
    return out + [("--entrada " + k, v) for k, v in _entradas(argv) if v != "guardado"]


def _orden(argv):
    return " ".join(argv)


# ------------------------------------------------------------------------------------------------ supervisión de cada llamada

def _terminar_arbol(pr):
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pr.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(pr.pid, signal.SIGKILL)
    pr.wait()


def _iniciar(argv, fo, fe):
    """El proceso de una llamada de reproducir.py: desde la base, con el intérprete y las opciones de esta invocación y el entorno del perfil."""
    orden = [sys.executable, *FLAGS, str(BASE / "reproducir.py"), *argv]
    kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    return subprocess.Popen(orden, cwd=BASE, env=dict(os.environ, **ENTORNO), stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, **kw)


def lanzar(argv, limite_s, registro: Path) -> dict:
    """Una llamada de reproducir.py en su proceso, desde la base, con el entorno del perfil y el límite externo; al agotarlo, árbol terminado."""
    t0 = time.time()
    with open(registro.with_suffix(".out"), "xb") as fo, open(registro.with_suffix(".err"), "xb") as fe:
        pr = _iniciar(argv, fo, fe)
        _seguir("alta", registro.name, pr)
        try:
            rc, vencido = pr.wait(timeout=limite_s), False
        except subprocess.TimeoutExpired:
            _terminar_arbol(pr)
            rc, vencido = None, True
        except BaseException:
            _terminar_arbol(pr)
            raise
        finally:
            _seguir("baja", registro.name)
    return {"rc": rc, "limite_agotado": vencido, "segundos": round(time.time() - t0, 3)}


# Durante ejecutar() con diario: <S>/en_curso.json con el pid y el instante de creación del proceso de cada llamada en curso, para que una
# reanudación termine los que el ejecutor anterior dejó vivos.
_SEGUIDOR = None


def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _reemplazar(p: Path, obj) -> bool:
    """Escritura atómica de un JSON de control (archivo temporal, fsync y os.replace; reintenta si otro proceso lo tiene abierto)."""
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    for _ in range(40):
        try:
            os.replace(tmp, p)
            return True
        except PermissionError:
            time.sleep(0.25)
    return False


def _creacion_proceso(pid: int):
    """Instante de creación del proceso pid si sigue vivo (distingue un pid reutilizado por otro proceso), o None."""
    if os.name != "nt":
        try:
            return Path("/proc/%d/stat" % pid).read_text().rsplit(")", 1)[1].split()[19]
        except (OSError, IndexError):
            return None
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    k32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        codigo = wintypes.DWORD()
        if not k32.GetExitCodeProcess(h, ctypes.byref(codigo)) or codigo.value != 259:  # STILL_ACTIVE
            return None
        t = [wintypes.FILETIME() for _ in range(4)]
        if not k32.GetProcessTimes(h, *(ctypes.byref(x) for x in t)):
            return None
        return str((t[0].dwHighDateTime << 32) | t[0].dwLowDateTime)
    finally:
        k32.CloseHandle(h)


class _Seguidor:
    def __init__(self, ruta: Path):
        self.ruta, self.procesos = ruta, {}
        self._guardar()

    def _guardar(self):
        if not _reemplazar(self.ruta, self.procesos):
            print("aviso: no se pudo actualizar %s" % self.ruta.name, file=sys.stderr)

    def alta(self, ident, pr):
        self.procesos[ident] = {"pid": pr.pid, "creacion": _creacion_proceso(pr.pid), "desde_utc": _utc()}
        self._guardar()

    def baja(self, ident):
        if self.procesos.pop(ident, None) is not None:
            self._guardar()


def _seguir(accion, *a):
    if _SEGUIDOR is not None:
        getattr(_SEGUIDOR, accion)(*a)


# ------------------------------------------------------------------------------------------------ plan: recetas -> llamadas

def _reubicar(texto: str, S: str) -> str:
    """salidas/famXX/<ejecucion> -> <S>/famXX; salidas/famXX/<nuevo> -> <S>/famXX/comprobar; salidas/famXX/ -> <S>/famXX/."""
    return re.sub(r"salidas/(fam\d\d)/(<ejecucion>|<nuevo>)?",
                  lambda m: "%s/%s%s" % (S, m.group(1), {"<ejecucion>": "", "<nuevo>": "/comprobar", None: "/"}[m.group(2)]), texto)


def _ordenes(receta: dict):
    """(paso de la receta, orden) en el orden de la receta: «previo», luego «pasos» o «tareas». Se omiten las formas declaradas equivalentes."""
    for o in receta.get("previo") or []:
        yield {"paso": "previo"}, o
    for clave in ("pasos", "tareas"):
        for p in receta.get(clave) or []:
            if "equivalente" in str(p.get("paso", "")):
                continue
            for o in ([p["orden"]] if "orden" in p else []) + list(p.get("ordenes") or []):
                yield p, o


def _meta(p: dict) -> dict:
    return {k: p[k] for k in ("paso", "tarea", "regla", "seleccion", "unidad", "unidades", "clave_estructural", "limite_externo_s", "familia",
                              "operacion", "depende_de", "consume_en_la_ejecucion") if k in p}


def _pasos_de_receta(fam: str, receta: dict, S: str) -> list:
    out = []
    for p, orden in _ordenes(receta):
        texto, limite_supervisor = None, None
        if isinstance(orden, list):
            argv = [_reubicar(a, S) for a in orden]
        else:
            texto = orden
            if "reproducir.py " not in orden:
                continue                                     # texto explicativo de la receta, no una orden
            cola = orden[orden.rfind("reproducir.py ") + len("reproducir.py "):]
            m = re.search(r"<supervisar\.py[^>]*>\s+\S+\s+(\d+)\s", orden)
            limite_supervisor = float(m.group(1)) if m else None
            if cola.startswith("fam10-tabla "):
                claves = re.findall(r"--entrada (\w+)=<([^>]*)>", cola)
                sal = re.search(r"--salida (\S+)\s*$", cola)
                need(sal and claves, "TABLA_ILEGIBLE_EN_LA_RECETA")
                argv = ["fam10-tabla"] + [x for k, _ in claves for x in ("--entrada", "%s=@%s" % (k, k))] + ["--salida", _reubicar(sal.group(1), S)]
                p = dict(p, cableado=dict(claves))
            else:
                cola = re.sub(r"\s+\([^()]*\)\s*$", "", cola)       # comentario final entre paréntesis
                argv = [_reubicar(a, S) for a in shlex.split(cola)]
        need(not any(re.search(r"[<>…]|\.\.\.", a) for a in argv if "=@" not in a), "ORDEN_CON_MARCADORES_SIN_RESOLVER: %s %s" % (fam, argv))
        out.append({"familia": fam, "argv": argv, "meta": _meta(p), "cableado": p.get("cableado"), "origen": "%s-receta" % fam.lower(),
                    "limite_supervisor": limite_supervisor, "limite_declarado": p.get("limite_externo_s")})
    return out


def _limite(fam: str, argv: list, receta: dict, limite_supervisor, limite_declarado=None) -> float:
    """Límite externo de la receta para los cálculos (el que declara la tarea, si lo declara); LIMITE_ORDINARIO_S para el resto."""
    c, t = argv[0], _opt(argv, "--tarea")
    if limite_supervisor is not None:
        return limite_supervisor
    if not c.endswith("-unidad"):
        return LIMITE_ORDINARIO_S
    if limite_declarado is not None:
        return float(limite_declarado)
    ej = receta.get("ejecucion") or {}
    if c == "fam11-unidad" and t in ("B1", "B2"):
        return float(ej["limite_externo_B_s"])
    for k in ("limite_externo_por_tarea_s", "tope_trabajo_s"):
        if k in ej:
            return float(ej[k])
    cond = " ".join(receta.get("condiciones") or [])
    m = re.search(r"piloto: (\d+) s por unidad", cond) or re.search(r"límite ordinario de ([\d.]+) s por tarea", cond)
    need(m, "LIMITE_NO_DECLARADO_EN_LA_RECETA: %s %s" % (fam, c))
    return float(m.group(1).replace(".", ""))


def _papeles(c: str, t) -> list:
    if c in ("fam01-listas", "fam07-comprobar"):
        return ["comprobacion_previa", "verificacion_integridad"]
    if c.endswith("-comprobar") or c == "fam09-listar":
        return ["comprobacion_previa"]
    if c in ("fam01-unidad", "fam02-unidad", "fam03-unidad"):
        return ["calculo", "validacion"]
    if c.endswith("-unidad"):
        return ["calculo"]
    if c == "fam09-etapa":
        return ["calculo"] if t == "TESTIGO" else (["verificacion_integridad"] if t == "HIST" else ["regeneracion"])
    if c.endswith("-validar"):
        return ["validacion"]
    if c.endswith("-comparar"):
        return ["comparacion"]
    if c == "fam01-na":
        return ["verificacion_integridad"]
    if c == "p7-suplemento":
        return ["calculo", "regeneracion", "comparacion"]
    if c == "q-local":
        return ["regeneracion", "comparacion"]
    if c == "fam10-tabla":
        return ["regeneracion", "validacion", "comparacion"]
    if c in ("fam13-reproducir", "fam14-reproducir"):
        return ["regeneracion", "verificacion_integridad", "validacion", "comparacion"]
    if c in ("fam06-conciliar", "fam07-ensamblar", "fam08-conciliar", "fam08-recuperar", "fam08-integrar", "fam11-ensamblar"):
        return ["regeneracion"]
    raise ErrorGeneral("PAPEL_DESCONOCIDO: %s" % c)


def _productor(ruta: str, prod: dict):
    p = PurePosixPath(ruta)
    for q in (p, *p.parents):
        if str(q) in prod:
            return prod[str(q)]
    return None


def _datos(pasos: list, S: str) -> list:
    """produce/consume por índice; devuelve los errores de cobertura de datos."""
    errores, prod = [], {}
    for i, p in enumerate(pasos):
        s = p["produce"] = _opt(p["argv"], "--salida")
        if s is None:
            errores.append("LLAMADA_SIN_SALIDA: %s" % _orden(p["argv"]))
            continue
        if s in prod:
            errores.append("SALIDA_REPETIDA: %s" % s)
        if not s.startswith(S + "/"):
            errores.append("SALIDA_FUERA_DE_LA_EJECUCION: %s" % s)
        prod[s] = i
    comparadores = {}
    for i, p in enumerate(pasos):
        if p["argv"][0].endswith("-comparar"):
            comparadores.setdefault(_opt(p["argv"], "--nueva"), []).append(i)
    for i, p in enumerate(pasos):
        p["_consume"] = []
        p["_comparaciones_previas"] = set()
        for o, ruta in _consumidas(p["argv"]):
            j = _productor(ruta, prod)
            if j is None or not ruta.startswith(S + "/"):
                errores.append("ENTRADA_SIN_PRODUCTOR_EN_ESTA_EJECUCION: %s %s (%s)" % (o, ruta, _orden(p["argv"])))
            elif j == i:
                errores.append("LLAMADA_QUE_SE_CONSUME_A_SI_MISMA: %s" % _orden(p["argv"]))
            else:
                p["_consume"].append({"opcion": o, "ruta": ruta, "_productor": j})
                # La validación, la recuperación T1 y la comparación producen la propia evidencia.
                # Un consumidor científico posterior sí espera también la comparación del producto.
                if not p["argv"][0].endswith(("-validar", "-recuperar", "-comparar")):
                    p["_comparaciones_previas"].update(comparadores.get(pasos[j]["produce"], ()))
        p["_historicas"] = [{"entrada": k, "valor": v} for k, v in _entradas(p["argv"]) if v == "guardado"]
    return errores


def _llamada_real(parser, argv) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            a = parser.parse_args(argv)
        return a.comando == argv[0]
    except SystemExit:
        return False


def construir(S: str, parser, registro: Path) -> dict:
    """Plan de las 39 claves: recetas lanzadas (sin cálculo) -> llamadas reubicadas, deduplicadas, cableadas, ordenadas por datos y ligadas."""
    t0 = time.time()
    cat = json.loads((BASE / "catalogo.json").read_text(encoding="utf-8"))["operaciones"]
    claves = {o["clave"]: o for o in cat}
    recetas, lanzadas = {}, {}
    for fam in ORDEN_FAMILIAS:
        if fam in SIN_RECETA:
            continue
        destino = "%s/recetas/%s.json" % (S, fam.lower())
        argv = [fam.lower() + "-receta", "--salida", destino]
        r = lanzar(argv, LIMITE_ORDINARIO_S, registro / ("receta_" + fam.lower()))
        lanzadas[fam] = {"orden": _orden(argv), **r}
        need(r["rc"] == 0 and (BASE / destino).is_file(), "RECETA_FALLIDA: %s (rc %s)" % (fam, r["rc"]))
        recetas[fam] = json.loads((BASE / destino).read_text(encoding="utf-8"))
    crudos = []
    for fam in ORDEN_FAMILIAS:
        crudos += _pasos_de_receta(fam, recetas[fam], S) if fam in recetas else []
        for argv, clave in DEL_CATALOGO.get(fam, []):
            need(argv[0] in claves[clave]["comando_base_limpia"], "LLAMADA_DEL_CATALOGO_NO_NOMBRADA: %s %s" % (clave, argv[0]))
            crudos.append({"familia": fam, "argv": [a.replace("{S}", S) for a in argv], "meta": {"paso": "catálogo"}, "cableado": None,
                           "origen": "catalogo.json (%s, comando_base_limpia)" % clave, "limite_supervisor": None})
    for clave, (nombrado, llamada, _) in SUBSUMIDAS.items():
        need(nombrado in claves[clave]["comando_base_limpia"] and any(a[0] == llamada for v in DEL_CATALOGO.values() for a, _ in v),
             "SUBSUMIDA_NO_NOMBRADA_O_SIN_LLAMADA: %s" % clave)
    # misma llamada en dos recetas (FAM06 lista el lado de origen de FAM05): se lanza una vez
    pasos, vistos, reutilizadas = [], {}, []
    for p in crudos:
        k = tuple(p["argv"])
        if k in vistos:
            reutilizadas.append({"familia": p["familia"], "orden": _orden(p["argv"]), "es_la_llamada_de": pasos[vistos[k]]["familia"]})
            pasos[vistos[k]].setdefault("tambien_en", []).append(p["familia"])
            continue
        vistos[k] = len(pasos)
        pasos.append(p)
    # cableado de fam10-tabla
    def unico(c, t):
        cand = [p for p in pasos if p["argv"][0] == c and (t is None or _opt(p["argv"], "--tarea") == t)]
        need(len(cand) == 1, "CABLEADO_AMBIGUO_O_AUSENTE: %s %s" % (c, t))
        return cand[0]
    for p in pasos:
        if p["argv"][0] != "fam10-tabla":
            continue
        need(set(p["cableado"]) == set(CABLEADO), "TABLA_CON_ENTRADAS_DISTINTAS_DE_LA_RECETA: %s" % sorted(p["cableado"]))
        for k, (c, t, nombre) in CABLEADO.items():
            need(all(x in p["cableado"][k] for x in nombre.split()), "LA_RECETA_NO_NOMBRA_EL_PRODUCTOR: %s -> %s" % (k, nombre))
            if c == "fam11-validar":
                b = unico("fam11-unidad", t)["argv"]
                v = [q for q in pasos if q["argv"][0] == "fam11-validar" and _opt(q["argv"], "--nueva") == _opt(b, "--salida")]
                need(len(v) == 1, "CABLEADO_AMBIGUO_O_AUSENTE: validación de %s" % t)
                ruta = _opt(v[0]["argv"], "--salida")
            else:
                ruta = _opt(unico(c, t)["argv"], "--salida")
            p["argv"] = [a.replace("@" + k, ruta) if a == "%s=@%s" % (k, k) else a for a in p["argv"]]
    errores = _datos(pasos, S)
    # dependencias estructurales: comprobación previa de la familia, parada secuencial declarada, depende_de de FAM02
    por_fam = {}
    for i, p in enumerate(pasos):
        p["papeles"] = _papeles(p["argv"][0], _opt(p["argv"], "--tarea"))
        p["previo"] = "comprobacion_previa" in p["papeles"]
        por_fam.setdefault(p["familia"], []).append(i)
    for fam, idx in por_fam.items():
        receta = recetas.get(fam, {})
        previos = [i for i in idx if pasos[i]["previo"]]
        secuencial = bool(re.search(r"siguiente no se lanza", str((receta.get("ejecucion") or {}).get("parada", ""))))
        anterior = None
        tareas_fam02 = {}
        for i in idx:
            p = pasos[i]
            p["_estructurales"] = set()
            if not p["previo"]:
                p["_estructurales"] |= set(previos)
                if secuencial and anterior is not None:
                    p["_estructurales"].add(anterior)
                anterior = i
            if fam == "FAM02" and "tarea" in p["meta"]:
                tareas_fam02.setdefault(p["meta"]["tarea"], []).append(i)
        if fam == "FAM02":
            for i in idx:
                meta = pasos[i]["meta"]
                for d in meta.get("consume_en_la_ejecucion", []):
                    need(d in tareas_fam02, "TAREA_DE_ENTRADA_NO_LOCALIZADA: %s" % d)
                for d in set(meta.get("depende_de", [])) | set(meta.get("consume_en_la_ejecucion", [])):
                    pasos[i]["_estructurales"] |= set(tareas_fam02.get(d, []))
                pasos[i]["prerrequisitos_externos"] = [d for d in pasos[i]["meta"].get("depende_de") or [] if d not in tareas_fam02]
        p_sec = "parada secuencial de la receta" if secuencial else None
        for i in idx:
            pasos[i]["parada"] = p_sec
    # orden por datos (Kahn estable por índice) e identificadores
    deps = [{c["_productor"] for c in p["_consume"]} | p["_estructurales"] | p["_comparaciones_previas"] for p in pasos]
    pendientes = [len(d) for d in deps]
    hijos = [[] for _ in pasos]
    for i, d in enumerate(deps):
        for j in d:
            hijos[j].append(i)
    listos = [i for i, n in enumerate(pendientes) if n == 0]
    heapq.heapify(listos)
    orden = []
    while listos:
        i = heapq.heappop(listos)
        orden.append(i)
        for h in hijos[i]:
            pendientes[h] -= 1
            if pendientes[h] == 0:
                heapq.heappush(listos, h)
    if len(orden) != len(pasos):
        errores.append("CICLO_DE_DEPENDENCIAS")
        orden += [i for i in range(len(pasos)) if i not in set(orden)]
    ids = {i: "P%05d" % (n + 1) for n, i in enumerate(orden)}
    completo = []
    for i in orden:
        p = pasos[i]
        receta = recetas.get(p["familia"], {})
        completo.append({
            "id": ids[i], "familia": p["familia"], "tambien_en": p.get("tambien_en", []), "origen": p["origen"], "meta": p["meta"],
            "argv": p["argv"], "orden": _orden(p["argv"]), "papeles": p["papeles"], "previo": p["previo"], "produce": p["produce"],
            "consume": [{"opcion": c["opcion"], "ruta": c["ruta"], "de": ids[c["_productor"]]} for c in p["_consume"]],
            "historicas": p["_historicas"], "depende_de": sorted(ids[j] for j in deps[i]),
            "dependencias_estructurales": sorted(ids[j] for j in p["_estructurales"]),
            "prerrequisitos_externos": p.get("prerrequisitos_externos", []), "parada": p.get("parada"),
            "limite_s": _limite(p["familia"], p["argv"], receta, p["limite_supervisor"], p.get("limite_declarado")),
            "supervision": "proceso propio; límite externo; al agotarlo se termina el árbol de procesos"})
    # claves del catálogo (las heredadas, después de sus productores)
    por_id = {p["id"]: p for p in completo}
    for p in completo:
        c, t = p["argv"][0], _opt(p["argv"], "--tarea")
        if c in DIRECTAS:
            k = DIRECTAS[c]
        elif c in POR_TAREA:
            k = POR_TAREA[c].get(t, ())
        elif c in ("fam01-unidad", "fam01-comparar"):
            k = ("F01-" + _opt(p["argv"], "--seleccion"),)
        elif c == "fam01-na":
            k = ("F01-" + p["meta"]["seleccion"],)
        elif c.startswith("fam02-") and not p["meta"].get("paso") == "catálogo":
            k = ("F02-R1",)
        elif c in ("fam03-unidad", "fam03-comparar"):
            k = (POR_FAMILIA_FAM03[p["meta"]["familia"]],)
        elif c.startswith("fam04-") and not p["previo"]:
            k = ("F04-LOTE1",)
        elif c.endswith(("-validar", "-comparar")) or c == "fam08-recuperar":
            k = tuple(sorted({x for d in p["consume"] for x in por_id[d["de"]]["claves"]}))
        else:
            k = ()
        p["claves"] = list(k)
        if not k and not p["previo"]:
            errores.append("LLAMADA_SIN_CLAVE: %s" % p["orden"])
        errores += ["CLAVE_FUERA_DEL_CATALOGO: %s" % x for x in k if x not in claves]
    # quién queda bloqueado si una llamada falta o es rechazada
    hijos_id = {p["id"]: [] for p in completo}
    for p in completo:
        for d in p["depende_de"]:
            hijos_id[d].append(p["id"])
    for p in reversed(completo):
        bloq = set()
        for h in hijos_id[p["id"]]:
            bloq |= {h} | por_id[h]["_bloquea"]
        p["_bloquea"] = bloq
    for p in completo:
        b = p.pop("_bloquea")
        p["si_falta_o_se_rechaza_bloquea"] = {"llamadas": len(b), "claves": sorted({k for x in b for k in por_id[x]["claves"]} - set(p["claves"]))}
    piloto, sustituciones, err_piloto = _piloto(completo, S)
    comprobaciones = _comprobar(completo, piloto, claves, parser, errores + err_piloto, S)
    return {"carpeta": S, "recetas": lanzadas, "llamadas_reutilizadas_entre_recetas": reutilizadas,
            "subsumidas": {k: {"nombrada": n, "la_cubre": c, "motivo": m} for k, (n, c, m) in SUBSUMIDAS.items()},
            "insumos_historicos": {fam: _historicos(fam, recetas.get(fam, {})) for fam in ORDEN_FAMILIAS},
            "comprobaciones": comprobaciones, "cumple": comprobaciones["cumple"],
            "modos": {"completo": {"pasos": completo},
                      "piloto": {"regla": "ENTRADA-GUARDADA-PILOTO-v1", "sustituciones": sustituciones, "pasos": piloto}},
            "claves": {k: _ficha(k, claves[k], completo, piloto) for k in claves}, "segundos": round(time.time() - t0, 3)}


def _historicos(fam, receta):
    f1 = receta.get("F1") or {}
    for k in ("reutilizado", "reutilizable"):
        if k in f1:
            return list(f1[k]) + list(f1.get("verificado_aparte") or [])
    if "reutilizable_segun_F1" in receta:
        return receta["reutilizable_segun_F1"]
    if fam in HISTORICOS_FIJOS:
        return HISTORICOS_FIJOS[fam]
    return [receta["nota"]] if "nota" in receta else []


def _piloto(completo, S):
    """Mismas llamadas; el integral ENF y el ensamblado COV con sus tareas guardadas; selección: lo que necesita fam10-tabla y las
    comparaciones de lo seleccionado."""
    por_id = {p["id"]: p for p in completo}
    copia, sust = [], []
    prod = {p["produce"]: p["id"] for p in completo}
    for p in completo:
        q = dict(p, argv=list(p["argv"]))
        c = p["argv"][0]
        if c in GUARDABLES:
            argv, i = [c], 1
            while i < len(p["argv"]):
                a = p["argv"][i]
                if a == "--entrada":
                    k, _, v = p["argv"][i + 1].partition("=")
                    if k in GUARDABLES[c] or k in QUITABLES.get(c, {}):
                        de = _productor(v, prod)
                        sust.append({"llamada": p["id"], "entrada": k, "en_el_plan_completo": v, "producida_en_el_plan_completo_por": de,
                                     "en_el_piloto": "guardado" if k in GUARDABLES[c] else QUITABLES[c][k],
                                     "procedencia_historica": PROCEDENCIA_GUARDADA[c] if k in GUARDABLES[c] else None})
                        if k in GUARDABLES[c]:
                            argv += ["--entrada", k + "=guardado"]
                        i += 2
                        continue
                argv.append(a)
                i += 1
            q["argv"], q["orden"] = argv, _orden(argv)
        copia.append(q)
    errores = _datos(copia, S)
    idx = {p["id"]: n for n, p in enumerate(copia)}
    for p in copia:
        estructurales = set(por_id[p["id"]]["dependencias_estructurales"])
        p["consume"] = [{"opcion": c["opcion"], "ruta": c["ruta"], "de": copia[c["_productor"]]["id"]} for c in p.pop("_consume")]
        p["historicas"] = p.pop("_historicas")
        for h in p["historicas"]:
            h["procedencia"] = PROCEDENCIA_GUARDADA.get(p["argv"][0])
        comparaciones = {copia[i]["id"] for i in p.pop("_comparaciones_previas")}
        p["depende_de"] = sorted(estructurales | comparaciones | {c["de"] for c in p["consume"]})
    tabla = [p for p in copia if p["argv"][0] == "fam10-tabla"]
    if len(tabla) != 1:
        return [], sust, errores + ["TABLA_AUSENTE_O_REPETIDA"]
    sel, pila = set(), [tabla[0]["id"]]
    while pila:
        x = pila.pop()
        if x not in sel:
            sel.add(x)
            pila += copia[idx[x]]["depende_de"]
    for p in copia:                        # comparaciones de lo seleccionado, si todo lo que necesitan está seleccionado
        if "comparacion" in p["papeles"] and p["id"] not in sel and p["consume"] and set(p["depende_de"]) <= sel:
            sel.add(p["id"])
    return [p for p in copia if p["id"] in sel], sust, errores


def _comprobar(completo, piloto, claves, parser, errores, S) -> dict:
    tipos = Counter(o["operacion"] for o in claves.values())
    sin_llamada = [k for k in claves if not any(k in p["claves"] for p in completo)]
    sin_comp = [k for k in claves if not any(k in p["claves"] and {"comparacion", "verificacion_integridad"} & set(p["papeles"]) for p in completo)]
    malas = sorted({p["orden"] for p in completo + piloto if not _llamada_real(parser, p["argv"])})
    vistos, fuera_de_orden = set(), []
    for p in completo:
        if not set(p["depende_de"]) <= vistos:
            fuera_de_orden.append(p["id"])
        vistos.add(p["id"])
    existentes = [p["produce"] for p in completo if p["produce"] and (BASE / p["produce"]).exists()]
    fuera = [c["ruta"] for p in completo + piloto for c in p["consume"] if not c["ruta"].startswith(S + "/")]
    productos = sum(1 for o in claves.values() for x in o["productos"] if x["papel"] == "producto_aceptado")
    out = {"claves_del_catalogo": {"total": len(claves), "por_tipo": dict(tipos),
                                   "esperado": ESPERADO, "conforme": len(claves) == ESPERADO["claves"] and all(tipos[t] == ESPERADO[t] for t in TIPOS)},
           "claves_sin_llamada": sin_llamada, "claves_sin_comparacion_ni_verificacion": sin_comp,
           "llamadas": {"completo": len(completo), "piloto": len(piloto), "rechazadas_por_la_cli": malas[:20], "rechazadas_total": len(malas)},
           "orden_por_datos": {"conforme": not fuera_de_orden, "fuera_de_orden": fuera_de_orden[:20]},
           "entradas_fuera_de_esta_ejecucion": fuera[:20], "salidas_preexistentes": existentes[:20],
           "productos_aceptados_del_catalogo": productos, "errores": errores[:50], "errores_total": len(errores)}
    out["cumple"] = (out["claves_del_catalogo"]["conforme"] and not sin_llamada and not sin_comp and not malas and not fuera_de_orden
                     and not fuera and not existentes and not errores and bool(piloto))
    return out


def _ficha(k, o, completo, piloto):
    """Clave del catálogo -> llamadas, comparación de sus productos, insumos históricos y lo documentado (criterios y límites)."""
    mias = [p for p in completo if k in p["claves"]]
    comp = [p["id"] for p in mias if {"comparacion", "verificacion_integridad"} & set(p["papeles"])]
    pil = [p["id"] for p in piloto if k in p["claves"]]
    return {"familia": o["familia_id"], "tipo": o["operacion"], "naturaleza": TIPOS[o["operacion"]], "disponibilidad": o["disponibilidad"],
            "llamadas_completo": len(mias), "primeras_llamadas": [p["id"] for p in mias[:6]],
            "llamadas_de_calculo": sum(1 for p in mias if "calculo" in p["papeles"]),
            "comprobada_por": comp, "comprobaciones_total": len(comp), "regla": COMPARACION_DE[o["familia_id"]],
            "productos": [{"id": x["id"], "sha256_aceptado": x["sha256_aceptado"], "tipo": x["tipo"], "granularidad": x.get("granularidad"),
                           **({"comprobado_por": [p["id"] for p in mias if p["argv"][0] == "fam03-comparar" and _opt(p["argv"], "--tarea") == x["id"]]}
                              if o["familia_id"] == "FAM03" else {"comparaciones_de_la_clave": k})}
                          for x in o["productos"] if x["papel"] == "producto_aceptado"],
            "en_el_piloto": pil, "subsumida": SUBSUMIDAS.get(k, (None, None, None))[2],
            "documentado": {"estado_base_limpia": o["estado_base_limpia"], "limites": o["limites"], "residuos": o.get("residuos", [])}}


# ------------------------------------------------------------------------------------------------ ejecución

def _manifiesto(p: Path) -> dict:
    if p.is_file():
        return {".": sha_archivo(p)}
    return {f.relative_to(p).as_posix(): sha_archivo(f) for f in sorted(p.rglob("*")) if f.is_file()}


def _bajo(ruta: str, raiz: str, man: dict):
    """(huellas actuales, huellas registradas) de la parte `ruta` de la salida `raiz`, con claves relativas a la raíz."""
    p = BASE / ruta
    sub = PurePosixPath(ruta).relative_to(PurePosixPath(raiz)).as_posix()
    if sub == ".":
        return (_manifiesto(p) if p.exists() else {}), man
    act = {(sub if k == "." else sub + "/" + k): v for k, v in _manifiesto(p).items()} if p.exists() else {}
    return act, {k: v for k, v in man.items() if k == sub or k.startswith(sub + "/")}


def _entrada_intacta(ruta: str, raiz: str, man: dict):
    """La entrada existe y sus bytes son los que dejó la última llamada aceptada que la produjo o la escribió."""
    if not (BASE / ruta).exists():
        return "ENTRADA_AUSENTE: %s" % ruta
    act, esp = _bajo(ruta, raiz, man)
    return None if act == esp else "ENTRADA_ALTERADA_FUERA_DEL_PLAN: %s" % ruta


def _bloqueo(p, estado, por_id, huellas):
    """Motivo por el que la llamada no se lanza (dependencia no aceptada, entrada ausente o alterada), o None."""
    for d in p["depende_de"]:
        e = estado.get(d)
        if e is None or e["estado"] != "aceptado":
            return "PENDIENTE: depende de %s (%s)" % (d, e["estado"] if e else "no ejecutado")
    for c in p["consume"]:
        motivo = _entrada_intacta(c["ruta"], por_id[c["de"]]["produce"], huellas[c["de"]])
        if motivo:
            return "PENDIENTE: " + motivo + " (producida por %s)" % c["de"]
    return None


def _cierre(p, r, S, por_id, huellas, gancho):
    """Estado de una llamada terminada: código, límite, salida, lectura de la comparación o verificación y entradas intactas."""
    if gancho:
        gancho("tras_proceso", p, S)
    sal = BASE / p["produce"]
    if r["limite_agotado"]:
        est = "limite_agotado"
    elif r["rc"] != 0:
        est = "rechazado"
    elif not sal.exists():
        est = "salida_ausente"
    else:
        est = "aceptado"
        if {"comparacion", "verificacion_integridad"}.intersection(p["papeles"]):
            if not _resultado_aceptado(p, _lectura(p)):
                est = "informe_no_conforme"
    e = {"estado": est, **r}
    escritas = []
    for c in p["consume"]:
        raiz = por_id[c["de"]]["produce"]
        act, esp = _bajo(c["ruta"], raiz, huellas[c["de"]])
        if act != esp:
            escritas.append(c["ruta"])
            if est == "aceptado":
                # Una validación puede añadir su informe. Los bytes de entrada ya aceptados se conservan.
                if p["argv"][0].endswith("-validar") and c["opcion"] == "--nueva" and esp.items() <= act.items():
                    huellas[c["de"]].update(act)
                    e.setdefault("_actualiza", {})[c["de"]] = dict(huellas[c["de"]])  # al diario (anotar), no a ejecucion.jsonl
                else:
                    e.update(estado="entrada_modificada", motivo="La llamada modificó su entrada: " + c["ruta"])
    if escritas:
        e["escribio_en_sus_entradas"] = escritas
    if e["estado"] == "aceptado":
        huellas[p["id"]] = _manifiesto(sal)
    if gancho:
        gancho("tras_registro", p, S)
    return e


def ejecutar(plan: dict, modo: str, S: Path, gancho=None, limites=None, procesos_fam01: int = 1, diario=None, previo=None) -> dict:
    """Las llamadas del modo, en el orden del plan. gancho(momento, paso, S) y limites {id: s} solo los usan los controles locales.
    procesos_fam01 = 1 (por omisión): una llamada a la vez. Con N > 1: hasta N llamadas de FAM01 a la vez (_en_paralelo).
    diario (_Diario): cada llamada cerrada se anota también en <S>/estado_llamadas.jsonl, forzada a disco, y los procesos en curso en
    <S>/en_curso.json. previo = (estado, huellas) de las llamadas reutilizadas al reanudar: no se lanzan y abren ejecucion.jsonl."""
    global _SEGUIDOR
    need(isinstance(procesos_fam01, int) and 1 <= procesos_fam01 <= MAX_PROCESOS_FAM01, "PROCESOS_FAM01_FUERA_DE_1_A_%d" % MAX_PROCESOS_FAM01)
    pasos = plan["modos"][modo]["pasos"]
    por_id = {p["id"]: p for p in pasos}
    estado, huellas = ({}, {}) if previo is None else (dict(previo[0]), {i: dict(m) for i, m in previo[1].items()})
    with open(S / "ejecucion.jsonl", "x", encoding="utf-8", newline="\n") as log:
        def escribir(p, e):
            log.write(json.dumps({"id": p["id"], "orden": p["orden"], **e}, ensure_ascii=False) + "\n")
            log.flush()

        def anotar(p, e):
            actualiza = e.pop("_actualiza", None)
            estado[p["id"]] = e
            if diario is not None:
                ok = e["estado"] == "aceptado"
                diario.anotar({"tipo": "llamada", "id": p["id"], "orden": p["orden"], "e": e, "manifiesto": huellas.get(p["id"]) if ok else None,
                               "actualiza": (actualiza or {}) if ok else {}})
            escribir(p, e)
        for p in pasos:
            if p["id"] in estado:
                escribir(p, estado[p["id"]])
        pendientes = [p for p in pasos if p["id"] not in estado]
        _SEGUIDOR = _Seguidor(S / "en_curso.json") if diario is not None else None
        try:
            if procesos_fam01 > 1:
                _en_paralelo(pendientes, S, por_id, estado, huellas, anotar, gancho, limites, procesos_fam01)
                return estado
            for p in pendientes:
                motivo = _bloqueo(p, estado, por_id, huellas)
                if motivo:
                    e = {"estado": "bloqueado", "motivo": motivo}
                else:
                    r = lanzar(p["argv"], (limites or {}).get(p["id"], p["limite_s"]), S / "registro" / p["id"])
                    e = _cierre(p, r, S, por_id, huellas, gancho)
                anotar(p, e)
        finally:
            _SEGUIDOR = None
    return estado


def _en_paralelo(pasos, S, por_id, estado, huellas, anotar, gancho, limites, n):
    """Hasta n llamadas de FAM01 a la vez, cada una en su proceso (un hilo numérico: ENTORNO) y con su límite externo. Se recorre el plan
    en orden: una llamada de FAM01 se lanza cuando todas sus dependencias quedaron resueltas (la comparación, después de su productor) y
    hay un hueco; si alguna no quedó aceptada, se bloquea como en serie. Una llamada de otra familia hace de barrera: se lanza sola, cuando
    todo lo anterior terminó, y nada empieza mientras corre. Cada línea de ejecucion.jsonl añade inicio, fin y llamadas en curso."""
    pendientes, en_curso = list(pasos), {}
    try:
        while pendientes or en_curso:
            i = 0
            barrera = any(x["p"]["familia"] not in PARALELIZABLES for x in en_curso.values())
            while i < len(pendientes) and not barrera:
                p = pendientes[i]
                if p["familia"] not in PARALELIZABLES:
                    if i > 0 or en_curso:
                        break
                elif not all(d in estado or d not in por_id for d in p["depende_de"]):
                    i += 1
                    continue
                elif len(en_curso) >= n:
                    break
                del pendientes[i]
                motivo = _bloqueo(p, estado, por_id, huellas)
                if motivo:
                    anotar(p, {"estado": "bloqueado", "motivo": motivo})
                    i = 0
                    continue
                reg = S / "registro" / p["id"]
                fo, fe = open(reg.with_suffix(".out"), "xb"), open(reg.with_suffix(".err"), "xb")
                t0 = time.time()
                try:
                    pr = _iniciar(p["argv"], fo, fe)
                except BaseException:
                    fo.close()
                    fe.close()
                    raise
                en_curso[p["id"]] = {"p": p, "pr": pr, "fo": fo, "fe": fe, "t0": t0, "limite": (limites or {}).get(p["id"], p["limite_s"]),
                                     "en_curso_al_lanzar": len(en_curso) + 1}
                _seguir("alta", p["id"], pr)
                barrera = p["familia"] not in PARALELIZABLES
            if not en_curso:
                need(not pendientes, "EJECUCION_SIN_AVANCE: %s" % (pendientes[0]["id"] if pendientes else ""))
                continue
            time.sleep(SONDEO_S)
            for pid in sorted(en_curso):
                x = en_curso[pid]
                rc, vencido = x["pr"].poll(), False
                if rc is None:
                    if time.time() - x["t0"] < x["limite"]:
                        continue
                    _terminar_arbol(x["pr"])
                    rc, vencido = None, True
                fin = time.time()
                x["fo"].close()
                x["fe"].close()
                del en_curso[pid]
                _seguir("baja", pid)
                r = {"rc": rc, "limite_agotado": vencido, "segundos": round(fin - x["t0"], 3)}
                e = _cierre(x["p"], r, S, por_id, huellas, gancho)
                e.update(inicio=round(x["t0"], 3), fin=round(fin, 3), en_curso_al_lanzar=x["en_curso_al_lanzar"])
                anotar(x["p"], e)
    except BaseException:
        for x in en_curso.values():
            _terminar_arbol(x["pr"])
            x["fo"].close()
            x["fe"].close()
        raise


# ------------------------------------------------------------------------------------------------ balance

def _leer(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _lectura(p: dict) -> dict:
    """Lo que dice la salida de una llamada de comparación o verificación."""
    c, sal = p["argv"][0], BASE / p["produce"]
    if c.endswith("-comparar"):
        r = _leer(sal) if sal.is_file() else None
        if not isinstance(r, dict):
            return {"lectura": "sin informe JSON legible en %s" % p["produce"]}
        est = r.get("estado")
        est = est if isinstance(est, dict) else ({"texto": est} if est is not None else {})
        return {"regla": r.get("regla"), "reproduccion": est.get("reproduccion"), "estado": {k: v for k, v in est.items() if k != "reproduccion"}}
    if c == "fam10-tabla":
        r = _leer(sal / "tabla.json") or {}
        ops = {"ENF": "F10-ENF-AFIRMACION", "SINTESIS": "F10-SINTESIS", "INTEGRACION": "F10-INTEGRACION"}
        return {"cumple": r.get("cumple"), "comparaciones": {t: (v.get("estado") or {}).get("reproduccion") for t, v in (r.get("comparaciones") or {}).items()},
                "por_clave": {k: (r.get("comparaciones") or {}).get(t, {}).get("estado", {}).get("reproduccion") for t, k in ops.items()},
                "pasos": [{k: x.get(k) for k in ("etapa", "exito", "aceptada", "error")} for x in r.get("pasos") or []]}
    if c in ("fam13-reproducir", "fam14-reproducir"):
        r = _leer(sal / "resumen.json") or {}
        if c == "fam13-reproducir":
            por_clave = {"F13-HISTORICAS": r.get("F13_HISTORICAS_cumple"), "F13-S1": r.get("F13_S1_conforme")}
        else:
            por_clave = {k: (r.get(k.replace("-", "_")) or {}).get("cumple" if k == "F14-GN-REGEN" else "conforme")
                         for k in DIRECTAS[c]}
        return {"cumple": r.get("cumple"), "por_clave": por_clave, **{k: r[k] for k in r if re.fullmatch(r"F1[34]_[A-Z0-9_]+_(cumple|conforme)", k)},
                "balance": r.get("balance") if c == "fam14-reproducir" else None}
    if c == "p7-suplemento":
        r = _leer(sal) or {}
        return {k: r.get(k) for k in ("concordante", "k1_comparacion_exacta", "k1_valores_comparados")} | {
            "identidad_bytes_con_referencia": (r.get("comparacion_referencia") or {}).get("identidad_bytes_con_referencia")}
    if c == "q-local":
        r = _leer(sal / "resumen.json") or {}
        return {"concordante": r.get("concordante")}
    if c == "fam09-etapa" and _opt(p["argv"], "--tarea") == "HIST":
        return _lectura_hist(p["produce"])
    r = _leer(sal) if sal.is_file() else None
    return {"cumple": (r or {}).get("cumple")} if r is not None else {}


HIST_PRESERVADAS = 9434   # F09-HIST: filas definitivas del anexo T8 (rem108) que la etapa preserva (catálogo; fam09.ESPERADO["hist"])


def _lectura_hist(produce: str) -> dict:
    """LECTURA-HIST-v1. F09-HIST (verificación de integridad) escribe una carpeta, no un informe JSON: el veredicto se lee de su registro de
    ejecución (ejecucion.json: etapa HIST con éxito, rc 0, sin excepción), de las huellas de sus dos productos (iguales a los bytes de la
    carpeta) y de las filas preservadas (las líneas de FILAS_PRESERVADAS.jsonl = las declaradas en HIST.json = 9.434, con su huella)."""
    sal = BASE / produce
    ej = _leer(sal / "ejecucion.json") if (sal / "ejecucion.json").is_file() else None
    h = _leer(sal / "HIST.json") if (sal / "HIST.json").is_file() else None
    fp = sal / "FILAS_PRESERVADAS.jsonl"
    if not (isinstance(ej, dict) and isinstance(h, dict) and fp.is_file()):
        return {"lectura": "sin ejecucion.json, HIST.json o FILAS_PRESERVADAS.jsonl legibles en %s" % produce, "cumple": False}
    prods = ej.get("productos_sha256") if isinstance(ej.get("productos_sha256"), dict) else {}
    esperados = {produce + "/FILAS_PRESERVADAS.jsonl", produce + "/HIST.json"}
    actuales = {k: sha_archivo(BASE / k) for k in esperados if (BASE / k).is_file()}
    raw = fp.read_bytes()
    filas = raw.count(b"\n") if raw.endswith(b"\n") or not raw else None
    controles = {"registro_de_ejecucion": ej.get("tarea") == "HIST" and ej.get("exito") is True and ej.get("rc") == 0 and ej.get("excepcion") is None,
                 "productos_declarados": set(prods) == esperados,
                 "huellas_iguales_a_los_bytes": set(prods) == esperados and all(actuales.get(k) == v for k, v in prods.items()),
                 "resumen_del_registro_igual_a_HIST": (ej.get("detalle") or {}).get("resumen") == h,
                 "filas_preservadas_declaradas": h.get("preservadas") == filas == HIST_PRESERVADAS,
                 "huella_de_las_filas_preservadas": h.get("preservadas_sha256") == actuales.get(produce + "/FILAS_PRESERVADAS.jsonl")}
    return {"regla": "LECTURA-HIST-v1 (src/general.py)", "cumple": all(controles.values()), "controles": controles,
            "preservadas": h.get("preservadas"), "lineas": filas, "filas_anexo": h.get("filas_anexo"), "preservadas_sha256": h.get("preservadas_sha256")}


def _resultado_aceptado(p: dict, lectura: dict) -> bool:
    c = p["argv"][0]
    if "por_clave" in lectura:
        return lectura.get("cumple") is True and all(v is True or v == "aceptada" for v in lectura["por_clave"].values())
    if c.endswith("-comparar"):
        validos = ("aceptada", "aceptada_comparacion_limpia", "aceptada_comparacion_limpia_con_F2") if c == "fam01-comparar" else ("aceptada",)
        return lectura.get("reproduccion") in validos
    if c == "p7-suplemento":
        return (lectura.get("concordante") is True and lectura.get("k1_comparacion_exacta") is True
                and (lectura.get("k1_valores_comparados") or 0) > 0)
    if c == "q-local":
        return lectura.get("concordante") is True
    return lectura.get("cumple") is True


def resultado_exp8(tabla: Path) -> dict:
    """1.728 afirmaciones; doce COL que pasan a robust_infeasible; las otras 1.716 iguales a la síntesis de entrada; COV 1.700/12/16."""
    fin, ent = tabla / "integracion/sintesis/EXP8_POR_AFIRMACION.jsonl", tabla / "sintesis/sintesis/EXP8_POR_AFIRMACION.jsonl"
    if not (fin.is_file() and ent.is_file()):
        return {"cumple": False, "motivo": "FILAS_AUSENTES"}
    a = ent.read_text(encoding="utf-8").splitlines()
    b = fin.read_text(encoding="utf-8").splitlines()
    cambiadas = [(json.loads(x), json.loads(y)) for x, y in zip(a, b) if x != y]
    cov = Counter(json.loads(y)["COV"]["conclusion"] for y in b)
    campos = Counter(k for x, y in cambiadas for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k))
    r = {"filas_finales": len(b), "filas_de_la_sintesis_de_entrada": len(a), "filas_cambiadas": len(cambiadas), "filas_identicas": len(b) - len(cambiadas),
         "cambiadas_por_pais": dict(Counter(y["dimensiones"]["pais"] for _, y in cambiadas)),
         "COV_antes_en_las_cambiadas": dict(Counter(x["COV"]["conclusion"] for x, _ in cambiadas)),
         "COV_despues_en_las_cambiadas": dict(Counter(y["COV"]["conclusion"] for _, y in cambiadas)),
         "campos_que_cambian": dict(campos), "COV_final": dict(cov), "filas_sha256": sha_archivo(fin)}
    r["controles"] = {"afirmaciones_1728": len(a) == len(b) == 1728, "doce_cambiadas": len(cambiadas) == 12,
                      "las_doce_son_COL": r["cambiadas_por_pais"] == {"COL": 12},
                      "las_doce_pasan_a_robust_infeasible": r["COV_despues_en_las_cambiadas"] == {"robust_infeasible": 12},
                      "otras_1716_identicas_a_la_sintesis": r["filas_identicas"] == 1716,
                      "COV_1700_12_16": r["COV_final"] == {"inconclusa_preservada": 1700, "robust_infeasible": 12, "no_decidida_por_testigos": 16}}
    r["cumple"] = all(r["controles"].values())
    return r


def balance(plan: dict, modo: str, estado: dict) -> dict:
    completo = plan["modos"]["completo"]["pasos"]
    pasos = plan["modos"][modo]["pasos"] if modo in plan["modos"] else []
    por_id = {p["id"]: p for p in pasos}
    por_id_c = {p["id"]: p for p in completo}
    sust = plan["modos"]["piloto"]["sustituciones"] if modo == "piloto" else []
    anc = {}

    def ancestros(i):
        if i not in anc:
            anc[i] = set()
            for d in por_id_c[i]["depende_de"]:
                anc[i] |= {d} | ancestros(d)
        return anc[i]
    anc_m = {}

    def ancestros_modo(i):
        if i not in anc_m:
            anc_m[i] = set()
            for d in por_id[i]["depende_de"]:
                anc_m[i] |= {d} | ancestros_modo(d)
        return anc_m[i]
    out = {}
    for k, f in plan["claves"].items():
        mias = [p for p in (completo if modo == "plan" else pasos) if k in p["claves"]]
        ests = {p["id"]: (estado.get(p["id"]) or {}).get("estado", "sin ejecutar") for p in mias}
        if modo == "plan":
            situacion = "plan sin cálculo: %d llamadas en el completo" % f["llamadas_completo"]
        elif not mias:
            situacion = "sin ejecutar (fuera del modo %s)" % modo
        elif any(v not in ("aceptado", "bloqueado") for v in ests.values()):
            situacion = "no conforme: %s" % ", ".join("%s %s" % (i, v) for i, v in ests.items() if v not in ("aceptado", "bloqueado"))
        elif any(v == "bloqueado" for v in ests.values()):
            situacion = "pendiente: bloqueada (%s)" % next(estado[i]["motivo"] for i, v in ests.items() if v == "bloqueado")
        else:
            calc = any("calculo" in p["papeles"] for p in mias)
            val = any("validacion" in p["papeles"] for p in mias)
            reut = [s for s in sust if s["llamada"] in ests]
            arriba = sorted({s["llamada"] for s in sust if s["llamada"] not in ests and any(s["llamada"] in ancestros_modo(i) for i in ests)})
            if f["tipo"] == "RN":
                situacion = ("calculada%s y comparada" % (", validada" if val else "")) if calc else \
                    "regenerada sobre entradas guardadas; su cálculo no se ejecutó"
            elif f["tipo"] == "RD":
                situacion = "regenerada y comparada" + (" (con entradas guardadas)" if reut else "")
            else:
                situacion = "verificada por integridad"
            if arriba:
                situacion += " (aguas arriba, %s con entradas guardadas)" % ", ".join(arriba)
        entradas = [{"llamada": p["id"], "ruta": c["ruta"], "de": c["de"]} for p in mias for c in p["consume"]]
        entradas += [{"llamada": p["id"], "entrada": h["entrada"], "de": "guardado (insumo histórico del paquete)", "procedencia": h.get("procedencia")}
                     for p in mias for h in p["historicas"]]
        comps = [{"llamada": p["id"], "orden": p["orden"], "estado_de_la_llamada": ests[p["id"]],
                  **(_lectura(p) if ests[p["id"]] in ("aceptado", "rechazado", "informe_no_conforme") else {})}
                 for p in mias if {"comparacion", "verificacion_integridad"} & set(p["papeles"])]
        for informe in comps:
            if "por_clave" in informe:
                v = informe["por_clave"].get(k)
                informe["veredicto_de_la_clave"] = ("aceptada" if v is True else "no_aceptada" if v is False else v or "sin comprobar")
        # reproducción completa: todas las llamadas del completo de la clave y sus ancestros, ejecutadas aquí con la misma orden y aceptadas
        necesarias = {p["id"] for p in completo if k in p["claves"]}
        necesarias |= {a for i in list(necesarias) for a in ancestros(i)}
        faltan = sorted(i for i in necesarias if not (i in por_id and por_id[i]["argv"] == por_id_c[i]["argv"]
                                                      and (estado.get(i) or {}).get("estado") == "aceptado"))
        completa = ("completa en esta ejecución: sus %d llamadas del plan completo (con sus antecesoras) ejecutadas con la misma orden y aceptadas"
                    % len(necesarias)) if not faltan else (
            "pendiente (Paso 3): faltan %d de %d llamadas del plan completo, p. ej. %s" % (len(faltan), len(necesarias), por_id_c[faltan[0]]["orden"]))
        if not faltan and f["disponibilidad"] == "INCOMPLETA":
            completa = "pendiente de decisión: " + "; ".join(f["documentado"]["residuos"])
        out[k] = {"familia": f["familia"], "tipo": f["tipo"], "naturaleza": f["naturaleza"], "en_esta_ejecucion": situacion,
                  "llamadas": {"en_este_modo": len(mias) if modo != "plan" else 0, "en_el_completo": f["llamadas_completo"],
                               "por_estado": dict(Counter(ests.values()))},
                  "entradas": entradas, "entradas_total": len(entradas),
                  "insumos_historicos_de_la_familia": plan["insumos_historicos"][f["familia"]],
                  "reutilizado": [s for s in sust if s["llamada"] in ests], "comparacion_aplicada": comps, "regla": f["regla"],
                  "reproduccion_completa": completa, "documentado": f["documentado"]}
    return out


def lecturas_fuera(S: Path) -> dict:
    """Suma de las lecturas fuera del paquete (y del intérprete) que registran las propias llamadas en sus salidas."""
    def buscar(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("fuera_del_paquete_y_del_interprete", "fuera_de_stdlib_y_paquete") and isinstance(v, list):
                    yield k, v
                else:
                    yield from buscar(v)
        elif isinstance(x, list):
            for v in x:
                yield from buscar(v)
    registros, fuera = 0, []
    for f in sorted(S.rglob("*.json")):
        partes = f.relative_to(S).parts
        if f.parent == S or "recetas" in partes or partes[0] in ("intentos", "reanudaciones"):
            continue
        hallados = list(buscar(_leer(f)))
        registros += bool(hallados)
        fuera += ["%s: %s" % (f.relative_to(S).as_posix(), x) for _, v in hallados for x in v]
    return {"archivos_que_registran_lecturas": registros, "lecturas_fuera_del_paquete": len(fuera), "ejemplos": fuera[:10]}


def _md(plan, modo, bal, exp8, resumen) -> str:
    def celda(x):
        return str(x).replace("|", "/").replace("\n", " ")
    L = ["# Balance del comando general (modo %s)" % modo, "",
         "Carpeta: `%s`. Conforme: **%s**. Llamadas del modo: %s." % (plan["carpeta"], "sí" if resumen["conforme"] else "no",
                                                                     ", ".join("%s %d" % kv for kv in resumen["llamadas_por_estado"].items()) or "ninguna"),
         ""]
    if modo == "piloto":
        L += ["El éxito del piloto no es la reproducción completa: la última columna dice qué falta de cada clave en el plan completo.", ""]
    if resumen.get("reanudacion"):
        r = resumen["reanudacion"]
        L += ["Sesión %s (reanudación, REANUDACION-PASO3-v1): %s llamadas reutilizadas de sesiones anteriores y %s repetidas o nuevas; "
              "lo apartado está en `%s`." % (resumen.get("sesion"), r.get("reutilizadas"), r.get("a_repetir"), r.get("intentos") or "—"), ""]
    if resumen.get("lecturas"):
        L += ["Lecturas fuera del paquete registradas por las llamadas: %d (en %d registros)." % (
            resumen["lecturas"]["lecturas_fuera_del_paquete"], resumen["lecturas"]["archivos_que_registran_lecturas"]), ""]
    if exp8:
        L += ["Resultado Exp8: %d afirmaciones; %d cambiadas (%s), %s; %d idénticas a la síntesis de entrada; COV final %s. Controles: %s." % (
            exp8.get("filas_finales", 0), exp8.get("filas_cambiadas", 0), exp8.get("cambiadas_por_pais"), exp8.get("COV_despues_en_las_cambiadas"),
            exp8.get("filas_identicas", 0), exp8.get("COV_final"), "todos conformes" if exp8.get("cumple") else exp8.get("controles", exp8.get("motivo"))), ""]
    L += ["| Clave | Tipo | En esta ejecución | Entradas | Comparación aplicada | Reproducción completa |", "|---|---|---|---|---|---|"]
    for k, b in bal.items():
        ent = Counter("guardada" if str(e["de"]).startswith("guardado") else "de esta ejecución" for e in b["entradas"])
        ent_txt = ", ".join("%d %s" % (n, t) for t, n in ent.items()) or "ninguna de otra llamada"
        ent_txt += "; insumos históricos declarados por la familia: %d" % len(b["insumos_historicos_de_la_familia"])
        comps = sorted(b["comparacion_aplicada"], key=lambda c: c["estado_de_la_llamada"] in ("aceptado", "sin ejecutar"))
        comp = "; ".join("%s → %s" % (c["llamada"], c.get("veredicto_de_la_clave") or c.get("reproduccion") or ("cumple" if c.get("cumple") or c.get("concordante") else c["estado_de_la_llamada"]))
                         for c in comps[:2]) or "—"
        L.append("| %s | %s | %s | %s | %s (%s) | %s |" % (k, b["tipo"], celda(b["en_esta_ejecucion"])[:220], ent_txt, celda(comp)[:160], celda(b["regla"]),
                                                       celda(b["reproduccion_completa"])[:200]))
    L += ["", "## Criterios adoptados y límites documentados", "",
          "La regla de cada clave figura entre paréntesis en «Comparación aplicada». Los límites y las piezas sin localizar se copian "
          "del catálogo: el comando no los adopta ni los levanta. Detalle completo en `balance.json` (campo `documentado`).", ""]
    for k, b in bal.items():
        doc = b.get("documentado") or {}
        sin_loc = re.findall(r"[^.;]*\bU\d+\b[^.;]*?no localizad[oa]s?", doc.get("estado_base_limpia") or "", flags=re.I)
        partes = ["sin localizar: " + "; ".join(x.strip() for x in sin_loc)] if sin_loc else []
        partes += ["%s (%s): %s" % (x.get("id"), x.get("tipo"), x.get("efecto_en_fila")) for x in doc.get("limites") or []]
        if partes:
            L.append("- **%s**: %s" % (k, celda(" · ".join(partes))))
    return "\n".join(L) + "\n"


def _ensayo_fam01(plan: dict, unidades, limite_s, Srel: str, parser) -> dict:
    """ENSAYO-FAM01-v1: las unidades nombradas en un mismo proceso fam01-unidad (salida nueva <S>/fam01/<sel>/ensayo), con fam01-listas
    antes, como en el plan, y una fam01-comparar por unidad, cada una contra su original. Varias unidades solo si son de la misma selección
    y de grupos de techo caro de la misma clave estructural. El límite es el de la regla de grupos para esas unidades, salvo que la orden
    fije otro (limite_s); ambos quedan en el plan."""
    unidades = list(unidades or [])
    need(unidades and len(set(unidades)) == len(unidades), "ENSAYO_SIN_UNIDADES_O_CON_REPETIDAS")
    completo = plan["modos"]["completo"]["pasos"]
    calc = {p["argv"][i + 1]: p for p in completo if p["argv"][0] == "fam01-unidad" for i in range(len(p["argv"]) - 1) if p["argv"][i] == "--unidad"}
    need(all(u in calc for u in unidades), "ENSAYO_CON_UNIDADES_FUERA_DE_LA_RECETA: %s" % [u for u in unidades if u not in calc])
    sels = {_opt(calc[u]["argv"], "--seleccion") for u in unidades}
    need(len(sels) == 1, "ENSAYO_CON_SELECCIONES_DISTINTAS")
    sel = sels.pop()
    rec = json.loads((BASE / Srel / "recetas" / "fam01.json").read_text(encoding="utf-8"))
    gt = rec["grupos_techo"]
    grupos = {p["tarea"]: p for p in rec["pasos"] if p.get("regla") == gt["regla"]}
    de = {u: next((t for t, g in grupos.items() if u in g["unidades"]), None) for u in unidades}
    claves = {grupos[t]["clave_estructural"] for t in de.values() if t}
    need(len(unidades) == 1 or (all(de.values()) and len(claves) == 1), "ENSAYO_CON_UNIDADES_SIN_GRUPO_DE_TECHO_COMUN")
    if all(de.values()):
        c = next(x for x in gt["claves_caras"] if x["clave_estructural"] in claves and x["seleccion"] == sel)
        K = gt["constantes"]
        f = len({grupos[de[u]]["frontera_por_unidad"][u] for u in unidades})
        regla_s = 60.0 * math.ceil((K["factor_frio"] * (c["techo_historico_s"] + f * c["macro_historica_s"]) + K["por_unidad_s"] * len(unidades)) / 60.0)
        detalle = {"clave_estructural": c["clave_estructural"], "fronteras": f, "techo_historico_s": c["techo_historico_s"],
                   "macro_historica_s": c["macro_historica_s"], "constantes": K}
    else:
        regla_s, detalle = calc[unidades[0]]["limite_s"], {"unidad_ordinaria": True}
    lim = float(limite_s) if limite_s is not None else regla_s
    need(lim > 0, "ENSAYO_CON_LIMITE_NO_POSITIVO")
    listas = [p for p in completo if p["argv"][0] == "fam01-listas"]
    need(len(listas) == 1, "ENSAYO_SIN_FAM01_LISTAS_EN_EL_PLAN")
    L = listas[0]["id"]
    T = "%s/fam01/%s/ensayo" % (Srel, sel)
    comun = {"familia": "FAM01", "tambien_en": [], "origen": "ensayo-fam01 (ENSAYO-FAM01-v1)", "historicas": [], "prerrequisitos_externos": [],
             "parada": None, "previo": False, "claves": ["F01-" + sel], "dependencias_estructurales": [L],
             "supervision": "proceso propio; límite externo; al agotarlo se termina el árbol de procesos"}
    argv = ["fam01-unidad", "--seleccion", sel] + [x for u in unidades for x in ("--unidad", u)] + ["--salida", T]
    pasos = [dict(listas[0]), dict(comun, id="E00001", meta={"regla": "ENSAYO-FAM01-v1", "seleccion": sel, "unidades": unidades, "grupos_en_el_plan": de},
                                   argv=argv, orden=_orden(argv), papeles=_papeles("fam01-unidad", None), produce=T, consume=[], depende_de=[L], limite_s=lim)]
    for n, u in enumerate(unidades, start=2):
        a = ["fam01-comparar", "--seleccion", sel, "--unidad", u, "--nueva", T, "--salida", "%s.%s.comparacion.json" % (T, u.replace(":", "_"))]
        pasos.append(dict(comun, id="E%05d" % n, meta={"regla": "ENSAYO-FAM01-v1", "seleccion": sel, "unidad": u}, argv=a, orden=_orden(a),
                          papeles=_papeles("fam01-comparar", None), produce=a[-1], consume=[{"opcion": "--nueva", "ruta": T, "de": "E00001"}],
                          depende_de=sorted({L, "E00001"}), limite_s=LIMITE_ORDINARIO_S))
    need(all(_llamada_real(parser, p["argv"]) for p in pasos), "ENSAYO_CON_LLAMADA_RECHAZADA_POR_LA_CLI")
    return {"regla": "ENSAYO-FAM01-v1", "seleccion": sel, "unidades": unidades, "grupos_en_el_plan": de, "limite_externo_s": lim,
            "limite_de_la_regla_s": regla_s, "limite_fijado_por": "la orden (--limite-ensayo-s)" if limite_s is not None else "la regla de grupos",
            "detalle_de_la_regla": detalle, "pasos": pasos}


# ------------------------------------------------------------------------------------------------ reanudación (REANUDACION-PASO3-v1)

def huella_ejecucion(raiz: Path = BASE) -> dict:
    """La huella del inventario de ejecución, como herramienta/inventario.ps1 -Ejecucion: mismas exclusiones y sin distinguir mayúsculas
    (PowerShell), orden ordinal, una línea «ruta<TAB>bytes<TAB>sha256» por archivo con LF, y sha256 de ese texto. En la copia pública
    excluye también lo que solo documenta o resume: docs/, tools/, sensitivities/ y, en la raíz, CITATION.cff y run.ps1."""
    rutas = []
    for e in sorted(raiz.iterdir()):
        n = e.name.lower()
        if e.is_dir():
            if n in (".git", "salidas", "local", "docs", "tools", "sensitivities") or n.startswith(".venv"):
                continue
            rutas += [f for f in e.rglob("*") if f.is_file()]
        elif e.is_file():
            rutas.append(e)
    sel = []
    for f in rutas:
        r = f.relative_to(raiz).as_posix()
        rl = r.lower()
        if re.search(r"(^|/)__pycache__/", rl) or rl.endswith(".pyc"):
            continue
        if rl.startswith("extraccion/") and rl != "extraccion/registro/lecturas_ejecucion_fam02.json":
            continue
        if "/" not in r and (rl.endswith(".md") or rl in ("plan_trabajo.txt", ".gitattributes", ".gitignore", "citation.cff", "run.ps1")):
            continue
        if rl.startswith("insumos_externos/"):
            continue
        sel.append(r)
    sel.sort(key=lambda s: s.encode("utf-16-be"))  # ordinal de .NET: unidades UTF-16
    filas, total = [], 0
    for r in sel:
        n = (raiz / r).stat().st_size
        total += n
        filas.append("%s\t%d\t%s" % (r, n, sha_archivo(raiz / r)))
    texto = ("\n".join(filas) + "\n").encode("utf-8")
    return {"sha256": hashlib.sha256(texto).hexdigest(), "archivos": len(sel), "bytes": total}


def _entorno() -> dict:
    """Lo que la reanudación exige igual: intérprete, opciones, variables de las llamadas y distribuciones instaladas. La ruta del
    intérprete queda solo como huella."""
    import importlib.metadata as md
    return {"python": sys.version, "implementacion": platform.python_implementation(), "arquitectura": platform.machine(),
            "ejecutable_sha256": hashlib.sha256(os.path.normcase(sys.executable).encode("utf-8")).hexdigest(),
            "entorno_virtual": sys.prefix != sys.base_prefix,
            "opciones_del_ejecutor": {k: getattr(sys.flags, k, None) for k in ("dont_write_bytecode", "no_user_site", "safe_path", "utf8_mode",
                                                                              "isolated", "ignore_environment", "hash_randomization")},
            "opciones_de_las_llamadas": list(FLAGS), "variables_de_las_llamadas": dict(ENTORNO),
            "variables_del_ejecutor": {k: os.environ.get(k) for k in ENTORNO},
            "distribuciones": sorted({"%s==%s" % (d.metadata["Name"], d.version) for d in md.distributions()})}


def _tomar_cerrojo(S: Path, sesion) -> int:
    """Un solo ejecutor por corrida: cerrojo exclusivo sobre <S>/ejecucion.lock mientras vive el proceso (el sistema lo suelta si muere)."""
    fd = os.open(S / "ejecucion.lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        q = _leer(S / "ejecutor.json") or {}
        raise ErrorGeneral("CORRIDA_EN_USO_POR_OTRA_INSTANCIA: %s la ocupa otro ejecutor (pid %s, sesión %s, desde %s)" % (
            S.relative_to(BASE).as_posix(), q.get("pid"), q.get("sesion"), q.get("desde_utc")))
    _reemplazar(S / "ejecutor.json", {"pid": os.getpid(), "creacion": _creacion_proceso(os.getpid()), "sesion": sesion, "desde_utc": _utc()})
    return fd


def _soltar_cerrojo(fd: int):
    with contextlib.suppress(OSError):
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    os.close(fd)


class _Diario:
    """<S>/estado_llamadas.jsonl, solo se añade: una línea por llamada cerrada (estado; si quedó aceptada, huellas de su salida y de las
    salidas que su validación amplió) y por llamada aceptada que una reanudación aparta. Cada línea se fuerza a disco antes de seguir."""

    def __init__(self, ruta: Path, sesion: int):
        self.sesion = sesion
        if ruta.exists() and ruta.stat().st_size:
            with open(ruta, "rb") as f:
                f.seek(-1, os.SEEK_END)
                cortada = f.read(1) != b"\n"
            if cortada:  # línea a medias de un corte: queda ilegible (se ignora) y no se pega a la siguiente
                with open(ruta, "ab") as f:
                    f.write(b"\n")
        self.f = open(ruta, "a", encoding="utf-8", newline="\n")

    def anotar(self, reg: dict):
        self.f.write(json.dumps({"sesion": self.sesion, **reg}, ensure_ascii=False, allow_nan=False) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())

    def close(self):
        self.f.close()


def _leer_diario(ruta: Path):
    """(último registro por llamada, huellas vigentes por salida, validaciones que ampliaron cada salida, líneas ilegibles)."""
    ultimo, man, ampliada_por, ilegibles = {}, {}, {}, 0
    texto = ruta.read_text(encoding="utf-8", errors="replace") if ruta.exists() else ""
    for linea in texto.splitlines():
        try:
            r = json.loads(linea)
        except ValueError:
            ilegibles += bool(linea.strip())
            continue
        if not (isinstance(r, dict) and isinstance(r.get("id"), str)):
            ilegibles += 1
            continue
        i = r["id"]
        if r.get("tipo") == "llamada" and isinstance(r.get("e"), dict):
            ultimo[i] = r
            if r["e"].get("estado") == "aceptado":
                man[i], ampliada_por[i] = r.get("manifiesto"), set()
            for de, m in (r.get("actualiza") or {}).items():
                man[de] = m
                ampliada_por.setdefault(de, set()).add(i)
        elif r.get("tipo") == "apartada":
            ultimo[i] = r
    return ultimo, man, ampliada_por, ilegibles


def _reutilizables(pasos, ultimo, man, ampliada_por):
    """Llamadas que no se repiten: su último registro es aceptado y con la misma orden, su salida conserva las huellas registradas, y
    todo aquello de lo que depende (y toda validación que amplió su salida) se reutiliza también. Lo demás, con su motivo."""
    por_id = {p["id"]: p for p in pasos}
    ok, motivo = set(), {}
    for p in pasos:
        r = ultimo.get(p["id"])
        if r is None:
            motivo[p["id"]] = "sin registro en el diario (no empezó o quedó a medias)"
        elif r.get("tipo") != "llamada" or r["e"].get("estado") != "aceptado":
            motivo[p["id"]] = "último registro: %s" % (r["e"].get("estado") if r.get("tipo") == "llamada" else "apartada")
        elif r.get("orden") != p["orden"]:
            motivo[p["id"]] = "orden distinta de la registrada"
        else:
            sal = BASE / p["produce"]
            if not sal.exists() or _manifiesto(sal) != man.get(p["id"]):
                motivo[p["id"]] = "su salida no conserva las huellas registradas"
            else:
                ok.add(p["id"])
    cambio = True
    while cambio:
        cambio = False
        for i in sorted(ok):
            falta = [d for d in por_id[i]["depende_de"] if d not in ok] + sorted(v for v in ampliada_por.get(i, ()) if v not in ok)
            if falta:
                ok.discard(i)
                motivo[i] = "se repite %s, de la que depende o que amplió su salida" % falta[0]
                cambio = True
    return ok, motivo


def _procesos_que_nombran(Srel: str) -> list:
    """Windows: pid de los procesos python cuya orden nombra la carpeta de la corrida, salvo este y sus antecesores."""
    guion = ("[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-CimInstance Win32_Process | ForEach-Object { "
             "'{0}|{1}|{2}|{3}' -f $_.ProcessId, $_.ParentProcessId, $_.Name, ($_.CommandLine -replace '[\\r\\n]', ' ') }")
    import base64
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", base64.b64encode(guion.encode("utf-16-le")).decode()],
                       capture_output=True, timeout=120)
    need(r.returncode == 0, "NO_SE_PUDIERON_LISTAR_LOS_PROCESOS: %s" % r.stderr.decode("utf-8", "replace")[:300])
    procs = {}
    for linea in r.stdout.decode("utf-8", "replace").splitlines():
        partes = linea.strip().lstrip("﻿").split("|", 3)
        if len(partes) == 4 and partes[0].isdigit() and partes[1].isdigit():
            procs[int(partes[0])] = (int(partes[1]), partes[2].lower(), partes[3].replace("\\", "/"))
    mios, x = set(), os.getpid()
    while x in procs and x not in mios:
        mios.add(x)
        x = procs[x][0]
    return sorted(pid for pid, (_, nombre, orden) in procs.items()
                  if pid not in mios and nombre.startswith("python") and Srel in orden)


def _terminar_huerfanos(S: Path, Srel: str) -> list:
    """Procesos de llamadas que el ejecutor anterior dejó vivos (murió sin terminarlos): se terminan con su árbol antes de tocar sus
    salidas. Se buscan en <S>/en_curso.json (pid e instante de creación) y, en Windows, por la orden."""
    vistos = {}
    for ident, x in (_leer(S / "en_curso.json") or {}).items():
        if isinstance(x, dict) and isinstance(x.get("pid"), int) and x.get("creacion") and _creacion_proceso(x["pid"]) == x["creacion"]:
            vistos[x["pid"]] = ident
    if os.name == "nt":
        for pid in _procesos_que_nombran(Srel):
            vistos.setdefault(pid, "proceso cuya orden nombra la corrida")
    for pid in sorted(vistos):
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(pid, signal.SIGKILL)
    t = time.time()
    while any(_creacion_proceso(pid) for pid in vistos) and time.time() - t < 60:
        time.sleep(0.5)
    vivos = [pid for pid in vistos if _creacion_proceso(pid)]
    need(not vivos, "PROCESOS_DE_LA_CORRIDA_SIN_TERMINAR: %s" % vivos)
    return [{"pid": pid, "llamada": vistos[pid]} for pid in sorted(vistos)]


def _apartar(S: Path, I: Path, pasos, ok) -> list:
    """Lleva a I (intentos/<k>) lo que la carpeta tiene y no se reutiliza: salidas de llamadas que se repiten, sus registros,
    ejecucion.jsonl, el balance anterior y cualquier resto. Quedan el control de la corrida, el plan, las recetas y lo reutilizado."""
    Sp = PurePosixPath(S.relative_to(BASE).as_posix())
    guardar = {PurePosixPath(p["produce"]).relative_to(Sp) for p in pasos if p["id"] in ok}
    guardar |= {PurePosixPath("registro", i + suf) for i in ok for suf in (".out", ".err")}
    recorrer_tambien = {a for g in guardar for a in g.parents} | {PurePosixPath("registro")}
    movidos = []

    def recorrer(d: Path):
        for x in sorted(d.iterdir()):
            r = PurePosixPath(x.relative_to(S).as_posix())
            if len(r.parts) == 1 and r.name in CONTROL_DE_LA_CORRIDA:
                continue
            if len(r.parts) == 2 and r.parts[0] == "registro" and r.name.startswith("receta_"):
                continue
            if r in guardar:
                continue
            if r in recorrer_tambien and x.is_dir():
                recorrer(x)
                continue
            destino = I / r
            destino.parent.mkdir(parents=True, exist_ok=True)
            os.rename(x, destino)
            movidos.append(r.as_posix())
    recorrer(S)
    return movidos


def _plan_comparable(plan: dict, Srel: str) -> str:
    def limpiar(x):
        if isinstance(x, dict):
            return {k: limpiar(v) for k, v in x.items() if k not in ("segundos", "carpeta")}
        if isinstance(x, list):
            return [limpiar(v) for v in x]
        return x
    return json.dumps(limpiar(plan), ensure_ascii=False, sort_keys=True).replace(Srel, "<S>")


def _plan_de_la_corrida(Srel: str, parser, registro: Path, modo: str, procesos_fam01: int, ensayo) -> dict:
    plan = construir(Srel, parser, registro)
    plan["ejecucion"] = {"procesos_fam01": procesos_fam01, "maximo": MAX_PROCESOS_FAM01, "familias_en_paralelo": list(PARALELIZABLES),
                         "regla": "una llamada a la vez" if procesos_fam01 == 1 else
                         "hasta %d llamadas de FAM01 a la vez, cada una tras sus dependencias; las demás familias, una a una" % procesos_fam01}
    if modo == "ensayo-fam01" and plan["cumple"]:
        plan["modos"][modo] = _ensayo_fam01(plan, ensayo.get("unidades"), ensayo.get("limite_s"), Srel, parser)
    return plan


def _cerrar(plan, modo, S, Srel, estado, procesos_fam01, t0, control=None, k=0, reanudacion=None) -> dict:
    """Exp8, balance y resumen de la sesión; con control, también su fila en control.json."""
    exp8 = None
    if modo != "plan" and plan["cumple"]:
        tabla = [p for p in plan["modos"][modo]["pasos"] if p["argv"][0] == "fam10-tabla"]
        if tabla and (estado.get(tabla[0]["id"]) or {}).get("estado") == "aceptado":
            exp8 = resultado_exp8(BASE / tabla[0]["produce"])
        elif tabla:
            exp8 = {"cumple": False, "motivo": "fam10-tabla no aceptada en esta ejecución"}
    bal = balance(plan, modo, estado)
    pasos = plan["modos"].get(modo, {}).get("pasos", [])
    por_estado = dict(Counter((estado.get(p["id"]) or {}).get("estado", "sin ejecutar") for p in pasos)) if modo != "plan" else {}
    if modo == "plan":
        conforme = plan["cumple"]
    else:
        conforme = plan["cumple"] and bool(pasos) and por_estado == {"aceptado": len(pasos)} and (exp8 is None or exp8["cumple"])
        if modo == "completo":
            conforme = conforme and all(b["reproduccion_completa"].startswith("completa") for b in bal.values())
    resumen = {"modo": modo, "carpeta": Srel, "plan_cumple": plan["cumple"], "procesos_fam01": procesos_fam01, "llamadas_por_estado": por_estado,
               "ensayo": ({k_: v for k_, v in plan["modos"][modo].items() if k_ != "pasos"} if modo == "ensayo-fam01" and modo in plan["modos"] else None),
               "claves_por_situacion": dict(Counter(b["en_esta_ejecucion"].split(":")[0].split(" (")[0] for b in bal.values())),
               "claves_completas_en_esta_ejecucion": sorted(k_ for k_, b in bal.items() if b["reproduccion_completa"].startswith("completa")),
               "no_conformes_o_bloqueadas": {k_: b["en_esta_ejecucion"] for k_, b in bal.items() if b["en_esta_ejecucion"].startswith(("no conforme", "pendiente"))},
               "resultado_exp8": exp8 and {k_: exp8.get(k_) for k_ in ("cumple", "controles", "motivo")},
               "lecturas": lecturas_fuera(S) if modo != "plan" else None,
               "sesion": k if control is not None else None, "reanudacion": reanudacion,
               "conforme": conforme, "segundos": round(time.time() - t0, 3)}
    _escribir(S / "balance.json", {"resumen": resumen, "resultado_exp8": exp8, "claves": bal})
    with open(S / "BALANCE.md", "x", encoding="utf-8", newline="\n") as f:
        f.write(_md(plan, modo, bal, exp8, resumen))
    if control is not None:
        control["sesiones"][k].update(fin_utc=_utc(), conforme=conforme, llamadas_por_estado=por_estado, segundos=resumen["segundos"])
        need(_reemplazar(S / "control.json", control), "CONTROL_SIN_ACTUALIZAR")
    return {"resumen": resumen, "conforme": conforme}


def general(modo: str, salida: Path, parser, gancho=None, limites=None, procesos_fam01: int = 1, ensayo=None) -> dict:
    """gancho y limites solo los usan los controles locales (local/pruebas_general.py); la orden pública no los expone.
    procesos_fam01: llamadas de FAM01 simultáneas (1 por omisión, como máximo MAX_PROCESOS_FAM01). ensayo: {"unidades": [...],
    "limite_s": s o None}, solo en el modo ensayo-fam01. Fuera del modo plan, la corrida queda preparada para reanudar()."""
    t0 = time.time()
    need(isinstance(procesos_fam01, int) and 1 <= procesos_fam01 <= MAX_PROCESOS_FAM01, "PROCESOS_FAM01_FUERA_DE_1_A_%d" % MAX_PROCESOS_FAM01)
    need((modo == "ensayo-fam01") == (ensayo is not None), "UNIDADES_DE_ENSAYO_SOLO_EN_EL_MODO_ENSAYO_FAM01")
    S = Path(salida).resolve()
    need(S.is_relative_to(BASE), "LA_SALIDA_DEBE_ESTAR_DENTRO_DE_LA_BASE")
    need(not S.exists(), "LA_SALIDA_YA_EXISTE")
    Srel = S.relative_to(BASE).as_posix()
    (S / "registro").mkdir(parents=True)
    cerrojo = _tomar_cerrojo(S, 0) if modo != "plan" else None
    try:
        plan = _plan_de_la_corrida(Srel, parser, S / "registro", modo, procesos_fam01, ensayo)
        _escribir(S / "plan.json", plan)
        estado, control = {}, None
        if modo != "plan" and plan["cumple"]:
            control = {"regla": REGLA_REANUDACION, "carpeta": Srel, "modo": modo, "procesos_fam01": procesos_fam01, "ensayo": ensayo,
                       "version": huella_ejecucion(), "entorno": _entorno(),
                       "plan": {"plan_json_sha256": sha_archivo(S / "plan.json"), "recetas": _manifiesto(S / "recetas"),
                                "llamadas": len(plan["modos"][modo]["pasos"])},
                       "sesiones": [{"sesion": 0, "tipo": "inicio", "inicio_utc": _utc(), "pid": os.getpid(), "procesos_fam01": procesos_fam01,
                                     "sistema": platform.platform()}]}
            need(_reemplazar(S / "control.json", control), "CONTROL_SIN_ESCRIBIR")
            diario = _Diario(S / "estado_llamadas.jsonl", 0)
            try:
                estado = ejecutar(plan, modo, S, gancho=gancho, limites=limites, procesos_fam01=procesos_fam01, diario=diario)
            finally:
                diario.close()
        return _cerrar(plan, modo, S, Srel, estado, procesos_fam01, t0, control, 0)
    finally:
        if cerrojo is not None:
            _soltar_cerrojo(cerrojo)


def reanudar(salida: Path, parser, procesos_fam01=None, modo=None, gancho=None, limites=None) -> dict:
    """REANUDACION-PASO3-v1 sobre la carpeta de una corrida empezada por general(): cerrojo; procesos huérfanos terminados; misma versión
    del paquete (huella del inventario de ejecución), mismo entorno y mismo plan (plan.json y recetas intactos, y el plan reconstruido
    ahora con el paquete, igual); se reutilizan las llamadas aceptadas e intactas (_reutilizables) y se repiten las demás con su orden y
    su límite. Lo que dejaron va a intentos/<k>. Cada intento, también el rechazado, queda como sesión en control.json."""
    t0 = time.time()
    S = Path(salida).resolve()
    need(S.is_relative_to(BASE), "LA_SALIDA_DEBE_ESTAR_DENTRO_DE_LA_BASE")
    need((S / "control.json").is_file(), "CORRIDA_SIN_CONTROL_DE_REANUDACION: %s" % Path(salida).as_posix())
    Srel = S.relative_to(BASE).as_posix()
    cerrojo = _tomar_cerrojo(S, None)
    try:
        control = json.loads((S / "control.json").read_text(encoding="utf-8"))
        need(control.get("regla") == REGLA_REANUDACION, "CONTROL_DE_OTRA_REGLA: %s" % control.get("regla"))
        k = len(control["sesiones"])
        sesion = {"sesion": k, "tipo": "reanudacion", "inicio_utc": _utc(), "pid": os.getpid(), "sistema": platform.platform()}
        control["sesiones"].append(sesion)
        need(_reemplazar(S / "control.json", control), "CONTROL_SIN_ACTUALIZAR")
        _reemplazar(S / "ejecutor.json", {"pid": os.getpid(), "creacion": _creacion_proceso(os.getpid()), "sesion": k, "desde_utc": _utc()})
        try:
            m = control["modo"]
            n = control["procesos_fam01"] if procesos_fam01 is None else procesos_fam01
            sesion.update(procesos_fam01=n, sistema_igual_al_inicio=sesion["sistema"] == control["sesiones"][0].get("sistema"))
            need(control["carpeta"] == Srel, "CORRIDA_EN_OTRA_CARPETA: control.json registra %s" % control["carpeta"])
            need(modo in (None, m), "MODO_DISTINTO_DEL_DE_LA_CORRIDA: la corrida es %s" % m)
            need(isinstance(n, int) and 1 <= n <= MAX_PROCESOS_FAM01, "PROCESOS_FAM01_FUERA_DE_1_A_%d" % MAX_PROCESOS_FAM01)
            sesion["en_curso_al_reanudar"] = sorted((_leer(S / "en_curso.json") or {}).keys())
            sesion["huerfanos_terminados"] = _terminar_huerfanos(S, Srel)
            v = huella_ejecucion()
            need(v["sha256"] == control["version"]["sha256"], "VERSION_DEL_PAQUETE_DISTINTA: la corrida empezó con %s y el paquete es %s"
                 % (control["version"]["sha256"], v["sha256"]))
            ent = _entorno()
            dif = sorted(x for x in set(ent) | set(control["entorno"]) if ent.get(x) != control["entorno"].get(x))
            need(not dif, "ENTORNO_DISTINTO: %s" % ", ".join(dif))
            need(sha_archivo(S / "plan.json") == control["plan"]["plan_json_sha256"], "PLAN_ALTERADO: plan.json no es el de la corrida")
            need(_manifiesto(S / "recetas") == control["plan"]["recetas"], "RECETAS_ALTERADAS: recetas/ no es el de la corrida")
            plan = json.loads((S / "plan.json").read_text(encoding="utf-8"))
            R = S / "reanudaciones" / ("%02d" % k)
            need(not R.exists(), "REANUDACION_YA_EXISTE: %s" % R.relative_to(S).as_posix())
            (R / "registro").mkdir(parents=True)
            Rrel = R.relative_to(BASE).as_posix()
            plan_k = _plan_de_la_corrida(Rrel, parser, R / "registro", m, control["procesos_fam01"], control.get("ensayo"))
            _escribir(R / "plan.json", plan_k)
            need(plan_k["cumple"], "PLAN_RECONSTRUIDO_NO_CUMPLE: %s" % R.relative_to(S).as_posix())
            need(_plan_comparable(plan_k, Rrel) == _plan_comparable(plan, Srel), "PLAN_RECONSTRUIDO_DISTINTO: el paquete ya no da el plan de la corrida")
            sesion["comprobaciones"] = {"version": v["sha256"], "entorno": "igual", "plan_json": "intacto", "recetas": "intactas",
                                        "plan_reconstruido": R.relative_to(S).as_posix() + "/plan.json (igual)"}
            pasos = plan["modos"][m]["pasos"]
            need(all(PurePosixPath(p["produce"]).is_relative_to(PurePosixPath(Srel)) for p in pasos), "SALIDA_FUERA_DE_LA_CORRIDA")
            ultimo, man, ampliada_por, ilegibles = _leer_diario(S / "estado_llamadas.jsonl")
            ok, motivo = _reutilizables(pasos, ultimo, man, ampliada_por)
            I = S / "intentos" / ("%02d" % k)
            movidos = _apartar(S, I, pasos, ok)
            sesion.update(reutilizadas=len(ok), a_repetir=len(pasos) - len(ok), lineas_ilegibles_del_diario=ilegibles,
                          motivos=dict(Counter(x if not x.startswith("se repite") else "depende de una llamada que se repite" for x in motivo.values())),
                          aceptadas_y_apartadas=sorted(i for i in motivo if (ultimo.get(i) or {}).get("tipo") == "llamada"
                                                       and ultimo[i]["e"].get("estado") == "aceptado"),
                          intentos=I.relative_to(S).as_posix() if movidos else None, apartados=len(movidos))
            need(_reemplazar(S / "control.json", control), "CONTROL_SIN_ACTUALIZAR")
        except Exception as e:
            sesion.update(rechazada=str(e) if isinstance(e, ErrorGeneral) else "%s: %s" % (type(e).__name__, e), fin_utc=_utc())
            _reemplazar(S / "control.json", control)
            raise
        diario = _Diario(S / "estado_llamadas.jsonl", k)
        try:
            for i in sesion["aceptadas_y_apartadas"]:
                diario.anotar({"tipo": "apartada", "id": i, "motivo": motivo[i]})
            previo = ({i: dict(ultimo[i]["e"], reutilizada={"sesion": ultimo[i]["sesion"]}) for i in ok}, {i: man[i] for i in ok})
            estado = ejecutar(plan, m, S, gancho=gancho, limites=limites, procesos_fam01=n, diario=diario, previo=previo)
        finally:
            diario.close()
        rean = {k_: sesion.get(k_) for k_ in ("reutilizadas", "a_repetir", "motivos", "huerfanos_terminados", "intentos", "comprobaciones")}
        return _cerrar(plan, m, S, Srel, estado, n, t0, control, k, rean)
    finally:
        _soltar_cerrojo(cerrojo)
