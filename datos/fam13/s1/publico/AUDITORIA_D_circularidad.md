# D. Auditoría de circularidad (§22.7)

**Estado:** candidato de preparación editorial S1 (rem183); fuera del manuscrito; no aceptado; no es exportación oficial.

**Alcance:** reconstrucción aceptada de circularity_audit (rem133), rotulada como reconstrucción; no es documento contemporáneo

**Nivel de evidencia:** reconstrucción documental

## Fuentes

| id | ruta | sha256 | autoridad |
|---|---|---|---|
| P_matriz_v4 | tmp/paso4_exp0_lambda_autenticada_desde_rem134/a_exp0/salida_a2/MATRIZ_REVISADA_v4.json | e020cff2bd9d7b22… | L_rem147 |
| P_ficha_dexp0 | tmp/paso4_conexion_cinco_filas_t8_desde_rem145/decisiones/FICHA_D_EXP0_REM145.md | f72ff8dbd605f677… | L_rem147 |

## Recuentos (conjunto, corrida y requisito por separado)

| unidad | valor |
|---|---|
| requisitos | 2 |
| corridas | "no aplica" |
| conjuntos | "no aplica" |

## Hallazgos

- la reconstrucción no se presenta como documento contemporáneo
- una búsqueda sin hallazgos no prueba ausencia de circularidad ni su presencia

## Limitaciones adoptadas

- la circularidad es una reconstrucción (D-EXP0)
- no localizado en el corpus revisado
- Gate 0 sin PASS global

## Requisitos (reconstrucción rotulada)

| requisito | clase | resultado | evidencia |
|---|---|---|---|
| H5 | retrospectiva_comprobada | comprobada_con_reconstruccion | G11 (construir_d7.py (toolchain S5, 5f15b2193f3caff1) líneas [452]) cubre escenarios/c_legal/c_trace; circularity_audit RECONSTRUIDO en rem133: {'PASS': 44, 'DERIVADO_DEL_REQUERIMIENTO_EXTERNO': 5, 'REQUERIMIENTO_EXTERNO_DEL_COMPANERO': 2, 'INACTIVO': 11} |
| G0-CIRCULARIDAD | reconstruccion_rem133 | reconstruida_hoy | no existía como objeto; reconstruida en A4 con {'PASS': 44, 'DERIVADO_DEL_REQUERIMIENTO_EXTERNO': 5, 'REQUERIMIENTO_EXTERNO_DEL_COMPANERO': 2, 'INACTIVO': 11} |

## Clases

| clase | contenido |
|---|---|
| contemporanea | no localizado en el corpus revisado (G0-CIRCULARIDAD: «no existía como objeto») |
| retrospectiva | H5 comprobada con reconstrucción (G11 cubre escenarios/c_legal/c_trace) |
| reconstruccion | G0-CIRCULARIDAD reconstruida (rem133, A4) |
| no_localizado | circularity_audit contemporáneo por corrida |
