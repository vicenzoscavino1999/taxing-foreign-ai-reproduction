# Reproduction package — *Taxing the Gains from Foreign AI: Fiscal Capture Frontiers in Developing Economies*

**Author:** Vicenzo Scavino Alfaro · **Package version:** 1.0.0 (2026-11-24) · **License:** MIT for code, CC BY 4.0 for
derived data, results and texts ([LICENSE.md](LICENSE.md)) · **DOI:** to be added when the package is deposited.

This package reproduces the numerical results of the article and of its technical supplement (the 40-page version
with supplement S1–S10). Everything runs on Windows from one entry point, `run.ps1`.

## What question the package answers

The article asks how much of the gains from foreign artificial intelligence a small developing economy can turn into
tax revenue with two instruments: a domestic tax on adopters (gross or net of the payment to the supplier) and a
withholding tax on payments to the foreign supplier. The answer is a certified *capture ceiling*: the largest revenue,
as a share of the potential AI gain, that each instrument menu can raise at points of declared structural supports for
Peru, Colombia and Mexico. The application confronts these ceilings with the cost of universal social protection and
classifies 1,728 claims.

The package recomputes the ceilings, the frontier meshes and the confrontation with the article's code; regenerates
tables from stored inputs; and verifies the integrity of stored outputs. Each operation compares what it produces with
the accepted result and reports whether the reproduction is accepted.

## Which command reproduces which result

Run every command from the package folder (see [Installation](#installation)). Outputs go to a new folder under
`salidas\`, named with the UTC time of the run.

| Article | Command | Output file | Time | Needs |
|---|---|---|---|---|
| **Table 3**: ceilings under lower rate caps, domestic share 81–91 % | `.\run.ps1 sensitivities` | `salidas\sensitivities_<time>\table3.md` (and `table3.csv`) | 1 min | the package |
| **§5.1**, formal adoption as the limit: 0.7821 and 0.5518 under the statutory allocation, threshold near τ_d = 0.588, and near 0.82 and 0.77 with the 0.35 cap | the same run | `salidas\sensitivities_<time>\threshold.md` | — | the package |
| **Table 6**: classification of the 1,728 claims | `.\run.ps1 table6` | `salidas\table6_<time>\table6.md` | 10 s | the package |
| **Table 4**: ceilings at the witnesses, from the stored certified values | the same run | `salidas\table6_<time>\table4_stored.md` | — | the package |
| **Table 4**, favorable column recomputed from scratch (0.7917, 0.5628, 0.5475, 0.4380, 0.2737) | `.\run.ps1 table4` | `salidas\table4_<time>\table4.md` | 4 min | the five downloadable sheets (`.\run.ps1 inputs`) |
| **§5.6**, Colombia's macro block under φ/2 (12 claims become robustly infeasible) | `.\run.ps1 pilot` | `salidas\pilot_<time>\BALANCE.md` | 1 min | the package |
| Base analysis — 39 operations, 14 families | `.\run.ps1 full -Processes 12` | `salidas\full_<time>\completo\BALANCE.md` | many hours | all six sheets that are not redistributed |

`full` runs the base analysis only; to reproduce also Table 3 and the adoption threshold of §5.1, run
`.\run.ps1 sensitivities` separately.

In the table, `.\run.ps1 <action>` stands for `powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 <action>`,
the form used in the rest of this page. (Windows usually blocks a script extracted from a downloaded archive when it is
called directly; the full form works with the default settings.)

Table 3 and the §5.1 results are sensitivities designed after the base results (article, Appendix C). In the gross
design under the statutory allocation with caps of 0.6, the *value* of the supremum (0.7821) is certified, but whether
some pair of rates *attains* it remains undecided; the threshold near 0.588 comes from a floating-point diagnostic, not a
certification. Details: [sensitivities/README.md](sensitivities/README.md).

## Requirements

- **Windows 11 x64, build 26200** (version 25H2; to see yours, press Win+R and run `winver`) is the validated
  environment for the operations that apply the RE-03 environment control: `table4` and `full`. Their FAM01
  recomputations are accepted only if the environment conforms to the package's environment manifest
  (`nucleo_s6\raiz\environment\sucesor_b3\integracion\environment_manifest.json`), which is validated only for the
  platform `Windows-11-build-26200`; the revision after the dot (such as 26200.6584) is not part of the check, and any
  other build is not covered without its own validation. The actions that only consult stored results or hashes
  (`check`, `plan`, `table6`, `verify`) and `inputs` do not apply RE-03 and do not depend on the build (64-bit
  Windows 10 or 11); `pilot` and `sensitivities` recompute without requiring RE-03 (the pilot records its assessment)
  and were tested on build 26200. Every action needs Windows PowerShell 5.1 (included in Windows), and the
  installation needs an internet connection.
- About 1 GB free: 80 MB for the archive, 510 MB for the extracted package, 345 MB for the Python environment, and up
  to 60 MB for the output of each action (plan 11 MB, pilot 56 MB, table4 59 MB). The full analysis writes its output
  inside the package folder; allow 1–3 GB more (an estimate).
- The **Microsoft Visual C++ Redistributable x64**, which PyMuPDF needs. If it is missing, creating the environment can
  stop with `DLL load failed while importing _extra`. Install it before step 1 of the installation (Windows may ask
  for administrator permission): [Microsoft downloads](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist).
- **Extract the package to a short path**: a folder of at most one letter at the root of a drive, such as `C:\p` or
  `D:\p`, with `run.ps1` directly inside it. The longest relative path in the package has 254 characters, so from
  `C:\p` the full path has 259, the most that Windows allows unless long paths are enabled. Inside a profile subfolder
  the integrity check failed because of path length.

The installation and the pilot were tested on a freshly installed virtual machine with Windows 11 Pro x64 25H2 (build
26200.6584) and Visual C++ x64 14.52.37029. This version of the package was tested as described in
[docs/FULL_RUN_HISTORY.md](docs/FULL_RUN_HISTORY.md).

## Installation

The installation downloads the official CPython 3.12.4 interpreter and creates a Python environment in
`%LOCALAPPDATA%\reproduccion-paper2`, outside the package and without touching any other Python on the computer. (It
lives outside the package because the read registry of the families counts everything inside the package folder as
"from the package".) To uninstall, delete that folder. To use another folder, change `$E` below and pass
`-Python <folder>\venv\Scripts\python.exe` to `run.ps1`.

Open Windows PowerShell in the folder where you saved the archive, extract it to `C:\p` (the archive has no top folder,
so `run.ps1` lands directly in `C:\p`; extraction takes about two minutes) and move there:

```powershell
Expand-Archive .\taxing-foreign-ai-reproduction-1.0.0.zip C:\p
```

```powershell
Set-Location C:\p
```

**Step 1. Interpreter.** Download CPython 3.12.4 (64-bit, python.org) and check its hash before using it:

```powershell
$E = "$env:LOCALAPPDATA\reproduccion-paper2"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory $E | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.zip" -OutFile "$E\python-3.12.4-amd64.zip"
if ((Get-FileHash -Algorithm SHA256 "$E\python-3.12.4-amd64.zip").Hash -ne "35B4AC3BC273C85C1D8023CF8A29935E896189F532AB497573C6DA7FB12310EA") { throw "The downloaded zip does not match the published hash; stop here." }
Expand-Archive "$E\python-3.12.4-amd64.zip" "$E\cpython-3.12.4-amd64"
```

If the download is interrupted or the hash differs, run the `Invoke-WebRequest` line again and check the hash before
`Expand-Archive`. If an incomplete extraction exists, use a new folder for `$E`.

**Step 2. Environment.** Create the environment with the package's recipe. It checks the hashes of `python.exe` and
`python312.dll`, installs the 10 packages of the lock file by their SHA-256 only, and verifies that nothing else is
installed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File nucleo_s6\raiz\environment\sucesor_b3\crear_entorno.ps1 -BasePython "$E\cpython-3.12.4-amd64\python.exe" -Perfil integracion -Venv "$E\venv"
```

It must end with `ENTORNO_OK 10 paquetes exactamente del lock`. If not, do not continue.

`run.ps1` sets the numerical environment of every run itself (`PYTHONHASHSEED=0`, `TZ=UTC` and one thread for BLIS,
MKL, NUMEXPR, OMP, OPENBLAS and VECLIB) and uses `%LOCALAPPDATA%\reproduccion-paper2\venv\Scripts\python.exe`.

## 1. Check the package and run the pilot

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 check
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 plan
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 pilot
```

**How to recognize success:**

- `check` (a few seconds, no computation) prints `Archivos y sintaxis conformes. Ningún cálculo ejecutado.`, then a
  fingerprint with `"recognized_as": "public"` (the archive as distributed), `"public_with_downloaded_sheets"` (after
  `inputs`, without `PER_2023.xlsx`) or `"complete"` (with the six sheets), the state of each of the six sheets, and
  ends with `CHECK PASSED`.
- `plan` (about 10 s, no computation) ends with a summary that includes `"plan_cumple": true`,
  `"plan sin cálculo": 39` and `"conforme": true`.
- `pilot` (about 1 minute) runs FAM08 + FAM11 + FAM12 → FAM10. Its summary includes `"aceptado": 16`,
  `"cumple": true` in `resultado_exp8`, `"lecturas_fuera_del_paquete": 0` and `"conforme": true`. The first lines of
  `BALANCE.md` say `Conforme: **sí**` and `Llamadas del modo: aceptado 16`, then the Exp8 result: 1728 claims,
  12 changed (all Colombian and `robust_infeasible`) and 1716 identical; the final COV split is
  `inconclusa_preservada` 1700, `robust_infeasible` 12 and `no_decidida_por_testigos` 16.
- Every action ends with exit code 0 (`inputs` ends with 2 when only `PER_2023.xlsx` is missing); a failure prints
  `FAILED:` and the reason.

**If something fails:** open `BALANCE.md` in the output folder. Each row is an operation; the column «En esta
ejecución» says `no conforme` or `pendiente: bloqueada (<motivo>)` with the affected call (`Pxxxxx`), whose error output
is in `registro\Pxxxxx.err`. If the plan does not conform, the errors are in `plan.json`, field `comprobaciones`. If
`check` reports missing files or a different hash, the copy is incomplete or altered.

The program messages and output files of the package are in Spanish; the summaries written by `run.ps1`'s helpers
(`table3.md`, `threshold.md`, `table6.md`, `table4*.md`) are in English.

## 2. Reproduce the main results

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 sensitivities
```

Recomputes Table 3 and the §5.1 results (25 computations, each in its own process), compares every certified value
bit for bit with the accepted results stored in `sensitivities\reference\`, and checks the rounded cells against the
printed article. It ends with `15/15 checks passed … SENSITIVITIES REPRODUCED`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 table6
```

Runs FAM13, which regenerates the claim-level confrontation table from the stored certified values and checks the
bytes against the accepted product, then writes Table 6 and Table 4 (stored values). It ends with
`TABLES 6 AND 4 REPRODUCED`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 inputs
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 table4
```

`table4` recomputes the six favorable witnesses of Table 4 from scratch with FAM01 (structural point, frontier,
certified ceiling, productive validation and comparison with the accepted original). It needs the five downloadable
sheets, so run `inputs` first (see [Inputs](#inputs-not-included-in-the-archive)). It ends with
`TABLE 4 (FAVORABLE COLUMN) REPRODUCED`.

## 3. Run the full analysis

The full analysis is the base analysis: the 39 operations of the 14 families, in 3,694 calls of the public plan,
including the 1,762 numerical units of FAM01. The historical closure accepted 3,708 calls, because there the 15 FAM01
units that version 1.0.0 groups in GT28 were 15 separate calls ([docs/FULL_RUN_HISTORY.md](docs/FULL_RUN_HISTORY.md)).
Table 3 and §5.1 are not part of it: they come from `sensitivities` (section 2).

1. Obtain the six sheets that are not redistributed ([Inputs](#inputs-not-included-in-the-archive)).
2. Check that the copy is complete:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 verify
   ```

   It ends with `VERIFY PASSED`.
3. Launch the run, with up to 12 simultaneous FAM01 calls (each single-threaded):

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 full -Processes 12
   ```

- **Time.** The historical full run took about 16.5 hours of wall-clock time (FAM01 about 11 h with 12 processes) on a
  desktop with 16 logical processors. With a single FAM01 process it would take much longer (57–134 h for FAM01 alone,
  by the pilot timings).
- **Keep the computer on**, without sleep or restarts. Each process of `reproducir.py` asks Windows not to throttle it
  for power saving, so that a run in a minimized or hidden window keeps its speed (in the historical run, without this,
  two FAM01 groups ran out of time).
- **If the run is interrupted** (power cut, closed window, Ctrl+C), resume it on the same folder; accepted calls whose
  outputs are intact are not recomputed:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 resume -Run salidas/full_<time>/completo
  ```

- **Progress:** `salidas\full_<time>\completo\ejecucion.jsonl` gets one line per finished call
  (`Get-Content ejecucion.jsonl -Tail 3 -Wait`). `BALANCE.md` is written at the end: success is `Conforme: **sí**` with
  all calls accepted and all 39 keys complete.

FAM01 puts the units of an expensive structural key in one process, so the expensive ceiling is computed once and
reused in memory (rule GRUPOS-TECHO-C2-v1, 29 groups with their own time limits); the other units run one per process
with a 600 s limit. The historical record of the full run, and how this version differs from the version that closed it,
are in [docs/FULL_RUN_HISTORY.md](docs/FULL_RUN_HISTORY.md).

## Inputs not included in the archive

FAM01 reads 18 national-accounts sheets. Six are not included because their terms do not allow redistribution or do
not mention it ([docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)). `check`, `plan`, `pilot`, `sensitivities` and `table6`
do not need them; `table4` needs the five downloadable ones; `verify` and `full` need all six.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 inputs
```

- Downloads `CHL_CEI.xls`, `CHL_COU.xlsx`, `COL_2023.xlsx` and `COL_2024p.xlsx` from their official URLs, and the UN
  AMA file from which it rebuilds `UN_bundle.tar` (about 3.4 MB in total). Each file is kept only if its SHA-256 is the
  one the package expects. The URLs and hashes are at the top of `insumos_externos\obtener_insumos.py`.
- If a source withdraws or changes a file, the script says so and does not keep it; that exact version then has to be
  requested from the source.
- Exit code 0 if all six sheets are present, 2 if only `PER_2023.xlsx` is missing, 1 otherwise.
- **Peru 2023, available on request.** INEI provided the author with the workbook `PBI_Imp_2023_CEIyCOU_R.xlsx`. To
  request that version, write to `infoinei@inei.gob.pe` giving the original file name and its four sheets: Resumen,
  CEI_2023, COU_2023 and Enlaces. Delivery depends on INEI ([INEI information center](https://www.inei.gob.pe/media/difusion/app/files/basic-html/page36.html)).
  Save the file unedited as `PER_2023.xlsx` in the folder that the script names and run `inputs` again. The version
  used has 251,614 bytes and SHA-256 `dca6ebf37c2c0865a7d579cf73ade2358a459ea51441e2a2ee9d6b4412f158e3`. The CEI and
  COU sheets published separately by INEI are useful for reference, but FAM01 also reads the Resumen sheet of the
  original workbook, so the units that use Peru 2023 need that workbook.

## What is recomputed, regenerated and verified

The catalog (`catalogo.json`) divides the work into 39 operations ("keys") in 14 families, of three kinds:

- **Recomputed (17 keys):** the numbers are computed again from the stored inputs with the article's code and compared
  with the accepted values: the 1,762 numerical units of FAM01 (structural point, frontier, certified ceiling and
  validation at each witness, R2 and R3), the R1 global extremes (FAM02), the regime breaks and Q (FAM03), the
  elasticity, λ and coordinate meshes of lots 1 and 2 and E4 (FAM04–FAM07), the ENF meshes and ceilings (FAM08), the
  high witness of T8 (FAM09), the 26 COV ceilings under φ/2 and the COV12 blocks B1/B2 (FAM11), and the K1 cases of P7
  (FAM12).
- **Regenerated (12 keys):** a product is rebuilt from stored inputs and compared byte for byte or value by value with
  the accepted one: the E4 and G/N conciliations, the ENF pairs and integral, the λ, capture and C5B products of T8,
  the Exp8 ENF claims, synthesis and integration (FAM10), and the P7 aggregate and local Q.
- **Verified for integrity (10 keys):** stored products whose computation is not repeated are checked against their
  accepted hashes and their provenance: the R3 frame, the historical elasticities, the reused and previous COORD
  comparisons, the T8 history, the historical tables and validations of FAM13 (T1/T2/T7; Table 6 comes from T7, which
  FAM13 regenerates from stored values and checks byte for byte), and the G/N, §18.7 and adoption records of FAM14.

The plan of the full analysis links each key to its calls and to the comparison or verification of its products;
`BALANCE.md` says, key by key, what was computed, regenerated, verified or not run. The detailed technical reference
(organization, environment, every command, in Spanish) is [docs/REFERENCE_es.md](docs/REFERENCE_es.md); the notes on
each family, written during the preparation (in Spanish), are in `docs/notes_es/`.

## Contents

| Path | What it is |
|---|---|
| `run.ps1` | the single entry point |
| `reproducir.py`, `src/` | command-line interface and the adapters of the 14 families |
| `nucleo_s6/` | the scientific core (model, certifier, national-accounts bridge, environment recipe) |
| `datos/`, `referencias/` | inputs, and the accepted values the results are compared with |
| `catalogo.json`, `fuentes_*.json` | catalog of the 39 operations and the hash manifests checked by `check` |
| `sensitivities/` | the post-base sensitivities of Table 3 and §5.1, with their inputs and accepted references |
| `insumos_externos/` | the script that obtains the sheets not included, and six UNdata files |
| `tools/` | fingerprint of the copy and the table summaries |
| `docs/` | data sources and terms, history of the full run, technical reference and family notes |
| `extraccion/registro/lecturas_ejecucion_fam02.json` | the list of inputs that FAM02 reads at run time |

## How to cite

Cite the article and this package; cite the data sources as indicated in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
The citation metadata are in [CITATION.cff](CITATION.cff).

```text
Scavino Alfaro, Vicenzo (2026). Reproduction package for "Taxing the Gains from Foreign AI: Fiscal Capture Frontiers in Developing Economies". Version 1.0.0. DOI to be added on deposit.
```

The convertible requirement of the application comes from version 1.1.1 of the replication package of the companion
analysis: Scavino, Vicenzo (2026). *Code and data for: AI, Fiscal Space, and Social Protection in Four Latin American
Economies: A Scenario-Based Threshold Framework*. Zenodo, version 1.1.1. <https://doi.org/10.5281/zenodo.21381145>.
That DOI identifies the companion package, not this one.

## License

The package's own code is under the MIT License; its derived data, results and texts under CC BY 4.0. Third-party data
and software keep their own terms ([docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)). Exact scope: [LICENSE.md](LICENSE.md).
