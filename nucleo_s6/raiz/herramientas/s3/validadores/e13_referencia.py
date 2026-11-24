"""E13 CANDIDATO: tabla `global_extreme` v3, su VALIDADOR (esquema, contenido y relaciones) y la REFERENCIA canónica que
consume la vía de celda por valores (INTEGRACION H4 3.7, NO OFICIAL; copia candidata, no incorporada).

Movido a la estructura candidata desde codigo/global_extreme_v3.py SIN cambios de lógica de validación ni de cálculo.
Cambios de integración (y solo esos):
  - sin rutas deducidas de la ubicación del archivo: la raíz de las FUENTES HISTÓRICAS autenticadas (datos, citadas por
    inventario; CADENA y FUENTE_PLAN) se pasa explícitamente (Referencia(ctx, raiz=...));
  - el contexto S5 es obligatorio (sin contexto por defecto del área);
  - las funciones que antes se importaban de módulos del área (extremos_dfd.grupo, extremos_G.preparar,
    demo/cobertura_compartida.q_pot_exact, demo/cobertura_mejorada.CLAIM_P3B) se incorporan aquí con la misma lógica;
    el universo por contextos viene de paper2b.seleccion_valores;
  - sin modos de línea de órdenes de desarrollo (exportar/validar del área).
Documentación original del validador (v3):
Tabla candidata `global_extreme` v3 (E7), su VALIDADOR de esquema completo, contenido y relaciones (E13) y el OBJETO
CANÓNICO que consume la vía de celda por valores (VALIDACION 3.7.4, NO OFICIAL).
Sustituye como candidato a codigo/global_extreme_v2.py (que se conserva byte a byte para reproducir los defectos).

  (Los modos de línea de órdenes exportar/validar del área NO existen en esta copia candidata: la tabla se valida por
   Referencia/TestigosValidados desde el punto de entrada herramientas/b/seleccion_paso4.py.)

Qué cambia frente a v2 (defectos reproducidos en demo/defectos/reproduccion_defectos_v2.json):
  1. ESQUEMA COMPLETO y estricto (ESQUEMA_DOC, ESQUEMA_FILA_CI, ESQUEMA_FILA_AGR): cada campo, anidado o no, tiene tipo,
     finitud, dominio, orden de intervalos y claves exactas (sin campos de más ni de menos). Se comprueba ANTES de usar
     cualquier valor (los ids no hashables, nulos o de tipo erróneo se rechazan con código, nunca con excepción).
  2. VÍNCULO de cada campo serializado con la referencia autenticada: L/U/estado, punto, índice y contexto, hoja,
     país/instrumento, C2 y K1 en el punto, respaldo, universo, componentes y citas. Cada cita lleva clave, entrega,
     sha256 del inventario, archivo, sha256 del archivo, LOCALIZADOR (ruta dentro del JSON) y el VALOR que hay allí; el
     validador resuelve el localizador en la fuente autenticada y compara el valor. Cuando la cota de C2 combina varios
     certificados (ínfimo df: varios techos del mismo punto), se citan TODOS los usados y la regla de combinación.
  3. Además del vínculo campo a campo (códigos legibles), la fila debe ser IGUAL, con tipos estrictos, a la fila canónica
     recalculada desde las fuentes: ningún campo, ni descriptivo, puede divergir.
  4. Los campos DESCRIPTIVOS (etiqueta, tabla, nota_hoja_ganadora, procedencia) se validan pero el consumidor NO los lee.
     El consumidor recibe, de `testigos_validados`, el testigo CANÓNICO de la referencia (no los bytes de la tabla), solo
     si la tabla entera valida; una tabla parcial válida se entrega marcada como NO completa y solo si se pide.
  5. `optimizador_identificado` de v2 pasa a `hoja_ganadora_identificada`: intervalos separados identifican la HOJA
     (afirmación ci, es decir, país e instrumento) que realiza la cota agregada; NO identifican el optimizador continuo
     (el punto exacto ω* donde se alcanza el extremo), que la tabla no afirma.
Fuentes y reglas de cálculo: las de v2 (ver codigo/global_extreme_v2.py), sin cambiar límites, clasificaciones ni testigos.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path
from types import MappingProxyType

# Fuente del PLAN de grupos autenticado (antes codigo/extremos_dfd.CERT/CERT_INV/PLAN_REL): datos citados por inventario.
FUENTE_PLAN = ("certificacion_3_7_2026-10-04", "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5", "demo/C2/plan.json")
CLAIM_P3B = "CLM:PREG-PER-APLICACION-E0E3:primary:ci:PER:f:conditional_full:G:sin_addback:micro:guardrail_deuda"
T2_G = 1e-4
TOL = 1e-12
VERSION = 3
ETIQUETA = "VALIDACION 374 3.7 NO OFICIAL"
NOMBRE_TABLA = "global_extreme (candidata, E7)"
SELECCION = "SEL-PROPAGACION-DF-v1"
DISENOS = ["G", "N"]
CADENA = {
    "SEL": ("cierre_G_df_3_7_2026-10-06_lima0754", "f6a79639c02ab0bb6a2d2ea0e5b0f5e872b85d3cc1bbad2d4e5934b4ba9e1c26"),
    "PRV": ("cierre_df_paso4_3_7_2026-10-05_lima1958", "f62789edc1e7f22c307e23cad95d71dcdff07f99715c63d5dbea9f5d0a991f8c"),
    "XDD": ("extremos_df_d_3_7_2026-10-05_lima0738", "116a3f06bb8f5dc449e6c9921a6fd4600abb2f349bb61b3ee8667b412d796bd4"),
    "CAN": ("cierre_candidato_3_7_2026-10-04_lima2103", "ea126009763844cf58f365fc5b9c8e68f8141a4302be59562e0b914094e0d9db"),
    "RES": ("resolucion_3_7_2026-10-04_lima1941", "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"),
    # P0 COMPLETO: ci-df de la muestra continuada M3 (validación/eficiencia H4, lima0003), autenticada por su inventario. Solo
    # amplía las claves citables: las tablas y selecciones anteriores no la citan y su comportamiento no cambia.
    "M3": ("validacion_eficiencia_h4_paso4_3_7_2026-10-09_lima0003", "36d10e10084ccb86298c132b338fb649e328285cd61421fc671222845940cb04"),
    # P1A PILOTO: ci-df de P1a validadas, exportadas con inventario propio (sha256 fijado aquí tras la validación)
    "P1A": ("p1a_piloto_h4_paso4_3_7_2026-10-09_lima1719/demo/p1a/catalogo", "42776211e3a59cbe3153216f0659d5edf008d809bb81a99e66f26c47744f2c51"),
    # P1B GLOBAL: los 12 de P1a REPRODUCIDOS con traza (mismo B&B), validados (v2) y exportados con vínculo (exportar_validados)
    "P1AT": ("p1b_global_h4_paso4_3_7_2026-10-09_lima1913/demo/p1a_traza/catalogo", "da77c6645a03d5f3a01af2dfc98d3c8cad77b71d66b246ac975215e429aae471"),
    # P1B GLOBAL: ci-df de P1b validadas (v2) y exportadas con vínculo, una fuente por trabajador
    "P1BW0": ("p1b_global_h4_paso4_3_7_2026-10-09_lima1913/demo/p1b/catalogo_w0", "a4dabfd7b377b045eb3c634c760ac2a01973f905d56531b4b57ca511b7706408"),
    "P1BW1": ("p1b_global_h4_paso4_3_7_2026-10-09_lima1913/demo/p1b/catalogo_w1", "9992b3658740eb4d61bead739fe0cc575a8f2a221a028c6958136bde6ea0267b"),
    "P1BW2": ("p1b_global_h4_paso4_3_7_2026-10-09_lima1913/demo/p1b/catalogo_w2", "64355d5d2aa478ee6b8131bf7e8f3850753a0e5c51fc305845ec082e5545487f"),
}
ORDEN_J = {"d": 0, "df": 1, "f": 2}
NOTA_HOJA = ("intervalos separados: la hoja (país e instrumento) que realiza la cota agregada queda identificada; esto NO "
             "identifica el optimizador continuo (punto exacto del extremo), que la tabla no afirma")
NOTA_SOLAPE = ("intervalos solapados: el testigo respalda la cota, pero no identifica la hoja que realiza el extremo agregado "
               "(ni, por tanto, el optimizador continuo)")
REGLA_CTX_DF = "índice del testigo guardado por la propagación (fuente_contexto)"
REGLA_CTX_DF_F = ("contexto de k_c mínimo (sup) o máximo (inf) del universo de la hoja, desempate por orden del universo "
                  "(las fuentes de d y f no guardan contexto)")
REGLA_K1 = "K1 = k_c·(1 − q_pot(punto)), k_c = n_min/(s_pi·gain) del contexto; aritmética de intervalos dirigida"
HEX16 = re.compile(r"^[0-9a-f]{16}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class Rechazo(Exception):
    def __init__(self, codigo, detalle=""):
        super().__init__(codigo + ": " + str(detalle))
        self.codigo, self.detalle = codigo, str(detalle)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def eid(cid, sentido):
    return sha((cid + "|" + sentido).encode())[:16]


def campos(cid):
    p = cid.split(":")
    if p[3] == "ci":
        return {"fam": "ci", "pid": p[1], "kind": p[2], "pais": p[4], "j": p[5], "dis": p[7], "resto": tuple(p[8:])}
    if p[3] == "c":
        return {"fam": "c", "pid": p[1], "kind": p[2], "pais": p[4], "scen": p[5], "dis": p[6], "resto": tuple(p[7:])}
    return {"fam": "g", "pid": p[1], "kind": p[2], "scen": p[4], "dis": p[5], "resto": tuple(p[6:])}


def ci_de(c_cid, j):
    f = campos(c_cid)
    avail = "domestic_unchanged" if j == "d" else "conditional_full"
    return ":".join(["CLM", f["pid"], f["kind"], "ci", f["pais"], j, avail, f["dis"]] + list(f["resto"]))


def multiconjunto_sha(keys):
    return sha(json.dumps(sorted(json.dumps(k) for k in keys)).encode())


def resolver(obj, loc):
    """Valor de `obj` en el localizador `loc`: lista de claves str / índices int; el ÚLTIMO elemento puede ser una
    proyección (lista de claves str de un objeto -> objeto con esas claves; lista de índices int -> lista). Rechazo
    E_LOCALIZADOR si no existe."""
    x = obj
    for n, k in enumerate(loc):
        if isinstance(k, list) and n == len(loc) - 1 and k:
            if isinstance(x, dict) and all(isinstance(q, str) and q in x for q in k):
                return {q: x[q] for q in k}
            if isinstance(x, list) and all(type(q) is int and 0 <= q < len(x) for q in k):
                return [x[q] for q in k]
            raise Rechazo("E_LOCALIZADOR", "proyección sin destino: %r" % (loc,))
        if isinstance(x, dict) and isinstance(k, str) and k in x:
            x = x[k]
        elif isinstance(x, list) and type(k) is int and 0 <= k < len(x):
            x = x[k]
        else:
            raise Rechazo("E_LOCALIZADOR", "localizador sin destino: %r" % (loc,))
    return x


# ================================================================================================ esquema
# Gramática: "str", "hex16", "hex64", "float" (finito, no bool), "int0" (int >= 0, no bool), "bool", ("const", v),
# ("enum", [..]), ("nulo_o", e), ("lista", e, min, max), ("tupla", [e1, ..]), ("intervalo",) [lo, hi] finitos lo <= hi,
# ("dict", {clave: e}) con claves EXACTAS, "punto" (las 9 primitivas estructurales -> float), "contexto",
# "localizador" (lista no vacía de str/int), "json" (cualquier valor JSON finito: valor citado, comparado aparte).
STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
CITA = ("dict", {"clave": ("enum", sorted(CADENA)), "entrega": "str", "inventario_sha256": "hex64", "archivo": "str",
                 "sha256": "hex64", "localizador": "localizador", "valor": "json"})
CERT_C2 = ("dict", {"cita": CITA, "localizador_punto": "localizador", "punto_del_certificado": "json"})
TESTIGO = ("dict", {
    "punto": "punto", "fuente_punto": CITA,
    "contexto": "contexto", "indice_contexto": "int0", "regla_contexto": ("enum", [REGLA_CTX_DF, REGLA_CTX_DF_F]),
    "fuente_contexto": ("nulo_o", CITA),
    "claim_id_hoja": "str", "instrumento_hoja": ("enum", ["d", "df", "f"]), "pais_hoja": ("enum", ["COL", "MEX", "PER"]),
    "C2_en_punto": ("intervalo",), "certificados_C2": ("lista", CERT_C2, 1, 64),
    "regla_C2": ("enum", ["unico", "interseccion_de_certificados"]),
    "K1_en_punto": ("intervalo",), "regla_K1": ("const", REGLA_K1),
    "cota_que_respalda": "float", "respalda": ("const", True)})
UNIVERSO = ("dict", {"n": "int0", "multiconjunto_sha256": "hex64", "igual_a_suma_de_hojas": ("const", True)})
COMUN = {"extreme_id": "hex16", "claim_id": "str", "diseno": ("enum", DISENOS), "sentido": ("enum", ["sup", "inf"]),
         "objeto": ("const", "G_best"), "L": "float", "U": "float", "brecha": "float", "estado": ("enum", ["pass", "incomplete"]),
         "categoria_v4": "str", "testigo": TESTIGO, "hoja_ganadora_identificada": "bool", "nota_hoja_ganadora": "str",
         "universo": UNIVERSO}
ESQUEMA_FILA_CI = ("dict", dict(COMUN, familia=("const", "ci"), instrumento=("const", "df"), fuente_cota=CITA,
                                fuente_estado=("lista", CITA, 1, 2)))
COMPONENTE = ("dict", {"claim_id": "str", "instrumento": ("enum", ["d", "df", "f"]), "pais": ("enum", ["COL", "MEX", "PER"]),
                       "L": "float", "U": "float", "convergida": "bool", "fuente_cota": CITA, "fuente_estado": ("lista", CITA, 1, 2)})
ESQUEMA_FILA_AGR = ("dict", dict(COMUN, familia=("enum", ["c", "g"]), instrumento=("const", None),
                                 componentes=("lista", COMPONENTE, 3, 64), procedencia="str"))
ALCANCE = ("dict", {"tipo": ("enum", ["seleccion_completa", "parcial"]), "seleccion": ("const", SELECCION),
                    "disenos": ("lista", ("enum", DISENOS), 1, 2), "filas_esperadas": "int0",
                    "extreme_ids": ("nulo_o", ("lista", "hex16", 1, 64))})
ESQUEMA_DOC = ("dict", {"etiqueta": "str", "no_exportable": ("const", True), "tabla": ("const", NOMBRE_TABLA),
                        "version": ("const", VERSION), "alcance": ALCANCE, "T2_G": ("const", T2_G), "filas": ("lista", "json", 0, 10000)})


def _es_float(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _json_finito(x, prof=0):
    if prof > 40:
        return False
    if x is None or isinstance(x, (bool, str)):
        return True
    if isinstance(x, (int, float)):
        return math.isfinite(x)
    if isinstance(x, list):
        return all(_json_finito(y, prof + 1) for y in x)
    if isinstance(x, dict):
        return all(isinstance(k, str) and _json_finito(v, prof + 1) for k, v in x.items())
    return False


def comprobar(x, e, ruta="$"):
    """Rechazo E_ESQUEMA (con la ruta) si `x` no cumple el esquema `e`."""
    def mal(msg):
        raise Rechazo("E_ESQUEMA", "%s: %s" % (ruta, msg))
    if e == "str":
        if not isinstance(x, str) or not x:
            mal("se esperaba texto no vacío")
    elif e == "hex16":
        if not isinstance(x, str) or not HEX16.match(x):
            mal("se esperaba id hexadecimal de 16")
    elif e == "hex64":
        if not isinstance(x, str) or not HEX64.match(x):
            mal("se esperaba sha256 hexadecimal")
    elif e == "float":
        if not _es_float(x):
            mal("se esperaba número finito")
    elif e == "int0":
        if type(x) is not int or x < 0:
            mal("se esperaba entero >= 0")
    elif e == "bool":
        if type(x) is not bool:
            mal("se esperaba booleano")
    elif e == "json":
        if not _json_finito(x):
            mal("valor no JSON finito")
    elif e == "punto":
        if not isinstance(x, dict) or set(x) != set(STRUCT):
            mal("el punto debe tener exactamente las 9 primitivas estructurales")
        for p in STRUCT:
            if type(x[p]) is not float or not math.isfinite(x[p]):
                mal("%s no es un float finito" % p)
    elif e == "contexto":
        ok = (isinstance(x, list) and len(x) == 8 and x[0] in DISENOS and x[1] in ("d", "df", "f") and isinstance(x[2], list)
              and len(x[2]) == 2 and all(_es_float(y) for y in x[2]) and all(_es_float(y) for y in x[3:]))
        if not ok:
            mal("contexto con forma [diseño, instrumento, [barra_d, barra_f], s_pi, s_t, eta_h, gain, n_min] inválida")
    elif e == "localizador":
        if not isinstance(x, list) or not x or not all(isinstance(k, str) or type(k) is int for k in x[:-1]) or not (
                isinstance(x[-1], str) or type(x[-1]) is int or (isinstance(x[-1], list) and x[-1] and (
                    all(isinstance(q, str) for q in x[-1]) or all(type(q) is int for q in x[-1])))):
            mal("localizador inválido")
    elif isinstance(e, tuple):
        k = e[0]
        if k == "const":
            if type(x) is not type(e[1]) or x != e[1]:
                mal("se esperaba %r" % (e[1],))
        elif k == "enum":
            if not any(type(x) is type(v) and x == v for v in e[1]):
                mal("valor fuera del dominio %r" % (e[1],))
        elif k == "nulo_o":
            if x is not None:
                comprobar(x, e[1], ruta)
        elif k == "lista":
            if not isinstance(x, list) or not (e[2] <= len(x) <= e[3]):
                mal("se esperaba lista de %d a %d elementos" % (e[2], e[3]))
            for i, y in enumerate(x):
                comprobar(y, e[1], "%s[%d]" % (ruta, i))
        elif k == "intervalo":
            if not isinstance(x, list) or len(x) != 2 or not all(_es_float(y) for y in x) or not x[0] <= x[1]:
                mal("se esperaba intervalo [lo, hi] finito con lo <= hi")
        elif k == "dict":
            if not isinstance(x, dict):
                mal("se esperaba objeto")
            falta, sobra = set(e[1]) - set(x), set(x) - set(e[1])
            if falta or sobra:
                mal("claves faltantes %s, sobrantes %s" % (sorted(falta), sorted(sobra)))
            for kk, ee in e[1].items():
                comprobar(x[kk], ee, ruta + "." + kk)
        else:
            raise AssertionError(e)
    else:
        raise AssertionError(e)


def diferencias(a, b, ruta="$", out=None):
    """Rutas en que a y b difieren (con tipos estrictos: 1 != 1.0, True != 1)."""
    out = [] if out is None else out
    if type(a) is not type(b):
        out.append(ruta)
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(ruta + "." + k)
            else:
                diferencias(a[k], b[k], ruta + "." + k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(ruta)
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diferencias(x, y, "%s[%d]" % (ruta, i), out)
    elif a != b:
        out.append(ruta)
    return out


def congelar(x):
    if isinstance(x, dict):
        return MappingProxyType({k: congelar(v) for k, v in x.items()})
    if isinstance(x, list):
        return tuple(congelar(v) for v in x)
    return x


# ================================================================================================ referencia
class Referencia:
    """Todo lo que el validador recalcula desde las fuentes autenticadas. Se construye UNA vez por proceso; las filas
    canónicas se calculan una vez y se guardan como texto JSON (inmutable): cada validación compara contra una copia."""

    def __init__(self, ctx, raiz):
        """ctx: contexto S5 autenticado (obligatorio). raiz: carpeta que contiene las entregas históricas de CADENA y de
        FUENTE_PLAN (datos autenticados por su inventario; normalmente <proyecto>/tmp)."""
        if ctx is None:
            raise Rechazo("E_CONTEXTO", "la Referencia exige el contexto S5 explícito")
        from paper2b import cobertura as COV
        from paper2b.intervalos import Iv
        self.T = Path(raiz)
        self.COV, self.Iv, self.qpe = COV, Iv, q_pot_exact
        assert tuple(COV.STRUCT) == STRUCT or set(COV.STRUCT) == set(STRUCT), "STRUCT"
        t0 = time.time()
        self.ctx = ctx
        COV.q_pot = q_pot_exact
        self._obj, self._ref, self._raw_sha = {}, {}, {}
        self.reg = self.leer("RES", "demo/registro/registro_candidato_v4.json")["afirmaciones"]
        self.xdd = self.leer("XDD", "demo/extremos/extremos_G_d.json")
        self.can = self.leer("CAN", "demo/extremos/extremos_G_f.json")
        self.prop, self.prod, self.sred, self.techos = {}, {}, {}, {}
        self.univ, self.grupo, self.esperadas, self.hojas, self.arch = {}, {}, {}, {}, {}
        for d in DISENOS:
            self.arch[("prop", d)] = ("SEL", "demo/hito2/extremos_G_df_v5_%s.json" % d)
            self.arch[("prod", d)] = ("PRV", "demo/hito2/produccion_inf_G_cid_%s.json" % d)
            self.arch[("sred", d)] = ("PRV", "demo/hito2/sred_%s_df.json" % d)
            self.prop[d] = self.leer(*self.arch[("prop", d)])
            self.prod[d] = self.leer(*self.arch[("prod", d)])
            self.sred[d] = self.leer(*self.arch[("sred", d)])
            for f in self.prop[d]["puntos_U"]["fuentes"]:
                obj = self.leer("SEL", f["archivo"])
                if self._ref[("SEL", f["archivo"])]["sha256"] != f["sha256"]:
                    raise Rechazo("E_FUENTE", "techo citado por la propagación con otro sha256: %s" % f["archivo"])
                for i, fila in enumerate(obj["filas"]):
                    if fila.get("admisible") and "U" in fila:
                        self.techos.setdefault(d, []).append((fila["theta"], f["archivo"], i, bool(fila.get("incompatible"))))
            sel = self.prop[d]["seleccion"]
            for j in ("d", "df", "f"):
                g = grupo(self.T, d, j)
                self.grupo[(d, j)] = (g["full"], g["fixed"])
            cids = list(sel["ci_df"]) + list(sel["country"]) + [sel["g"]]
            for c in cids:
                for s in ("sup", "inf"):
                    self.esperadas[eid(c, s)] = (c, s, d)
            hojas_all = set(sel["ci_df"])
            for c in sel["country"]:
                self.hojas[c] = [ci_de(c, j) for j in ("d", "df", "f")]
                hojas_all |= set(self.hojas[c])
            gf = campos(sel["g"])
            self.hojas[sel["g"]] = sorted({h for c in sel["country"] if (campos(c)["pid"], campos(c)["kind"], campos(c)["resto"]) ==
                                           (gf["pid"], gf["kind"], gf["resto"]) for h in self.hojas[c]})
            for h in sel["ci_df"]:
                self.hojas[h] = [h]
            st = preparar(self.ctx, d, sorted(hojas_all | set(sel["country"]) | {sel["g"]}))
            for c, cx in st["univ"].items():
                self.univ[c] = cx
        self.ctx_keys = {h: [self.ctx_key(c) for c in cx] for h, cx in self.univ.items()}
        self._canon = {}
        for e, (c, s, d) in self.esperadas.items():
            self._canon[e] = json.dumps(self.fila(c, s, d), ensure_ascii=False)
        self.orden = [e for e, _ in sorted(self.esperadas.items(), key=lambda kv: (kv[1][2], kv[1][0], kv[1][1]))]
        self.segundos = round(time.time() - t0, 1)

    # -------------------------------------------------------------------------------------------- fuentes y citas
    def leer(self, clave, rel):
        """Objeto JSON de un archivo autenticado por la cadena de inventarios (sha256 del inventario + del archivo)."""
        if (clave, rel) in self._obj:
            return self._obj[(clave, rel)]
        if clave not in CADENA:
            raise Rechazo("E_FUENTE", "clave desconocida %s" % clave)
        base, h = CADENA[clave]
        try:
            inv_raw = (self.T / base / "audit/entrega.json").read_bytes()
        except OSError as e:
            raise Rechazo("E_FUENTE", "inventario ilegible %s: %s" % (clave, e))
        if sha(inv_raw) != h:
            raise Rechazo("E_FUENTE", "inventario de %s alterado" % clave)
        files = json.loads(inv_raw)["files"]
        if rel not in files:
            raise Rechazo("E_FUENTE", "%s no está en el inventario de %s" % (rel, clave))
        try:
            raw = (self.T / base / rel).read_bytes()
        except OSError as e:
            raise Rechazo("E_FUENTE", "archivo ilegible %s: %s" % (rel, e))
        if files[rel]["sha256"] != sha(raw):
            raise Rechazo("E_FUENTE", "sha256 de %s distinto del inventario" % rel)
        self._obj[(clave, rel)] = json.loads(raw)
        self._ref[(clave, rel)] = {"clave": clave, "entrega": base, "inventario_sha256": h, "archivo": rel, "sha256": sha(raw)}
        return self._obj[(clave, rel)]

    def cita(self, clave, rel, loc):
        """(valor, cita) con el valor LEÍDO en el localizador: el cálculo usa ese valor, así que la cita es la de verdad."""
        v = resolver(self.leer(clave, rel), loc)
        return v, dict(self._ref[(clave, rel)], localizador=list(loc), valor=copy.deepcopy(v))

    def verificar_cita(self, c):
        """Rechazo si la cita no es resoluble en una fuente autenticada o su valor no es el que hay en el localizador."""
        clave, rel = c["clave"], c["archivo"]
        if clave not in CADENA:
            raise Rechazo("E_FUENTE", "clave desconocida %s" % clave)
        base, h = CADENA[clave]
        if c["entrega"] != base or c["inventario_sha256"] != h:
            raise Rechazo("E_FUENTE", "entrega o inventario distintos de la cadena para %s" % clave)
        if (clave, rel) not in self._obj:
            self.leer(clave, rel)          # autentica (inventario + archivo) o Rechazo E_FUENTE
        if c["sha256"] != self._ref[(clave, rel)]["sha256"]:
            raise Rechazo("E_FUENTE", "sha256 citado distinto del autenticado: %s" % rel)
        v = resolver(self._obj[(clave, rel)], c["localizador"])
        if diferencias(v, c["valor"]):
            raise Rechazo("E_LOCALIZADOR", "el valor citado no es el que hay en %s%r" % (rel, c["localizador"]))

    def reverificar_fuentes(self):
        """Los bytes de todas las fuentes leídas siguen siendo los autenticados (al final de cada validación)."""
        for (clave, rel), r in self._ref.items():
            raw = (self.T / r["entrega"] / rel).read_bytes()
            if sha(raw) != r["sha256"]:
                raise Rechazo("E_FUENTE", "la fuente %s cambió durante la validación" % rel)

    # -------------------------------------------------------------------------------------------- modelo
    def ctx_key(self, c):
        return [c.design, c.instrument, list(c.bars), c.s_pi, c.s_t, c.eta_h, c.gain, c.n_min]

    def k_iv(self, c):
        Iv = self.Iv
        return Iv(c.n_min, c.n_min) / (Iv(c.s_pi, c.s_pi) * Iv(c.gain, c.gain))

    def K1(self, punto, c):
        bx = {p: (float(punto[p]), float(punto[p])) for p in self.COV.STRUCT}
        return self.k_iv(c) * (1.0 - self.qpe(bx))

    def admisible(self, punto, d, j):
        full, fixed = self.grupo[(d, j)]
        try:
            if set(punto) != set(full):
                return False, "ejes distintos del soporte"
            vals = {p: float(punto[p]) for p in full}
        except (TypeError, ValueError):
            return False, "valores no numéricos"
        if not all(math.isfinite(v) and full[p][0] <= v <= full[p][1] for p, v in vals.items()):
            return False, "fuera del soporte"
        return bool(self.COV.box_admissible({p: (v, v) for p, v in vals.items()}, fixed)), "box_admissible"

    def contexto_de(self, hoja, sentido):
        # VALIDACION EFICIENCIA H4 3.7: mismo resultado que cx.index(min(cx, key=(k, cx.index(c)))) —índice del PRIMER
        # contexto de cota extrema— en tiempo lineal (antes, cx.index dentro de la clave hacía la búsqueda cuadrática).
        cx = self.univ[hoja]
        if sentido == "sup":
            return min(range(len(cx)), key=lambda i: (self.k_iv(cx[i]).lo, i))
        return min(range(len(cx)), key=lambda i: (-self.k_iv(cx[i]).hi, i))

    def respaldo(self, sentido, c2, k1, L, U):
        Iv = self.Iv
        if sentido == "sup":
            cota = (Iv(c2[0], c2[0]) - k1).lo
            return cota, cota >= L - TOL * max(1.0, abs(L))
        cota = (Iv(c2[1], c2[1]) - k1).hi
        return cota, cota <= U + TOL * max(1.0, abs(U))

    # -------------------------------------------------------------------------------------------- hoja: cota y testigo
    def hoja(self, h, sentido):
        f = campos(h)
        d, j = f["dis"], f["j"]
        p_struct = None
        if j == "df":
            k, rel = self.arch[("prop", d)]
            if h not in self.prop[d]["ci_df"]:
                raise Rechazo("E_FUENTE", "ci-df sin resultado en la propagación: %s" % h)
            (L, U), fc = self.cita(k, rel, ["ci_df", h, sentido + "_G"])
            est, fe1 = self.cita(k, rel, ["ci_df", h, "estado_" + sentido])
            fes = [fe1]
            conv = est == "convergida"
            if sentido == "inf":
                est2, fe2 = self.cita(k, rel, ["ci_df", h, "inf_bb", "estado"])
                fes.append(fe2)
                conv = conv and est2 == "convergido"
            punto, fp = self.cita(k, rel, ["ci_df", h, "testigo_" + sentido, "punto"])
            idx, fctx = self.cita(k, rel, ["ci_df", h, "testigo_" + sentido, "indice_contexto"])
            ctxk_fuente = resolver(self.prop[d], ["ci_df", h, "testigo_" + sentido, "contexto"])
            if type(idx) is not int or not 0 <= idx < len(self.univ[h]) or self.ctx_key(self.univ[h][idx]) != ctxk_fuente:
                raise Rechazo("E_TESTIGO_CONTEXTO", "el índice del testigo no corresponde a su contexto en la fuente: %s" % h)
            regla_ctx = REGLA_CTX_DF
            p_struct = {p: float(punto[p]) for p in STRUCT}
            if sentido == "sup":
                ks, rs = self.arch[("sred", d)]
                v2, cc = self.cita(ks, rs, [["L", "U"]])
                pc = resolver(self.sred[d], ["punto_cota_inferior"])
                if {p: float(pc[p]) for p in STRUCT} != p_struct:
                    raise Rechazo("E_TESTIGO_DISTINTO", "el punto del testigo sup no es p⁺ de SRED: %s" % h)
                c2 = [v2["L"], v2["U"]]
                certs = [{"cita": cc, "localizador_punto": ["punto_cota_inferior"], "punto_del_certificado": copy.deepcopy(pc)}]
                regla_c2 = "unico"
            else:
                cands = [x for x in self.techos[d] if {p: float(x[0][p]) for p in STRUCT} == p_struct and not x[3]]
                if not cands:
                    raise Rechazo("E_TESTIGO_DISTINTO", "sin techo certificado compatible en el punto del testigo inf: %s" % h)
                certs, los, his = [], [], []
                for theta, rel_t, i, _ in cands:
                    v2, ct = self.cita("SEL", rel_t, ["filas", i, ["L_punto", "U"]])
                    lo, hi = v2["L_punto"], v2["U"]
                    certs.append({"cita": ct, "localizador_punto": ["filas", i, "theta"], "punto_del_certificado": copy.deepcopy(theta)})
                    los.append(lo)
                    his.append(hi)
                c2 = [max(los), min(his)]
                regla_c2 = "unico" if len(certs) == 1 else "interseccion_de_certificados"
        elif j == "d":
            if sentido == "sup":
                k, rel = "XDD", "demo/extremos/extremos_G_d.json"
                if h not in self.xdd["afirmaciones"]:
                    raise Rechazo("E_FUENTE", "ci-d sin sup en XDD: %s" % h)
                (L, U), fc = self.cita(k, rel, ["afirmaciones", h, "sup_G"])
                est, fe1 = self.cita(k, rel, ["afirmaciones", h, "estado_sup"])
                punto, fp = self.cita(k, rel, ["p_max"])
                c2, cc = self.cita(k, rel, ["C2", d, "p_max", [0, 1]])
                certs = [{"cita": cc, "localizador_punto": ["p_max"], "punto_del_certificado": copy.deepcopy(punto)}]
            else:
                k, rel = self.arch[("prod", d)]
                if h not in self.prod[d]["afirmaciones"]:
                    raise Rechazo("E_FUENTE", "ci-d sin inf en la producción: %s" % h)
                (L, U), fc = self.cita(k, rel, ["afirmaciones", h, "inf_G"])
                est, fe1 = self.cita(k, rel, ["afirmaciones", h, "estado_inf"])
                punto, fp = self.cita(k, rel, ["afirmaciones", h, "punto_cota_superior"])
                ts = [i for i, x in enumerate(self.prod[d]["C2"][d]["techos"]) if x[0] == punto["a"]]
                if len(ts) != 1:
                    raise Rechazo("E_FUENTE", "techo de C2 d no único en a = %s" % punto["a"])
                c2, cc = self.cita(k, rel, ["C2", d, "techos", ts[0], [1, 2]])
                certs = [{"cita": cc, "localizador_punto": ["C2", d, "techos", ts[0], 0],
                          "punto_del_certificado": resolver(self.prod[d], ["C2", d, "techos", ts[0], 0])}]
            fes = [fe1]
            conv = est == "convergida"
            idx, fctx, regla_ctx = self.contexto_de(h, sentido), None, REGLA_CTX_DF_F
            regla_c2 = "unico"
        else:
            k, rel = "CAN", "demo/extremos/extremos_G_f.json"
            if h not in self.can["afirmaciones"]:
                raise Rechazo("E_FUENTE", "ci-f sin resultado en CAN: %s" % h)
            (L, U), fc = self.cita(k, rel, ["afirmaciones", h, sentido + "_G"])
            est, fe1 = self.cita(k, rel, ["afirmaciones", h, "estado"])
            fes = [fe1]
            conv = est == "convergida"
            punto, fp = self.cita(k, rel, ["puntos", "sup_C2" if sentido == "sup" else "inf_C2"])
            c2, cc = self.cita(k, rel, ["C2_" + d, "p_sup" if sentido == "sup" else "p_inf", [0, 1]])
            certs = [{"cita": cc, "localizador_punto": ["puntos", "sup_C2" if sentido == "sup" else "inf_C2"],
                      "punto_del_certificado": copy.deepcopy(punto)}]
            idx, fctx, regla_ctx = self.contexto_de(h, sentido), None, REGLA_CTX_DF_F
            regla_c2 = "unico"
        c = self.univ[h][idx]
        pt = {p: float(punto[p]) for p in STRUCT}
        k1 = self.K1(pt, c)
        cota, respalda = self.respaldo(sentido, c2, k1, L, U)
        return {"claim_id": h, "instrumento": j, "pais": f["pais"], "diseno": d, "L": L, "U": U, "convergida": conv,
                "fuente_cota": fc, "fuente_estado": fes,
                "testigo": {"punto": pt, "fuente_punto": fp, "contexto": self.ctx_key(c), "indice_contexto": idx,
                            "regla_contexto": regla_ctx, "fuente_contexto": fctx,
                            "claim_id_hoja": h, "instrumento_hoja": j, "pais_hoja": f["pais"],
                            "C2_en_punto": [float(c2[0]), float(c2[1])], "certificados_C2": certs, "regla_C2": regla_c2,
                            "K1_en_punto": [k1.lo, k1.hi], "regla_K1": REGLA_K1, "cota_que_respalda": cota, "respalda": respalda}}

    # -------------------------------------------------------------------------------------------- fila canónica
    def fila(self, cid, sentido, d):
        f = campos(cid)
        hs = [self.hoja(h, sentido) for h in self.hojas[cid]]
        if f["fam"] == "ci":
            real = hs[0]
            L, U = real["L"], real["U"]
        else:
            if sentido == "sup":
                L, U = max(x["L"] for x in hs), max(x["U"] for x in hs)
                real = min(hs, key=lambda x: (-x["L"], ORDEN_J[x["instrumento"]], x["pais"], x["claim_id"]))
            else:
                L, U = min(x["L"] for x in hs), min(x["U"] for x in hs)
                real = min(hs, key=lambda x: (x["U"], ORDEN_J[x["instrumento"]], x["pais"], x["claim_id"]))
        otros = [x for x in hs if x is not real]
        ident = all(real["L"] > x["U"] for x in otros) if sentido == "sup" else all(real["U"] < x["L"] for x in otros)
        estado = "pass" if (U - L <= T2_G and all(x["convergida"] for x in hs)) else "incomplete"
        univ_c = Counter(json.dumps(k) for k in self.ctx_keys[cid])
        univ_h = sum((Counter(json.dumps(k) for k in self.ctx_keys[h]) for h in self.hojas[cid]), Counter())
        if univ_c != univ_h:
            raise Rechazo("E_UNIVERSO", "el universo de %s no es la suma de los de sus hojas" % cid)
        r = {"extreme_id": eid(cid, sentido), "claim_id": cid, "familia": f["fam"], "diseno": d,
             "instrumento": "df" if f["fam"] == "ci" else None, "sentido": sentido, "objeto": "G_best", "L": L, "U": U,
             "brecha": U - L, "estado": estado, "categoria_v4": self.reg[cid]["categoria"], "testigo": copy.deepcopy(real["testigo"]),
             "hoja_ganadora_identificada": ident, "nota_hoja_ganadora": NOTA_HOJA if ident else NOTA_SOLAPE,
             "universo": {"n": sum(univ_c.values()), "multiconjunto_sha256": multiconjunto_sha([json.loads(k) for k in univ_c.elements()]),
                          "igual_a_suma_de_hojas": True}}
        if f["fam"] == "ci":
            r["fuente_cota"], r["fuente_estado"] = real["fuente_cota"], real["fuente_estado"]
        else:
            r["componentes"] = [{"claim_id": x["claim_id"], "instrumento": x["instrumento"], "pais": x["pais"], "L": x["L"], "U": x["U"],
                                 "convergida": x["convergida"], "fuente_cota": x["fuente_cota"], "fuente_estado": x["fuente_estado"]} for x in hs]
            r["procedencia"] = "%s <- %s (testigo de la hoja que realiza la cota; regla %s)" % (
                cid, real["claim_id"], "max L (sup)" if sentido == "sup" else "min U (inf)")
        return r

    def fila_canonica(self, e):
        return json.loads(self._canon[e])

    def tabla(self):
        return {"etiqueta": ETIQUETA, "no_exportable": True, "tabla": NOMBRE_TABLA, "version": VERSION,
                "alcance": {"tipo": "seleccion_completa", "seleccion": SELECCION, "disenos": list(DISENOS),
                            "filas_esperadas": len(self.esperadas), "extreme_ids": None},
                "T2_G": T2_G, "filas": [self.fila_canonica(e) for e in self.orden]}


# ================================================================================================ validador
def validar_tabla(ref: Referencia, doc) -> dict:
    """Valida un documento ya cargado. Nunca lanza: cualquier fallo es una violación con código."""
    viol = []

    def v(codigo, clave, detalle=""):
        viol.append({"codigo": codigo, "fila": clave, "detalle": str(detalle)[:400]})
    tipo = None
    n_filas = None
    try:
        tipo, n_filas = _validar(ref, doc, v)
    except Rechazo as e:
        v(e.codigo, None, e.detalle)
    except Exception as e:  # noqa: BLE001  (rechazo controlado de cualquier error no previsto)
        v("E_ESQUEMA", None, "%s: %s" % (type(e).__name__, e))
    return {"cumple": tipo == "seleccion_completa" and not viol, "tipo": tipo, "valida_parcial": tipo == "parcial" and not viol,
            "entrega_completa": tipo == "seleccion_completa" and not viol, "n_filas": n_filas, "violaciones": viol,
            "codigos": sorted({x["codigo"] for x in viol})}


def _validar(ref, doc, v):
    comprobar(doc, getattr(ref, "esquema_doc", ESQUEMA_DOC))     # CACHE FINAL P0: la Referencia v4 (e13_v4.py) declara su esquema
    if "NO OFICIAL" not in doc["etiqueta"]:
        raise Rechazo("E_ESQUEMA", "$.etiqueta: debe declarar NO OFICIAL")
    alc = doc["alcance"]
    tipo = alc["tipo"]
    # ---- identidad de las filas (antes de cualquier uso como clave: solo ids hex16 válidos entran en el conteo)
    ids, validas = [], []
    for i, f in enumerate(doc["filas"]):
        if not isinstance(f, dict) or not (isinstance(f.get("extreme_id"), str) and HEX16.match(f["extreme_id"])):
            v("E_ESQUEMA", "#%d" % i, "fila sin extreme_id hexadecimal de 16 (o no es un objeto)")
            continue
        ids.append(f["extreme_id"])
        validas.append((i, f))
    vistos = Counter(ids)
    for e, n in vistos.items():
        if n > 1:
            v("E_DUPLICADA", e, "%d filas" % n)
    esperadas = dict(ref.esperadas)
    if tipo == "seleccion_completa":
        if alc["extreme_ids"] is not None:
            v("E_ALCANCE", None, "una selección completa no lleva extreme_ids")
        if alc["filas_esperadas"] != len(esperadas) or alc["disenos"] != getattr(ref, "disenos", DISENOS):
            v("E_ALCANCE", None, "filas_esperadas o diseños distintos de la selección autenticada")
    else:
        sub = alc["extreme_ids"]
        if sub is None:
            v("E_ALCANCE", None, "alcance parcial sin extreme_ids")
            sub = []
        if len(set(sub)) != len(sub):
            v("E_ALCANCE", None, "extreme_ids repetidos en el alcance parcial")
        fuera = [e for e in sub if e not in esperadas]
        if fuera:
            v("E_ALCANCE", None, "extreme_ids del alcance fuera de la selección: %s" % fuera[:5])
        if alc["filas_esperadas"] != len(set(sub)):
            v("E_ALCANCE", None, "filas_esperadas distinto del número de extreme_ids")
        dis = sorted({esperadas[e][2] for e in sub if e in esperadas})
        if alc["disenos"] != dis:
            v("E_ALCANCE", None, "diseños del alcance distintos de los de sus extreme_ids")
        esperadas = {k: x for k, x in esperadas.items() if k in set(sub)}
    for e in esperadas:
        if e not in vistos:
            v("E_FALTA", e, "%s|%s" % esperadas[e][:2])
    for e in vistos:
        if e not in esperadas:
            v("E_SOBRA", e, "fila no esperada en el alcance")
    orden = [e for e in ref.orden if e in esperadas]
    if set(vistos) == set(esperadas) and all(n == 1 for n in vistos.values()) and ids != orden:
        v("E_ORDEN", None, "filas fuera del orden canónico (diseño, claim_id, sentido)")
    for i, f in validas:
        clave = f["extreme_id"]
        if clave not in esperadas:
            continue
        try:
            _validar_fila(ref, f, esperadas[clave], v)
        except Rechazo as e:
            v(e.codigo, clave, e.detalle)
        except Exception as e:  # noqa: BLE001
            v("E_ESQUEMA", clave, "%s: %s" % (type(e).__name__, e))
    ref.reverificar_fuentes()
    return tipo, len(doc["filas"])


def _validar_fila(ref, f, esperada, v):
    c, s, d = esperada
    clave = f["extreme_id"]
    fc = campos(c)
    comprobar(f, ESQUEMA_FILA_CI if fc["fam"] == "ci" else ESQUEMA_FILA_AGR, "$.filas[%s]" % clave)
    esp = ref.fila_canonica(clave)
    # ---- identidad
    if f["extreme_id"] != eid(f["claim_id"], f["sentido"]):
        v("E_IDENTIDAD", clave, "extreme_id no corresponde a claim_id|sentido")
    for k in ("claim_id", "familia", "diseno", "instrumento", "sentido"):
        if diferencias(f[k], esp[k]):
            v("E_IDENTIDAD", clave, "%s distinto de la selección autenticada" % k)
    # ---- límites, estado y clasificación
    if not f["L"] <= f["U"]:
        v("E_LIMITES", clave, "L > U")
    if abs(f["brecha"] - (f["U"] - f["L"])) > TOL * max(1.0, abs(f["U"])):
        v("E_LIMITES", clave, "brecha distinta de U − L")
    if diferencias([f["L"], f["U"], f["brecha"]], [esp["L"], esp["U"], esp["brecha"]]):
        v("E_VINCULO", clave, "límites distintos de los recalculados: tabla %r, fuente %r" % ([f["L"], f["U"]], [esp["L"], esp["U"]]))
    if f["estado"] != esp["estado"]:
        v("E_ESTADO", clave, "estado %s; según las fuentes %s" % (f["estado"], esp["estado"]))
    if f["categoria_v4"] != esp["categoria_v4"]:
        v("E_VINCULO", clave, "categoría v4 distinta del registro")
    # ---- citas de la fila
    for nombre in (["fuente_cota"] if fc["fam"] == "ci" else []):
        _cita(ref, f[nombre], esp[nombre], v, clave, nombre)
    if fc["fam"] == "ci":
        for i, ci in enumerate(f["fuente_estado"]):
            _cita(ref, ci, esp["fuente_estado"][i] if i < len(esp["fuente_estado"]) else None, v, clave, "fuente_estado[%d]" % i)
        if diferencias(f["fuente_cota"]["valor"], [f["L"], f["U"]]):
            v("E_VINCULO", clave, "L, U distintos del valor citado en fuente_cota")
    # ---- testigo
    t, te = f["testigo"], esp["testigo"]
    hoja = t["claim_id_hoja"]
    if hoja not in ref.univ or (fc["fam"] == "ci" and hoja != c) or (fc["fam"] != "ci" and hoja not in ref.hojas[c]):
        v("E_TESTIGO_HOJA", clave, "hoja del testigo desconocida o ajena a la afirmación")
        return
    fh = campos(hoja)
    if t["instrumento_hoja"] != fh["j"] or t["pais_hoja"] != fh["pais"] or fh["dis"] != d:
        v("E_TESTIGO_HOJA", clave, "instrumento, país o diseño del testigo distintos de su hoja")
    if hoja != te["claim_id_hoja"]:
        v("E_TESTIGO_DISTINTO", clave, "hoja del testigo distinta de la que realiza la cota (regla: %s)" % te["claim_id_hoja"])
    ok_p, motivo = ref.admisible(t["punto"], d, fh["j"])
    if not ok_p:
        v("E_TESTIGO_PUNTO", clave, motivo)
    _cita(ref, t["fuente_punto"], te["fuente_punto"], v, clave, "testigo.fuente_punto")
    if {p: float(t["fuente_punto"]["valor"][p]) for p in STRUCT if isinstance(t["fuente_punto"]["valor"], dict) and p in t["fuente_punto"]["valor"]} != t["punto"]:
        v("E_TESTIGO_PUNTO", clave, "el punto no es el valor citado en fuente_punto")
    if diferencias(t["punto"], te["punto"]):
        v("E_TESTIGO_DISTINTO", clave, "punto distinto del testigo de la fuente")
    # índice y contexto: el índice DEBE dar, en el universo de la hoja, exactamente el contexto serializado
    idx = t["indice_contexto"]
    if idx >= len(ref.univ[hoja]):
        v("E_TESTIGO_INDICE", clave, "indice_contexto %d fuera del universo de la hoja (n = %d)" % (idx, len(ref.univ[hoja])))
        cx = None
    else:
        cx = ref.univ[hoja][idx]
        if ref.ctx_keys[hoja][idx] != t["contexto"]:
            v("E_TESTIGO_INDICE", clave, "el contexto del índice %d no es el serializado" % idx)
    if idx != te["indice_contexto"] or diferencias(t["contexto"], te["contexto"]):
        v("E_TESTIGO_CONTEXTO", clave, "índice o contexto distintos del testigo canónico (índice %d)" % te["indice_contexto"])
    if t["contexto"][0] != d or t["contexto"][1] != fh["j"]:
        v("E_TESTIGO_CONTEXTO", clave, "diseño o instrumento del contexto distintos de la hoja")
    if t["regla_contexto"] != te["regla_contexto"] or diferencias(t["fuente_contexto"], te["fuente_contexto"]):
        v("E_TESTIGO_CONTEXTO", clave, "regla o fuente del contexto distintas de las canónicas")
    if t["fuente_contexto"] is not None:
        _cita(ref, t["fuente_contexto"], te["fuente_contexto"], v, clave, "testigo.fuente_contexto")
        if t["fuente_contexto"]["valor"] != idx:
            v("E_TESTIGO_INDICE", clave, "indice_contexto distinto del citado en fuente_contexto")
    # C2: certificados citados (todos), regla de combinación y valor
    if len(t["certificados_C2"]) != len(te["certificados_C2"]) or t["regla_C2"] != te["regla_C2"]:
        v("E_TESTIGO_C2", clave, "certificados de C2 o regla de combinación distintos de los usados")
    los, his = [], []
    for i, ce in enumerate(t["certificados_C2"]):
        _cita(ref, ce["cita"], te["certificados_C2"][i]["cita"] if i < len(te["certificados_C2"]) else None, v, clave, "testigo.certificados_C2[%d]" % i)
        val = ce["cita"]["valor"]
        try:
            lo, hi = _par_c2(val)
        except (KeyError, TypeError, IndexError, ValueError):
            v("E_TESTIGO_C2", clave, "certificado %d sin par [lo, hi] reconocible" % i)
            continue
        los.append(lo)
        his.append(hi)
        _cita_punto(ref, ce, t["punto"], v, clave, i)
    if los:
        comb = [max(los), min(his)]
        if diferencias(comb, t["C2_en_punto"]):
            v("E_TESTIGO_C2", clave, "C2_en_punto %r no es la combinación de los certificados citados %r" % (t["C2_en_punto"], comb))
    if diferencias(t["C2_en_punto"], te["C2_en_punto"]):
        v("E_TESTIGO_C2", clave, "C2_en_punto distinto del recalculado desde las fuentes %r" % (te["C2_en_punto"],))
    # K1: recalculado con el contexto del ÍNDICE serializado y el punto serializado
    if cx is not None:
        k1 = ref.K1(t["punto"], cx)
        if diferencias(t["K1_en_punto"], [k1.lo, k1.hi]):
            v("E_TESTIGO_K1", clave, "K1_en_punto %r distinto del recalculado %r" % (t["K1_en_punto"], [k1.lo, k1.hi]))
    if diferencias(t["K1_en_punto"], te["K1_en_punto"]):
        v("E_TESTIGO_K1", clave, "K1_en_punto distinto del canónico")
    # respaldo: recalculado con C2 y K1 SERIALIZADOS y con los canónicos
    Iv = ref.Iv
    cota, resp = ref.respaldo(s, t["C2_en_punto"], Iv(t["K1_en_punto"][0], t["K1_en_punto"][1]), esp["L"], esp["U"])
    if not resp or not te["respalda"]:
        v("E_TESTIGO_RESPALDO", clave, "con C2 y K1 en el mismo punto, el testigo no respalda la cota (%r)" % cota)
    if diferencias(t["cota_que_respalda"], te["cota_que_respalda"]) or diferencias(cota, te["cota_que_respalda"]):
        v("E_TESTIGO_RESPALDO", clave, "cota_que_respalda distinta de la recalculada")
    # ---- hoja ganadora (no optimizador continuo)
    if f["hoja_ganadora_identificada"] != esp["hoja_ganadora_identificada"]:
        v("E_OPTIMIZADOR", clave, "identificación de la hoja ganadora sin evidencia o contraria a ella")
    # ---- universo
    if diferencias(f["universo"], esp["universo"]):
        v("E_UNIVERSO", clave, "multiconjunto de contextos distinto del recalculado")
    # ---- componentes y agregación
    if fc["fam"] != "ci":
        comp, ec = f["componentes"], esp["componentes"]
        if [x["claim_id"] for x in comp] != [x["claim_id"] for x in ec]:
            v("E_COMPONENTES", clave, "componentes faltantes, inesperadas, duplicadas o fuera de orden")
        else:
            for y, x in zip(comp, ec):
                if diferencias([y["instrumento"], y["pais"], y["L"], y["U"], y["convergida"]], [x["instrumento"], x["pais"], x["L"], x["U"], x["convergida"]]):
                    v("E_COMPONENTES", clave, "valores de la componente %s distintos de su fuente" % x["claim_id"])
                _cita(ref, y["fuente_cota"], x["fuente_cota"], v, clave, "componente %s fuente_cota" % x["claim_id"])
                for i, ci in enumerate(y["fuente_estado"]):
                    _cita(ref, ci, x["fuente_estado"][i] if i < len(x["fuente_estado"]) else None, v, clave, "componente %s fuente_estado" % x["claim_id"])
                if diferencias(y["fuente_cota"]["valor"], [y["L"], y["U"]]):
                    v("E_COMPONENTES", clave, "L, U de la componente %s distintos de su cita" % x["claim_id"])
        agg = max if s == "sup" else min
        Lc, Uc = agg(x["L"] for x in comp), agg(x["U"] for x in comp)
        if diferencias([f["L"], f["U"]], [Lc, Uc]):
            v("E_AGREGADO", clave, "límites agregados distintos del %s de las componentes de la tabla" % agg.__name__)
        conv = all(x["convergida"] for x in comp)
        if f["estado"] == "pass" and not (conv and f["U"] - f["L"] <= T2_G):
            v("E_AGREGADO", clave, "pass con componentes sin convergencia o brecha > T2")
        realiza = [x for x in comp if x["claim_id"] == hoja]
        if not realiza or (s == "sup" and realiza[0]["L"] != Lc) or (s == "inf" and realiza[0]["U"] != Uc):
            v("E_AGREGADO", clave, "la hoja del testigo no realiza la cota agregada de la tabla")
    # ---- descriptivos: validados, nunca consumidos
    for k in ("nota_hoja_ganadora", "procedencia"):
        if k in esp and f.get(k) != esp[k]:
            v("E_DESCRIPTIVO", clave, "%s distinto del canónico (campo descriptivo)" % k)
    # ---- cierre: igualdad estricta con la fila canónica (ningún campo escapa al vínculo)
    dif = diferencias(f, esp)
    if dif:
        v("E_VINCULO", clave, "campos distintos de la fila canónica: %s" % dif[:8])


def _par_c2(val):
    """[lo, hi] de un certificado citado por proyección: {L, U}, {L_punto, U} o [lo, hi]."""
    if isinstance(val, dict) and set(val) == {"L_punto", "U"}:
        lo, hi = val["L_punto"], val["U"]
    elif isinstance(val, dict) and set(val) == {"L", "U"}:
        lo, hi = val["L"], val["U"]
    elif isinstance(val, list) and len(val) == 2:
        lo, hi = val
    else:
        raise ValueError("par")
    if not (_es_float(lo) and _es_float(hi) and lo <= hi):
        raise ValueError("par")
    return float(lo), float(hi)


def _cita_punto(ref, ce, punto, v, clave, i):
    """El punto del certificado (en su localizador) coincide con el del testigo en los ejes que el certificado fija."""
    c = ce["cita"]
    try:
        pv = resolver(ref.leer(c["clave"], c["archivo"]), ce["localizador_punto"])
    except Rechazo as e:
        v(e.codigo, clave, "certificado %d: %s" % (i, e.detalle))
        return
    if diferencias(pv, ce["punto_del_certificado"]):
        v("E_TESTIGO_C2", clave, "certificado %d: punto_del_certificado no es el que hay en su localizador" % i)
        return
    if isinstance(pv, dict):
        comunes = [p for p in STRUCT if p in pv]
        if not comunes or any(float(pv[p]) != punto[p] for p in comunes):
            v("E_TESTIGO_C2", clave, "certificado %d de otro punto" % i)
    elif not (_es_float(pv) and float(pv) == punto["a"]):
        v("E_TESTIGO_C2", clave, "certificado %d de otro a" % i)


def _cita(ref, c, canon, v, clave, nombre):
    try:
        ref.verificar_cita(c)
    except Rechazo as e:
        v(e.codigo, clave, "%s: %s" % (nombre, e.detalle))
        return
    if canon is None or diferencias(c, canon):
        v("E_FUENTE", clave, "%s: cita distinta de la usada por el cálculo canónico" % nombre)


# ================================================================================================ consumo canónico
class TestigosValidados:
    """Lo ÚNICO que consume la vía de celda por valores: testigos CANÓNICOS (de la referencia, inmutables) de una tabla
    que validó entera. Los bytes de la tabla no se entregan; los campos descriptivos no se incluyen."""

    CAMPOS = ("claim_id_hoja", "instrumento_hoja", "pais_hoja", "punto", "indice_contexto", "contexto", "C2_en_punto", "K1_en_punto")

    def __init__(self, ref, doc, *, permitir_parcial=False):
        r = validar_tabla(ref, doc)
        if not (r["cumple"] or (permitir_parcial and r["valida_parcial"])):
            raise Rechazo("E_TABLA_NO_VALIDA", "la tabla no valida (%s); no se entrega ningún testigo" % r["codigos"])
        self.entrega_completa = r["entrega_completa"]
        self.validacion = r
        self._t = {}
        for f in doc["filas"]:
            e = f["extreme_id"]
            c = ref.fila_canonica(e)
            self._t[e] = congelar(dict({k: c["testigo"][k] for k in self.CAMPOS}, diseno=c["diseno"], sentido=c["sentido"],
                                       extreme_id=e, claim_id=c["claim_id"]))

    def ids(self):
        return sorted(self._t)

    def __getitem__(self, e):
        return self._t[e]


# ================================================================================================ CLI


# ================================================================================================ funciones incorporadas
# (misma lógica que codigo/extremos_dfd.grupo, codigo/extremos_G.preparar y codigo/demo/cobertura_compartida.q_pot_exact)
def _nec(t, codigo):
    if not t:
        raise Rechazo("E_REFERENCIA", codigo)


def _q_pot_ingenuo():
    from paper2b import cobertura as _COV
    if not hasattr(_COV, "_q_pot_original"):
        _COV._q_pot_original = _COV.q_pot          # la cota natural, antes de sustituirla por la exacta
    return _COV._q_pot_original


def q_pot_exact(box):
    """Rango EXACTO de q_pot por vértices (monotonía en a, ρ y κ̃ en el dominio admisible); si no aplica, la natural."""
    NAIVE = _q_pot_ingenuo()
    a, rho, k = box["a"], box["rho"], box["kappa_tilde"]
    if not (a[0] > 1.0 and rho[1] <= 1.0 and a[0] - rho[1] > 0 and k[0] > 0):
        return NAIVE(box)
    from paper2b.intervalos import Iv
    lo = NAIVE({"a": (a[0], a[0]), "rho": (rho[0], rho[0]), "kappa_tilde": (k[0], k[0])}).lo
    hi = NAIVE({"a": (a[1], a[1]), "rho": (rho[1], rho[1]), "kappa_tilde": (k[1], k[1])}).hi
    return Iv(lo, hi)


def grupo(raiz, dis, j):
    """Caja completa del soporte, fijos y barras del grupo (diseño, instrumento) del plan AUTENTICADO."""
    base, inv_h, rel = FUENTE_PLAN
    inv_raw = (Path(raiz) / base / "audit/entrega.json").read_bytes()
    _nec(sha(inv_raw) == inv_h, "INVENTARIO:" + base)
    raw = (Path(raiz) / base / rel).read_bytes()
    _nec(json.loads(inv_raw)["files"][rel]["sha256"] == sha(raw), "NO_AUTENTICADO:" + rel)
    plan, h = json.loads(raw), sha(raw)
    gs = [g for g in plan["grupos"] if g["clave"]["diseno"] == dis and g["clave"]["instrumento"] == j]
    _nec(len(gs) == 1, "GRUPO_NO_UNICO")
    key = gs[0]["clave"]
    full = {p: (float.fromhex(v[0]), float.fromhex(v[1])) for p, v in key["caja"].items()}
    fixed = dict(key["fijos"])
    from paper2b import cobertura as COV
    _q_pot_ingenuo()
    COV.q_pot = q_pot_exact              # rango EXACTO de q_pot por vértices (como c2_extremos); la natural no prueba q_pot < 1
    _nec(COV.box_admissible(full, fixed), "CAJA_NO_ADMISIBLE")
    return {"grupo": gs[0]["grupo"], "sid_ref": gs[0]["sid_ref"], "plan_sha256": h, "full": full, "fixed": fixed,
            "bd": float(fixed["bar_tau_d"]), "bf": float(fixed["bar_tau_f"])}


def preparar(ctx, dis, cids):
    """Contextos oficiales por conjunto (Universo) de las afirmaciones, fijos y ejes comunes comprobados."""
    from decimal import Decimal
    from paper2b import run as RUNMOD
    from paper2b import seleccion_valores as SV
    claims = {c.claim_id: c for c in ctx.claims}
    sets = sorted({s for cid in cids for s in claims[cid].support_sets})
    runs = {sid: ctx.run(sid, "extremos:" + sid) for sid in sets}
    ref_sid = claims[CLAIM_P3B].support_sets[0]
    if ref_sid not in runs:
        runs[ref_sid] = ctx.run(ref_sid, "extremos:" + ref_sid)
    axes = runs[ref_sid].struct_axes(ref_sid)
    _nec(all(runs[s].struct_axes(s) == axes for s in runs), "EJES_DISTINTOS_NO_SE_COMPARTE")
    ax0 = SV.axes_nodes(ctx.view, ctx.cfg, ref_sid)
    corner = {p: Decimal(str(ax0[p][0])) for p in RUNMOD.STRUCT}
    U = SV.Universo(runs, SV.qmin_table(ctx.inp.grid_cells))
    univ, fixed_ref, fx_set = {}, None, set()
    for cid in cids:
        cl = claims[cid]
        cx = []
        for sid in cl.support_sets:
            c, fx = U.contexts(cl, sid, corner)
            cx += [x for x, _ in c]
            fixed_ref = fixed_ref or fx
            fx_set.add(json.dumps(fx, sort_keys=True, default=str))
        univ[cid] = cx
    _nec(len(fx_set) == 1, "FIJOS_DISTINTOS")
    return {"univ": univ, "fixed": fixed_ref, "model": runs[ref_sid].model, "axes": axes}


_q_pot_ingenuo()      # captura la cota NATURAL de q_pot al importar, antes de cualquier sustitución (como cobertura_compartida.NAIVE)
