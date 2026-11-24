# RESULTADO FAM10 — Exp8 (ENF por afirmación, síntesis e integración de las doce COV)

Fecha: 2026-11-18 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original y los libros se consultaron en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | **Revisada y cerrada en su alcance documental y aritmético por Codex el 18 de noviembre de 2026**. El paquete contiene el código de las tres operaciones (U41 copia exacta; U44 y U47 proyecciones saneadas ligadas a su original), el bloque científico de la auditoría rem148, las entradas históricas, los resúmenes de los libros que lee el código, las referencias y la receta. Las tres etapas, sus validaciones y sus comparaciones están conectadas en una sola orden y probadas. |
| F10-ENF-AFIRMACION (RD) | Regenerada con U41 sobre el integral ENF **nuevo** de FAM08. 1.728 filas sin diferencias científicas frente a e0670acc…; 1.720 líneas idénticas y 8 que difieren solo en `inf.garantia_clave.segundos` (duración de la T2 nueva). Huella ed2e098b…. |
| U42 | **No localizado.** Se ejecutó la parte científica de la auditoría rem148 sobre el producto nuevo: 6/6 comprobaciones, más el resumen por país. **Decisión del autor (2026-11-18): límite adoptado L-ENF-AFIRMACION-AUDITORIA-REM148.** La fila sigue RD y ese bloque es la validación del ENF regenerado. No acredita la identidad de U42 (ver «U42: lo verificado y su límite» y «Decisión del autor sobre U42»). |
| F10-SINTESIS (RD) | Regenerada con U44 sobre el ENF nuevo validado, la conciliación COV de FAM11, el suplemento P7 y las dos versiones de Q local de FAM12. 0 diferencias científicas frente a rem160; los 11 recuentos del libro rem161 coinciden. |
| F10-INTEGRACION (RD, aritmética exacta) | Regenerada con U47 sobre la síntesis nueva y la lectura B1 → B2 validada de FAM11. Cambian exactamente las doce claves aceptadas en rem170/rem171; las otras 1.716 líneas son idénticas byte a byte a la síntesis nueva. 0 diferencias científicas frente a rem171 en filas, resolución, resumen y manifiesto; los 15 recuentos del libro rem171 coinciden. |
| Orden única | `fam10-tabla`: código 0 y `cumple: true` en 31,9 s (`salidas/fam10/tabla_03`). |
| Reproducción completa | Pendiente (Paso 3). Las entradas de esta prueba tienen procedencia mixta. |

## Orden única probada

Desde la base, con el intérprete de `.venv-fam01` y `PYTHONHASHSEED=0`.
`py` abrevia `<python de .venv-fam01> -B -P -s -X utf8 reproducir.py`.

```
py fam10-tabla \
  --entrada enf_integral=salidas/fam08/mixta_03/integral \
  --entrada registro_enf_integral=salidas/fam08/mixta_03/integral.comparacion.json \
  --entrada cov=salidas/fam11/mixta_01 \
  --entrada registro_cov=salidas/fam11/mixta_01.comparacion.json \
  --entrada p7=salidas/p7_suplemento_08.json \
  --entrada q_local=salidas/q_local_08 \
  --entrada b1=salidas/fam11/piloto_01/B1 \
  --entrada validacion_b1=salidas/fam11/piloto_01/B1.validacion.json \
  --entrada b2=salidas/fam11/piloto_01/B2 \
  --entrada validacion_b2=salidas/fam11/piloto_01/B2.validacion.json \
  --salida salidas/fam10/tabla_03
```

Antes de crear la carpeta, la orden comprueba las 45 piezas de
`fuentes_fam10.json` y las diez entradas con sus registros. Luego corre en
cadena:

1. ENF;
2. `fam10-validar` de ENF;
3. SINTESIS, con la carpeta ENF y su registro;
4. `fam10-validar` de SINTESIS;
5. INTEGRACION, con la síntesis y su registro;
6. `fam10-validar` de INTEGRACION.

Las referencias solo se abren después, en las tres comparaciones.
`tabla.json` reúne los pasos, los estados y la tabla final:

- filas: `integracion/sintesis/EXP8_POR_AFIRMACION.jsonl`;
- resumen: `integracion/sintesis/RESUMEN_EXP8.json`;
- resolución de las doce: `integracion/sintesis/COV12_RESOLUCION_GLOBAL.jsonl`.

La forma por etapas (`fam10-etapa`, `fam10-validar`, `fam10-comparar`) es
equivalente. `fam10-receta` la lista (`salidas/fam10/receta_01.json`).

## Entradas: qué necesita cada etapa y cómo se obtiene

Todas las entradas deben estar **dentro de la base**; si no, la orden se
niega (`ENTRADA_FUERA_DE_LA_BASE`). El nombre de carpeta es libre y no hace
falta una carpeta `salidas/` previa: en la copia de otra carpeta, P7 y Q
estaban en `insumos/` y la salida en `otra/`. Los registros de FAM08 y FAM11
nombran la ruta de su carpeta, así que esas carpetas van en la ruta que
declara su registro, o se regeneran con su receta.

| Etapa | Entrada | Probada con | Cómo obtenerla | Procedencia |
|---|---|---|---|---|
| ENF | `enf_integral`, `registro_enf_integral` | `salidas/fam08/mixta_03/integral` y su `.comparacion.json` | `fam08-receta`, paso integral: `fam08-integrar … --salida <c>/integral` y `fam08-comparar --tarea INTEGRAL` aceptada | **Mixta**: T1 guardada (rem127, incompleta, recuperada con el certificado guardado); T2 **nueva** (`salidas/fam08/piloto_02/ABL-ENF-T2`); T3–T6 guardadas (rem128); mallas mixtas (tres mallas piloto nuevas: d con 5 filas, f con 5 y df con 25; el resto del producto guardado) |
| SINTESIS | `enf`, `validacion_enf` | la etapa ENF de la misma orden | `fam10-etapa --tarea ENF` + `fam10-validar` | nueva |
| SINTESIS | `cov`, `registro_cov` | `salidas/fam11/mixta_01` y su `.comparacion.json` | `fam11-receta`, ensamblado y conciliación: `fam11-ensamblar` + `fam11-comparar --tarea ENSAMBLADO` aceptada | **Mixta**: ABL-COV-T1 **nueva**; T2–T6 guardadas (rem151) |
| SINTESIS | `p7` | `salidas/p7_suplemento_08.json` | `p7-suplemento --salida salidas/p7_suplemento_<n>.json` (concordante) | FAM12 |
| SINTESIS | `q_local` | `salidas/q_local_08` | `q-local --salida salidas/q_local_<n>` (concordante) | FAM12: aritmética exacta sobre posiciones guardadas |
| INTEGRACION | `sintesis`, `validacion_sintesis` | la etapa SINTESIS de la misma orden | `fam10-etapa --tarea SINTESIS` + `fam10-validar` | nueva |
| INTEGRACION | `b1`, `validacion_b1`, `b2`, `validacion_b2` | `salidas/fam11/piloto_01/B1` y `B2` con sus `.validacion.json` | `fam11-unidad --tarea B1`; `fam11-unidad --tarea B2 --b1 …`; `fam11-validar` de cada una | nuevas (B2 sobre ese B1; la orden exige el enlace) |

Cada entrada se acepta solo con su registro aceptado y con las huellas que
ese registro (o la ejecución) fija:

- `fam08-integrar` y `fam11-ensamblar` deben tener éxito, y su comparación
  debe estar aceptada para esa carpeta;
- B1/B2 necesitan `fam11-validar` aceptado, con la evidencia, la lectura y la
  validación sin cambios;
- P7 y Q deben ser concordantes;
- las etapas FAM10 necesitan su registro de `fam10-validar` aceptado para
  esos bytes.

## Insumos históricos y piezas reutilizadas (`fuentes_fam10.json`)

Herramienta: `extraccion/extraer_fam10.py`, en solo lectura desde el
original y el directorio de los libros. Copió 42 archivos (38,8 MB). Hay 7
proyecciones saneadas, cada una con su original. 24 actos se autentican solo
por huella. Las rutas personales son 0.

- **Código**:
  - U41 `conciliar_exp8_rem147.py` (8e9d207c…), copia exacta;
  - U44 `construir_sintesis_rem160.py`: proyección c32b83d8… del original
    e96814df…;
  - U47 `construir_integracion_rem170.py`: proyección cc9f79d2… del original
    95493c61…;
  - el bloque científico de la auditoría rem148: líneas 49–116 de
    `review_20261105_rem148_audit.py` (d226ad70…), copia exacta (693070a7…).
- **Entradas históricas en la raíz Exp8** (`nucleo_s6/exp8`, espejo de
  `tmp/<área>/<rel>`):
  - T7_anexo (070f3c8e…) y EXP8_TABLA (8e43185e…) de rem108;
  - las 16 filas padre que U41 lee para el cell_id de las robustas. Son los
    mismos bytes que `referencias/fam01/originales/…`;
  - el esquema declarado de rem170 (f4e47445…).
- **Autoridad** (`datos/fam10/autoridad/`): resúmenes de los siete libros
  que U44/U47 cargan. Contienen solo los campos que el código lee, ligados a
  la huella del original:
  - ENF rem148 (74342fd0…);
  - COV rem152;
  - P7 rem155;
  - Q rem159;
  - Q_DIAG rem156;
  - ENF_ORIGEN rem132;
  - elección m_Q.

  Los dictámenes (rem148/149/157/158/159/161/170/171) y los libros B1/B2 y de
  la síntesis se autentican por huella; no se copian.
- **Reutilizadas de FAM11**:
  - `datos/fam11/fuentes/CONTEXTO_COL_POR_GRUPO.json` (papel soporte_rem162);
  - como referencias, solo en la comparación: `datos/fam11/cov/ENF_POR_AFIRMACION.jsonl`
    (e0670acc…) y `referencias/fam11/rem170/COV12_RESOLUCION_GLOBAL.jsonl` (ac182268…).
- **Referencias** (`referencias/fam10/`):
  - rem147: COBERTURA_EXP8.json/.md y RESUMEN_POR_PAIS.json;
  - rem160 y rem171: filas (proyecciones a43756e1… de 816209e4… y 55157838…
    de b4abf72c…), resumen y manifiesto;
  - resúmenes de los libros rem148, rem161 y rem171.

## Adaptaciones (declaradas en `src/fam10.py`)

Ninguna cambia fórmulas, claves, tolerancias, criterios ni serialización.
Cada sustitución es única y se comprueba sobre los bytes autenticados
(`fam10-comprobar`: 4/4 guiones compilan).

- **GUION-v1**: cada guion corre en el proceso desde sus bytes, con
  cwd = la base y rutas relativas.
- **RAIZ-EXP8-v1**: la raíz histórica es `nucleo_s6/exp8`.
- **ENTRADAS-ENF-v1** (U41, 1 sustitución): las cuatro fuentes rem131 se
  leen del integral nuevo (`conciliacion/`, `ensamblado/`). Sus huellas son
  las fijadas por su ejecución, en `fuentes/AUTENTICACION_LOCAL_FAM10.json`,
  que ocupa el papel de AUTENTICACION_FUENTES_REM147.
- **MARCADOR-W-v1 / MARCADOR-R-v1** (U44): el directorio de los libros y la
  raíz histórica son marcadores que solo aparecen en rutas de procedencia.
  Nada se lee de ellos.
- **AUTORIDAD-EXTRAIDA-v1** (U44): los libros se cargan desde sus
  resúmenes; los dictámenes, por huella.
- **ENLACE-SINTESIS-v1** (U44): los cinco productos de entrada son los
  nuevos, ligados a sus registros (`ENLACE_SINTESIS.json`). El campo
  `autorizada_por` del manifiesto nombra el **papel** (libro histórico y su
  huella), no una aceptación de Codex de estos bytes.
- **Q-LOCAL-v1** (U44): las filas `posicion`/`afirmacion` de
  `q_local_<versión>.jsonl` ocupan las listas de `resultado.json`. Se exige
  la versión en la cabecera y en cada fila.
- **ENLACE-INTEGRACION-v1** (U47, 2 sustituciones):
  - S es la síntesis nueva;
  - las 26 claves de autenticación las ocupan piezas declaradas en
    `enlace/ENLACE_INTEGRACION.json`. Los libros B1/B2, la auditoría y el
    enlace de las doce son **locales** y derivan de la lectura validada; no
    son libros de Codex. El papel del dictamen rem170 lo ocupa el registro
    de `fam11-validar` B2.
  - Los nombres de los actos históricos que U47 escribe en
    `resolucion_global.procedencia` son **etiquetas de papel**; sus huellas
    son las de las piezas locales.
- **AUDITORIA-REM148-v1** (4 sustituciones de ruta): el bloque de auditoría
  lee el integral nuevo y el producto nuevo.

## Resultado de cada operación

### F10-ENF-AFIRMACION

- **Etapa**: U41, código 0. Escribe `COBERTURA_EXP8.json` (conforme, sin
  fallos), `ENF_POR_AFIRMACION.jsonl` (ed2e098b…), `RESUMEN_POR_PAIS.json` y
  `COBERTURA_EXP8.md`. Lee 32 filas padre: dos por cada robusta.
- **Validación sin referencia** (bloque de la auditoría rem148 sobre los
  bytes nuevos):
  - las 6 comprobaciones de la auditoría:
    `source_and_product_universes`, `T7_original_categories`,
    `claims_independently_joined_with_certified_bounds`,
    `3449_slots_1724_exact_cells`,
    `economic_margins_also_exceed_report_tolerance` y
    `accepted_sources_unchanged_by_join`;
  - 1.705 inconclusas preservadas, 4 que solo descartan la robustez
    infactible, 3 que solo descartan la factible y 16 robustas padre sin
    decisión ENF;
  - 3.449 posiciones enlazadas por (unidad, cell_id), con G padre igual; las
    1.724 celdas únicas son exactamente las de `brechas_celdas`;
  - 1.705 pares con signos opuestos certificados;
  - margen mínimo exacto 611759196644110904590311/7555786372591432341913600
    (≈ 0,0809657);
  - posiciones por garantía: 2.781 T1 recuperada, 352 resolución del no
    alcanzado y 316 tarea completa.

  La estructura también cumple:
  - 1.728 filas únicas, con la serialización de U41 reproducible;
  - la huella del producto declarada en la cobertura;
  - dos filas padre por robusta;
  - el resumen por país igual a las afirmaciones reconstruidas (línea 175 de
    la auditoría).
- **Comparación** (después de validar):
  - **Filas frente a e0670acc…, por afirmación**: mismas 1.728 claves y el
    mismo orden. 1.720 líneas son idénticas. Las 8 restantes difieren solo en
    `inf.garantia_clave.segundos`, cada una igual a la
    `fila_historica.segundos` de su clave en el integral nuevo. Es la
    duración de la T2 recalculada, no un dato científico, y por eso la
    huella del archivo cambia.
  - **COBERTURA_EXP8.json**: sin diferencias científicas. Cambian la huella
    del producto, la ruta y la huella de la autenticación local y la huella
    de `enf_techos_integrados` (46ea8d72… frente a 31ee1d74…). Cada una está
    ligada a su archivo nuevo.
  - **COBERTURA_EXP8.md y RESUMEN_POR_PAIS.json**: idénticos byte a byte.
  - **Libro rem148**: coinciden los 10 recuentos (afirmaciones, padre
    inconclusas, 1.705/4/3/16, 3.449 posiciones, 1.724 celdas, margen
    mínimo y distribución por país) y las cotas por fila de las 1.728
    afirmaciones.

### U42: lo verificado y su límite

**Búsqueda.** El catálogo y el índice del paquete rem197 registran U42 como
«validador, requerido, piezas: ninguna, NO_LOCALIZADO_PROPUESTA_LIMITACION».
En el área rem147 del original (solo lectura) no hay ninguna pieza que valide
el producto ENF. Los guiones presentes son:

- `conciliar_exp8_rem147.py` (U41) y dos intentos fallidos guardados como
  `.py.txt`;
- `siete_casos_rem147.py`, una búsqueda e inventario de los siete casos;
- `autenticar_fuentes_rem147.py`;
- los guiones administrativos;
- las piezas COV de `paquete_ablaciones`.

U42 sigue sin localizarse, así que no se pudo acreditar ni ejecutar.

**Base de la aceptación.** El dictamen rem148 (§3) aceptó e0670acc… por la
reconstrucción independiente del revisor (`review_20261105_rem148_audit.py`
y su `.json`), no por un validador de la entrega.

**Lo verificado de forma independiente** (resultado, separado del límite).
El bloque científico de esa auditoría (líneas 49–116), ejecutado sobre el
producto nuevo y el integral nuevo, rehace:

- los enlaces por afirmación desde T7/EXP8_TABLA y las filas padre;
- la igualdad de unidad, cell_id, G_T7, estado, K1, C2, G, dG, clave y origen
  en cada posición;
- las cotas certificadas con fracciones, incluido el encierro del límite del
  caso no alcanzado d59edf8a, sin fabricar un máximo;
- la conclusión de cada afirmación.

Todo concuerda: 6/6 comprobaciones; las cotas por fila son iguales a las del
libro rem148 en las 1.728 afirmaciones; el resumen por país es igual a las
afirmaciones reconstruidas.

**Límite.**

- No se ejecutan las líneas 1–48 y 117–222 de la auditoría. Tratan de la
  línea base del revisor, el sello y el inventario de rem147, el censo COV,
  los siete casos, el reloj y la transcripción; la única excepción, la
  línea 175, se reproduce.
- La auditoría es la comprobación documental de un revisor:
  - no acredita la identidad de U42;
  - no adopta L-ENF-AFIRMACION-VALIDADOR-REM191 (propuesta, sin efecto hasta
    decisión).

  La fila conserva RD sin validador propio mientras no se decida.

**Decidido el 2026-11-18.** El autor mantiene la fila en RD y acepta ese
bloque como validación del ENF regenerado, con estos mismos límites. El
límite adoptado es `L-ENF-AFIRMACION-AUDITORIA-REM148` y ocupa el lugar de la
propuesta L-ENF-AFIRMACION-VALIDADOR-REM191. U42 sigue sin localizarse.

### F10-SINTESIS

- **Etapa**: U44, código 0, con todos sus cotejos internos cumplidos.
- **Validación sin referencia**: 17/17 comprobaciones derivadas de las filas
  y de las entradas:
  - enlace por clave y lado con los campos de ENF, COV, Q por versión y P7,
    sin discrepancias;
  - padre: 1.712 inconclusas y 16 robustas MEX;
  - ENF con P7: 1.712 `inconclusa_preservada` y 16 sin decidir;
  - COV: 1.700 preservadas y 28 `no_decidida_por_testigos` (12 inconclusas
    COL y 16 robustas MEX);
  - regla ±ε de ambos testigos: sup g_lo > −1/100 e inf g_hi < 1/100 en las
    preservadas con dos lados. Incluye las 8 COV micro con ambos signos
    negativos;
  - Q por versión: 3.456 posiciones (3.449 de filas padre + 7 de P7), 1.712
    preservadas y 16 robusteces refutadas por el testigo sup;
  - P7 aplicado una vez a 7 afirmaciones de 4 unidades;
  - 1.705 descomposiciones históricas; las 7 sin descomposición son las de
    P7;
  - m = 1/2 separado del diagnóstico general (dominio 0 < m ≤ 1), con las
    dos m* exactas iguales a las del libro rem156:
    - contrato: −29631728656581536186343/28491468583357561333350400;
    - conservadora: −1058276023447533041831/1017552449405627190476800;
  - resumen y manifiesto ligados a las salidas.
- **Comparación frente a rem160, por clave y escenario**: 1.728 filas, 0
  diferencias científicas. Las diferencias son de procedencia, todas ligadas
  a su archivo:
  - `fuente.ruta` de ENF, COV, P7 y Q;
  - la huella de ENF (ed2e098b…);
  - las huellas de Q, porque la fuente es el `.jsonl` de q-local y no el
    `resultado.json` histórico.

  El resumen difiere en `filas_sha256` y `utc`. El manifiesto difiere en
  rutas, huellas, tamaños, `utc` y la huella de código del constructor
  (c32b83d8… de la proyección frente a e96814df… del original). Los 11
  recuentos del libro rem161 coinciden.

### F10-INTEGRACION

**Aritmética** (exacta, desde la lectura B1 → B2 validada):

U_C2 = 0x1.628ed46d42e18p-3 = 779681131038147/4503599627370496.

| Grupo | L_K1 | G_hi = U_C2 − L_K1 | margen −1/100 − G_hi | Veredicto |
|---|---|---|---|---|
| K1 | 0x1.b98c85d42628dp-3 | −1530361648395381/36028797018963968 (−0,04248) | 0,03248 | robust_infeasible |
| K2 | 0x1.b8c3b85c299c6p-3 | −758281298982359/18014398509481984 (−0,04209) | 0,03209 | robust_infeasible |
| K3 | 0x1.b5da2b3dba041p-3 | −1465328706482729/36028797018963968 (−0,04067) | 0,03067 | robust_infeasible |
| K4 | 0x1.b5130c24fe36ap-3 | −725822591589033/18014398509481984 (−0,04029) | 0,03029 | robust_infeasible |
| K5 | = K1 | = K1 | 0,03248 | robust_infeasible |
| K6 | = K2 | = K2 | 0,03209 | robust_infeasible |

Cada grupo tiene dos afirmaciones COL (G y N, con y sin addback) y se aplica
la regla inclusiva G_hi ≤ −1/100.

**Etapa**: U47, código 0, con todos sus cotejos cumplidos.

**Validación sin referencia**: 12/12 comprobaciones.

- Las líneas que cambian son exactamente 12. Son las 12 COV
  `no_decidida_por_testigos` inconclusas de la síntesis nueva, las mismas de
  la evidencia B2, todas COL.
- Las otras 1.716 líneas son idénticas byte a byte a la síntesis nueva, con
  la misma serialización.
- En las doce solo cambian `COV.conclusion`, `COV.resolucion_global`,
  `se_sabe` y `no_se_concluye`. Se conservan la categoría padre
  (`inconclusa_por_testigos_en_tolerancia`) y la lectura COV histórica
  (`no_decidida_por_testigos`). La aritmética de cada fila es la del grupo.
- Vista final:
  - COV: 1.700 preservadas, 12 `robust_infeasible` bajo φ/2 y 16 mexicanas
    sin clasificación transformada (robustas padre);
  - 20 cambios de signo, contados aparte (8 en preservadas y 12 en las
    nuevas robustas);
  - ENF, Q, P7, categoría y padre sin cambios en las 1.728 filas.
- COV12: 12 líneas ligadas a su línea de la síntesis, a su fila canónica y
  a las filas finales.

**Comparación frente a rem171**: 0 diferencias científicas en filas (1.728),
COV12 (12; frente a ac182268…), resumen y manifiesto.

- Las doce claves cambiadas son las mismas que cambian entre rem160 y
  rem171.
- Diferencias de procedencia, todas ligadas:
  - en las filas, las rutas y huellas de fuente;
  - en las doce, las 12 huellas de `resolucion_global.procedencia`, que
    apuntan a las piezas locales;
  - en el manifiesto, la autoridad de actualización (rutas y huellas
    locales), la fuente histórica y las huellas de código (U47 cc9f79d2…
    frente a 95493c61…; constructor de la síntesis c32b83d8… frente a
    e96814df…).
- Los 15 recuentos del libro rem171 coinciden.

Las doce afirmaciones:

| Grupo | Afirmaciones (COL, ci, f, conditional_full, macro, guardrail_deuda) |
|---|---|
| K1 / K2 | PREG-COL-E2-2023:primary — G y N; addback_completo (K1) y sin_addback (K2) |
| K3 / K4 | PREG-COMPARACION-E1:historical_anchor — G y N; addback_completo (K3) y sin_addback (K4) |
| K5 / K6 | PREG-COMPARACION-E1:primary — G y N; addback_completo (K5) y sin_addback (K6) |

## Reglas de comparación (COMPARACION-FAM10-v1)

- Las referencias solo se abren después de producir y validar. Las etapas y
  las validaciones registran 0 lecturas fuera del paquete y ninguna
  referencia leída.
- **Igualdad exacta por clave**:
  - filas por `afirmacion`;
  - escenario por bloque: ABL-ENF η_f/2, ABL-COV φ/2, Q m=1/2 por versión y
    `dimensiones.escenario`;
  - comparación hoja a hoja.
- Toda diferencia se clasifica:
  - ruta: el archivo existe y su `sha256` hermano coincide;
  - huella: la huella de un archivo, línea o fila canónica de esta ejecución
    o de sus entradas;
  - huella de código: proyección frente a su original, con el valor real
    declarado;
  - hora;
  - tiempo: `garantia_clave.segundos`, igual al del integral nuevo;
  - tamaño;
  - científica: cualquier otra diferencia, que impide la aceptación.
- Los recuentos se derivan de las filas y se contrastan con los libros:
  - rem148: 10;
  - rem161: 11;
  - rem171: 15.

## Controles (`local/pruebas_fam10.py`, `salidas/fam10/pruebas_03.json`: 28/28 con el código final)

Fuera de FAM10 no se recalcula nada. Las negativas se niegan antes de
escribir o actúan sobre copias reselladas de forma coherente de
`salidas/fam10/tabla_01`.

- **Cruce de clave**:
  - ENF con las claves de dos filas permutadas (COL/PER): la auditoría
    rem148 la rechaza (`pid` distinto del de T7) y la comparación señala 40
    diferencias científicas;
  - síntesis con dos claves permutadas: la validación la rechaza (enlace
    ENF, COV y Q por clave y lado: 4 + 4 + 4 + 4) y la comparación señala
    80.
- **Cruce de escenario**:
  - vista final con los bloques ENF, COV y Q de dos filas gemelas
    conditional_full y conditional_none intercambiados, con recuentos
    iguales: la validación la rechaza (no se conservan las 1.716 filas; ENF
    y Q cambian) y la comparación señala 88;
  - Q local con contrato y conservadora cruzadas en la entrada: la etapa no
    produce síntesis (`Q_LOCAL_SIN_CABECERA_contrato`).
- **P7 dos veces**:
  - suplemento con una fila duplicada: se niega antes de escribir
    (`P7_NO_ES_UN_SUPLEMENTO_CONCORDANTE`);
  - U44 en proceso con la línea duplicada y la guarda de entrada
    desactivada: el propio constructor se detiene
    (`DUPLICADO_EN_FUENTE`, `SUPLEMENTO_P7`);
  - síntesis con `aplicaciones = 2`: la validación la rechaza y la
    comparación señala `P7/aplicaciones`.
- **B2 sin validación o con la cota alterada**:
  - con la validación de B1, o con un registro no aceptado: se niega
    (`REGISTRO_B2_NO_ACEPTADO_O_AJENO`);
  - con L_K1(K1) + 1 ulp en la lectura después de validar: se niega
    (`B2_LECTURA_CAMBIADA_DESPUES_DE_VALIDAR`);
  - con el mismo cambio y un registro **forjado** con las huellas nuevas,
    sin pasar `fam11-validar`: U47 y la validación local lo aceptan, porque
    recalculan G_hi desde la lectura que reciben. La comparación exacta con
    rem171 lo rechaza: G_hi, L_K1 y el margen de K1 en las filas, la COV12 y
    el libro local (16 diferencias). Es el mismo patrón que el C2 + 1 ulp de
    FAM09.
- **Entradas**: la tabla sin las entradas B1/B2, o con P7 fuera de la base,
  se niega sin carpeta.
- **Otra carpeta**: copia mínima del paquete fuera de la base, con el mismo
  intérprete.
  - `fam10-comprobar` cumple.
  - `fam10-tabla`, con P7 y Q en `insumos/` y la salida en `otra/`, valida
    las tres etapas y acepta las tres comparaciones.
  - Su tabla final, frente a la del paquete por clave, tiene las mismas
    1.728 claves. Solo difieren rutas de fuente (1.728 ENF, 1.728 × 2 Q,
    7 × 3 P7) y tres huellas de procedencia en las doce, todas de vínculo.
- **Dependencias** (en la copia): U44 alterado, el resumen P7 retirado, el
  bloque de auditoría retirado o el esquema rem170 alterado.
  - `fam10-comprobar` no cumple y nombra la pieza.
  - `fam10-tabla` y `fam10-validar` se niegan sin salida
    (`DEPENDENCIA_AUSENTE_O_ALTERADA`).

## Comprobación, regresión y saneado

- `salidas/fam10/comprobar_02.json` (final): cumple. Son 45 piezas sin
  alteraciones, 4 sustituciones que compilan, código ligado a su original,
  7 resúmenes de autoridad y 14 referencias íntegras.
- Regresión (`reproducir.py` es compartido): `revisar` y `fam01-comprobar`
  … `fam09-comprobar` y `fam11-comprobar` terminan con código 0 y cumplen
  (`salidas/fam10/regresion_fam*_comprobar.json`). Después de editar
  `catalogo.json`, que leen FAM03–FAM09 y FAM11, se repitieron esos
  `comprobar` y el de FAM10: todos con código 0
  (`salidas/fam10/tras_catalogo_*_comprobar.json`).
- Saneado, revisado sobre los archivos finales: 0 rutas personales, nombres
  de usuario o correos en:
  - `src/fam10.py`, `local/pruebas_fam10.py`, `reproducir.py` y
    `extraccion/extraer_fam10.py`;
  - `fuentes_fam10.json`, `datos/fam10`, `referencias/fam10` y
    `nucleo_s6/exp8`;
  - todo `salidas/fam10`;
  - los cuatro documentos y este resultado.

  Las rutas registradas son relativas a la base. Las copias de otra carpeta
  quedaron fuera del paquete.

## Tiempos medidos (pared, s; `tabla_03`)

| Etapa | Etapa | Validación | Comparación |
|---|---:|---:|---:|
| ENF | 0,22 | 0,30 | 1,10 |
| SINTESIS | 0,40 | 0,44 | 12,9 |
| INTEGRACION | 0,55 | 0,42 | 15,4 |

Orden completa: 31,9 s. Los controles tardaron 142,1 s, incluida la copia de
otra carpeta.

## Correcciones rutinarias de esta sesión

- **Ejecuciones previas**:
  - `tabla_01` usó el código anterior a las correcciones siguientes. Produjo
    los mismos bytes ENF y el mismo contenido científico, y es la base
    copiada por los controles.
  - `tabla_02` es anterior a la comprobación por país.
  - `tabla_03` es la ejecución final.
  - Las tres difieren entre sí solo en las rutas de su carpeta y en las
    huellas que las nombran (comprobado por clave).
- **Comparación**: la huella de cada archivo citado se memoriza dentro de una
  comparación. Bajó de unos 44 s a 13–15 s.
- **`fam10-tabla`**: comprueba las dependencias y las diez entradas antes de
  crear la carpeta. Antes, una entrada mala dejaba una carpeta parcial.
- **`fam10-comprobar`**: informa un código ausente en lugar de terminar con
  una excepción.
- **La comparación ENF**: repite la auditoría cuando la validación no la
  trae, por ejemplo en una validación rechazada.
- **El registro ENF**: anota la procedencia de cada tarea de FAM08.
- **La validación ENF**: añade la comprobación por país (línea 175 de la
  auditoría). Después se repitieron la orden única (`tabla_03`),
  `fam10-comprobar` (`comprobar_02`) y los controles (`pruebas_03`).
- **Los controles**: `pruebas_01` se detuvo en el script de controles con
  9/9 casos conformes hasta ese punto. La lectura B2 no trae `U_C2_hex` en
  `datos_validados`; se corrigió.
  - `pruebas_02` corrió completa (28/28), con el código anterior a la
    comprobación por país.
  - `pruebas_03` (28/28) es la ejecución con el código final.

## Límites y diferencias pendientes

- **U42** no está localizado. Límite adoptado por el autor el 2026-11-18,
  `L-ENF-AFIRMACION-AUDITORIA-REM148`: la validación del ENF regenerado es el
  bloque científico (líneas 49–116) de la auditoría del revisor rem148. No se
  ejecutan las partes que verifican la ronda histórica, y la identidad de U42
  no queda acreditada.
- **U45 y U48 no se ejecutan.** Verifican rondas históricas completas
  (inventarios, libros, textos y negativos de rem160/rem170) que no
  corresponden a bytes nuevos. En su lugar:
  - la validación local recalcula enlaces, recuentos, la regla ε, P7, m* y
    la aritmética B2 desde las filas y las entradas;
  - la comparación exacta contrasta con rem160 y rem171.
- **Huella ENF distinta de e0670acc…**: se debe solo a la duración de la T2
  nueva (8 campos `segundos`). El contenido científico es igual.
- **La huella de las filas finales depende de la carpeta de salida**: U44 y
  U47 registran `fuente.ruta`. El contenido científico es el mismo en
  cualquier carpeta (copia de otra carpeta y tres ejecuciones).
- **Piezas locales de papel** (ENLACE-INTEGRACION-v1):
  - los libros B1/B2, la auditoría y el enlace de las doce derivan de la
    lectura validada y no son actos de Codex;
  - los nombres de actos que quedan en `procedencia` son etiquetas de
    papel;
  - frente a una lectura B2 reescrita con un registro forjado, la garantía
    es la comparación exacta, no la validación local.
- **Q local**: `q-local` no fija en su resumen la huella de los `.jsonl`. La
  entrada se acepta por carpeta, con el resumen concordante y la versión en
  cada fila.
- **Procedencia mixta**: ENF descansa en un integral con una T2 nueva y el
  resto guardado; COV, en una T1 nueva y T2–T6 guardadas. B1/B2, P7 y Q son
  salidas nuevas o concordantes. No es una reproducción completa sobre
  entradas nuevas.
- **Aislamiento (2.4.2)**: pendiente. La copia de otra carpeta usa el mismo
  intérprete.

## Propuesta de cierre

Se propone cerrar la preparación de FAM10 en su alcance. Las tres
operaciones RD están conectadas en una orden única de `reproducir.py`, que va
desde las entradas de Exp8 hasta la tabla final de 1.728 afirmaciones, su
resumen y la resolución de las doce COV, con validación por etapa y
comparación exacta con rem147/rem148, rem160/rem161 y rem170/rem171. Hay 0
diferencias científicas y 28/28 controles. La limitación de U42 queda a
decisión y no se adopta aquí.

## Lo que falta

- ~~La decisión sobre L-ENF-AFIRMACION-VALIDADOR-REM191 (U42).~~ Tomada el
  2026-11-18 (ver «Decisión del autor sobre U42»).
- La ejecución sobre entradas totalmente nuevas: integral ENF con T1–T6 y
  mallas nuevas, y COV T1–T6 nuevas (Paso 3).
- El aislamiento de 2.4.2.
- FAM13, FAM14, el manuscrito, la publicación y los commits, cada uno en su
  encargo.

## Dictamen de Codex

El 18 de noviembre de 2026 cierro la preparación de las tres operaciones de FAM10 en su alcance documental y aritmético. Ejecuté `fam10-tabla` en una carpeta nueva (`salidas/fam10/dictamen_20261118_102955`). Terminó con código 0 en 30,3 s y aceptó las tres etapas. Contrasté las 1.728 filas de cada etapa directamente con los archivos originales cuyas huellas constan en los libros rem148, rem161 y rem171.

En ENF hay 1.720 líneas idénticas al original. Las ocho restantes difieren únicamente en la duración de T2. Comprobé también que el bloque de auditoría usado corresponde a las líneas 49–116 del original rem148. Las seis comprobaciones pasaron sobre el producto nuevo, con 3.449 posiciones enlazadas y 1.724 celdas.

La síntesis y la integración coinciden en todo el contenido científico con sus originales. Comprobé las rutas y huellas de ENF, COV, P7 y ambas versiones de Q por fila. Para las doce COV verifiqué las huellas de la procedencia local contra los archivos correspondientes y recalculé con fracciones las seis cotas desde las lecturas B1 y B2. Las doce claves coinciden con la resolución aceptada. Las otras 1.716 líneas se conservaron byte a byte entre las dos etapas de mi ejecución. El recuento final de COV es de 1.700 preservadas, 12 colombianas `robust_infeasible` bajo φ/2 y 16 mexicanas con clasificación transformada pendiente. Los 20 cambios de signo se cuentan aparte.

U42 sigue sin localizarse y su limitación propuesta queda pendiente de decisión. La preparación se acredita con entradas de procedencia mixta y con las tres comparaciones finales. Quedan por hacer la instalación aislada de 2.4.2 y la ejecución general del Paso 3.

## Decisión del autor sobre U42 (2026-11-18, 2.1.2)

Texto adoptado por el autor:

> Para U42, adopto como decisión específica de la reproducción limpia
> mantener F10-ENF-AFIRMACION como RD y aceptar el bloque científico de
> rem148 como validación del ENF regenerado, con los límites documentados.
> U42 sigue sin localizarse.

**Búsqueda dirigida previa.** No hay ninguna pista nueva que ligue un
candidato, su versión y el producto validado:

- las invocaciones registradas de rem147 (A1–A5, B1, B2) no ejecutan ningún
  validador del ENF;
- la aceptación de e0670acc… cita la salida de la auditoría
  (`review_20261105_rem148_audit.json`, 6aa49afd…), no un validador de la
  entrega;
- el guion de la auditoría (d226ad70…) no aparece citado por huella. Se
  liga a esa salida por contenido: sus 99 comprobaciones corresponden una a
  una a las del guion.

**Lo aplicado:**

- `catalogo.json`:
  - la fila sigue RD;
  - disponibilidad `COPIADA_CON_LIMITE_ADOPTADO`, sin residuos;
  - límite `L-ENF-AFIRMACION-AUDITORIA-REM148`, con el texto del autor.
- `src/fam10.py`: solo los textos del validador. La lógica, los productos y
  las comparaciones no cambian.

**Comprobado:**

- `fam10-tabla` sobre las entradas guardadas de la orden única
  (`salidas/fam10/tabla_04`, 14,3 s):
  - código 0 y las tres comparaciones aceptadas;
  - ENF con los mismos bytes que `tabla_03` (ed2e098b…);
  - la validación declara el límite adoptado.
- `local/pruebas_fam10.py` con el código nuevo (`salidas/fam10/pruebas_04.json`)
  da 28/28, entre ellos:
  - un ENF con las claves de dos filas permutadas: la auditoría lo rechaza y
    la comparación encuentra 40 diferencias científicas;
  - el bloque de auditoría retirado: `fam10-tabla` y `fam10-validar ENF` se
    niegan sin salida.
- El balance general (`salidas/u42_u60/`):
  - con todas las llamadas aceptadas, la fila queda «completa» y el pie de
    BALANCE.md muestra el límite;
  - con `fam10-tabla` no conforme u omitida, la fila queda «no conforme» y
    «pendiente».

La fila queda resuelta en el catálogo. La reproducción completa sobre
entradas nuevas sigue pendiente del Paso 3.
