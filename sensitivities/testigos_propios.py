"""Sensibilidad en los testigos favorables propios de los menús d y f (columnas «Domestic only» y «Withholding only» de la
Tabla 3 del artículo), con la regla E11 y topes bajos.

Copia adaptada para el paquete público de comparacion_menus/testigos_propios.py (2026-11-22). Cambios declarados:
- el núcleo E11 es nucleo_s6/instalacion/src del paquete (verificado por run_sensitivities.py contra
  manifests/kernel_SHA256SUMS.txt), en lugar de la copia del piloto;
- las filas de cada testigo se leen de inputs/ y se autentican por su sha256, el de la comparación aceptada de la corrida
  completa del Paso 3, en lugar de leer las salidas de esa corrida (que no se distribuyen);
- las funciones sha, bounds y measured_ceiling se copian de comparacion_menus/comparar.py, sin cambios.
La elección del testigo (máximo de sup_C2 en el anexo público de la tabla de afirmaciones y, en el empate, el primer
identificador), el control del techo base y los certificados son los mismos.

Uso: python -B -I testigos_propios.py <salida.json>
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
package = here.parent
sys.path.insert(0, str(here))
import calculo as CA  # noqa: E402  (ENTORNO y ruta del núcleo E11)
sys.path.insert(0, str(CA.REGLAS["E11"]))
from paper2b import model, run  # noqa: E402

# sha256 de las filas de cada testigo propio: «nueva.filas_sha256» de su comparación aceptada (corrida completa del Paso 3)
FILAS = {
    "006ff4b8f97fe92d199d881fc379e836e9bb921a2478a12178baad3996846613": "33d71fc638371ba60e9c6362e5afe28ecdf7c90a9fef418be22deceb9faa3190",
    "03beead43d6bbaf874ccb9156340480a1f090d7bebf8cd3b4d5ed3f3ad8aab80": "8c9e7f70f23f992dd4ab6666320381cf70859d78c3412ccec03e318961949a09",
    "00aa08825b83610dd8078d543c55cd55adb9cdbd1c4cb32734963a8a585c8af0": "e63c6a7e8dbfe08caf5dd9861177919e340fd1b43bd15a5b8563e776cf98326a",
    "00b2ae57b20eb687c9f330d40e441cb11b49cb4e9e474e00ef472d79abe67341": "efdc522a99fac412ff9b75f5b289e054d049d00531332223dbea58f2d17569aa",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(value, error):
    if not (math.isfinite(value) and math.isfinite(error) and error >= 0):
        raise ValueError("Techo o error no admisible")
    return [math.nextafter(value - error, -math.inf), math.nextafter(value + error, math.inf)]


def measured_ceiling(model, state, config, design, menu, domestic, foreign):
    start = time.perf_counter()
    result = model.capture_ceiling(state, design, menu, domestic, foreign, True, config.sup)
    elapsed = time.perf_counter() - start
    s = result.sup
    if not (result.status == "complete" and s.error_kind == "certified_bound"
            and 0 <= result.numerical_error <= config.sup.tol_converge):
        raise ValueError(f"Certificación insuficiente: {design} {menu} {result.reason}")
    if not (0 <= s.tau_d <= domestic and 0 <= s.tau_f <= foreign):
        raise ValueError("Tasas fuera del dominio del menú")
    return {"menu": menu, "topes_activos": [domestic, foreign], "C2": result.C2,
            "error": result.numerical_error, "intervalo": bounds(result.C2, result.numerical_error),
            "tasas": [s.tau_d, s.tau_f], "estado": result.status, "tipo_error": s.error_kind,
            "alcanzado": s.attained, "segundos": elapsed}


def parameters(rows):
    payload = rows["frontier_context"][0]["structural_key_payload"]
    return {v["parameter_id"]: float(v["value"]) for v in payload["values"]}


def calculate():
    if any(os.environ.get(k) != v for k, v in CA.ENTORNO.items()):
        raise ValueError("Se requiere el entorno numérico del piloto")
    if not str(Path(run.__file__).resolve()).startswith(str(CA.REGLAS["E11"].resolve())):
        raise ValueError("paper2b cargado desde otra ruta: %s" % run.__file__)
    annex = package / "datos/fam13/s1/publico/T7_anexo.jsonl"
    claims = [json.loads(line) for line in annex.read_bytes().splitlines()]
    originals = package / "referencias/fam01/originales"
    config = run.RunConfig()
    provider = run.provider_for(config)
    if not provider.certified:
        raise ValueError("Proveedor sin garantía")
    results = {"anexo_sha256": sha(annex), "incidencia": "E11", "testigos": []}
    for design in ("G", "N"):
        for menu in ("d", "f"):
            subset = [r for r in claims if r["diseno"] == design and r["j"] == menu
                      and r.get("sup_C2") is not None]
            high = max(r["sup_C2"] for r in subset)
            tied = sorted({r["testigo_sup"] for r in subset if r["sup_C2"] == high})
            witness = tied[0]
            source = here / "inputs" / (witness + "_filas.json")
            if FILAS.get(witness) is None or sha(source) != FILAS[witness]:
                raise ValueError("Las filas del testigo no son las de su comparación aceptada")
            rows = json.loads(source.read_bytes())
            params = parameters(rows)
            for uid in tied:
                original_rows = json.loads((originals / (uid + "_filas.json")).read_bytes())
                if parameters(original_rows) != params:
                    raise ValueError("Más de un punto estructural en el empate")
            base = rows["capture_ceiling_result"][0]
            payload = rows["frontier_context"][0]["structural_key_payload"]
            state = provider.state(params)
            control = model.revenue(state, base["tau_d_at_sup"], base["tau_f_at_sup"], design) / state.B_pot
            if ((payload["design_v"], payload["instrument_j"]) != (design, menu)
                    or base["computation_status"] != "complete" or control != base["C_2"] or control != high):
                raise ValueError("El control base no coincide con el techo base (Tabla 4 del artículo) y sus filas")
            caps = [(0.35, 0.0)] if menu == "d" else [(0.0, 0.15), (0.0, 0.30)]
            certs = [measured_ceiling(provider, state, config, design, menu, d, f) for d, f in caps]
            results["testigos"].append({"diseno": design, "menu": menu, "testigo": witness,
                "unidades_empatadas": len(tied), "parametros": params, "C2_base": control,
                "filas_sha256": sha(source), "certificados": certs})
    return results


if __name__ == "__main__":
    out = Path(sys.argv[1])
    data = calculate()
    with out.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
