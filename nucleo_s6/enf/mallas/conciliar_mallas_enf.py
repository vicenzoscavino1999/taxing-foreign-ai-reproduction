"""rem126 — CONCILIACIÓN DEL CONTRASTE ABL-ENF COMPLETO: mallas emparejadas padre/ENF, techos y brechas (solo lectura de productos; ninguna
evaluación científica nueva).
1. Mallas: el producto del lanzamiento de mallas (paquete rem119 aceptado, tarea L1-ELAST, manifiesto MANIFIESTO_MALLAS_ENF.json) se lee una vez,
   se autentica por el sha256 que registra su resultado y se valida con el VALIDADOR ELAST ACEPTADO (rem119 validar_lote.py, el mismo de la
   tarea) en subproceso; después se comprueba que los bytes no cambiaron y se usan ESOS bytes.
2. Mallas padre reutilizadas: se leen de su producto aceptado (sha256 del manifiesto), con identidad completa recalculada desde su manifiesto
   aceptado y origen C0 comprobado (una malla del lote 1 o con suplemento histórico declarada como C0 es mezcla de núcleos no declarada).
3. Pares: identidad ENF = padre con eta_f/2 exacto y phi y resto intactos, mismo diseño/menú/dominio; puntos de la regla de malla en ambos
   lados; comparación por coordenadas (τ_d, τ_f) de R, CS = R/B_pot, B_d, B_f, régimen, topología y kink; laterales solo si existen en ambos
   lados en el mismo punto y lado (si no, se declaran no comparables); sin interpolar ni rellenar. Control del menú d: |ΔR| y |ΔCS| dentro de
   T1 = 1e-12 del contrato (R(τ_d, 0) no depende de eta_f).
4. Techos (si se pasan con --techos): cada tarea de lote_enf se acepta con validar_coord_rec.validar_tarea del paquete ENF y el ensamblado con
   validar_ensamblado, sobre los mismos bytes; por par se informa ΔC2 = C2' − C2 padre y por celda G' − G padre con K1 fijo.
Escribe en exclusiva <salida_nueva>/ (CONCILIACION_MALLAS_ENF.json y pares_puntos.jsonl) y en la última línea {aceptada, dictamen, fallos}.
Uso: python -B -X utf8 conciliar_mallas_enf.py <raiz> <manifiesto_mallas> <anexo_mallas> <salida_nueva> <lanzamiento_mallas>
                                              [--techos <manifiesto_techos> <lanzamiento_techos> [<otro> ...]]"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

a = sys.argv[1:]
R, MAN, COB, SAL, LM = (Path(x) for x in a[:5])
TEC = a[a.index("--techos") + 1:] if "--techos" in a else []
T = R / "tmp"
L119 = T / "paso4_suplemento_topologia_desde_rem119/lote2"
LENF = T / "paso4_enforcement_desde_rem125/lote_enf"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
T1 = 1e-12
fallos = []
falla = fallos.append


def salir(v, rc):
    print(json.dumps(v, ensure_ascii=False))
    raise SystemExit(rc)


def canon(clave, d, j, tau):
    return json.dumps({"clave": clave, "diseno": d, "j": j, "tau": tau}, sort_keys=True)


def leer(ref):
    p = R / ref["ruta"]
    if not p.is_file():
        return None, "FUENTE_AUSENTE:" + ref["ruta"]
    b = p.read_bytes()
    if H(b) != ref["sha256"]:
        return None, "FUENTE_NO_AUTENTICA:" + ref["ruta"]
    t = b.decode("utf-8")
    return (json.loads(t) if ref["ruta"].endswith(".json") else [json.loads(x) for x in t.splitlines() if x.strip()]), None


raw = MAN.read_bytes()
man = json.loads(raw)
mm = man["ABL-ENF-MALLAS"]
an = json.loads(COB.read_bytes())
if an.get("kind") != "cobertura-nacional-lote1" or an.get("manifiesto_sha256") != H(raw):
    falla("ANEXO_DE_OTRO_MANIFIESTO")
SINT = str(man.get("kind", "")).endswith("-SINTETICO")

# ------------------------------------------------ 1. mallas: mismos bytes autenticados y validados por el validador ELAST aceptado
d_m = LM / "L1-ELAST"
rb = (d_m / "resultado.json").read_bytes() if (d_m / "resultado.json").is_file() else b"{}"
res = json.loads(rb)
prod = {p["archivo"]: p["sha256"] for p in res.get("productos") or []}
pb = (d_m / "salida/frontier_result.jsonl").read_bytes() if (d_m / "salida/frontier_result.jsonl").is_file() else b""
if res.get("manifiesto_sha256") != H(raw) or res.get("tarea") != "L1-ELAST" or res.get("estado") != "completa" or prod.get("frontier_result.jsonl") != H(pb):
    falla("PRODUCTO_DE_MALLAS_NO_LIGADO_O_NO_AUTENTICO")
p = subprocess.run([sys.executable, "-B", "-I", "-X", "utf8", str(L119 / "validar_lote.py"), str(R), str(MAN), str(d_m / "resultado.json"), str(d_m / "salida"), str(COB)],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
try:
    val = json.loads(p.stdout.strip().splitlines()[-1])
except (ValueError, IndexError):
    val = {"aceptada": False, "fallos": ["SALIDA_DEL_VALIDADOR_ILEGIBLE"]}
if p.returncode != 0 or val.get("aceptada") is not True:
    falla("MALLAS_NO_VALIDADAS_POR_EL_VALIDADOR_ELAST:%s" % val.get("fallos", [])[:3])
if (d_m / "salida/frontier_result.jsonl").read_bytes() != pb or (d_m / "resultado.json").read_bytes() != rb:
    falla("BYTES_DE_MALLAS_CAMBIARON_DURANTE_LA_VALIDACION")
filas_m = [json.loads(x) for x in pb.decode("utf-8").splitlines() if x.strip()]
fr = man["L1-ELAST"]["fronteras"]
ent_por_fid = {v["frontier_id"]: (k.split("|")[0], k.split("|")[1], v) for k, v in fr.items()}

# ------------------------------------------------ 2. fuentes de mallas padre reutilizadas (autenticadas; origen C0)
cache = {}


def fuente(nombre):
    if nombre not in cache:
        cache[nombre] = leer(mm["fuentes"][nombre]) if nombre in mm["fuentes"] else (None, "FUENTE_NO_DECLARADA:" + nombre)
    return cache[nombre]


def padre_reutilizado(par):
    pd = par["padre"]
    filas, err = fuente(pd["producto"])
    if err:
        return None, err
    man_n = {"elast_lote2_rem120": "lote2_manifiesto", "elast_e4_rem121": "e4_manifiesto", "elast_lote1_rem112": "lote1_manifiesto"}.get(pd["producto"])
    mref, err = fuente(man_n) if man_n else (None, "PRODUCTO_SIN_MANIFIESTO_ACEPTADO")
    if err:
        return None, err
    ent = [(k, v) for k, v in mref["L1-ELAST"]["fronteras"].items() if v["frontier_id"] == pd["frontier_id"]]
    if not ent:
        return None, "MALLA_PADRE_AUSENTE_EN_SU_MANIFIESTO:" + pd["frontier_id"]
    k, v = ent[0]
    if H(canon(v["clave_estructural"], k.split("|")[0], k.split("|")[1], v["dominio_tau"]).encode()) != pd["identidad_sha256"]:
        return None, "IDENTIDAD_PADRE_DISTINTA:" + pd["frontier_id"]
    sup, err = fuente("procedencia_suplemento_rem120")
    historica = man_n == "lote1_manifiesto" or v.get("suplemento_topologia") or (sup and pd["frontier_id"] in {x["frontier_id"] for x in sup})
    if historica or not str(pd.get("origen", "")).startswith("C0_"):
        return None, "MEZCLA_DE_NUCLEOS_NO_DECLARADA:" + pd["frontier_id"]
    return [r for r in filas if r.get("frontier_id") == pd["frontier_id"]], None


# ------------------------------------------------ 3. pares
CAMPOS = ("R", "CS", "B_d", "B_f", "B_pot")
pares_ids = [x["par_id"] for x in mm["pares"]]
if len(pares_ids) != len(set(pares_ids)) or len({x["clave_enf"] for x in mm["pares"]}) != len(mm["pares"]):
    falla("PARES_DUPLICADOS")
filas_puntos, resumen = [], []
for par in mm["pares"]:
    e = ent_por_fid.get(par["enf"]["frontier_id"])
    if e is None:
        falla("MALLA_ENF_NO_DECLARADA:" + par["par_id"])
        continue
    d, j, ve = e
    if par["padre"]["modo"] == "evaluar_con_C0":
        pe = ent_por_fid.get(par["padre"]["frontier_id"])
        if pe is None:
            falla("MALLA_PADRE_NO_DECLARADA:" + par["par_id"])
            continue
        clave_p, filas_p = pe[2]["clave_estructural"], [r for r in filas_m if r.get("frontier_id") == par["padre"]["frontier_id"]]
        if (pe[0], pe[1], pe[2]["dominio_tau"]) != (d, j, ve["dominio_tau"]):
            falla("DISENO_MENU_O_DOMINIO_DISTINTOS:" + par["par_id"])
        origen_p = "C0_este_lanzamiento"
    else:
        filas_p, err = padre_reutilizado(par)
        if err:
            falla("%s (%s)" % (err, par["par_id"]))
            continue
        mref = fuente({"elast_lote2_rem120": "lote2_manifiesto", "elast_e4_rem121": "e4_manifiesto"}[par["padre"]["producto"]])[0]
        clave_p = next(v["clave_estructural"] for v in mref["L1-ELAST"]["fronteras"].values() if v["frontier_id"] == par["padre"]["frontier_id"])
        origen_p = par["padre"]["origen"]
    ce = ve["clave_estructural"]
    trans = (set(ce) == set(clave_p) and Decimal(ce["eta_f"]) * 2 == Decimal(clave_p["eta_f"]) and ce["phi"] == clave_p["phi"]
             and all(ce[x] == clave_p[x] for x in ce if x != "eta_f"))
    if not trans:
        falla("TRANSFORMACION_NO_ENF (solo eta_f/2 con phi y resto del padre):" + par["par_id"])
    if H(canon(ce, d, j, ve["dominio_tau"]).encode()) != par["enf"]["identidad_sha256"] or H(canon(clave_p, d, j, ve["dominio_tau"]).encode()) != par["padre"]["identidad_sha256"]:
        falla("IDENTIDAD_DEL_PAR_DISTINTA:" + par["par_id"])
    esperados = {(x["tau_d"], x["tau_f"]): x["point_id"] for x in par["puntos"]}
    fe = [r for r in filas_m if r.get("frontier_id") == par["enf"]["frontier_id"]]
    lado = {}
    for nombre, filas in (("enf", fe), ("padre", filas_p)):
        pts = {}
        for r in filas:
            pts.setdefault((r["tau_d"], r["tau_f"], r["side"]), []).append(r)
        if any(len(v) > 1 for v in pts.values()):
            falla("FILA_DUPLICADA:%s:%s" % (nombre, par["par_id"]))
        if {(k_[0], k_[1]) for k_ in pts if k_[2] == "point"} != set(esperados):
            falla("PUNTOS_DISTINTOS_DE_LA_MALLA:%s:%s" % (nombre, par["par_id"]))
        lado[nombre] = {k_: v[0] for k_, v in pts.items()}
    if any(f.startswith(("PUNTOS_DISTINTOS", "FILA_DUPLICADA")) and f.endswith(par["par_id"]) for f in fallos):
        continue
    comparables, no_comp, max_dr, max_dcs, cambia_top, cambia_reg = 0, [], 0.0, 0.0, 0, 0
    for k_ in sorted(set(lado["enf"]) | set(lado["padre"])):
        a_, b_ = lado["enf"].get(k_), lado["padre"].get(k_)
        if a_ is None or b_ is None:
            no_comp.append({"tau_d": k_[0], "tau_f": k_[1], "side": k_[2], "solo_en": "enf" if b_ is None else "padre"})
            continue
        comparables += 1
        dif = {c: (a_[c] - b_[c]) if isinstance(a_.get(c), (int, float)) and isinstance(b_.get(c), (int, float)) else None for c in CAMPOS}
        max_dr, max_dcs = max(max_dr, abs(dif["R"] or 0.0)), max(max_dcs, abs(dif["CS"] or 0.0))
        cambia_top += a_.get("topology") != b_.get("topology")
        cambia_reg += a_.get("regime") != b_.get("regime")
        filas_puntos.append({"par_id": par["par_id"], "clave_enf": par["clave_enf"], "point_id": esperados.get((k_[0], k_[1])), "tau_d": k_[0], "tau_f": k_[1], "side": k_[2],
                             "enf": {c: a_.get(c) for c in CAMPOS + ("regime", "topology", "kink_adjacent")},
                             "padre": {c: b_.get(c) for c in CAMPOS + ("regime", "topology", "kink_adjacent")}, "dif": dif, "origen_padre": origen_p})
        if par["control_menu_d"] and (abs(dif["R"] or 0.0) > T1 * max(1, abs(b_["R"])) or abs(dif["CS"] or 0.0) > T1 * max(1, abs(b_["CS"]))):
            falla("CONTROL_D_NO_INVARIANTE:%s:%s" % (par["par_id"], k_))
    resumen.append({"par_id": par["par_id"], "clave_enf": par["clave_enf"], "diseno": d, "j": j, "puntos": len(esperados), "filas_comparables": comparables,
                    "no_comparables": no_comp, "max_abs_dR": max_dr, "max_abs_dCS": max_dcs, "puntos_con_cambio_topologia": cambia_top, "puntos_con_cambio_regimen": cambia_reg,
                    "origen_padre": origen_p, "control_menu_d": par["control_menu_d"]})
declaradas = {par["enf"]["frontier_id"] for par in mm["pares"]} | {par["padre"]["frontier_id"] for par in mm["pares"] if par["padre"]["modo"] == "evaluar_con_C0"}
if set(ent_por_fid) != declaradas:
    falla("MALLAS_DEL_MANIFIESTO_SIN_PAR_O_PAR_SIN_MALLA")

# ------------------------------------------------ 4. techos y brechas con la validación común de lote_enf, sobre los mismos bytes
techos_res = None
if TEC:
    sp = importlib.util.spec_from_file_location("validar_coord_rec_enf", LENF / "validar_coord_rec.py")
    VC = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(VC)
    mt = Path(TEC[0])
    raw_t = mt.read_bytes()
    if H(raw_t) != mm["manifiesto_techos"]["sha256"]:
        falla("MANIFIESTO_DE_TECHOS_DISTINTO_DEL_LIGADO")
    co = json.loads(raw_t)["ABL-ENF"]
    techos = []
    for t_, ks in co["tareas"].items():
        dirs = [Path(x) / t_ for x in TEC[1:] if (Path(x) / t_ / "resultado.json").is_file()]
        if len(dirs) != 1:
            falla("TAREA_DE_TECHOS_SIN_SALIDA_UNICA:" + t_)
            continue
        v = VC.validar_tarea(raw_t, dirs[0] / "resultado.json", dirs[0] / "salida")
        if not v["aceptada"] or v["tarea"] != t_:
            falla("TAREA_DE_TECHOS_NO_VALIDA:%s:%s" % (t_, v["fallos"][:2]))
        techos += v["techos"]
    ens, filas_ens = VC.validar_ensamblado(R, co, techos)
    if ens["dictamen"] != "completa_validada":
        falla("ENSAMBLADO_DE_TECHOS_NO_VALIDO:%s" % ens["fallos"][:3])
    if {x["clave_enf"] for x in mm["pares"]} != set(co["claves_recalculadas"]):
        falla("PARES_DISTINTOS_DE_LAS_CLAVES_DE_TECHOS")
    tk = {t["clave_transformada_sha256"]: t for t in techos}
    c2p = {}
    for c in co["celdas_afectadas"]:
        c2p.setdefault(c["clave_transformada_sha256"], set()).add(c["C2_padre"])
    for r_ in resumen:
        t = tk.get(r_["clave_enf"]) or {}
        r_["C2_enf"], r_["C2_padre"] = t.get("C_2"), sorted(c2p.get(r_["clave_enf"], []))
        r_["dC2"] = (t["C_2"] - r_["C2_padre"][0]) if t.get("C_2") is not None and len(r_["C2_padre"]) == 1 else None
    dg = [x["G_coord"] - x["G_padre"] for x in filas_ens if x.get("G_coord") is not None]
    techos_res = {"ensamblado": {k: v for k, v in ens.items() if k != "fallos"}, "celdas": len(filas_ens), "dG_min": min(dg) if dg else None, "dG_max": max(dg) if dg else None,
                  "cambios_de_signo_G": sum(1 for x in filas_ens if x.get("G_coord") is not None and (x["G_coord"] < 0) != (x["G_padre"] < 0))}

dictamen = "rechazada" if fallos else ("completa_validada" if TEC else "mallas_conciliadas_techos_pendientes")
SAL.mkdir()
with (SAL / "pares_puntos.jsonl").open("x", encoding="utf-8") as f:
    f.write("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in filas_puntos))
out = {"kind": "conciliacion-mallas-abl-enf-rem126", "sintetico": SINT, "manifiesto_mallas_sha256": H(raw), "producto_mallas_sha256": H(pb), "resultado_mallas_sha256": H(rb),
       "validador_elast": {"ruta": str(L119 / "validar_lote.py"), "dictamen": val.get("dictamen"), "fallos": val.get("fallos")}, "pares": resumen, "techos": techos_res,
       "pares_puntos_sha256": H((SAL / "pares_puntos.jsonl").read_bytes()), "dictamen": dictamen, "aceptada": not fallos, "fallos": fallos}
with (SAL / "CONCILIACION_MALLAS_ENF.json").open("x", encoding="utf-8") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
salir({"aceptada": not fallos, "dictamen": dictamen, "fallos": fallos[:8], "pares": len(resumen), "filas_comparadas": len(filas_puntos),
       "techos": None if techos_res is None else {k: techos_res[k] for k in ("celdas", "cambios_de_signo_G")}}, 0 if not fallos else 4)
