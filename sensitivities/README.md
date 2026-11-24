# Post-base sensitivities: Table 3 and the adoption threshold (Section 5.1)

These computations were designed **after** the base results (see the article's appendix on chronology). They are not
part of the base specification and do not change any base result. They cover two structural points only: the favorable
witnesses of Table 4, with the structural point held fixed and the tax rates re-optimized.

Run them from the package root with the single entry point:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 sensitivities
```

or directly, with the package Python and the session variables of the main README:

```powershell
& $py -B -I sensitivities\run_sensitivities.py
```

About one minute. Success ends with `SENSITIVITIES REPRODUCED` and exit code 0. Results go to a new folder
`salidas\sensitivities_<UTC time>\`: `table3.md`, `table3.csv`, `threshold.md`, `summary.json`, one JSON and one console
log per computation, and the statutory variant of the kernel that was built for the run (`variant\`).

## What is computed

| Article | Computation | Script |
|---|---|---|
| Table 3, column (E11) | combined menu at caps (0.35; 0.15) and (0.35; 0.30), gross and net designs | `calculo.py E11 …` |
| Table 3, column Statutory | the same four ceilings under the statutory allocation | `calculo.py estatutaria …` |
| Table 3, columns d only and f only | each menu at its own favorable witness, caps 0.35 (d) and 0.15/0.30 (f) | `testigos_propios.py` |
| §5.1, 0.7821 and 0.5518 | combined menu, caps (0.6; 0.6), statutory allocation; (E11) as control (0.7917, 0.5628) | `calculo.py` |
| §5.1, threshold near 0.588 | floating-point diagnostic of the formal-adoption jump at τ_f = 0.6 | `diagnostico_salto.py` |
| §5.1, thresholds near 0.82 and 0.77 | floating-point diagnostic of the adoption margin with the 0.35 cap | `diagnostico_umbral.py` |

Certified ceilings use the package's certifier (`ModeloTeorico.capture_ceiling`, production configuration,
tolerance 1e-7). The two diagnostics evaluate the model in floating point; they locate the threshold but are **not**
certifications.

**Scope.** In the gross design under the statutory allocation with caps of 0.6, the *value* of the supremum (0.7821) is
certified, but whether some pair of rates *attains* it is undecided (`SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE`). Every
combined ceiling of Table 3 is attained at the caps. Under the statutory allocation another admissible point could have
a higher favorable ceiling; that was not examined. No ceilings over the support or classifications are recomputed here.

## What is checked

- the package kernel `nucleo_s6/instalacion/src` (37 files) against `manifests/kernel_SHA256SUMS.txt`;
- the six witness-row files in `inputs/` against `inputs/SHA256SUMS.txt` (they are the rows of the accepted
  computations of the full run; `testigos_propios.py` also checks the tied witnesses against
  `referencias/fam01/originales/`);
- the statutory variant, built from the kernel by `construir_variante.py` (one new module, `incidencia_estatutaria.py`,
  and exact patches to four files; formulation in `VARIANTE_ESTATUTARIA.md`, in Spanish), against
  `manifests/variant_SHA256SUMS.txt`;
- every result against the accepted results in `reference/accepted.json`, bit for bit (certified value, error,
  interval, status, rates, box count; whole documents for the diagnostics);
- the rounded cells of Table 3 and the numbers of §5.1 against the printed article.

## Adaptations of the accepted scripts

The scripts are copies of the accepted ones with declared minimal changes: paths relative to the package instead of
the original working folders, the kernel read from `nucleo_s6/instalacion/src` (byte-identical to the copy used
originally), witness rows read from `inputs/` and authenticated by hash, and the statutory variant built in the run's
output folder. `incidencia_estatutaria.py` differs from the accepted module only in its docstring, so one line of the
variant manifest differs from the accepted one. No numerical code was changed. Bash is not needed.
