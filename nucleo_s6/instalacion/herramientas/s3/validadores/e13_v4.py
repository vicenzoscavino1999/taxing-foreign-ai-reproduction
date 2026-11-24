"""E13 v4 CANDIDATA integrada (CACHE FINAL P0 H4 3.7; catálogo CENSO-v2 con M3 en P0 COMPLETO H4 3.7, NO OFICIAL; copia
candidata, no incorporada).

`global_extreme` v4 = v3 PARAMETRIZADA POR CATÁLOGO de fuentes autenticadas (lógica de codigo/global_extreme_v4.py,
entrega integracion_e12_paso4_3_7_2026-10-07_lima0746), integrada en la estructura candidata como SUBCLASE de la Referencia v3
del candidato (herramientas/s3/validadores/e13_referencia.py). La v3 sigue siendo la que usan las selecciones y productores
anteriores (DEMO, PILOTO, COMPLEMENTO-A/B): su comportamiento no cambia.

Interfaz explícita: Referencia(ctx, raiz, catalogo). Reglas de catálogo:
- «propagacion»: la selección guardada por la propagación autenticada (SEL-PROPAGACION-DF-v1). Con CATALOGO_PROPAGACION la
  tabla es IGUAL a la v3 (prueba de no regresión).
- «fuentes_df» (v4 de lima0746): ci-df = hojas df de las fuentes declaradas; country/global solo con TODAS sus hojas con
  fuente autenticada (ci-d: XDD y PRV completas; ci-f: CAN completa).
- «hojas_completas» (CENSO, esta ronda): como «fuentes_df» para las filas de la tabla y, ADEMÁS, el universo de contextos de
  TODAS las hojas ci del registro v4 con fuente autenticada, para que Referencia.hoja() dé su testigo canónico (ci-d y ci-f
  desde sus producciones completas, SIN recalcular). Esas hojas no añaden filas a la tabla.
Las fuentes ci-df se leen siempre por la cadena autenticada (CADENA de la v3: inventario + archivo); una hoja ci-df sin fuente
en el catálogo da Rechazo(E_FUENTE) en hoja(): nunca se fabrica autoridad.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

_V3 = Path(__file__).with_name("e13_referencia.py")
if "cand_e13_referencia" in sys.modules:
    V3 = sys.modules["cand_e13_referencia"]
else:
    _spec = importlib.util.spec_from_file_location("cand_e13_referencia", _V3)
    V3 = importlib.util.module_from_spec(_spec)
    sys.modules["cand_e13_referencia"] = V3
    _spec.loader.exec_module(V3)

Rechazo, campos, ci_de, eid, sha = V3.Rechazo, V3.campos, V3.ci_de, V3.eid, V3.sha
CATALOGO_PROPAGACION = {"seleccion": "SEL-PROPAGACION-DF-v1", "disenos": ["G", "N"], "regla": "propagacion",
                        "df": {"G": [("SEL", "demo/hito2/extremos_G_df_v5_G.json")], "N": [("SEL", "demo/hito2/extremos_G_df_v5_N.json")]}}
CATALOGO_MUESTRA = {"seleccion": "SEL-MUESTRA-DF-v1+AGREGADAS", "disenos": ["G", "N"], "regla": "fuentes_df",
                    "df": {"G": [("SEL", "demo/hito2/muestra_G_df_G.json")], "N": [("SEL", "demo/hito2/muestra_G_df_N.json")]}}
CATALOGO_CENSO = {"seleccion": "CENSO-HOJAS-CI-v1", "disenos": ["G", "N"], "regla": "hojas_completas",
                  "df": {"G": [("SEL", "demo/hito2/extremos_G_df_v5_G.json"), ("SEL", "demo/hito2/muestra_G_df_G.json")],
                         "N": [("SEL", "demo/hito2/extremos_G_df_v5_N.json"), ("SEL", "demo/hito2/muestra_G_df_N.json")]}}
# P0 COMPLETO: CENSO-v2 = CENSO-v1 + la muestra continuada M3 (lima0003): 20 ci-df más (40 pares). Sus puntos U citan los mismos
# archivos de techo de lima0754 (ruta relativa ../cierre_G_df_...); se normalizan a la clave SEL y se autentican igual.
CATALOGO_CENSO_V2 = {"seleccion": "CENSO-HOJAS-CI-v2", "disenos": ["G", "N"], "regla": "hojas_completas",
                     "df": {d: CATALOGO_CENSO["df"][d] + [("M3", "demo/h4/inf_cidf/muestra_continuada_%s.json" % d)] for d in ("G", "N")}}

# P1A PILOTO: CENSO-v3 = CENSO-v2 + las ci-df de P1a con AMBOS sentidos convergidos y VALIDADOS sin histórico
# (codigo/validar_nuevos_cidf.py), exportadas por codigo/exportar_p1a.py a una fuente con inventario propio (clave P1A).
CATALOGO_CENSO_V3 = {"seleccion": "CENSO-HOJAS-CI-v3", "disenos": ["G", "N"], "regla": "hojas_completas",
                     "df": {d: CATALOGO_CENSO_V2["df"][d] + [("P1A", "demo/h4/p1a/extremos_p1a_%s.json" % d)] for d in ("G", "N")}}

# P1B GLOBAL: CENSO-v4a = CENSO-v2 + P1AT (los 12 de P1a con traza, validación v2 y exportación vinculada). CENSO-v3 (P1A sin
# respaldo global verificable) se conserva solo como evidencia histórica.
CATALOGO_CENSO_V4A = {"seleccion": "CENSO-HOJAS-CI-v4a", "disenos": ["G", "N"], "regla": "hojas_completas",
                      "df": {d: CATALOGO_CENSO_V2["df"][d] + [("P1AT", "demo/h4/p1b/extremos_validados_%s.json" % d)] for d in ("G", "N")}}

# P1B GLOBAL: CENSO-v4 = CENSO-v4a + las ci-df de P1b validadas y exportadas con vínculo (una fuente por trabajador)
CATALOGO_CENSO_V4 = {"seleccion": "CENSO-HOJAS-CI-v4", "disenos": ["G", "N"], "regla": "hojas_completas",
                     "df": {d: CATALOGO_CENSO_V4A["df"][d] + [("P1BW%d" % w, "demo/h4/p1b/extremos_validados_%s.json" % d) for w in [0, 1, 2]] for d in ("G", "N")}}


def rel_sel(archivo):
    """Ruta de un archivo de techo citado por una fuente ci-df, relativa a la entrega SEL (lima0754). Las fuentes de lima0754
    citan «demo/hito2/...»; M3 (lima0003) cita «../cierre_G_df_3_7_2026-10-06_lima0754/demo/hito2/...». Otra cosa: Rechazo."""
    pref = "../" + V3.CADENA["SEL"][0] + "/"
    if archivo.startswith(pref):
        return archivo[len(pref):]
    if archivo.startswith("../") or archivo.startswith("/") or ":" in archivo:
        raise Rechazo("E_FUENTE", "techo citado fuera de la entrega SEL: %s" % archivo)
    return archivo


def esquema_doc(seleccion, max_ids=64):
    """Esquema del documento con el identificador de selección del catálogo (como codigo/global_extreme_v4.esquema_doc)."""
    alc = ("dict", {"tipo": ("enum", ["seleccion_completa", "parcial"]), "seleccion": ("const", seleccion),
                    "disenos": ("lista", ("enum", V3.DISENOS), 1, 2), "filas_esperadas": "int0",
                    "extreme_ids": ("nulo_o", ("lista", "hex16", 1, max_ids))})
    return ("dict", {"etiqueta": "str", "no_exportable": ("const", True), "tabla": ("const", V3.NOMBRE_TABLA),
                     "version": ("const", V3.VERSION), "alcance": alc, "T2_G": ("const", V3.T2_G), "filas": ("lista", "json", 0, 100000)})


class Referencia(V3.Referencia):
    """Referencia v4 (catálogo). Misma construcción que la v3 salvo la fuente ci-df (catálogo) y la selección (regla)."""

    def __init__(self, ctx, raiz, catalogo=None):
        if ctx is None:
            raise Rechazo("E_CONTEXTO", "la Referencia exige el contexto S5 explícito")
        from paper2b import cobertura as COV
        from paper2b.intervalos import Iv
        self.T = Path(raiz)
        self.COV, self.Iv, self.qpe = COV, Iv, V3.q_pot_exact
        t0 = time.time()
        self.ctx = ctx
        COV.q_pot = V3.q_pot_exact
        self.catalogo = catalogo or CATALOGO_PROPAGACION
        self.seleccion_id, self.disenos = self.catalogo["seleccion"], list(self.catalogo["disenos"])
        self.fuente_df, self.excluidas, self.hojas_censo, self.duplicadas_df = {}, [], {}, []
        self._obj, self._ref, self._raw_sha = {}, {}, {}
        self.reg = self.leer("RES", "demo/registro/registro_candidato_v4.json")["afirmaciones"]
        self.xdd = self.leer("XDD", "demo/extremos/extremos_G_d.json")
        self.can = self.leer("CAN", "demo/extremos/extremos_G_f.json")
        self.prop, self.prod, self.sred, self.techos = {}, {}, {}, {}
        self.univ, self.grupo, self.esperadas, self.hojas, self.arch = {}, {}, {}, {}, {}
        for d in self.disenos:
            self.arch[("prop", d)] = tuple(self.catalogo["df"][d][0])
            self.arch[("prod", d)] = ("PRV", "demo/hito2/produccion_inf_G_cid_%s.json" % d)
            self.arch[("sred", d)] = ("PRV", "demo/hito2/sred_%s_df.json" % d)
            self.prop[d] = self.leer(*self.arch[("prop", d)])
            self.prod[d] = self.leer(*self.arch[("prod", d)])
            self.sred[d] = self.leer(*self.arch[("sred", d)])
            vistos_t = set()
            for kf, relf in self.catalogo["df"][d]:
                fobj = self.leer(kf, relf)
                for hh in fobj["ci_df"]:
                    if campos(hh)["dis"] == d:
                        if hh in self.fuente_df:
                            self.duplicadas_df.append((hh, self.fuente_df[hh], (kf, relf)))   # se queda la PRIMERA fuente
                        self.fuente_df.setdefault(hh, (kf, relf))
                for f in fobj["puntos_U"]["fuentes"]:
                    ra = rel_sel(f["archivo"])
                    obj = self.leer("SEL", ra)
                    if self._ref[("SEL", ra)]["sha256"] != f["sha256"]:
                        raise Rechazo("E_FUENTE", "techo citado por la propagación con otro sha256: %s" % f["archivo"])
                    for i, fila in enumerate(obj["filas"]):
                        if fila.get("admisible") and "U" in fila and (ra, i) not in vistos_t:
                            vistos_t.add((ra, i))
                            self.techos.setdefault(d, []).append((fila["theta"], ra, i, bool(fila.get("incompatible"))))
            sel = self.seleccion_de(d)
            for j in ("d", "df", "f"):
                g = V3.grupo(self.T, d, j)
                self.grupo[(d, j)] = (g["full"], g["fixed"])
            gl = [sel["g"]] if isinstance(sel["g"], str) else list(sel["g"])
            cids = list(sel["ci_df"]) + list(sel["country"]) + gl
            for c in cids:
                for s in ("sup", "inf"):
                    self.esperadas[eid(c, s)] = (c, s, d)
            hojas_all = set(sel["ci_df"])
            for c in sel["country"]:
                self.hojas[c] = [ci_de(c, j) for j in ("d", "df", "f")]
                hojas_all |= set(self.hojas[c])
            for g_ in gl:
                gf = campos(g_)
                self.hojas[g_] = sorted({h for c in sel["country"] if (campos(c)["pid"], campos(c)["kind"], campos(c)["resto"]) ==
                                         (gf["pid"], gf["kind"], gf["resto"]) for h in self.hojas[c]})
            for h in sel["ci_df"]:
                self.hojas[h] = [h]
            if self.catalogo["regla"] == "hojas_completas":
                for h in sorted(x for x in self.reg if campos(x)["fam"] == "ci" and campos(x)["dis"] == d):
                    disp = self._hoja_disponible(h)
                    self.hojas_censo[h] = disp
                    if disp:
                        hojas_all.add(h)
            st = V3.preparar(self.ctx, d, sorted(hojas_all | set(sel["country"]) | set(gl)))
            for c, cx in st["univ"].items():
                self.univ[c] = cx
        self.ctx_keys = {h: [self.ctx_key(c) for c in cx] for h, cx in self.univ.items()}
        self._canon = {}
        for e, (c, s, d) in self.esperadas.items():
            self._canon[e] = json.dumps(self.fila(c, s, d), ensure_ascii=False)
        self.orden = [e for e, _ in sorted(self.esperadas.items(), key=lambda kv: (kv[1][2], kv[1][0], kv[1][1]))]
        self.esquema_doc = esquema_doc(self.seleccion_id, max(64, len(self.esperadas)))
        self.segundos = round(time.time() - t0, 1)

    def seleccion_de(self, d):
        """{ci_df, country, g} del catálogo para el diseño d (lógica de codigo/global_extreme_v4.Referencia.seleccion_de)."""
        if self.catalogo["regla"] == "propagacion":
            return self.prop[d]["seleccion"]
        ci_df = sorted(h for h in self.fuente_df if campos(h)["dis"] == d)
        country = []
        for h in ci_df:
            f = campos(h)
            c = ":".join(["CLM", f["pid"], f["kind"], "c", f["pais"], "conditional_full", f["dis"]] + list(f["resto"]))
            if c not in self.reg:
                self.excluidas.append((c, "no está en el registro v4"))
                continue
            faltan = [x for x in (ci_de(c, "d"), ci_de(c, "df"), ci_de(c, "f")) if not self._hoja_disponible(x)]
            if faltan:
                self.excluidas.append((c, "hojas sin fuente autenticada: %s" % faltan))
                continue
            if c not in country:
                country.append(c)
        gs = []
        for c in country:
            f = campos(c)
            g = ":".join(["CLM", f["pid"], f["kind"], "g", f["scen"], f["dis"]] + list(f["resto"]))
            if g in gs or g not in self.reg:
                continue
            todas = [x for x in self.reg if campos(x)["fam"] == "c" and (lambda q: (q["pid"], q["kind"], q.get("scen"), q["dis"], q["resto"]))(campos(x)) ==
                     (f["pid"], f["kind"], f["scen"], f["dis"], f["resto"])]
            if all(x in country for x in todas):
                gs.append(g)
            else:
                self.excluidas.append((g, "country del registro sin todas sus hojas: %s" % sorted(set(todas) - set(country))[:3]))
        return {"ci_df": ci_df, "country": country, "g": gs}

    def _hoja_disponible(self, h):
        j = campos(h)["j"]
        if j == "df":
            return h in self.fuente_df
        if j == "d":
            return h in self.xdd["afirmaciones"] and h in self.prod[campos(h)["dis"]]["afirmaciones"]
        return h in self.can["afirmaciones"]

    def hoja(self, h, sentido):
        """Como la v3, con la fuente ci-df del CATÁLOGO (la v3 solo conoce la propagación): misma lógica y mismas citas."""
        f = campos(h)
        if f["j"] != "df":
            return super().hoja(h, sentido)
        if h not in self.fuente_df:
            raise Rechazo("E_FUENTE", "ci-df sin resultado en las fuentes del catálogo: %s" % h)
        d = f["dis"]
        previo = (self.arch[("prop", d)], self.prop[d])
        self.arch[("prop", d)] = self.fuente_df[h]
        self.prop[d] = self.leer(*self.fuente_df[h])
        try:
            return super().hoja(h, sentido)
        finally:
            self.arch[("prop", d)], self.prop[d] = previo

    def tabla(self):
        t = super().tabla()
        t["alcance"]["seleccion"], t["alcance"]["disenos"] = self.seleccion_id, list(self.disenos)
        return t
