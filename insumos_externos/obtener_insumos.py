"""Obtiene las hojas de cuentas nacionales que la copia pública no incluye y comprueba su huella.

Seis archivos de la recepción nacional de FAM01 no se distribuyen con el paquete, porque sus condiciones no
permiten redistribuirlos o no lo dicen (docs/DATA_SOURCES.md):
- cinco se descargan aquí de su URL oficial y solo se guardan si su tamaño y su sha256 son los que espera el paquete;
- UN_bundle.tar se rehace con el archivo AMA descargado y los otros siete miembros, que vienen en un_bundle/;
- PER_2023.xlsx no se publica en ninguna URL: el script solo comprueba si está y con qué huella.

Uso, desde la carpeta del paquete:  & $py -B -P -s -X utf8 insumos_externos/obtener_insumos.py
No sobrescribe un archivo que ya esté con otra huella. Solo usa la biblioteca estándar.
Código de salida: 0 si los seis archivos están con su huella; 2 si solo falta PER_2023.xlsx; 1 en cualquier otro caso.
"""
import hashlib
import io
import os
import sys
import tarfile
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
SNAP = BASE / ("nucleo_s6/raiz/fase2_datos/recepcion_nacional/versions/"
               "866aa139fb50578cae1ec5d77e1f98e6a5b87b56780aa1d95a118dffc5644984/snapshots")
AGENTE = "obtener-insumos/1 (paquete de reproduccion)"

# archivo, URL oficial, bytes, sha256
DESCARGAS = (
    ("CHL_CEI.xls", "https://si3.bcentral.cl/estadisticas/Principal1/informes/AnuarioCCNN/excel2025/CEI_anuario_2013-2024.xls",
     416256, "84f025caad43d5df78e5197bf038bb8e790aa3e4e0beb4972503771f11da0460"),
    ("CHL_COU.xlsx", "https://si3.bcentral.cl/estadisticas/Principal1/informes/AnuarioCCNN/excel2025/2023_Cuadros_12x12.xlsx",
     73484, "4fa4dc3da102ec26a07d2215d0f4fabea2be1a348077f6c5aee2b805d69ed058"),
    ("COL_2023.xlsx", "https://www.dane.gov.co/files/operaciones/PIB/anex-CuentasNalAnuales-CuentasEconomicasIntegradas-2023p.xlsx",
     318826, "fa799bfe8e087ba1921a7c9623490748d0b24985fdf14acb0e53e155c125da5c"),
    ("COL_2024p.xlsx", "https://www.dane.gov.co/files/operaciones/PIB/anex-CuentasNalAnuales-CuentasEconomicasIntegradas-2024p.xlsx",
     331132, "18de220550313fddd23e792bf08b5090867f6a7d24d50f9e23a55f7cab209613"),
)
AMA = ("https://unstats.un.org/unsd/amaapi/api/file/1", 2255482,
       "2434ffdbcfc527314cf5bae6e3530cc8be8138cfeae96c1aea6a979a213ee29f")
BUNDLE = ("UN_bundle.tar", 2600960, "03e965f45a01f0fc4eb5ab8629a65ea3837784c1c50d898696dcb823866c044b")
# Miembros de UN_bundle.tar en su orden; None = el archivo AMA que se descarga.
MIEMBROS = (
    ("ama_gdp_current_ncu.xls", None),
    ("bundle_manifest.json", "38b0a7f85b6f346a99f2ca692b45e51e232566c2be319436dbe441d7ea4c12ad"),
    ("chl_gdp_footnote.html", "00aacc739384e665b9f23ead747bd969369c646a540405d87a2fa41deb67cb52"),
    ("chl_gos_footnote.html", "e80f6755f8d4d94544ea7730e9a766c7f93b2c86514e2ca0bb5517bb2fac2d82"),
    ("table401_CHL.zip", "b23a2b4f530cdc15797c00b148afa23feb27edea35b07f66c734060e8d488ed4"),
    ("table401_COL.zip", "7ca3768c4ca49d190597afde2541773c150d99090ac3d9154ab6ccc3540be25d"),
    ("table401_MEX.zip", "e7d26430ad401bf169fff57f03d4e73ff0639b4a0e68fc22cb1d986bf7a97c7d"),
    ("table401_PER.zip", "68fa021932e451fc509ff67f2f547ac3ce7acc69bbaa45fb85f24bae52d9609d"),
)
PER = ("PER_2023.xlsx", 251614, "dca6ebf37c2c0865a7d579cf73ade2358a459ea51441e2a2ee9d6b4412f158e3")


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def presente(nombre, esperado):
    """None si falta; True si está con la huella esperada; False si está con otra."""
    ruta = SNAP / nombre
    if not ruta.is_file():
        return None
    return sha(ruta.read_bytes()) == esperado


def descargar(url, n, esperado):
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(peticion, timeout=180) as respuesta:
        datos = respuesta.read()
    if len(datos) != n or sha(datos) != esperado:
        raise ValueError("la fuente entrega otra versión (%d bytes, sha256 %s…); se esperaba %d bytes y %s…"
                         % (len(datos), sha(datos)[:12], n, esperado[:12]))
    return datos


def guardar(nombre, datos):
    destino = SNAP / nombre
    parcial = destino.with_name(destino.name + ".parcial")
    parcial.write_bytes(datos)
    os.replace(parcial, destino)


def rehacer_bundle(ama):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for nombre, esperado in MIEMBROS:
            if esperado is None:
                datos = ama
            else:
                datos = (AQUI / "un_bundle" / nombre).read_bytes()
                if sha(datos) != esperado:
                    raise ValueError("el miembro incluido %s no tiene su huella" % nombre)
            info = tarfile.TarInfo(nombre)
            info.size, info.mode, info.mtime = len(datos), 0o644, 0
            tar.addfile(info, io.BytesIO(datos))
    datos = buf.getvalue()
    if len(datos) != BUNDLE[1] or sha(datos) != BUNDLE[2]:
        raise ValueError("el tar rehecho no coincide con la huella esperada")
    return datos


def main():
    if not SNAP.is_dir():
        print("No existe la carpeta de la recepción nacional: %s" % SNAP)
        return 1
    fallos = 0
    for nombre, url, n, esperado in DESCARGAS:
        estado = presente(nombre, esperado)
        if estado is True:
            print("%s: ya está, huella conforme" % nombre)
            continue
        if estado is False:
            print("%s: ya existe con otra huella; no se toca. Bórrelo y repita, o revise la copia." % nombre)
            fallos += 1
            continue
        try:
            guardar(nombre, descargar(url, n, esperado))
            print("%s: descargado de %s, huella conforme" % (nombre, url))
        except Exception as error:  # red, servidor o versión distinta: se informa y se sigue con el resto
            print("%s: no se pudo obtener de %s: %s" % (nombre, url, error))
            fallos += 1
    nombre, n, esperado = BUNDLE
    estado = presente(nombre, esperado)
    if estado is True:
        print("%s: ya está, huella conforme" % nombre)
    elif estado is False:
        print("%s: ya existe con otra huella; no se toca. Bórrelo y repita, o revise la copia." % nombre)
        fallos += 1
    else:
        try:
            guardar(nombre, rehacer_bundle(descargar(*AMA)))
            print("%s: rehecho con el archivo AMA de %s, huella conforme" % (nombre, AMA[0]))
        except Exception as error:
            print("%s: no se pudo rehacer: %s" % (nombre, error))
            fallos += 1
    nombre, n, esperado = PER
    estado = presente(nombre, esperado)
    if estado is True:
        print("%s: ya está, huella conforme" % nombre)
    elif estado is False:
        print("%s: existe con otra huella; no es la versión que usa el paquete." % nombre)
        fallos += 1
    else:
        print("%s: solicite el libro de 2023 al INEI (docs/DATA_SOURCES.md, «Peruvian workbook»). "
              "Guárdelo en %s; "
              "debe tener %d bytes y sha256 %s." % (nombre, SNAP, n, esperado))
        return 1 if fallos else 2
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
