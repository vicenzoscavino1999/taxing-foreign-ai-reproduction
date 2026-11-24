"""rem121 — CONCILIACIÓN DERIVADA de los 391 pares G/N (solo lectura; sin ciencia): 383 contrapartes E4 (producto validado de REM121_E4)
con su malla de origen del producto L1-ELAST ACEPTADO de rem120 (007095a9…, registro parcial rem121), más los 8 pares existentes del
manifiesto E4 (ambas mallas en el producto aceptado). Por par: vínculo exacto (misma clave estructural, mismo instrumento, mismo dominio τ,
diseño distinto), mismos puntos, campos comunes y diferentes, topologías, kinks, regímenes y nulos legítimos; origen C0 o histórico (las 70
filas del lote 1 enriquecidas). No fuerza igualdad entre G y N, no trata un kink como error ni un nulo como cero. Escribe en exclusiva <salida.json>.
Uso: python -B -I -X utf8 conciliacion_e4_rem121.py <raiz> <area> <salida.json>"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

R, A, SAL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
T = R / "tmp"
HF = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
jl = lambda p: [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]  # noqa: E731
L = T / "paso4_suplemento_topologia_desde_rem119/lote2"
E4 = A / "lote2e4_REM121_E4/L1-ELAST"
ACC = T / "paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-ELAST/salida"
res4 = json.loads((E4 / "resultado.json").read_bytes())
p4 = E4 / "salida/frontier_result.jsonl"
assert HF(p4) == next(p["sha256"] for p in res4["productos"] if p["archivo"] == "frontier_result.jsonl")
assert HF(ACC / "frontier_result.jsonl") == "007095a94b7d1fce18aea6214c56c45b370e9a6eb5b0e415da6a0cc09a26ea8c"
assert HF(ACC / "suplemento_procedencia.jsonl") == "d6a12af3818993288d8b1f1cbbb87eb7cb64bf2ee25492ae4ff1d95cc2e55b39"
m2 = json.loads((L / "LOTE2_MANIFIESTO.json").read_bytes())["L1-ELAST"]
m4 = json.loads((L / "LOTE2E4_MANIFIESTO.json").read_bytes())["L1-ELAST"]
assert HF(L / "LOTE2E4_MANIFIESTO.json") == "d430b39db2cea7801cdcf8b55f0455063270d58f5aebea57776241fcde04b4af"
por_fid2 = {v["frontier_id"]: (k, v) for k, v in m2["fronteras"].items()}
historicas = {q["frontier_id"] for q in jl(ACC / "suplemento_procedencia.jsonl")}
filas = {}
for r in jl(ACC / "frontier_result.jsonl") + jl(p4):
    filas.setdefault(r["frontier_id"], []).append(r)
COMUNES = ("tau_d", "tau_f", "regime")
NUM = ("B_d", "B_f", "R", "B_pot", "CS", "eps_dd", "eps_df", "eps_fd", "eps_ff", "s_P")
BASE = {"eps_dd": "B_d", "eps_df": "B_d", "eps_fd": "B_f", "eps_ff": "B_f"}


def nulos(r):
    return sorted(c for c in BASE if r.get(c) is None)


def par(id_par, fg, fn, entrada_g, entrada_n, origen):
    (kg, vg), (kn, vn) = entrada_g, entrada_n
    dg, jg = kg.split("|")[:2]
    dn, jn = kn.split("|")[:2]
    vinculo = {"misma_clave": vg["clave_estructural"] == vn["clave_estructural"], "mismo_instrumento": jg == jn, "mismo_dominio_tau": vg["dominio_tau"] == vn["dominio_tau"],
               "disenos": sorted([dg, dn])}
    rg = {(r["point_id"], r["side"]): r for r in filas.get(fg, [])}
    rn = {(r["point_id"], r["side"]): r for r in filas.get(fn, [])}
    pg = {k[0] for k in rg if k[1] == "point"}
    pn = {k[0] for k in rn if k[1] == "point"}
    out = {"par": id_par, "G": fg, "N": fn, "instrumento": jg, "origen": origen, "vinculo": vinculo,
           "puntos": len(pg), "mismos_puntos": pg == pn and len(pg) > 0}
    if not (all(v for k, v in vinculo.items() if k != "disenos") and vinculo["disenos"] == ["G", "N"] and out["mismos_puntos"]):
        out["conciliado"] = False
        return out
    comunes_ok, topo_igual, difiere = True, 0, Counter()
    kinks = {"G": 0, "N": 0}
    nul = {"G": 0, "N": 0}
    for p in sorted(pg):
        a, b = rg[(p, "point")], rn[(p, "point")]
        comunes_ok = comunes_ok and all(a[c] == b[c] for c in COMUNES)
        topo_igual += a.get("topology") == b.get("topology")
        for c in NUM:
            if a.get(c) != b.get(c):
                difiere[c] += 1
        kinks["G"] += a["kink_adjacent"] is True
        kinks["N"] += b["kink_adjacent"] is True
        nul["G"] += bool(nulos(a))
        nul["N"] += bool(nulos(b))
    out.update(campos_comunes_identicos=comunes_ok, topologia_igual_en_puntos=topo_igual, campos_con_diferencias=dict(difiere),
               puntos_con_kink=kinks, puntos_con_algun_nulo=nul, conciliado=comunes_ok)
    return out


pares = []
for k4, v4 in m4["fronteras"].items():
    ko = v4["origen"]["malla_de_origen"]
    vo = m2["fronteras"][ko]
    d4 = k4.split("|")[0]
    g, n = ((v4["frontier_id"], vo["frontier_id"]) if d4 == "G" else (vo["frontier_id"], v4["frontier_id"]))
    eg, en = (((k4, v4), (ko, vo)) if d4 == "G" else ((ko, vo), (k4, v4)))
    pares.append(par("E4:" + v4["frontier_id"], g, n, eg, en, "histórico lote 1 + topología C0" if vo["frontier_id"] in historicas else "C0 (rem120 aceptado)"))
for i, pe in enumerate(m4["pares_existentes"]):
    pares.append(par("existente:%d" % i, pe["G"], pe["N"], por_fid2[pe["G"]], por_fid2[pe["N"]],
                     "existente: G %s / N %s" % ("histórico" if pe["G"] in historicas else "C0", "histórico" if pe["N"] in historicas else "C0")))
pend = [p for p in pares if not p["conciliado"]]
out = {"kind": "conciliacion-e4-rem121", "producto_e4_sha256": HF(p4), "producto_elast_aceptado_sha256": HF(ACC / "frontier_result.jsonl"),
       "pares": len(pares), "contrapartes_e4": sum(1 for p in pares if p["par"].startswith("E4:")), "existentes": sum(1 for p in pares if p["par"].startswith("existente")),
       "conciliados": len(pares) - len(pend), "pendientes": [{k: p[k] for k in ("par", "G", "N", "vinculo", "mismos_puntos")} for p in pend],
       "puntos_contraparte_total": sum(p["puntos"] for p in pares if p["par"].startswith("E4:")),
       "origenes": dict(Counter(p["origen"] for p in pares)), "por_instrumento": dict(Counter(p["instrumento"] for p in pares)),
       "topologia_igual_en_todos_los_puntos": sum(1 for p in pares if p.get("topologia_igual_en_puntos") == p["puntos"]),
       "pares_con_kink": {"G": sum(1 for p in pares if (p.get("puntos_con_kink") or {}).get("G")), "N": sum(1 for p in pares if (p.get("puntos_con_kink") or {}).get("N"))},
       "universo_padre_sin_cambio": 572, "detalle": pares}
with SAL.open("x", encoding="utf-8") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "detalle"}, ensure_ascii=False, indent=1))
