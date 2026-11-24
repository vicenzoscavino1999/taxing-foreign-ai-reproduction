"""Escritura y lectura de tablas y documentos del catálogo integrado (CA2-3) sin esquemas propios.

El catálogo autenticado es la única fuente de columnas, tipos, nulos, PK/UK/FK y orden. Cada tabla se valida con
Contracts.table (núcleo S3) antes de serializarse y se relee byte a byte después. Árbol de familia:
tree_sha256 = H(lista ordenada {path, sha256, bytes}) (CONTRATOS_D7_B_D8: 'tree'); manifiesto y punteros excluidos.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from decimal import Decimal
from pathlib import Path

from .keys import H, canon
from .numeric import canon_dec


class TableError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _cell(value, typ: str) -> str:
    if value is None:
        return ""
    if typ == "bool":
        if type(value) is not bool:
            raise TableError("bool tipado requerido")
        return "true" if value else "false"
    if typ == "int":
        if type(value) is not int or value < 0:
            raise TableError("int no negativo requerido")
        return str(value)
    if typ in ("dec", "positive", "rate"):
        return canon_dec(value)
    if typ == "json":
        return canon(value).decode("utf-8")
    s = str(value)
    if not s:
        raise TableError("texto vacío prohibido")
    return s


def normalize_row(contracts, name: str, row: dict) -> dict:
    """Convierte floats/Fractions a decimales canónicos según el tipo de columna (lo que valida Contracts.table)."""
    cols = {c["name"]: c for c in contracts.C["tables"][name]["columns"]}
    if set(row) != set(cols):
        missing, extra = set(cols) - set(row), set(row) - set(cols)
        raise TableError(f"columnas exactas {name}: faltan {sorted(missing)} sobran {sorted(extra)}")
    out = {}
    for k, v in row.items():
        t = cols[k]["type"]
        if v is None:
            out[k] = None
        elif t in ("dec", "positive", "rate"):
            out[k] = canon_dec(v)
        else:
            out[k] = v
    return out


def sort_rows(contracts, name: str, rows: list) -> list:
    tab = contracts.C["tables"][name]
    cols = {c["name"]: c for c in tab["columns"]}

    def typed(r):
        return tuple(Decimal(r[k]) if cols[k]["type"] in ("dec", "positive", "rate") else r[k] for k in tab["order_by"])
    return sorted(rows, key=typed)


def table_bytes(contracts, name: str, rows: list) -> bytes:
    tab = contracts.C["tables"][name]
    norm = sort_rows(contracts, name, [normalize_row(contracts, name, r) for r in rows])
    contracts.table(name, norm)
    stream = io.StringIO(newline="")
    w = csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerow([c["name"] for c in tab["columns"]])
    for r in norm:
        w.writerow([_cell(r[c["name"]], c["type"]) for c in tab["columns"]])
    return stream.getvalue().encode("utf-8")


def json_doc_bytes(contracts, name: str, obj: dict) -> bytes:
    """Documento JSON exacto del catálogo (propiedades exactas, tipos) en JSON canónico con LF final."""
    doc = contracts.C["json_documents"][name]
    props = {p["name"]: p for p in doc["properties"]}
    if set(obj) != set(props):
        raise TableError(f"propiedades exactas {name}: {sorted(set(props) ^ set(obj))}")
    for k, v in obj.items():
        if v is None:
            if not props[k]["nullable"]:
                raise TableError("null prohibido: " + k)
        elif props[k]["type"] in ("dec", "positive", "rate"):
            obj[k] = canon_dec(v)
            contracts.scalar(obj[k], props[k]["type"])
        else:
            contracts.scalar(v, props[k]["type"])
    return canon(obj) + b"\n"


def read_table(contracts, path: Path, name: str) -> list:
    return contracts.read_csv(path, name)


def file_entry(rel: str, data: bytes, rows: int | None) -> dict:
    return {"path": rel, "sha256": sha(data), "bytes": len(data), "rows": rows}


def tree_sha256(entries: list) -> str:
    return H([{k: e[k] for k in ("path", "sha256", "bytes")} for e in sorted(entries, key=lambda e: e["path"])])


def write_exact(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as h:
        h.write(data)
        h.flush()
        os.fsync(h.fileno())
    if path.read_bytes() != data:
        raise TableError("escritura no verificada: " + str(path))


def csv_rows(data: bytes) -> int:
    return max(0, data.count(b"\n") - 1)


def order_key(contracts, name: str):
    """Clave de orden canónica de la tabla (la misma de sort_rows / Contracts.table)."""
    tab = contracts.C["tables"][name]
    cols = {c["name"]: c for c in tab["columns"]}
    order = tab["order_by"]

    def typed(r):
        return tuple(Decimal(r[k]) if cols[k]["type"] in ("dec", "positive", "rate") else r[k] for k in order)
    return typed


class StreamTable:
    """Escritura CSV en flujo (memoria acotada) con las mismas reglas que table_bytes: filas normalizadas, validadas
    una a una contra el catálogo, orden canónico estricto y PK única comprobados entre filas consecutivas; SHA-256 y
    tamaño incrementales. Filas repetidas IDÉNTICAS (identificadores por contenido) se colapsan; misma PK con
    contenido distinto es un error."""

    def __init__(self, contracts, name: str, path: Path):
        self.C, self.name, self.path = contracts, name, Path(path)
        self.tab = contracts.C["tables"][name]
        self.key = order_key(contracts, name)
        self.pk = self.tab["primary_key"]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.h = hashlib.sha256()
        self.n_bytes = self.rows = 0
        self.last = None
        self.fh = self.path.open("wb")
        self._write([c["name"] for c in self.tab["columns"]])

    def _write(self, items):
        stream = io.StringIO(newline="")
        csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL).writerow(items)
        b = stream.getvalue().encode("utf-8")
        self.fh.write(b)
        self.h.update(b)
        self.n_bytes += len(b)

    def write(self, row: dict) -> bool:
        norm = normalize_row(self.C, self.name, row)
        self.C.table(self.name, [norm])
        if self.last is not None:
            k0, k1 = self.key(self.last), self.key(norm)
            if k1 < k0:
                raise TableError("orden no canónico en flujo: " + self.name)
            if tuple(self.last[k] for k in self.pk) == tuple(norm[k] for k in self.pk):
                if norm == self.last:
                    return False
                raise TableError("PK duplicada con contenido distinto: " + self.name)
        self._write([_cell(norm[c["name"]], c["type"]) for c in self.tab["columns"]])
        self.rows += 1
        self.last = norm
        return True

    def close(self) -> dict:
        self.fh.flush()
        os.fsync(self.fh.fileno())
        self.fh.close()
        return {"sha256": self.h.hexdigest(), "bytes": self.n_bytes, "rows": self.rows}
