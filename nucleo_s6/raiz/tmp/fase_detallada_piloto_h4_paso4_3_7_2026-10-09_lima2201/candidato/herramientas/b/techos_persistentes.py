"""CANDIDATO (CIERRE CACHE CUPOS H4 3.7; contrato v2.1 en CACHE FINAL P0 H4 3.7, NO OFICIAL): caché PERSISTENTE de techos C2
entre procesos de UNA MISMA corrida. Formato de documento «techo-persistente-v2»; CONTRATO de validación «v2.1». Una sola
implementación activa. TODA entrada, la escribiera quien la escribiera, se valida con el contrato vigente al leerla: ninguna
entrada antigua se salta la validación nueva. El esquema v1 se RECHAZA (nunca se consume por conveniencia).

v2.1 añade dos vínculos (dictamen del revisor sobre v2):
8. DISPONIBILIDAD derivada del CONSUMIDOR auténtico, nunca de la entrada: al vincular, se audita el código de Run.ceiling
   (núcleo): debe ser el ÚNICO lector de techos_compartidos y debe pedir el techo al proveedor con available=True literal.
   Por tanto una entrada «no aplicable» contradice la solicitud y se rechaza. Los no aplicables legítimos los construye el
   núcleo a nivel de fila (Run.build_frontiers/ceiling_rows con structural_only) SIN pasar por esta caché, y no cambian.
9. PUNTO vinculado al VALOR declarado con el proveedor autorizado y su semántica numérica EXACTA (sin tolerancia): en el
   proveedor certificado (sup_bound) el valor del supremo es value(x, y) = model.revenue(estado, x, y, diseño) en el punto
   devuelto, y la cota inferior es el extremo inferior del encierro puntual del motor en ese punto (Engine.R sin Phi). Se
   comprueban ambas igualdades; no se repite la optimización global.

Run.ceiling (núcleo, sin cambios) consulta `techos_compartidos.get(compat_techo(skey))` y, si no hay techo, lo calcula y lo
guarda con `techos_compartidos[clave] = hit`. Esta clase ofrece esa interfaz, persistida en disco, y la VINCULA a la
solicitud: el almacén se ata (vincular) al Run de la corrida y, con él, reconstruye las relaciones deterministas de cada
entrada antes de consumirla. El checksum escrito junto al contenido y una clave copiada NO bastan:

1. Esquema, tipos, cardinalidades y FINITUD de todo lo que se consume, ANTES de convertir, dividir o construir objetos
   (el JSON con NaN/Infinity se rechaza al leerlo). Toda entrada defectuosa -> EntradaInvalida (rechazo controlado), se
   aparta como .rechazada y se recalcula; nunca TypeError/ZeroDivisionError hacia el consumidor.
2. Identidad completa de la corrida (EjecutorSeleccion.ident) campo por campo; otra identidad (p. ej. R2) usa otro
   directorio y nunca reutiliza.
3. Payload VINCULADO a la clave pedida: clave == compat_techo(C.key("structural", payload)) recalculadas con el Run
   vinculado. Así el diseño, el menú, el dominio τ, la teoría, las técnicas y las 13 primitivas son las de la solicitud.
4. Barras vinculadas al dominio τ del payload (keys.tau_domain) y dentro de [0, 1); el eje inactivo del menú no entra en la
   clave del núcleo (tampoco en su caché de proceso) y solo se exige finito y en dominio.
5. Estado RECONSTRUIDO desde las primitivas del payload con el proveedor (model.state) e igual campo a campo al guardado; se
   devuelve el reconstruido. B_pot = estado.B_pot > 0.
6. Techo: solo el proveedor certificado modelo_teorico_v2_2 (cota de rama y cota). Se reconstruyen sus relaciones:
   lower <= sup <= upper; punto (tau_d, tau_f) dentro de los ejes del menú; C2 = sup/B_pot; error normalizado = el que
   resulta de las cotas con la MISMA aritmética de intervalos del proveedor (B_pot como intervalo, redondeo hacia fuera);
   error absoluto = error·B_pot; y el estado (complete / incomplete y su motivo, convergido) es exactamente el que fijan
   alcanzado, error y tolerancia contractual (tol_converge). Un resultado incompleto válido se devuelve INCOMPLETO.
   Instrumento no disponible: solo la forma not_applicable del proveedor.
7. El mismo contrato en ESCRITURA (lo que no pasa no se escribe; el proceso conserva su propio cálculo) y en LECTURA, y el
   consumidor recibe objetos reconstruidos de lo validado.
Concurrencia: candado por clave (os.mkdir) con dueño (pid, hora de creación del proceso, token). Una segunda solicitud
ESPERA y reutiliza; una espera agotada lanza EsperaAgotada (estado controlado: no inicia un cálculo duplicado). Solo se
libera el candado PROPIO (token); uno huérfano (dueño muerto o reserva sin dueño tras GRACIA_S) se recupera. Los candados
propios se liberan también ante errores del cálculo (liberar_propios, que llama el ejecutor) y al salir del proceso.
Solo guarda resultados CANDIDATOS de esta corrida: no promueve nada a oficial ni sirve entre corridas distintas.
"""
from __future__ import annotations

import atexit
import ctypes
import hashlib
import json
import math
import os
import time
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

ESQUEMA = "techo-persistente-v2"
ESQUEMAS_RECHAZADOS = {"techo-persistente-v1": "ESQUEMA_V1_INCOMPATIBLE"}
PROVEEDOR = "modelo_teorico_v2_2"
GRACIA_S = 30.0
CAMPOS_DOC = ("esquema", "corrida_sha256", "identidad_corrida", "clave_compat", "contenido", "contenido_sha256", "productor")
CAMPOS_STATE = ("a", "rho", "kappa0", "beta", "delta", "theta", "gamma", "z_m", "eta_d", "eta_f", "phi", "t", "c_legal")
CAMPOS_CEILING = ("instrument_available", "sup", "C2", "B_pot", "numerical_error", "status", "reason")
CAMPOS_SUP = ("sup", "attained", "tau_d", "tau_f", "lateral_low", "lateral_high", "witnesses", "level_values", "numerical_error", "converged",
              "status", "reason", "evaluations", "lateral_axis", "final_n", "error_kind", "upper", "lower", "n_jump_points")
CAMPOS_PAYLOAD = ("kind", "values", "design_v", "instrument_j", "tau_domain", "theory_sha256", "technical")
CAMPOS_VALOR = ("parameter_id", "value", "value_unit")


def canon(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class EntradaInvalida(Exception):
    """Entrada de la caché que no cumple el contrato: se aparta y se recalcula (rechazo controlado)."""


class EsperaAgotada(RuntimeError):
    """Otro proceso de la corrida calcula esta clave y la espera superó su límite: estado controlado, sin cálculo duplicado."""


class AlmacenNoVinculado(RuntimeError):
    """El almacén se usó sin vincularlo al Run de la corrida (error de integración, no de una entrada)."""


def _need(t, code):
    if not t:
        raise EntradaInvalida(code)


def _num(x, code):
    _need(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x), code)
    return float(x)


def _no_finito(c):
    raise EntradaInvalida("NO_FINITO_EN_JSON:%s" % c)


# ------------------------------------------------------------------------------------------------- procesos (dueños)
_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.OpenProcess.restype = ctypes.c_void_p


class _FT(ctypes.Structure):
    _fields_ = [("lo", ctypes.c_uint32), ("hi", ctypes.c_uint32)]


def _creacion(pid):
    try:
        h = _k32.OpenProcess(0x1000, False, int(pid))
    except (TypeError, ValueError, OverflowError):
        return None
    if not h:
        return None
    try:
        c, e, k, u = _FT(), _FT(), _FT(), _FT()
        if not _k32.GetProcessTimes(ctypes.c_void_p(h), ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u)):
            return None
        code = ctypes.c_ulong()
        if not _k32.GetExitCodeProcess(ctypes.c_void_p(h), ctypes.byref(code)) or code.value != 259:
            return None
        return (c.hi << 32) | c.lo
    finally:
        _k32.CloseHandle(ctypes.c_void_p(h))


def _vivo(pid, creado) -> bool:
    return creado is not None and _creacion(pid) == creado


# ------------------------------------------------------------------------------------------------- vínculo con el Run
class Verificador:
    """Relaciones deterministas de la corrida, tomadas del Run vinculado (todas las de una corrida comparten run_id,
    contratos, proveedor y SupConfig)."""

    def __init__(self, run):
        m = run.model
        if getattr(m, "kind", None) != PROVEEDOR or not bool(getattr(m, "certified", False)):
            raise AlmacenNoVinculado("PROVEEDOR_NO_SOPORTADO:%s" % getattr(m, "kind", None))
        self.clave_estructural = lambda payload: run.C.key("structural", payload)
        self.compat = run.compat_techo
        self.state = m.state
        self.ids = sorted(run.C.K["structural_primitive_ids"])
        self.tol = float(run.cfg.sup.tol_converge)
        self.disponible = disponibilidad_del_consumidor(type(run))
        self.revenue = None
        self.engine = None
        from paper2b import encierros_modelo as EM
        from paper2b import model as M
        self.revenue = M.revenue
        self.engine = lambda st, dis: EM.Engine(EM.IParams.from_state(st), dis)
        self.firma = sha(canon({"run_id": run.run_id, "sup": run.cfg.sup.as_dict(), "modelo": m.kind, "garantia": m.garantia,
                                "cajas": getattr(m, "sup_max_boxes", None), "saltos": getattr(m, "jump_budget", None), "ids": self.ids,
                                "disponible": self.disponible}))


def disponibilidad_del_consumidor(clase_run):
    """Disponibilidad que pide el ÚNICO consumidor de la caché (Run.ceiling), leída de su código (AST), no de la entrada.
    Exige: (a) en el módulo del Run, solo Run.ceiling lee techos_compartidos (.get); (b) Run.ceiling llama
    self.model.capture_ceiling con el 6.º argumento posicional igual a una constante booleana. Si no, el almacén no se
    vincula (consumidor no auditado)."""
    import ast
    import inspect
    import sys as _sys
    arbol = ast.parse(inspect.getsource(_sys.modules[clase_run.__module__]))
    lectores = set()
    for cls in (n for n in arbol.body if isinstance(n, ast.ClassDef) and n.name == clase_run.__name__):
        for f in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
            for c in ast.walk(f):
                if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "get" and isinstance(c.func.value, ast.Attribute)
                        and c.func.value.attr == "techos_compartidos"):
                    lectores.add(f.name)
    if lectores != {"ceiling"}:
        raise AlmacenNoVinculado("CONSUMIDOR_NO_AUDITADO:lectores=%s" % sorted(lectores))
    valores = set()
    for cls in (n for n in arbol.body if isinstance(n, ast.ClassDef) and n.name == clase_run.__name__):
        for f in (n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "ceiling"):
            for c in ast.walk(f):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "capture_ceiling":
                    if len(c.args) < 6 or not (isinstance(c.args[5], ast.Constant) and isinstance(c.args[5].value, bool)):
                        raise AlmacenNoVinculado("CONSUMIDOR_NO_AUDITADO:disponibilidad_no_constante")
                    valores.add(c.args[5].value)
    if len(valores) != 1:
        raise AlmacenNoVinculado("CONSUMIDOR_NO_AUDITADO:llamadas=%s" % sorted(valores))
    return valores.pop()


class AlmacenTechos:
    """Interfaz de diccionario que usa Run.ceiling (get / __setitem__), persistida por corrida y vinculada a su Run."""

    def __init__(self, raiz, ident_corrida: dict, *, espera_max_s: float = 1800.0, sondeo_s: float = 1.0):
        self.ident = json.loads(canon(ident_corrida))
        self.corrida_sha256 = sha(canon(self.ident))
        self.dir = Path(raiz) / self.corrida_sha256
        self.dir.mkdir(parents=True, exist_ok=True)
        idf = self.dir / "corrida.json"
        if not idf.exists():
            self._atomico(idf, canon({"esquema": ESQUEMA, "corrida_sha256": self.corrida_sha256, "identidad": self.ident}))
        self.espera_max_s, self.sondeo_s = float(espera_max_s), float(sondeo_s)
        self.verif = None
        self._propios = {}             # clave -> (token, instante de la reserva): candados de ESTE proceso
        self.memoria = {}              # misma semántica que el dict del proceso
        self._yo = (os.getpid(), _creacion(os.getpid()))
        self.estadistica = {"aciertos_disco": 0, "aciertos_memoria": 0, "calculos": 0, "esperas": 0, "rechazos": 0, "candados_recuperados": 0,
                            "escrituras_rechazadas": 0, "esperas_agotadas": 0, "candados_liberados_por_error": 0}
        atexit.register(self.liberar_propios, "salida_del_proceso")

    # ------------------------------------------------------------------------------------------------- vínculo
    def vincular(self, run):
        v = Verificador(run)
        if self.verif is None:
            self.verif = v
            self._evento(evento="vinculo", firma=v.firma)
        elif v.firma != self.verif.firma:
            raise AlmacenNoVinculado("RUN_DE_OTRA_CONFIGURACION")

    def _exigir_vinculo(self):
        if self.verif is None:
            raise AlmacenNoVinculado("ALMACEN_SIN_VINCULAR")

    # ------------------------------------------------------------------------------------------------- rutas y registro
    def _f(self, clave):
        if not (isinstance(clave, str) and len(clave) == 64 and all(c in "0123456789abcdef" for c in clave)):
            raise ValueError("CLAVE_MAL_FORMADA")
        return self.dir / (clave + ".json")

    def _candado(self, clave):
        return self.dir / (clave + ".candado")

    def _evento(self, **kw):
        kw.update(t_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), t=round(time.time(), 3), pid=os.getpid())
        with open(self.dir / "eventos.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")

    @staticmethod
    def _atomico(p: Path, data: bytes):
        tmp = p.with_name("." + p.name + "." + uuid.uuid4().hex + ".tmp")
        try:
            with open(tmp, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, p)
        finally:
            if tmp.exists():
                tmp.unlink()

    # ------------------------------------------------------------------------------------------------- serialización
    @staticmethod
    def contenido(hit) -> dict:
        st, ce = hit["state"], hit["ceiling"]
        _need(type(st).__name__ == "State" and type(ce).__name__ == "Ceiling", "TIPO_NO_PERSISTIBLE")
        sup = None
        if ce.sup is not None:
            _need(not ce.sup.evaluations, "EVALUACIONES_NO_PERSISTIBLES")
            sup = {k: getattr(ce.sup, k) for k in CAMPOS_SUP}
            sup["witnesses"] = [dict(vars(w)) for w in ce.sup.witnesses]
        return {"state": {k: getattr(st, k) for k in CAMPOS_STATE}, "ceiling": dict({k: getattr(ce, k) for k in CAMPOS_CEILING if k != "sup"}, sup=sup),
                "payload": hit["payload"], "bars": list(hit["bars"])}

    def documento(self, clave, hit, segundos=None) -> bytes:
        try:
            c = json.loads(canon(self.contenido(hit)))
        except ValueError as e:                    # NaN/Infinity: allow_nan=False
            raise EntradaInvalida("NO_FINITO_AL_ESCRIBIR:%s" % e)
        return canon({"esquema": ESQUEMA, "corrida_sha256": self.corrida_sha256, "identidad_corrida": self.ident, "clave_compat": clave,
                      "contenido": c, "contenido_sha256": sha(canon(c)),
                      "productor": {"pid": os.getpid(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "segundos_calculo": segundos}})

    # ------------------------------------------------------------------------------------------------- validación
    def _validar(self, clave, raw: bytes):
        """Valida una entrada contra el contrato y la solicitud y reconstruye el hit. Toda discrepancia -> EntradaInvalida."""
        self._exigir_vinculo()
        try:
            return self._validar_contrato(clave, raw)
        except EntradaInvalida:
            raise
        except Exception as e:  # noqa: BLE001 — defensa en profundidad: ninguna excepción no prevista llega al consumidor
            raise EntradaInvalida("EXCEPCION_NO_PREVISTA:%s" % type(e).__name__)

    def _validar_contrato(self, clave, raw):
        from paper2b import frontier as FR
        from paper2b import keys as K
        from paper2b import supremum as SU
        from paper2b.encierros_modelo import IParams
        from paper2b.intervalos import Iv
        V = self.verif
        try:
            d = json.loads(raw, parse_constant=_no_finito)
        except (ValueError, UnicodeDecodeError):
            raise EntradaInvalida("JSON_ILEGIBLE")
        _need(isinstance(d, dict), "DOCUMENTO_TIPO")
        esq = d.get("esquema")
        if esq in ESQUEMAS_RECHAZADOS:
            raise EntradaInvalida(ESQUEMAS_RECHAZADOS[esq])
        _need(esq == ESQUEMA, "ESQUEMA_DESCONOCIDO")
        _need(set(d) == set(CAMPOS_DOC), "DOCUMENTO_CAMPOS")
        _need(d["corrida_sha256"] == self.corrida_sha256 and d["identidad_corrida"] == self.ident, "IDENTIDAD_CORRIDA_DISTINTA")
        _need(d["clave_compat"] == clave, "CLAVE_DISTINTA")
        c = d["contenido"]
        _need(isinstance(c, dict) and set(c) == {"state", "ceiling", "payload", "bars"}, "CONTENIDO_CAMPOS")
        _need(isinstance(d["contenido_sha256"], str) and sha(canon(c)) == d["contenido_sha256"], "CONTENIDO_ALTERADO")
        # --- payload y su vínculo con la clave pedida
        pl = c["payload"]
        _need(isinstance(pl, dict) and set(pl) == set(CAMPOS_PAYLOAD), "PAYLOAD_CAMPOS")
        _need(pl["kind"] == "structural-v2", "PAYLOAD_TIPO")
        _need(pl["design_v"] in ("G", "N") and pl["instrument_j"] in ("d", "f", "df"), "PAYLOAD_DISENO_O_MENU")
        vals = pl["values"]
        _need(isinstance(vals, list) and all(isinstance(r, dict) and set(r) == set(CAMPOS_VALOR) and isinstance(r["parameter_id"], str)
                                              and isinstance(r["value"], str) for r in vals), "PAYLOAD_VALORES")
        _need([r["parameter_id"] for r in vals] == V.ids, "PAYLOAD_PRIMITIVAS")
        prims = {}
        for r in vals:
            try:
                x = Decimal(r["value"])
            except InvalidOperation:
                raise EntradaInvalida("PAYLOAD_VALOR_NO_NUMERICO")
            _need(x.is_finite(), "PAYLOAD_VALOR_NO_FINITO")
            prims[r["parameter_id"]] = float(x)
        _need(isinstance(pl["tau_domain"], dict), "PAYLOAD_DOMINIO")
        _need(V.compat(V.clave_estructural(pl)) == clave, "PAYLOAD_NO_VINCULADO_A_LA_CLAVE")
        # --- barras vinculadas al dominio τ
        b = c["bars"]
        _need(isinstance(b, list) and len(b) == 2, "BARRAS_CARDINALIDAD")
        bd, bf = _num(b[0], "BARRA_NO_FINITA"), _num(b[1], "BARRA_NO_FINITA")
        _need(0.0 <= bd < 1.0 and 0.0 <= bf < 1.0, "BARRA_FUERA_DE_DOMINIO")
        _need(K.tau_domain(pl["instrument_j"], bd, bf) == pl["tau_domain"], "BARRAS_NO_VINCULADAS_AL_DOMINIO")
        # --- estado reconstruido desde el payload
        s0 = c["state"]
        _need(isinstance(s0, dict) and set(s0) == set(CAMPOS_STATE), "STATE_CAMPOS")
        for k in CAMPOS_STATE:
            _num(s0[k], "STATE_NO_FINITO")
        try:
            st = V.state(prims)
        except Exception:  # noqa: BLE001 — dominio del proveedor
            raise EntradaInvalida("STATE_NO_RECONSTRUIBLE")
        _need(all(float(s0[k]) == getattr(st, k) for k in CAMPOS_STATE), "STATE_NO_VINCULADO_AL_PAYLOAD")
        B = st.B_pot
        _need(isinstance(B, float) and math.isfinite(B) and B > 0, "B_POT_INVALIDO")
        # --- techo
        ce = c["ceiling"]
        _need(isinstance(ce, dict) and set(ce) == set(CAMPOS_CEILING), "CEILING_CAMPOS")
        _need(isinstance(ce["instrument_available"], bool), "CEILING_TIPO")
        _need(_num(ce["B_pot"], "B_POT_NO_FINITO") == B, "B_POT_NO_VINCULADO")
        _need(ce["instrument_available"] is V.disponible, "DISPONIBILIDAD_CONTRADICE_LA_SOLICITUD")
        if not ce["instrument_available"]:
            _need(ce["sup"] is None and ce["C2"] is None and ce["numerical_error"] is None and ce["status"] == "not_applicable"
                  and ce["reason"] == "INSTRUMENT_NOT_AVAILABLE", "NO_APLICABLE_INCOHERENTE")
            ceil = FR.Ceiling(False, None, None, B, None, "not_applicable", "INSTRUMENT_NOT_AVAILABLE")
        else:
            s = ce["sup"]
            _need(isinstance(s, dict) and set(s) == set(CAMPOS_SUP), "SUP_CAMPOS")
            valor, lo, hi = _num(s["sup"], "SUP_NO_FINITO"), _num(s["lower"], "COTA_NO_FINITA"), _num(s["upper"], "COTA_NO_FINITA")
            td, tf = _num(s["tau_d"], "PUNTO_NO_FINITO"), _num(s["tau_f"], "PUNTO_NO_FINITO")
            e_abs, C2, err = _num(s["numerical_error"], "ERROR_NO_FINITO"), _num(ce["C2"], "C2_NO_FINITO"), _num(ce["numerical_error"], "ERROR_NO_FINITO")
            _need(isinstance(s["attained"], bool) and isinstance(s["converged"], bool), "SUP_TIPOS")
            _need(s["error_kind"] == "certified_bound" and s["lateral_low"] is None and s["lateral_high"] is None and s["lateral_axis"] is None
                  and s["witnesses"] == [] and s["evaluations"] == {} and s["n_jump_points"] == 0, "SUP_NO_ES_DEL_PROVEEDOR_CERTIFICADO")
            _need(isinstance(s["final_n"], int) and not isinstance(s["final_n"], bool) and s["final_n"] >= 0, "SUP_FINAL_N")
            _need(isinstance(s["level_values"], list) and len(s["level_values"]) == 1 and _num(s["level_values"][0], "SUP_NO_FINITO") == valor, "SUP_NIVELES")
            _need(lo <= valor <= hi, "COTAS_NO_CONTIENEN_EL_VALOR")
            (dl, dh), (fl, fh) = SU.axes(pl["instrument_j"], bd, bf)
            _need(dl <= td <= dh and fl <= tf <= fh, "PUNTO_FUERA_DEL_DOMINIO")
            # contrato del proveedor certificado (encierros_modelo.sup_bound + ModeloTeorico.capture_ceiling): valor =
            # revenue(estado, punto) y cota inferior = extremo inferior del encierro puntual en el punto; igualdad EXACTA
            _need(valor == V.revenue(st, td, tf, pl["design_v"]), "VALOR_NO_CORRESPONDE_AL_PUNTO")
            vpt, _ = V.engine(st, pl["design_v"]).R(Iv(td, td), Iv(tf, tf), None, grad=False)
            _need(lo == vpt.lo, "COTA_INFERIOR_NO_CORRESPONDE_AL_PUNTO")
            _need(C2 == valor / B, "C2_NO_VINCULADO")
            Bi = IParams.from_state(st).B_pot
            err_r = math.nextafter(max(0.0, (Iv.point(hi) / Bi).hi - C2, C2 - (Iv.point(lo) / Bi).lo), math.inf)
            _need(err == err_r, "ERROR_NO_RECONSTRUIBLE_DESDE_LAS_COTAS")
            _need(e_abs == err_r * B, "ERROR_ABSOLUTO_INCOHERENTE")
            if not s["attained"]:
                esp = ("incomplete", "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE", False)
            elif err_r > V.tol:
                esp = ("incomplete", "CERTIFIED_BOUND_NOT_CLOSED", False)
            else:
                esp = ("complete", None, True)
            _need((s["status"], s["reason"], s["converged"]) == esp and (ce["status"], ce["reason"]) == esp[:2], "ESTADO_INCOHERENTE_CON_ERROR_Y_TOLERANCIA")
            sup = SU.SupResult(sup=valor, attained=s["attained"], tau_d=td, tau_f=tf, lateral_low=None, lateral_high=None)
            sup.level_values, sup.numerical_error, sup.converged, sup.status, sup.reason = [valor], e_abs, s["converged"], s["status"], s["reason"]
            sup.final_n, sup.error_kind, sup.upper, sup.lower = s["final_n"], "certified_bound", hi, lo
            ceil = FR.Ceiling(True, sup, C2, B, err, s["status"], s["reason"])
        return {"state": st, "ceiling": ceil, "payload": pl, "bars": (bd, bf), "frontier": None, "cs_cache": {}}

    def _leer(self, clave):
        f = self._f(clave)
        try:
            raw = f.read_bytes()
        except FileNotFoundError:
            return None
        try:
            return self._validar(clave, raw)
        except EntradaInvalida as e:
            dest = f.with_name(f.name + ".rechazada." + uuid.uuid4().hex[:8])
            try:
                os.replace(f, dest)
            except FileNotFoundError:
                pass
            self.estadistica["rechazos"] += 1
            self._evento(evento="rechazo", clave=clave, motivo=str(e), apartada_como=dest.name)
            return None

    # ------------------------------------------------------------------------------------------------- candados
    def _leer_dueno(self, cand):
        try:
            d = json.loads((cand / "dueno.json").read_bytes())
            return d if isinstance(d, dict) else None
        except (OSError, ValueError):
            return None

    def _tomar(self, clave):
        cand = self._candado(clave)
        try:
            os.mkdir(cand)
        except FileExistsError:
            return False
        token = uuid.uuid4().hex
        try:
            self._atomico(cand / "dueno.json", canon({"pid": self._yo[0], "creacion": self._yo[1], "token": token,
                                                      "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
        except BaseException:
            os.rmdir(cand)
            raise
        self._propios[clave] = (token, time.time())
        return True

    def _recuperar(self, clave, dueno):
        """Aparta un candado HUÉRFANO (dueño muerto o sin dueño tras GRACIA_S) con un renombrado atómico."""
        cand = self._candado(clave)
        dest = cand.with_name(cand.name + ".recuperado." + uuid.uuid4().hex[:8])
        try:
            os.replace(cand, dest)
        except OSError:
            return
        for q in dest.iterdir():
            q.unlink()
        dest.rmdir()
        self.estadistica["candados_recuperados"] += 1
        self._evento(evento="candado_recuperado", clave=clave, dueno=dueno)

    def _liberar_propio(self, clave, motivo):
        token, _ = self._propios.pop(clave)
        cand = self._candado(clave)
        dueno = self._leer_dueno(cand)
        if not dueno or dueno.get("token") != token:
            self._evento(evento="candado_ajeno_no_liberado", clave=clave, motivo=motivo, dueno=dueno)
            return
        dest = cand.with_name(cand.name + ".liberado." + uuid.uuid4().hex[:8])
        os.replace(cand, dest)
        for q in dest.iterdir():
            q.unlink()
        dest.rmdir()
        if motivo != "escritura":
            self.estadistica["candados_liberados_por_error"] += 1
            self._evento(evento="candado_liberado", clave=clave, motivo=motivo)

    def liberar_propios(self, motivo="error_del_calculo"):
        """Libera los candados de ESTE proceso (cálculo interrumpido o fallido): otros procesos podrán calcular."""
        for clave in list(self._propios):
            try:
                self._liberar_propio(clave, motivo)
            except OSError:
                pass

    # ------------------------------------------------------------------------------------------------- interfaz dict
    def get(self, clave, default=None):
        self._exigir_vinculo()
        if clave in self.memoria:
            self.estadistica["aciertos_memoria"] += 1
            return self.memoria[clave]
        t0, avisado = time.time(), False
        while True:
            hit = self._leer(clave)
            if hit is not None:
                self.memoria[clave] = hit
                self.estadistica["aciertos_disco"] += 1
                self._evento(evento="acierto_disco", clave=clave, espera_s=round(time.time() - t0, 3))
                return hit
            if self._tomar(clave):
                self._evento(evento="sin_entrada_calcula", clave=clave)
                return default
            cand = self._candado(clave)
            dueno = self._leer_dueno(cand)
            if dueno is None:
                try:
                    edad = time.time() - cand.stat().st_mtime
                except FileNotFoundError:
                    continue
                if edad > GRACIA_S:
                    self._recuperar(clave, {"sin_dueno": True, "edad_s": round(edad, 1)})
                    continue
            elif not _vivo(dueno.get("pid"), dueno.get("creacion")):
                self._recuperar(clave, dueno)
                continue
            if time.time() - t0 > self.espera_max_s:
                self.estadistica["esperas_agotadas"] += 1
                self._evento(evento="espera_agotada", clave=clave, espera_s=round(time.time() - t0, 1), dueno=dueno)
                raise EsperaAgotada("ESPERA_AGOTADA:%s:%.0fs" % (clave[:16], time.time() - t0))
            if not avisado:
                avisado = True
                self.estadistica["esperas"] += 1
                self._evento(evento="espera", clave=clave, dueno=dueno)
            time.sleep(self.sondeo_s)

    def __getitem__(self, clave):
        hit = self.get(clave)
        if hit is None:
            raise KeyError(clave)
        return hit

    def __setitem__(self, clave, hit):
        self._exigir_vinculo()
        t_res = self._propios.get(clave, (None, None))[1]
        seg = round(time.time() - t_res, 3) if t_res else None
        try:
            doc = self.documento(clave, hit, seg)
            self._validar(clave, doc)                  # el mismo contrato en escritura
            self._atomico(self._f(clave), doc)
            self.estadistica["calculos"] += 1
            self._evento(evento="escritura", clave=clave, segundos_calculo=seg, bytes=len(doc))
        except EntradaInvalida as e:
            self.estadistica["escrituras_rechazadas"] += 1
            self._evento(evento="escritura_rechazada", clave=clave, motivo=str(e))
        finally:
            self.memoria[clave] = hit                  # el proceso conserva su propio cálculo (semántica del núcleo)
            if clave in self._propios:
                self._liberar_propio(clave, "escritura")

    def __contains__(self, clave):
        return clave in self.memoria or self._f(clave).exists()


def campos_cientificos(hit) -> dict:
    """Campos científicos canónicos de un techo, para comparar resultado calculado y reutilizado (sin tiempos ni pid)."""
    return json.loads(canon(AlmacenTechos.contenido(hit)))


def fabrica(raiz, **kw):
    """Fábrica explícita para EjecutorSeleccion(almacen_techos=...): recibe la identidad de la corrida del ejecutor; el
    ejecutor VINCULA el almacén a sus Run (vincular) antes de usarlo."""
    return lambda ident: AlmacenTechos(raiz, ident, **kw)
