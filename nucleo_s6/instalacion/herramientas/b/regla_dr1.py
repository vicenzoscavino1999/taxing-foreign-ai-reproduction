"""DR-1 v2 (rem41) — regla R-SUCESION-S6 PROPUESTA y DESACTIVADA del comparador: solo actúa si una correspondencia la SELLA por el
sha256 de su TEXTO (que incluye el sha256 de sus datos). Sustituye a la v1 de rem40 (59f71674…), que no fijaba las tuplas nuevas por
procedencia y no cubría las definiciones de evidencia que el núcleo S6 cambió (ver review/DECISIONES_DR1_DR2.md, diferencial v1->v2).

Diferencias concretas que cubre (y por qué; pruebas/resultados/dr1_diferencias.json y dr1_nucleos.json):
  - technical.code_sha256: manifiesto de la RAÍZ (reconstruido EXACTO: 037d20d3… antes de s6r39 -> 8dd90dc5… S6); el núcleo que
    CALCULÓ los originales (candidato/src/paper2b de las 12 entregas) es idéntico al de la raíz S6 salvo run.py, rules.py y el nuevo
    aplicabilidad.py, cuyas diferencias son: NA explícita de G (solo con G-NA-1 e INSTRUMENT_NOT_AVAILABLE), validaciones G-NA-1 y los
    TEXTOS de tres definiciones de evidencia (E1–E3 abajo). Valores, métodos y estados de las celdas numéricas: mismo código.
  - technical.contract_sha256: CA2-4 (4d7e676a…) -> G-NA-1 (7bde9f15…): G-NA-1 = CA2-4 + regla NA de G en convergence_result
    (catálogo), G_NA_1.md y nota de enmienda; nada más.
  - technical.configuration_sha256 / method_sha256: dependen SOLO del run_class (12/12 clases recalculadas bajo S6 = originales).
  - hashes derivados por fórmula de esas cargas en CADA lado (structural_key_sha256 = resultado.clave_estructural = H(carga
    estructural); macro_key_sha256 = expected_macro_key_sha256 = H(carga macro)); los ids FRN/MAC/CEL/CEI/NEV ya los normaliza el
    comparador tras validarlos por fórmula.
  - numerical_evidence.definition: SOLO las sustituciones exactas E1–E3 (texto descriptivo del método; la evidencia normalizada,
    su cota, unidad, método y estado se comparan sin regla).
No cubre: ningún valor calculado (C_2, K_comp_1, G, cotas, errores, raíces, inversiones, geometría, veredictos, estados), ni
environment/tolerances (deben ser idénticos), ni otro campo de las cargas, ni national_state_sha256, ni cadenas con forma de hash
fuera de las nombradas, ni tuplas técnicas no listadas en los datos fijados.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DATOS_P = Path(__file__).resolve().parents[2] / "datos/paso4/dr1_tecnicas_admitidas.json"
_RAW = DATOS_P.read_bytes()
DATOS = json.loads(_RAW)
DATOS_SHA256 = hashlib.sha256(_RAW).hexdigest()
CAMPOS_TECNICOS = ("code_sha256", "configuration_sha256", "contract_sha256", "method_sha256")
IGUALES = ("environment_sha256", "tolerances_sha256")
R1_MAX_LEVEL = 6          # RunConfig.r1_max_level: igual en las 12 clases y en S6 (la configuración solo difiere en run_class)
G_ANT = "G = C2 - K1 en el mismo omega: cota = error certificado de C2 + "
G_NUE = "G: NA autenticada o C2 - K1 en el mismo omega; cota numérica si aplica = error certificado de C2 + "
R1_SUF = re.compile(r"; nivel configurado=(\d+), efectivo=(\d+)$")
R1_INC_ANT = re.compile(r"o cajas sin resolver al nivel máximo (\d+); no se publican componentes")
R1_INC_NUE = re.compile(r"o cajas sin resolver; nivel configurado=(\d+), efectivo=(\d+); no se publican componentes")
TEXTO = ("R-SUCESION-S6 v2 (DR-1; propuesta rem41, DESACTIVADA salvo sellado por el sha256 de este texto). Datos fijados: "
         "datos/paso4/dr1_tecnicas_admitidas.json sha256 %s (12 tuplas técnicas originales por procedencia y las tuplas S6 admitidas por "
         "run_class). En la comparación R2/R3 de una unidad ORIGINAL (autoridad histórica, su contrato y su D7 S5) con su reproducción "
         "bajo S6 pueden diferir SOLO: (1) technical.code_sha256, configuration_sha256, contract_sha256 y method_sha256 dentro de "
         "frontier_context.structural_key_payload y lambda_pi_envelope.macro_key_payload, si la técnica del original es EXACTAMENTE una "
         "tupla original admitida, la nueva EXACTAMENTE una tupla S6 admitida, environment_sha256 y tolerances_sha256 son idénticos y la "
         "técnica de ambas cargas de cada lado coincide; (2) national_dependencies[*].manifest_path y manifest_sha256 con "
         "artifact_path y artifact_sha256 idénticos; (3) structural_key_sha256, resultado.clave_estructural, macro_key_sha256 y "
         "expected_macro_key_sha256, solo si en CADA lado son el hash de SU carga; (4) numerical_evidence.definition solo por las "
         "sustituciones E1 (prefijo de la evidencia de G: «%s» -> «%s»), E2 (sufijo de R1 certificado «; nivel configurado=6, "
         "efectivo=k», 0<=k<=6) y E3 (R1 incompleto: «al nivel máximo 6» -> «; nivel configurado=6, efectivo=k»). Todo lo demás de las "
         "cargas, de las tablas y del documento debe ser idéntico o cubierto por otra regla vigente. Nunca cubre valores calculados, "
         "estados, veredictos, evidencia numérica distinta de su texto descriptivo, ni amplía tolerancias.") % (DATOS_SHA256, G_ANT.strip(), G_NUE.strip())
CAMPOS_REGLA = [("frontier_context", "structural_key_payload"), ("frontier_context", "structural_key_sha256"), ("lambda_pi_envelope", "macro_key_payload"),
                ("lambda_pi_envelope", "macro_key_sha256"), ("cell_context", "expected_macro_key_sha256"), ("numerical_evidence", "definition"),
                ("doc", "resultado.clave_estructural")]
IDENT_CUBIERTA = {"expected_macro_key_sha256", "frontera.structural_key_payload", "frontera.structural_key_sha256", "macro.macro_key_sha256",
                  "resultado.clave_estructural"}


def _sin(d, k):
    return {x: v for x, v in (d or {}).items() if x != k}


def _deps(p):
    return [{x: v for x, v in dd.items() if x not in ("manifest_path", "manifest_sha256")} for dd in (p.get("national_dependencies") or [])]


def condiciones(Fo, Fn, do, dn, K) -> dict:
    """Condiciones de la sucesión técnica para UNA unidad (ambos lados ya validados por sus contratos)."""
    mot = []
    try:
        fo, fn = Fo["frontier_context"], Fn["frontier_context"]
        mo, mn = Fo["lambda_pi_envelope"], Fn["lambda_pi_envelope"]
        if not (len(fo) == len(fn) == len(mo) == len(mn) == 1):
            return {"ok": False, "motivos": ["frontera/macro no únicas"]}
        fo, fn, mo, mn = fo[0], fn[0], mo[0], mn[0]
        so, sn, po, pn = fo["structural_key_payload"], fn["structural_key_payload"], mo["macro_key_payload"], mn["macro_key_payload"]
        to, tn = so.get("technical"), sn.get("technical")
        if to != po.get("technical") or tn != pn.get("technical"):
            mot.append("técnica distinta entre las cargas de un mismo lado")
        if to not in [x["technical"] for x in DATOS["originales"]]:
            mot.append("técnica del original no admitida")
        if tn not in [x["technical"] for x in DATOS["nuevas"]]:
            mot.append("técnica nueva no admitida")
        if any((to or {}).get(k) != (tn or {}).get(k) for k in IGUALES):
            mot.append("environment/tolerances distintos")
        if set(to or {}) != set(CAMPOS_TECNICOS + IGUALES) or set(tn or {}) != set(CAMPOS_TECNICOS + IGUALES):
            mot.append("técnica con campos distintos de los fijados")
        if _sin(so, "technical") != _sin(sn, "technical"):
            mot.append("carga estructural distinta fuera de la técnica")
        if _sin(_sin(po, "technical"), "national_dependencies") != _sin(_sin(pn, "technical"), "national_dependencies") or _deps(po) != _deps(pn):
            mot.append("carga macro distinta fuera de la técnica o del manifiesto de dependencias")
        for lado, f, m, F, d in (("original", fo, mo, Fo, do), ("nueva", fn, mn, Fn, dn)):
            if K.H(f["structural_key_payload"]) != f["structural_key_sha256"] or (d.get("resultado") or {}).get("clave_estructural") != f["structural_key_sha256"]:
                mot.append("%s: clave estructural no es el hash de su carga" % lado)
            if K.H(m["macro_key_payload"]) != m["macro_key_sha256"] or F["cell_context"][0]["expected_macro_key_sha256"] != m["macro_key_sha256"]:
                mot.append("%s: clave macro no es el hash de su carga" % lado)
    except (KeyError, TypeError, IndexError) as ex:
        mot.append("estructura inesperada: %s" % ex)
    return {"ok": not mot, "motivos": mot}


def definicion_equivalente(a, b) -> bool:
    """E1–E3: la definición nueva es la antigua con EXACTAMENTE una de las sustituciones de texto del núcleo S6."""
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    if a.startswith(G_ANT) and b.startswith(G_NUE) and a[len(G_ANT):] == b[len(G_NUE):]:
        return True
    m = R1_SUF.search(b)
    if a.startswith("R1 CERTIFICADO: ") and m and b[:m.start()] == a and int(m.group(1)) == R1_MAX_LEVEL and 0 <= int(m.group(2)) <= R1_MAX_LEVEL:
        return True
    ma, mb = R1_INC_ANT.search(a), R1_INC_NUE.search(b)
    if ma and mb and int(ma.group(1)) == int(mb.group(1)) == R1_MAX_LEVEL and 0 <= int(mb.group(2)) <= R1_MAX_LEVEL:
        return a[:ma.start()] == b[:mb.start()] and a[ma.end():] == b[mb.end():]
    return False
