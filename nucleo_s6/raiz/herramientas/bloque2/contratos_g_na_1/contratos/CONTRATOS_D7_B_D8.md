# Contratos D7/B/D8 — ajuste contractual

> **Enmienda candidata CA2-4 (2026-09-29, SIN ACTIVACIÓN).** Acotada a integrar la rama condicional macro-ca2-v2 en `lambda_pi_envelope` (reglas y esquema `macro_ca2` en CLAVES_DE_CALCULO.json). El contrato antecedente CA2-3 `eda3d6e5a0c0c0c318bb075c3314f7c927382c955d76e2dcdd3b5c1f4659af32` conserva sus bytes y no cubre esta enmienda.


**BORRADOR NO APROBADO.** Representación generada del catálogo exacto. Reglas textuales y esquemas anidados también son obligatorios.

## Convenciones globales

```json
{
  "encoding": "UTF-8",
  "newline": "LF final único",
  "CSV": "RFC4180,coma,encabezado exacto y columnas en orden listado; null vacío, text vacío prohibido; bool true/false; int decimal sin ceros iniciales",
  "decimal": "finito; sin -0; cadena shortest-roundtrip del entorno aprobado para calculados; decimales exactos declarados en forma canónica sin ceros finales; no redondeo ad hoc",
  "JSON": "claves ordenadas,separadores compactos,sin claves repetidas,arrays según orden especificado; null tipado; JSON en CSV escapado RFC4180",
  "row_order": "PK lexicográfica por valor tipado; id lexicográfico ASCII,int numérico",
  "unknown_columns": "reject",
  "unknown_files": "reject inside product tree",
  "tree": "SHA256(JSON canónico lista ordenada {path,sha256,bytes}); manifests y punteros y recibos excluidos; manifest independiente enlazado por hash"
}
```

## Tipos

```json
{
  "id": {
    "type": "string",
    "pattern": "^[A-Za-z0-9_.:-]+$"
  },
  "atom": {
    "type": "string",
    "pattern": "^[A-Za-z0-9_.-]+$"
  },
  "text": {
    "type": "string",
    "minLength": 1
  },
  "sha": {
    "type": "string",
    "pattern": "^[0-9a-f]{64}$"
  },
  "int": {
    "type": "integer",
    "minimum": 0
  },
  "bool": {
    "type": "boolean"
  },
  "dec": {
    "type": "decimal",
    "finite": true
  },
  "positive": {
    "type": "decimal",
    "exclusiveMinimum": 0
  },
  "rate": {
    "type": "decimal",
    "minimum": 0,
    "maximum": 1
  },
  "json": {
    "type": "json",
    "canonical": true
  },
  "path": {
    "type": "string",
    "relativePOSIX": true
  },
  "date": {
    "type": "string",
    "format": "date-time-zone"
  },
  "country": {
    "type": "string",
    "enum": [
      "CHL",
      "COL",
      "MEX",
      "PER"
    ]
  },
  "design": {
    "type": "string",
    "enum": [
      "G",
      "N"
    ]
  },
  "instrument": {
    "type": "string",
    "enum": [
      "d",
      "f",
      "df"
    ]
  },
  "side": {
    "type": "string",
    "enum": [
      "point",
      "left_limit",
      "right_limit"
    ]
  },
  "block": {
    "type": "string",
    "enum": [
      "micro",
      "macro"
    ]
  },
  "direction": {
    "type": "string",
    "enum": [
      "inferior",
      "superior"
    ]
  },
  "gate": {
    "type": "string",
    "enum": [
      "pass",
      "limitation",
      "fail",
      "not_applicable"
    ]
  },
  "computation": {
    "type": "string",
    "enum": [
      "complete",
      "excluded",
      "not_applicable",
      "failed",
      "incomplete"
    ]
  },
  "reason": {
    "type": "string",
    "pattern": "^[A-Z][A-Z0-9_]*$"
  }
}
```

## D7/authority.csv

Autoridad exacta de la versión consumidora; no se instancia sin aprobación real

una fila por authority_id

PK: ['authority_id']; UK: []; orden: ['authority_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| authority_id | id | none | false |
| package_sha256 | sha | none | false |
| manifest_sha256 | sha | none | false |
| decision_path | path | none | false |
| decision_sha256 | sha | none | false |
| approval_evidence_sha256 | sha | none | false |
| consumer_scope | text | none | false |
| lineage_manifest_sha256 | sha | none | false |


## D7/source_evidence.csv

Procedencia sin datos personales

una fila por evidence_id

PK: ['evidence_id']; UK: []; orden: ['evidence_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| evidence_id | id | none | false |
| source_id | id | none | false |
| source_path | path | none | false |
| payload_sha256 | sha | none | false |
| source_locator | text | none | false |
| source_year | int | none | false |
| source_vintage | text | none | false |
| unit | text | none | false |
| multiplier | positive | dimensionless | false |
| universe | text | none | false |
| identified_object | text | none | false |
| target_object | text | none | false |
| permitted_use | text | none | false |
| transport_status | text | none | false |
| precision_evidence_id | id | none | true |
| authority_id | id | none | false |

FK: {"columns": ["authority_id"], "table": "authority", "target_columns": ["authority_id"], "nullable": false}

- permitted_use in {measurement,formula_input,declared_stress,plausibility_only,rejected}
- transport_status in {direct_verified,limited,not_applicable,rejected}; limited/rejected prohíbe transporte numérico nacional
- precision_evidence_id obligatorio para medida nacional consumida; referencia a registro de precisión externo autenticado por dependencias del manifiesto

## D7/parameter_registry.csv

Definición global del parámetro; los valores y soportes dependen de binding

una fila por parameter_id

PK: ['parameter_id']; UK: []; orden: ['parameter_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| parameter_id | atom | none | false |
| name | text | none | false |
| symbol | text | none | false |
| module | text | none | false |
| role | text | none | false |
| unit | text | none | false |
| denominator | text | none | false |
| universe | text | none | false |
| horizon | text | none | false |
| formula_id | id | none | true |
| active_primary | bool | none | false |
| inactive_reason | reason | none | true |

FK: {"columns": ["formula_id"], "table": "formula_registry", "target_columns": ["formula_id"], "nullable": true}

- role in {primitive,derived,fixed,measured,evidence_only,inactive}
- derived exige formula_id; inactive exige active_primary=false e inactive_reason; ningún dato nacional tiene country_id=GLOBAL
- Todo derived tiene formula_id resoluble, output_parameter_id idéntico y unidad compatible; no basta un texto source. Los objetos B pueden declararse sin valor D7; su resultado se exige solo en la etapa B aplicable.

## D7/formula_registry.csv

Fórmula declarativa exacta; no código productor

una fila por formula_id

PK: ['formula_id']; UK: []; orden: ['formula_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| formula_id | atom | none | false |
| expression | text | none | false |
| output_parameter_id | id | none | false |
| output_unit | text | none | false |
| domain_predicate | text | none | false |
| definition_clause | text | none | false |
| verification_requirement | text | none | false |
| definition_kind | text | none | false |
| context_inputs | json | none | false |
| result_binding | json | none | true |
| declaration_only_in_D7 | bool | none | false |

FK: {"columns": ["output_parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

- definition_kind in {algebraic_expression,numerical_function,numerical_operator}; forma cerrada no implícita para numerical_operator. Cada output_parameter_id y unidad coincide con registry.
- context_inputs son referencias a campos declarados del catálogo; result_binding designa familia/tabla/campo/PK y conversión de unidad, no fila calculada ni dependencia productiva de D7. declaration_only_in_D7=true siempre.
- R: numerical_function; C_2: numerical_operator, supremo de R/B_pot, unit=share, resultado B.capture_ceiling_result.C_2. Se preservan no alcanzado,laterales,disponibilidad,error y testigos.

## D7/formula_inputs.csv

Arista de dependencia de fórmulas; grafo sin ciclos

una fila por formula_id,input_order

PK: ['formula_id', 'input_order']; UK: [['formula_id', 'parameter_id']]; orden: ['formula_id', 'input_order']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| formula_id | id | none | false |
| input_order | int | none | false |
| parameter_id | id | none | false |

FK: {"columns": ["formula_id"], "table": "formula_registry", "target_columns": ["formula_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

- input_order consecutivo desde 0; grafo de parámetros derivados acíclico

## D7/support_sets.csv

Conjunto base, coordinado, de robustez o sensibilidad

una fila por support_set_id

PK: ['support_set_id']; UK: []; orden: ['support_set_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| support_set_id | atom | none | false |
| kind | text | none | false |
| parent_support_set_id | id | none | true |
| transformation_id | id | none | true |
| authority_id | id | none | false |
| description | text | none | false |

FK: {"columns": ["parent_support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": true}

FK: {"columns": ["authority_id"], "table": "authority", "target_columns": ["authority_id"], "nullable": false}

- kind in {base,coordination,robustness,external_sensitivity,domain_stress}
- base exige parent_support_set_id=null y transformation_id=null; resto exige ambos; grafo de padres acíclico
- transformation_id referencia formulas.json, sección transformations, autenticada por contract_sha256

## D7/support_set.csv

Dominio de un parámetro en un conjunto; support_id globalmente único

una fila por support_id

PK: ['support_id']; UK: [['support_set_id', 'parameter_id', 'variant_id']]; orden: ['support_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| support_id | id | none | false |
| support_set_id | id | none | false |
| parameter_id | id | none | false |
| variant_id | atom | none | false |
| domain_kind | text | none | false |
| lower | dec | dimensionless | true |
| upper | dec | dimensionless | true |
| lower_closed | bool | none | true |
| upper_closed | bool | none | true |
| scale | text | none | true |
| level0_nodes | json | none | false |
| central | dec | dimensionless | true |
| has_central | bool | none | false |
| formula_id | id | none | true |
| inactive_reason | reason | none | true |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

FK: {"columns": ["formula_id"], "table": "formula_registry", "target_columns": ["formula_id"], "nullable": true}

- support_id = SUP:<support_set_id>:<parameter_id>:<variant_id>; componentes atom sin dos puntos
- domain_kind in {continuous,discrete,singleton,derived,inactive}; scale in {arithmetic,logarithmic,discrete} o null
- continuous exige lower<upper, flags de extremos, scale y al menos dos nudos; log exige lower>0
- discrete/singleton exige nodos finitos únicos ordenados y extremos=min/max; singleton tiene un nudo
- derived exige formula_id y lower/upper/flags/scale=null, nodos=[]; inactive exige motivo y demás valores null/nodos=[]
- has_central=false implica central=null; true exige centro admisible; no centro por defecto

## D7/parameter_bindings.csv

Asignación por conjunto y ámbito; identifica simultáneamente soporte y procedencia

una fila por binding_id

PK: ['binding_id']; UK: [['support_set_id', 'parameter_id', 'scope_id']]; orden: ['binding_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| binding_id | id | none | false |
| support_set_id | id | none | false |
| parameter_id | id | none | false |
| scope_id | id | none | false |
| country_id | country | none | true |
| value_type | text | none | false |
| support_id | id | none | true |
| source_evidence_id | id | none | true |
| value | dec | dimensionless | true |
| formula_id | id | none | true |
| authority_id | id | none | false |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

FK: {"columns": ["support_id"], "table": "support_set", "target_columns": ["support_id"], "nullable": true}

FK: {"columns": ["source_evidence_id"], "table": "source_evidence", "target_columns": ["evidence_id"], "nullable": true}

FK: {"columns": ["formula_id"], "table": "formula_registry", "target_columns": ["formula_id"], "nullable": true}

FK: {"columns": ["authority_id"], "table": "authority", "target_columns": ["authority_id"], "nullable": false}

- scope_id=global exige country_id=null; scope_id=country:<ISO> exige ese country_id
- support_id referido debe pertenecer al mismo support_set_id y parameter_id de la fila
- value_type in {measured,internal_derived,declared_scenario,fixed_institutional_constant,evidence_for_support,inactive}
- measured exige source_evidence_id y value; declared_scenario exige support_id; internal_derived exige formula_id; fixed exige value; inactive exige value=null
- Para definiciones con evaluation_stage=B, value=null en D7; declarar fórmula no exige construir resultado ni evaluarlo. C_2 no se materializa como coordenada de omega_values.

## D7/joint_constraints.csv

Restricción conjunta y su frontera explícita

una fila por constraint_id

PK: ['constraint_id']; UK: []; orden: ['constraint_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| constraint_id | id | none | false |
| support_set_id | id | none | false |
| predicate | text | none | false |
| reason_code | reason | none | false |
| boundary_kind | text | none | false |
| severity | text | none | false |
| definition_clause | text | none | false |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

- severity in {hard_fail,exclude,domain_stop}; boundary_kind in {theoretical,admissibility,epistemic,none}

## D7/constraint_inputs.csv

Participación de parámetros en restricción

una fila por constraint_id,parameter_id

PK: ['constraint_id', 'parameter_id']; UK: []; orden: ['constraint_id', 'parameter_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| constraint_id | id | none | false |
| parameter_id | id | none | false |

FK: {"columns": ["constraint_id"], "table": "joint_constraints", "target_columns": ["constraint_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}


## D7/scenario_map.csv

Escenario y transformación de primitivas; casos del modelo enlazados al D4 autenticado

una fila por scenario_id

PK: ['scenario_id']; UK: []; orden: ['scenario_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| scenario_id | id | none | false |
| support_set_id | id | none | false |
| parent_scenario_id | id | none | true |
| layer_id | id | none | false |
| coordination_scenario_id | id | none | true |
| transformation_id | id | none | true |
| country_id | country | none | true |
| design | design | none | true |
| instrument | instrument | none | true |
| availability_case_id | id | none | true |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["parent_scenario_id"], "table": "scenario_map", "target_columns": ["scenario_id"], "nullable": true}

- availability_case_id no nulo referencia D4.model_case_map en dependencia autenticada; país/instrumento concuerdan
- coordination requiere parent_scenario_id,coordination_scenario_id,transformation_id; no requiere un país si transformación es común

## D7/tax_component_supports.csv

Tres componentes por país y conjunto, ligados al mismo PIB y primitivas de fuente

una fila por support_set_id,country_id,component_id

PK: ['support_set_id', 'country_id', 'component_id']; UK: []; orden: ['support_set_id', 'country_id', 'component_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| support_set_id | id | none | false |
| country_id | country | none | false |
| component_id | text | none | false |
| d6_tree_sha256 | sha | none | false |
| d6_row_id | id | none | false |
| source_low | dec | share | false |
| source_high | dec | share | false |
| pi_support_id | id | none | false |
| primitive_group_id | id | none | false |
| evidence_id | id | none | false |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["pi_support_id"], "table": "support_set", "target_columns": ["support_id"], "nullable": false}

FK: {"columns": ["evidence_id"], "table": "source_evidence", "target_columns": ["evidence_id"], "nullable": false}

- component_id in {iva,otros_productos,produccion}; low<=high
- pi_support_id pertenece al mismo set y parámetro pi de ese componente; D6 row/primitivas existen en producto autenticado
- por caso preregistrado exactamente 3×|country_set| filas elegibles; no cuatro PIB independientes dentro de un país
- primitive_group_id debe resolver al menos un miembro de shared_primitive_members; miembros del mismo d6_tree_sha256; el conjunto de tres componentes de un país comparte la misma primitiva PIB; no basta un ID sin miembros

## D7/tax_rate_inputs.csv

Tasa estatutaria para sección R2; no share efectivo

una fila por rate_input_id

PK: ['rate_input_id']; UK: [['country_id', 'regime_id', 'legal_effective_date', 'rate_type']]; orden: ['rate_input_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| rate_input_id | id | none | false |
| country_id | country | none | false |
| regime_id | id | none | false |
| legal_effective_date | text | none | false |
| rate_type | text | none | false |
| value | rate | dimensionless | true |
| evidence_id | id | none | false |
| source_locator | text | none | false |
| consumed_section | text | none | false |
| status | text | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["evidence_id"], "table": "source_evidence", "target_columns": ["evidence_id"], "nullable": false}

- status in {verified,blocked}; verified exige value; blocked exige value=null y motivo; consumed_section=tau_d_estatutario

## D7/d7_admissibility_report.csv

Conteos por restricción, con solapamientos declarados

una fila por support_set_id,layer_id,constraint_id

PK: ['support_set_id', 'layer_id', 'constraint_id']; UK: []; orden: ['support_set_id', 'layer_id', 'constraint_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| support_set_id | id | none | false |
| layer_id | id | none | false |
| constraint_id | id | none | false |
| evaluated_count | int | none | false |
| accepted_count | int | none | false |
| rejected_count | int | none | false |
| reason_code | reason | none | false |
| evidence_id | id | none | false |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["constraint_id"], "table": "joint_constraints", "target_columns": ["constraint_id"], "nullable": false}

FK: {"columns": ["evidence_id"], "table": "source_evidence", "target_columns": ["evidence_id"], "nullable": false}

- accepted_count+rejected_count=evaluated_count; no sumar rechazos de restricciones solapadas como si fueran disjuntos

## D7/d7_gate_report.csv

Gates de esquema, autoridad, datos, soporte, transporte y publicación

una fila por gate_id,scope_id

PK: ['gate_id', 'scope_id']; UK: []; orden: ['gate_id', 'scope_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| gate_id | id | none | false |
| scope_id | id | none | false |
| required | bool | none | false |
| status | gate | none | false |
| reason_code | reason | none | false |
| evidence_id | id | none | false |
| blocking | bool | none | false |

FK: {"columns": ["evidence_id"], "table": "source_evidence", "target_columns": ["evidence_id"], "nullable": false}

- fail requerido implica blocking=true; limitation solo habilita la rama expresamente permitida

## B/omega.csv

Estado común de coordenadas declaradas, sin datos ni claves macro nacionales

una fila por omega_id

PK: ['omega_id']; UK: []; orden: ['omega_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| omega_id | id | none | false |
| support_set_id | id | none | false |
| scenario_id | id | none | false |
| primitive_values_sha256 | sha | none | false |
| domain_status | text | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["scenario_id"], "table": "scenario_map", "target_columns": ["scenario_id"], "nullable": false}

- domain_status in {admissible,excluded}; excluido requiere motivo; ninguna fila evaluada puede referir omega excluido
- omega contiene coordenadas de escenario y derivados comunes; datos nacionales están en contexto macro y bindings country, no se confunden con escenarios comunes; scenario.support_set_id debe coincidir
- primitive_values_sha256 y omega_id se reconstruyen con common_values y omega_identity de CLAVES_DE_CALCULO.json. No contienen snapshot nacional, país, código o tolerancia. Las claves de cálculo pertenecen a frontier_context y lambda_pi_envelope, no a omega.

- domain_status de omega solo evalúa restricciones comunes; inadmisibilidad macro nacional se registra en lambda_pi_envelope por país/estado y no excluye omega para los otros países.

## B/omega_values.csv

Valores primitivos y derivados auditables por omega

una fila por omega_id,parameter_id

PK: ['omega_id', 'parameter_id']; UK: []; orden: ['omega_id', 'parameter_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| omega_id | id | none | false |
| parameter_id | id | none | false |
| value | dec | dimensionless | true |
| value_unit | text | none | false |
| binding_id | id | none | true |
| formula_id | id | none | true |
| reason_code | reason | none | true |

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

FK: {"columns": ["binding_id"], "table": "parameter_bindings", "target_columns": ["binding_id"], "nullable": true}

FK: {"columns": ["formula_id"], "table": "formula_registry", "target_columns": ["formula_id"], "nullable": true}

- null solo parámetro inactivo con motivo; derivado exige formula; primitiva activa exige binding del mismo set
- Solo primitivas comunes y derivados comunes: lista exhaustiva en CLAVES_DE_CALCULO.json. No incluye s_L_bar,shares tributarios nacionales,lambda,C2,G ni otros resultados B. Binding de primitiva es global y del mismo set; derivado común exige definición registrada.
- common_values hashea únicamente filas primitivas activas de la lista común, ordenadas por parameter_id; los derivados auditables no se hashean como entradas. Las claves estructural/macro añaden sus dependencias propias y no se deducen de esta tabla sola.

## B/cell_context.csv

Llave completa de confrontación/inversión; unicidad natural explícita

una fila por cell_id

PK: ['cell_id']; UK: [['run_id', 'design_v', 'country_id', 'instrument_j', 'availability_case_id', 'omega_id', 'eta_w_block', 'policy_variant_id', 'regime_id', 'requirement_basis', 'xi', 'layer', 'bound_variant', 'external_cell_id', 'national_state_sha256', 'expected_macro_key_sha256']]; orden: ['cell_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| run_id | id | none | false |
| design_v | design | none | false |
| country_id | country | none | false |
| instrument_j | instrument | none | false |
| availability_case_id | id | none | false |
| availability_matrix_hash | sha | none | false |
| availability_assumed | bool | none | false |
| availability_status | text | none | false |
| availability_source | text | none | false |
| instrument_available | bool | none | false |
| omega_id | id | none | false |
| eta_w_block | block | none | false |
| policy_variant_id | id | none | false |
| regime_id | id | none | false |
| requirement_basis | text | none | false |
| xi | dec | dimensionless | false |
| layer | text | none | false |
| bound_variant | text | none | false |
| external_cell_id | id | none | false |
| coordination_scenario_id | id | none | true |
| national_state_sha256 | sha | none | false |
| expected_macro_key_sha256 | sha | none | false |

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": false}

- bound_variant in {sin_addback,addback_completo}; requirement_basis y layer reproducen grilla externa autenticada
- external_cell_id FK externa a grilla fijada por manifest; D4 verifica caso e instrumento
- run_id FK al run_manifest; country_id nunca GLOBAL

## B/frontier_context.csv

Contexto de frontera; independiente de celda externa, comparte cómputo cuando huellas coinciden

una fila por frontier_id

PK: ['frontier_id']; UK: [['run_id', 'design_v', 'country_id', 'instrument_j', 'availability_case_id', 'omega_id', 'tau_domain_id']]; orden: ['frontier_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| frontier_id | id | none | false |
| run_id | id | none | false |
| design_v | design | none | false |
| country_id | country | none | false |
| instrument_j | instrument | none | false |
| availability_case_id | id | none | false |
| availability_matrix_hash | sha | none | false |
| omega_id | id | none | false |
| structural_key_sha256 | sha | none | false |
| tau_domain_id | id | none | false |
| structural_key_payload | json | none | false |

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": false}

FK: {"columns": ["tau_domain_id"], "table": "tau_domains", "target_columns": ["tau_domain_id"], "nullable": false}

- tau_domain_id refiere soporte de topes aprobado; no se confunde reuse_id con cambio de país jurídico
- structural_key_sha256=H(structural_key_payload) según contrato de claves. Payload concuerda con proyección estructural de omega_values,diseño,menú efectivo y tau_domains. País,caso y autorización D4 se validan al enlazar; no fuerzan recalcular C2 si el dominio efectivo y restantes dependencias son idénticos.

## B/frontier_result.csv

Frontera detallada y evaluaciones laterales separadas

una fila por frontier_id,point_id,side

PK: ['frontier_id', 'point_id', 'side']; UK: []; orden: ['frontier_id', 'point_id', 'side']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| frontier_id | id | none | false |
| point_id | id | none | false |
| side | side | none | false |
| tau_d | rate | dimensionless | false |
| tau_f | rate | dimensionless | false |
| B_d | dec | normalized_flow | true |
| B_f | dec | normalized_flow | true |
| B_f_grav | dec | normalized_flow | true |
| R | dec | normalized_flow | true |
| B_pot | positive | normalized_flow | true |
| CS | dec | share | true |
| eps_dd | dec | dimensionless | true |
| eps_df | dec | dimensionless | true |
| eps_fd | dec | dimensionless | true |
| eps_ff | dec | dimensionless | true |
| s_P | rate | dimensionless | true |
| regime | text | none | false |
| kink_adjacent | bool | none | false |
| audit_status | gate | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["frontier_id"], "table": "frontier_context", "target_columns": ["frontier_id"], "nullable": false}

- complete exige bases,R,Bpot,CS; elasticidades null solo base cero/no derivada con motivo; no promediar laterales
- regime in {interior,esquina_f,esquina_d,origen,borde}; clasificación de adopción va en regime_evidence de auditoría
- B_f_grav=B_f bajo baseline; CS=R/B_pot; no R negativo convertido a cero

## B/capture_ceiling_result.csv

Techo por contexto y estado de consecución; nunca cero para instrumento ausente

una fila por ceiling_id

PK: ['ceiling_id']; UK: [['frontier_id']]; orden: ['ceiling_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| ceiling_id | id | none | false |
| frontier_id | id | none | false |
| C_2 | dec | share | true |
| tau_d_at_sup | rate | dimensionless | true |
| tau_f_at_sup | rate | dimensionless | true |
| sup_not_attained | bool | none | true |
| sup_lateral_low | dec | share | true |
| sup_lateral_high | dec | share | true |
| instrument_available | bool | none | false |
| availability_status | text | none | false |
| availability_source | text | none | false |
| availability_assumed | bool | none | false |
| coordination_scenario_id | id | none | true |
| monotonicity_check | text | none | false |
| numerical_error | dec | share | true |
| computation_status | computation | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["frontier_id"], "table": "frontier_context", "target_columns": ["frontier_id"], "nullable": false}

- instrument_available=false implica not_applicable,C_2=null y monotonicity_check=not_applicable
- complete exige C_2,error y sup_not_attained; sup_not_attained=true exige tasas=null,ambos laterales y al menos un sup_witness
- sup_not_attained=false exige tasas pobladas; monotonicity_check in {pass,fail,not_applicable}; solo compara instrumentos disponibles

## B/sup_witness.csv

Aproximación al supremo no alcanzado por rama, conserva ubicación y lado

una fila por ceiling_id,sequence_index,side

PK: ['ceiling_id', 'sequence_index', 'side']; UK: []; orden: ['ceiling_id', 'sequence_index', 'side']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| ceiling_id | id | none | false |
| sequence_index | int | none | false |
| side | side | none | false |
| tau_d | rate | dimensionless | false |
| tau_f | rate | dimensionless | false |
| limit_value | dec | share | false |
| residual | dec | share | false |
| approach_distance | dec | rate_distance | false |
| branch_id | id | none | false |

FK: {"columns": ["ceiling_id"], "table": "capture_ceiling_result", "target_columns": ["ceiling_id"], "nullable": false}

- sequence_index inicia0; approach_distance>=0; secuencia por lado con distancia decreciente, límite consistente a tolerancia

## B/lambda_pi_envelope.csv

Puente por omega compatible y país; no extremo laboral de otro estado

una fila por macro_id

PK: ['macro_id']; UK: [['run_id', 'country_id', 'omega_id', 'eta_w_block', 'macro_key_sha256']]; orden: ['macro_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| macro_id | id | none | false |
| run_id | id | none | false |
| country_id | country | none | false |
| omega_id | id | none | false |
| s_L_bar | rate | dimensionless | false |
| eta_w | dec | dimensionless | false |
| eta_H | dec | dimensionless | false |
| theta_W | dec | dimensionless | false |
| s_T_marg | dec | share | false |
| q_pot | dec | share | false |
| lambda_pi | dec | dimensionless | true |
| admissible | bool | none | false |
| eta_w_block | block | none | false |
| theta_W_negative | bool | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |
| macro_key_sha256 | sha | none | false |
| macro_key_payload | json | none | false |
| national_state_sha256 | sha | none | false |

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": false}

- admissible exige q_pot<1,eta_H>−1,lambda>0,s_T_marg>=0,s_Pi>=0; negativos de theta_W se incluyen y marcan
- Rama estricta (E0/E3, kind=macro-v2): macro_key_payload contiene país,bloque,proyección macro de omega,cuatro shares nacionales,primitivas fuente,dependencias D2/D6/precisión/conjunto correlacionado,protocolo y huellas técnicas exactas. H(payload)=macro_key_sha256; H(national_state)=national_state_sha256. Ver CLAVES_DE_CALCULO.json.
- Rama condicional (E1/E2, kind=macro-ca2-v2): macro_key_payload tiene exactamente los campos de CLAVES_DE_CALCULO.json schemas.macro_ca2 y H(payload)=macro_key_sha256. El bundle se resuelve por bundle_sha256 en el índice CA2 fijado por el manifiesto D7; la fila ca2_inputs(case_id,country_id,anchor_year) reproduce d2_vector_sha256, d6_vector_sha256 y context_sha256; el caso ca2_cases reproduce scenario∈{E1,E2}, preregistration_id, case_type y country_set; country_id∈country_set; el vector D2 es de familia D2, del año ancla y representación d2_*; el vector D6 es D6 2023 y representación d6_*; el archivo de contexto fija design_v, instrument_j, availability_case_id y availability_matrix_hash iguales a los de cada celda que enlaza la fila y case_id termina en <design_v>-<instrument_j>-<availability_case_id>; common_values_sha256=H(common_values del omega); protocolo y huellas técnicas iguales a las de la corrida. national_state (national-state-v2) usa las primitivas publicadas de esos vectores y joint_domain_sha256=bundle_sha256; national_state_sha256=H(national_state). La rama condicional no afirma precisión: ninguna evidencia de precisión se inventa (precision_evidence_id con prefijo CA2COND) y la separación con la rama estricta se conserva.
- s_L_bar,eta_w,eta_H coinciden exactamente con payload y omega; cada referencia nacional resuelve en manifest fijado y país correcto. Dos puntos nacionales admisibles distintos pueden compartir omega; los distingue national_state_sha256 y la clave macro, sin duplicar el cálculo estructural.
- Una misma clave macro puede reutilizarse entre omegas cuya proyección macro coincida, pero cada fila mantiene su omega_id; no se enlaza una fila de otro omega por mera igualdad de hash.

## B/confrontation_result.csv

Confrontación por llave completa en cell_context

una fila por cell_id

PK: ['cell_id']; UK: []; orden: ['cell_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| ceiling_id | id | none | false |
| macro_id | id | none | false |
| sup_not_attained | bool | none | true |
| C_2 | dec | share | true |
| K_comp_1 | dec | share | true |
| G | dec | share | true |
| verdict | text | none | false |
| run_readiness_flag | bool | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["cell_id"], "table": "cell_context", "target_columns": ["cell_id"], "nullable": false}

FK: {"columns": ["ceiling_id"], "table": "capture_ceiling_result", "target_columns": ["ceiling_id"], "nullable": false}

FK: {"columns": ["macro_id"], "table": "lambda_pi_envelope", "target_columns": ["macro_id"], "nullable": false}

- macro coincide exactamente con cell en run_id,country_id,omega_id,eta_w_block,national_state_sha256 y macro_key_sha256=cell.expected_macro_key_sha256. ceiling.frontier coincide con cell en run_id,country_id,omega_id,design_v,instrument_j,availability_case_id,availability_matrix_hash. Las demás dimensiones externas permanecen en cell_context y no se eliminan al reutilizar cálculo.
- complete exige C2,K,G y G=C2−K; verdict in {factible,infactible,inconcluso,no_verdict}; no complete implica no_verdict y readiness=false
- no combinar sup C2 sobre omega con inf K sobre otro omega
- Revalidar ambas claves desde sus payloads; no basta comparar hashes declarados. Requerimiento usa lambda de esa fila macro, gain_share de ese omega y external_cell_id,capa,cota,variante,xi de esa celda. Cambio de fuente nacional exige clave nueva y bloquea la reutilización macro anterior aunque el valor puntual coincida.

## B/inversion_result.csv

Cuatro despejes y dos problemas endógenos, una fila por objeto aun si no ejecutable

una fila por cell_id,inversion_id

PK: ['cell_id', 'inversion_id']; UK: []; orden: ['cell_id', 'inversion_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| inversion_id | text | none | false |
| lambda_pi_required | dec | dimensionless | true |
| delta_y_required | dec | share | true |
| C_2_required | dec | share | true |
| external_factor_required | rate | dimensionless | true |
| fixed_point_converged | bool | none | true |
| phi_critical_partial | dec | dimensionless | true |
| phi_critical_total | rate | dimensionless | true |
| outside_support | bool | none | false |
| no_solution | bool | none | false |
| corner_binding | bool | none | false |
| kink_adjacent | bool | none | false |
| admissibility_violated | bool | none | false |
| target_value | dec | dimensionless | true |
| target_unit | text | none | false |
| equation_id | id | none | false |
| method_id | id | none | false |
| result_status | text | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |
| n_scalar_solutions | int | none | true |
| n_scalar_intervals | int | none | true |

FK: {"columns": ["cell_id"], "table": "cell_context", "target_columns": ["cell_id"], "nullable": false}

- inversion_id in {lambda_required,gain_required,capture_required,external_factor,phi_partial,phi_total}
- solo campo de valor propio de inversion_id puede ser no nulo; método algebraic para cuatro despejes, fixed_point para external_factor/phi_total
- fixed_point_converged null en algebraicas; no_solution significa inexistencia demostrada, no fallo numérico
- result_status in {computed,no_feasible_solution,outside_support,not_identified,undefined_denominator,failed,incomplete}; not_identified no inventa Ptarget
- phi_partial exige tau_f>0 y umbral proveedor en inversion_targets
- para problemas endógenos completos n_scalar_solutions=conteo de tabla hija; valor resumen solo si hay exactamente una solución; múltiples conservan todos los hijos y valor resumen=null
- problemas endógenos completos exigen ambos conteos; resumen solo para una raíz aislada y cero intervalos; las filas algebraicas dejan ambos conteos null; external_factor_required=s_AI*s_FN en[0,1], distinto de m_Q de sensibilidad
- computed/outside_support/no_feasible_solution=>complete; not_identified=>not_applicable; undefined_denominator=>excluded; failed=>failed; incomplete=>incomplete. no_solution=true solo no_feasible_solution; outside_support=true solo outside_support. Sin valor matemático definido los campos numéricos son null; no se truncan valores algebraicos fuera del soporte.

## B/inversion_targets.csv

Parámetros y ecuación objetivo de cada inversión

una fila por cell_id,inversion_id

PK: ['cell_id', 'inversion_id']; UK: []; orden: ['cell_id', 'inversion_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| inversion_id | text | none | false |
| tau_f_given | rate | dimensionless | true |
| supplier_share_target | rate | dimensionless | true |
| definition | text | none | false |
| evidence_ref | text | none | false |

FK: {"columns": ["cell_id"], "table": "cell_context", "target_columns": ["cell_id"], "nullable": false}

- phi_partial requiere tau_f_given en(0,1),supplier_share_target; otros objetivos fijan referencia al contrato o grilla, nunca salida deseada

## B/r1_summary.csv

Cobertura y estado de la curva completa

una fila por cell_id

PK: ['cell_id']; UK: []; orden: ['cell_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| n_components | int | none | true |
| n_rejected_crossings | int | none | false |
| no_solution | bool | none | false |
| topology_stable | bool | none | false |
| residual_bound | dec | share | true |
| geometry_error_bound | dec | rate_distance | true |
| computation_status | computation | none | false |
| reason_code | reason | none | true |
| outside_support | bool | none | false |
| corner_binding | bool | none | false |
| kink_adjacent | bool | none | false |
| admissibility_violated | bool | none | false |

FK: {"columns": ["cell_id"], "table": "cell_context", "target_columns": ["cell_id"], "nullable": false}

- complete exige n_components; si cero e inexistencia demostrada no_solution=true; incompleto no declara cero definitivo

## B/r1_components.csv

Componente conexa con ramas y geometría 2D

una fila por cell_id,component_id

PK: ['cell_id', 'component_id']; UK: []; orden: ['cell_id', 'component_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| component_id | int | none | false |
| arc_length | dec | rate_distance | false |
| tau_d_min | rate | dimensionless | false |
| tau_d_max | rate | dimensionless | false |
| tau_f_min | rate | dimensionless | false |
| tau_f_max | rate | dimensionless | false |
| n_boundary_intersections | int | none | false |
| closed_curve | bool | none | false |
| topology_kind | text | none | false |

FK: {"columns": ["cell_id"], "table": "r1_summary", "target_columns": ["cell_id"], "nullable": false}

- topology_kind in {closed_loop,open_arc,branched,isolated_point}; closed_curve=true solo closed_loop sin extremos libres; contacto con borde se informa independientemente; corrige equivalencia histórica no toca borde=>cerrada

## B/r1_vertices.csv

Vértice 2D validado en una rama lateral; no intervalo escalar

una fila por cell_id,component_id,vertex_id

PK: ['cell_id', 'component_id', 'vertex_id']; UK: []; orden: ['cell_id', 'component_id', 'vertex_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| component_id | int | none | false |
| vertex_id | int | none | false |
| tau_d | rate | dimensionless | false |
| tau_f | rate | dimensionless | false |
| side | side | none | false |
| branch_id | id | none | false |
| residual | dec | share | false |
| is_boundary | bool | none | false |
| boundary_label | text | none | true |

FK: {"columns": ["cell_id", "component_id"], "table": "r1_components", "target_columns": ["cell_id", "component_id"], "nullable": false}

- is_boundary requiere boundary_label; vertex único por ID no necesariamente por coordenada si cambian rama/lado

## B/r1_edges.csv

Arista de polilínea certificada o refinada; dos FKs a vértices

una fila por cell_id,component_id,edge_id

PK: ['cell_id', 'component_id', 'edge_id']; UK: []; orden: ['cell_id', 'component_id', 'edge_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| component_id | int | none | false |
| edge_id | int | none | false |
| from_vertex_id | int | none | false |
| to_vertex_id | int | none | false |
| branch_id | id | none | false |
| max_residual | dec | share | false |
| geometric_error_bound | dec | rate_distance | false |

FK: {"columns": ["cell_id", "component_id"], "table": "r1_components", "target_columns": ["cell_id", "component_id"], "nullable": false}

FK: {"columns": ["cell_id", "component_id", "from_vertex_id"], "table": "r1_vertices", "target_columns": ["cell_id", "component_id", "vertex_id"], "nullable": false}

FK: {"columns": ["cell_id", "component_id", "to_vertex_id"], "table": "r1_vertices", "target_columns": ["cell_id", "component_id", "vertex_id"], "nullable": false}

- sin aristas a través de salto; misma rama de from/to salvo punto de unión validado; grafo por componente conexo, IDs ordenados canónicamente

## B/r1_rejected_crossings.csv

Cruces por discontinuidad descartados con caja y ramas

una fila por cell_id,crossing_id

PK: ['cell_id', 'crossing_id']; UK: []; orden: ['cell_id', 'crossing_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| crossing_id | int | none | false |
| tau_d_low | rate | dimensionless | false |
| tau_d_high | rate | dimensionless | false |
| tau_f_low | rate | dimensionless | false |
| tau_f_high | rate | dimensionless | false |
| branch_left | id | none | false |
| branch_right | id | none | false |
| reason_code | reason | none | false |

FK: {"columns": ["cell_id"], "table": "r1_summary", "target_columns": ["cell_id"], "nullable": false}


## B/r2_sections.csv

Resumen obligatorio de cada una de las cuatro secciones

una fila por cell_id,section_id

PK: ['cell_id', 'section_id']; UK: []; orden: ['cell_id', 'section_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| section_id | text | none | false |
| n_roots_by_section | int | none | true |
| n_tangential_roots | int | none | true |
| rate_input_id | id | none | true |
| no_solution | bool | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |
| outside_support | bool | none | false |
| corner_binding | bool | none | false |
| kink_adjacent | bool | none | false |
| admissibility_violated | bool | none | false |

FK: {"columns": ["cell_id"], "table": "cell_context", "target_columns": ["cell_id"], "nullable": false}

FK: {"columns": ["rate_input_id"], "table": "tax_rate_inputs", "target_columns": ["rate_input_id"], "nullable": true}

- section_id in {tau_f_0,tau_d_0,paridad,tau_d_estatutario}; exactamente4porcell
- tau_d_estatutario exige rate_input_id verified para completar; incomplete/failed deja conteos null, no cero ficticio

## B/r2_roots.csv

Raíz de sección identificada, con parámetro escalar de ESA trayectoria

una fila por cell_id,section_id,root_index

PK: ['cell_id', 'section_id', 'root_index']; UK: []; orden: ['cell_id', 'section_id', 'root_index']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| section_id | text | none | false |
| root_index | int | none | false |
| tau_d_root | rate | dimensionless | false |
| tau_f_root | rate | dimensionless | false |
| parameter_low | dec | dimensionless | false |
| parameter_high | dec | dimensionless | false |
| root_type | text | none | false |
| side | side | none | false |
| branch_id | id | none | false |
| residual | dec | share | false |
| method_id | id | none | false |
| corner_binding | bool | none | false |
| kink_adjacent | bool | none | false |

FK: {"columns": ["cell_id", "section_id"], "table": "r2_sections", "target_columns": ["cell_id", "section_id"], "nullable": false}

- root_type in {crossing,tangent,boundary}; índices consecutivos desde0, conteos concuerdan
- trayectorias:f0:(t,0),d0:(0,t),paridad:(t,t),estatutario:(rate,t); extremos brackets pertenecen a misma rama

## B/claims.csv

Afirmación preespecificada y sus cuantificadores; ningún quiebre sin claim

una fila por claim_id

PK: ['claim_id']; UK: []; orden: ['claim_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| claim_id | id | none | false |
| claim_scope | text | none | false |
| country_id | country | none | true |
| instrument_j | instrument | none | true |
| availability_case_id | id | none | false |
| bound_variant | text | none | false |
| eta_w_block | block | none | false |
| layer | text | none | false |
| predicate | text | none | false |
| quantifier | text | none | false |
| epsilon_econ | dec | share | false |
| baseline_status | text | none | false |

- claim_scope in {global,country,country_instrument}; global=>country_id=null,instrument=null; country=>country no nulo; country_instrument=>ambos no nulos
- baseline_status in {verified,inconclusive,not_evaluated}; epsilon_econ=0.01; quantifier especifica universo de celdas y omega compatible

## B/support_breakdown_result.csv

Expansión de cuatro bloques propios; detención rho explícita, no sensibilidad Q

una fila por breakdown_id

PK: ['breakdown_id']; UK: []; orden: ['breakdown_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| breakdown_id | id | none | false |
| run_id | id | none | false |
| design_v | design | none | false |
| country_id | country | none | true |
| instrument_j | instrument | none | true |
| availability_case_id | id | none | false |
| bound_variant | text | none | false |
| eta_w_block | block | none | false |
| omega_id | id | none | true |
| claim_id | id | none | false |
| block_id | text | none | false |
| parameter_id | id | none | true |
| component_id | text | none | true |
| direction | direction | none | false |
| support_low_primary | dec | dimensionless | false |
| support_high_primary | dec | dimensionless | false |
| expansion_factor_r | dec | dimensionless | false |
| r_critical | dec | dimensionless | true |
| witness_set_id | id | none | true |
| status | text | none | false |
| domain_edge_reached | text | none | false |
| boundary_kind | text | none | false |
| boundary_value | dec | dimensionless | true |
| reached_expansion_factor | dec | dimensionless | true |
| evaluated_domain | text | none | false |
| theoretical_domain | text | none | false |
| n_components | int | none | true |
| epsilon_econ | dec | share | false |
| joint_breakdown | bool | none | false |
| scale_kind | text | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": true}

FK: {"columns": ["claim_id"], "table": "claims", "target_columns": ["claim_id"], "nullable": false}

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": true}

FK: {"columns": ["witness_set_id"], "table": "witness_sets", "target_columns": ["witness_set_id"], "nullable": true}

- block_id in {incidencia_laboral,cuna_tributaria,tecnologia,cobertura_residual}
- status in {breakdown_found,domain_exhausted_no_breakdown,declared_ladder_exhausted_no_breakdown,not_applicable_baseline_inconclusive,not_applicable_support_gap,not_applicable_not_identified,theoretical_boundary_no_breakdown,admissibility_boundary_no_breakdown,no_solution,incomplete_search}
- component_id obligatorio solo para pi individual; joint_breakdown=true exige omega_id=null y witness_set_id si hay quiebre
- breakdown_found requiere r_critical>=1,witness_set_id,n_components>=1; otro estado r_critical=null
- theoretical_boundary_no_breakdown exige boundary_kind=theoretical,reason_code y boundary_value; no afirma robustez fuera del dominio
- domain_edge_reached in {rho_upper_S4,rho_zero_limit,a_gt1,theta_gt1,theta_lt_a,kappa_positive,q_pot,eta_H,lambda_pi,s_T_marg,s_Pi_marg,ninguno}
- boundary_kind in {theoretical,admissibility,epistemic,none}; scale_kind in {aritmetica,logaritmica,escalera_discreta}
- no_solution es fallo heredado del solver, separado de inexistencia sustantiva de raíz de inversión
- computation_status: breakdown_found y estados de agotamiento/borde demostrado=>complete; not_applicable_*=>not_applicable; no_solution=>failed; incomplete_search=>incomplete. failed/incomplete/excluded requieren reason_code. Baseline verificado es condición de todo agotamiento o frontera no_breakdown.
- rho superior detenido exige edge=rho_upper_S4,reason=RHO_UPPER_S4,boundary=1,reached_expansion_factor=1,r_critical=null; inferior al límite exige edge=rho_zero_limit,reason=RHO_ZERO_LIMIT,boundary=0,factor=7/3 y evidencia lateral suficiente
- cobertura_residual usa chi_r, intensidad relativa de pagos; sin momento/crosswalk D19 admisible: status=not_applicable_not_identified,computation_status=not_applicable,reason=MOMENT_NOT_IDENTIFIED,r_critical=null,testigos null. No multiplica C2 ni inventa captura reducida.

## B/breakdown_witnesses.csv

Testigos multivariantes del conjunto de quiebre; no presume número finito de puntos

una fila por witness_set_id,component_index,witness_index,parameter_id

PK: ['witness_set_id', 'component_index', 'witness_index', 'parameter_id']; UK: []; orden: ['witness_set_id', 'component_index', 'witness_index', 'parameter_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| witness_set_id | id | none | false |
| component_index | int | none | false |
| witness_index | int | none | false |
| parameter_id | id | none | false |
| value | dec | dimensionless | false |
| omega_id | id | none | true |

FK: {"columns": ["parameter_id"], "table": "parameter_registry", "target_columns": ["parameter_id"], "nullable": false}

FK: {"columns": ["omega_id"], "table": "omega", "target_columns": ["omega_id"], "nullable": true}

FK: {"columns": ["witness_set_id"], "table": "witness_sets", "target_columns": ["witness_set_id"], "nullable": false}

- witness_set_id corresponde a soporte o sensibilidad que lo declara; cada testigo contiene todas las primitivas cambiadas y omega compatible o conjunto de estados

## B/external_requirement_sensitivity_result.csv

Escala reducida de Q, distinta de ampliar soporte propio

una fila por sensitivity_id

PK: ['sensitivity_id']; UK: []; orden: ['sensitivity_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| sensitivity_id | id | none | false |
| run_id | id | none | false |
| design_v | design | none | false |
| instrument_j | instrument | none | true |
| availability_case_id | id | none | false |
| bound_variant | text | none | false |
| eta_w_block | block | none | false |
| claim_id | id | none | false |
| scale_scope | text | none | false |
| claim_scope | text | none | false |
| country_id | country | none | true |
| m_Q_critical | rate | dimensionless | true |
| reduction_from_reported | rate | dimensionless | true |
| status | text | none | false |
| witness_set_id | id | none | true |
| epsilon_econ | dec | share | false |
| external_grid_sha256 | sha | none | false |
| computation_status | computation | none | false |
| reason_code | reason | none | true |
| scale_country_id | country | none | true |

FK: {"columns": ["claim_id"], "table": "claims", "target_columns": ["claim_id"], "nullable": false}

FK: {"columns": ["witness_set_id"], "table": "witness_sets", "target_columns": ["witness_set_id"], "nullable": true}

- scale_scope in {global,country}; claim_scope in {global,country,country_instrument},coincide con claims; country null solo claim_scope=global
- status in {breakdown_found,scale_range_exhausted_no_breakdown,not_applicable_baseline_inconclusive,no_solution,incomplete_search}
- breakdown_found exige m_Q_critical,reduction=1−m_Q_critical,witness_set_id; demás m/reduction=null
- no admite expansion_factor_r,r_critical,domain_exhausted ni declared_ladder; escala por celda prohibida
- scale_scope=country exige scale_country_id; global exige null. Independiente del country_id del claim, incluso para afirmación global.
- computation_status: breakdown_found y estados de agotamiento/borde demostrado=>complete; not_applicable_*=>not_applicable; no_solution=>failed; incomplete_search=>incomplete. failed/incomplete/excluded requieren reason_code. Baseline verificado es condición de todo agotamiento o frontera no_breakdown.

## B/convergence_result.csv

Cada cifra publicada, raíz, geometría, quiebre y clasificación

una fila por quantity_id,level_before,level_after

PK: ['quantity_id', 'level_before', 'level_after']; UK: []; orden: ['quantity_id', 'level_before', 'level_after']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| quantity_id | id | none | false |
| level_before | int | none | false |
| level_after | int | none | false |
| result_ref | text | none | false |
| method_id | id | none | false |
| value_before | dec | dimensionless | true |
| value_after | dec | dimensionless | true |
| change_bound | dec | dimensionless | true |
| tolerance | positive | dimensionless | false |
| unit | text | none | false |
| topology_before | int | none | true |
| topology_after | int | none | true |
| verdict_changes | int | none | false |
| coverage_complete | bool | none | false |
| status | text | none | false |
| evidence_ref | text | none | false |

FK: {"columns": ["evidence_ref"], "table": "numerical_evidence", "target_columns": ["evidence_ref"], "nullable": false}

- status in {pass,fail,incomplete}; pass exige cobertura completa,change_bound<=tolerance,0 cambios de veredicto y topología estable cuando aplique
- tolerancia es medida de método, no redondeo fuente; no missing tratado como0
- result_ref interno usa table_name:PK_JSON_canónico y run_id implícito del producto; NO incluye hash de su propio manifiesto. D8_post añade b_manifest_sha256 después de cerrar B. Toda referencia debe resolver una fila de tabla B.

## B/computation_coverage.csv

Trabajo reanudable, cobertura y recursos sin confundir incompleto con resultado

una fila por work_unit_id

PK: ['work_unit_id']; UK: []; orden: ['work_unit_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| work_unit_id | id | none | false |
| parent_work_unit_id | id | none | true |
| support_set_id | id | none | false |
| domain_box | json | none | false |
| algorithm_id | id | none | false |
| checkpoint_sha256 | sha | none | true |
| coverage_kind | text | none | false |
| unresolved_boxes | int | none | false |
| estimated_error | dec | dimensionless | true |
| unit | text | none | false |
| elapsed_seconds | dec | seconds | false |
| peak_bytes | int | none | false |
| status | text | none | false |
| reason_code | reason | none | true |
| evidence_ref | id | none | true |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["parent_work_unit_id"], "table": "computation_coverage", "target_columns": ["work_unit_id"], "nullable": true}

FK: {"columns": ["evidence_ref"], "table": "numerical_evidence", "target_columns": ["evidence_ref"], "nullable": true}

- coverage_kind in {evaluated,certified_pruned,pending}; status in {complete,incomplete,failed}; certified_pruned exige evidence_ref en auditoría; pending no publica cifras concluyentes
- certified_pruned exige evidence_ref no null, kind=pruning,status=pass y cota para todas las salidas afectadas

## D8_pre/input_audit_report.csv

Todos los gates previos, incluidos PASS

una fila por run_id,gate_id,scope_id

PK: ['run_id', 'gate_id', 'scope_id']; UK: []; orden: ['run_id', 'gate_id', 'scope_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| gate_id | id | none | false |
| scope_id | id | none | false |
| level | text | none | false |
| n_cells_affected | int | none | false |
| decision | text | none | false |
| note | text | none | false |
| evidence_ref | text | none | false |

FK: {"columns": ["evidence_ref"], "table": "evidence_records", "target_columns": ["evidence_ref"], "nullable": false}

- level in {hard_fail,limitation,info}; decision in {pass,fail,not_applicable}

## D8_pre/double_counting_audit.csv

Costos, bases, reporte y gravabilidad sin duplicación

una fila por run_id,mechanism

PK: ['run_id', 'mechanism']; UK: []; orden: ['run_id', 'mechanism']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| mechanism | text | none | false |
| where_counted | text | none | false |
| where_not_counted | text | none | false |
| verified_by | text | none | false |
| status | gate | none | false |
| evidence_ref | text | none | false |

FK: {"columns": ["evidence_ref"], "table": "evidence_records", "target_columns": ["evidence_ref"], "nullable": false}


## D8_pre/admissibility_report.csv

Totales de exclusión y solapamiento declarados

una fila por run_id,support_set_id

PK: ['run_id', 'support_set_id']; UK: []; orden: ['run_id', 'support_set_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| support_set_id | id | none | false |
| n_declared | int | none | false |
| n_admissible | int | none | false |
| n_violates_q_pot | int | none | false |
| n_violates_eta_H | int | none | false |
| n_violates_shares | int | none | false |
| n_violates_theory | int | none | false |
| n_excluded_union | int | none | false |
| share_discarded | dec | share | true |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

- n_admissible+n_excluded_union=n_declared; share_discarded=union/declared si declared>0; no sumar categorías solapadas
- n_declared=0 exige share_discarded=null y bloquea readiness; no división por cero

## D8_post/d8_claim_audit.csv

Afirmación y fila exacta de resultado; restricción de lectura nacional/condicional

una fila por claim_id,result_ref

PK: ['claim_id', 'result_ref']; UK: []; orden: ['claim_id', 'result_ref']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| claim_id | id | none | false |
| result_ref | text | none | false |
| scope | text | none | false |
| permitted_interpretation | text | none | false |
| source_chain_sha256 | sha | none | false |
| status | gate | none | false |
| evidence_ref | text | none | false |

FK: {"columns": ["claim_id"], "table": "claims", "target_columns": ["claim_id"], "nullable": false}

FK: {"columns": ["evidence_ref"], "table": "d8_post_evidence_records", "target_columns": ["evidence_ref"], "nullable": false}

FK: {"columns": ["result_ref"], "table": "result_references", "target_columns": ["result_ref"], "nullable": false}

- result_ref codifica archivo+PK canónica y manifest SHA; debe resolver exactamente una fila de B
- status pass exige readiness y convergence pass y no dominio omitido relevante

## D8_post/d8_coverage.csv

Cobertura íntegra de familias científicas y celdas

una fila por run_id,cell_family

PK: ['run_id', 'cell_family']; UK: []; orden: ['run_id', 'cell_family']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| cell_family | text | none | false |
| expected | int | none | false |
| observed | int | none | false |
| excluded_with_reason | int | none | false |
| unexplained_missing | int | none | false |
| audit_status | gate | none | false |

- expected=observed+excluded_with_reason+unexplained_missing; pass requiere unexplained_missing=0; exclusiones no ocultan incomplete_search

## D8_post/d8_post_audit.csv

Integridad, convergencia, geometría, llaves y divulgación posteriores

una fila por run_id,gate_id,scope_id

PK: ['run_id', 'gate_id', 'scope_id']; UK: []; orden: ['run_id', 'gate_id', 'scope_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| gate_id | id | none | false |
| scope_id | id | none | false |
| status | gate | none | false |
| reason_code | reason | none | false |
| result_ref | text | none | true |
| evidence_ref | text | none | false |

FK: {"columns": ["evidence_ref"], "table": "d8_post_evidence_records", "target_columns": ["evidence_ref"], "nullable": false}

FK: {"columns": ["result_ref"], "table": "result_references", "target_columns": ["result_ref"], "nullable": true}


## B/witness_sets.csv

Identidad única del conjunto de testigos

una fila por witness_set_id

PK: ['witness_set_id']; UK: []; orden: ['witness_set_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| witness_set_id | id | none | false |
| scope | text | none | false |
| definition | text | none | false |

- scope in {support_breakdown,external_requirement,scalar_inversion}

## B/scalar_inversion_roots.csv

Todas las soluciones de inversiones escalares endógenas, nunca curva R1

una fila por cell_id,inversion_id,root_index

PK: ['cell_id', 'inversion_id', 'root_index']; UK: []; orden: ['cell_id', 'inversion_id', 'root_index']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| inversion_id | text | none | false |
| root_index | int | none | false |
| value | dec | dimensionless | false |
| bracket_low | dec | dimensionless | false |
| bracket_high | dec | dimensionless | false |
| residual | dec | share | false |
| method_id | id | none | false |
| converged | bool | none | false |

FK: {"columns": ["cell_id", "inversion_id"], "table": "inversion_result", "target_columns": ["cell_id", "inversion_id"], "nullable": false}

- solo external_factor y phi_total; todas las raíces aisladas; intervalos continuos pertenecen a scalar_inversion_intervals; identidad no demostrada deja incomplete

## D8_pre/evidence_records.csv

Dirección de evidencia exacta en archivo autenticado, sin cuerpos de correo

una fila por evidence_ref

PK: ['evidence_ref']; UK: []; orden: ['evidence_ref']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| evidence_ref | id | none | false |
| artifact_path | path | none | false |
| artifact_sha256 | sha | none | false |
| record_pk | json | none | false |
| evidence_kind | text | none | false |
| authority_manifest_sha256 | sha | none | false |
| note | text | none | false |

- evidence_kind in {source,contract,validation,domain,computation}; record_pk objeto de PK exacta o {} para documento completo

## D8_post/result_references.csv

Referencia unívoca a fila B, usada por convergencia y claims

una fila por result_ref

PK: ['result_ref']; UK: []; orden: ['result_ref']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| result_ref | id | none | false |
| b_manifest_sha256 | sha | none | false |
| table_name | text | none | false |
| record_pk | json | none | false |
| source_chain_sha256 | sha | none | false |

- record_pk tiene exactamente las columnas PK de table_name; resolver en manifest fijado, no en el activo posterior

## D8_post/d8_post_evidence_records.csv

Evidencia posterior propia, sin añadir filas al producto D8_pre inmutable

una fila por evidence_ref

PK: ['evidence_ref']; UK: []; orden: ['evidence_ref']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| evidence_ref | id | none | false |
| artifact_path | path | none | false |
| artifact_sha256 | sha | none | false |
| record_pk | json | none | false |
| evidence_kind | text | none | false |
| authority_manifest_sha256 | sha | none | false |
| note | text | none | false |

- puede apuntar a evidencia previa por archivo/hash; las evidencias de resultados se autentican contra B definitivo

## D7/tau_domains.csv

Dominio de tasas del menú fiscal, con dos referencias globales

una fila por tau_domain_id

PK: ['tau_domain_id']; UK: []; orden: ['tau_domain_id']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| tau_domain_id | id | none | false |
| support_set_id | id | none | false |
| tau_d_support_id | id | none | false |
| tau_f_support_id | id | none | false |
| instrument_j | instrument | none | false |

FK: {"columns": ["support_set_id"], "table": "support_sets", "target_columns": ["support_set_id"], "nullable": false}

FK: {"columns": ["tau_d_support_id"], "table": "support_set", "target_columns": ["support_id"], "nullable": false}

FK: {"columns": ["tau_f_support_id"], "table": "support_set", "target_columns": ["support_id"], "nullable": false}

- ambos soportes pertenecen al set de la fila y parámetros tau_d/tau_f respectivamente; menú d exige tau_f singleton0, menú f exige tau_d singleton0; df usa ambos intervalos; se intersecta con disponibilidad del caso D4

## D7/shared_primitive_members.csv

Dependencias compartidas del intervalo tributario, sin convertirlas en cajas independientes

una fila por primitive_group_id,member_index

PK: ['primitive_group_id', 'member_index']; UK: [['primitive_group_id', 'primitive_id']]; orden: ['primitive_group_id', 'member_index']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| primitive_group_id | id | none | false |
| member_index | int | none | false |
| d6_tree_sha256 | sha | none | false |
| primitive_id | id | none | false |
| source_path | path | none | false |
| source_locator | text | none | false |
| source_sha256 | sha | none | false |
| unit | text | none | false |

- grupo contiene IDs exactos de primitivas D6 autenticadas, incluido el PIB compartido; member_index consecutivo desde0, orden primitive_id ASCII; grupo es hash de lista canónica de miembros sin su propio group_id

## B/scalar_inversion_intervals.csv

Componentes continuas de soluciones endógenas, cuando se demuestra identidad en un intervalo

una fila por cell_id,inversion_id,interval_index

PK: ['cell_id', 'inversion_id', 'interval_index']; UK: []; orden: ['cell_id', 'inversion_id', 'interval_index']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| cell_id | id | none | false |
| inversion_id | text | none | false |
| interval_index | int | none | false |
| lower | dec | dimensionless | false |
| upper | dec | dimensionless | false |
| lower_closed | bool | none | false |
| upper_closed | bool | none | false |
| residual_bound | dec | share | false |
| method_id | id | none | false |

FK: {"columns": ["cell_id", "inversion_id"], "table": "inversion_result", "target_columns": ["cell_id", "inversion_id"], "nullable": false}

- lower<upper; intervalos maximales disjuntos, ordenados por lower; demostrar ecuación en todo intervalo; nunca inferir identidad de residuos pequeños en una malla

## B/numerical_evidence.csv

Evidencia numérica autocontenida de convergencia, régimen o poda; sin hash circular de B

una fila por evidence_ref

PK: ['evidence_ref']; UK: []; orden: ['evidence_ref']

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| evidence_ref | id | none | false |
| kind | text | none | false |
| definition | text | none | false |
| result_table | text | none | true |
| record_pk | json | none | false |
| domain_box | json | none | false |
| error_bound | dec | dimensionless | true |
| unit | text | none | false |
| method_id | id | none | false |
| status | gate | none | false |

- kind in {regime,convergence,pruning,limit,coverage,root}; record_pk usa PK exacta de result_table, o {} y result_table=null para demostración de dominio; definición contiene prueba/criterio reproducible y no solo una conclusión

## B/run_manifest.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| theory_version | id | none | false |
| theory_path | path | none | false |
| theory_sha256 | sha | none | false |
| protocol_version | id | none | false |
| protocol_path | path | none | false |
| protocol_sha256 | sha | none | false |
| manifest_hash | sha | none | false |
| support_set_ids | json | none | false |
| external_grid_sha256 | sha | none | false |
| availability_matrix_hash | sha | none | false |
| availability_case_set | json | none | false |
| n_omega | int | none | false |
| n_cells | int | none | false |
| n_cells_by_availability_case | json | none | false |
| n_inadmissible | int | none | false |
| run_readiness_flag | bool | none | false |
| created_at | date | none | false |
| producer_sha256 | sha | none | false |
| environment_manifest_sha256 | sha | none | false |
| contract_sha256 | sha | none | false |
| algorithm_config_sha256 | sha | none | false |
| run_class | text | none | false |
| status | text | none | false |

- support_set_ids lista única ordenada de sets consumidos; singleton histórico se normaliza a lista
- availability_case_set lista única ordenada; n_cells_by_availability_case objeto entero por esa misma llave; suma=n_cells
- run_class in {synthetic_validation,official}; no se genera ninguno en esta ronda
- status in {prepared,complete,incomplete,failed}; protocolo futuro sucesor se autentica por selección explícita, nunca literal v1.2.7 simultáneamente obsoleto
- synthetic_validation no depende de D8_pre posterior ni habilita exportación oficial; official exige referencias al D8_pre PASS y freeze-run real. Las validaciones sintéticas entran como evidencia del auditor previo, evitando dependencia circular.
- manifest_hash es SHA del manifiesto de autoridad de planes, nunca el propio B. contract_sha256 es SHA256 de contratos/contract_manifest.json; este enumera rutas desde raíz de entrega, incluye estrategia y tres planes, excluye sí mismo. algorithm_config_sha256 autentica configuración previa.

## D7/d7_phase_report.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| phase_status | text | none | false |
| expected_countries | json | none | false |
| eligible_countries | json | none | false |
| hard_fail_count | int | none | false |
| limitation_count | int | none | false |
| ready_for_b | bool | none | false |
| ready_for_d8_input_audit | bool | none | false |

- expected_countries=country_set del caso preregistrado; ready_for_b exige todos los miembros elegibles, D6 3×|country_set|,registry completo y hard_fail_count=0
- phase_status in {prepared,complete,incomplete,blocked,failed}

## D8_pre/d8_pre_phase_report.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| status | text | none | false |
| input_gate_failures | int | none | false |
| validation_failures | int | none | false |
| ready_for_freeze_run | bool | none | false |

- status in {pass,blocked}; ready exige cero fallos y ambiente/validaciones; no resultados B oficiales para auditoría previa

## D8_post/d8_post_phase_report.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| run_id | id | none | false |
| status | text | none | false |
| result_failures | int | none | false |
| incomplete_families | int | none | false |
| ready_for_export | bool | none | false |

- ready exige0fallos/0familias incompletas y todas cifras publicadas validadas
- status in {pass,blocked}

## D7/d7_manifest.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| run_id | id | none | false |
| created_at | date | none | false |
| producer_path | path | none | false |
| producer_sha256 | sha | none | false |
| authority_package_sha256 | sha | none | false |
| authority_manifest_sha256 | sha | none | false |
| contract_sha256 | sha | none | false |
| input_dependencies | json | none | false |
| files | json | none | false |
| tree_sha256 | sha | none | false |
| phase_status | text | none | false |

- schema_version=1 de esta nueva familia; no cambia schemas históricos
- files lista exacta ordenada {path,sha256,bytes,rows}, sin sí mismo/puntero/recibo; tree SHA256 sobre proyección {path,sha256,bytes} de esa lista, JSON compacto UTF8 sin LF; bytes de archivos sí incluyen su LF final
- input_dependencies lista {role,path,sha256,tree_sha256,version,authority_package_sha256}; null solo campos no aplicables al tipo raw
- D8_pre referencia contrato D7 y validaciones sintéticas B; D8_post referencia manifiestos B oficial y D8_pre, nunca dependencia circular
- phase_status in {prepared,complete,incomplete,blocked,failed}

## D7/active_product.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| active_tree_sha256 | sha | none | false |
| active_relative_path | path | none | false |
| active_manifest_sha256 | sha | none | false |
| predecessor_reference | json | none | true |
| promotion_receipt_sha256 | sha | none | false |
| immutable_tree_sha256s | json | none | false |

- fuera del árbol inmutable; no publicar en esta ronda
- predecessor_reference null solo primera activación o objeto {path,sha256,tree_sha256}; historial preserva prefijo; recibo de promoción real debe existir

## D7/promotion_receipt.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| receipt_id | id | none | false |
| product_type | text | none | false |
| new_tree_sha256 | sha | none | false |
| old_tree_sha256 | sha | none | true |
| authority_id | id | none | false |
| checks_manifest_sha256 | sha | none | false |
| approved_action_evidence_sha256 | sha | none | false |
| promoted_at | date | none | false |

- fuera del árbol/puntero; consentimiento real no se genera en esta ronda; authority_id autenticada por manifiesto

## B/b_manifest.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| run_id | id | none | false |
| created_at | date | none | false |
| producer_path | path | none | false |
| producer_sha256 | sha | none | false |
| authority_package_sha256 | sha | none | false |
| authority_manifest_sha256 | sha | none | false |
| contract_sha256 | sha | none | false |
| input_dependencies | json | none | false |
| files | json | none | false |
| tree_sha256 | sha | none | false |
| phase_status | text | none | false |

- schema_version=1 de esta nueva familia; no cambia schemas históricos
- files lista exacta ordenada {path,sha256,bytes,rows}, sin sí mismo/puntero/recibo; tree SHA256 sobre proyección {path,sha256,bytes} de esa lista, JSON compacto UTF8 sin LF; bytes de archivos sí incluyen su LF final
- input_dependencies lista {role,path,sha256,tree_sha256,version,authority_package_sha256}; null solo campos no aplicables al tipo raw
- D8_pre referencia contrato D7 y validaciones sintéticas B; D8_post referencia manifiestos B oficial y D8_pre, nunca dependencia circular
- phase_status in {prepared,complete,incomplete,blocked,failed}

## B/active_product.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| active_tree_sha256 | sha | none | false |
| active_relative_path | path | none | false |
| active_manifest_sha256 | sha | none | false |
| predecessor_reference | json | none | true |
| promotion_receipt_sha256 | sha | none | false |
| immutable_tree_sha256s | json | none | false |

- fuera del árbol inmutable; no publicar en esta ronda
- predecessor_reference null solo primera activación o objeto {path,sha256,tree_sha256}; historial preserva prefijo; recibo de promoción real debe existir

## B/promotion_receipt.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| receipt_id | id | none | false |
| product_type | text | none | false |
| new_tree_sha256 | sha | none | false |
| old_tree_sha256 | sha | none | true |
| authority_id | id | none | false |
| checks_manifest_sha256 | sha | none | false |
| approved_action_evidence_sha256 | sha | none | false |
| promoted_at | date | none | false |

- fuera del árbol/puntero; consentimiento real no se genera en esta ronda; authority_id autenticada por manifiesto

## D8_pre/d8_pre_manifest.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| run_id | id | none | false |
| created_at | date | none | false |
| producer_path | path | none | false |
| producer_sha256 | sha | none | false |
| authority_package_sha256 | sha | none | false |
| authority_manifest_sha256 | sha | none | false |
| contract_sha256 | sha | none | false |
| input_dependencies | json | none | false |
| files | json | none | false |
| tree_sha256 | sha | none | false |
| phase_status | text | none | false |

- schema_version=1 de esta nueva familia; no cambia schemas históricos
- files lista exacta ordenada {path,sha256,bytes,rows}, sin sí mismo/puntero/recibo; tree SHA256 sobre proyección {path,sha256,bytes} de esa lista, JSON compacto UTF8 sin LF; bytes de archivos sí incluyen su LF final
- input_dependencies lista {role,path,sha256,tree_sha256,version,authority_package_sha256}; null solo campos no aplicables al tipo raw
- D8_pre referencia contrato D7 y validaciones sintéticas B; D8_post referencia manifiestos B oficial y D8_pre, nunca dependencia circular
- phase_status in {prepared,complete,incomplete,blocked,failed}

## D8_pre/active_product.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| active_tree_sha256 | sha | none | false |
| active_relative_path | path | none | false |
| active_manifest_sha256 | sha | none | false |
| predecessor_reference | json | none | true |
| promotion_receipt_sha256 | sha | none | false |
| immutable_tree_sha256s | json | none | false |

- fuera del árbol inmutable; no publicar en esta ronda
- predecessor_reference null solo primera activación o objeto {path,sha256,tree_sha256}; historial preserva prefijo; recibo de promoción real debe existir

## D8_pre/promotion_receipt.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| receipt_id | id | none | false |
| product_type | text | none | false |
| new_tree_sha256 | sha | none | false |
| old_tree_sha256 | sha | none | true |
| authority_id | id | none | false |
| checks_manifest_sha256 | sha | none | false |
| approved_action_evidence_sha256 | sha | none | false |
| promoted_at | date | none | false |

- fuera del árbol/puntero; consentimiento real no se genera en esta ronda; authority_id autenticada por manifiesto

## D8_post/d8_post_manifest.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| run_id | id | none | false |
| created_at | date | none | false |
| producer_path | path | none | false |
| producer_sha256 | sha | none | false |
| authority_package_sha256 | sha | none | false |
| authority_manifest_sha256 | sha | none | false |
| contract_sha256 | sha | none | false |
| input_dependencies | json | none | false |
| files | json | none | false |
| tree_sha256 | sha | none | false |
| phase_status | text | none | false |

- schema_version=1 de esta nueva familia; no cambia schemas históricos
- files lista exacta ordenada {path,sha256,bytes,rows}, sin sí mismo/puntero/recibo; tree SHA256 sobre proyección {path,sha256,bytes} de esa lista, JSON compacto UTF8 sin LF; bytes de archivos sí incluyen su LF final
- input_dependencies lista {role,path,sha256,tree_sha256,version,authority_package_sha256}; null solo campos no aplicables al tipo raw
- D8_pre referencia contrato D7 y validaciones sintéticas B; D8_post referencia manifiestos B oficial y D8_pre, nunca dependencia circular
- phase_status in {prepared,complete,incomplete,blocked,failed}

## D8_post/active_product.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| schema_version | int | none | false |
| product_type | text | none | false |
| active_tree_sha256 | sha | none | false |
| active_relative_path | path | none | false |
| active_manifest_sha256 | sha | none | false |
| predecessor_reference | json | none | true |
| promotion_receipt_sha256 | sha | none | false |
| immutable_tree_sha256s | json | none | false |

- fuera del árbol inmutable; no publicar en esta ronda
- predecessor_reference null solo primera activación o objeto {path,sha256,tree_sha256}; historial preserva prefijo; recibo de promoción real debe existir

## D8_post/promotion_receipt.json

Objeto JSON exacto; sin propiedades adicionales

Un objeto por archivo

PK: []; UK: []; orden: propiedades JSON canónicas

| Campo | Tipo | Unidad | Null |
|---|---|---|---|
| receipt_id | id | none | false |
| product_type | text | none | false |
| new_tree_sha256 | sha | none | false |
| old_tree_sha256 | sha | none | true |
| authority_id | id | none | false |
| checks_manifest_sha256 | sha | none | false |
| approved_action_evidence_sha256 | sha | none | false |
| promoted_at | date | none | false |

- fuera del árbol/puntero; consentimiento real no se genera en esta ronda; authority_id autenticada por manifiesto

## json_value_shapes

```json
{
  "level0_nodes": {
    "type": "array",
    "items": "dec",
    "unique": true,
    "order": "numeric ascending"
  },
  "support_set_ids": {
    "type": "array",
    "items": "atom",
    "unique": true,
    "order": "ASCII"
  },
  "availability_case_set": {
    "type": "array",
    "items": "id",
    "unique": true,
    "order": "ASCII"
  },
  "expected_countries": {
    "type": "array",
    "items": "country",
    "unique": true,
    "order": "ASCII"
  },
  "eligible_countries": {
    "type": "array",
    "items": "country",
    "unique": true,
    "order": "ASCII"
  },
  "n_cells_by_availability_case": {
    "type": "object",
    "key_type": "id",
    "value_type": "int",
    "keys": "exact availability_case_set"
  },
  "record_pk": {
    "type": "object",
    "keys": "exact referenced table primary_key",
    "values": "referenced PK types; no null"
  },
  "domain_box": {
    "type": "object",
    "key_type": "atom",
    "values": {
      "type": "object",
      "properties": {
        "lower": "dec",
        "upper": "dec",
        "lower_closed": "bool",
        "upper_closed": "bool"
      },
      "additionalProperties": false
    },
    "rules": "all primitive axes relevant to proof; lower<=upper; singleton requires both closed"
  },
  "files": {
    "type": "array",
    "order": "path ASCII",
    "unique_key": "path",
    "items": {
      "type": "object",
      "properties": {
        "path": "path",
        "sha256": "sha",
        "bytes": "int",
        "rows": "int?"
      },
      "additionalProperties": false
    },
    "rules": "rows nonnull CSV; null JSON; relative to family root"
  },
  "input_dependencies": {
    "type": "array",
    "order": "role,path ASCII",
    "unique_key": [
      "role",
      "path"
    ],
    "items": {
      "type": "object",
      "properties": {
        "role": "text",
        "path": "path",
        "sha256": "sha",
        "tree_sha256": "sha?",
        "version": "text?",
        "authority_package_sha256": "sha?"
      },
      "additionalProperties": false
    }
  },
  "predecessor_reference": {
    "type": "object",
    "properties": {
      "path": "path",
      "sha256": "sha",
      "tree_sha256": "sha"
    },
    "additionalProperties": false
  },
  "immutable_tree_sha256s": {
    "type": "array",
    "items": "sha",
    "unique": true,
    "order": "chronological prefix preserving; active is last"
  },
  "structural_key_payload": {
    "type": "object",
    "schema": "CLAVES_DE_CALCULO.json#/schemas/structural",
    "additionalProperties": false
  },
  "macro_key_payload": {
    "type": "object",
    "schema": "CLAVES_DE_CALCULO.json#/schemas/macro",
    "additionalProperties": false
  },
  "context_inputs": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "table": "text",
        "field": "text"
      },
      "additionalProperties": false
    },
    "order": "table,field ASCII; unique pair"
  },
  "result_binding": {
    "type": "object",
    "properties": {
      "family": "text",
      "table": "text",
      "value_field": "text",
      "key_fields": "array of exact PK names",
      "stored_unit": "text",
      "scale_to_declared_unit": "text"
    },
    "additionalProperties": false
  }
}
```

## key_contract

```json
"contratos/CLAVES_DE_CALCULO.json"
```

## normative_manifest

```json
{
  "path": "contratos/contract_manifest.json",
  "path_base": "delivery_root",
  "contract_sha256": "SHA256 de bytes exactos del manifiesto, incluido LF final; no hash del catálogo solo",
  "approval_scope": "todas las entradas exactas del manifiesto, incluidos tres planes y única estrategia, más el hash del propio manifiesto autenticado por la aprobación futura",
  "self_excluded": true
}
```

Unidades y normalización se conservan: normalized_flow es flujo dividido por gamma*z_m; share es cociente; rate_distance es distancia en plano fiscal; seconds segundos. Los campos unit/value_unit deben concordar con definición y fuente.

D7 declara fórmulas/operadores sin consumir resultados B. Las preimágenes de claves se especifican en CLAVES_DE_CALCULO.json y su explicación; el manifiesto contractual usa raíz de entrega, mientras fuentes productivas fijadas usan raíz de proyecto. Son espacios de rutas declarados, nunca resolución por carpeta de trabajo.


## Enmienda candidata G-NA-1
Convergencia G admite not_applicable solo según G_NA_1.md. Q07 exige pass numérico o no aplicabilidad autenticada; readiness y exportación conservan todos los gates. Sin adopción oficial ni científica.
