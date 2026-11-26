# Taxing the Gains from Foreign AI: Fiscal Capture Frontiers in Developing Economies

Replication package · Vicenzo Scavino Alfaro · v1.1.0 · [Guía en español](docs/REFERENCE_es.md)

How much does withholding on payments to foreign AI suppliers add when a country already taxes domestic adopters’ profits? This version brings together the base analysis and the replication addendum described in Section S9 of the supplement. The instructions follow the revised article’s table numbers.

## Start here

In Windows PowerShell (64-bit Windows 10 or 11), open the folder containing the ZIP. Extract it into an empty, single-letter folder at the root of a drive. A short path accommodates the nested base inputs.

~~~powershell
Expand-Archive .\taxing-foreign-ai-reproduction-1.1.0.zip C:\p
Set-Location C:\p
~~~

If you already have the v1.0.0 Python environment, go straight to [Table 2](#reproduce-table-2) or [Table 4](#reproduce-table-4).

### Installation

Allow about 0.5 GB for the extracted files and 0.35 GB for Python and its packages. Install the [Microsoft Visual C++ x64 Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist) if needed. From the extracted folder, run the following once with an internet connection:

~~~powershell
$E = "$env:LOCALAPPDATA\reproduccion-paper2"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force $E | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.zip" -OutFile "$E\python-3.12.4-amd64.zip"
if ((Get-FileHash "$E\python-3.12.4-amd64.zip" -Algorithm SHA256).Hash -ne "35B4AC3BC273C85C1D8023CF8A29935E896189F532AB497573C6DA7FB12310EA") { throw "Unexpected Python download. Check the file before continuing." }
Expand-Archive "$E\python-3.12.4-amd64.zip" "$E\cpython-3.12.4-amd64"
powershell -NoProfile -ExecutionPolicy Bypass -File .\nucleo_s6\raiz\environment\sucesor_b3\crear_entorno.ps1 -BasePython "$E\cpython-3.12.4-amd64\python.exe" -Perfil integracion -Venv "$E\venv"
~~~

The installer prints `ENTORNO_OK` on success. If the environment is in a different location, append `-Python <path-to-venv\Scripts\python.exe>` to the commands below.

### Reproduce Table 2

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 check
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 sensitivities
~~~

The first command checks the base files. The second prints Table 2 and saves it as `table3.md` in the output folder shown on screen. The last two columns give the domestic-only ceiling as a percentage of the combined ceiling under each incidence rule. For example, with the gross design and a 15% withholding cap, the domestic-only ceiling is 33.52% of potential gains and the combined ceiling is 36.93%. Their ratio is **90.8%**. Each menu is evaluated at its own favorable structural point. The four rows give the article’s **81–91%** range after rounding.

### Reproduce Table 4

From the extracted folder, run `table6`, the package’s original name for this table. It reads the certificates included in the ZIP.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 table6
~~~

In the folder printed on screen, open `table6.md` for Table 4 or `table4_claims.csv` for the bounds on each claim. The gap is fiscal capacity minus the requirement, in shares of potential AI gains.

Table 4 groups the 1,728 claims by instrument and scope. The three country subrows break down withholding alone. The **1,712 inconclusive claims** each have a gap above +0.01 at one admissible point and below −0.01 at another, under both the linear allocation (E11) and statutory incidence. The **16 robust shortfalls** are all Mexican: withholding alone falls short of the debt-consistent requirement throughout the specified support. Section S6 of the supplement explains how the certificates apply under both rules.

## Find a result

To explore another result, use the corresponding action with `run.ps1`. Each action prints its output folder.

| Result | Action | What to open in the output folder |
|---|---|---|
| Table 2 and §5.1. Lower caps and the adoption threshold | `sensitivities` | `table3.md` for the ceilings and domestic shares, `threshold.md` for the threshold and whether the supremum is attained |
| Table 3. Base ceilings | `table6` | The [Table 4 command](#reproduce-table-4) also writes `table4_stored.md` with the ceilings for each menu and design |
| §5.6. Colombian classifications when both incidence and concealment costs change | `pilot` | `BALANCE.md` summarizes the 12 claims that change classification |
| S6.1. Tax menus at common structural points with informal adoption, and the prior-income reporting pilot | `extensions` | `results.md` compares the two designs. `menus/` contains the ceilings, grids and fixed-rate results |
| S6.2, S7.1 and S7.4. Withholding under alternative concealment costs, Mexico’s two bounds and Colombia with concealment costs held fixed | `extensions` | The same `results.md` explains the three exercises. `bounds.json` gives the underlying values and country claims |

All actions in the table use inputs in the ZIP. For the model and source files, see the [rate-cap guide](sensitivities/README.md) and the [guide to the additional results](sensitivities/extensions/README.md).

## Full base reproduction

Two further actions use external national-accounts files. Both require **Windows 11 x64, build 26200** for the base environment check. Use `winver` to see your build.

1. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 inputs`. This downloads the five public inputs and checks their hashes. If only the Peruvian workbook is missing, the command returns exit code 2. At this point you can run `table4` to **recompute the six favorable ceilings of Table 3**. To reproduce the entire base analysis, continue to step 2.
2. [Obtain the 2023 workbook from INEI](docs/DATA_SOURCES.md#peruvian-workbook) and save it as `PER_2023.xlsx` in the snapshots folder printed by `inputs`.
3. Run the two commands below. Continue to `full` once `verify` reports `VERIFY PASSED`. The example uses up to 12 processes for FAM01. Allow another 1–3 GB for outputs. The historical base analysis took about 17 hours across successive runs.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 verify
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 full -Processes 12
~~~

Read `completo/BALANCE.md` for the results. If interrupted, use the `resume -Run` command printed at startup with the same output folder. To inspect the 39 base operations before running them, use `plan`. The [coverage note](docs/FULL_RUN_HISTORY.md) explains which results are recomputed, regenerated or checked against archived outputs. The two sensitivity actions in the table above run separately from `full`.

## Citation and reuse

Cite the article, the version used and the [data sources](docs/DATA_SOURCES.md). The [Zenodo record](https://doi.org/10.5281/zenodo.24511871) groups the archived versions. The [companion dataset](https://doi.org/10.5281/zenodo.21381145) supplies the fiscal requirement. Code is licensed under MIT and original derived data, results and documentation under CC BY 4.0. Third-party inputs retain their own terms. See [CITATION.cff](CITATION.cff) and [LICENSE.md](LICENSE.md).
