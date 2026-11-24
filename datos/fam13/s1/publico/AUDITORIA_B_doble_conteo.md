# B. Auditoría de doble conteo (§22.7)

**Estado:** candidato de preparación editorial S1 (rem183); fuera del manuscrito; no aceptado; no es exportación oficial.

**Alcance:** compuertas H7/H13 por sus clases auténticas y, por separado, §18.7 (double_counting_audit) como limitación documental adoptada

**Nivel de evidencia:** evidencia_documental

## Fuentes

| id | ruta | sha256 | autoridad |
|---|---|---|---|
| P_matriz_v4 | tmp/paso4_exp0_lambda_autenticada_desde_rem134/a_exp0/salida_a2/MATRIZ_REVISADA_v4.json | e020cff2bd9d7b22… | L_rem147 |
| P_registro_18_7 | tmp/paso4_supremos_gn_auditoria_desde_rem174/bloque_b/salida_1/REGISTRO_LOCALIZACION_18_7_REM174.json | 429dd087bd80cadb… | D_rem174, D_rem176, A_rem177_cierre |
| P_limites_rem175 | tmp/paso4_correcciones_extension_global_desde_rem175/PROPUESTAS_ALCANCE_LIMITACION_REM175.md | 25b27c424c2a06dc… | D_rem176, ADOPCION_AUTOR_rem176, A_rem177_cierre |
| P_adopcion_rem176 | tmp/paso4_integracion_cierre_global_desde_rem176/decisiones/REFERENCIA_ADOPCION_REM176.json | a975e3f9c48f3f8d… | D_rem176, ADOPCION_AUTOR_rem176 |

## Recuentos (conjunto, corrida y requisito por separado)

| unidad | valor |
|---|---|
| requisitos | 2 |
| corridas_consultadas | 14 |
| conjuntos | "no aplica" |

## Hallazgos

- H7: retrospectiva comprobada (F_fix solo dentro de Q)
- H13: contemporánea (c_trace inactivo, H13_NO_TRACE_FACTOR)
- §18.7: registro no localizado en las 14 corridas consultadas

## Limitaciones adoptadas

- En las 14 corridas T8 no se recuperó un double_counting_audit contemporáneo dentro del corpus examinado y delimitado en rem174. Se conserva como limitación documental la falta de ese registro recuperado; este resultado no acredita que el auditor nunca se ejecutara. El generador D8 localizado no sustituye una salida ligada a cada corrida. H7/H13 y D-EXP0 conservan su alcance y no satisfacen por sí solos §18.7. No se afirma una auditoría contemporánea ni un PASS no documentados. Cualquier revisión retrospectiva o auditoría futura deberá identificar fecha, fuentes, alcance y limitaciones propios, sin retrofechar ni alterar las salidas históricas.

## Compuertas H7/H13 (clases auténticas)

| requisito | clase | resultado | evidencia |
|---|---|---|---|
| H7 | retrospectiva_comprobada | comprobada | F_fix solo existe en external.py dentro de Q (cotas sin_addback/addback_completo) con identities() T1=1e-12; ningún otro módulo lo suma |
| H13 | contemporanea | satisfecha | parameter_registry c_trace inactive_reason=H13_NO_TRACE_FACTOR; G11 trace_inactive [450] |

## §18.7 — limitación documental adoptada (objeto distinto de H7/H13)

> En las 14 corridas T8 no se recuperó un double_counting_audit contemporáneo dentro del corpus examinado y delimitado en rem174. Se conserva como limitación documental la falta de ese registro recuperado; este resultado no acredita que el auditor nunca se ejecutara. El generador D8 localizado no sustituye una salida ligada a cada corrida. H7/H13 y D-EXP0 conservan su alcance y no satisfacen por sí solos §18.7. No se afirma una auditoría contemporánea ni un PASS no documentados. Cualquier revisión retrospectiva o auditoría futura deberá identificar fecha, fuentes, alcance y limitaciones propios, sin retrofechar ni alterar las salidas históricas.

Adopción del autor: «Adopto las delimitaciones de C3, E4, Exp. 2 y T4 y el tratamiento de §18.7 como limitación documental, conforme al dictamen rem176. Mantengo las tablas del cuerpo como etapa posterior. No activo la asignación a D8 ni una ampliación de cálculos.»

Resultado por corrida: {"no localizado en el corpus revisado": 14}.

Campos del registro §18.7: {"mechanism": "no_localizado", "where_counted": "no_localizado", "where_not_counted": "no_localizado", "verified_by": "no_localizado", "status": "no_localizado"} (no se inventan).

No se deduce nada sobre si el auditor se ejecutó; no se asigna D8; H7/H13 no equivalen al registro §18.7.
