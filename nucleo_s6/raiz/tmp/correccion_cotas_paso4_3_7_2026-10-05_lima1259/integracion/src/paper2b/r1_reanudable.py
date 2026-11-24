"""R1 CERTIFICADO con avance recuperable, versión 4 (CONSOLIDACIÓN 3.7, NO OFICIAL) = versión 3 con:
- COMPROBACIÓN FINAL INDEPENDIENTE antes de `complete` (`comprobar_complete`), aplicada a TODAS las rutas (criterio
  estándar, direccional y local): recalcula desde los registros del último nivel la cobertura (cada caja activa con
  registro y ninguna sin resolver), la localización, el residuo de cada tramo (finito y <= tol_residual), que los
  extremos de cada tramo estén en su caja y la cota geométrica (finita y <= geometry_tol). Si algo falla: `incomplete`
  con motivo COMPROBACION_FINAL_FALLIDA y la lista de fallos en el diagnóstico. (En la versión 3 el residuo final se
  calculaba pero no se comparaba con la tolerancia.)
- Registro de la ruta local con la evidencia de aristas de r1_local v2, la configuración local y la versión del criterio.
La versión 3 = versión 2 + subdivisión LOCAL opcional en el último nivel (r1_local.py). Texto de la versión 2:

R1 CERTIFICADO con avance recuperable, versión 2 (CERTIFICACIÓN 3.7, NO OFICIAL).

Copia corregida de mejoras_calculo_3_7_2026-10-04/codigo/demo/r1_reanudable.py (que a su vez copia
paper2b.contour.level_set_certified con el mismo código por caja). Correcciones de la recuperación (hallazgos del
revisor a-d):
- CABECERA OBLIGATORIA: la primera línea COMPLETA debe ser JSON válido, de tipo `cabecera`, con suma propia correcta e
  identidad igual; si falta, está vacía, es inválida o no coincide -> CheckpointRechazado y NO se reutiliza nada.
- SOLO la escritura FINAL INCOMPLETA (bytes tras el último salto de línea) se recupera, y de forma explícita: sus bytes
  se guardan como evidencia en `<checkpoint>.corte-<k>.bin` (con fsync), el archivo se trunca al último salto de línea
  (fsync) y se añade un registro `corte_reparado` con tamaño, sha256 y nombre de la evidencia. Así la siguiente escritura
  empieza en línea nueva y nada queda concatenado.
- CORRUPCIÓN INTERIOR: cualquier línea COMPLETA (terminada en salto de línea) que no sea JSON válido o cuya suma `sha`
  no coincida -> rechazo controlado (CheckpointRechazado), aunque sea la última línea completa.
- DUPLICADOS: el mismo (nivel, i, j) o el mismo nivel registrado dos veces con contenido distinto (salvo `segundos`)
  -> rechazo; idénticos -> se aceptan y se cuentan.
- IDENTIDAD: la cabecera la fija el llamador y debe cubrir datos, código, parámetros y criterio; este módulo añade la
  versión del criterio y el sha256 de sus propios bytes.
Criterio opcional nuevo (`direcciones`): monotonía DIRECCIONAL (ver review/FUNDAMENTO_R1_DIRECCIONAL.md). Solo se intenta
si el criterio original (monotonía en x o en y) no resuelve la caja; si una dirección d tiene derivada direccional
encerrada sin cero, el conjunto de nivel en la caja es un grafo sobre la coordenada ortogonal a d y los cruces
certificados de las aristas, ordenados por esa coordenada, se emparejan consecutivamente.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path

from . import contour as R1M
from .contour import R1Result, _components_from_segments, _edge_roots
from .intervalos import Iv
from .supremum import axes

from . import r1_local as R1L

VERSION_CRITERIO = "level_set_certified/reanudable-5-integrado"
CODIGO_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class Interrupcion(Exception):
    """Interrupción simulada (prueba): se lanza DENTRO de una caja, antes de registrarla."""


class CheckpointRechazado(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def sellar(rec: dict) -> dict:
    r = {k: v for k, v in rec.items() if k != "sha"}
    r["sha"] = sha(canon(r))
    return r


def sello_ok(rec: dict) -> bool:
    return isinstance(rec, dict) and rec.get("sha") == sha(canon({k: v for k, v in rec.items() if k != "sha"}))


def _contenido(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if k not in ("sha", "segundos")}


class Checkpoint:
    def __init__(self, path, identidad: dict, *, escritor=None):
        self.path = Path(path) if path is not None else None
        self.identidad = dict(identidad, criterio=VERSION_CRITERIO, codigo_r1_sha256=CODIGO_SHA256)
        self.ident_sha = sha(canon(self.identidad))
        self.cajas, self.niveles = {}, {}
        self.duplicados_identicos = 0
        self.cortes_reparados = []
        self._escritor = escritor            # solo para pruebas de corte: escribe los bytes indicados
        self.memoria = path is None
        if self.memoria:
            self.recuperadas = 0
            return
        if self.path.exists() and self.path.stat().st_size > 0:
            self._cargar()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._cabecera()
        self.recuperadas = len(self.cajas)

    # ------------------------------------------------------------------------------------------- carga estricta
    def _cargar(self):
        raw = self.path.read_bytes()
        corte = raw.rfind(b"\n") + 1                    # bytes [corte:] = escritura final incompleta (si los hay)
        completas, cola = raw[:corte], raw[corte:]
        lineas = completas.split(b"\n")[:-1] if completas else []
        if not lineas:
            if cola:                                    # se cortó la escritura de la propia cabecera: nada que reutilizar
                self._reparar_cola(cola, 0, sin_cabecera=True)
                return
            raise CheckpointRechazado("CABECERA_AUSENTE")
        try:
            head = json.loads(lineas[0])
        except ValueError:
            raise CheckpointRechazado("CABECERA_INVALIDA: primera línea no es JSON válido") from None
        if not (isinstance(head, dict) and head.get("tipo") == "cabecera" and sello_ok(head)):
            raise CheckpointRechazado("CABECERA_INVALIDA: tipo o suma")
        if head.get("identidad_sha256") != self.ident_sha or sha(canon(head.get("identidad"))) != self.ident_sha:
            raise CheckpointRechazado("IDENTIDAD_DISTINTA: %s" % head.get("identidad_sha256"))
        for n, x in enumerate(lineas[1:], start=2):
            try:
                rec = json.loads(x)
            except ValueError:
                raise CheckpointRechazado("CORRUPCION_INTERIOR: línea %d no es JSON válido" % n) from None
            if not sello_ok(rec):
                raise CheckpointRechazado("CORRUPCION_INTERIOR: suma de la línea %d" % n)
            t = rec.get("tipo")
            if t == "caja":
                self._agregar(self.cajas, (rec["nivel"], rec["i"], rec["j"]), rec, n)
            elif t == "nivel":
                self._agregar(self.niveles, rec["nivel"], rec, n)
            elif t == "corte_reparado":
                self.cortes_reparados.append(rec)
            else:
                raise CheckpointRechazado("CORRUPCION_INTERIOR: tipo desconocido en la línea %d" % n)
        if cola:
            self._reparar_cola(cola, len(lineas) + 1)

    def _agregar(self, tabla, key, rec, n):
        if key in tabla:
            if _contenido(tabla[key]) != _contenido(rec):
                raise CheckpointRechazado("DUPLICADO_CONTRADICTORIO: %s en la línea %d" % (key, n))
            self.duplicados_identicos += 1
            return
        tabla[key] = rec

    def _reparar_cola(self, cola: bytes, linea: int, sin_cabecera: bool = False):
        k = 1
        while self.path.with_name(self.path.name + ".corte-%d.bin" % k).exists():
            k += 1
        ev = self.path.with_name(self.path.name + ".corte-%d.bin" % k)
        with open(ev, "wb") as fh:                      # 1) evidencia del corte, persistida
            fh.write(cola)
            fh.flush()
            os.fsync(fh.fileno())
        size = self.path.stat().st_size
        with open(self.path, "r+b") as fh:              # 2) truncar al último salto de línea, persistido
            fh.truncate(size - len(cola))
            fh.flush()
            os.fsync(fh.fileno())
        rec = {"tipo": "corte_reparado", "linea": linea, "bytes": len(cola), "sha256_bytes": sha(cola), "evidencia": ev.name,
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        if sin_cabecera:
            self._cabecera()
        self._escribir(sellar(rec))                     # 3) registro explícito de la reparación
        self.cortes_reparados.append(rec)

    # ------------------------------------------------------------------------------------------- escritura
    def _cabecera(self):
        self._escribir(sellar({"tipo": "cabecera", "identidad_sha256": self.ident_sha, "identidad": self.identidad,
                               "creado_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))

    def _escribir(self, rec):
        if self.memoria:
            return
        data = canon(rec) + b"\n"
        if self._escritor is not None:
            self._escritor(self.path, data)
            return
        with open(self.path, "ab") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())

    def caja(self, rec):
        rec = sellar(rec)
        self.cajas[(rec["nivel"], rec["i"], rec["j"])] = rec
        self._escribir(rec)

    def nivel(self, rec):
        rec = sellar(rec)
        self.niveles[rec["nivel"]] = rec
        self._escribir(rec)


class Contadores:
    def __init__(self):
        self.n, self.t = {}, {}

    def envolver(self, nombre, fn):
        def w(*a, **k):
            b = time.perf_counter()
            try:
                return fn(*a, **k)
            finally:
                self.n[nombre] = self.n.get(nombre, 0) + 1
                self.t[nombre] = self.t.get(nombre, 0.0) + time.perf_counter() - b
        return w

    def resumen(self):
        return {k: {"llamadas": self.n[k], "segundos": round(self.t[k], 2)} for k in sorted(self.n)}


def _cruces(edge, i, j, tol_residual):
    """Cruces certificados de las 4 aristas (mismo código que el original): (pts, motivo, no_localizada)."""
    pts = {}
    for axis, k, m in (("h", j, i), ("h", j + 1, i), ("v", i, j), ("v", i + 1, j)):
        rs, found = edge(axis, k, m)
        if rs.status != "complete":
            return None, "ARISTA_SIN_COBERTURA_CERTIFICADA", False
        if any(r.kind == "tangent" for _, r in found):
            return None, "CRUCE_TANGENTE", False
        if any(r.residual > tol_residual for _, r in found):
            return None, "RESIDUO_SOBRE_TOLERANCIA", True
        for pt, r in found:
            pts[(round(pt[0], 15), round(pt[1], 15))] = (pt, r)
    if len(pts) % 2:
        return None, "CRUCES_IMPARES", False
    return pts, None, False


def _direccion_adaptativa(ev, x0, x1, y0, y1):
    """Dirección d = bisectriz de los gradientes de rama del pliegue (ev.ramas), certificada si d·g_out y d·g_in
    excluyen 0 con el mismo signo en TODA la caja (min/max de funciones estrictamente monótonas a lo largo de d)."""
    ramas = getattr(ev, "ramas", None)
    if ramas is None:
        return None
    _, g, br = ramas(x0, x1, y0, y1)
    if g is None or br is None or br.get("kind") not in ("min", "max"):
        return None
    xm, ym = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    _, _, brc = ramas(xm, xm, ym, ym)
    if brc is None or brc.get("kind") not in ("min", "max"):
        brc = br
    mid = lambda v: 0.5 * (v.lo + v.hi)  # noqa: E731
    vo = (mid(brc["g_out"][0]), mid(brc["g_out"][1]))
    vi = (mid(brc["g_in"][0]), mid(brc["g_in"][1]))
    no, ni = math.hypot(*vo), math.hypot(*vi)
    if no == 0 or ni == 0:
        return None
    sx, sy = vo[0] / no + vi[0] / ni, vo[1] / no + vi[1] / ni
    ns = math.hypot(sx, sy)
    if ns == 0:
        return None
    d = (sx / ns, sy / ns)
    comb = lambda G: Iv(d[0], d[0]) * G[0] + Iv(d[1], d[1]) * G[1]  # noqa: E731
    bo, bi = comb(br["g_out"]), comb(br["g_in"])
    sg = lambda v: 1 if v.lo > 0 else (-1 if v.hi < 0 else 0)  # noqa: E731
    return d if sg(bo) != 0 and sg(bo) == sg(bi) else None


def evaluar_caja(f, ev, X, Y, i, j, edge, tol_residual, cont: Contadores, fallo=None, direcciones=None, local=None):
    """Una caja del nivel: criterio ORIGINAL (vacía; monotonía en y o en x) y, si no resuelve y se piden direcciones,
    el criterio DIRECCIONAL. Devuelve el registro."""
    x0, x1, y0, y1 = X(i), X(i + 1), Y(j), Y(j + 1)
    if cont.envolver("rango", ev.range)(x0, x1, y0, y1).excludes_zero():
        return {"resultado": "vacia"}
    if fallo is not None:
        fallo()
    mono_y = cont.envolver("derivada_y", ev.dy)(x0, x1, y0, y1).excludes_zero()
    mono_x = (not mono_y) and cont.envolver("derivada_x", ev.dx)(x0, x1, y0, y1).excludes_zero()
    dsel = None
    if not (mono_x or mono_y):
        if direcciones and getattr(ev, "ddir", None) is not None:
            for k, d in enumerate(direcciones):
                if cont.envolver("derivada_direccional", ev.ddir)(x0, x1, y0, y1, d).excludes_zero():
                    dsel = (k, d)
                    break
        if dsel is None and local:
            # v3: subdivisión LOCAL (solo en el último nivel) con las aristas COMPLETAS de la madre, compartidas con las vecinas
            loc = R1L.resolver(f, ev, (x0, x1, y0, y1), {"abajo": edge("h", j, i), "arriba": edge("h", j + 1, i),
                                                         "izq": edge("v", i, j), "der": edge("v", i + 1, j)},
                               tol_residual, m=local["m"], profundidad=local["profundidad"])
            comun = {"local": loc["estadisticas"], "config_local": dict(local), "criterio": VERSION_CRITERIO,
                     "evidencia_aristas": loc["evidencia"]}
            if loc["resultado"] == "resuelta":
                return dict(comun, resultado="resuelta", piezas=loc["piezas"], diag=loc["diag"], monotonia="local")
            ad = _direccion_adaptativa(ev, x0, x1, y0, y1)
            if ad is not None:
                pts, motivo, no_loc = _cruces(edge, i, j, tol_residual)
                if pts is not None:
                    d0, d1 = ad
                    order = sorted(pts.values(), key=lambda pr: (-d1 * pr[0][0] + d0 * pr[0][1], d0 * pr[0][0] + d1 * pr[0][1]))
                    piezas = [[list(order[q][0]), list(order[q + 1][0]), max(order[q][1].residual, order[q + 1][1].residual)]
                              for q in range(0, len(order), 2)]
                    dg = math.hypot(x1 - x0, y1 - y0) if order else 0.0
                    if not R1L.comprobar_resuelta((x0, x1, y0, y1), piezas, dg, tol_residual):
                        return dict(comun, resultado="resuelta", piezas=piezas, diag=dg, monotonia="direccional_adaptativa_por_ramas",
                                    direccion=list(ad))
            return dict(comun, resultado="sin_resolver", motivo="LOCAL_PENDIENTE: " + ";".join(loc["motivos"]))
        if dsel is None:
            return {"resultado": "sin_resolver", "motivo": "SIN_MONOTONIA_CERTIFICADA (rango contiene 0; dx y dy contienen 0"
                    + ("; ninguna dirección declarada excluye 0)" if direcciones else ")")}
    pts, motivo, no_loc = _cruces(edge, i, j, tol_residual)
    if pts is None:
        return {"resultado": "sin_resolver", "motivo": motivo, "no_localizada": no_loc}
    if dsel is None:
        key = (lambda pr: (pr[0][0], pr[0][1])) if mono_y else (lambda pr: (pr[0][1], pr[0][0]))
        mono = "y" if mono_y else "x"
    else:
        d0, d1 = dsel[1]
        # coordenada ortogonal a d: t = -d1 x + d0 y; desempate por la coordenada a lo largo de d
        key = (lambda pr, d0=d0, d1=d1: (-d1 * pr[0][0] + d0 * pr[0][1], d0 * pr[0][0] + d1 * pr[0][1]))
        mono = "direccional:%d" % dsel[0]
    order = sorted(pts.values(), key=key)
    piezas = [[list(order[q][0]), list(order[q + 1][0]), max(order[q][1].residual, order[q + 1][1].residual)]
              for q in range(0, len(order), 2)]
    return {"resultado": "resuelta", "piezas": piezas, "diag": math.hypot(x1 - x0, y1 - y0) if order else 0.0, "monotonia": mono}


def comprobar_complete(registros, X, Y, geometry_tol, tol_residual, no_localizada=False):
    """Comprobación INDEPENDIENTE de las condiciones necesarias para `complete`, desde los registros del último nivel
    {(i, j): registro o None} (todas las cajas activas del nivel). Devuelve la lista de fallos (vacía = se cumplen)."""
    fallos = []
    if no_localizada:
        fallos.append("LOCALIZACION: algún cruce no localizado")
    diag = 0.0
    for (i, j), rec in sorted(registros.items()):
        if rec is None:
            fallos.append("COBERTURA: caja %d,%d sin registro" % (i, j))
            continue
        if rec.get("resultado") not in ("vacia", "resuelta"):
            fallos.append("COBERTURA: caja %d,%d %s" % (i, j, rec.get("resultado")))
            continue
        if rec["resultado"] == "vacia":
            continue
        x0, x1, y0, y1 = X(i), X(i + 1), Y(j), Y(j + 1)
        piezas = rec.get("piezas") or []
        if len(piezas) == 0:
            continue
        d = rec.get("diag")
        if not (isinstance(d, (int, float)) and math.isfinite(d) and 0 < d <= math.hypot(x1 - x0, y1 - y0) * (1 + 1e-12)):
            fallos.append("GEOMETRIA: caja %d,%d cota %r" % (i, j, d))
        else:
            diag = max(diag, d)
        for k, (pa, pb, rr) in enumerate(piezas):
            for x, y in (pa, pb):
                if not (x0 <= x <= x1 and y0 <= y <= y1):
                    fallos.append("GEOMETRIA: caja %d,%d tramo %d fuera de la caja" % (i, j, k))
            if not (isinstance(rr, (int, float)) and math.isfinite(rr) and rr <= tol_residual):
                fallos.append("RESIDUO: caja %d,%d tramo %d residuo %r > %r" % (i, j, k, rr, tol_residual))
    if not diag <= geometry_tol:
        fallos.append("GEOMETRIA: cota %r > tolerancia %r" % (diag, geometry_tol))
    return fallos


def level_set_reanudable(f, instrument: str, bar_d: float, bar_f: float, ev, *, n0: int = 4, max_level: int = 6,
                         geometry_tol: float = 1e-3, tol_residual: float = 1e-9, checkpoint: Checkpoint,
                         plazo: float | None = None, fallo_en: int | None = None, progreso=None, direcciones=None,
                         caja=None, local=None) -> R1Result:
    box = caja if caja is not None else axes(instrument, bar_d, bar_f)
    (dl, dh), (fl, fh) = box
    if dh == dl or fh == fl:
        return R1M._level_set_certified_original(f, instrument, bar_d, bar_f, ev, n0=n0, max_level=max_level,
                                       geometry_tol=geometry_tol, tol_residual=tol_residual)
    cont = Contadores()
    res = R1Result()
    res.certified = True
    active = [(i, j) for i in range(n0) for j in range(n0)]
    not_localized = False
    nuevas = [0]
    diag_info = {"recuperadas_del_checkpoint": checkpoint.recuperadas, "cortes_reparados": len(checkpoint.cortes_reparados),
                 "duplicados_identicos": checkpoint.duplicados_identicos, "evaluadas_ahora": 0, "reutilizadas": 0}
    for level in range(max_level + 1):
        N = n0 * (2 ** level)
        X = lambda i, N=N: dl + (dh - dl) * i / N  # noqa: E731
        Y = lambda j, N=N: fl + (fh - fl) * j / N  # noqa: E731
        unresolved, pieces, diag, kept = [], [], 0.0, []
        edge_cache = {}
        aristas = cont.envolver("raices_arista", _edge_roots)

        def edge(axis, k, m, X=X, Y=Y, edge_cache=edge_cache):
            key = (axis, k, m)
            if key not in edge_cache:
                if axis == "h":
                    edge_cache[key] = aristas(f, ev, "y", Y(k), X(m), X(m + 1), tol_residual)
                else:
                    edge_cache[key] = aristas(f, ev, "x", X(k), Y(m), Y(m + 1), tol_residual)
            return edge_cache[key]
        motivos = {}
        for pos, (i, j) in enumerate(active):
            rec = checkpoint.cajas.get((level, i, j))
            if rec is None:
                if plazo is not None and time.time() > plazo:
                    res.status, res.reason = "incomplete", "R1_INTERRUMPIDO_CON_CHECKPOINT"
                    res.n = N
                    res.diagnostics = dict(diag_info, nivel=level, cajas_del_nivel=len(active), hechas_en_el_nivel=pos,
                                           cola_pendiente=len(active) - pos, evaluaciones=cont.resumen(), motivos=motivos)
                    return res
                fallo = None
                if fallo_en is not None and nuevas[0] + 1 >= fallo_en:      # primera caja NO vacía desde la k-ésima
                    def fallo():
                        raise Interrupcion("interrupción simulada dentro de la caja %d" % fallo_en)
                b = time.perf_counter()
                out = evaluar_caja(f, ev, X, Y, i, j, edge, tol_residual, cont, fallo=fallo, direcciones=direcciones,
                                   local=local if level == max_level else None)
                rec = dict(out, tipo="caja", nivel=level, i=i, j=j, N=N, segundos=round(time.perf_counter() - b, 3))
                checkpoint.caja(rec)
                nuevas[0] += 1
                diag_info["evaluadas_ahora"] += 1
                if progreso:
                    progreso({"nivel": level, "caja": [i, j], "pos": pos + 1, "de": len(active), "resultado": rec["resultado"],
                              "motivo": rec.get("motivo"), "monotonia": rec.get("monotonia"), "segundos": rec["segundos"]})
            else:
                diag_info["reutilizadas"] += 1
            if rec["resultado"] == "vacia":
                continue
            kept.append((i, j))
            if rec["resultado"] == "sin_resolver":
                motivos[rec["motivo"]] = motivos.get(rec["motivo"], 0) + 1
                if rec.get("no_localizada"):
                    not_localized = True
                unresolved.append((X(i), X(i + 1), Y(j), Y(j + 1)))
                continue
            for pa, pb, rr in rec["piezas"]:
                pieces.append((tuple(pa), tuple(pb), rr))
            if rec["piezas"]:
                diag = max(diag, rec["diag"])
        if level not in checkpoint.niveles:
            checkpoint.nivel({"tipo": "nivel", "nivel": level, "N": N, "cajas": len(active), "conservadas": len(kept),
                              "sin_resolver": len(unresolved), "diag": diag, "motivos": motivos})
        active_final = list(active)
        active = [(2 * i + a, 2 * j + b) for i, j in kept for a in (0, 1) for b in (0, 1)]
        res.n = N
        if (unresolved or diag > geometry_tol) and level < max_level:
            continue
        res.diagnostics = dict(diag_info, nivel=level, evaluaciones=cont.resumen(), motivos=motivos)
        if unresolved:
            res.status = "incomplete"
            res.reason = "EDGE_CROSSING_NOT_LOCALIZED" if not_localized else "CONTOUR_BOXES_UNRESOLVED"
            res.diagnostics.update(cajas_sin_resolver=len(unresolved), tolerancia_residuo=tol_residual)
            return res
        if diag > geometry_tol:
            res.status, res.reason, res.geometry_error_bound = "incomplete", "GEOMETRY_TOLERANCE_NOT_REACHED", diag
            return res
        fallos = comprobar_complete({(i, j): checkpoint.cajas.get((level, i, j)) for i, j in active_final}, X, Y,
                                    geometry_tol, tol_residual, not_localized)
        if fallos:
            res.status, res.reason = "incomplete", "COMPROBACION_FINAL_FALLIDA"
            res.diagnostics.update(comprobacion_final=fallos[:50], n_fallos=len(fallos))
            return res
        keyof, points = {}, {}
        for (pa, pb, _) in pieces:
            for pt in (pa, pb):
                k = ("q", round(pt[0], 12), round(pt[1], 12))
                keyof[pt] = k
                points.setdefault(k, (k, pt, "certificada"))
        segs = [(keyof[pa], keyof[pb]) for pa, pb, _ in pieces]
        res.components = _components_from_segments(points, segs, box, lambda x, y: abs(f(x, y)))
        for c in res.components:
            for e in c.edges:
                e.geometric_error_bound = diag
        res.geometry_error_bound = diag
        res.residual_bound = max((r for _, _, r in pieces), default=0.0)
        res.topology_stable = True
        res.status, res.reason = "complete", None
        return res
    return res
