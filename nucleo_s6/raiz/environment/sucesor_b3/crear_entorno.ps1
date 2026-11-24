param(
    [Parameter(Mandatory = $true)][string]$BasePython,
    [Parameter(Mandatory = $true)][ValidateSet("numerico", "integracion")][string]$Perfil,
    [Parameter(Mandatory = $true)][string]$Venv,
    [string]$PipCache = ""
)
# Receta CANDIDATA sucesora de environment/package_a/create_env.ps1 (bloque 3). No aprobada.
# - Intérprete base: la distribución OFICIAL de CPython 3.12.4 de python.org (python-3.12.4-amd64.zip, verificada contra
#   https://www.python.org/ftp/python/index-windows-recent.json); se exige el hash exacto de python.exe y python312.dll.
# - Perfil "numerico": exactamente pip + numpy (el lock aprobado de Paquete A, mismos bytes); contratos A/A-ter y B3-3.
# - Perfil "integracion": numerico + PyMuPDF (módulo fitz), openpyxl, pandas y sus dependencias; congelador,
#   documentación dependiente, D6, suites históricas/S3 y compuerta S4.
# - Instalación solo con hashes del lock, sin dependencias implícitas y solo binarios; después se comprueba que el
#   conjunto instalado es EXACTAMENTE el del lock (ningún paquete adicional) y que fitz lo provee PyMuPDF.
$ErrorActionPreference = "Stop"
$lock = Join-Path $PSScriptRoot (Join-Path $Perfil "requirements.lock")
$esperado = @{
    "python.exe"    = "fd5c46d73d29ba21b04c844bbaf9096066136526911230645a2a040d23fb612b";
    "python312.dll" = "21700f0bad5769a1b61ea408dc0a140ffd0a356a774c6eb0cc70e574b929d2e2"
}
$baseDir = Split-Path -Parent (Resolve-Path -LiteralPath $BasePython).Path
foreach ($f in $esperado.Keys) {
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $baseDir $f)).Hash.ToLower()
    if ($h -ne $esperado[$f]) { throw "interprete base no es CPython 3.12.4 oficial: $f $h" }
}
if (Test-Path -LiteralPath $Venv) { throw "venv ya existe: $Venv" }
& $BasePython -m venv $Venv
if ($LASTEXITCODE -ne 0) { throw "venv fallo" }
$venvPython = Join-Path $Venv "Scripts\python.exe"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
if ($PipCache -ne "") { $env:PIP_CACHE_DIR = $PipCache }
& $venvPython -m pip install --require-hashes --no-deps --only-binary=:all: -r $lock
if ($LASTEXITCODE -ne 0) { throw "instalacion bloqueada fallo" }
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONHASHSEED = "0"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:VECLIB_MAXIMUM_THREADS = "1"
$env:BLIS_NUM_THREADS = "1"
$env:TZ = "UTC"
$comprobacion = @'
import importlib.metadata as md, re, sys
import numpy as np
lock = sys.argv[1]
esperado = {}
for linea in open(lock, encoding="utf-8").read().splitlines():
    m = re.match(r"([A-Za-z0-9_.\-]+)\s*@\s*\S+/[A-Za-z0-9_.]+?-([0-9][A-Za-z0-9_.]*?)-(?:py|cp)", linea.strip())
    if m:
        esperado[m.group(1).lower()] = m.group(2)
instalado = {d.metadata["Name"].lower(): d.version for d in md.distributions()}
assert sys.version_info[:3] == (3, 12, 4), sys.version
assert np.__version__ == "2.0.2", np.__version__
assert instalado == esperado, ("conjunto instalado distinto del lock", sorted(set(instalado) ^ set(esperado)), instalado)
cfg = str(np.show_config(mode="dicts"))
assert "0.3.27" in cfg and "USE64BITINT" in cfg, "OpenBLAS 0.3.27 ILP64 requerido"
if "pymupdf" in esperado:
    import fitz, openpyxl, pandas
    prov = md.packages_distributions().get("fitz")
    assert prov and [p.lower() for p in prov] == ["pymupdf"], ("fitz no proviene de PyMuPDF", prov)
    assert "fitz" not in instalado, "paquete homonimo fitz instalado"
print("ENTORNO_OK", len(instalado), "paquetes exactamente del lock")
'@
$tmp = Join-Path $Venv "comprobar_entorno.py"
Set-Content -LiteralPath $tmp -Value $comprobacion -Encoding utf8
& $venvPython -B $tmp $lock
if ($LASTEXITCODE -ne 0) { throw "entorno no reproduce el lock" }
Remove-Item -LiteralPath $tmp
