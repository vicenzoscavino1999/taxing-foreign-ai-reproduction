# A. Auditoría de insumos (§22.7)

**Estado:** candidato de preparación editorial S1 (rem183); fuera del manuscrito; no aceptado; no es exportación oficial.

**Alcance:** reporte de las entradas (Exp0) de las 14 corridas T8 y de los 120 conjuntos D7 según D-EXP0 adoptada; ensamblado documental, no ejecución nueva ni certificación retrospectiva

**Nivel de evidencia:** evidencia_documental (clases separadas de la matriz v4)

## Fuentes

| id | ruta | sha256 | autoridad |
|---|---|---|---|
| P_ficha_dexp0 | tmp/paso4_conexion_cinco_filas_t8_desde_rem145/decisiones/FICHA_D_EXP0_REM145.md | f72ff8dbd605f677… | L_rem147 |
| P_aut_dexp0 | tmp/paso4_cinco_filas_exp0_desde_rem144/decisiones/AUTENTICACION_FUENTES_D_EXP0.json | 7a91ffeb69aea428… | L_rem147 |
| P_matriz_v4 | tmp/paso4_exp0_lambda_autenticada_desde_rem134/a_exp0/salida_a2/MATRIZ_REVISADA_v4.json | e020cff2bd9d7b22… | L_rem147 |
| P_input_audit_v4 | tmp/paso4_exp0_lambda_autenticada_desde_rem134/a_exp0/salida_a2/input_audit_report_v4.json | fd02e9a589d6043b… | L_rem147 |
| P_admisibilidad | tmp/paso4_conciliacion_portabilidad_desde_rem107/conciliacion/ensamblajes/admissibility_report.csv | d35ccaac6f6ab8c4… | D_rem108 |
| P_registro_18_7 | tmp/paso4_supremos_gn_auditoria_desde_rem174/bloque_b/salida_1/REGISTRO_LOCALIZACION_18_7_REM174.json | 429dd087bd80cadb… | D_rem174, D_rem176, A_rem177_cierre |
| P_t8_vista_C5B | tmp/paso4_emision_cinco_filas_t8_desde_rem146/t8_c5b_vista_T8_C5B/VISTA_T8_CAPTURA.jsonl | 12826a0518b4a747… | L_rem147 |

## Recuentos (conjunto, corrida y requisito por separado)

| unidad | valor |
|---|---|
| conjuntos | 120 |
| corridas | 14 |
| requisitos | 42 |
| requisitos_por_clase | {"obligacion_fase_posterior": 9, "retrospectiva_comprobada": 19, "contemporanea": 10, "retrospectiva_comprobada_con_hallazgo": 1, "reconstruccion_rem133": 1, "limitacion_no_recuperable": 2} |
| corridas_en_T8 | 14 |
| corridas_en_input_audit_report_v4 | 14 |

## Hallazgos

- H30 es contemporánea con limitaciones (fase_estado complete_with_limitations en su evidencia almacenada)
- R1: 2.520 vinculaciones coinciden con el rango documentado; R1 no valida empíricamente los escenarios
- H4: excepción formal η_w = 0,3 sin efecto en los 120 conjuntos D7 comprobados (L_rem147 l.565); no se afirma ausencia universal de calibración oculta
- E-INPUT_AUDIT y E-RUN_MANIFEST: no localizados en el corpus revisado (la matriz almacena «no_existio»; D-EXP0 no afirma que nunca existieran)

## Limitaciones adoptadas

- Adoptar D-EXP0 para reportar las entradas de las catorce corridas T8 mediante las clases separadas de la matriz v4: evidencia contemporánea, incluida H30 complete_with_limitations; evidencia retrospectiva comprobada R1/H4; reconstrucción de circularidad; y documentos contemporáneos no localizados en el corpus revisado. R1 no valida empíricamente los escenarios. La excepción formal H4 de eta_w=0,3 se declara sin efecto en los 120 conjuntos D7 comprobados y sin afirmar ausencia universal de calibración oculta. La selección planificada completa sigue desconocida y Gate 0 no recibe un PASS global. No se retrofechan auditorías ni se alteran resultados o código histórico.
- Gate 0 sin PASS global (L_rem147 /Gate0_global_PASS = false)
- la selección planificada completa sigue desconocida
- no localizado en el corpus revisado

## Clases D-EXP0 (se reportan por separado; no se suman en un PASS de Gate 0)

| clase | requisitos |
|---|---|
| contemporanea | H3, H9, H13, H27, H30, G0-REGISTRO, G0-SOPORTES, G0-ADMISIBILIDAD, G0-HARD_FAIL, G0-INADMISIBLES |
| retrospectiva_comprobada | H2, H4, H5, H6, H7, H8, H10, H14, H15, H16, H17, H19, H20, H21, H22, H23, H26, R1, R3, R4 |
| reconstruccion_circularidad | G0-CIRCULARIDAD |
| documentos_contemporaneos_no_localizados | E-INPUT_AUDIT, E-RUN_MANIFEST |
| obligacion_fase_posterior | H1, H11, H12, H18, H24, H25, H28, H28-bis, H29 |

## Requisitos de la matriz v4 (42)

| requisito | clase almacenada | clase D-EXP0 | resultado almacenado |
|---|---|---|---|
| H1 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H2 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H3 | contemporanea | contemporánea | satisfecha |
| H4 | retrospectiva_comprobada_con_hallazgo | retrospectiva comprobada (con hallazgo formal) | sin_calibracion_oculta; hallazgo_formal_sin_impacto_numerico |
| H5 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_con_reconstruccion |
| H6 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H7 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H8 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H9 | contemporanea | contemporánea | satisfecha |
| H10 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H11 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H12 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H13 | contemporanea | contemporánea | satisfecha |
| H14 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H15 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H16 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H17 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_estatica |
| H18 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H19 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_estatica |
| H20 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_inactiva |
| H21 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H22 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H23 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H24 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H25 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H26 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| H27 | contemporanea | contemporánea | satisfecha |
| H28 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H28-bis | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H29 | obligacion_fase_posterior | obligación de fase posterior | asignada_a_presentacion_o_exportacion |
| H30 | contemporanea | contemporánea | comprobada |
| R1 | retrospectiva_comprobada | retrospectiva comprobada | comprobada |
| R3 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_no_usada |
| R4 | retrospectiva_comprobada | retrospectiva comprobada | comprobada_definitivas |
| G0-REGISTRO | contemporanea | contemporánea | satisfecha_parcial |
| G0-SOPORTES | contemporanea | contemporánea | satisfecha |
| G0-ADMISIBILIDAD | contemporanea | contemporánea | satisfecha_datos |
| G0-CIRCULARIDAD | reconstruccion_rem133 | reconstrucción (circularidad) | reconstruida_hoy |
| G0-HARD_FAIL | contemporanea | contemporánea | satisfecha_en_D7 |
| G0-INADMISIBLES | contemporanea | contemporánea | satisfecha |
| E-INPUT_AUDIT | limitacion_no_recuperable | documento contemporáneo no localizado en el corpus revisado | no_existio |
| E-RUN_MANIFEST | limitacion_no_recuperable | documento contemporáneo no localizado en el corpus revisado | no_existio |

## Corridas (14)

| run_id | entrega (ID) | filas T8 | filas input_audit_report v4 | §18.7 |
|---|---|---|---|---|
| BRUN-050091213b198d7cd7ba9ea2 | PRIV-e0d9520ea94836bc | 66 | 34 | no localizado en el corpus revisado |
| BRUN-1368187e9a43de0d95926dca | PRIV-2305a8b97732707d | 684 | 34 | no localizado en el corpus revisado |
| BRUN-47e3d9f48d2b65e9ddeed02f | PRIV-5fa75f5a41e0f7bf | 12 | 34 | no localizado en el corpus revisado |
| BRUN-4ef8507fcdefbddc55dbc3b7 | PRIV-b29481d6bdc2724f | 1014 | 34 | no localizado en el corpus revisado |
| BRUN-5b35ba3f51bc08bd48b384bd | PRIV-3f0dc579a8229f90 | 3456 | 34 | no localizado en el corpus revisado |
| BRUN-612818cb081c6797d4923b4d | PRIV-5f4f1376e446e66d | 2280 | 34 | no localizado en el corpus revisado |
| BRUN-63a9e9ea157b2faaf317ae61 | PRIV-81b14948c08a0578 | 798 | 34 | no localizado en el corpus revisado |
| BRUN-7bdfe0a1bee57298e31e1b34 | PRIV-6a906043e947a85a | 606 | 34 | no localizado en el corpus revisado |
| BRUN-991c466a1938ddbf2192eefb | PRIV-5dc13bff815c0803 | 1128 | 34 | no localizado en el corpus revisado |
| BRUN-9c6c66e7af8b139a613b1c3f | PRIV-305f4e4a4e12a7b9 | 972 | 34 | no localizado en el corpus revisado |
| BRUN-a81e3f45f7111e18b1f39370 | PRIV-4ce918ee5d358adc | 132 | 34 | no localizado en el corpus revisado |
| BRUN-c5af32a993773f5258ce570f | PRIV-cad73f3c6d57303d | 894 | 34 | no localizado en el corpus revisado |
| BRUN-cb33e6b24039acc84fb1a065 | PRIV-d527e684f6bcfda3 | 1608 | 34 | no localizado en el corpus revisado |
| BRUN-f5f58960bbf9017776d3d7fc | PRIV-da59a94b81b53901 | 6 | 34 | no localizado en el corpus revisado |

## Conjuntos (120)

| support_set_id | capa | n_declared | n_admissible | share_discarded |
|---|---|---|---|---|
| CMP-E1.macro | base | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| CMP-E1.macro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro | base | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| CMP-E1.micro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro | base | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.macro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro | base | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2023p.micro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro | base | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.macro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro | base | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| COL-E2-2023.2024p.micro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro | base | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E0E3.macro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro | base | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E0E3.micro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E1.macro | base | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E1.macro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E1.micro | base | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ABL-COV | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ABL-ENF | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.COORD | coordination | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.EXT-Q | external_sensitivity | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ROB-LABH | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ROB-LABW | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ROB-RES | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ROB-TAX | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.ROB-TEC | robustness | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.STR-040 | domain_stress | 546750000 | 546750000 | 0.0 |
| PER-E1.micro.STR-080 | domain_stress | 546750000 | 546750000 | 0.0 |
