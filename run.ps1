# Single entry point of the reproduction package for
# "Taxing the Gains from Foreign AI: Fiscal Capture Frontiers in Developing Economies".
#
# Run from the package folder, in Windows PowerShell:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 <action> [-Processes N] [-Run <folder>] [-Python <python.exe>]
#
# Actions (see README.md):
#   check          verify files and syntax, and report which distributed version this copy is (no computation)
#   plan           build the plan of the full analysis without computing (about 10 s)
#   pilot          run the pilot: FAM08 + FAM11 + FAM12 -> FAM10, 16 calls (about 1 min)
#   sensitivities  reproduce Table 3 and the Section 5.1 threshold results (about 1 min)
#   table6         regenerate Table 6 (and Table 4 from stored values) with FAM13 (about 10 s)
#   table4         recompute the favorable column of Table 4 from scratch: six FAM01 units (about 4 min; needs the downloaded inputs)
#   inputs         download the five national-accounts sheets that are not redistributed (needs internet)
#   verify         check that the copy is the complete version (with the six sheets) required by the full analysis
#   full           run the full analysis: 3,694 calls (many hours; needs the six sheets); -Processes 1..12 for FAM01
#   resume         resume an interrupted full run: -Run salidas/full_<time>/completo
#
# Every action writes to a new folder under salidas\ and never overwrites earlier output.
param(
  [Parameter(Position = 0, Mandatory = $true)]
  [ValidateSet("check", "plan", "pilot", "sensitivities", "table6", "table4", "inputs", "verify", "full", "resume")]
  [string]$Action,
  [ValidateRange(1, 12)][int]$Processes = 1,
  [string]$Run = "",
  [string]$Python = "$env:LOCALAPPDATA\reproduccion-paper2\venv\Scripts\python.exe"
)
$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $PSScriptRoot
$script:Code = 0
$ProcessesGiven = $PSBoundParameters.ContainsKey("Processes")

# Session variables of the numerical environment (the same for every action).
$env:PYTHONHASHSEED = "0"; $env:TZ = "UTC"
"BLIS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS" |
  ForEach-Object { Set-Item "env:$_" "1" }
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$snap = "nucleo_s6\raiz\fase2_datos\recepcion_nacional\versions\866aa139fb50578cae1ec5d77e1f98e6a5b87b56780aa1d95a118dffc5644984\snapshots"

function Stop-Run([string]$Message, [int]$ExitCode = 1) {
  if ($ExitCode -eq 0) { $ExitCode = 1 }
  $script:Code = $ExitCode
  throw $Message
}

# reproducir.py with the options of the package (-B -P -s -X utf8); stops on a non-zero exit code.
function Invoke-Package([string[]]$Arguments, [string]$Console = "") {
  if ($Console) {
    & $Python -B -P -s -X utf8 reproducir.py @Arguments > $Console 2>&1
  } else {
    & $Python -B -P -s -X utf8 reproducir.py @Arguments | Out-Host
  }
  if ($LASTEXITCODE -ne 0) {
    $hint = ""
    if ($Console) { $hint = " (console output in $Console)" }
    Stop-Run "reproducir.py $($Arguments -join ' ') ended with exit code $LASTEXITCODE$hint" $LASTEXITCODE
  }
}

# A helper script in isolated mode (-B -I); its output goes to the screen and its exit code is returned.
function Invoke-Tool([string]$Script, [string[]]$Arguments) {
  & $Python -B -I $Script @Arguments | Out-Host
  return $LASTEXITCODE
}

function Assert-Complete {
  $rc = Invoke-Tool "tools\fingerprint.py" @("--expect", "complete")
  if ($rc -ne 0) {
    Stop-Run ("this copy is not the complete version. The full analysis needs the six national-accounts sheets that are not " +
      "redistributed: run '.\run.ps1 inputs' for five of them and request PER_2023.xlsx from INEI (README.md, Inputs).")
  }
}

function Invoke-Action {
  if (-not (Test-Path -LiteralPath $Python)) {
    Stop-Run ("Python environment not found: $Python. Create it first (README.md, Installation), or pass " +
      "-Python <path to the environment's python.exe>.")
  }
  switch ($Action) {
    "check" {
      Invoke-Package @("revisar")
      $rc = Invoke-Tool "tools\fingerprint.py" @("--expect", "any")
      if ($rc -ne 0) { Stop-Run "the files of this copy differ from the distributed version (see 'recognized_as' above)" }
      Write-Host "CHECK PASSED"
    }
    "plan" {
      $out = "salidas/plan_$stamp"
      Invoke-Package @("general", "--modo", "plan", "--salida", $out)
      Write-Host "Plan: $out/plan.json; summary: $out/BALANCE.md"
    }
    "pilot" {
      $out = "salidas/pilot_$stamp"
      Invoke-Package @("general", "--modo", "piloto", "--salida", $out)
      Get-Content -Encoding UTF8 "$out/BALANCE.md" -TotalCount 9 | Out-Host
      Write-Host "Pilot: $out (BALANCE.md, plan.json, ejecucion.jsonl)"
    }
    "sensitivities" {
      $rc = Invoke-Tool "sensitivities\run_sensitivities.py" @("--out", "salidas/sensitivities_$stamp")
      if ($rc -ne 0) { Stop-Run "the sensitivities did not reproduce (see the checks above)" $rc }
    }
    "table6" {
      $out = "salidas/table6_$stamp"
      New-Item -ItemType Directory $out | Out-Null
      Invoke-Package @("fam13-reproducir", "--salida", "$out/fam13") "$out/fam13.console.txt"
      $rc = Invoke-Tool "tools\tables_from_fam13.py" @("$out/fam13")
      if ($rc -ne 0) { Stop-Run "Table 6 did not reproduce (see above)" $rc }
      Write-Host "Tables: $out/table6.md and $out/table4_stored.md"
    }
    "table4" {
      $missing = @("CHL_CEI.xls", "CHL_COU.xlsx", "COL_2023.xlsx", "COL_2024p.xlsx", "UN_bundle.tar") |
        Where-Object { -not (Test-Path -LiteralPath (Join-Path $snap $_)) }
      if ($missing) { Stop-Run "missing downloaded inputs ($($missing -join ', ')): run '.\run.ps1 inputs' first" }
      $out = "salidas/table4_$stamp"
      New-Item -ItemType Directory $out | Out-Null
      foreach ($d in "G", "N") {
        foreach ($j in "df", "d", "f") {
          $t0 = Get-Date
          Invoke-Package @("general", "--modo", "ensayo-fam01", "--unidad", "C2:${d}:${j}:sup", "--salida", "$out/${d}_${j}") "$out/${d}_${j}.console.txt"
          Write-Host ("  C2:{0}:{1}:sup recomputed in {2:N0} s" -f $d, $j, ((Get-Date) - $t0).TotalSeconds)
        }
      }
      $rc = Invoke-Tool "tools\table4.py" @($out)
      if ($rc -ne 0) { Stop-Run "Table 4 did not reproduce (see above)" $rc }
    }
    "inputs" {
      & $Python -B -P -s -X utf8 insumos_externos\obtener_insumos.py | Out-Host
      $rc = $LASTEXITCODE
      if ($rc -eq 0) { Write-Host "All six sheets are present: '.\run.ps1 verify' and '.\run.ps1 full' can run." }
      elseif ($rc -eq 2) { Write-Host "The five downloadable sheets are present; only PER_2023.xlsx is missing (request it from INEI: README.md, Inputs)." }
      else { Stop-Run "some downloadable input could not be obtained with the expected hash (see above)" $rc }
      $script:Code = $rc
    }
    "verify" {
      Assert-Complete
      Write-Host "VERIFY PASSED: complete version, ready for the full analysis"
    }
    "full" {
      Assert-Complete
      Invoke-Package @("revisar")
      $out = "salidas/full_$stamp"
      New-Item -ItemType Directory $out | Out-Null
      Invoke-Package @("general", "--modo", "plan", "--salida", "$out/plan_previo") "$out/plan_previo.console.txt"
      Write-Host "Plan conforms. Full run with $Processes FAM01 process(es) started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') -> $out/completo"
      Write-Host "If it is interrupted: .\run.ps1 resume -Run $out/completo"
      & $Python -B -P -s -X utf8 reproducir.py general --modo completo --procesos-fam01 $Processes --salida "$out/completo" | Out-Host
      $script:Code = $LASTEXITCODE
      if (Test-Path "$out/completo/BALANCE.md") { Get-Content -Encoding UTF8 "$out/completo/BALANCE.md" -TotalCount 11 | Out-Host }
      Write-Host "Finished at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') with exit code $script:Code"
    }
    "resume" {
      if (-not $Run) { Stop-Run "give the run folder: .\run.ps1 resume -Run salidas/full_<time>/completo" }
      $r = $Run.Replace('\', '/').TrimEnd('/')
      if (-not (Test-Path -LiteralPath (Join-Path $r "control.json"))) { Stop-Run "not a resumable run: $r/control.json is missing" }
      Assert-Complete
      Invoke-Package @("revisar")
      $a = @("general", "--reanudar", "--salida", $r)
      if ($ProcessesGiven) { $a += @("--procesos-fam01", "$Processes") }
      & $Python -B -P -s -X utf8 reproducir.py @a | Out-Host
      $script:Code = $LASTEXITCODE
      if (Test-Path "$r/BALANCE.md") { Get-Content -Encoding UTF8 "$r/BALANCE.md" -TotalCount 11 | Out-Host }
    }
  }
}

# Python writes UTF-8 (-X utf8); read it as UTF-8 and restore the console encoding afterwards.
$previousEncoding = [Console]::OutputEncoding
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch { }
try {
  Invoke-Action
} catch {
  if ($script:Code -eq 0) { $script:Code = 1 }
  Write-Host ""
  Write-Host "FAILED: $($_.Exception.Message)"
} finally {
  try { [Console]::OutputEncoding = $previousEncoding } catch { }
}
exit $script:Code
