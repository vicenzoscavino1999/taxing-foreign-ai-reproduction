"""Descubrimiento unittest de la suite del bloque 2 (D7/B/D8/S4): AST = descubrimiento = ejecutadas, cero omitidas.

Imprime la línea {"discovery": ...} que consumen s3_gate.run_discovery_suite y la compuerta S4. Con --informe <ruta>
escribe además un reporte JSON (passed/failed/errors/t2_measured) que D8_pre autentica por hash explícito. El informe se
VINCULA a lo que midió: manifiesto de código productor (code_manifest_sha256), código de la suite (suite_code_sha256),
huella del entorno RE-03 (environment_fingerprint_sha256, con conforms/discrepancias) y configuraciones del supremo en
que se midió T2 (measured_sup_configs). D8_pre y el freeze-run rechazan una suite de otra versión, código, entorno o
configuración. Evidencia de desarrollo en el entorno donde corra (3.12.10 documental): no es revalidación canónica.
"""
from pathlib import Path
import ast
import json
import os
import platform
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT, ROOT / 'src'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
sys.dont_write_bytecode = True


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def anclas_cli(argv):
    """Contexto EXTERNO del operador para informes tras S6; no se lee del paquete.
    Se vuelve a proporcionar completo al reubicar. Sin argumentos se conserva S4/S5.
    """
    campos = {"--s6-policy-sha256": "policy_sha256", "--s6-receipt-sha256": "receipt_sha256",
              "--s6-author": "author", "--s6-lanzamiento-sha256": "lanzamiento_sha256"}
    if not any(k in argv for k in campos):
        return None
    if not all(argv.count(k) == 1 and argv.index(k) + 1 < len(argv)
               and not argv[argv.index(k) + 1].startswith("--") for k in campos):
        raise ValueError("CONTEXTO_S6_EXTERNO_INCOMPLETO_O_DUPLICADO")
    return {v: argv[argv.index(k) + 1] for k, v in campos.items()}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    anclas = anclas_cli(argv)
    from herramientas.bloque2 import entorno as E
    E.set_runtime_conventions()
    pattern = 'test_*.py'
    discovered = unittest.defaultTestLoader.discover(str(HERE / 'pruebas'), pattern=pattern, top_level_dir=str(HERE))
    ids = [t.id() for t in flatten(discovered)]
    count = sum(isinstance(n, ast.FunctionDef) and n.name.startswith('test_')
                for q in (HERE / 'pruebas').glob(pattern) for n in ast.walk(ast.parse(q.read_text(encoding='utf-8'))))
    if len(ids) != len(set(ids)) or count != len(ids):
        raise RuntimeError('AST/descubrimiento del bloque 2 incoherentes')
    result = unittest.TextTestRunner(verbosity=2).run(discovered)
    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    from pruebas import analiticos
    t2 = analiticos.t2_measured()
    print(json.dumps({'discovery': 'unittest', 'ids': ids, 'ast_total': count, 'total': result.testsRun, 'passed': passed,
                      'skipped': len(result.skipped)}))
    print(f'{passed}/{result.testsRun} pruebas pasan')
    if '--informe' in argv:
        from herramientas.b import ejecutar_b as EB
        from herramientas.bloque2 import perfiles as P
        profile, profile_source = P.perfil_informe(ROOT, anclas=anclas)
        env = P.environment(ROOT, profile)
        out = Path(argv[argv.index('--informe') + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({'suite': 'herramientas/bloque2/run_suite.py', 'total': result.testsRun, 'passed': passed,
                                   'failed': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
                                   'ast_total': count, 't2_measured': repr(t2['max_error']), 't2_detail': t2['detail'],
                                   'python_version': platform.python_version(),
                                   'code_manifest_sha256': EB.code_manifest_sha256(ROOT),
                                   'suite_code_sha256': EB.code_manifest_sha256(ROOT, EB.SUITE_GLOBS),
                                   'environment_fingerprint_sha256': env['fingerprint_sha256'],
                                   'environment_conforms_approved': env['conforms'],
                                   'environment_mismatches': env['mismatches'],
                                   'environment_profile_source': profile_source,
                                   'measured_sup_configs': [c.as_dict() for c in analiticos.CONFIGS.values()],
                                   'note': 'evidencia de desarrollo; no revalidación canónica 3.12.4'},
                                  indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return 0 if result.wasSuccessful() and passed == count else 1


if __name__ == '__main__':
    raise SystemExit(main())
