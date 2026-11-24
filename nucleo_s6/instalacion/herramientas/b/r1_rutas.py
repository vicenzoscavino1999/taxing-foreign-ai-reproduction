"""RUTAS R1 POR COMANDO HISTÓRICO (rem44; candidato; NO OFICIAL). Conecta las rutas R1 distintas del orquestador (A1, A2, A3×4, B1–B3, F)
y el intercambio de productos ACEPTADOS de D/V, con la misma disciplina que r1_s6:
  entrada sellada  = tarea del plan + ids de la cobertura R1 AUTENTICADA + referencia citada AUTENTICADA;
  productor        = comando HISTÓRICO exacto (módulo y argumentos) del registro de lanzamiento autenticado de su entrega, DERIVADO de las
                     fuentes de la referencia (el comando cuyo argumento es el archivo fuente) o de los registros C2 de la cobertura;
                     se ejecuta con el NÚCLEO S6 y el ContextoS6 (importador por entrega con las sustituciones genéricas registradas);
  entradas         = archivos de la entrega histórica (copias en el paquete) o PRODUCTOS ACEPTADOS de las dependencias (nunca el
                     histórico cuando la cobertura exige regenerarlo, p. ej. la L de A3 con el certificado U NUEVO);
  validación       = cada salida del comando IGUAL a la salida histórica del MISMO comando (bytes autenticados), sin campos operativos;
                     cobertura: cada id requerido mapeado a una fuente presente y validada; nada ajeno ni duplicado;
  registro         = registro_productivo.generar_r1_ruta (validador de la fase R1 = r1_s6.py, que fija este módulo por sha256).
Mecanismos de PRUEBA (dobles en el límite del cálculo) separados de la ejecución productiva: `ejecutar_comando(..., doble=None)`.
  derivar(tarea, raiz_fuentes) -> plan de la ruta;  preparar/ejecutar/validar -> productos;  importar_aceptados (D/V)."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import runpy
import shutil
import sys
from pathlib import Path

COBERTURA = ("validacion_evidencia_comparador_paso4_3_7_2026-10-12_lima1857", "369beaa07cc56fffc966112b6d1faaebac60d072529dc299e761eebf523bca42",
             "demo/plan15/cobertura_r1.json")
OPERATIVOS = {"segundos", "pared_s", "cpu_s", "t_utc", "inicio_utc", "fin_utc", "fecha", "fecha_utc", "pid", "duracion_s", "tiempo_s", "tiempos_s",
              "transcurrido_s", "hora", "maquina", "python", "entorno"}
# registros C2 de la cobertura (tareas_c2_registradas) para las cotas de A3 (la referencia cita una INSTANTÁNEA de su salida)
A3 = {"R1-A3-G-U": "CERTA-G", "R1-A3-N-U": "CERTA-N", "R1-A3-G-L": "INFBB5b-G", "R1-A3-N-L": "INFBB5-N"}
DEPENDENCIA_DE_ENTRADA = {"R1-A3-G-L": ("R1-A3-G-U", 1), "R1-A3-N-L": ("R1-A3-N-U", 1)}   # argumento que DEBE venir del producto aceptado
# presupuesto (base declarada) para A1: SUPC (lima1259) y SRED (lima1958); se contrasta con la fuente_punto de la referencia citada
A1_BASE = [("correccion_cotas_paso4_3_7_2026-10-05_lima1259", "logs/H2/SUPC-%s.tarea.json" % k) for k in ("Gd", "Gf", "Nd", "Nf")] + \
          [("cierre_df_paso4_3_7_2026-10-05_lima1958", "logs/H2/SRED-%s.tarea.json" % k) for k in ("G", "N")]


class RutaError(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle) if detalle else codigo)
        self.codigo, self.detalle = codigo, detalle


def need(t, c, d=""):
    if not t:
        raise RutaError(c, d)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _inv(T: Path, entrega: str) -> dict:
    return json.loads((T / entrega / "audit/entrega.json").read_bytes())["files"]


def _aut(T: Path, entrega: str, rel: str, inv=None) -> bytes:
    inv = inv or _inv(T, entrega)
    raw = (T / entrega / rel).read_bytes()
    x = inv.get(rel)
    need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "ARCHIVO_HISTORICO_NO_AUTENTICADO", "%s/%s" % (entrega, rel))
    return raw


def cobertura(T: Path) -> dict:
    ent, h, rel = COBERTURA
    inv_raw = (T / ent / "audit/entrega.json").read_bytes()
    need(sha(inv_raw) == h, "COBERTURA_R1_NO_AUTENTICADA")
    return json.loads(_aut(T, ent, rel, json.loads(inv_raw)["files"]))


def _comando(T: Path, entrega: str, registro: str) -> dict:
    """Comando histórico de un registro de lanzamiento AUTENTICADO: módulo, argumentos (tras «-m módulo») y código de salida 0."""
    d = json.loads(_aut(T, entrega, registro))
    c = [str(x).strip() for x in (d.get("comando") or [])]
    need("-m" in c and d.get("codigo_salida") == 0, "REGISTRO_SIN_COMANDO_O_FALLIDO", registro)
    i = c.index("-m")
    return {"entrega": entrega, "registro": registro, "registro_sha256": sha((T / entrega / registro).read_bytes()), "modulo": c[i + 1], "argv": c[i + 2:]}


def _comando_que_escribe(T: Path, entrega: str, archivo: str) -> dict:
    """El ÚNICO registro de lanzamiento (logs/**.tarea.json, autenticado) de la entrega cuyo comando tiene `archivo` como argumento."""
    inv = _inv(T, entrega)
    cands = []
    for rel in sorted(k for k in inv if k.startswith("logs/") and k.endswith(".tarea.json") and "/intento" not in k):   # intentos superados: fuera
        try:
            d = json.loads((T / entrega / rel).read_bytes())
        except (OSError, ValueError):
            continue
        if archivo in [str(x).strip() for x in (d.get("comando") or [])] and d.get("codigo_salida") == 0:
            cands.append(rel)
    need(len(cands) >= 1, "PRODUCTOR_NO_DERIVABLE", "%s/%s" % (entrega, archivo))
    need(len(cands) == 1, "PRODUCTOR_AMBIGUO", "%s/%s: %s" % (entrega, archivo, cands))
    return _comando(T, entrega, cands[0])


def _fuente(x):
    return ast.literal_eval(x) if isinstance(x, str) else x


def derivar(tarea: str, T) -> dict:
    """Plan de la ruta desde lo AUTENTICADO: ids requeridos, referencia citada, comandos productores y mapeo id -> (entrega, archivo)."""
    T = Path(T)
    cob = cobertura(T)
    tt = {t["tarea"]: t for t in cob["tareas"]}
    ids = [i for k, v in tt.items() if k == tarea or k.startswith(tarea + "-") for i in (v.get("ids") or [])]
    need(ids, "TAREA_SIN_COBERTURA", tarea)
    cita = ((tt.get(tarea) or {}).get("referencia") or {}).get("cita")
    out = {"tarea": tarea, "ids": ids, "cita": cita, "comandos": [], "id_fuente": {}, "observaciones": []}
    if cita:
        need(sha((T / cita["entrega"] / "audit/entrega.json").read_bytes()) == cita["inventario_sha256"], "REFERENCIA_R1_NO_AUTENTICADA", cita["archivo"])
        ref = json.loads(_aut(T, cita["entrega"], cita["archivo"]))
    if tarea in A3:
        reg = cob["tareas_c2_registradas"][A3[tarea]]
        f = reg["fuente"]
        out["comandos"].append(_comando(T, f["entrega"], f["archivo"]))
        dis = "G" if "-G-" in tarea else "N"
        lado = "U_fuente" if tarea.endswith("-U") else "L_fuente"
        fu = ref["disenos"][dis][lado]
        arch = str(fu.get("fuente", "")).split(" (")[0]
        out["id_fuente"] = {ids[0]: {"entrega": cita["entrega"], "archivo": arch, "sha256": fu.get("sha256"), "valor": fu.get("U" if lado == "U_fuente" else "L")}}
        if lado == "U_fuente":
            base = arch.replace("_instantanea", "")                       # la referencia cita una INSTANTÁNEA del certificado
            try:
                out["comandos"].insert(0, dict(_comando_que_escribe(T, cita["entrega"], base), salida=base))
            except RutaError as ex:
                out["observaciones"].append({"codigo": ex.codigo, "detalle": ex.detalle})
            if fu.get("estado_techo") == "tope_tiempo":
                out["observaciones"].append({"codigo": "REFERENCIA_DEPENDE_DEL_RELOJ", "detalle": "U de una instantánea tomada al agotar el tope de tiempo "
                                             "(estado_techo=tope_tiempo): la igualdad exacta no es un criterio reproducible; requiere decisión"})
        if tarea in DEPENDENCIA_DE_ENTRADA:
            out["entrada_de_dependencia"] = {"tarea": DEPENDENCIA_DE_ENTRADA[tarea][0], "argumento": DEPENDENCIA_DE_ENTRADA[tarea][1]}
            out["observaciones"].append({"codigo": "VALIDACION_POR_IGUALDAD_NO_APLICABLE", "detalle": "la cobertura exige regenerar la L con el certificado U "
                                         "NUEVO (nunca la L histórica): su criterio de aceptación frente a la referencia requiere decisión"})
    elif tarea in ("R1-B1", "R1-B2", "R1-B3"):
        filas = {}
        for f in ref["filas"]:
            filas[sha((f["hoja"] + "|" + f["sentido"]).encode("utf-8"))[:16]] = _fuente(f["fuente_cota"])
        fuentes = {}
        for i in ids:
            need(i in filas, "ID_SIN_FILA_EN_LA_REFERENCIA", i)
            fu = filas[i]
            out["id_fuente"][i] = {"entrega": fu["entrega"], "archivo": fu["archivo"], "sha256": fu.get("sha256")}
            fuentes[(fu["entrega"], fu["archivo"])] = 1
        for e, a in sorted(fuentes):
            out["comandos"].append(dict(_comando_que_escribe(T, e, a), salida=a))
    elif tarea == "R1-F":
        out["comandos"].append(dict(_comando_que_escribe(T, cita["entrega"], cita["archivo"]), salida=cita["archivo"]))
        out["id_fuente"] = {i: {"entrega": cita["entrega"], "archivo": cita["archivo"], "sha256": cita["sha256"]} for i in ids}
    elif tarea in ("R1-A1", "R1-A2"):
        c2 = {x["witness_of"]: _fuente(x.get("fuente_punto")) for x in ref.get("C2", [])}
        for i in ids:
            need(i in c2 and c2[i], "ID_SIN_TESTIGO_EN_LA_REFERENCIA", i)
            out["id_fuente"][i] = {"entrega": c2[i]["entrega"], "archivo": c2[i]["archivo"], "sha256": c2[i].get("sha256")}
        out["observaciones"].append({"codigo": "TESTIGO_C2_DE_PRODUCTOS_DE_OTRAS_RUTAS", "detalle": "los testigos C2 de la referencia proceden de "
                                     "salidas de B3 (extremos_G_d/f) y de SRED: definir si la ruta C2 consume esos productos aceptados o recalcula (decisión)"})
        if tarea == "R1-A1":
            out["comandos"] = [_comando(T, e, r) for e, r in A1_BASE]
            pos = {(c["entrega"], a) for c in out["comandos"] for a in c["argv"]}
            fuera = sorted({(v["entrega"], v["archivo"]) for v in out["id_fuente"].values()} - pos)
            if fuera:
                out["observaciones"].append({"codigo": "FUENTE_DEL_TESTIGO_DISTINTA_DE_LA_BASE_DEL_PRESUPUESTO", "fuentes_de_la_referencia": fuera,
                                             "base": [c["registro"] for c in out["comandos"]]})
        else:
            fuentes = sorted({(v["entrega"], v["archivo"]) for v in out["id_fuente"].values()})
            for e, a in fuentes:
                try:
                    out["comandos"].append(dict(_comando_que_escribe(T, e, a), salida=a))
                except RutaError as ex:
                    out["observaciones"].append({"codigo": ex.codigo, "detalle": ex.detalle})
    else:
        raise RutaError("RUTA_NO_POR_COMANDO", tarea)
    nuc = Path(__file__).resolve().parents[2] / "src/paper2b"
    for e in sorted({c["entrega"] for c in out["comandos"]}):
        n = nucleo_por_entrega(T, e, nuc)
        extra = sorted(set(n["distintos"]) - {"run.py", "rules.py"})        # run.py/rules.py: identidad técnica, contrato y NA (ninguna fórmula R1)
        if extra:
            out["observaciones"].append({"codigo": "NUCLEO_HISTORICO_DISTINTO_DE_S6_EN_MODULOS_DE_CALCULO", "entrega": e, "modulos": extra,
                                         "detalle": "la referencia se calculó con un núcleo anterior; reproducir con el núcleo S6 puede cambiar el resultado: decisión"})
    return out


def salidas_del_comando(c: dict, T: Path) -> list:
    """Argumentos que son SALIDAS: archivos de la entrega histórica escritos por ese comando (declarado por «salida» o por estar en el
    inventario de la entrega con la extensión de datos y no ser una entrada preexistente referida por otro registro)."""
    if c.get("salida"):
        return [c["salida"]]
    inv = _inv(T, c["entrega"])
    return [a for a in c["argv"] if a in inv and a.endswith((".json", ".jsonl")) and "instantanea" not in a]


def _sin_operativos(x):
    if isinstance(x, dict):
        return {k: _sin_operativos(v) for k, v in x.items() if k not in OPERATIVOS}
    if isinstance(x, list):
        return [_sin_operativos(v) for v in x]
    return x


def _cargar(b: bytes):
    try:
        return json.loads(b)
    except ValueError:
        return [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]


def igual_a_historica(producido: bytes, historico: bytes) -> bool:
    return _sin_operativos(_cargar(producido)) == _sin_operativos(_cargar(historico))


def preparar(plan_ruta: dict, T, paquete: Path, aceptados: dict | None = None) -> dict:
    """Copia al paquete las ENTRADAS de cada comando (archivos de la entrega histórica autenticados) y, cuando la cobertura exige
    regenerar, el PRODUCTO ACEPTADO de la dependencia (nunca el histórico). Devuelve {comando_idx: argv con rutas del paquete}."""
    T, out = Path(T), {}
    for n, c in enumerate(plan_ruta["comandos"]):
        inv = _inv(T, c["entrega"])
        sal = set(salidas_del_comando(c, T))
        argv = list(c["argv"])
        dep = plan_ruta.get("entrada_de_dependencia")
        for k, a in enumerate(argv):
            if dep and k == dep["argumento"]:
                need(aceptados and dep["tarea"] in aceptados, "ENTRADA_DE_DEPENDENCIA_NO_ACEPTADA", dep["tarea"])
                src = aceptados[dep["tarea"]]
                (paquete / a).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, paquete / a)
                continue
            if a in inv and a not in sal:
                (paquete / a).parent.mkdir(parents=True, exist_ok=True)
                (paquete / a).write_bytes(_aut(T, c["entrega"], a, inv))
        out[n] = argv
    return out


RC_EXCEPCION, RC_GUARDA = 70, 71


def ejecutar_comando(c: dict, argv: list, paquete: Path, importador, doble=None) -> int:
    """PRODUCTIVO: ejecuta `-m módulo argv` del comando histórico con el importador de SU entrega (núcleo S6, ContextoS6) y cwd = paquete.
    rem45 (P4-R1-ENTRADA-COMANDO): runpy.run_module resuelve el módulo con el importador (find_spec + get_code: los MISMOS bytes autenticados
    y portados que exec_module) y lo ejecuta como __main__ con NUCLEO_S6 en sus globales. Rechazo CONTROLADO: SystemExit -> su código; una
    excepción (autenticación, importación o cálculo) -> RC_EXCEPCION con el error en importador.errores; tras la ejecución, la guarda del
    núcleo (un paper2b histórico introducido -> RC_GUARDA). cwd y argv se restauran siempre.
    PRUEBA: `doble(c, argv, paquete)` sustituye la llamada en el LÍMITE DEL CÁLCULO (nunca en producción)."""
    if doble is not None:
        return int(doble(c, argv, paquete) or 0)
    viejo_cwd, viejo_argv = os.getcwd(), list(sys.argv)
    try:
        os.chdir(paquete)
        sys.argv = [c["modulo"]] + list(argv)
        try:
            importador.instalar()                    # aislamiento: otro paquete «codigo» cargado o paper2b ajeno -> rechazo controlado
            runpy.run_module(c["modulo"], init_globals={"NUCLEO_S6": importador.nucleo}, run_name="__main__", alter_sys=True)
            rc = 0
        except SystemExit as ex:
            rc = int(ex.code or 0) if not isinstance(ex.code, str) else 1
        except Exception as ex:  # noqa: BLE001
            importador.errores.append({"modulo": c["modulo"], "tipo": type(ex).__name__, "codigo": getattr(ex, "codigo", None), "detalle": str(ex)[:400]})
            rc = RC_EXCEPCION
        try:
            importador.guarda()
        except RutaError as ex:
            importador.errores.append({"modulo": c["modulo"], "tipo": "RutaError", "codigo": ex.codigo, "detalle": str(ex)[:300]})
            rc = RC_GUARDA
        return rc
    finally:
        os.chdir(viejo_cwd)
        sys.argv = viejo_argv


# rem50 (P4-R1-ARTEFACTO-PREFLIGHT): ARTEFACTO que el TRABAJADOR (tarea_r1) escribe en el paquete durante el PREFLIGHT: el plan del
# orquestador regenerado bajo S6 (orquestador_b.plan, sin cálculo). No es un producto científico ni una salida de comando. validar lo admite
# SOLO si la ruta lo DECLARA (plan_ruta["artefactos_del_trabajador"] = {ruta: sha256 registrado por el preflight}), sus bytes tienen ese
# sha256 y su contenido (afirmación, ruta, dependencias de cada fila) es el del plan histórico AUTENTICADO de lima1351. Sin declaración, o
# alterado, ausente, ilegible o distinto, no se admite; cualquier otro archivo sigue siendo ajeno (no hay exclusión por nombre ni carpeta).
ARTEFACTO_PREFLIGHT = "plan_orquestador_s6.json"
PLAN_HISTORICO = ("p0_completo_h4_paso4_3_7_2026-10-09_lima1351", "demo/orquestador3/plan_1728_v3.json")


def plan_orquestador_conforme(T, raw: bytes) -> dict:
    """Contraste del plan del orquestador regenerado con el histórico AUTENTICADO (afirmación, ruta y dependencias de cada fila)."""
    hraw = _aut(Path(T), *PLAN_HISTORICO)
    clave = lambda f: (f["afirmacion"], f["ruta"], tuple(f["dependencias"]))  # noqa: E731
    nuevo = json.loads(raw)["filas"]
    return {"sha256": sha(raw), "filas": len(nuevo), "igual_al_historico_en_afirmaciones_rutas_y_dependencias": sorted(map(clave, nuevo)) == sorted(map(clave, json.loads(hraw)["filas"])),
            "historico": {"entrega": PLAN_HISTORICO[0], "archivo": PLAN_HISTORICO[1], "sha256": sha(hraw)}}


def _artefactos(plan_ruta: dict, T, paquete: Path) -> tuple:
    """(rutas admitidas, informe ligado al preflight, códigos de rechazo) de los artefactos DECLARADOS por la ruta."""
    adm, inf, cods = set(), [], []
    for rel, h in sorted((plan_ruta.get("artefactos_del_trabajador") or {}).items()):
        if rel != ARTEFACTO_PREFLIGHT:
            cods.append("ARTEFACTO_DECLARADO_NO_PREVISTO")
            continue
        p = Path(paquete) / rel
        if not p.is_file():
            cods.append("ARTEFACTO_DEL_TRABAJADOR_AUSENTE")
            continue
        raw = p.read_bytes()
        if sha(raw) != h:
            cods.append("ARTEFACTO_DEL_TRABAJADOR_ALTERADO")
            continue
        try:
            c = plan_orquestador_conforme(T, raw)
        except (ValueError, KeyError, TypeError, RutaError):
            cods.append("ARTEFACTO_DEL_TRABAJADOR_ILEGIBLE")
            continue
        if not c["igual_al_historico_en_afirmaciones_rutas_y_dependencias"]:
            cods.append("ARTEFACTO_DEL_TRABAJADOR_DISTINTO_DEL_HISTORICO")
            continue
        adm.add(rel)
        inf.append(dict(c, archivo=rel, origen="preflight de tarea_r1: orquestador_b.plan bajo S6 (sin cálculo); no es producto científico"))
    return adm, inf, cods


def validar(plan_ruta: dict, T, paquete: Path, rcs: dict) -> dict:
    """Cada comando terminó con 0 y cada SALIDA es igual a la histórica del mismo comando; cada id requerido tiene su fuente entre las
    salidas validadas (cobertura); sin salidas ajenas en el paquete fuera de las declaradas y las entradas copiadas. rem50: el artefacto
    del preflight DECLARADO por la ruta se admite tras comprobar sus bytes y su contenido (_artefactos); queda en el informe."""
    T = Path(T)
    malos, validas, faltan = [], set(), []
    for n, c in enumerate(plan_ruta["comandos"]):
        if rcs.get(n) != 0:
            malos.append({"comando": c["registro"], "motivo": "CODIGO_DE_SALIDA_%s" % rcs.get(n)})
            continue
        for s in salidas_del_comando(c, T):
            p = paquete / s
            if not p.exists():
                faltan.append(s)
                continue
            if not igual_a_historica(p.read_bytes(), _aut(T, c["entrega"], s)):
                malos.append({"comando": c["registro"], "salida": s, "motivo": "SALIDA_DISTINTA_DE_LA_HISTORICA"})
                continue
            validas.add((c["entrega"], s))
    sin = [i for i, f in plan_ruta["id_fuente"].items() if (f["entrega"], f["archivo"]) not in validas]
    adm, inf_art, cods_art = _artefactos(plan_ruta, T, paquete)
    permitidos = {a for c in plan_ruta["comandos"] for a in c["argv"]} | {s for c in plan_ruta["comandos"] for s in salidas_del_comando(c, T)} | adm
    ajenos = sorted(q.relative_to(paquete).as_posix() for q in paquete.rglob("*") if q.is_file() and q.relative_to(paquete).as_posix() not in permitidos) \
        if paquete.exists() else []
    cods = [k for k, v in (("SIN_COMANDOS", not plan_ruta["comandos"]), ("COMANDO_FALLIDO_O_SALIDA_DISTINTA", malos), ("SALIDA_FALTANTE", faltan),
                           ("ID_REQUERIDO_SIN_SALIDA_VALIDADA", sin), ("ARCHIVO_AJENO_EN_EL_PAQUETE", ajenos),
                           ("OBSERVACIONES_DE_DERIVACION", plan_ruta.get("observaciones"))) if v] + sorted(set(cods_art))
    return {"cumple": not cods, "codigos": cods, "comandos": len(plan_ruta["comandos"]), "salidas_validadas": len(validas), "ids": len(plan_ruta["id_fuente"]),
            "ids_sin_salida_validada": sin[:20], "n_ids_sin_salida": len(sin), "fallos": malos[:10], "faltan": faltan[:10], "ajenos": ajenos[:10],
            "observaciones": plan_ruta.get("observaciones"), "artefactos_del_trabajador": inf_art}


# ------------------------------------------------------------------------------------------- importador por ENTREGA (núcleo S6)
# Anclas de inventario de las entregas de los productores (de E5.SRC, de las citas de la cobertura y del adaptador r1_s6); una entrega
# sin ancla no se usa.
ENTREGAS = {"correccion_cotas_paso4_3_7_2026-10-05_lima1259": "6bc4c909a24596c972ccf8e5140cc893d3ca36ac15f85c112fb7eef9b3643577",
            "cierre_df_paso4_3_7_2026-10-05_lima1958": "f62789edc1e7f22c307e23cad95d71dcdff07f99715c63d5dbea9f5d0a991f8c",
            "extremos_df_d_3_7_2026-10-05_lima0738": "116a3f06bb8f5dc449e6c9921a6fd4600abb2f349bb61b3ee8667b412d796bd4",
            "cierre_candidato_3_7_2026-10-04_lima2103": "ea126009763844cf58f365fc5b9c8e68f8141a4302be59562e0b914094e0d9db",
            "cierre_inf_df_paso4_3_7_2026-10-05_lima2149": "646202ea417e4a874498c26cd940788d26bb7dd33d4f6932e9f2eec1efa973bb",
            "p1b_global_h4_paso4_3_7_2026-10-09_lima1913": "829c6663e527075f4966ddf549f4a95ca36154f224602004a194f0ad9e436c8b",
            "p0_completo_h4_paso4_3_7_2026-10-09_lima1351": "ba473a76059faa9719e0f2a0638ce51878a872e74fccf6c680b9d9d73fb14743"}
GENERICAS = [('sys.path.insert(0, str(AREA / "integracion/src"))     # paper2b de la INTEGRACIÓN CANDIDATA (bytes probados)', "pass  # rem44: núcleo S6"),
             ('sys.path.insert(0, str(AREA / "integracion/src"))', "pass  # rem44: núcleo S6"),
             ('(AREA / "integracion/src/paper2b").resolve()', "NUCLEO_S6"),
             ('for p in (ROOT, ROOT / "src"):', "for p in ():  # rem44: el candidato S6 ya está en sys.path")]


def nucleo_por_entrega(T, entrega: str, nucleo_s6: Path) -> dict:
    """Comparación CONCRETA del paper2b aislado de una entrega con el núcleo S6 (los distintos se presentan; nunca se ocultan)."""
    d = Path(T) / entrega / "integracion/src/paper2b"
    if not d.exists():
        return {"entrega": entrega, "sin_nucleo_aislado": True, "distintos": []}
    fs = sorted({p.name for p in d.glob("*.py")} | {p.name for p in Path(nucleo_s6).glob("*.py")})
    return {"entrega": entrega, "distintos": [f for f in fs if (d / f).exists() and (Path(nucleo_s6) / f).exists() and (d / f).read_bytes() != (Path(nucleo_s6) / f).read_bytes()],
            "solo_historico": [f for f in fs if (d / f).exists() and not (Path(nucleo_s6) / f).exists()]}


class ImportadorEntrega:
    """`codigo.*` desde los BYTES de UNA entrega autenticados por su inventario ANCLADO, con las sustituciones GENÉRICAS registradas
    (cada una se aplica donde aparece) y `codigo.demo.nucleo_v.Contexto` -> el ContextoS6 de la corrida. Un proceso aloja una sola
    entrega (el paquete «codigo» es único). Guarda: todo paper2b debe ser el núcleo S6."""

    def __init__(self, T, entrega: str, nucleo_s6: Path, ctx=None):
        self.T, self.entrega, self.nucleo, self.ctx = Path(T), entrega, Path(nucleo_s6).resolve(), ctx
        need(entrega in ENTREGAS, "ENTREGA_SIN_ANCLA", entrega)
        raw = (self.T / entrega / "audit/entrega.json").read_bytes()
        need(sha(raw) == ENTREGAS[entrega], "INVENTARIO_DE_ENTREGA_ALTERADO", entrega)
        self.inv = json.loads(raw)["files"]
        self.area = self.T / entrega
        self.registro = {}
        self.errores = []

    def guarda(self):
        malos = sorted(n for n, m in list(sys.modules.items()) if (n == "paper2b" or n.startswith("paper2b.")) and getattr(m, "__file__", None)
                       and not Path(m.__file__).resolve().is_relative_to(self.nucleo))
        need(not malos, "NUCLEO_HISTORICO_INTRODUCIDO", str(malos[:3]))

    def find_spec(self, fullname, path=None, target=None):
        import importlib.util
        if fullname != "codigo" and not fullname.startswith("codigo."):
            return None
        rel = fullname.replace(".", "/")
        pkg = self.area / rel / "__init__.py"
        f = pkg if pkg.is_file() else self.area / (rel + ".py")
        if not f.is_file():
            return None
        return importlib.util.spec_from_file_location(fullname, f, loader=self, submodule_search_locations=[str(f.parent)] if f == pkg else None)

    def create_module(self, spec):
        return None

    def _portar(self, f: Path):
        """BYTES de la entrega autenticados por su inventario ANCLADO + sustituciones GENÉRICAS registradas -> (rel, raw, fuente portada, hechas)."""
        f = Path(f)
        rel = f.relative_to(self.area).as_posix()
        raw = f.read_bytes()
        x = self.inv.get(rel)
        need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "PILA_HISTORICA_NO_AUTENTICADA", "%s/%s" % (self.entrega, rel))
        src, hechas = raw.decode("utf-8"), []
        for a, b in GENERICAS:
            n = src.count(a)
            if n:
                src = src.replace(a, b)
                hechas.append({"original": a, "puerto": b, "veces": n})
        return rel, raw, src, hechas

    def _origen(self, fullname):
        spec = self.find_spec(fullname)
        need(spec is not None, "MODULO_FUERA_DE_LA_ENTREGA", fullname)
        return Path(spec.origin), spec

    def get_code(self, fullname):
        """rem45 (P4-R1-ENTRADA-COMANDO): punto de entrada de runpy.run_module (-m módulo): el MISMO código autenticado y portado que
        exec_module (registrado como «<módulo> (__main__)»); runpy pone NUCLEO_S6 en los globales (init_globals de ejecutar_comando)."""
        f, _ = self._origen(fullname)
        rel, raw, src, hechas = self._portar(f)
        self.registro[fullname + " (__main__)"] = {"archivo": rel, "sha256_historico": sha(raw), "sha256_puerto": sha(src.encode("utf-8")), "sustituciones": hechas,
                                                   "entrada": "runpy.run_module"}
        return compile(src, str(f), "exec")

    def get_source(self, fullname):
        f, _ = self._origen(fullname)
        return self._portar(f)[2]

    def is_package(self, fullname):
        _, spec = self._origen(fullname)
        return spec.submodule_search_locations is not None

    def exec_module(self, module):
        f = Path(module.__spec__.origin)
        rel, raw, src, hechas = self._portar(f)
        module.__dict__.update(NUCLEO_S6=self.nucleo)
        self.registro[module.__name__] = {"archivo": rel, "sha256_historico": sha(raw), "sha256_puerto": sha(src.encode("utf-8")), "sustituciones": hechas}
        exec(compile(src, str(f), "exec"), module.__dict__)
        if module.__name__ == "codigo.demo.nucleo_v" and self.ctx is not None:
            module.Contexto = lambda *a, **k: self.ctx                 # ContextoS6 de la corrida
        self.guarda()

    def instalar(self):
        import paper2b
        need(Path(paper2b.__file__).resolve().parent == self.nucleo, "PAPER2B_NO_ES_EL_NUCLEO_S6", paper2b.__file__)
        need("codigo" not in sys.modules or getattr(sys.modules["codigo"], "__file__", "").startswith(str(self.area)), "OTRO_PAQUETE_CODIGO_CARGADO")
        if self not in sys.meta_path:
            sys.meta_path.insert(0, self)
        self.guarda()
