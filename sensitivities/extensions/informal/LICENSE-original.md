# Licencia

Este archivo cubre lo que es propio del paquete. Las piezas de terceros
conservan sus propias condiciones. Están listadas en el README, apartado
«Fuentes, cita y condiciones de distribución».

Titular de los derechos: Vicenzo Scavino Alfaro.

## Qué cubre cada licencia

| Parte | Licencia |
|---|---|
| Código propio: los archivos de programa (`.py`, `.ps1`) de `reproducir.py`, `src/`, `insumos_externos/` y `nucleo_s6/`, y la receta del entorno (`nucleo_s6/raiz/environment/`) | MIT, texto completo abajo |
| Datos derivados, resultados y textos propios: todos los demás archivos propios, como `datos/`, `referencias/`, `catalogo.json`, `fuentes_*.json`, los derivados de `nucleo_s6/raiz/fase2_datos/`, `insumos_externos/un_bundle/bundle_manifest.json`, los `RESULTADO_*.md` y la documentación | CC BY 4.0: <https://creativecommons.org/licenses/by/4.0/legalcode.es> |
| De terceros, fuera de estas licencias: las 12 hojas de cuentas nacionales incluidas en `nucleo_s6/raiz/fase2_datos/recepcion_nacional/versions/866aa139…/snapshots/`, los seis archivos de UNdata en `insumos_externos/un_bundle/` y la rueda de xlrd en `nucleo_s6/raiz/herramientas/nacionales/vendor/` | Las de su fuente (README) |

Algunos datos derivados contienen valores tomados de las cuentas nacionales.
Al reutilizarlos hay que citar al autor del paquete, con CC BY 4.0, y además
la fuente original de esos valores, como indica el README.

El código importa PyMuPDF, que se instala desde PyPI y se licencia bajo
AGPL-3.0 o bajo una licencia comercial de Artifex. La licencia MIT es
compatible con AGPL-3.0. Si se distribuye una obra combinada cubierta por la
AGPL, sus condiciones se aplican al conjunto, incluido el código fuente
correspondiente. [Condiciones de Artifex](https://artifex.com/licensing).

## Texto de la licencia MIT

```
MIT License

Copyright (c) 2026 Vicenzo Scavino Alfaro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
