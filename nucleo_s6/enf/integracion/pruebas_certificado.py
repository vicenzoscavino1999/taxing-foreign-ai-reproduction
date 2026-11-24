"""rem128 — CONTRASTES SINTÉTICOS del certificador de alcance (DIAGNÓSTICO NO PRODUCTIVO). Parten de la clave real d59edf8a (manifiesto
ABL-ENF autenticado) y cambian UNA cosa por caso, para comprobar que el certificador distingue alcanzado / no alcanzado demostrado / no
decidido y nunca promueve un estado no decidido. No evalúa techos ni llama a capture_ceiling/sup_bound.
Casos (regla finita, declarados en DECLARACION_PRUEBAS_DIAGNOSTICAS.json):
  S1 dominio [0, 0.5]² (la curva no corta la caja)        → alcanzado_demostrado en (0.5, 0.5)
  S2 diseño N                                             → no_decidido (FUERA_DEL_ALCANCE_DEL_CERTIFICADO)
  S3 rho = 0.9                                            → no_decidido (FUERA_DEL_ALCANCE_DEL_CERTIFICADO)
  S4 kappa_tilde = 0.9 (H3 falla)                         → no_decidido (HIPOTESIS_NO_DEMOSTRADAS)
  S5 cotas persistidas desplazadas +1 en R                → no_decidido (COTA_PERSISTIDA_INCOMPATIBLE)
  S6 menú d (tau_f ≡ 0)                                   → no_decidido (FUERA_DEL_ALCANCE_DEL_CERTIFICADO)
  S7 la clave real con sus cotas persistidas              → no_alcanzado_demostrado (referencia)
Escribe en exclusiva <salida.json>. Uso: python -B -I pruebas_certificado.py <raiz> <salida.json>"""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

R, S = Path(sys.argv[1]), Path(sys.argv[2])
AQUI = Path(__file__).resolve()
sp = importlib.util.spec_from_file_location("certificado_salto", AQUI.parent / "certificado_salto.py")
CS = importlib.util.module_from_spec(sp)
sp.loader.exec_module(CS)
man_p = R / "tmp/paso4_enforcement_desde_rem125/lote_enf/MANIFIESTO_ABL_ENF.json"
raw = man_p.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "0b27b32abdfb4eaf0db11427a8a8bb93c7d4014c6c7acd1bdbfbe6e32d28b3ad"
cl = json.loads(raw)["ABL-ENF"]["claves_recalculadas"]["d59edf8a9d1461d1"]
COTAS = (8.78074346560998, 8.78074346561024)       # lower_R / upper_R persistidos de T1 (rem127, enf_techos ee766293…)
casos = []


def caso(cid, esperado, prim, diseno, j, tau, cotas):
    c = CS.certificar(prim, diseno, j, tau, cotas)
    ok = c["estado"] == esperado[0] and (esperado[1] is None or c["motivo"] == esperado[1])
    casos.append({"caso": cid, "esperado": list(esperado), "obtenido": [c["estado"], c["motivo"]], "ok": ok,
                  "hipotesis": {k: v.get("ok", v) for k, v in c["hipotesis"].items()}, "punto": c.get("punto"), "testigo_lateral": c.get("testigo_lateral")})


tau05 = dict(cl["tau"], tau_d_upper="0.5", tau_f_upper="0.5")
caso("S1_dominio_sin_curva", ("alcanzado_demostrado", None), cl["clave"], "G", "df", tau05, None)
caso("S2_diseno_N", ("no_decidido", "FUERA_DEL_ALCANCE_DEL_CERTIFICADO"), cl["clave"], "N", "df", cl["tau"], COTAS)
caso("S3_rho_0_9", ("no_decidido", "FUERA_DEL_ALCANCE_DEL_CERTIFICADO"), dict(cl["clave"], rho="0.9"), "G", "df", cl["tau"], COTAS)
caso("S4_kappa_0_9_H3_falla", ("no_decidido", "HIPOTESIS_NO_DEMOSTRADAS"), dict(cl["clave"], kappa_tilde="0.9"), "G", "df", cl["tau"], COTAS)
caso("S5_cotas_incompatibles", ("no_decidido", "COTA_PERSISTIDA_INCOMPATIBLE"), cl["clave"], "G", "df", cl["tau"], (COTAS[0] + 1.0, COTAS[1] + 1.0))
taud = dict(copy.deepcopy(cl["tau"]), tau_f_upper="0")
caso("S6_menu_d", ("no_decidido", "FUERA_DEL_ALCANCE_DEL_CERTIFICADO"), cl["clave"], "G", "d", taud, COTAS)
caso("S7_clave_real", ("no_alcanzado_demostrado", None), cl["clave"], "G", "df", cl["tau"], COTAS)
out = {"kind": "pruebas-certificado-salto-rem128", "estado": "DIAGNOSTICO_NO_PRODUCTIVO", "certificador_sha256": hashlib.sha256((AQUI.parent / "certificado_salto.py").read_bytes()).hexdigest(),
       "casos": casos, "aprobadas": sum(c["ok"] for c in casos), "total": len(casos)}
with S.open("x", encoding="utf-8") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"aprobadas": out["aprobadas"], "total": out["total"], "casos": [(c["caso"], c["ok"], c["obtenido"]) for c in casos]}, ensure_ascii=False, indent=1))
raise SystemExit(0 if out["aprobadas"] == out["total"] else 4)
