#!/usr/bin/env python3
"""Construcción determinista de D-2 desde UN_SNA_MAIN adquirido.

La frontera de este módulo termina en ``labor_income_shares``. No produce
insumos D-3--D-8 ni objetos económicos del modelo.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, getcontext
from functools import reduce
from math import gcd
from pathlib import Path
from typing import Iterable, Mapping

from openpyxl import load_workbook


getcontext().prec = 60

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = MODULE_DIR / "output"
ACQUISITION_MANIFEST = ROOT / "fase2_datos/acquisition_manifest.csv"
SOURCE_CATALOG = ROOT / "fase2_datos/source_catalog/source_catalog.csv"
TEST_FILE = MODULE_DIR / "test_d2.py"
FREEZE_MANIFEST = ROOT / "fase6_planes/freeze_plans_manifest.json"

COUNTRIES = ("CHL", "COL", "MEX", "PER")
COUNTRY_NAMES = {
    "CHL": "Chile",
    "COL": "Colombia",
    "MEX": "Mexico",
    "PER": "Peru",
}
SENSITIVITY_START = 2015
SOURCE_ID = "UN_SNA_MAIN"
PRECISION_SOURCE_ID = "INEGI_CSI_2023_D2_PRECISION"
MI_STATE = "D2_NO_PARTITION"
SCHEMA_COLUMNS = (
    "country_id",
    "observation_year",
    "source_snapshot_id",
    "source_vintage",
    "coe_gdp",
    "gos_mi_gdp",
    "taxes_net_gdp",
    "gdp_market_prices",
    "identity_residual",
    "precision_basis",
    "precision_source_id",
    "precision_half_width_ncu",
    "rounding_consistency_status",
    "s_L_bar",
    "mi_partition_status",
    "source_id",
    "retrieved_at",
)

# Fotografía autorizada al cierre de D-1. Se verifica antes de interpretar
# acquisition_manifest o abrir un payload.
D1_SURFACE_HASHES = {
    "fase2_datos/data_decision_manifest.md":
        "3488304e401b31b43f23468ecf35073390c49ec020c2d107b3cdfbe52360f1b1",
    "fase2_datos/acquisition_manifest.csv":
        "b2caad587d20d86893a951622543f58c85ddecc759bd3ee30be143ac1d9da3fb",
    "fase2_datos/adquisicion/matriz_trabajo.csv":
        "6f626a039b9f7ee824a6da949dab2804f9d6fc5f6c8681326aa0622dd8fc9339",
    "fase2_datos/adquisicion/bitacora_adquisicion.jsonl":
        "d443c86677e6dad4b0b7af7ef3fe3d6f81b46dda50ac8e7b824972e8af7e3b5c",
    "fase2_datos/adquisicion/bitacora_ancla.json":
        "21c7df0e3385db38de1dd87500484292249b71d1050b638ca1e14b4a0c6ceaaf",
    "fase2_datos/source_catalog/source_catalog.csv":
        "aebcc1562ad7029db010be65136b584f816a6210c9fa66566587c7d24137b6dd",
}

TABLE_HEADER = (
    "Country or Area",
    "SNA93 Table Code",
    "Sub Group",
    "Item",
    "SNA93 Item Code",
    "Year",
    "Series",
    "Currency",
    "SNA System",
    "Fiscal Year Type",
    "Value",
    "Value Footnotes",
    "Value Footnotes",
)
GEN_RESOURCES = "II.1.1 Generation of income account - Resources"
GEN_USES = "II.1.1 Generation of income account - Uses"
ITEMS = {
    "B.1*g": ("GROSS DOMESTIC PRODUCT", GEN_RESOURCES),
    "D.1": ("Compensation of employees", GEN_USES),
    "D.2-D.3": ("Taxes on production and imports, less Subsidies", GEN_USES),
    "B.2g": ("OPERATING SURPLUS, GROSS", GEN_USES),
    "B.3g": ("MIXED INCOME, GROSS", GEN_USES),
}


class D2Error(RuntimeError):
    """Fallo cerrado de una compuerta D-2."""


@dataclass(frozen=True)
class Acquisition:
    country: str
    raw_path: Path
    raw_rel: str
    file_hash: str
    retrieved_at: str
    vintage_actual: str


@dataclass(frozen=True)
class Panel:
    country: str
    values: Mapping[int, Mapping[str, Decimal]]
    raw_text: Mapping[int, Mapping[str, str]]
    quanta: Mapping[str, Decimal]
    currency: str


@dataclass(frozen=True)
class Observation:
    country: str
    year: int
    coe: Decimal
    gos_mi: Decimal
    taxes_net: Decimal
    gdp_market: Decimal
    residual_level: Decimal
    tolerance_level: Decimal
    method: str
    precision_quanta: Mapping[str, Decimal]
    precision_basis: str
    rounding_consistency_status: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: object) -> bytes:
    return (
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    ).encode("utf-8")


def parse_decimal(text: str, label: str) -> Decimal:
    if text is None or str(text).strip() == "":
        raise D2Error(f"{label}: valor vacío")
    try:
        value = Decimal(str(text).strip())
    except InvalidOperation as exc:
        raise D2Error(f"{label}: decimal inválido {text!r}") from exc
    if not value.is_finite():
        raise D2Error(f"{label}: NaN o infinito prohibido")
    return value


def decimal_text(value: Decimal, places: int | None = None) -> str:
    if not value.is_finite():
        raise D2Error("serialización de NaN o infinito prohibida")
    if value == 0:
        return "0" if places is None else "0." + "0" * places
    if places is not None:
        quantum = Decimal(1).scaleb(-places)
        value = value.quantize(quantum)
        if value == 0:
            value = abs(value)
        return format(value, f".{places}f")
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def implied_quantum(values: Iterable[Decimal]) -> Decimal:
    """Diagnóstico aritmético MCD; nunca mide precisión ni abre un gate.

    Para una serie que publica millones convertidos a moneda corriente, por
    ejemplo, todos sus valores quedan en un retículo de un millón. La regla no
    usa el residuo contable y por ello no puede escoger una tolerancia para
    hacer cerrar la identidad.
    """
    vals = [v for v in values if v != 0]
    if not vals:
        raise D2Error("no se puede derivar precisión de una serie vacía")
    min_exp = min(min(v.as_tuple().exponent, 0) for v in vals)
    scale = Decimal(10) ** (-min_exp)
    ints = []
    for value in vals:
        scaled = value * scale
        if scaled != scaled.to_integral_value():
            raise D2Error("la escala decimal no produjo enteros")
        ints.append(abs(int(scaled)))
    grid = reduce(gcd, ints)
    if grid <= 0:
        raise D2Error("retículo de precisión no positivo")
    return Decimal(grid) / scale


def _safe_repo_path(raw_rel: str) -> Path:
    path = (ROOT / raw_rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise D2Error(f"raw_path escapa del repositorio: {raw_rel}") from exc
    return path


def verify_d1_surfaces(expected: Mapping[str, str] = D1_SURFACE_HASHES) -> dict[str, str]:
    observed = {}
    for rel, wanted in expected.items():
        path = ROOT / rel
        if not path.is_file():
            raise D2Error(f"superficie D-1 ausente: {rel}")
        got = sha256_file(path)
        if got != wanted:
            raise D2Error(f"hash D-1 alterado antes de escribir: {rel}: {got}")
        observed[rel] = got
    return observed


def read_acquisitions() -> dict[str, Acquisition]:
    with ACQUISITION_MANIFEST.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 95:
        raise D2Error(f"acquisition_manifest: se esperaban 95 filas, hay {len(rows)}")
    selected = [r for r in rows if r["dataset_id"] == SOURCE_ID]
    if sorted(r["country"] for r in selected) != list(COUNTRIES):
        raise D2Error("UN_SNA_MAIN no contiene exactamente CHL/COL/MEX/PER")
    result = {}
    for row in selected:
        country = row["country"]
        if row["access_result"] != "obtenido":
            raise D2Error(f"{country}: UN_SNA_MAIN no está obtenido")
        raw_rel = row["raw_path"]
        path = _safe_repo_path(raw_rel)
        if not path.is_file():
            raise D2Error(f"{country}: payload ausente: {raw_rel}")
        got = sha256_file(path)
        if got != row["file_hash"]:
            raise D2Error(f"{country}: payload no coincide con su pin: {got}")
        if not row["retrieved_at"]:
            raise D2Error(f"{country}: retrieved_at ausente (D12)")
        result[country] = Acquisition(
            country=country,
            raw_path=path,
            raw_rel=raw_rel,
            file_hash=got,
            retrieved_at=row["retrieved_at"],
            vintage_actual=row["vintage_actual"],
        )
    return result


def read_precision_acquisition() -> Acquisition:
    with ACQUISITION_MANIFEST.open("r", encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["dataset_id"] == PRECISION_SOURCE_ID]
    if len(rows) != 1 or rows[0]["country"] != "MEX":
        raise D2Error("fuente de precisión INEGI debe tener una fila MEX")
    row = rows[0]
    if row["access_result"] != "obtenido":
        raise D2Error("fuente de precisión INEGI no está obtenida")
    path = _safe_repo_path(row["raw_path"])
    if not path.is_file() or sha256_file(path) != row["file_hash"]:
        raise D2Error("payload INEGI ausente o distinto de su pin")
    return Acquisition(
        "MEX", path, row["raw_path"], row["file_hash"],
        row["retrieved_at"], row["vintage_actual"]
    )


def _norm(text: str) -> str:
    base = unicodedata.normalize("NFKD", text)
    ascii_ = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", ascii_.lower()).strip()


def parse_inegi_precision(path: Path) -> dict[str, Decimal]:
    """El parser extrae los valores de los bytes autenticados y los valida
    contra el contrato predeclarado; las constantes no sustituyen la
    extracción ni generan la salida.
    """
    try:
        import fitz
        with fitz.open(path) as doc:
            text = "\n".join(page.get_text() for page in doc)
    except Exception as exc:
        raise D2Error(f"PDF INEGI ilegible: {exc}") from exc
    field = _norm(text)
    required = (
        "cuentas por sectores institucionales csi 2023",
        "determinacion del ingreso nacional disponible bruto",
        "millones de pesos corrientes",
        "la suma de los parciales puede no coincidir con el total debido al redondeo",
    )
    missing = [x for x in required if x not in field]
    if missing:
        raise D2Error(f"PDF INEGI no demuestra precisión: {missing}")
    table_match = re.search(
        r"Cuadro 2\s+Determinaci[oó]n del ingreso nacional disponible bruto"
        r"(?P<table>.*?)Remuneraciones netas con el exterior",
        text, flags=re.DOTALL,
    )
    if not table_match:
        raise D2Error("PDF INEGI no contiene el cuadro 2 autenticado")
    table = table_match.group("table")
    contract = {
        "gdp": (r"\bPIB\b", Decimal(31855566)),
        "compensation": (r"\bRemuneraciones\b", Decimal(9076368)),
        "gross_operating_surplus": (
            r"\bExcedente bruto de operaci[oó]n\b", Decimal(13618795)
        ),
        "gross_mixed_income": (
            r"\bIngreso mixto bruto\b", Decimal(7020820)
        ),
        "net_taxes_production_imports": (
            r"\bImpuestos sobre la producci[oó]n y las\s+importaciones netos de subsidios\b",
            Decimal(2139584),
        ),
    }
    extracted: dict[str, Decimal] = {}
    for name, (label, expected) in contract.items():
        match = re.search(
            label + r"\s+(?P<value>\d{1,3}(?:[ ,]\d{3}){2})",
            table, flags=re.DOTALL,
        )
        if not match:
            raise D2Error(f"PDF INEGI: concepto o valor ausente: {name}")
        observed = Decimal(match.group("value").replace(" ", "").replace(",", ""))
        if observed != expected:
            raise D2Error(
                f"PDF INEGI: valor alterado para {name}: {observed} != {expected}"
            )
        extracted[name] = observed
    return extracted


def bind_mexico_precision(
    obs: Observation, panel: Panel, ama: Mapping[int, Decimal],
    published_millions: Mapping[str, Decimal]
) -> tuple[Observation, dict[str, object]]:
    if obs.country != "MEX" or obs.year != 2023:
        raise D2Error("la evidencia INEGI sólo liga MEX/2023")
    vals = panel.values[obs.year]
    un_ncu = {
        "gdp": ama[obs.year],
        "compensation": vals["D.1"],
        "gross_operating_surplus": vals["B.2g"],
        "gross_mixed_income": vals["B.3g"],
        "net_taxes_production_imports": vals["D.2-D.3"],
    }
    half_million = Decimal("0.5")
    differences = {}
    for name, ncu in un_ncu.items():
        difference = ncu / Decimal(1_000_000) - published_millions[name]
        differences[name] = difference
        if abs(difference) > half_million:
            raise D2Error(
                f"MEX/2023 {name}: UN fuera del intervalo INEGI ±0.5 millones"
            )
    # También la línea B.1*g usada debe ligar al mismo PIB publicado.
    table_difference = (
        vals["B.1*g"] / Decimal(1_000_000) - published_millions["gdp"]
    )
    if abs(table_difference) > half_million:
        raise D2Error("MEX/2023 B.1*g fuera del intervalo INEGI")
    tolerance = half_million * Decimal(5) * Decimal(1_000_000)
    validate_identity(obs.residual_level, tolerance)
    bound = replace(
        obs, tolerance_level=tolerance,
        precision_basis="source_declared_rounding_interval",
        rounding_consistency_status="PASS",
    )
    return bound, {
        "unit": "millions_of_current_pesos",
        "component_half_width_millions": "0.5",
        "tolerance_level_ncu": decimal_text(tolerance),
        "residual_level_ncu": decimal_text(obs.residual_level),
        "un_minus_inegi_millions": {
            k: decimal_text(v) for k, v in differences.items()
        },
        "table_gdp_minus_inegi_millions": decimal_text(table_difference),
    }


def validate_catalog_contract() -> dict[str, str]:
    with SOURCE_CATALOG.open("r", encoding="utf-8", newline="") as fh:
        catalog = list(csv.DictReader(fh))
    rows = [r for r in catalog if r["dataset_id"] == SOURCE_ID]
    by_country = {r["country"]: r for r in rows}
    if sorted(by_country) != list(COUNTRIES):
        raise D2Error("catálogo UN_SNA_MAIN incompleto")
    expected = {
        "denominator": "PIB a precios de mercado",
        "universe": "economia total",
        "horizon": "anual",
        "unit": "moneda nacional corriente",
    }
    for country, row in by_country.items():
        for field, wanted in expected.items():
            if row.get(field, "") != wanted:
                raise D2Error(f"{country}: {field} incompatible o ausente (D2)")
        if row["target_kind"] != "observation_row" or row["target_id"] != "a":
            raise D2Error(f"{country}: contrato de objetivo incorrecto")
    precision = [r for r in catalog if r["dataset_id"] == PRECISION_SOURCE_ID]
    if len(precision) != 1 or precision[0]["country"] != "MEX":
        raise D2Error("catálogo de precisión INEGI no es una fila MEX única")
    if (precision[0]["target_kind"], precision[0]["target_id"],
            precision[0]["priority"]) != ("observation_row", "a", "secundaria"):
        raise D2Error("contrato auxiliar INEGI incompatible con la fila (a)")
    return {
        **expected,
        "precision_source_id": PRECISION_SOURCE_ID,
        "precision_country": "MEX",
    }


def _validate_member_hash(name: str, data: bytes, members: Mapping[str, Mapping[str, object]]) -> None:
    if name not in members:
        raise D2Error(f"bundle_manifest no autentica {name}")
    row = members[name]
    if sha256_bytes(data) != row.get("sha256") or len(data) != row.get("size_bytes"):
        raise D2Error(f"miembro alterado dentro del bundle: {name}")


def read_bundle(path: Path) -> tuple[dict[str, bytes], dict[str, Mapping[str, object]]]:
    try:
        with tarfile.open(path, "r") as tf:
            names = [m.name for m in tf.getmembers() if m.isfile()]
            if "bundle_manifest.json" not in names:
                raise D2Error("bundle sin bundle_manifest.json")
            manifest = json.loads(tf.extractfile("bundle_manifest.json").read())
            members = {r["name"]: r for r in manifest["files"]}
            blobs = {}
            for name in members:
                if name not in names:
                    raise D2Error(f"bundle sin miembro declarado: {name}")
                blob = tf.extractfile(name).read()
                _validate_member_hash(name, blob, members)
                blobs[name] = blob
    except (tarfile.TarError, KeyError, json.JSONDecodeError) as exc:
        raise D2Error(f"bundle UN_SNA_MAIN inválido: {exc}") from exc
    return blobs, members


def unzip_single_csv(blob: bytes, label: str) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            files = [n for n in zf.namelist() if not n.endswith("/")]
            if len(files) != 1 or not files[0].lower().endswith(".csv"):
                raise D2Error(f"{label}: se exige un único CSV")
            return zf.read(files[0])
    except zipfile.BadZipFile as exc:
        raise D2Error(f"{label}: ZIP inválido") from exc


def parse_table_csv(blob: bytes, country: str) -> Panel:
    if blob.startswith(b"\xef\xbb\xbf"):
        text = blob[3:].decode("utf-8", errors="strict")
    else:
        text = blob.decode("utf-8", errors="strict")
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header = tuple(next(reader))
    except StopIteration as exc:
        raise D2Error(f"{country}: CSV vacío") from exc
    if header != TABLE_HEADER:
        raise D2Error(f"{country}: esquema físico de tabla 4.1 inesperado")
    values: dict[int, dict[str, Decimal]] = {}
    raw_text: dict[int, dict[str, str]] = {}
    currencies: set[str] = set()
    expected_name = COUNTRY_NAMES[country]
    for row in reader:
        if not row or all(cell == "" for cell in row):
            continue
        if tuple(row) == ("footnote_SeqID", "Footnote"):
            break
        if len(row) != len(TABLE_HEADER):
            raise D2Error(f"{country}: fila con {len(row)} columnas")
        (area, table, subgroup, item, code, year_s, series, currency,
         sna, fiscal, value_s, _foot1, _foot2) = row
        if area != expected_name or table != "4.1" or series != "1000" or sna != "2008":
            continue
        if fiscal != "Western calendar year" or code not in ITEMS:
            continue
        wanted_item, wanted_subgroup = ITEMS[code]
        if subgroup != wanted_subgroup:
            continue
        if item != wanted_item:
            raise D2Error(f"{country}: concepto equivocado para {code}: {item}")
        try:
            year = int(year_s)
        except ValueError as exc:
            raise D2Error(f"{country}: año inválido {year_s!r}") from exc
        value = parse_decimal(value_s, f"{country}/{year}/{code}")
        if code in values.setdefault(year, {}):
            raise D2Error(f"{country}/{year}: concepto duplicado {code}")
        values[year][code] = value
        raw_text.setdefault(year, {})[code] = value_s
        currencies.add(currency)
    if not values:
        raise D2Error(f"{country}: sin observaciones contractuales")
    if len(currencies) != 1:
        raise D2Error(f"{country}: monedas heterogéneas: {currencies}")
    quanta = {}
    for code in ITEMS:
        series_values = [v[code] for y, v in values.items()
                         if y >= SENSITIVITY_START and code in v]
        if series_values:
            quanta[code] = implied_quantum(series_values)
    return Panel(country, values, raw_text, quanta, next(iter(currencies)))


def parse_ama_gdp(blob: bytes) -> tuple[dict[str, dict[int, Decimal]], dict[str, Decimal]]:
    try:
        wb = load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
    except Exception as exc:  # openpyxl tipa varias corrupciones OOXML
        raise D2Error(f"workbook AMA inválido: {exc}") from exc
    sheet = "Download-GDPcurrent-NCU-countri"
    if sheet not in wb.sheetnames:
        raise D2Error("AMA sin hoja de PIB corriente")
    rows = wb[sheet].iter_rows(values_only=True)
    try:
        next(rows)
        next(rows)
        header = tuple(next(rows))
    except StopIteration as exc:
        raise D2Error("AMA truncado") from exc
    if header[:4] != ("CountryID", "Country", "Currency", "IndicatorName"):
        raise D2Error("AMA: encabezado conceptual inesperado")
    years = header[4:]
    if not all(isinstance(y, int) for y in years):
        raise D2Error("AMA: columnas anuales inválidas")
    found: dict[str, dict[int, Decimal]] = {}
    for row in rows:
        if len(row) < 4 or row[1] not in COUNTRY_NAMES.values():
            continue
        if row[3] != "Gross Domestic Product (GDP)":
            continue
        country = next(k for k, v in COUNTRY_NAMES.items() if v == row[1])
        if country in found:
            raise D2Error(f"AMA: PIB duplicado para {country}")
        found[country] = {
            year: parse_decimal(str(value), f"AMA/{country}/{year}")
            for year, value in zip(years, row[4:]) if value is not None
        }
    if sorted(found) != list(COUNTRIES):
        raise D2Error("AMA: faltan países o concepto GDP")
    quanta = {
        c: implied_quantum(v for y, v in panel.items() if y >= SENSITIVITY_START)
        for c, panel in found.items()
    }
    return found, quanta


def complete_years(panel: Panel, ama: Mapping[int, Decimal], country: str) -> set[int]:
    if country == "CHL":
        needed = {"B.1*g", "D.1", "D.2-D.3"}
    else:
        needed = set(ITEMS)
    return {year for year, vals in panel.values.items()
            if needed <= set(vals) and year in ama}


def derive_common_year(years_by_country: Mapping[str, set[int]]) -> int:
    if sorted(years_by_country) != list(COUNTRIES):
        raise D2Error("falta un país para derivar el año común")
    common = set.intersection(*(set(years_by_country[c]) for c in COUNTRIES))
    if not common:
        raise D2Error("no existe año completo común; no se interpola")
    return max(common)


def identity_tolerance(quanta: Iterable[Decimal]) -> Decimal:
    qs = list(quanta)
    if not qs or any(q <= 0 for q in qs):
        raise D2Error("precisión publicada inválida")
    return sum(qs, Decimal(0)) / Decimal(2)


def validate_identity(residual: Decimal, tolerance: Decimal) -> None:
    if abs(residual) > tolerance:
        raise D2Error(
            f"D1: identidad fuera de precisión: |{residual}| > {tolerance}"
        )


def ordinary_observation(country: str, year: int, panel: Panel,
                         ama: Mapping[int, Decimal], ama_quantum: Decimal) -> Observation:
    vals = panel.values[year]
    required = set(ITEMS)
    if not required <= set(vals):
        raise D2Error(f"{country}/{year}: componentes incompletos")
    gdp = ama[year]
    table_gdp = vals["B.1*g"]
    if gdp != table_gdp and country != "MEX":
        raise D2Error(f"{country}/{year}: B.1*g no coincide exactamente con PIB")
    coe = vals["D.1"]
    gos_mi = vals["B.2g"] + vals["B.3g"]
    taxes = vals["D.2-D.3"]
    residual = coe + gos_mi + taxes - gdp
    qs = {
        "gdp_market": ama_quantum,
        "coe": panel.quanta["D.1"],
        "gos": panel.quanta["B.2g"],
        "mi": panel.quanta["B.3g"],
        "taxes_net": panel.quanta["D.2-D.3"],
    }
    if residual == 0:
        tolerance = Decimal(0)
        basis = "exact_identity_no_tolerance_needed"
        status = "PASS"
    elif country == "MEX":
        # La evidencia fuente-específica se liga después de extraer el PDF.
        tolerance = Decimal(0)
        basis = "diagnostic_precision_not_validated"
        status = "NOT_VALIDATED"
    else:
        raise D2Error(
            f"{country}/{year}: identidad no exacta sin evidencia de precisión"
        )
    return Observation(
        country, year, coe, gos_mi, taxes, gdp, residual, tolerance,
        "ordinary_income_account_market_prices", qs, basis, status
    )


def chile_observation(year: int, panel: Panel, ama: Mapping[int, Decimal],
                      ama_quantum: Decimal) -> Observation:
    vals = panel.values[year]
    needed = {"B.1*g", "D.1", "D.2-D.3"}
    if not needed <= set(vals):
        raise D2Error(f"CHL/{year}: componentes de crosswalk incompletos")
    basic = vals["B.1*g"]
    market = ama[year]
    coe = vals["D.1"]
    d29 = vals["D.2-D.3"]
    if market <= basic:
        raise D2Error(f"CHL/{year}: la valoración no distingue mercado de básicos")
    gos_mi = basic - coe - d29
    taxes_products = market - basic
    taxes_total = d29 + taxes_products
    residual = coe + gos_mi + taxes_total - market
    qs = {
        "gdp_market": ama_quantum,
        "gdp_basic": panel.quanta["B.1*g"],
        "coe": panel.quanta["D.1"],
        "d29": panel.quanta["D.2-D.3"],
    }
    tolerance = Decimal(0)
    validate_identity(residual, tolerance)
    # Trampa E-07: el mismo numerador completo no puede cerrar contra básicos.
    bad_residual = coe + gos_mi + taxes_total - basic
    if abs(bad_residual) <= tolerance:
        raise D2Error("CHL: la prueba adversarial no distinguió el denominador")
    return Observation(
        "CHL", year, coe, gos_mi, taxes_total, market, residual,
        tolerance, "chile_basic_to_market_crosswalk", qs,
        "exact_identity_no_tolerance_needed", "PASS"
    )


def make_observation(country: str, year: int, panel: Panel,
                     ama: Mapping[int, Decimal], ama_quantum: Decimal) -> Observation:
    if country == "CHL":
        return chile_observation(year, panel, ama, ama_quantum)
    return ordinary_observation(country, year, panel, ama, ama_quantum)


def observation_row(
    obs: Observation, acquisition: Acquisition, source_snapshot_id: str
) -> dict[str, str]:
    if obs.gdp_market <= 0:
        raise D2Error(f"{obs.country}/{obs.year}: PIB no positivo")
    coe_gdp = obs.coe / obs.gdp_market
    gos_mi_gdp = obs.gos_mi / obs.gdp_market
    tax_gdp = obs.taxes_net / obs.gdp_market
    residual = obs.residual_level / obs.gdp_market
    s_l = coe_gdp
    row = {
        "country_id": obs.country,
        "observation_year": str(obs.year),
        "source_snapshot_id": source_snapshot_id,
        "source_vintage": acquisition.vintage_actual,
        "coe_gdp": decimal_text(coe_gdp, 15),
        "gos_mi_gdp": decimal_text(gos_mi_gdp, 15),
        "taxes_net_gdp": decimal_text(tax_gdp, 15),
        "gdp_market_prices": decimal_text(obs.gdp_market),
        "identity_residual": decimal_text(residual, 15),
        "precision_basis": obs.precision_basis,
        "precision_source_id": (
            PRECISION_SOURCE_ID
            if obs.precision_basis == "source_declared_rounding_interval"
            else "not_applicable"
        ),
        "precision_half_width_ncu": decimal_text(obs.tolerance_level),
        "rounding_consistency_status": obs.rounding_consistency_status,
        "s_L_bar": decimal_text(s_l, 15),
        "mi_partition_status": MI_STATE,
        "source_id": SOURCE_ID,
        "retrieved_at": acquisition.retrieved_at,
    }
    validate_output_row(row)
    return row


def validate_output_row(row: Mapping[str, str]) -> None:
    if tuple(row.keys()) != SCHEMA_COLUMNS:
        raise D2Error("esquema u orden de columnas incorrecto")
    for key, value in row.items():
        if value == "":
            raise D2Error(f"salida vacía: {key}")
    numeric = ("coe_gdp", "gos_mi_gdp", "taxes_net_gdp",
               "gdp_market_prices", "identity_residual",
               "precision_half_width_ncu", "s_L_bar")
    for key in numeric:
        value = parse_decimal(row[key], f"output/{key}")
        if row[key].startswith("-0") and value == 0:
            raise D2Error(f"-0.0 no normalizado en {key}")
    if row["s_L_bar"] != row["coe_gdp"]:
        raise D2Error("s_L_bar debe ser exactamente COE/PIB_mercado")
    if row["mi_partition_status"] != MI_STATE:
        raise D2Error("partición silenciosa del ingreso mixto")
    if row["rounding_consistency_status"] not in {"PASS", "NOT_VALIDATED"}:
        raise D2Error("estado de precisión fuera de dominio")
    if not re.fullmatch(r"[0-9a-f]{64}", row["source_snapshot_id"]):
        raise D2Error("source_snapshot_id ausente o inválido")


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=SCHEMA_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        validate_output_row(row)
        writer.writerow(row)
    data = stream.getvalue().encode("utf-8")
    if data.startswith(b"\xef\xbb\xbf") or b"\r\n" in data:
        raise D2Error("CSV no es UTF-8 sin BOM con LF determinista")
    return data


def validate_comparison(
    rows: Iterable[Mapping[str, str]], comparison_kind: str | None,
    *, lag_or_snapshot_declared: bool = False
) -> str:
    rows = list(rows)
    if comparison_kind is None or len(rows) < 2:
        return "not_applicable"
    if comparison_kind not in {"level", "ratio"}:
        raise D2Error("D13: tipo de comparación fuera de dominio")
    if any(not re.fullmatch(r"[0-9a-f]{64}", r.get("source_snapshot_id", ""))
           for r in rows):
        raise D2Error("D13: source_snapshot_id ausente")
    snapshots = {r["source_snapshot_id"] for r in rows}
    years = {r.get("observation_year") for r in rows}
    if comparison_kind == "level" and len(snapshots) > 1:
        raise D2Error("D13: comparación monetaria entre snapshots incompatibles")
    if comparison_kind == "ratio" and (
        len(snapshots) > 1 or len(years) > 1
    ) and not lag_or_snapshot_declared:
        raise D2Error("D13: razón con desfase/snapshot no declarado")
    return "PASS"


def source_snapshot_id(artifacts: list[dict[str, str]]) -> str:
    if not artifacts or any(
        not re.fullmatch(r"[0-9a-f]{64}", a.get("sha256", ""))
        for a in artifacts
    ):
        raise D2Error("snapshot: artefacto o hash ausente")
    return sha256_bytes(canonical_json(sorted(
        artifacts, key=lambda a: (a["role"], a["sha256"])
    )))


def validate_authoritative_primary_table(
    rows: Iterable[Mapping[str, str]], documents: Iterable[Path]
) -> dict[str, str]:
    """Liga las cuatro cifras documentales a las filas generadas, sin tolerancia."""
    produced = {row["country_id"]: row["s_L_bar"] for row in rows}
    if sorted(produced) != list(COUNTRIES):
        raise D2Error("tabla primaria: países producidos incompletos")
    checked = []
    for document in documents:
        text = document.read_text(encoding="utf-8")
        missing = {
            country: value for country, value in produced.items()
            if f"{country} {value}" not in text
        }
        if missing:
            raise D2Error(
                f"tabla primaria documental no coincide en {document.name}: {missing}"
            )
        checked.append(
            "design_plan" if document.name.startswith("PLAN_DISENO_")
            else "quantification_protocol"
        )
    if not checked:
        raise D2Error("tabla primaria: no se proporcionaron documentos autoritativos")
    return {"status": "PASS", "documents": ",".join(checked)}


def active_primary_table_documents() -> list[Path]:
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    paths = [row["path"] for row in manifest.get("documents", [])]
    selected = [
        ROOT / path for path in paths
        if (Path(path).name.startswith("PLAN_DISENO_")
            or Path(path).name.startswith("PROTOCOLO_ENVOLVENTE_LAMBDA_PI_"))
    ]
    if len(selected) != 2 or any(not path.is_file() for path in selected):
        raise D2Error("manifiesto vigente no identifica plan de diseño y protocolo")
    return selected


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name.startswith("test_") for node in tree.body)


def run_behavioral_suite() -> dict[str, object]:
    ast_count = _count_tests(TEST_FILE)
    proc = subprocess.run(
        [sys.executable, str(TEST_FILE)], cwd=str(ROOT),
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    stdout = proc.stdout.replace("\r\n", "\n")
    stderr = proc.stderr.replace("\r\n", "\n")
    passed = sum(line.strip().startswith("PASA ") for line in stdout.splitlines())
    if proc.returncode != 0 or passed != ast_count:
        raise D2Error(
            f"suite D-2 no verde: rc={proc.returncode}, AST={ast_count}, "
            f"ejecutadas={passed}\n{stdout}\n{stderr}"
        )
    return {
        "suite": "fase2_datos/d2_cuentas_nacionales/test_d2.py",
        "ast_count": ast_count,
        "executed_count": passed,
        "status": "PASS",
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
    }


def _audit_text(
    common_year: int,
    observations: Mapping[str, Mapping[int, Observation]],
    primary_rows: list[dict[str, str]],
    sensitivity_rows: list[dict[str, str]],
    mex_precision: Mapping[str, object],
    precision_acquisition: Acquisition,
) -> bytes:
    lines = [
        "# AUDITORÍA D-2 — cuentas nacionales y participación laboral",
        "",
        "## Alcance",
        "",
        "D-2 construye las cuentas exclusivamente desde `UN_SNA_MAIN` y usa `INEGI_CSI_2023_D2_PRECISION` sólo para validar la resolución e identidad de México en 2023. INEGI no sustituye valores UN SNA ni calibra otro objeto. D-2 no usa `UN_SNA_SECTOR_SURPLUS_A5`, no interpola, no extrapola y no produce artefactos D-3–D-8 ni resultados del modelo.",
        "",
        "## Año y metadatos",
        "",
        f"El año primario **{common_year}** es el máximo de la intersección de años completos observados para CHL, COL, MEX y PER. La salida primaria tiene {len(primary_rows)} filas; la sensibilidad 2015–{common_year} conserva {len(sensitivity_rows)} observaciones realmente disponibles.",
        "",
        "Denominador: PIB a precios de mercado. Universo: economía total. Horizonte: anual. Unidad del nivel: moneda nacional corriente. `observation_year` es el periodo económico; `source_vintage` es metadata del release; `source_snapshot_id` se deriva de los hashes de los payloads y miembros exactos. No existe un `reference_year` separado porque la regla primaria selecciona directamente un único `observation_year` común. No se comparan niveles entre países o snapshots; sólo se construyen cocientes adimensionales dentro de cada país-año.",
        "",
        "## Crosswalk contable",
        "",
        "| País | Camino | Componentes | Denominador |",
        "|---|---|---|---|",
        "| PER | ordinario | D.1 + B.2g + B.3g + (D.2−D.3), cuenta de generación del ingreso | B.1*g de mercado, reconciliado con AMA grupo 101 |",
        "| COL | ordinario | D.1 + B.2g + B.3g + (D.2−D.3), cuenta de generación del ingreso | B.1*g de mercado, reconciliado con AMA grupo 101 |",
        "| MEX | ordinario | D.1 + B.2g + B.3g + (D.2−D.3), cuenta de generación del ingreso | B.1*g de mercado, reconciliado con AMA grupo 101 |",
        "| CHL | E-07 | `GOS+MI = PIB_básico − D.1 − D.29`; `T_net = D.29 + (PIB_mercado − PIB_básico)` | AMA grupo 101; la línea B.1*g de tabla 4.1 se trata como valor agregado a precios básicos |",
        "",
        "La prueba adversarial sustituye el denominador chileno de mercado por el básico manteniendo los componentes completos y exige FAIL. El residuo se calcula siempre como `(COE + GOS + MI + T_net − PIB_mercado)/PIB_mercado`; nunca se asigna a cero.",
        "",
        "## Precisión publicada",
        "",
        "El MCD de valores observados no identifica precisión publicada y queda retirado del hard gate. Chile, Colombia y Perú cierran exactamente y usan tolerancia cero. Para México 2023, el cuadro 2 de INEGI publica cinco términos por separado en millones de pesos corrientes y advierte que los parciales pueden no coincidir con el total por redondeo. Cada cifra tiene semiamplitud de redondeo de 0.5 millones. Por desigualdad triangular, la cota conservadora del residuo es `T = 5 × 0.5 × 10^6 = 2,500,000` pesos. No se supone independencia estadística. La tolerancia se deriva antes de mirar el residuo y el gate exige `|residuo_nivel| ≤ T`.",
        "",
        f"Fuente de precisión: `{precision_acquisition.raw_rel}`; SHA-256 `{precision_acquisition.file_hash}`. Unidad: `{mex_precision['unit']}`; semiamplitud por componente: `{mex_precision['component_half_width_millions']}` millones.",
        "",
        "| País | Año | s_L_bar | identity_residual | tolerancia de nivel | precision_basis | estado |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    by_country = {r["country_id"]: r for r in primary_rows}
    for country in COUNTRIES:
        row = by_country[country]
        obs = observations[country][common_year]
        lines.append(
            f"| {country} | {common_year} | {row['s_L_bar']} | "
            f"{row['identity_residual']} | {decimal_text(obs.tolerance_level)} | "
            f"{obs.precision_basis} | {obs.rounding_consistency_status} |"
        )
    lines += [
        "",
        "### Ligadura UN SNA ↔ INEGI para México 2023",
        "",
        "| Componente | UN menos INEGI, millones de pesos | Intervalo exigido |",
        "|---|---:|---:|",
    ]
    differences = mex_precision["un_minus_inegi_millions"]
    for component in (
        "gdp", "compensation", "gross_operating_surplus",
        "gross_mixed_income", "net_taxes_production_imports",
    ):
        lines.append(f"| {component} | {differences[component]} | ±0.5 |")
    lines += [
        "",
        "La sensibilidad MEX 2015–2022 se conserva con `diagnostic_precision_not_validated`: la evidencia 2023 no se transporta hacia atrás. No se localizó, dentro del alcance autorizado de una única fuente oficial, un tabulado único que documente los mismos cinco conceptos y la misma regla de redondeo para todos esos años. Sus filas no son pases de identidad por precisión publicada.",
        "",
        "## Tabla primaria autoritativa",
        "",
        "| País | s_L_bar |",
        "|---|---:|",
    ]
    for country in COUNTRIES:
        lines.append(f"| {country} | {by_country[country]['s_L_bar']} |")
    lines += [
        "",
        "`COL=0.339` corresponde a un diagnóstico de 2024 y no pertenece al corte común primario de 2023.",
        "",
        "## Ingreso mixto y vocabulario",
        "",
        f"`mi_partition_status={MI_STATE}` es un estado nulo de vocabulario, no un escenario económico: MI no se asigna al trabajo ni se estima una fracción. `s_L_bar = COE/PIB_mercado`, mientras `GOS+MI` permanece agregado.",
        "",
        "## Compuertas",
        "",
        "D1 verifica identidad y conserva discrepancias; D2 exige denominador, universo y horizonte; D3 registra ausencia de circularidad; D11 prohíbe promediar la primaria; D12 hereda `retrieved_at`; D13 bloquea comparaciones de nivel entre snapshots incompatibles y devuelve `not_applicable` cuando no existe comparación. Todas operan con fallo cerrado.",
        "",
    ]
    return ("\n".join(lines)).encode("utf-8")


def build_artifacts(*, run_tests: bool = True) -> tuple[dict[str, bytes], dict[str, object]]:
    d1_hashes = verify_d1_surfaces()
    acquisitions = read_acquisitions()
    precision_acquisition = read_precision_acquisition()
    inegi_values = parse_inegi_precision(precision_acquisition.raw_path)
    catalog_contract = validate_catalog_contract()

    bundle_paths = {a.raw_path for a in acquisitions.values()
                    if a.raw_path.suffix.lower() == ".tar"}
    if len(bundle_paths) != 1:
        raise D2Error("se esperaba un único bundle TAR para CHL/MEX/PER")
    bundle, member_manifest = read_bundle(next(iter(bundle_paths)))
    ama, ama_quanta = parse_ama_gdp(bundle["ama_gdp_current_ncu.xls"])

    panels = {}
    for country in ("CHL", "MEX", "PER"):
        member = f"table401_{country}.zip"
        panels[country] = parse_table_csv(
            unzip_single_csv(bundle[member], member), country
        )
    col_blob = acquisitions["COL"].raw_path.read_bytes()
    panels["COL"] = parse_table_csv(
        unzip_single_csv(col_blob, "UN_SNA_MAIN/COL"), "COL"
    )

    years_by_country = {
        c: complete_years(panels[c], ama[c], c) for c in COUNTRIES
    }
    if any(not years for years in years_by_country.values()):
        raise D2Error("país sin años completos")
    common_year = derive_common_year(years_by_country)

    observations: dict[str, dict[int, Observation]] = {c: {} for c in COUNTRIES}
    for country in COUNTRIES:
        for year in sorted(y for y in years_by_country[country]
                           if SENSITIVITY_START <= y <= common_year):
            observations[country][year] = make_observation(
                country, year, panels[country], ama[country], ama_quanta[country]
            )
        if common_year not in observations[country]:
            raise D2Error(f"{country}: año común no construido")

    if common_year != 2023:
        raise D2Error("la evidencia INEGI predeclarada sólo valida el corte común 2023")
    observations["MEX"][common_year], mex_precision = bind_mexico_precision(
        observations["MEX"][common_year], panels["MEX"], ama["MEX"],
        inegi_values,
    )

    ama_sha = member_manifest["ama_gdp_current_ncu.xls"]["sha256"]
    snapshot_artifacts: dict[str, list[dict[str, str]]] = {}
    snapshot_ids = {}
    for country in COUNTRIES:
        if country == "COL":
            parts = [
                {"role": "table_4_1_payload_zip", "sha256": acquisitions[country].file_hash},
                {"role": "ama_gdp_member", "sha256": str(ama_sha)},
            ]
        else:
            member = f"table401_{country}.zip"
            parts = [
                {"role": "sna_bundle", "sha256": acquisitions[country].file_hash},
                {"role": "table_4_1_member", "sha256": str(member_manifest[member]["sha256"])},
                {"role": "ama_gdp_member", "sha256": str(ama_sha)},
            ]
        if country == "MEX":
            parts.append({
                "role": "inegi_precision_pdf",
                "sha256": precision_acquisition.file_hash,
            })
        snapshot_artifacts[country] = parts
        snapshot_ids[country] = source_snapshot_id(parts)

    primary_rows = [
        observation_row(
            observations[c][common_year], acquisitions[c], snapshot_ids[c]
        )
        for c in COUNTRIES
    ]
    sensitivity_rows = [
        observation_row(observations[c][year], acquisitions[c], snapshot_ids[c])
        for c in COUNTRIES for year in sorted(observations[c])
    ]
    primary_csv = csv_bytes(primary_rows)
    sensitivity_csv = csv_bytes(sensitivity_rows)
    primary_table_check = validate_authoritative_primary_table(
        primary_rows, active_primary_table_documents()
    )

    # D11: la primaria contiene una observación, no un promedio temporal.
    if len(primary_rows) != len(COUNTRIES) or any(
        int(r["observation_year"]) != common_year for r in primary_rows
    ):
        raise D2Error("D11: especificación primaria no puntual")
    # D13: construir cocientes país-año no compara niveles entre snapshots.
    d13_status = validate_comparison(primary_rows, None)

    test_result = run_behavioral_suite() if run_tests else {
        "suite": "test_mode",
        "ast_count": 0,
        "executed_count": 0,
        "status": "NOT_RUN_TEST_MODE",
        "stdout_sha256": "not_applicable",
    }

    gate = {
        "schema_version": "d2_gate_report/2.0.0",
        "phase": "D-2",
        "status": "PASS",
        "gates": [
            {"gate": "D1", "status": "PASS", "evidence": "identity residual retained and within source-derived precision"},
            {"gate": "D2", "status": "PASS", "evidence": catalog_contract},
            {"gate": "D3", "status": "PASS", "evidence": "only UN_SNA_MAIN; no companion-paper result used"},
            {"gate": "D11", "status": "PASS", "evidence": "one observed common-year row per country; no averaging"},
            {"gate": "D12", "status": "PASS", "evidence": "retrieved_at inherited from acquisition_manifest"},
            {"gate": "D13", "status": "PASS", "evidence": d13_status},
            {"gate": "PRIMARY_TABLE", "status": "PASS", "evidence": primary_table_check},
            {"gate": "CHL_E07", "status": "PASS", "evidence": "market/basic valuation paths differ and basic-denominator fixture fails"},
            {"gate": "MI", "status": "PASS", "evidence": f"{MI_STATE}; no allocation to labor"},
            {"gate": "NO_DOWNSTREAM", "status": "PASS", "evidence": "builder output allowlist contains only D-2 artifacts"},
        ],
        "behavioral_suite": test_result,
    }
    gate_bytes = canonical_json(gate)
    audit_bytes = _audit_text(
        common_year, observations, primary_rows, sensitivity_rows,
        mex_precision, precision_acquisition,
    )

    input_payloads = {}
    for country, acq in acquisitions.items():
        input_payloads[country] = {
            "dataset_id": SOURCE_ID,
            "raw_path": acq.raw_rel,
            "sha256": acq.file_hash,
            "retrieved_at": acq.retrieved_at,
            "source_vintage": acq.vintage_actual,
            "source_snapshot_id": snapshot_ids[country],
        }
    member_hashes = {
        name: {"sha256": row["sha256"], "size_bytes": row["size_bytes"]}
        for name, row in sorted(member_manifest.items())
    }
    artifacts = {
        "labor_income_shares.csv": primary_csv,
        "labor_income_shares_sensitivity.csv": sensitivity_csv,
        "AUDITORIA_D2.md": audit_bytes,
        "d2_gate_report.json": gate_bytes,
    }
    combined = hashlib.sha256()
    for name in ("labor_income_shares.csv", "labor_income_shares_sensitivity.csv"):
        combined.update(name.encode("utf-8") + b"\0" + artifacts[name])
    manifest = {
        "schema_version": "d2_manifest/2.0.0",
        "labor_income_shares_schema_version": "13.1/2.0.0",
        "phase": "D-2",
        "primary_common_year": common_year,
        "common_year_rule": "max(intersection(complete_observed_years_by_country))",
        "complete_years_by_country": {
            c: sorted(years_by_country[c]) for c in COUNTRIES
        },
        "primary_rows": len(primary_rows),
        "sensitivity_start_year": SENSITIVITY_START,
        "sensitivity_rows": len(sensitivity_rows),
        "temporal_semantics": {
            "observation_year": "economic period observed",
            "source_vintage": "release metadata; not copied from observation_year",
            "source_snapshot_id": "sha256 of exact payload/member roles used",
            "reference_year": "omitted: no distinct object; the common-year rule selects observation_year directly",
        },
        "metadata_contract": catalog_contract,
        "source_id": SOURCE_ID,
        "mi_partition": {
            "mi_partition_status": MI_STATE,
            "status": MI_STATE,
            "labor_allocation_fraction": None,
            "is_economic_scenario": False,
        },
        "identity": {
            "residual_formula": "(COE + GOS + MI + T_net - GDP_market)/GDP_market",
            "mcd_role": "diagnostic_only_not_a_precision_gate",
            "primary_mexico_tolerance_formula": "5 * 0.5 * 1,000,000 NCU",
            "primary_mexico_tolerance_logic": "triangle_inequality_five_separately_published_terms_no_statistical_independence_assumed",
            "residual_is_overwritten": False,
            "countries": {
                c: {
                    "method": observations[c][common_year].method,
                    "residual_level": decimal_text(observations[c][common_year].residual_level),
                    "tolerance_level": decimal_text(observations[c][common_year].tolerance_level),
                    "precision_basis": observations[c][common_year].precision_basis,
                    "precision_source_id": (
                        PRECISION_SOURCE_ID if c == "MEX" else "not_applicable"
                    ),
                    "rounding_consistency_status": observations[c][common_year].rounding_consistency_status,
                    "precision_quanta": {
                        k: decimal_text(v) for k, v in observations[c][common_year].precision_quanta.items()
                    },
                } for c in COUNTRIES
            },
            "mexico_inegi_binding": mex_precision,
            "sensitivity_mexico_2015_2022": "diagnostic_precision_not_validated",
        },
        "authoritative_primary_table": {
            **primary_table_check,
            "values": {r["country_id"]: r["s_L_bar"] for r in primary_rows},
            "col_0_339_status": "2024_diagnostic_not_primary_common_year",
        },
        "input_surface_hashes": d1_hashes,
        "input_payloads": input_payloads,
        "authenticated_bundle_members": member_hashes,
        "source_snapshot_artifacts": snapshot_artifacts,
        "precision_source": {
            "dataset_id": PRECISION_SOURCE_ID,
            "raw_path": precision_acquisition.raw_rel,
            "sha256": precision_acquisition.file_hash,
            "retrieved_at": precision_acquisition.retrieved_at,
            "values_millions": {k: decimal_text(v) for k, v in inegi_values.items()},
        },
        "implementation": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "openpyxl": __import__("openpyxl").__version__,
            "xlsx_mode": "read_only=True,data_only=True",
        },
        "artifacts": {
            name: {"sha256": sha256_bytes(data), "size_bytes": len(data)}
            for name, data in sorted(artifacts.items())
        },
        "builder_sha256": sha256_file(Path(__file__)),
        "tests_sha256": sha256_file(TEST_FILE),
        "scientific_payload_sha256": combined.hexdigest(),
        "downstream_outputs_created": [],
    }
    artifacts["d2_manifest.json"] = canonical_json(manifest)
    return artifacts, manifest


def publish_atomic(artifacts: Mapping[str, bytes], output_dir: Path = OUTPUT_DIR,
                   fail_after: int | None = None) -> str:
    allowed = {
        "labor_income_shares.csv",
        "labor_income_shares_sensitivity.csv",
        "AUDITORIA_D2.md",
        "d2_gate_report.json",
        "d2_manifest.json",
    }
    if set(artifacts) != allowed:
        raise D2Error("allowlist D-2 violada")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".d2-output-", dir=output_dir.parent))
    try:
        for index, name in enumerate(sorted(artifacts), start=1):
            path = temp / name
            with path.open("wb") as fh:
                fh.write(artifacts[name])
                fh.flush()
                os.fsync(fh.fileno())
            if fail_after is not None and index >= fail_after:
                raise D2Error("fallo tardío inyectado")
        if output_dir.exists():
            existing = {p.name: p.read_bytes() for p in output_dir.iterdir() if p.is_file()}
            if existing != dict(artifacts):
                raise D2Error("salida D-2 existente difiere; no se sobrescribe")
            return "idempotent_no_change"
        os.replace(temp, output_dir)
        temp = None
        return "published"
    finally:
        if temp is not None and temp.exists():
            shutil.rmtree(temp)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--no-tests", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        artifacts, manifest = build_artifacts(run_tests=not args.no_tests)
        if args.command == "build":
            status = publish_atomic(artifacts)
        else:
            if not OUTPUT_DIR.is_dir():
                raise D2Error("salida D-2 ausente")
            existing = {p.name: p.read_bytes() for p in OUTPUT_DIR.iterdir() if p.is_file()}
            if existing != artifacts:
                raise D2Error("salida D-2 no reproduce byte a byte")
            status = "verified"
        print(
            f"D2 {status}: common_year={manifest['primary_common_year']} "
            f"primary={manifest['primary_rows']} sensitivity={manifest['sensitivity_rows']} "
            f"scientific_payload_sha256={manifest['scientific_payload_sha256']}"
        )
        return 0
    except D2Error as exc:
        print(f"D2 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
