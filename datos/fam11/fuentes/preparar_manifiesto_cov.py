"""rem148 — PREPARADOR del paquete ABL-COV en paquete_cov_i2/ de rem148 (copia de paquete_ablaciones/preparar_manifiesto_cov.py rem147 bcbedcc8… con sustituciones contadas: ubicación del paquete en la receta, diferencial DIFERENCIAS_REM148.json y rótulos rem148; misma partición y lógica).
rem147 — PREPARACIÓN EXPLÍCITA del paquete ABL-COV (derivado de lote_enf/preparar_manifiesto_enf.py rem125 df6a6ad0…; solo lectura de fuentes
autenticadas; sin techos, supremo ni bridge; sin emitir alcances). Escribe en exclusiva, dentro de su carpeta:
- MANIFIESTO_ABL_COV.json (PROPUESTO_NO_EMITIDO) y COBERTURA_ABL_COV.json: 26 claves ABL-COV (phi/2, eta_f y resto del padre), 1.724 celdas padre
  testigo con su K1, partición determinista y presupuesto con antecedentes (no medidos para COV);
- manifiestos de PRUEBA: SINTETICO, SINTETICO-FALLO (salto vivo en la primera clave de T1) y FIXTURE-PUERTA (motor sin identidad válida),
  con claves SINT- y el doble declarado de sup_bound; ninguno habilita producción;
- receta_cov.sh (derivada de receta_enf.sh rem125 por sustituciones contadas, con la lista de tareas de ESTA partición);
- DIFERENCIAS_REM148.json (frente a las piezas lote_enf rem125) y PAQUETE_ABL_COV.json (índice con tamaño y sha256).
Partición (la de rem125): T1 = claves con antecedente < 60 s; el resto por first-fit decreasing con tope 1.500 s por grupo (> 1.500 s va
sola); grupos en orden ascendente de suma. Antecedente por clave = máximo entre (a) techos padre certificados de sus celdas (otra clave: phi
doble), (b) COORD B observado en esas celdas (otra clave: eta_f/2) y (c) ENF MEDIDO en rem127/rem128 para la clave ENF de las mismas celdas
(otra clave: eta_f/2 con phi padre). Ninguno es duración de las claves COV.
Uso: python -B -I -X utf8 preparar_manifiesto_cov.py <raiz> <censo_cov_rem147.json> <sha256_del_censo_cov>"""
import difflib
import hashlib
import json
import sys
from pathlib import Path

R, CE, CE_SHA = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
T = R / "tmp"
AQUI = Path(__file__).resolve().parent
C0 = T / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
S125 = T / "paso4_enforcement_desde_rem125/lote_enf"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
rel = lambda p: Path(p).relative_to(R).as_posix()  # noqa: E731
assert HF(S125 / "PAQUETE_ABL_ENF.json") == "039c85beb88e5912867ef8ebadcf47995cc8f9a99a5fd92e20bc072a7abda57c"
sys.path[:0] = [str(AQUI), str(C0 / "src"), str(C0 / "herramientas/b")]
import aprobacion_alcance as AA  # noqa: E402
import conexion_coord_cert as CX  # noqa: E402
import validar_coord_rec as VC  # noqa: E402
from paper2b import run as RUN  # noqa: E402

assert HF(CE) == CE_SHA
ce = json.loads(CE.read_bytes())
assert ce["conforme"] and ce["totales"]["celdas"] == 1724 and ce["totales"]["claves_unicas"] == 26 and ce["frente_a_ENF"]["mismas_celdas_que_ENF"]
FUENTE = {"ruta": "tmp/paso4_remanente_lotes_desde_rem113/censo/CENSO_REMANENTE.json", "sha256": ce["fuentes"]["censo_rem113"]["sha256"], "familia": "ABL-COV"}
censo, err = VC.leer_autenticado(R, FUENTE)
assert err is None and ce["fuentes"]["censo_rem113"]["en_inventario_sellado"]
fam = censo["ABL-COV"]
celdas_censo = [dict(c, conjunto_coord=s) for s, v in sorted(fam.items()) for c in v["celdas"]]
claves_censo = {}
for v in fam.values():
    claves_censo.update(v["claves_transformadas"])
assert set(claves_censo) == set(ce["claves"])
cfg = RUN.RunConfig()
prov = RUN.provider_for(cfg)
MOTOR = {"ruta": "RUN.provider_for(RUN.RunConfig()).capture_ceiling → ModeloTeorico.capture_ceiling → encierros_modelo.sup_bound (rama y cota con encierros)",
         "configuracion": CX.configuracion(prov, cfg.sup), "codigo": CX.identidad_codigo(C0 / "src/paper2b"), "instalacion_identidad": AA.identidad_instalacion(C0),
         "certificado_en_esta_plataforma": bool(prov.certified), "garantia": prov.garantia,
         "cierre": "NORMALIZADO: error_normalizado (cota demostrada de |C2 − sup/B_pot|) <= 1e-7 y sin caja viva en curva de salto; el error en R "
                   "(= error_normalizado·B_pot) se conserva y NO se equipara a 1e-7 en R",
         "metodo_a_fijar_en_el_alcance": "ruta certificada existente (la de ENF aceptado); su aceptación en ENF es antecedente técnico, no autorización para COV"}
LIM = {"tope_trabajo_s": 2400.0, "holgura_trabajo_s": 120.0, "tope_efectivo_trabajador_s": 2280.0, "tope_validacion_s": 300.0, "margen_s": 90.0, "cierre_s": 60.0,
       "reserva_suite_s": 2940.0, "tope_ensamblado_s": 300.0, "reserva_ensamblado_s": 390.0, "suite_max_s": 3600.0, "union_max_s": 10800.0, "procesos_max": 3}


def estimacion(k):
    v = ce["claves"][k]
    a = [x["segundos_calculo"] for x in v["antecedentes_padre"] if isinstance(x.get("segundos_calculo"), (int, float))]
    o = [s for s in v["segundos_observados_COORD_B_de_esas_claves"].values() if isinstance(s, (int, float))]
    e = [x["segundos"] for x in v["antecedentes_ENF_medidos"] if isinstance(x.get("segundos"), (int, float))]
    return (max(a + o + e) if a + o + e else None), {"padre_certificado_s": a, "coord_b_observado_s": o, "enf_medido_s": e,
                                                    "enf_estado": [(x["clave_enf"], x["estado"], x["resolucion"]) for x in v["antecedentes_ENF_medidos"]]}


est = {k: estimacion(k) for k in sorted(ce["claves"])}
assert all(e[0] is not None for e in est.values()), "clave sin antecedente: declararla no medida"
ligeras = sorted(k for k, e in est.items() if e[0] < 60)
pesadas = sorted((k for k, e in est.items() if e[0] >= 60), key=lambda k: (-est[k][0], k))
grupos = []                                          # first-fit decreasing con tope 1.500 s por grupo
for k in pesadas:
    e = est[k][0]
    g = next((g for g in grupos if e <= 1500 and sum(est[x][0] for x in g) + e <= 1500), None)
    if g is None:
        grupos.append([k])
    else:
        g.append(k)
grupos.sort(key=lambda g: (sum(est[x][0] for x in g), g))
tareas = ([ligeras] if ligeras else []) + [sorted(g, key=lambda k: (est[k][0], k)) for g in grupos]
assert len(tareas) <= 6 and sorted(sum(tareas, [])) == sorted(ce["claves"]), "la partición excede la lista cerrada de 6 tareas del conductor"
TAREAS = {"ABL-COV-T%d" % (i + 1): ks for i, ks in enumerate(tareas)}
CAMPOS = ("unidad", "cell_id", "pais", "diseno", "j", "menu", "cota", "capa", "ext", "K1_reutilizado", "G_padre", "C2_padre", "clave_transformada_sha256", "ref",
          "filas_sha256", "conjunto_coord")
DEGEN = ce["frente_a_ENF"]["controles_degenerados_identicos_al_padre"]


def manifiesto(sint=None, kind_extra=""):
    nombre = (lambda k: k) if sint is None else (lambda k: "SINT-" + k)
    rec = {}
    for k in sorted(ce["claves"]):
        v = ce["claves"][k]
        rec[nombre(k)] = {"clave": claves_censo[k]["clave"], "diseno": claves_censo[k]["diseno"], "j": claves_censo[k]["j"], "tau": claves_censo[k]["tau"],
                          "clave_completa_sha256": v["clave_completa_sha256"], "parametros_padre": v["parametros_padre"],
                          "motivo_recalculo": "ABL-COV preespecificado: phi/2 frente al padre (eta_f y resto fijos)",
                          "control_degenerado_identico_al_padre": k in DEGEN, "menu_d_invariancia_analitica": v["j"] == "d"}
    pres = {t: {"claves": [nombre(k) for k in ks], "antecedente_max_s": {nombre(k): est[k][0] for k in ks}, "suma_antecedentes_s": round(sum(est[k][0] for k in ks), 3),
                "detalle": {nombre(k): est[k][1] for k in ks}, "reserva_s": LIM["reserva_suite_s"] + (LIM["reserva_ensamblado_s"] if t == list(TAREAS)[-1] else 0)}
            for t, ks in TAREAS.items()}
    co = {"variante": "COV", "escenario": "ABL-COV", "transformacion": "coverage_half: phi ← phi/2 exacto; eta_f y las otras 11 entradas del padre intactas",
          "fuente_celdas": FUENTE, "fuentes": {"censo_cov_rem147": {"ruta": rel(CE), "sha256": CE_SHA}},
          "claves_coord_total": sorted(rec), "nota_esquema": "claves_coord_total y claves_recalculadas son nombres de campo heredados del esquema rem123; aquí son las 26 claves ABL-COV",
          "claves_recalculadas": rec, "claves_reutilizadas": {}, "tareas": {t: [nombre(k) for k in ks] for t, ks in TAREAS.items()},
          "celdas_afectadas": [dict({x: c[x] for x in CAMPOS}, clave_transformada_sha256=nombre(c["clave_transformada_sha256"]),
                                    unidad=(c["unidad"] if sint is None else "SINT-" + c["unidad"])) for c in celdas_censo],
          "celdas_total": len(celdas_censo),
          "motor": MOTOR if kind_extra != "-FIXTURE-PUERTA" else {"codigo": {"FIXTURE": "sin motor válido: rechazo antes de calcular"}, "configuracion": {}},
          "presupuesto": {"limites": LIM, "por_tarea": pres, "reserva_peor_caso_total_s": LIM["reserva_suite_s"] * len(TAREAS) + LIM["reserva_ensamblado_s"],
                          "suma_antecedentes_s": round(sum(est[k][0] for k in ce["claves"]), 3),
                          "regla_de_particion": "T1: antecedente < 60 s; resto por first-fit decreasing con tope 1.500 s por grupo (> 1.500 s va sola); grupos en orden ascendente de suma",
                          "nota": "antecedentes = techos padre certificados de las mismas celdas (otra clave), COORD B observado (otra clave) y ENF medido "
                                  "(otra clave); no son duración medida ni garantía para las claves COV"},
          "reutilizacion": {"adoptada": "ninguna: las 26 se recalculan por la ruta certificada",
                            "opcion_no_adoptada": {"claves": DEGEN, "motivo": "phi padre = 0: la clave COV es idéntica (sha256 completo) a la clave padre, de modo que "
                                                   "dC2 = 0 por identidad del modelo; el techo padre existe solo en corridas de otra instalación/método (código 037d20d3…), "
                                                   "sin autoridad para reutilizarlo como techo certificado; recalcularlas sirve además de control: C2_COV debe coincidir "
                                                   "con C2_padre dentro de su error"}},
          "k1": "K1_reutilizado de cada celda padre (censo rem113 = manifiestos COORD aceptados), sin cambio; K1 no depende de phi (ec. 24), como en COORD",
          "fuera_del_lote": {s: {"celdas": 0, "estado": "fuera del nivel por D-COORD-ALCANCE (sin testigos padre); no NA"} for s, v in fam.items() if not v["celdas"]},
          "separados": ["D-EXP8/N3 (no adoptadas)", "ABL-ENF (aceptado en rem132; canal eta_f, no se repite)", "canales locales EXT-Q y ROB-LABH/LABW/TAX"],
          "continuidad": "una tarea incompleta detiene la cadena; las no iniciadas siguen en el mismo alcance y su relanzamiento exige permiso expreso de un "
                         "encargo posterior; una clave con supremo no alcanzado solo se integra con una resolución y un certificado propios de ESA clave "
                         "(derivando la integración corregida rem130), nunca extrapolando la de ENF d59edf8a9d1461d1"}
    if sint is not None:
        co["sintetico"] = {"renombre": {nombre(k): k for k in ce["claves"]}, "supbound": {nombre(k): sint(k) for k in ce["claves"]},
                           "nota": "DOBLE DECLARADO de encierros_modelo.sup_bound: SupBound sintético; ninguna rama y cota real; no es producción"}
    kind = "manifiesto-abl-cov-rem148" + kind_extra + ("-SINTETICO" if sint is not None and kind_extra != "-FIXTURE-PUERTA" else "")
    return {"kind": kind, "estado": "PROPUESTO_NO_EMITIDO" if sint is None else "PRUEBA_NO_PRODUCCION", "variante": "COV",
            "b_official_run_authorized": False, "freeze_run_authorized": False, "official_export_authorized": False, "ABL-COV": co}


k_legit = sorted(ce["claves"])[0]
cerrado = lambda k: {"approx": 0.0029, "lower": 0.0029 - 2.5e-8, "upper": 0.0029 + (1.5e-7 if k == k_legit else 5e-8), "punto": [0.0, 0.0], "cajas": 100, "salto_vivo": False}  # noqa: E731
primero_t1 = TAREAS["ABL-COV-T1"][0]
salidas = {"MANIFIESTO_ABL_COV.json": manifiesto(), "MANIFIESTO_ABL_COV-SINTETICO.json": manifiesto(sint=cerrado),
           "MANIFIESTO_ABL_COV-SINTETICO-FALLO.json": manifiesto(sint=lambda k: dict(cerrado(k), salto_vivo=(k == primero_t1)), kind_extra="-FALLO"),
           "MANIFIESTO_ABL_COV_FIXTURE-PUERTA.json": manifiesto(sint=cerrado, kind_extra="-FIXTURE-PUERTA")}
resumen = {}
for nombre, doc in salidas.items():
    p = AQUI / nombre
    with p.open("x", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    with (AQUI / nombre.replace("MANIFIESTO_", "COBERTURA_")).open("x", encoding="utf-8") as f:
        f.write(json.dumps({"kind": "cobertura-nacional-lote1", "manifiesto_sha256": HF(p), "conjuntos": {}, "origen": "rem148 preparar_manifiesto_cov.py",
                            "nota": "ABL-COV: sin conjuntos λπ; anexo exigido por el conductor y ligado a este manifiesto"}, ensure_ascii=False, indent=1) + "\n")
    co = doc["ABL-COV"]
    resumen[nombre] = {"kind": doc["kind"], "sha256": HF(p), "claves": len(co["claves_recalculadas"]), "celdas": len(co["celdas_afectadas"]),
                       "tareas": {t: len(v) for t, v in co["tareas"].items()}, "transformacion_valida": VC.validar_transformacion(co) == []}
    assert resumen[nombre]["transformacion_valida"], nombre

# receta: receta_enf.sh rem125 con sustituciones contadas y la lista de tareas de esta partición
rb = (S125 / "receta_enf.sh").read_bytes()
rt = rb.decode("utf-8")
REC = [("# rem125 — RECETA CONECTADA DEL CONTRASTE ABL-ENF", "# rem148 — RECETA CONECTADA DEL CONTRASTE ABL-COV (derivada de receta_enf.sh rem125 %s… por sustituciones "
        "contadas; mismo flujo, manifiesto y anexo COV, tareas %s).\n# rem125 — RECETA CONECTADA DEL CONTRASTE ABL-ENF" % (H(rb)[:8], ",".join(TAREAS)), 1),
       ("USO: receta_enf.sh <area> <ENF>", "USO: receta_cov.sh <area> <COV>", 1),
       ('  ENF) TAREAS="ABL-ENF-T1,ABL-ENF-T2,ABL-ENF-T3,ABL-ENF-T4,ABL-ENF-T5,ABL-ENF-T6" ;;', '  COV) TAREAS="%s" ;;' % ",".join(TAREAS), 1),
       ('L="$RAIZ/tmp/paso4_enforcement_desde_rem125/lote_enf"', 'L="$RAIZ/tmp/paso4_cov_remanente_desde_rem148/paquete_cov_i2"', 1),
       ('SAL="$1/enf_$5"', 'SAL="$1/cov_$5"', 1), ("MANIFIESTO_ABL_ENF.json", "MANIFIESTO_ABL_COV.json", 1), ("COBERTURA_ABL_ENF.json", "COBERTURA_ABL_COV.json", 1),
       ('echo "RC_ABL_ENF=$rc"', 'echo "RC_ABL_COV=$rc"', 1)]
cuentas_receta = []
for o, nw, k in REC:
    c = rt.count(o)
    assert c == k, (o, c)
    rt = rt.replace(o, nw)
    cuentas_receta.append({"origen": o, "destino": nw, "esperadas": k, "halladas": c})
with (AQUI / "receta_cov.sh").open("xb") as f:
    f.write(rt.encode("utf-8"))


def dif(a, b):
    la, lb = Path(a).read_text(encoding="utf-8").splitlines(), Path(b).read_text(encoding="utf-8").splitlines()
    return {"origen": rel(a), "origen_sha256": HF(a), "destino": rel(b), "destino_sha256": HF(b), "diff": list(difflib.unified_diff(la, lb, rel(a), rel(b), lineterm="", n=1))}


pares = [(n, n) for n in ("conducir_lote.py", "tarea_lote.py", "conexion_coord_cert.py", "validar_coord_rec.py", "validar_lote.py", "ensamblar_coord.py",
                          "emitir_alcance_rec.py", "referencia_decision.py")] + [("receta_enf.sh", "receta_cov.sh"), ("preparar_manifiesto_enf.py", "preparar_manifiesto_cov.py")]
with (AQUI / "DIFERENCIAS_REM148.json").open("x", encoding="utf-8") as f:
    f.write(json.dumps({"piezas": {d: dif(S125 / o, AQUI / d) for o, d in pares}, "receta_sustituciones": cuentas_receta}, ensure_ascii=False, indent=1) + "\n")
piezas = {p.name: {"sha256": HF(p), "bytes": p.stat().st_size} for p in sorted(AQUI.iterdir()) if p.is_file() and p.name != "PAQUETE_ABL_COV.json"}
with (AQUI / "PAQUETE_ABL_COV.json").open("x", encoding="utf-8") as f:
    f.write(json.dumps({"kind": "paquete-abl-cov-rem148", "estado": "CANDIDATO_NO_EMITIDO", "piezas": piezas, "nucleo": {"ruta": rel(C0), "identidad": MOTOR["instalacion_identidad"]},
                        "deriva_de": {"paquete": rel(S125), "indice_sha256": HF(S125 / "PAQUETE_ABL_ENF.json")}, "fuente_celdas": FUENTE,
                        "censo": {"ruta": rel(CE), "sha256": CE_SHA},
                        "alcance_necesario": "un alcance v3 con las %d tareas ABL-COV + una decisión humana nativa dedicada sobre su sha256; no emitido en rem148" % len(TAREAS)},
                       ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"resumen": resumen, "tareas": TAREAS, "estimacion_por_tarea": {t: round(sum(est[k][0] for k in ks), 1) for t, ks in TAREAS.items()},
                  "antecedente_por_clave": {k: est[k][0] for k in sorted(est)}, "degenerados": DEGEN, "piezas": len(piezas)}, ensure_ascii=False, indent=1))
