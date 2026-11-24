# Contrato C-A2 v2 — catálogo único

**CANDIDATO PARA REVISIÓN, SIN ACTIVACIÓN. A1–A7 y C-A2 elegidas.**

Fuente única: catalogo_contratos.json, sección ca2 y tablas ca2_*. Este render no define esquemas alternativos.

## CA2-01

Vector identificado por país/familia/año/source/vintage/snapshot. D2 2015–2023; D6 solo 2023. Snapshot por hash y adaptador explícito; sin adaptador, pendiente de evidencia.

## CA2-02

Miembros exactos por representación; PIB único y denominador referenciado compartido en la cuenta. Hash vector=H({header sin vector_sha256,members ordenados por member_id}). No rellenar brutos ausentes ni omitir TAX_NET histórico.

## CA2-03

Cada miembro coincide con país/año/vintage/snapshot/unidad/multiplicador del vector. Valores/seletores contrastados con extracción del adaptador. La biblioteca no calcula identidades, shares ni intervalos.

## CA2-04

Todo registro presente conserva validación de estructura, archivo/hash, scope/selectores y recibo de adaptador. Los cinco roles comunes y el snapshot son indispensables. Los estados se guardan por rol; common_conflicts enumera contradicciones comunes extraídas por el adaptador y bloquea todos los escenarios, aunque aparezcan en un documento de precisión. No se ocultan registros desfavorables.

## CA2-05

La evidencia se exige por escenario: E1/E2 no requieren precisión y su desconocimiento o refutación no bloquea por sí solos estas vías; E0/E3 requieren precision acreditada y regla aplicable. Los registros presentes, usados o no, se autentican y su regla, si existe, se valida. Una contradicción común nunca se trata como simple falta de precisión. E4 no recibe dominios inventados; measurement_domain sigue null.

## CA2-06

Input pareja D2/D6 mismo país. Primaria2023 comparte PIB/identidad o evidencia de conciliación conjunta aplicable; coincidencia numérica no prueba crosswalk. Histórica conserva denominadores propios y el vector D6 2023/contexto fijo por país entre años; no cuenta contemporánea histórica. En CA2-1 las cuentas primarias requieren igual unidad, multiplicador y base; puentes entre unidades/bases necesitan extensión auditada.

## CA2-07

Cada caso declara preregistration_id, case_type y country_set coincidentes con ca2.case_registry (A1-E v2) y tiene exactamente esos países; la sensibilidad individual no exige PER. Cada afirmación usa un tipo permitido por su preregistro con exactamente sus años, y cada vector la representación preregistrada cuando esta se fija. Claims fijan lista de casos, escenarios, años/cobertura y cuantificador externo forall, sin omitir escenarios. El archivo bundle se lee por hash esperado externo, nunca último activo.

## CA2-08

E2 requiere al menos dos vintages completos comparables por país/año dentro del claim; mismo concepto/unidad/base y evidencia de comparabilidad que enumera todos sus snapshots. No bastan dos PIB. Una familia puede quedar fija si la otra tiene al menos dos revisiones; las coordenadas no revisadas del contexto permanecen fijas por país. La comparabilidad se exige solo para las familias revisadas del E2 declarado; su resultado se incorpora al estado de sus casos, sin contaminar E1 que comparte vectores.

## CA2-09

Admisibilidad de metadatos distinta de estado técnico y resultado. not_run/incomplete/failed no producen resultado condicionado. E4 sin dominio deja no_identificado; resultados numéricos complete no son certificables por esta biblioteca. Todos los retornos indican real_source_admission=false. Un diagnóstico pending_evidence anterior puede conservarse de forma conservadora cuando nuevos adaptadores validan sus bytes; no se promueve en sitio.

## CA2-10

Inicial, independiente y sucesor son relaciones explícitas verificables según lineage. Ningún cambio de ID o predecessor_id nulo evade el ámbito previo. La prueba independiente enlaza hashes de antecedentes; la sucesión exige ámbito compatible y posterioridad UTC racional exacta. Se rechazan ciclos, borrados, sustituciones y ancla externa incorrecta. Todas las filas del bundle anterior se conservan exactamente; no se emite autoridad.

## Linaje y fechas

Un initial por ámbito, únicamente cuando no hay antecedente del ámbito. successor exige predecessor_id explícito; no se selecciona último por nombre/fecha. independent exige prueba por archivo/hash y adaptador registrado, referencias explícitas a antecedentes y sin predecessor_id de sucesión.

Adaptador independence(bytes) debe devolver proof_fields: identidad/hash del nuevo artefacto, scope exacto, against_records ordenados con evidence_id y H(fila antecedente), outcome=pass. La transición exige referir todos los registros del ámbito en el bundle anterior; pruebas desconocidas/negativas/ausentes bloquean. Nuevas fuentes realmente independientes pueden tener fecha anterior: la prueba de independencia, no una etiqueta, justifica su raíz.

YYYY-MM-DDTHH:MM:SS con fracción decimal opcional (punto o coma) y zona Z o ±HH:MM. Calendario/hora/offset válidos; parte entera normalizada UTC y fracción racional exacta. Posterioridad estricta en successor; igualdad de instantes se rechaza. Nulos/fechas inválidas/sin zona: ContractError.

## ca2_vectors

PK: vector_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| vector_id | id | false | none |
| family | ca2_family | false | none |
| country_id | country | false | none |
| observation_year | int | false | none |
| source_id | id | false | none |
| source_vintage | text | false | none |
| snapshot_path | path | false | none |
| snapshot_sha256 | sha | false | none |
| adapter_id | id | false | none |
| representation | ca2_representation | false | none |
| unit | atom | false | none |
| multiplier | positive | false | dimensionless |
| accounting_basis | atom | false | none |
| denominator_member_id | id | false | none |
| vector_sha256 | sha | false | none |

FK: []

## ca2_members

PK: vector_id, member_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| vector_id | id | false | none |
| member_id | id | false | none |
| concept | atom | false | none |
| country_id | country | false | none |
| observation_year | int | false | none |
| source_vintage | text | false | none |
| snapshot_sha256 | sha | false | none |
| selector | text | false | none |
| unit | atom | false | none |
| multiplier | positive | false | dimensionless |
| value_literal | dec | false | source_unit |
| denominator_member_id | id | false | none |

FK: [{"columns": ["vector_id"], "table": "ca2_vectors", "target_columns": ["vector_id"], "nullable": false}, {"columns": ["vector_id", "denominator_member_id"], "table": "ca2_members", "target_columns": ["vector_id", "member_id"], "nullable": false}]

## ca2_evidence

PK: evidence_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| evidence_id | id | false | none |
| vector_id | id | false | none |
| role | ca2_role | false | none |
| artifact_path | path | false | none |
| artifact_sha256 | sha | false | none |
| adapter_id | id | false | none |
| selectors | json | false | none |
| related_snapshots | json | false | none |
| created_at | ca2_date | false | none |
| predecessor_id | id | true | none |
| relation_kind | ca2_relation | false | metadata |
| against_evidence_ids | json | false | metadata |
| independence_path | path | true | metadata |
| independence_sha256 | sha | true | metadata |

FK: [{"columns": ["vector_id"], "table": "ca2_vectors", "target_columns": ["vector_id"], "nullable": false}, {"columns": ["predecessor_id"], "table": "ca2_evidence", "target_columns": ["evidence_id"], "nullable": true}]

## ca2_cases

PK: case_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| case_id | id | false | none |
| scenario | ca2_scenario | false | none |
| channel | ca2_channel | false | none |
| precision_claim | ca2_precision | false | none |
| admissibility | ca2_admissibility | false | none |
| measurement_domain | json | true | none |

FK: []

## ca2_inputs

PK: case_id, country_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| case_id | id | false | none |
| country_id | country | false | none |
| anchor_year | int | false | none |
| d2_vector_id | id | false | none |
| d6_vector_id | id | false | none |
| context_path | path | false | none |
| context_sha256 | sha | false | none |

FK: [{"columns": ["case_id"], "table": "ca2_cases", "target_columns": ["case_id"], "nullable": false}, {"columns": ["d2_vector_id"], "table": "ca2_vectors", "target_columns": ["vector_id"], "nullable": false}, {"columns": ["d6_vector_id"], "table": "ca2_vectors", "target_columns": ["vector_id"], "nullable": false}]

## ca2_claims

PK: claim_id

| Campo | Tipo | Nulo | Unidad |
|---|---|---|---|
| claim_id | id | false | none |
| kind | ca2_claim_kind | false | none |
| case_ids | json | false | none |
| required_scenarios | json | false | none |
| countries | json | false | none |
| anchor_years | json | false | none |
| inner_quantifier | ca2_quantifier | false | none |
| outer_quantifier | ca2_quantifier | false | none |
| technical_status | ca2_technical | false | none |
| interpretation | ca2_interpretation | false | none |

FK: []

## Adaptadores y límites

Método snapshot(bytes) retorna {context: proyección snapshot_projection, members: proyección snapshot_member_projection orden concept}. El adaptador debe verificar organismo, extracción y marco; la biblioteca comprueba bytes y concordancia.
Método evidence(bytes) retorna evidence_receipt_fields del catálogo: facts con scope, outcome pass/fail/unknown, precision_rule y common_conflicts (lista ordenada de roles comunes). Toda regla presente se valida, aun si no es requisito del caso. El adaptador debe comunicar contradicciones conceptuales/contables como conflictos comunes; un pass autoescrito no prueba institución.
Mapa de adaptadores suministrado por código del llamador, nunca importado desde bundle. Sin registro: pending_evidence. Esta entrega solo aporta adaptador ficticio en pruebas, no adaptadores INEI/INEGI/DANE/BCCh ni auditoría numérica.
Adaptador independence(bytes) debe devolver proof_fields: identidad/hash del nuevo artefacto, scope exacto, against_records ordenados con evidence_id y H(fila antecedente), outcome=pass. La transición exige referir todos los registros del ámbito en el bundle anterior; pruebas desconocidas/negativas/ausentes bloquean. Nuevas fuentes realmente independientes pueden tener fecha anterior: la prueba de independencia, no una etiqueta, justifica su raíz.

Sin admisión institucional ni evaluación económica.
