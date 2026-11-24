"""rem137 — C2 v3: añade el tipo exclusion_cota_U (nota del revisor rem137 cf738de6…: v > U + banda ⇒ outside_support; la igualdad no
excluye y la cota nunca prueba pertenencia). Fuentes v3 (77d9a10b…) = v2 sin cambios + nota U, dictamen, cota U, modelo, pruebas aceptadas y
derivado C3. Premisas U comprobadas en el contexto sobre los MISMOS bytes de D7 (texto y binary64; gamma = z_m = 1; raíces y U con enteros
exactos). Los tres tipos existentes, su regla y la función común `validar` no cambian (derivado de rem136 7f15b5b6… con sustituciones contadas).
rem136 — C2 v2: certificación POR FILA de captura de T8 con FUENTES FIJADAS (P4-T8-CAPTURA-FUENTES-PROCEDENCIA; derivado de rem135 9a3c2cf9…;
candidato aislado: no finaliza estados reales, no es un soporte global ni lo sustituye, no activa F-T8-SOPORTE).
Cambios frente a rem135, solo de fuentes y procedencia (la regla matemática y la función común `validar` no cambian):
  - TODA autoridad sale de FUENTES_CAPTURA.json, junto a este módulo, fijada por FUENTES_SHA256: equivalencia, anexo, mapa, inventarios de las 14
    entregas testigo, CSV de D7 (autoridad: línea base aceptada del original de rem104), nota, plan, garantía y banda. El llamador no elige
    ninguna (Contexto(R) no admite rutas ni hashes) y ningún hash de una prueba se usa como autoridad: solo se coteja con ella.
  - Cada fuente se lee UNA vez; esos mismos bytes se autentican (inventario fijado → archivo listado) y se parsean (CSV de D7 incluidos).
  - Campos de procedencia publicados en las pruebas: se cotejan contra la fuente o se derivan de ella (país, dominio, frontera, garantía, estado,
    conjunto, inventario, grupo/equivalencia; nota/premisas/plan en exclusiones); esquema cerrado: un campo no declarado se rechaza.
Tipos (aritmética exacta con fracciones; error en escala C_2):
  pertenencia_misma_corrida / pertenencia_transferida: C2_inf+err_inf <= v <= C2_sup-err_sup  ⇒ computed;
  exclusion_cota_33_10: nota fijada + premisas D7 auténticas ⇒ C2 <= 33/10 en el plan; v > 33/10 + banda ⇒ outside_support;
  sin prueba suficiente: pendiente."""
import csv
import hashlib
import io
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
AQUI = Path(__file__).resolve().parent
FUENTES = AQUI / "FUENTES_CAPTURA.json"
FUENTES_SHA256 = "77d9a10b409416a0f148ff665584c20e4a8f8d997862e4b79cc7f8b5f1c506e1"
NOTA_SHA256 = "7a9769896d533cb793254e09ef5a36f0205b02d2ad92a4c1c01bbee932f6fada"
COTA = Fraction(33, 10)
# rem137 — cota U (nota rem137): primero eta_d = 1/10 y solo después el máximo en tau_d; K = binary64(0.2); raíces racionales por exceso
NOTA_U_SHA256 = "cf738de6945a86ffb55ed0994610bc6d8d9d21860a5cd0b7e92a27f0afe0f34a"
DICTAMEN_U_SHA256 = "008e15b95c7a2f4ba8b140bd69fd0b80e521390b7f5dc2925ed03d08f67fb62d"
MODELO_SHA256 = "24af1c4222a25a6e569cb42311406ffeb6d5df0603d3abe15eb34e10bcbaf4d9"
K = Fraction(3602879701896397, 18014398509481984)
QD, QF = Fraction(73, 80), Fraction(5703, 2500)
U = Fraction(184927708619012784273, 225179981368524800000)
REGLA_U = "Fraction(v) > U + banda  =>  outside_support (la igualdad no excluye; nunca prueba pertenencia)"
MAGNITUD_U = {"k": "C2", "escala": "C_2_share", "normalizacion": "gamma = z_m = 1 en los diez conjuntos base"}
PLAN = "6cec0a6d662104dab6a490cea647cd24ae995819a416eaf3cfd4fd9f3c060e42"
TIPOS = ("pertenencia_misma_corrida", "pertenencia_transferida", "exclusion_cota_33_10", "exclusion_cota_U")
ESCALA = "C_2_share"
STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
BASE = ("tipo", "fila", "run_destino", "cell_id", "ref_fila", "fila_en_unidad", "valor_requerido", "escala")
ESQUEMA = {"pertenencia_misma_corrida": frozenset(BASE + ("equivalencia_sha256", "grupo_equivalencia", "testigo_inferior", "testigo_superior")),
           "pertenencia_transferida": frozenset(BASE + ("equivalencia_sha256", "grupo_equivalencia", "testigo_inferior", "testigo_superior")),
           "exclusion_cota_33_10": frozenset(BASE + ("cota", "banda", "nota_sha256", "premisas_sha256", "plan_sha256")),
           "exclusion_cota_U": frozenset(BASE + ("cota", "banda", "regla", "magnitud", "nota_sha256", "premisas_sha256", "plan_sha256",
                                                 "fuentes_sha256"))}
CAMPOS_TESTIGO = frozenset(("ref", "ref_sha256", "inventario", "inventario_sha256", "run_origen", "ceiling_id", "frontier_id", "structural_key_sha256",
                            "conjunto", "indices_L0", "diseno", "instrumento", "pais", "caso", "dominio_tau", "C_2", "numerical_error", "escala", "garantia",
                            "computation_status", "sup_not_attained"))


class Rechazo(Exception):
    pass


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _dec(x):
    return Decimal(repr(x)) if isinstance(x, float) else Decimal(str(x))


def _csv(b):
    return list(csv.DictReader(io.StringIO(b.decode("utf-8"), newline="")))


def premisas_d7(d7b):
    """Premisas de aplicación de la nota sobre los BYTES autenticados de D7 (conjuntos base por support_sets.csv.kind); misma regla que rem135."""
    base = sorted(r["support_set_id"] for r in _csv(d7b["support_sets.csv"]) if r["kind"] == "base")
    filas = {}
    for r in _csv(d7b["support_set.csv"]):
        if r["support_set_id"] in base:
            filas.setdefault((r["support_set_id"], r["parameter_id"]), []).append(r)
    menus = sorted({r["instrument_j"] for r in _csv(d7b["tau_domains.csv"]) if r["support_set_id"] in base})

    def vals(s, p):
        out = []
        for r in filas.get((s, p), []):
            out += [Fraction(r["lower"]), Fraction(r["upper"])] + [Fraction(str(x)) for x in json.loads(r["level0_nodes"])]
        return out

    def flt(s, p, f):
        return f(Fraction(float(r["upper"])) for r in filas[(s, p)])

    chk, cota_flotante = {}, {}
    for s in base:
        c = {"bar_tau_d=3/5": set(vals(s, "bar_tau_d")) == {Fraction(3, 5)}, "bar_tau_f=3/5": set(vals(s, "bar_tau_f")) == {Fraction(3, 5)},
             "0<=beta_tilde<=4": min(vals(s, "beta_tilde")) >= 0 and max(vals(s, "beta_tilde")) <= 4,
             "0<kappa_tilde<=1/5": min(vals(s, "kappa_tilde")) > 0 and max(vals(s, "kappa_tilde")) <= Fraction(1, 5),
             "0<=phi<=1": min(vals(s, "phi")) >= 0 and max(vals(s, "phi")) <= 1, "a>1": min(vals(s, "a")) > 1,
             "0<=rho<=1": min(vals(s, "rho")) >= 0 and max(vals(s, "rho")) <= 1, "eta_d>=0": min(vals(s, "eta_d")) >= 0,
             "eta_f>0": min(vals(s, "eta_f")) > 0}
        chk[s] = c
        bd, bf = flt(s, "bar_tau_d", max), flt(s, "bar_tau_f", max)
        b, k = flt(s, "beta_tilde", max), flt(s, "kappa_tilde", max)
        cota_flotante[s] = bd * (1 + b) + bf * k / (1 - bf)
    ok = len(base) == 10 and all(all(c.values()) for c in chk.values()) and menus == ["d", "df", "f"] \
        and all(x <= COTA for x in cota_flotante.values())
    return ok, {"conjuntos_base": base, "menus": menus, "por_conjunto": chk, "cota_con_binary64": {s: str(x) for s, x in cota_flotante.items()},
                "cota_con_binary64_max_float": float(max(cota_flotante.values()))}


def premisas_U(d7b):
    """rem137 — premisas de la nota U sobre los BYTES autenticados de D7: diez conjuntos base (support_sets.csv.kind), menús d/df/f; en cada
    conjunto, todo valor declarado (lower, upper, nodos L0) en su texto Y en el binary64 que recibe el modelo cumple a>1, 0<=rho<=1,
    beta_tilde>=0, eta_d>=1/10, eta_f>=1/10, 0<=phi<=1, 0<kappa_tilde<=K, 0<=bar_tau_d<=3/5, 0<=bar_tau_f<=3/5 y gamma = z_m = 1 exactamente.
    Raíces: (73/80)^10 >= 2/5 y (5703/2500)^10 >= (5/2)^9, mínimas entre los múltiplos de 1/10000; U = (3/5)QD + K(3/5)QF; K = binary64(0.2)."""
    base = sorted(r["support_set_id"] for r in _csv(d7b["support_sets.csv"]) if r["kind"] == "base")
    filas = {}
    for r in _csv(d7b["support_set.csv"]):
        if r["support_set_id"] in base:
            filas.setdefault((r["support_set_id"], r["parameter_id"]), []).append(r)
    menus = sorted({r["instrument_j"] for r in _csv(d7b["tau_domains.csv"]) if r["support_set_id"] in base})

    def ext(s, p):
        out = []
        for r in filas.get((s, p), []):
            for x in [r["lower"], r["upper"]] + [str(v) for v in json.loads(r["level0_nodes"])]:
                out += [Fraction(x), Fraction(float(x))]
        return out

    chk = {}
    for s in base:
        e = {p: ext(s, p) for p in ("a", "rho", "beta_tilde", "eta_d", "eta_f", "phi", "kappa_tilde", "bar_tau_d", "bar_tau_f", "gamma", "z_m")}
        if not all(e.values()):
            chk[s] = {"parametros_presentes": False}
            continue
        chk[s] = {"a>1": min(e["a"]) > 1, "0<=rho<=1": min(e["rho"]) >= 0 and max(e["rho"]) <= 1, "beta_tilde>=0": min(e["beta_tilde"]) >= 0,
                  "eta_d>=1/10": min(e["eta_d"]) >= Fraction(1, 10), "eta_f>=1/10": min(e["eta_f"]) >= Fraction(1, 10),
                  "0<=phi<=1": min(e["phi"]) >= 0 and max(e["phi"]) <= 1, "0<kappa_tilde<=K": min(e["kappa_tilde"]) > 0 and max(e["kappa_tilde"]) <= K,
                  "0<=bar_tau_d<=3/5": min(e["bar_tau_d"]) >= 0 and max(e["bar_tau_d"]) <= Fraction(3, 5),
                  "0<=bar_tau_f<=3/5": min(e["bar_tau_f"]) >= 0 and max(e["bar_tau_f"]) <= Fraction(3, 5),
                  "gamma=1": set(e["gamma"]) == {1}, "z_m=1": set(e["z_m"]) == {1}}
    m = Fraction(1, 10000)
    raices = {"QD^10>=2/5": QD ** 10 >= Fraction(2, 5), "QD_minima": (QD - m) ** 10 < Fraction(2, 5),
              "QF^10>=(5/2)^9": QF ** 10 >= Fraction(5, 2) ** 9, "QF_minima": (QF - m) ** 10 < Fraction(5, 2) ** 9,
              "K=binary64(0.2)": K == Fraction(0.2), "U=(3/5)QD+K(3/5)QF": U == Fraction(3, 5) * QD + K * Fraction(3, 5) * QF}
    ok = len(base) == 10 and menus == ["d", "df", "f"] and all(all(c.values()) for c in chk.values()) and all(raices.values())
    return ok, {"conjuntos_base": base, "menus": menus, "por_conjunto": chk, "raices": raices, "U": str(U), "K": str(K), "QD": str(QD), "QF": str(QF)}


class Contexto:
    """Fuentes autenticadas que consumen las pruebas. Toda autoridad procede de FUENTES_CAPTURA.json (FUENTES_SHA256); sin parámetros de autoridad."""

    def __init__(self, R):
        self.R, self.T = Path(R), Path(R) / "tmp"
        fb = FUENTES.read_bytes()
        if H(fb) != FUENTES_SHA256:
            raise Rechazo("FUENTES_NO_AUTENTICAS")
        self.fuentes = F = json.loads(fb)
        self.inv = {}
        self.eq_sha = F["equivalencia"]["sha256"]
        self.eq = json.loads(self._fuente(F["equivalencia"]))
        if self.eq.get("plan_sha256") != PLAN or F["plan_sha256"] != PLAN or str(self.eq["banda_tol_converge"]) != str(F["banda_tol_converge"]) \
                or self.eq["garantia_plataforma"] != F["garantia_plataforma"]:
            raise Rechazo("EQUIVALENCIA_INCOHERENTE_CON_LAS_FUENTES")
        if {c["inventario"]: c["inventario_sha256"] for c in self.eq["nucleo_por_corrida"].values()} != \
                {x["ruta"]: x["sha256"] for x in F["inventarios_testigo"].values()}:
            raise Rechazo("INVENTARIOS_TESTIGO_INCOHERENTES_CON_LA_EQUIVALENCIA")
        self.grupo = {r: g for g, rs in self.eq["grupos"].items() for r in rs} if self.eq.get("equivalentes") else {}
        self.banda = Fraction(self.eq["banda_tol_converge"])
        self.garantia = "certified_bound (ModeloTeorico, plataforma %s)" % self.eq["garantia_plataforma"]
        self.nota_ok = F["nota"]["sha256"] == NOTA_SHA256 and H(Path(F["nota"]["ruta"]).read_bytes()) == NOTA_SHA256
        lb = json.loads(self._fuente(F["d7"]["autoridad"]))["files"]
        self.d7b = {}
        for n, x in F["d7"]["archivos"].items():
            b = (self.R / x["ruta"]).read_bytes()
            if H(b) != x["sha256"] or lb.get(x["ruta"], {}).get("sha256") != x["sha256"]:
                raise Rechazo("FUENTE_NO_AUTENTICA:" + n)
            self.d7b[n] = b
        self.premisas_ok, self.premisas = premisas_d7(self.d7b)
        self.premisas_sha256 = H(canon(self.premisas))
        # rem137 — cota U: nota, dictamen y modelo leídos y autenticados; la cota de las fuentes debe ser EXACTAMENTE la de este módulo
        cu = F.get("cota_U") or {}
        try:
            self.nota_U_ok = (F["nota_U"]["sha256"] == NOTA_U_SHA256 and H(Path(F["nota_U"]["ruta"]).read_bytes()) == NOTA_U_SHA256
                              and F["dictamen_rem137"]["sha256"] == DICTAMEN_U_SHA256
                              and H(Path(F["dictamen_rem137"]["ruta"]).read_bytes()) == DICTAMEN_U_SHA256
                              and F["modelo"]["sha256"] == MODELO_SHA256 and H((self.R / F["modelo"]["ruta"]).read_bytes()) == MODELO_SHA256
                              and cu.get("U") == str(U) and cu.get("banda") == str(self.banda) and cu.get("K_binary64_0.2") == str(K)
                              and cu.get("QD_(2/5)^(1/10)") == str(QD) and cu.get("QF_(5/2)^(9/10)") == str(QF) and cu.get("regla") == REGLA_U
                              and cu.get("magnitud") == MAGNITUD_U)
        except (KeyError, OSError, TypeError):
            self.nota_U_ok = False
        self.premisas_U_ok, self.premisas_U = premisas_U(self.d7b)
        self.premisas_U_sha256 = H(canon(self.premisas_U))
        self.anexo = json.loads(self._fuente(F["anexo_t8"]))["filas"]
        mp = json.loads(self._fuente(F["mapa_corridas"]))
        self.run_de = {e: r for r, v in mp.items() for e in v["entregas"]}
        if set(self.run_de) != set(F["inventarios_testigo"]) or any(self.run_de[e] != x["run"] for e, x in F["inventarios_testigo"].items()):
            raise Rechazo("MAPA_INCOHERENTE_CON_LAS_FUENTES")
        self.captura = {i: f for i, f in enumerate(self.anexo) if f["estado_es_por_unidad"] and f["inversion_id"] == "capture_required"}
        self.conjunto_de = {}
        for f in self.anexo:
            self.conjunto_de.setdefault(f["ref"], set()).add(f["conjunto"])
        self.plan = {r: c["plan_sha256"] for r, c in self.eq["configuracion_y_metodo"].items()}
        self.nodos = {}
        for r in _csv(self.d7b["support_set.csv"]):
            if r["parameter_id"] in STRUCT and r["support_set_id"] in self.premisas["conjuntos_base"]:
                self.nodos[(r["support_set_id"], r["parameter_id"])] = [_dec(x) for x in json.loads(r["level0_nodes"])]
        self._unid = {}

    def _inventario(self, area, sha_fijado):
        if area not in self.inv:
            b = (self.T / area / "audit/entrega.json").read_bytes()
            if H(b) != sha_fijado:
                raise Rechazo("INVENTARIO_NO_AUTENTICO:" + area)
            self.inv[area] = json.loads(b)["files"]
        return self.inv[area]

    def _fuente(self, x):
        f = self._inventario(x["area"], x["inventario"]["sha256"])
        b = (self.T / x["area"] / x["rel"]).read_bytes()
        if H(b) != x["sha256"] or f.get(x["rel"], {}).get("sha256") != x["sha256"]:
            raise Rechazo("FUENTE_NO_AUTENTICA:" + x["rel"])
        return b

    def unidad(self, ref):
        """Unidad testigo: su entrega debe tener inventario de autoridad en las fuentes; inventario y unidad se autentican contra él."""
        if ref not in self._unid:
            area, rel = ref.split("/", 1)
            a = self.fuentes["inventarios_testigo"].get(area)
            if a is None:
                raise Rechazo("ENTREGA_SIN_AUTORIDAD:" + area)
            f = self._inventario(area, a["sha256"])
            b = (self.T / area / rel).read_bytes()
            if f.get(rel, {}).get("sha256") != H(b):
                raise Rechazo("UNIDAD_NO_AUTENTICA:" + ref)
            self._unid[ref] = (H(b), a, json.loads(b), self.run_de.get(area))
        return self._unid[ref]


def _testigo(ctx, w):
    if not isinstance(w, dict) or set(w) != CAMPOS_TESTIGO:
        return "TESTIGO_FUERA_DE_ESQUEMA"
    try:
        h, a, d, run = ctx.unidad(w["ref"])
    except (Rechazo, KeyError, OSError, ValueError, AttributeError):
        return "TESTIGO_NO_AUTENTICO"
    # lo que publica la prueba se COTEJA con la autoridad; nunca la sustituye
    if h != w["ref_sha256"] or a["sha256"] != w["inventario_sha256"] or w["inventario"] != a["ruta"]:
        return "TESTIGO_NO_AUTENTICO"
    if run != w["run_origen"] or ctx.plan.get(run) != PLAN:
        return "TESTIGO_RUN_ORIGEN"
    ts = [t for t in d.get("capture_ceiling_result", []) if t.get("ceiling_id") == w["ceiling_id"]]
    if len(ts) != 1:
        return "TESTIGO_AJENO"
    t = ts[0]
    if t.get("computation_status") != "complete" or t.get("sup_not_attained") is not False:
        return "TESTIGO_NO_COMPLETO"
    if w["computation_status"] != t["computation_status"]:
        return "TESTIGO_PROCEDENCIA_DISTINTA:computation_status"
    if w["sup_not_attained"] is not t["sup_not_attained"]:
        return "TESTIGO_PROCEDENCIA_DISTINTA:sup_not_attained"
    if t.get("C_2") != w["C_2"] or t.get("numerical_error") != w["numerical_error"] or w["escala"] != ESCALA:
        return "TESTIGO_ALTERADO_O_ESCALA"
    if not isinstance(t["numerical_error"], float) or not t["numerical_error"] >= 0 or not isinstance(t["C_2"], float):
        return "TESTIGO_SIN_ERROR_VALIDO"
    frs = [x for x in d.get("frontier_context", []) if x.get("frontier_id") == "FRN:" + w["ceiling_id"][4:]]
    if len(frs) != 1 or frs[0].get("structural_key_sha256") != w["structural_key_sha256"] or frs[0].get("design_v") != w["diseno"] \
            or frs[0].get("instrument_j") != w["instrumento"] or frs[0].get("availability_case_id") != w["caso"]:
        return "TESTIGO_FRONTERA_DISTINTA"
    fx = frs[0]
    for campo, fuente in (("frontier_id", fx.get("frontier_id")), ("pais", fx.get("country_id")), ("dominio_tau", fx.get("tau_domain_id")),
                          ("garantia", ctx.garantia), ("conjunto", next(iter(ctx.conjunto_de.get(w["ref"], {None})), None))):
        if w[campo] != fuente or (campo == "conjunto" and len(ctx.conjunto_de.get(w["ref"], ())) != 1):
            return "TESTIGO_PROCEDENCIA_DISTINTA:" + campo
    vals = {x["parameter_id"]: x["value"] for x in fx["structural_key_payload"].get("values", [])}
    if w["conjunto"] not in ctx.premisas["conjuntos_base"] or not isinstance(w["indices_L0"], dict):
        return "TESTIGO_FUERA_DEL_PLAN"
    for p in STRUCT:
        ns = ctx.nodos.get((w["conjunto"], p), [])
        v = _dec(vals[p]) if vals.get(p) is not None else None
        if v is None or v not in ns or ns.index(v) != w["indices_L0"].get(p):
            return "TESTIGO_FUERA_DEL_PLAN"
    return None


def validar(ctx, prueba):
    """ÚNICA validación de una prueba por fila (tres tipos). Devuelve (True, estado_candidato) o (False, motivo)."""
    tipo = prueba.get("tipo") if isinstance(prueba, dict) else None
    if tipo not in TIPOS:
        return False, "TIPO_DESCONOCIDO"
    if set(prueba) != ESQUEMA[tipo]:
        return False, "PRUEBA_FUERA_DE_ESQUEMA"
    i = prueba["fila"]
    f = ctx.captura.get(i) if isinstance(i, int) and not isinstance(i, bool) else None
    if f is None:
        return False, "FILA_NO_ES_CAPTURA_PROVISIONAL"
    dest = ctx.run_de.get(f["ref"].split("/", 1)[0])
    if prueba["run_destino"] != dest or prueba["cell_id"] != f["cell_id"] or prueba["ref_fila"] != f["ref"] or prueba["fila_en_unidad"] != f["fila_en_unidad"]:
        return False, "FILA_NO_COINCIDE"
    v = f["fin_por_unidad"]["value"]
    if prueba["valor_requerido"] != v or not isinstance(v, float) or prueba["escala"] != ESCALA or not f["fin_por_unidad"].get("c2_defined"):
        return False, "VALOR_O_ESCALA_NO_COINCIDE"
    if ctx.plan.get(dest) != PLAN:
        return False, "PLAN_DISTINTO"
    V = Fraction(v)
    if tipo == "exclusion_cota_33_10":
        if not (ctx.nota_ok and ctx.premisas_ok):
            return False, "COTA_NO_APLICABLE"
        for campo, autoridad in (("nota_sha256", NOTA_SHA256), ("premisas_sha256", ctx.premisas_sha256), ("plan_sha256", PLAN)):
            if prueba[campo] != autoridad:
                return False, "EXCLUSION_REFERENCIA_DISTINTA:" + campo
        if prueba["cota"] != "33/10" or not isinstance(prueba["banda"], str) or Fraction(prueba["banda"]) != ctx.banda:
            return False, "COTA_O_BANDA_DISTINTA"
        if not V > COTA + ctx.banda:
            return False, "V_NO_SUPERA_COTA_MAS_BANDA"
        return True, "outside_support"
    if tipo == "exclusion_cota_U":
        # rem137 — magnitud y unidades de la fila: C2 en share (la cota U es del share normalizado con gamma = z_m = 1)
        if f["fin_por_unidad"].get("k") != MAGNITUD_U["k"] or f.get("target_unit") != "share":
            return False, "UNIDAD_O_MAGNITUD_NO_ES_C2_SHARE"
        if not (ctx.nota_U_ok and ctx.premisas_U_ok):
            return False, "COTA_U_NO_APLICABLE"
        for campo, autoridad in (("nota_sha256", NOTA_U_SHA256), ("premisas_sha256", ctx.premisas_U_sha256), ("plan_sha256", PLAN),
                                 ("fuentes_sha256", FUENTES_SHA256)):
            if prueba[campo] != autoridad:
                return False, "EXCLUSION_U_REFERENCIA_DISTINTA:" + campo
        try:
            banda_ok = isinstance(prueba["banda"], str) and Fraction(prueba["banda"]) == ctx.banda
        except (ValueError, ZeroDivisionError):
            banda_ok = False
        if prueba["cota"] != str(U) or not banda_ok or prueba["regla"] != REGLA_U or prueba["magnitud"] != MAGNITUD_U:
            return False, "COTA_U_BANDA_REGLA_O_MAGNITUD_DISTINTA"
        if not V > U + ctx.banda:
            return False, "V_NO_SUPERA_U_MAS_BANDA"
        return True, "outside_support"
    # esquema declarado: la misma corrida no usa equivalencia (null); la transferida cita el documento de autoridad
    if prueba["equivalencia_sha256"] != (ctx.eq_sha if tipo == "pertenencia_transferida" else None):
        return False, "PRUEBA_PROCEDENCIA_DISTINTA:equivalencia_sha256"
    if prueba["grupo_equivalencia"] != ctx.grupo.get(dest):
        return False, "PRUEBA_PROCEDENCIA_DISTINTA:grupo_equivalencia"
    wi, ws = prueba["testigo_inferior"], prueba["testigo_superior"]
    for w in (wi, ws):
        m = _testigo(ctx, w)
        if m:
            return False, m
    origen = {wi["run_origen"], ws["run_origen"]}
    if tipo == "pertenencia_misma_corrida" and origen != {dest}:
        return False, "TESTIGO_DE_OTRA_CORRIDA"
    if tipo == "pertenencia_transferida":
        if not ctx.grupo or any(ctx.grupo.get(r) != ctx.grupo.get(dest) or r is None for r in origen):
            return False, "CORRIDA_DESTINO_NO_EQUIVALENTE"
        if dest in origen:
            return False, "TRANSFERENCIA_CON_TESTIGO_PROPIO"
    if not (Fraction(wi["C_2"]) + Fraction(wi["numerical_error"]) <= V <= Fraction(ws["C_2"]) - Fraction(ws["numerical_error"])):
        return False, "DESIGUALDAD_NO_CUBRE_V"
    return True, "computed"


def clave(f):
    return H(canon({"ref": f["ref"], "fila_en_unidad": f["fila_en_unidad"], "inversion_id": f["inversion_id"], "cell_id": f["cell_id"]}))


def construir(ctx, pruebas):
    """Candidato fila a fila para las filas de captura provisionales. Una prueba por fila como máximo; las filas sin prueba válida quedan
    pendientes con su causa. No escribe nada ni toca estados reales."""
    por = {}
    for p in pruebas:
        k = p.get("fila") if isinstance(p, dict) else None
        if k in por:
            raise Rechazo("PRUEBA_DUPLICADA:%s" % k)
        por[k] = p
    ajenas = sorted(str(k) for k in por if k not in ctx.captura)
    if ajenas:
        raise Rechazo("PRUEBA_DE_FILA_AJENA:%s" % ajenas[:3])
    filas = []
    for i, f in sorted(ctx.captura.items()):
        p = por.get(i)
        x = {"fila": i, "clave_fila": clave(f), "run_id": ctx.run_de[f["ref"].split("/", 1)[0]], "cell_id": f["cell_id"],
             "estado_historico": f["result_status"], "valor_requerido": f["fin_por_unidad"]["value"]}
        if p is None:
            x.update(estado_candidato="pendiente", causa_pendiente="SIN_PRUEBA_POR_FILA", tipo_prueba=None, prueba_sha256=None)
        else:
            ok, r = validar(ctx, p)
            x.update(estado_candidato=r if ok else "pendiente", causa_pendiente=None if ok else "PRUEBA_RECHAZADA:" + r,
                     tipo_prueba=p["tipo"], prueba_sha256=H(canon(p)))
        filas.append(x)
    return filas


def resumen(filas):
    from collections import Counter
    return {"filas": len(filas), "por_estado": dict(sorted(Counter(x["estado_candidato"] for x in filas).items())),
            "por_tipo": dict(sorted(Counter(x["tipo_prueba"] for x in filas if x["estado_candidato"] != "pendiente").items())),
            "pendientes_por_causa": dict(sorted(Counter(x["causa_pendiente"] for x in filas if x["causa_pendiente"]).items())),
            "cambios_frente_al_historico": sum(1 for x in filas if x["estado_candidato"] not in ("pendiente", x["estado_historico"]))}


def verificar(ctx, pruebas_raw, cand_raw):
    """Recalcula el candidato desde los MISMOS bytes de pruebas y lo coteja con el candidato escrito: universo, claves, duplicados,
    faltantes, estados y promoción indebida."""
    fallos = []
    try:
        esperado = construir(ctx, json.loads(pruebas_raw))
    except (Rechazo, ValueError, AttributeError) as ex:
        return False, [str(ex) or type(ex).__name__]
    try:
        filas = [json.loads(x) for x in cand_raw.decode("utf-8").splitlines() if x.strip()]
    except ValueError:
        return False, ["CANDIDATO_ILEGIBLE"]
    if len(filas) != len(ctx.captura):
        fallos.append("UNIVERSO_DISTINTO:%d!=%d" % (len(filas), len(ctx.captura)))
    claves = [x.get("clave_fila") for x in filas]
    if len(set(claves)) != len(claves):
        fallos.append("CLAVES_DUPLICADAS")
    esp = {x["clave_fila"]: x for x in esperado}
    if set(claves) != set(esp):
        fallos.append("CLAVES_FALTANTES_O_AJENAS")
    dist = [x.get("fila") for x in filas if esp.get(x.get("clave_fila")) != x]
    if dist:
        fallos.append("FILAS_DISTINTAS_DEL_RECALCULO:%d" % len(dist))
    promo = [x.get("fila") for x in filas if x.get("estado_candidato") != "pendiente" and esp.get(x.get("clave_fila"), {}).get("estado_candidato") == "pendiente"]
    if promo:
        fallos.append("PROMOCION_INDEBIDA:%d" % len(promo))
    return not fallos, fallos
