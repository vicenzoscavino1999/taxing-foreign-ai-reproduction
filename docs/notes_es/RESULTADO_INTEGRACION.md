# RESULTADO INTEGRACIÓN — Comando general de las 14 familias (2.2.3 y 2.2.2)

Fecha: 2026-11-18 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). Este encargo solo ejecuta el plan sin cálculo y el piloto
acotado. El modo completo queda implementado para el Paso 3 y no se ejecutó.

## Estado

| Parte | Estado |
|---|---|
| Comando general | `reproducir.py general --modo plan\|piloto\|completo --salida <carpeta nueva>`. `--modo` no tiene valor por omisión: el completo se elige expresamente. Código en `src/general.py`. |
| Plan (`salidas/general/plan_05`) | Cumple en 6,8 s. Resuelve las 39 claves del catálogo (17 RN, 13 RD, 9 VI; desde las decisiones de 2.1.2 del 2026-11-18, 17 RN, 12 RD y 10 VI en `plan_06`). Las conecta a 3.955 llamadas reales que la CLI acepta (0 rechazadas) y a 346 productos. Ninguna clave queda sin llamada ni sin comparación o verificación. El orden por datos es conforme. |
| Piloto (`salidas/general/piloto_05`) | Conforme. 16/16 llamadas aceptadas en 51,3 s: FAM08 + FAM11 + FAM12 → FAM10. Resultado Exp8: 1.728 afirmaciones, 12 COL pasan a `robust_infeasible`, 1.716 idénticas a la síntesis de entrada y COV 1.700/12/16. |
| Sin árbol original ni `salidas/` previas (`salidas/general/traslado_03`) | Se copió el paquete sin `salidas/`, `local/`, `.venv*`, `.git` ni `extraccion` (6.322 archivos). Desde esa copia, plan y piloto son conformes y se registran 0 lecturas fuera del paquete. |
| Controles (`salidas/general/pruebas_general_05.json`) | 7/7. Salida alterada, validación retirada, discrepancia en una comparación, límite agotado, entrada preexistente, marcadores sin resolver e interfaz. |
| Lectura de comparaciones guardadas (`salidas/general/lecturas_guardadas_01.json`) | Conforme. El balance lee el resultado de 95 informes de comparación de las 10 familias con `-comparar`, aceptados y no aceptados, y de 7 informes de órdenes únicas e integridad. |
| Regresión de la CLI (`salidas/general/regresion_01`) | 17/17 con código 0: `revisar`, `fam01-listas`, los 13 `famXX-comprobar`, `fam09-listar` y `p7`. |
| Fuera de este encargo | Lotes completos del Paso 3, instalación aislada (2.4.2), decisiones científicas, manuscrito, publicación y commits. |

## Órdenes

Desde la base, con el intérprete de `.venv-fam01`, las opciones `-B -P -s -X utf8`
y `PYTHONHASHSEED=0` (el comando lo exige y lo transmite a cada llamada junto
con `TZ=UTC` y las seis variables de hilos = 1). `py` abrevia
`<python de .venv-fam01> -B -P -s -X utf8 reproducir.py`.

```
py general --modo plan      --salida salidas/general/<carpeta nueva>
py general --modo piloto    --salida salidas/general/<carpeta nueva>
py general --modo completo  --salida salidas/general/<carpeta nueva>   # Paso 3; no ejecutado
```

Las ejecuciones de este encargo:

```
py general --modo plan   --salida salidas/general/plan_05
py general --modo piloto --salida salidas/general/piloto_05
```

- La salida debe ser una carpeta nueva dentro de la base. Si existe, la orden
  se niega con código 2.
- Código 0 si el resultado es conforme y 1 si no lo es o si el plan no se
  pudo construir.
- Dónde leer el resultado, dentro de la carpeta:
  - `BALANCE.md`: el balance legible, una fila por clave, más el resultado
    Exp8 y los criterios y límites documentados;
  - `balance.json`: el mismo balance completo;
  - `plan.json`: las llamadas de los dos modos, con dependencias, límites,
    sustituciones e insumos históricos;
  - `ejecucion.jsonl`: una línea por llamada lanzada o bloqueada;
  - `registro/`: stdout y stderr de cada llamada;
  - `recetas/`: las recetas de las 13 familias, tal como se emitieron.

## Cómo se construye el plan

1. **Recetas existentes.** El comando lanza las 13 recetas (`famXX-receta`,
   sin cálculo; FAM12 no tiene). Las escribe en `recetas/` y convierte sus
   órdenes en llamadas de `reproducir.py`. Los marcadores `salidas/famXX/<ejecucion>`
   y `<nuevo>` se reubican dentro de la carpeta de la ejecución. Si queda un
   marcador sin resolver, el plan se niega (C06).
2. **Catálogo.** Cuatro llamadas salen de `comando_base_limpia` del catálogo
   porque ninguna receta las emite: `fam01-listas` (F01-R3-MARCO),
   `fam02-comprobar`, `p7-suplemento` y `q-local`.
3. **Sin cálculo repetido.**
   - FAM06 lista las tres llamadas L1-ELAST de FAM05. Se lanzan una sola
     vez y el plan las anota en `llamadas_reutilizadas_entre_recetas`.
   - F12-P7-K1 la cubre `p7-suplemento`, que recalcula los cuatro K1 con
     `derivar_k1` y los compara en binary64 exacto antes de generar las siete
     filas. Por eso `p7-k1` no se lanza aparte. El balance solo da la clave
     por cumplida si esa lectura trae `k1_comparacion_exacta` verdadero con
     valores comparados.
4. **Mismas llamadas.** Cada argv del plan se analiza con el mismo parser de la
   CLI (`crear_parser`) y es el que se ejecuta. Ninguna de las 3.955 se
   rechaza.
5. **Orden por datos.**
   - Cada ruta que una llamada consume se liga a la llamada que la produce
     dentro de la ejecución. Esas rutas son las de `--entrada`, `--nueva`,
     `--validacion`, `--b1`, `--validacion-b1`, `--e4`, `--lote2`,
     `--validacion-e4` y `--validacion-lote2`.
   - Se añaden tres dependencias estructurales:
     - el paso previo de cada familia (`comprobar`, `listar` o `listas`);
     - la parada secuencial que declaran las recetas de FAM04 a FAM07, en
       35 llamadas;
     - el `depende_de` de las tareas de FAM02.
   - El orden es topológico. Una entrada sin productor en la ejecución, una
     salida repetida o fuera de la carpeta y una llamada sin salida son
     errores del plan.
   - Una ruta preexistente de `salidas/` como entrada también es un error
     (C05).
6. **Entradas de FAM10.** `fam10-tabla` recibe las diez entradas de
   RESULTADO_FAM10.md con los mismos nombres, ligadas a los productos de esta
   ejecución:
   - `enf_integral` y `registro_enf_integral`;
   - `cov` y `registro_cov`;
   - `p7` y `q_local`;
   - `b1`, `validacion_b1`, `b2` y `validacion_b2`.
7. **Insumos históricos.** Cada familia declara los suyos (`insumos_historicos`
   en `plan.json`) y cada llamada los que consume (`historicas`, con su
   procedencia).
   - F0, la fase previa del presupuesto histórico, figura como prerrequisito
     externo en 26 llamadas de FAM02. La receta de FAM02 la da por hecha.
8. **Límites y supervisión.**
   - Cada llamada corre en su propio proceso, con el mismo intérprete y las
     mismas opciones, y desde la base.
   - El límite externo es el de su receta:
     - 2.400 s de tope de trabajo o por tarea;
     - 600 s para B1/B2 y para el TESTIGO de FAM09;
     - 600 s por unidad en FAM01;
     - 2.400 s por tarea en FAM02.
   - Las llamadas sin cálculo tienen 600 s.
   - Al agotarse el límite se termina el árbol de procesos (C04).

Llamadas del modo completo por familia: FAM01 3.530, FAM02 35, FAM03 273,
FAM04 10, FAM05 7, FAM06 6, FAM07 12, FAM08 27, FAM09 20, FAM10 2, FAM11 27,
FAM12 2, FAM13 2, FAM14 2.

## Paso entre etapas y bloqueo

Al aceptar una llamada, el comando guarda la huella de cada archivo de su
producto. Antes de lanzar un consumidor comprueba que sus productores fueron
aceptados y que cada entrada sigue presente e igual.

- Una entrada que falta deja la llamada `bloqueado` con el motivo
  `ENTRADA_AUSENTE`.
- Una entrada que cambió desde que se produjo la deja `bloqueado` con
  `ENTRADA_ALTERADA_FUERA_DEL_PLAN`.
- Si el productor falló, se rechazó o agotó su límite, el motivo es
  `depende de Pxxxxx (<estado>)`.
- Todo lo que depende de una llamada bloqueada queda pendiente.
- Una llamada aceptada puede escribir dentro de sus propias entradas. Así lo
  hace `fam11-validar`, que crea `VALIDACION/` dentro de B1 y B2. Esas
  escrituras se incorporan a la huella y se registran en
  `escribio_en_sus_entradas`.

## Piloto FAM08 + FAM11 + FAM12 → FAM10 (`salidas/general/piloto_05`)

Usa las mismas llamadas del plan completo con la regla
ENTRADA-GUARDADA-PILOTO-v1.

- `fam08-integrar` y `fam11-ensamblar` reciben `<tarea>=guardado` donde sus
  recetas lo admiten. Son 13 sustituciones: ABL-ENF-T1…T6, las mallas ENF y
  ABL-COV-T1…T6.
- Cada sustitución consta en `plan.json` con la llamada del completo que
  sustituye y su procedencia histórica.
- El certificado reemitido no se pasa: con la T1 guardada vale su certificado
  guardado, como en `regeneracion_02` de FAM08.
- No se repite la T2 larga de ENF.
- Nada depende de `mixta_03`, `piloto_01` ni `tabla_03`. La copia sin
  `salidas/` lo demuestra.

| Llamada | Orden | Estado | s |
|---|---|---|---|
| P03874 | `fam08-comprobar` | aceptado | 0,9 |
| P03899 | `fam08-integrar` (T1–T6 y mallas guardadas) | aceptado | 1,1 |
| P03900 | `fam08-comparar --tarea INTEGRAL` | aceptado | 0,7 |
| P03901 | `fam11-comprobar` | aceptado | 1,1 |
| P03920 | `fam11-ensamblar` (T1–T6 guardadas) | aceptado | 1,1 |
| P03921 | `fam11-comparar --tarea ENSAMBLADO` | aceptado | 0,7 |
| P03922–P03924 | B1: `fam11-unidad`, `fam11-validar`, `fam11-comparar` | aceptado | 2,7 |
| P03925–P03927 | B2 sobre el B1 validado de esta ejecución: unidad, validar, comparar | aceptado | 2,3 |
| P03928 | `p7-suplemento` | aceptado | 0,4 |
| P03929 | `q-local` | aceptado | 0,6 |
| P03950 | `fam10-comprobar` | aceptado | 0,5 |
| P03951 | `fam10-tabla` con las diez entradas de esta ejecución | aceptado | 31,9 |

Resultado Exp8, comprobado sobre la tabla nueva:

- 1.728 afirmaciones.
- Cambian exactamente 12 filas, todas COL. Las doce pasan de
  `no_decidida_por_testigos` a `robust_infeasible`. Los únicos campos que
  cambian son COV, `no_se_concluye` y `se_sabe`.
- Las otras 1.716 filas son idénticas a la síntesis de entrada.
- El reparto COV final es `inconclusa_preservada` 1.700,
  `robust_infeasible` 12 y `no_decidida_por_testigos` 16.
- `fam10-tabla` compara además con rem147, rem160 y rem171
  (COMPARACION-FAM10-v1): cumple.
- La huella de las filas varía entre ejecuciones porque cada fila lleva la
  ruta de su salida.

## Balance por operación

Cada una de las 39 claves tiene una fila en `BALANCE.md` y su detalle en
`balance.json`:

- qué se hizo en esta ejecución: calculada, regenerada, verificada por
  integridad, sin ejecutar, bloqueada o no conforme;
- de dónde vienen las entradas: de otra llamada de esta ejecución o guardadas
  del paquete;
- los insumos históricos de la familia y las sustituciones del piloto;
- la comparación aplicada: la llamada, su regla y lo que dice su informe
  (`reproduccion`, `motivos` o `cumple`);
- el estado de la reproducción completa.

La última columna separa el éxito del piloto del estado de la reproducción
completa. Una clave solo está «completa en esta ejecución» si todas sus
llamadas del plan completo y sus antecesoras corrieron aquí con la misma orden
y fueron aceptadas. Si no, la columna dice cuántas faltan y nombra una.

En `piloto_05`:

- **Completas:** F11-B1, F11-B2, F12-P7-K1, F12-P7-G y F12-QLOCAL.
- **Regeneradas sobre entradas guardadas, pendientes del Paso 3:**
  F08-INTEGRAL, F11-COV26 (su cálculo no se ejecutó) y F10-ENF-AFIRMACION,
  F10-SINTESIS y F10-INTEGRACION (faltan 16 de 28 llamadas).
- **Sin ejecutar, fuera del modo piloto:** las otras 29.

Al pie, `BALANCE.md` copia del catálogo los criterios adoptados y los límites
documentados. No los adopta ni los levanta. Allí figuran U42 no localizado
(F10-ENF-AFIRMACION) y U60 no localizado (F13-HISTORICAS), además de los
límites L-2276, L-QUIEBRES, L-T8 y L-T8-TESTIGO-VALIDADOR. La regla de cada
clave aparece en la columna de comparación, por ejemplo
F2-ENTORNO-PORTABLE-v1, adoptada solo para FAM01.

| Clave | Tipo | Llamadas (completo) | Comparación o verificación ligada | piloto_05 |
|---|---|---|---|---|
| F01-R2 | RN | 3.480 | `fam01-comparar` por unidad (histórica, limpia y limpia con F2) | sin ejecutar |
| F01-R3 | RN | 49 | `fam01-comparar` por unidad; `fam01-na` para las 5 NA | sin ejecutar |
| F01-R3-MARCO | VI | 1 | `fam01-listas` | sin ejecutar |
| F02-R1 | RN | 34 | `fam02-comparar` por tarea (IGUALDAD-R1F-TIEMPOS-v1 en R1-F) | sin ejecutar |
| F03-QUIEBRES | RN | 240 | `fam03-comparar` (COMPARACION-FAM03-v1) | sin ejecutar |
| F03-Q | RN | 32 | `fam03-comparar` (COMPARACION-FAM03-v1) | sin ejecutar |
| F04-LOTE1 | RN | 9 | `fam04-comparar` (COMPARACION-FAM04-v1) | sin ejecutar |
| F05-ELAST-C0 | RN | 3 | `fam05-comparar` (COMPARACION-FAM05-v1 + VINCULO-PROCEDENCIA-v1) | sin ejecutar |
| F05-ELAST-HIST | VI | 3 | `fam05-comparar L1-ELAST` (la misma llamada que F05-ELAST-C0) | sin ejecutar |
| F05-LAMBDA | RN | 3 | `fam05-comparar L1-LAMBDA` | sin ejecutar |
| F06-MALLAS | RN | 3 | `fam06-comparar L1-ELAST` (MALLAS-v1) | sin ejecutar |
| F06-CONCILIACION | RD | 2 | `fam06-comparar CONCILIACION` (CONCILIACION-v1) | sin ejecutar |
| F07-RECALCULO | RN | 11 | `fam07-comparar` (COMPARACION-FAM07-v1) | sin ejecutar |
| F07-REUTILIZADAS | VI | 3 | `fam07-comprobar` y `fam07-comparar ENSAMBLADO` | sin ejecutar |
| F07-PREVIAS-192 | VI | 1 | `fam07-comprobar` | sin ejecutar |
| F08-MALLAS | RN | 3 | `fam08-comparar L1-ELAST` (COMPARACION-FAM08-v1) | sin ejecutar |
| F08-PARES | RD | 2 | `fam08-comparar PARES` | sin ejecutar |
| F08-TECHOS | RN | 19 | `fam08-comparar ABL-ENF-T1…T6` y `RECUPERACION` | sin ejecutar |
| F08-INTEGRAL | RD | 2 | `fam08-comparar INTEGRAL` | regenerada y comparada (entradas guardadas) |
| F09-HIST | VI | 3 | `fam09-etapa HIST` y `fam09-comparar HIST` | sin ejecutar |
| F09-LAMBDA | RD | 3 | `fam09-comparar LAMBDA` | sin ejecutar |
| F09-CAPTURA | RD | 3 | `fam09-comparar CAPTURA` | sin ejecutar |
| F09-TESTIGO | RN | 6 | `fam09-comparar TESTIGO` e `INCORPORACION` | sin ejecutar |
| F09-C5B | RD | 3 | `fam09-comparar C5B` | sin ejecutar |
| F10-ENF-AFIRMACION | RD | 1 | `fam10-tabla` (COMPARACION-FAM10-v1, etapa ENF) | regenerada y comparada (aguas arriba, guardadas) |
| F10-SINTESIS | RD | 1 | `fam10-tabla` (etapa SINTESIS) | regenerada y comparada (aguas arriba, guardadas) |
| F10-INTEGRACION | RD | 1 | `fam10-tabla` (etapa INTEGRACION) | regenerada y comparada (aguas arriba, guardadas) |
| F11-COV26 | RN | 20 | `fam11-comparar ABL-COV-T1…T6` y `ENSAMBLADO` (COMPARACION-FAM11-v1) | regenerada sobre guardadas; cálculo no ejecutado |
| F11-B1 | RN | 3 | `fam11-comparar B1` | calculada, validada y comparada; completa |
| F11-B2 | RN | 3 | `fam11-comparar B2` | calculada, validada y comparada; completa |
| F12-P7-K1 | RN | 1 | `p7-suplemento` (K1 en binary64 exacto) | calculada y comparada; completa |
| F12-P7-G | RD | 1 | `p7-suplemento` (filas y bytes) | regenerada y comparada; completa |
| F12-QLOCAL | RD | 1 | `q-local` (filas y bytes) | regenerada y comparada; completa |
| F13-HISTORICAS | RD | 1 | `fam13-reproducir` (COMPARACION-FAM13-v1) | sin ejecutar |
| F13-S1 | VI | 1 | `fam13-reproducir` (integridad S1) | sin ejecutar |
| F14-GN | VI | 1 | `fam14-reproducir` (integridad) | sin ejecutar |
| F14-GN-REGEN | RD | 1 | `fam14-reproducir` (COMPARACION-FAM14-v1) | sin ejecutar |
| F14-187 | VI | 1 | `fam14-reproducir` (integridad) | sin ejecutar |
| F14-176 | VI | 1 | `fam14-reproducir` (integridad) | sin ejecutar |

Las llamadas por clave cuentan las propias. Una llamada compartida, como la
previa de una familia, puede contar en varias claves.

## Paquete sin árbol original ni salidas previas (`salidas/general/traslado_03`)

- **Copia.** Se copió el paquete a una carpeta temporal fuera de la base, sin
  `salidas/`, `local/`, `.venv*`, `.git` ni `extraccion`: 6.322 archivos.
- **Ejecución.** Se lanzó con `-Cwd` y la base en la copia y con el
  intérprete de `.venv-fam01`. Corrieron `general --modo plan` y
  `general --modo piloto`.
- **Resultado.** Ambas son conformes: 16/16 aceptadas y Exp8 6/6. Las
  lecturas fuera del paquete son 0 en los 21 registros de lectura de las
  llamadas, y ninguna salida contiene rutas de la base.
- **Qué se guarda.** `traslado_03/` conserva los balances y
  `ejecucion.jsonl`. No guarda los registros del lanzador, que llevan rutas
  locales. `traslado_02/` es la misma prueba con el código anterior a la
  sección de límites del balance.

## Controles (`local/pruebas_general.py`; `salidas/general/pruebas_general_05.json`: 7/7)

Cada control corre el piloto en una carpeta nueva bajo `pruebas_05/` y altera
algo entre llamadas.

| Control | Alteración | Resultado |
|---|---|---|
| C01 | Se cambia `fam12/p7_suplemento.json` después de aceptarse | `fam10-tabla` queda `bloqueado` con `ENTRADA_ALTERADA_FUERA_DEL_PLAN` (producida por P03928). Las tres F10 quedan pendientes y el resultado es no conforme. |
| C02 | Se retira `fam11/B1.validacion.json` | `fam11-comparar B1` y la unidad B2 quedan `bloqueado` con `ENTRADA_AUSENTE`. F11-B1 y F11-B2 quedan pendientes y el resultado es no conforme. |
| C03 | Se cambia un dígito de `enf_comparacion_integral.jsonl` en el integral recién producido | `fam08-comparar INTEGRAL` se rechaza (código 1). El balance de F08-INTEGRAL dice `no_aceptada`, con tres motivos: `DIFERENCIA_NUMERICA (CR-HASH-CANONICO): enf_comparacion_integral.jsonl ['/C2_enf']`, `BYTES_DISTINTOS` y `HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES`. Las tres F10 quedan pendientes por depender de P03900 (rechazado) y el resultado es no conforme. |
| C04 | Límite de B1 reducido a 0,2 s | B1 queda en `limite_agotado`. No queda vivo ningún proceso Python y el resultado es no conforme. |
| C05 | `p7=salidas/p7_suplemento_08.json` como entrada | El plan la rechaza: entrada sin productor en esta ejecución. |
| C06 | Receta con un marcador sin resolver | El plan se niega a construirse. |
| C07 | Sin `--modo`, `--modo` con otro comando, salida existente y modo desconocido | Código 2 en los cuatro casos. |

Para el resto, los controles de cada familia siguen vigentes. Detectan valores
alterados en 1 ulp, validaciones ausentes, referencias ajenas y cosas
parecidas. El comando general no los relaja: cada comparación es la misma
llamada de la familia.

`local/lecturas_guardadas.py` comprueba que el balance lee también los
informes de las familias que el piloto no ejecuta. Aplica la función del
balance a los informes guardados y obtiene resultado legible en todos:

- **FAM01:** 6 `aceptada_comparacion_limpia_con_F2`, 4 aceptadas bajo F2
  candidata y 7 `no_aceptada`.
- **FAM02:** 4 aceptadas, 10 `no_aceptada` con sus motivos y 2
  `se_compara_en_su_par`.
- **FAM03 a FAM09:** aceptadas, y además 2 `no_aceptada` en FAM08.
- **FAM11:** 5 aceptadas y 1 `no_aceptada`.
- **FAM13 y FAM14:** `fam13-reproducir` y `fam14-reproducir`, este último
  también con `cumple: false` en `reproducir_01`.
- **Integridad:** `fam01-na`, `fam01-listas` y `fam07-comprobar`.

## Regresión y correcciones de esta sesión

Regresión de la CLI tras los cambios en `reproducir.py`:
`salidas/general/regresion_01`, 17 órdenes con código 0.

- `reproducir.py`:
  - el parser pasa a `crear_parser()`, que usa también el comando general;
  - se añade `general`;
  - `--modo` solo se admite con `general`.
- Correcciones rutinarias:
  - `plan_01` falló por un campo `previo` ausente en las llamadas del
    completo.
  - `piloto_01` quedó bloqueado en B1 porque `fam11-validar` escribe
    `VALIDACION/` dentro de B1. Se resolvió incorporando esas escrituras a la
    huella de la llamada aceptada.
  - `pruebas_01` dio 6/7: la consulta de procesos se contaba a sí misma.
  - El balance legible no mostraba U42 ni U60 y ahora tiene la sección de
    criterios y límites.
  - La lectura de un informe con `estado` en texto hacía fallar el balance y
    ahora la lectura es tolerante.
- Las salidas `plan_01`–`plan_04`, `piloto_01`–`piloto_04`,
  `pruebas_01`–`pruebas_04` y `traslado_02` se conservan como antecedentes.
  Las finales son las `_05` y `traslado_03`.

Huellas del código final (sha256, 16 primeros):

- `src/general.py` 20829b1cdd0b7967;
- `reproducir.py` 67b91d77e07e4f76;
- `local/pruebas_general.py` 2a023a8fc3b48a2e.

## Límites concretos

1. **El modo completo no se ejecutó.** Sus 3.955 llamadas, el tiempo total y
   el espacio en disco se conocerán en el Paso 3. Puede haber ajustes
   rutinarios la primera vez.
2. **El piloto usa tareas guardadas para ENF y COV.** F08-MALLAS, F08-TECHOS,
   F08-PARES y el cálculo de F11-COV26 no corren en el piloto. Los productos
   de F10 se regeneran sobre esas entradas, así que su reproducción completa
   depende del Paso 3. El balance lo dice clave por clave.
3. **Intérprete.** `.venv-fam01` tiene su intérprete base en el árbol
   original. El traslado se hizo en la misma máquina con ese intérprete. El
   aislamiento real corresponde a 2.4.2.
4. **Piezas no localizadas.** U42 (validador ENF de FAM10) y U60 (FAM13)
   siguen sin localizarse. El balance los muestra y no los adopta.
5. **F2** está adoptada solo para FAM01. El comando no la extiende.
6. **Lecturas fuera del paquete.** Se suman las que registran las propias
   llamadas: 21 registros en el piloto. Una llamada que no registra lecturas
   no aporta a ese recuento.
7. **Escrituras en entradas propias.** Cuando una llamada aceptada escribe
   dentro de sus entradas, la escritura se incorpora a la huella y queda
   registrada. Una alteración hecha por otra llamada o desde fuera sí bloquea.
8. **F0 de FAM02** es una fase histórica previa. Figura como prerrequisito
   externo y no la ejecuta ninguna llamada del paquete.

## Propuesta de cierre

**2.2.3 (punto de entrada completo).** Propongo cerrarlo en su alcance:

- las 39 operaciones están conectadas a 3.955 llamadas reales de la CLI, con
  sus dependencias y el orden por datos;
- el plan se construye desde una salida vacía, también en una copia sin
  `salidas/`;
- el modo completo queda implementado y solo corre si se elige;
- la cadena FAM08 + FAM11 + FAM12 → FAM10 corre de extremo a extremo con el
  comando general y da el resultado Exp8 esperado.

La ejecución completa pertenece al Paso 3.

**2.2.2 (comparaciones científicas).** Propongo cerrarlo en su alcance:

- cada una de las 39 claves tiene ligada su comparación o verificación, con la
  regla de su familia;
- el balance transmite el éxito (`piloto_05`);
- transmite también la discrepancia (C03), con la clave no conforme, sus
  motivos y los consumidores pendientes;
- transmite el bloqueo por salida alterada o validación retirada (C01 y C02);
- la lectura funciona con los informes de todas las familias
  (`lecturas_guardadas_01`).

Las 39 claves tienen una comparación o verificación asignada. El piloto
aplicó comprobaciones a 10 claves. Cinco completaron su recorrido previsto,
otras cinco utilizaron entradas guardadas y 29 quedaron fuera del piloto.

## Lo que falta

- Corrida completa (`--modo completo`) en el Paso 3.
- Instalación aislada (2.4.2).
- ~~Resolver U42 y U60 en 2.1.2, por localización o por decisión sobre las limitaciones propuestas.~~
  Decididas por el autor el 2026-11-18 (ver «Decisiones de 2.1.2 en el comando general»).

## Dictamen de Codex

**2026-11-18. Se cierran en el alcance de preparación 2.2.2 y 2.2.3.**
Las 39 operaciones de las 14 familias tienen un punto de entrada común y una
comparación o verificación asignada. Comprobé que el plan contiene 3.955
llamadas con identificadores y destinos únicos, ordenadas después de sus
dependencias. Las 136 comparaciones de árboles de FAM03 se ligan por tarea.

Durante la revisión corregí la propagación de las comparaciones. B2 exige
la comparación aceptada de B1 y la tabla Exp8 exige las de B1 y B2. Las
tareas de FAM02 respetan también las dependencias declaradas en su receta.
El balance conserva todas las comparaciones y da prioridad a una discrepancia
aunque haya otras llamadas pendientes. U42 y U60 siguen visibles como decisiones
pendientes aun si sus comandos terminan bien.

El piloto de revisión (`salidas/general/dictamen_piloto_final`) aceptó 16 de
16 llamadas en 35 s. Cotejé las 1.728 claves con rem171. Las doce que cambian
respecto a la síntesis son exactamente las doce COL esperadas. Las otras 1.716
líneas conservan sus bytes. En COV quedan 1.700 preservadas, 12
`robust_infeasible` y 16 sin decidir. ENF y COV usaron las tareas guardadas
que declara el piloto.

Los ocho controles finales fueron conformes. Sus resultados están en
`salidas/general/dictamen_controles_final.json`.
El control añadido comprueba que un informe de B1 que rechaza el resultado
bloquea B2 y la tabla, incluso cuando el proceso termina con código 0. En el
primer pase de revisión dos controles conservaban expectativas anteriores.
Para la validación ausente, B1 informa la ausencia y B2 cita el bloqueo de
su antecesora. Cuando B1 agota su tiempo, la clave B1 figura como no conforme
y B2 queda pendiente. Se conservaron las salidas de ambos pases.

## Decisiones de 2.1.2 en el comando general (2026-11-18)

Las cifras de arriba (17 RN, 13 RD y 9 VI en `plan_05`) describen la versión
anterior a estas decisiones.

**Lo decidido por el autor:**

- `F10-ENF-AFIRMACION` sigue RD, con el límite adoptado
  `L-ENF-AFIRMACION-AUDITORIA-REM148`. La validación del ENF regenerado es
  el bloque científico de la auditoría rem148, y U42 sigue sin localizarse.
- `F13-HISTORICAS` pasa de RD a VI por `L-F13-VALIDADOR-REM191`.

**Lo que cambia:**

- El catálogo tiene ahora 17 RN, 12 RD y 10 VI. `src/general.py` espera esos
  recuentos.
- Ya no queda ninguna fila con disponibilidad `INCOMPLETA`.
- Al pie de `BALANCE.md` figuran los dos límites, además de la mención de
  U42 y U60 no localizados.

**Comprobado sin cálculo:**

- Plan:
  - `salidas/general/plan_06` cumple;
  - el lanzador del Paso 3 cumple en `salidas/paso3_20261118_230624`;
  - 3.955 llamadas, 0 rechazadas y 13 recetas con código 0.
- Control del balance (`local/pruebas_balance_u42_u60.py`, `salidas/u42_u60/`).
  Supone en memoria que todas las llamadas del completo se aceptaron:
  - **antes de las decisiones** (`balance_antes.json`): las dos filas
    quedaban «pendiente de decisión», así que el modo completo no podía ser
    conforme;
  - **con las decisiones** (`balance_despues.json`): las dos filas quedan
    «completa», las 39 claves pueden completarse y los dos límites aparecen
    al pie;
  - **con una de las dos filas pendiente** (variante simulada): solo esa
    fila queda «pendiente de decisión»;
  - **con `fam13-reproducir` o `fam10-tabla` rechazada o no conforme**: su
    fila queda «no conforme» y «pendiente (Paso 3)»;
  - **con una de esas llamadas omitida**: igual, «no conforme» y «pendiente
    (Paso 3)»;
  - en esos casos el modo completo tampoco podría ser conforme.

## Dictamen de cierre de 2.1.2 (2026-11-18)

Codex acepta el cierre en el alcance adoptado por el autor. U42 y U60 siguen sin localizarse. F10-ENF-AFIRMACION conserva la categoría RD con el bloque científico de rem148 aplicado al ENF nuevo. F13-HISTORICAS queda en VI. Cinco de sus siete productos se regeneraron con sus huellas aceptadas. Para los otros dos, la evidencia procede de los valores guardados.

En una copia pública nueva, el piloto aceptó sus 16 llamadas y FAM13 volvió a producir los cinco archivos con sus huellas esperadas. Los ocho controles del comando general pasaron. En una simulación del balance, rechazar u omitir la llamada de cualquiera de las dos filas impidió declararla completa. El lanzador reconoció el inventario de 6.303 archivos y validó en modo plan las 3.955 llamadas de las 39 operaciones (17 RN, 12 RD, 10 VI). La corrida completa sigue pendiente.

Evidencia local en `salidas/u42_u60/dictamen_copia.json`, `salidas/u42_u60/dictamen_controles.json` y `salidas/paso3_20261118_232431/plan/`.
