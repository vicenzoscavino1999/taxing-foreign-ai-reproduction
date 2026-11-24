"""rem134 — ENTRADA AUTENTICADA de la finalización lambda (CANDIDATO AISLADO; no incorporado; producción NO habilitada).
Frontera única ante el helper soporte_lambda_demostrado (rem133, función interna, mismos bytes):
  1. el MANIFIESTO de fuentes aceptadas se fija aquí por su sha256 (MANIFIESTO_SHA256): quien llama no puede sustituir a la vez una fuente y su
     hash esperado, porque los hashes esperados viven en un manifiesto que también se autentica;
  2. cada fuente se LEE UNA VEZ, se autentica (sha256 del manifiesto y presencia con el mismo sha256 en su inventario SELLADO, también fijado por
     sha256) y se analizan ESOS MISMOS bytes, sin relectura;
  3. coherencia de contenido mínima: los intervalos λ de la equivalencia coinciden con las envolventes aceptadas autenticadas;
  4. solo se admiten las 14 corridas y el plan del manifiesto (run_id y plan explícitos; cada soporte conserva su corrida);
  5. la SELECCIÓN de filas parte del anexo autenticado: solo lambda_required con estado_es_por_unidad TRUE; las definitivas y las de captura
     quedan intactas; C2 permanece «no_evaluado» (el helper rechaza su promoción).
Capas de rechazo: «ENTRADA_*» (esta frontera) y «SoporteLambdaError» (helper)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

MANIFIESTO_SHA256 = "647744d0ffd26284bf2008d4c1b7bbccabaa5471bbb16a1e039a6321e282e9a1"
MANIFIESTO_RUTA = "tmp/paso4_exp0_lambda_autenticada_desde_rem134/b_lambda/entrada/MANIFIESTO_ENTRADA_LAMBDA.json"


class EntradaError(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo = codigo


def need(t, c, d=""):
    if not t:
        raise EntradaError(c, d)


def _leer(raiz: Path, rel: str) -> bytes:
    """ÚNICO punto de lectura de bytes (las pruebas lo sustituyen para simular archivos alterados en disco)."""
    return (Path(raiz) / rel).read_bytes()


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class EntradaLambda:
    def __init__(self, raiz, manifiesto_ruta: str = MANIFIESTO_RUTA):
        self.raiz = Path(raiz)
        mb = _leer(self.raiz, manifiesto_ruta)
        need(_sha(mb) == MANIFIESTO_SHA256, "ENTRADA_MANIFIESTO_NO_ACEPTADO", _sha(mb)[:16])
        self.man = json.loads(mb)
        need(self.man.get("produccion_habilitada") is False and self.man.get("c2_estado") == "no_evaluado", "ENTRADA_MANIFIESTO_ALCANCE")
        self.bytes, self.inventarios = {}, {}
        for k, f in sorted(self.man["fuentes"].items()):
            b = _leer(self.raiz, f["ruta"])
            need(_sha(b) == f["sha256"], "ENTRADA_FUENTE_ALTERADA", k)
            inv = f["inventario"]
            if inv["ruta"] not in self.inventarios:
                ib = _leer(self.raiz, inv["ruta"])
                need(_sha(ib) == inv["sha256"], "ENTRADA_INVENTARIO_ALTERADO", inv["ruta"])
                self.inventarios[inv["ruta"]] = json.loads(ib)["files"]
            rel = f["ruta"].split("/", 2)[2]
            need(self.inventarios[inv["ruta"]].get(rel, {}).get("sha256") == f["sha256"], "ENTRADA_FUENTE_FUERA_DE_INVENTARIO", k)
            self.bytes[k] = b
        self.eq = json.loads(self.bytes["equivalencia_rem132"])
        self.b1 = json.loads(self.bytes["universo_nacional_b1"])
        self.anexo = json.loads(self.bytes["anexo_t8"])["filas"]
        self.mapa = json.loads(self.bytes["mapa_corridas"])
        ident = json.loads(self.bytes["identidad_plan_rem132"])
        need(sorted(r for r, v in ident["corridas"].items() if v.get("run_id_recalculado") is True) == self.man["corridas"], "ENTRADA_CORRIDAS")
        need({v["plan"]["plan_sha256"] for v in ident["corridas"].values()} == {self.man["plan_sha256"]}, "ENTRADA_PLAN")
        env = {}
        for k in ("envolventes_lote1", "envolventes_lote2"):
            for x in (json.loads(y) for y in self.bytes[k].decode("utf-8").splitlines() if y.strip()):
                if x["variante"] == "con":
                    env[x["conjunto"] if "|" in x["conjunto"] else x["conjunto"] + "|" + x["pais"]] = x
        for c in self.man["claves"]:
            e, q = env.get(c), self.eq["por_clave"].get(c, {}).get("envolvente") or {}
            need(e is not None and Fraction(q.get("lambda_min", "nan")) == Fraction(e["lambda_min"]) and Fraction(q.get("lambda_max", "nan")) == Fraction(e["lambda_max"]),
                 "ENTRADA_INTERVALO_DISTINTO_DE_LA_ENVOLVENTE", c)
        need(sorted(self.eq["por_clave"]) == self.man["claves"] and sorted(self.b1["claves"]) == self.man["claves"], "ENTRADA_CLAVES")
        # helper interno: sus bytes son la fuente autenticada «helper_rem133»
        spec = importlib.util.spec_from_loader("soporte_lambda_demostrado_rem133", loader=None)
        self.SL = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.SL
        exec(compile(self.bytes["helper_rem133"], "soporte_lambda_demostrado.py", "exec"), self.SL.__dict__)
        self.fuentes = {"equivalencia_rem132": self.man["fuentes"]["equivalencia_rem132"]["sha256"],
                        "universo_nacional_b1": self.man["fuentes"]["universo_nacional_b1"]["sha256"]}
        self.docs = {r: self.SL.construir(self.eq, self.b1, run_id=r, plan_sha256=self.man["plan_sha256"], fuentes=self.fuentes) for r in self.man["corridas"]}
        self.run_de = {e: r for r, v in self.mapa.items() for e in v["entregas"]}

    def cerrar(self, run_id, filas, finalizar):
        """Filas del ANEXO autenticado: solo lambda_required con estado_es_por_unidad TRUE (se exige la marca, no se deduce del estado)."""
        need(run_id in self.docs, "ENTRADA_CORRIDA_NO_ADMITIDA", run_id)
        rows = []
        for f in filas:
            need(f.get("estado_es_por_unidad") is True, "ENTRADA_FILA_NO_PROVISIONAL", f.get("cell_id"))
            need(f.get("inversion_id") == "lambda_required", "ENTRADA_FILA_NO_LAMBDA", f.get("inversion_id"))
            need(self.run_de.get(f["ref"].split("/", 1)[0]) == run_id, "ENTRADA_FILA_DE_OTRA_CORRIDA", f.get("cell_id"))
            rows.append(dict({k: f[k] for k in ("inversion_id", "result_status", "outside_support", "computation_status")}, _fin=f["fin_por_unidad"]))
        return self.SL.cerrar_lambda(rows, self.docs[run_id], finalizar, self.eq, self.b1, run_id=run_id, plan_sha256=self.man["plan_sha256"], fuentes=self.fuentes)

    def vista(self, finalizar):
        por_run = {}
        for i, f in enumerate(self.anexo):
            por_run.setdefault(self.run_de[f["ref"].split("/", 1)[0]], []).append(i)
        out = [None] * len(self.anexo)
        for run, idx in sorted(por_run.items()):
            lam = [i for i in idx if self.anexo[i]["estado_es_por_unidad"] is True and self.anexo[i]["inversion_id"] == "lambda_required"]
            for i, o in zip(lam, self.cerrar(run, [self.anexo[i] for i in lam], finalizar)):
                out[i] = {"tipo": "lambda_candidato_por_demostracion", "estado": o["result_status"], "regla": "unidades._finalize", "soporte": self.docs[run]["sha256"]}
            for i in idx:
                f = self.anexo[i]
                if out[i] is None:
                    out[i] = ({"tipo": "definitivo_almacenado", "estado": f["result_status"], "regla": None, "soporte": None} if not f["estado_es_por_unidad"]
                              else {"tipo": "captura_pendiente_sin_soporte_C2", "estado": "pendiente_soporte_global", "regla": None, "soporte": None})
                out[i].update(fila=i, run_id=run, cell_id=f["cell_id"], inversion_id=f["inversion_id"], estado_anexo=f["result_status"],
                              cambio=out[i]["tipo"] == "lambda_candidato_por_demostracion" and out[i]["estado"] != f["result_status"])
        return out
