"""Construye el paquete derivado <destino>/src/paper2b: copia del nucleo del paquete (nucleo_s6/instalacion/src/paper2b,
verificada contra manifests/kernel_SHA256SUMS.txt), mas incidencia_estatutaria.py y los parches exactos de abajo, todos
con conteo 1. No modifica el nucleo del paquete. No sobrescribe: si <destino>/src existe, se detiene.

Uso: python -B -I construir_variante.py <destino>
"""
import difflib, hashlib, shutil, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIG = AQUI.parent / "nucleo_s6" / "instalacion" / "src"
SUMS = AQUI / "manifests" / "kernel_SHA256SUMS.txt"
DEST = Path(sys.argv[1]).resolve() / "src"

IMP_REL = "from . import incidencia_estatutaria as IE\n"
PARCHES = {
    "model.py": [
        ("from .numeric import brent, NumericError\n",
         "from .numeric import brent, NumericError\n" + IMP_REL),
        ("    return s.kappa0 * (1.0 + s.phi * tilde_f(tau_f, s.eta_f, s.phi))\n",
         "    return s.kappa0 * (1.0 + IE.omega(tau_f, s.phi) * tilde_f(tau_f, s.eta_f, s.phi))\n"),
        ("    tf = tilde_f(tau_f, s.eta_f, s.phi)\n    kF = s.kappa0 * (1.0 + s.phi * tf)\n",
         "    tf = tilde_f(tau_f, s.eta_f, s.phi)\n    om = IE.omega(tau_f, s.phi)\n    kF = s.kappa0 * (1.0 + om * tf)\n"),
        ("-k0 * s.phi * tf, -(tb + td * gamma + k0 * s.phi * tf))",
         "-k0 * om * tf, -(tb + td * gamma + k0 * om * tf))"),
    ],
    "encierros_modelo.py": [
        ("from . import model as M\n",
         "from . import model as M\n" + IMP_REL),
        ("    kF = mul(P.kappa0, add(1.0, mul(Ph, tf)))\n",
         "    om = IE.omega_ad(lf, Ph)\n    kF = mul(P.kappa0, add(1.0, mul(om, tf)))\n"),
        ("    return Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)\n",
         "    x = Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)\n    x._om = om\n    return x\n"),
        ('        phitf = mul(mul(k0, P.phi if not hasattr(x, "_ph") else x._ph), tf)\n',
         "        phitf = mul(mul(k0, x._om), tf)\n"),
    ],
    "motor_theta.py": [
        ("from paper2b import encierros_modelo as EM\n",
         "from paper2b import encierros_modelo as EM\nfrom paper2b import incidencia_estatutaria as IE\n"),
        ("    kF = mul(Q.kappa0, add(1.0, mul(Q.phi, tf)))\n",
         "    om = IE.omega_ad(lf, Q.phi)\n    kF = mul(Q.kappa0, add(1.0, mul(om, tf)))\n"),
        ("    return EM.Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)\n",
         "    x = EM.Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)\n    x._om = om\n    return x\n"),
        ("        phitf = mul(mul(k0, Q.phi), tf)\n",
         "        phitf = mul(mul(k0, x._om), tf)\n"),
    ],
    "modelos.py": [
        ('    kind = "modelo_teorico_v2_2"\n',
         '    kind = "modelo_teorico_v2_2_incidencia_estatutaria"\n'),
    ],
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main():
    if DEST.exists():
        sys.exit("variante/ ya existe; no se sobrescribe")
    esperado = {}
    for linea in SUMS.read_text(encoding="utf-8").splitlines():
        h, rel = linea.split(maxsplit=1)
        esperado[rel.lstrip("*")] = h
    for rel, h in esperado.items():
        if sha((ORIG.parent / rel).read_bytes()) != h:
            sys.exit("la copia del piloto no coincide con su manifiesto: " + rel)
    shutil.copytree(ORIG / "paper2b", DEST / "paper2b", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(AQUI / "incidencia_estatutaria.py", DEST / "paper2b" / "incidencia_estatutaria.py")
    diffs = []
    for nombre, reps in PARCHES.items():
        p = DEST / "paper2b" / nombre
        antes = p.read_bytes().decode("utf-8")
        s = antes
        fin = "\r\n" if "\r\n" in antes else "\n"            # se respeta el final de linea de cada archivo
        for viejo, nuevo in reps:
            viejo, nuevo = viejo.replace("\n", fin), nuevo.replace("\n", fin)
            n = s.count(viejo)
            if n != 1:
                sys.exit("CONTEO %d != 1 en %s: %r" % (n, nombre, viejo[:70]))
            s = s.replace(viejo, nuevo)
        p.write_bytes(s.encode("utf-8"))
        diffs += difflib.unified_diff(antes.splitlines(True), s.splitlines(True), "original/paper2b/" + nombre,
                                      "variante/paper2b/" + nombre, n=1)
    (DEST.parent / "DIFF_paper2b.txt").write_text("".join(diffs), encoding="utf-8")
    filas = []
    for f in sorted((DEST / "paper2b").rglob("*")):
        if f.is_file():
            filas.append("%s *%s" % (sha(f.read_bytes()), f.relative_to(DEST).as_posix()))
    (DEST.parent / "SHA256SUMS_variante.txt").write_text("\n".join(filas) + "\n", encoding="utf-8")
    iguales = sum(1 for fl in filas if esperado.get("src/" + fl.split("*", 1)[1]) == fl.split()[0])
    print("paquete derivado:", len(filas), "archivos;", iguales, "identicos al original;",
          len(filas) - iguales, "distintos o nuevos")


if __name__ == "__main__":
    main()
