"""Reutilización EXACTA de encierros de C2 dentro de un proceso (MEJORAS DE CÁLCULO 3.7, NO OFICIAL).

La mirada adelante de M2r encierra las dos mitades de la raíz por cada eje; la partición dirigida vuelve a partir la
raíz por el primer eje elegido y encierra otra vez esas mismas dos mitades como hijas. c2_struct_enclosure es una
función pura de sus argumentos (crea su propio Engine y su propia rama y cota en cada llamada), así que el resultado
de una llamada idéntica es el mismo: se reutiliza en vez de recalcular.

Identidad de la entrada (TODO lo que entra en el cálculo): caja (extremos en float.hex), diseño, instrumento (menú),
cotas fiscales (barras), fijos completos, proveedor (clase, certificación, struct_tol, struct_max_boxes), método de
encierro (original o normalizado) e identidad de datos y código del contexto. Una identidad distinta no reutiliza.
"""
from __future__ import annotations

import hashlib
import json


def clave(box: dict, design: str, instrumento: str, bd: float, bf: float, fixed: dict, model, metodo: str, identidad: str) -> str:
    doc = {"caja": sorted((p, [float(lo).hex(), float(hi).hex()]) for p, (lo, hi) in box.items()),
           "diseno": design, "instrumento": instrumento, "barras": [float(bd).hex(), float(bf).hex()],
           "fijos": sorted((k, str(v)) for k, v in fixed.items()),
           "proveedor": {"kind": model.kind, "certified": bool(model.certified), "struct_tol": float(model.struct_tol).hex(),
                         "struct_max_boxes": int(model.struct_max_boxes)},
           "metodo": metodo, "identidad": identidad}
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class Memo:
    def __init__(self, activo: bool):
        self.activo = activo
        self.tabla: dict = {}
        self.pedidos = self.calculados = self.reutilizados = 0
        self.secuencia = hashlib.sha256()        # huella de TODOS los resultados entregados, en orden

    def obtener(self, k: str, calcular, caja: dict):
        self.pedidos += 1
        if self.activo and k in self.tabla:
            self.reutilizados += 1
            v = self.tabla[k]
        else:
            self.calculados += 1
            v = calcular()
            if self.activo:
                self.tabla[k] = v
        reg = [sorted((p, [float(a).hex(), float(b).hex()]) for p, (a, b) in caja.items()),
               None if v is None else [float(v.lo).hex(), float(v.hi).hex()]]
        self.secuencia.update(json.dumps(reg, separators=(",", ":")).encode("utf-8"))
        return v
