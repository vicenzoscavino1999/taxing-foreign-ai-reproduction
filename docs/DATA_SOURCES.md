# Data sources, attribution and distribution terms

The following sources supply the national accounts used by the base model. The article reports conditional bounds on fiscal capacity for Peru, Colombia and Mexico. The base package also reads Chilean files as part of the national-accounts input set. The table records the distribution terms consulted in November 2026.

## Peruvian workbook

For a full base run, request the 2023 integrated economic accounts and supply–use workbook, `PBI_Imp_2023_CEIyCOU_R.xlsx`, from Peru’s INEI at `infoinei@inei.gob.pe`. Identify the worksheets Resumen, CEI_2023, COU_2023 and Enlaces. Save the file unedited as `PER_2023.xlsx` in the snapshots directory printed by `run.ps1 inputs`. Its size is 251,614 bytes and its SHA-256 is `dca6ebf37c2c0865a7d579cf73ade2358a459ea51441e2a2ee9d6b4412f158e3`. Return to the [full-run instructions](../README.md#full-base-reproduction) for verification and execution.

## National-accounts files

Of the 18 files in the base input set, 12 are included, five are obtained by `run.ps1 inputs`, and one is the workbook above. If a provider has updated a download and the hash differs, use the edition identified in the table.

| Source and files | In the public archive | Identification | Terms that apply |
|---|---|---|---|
| Banco Central de Chile, *Anuario de Cuentas Nacionales 2025*: `CHL_CEI.xls` (integrated economic accounts 2013–2024) and `CHL_COU.xlsx` (supply and use 2023, 12×12) | No. Downloaded by `obtener_insumos.py` | <https://si3.bcentral.cl/estadisticas/Principal1/informes/AnuarioCCNN/excel2025/CEI_anuario_2013-2024.xls> and <https://si3.bcentral.cl/estadisticas/Principal1/informes/AnuarioCCNN/excel2025/2023_Cuadros_12x12.xlsx>, linked from <https://si3.bcentral.cl/estadisticas/principal1/enlaces/informes/anuariosccnn/anuario_ccnn_2025.html> | <https://www.bcentral.cl/condiciones-de-uso> (same text at <https://portalbiblioteca.bcentral.cl/condiciones-de-uso>). Unaltered copies are allowed for personal use or use within one's organization, acknowledging the Bank's ownership. Distribution without express authorization is prohibited (Law 17,336). |
| DANE (Colombia), integrated economic accounts, base 2015: `COL_2023.xlsx` (2023 provisional, published 2025-02-17) and `COL_2024p.xlsx` (2024 provisional, published 2026-02-16) | No. Downloaded by `obtener_insumos.py` | <https://www.dane.gov.co/files/operaciones/PIB/anex-CuentasNalAnuales-CuentasEconomicasIntegradas-2023p.xlsx> and <https://www.dane.gov.co/files/operaciones/PIB/anex-CuentasNalAnuales-CuentasEconomicasIntegradas-2024p.xlsx> | <https://www.dane.gov.co/index.php/terminos-y-condiciones>. Use, exploitation, transformation and analysis are authorized with a verbatim citation of the source. The material is provided "individually, as an end-user license"; redistribution is not mentioned. |
| INEGI (Mexico), *Sistema de Cuentas Nacionales de México, Cuentas por Sectores Institucionales*, base year 2018, series 2003–2024, 2024 revised: `MEX_2015_public.xlsx` … `MEX_2023_public.xlsx` and `MEX_CSI_103.xlsx` | Yes | `https://www.inegi.org.mx/contenidos/programas/si/2018/tabulados/ori/CSI_<yy>.xlsx`, with `<yy>` from 15 to 23, and `…/ori/CSI_103.xlsx`, accessed 2026-09-19 | <https://www.inegi.org.mx/inegi/terminos.html>. Copies may be made and distributed without altering or removing their metadata, and adapted and exploited. Credit to INEGI is required, analyses or transformations must be disclosed, and they must not be presented as INEGI's or as its official position. |
| INEI (Peru), *Perú: Cuentas Nacionales 1950-2024. Cuentas de bienes y servicios y cuentas por sectores institucionales*: `PER_1950_2024.pdf` | Yes | <https://cdn.www.gob.pe/uploads/document/file/8978115/7387220-peru-cuentas-nacionales-1950-2024-cuentas-de-bienes-y-servicios-y-cuentas-por-sectores-institucionales.pdf?v=1762882540> | The notice on page 2 of the PDF allows total or partial reproduction provided the source is cited (Instituto Nacional de Estadística e Informática). |
| INEI (Peru), integrated economic accounts and supply and use 2023: `PER_2023.xlsx` (251,614 bytes, SHA-256 `dca6ebf3…`) | No. Available from INEI on individual request | INEI sent the author the workbook `PBI_Imp_2023_CEIyCOU_R.xlsx`. Its sheet CEI_2023 matches <https://www.inei.gob.pe/media/MenuRecursivo/indices_tematicos/cei_econtotal_2023.xlsx> except cell O25, which the code does not use. Its sheet COU_2023 matches sheet "Tip" of <https://www.inei.gob.pe/media/MenuRecursivo/indices_tematicos/cou_2023_corrientes_365_prod_x_101_activ.xlsx>. Its Resumen sheet, which the code also reads, exists only in the file sent by INEI | Available by individual request. The public ZIP omits the workbook because redistribution permission is undocumented. |
| United Nations Statistics Division, UNdata, *National Accounts Official Country Data*, table 4.1: `UN_COL.zip` (UNdata export of 2026-07-29) and six files of `UN_bundle.tar`: `table401_CHL.zip`, `table401_COL.zip`, `table401_MEX.zip`, `table401_PER.zip`, `chl_gdp_footnote.html` and `chl_gos_footnote.html` | Yes. The six files are in `insumos_externos/un_bundle/` | <https://data.un.org/Data.aspx?d=SNA&f=group_code%3A401>. The URL of each file of `UN_bundle.tar` is in `insumos_externos/un_bundle/bundle_manifest.json`. A new export does not have the same hash | <https://data.un.org/Host.aspx?Content=UNdataUse>. Free copying, duplication and redistribution are allowed, citing UNdata as the reference. |
| United Nations Statistics Division, *National Accounts – Analysis of Main Aggregates (AMA)*, GDP at current prices in national currency: `ama_gdp_current_ncu.xls`, inside `UN_bundle.tar` | No. Downloaded, and `UN_bundle.tar` rebuilt, by `obtener_insumos.py` | <https://unstats.un.org/unsd/amaapi/api/file/1>, linked from <https://unstats.un.org/unsd/snaama/> | The AMA page refers to the general UN terms: <https://www.un.org/en/about-us/terms-of-use>. Downloading and copying are allowed for personal, non-commercial use, without a right to redistribute. |

`UN_bundle.tar` was assembled by the project; its `bundle_manifest.json` is the project's own. The script rebuilds it
byte for byte (hash `03e965f4…`).

### Attribution of the data

When using or redistributing these data, or results that contain their values, cite each source in addition to the
package:

```text
Banco Central de Chile, Anuario de Cuentas Nacionales 2025. Propiedad del Banco Central de Chile.
Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co
Fuente: INEGI. Sistema de Cuentas Nacionales de México. Cuentas por Sectores Institucionales. Año Base 2018. Serie 2003-2024. 2024 Revisada.
Fuente: Instituto Nacional de Estadística e Informática (INEI). Perú: Cuentas Nacionales 1950-2024; Cuentas Económicas Integradas y Cuadro de Oferta y Utilización 2023.
UNdata (United Nations Statistics Division). National Accounts Official Country Data, Table 4.1; National Accounts - Analysis of Main Aggregates.
```

The calculations and transformations of these data are the package author's, not those of the institutions cited, and
do not represent their official position.

## Software

| Piece | How it arrives | Terms and effect on the package |
|---|---|---|
| CPython 3.12.4, 64-bit, `python-3.12.4-amd64.zip` (32,793,834 bytes, SHA-256 `35b4ac3b…`) from python.org | Downloaded by the user. Not redistributed | PSF License, in `LICENSE.txt` inside the zip. The [installation instructions](../README.md#installation) verify the download before extraction. |
| The 10 packages of the lock file `nucleo_s6/raiz/environment/sucesor_b3/integracion/requirements.lock` (pip 26.1.2, numpy 2.0.2, pymupdf 1.27.2.3, openpyxl 3.1.5, et_xmlfile 2.0.0, pandas 2.2.2, python-dateutil 2.9.0.post0, pytz 2026.3.post1, six 1.17.0, tzdata 2026.3) | Installed by the user from PyPI by hash. Not redistributed | Licenses declared in their metadata: MIT (pip, openpyxl, et_xmlfile, pytz, six), BSD (numpy, pandas), BSD or Apache-2.0 (python-dateutil), Apache-2.0 (tzdata). |
| PyMuPDF 1.27.2.3, `pymupdf-1.27.2.3-cp310-abi3-win_amd64.whl`, SHA-256 `d20f68ef…` | Installed by the user from PyPI with the lock file. Not included | Its metadata and `COPYING` say "Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License". The package's own code imports it in `nucleo_s6/raiz/herramientas/nacionales/nacionales.py` to read the INEI PDF in FAM01. MIT covers the package's own code. If a combined work covered by the AGPL-3.0 is distributed, its terms apply to the whole, including the availability of the corresponding source code. Installing the wheel separately does not by itself determine the scope of those terms. [Artifex terms](https://artifex.com/licensing). |
| xlrd 2.0.2, `nucleo_s6/raiz/herramientas/nacionales/vendor/xlrd-2.0.2-py2.py3-none-any.whl`, SHA-256 `ea762c3d…` (<http://www.python-excel.org/>) | Included, unmodified | Two BSD-style licenses, in `xlrd-2.0.2.dist-info/LICENSE` inside the wheel: "Portions copyright © 2005-2009, Stephen John Machin, Lingfo Pty Ltd" and "Copyright (c) 2001 David Giffin". The notices must be kept and the names may not be used to promote the package. The second requires this acknowledgment: "This product includes software developed by David Giffin <david@giffin.org>." |
| Microsoft Visual C++ Redistributable x64 | Installed by the user if missing | Microsoft's terms. PyMuPDF needs it on a clean Windows installation. |
