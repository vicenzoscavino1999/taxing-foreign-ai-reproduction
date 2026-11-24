# License

This file covers what belongs to the package itself. Third-party pieces keep their own terms; they are listed in
[docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

Copyright holder: Vicenzo Scavino Alfaro.

## What each license covers

| Part | License |
|---|---|
| Own code: the program files (`.py`, `.ps1`) of `run.ps1`, `reproducir.py`, `src/`, `tools/`, `sensitivities/`, `insumos_externos/` and `nucleo_s6/`, and the environment recipe (`nucleo_s6/raiz/environment/`) | MIT, full text below |
| Own derived data, results and texts: every other own file, such as `datos/`, `referencias/`, `catalogo.json`, `fuentes_*.json`, `sensitivities/inputs/` and `sensitivities/reference/`, the derived files of `nucleo_s6/raiz/fase2_datos/`, `insumos_externos/un_bundle/bundle_manifest.json`, `README.md`, `CITATION.cff` and `docs/` | CC BY 4.0: <https://creativecommons.org/licenses/by/4.0/legalcode> |
| Third-party, outside these licenses: the 12 national-accounts sheets included in `nucleo_s6/raiz/fase2_datos/recepcion_nacional/versions/866aa139…/snapshots/`, the six UNdata files in `insumos_externos/un_bundle/` and the xlrd wheel in `nucleo_s6/raiz/herramientas/nacionales/vendor/` | Those of their source ([docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)) |

Some derived data contain values taken from the national accounts. When reusing them, cite the package author, under
CC BY 4.0, and also the original source of those values, as [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) indicates.

The code imports PyMuPDF, which is installed from PyPI and licensed under the AGPL-3.0 or under a commercial license from
Artifex. The MIT License is compatible with the AGPL-3.0. If a combined work covered by the AGPL is distributed, its
terms apply to the whole, including the corresponding source code. [Artifex terms](https://artifex.com/licensing).

## Text of the MIT License

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
