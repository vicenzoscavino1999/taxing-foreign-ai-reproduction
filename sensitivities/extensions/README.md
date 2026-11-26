# Results added in version 1.1.0

Run `extensions` from the [package entry point](../../README.md#start-here). Read `results.md` for the tables. The supporting JSON files give receipts as fractions of potential AI gains and formal shares as fractions of all establishments.

### Tax menus and informal adoption

Online Appendix S6.1 selects one structural point per design where some formerly formal establishments adopt informally on the archived policy grid. Selection uses the number of interior parameters and then the frontier identifier. The code in `informal/` computes the two domestic-only and eight combined-menu ceilings at those points. `menus/resumen.json` gives the certified ratio intervals. `menus/mallas.json` gives the discrete maxima over the recorded rates on 110 grids at each of the two withholding caps. Switching at a fixed pair of rates and switching at a revenue-maximizing policy are distinct quantities.

The 15% fixed-rate pilot evaluates prior-income underreporting under linear incidence. Each reporting rule has its own no-AI counterfactual. `menus/prior_income.json` gives formal shares before and after adoption, entries and exits, and the domestic and withholding components of incremental receipts for both designs.

The grid inputs come from the FAM05 elasticity meshes and their structural points. The two model implementations, inputs and reference outputs are supplied in `informal/`.

### Analytical bounds

- **Withholding alone.** The two designs share the original favorable withholding-only witness in `sensitivities/inputs/`. Full contractual gross-up gives a tax wedge of `w = τ/(1−τ)`. With a cost schedule indexed by α, the reported fraction is `x^0.1`, where `w = (1−x)/x^α`. Applying the rate cap and maximizing receipts gives 0.1431, 0.2612 and 0.2737 at α = 0, ½ and 1. These are ceilings at that structural point.
- **Colombia.** With contractual incidence halved and the original concealment cost held fixed, full reporting bounds receipts from above. The program uses the foreign-rate bound in `referencias/fam11/rem166/TRABAJO/EVIDENCIA_B1.json`, the six requirement bounds and payment share in `referencias/fam11/rem169/TRABAJO/EVIDENCIA_B2.json`, and the claim identifiers in `datos/fam11/b2/MANIFIESTO_B2.json`. It compares each requirement with the conservative upper bound 0.18974 using exact rational arithmetic.
- **Mexico.** The full-reporting upper bound is `0.20 × 0.60 / 0.40 = 0.30`. The model’s reporting response multiplies it by `0.40^0.1`. `datos/fam13/s1/publico/T6.json` supplies the conversion factors and `T7_anexo.jsonl` identifies the 16 claims and their witnesses. The calculation uses the Mexican PROD3 fiscal contexts in `referencias/fam03/paquete/objetos/` and matches the requirements and gaps to their corresponding FAM01 witnesses. The decision margin is one percentage point of potential gains.

`bounds.json` contains the three schedules, the twelve Colombian claim identifiers grouped by requirement, and the sixteen individual Mexican shortfalls.

