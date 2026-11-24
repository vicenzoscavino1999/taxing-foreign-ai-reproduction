"""Inicialización autenticada REUTILIZABLE (MEJORAS DE CÁLCULO 3.7, NO OFICIAL).

Qué se reutiliza: el RESULTADO de `s5_publicador.verify_products(root, política, recibo, autor)` (un dict JSON: S5,
D2, D6 y bundles verificados), que es el ~95 % de la preparación de cada trabajador (lectura y validación de
snapshots xlsx de los bundles CA2). Nada más: el resto de la preparación (contratos, D7, proveedores, entorno,
afirmaciones) se sigue ejecutando completo en cada proceso.

Cuándo se reutiliza (TODO debe coincidir, si no se recalcula con la verificación completa y se guarda otra entrada):
- `archivos`: sha256 del CONTENIDO de cada archivo que la verificación abrió (rastreo de open/io.open/os.open);
- `existencia`: tipo (archivo, directorio o ausente) de cada ruta que la verificación consultó (rastreo de os.stat y
  os.lstat; cubre exists/is_file/is_dir de pathlib y os.path), así que una transacción pendiente nueva la invalida;
- `listados`: nombres de cada directorio que la verificación listó (os.scandir/os.listdir: glob, iterdir, walk);
- `codigo`: sha256 de TODO el código del proyecto (`herramientas/**/*.py`, `src/**/*.py`) y de este módulo, es decir,
  del código validador y de todo lo que pueda importar;
- `python`: versión e intérprete (sha256 del ejecutable);
- `argumentos`: política, recibo y autor.
La clave es el sha256 canónico de todo lo anterior: una entrada solo sirve para ESA combinación exacta (no se pueden
mezclar entradas de versiones distintas). La entrada guarda además el sha256 de su resultado y se rechaza si no
coincide. No se usan rutas, fechas de modificación ni banderas de «ya verificado» como prueba: solo contenido.

Límite declarado: protege contra cambios de dependencias y corrupción accidental de la caché, no contra quien pueda
reescribir a la vez la caché y su sha256 dentro del área (el mismo actor podría alterar el código validador).
"""
from __future__ import annotations

import builtins
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

VERSION = "init-autenticada-1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


class Rastreo:
    """Registra archivos abiertos, rutas consultadas y directorios listados mientras está activo."""

    def __init__(self):
        self.abiertos, self.consultados, self.listados = set(), set(), set()
        self._orig = {}

    @staticmethod
    def _p(x):
        if isinstance(x, int):
            return None
        try:
            return os.path.abspath(os.fsdecode(os.fspath(x)))
        except TypeError:
            return None

    def __enter__(self):
        r = self
        o_open, o_ioopen, o_osopen = builtins.open, io.open, os.open
        o_stat, o_lstat, o_scandir, o_listdir = os.stat, os.lstat, os.scandir, os.listdir
        self._orig = {"open": o_open, "ioopen": o_ioopen, "osopen": o_osopen, "stat": o_stat, "lstat": o_lstat,
                      "scandir": o_scandir, "listdir": o_listdir}

        def w_open(f, *a, **k):
            p = r._p(f)
            if p:
                r.abiertos.add(p)
            return o_ioopen(f, *a, **k)

        def w_osopen(f, *a, **k):
            p = r._p(f)
            if p:
                r.abiertos.add(p)
            return o_osopen(f, *a, **k)

        def w_stat(f, *a, **k):
            p = r._p(f)
            if p:
                r.consultados.add(p)
            return o_stat(f, *a, **k)

        def w_lstat(f, *a, **k):
            p = r._p(f)
            if p:
                r.consultados.add(p)
            return o_lstat(f, *a, **k)

        def w_scandir(f=".", *a, **k):
            p = r._p(f)
            if p:
                r.listados.add(p)
            return o_scandir(f, *a, **k)

        def w_listdir(f=".", *a, **k):
            p = r._p(f)
            if p:
                r.listados.add(p)
            return o_listdir(f, *a, **k)
        builtins.open, io.open, os.open = w_open, w_open, w_osopen
        os.stat, os.lstat, os.scandir, os.listdir = w_stat, w_lstat, w_scandir, w_listdir
        return self

    def __exit__(self, *exc):
        o = self._orig
        builtins.open, io.open, os.open = o["open"], o["ioopen"], o["osopen"]
        os.stat, os.lstat, os.scandir, os.listdir = o["stat"], o["lstat"], o["scandir"], o["listdir"]
        return False


def _rel(root: Path, p: str) -> str:
    try:
        return Path(p).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "ABS:" + Path(p).as_posix()


def _abs(root: Path, r: str) -> Path:
    return Path(r[4:]) if r.startswith("ABS:") else root / r


def _tipo(p: Path) -> str:
    return "archivo" if p.is_file() else ("directorio" if p.is_dir() else "ausente")


def _hash_archivo(p: Path) -> str | None:
    try:
        return sha(p.read_bytes()) if p.is_file() else None
    except OSError:
        return None


def _listado(p: Path):
    try:
        return sorted(os.listdir(p))
    except OSError:
        return None


def huella_codigo(root: Path) -> dict:
    out = {}
    for base in ("herramientas", "src"):
        for q in sorted((root / base).rglob("*.py")):
            if "__pycache__" in q.parts:
                continue
            out[q.relative_to(root).as_posix()] = sha(q.read_bytes())
    out["MODULO_INIT:" + Path(__file__).name] = sha(Path(__file__).read_bytes())
    return out


def huella_python() -> dict:
    return {"version": sys.version, "ejecutable_sha256": sha(Path(sys.executable).read_bytes()), "init": VERSION}


def _dependencias(root: Path, rastreo: Rastreo) -> dict:
    prefijos = {os.path.abspath(p) for p in {sys.prefix, sys.base_prefix, sys.exec_prefix}}
    fuera_python = lambda p: not any(os.path.commonpath([p, q]) == q for q in prefijos if os.path.splitdrive(p)[0] == os.path.splitdrive(q)[0])  # noqa: E731
    arch = {}
    for p in sorted(rastreo.abiertos):
        if fuera_python(p) and os.path.isfile(p):
            arch[_rel(root, p)] = _hash_archivo(Path(p))
    exis = {}
    for p in sorted(rastreo.consultados | rastreo.abiertos):
        if fuera_python(p):
            exis[_rel(root, p)] = _tipo(Path(p))
    lis = {}
    for p in sorted(rastreo.listados):
        if fuera_python(p):
            lis[_rel(root, p)] = _listado(Path(p))
    return {"archivos": arch, "existencia": exis, "listados": lis}


def estado_actual(root: Path, deps: dict) -> dict:
    """Recalcula, desde el disco, el estado de exactamente las dependencias registradas."""
    return {"archivos": {r: _hash_archivo(_abs(root, r)) for r in deps["archivos"]},
            "existencia": {r: _tipo(_abs(root, r)) for r in deps["existencia"]},
            "listados": {r: _listado(_abs(root, r)) for r in deps["listados"]}}


def clave(args: list, deps: dict, codigo: dict, python: dict) -> str:
    return sha(canon({"argumentos": args, "dependencias": deps, "codigo": codigo, "python": python}))


def comprobar_entrada(root: Path, entrada: dict, args: list) -> tuple[bool, list]:
    """(válida, motivos). Recalcula TODO desde el contenido actual; ninguna comprobación se omite."""
    motivos = []
    if entrada.get("version") != VERSION:
        motivos.append("VERSION")
    if entrada.get("argumentos") != args:
        motivos.append("ARGUMENTOS")
    res = entrada.get("resultado")
    if sha(canon(res)) != entrada.get("resultado_sha256"):
        motivos.append("RESULTADO_ALTERADO")
    deps = entrada.get("dependencias") or {}
    act = estado_actual(root, deps)
    for parte in ("archivos", "existencia", "listados"):
        dif = sorted(r for r in deps.get(parte, {}) if deps[parte][r] != act[parte][r])
        if dif:
            motivos.append(f"{parte.upper()}_CAMBIADOS:{len(dif)}:" + ";".join(dif[:3]))
    cod = huella_codigo(root)
    if cod != entrada.get("codigo"):
        dif = sorted(set(cod) ^ set(entrada.get("codigo") or {}) | {k for k in cod if (entrada.get("codigo") or {}).get(k) != cod[k]})
        motivos.append(f"CODIGO_CAMBIADO:{len(dif)}:" + ";".join(dif[:3]))
    if huella_python() != entrada.get("python"):
        motivos.append("PYTHON_CAMBIADO")
    if not motivos and clave(args, deps, cod, entrada["python"]) != entrada.get("clave_sha256"):
        motivos.append("CLAVE")
    return (not motivos), motivos


def con_reutilizacion(root: Path, cache_dir: Path, fn, args: list, *, etiqueta: str):
    """Devuelve (resultado, info). Busca una entrada cuyo estado coincida EXACTAMENTE con el actual; si no la hay,
    ejecuta `fn(*args)` (verificación completa) bajo rastreo y guarda una entrada nueva."""
    t0 = time.time()
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    rechazos = []
    for q in sorted(cache_dir.glob("init_*.json")):
        try:
            entrada = json.loads(q.read_bytes())
        except (OSError, ValueError):
            rechazos.append({"archivo": q.name, "motivos": ["ILEGIBLE"]})
            continue
        ok, mot = comprobar_entrada(root, entrada, args)
        if ok:
            return entrada["resultado"], {"modo": "reutilizada", "entrada": q.name, "clave_sha256": entrada["clave_sha256"],
                                          "dependencias": {k: len(v) for k, v in entrada["dependencias"].items()},
                                          "segundos": round(time.time() - t0, 2), "rechazadas": rechazos}
        rechazos.append({"archivo": q.name, "motivos": mot})
    with Rastreo() as ras:
        res = fn(Path(root), *args)
    deps = _dependencias(Path(root), ras)
    cod, py = huella_codigo(Path(root)), huella_python()
    k = clave(args, deps, cod, py)
    entrada = {"version": VERSION, "etiqueta": etiqueta, "argumentos": args, "clave_sha256": k, "dependencias": deps, "codigo": cod,
               "python": py, "resultado": res, "resultado_sha256": sha(canon(res)),
               "creada_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    raw = json.dumps(entrada, indent=0, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    dest = cache_dir / f"init_{k[:16]}.json"
    tmp = dest.with_name(dest.name + ".tmp-%d" % os.getpid())
    tmp.write_bytes(raw)
    os.replace(tmp, dest)
    return res, {"modo": "calculada", "entrada": dest.name, "clave_sha256": k, "dependencias": {kk: len(v) for kk, v in deps.items()},
                 "segundos": round(time.time() - t0, 2), "rechazadas": rechazos}
