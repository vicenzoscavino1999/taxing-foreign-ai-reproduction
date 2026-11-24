# History of the full run, and how this version was tested

This page separates two things:

1. **the historical closure**: how the 3,708 calls of the full analysis were all accepted in November 2026, with the
   version of the package that existed then;
2. **the tests of this version (1.0.0)**: what was run with the package as distributed, which changes only the
   scheduling of FAM01 and the process priority.

No single uninterrupted run of the full analysis has been made with version 1.0.0. The historical closure combines
several runs, described below.

Times are local time in Peru (UTC−5). The computer was a desktop with 16 logical processors under Windows 11 Pro.

## 1. Historical closure: 3,708 of 3,708 calls (2026-11-19 to 2026-11-21)

### 1.1 The full run

The full analysis was launched with `-Modo completo` and 12 FAM01 processes on 2026-11-19 at 22:15, with the version
whose execution fingerprint was `9c7d6047…`. It was interrupted at 22:27 when its console window was closed, resumed
at 22:31, and ended on 2026-11-20 at 14:54 (16 h 23 min in the resumed session).

| Family | Start → end | Duration |
|---|---|---|
| FAM01 | 22:31 → 09:26 | ≈ 10 h 55 min with 12 processes (466,695 s of calls added up) |
| FAM02 | 09:26 → 11:57 | 2 h 31 min |
| FAM03 to FAM06 | 11:57 → 12:01 | 4 min |
| FAM07 | 12:01 → 12:41 | 41 min |
| FAM08 | 12:41 → 13:42 | 1 h 01 min |
| FAM11 | 13:42 → 14:53 | 1 h 10 min |
| FAM12, FAM09, FAM10, FAM13, FAM14 | 14:53 → 14:54 | under 1 min |

Result: 3,379 calls accepted, 18 time limit reached, 170 blocked (their inputs were missing), 140 rejected and
1 report not conforming; 31 of the 39 keys complete. No scientific difference was found in any accepted call.

What was not accepted, and why:

- **FAM01, 18 calls (22 units) reached their time limit.**
  - The groups GT05 (4 units, limit 5,340 s) and GT08 (2 units, 3,840 s) expired while Windows confined the hidden
    run to its efficiency cores (power throttling, "EcoQoS"): an interpreter in the background got about a quarter of
    a core.
  - The 15 units of the structural key `3eb7dcff…` and the unit `C2:G:df:inf` (key `2fbaf756…`) reached the ordinary
    limit of 600 s. Their original documents record an almost null ceiling time (at most 10.0 s and 0.376 s), because
    when they were written the ceiling was already in the memory of the process; the expensive-ceiling rule
    (GRUPOS-TECHO-C2-v1) therefore did not group them.
  - Their 22 comparisons were blocked.
- **FAM02 (R1-B1, R1-B2)** were rejected only because of timing fields that the comparator did not cover; R1-B3's
  comparison needed a decision on 160 known units; the calls that depend on them (R1-A, R1-D, R1-V) were blocked.
- **FAM03** (273 calls) was rejected or blocked: its context was built with the public environment, which its
  environment-identity check did not admit.
- **FAM09 and FAM10**: an output-reading error of the executor (F09-HIST) and a certificate link that the FAM10
  comparator did not receive (Exp8).

### 1.2 How the pending calls were closed

Each step ran in its own new folder and copy of the package; earlier runs were never modified. Accepted calls were
reused by their hashes, without being recomputed. The rules named below are in the package code and in
[REFERENCE_es.md](REFERENCE_es.md).

| Date | Step | Package version | Accepted after the step |
|---|---|---|---|
| 2026-11-20 | FAM03 with the portable-environment rule F2, extended to FAM03 by the author's decision | `4ffda83a…` | 3,651 (FAM03: 273 of 273, the same states as the references) |
| 2026-11-20 | FAM09/FAM10: reading of F09-HIST (LECTURA-HIST-v1) and certificate link (VINCULO-CERTIFICADO-v1) | `e92b1f8a…` | 3,655 (Exp8 accepted: 1,728 claims, 12 changed, all Colombian and robustly infeasible) |
| 2026-11-20 | Recovery of FAM01 (F01-R2), with high process priority applied to the whole process tree (table below), and of FAM02 R1-B1/R1-B2 (IGUALDAD-R1B-TIEMPOS-v1) | `e92b1f8a…` and `62d0fed2…` | 3,701 |
| 2026-11-20 | Backing of the 160 d-sup-N units of R1-B3 (RESPALDO-E13-PUNTO-v1) | `c7b63465…` | 3,702 |
| 2026-11-20 | Timing fields of the two SRED outputs of R1-A1 (IGUALDAD-SRED-TIEMPOS-v1) | `ff19eae1…` | 3,704 |
| 2026-11-21 | Closure of the R1-D sample (CIERRE-MUESTRA-R1D-v1): R1-D, R1-V and their comparisons | `59411f52…` | **3,708 of 3,708 calls, 39 of 39 keys, 14 of 14 families** |

The rules F2, AGRUPACION-F01R2-v1 (the 14-unit group below), IGUALDAD-R1B-TIEMPOS-v1, IGUALDAD-SRED-TIEMPOS-v1 and
CIERRE-MUESTRA-R1D-v1 were authorized by the author for their stated scope only. None of these rules changes a
scientific value, and no scientific difference was found in any accepted call.

The FAM01 recovery, with the same bounds, tolerances, validation and comparison as the full run:

| Run | Units | Limit (s) | Duration (s) | Cold ceiling (s) | Cold macro block (s) | Result |
|---|---|---|---|---|---|---|
| GT05 | 4 | 5,340 (original) | 1,173.3 | 535.4 | 154.0 | 4 complete and validated, accepted |
| GT08 | 2 | 3,840 (original) | 781.6 | 536.5 | 1.8 | 2 accepted |
| P01233 (one unit of key `3eb7dcff…`) | 1 | 6,960 | 1,212.0 | 965.48 | 122.642 | accepted |
| P02119 (`C2:G:df:inf`, key `2fbaf756…`) | 1 | 6,960 | 974.0 | 848.32 | 1.676 | accepted |
| the other 14 units of key `3eb7dcff…`, in one process | 14 | 8,460 | 2,710.2 | 896.7 | 126.0 | 14 accepted |

All were accepted with the clean comparison and rule F2 (`aceptada_comparacion_limpia_con_F2`).

## 2. What version 1.0.0 changes

Version 1.0.0 starts from `59411f52…`, the version that closed the full analysis, and changes two files. The changes
make the recovery above part of the ordinary full run, so that a reader does not need a separate recovery:

- **`reproducir.py`**
  - **TECHO-FRIO-MEDIDO-F01R2-v1.** The two keys whose originals do not record the cold cost of their ceiling
    (`3eb7dcff…` and `2fbaf756…`) take, as their "historical" ceiling and macro times, the cold times measured in the
    accepted recovery (965.48 and 122.642 s; 848.32 and 1.676 s). With them, each key is expensive and its units are
    grouped by GRUPOS-TECHO-C2-v1, with the same formula for the limit. The two new groups run after the others:
    GT28 (the 15 units of `3eb7dcff…`, 2 frontiers, limit 8,760 s) and GT29 (`C2:G:df:inf`, limit 3,300 s). The plan
    of the full analysis therefore has 3,694 calls instead of 3,708 (15 calls become one), with 290 units in 29 groups
    and 1,472 units in their own process with 600 s.
  - **PRIORIDAD-ALTA-v1.** Every process of `reproducir.py` asks Windows, at start, not to throttle it for power saving
    (`SetProcessInformation`, `ProcessPowerThrottling`). Every FAM01 call is a process of `reproducir.py`, so the
    priority now reaches the interpreter that computes. Before, it was set only on the launching process, and the
    environment's `python.exe` is a launcher whose child interpreter did not inherit it.
- **`src/general.py`.** The execution fingerprint no longer counts the documentation and the helper files added for
  readers (`docs/`, `tools/`, `sensitivities/`, `CITATION.cff`, `run.ps1`), in addition to the root `*.md` files that it
  already excluded.

Neither change touches computations, budgets, bounds, tolerances, rule F2, validation or comparison: only which units
share a process, with what external limit, and at what process priority. The fingerprint of version 1.0.0 is
`c3cb29f7…` as distributed (6,299 files) and `2e092f48…` with the six sheets that are not redistributed (6,305 files);
see `tools/version.json`.

The package also adds, outside the execution fingerprint: `run.ps1`, `tools/`, `docs/`, `CITATION.cff`, `LICENSE.md`,
the English `README.md`, and `sensitivities/` (the post-base computations of Table 3 and §5.1, adapted from the accepted
scripts with relative paths; see [sensitivities/README.md](../sensitivities/README.md)).

## 3. Tests of version 1.0.0

These tests were made on 2026-11-24, with the Python environment of the package (CPython 3.12.4 and the 10 packages of
the lock file) that already existed on the test computer; the environment was not created again for them.

**The two new FAM01 groups**, each recomputed from scratch with `general --modo ensayo-fam01` (the same process, limit,
validation and comparison as in the full run), on a copy with the six sheets:

| Group | Units | Limit (s) | Duration (s) | Result |
|---|---|---|---|---|
| GT29 (`C2:G:df:inf`, key `2fbaf756…`) | 1 | 3,300 | 867.7 (cold ceiling 742.0) | accepted with F2; C_2 equal to the recovery |
| GT28 (key `3eb7dcff…`: 14 S1-df units and `C2:N:df:inf`) | 15 | 8,760 | 2,774.7 (cold ceiling 854.3) | 15 accepted with F2; C_2 equal to the originals |

While they ran, the priority was read back from the computing interpreters: the power-throttling control was set,
with speed not throttled, and each used about one CPU-second per second.

**The archive as a reader gets it.** The archive was extracted with `Expand-Archive` (Windows PowerShell 5.1) to a
new folder `D:\p` (97 s), and every action was run from there with `run.ps1`:

| Action | Copy | Result | Time |
|---|---|---|---|
| `check` | as distributed | `CHECK PASSED`, recognized as `public` (`c3cb29f7…`) | 6 s |
| `plan` | as distributed | conforming: 3,694 calls, 39 keys; 29 FAM01 groups with 290 units (GT28: 15 units, 8,760 s; GT29: 3,300 s) and 1,472 units at 600 s | 8 s |
| `pilot` | as distributed | conforming: 16 calls accepted; Exp8 1,728 claims, 12 changed (Colombia, robustly infeasible), 1,716 identical; final COV 1,700 / 12 / 16; 0 reads outside the package | 38 s |
| `sensitivities` | as distributed | 15 of 15 checks; 25 of 25 computations identical to the accepted results; Table 3 and §5.1 equal the article | 15 s |
| `table6` | as distributed | FAM13 accepted; Table 6 and Table 4 (stored) equal the article | 7 s |
| `table4` | as distributed | refuses and asks for `inputs` | — |
| `inputs` | with the five downloadable sheets, copied from the author's copy (nothing was downloaded) | exit code 2: the five present with their hashes, only `PER_2023.xlsx` missing | — |
| `check` | the same | recognized as `public_with_downloaded_sheets` | — |
| `table4` | the same | the six favorable witnesses recomputed and accepted with F2 (0.7917, 0.5628, 0.5475, 0.4380, 0.2737, 0.2737), C_2 equal to the originals | 216 s |
| `verify`, `full` | the same | refuse: not the complete version | — |
| `resume` on a folder that is not a run | — | refuses: `control.json` missing | — |
| `inputs`, `verify` | with the six sheets | exit code 0; recognized as `complete` (`2e092f48…`) | — |

**The downloads, independent check (2026-11-24).** A separate check was run from a new extraction of the archive,
which has none of the six sheets. `inputs` obtained the five public inputs from their official sources, each with the
size and SHA-256 that the package expects: `CHL_CEI.xls`, `CHL_COU.xlsx`, `COL_2023.xlsx`, `COL_2024p.xlsx`, and
`UN_bundle.tar`, rebuilt from the downloaded UN AMA file and the seven members included in the package. It ended with
exit code 2 because only `PER_2023.xlsx` was missing; that file is available on request from INEI (README.md, Inputs).
`check` then ended with exit code 0 and recognized the copy as `public_with_downloaded_sheets`. Unlike the tests in the
table above, in which the five sheets were copied from the author's computer and nothing was downloaded, this check
exercised the downloads themselves.

Limits of these tests:

- They test the changed route of FAM01 in a targeted way (the plan, the two new groups, six ordinary units and the
  pilot). The full analysis was not run again with version 1.0.0: its other calls have code and inputs byte-identical
  to version `59411f52…`, which closed the analysis, except for the two files above.
- In the tests of the table, the five downloadable sheets were copied from the author's computer; the downloads were
  exercised only in the independent check above. The full analysis also needs `PER_2023.xlsx`, which is available only
  on request from INEI; `verify` was tested with the author's copy of that file.
- The FAM08 validator starts its own subprocess, which does not set its priority. In the historical run, where no
  process of the package set its priority, FAM08 (27 calls, in series) was accepted within its limits.
- The machine used for these tests has long paths enabled in Windows, so they do not test the 259-character limit;
  the longest path is the same file as in the version tested from `C:\p` on a clean Windows 11 installation.
- One comment in `src/fam02.py` still names the local folder of the diagnostic that preceded CIERRE-MUESTRA-R1D-v1; it
  was left as it is because that file is part of the accepted executed code.
