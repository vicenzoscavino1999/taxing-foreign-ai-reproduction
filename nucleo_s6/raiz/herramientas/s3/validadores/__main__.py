"""CLI de solo lectura; hash externo obligatorio, nunca elige producto activo."""
import argparse
import json
from .core import Contracts

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root')
    p.add_argument('--manifest-sha256', required=True)
    p.add_argument('--ca2-bundle')
    p.add_argument('--bundle-sha256')
    p.add_argument('--source-root')
    args = p.parse_args()
    if any((args.ca2_bundle,args.bundle_sha256,args.source_root)) and not all((args.ca2_bundle,args.bundle_sha256,args.source_root)):
        p.error('C-A2 requiere --ca2-bundle, --bundle-sha256 y --source-root juntos')
    c = Contracts.load(args.root, args.manifest_sha256)
    graph = c.definitions()
    if args.ca2_bundle:
        from .ca2 import CA2Validator
        print(json.dumps(CA2Validator(c,args.source_root).read_bundle(args.ca2_bundle,args.bundle_sha256),ensure_ascii=False))
        return
    print(json.dumps({'status':'PASS', 'scope':'integridad normativa y declaraciones de fórmulas',
                      'formula_definitions':len(graph), 'economic_results_required':False,
                      'production_admission':False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
