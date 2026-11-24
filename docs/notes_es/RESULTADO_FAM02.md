# RESULTADO FAM02 — R1: salidas globales de afirmaciones y extremos

## Revisión puntual de las duraciones de R1-F — Codex, 2026-11-16

Se revisó sensibilidad_q.py: contexto_s se calcula como time.time() - t0;
preparacion_s, rama_y_cota_s y por_contexto_s registran respectivamente la
preparación, el cálculo de phi_star (o su consulta en caché) y el recorrido
de contextos. Son mediciones de ejecución, no parámetros del método ni
criterios de convergencia.

Procede corregir su tratamiento como metadatos operativos en el adaptador
limpio de R1-F. Limitar la exclusión de igualdad a /contexto_s y a los tres
campos de duración directamente bajo cada afirmación de sensibilidad_q.
Conservar esos campos y sus diferencias visibles; no ignorar claves con
esos nombres en otros objetos ni ampliar OPERATIVOS para todas las tareas.
El resto del contenido científico conserva su comparación exacta y la
regla histórica permanece disponible como antecedente.

Esta corrección de comparación no requiere cambiar criterios científicos
ni repetir el cálculo. Revalidar F_piloto_02 en una salida nueva, comprobar
la comparación y el enlace, y conservar el rechazo original. Un control de
alteración científica debe seguir rechazándose. Comprobar también el límite
de escritura de AREA-ESCRITURA-v1 con una escritura dentro y otra fuera del
directorio permitido, sin ejecutar otra corrida científica.

Esta revisión puntual no declara reproducidas las otras rutas ni cierra
todavía FAM02; queda por comprobar el resultado de esa revalidación.

Fecha: 2026-11-16. Base: `reproduccion_limpia` (sin commits). El original se
consultó en solo lectura.

## Estado

**Dictamen de Codex, 2026-11-16: preparación de FAM02 cerrada en el alcance
de incorporación, receta y pilotos de esta etapa.** La revisión de la
revalidación indicada arriba queda completada. Esto no cierra la ejecución
de las 18 tareas, la instalación aislada ni el Paso 2 completo.

Comprobación independiente sobre los archivos guardados: las 466 fuentes
coinciden con su manifiesto; el producto revalidado es idéntico al calculado
en `F_piloto_02`; las tres afirmaciones coinciden tras separar las duraciones
acotadas y los campos operativos ya previstos por la regla histórica. Hay
10 posiciones de duración y 7 diferencias en ellas. El enlace liga los 8
archivos actuales, incluido el registro y la validación, y el rechazo
original sigue sin enlace. Volví a ejecutar solo `fam02-comparar`: código
0, `aceptada`, sin motivos de rechazo. No repetí el cálculo científico.

La inspección del adaptador y de los resultados guardados de `pruebas_03`
(23/23) respalda el alcance de la corrección: solo R1-F, sin modificar
`r1_rutas.py`, con rechazo de alteraciones científicas y conservación de
las diferencias de tiempo. No se declara aquí una repetición de esa batería.

La regla R1 no exige identidad de la tupla de entorno para esta aceptación.
Se utiliza el perfil comprobado y documentado; F2 continúa adoptada solo
para FAM01. No hace falta otra firma para cerrar esta preparación bajo la
regla R1, ni se amplía por analogía la adopción de F2.

Se distinguen cuatro niveles. «Conectado» no significa «probado», y
«probado» no significa «reproducido».

| Nivel | Estado |
|---|---|
| Conectado | Las 18 tareas corren por `fam02-unidad`, con `fam02-validar` y `fam02-comparar`. C1–C6 y D van por el orquestador; A1, A2, A3×4, B1, B2, B3 y F por sus comandos históricos; V es la validación global, sin cálculo. Las tareas se ligan por el enlace local de aceptación (ENLACE-LOCAL-FAM02-v1), sin reconstruir la autorización histórica. `fam02-comprobar` cumple 10/10 (`comprobar_09`). |
| Probado sin cálculo | Las 10 rutas por comando pasan la **prueba de conexión** con las salidas guardadas de sus comandos (`conexion_03`). En cada una se comprueban preparación de entradas, validación, registro, enlace y consumo: A1/A2 consumen la B3 enlazada y las L de A3 su U enlazada. R1-D se rechaza antes de calcular (faltan C1–C6 aceptadas). R1-V liga las 10 fuentes aceptadas y rechaza la validación global con códigos exactos. Los 11 casos de fallo y control, el traslado y la regresión dan lo esperado (`pruebas_02`). |
| Probado con cálculo | Los dos pilotos autorizados. (1) Una hoja de R1-C1: calculada, validada y comparada (61,7 s; igual exacta a la referencia citada). (2) La tarea R1-F completa (`F_piloto_02`): el comando `sensibilidad_q` termina en el paquete (14,3 s), con 0 lecturas fuera y sin dependencias faltantes. La regla instalada la rechazó por 7 valores de 4 campos de duración (rechazo conservado). Con la corrección técnica IGUALDAD-R1F-TIEMPOS-v1, solo para esos campos de R1-F, la **revalidación sin cálculo** (`F_revalidacion_01`) cumple con igualdad exacta del contenido científico; la comparación queda `aceptada` y el enlace escrito se consume. |
| Pendiente | Las demás rutas por comando (A*, B*) no se han ejecutado en el paquete; sus lecturas en ejecución solo se conocen por análisis estático, que en R1-F omitió un archivo (declarado). D necesita C1–C6 completas (1.289 s central cada una) y V necesita D y F aceptadas. La reproducción de las 18 tareas y las 1.728 afirmaciones no está ejecutada ni autorizada, y el Paso 3 sigue pendiente. |

El R1 de FAM02 son las salidas globales del paso 4. No es la geometría R1
interna de las unidades R2/R3 de FAM01. R1-F (ensayo QSEN2, 3 afirmaciones)
no produce ni autoriza las 32 salidas de Q histórica de FAM03.

## Alcance incorporado

`fuentes_fam02.json` (8ab52a98…) lista 466 piezas con origen, sha256 y papel:
- **Ruta R1 instalada** (`nucleo_s6/instalacion/herramientas/b`, 8 piezas):
  - `tarea_r1.py` fdf4ba1e… (U04);
  - `r1_s6.py` 31faa40d…;
  - `r1_rutas.py` e6f922fb…;
  - `opciones_p1.py` 0c940eca…;
  - `registro_productivo.py` d9addec6… (U05, ya estaba por FAM01);
  - `comparar_tarea.py` 6cb512a1… (U06);
  - `comparar_reproduccion.py` c90fd220… (U06, ya estaba);
  - `datos/paso4/opciones_r1.json` 00c27b59….
- **Núcleo S6 de la instalación** (`nucleo_s6/instalacion/src/paper2b`, 37
  archivos): idéntico archivo por archivo a `nucleo_s6/raiz/src/paper2b`.
- **Entregas históricas** (`nucleo_s6/raiz/tmp/<entrega>/…`): 420 archivos de
  17 entregas, con la misma ruta relativa que en el original.
  - 284 de código: la pila de lima1351 y los módulos de las rutas por
    comando con su núcleo.
  - 113 registros de lanzamiento (`logs/**.tarea.json`), de los que
    `r1_rutas` deriva módulo y argumentos. Se publican en su copia pública
    SAN-RUTAS-v1 (ver abajo).
  - 17 inventarios (`audit/entrega.json`), anclas de huellas.
  - 29 entradas o referencias del método y de C (sin cambios; ver la lista
    siguiente).
  - **Nuevas en esta etapa** (27):
    - 15 entradas que los comandos leen al ejecutarse, más los inventarios de
      sus 5 entregas;
    - 4 salidas guardadas de los comandos de A3;
    - 3 productos históricos de lima2149 que la comparación de A3 lee para
      detectar copias.
- **Dato nuevo**: `datos/fam02/piloto.json` (f14d6d42…), la selección del
  piloto, fijada antes de calcular.

`rutas_personales` de `fuentes_fam02.json` es `[]`.

Las 29 entradas y referencias anteriores, por papel:
- **Entradas del método** (datos aceptados previos, no salidas R1):
  - registro v4 (lima1941 `registro_candidato_v4.json`);
  - puntos U del techo v3 citados por lima0754 (`previa_*`, `puntos_U_G_a21`);
  - SRED-G/N (lima1958 `sred_{G,N}_df.json`);
  - caja del grupo del plan C2 (certificacion `demo/C2/plan.json`);
  - PRV/XDD/CAN (`produccion_inf_G_cid_*`, `seleccion_produccion_*`,
    `extremos_G_d`, `extremos_G_f`).
- **Referencias**, solo para comparar:
  - cobertura R1 y presupuesto (lima1857);
  - hojas E13 v4 citadas (lima1913 `hojas_ci_v4.json`) y `cell_selection.json`;
  - hojas E13 v4 CENSO-v2 y plan histórico del orquestador (lima1351);
  - mediciones ci-df históricas (lima0754 `extremos_G_df_v5_*` y
    `muestra_G_df_*`; lima0003 `muestra_continuada_*`);
  - `cierre_infimos_df.json` (lima2149) y `sensibilidad_q.json` (lima1958).
- **Doble papel**: lima0754 `extremos_G_df_v5_{G,N}.json` es a la vez
  entrada y referencia. Separar ambos papeles exigiría editar código
  histórico.

Cómo se extrajo (`extraccion/extraer_fam02.py`, 66650682…):
- `instalar` copia las piezas de la instalación.
- `trazar`: traza sin cálculo hasta el preflight de las 18 tareas y la parte
  previa al cálculo de `orquestador_b.ejecutar` y de `verificar`. Archivo
  `extraccion/registro/traza_fam02.json` (3b616a44…): 469 archivos, 0
  escrituras en el original.
- `lecturas`: análisis **estático** de los módulos que carga cada comando de
  las rutas por comando (A1 con la opción A1/A2: solo los de SRED). Recoge:
  - importaciones, también las perezosas;
  - literales de datos (constantes, `%` y f-strings) en su entrega y en sus
    entregas base;
  - las salidas de cada comando (`r1_rutas.salidas_del_comando`);
  - los productos de lima2149 citados por la referencia de A3.

  Archivo `extraccion/registro/lecturas_ejecucion_fam02.json` (f12d7a54…): 28
  entradas, 11 salidas guardadas y 8 referencias A3. No prueba que no haya
  otras lecturas: eso lo mostraría el rastro de un cálculo real.
- `copiar` copia todo lo anterior (excepto la biblioteca estándar del
  intérprete base) y sanea los registros de lanzamiento.

No se copiaron árboles de intentos, transcripciones ni la infraestructura de
autorización histórica (`corrida_paso4`, diarios, actos).

## Las 18 tareas

Los datos salen del presupuesto autenticado (lima1857
`presupuesto_lotes.json`). Las dependencias «R1-A*» se expanden como en
`corrida_paso4.construir_plan` y el orden es topológico. «Consume» indica el
producto aceptado en la misma ejecución que la tarea lee por decisión firmada
o por ruta instalada; no figura en `depende_de`.

| Tarea | Contenido | Consume (enlace local) | ids | Ruta en el paquete | Conectada | Probada |
|---|---|---|---|---|---|---|
| R1-A1 | C2: 6 supremos | R1-B3 | 6 | opción A1A2: 2 `sup_reducido` (SRED, lima1958) + intercambio de testigos con la B3 enlazada + `generar_r1_opcion` | sí | conexión: 6/6 testigos |
| R1-A2 | C2: ínfimos d/f | R1-B3 | 4 | opción A1A2: sin comandos; intercambio + `generar_r1_opcion` | sí | conexión: 4/4 testigos |
| R1-A3-G-U / N-U | C2 ínfimo df: cota U | — | 1 / 1 | `certificar_puntos` (lima2149) + `validacion_inicial` (A3) + `generar_r1_opcion` | sí | conexión |
| R1-A3-G-L / N-L | cota L | su U | 1 / 1 | `inf_df_bb_v5` (lima2149) con el certificado U enlazado como argumento + `validacion_inicial` (A3); el par por `a3_evaluar` | sí | conexión; el par rechaza la U copiada |
| R1-B1 / B2 | ínfimos G ci-d, diseños G / N | — | 160 / 160 | `extremos_G_d_inf_v3` (lima1958) + `r1_rutas.validar` + `generar_r1_ruta` | sí | conexión |
| R1-B3 | ci-d 320 sup; ci-f 640 extremos | — | 960 | `extremos_G` (lima2103) + `extremos_G_d` (lima0738) + `validacion_inicial` (B3) + `generar_r1_opcion`; comparación por unidad | sí | conexión: 800 conformes, 160 sin respaldo |
| R1-C1…C6 | ínfimos G ci-df (54, 54, 53, 53, 53, 53) | — | 320 | `orquestador_b.ejecutar` + `verificar` + `generar_r1` | sí | **cálculo**: una hoja de C1 |
| R1-D | supremos ci-df cerrados, agregación, clasificación 1.728, testigos | A1, B1–B3, C1–C6 (15 del plan) | 7.040 | `hojas_y_fuentes_de` + `PilaR1S6.intercambio` + orquestador + `verificar` + `generar_r1` | sí | rechazo previo sin C1–C6 |
| R1-F | sensibilidad de Q, ensayo QSEN2 | — | 3 | `sensibilidad_q` (lima1958) + `r1_rutas.validar` (con IGUALDAD-R1F-TIEMPOS-v1) + `generar_r1_ruta` | sí | conexión; **cálculo** completo (`F_piloto_02`); aceptada al revalidarlo (`F_revalidacion_01`) |
| R1-V | validación global | D, F (cierre: las 17) | — | `generar_r1_global` con las procedencias del enlace local | sí | rechazo con 10 de 17 fuentes |

Orden de ejecución, respetando también los consumos:
1. A3-G-U, A3-N-U, B1, B2, B3, C1–C6, F;
2. A1, A2, A3-G-L, A3-N-L;
3. D;
4. V.

El presupuesto suma 13.037 s central y 20.546 s prudente, de pared en
secuencia. Por tarea (central / prudente, s):

| Tarea | s |
|---|---|
| F | 121 / 241 |
| B3 | 243 / 583 |
| A1, A2 | 193 / 484; 162 / 422 |
| A3 U (G, N) | 458 / 687; 450 / 676 |
| A3 L (G, N) | 232 / 348; 421 / 631 |
| B1, B2 | 1.194 / 1.790; 1.197 / 1.796 |
| C1–C6 | 1.289 / 1.934 cada una |
| D | 525 / 1.051 |
| V | 107 / 233 |

Decisiones vigentes de `opciones_r1` (las tres «aprobadas» en el catálogo
instalado, ninguna añadida):
- **A1A2_INTERCAMBIO_DE_TESTIGOS**: A1 y A2 dependen de B3.
- **A3_CRITERIO_GLOBAL**: el par converge si L ≤ U y U − L ≤ 1e-4, e
  incompatible si L > U, con U y L de productos aceptados en la corrida.
- **B3_VALIDEZ_Y_COMPARACION**: aceptación por unidad; las 160 unidades
  d-sup-N quedan sin respaldo.

Las observaciones de derivación son exactamente las que esas opciones
resuelven: `PRODUCTOR_NO_DERIVABLE`, `REFERENCIA_DEPENDE_DEL_RELOJ`,
`VALIDACION_POR_IGUALDAD_NO_APLICABLE`, `NUCLEO_HISTORICO_DISTINTO_DE_S6…` y
`TESTIGO_C2_DE_PRODUCTOS_DE_OTRAS_RUTAS`.

## Enlace local entre tareas (ENLACE-LOCAL-FAM02-v1)

Sustituye a `tarea_r1.productos_aceptados`, `corrida_paso4.aceptaciones_previas`
y `procedencia_vigente`. No reconstruye la autorización histórica: ni diario,
ni admisión, ni acto.
- **Una ejecución es una carpeta** (`salidas/fam02/<ejecucion>/`), con una
  subcarpeta nueva por tarea.
- **Una salida queda aceptada** cuando su registro productivo pasa las
  comprobaciones que `generar_r1_global` aplica a una fuente:
  - generado por el `registro_productivo` instalado (módulo y huella);
  - validador `r1_s6` instalado;
  - dictamen igual a la verificación;
  - única unidad `R1:<tarea>`, en estado admisible (`completa_validada`) y
    ligada a sus productos.
- **El enlace** `<ejecucion>/aceptaciones/<tarea>.json` fija:
  - la salida (ruta relativa) y su árbol (sha256 de cada archivo);
  - las huellas del registro y del dictamen;
  - la identidad del contexto;
  - las dependencias consumidas;
  - `reproduccion` (verdadero o falso).

  No se sobrescribe. Como es relativo, una ejecución copiada a otra carpeta
  conserva sus enlaces.
- **Una tarea consume solo dependencias enlazadas en la misma ejecución.**
  Justo antes de consumirlas se re-enumera el árbol (debe ser igual al
  fijado) y se repiten las comprobaciones del registro. Si falla, se rechaza
  antes de crear la salida.
- **Las procedencias** que reciben las funciones instaladas (`_leer_b3`,
  `a3_evaluar`, `hojas_y_fuentes_de`, `generar_r1_global`) tienen la forma
  que esas funciones esperan; `corrida_id` es la ejecución.

## Prueba de conexión sin cálculo (`--salidas-guardadas`)

Solo en las rutas por comando.
- Las entradas se preparan como en la ruta real (`r1_rutas.preparar`). En
  lugar de ejecutar cada comando, se pone en el paquete su salida guardada:
  los bytes históricos autenticados por el inventario de su entrega.
- Prueba el enlace, la validación, el registro y los consumidores.
- **No es cálculo ni reproducción**:
  - la salida se enlaza con `reproduccion=false`, y todo consumidor lo
    hereda;
  - un cálculo real se niega a consumirla
    (`DEPENDENCIA_DE_UNA_PRUEBA_DE_CONEXION_EN_UN_CALCULO`);
  - `fam02-comparar` nunca la acepta (`NO_ES_REPRODUCCION`).
- En B1, B2 y F la igualdad con la histórica se cumple por construcción. Lo
  que la prueba acredita es la cadena, no el resultado.

Resultados en `salidas/fam02/conexion_03`:
- cada tarea se lanzó con `supervisar.py` (límite 600 s), un proceso a la
  vez, en 1,9–2,3 s de pared;
- comparaciones en `conexion_03/<tarea>.comparacion.json`;
- código: `fam02.py` 79b14bac….

| Tarea | Unidad | Comparación (`fam02-comparar`) |
|---|---|---|
| B1, B2 | `completa_validada`; 1 salida validada; 160 ids, 0 sin salida | regla cumple; `no_aceptada`: `NO_ES_REPRODUCCION` |
| F | `completa_validada`; 1 salida; 3 ids | ídem |
| B3 | `completa_validada` (validación inicial) | 800 `conforme` y 160 `igual_a_referencia_no_respaldada` (requieren dictamen, decisión R1-B3A2); `no_aceptada` |
| A2 | consume la B3 enlazada; `completa_validada` | intercambio 4/4 testigos (C2 d/f inf); `no_aceptada` por conexión |
| A1 | consume B3; ejecuta los 2 comandos SRED (sustituidos), SRED validado | 6/6 testigos (d, f, df sup); `no_aceptada` por conexión |
| A3-G-U, A3-N-U | `completa_validada` | `se_compara_en_su_par` |
| A3-G-L, A3-N-L | la L recibe como argumento el certificado U enlazado | par `rechazado`: U `COTA_COPIADA_DE_UN_PRODUCTO_HISTORICO`, L `SIN_U_ACEPTADA` (lo esperado con una copia) |
| D | rc 1 antes de crear nada: `DEPENDENCIA_NO_ACEPTADA_EN_ESTA_EJECUCION` (C1–C6 `SIN_ACEPTACION_EN_ESTA_EJECUCION`) | — |
| V | 10 fuentes ligadas, 0 rechazadas; `rechazada`: `TAREAS_R1_SIN_ACEPTAR` (faltan C1–C6 y D) y `COBERTURA_GLOBAL_INCOMPLETA` (1.297 de 8.657 ids) | `no_aceptada` |

Pasadas anteriores, conservadas:
- **`conexion_01`**: A3-U fallaba porque faltaban sus salidas guardadas en
  la base, y A3-L se rechazaba por dependencia no aceptada. Se añadieron a la
  extracción.
- **`conexion_02`**: completa. La L de A3 tomaba el primer archivo del
  producto U por orden alfabético, que resultó ser el certificado. Ahora se
  selecciona por el patrón de `opciones_p1.a3_cota_U` y se exige que sea
  único.
- En la primera comparación de A3-L faltaban los productos históricos de
  lima2149. Se añadieron como referencias A3 y se repitió solo esa
  comparación.

## Comandos y entorno

Se lanzan con el Python de `.venv-fam01`, `-B -P -s -X utf8`,
`PYTHONHASHSEED=0`, `TZ=UTC` y las seis variables de hilos a 1:

```text
reproducir.py fam02-listar    --salida salidas/fam02/<archivo>.json
reproducir.py fam02-comprobar --salida salidas/fam02/<archivo>.json
reproducir.py fam02-unidad    --tarea <R1-…> [--hoja <afirmación> ...] [--tope 2400] [--salidas-guardadas] --salida salidas/fam02/<ejecucion>/<tarea>
reproducir.py fam02-validar   --tarea <R1-…> --nueva <salida> --salida <carpeta nueva> [--enlazar]
reproducir.py fam02-comparar  --tarea <R1-…> --nueva <salida> --salida <archivo>.json
reproducir.py fam02-receta    --salida salidas/fam02/<archivo>.json
```

| Comando | Qué hace |
|---|---|
| `fam02-listar` | Plan de las 18 tareas, ids, rutas y piloto, contrastado con el fijado. Sin modelo (`listar_02`). |
| `fam02-comprobar` | Sin cálculo. Comprueba: huellas de `fuentes_fam02.json` (si fallan, se detiene); `opciones_r1`; plan sin ciclos; piloto; plan del orquestador igual al histórico; por tarea, referencias, productores, preflight y, en las rutas por comando, derivación, importación y entradas de argv; para C, entradas y referencias. Además, la correspondencia SAN-RUTAS-v1 de las 113 copias públicas, la ausencia de rutas personales y la presencia autenticada de las entradas en ejecución, salidas guardadas y referencias A3. Cubre también entorno y F2. `comprobar_08`: 10/10. |
| `fam02-unidad` | Despacho por tarea: C y D por el orquestador (`correr`), A*, B* y F por sus comandos (`correr_ruta`), V por la validación global. Separa dependencias (enlace local) → preflight → **cálculo** → **validación** → enlace. Escribe `ejecucion.json` (naturaleza, `reproduccion`, dependencias consumidas, cálculo, validación y tiempos por separado), `entorno.json` y `archivos_leidos.json`. Código 0 solo si el cálculo termina y la validación cumple. Una asignación parcial (piloto) no se enlaza. |
| `fam02-validar` | Sin cálculo. Repite la validación de una salida en una carpeta nueva (C, D y rutas por comando). No enlaza, salvo con `--enlazar` en una ruta por comando: si el cálculo de origen terminó y la revalidación cumple, enlaza la carpeta nueva en su ejecución (`<ejecucion>/<tarea>`). |
| `fam02-comparar` | Ligadura y validación registrada admisible. Por ruta: C, la referencia citada y la medición histórica; B1/B2/F, igualdad con la histórica del mismo comando (en R1-F, con IGUALDAD-R1F-TIEMPOS-v1, recalculada sobre los bytes); B3, clasificación por unidad; A1/A2, testigos; A3, el par en L; D, verificación; V, la global. «aceptada» exige además `reproduccion=true`. |
| `fam02-receta` | Las 18 tareas con órdenes, consumos, comandos derivados y prueba de conexión (`receta_03`). |

**Entorno.** `.venv-fam01` (CPython 3.12.4, perfil «integracion», numpy
2.0.2) cubre los requisitos de FAM02:
- conforme, sin discrepancias, en todas las salidas;
- dependencias fuera de la biblioteca estándar: solo numpy 2.0.2;
- no se alteró el Python global ni los entornos históricos;
- su intérprete base es el CPython 3.12.4 de
  `tmp/pilotos_b36_b37_2026-10-02/entorno` del original. Por eso el traslado
  no es aislamiento: queda para 2.4.2.

**F2.** Se informa en cada salida: equivalente (4cc5b9a8… frente a
41b467a1…, sin motivos). Está adoptada solo para FAM01; ver «Decisiones y
alcance del entorno». La regla R1 no exige otra adopción para esta preparación.

## Piloto R1-C1 (cálculo autorizado)

**Selección.** La fija `datos/fam02/piloto.json` (20:32:06Z, antes de
calcular a las 20:34:12Z). Regla: primera tarea C del plan con hojas
numéricas y su primera hoja en el orden estable de (afirmación, sentido):
- tarea R1-C1;
- hoja `CLM:PREG-COL-E2-2023:primary:ci:COL:df:conditional_full:G:addback_completo:macro:buffer_destacado`;
- sentido inf, extreme_id e4bb0cc0e78a9fc7.

**Aislamiento.** La hoja es una unidad científica completa:
- no tiene dependencias en el plan del orquestador;
- usa los contextos de su propia afirmación, el dominio completo del grupo
  df del diseño G, los 13 puntos U admisibles y el presupuesto del B&B del
  método (300 s);
- no se redujo dominio, soporte ni precisión;
- el sup se calcula como subproducto y no cuenta.

| | `salidas/fam02/C1_piloto_01` |
|---|---|
| Supervisor | TERMINO, rc 0; pared 61,7 s; CPU 59,6 s; memoria pico 187,8 MB |
| Cálculo | inf y sup convergidos; B&B inf 59,0 s, 646 divisiones, 73.826 evaluaciones de cota |
| Resultado inf | G = [−2,4265865146380836; −2,4264868329940374], brecha 9,968e-5 ≤ 1e-4; testigo con índice de contexto 23 |
| Validación | `hojas_validadas_por_referencia_citada`, cumple (sin medición histórica para esta hoja) |
| Comparación | aceptada frente a la referencia citada (lima1913 `hojas_ci_v4.json`): G, testigo, índice y estado iguales |
| Lecturas | 330 del paquete, 141 del intérprete, 0 fuera |

Lo que el piloto no acredita:
- la condición de tarea de `generar_r1` (sin medición histórica en esta
  hoja; C1 tiene 7 de 54 con ella);
- la duración de la tarea: el presupuesto de C1 es de 1.289 s central.

Una asignación parcial no se enlaza: su registro no es el de la ruta
instalada ni de estado admisible (prueba 8). Revalidado con el código actual
(`C1_piloto_01_validar_03`): verificación, dictamen y `r1_productos`
idénticos a `_validar_02`; el registro solo difiere en
`generado_por.sha256`, la huella de `fam02.py`. La comparación
`C1_piloto_01.comparacion_03` es igual a `_02` salvo los segundos.

## Piloto R1-F (cálculo autorizado)

**Alcance.** El autor autorizó el 2026-11-16 solo este piloto: la tarea R1-F
(comando `sensibilidad_q` de lima1958, ensayo QSEN2, 3 afirmaciones), con un
proceso de cálculo y el lanzador de 600 s. Es la tarea entera, no una hoja:
R1-F no tiene dependencias y la ruta no se redujo.

**Primer intento (`F_piloto_01`).**
- El comando terminó con rc 70 al escribir su salida:
  `DemoError DEMO_WRITE_OUTSIDE_AREA:demo\paso4\sensibilidad_q.json`.
  Lanzador: 10,6 s, sin agotar el límite.
- Es un fallo rutinario de interfaz, no de método. El guardián de
  `nucleo_v.write_json_atomic` solo admite escrituras bajo AREA, la carpeta de
  la entrega, porque históricamente el comando corría con la entrega como
  directorio de trabajo. `r1_rutas.ejecutar_comando` lo corre con el paquete
  como directorio de trabajo y escribe allí sus salidas.
- Se corrigió con la adaptación 10 (AREA-ESCRITURA-v1). La salida del
  intento fallido se conserva.

**Segundo intento (`F_piloto_02`).**

| | `salidas/fam02/F_piloto_02/R1-F` |
|---|---|
| Lanzador | terminó dentro del límite: pared 16,4 s, CPU 15,5 s, memoria pico 194,9 MB. Código de salida 1, porque la validación no cumple. |
| Cálculo | el comando terminó, rc 0, en 14,3 s (histórico: 119,8 s). Sustituciones de carga: `sys.path` y el guardián de escritura. |
| Validación | **rechazada**: `COMANDO_FALLIDO_O_SALIDA_DISTINTA`, `ID_REQUERIDO_SIN_SALIDA_VALIDADA`. `r1_rutas.validar` informa `SALIDA_DISTINTA_DE_LA_HISTORICA`. |
| Enlace | no se escribió `aceptaciones/R1-F.json`. Un consumidor recibe `SIN_ACEPTACION_EN_ESTA_EJECUCION` y el registro `ESTADO_NO_ADMISIBLE:rechazada`. |
| Comparación | `no_aceptada` (`ESTADO_NO_ADMISIBLE:rechazada`, `COMPARACION_NO_CUMPLE`), con `reproduccion` declarada verdadera (no es prueba de conexión). |
| Revalidación | `F_piloto_02_validar_01`: el mismo rechazo y la misma `validacion_ruta`. |

**Causa del rechazo** (`salidas/fam02/F_piloto_02.diagnostico.json`,
generado por `local/diagnostico_fam02_F.py`).
- La regla instalada, `r1_rutas.igual_a_historica`, exige igualdad exacta
  tras quitar los campos de `OPERATIVOS`. Esa lista ya excluye tiempos como
  `segundos`, `pared_s`, `cpu_s` y `duracion_s`.
- `sensibilidad_q` escribe además cuatro campos de duración que esa lista no
  incluye. Todos se miden con `round(time.time() - t, …)` en
  `sensibilidad_q.py` (líneas 124, 132, 142, 151 y 191):

  | Campo | Nuevo | Histórico | Valores |
  |---|---|---|---|
  | `contexto_s` | 0,0 | 74,6 | 1 |
  | `preparacion_s` | 0,3 | 0,5 / 0,5 / 0,6 | 3 |
  | `rama_y_cota_s` | 4,5 | 8,9 | 1 |
  | `por_contexto_s` | 0,0 | 0,001 | 2 |

- Sin esos cuatro campos, los 120 valores restantes son exactamente iguales:
  en las 3 afirmaciones, Φ*, m* continuo, estado de la fórmula,
  comprobaciones, universos de testigo y de nudos e identidad G/N en el
  punto; y en el conjunto, `cumple_todo` y `G_N_mismo_m_estrella`
  (verdaderos en ambas).
- No es una discrepancia científica: la diferencia es de reloj. Pero con la
  regla tal como está instalada, ninguna nueva ejecución de este comando
  podría aceptarse, porque esos tiempos cambian en cada corrida. El
  rechazo de `F_piloto_02` se conserva; la corrección se describe en
  «Corrección técnica y revalidación».
- No se investigó por qué esta corrida es más rápida que la histórica; los
  valores científicos coinciden.
- Huellas de la salida del comando: nueva 80d76970…, histórica a34ce594….

**Lecturas reales** (mismo diagnóstico).
- El cálculo leyó 381 archivos del paquete y 144 del intérprete, y 0 fuera
  de ambos.
- Frente a la prueba de conexión de la misma ruta (`conexion_03`, 373 del
  paquete), leyó 8 archivos más. Todos estaban declarados:
  - 3 en `fuentes_fam01.json`: el paquete CA2 (b2a90d7d…), el índice de
    paquetes S5 y el `tax_shares_marg.csv` de D6 v2;
  - 5 en `fuentes_fam02.json`: `codigo/demo/cobertura_mejorada.py` de
    lima1351; `audit/entrega.json` y el parcial P3 de `pilotos_b36_b37`; y
    `audit/entrega.json` y `analisis_final.json` de
    `viabilidad_alternativa`.
- El análisis estático de lecturas no previó `cobertura_mejorada.py`, que
  estaba declarado como parte de la pila de lima1351. En cambio, previó 7
  archivos que el cálculo no leyó.
- Las únicas lecturas sin manifiesto son las del entorno (116 de
  `.venv-fam01`) y dos archivos del propio adaptador
  (`datos/fam01/contexto_s6.json` y `fuentes_fam02.json`). Son las mismas de
  la prueba de conexión.

**Corrección técnica y revalidación (`F_revalidacion_01`).**
- El autor indicó la corrección técnica el 2026-11-16, y se aplicó como
  adaptación 11 (IGUALDAD-R1F-TIEMPOS-v1). Solo en R1-F se tratan como
  operativos `/contexto_s` y los campos `preparacion_s`, `rama_y_cota_s` y
  `por_contexto_s` que cuelgan directamente de cada afirmación.
  `r1_rutas.OPERATIVOS` y `r1_rutas.py` no cambian.
- Cualquier otra clave con esos nombres, cualquier otra tarea y todo el
  contenido científico siguen con la igualdad exacta instalada.
- Los campos se conservan en las salidas, y sus diferencias se informan en la
  validación y en la comparación.
- No se repitió el cálculo. `fam02-validar --enlazar` copió el paquete de
  `F_piloto_02` en la ejecución nueva y repitió la validación. La salida del
  comando es la misma (80d76970…).

| | `salidas/fam02/F_revalidacion_01/R1-F` |
|---|---|
| Revalidación | sin cálculo; lanzador 1,3 s, rc 0. Validación `completa_validada`, cumple, sin códigos; 1 salida validada, 3 ids. |
| Igualdad | contenido científico igual; los 10 campos de tiempo están en las dos salidas y 7 difieren (los de la tabla anterior). Sin la adaptación, la regla instalada seguiría rechazando. |
| Enlace | `F_revalidacion_01/aceptaciones/R1-F.json` (6d186e57…), con `reproduccion=true`, la regla de igualdad y el origen de la revalidación (`F_piloto_02`). Un consumidor lo acepta. |
| Comparación | `aceptada`: ligadura y validación admisibles, igualdad recalculada sobre los bytes y reproducción declarada (`R1-F.comparacion.json`, 4ac2daf1…). |
| Rechazo anterior | `F_piloto_01`, `F_piloto_02`, `F_piloto_02_validar_01` y el diagnóstico conservan sus 27 archivos con las mismas huellas; `F_piloto_02` sigue sin enlace. |

**Pruebas de la corrección** (`local/pruebas_fam02_r1f.py`, a5b04a85…;
`salidas/fam02/pruebas_03.json`). Dieron 23 de 23 conformes, sin cálculo
científico, en 7 s.
- **Regla, sobre los bytes reales.** La salida real de `F_piloto_02` es
  igual. La rechazan, en cambio:
  - un cambio de 1 ulp en `m_estrella_continuo`, en `Phi_estrella` o en
    `D_dme_gai`;
  - otro `estado_formula`;
  - `preparacion_s` anidado en `Phi_estrella` o en la raíz;
  - `contexto_s` bajo una afirmación;
  - un campo de tiempo ausente, de texto, negativo o booleano.

  Un tiempo cambiado (`rama_y_cota_s` = 999,9 o `contexto_s` = 12.345,6)
  sigue siendo igual y se informa.
- **Alcance.**
  - En R1-B1 la regla no actúa: `r1_rutas.igual_a_historica` queda sin
    cambio, y la revalidación de B1 de `conexion_03` reproduce su
    `validacion_ruta.json` byte a byte.
  - Con una ruta distinta de la prevista, R1-F se detiene con
    `R1F_RUTA_DISTINTA_DE_LA_PREVISTA`.
  - La regla instalada se restaura al salir, también tras un error.
- **De punta a punta.** Una copia de `F_piloto_02` con `m_estrella_continuo`
  alterado en 1 ulp se revalida con `--enlazar`. Queda rechazada
  (`SALIDA_DISTINTA_DE_LA_HISTORICA`), sin enlace, y su comparación da
  `no_aceptada`.
- **Área de escritura.** Se carga `nucleo_v` de lima1958 con el importador
  instalado, con el paquete nuevo como directorio de trabajo y un intérprete
  por caso:
  - con la adaptación, escribe dentro con ruta relativa y absoluta;
  - también con la adaptación, rechaza fuera (`../`, una ruta absoluta
    exterior y `demo/../../`) con `DEMO_WRITE_OUTSIDE_AREA`, sin crear
    nada;
  - sin la adaptación (control), rechaza incluso dentro del paquete, como en
    `F_piloto_01`.

**Lo que este piloto acredita:**
- la ruta R1-F calcula dentro del paquete, con el entorno fijado, sin
  dependencias faltantes ni lecturas externas;
- su salida científica coincide exactamente con la histórica; solo difieren
  los cuatro campos de reloj;
- con la validación rechazada no se escribió enlace; con la corrección
  técnica, la revalidación cumple, se enlaza y la comparación se acepta.

**Lo que no acredita:**
- que la aceptación sea un cálculo nuevo de la revalidación: el cálculo es
  el de `F_piloto_02`. La revalidación solo repite la validación, y el
  enlace lo declara;
- que las demás rutas estén libres de dependencias faltantes. Las rutas A* y
  B* solo tienen prueba de conexión. En R1-F, el análisis estático omitió un
  archivo, así que su lista no basta por sí sola;
- que AREA-ESCRITURA-v1 baste en las otras rutas. El mismo guardián está en
  el `nucleo_v.py` de otras cinco entregas (lima2103, lima2149, lima1259,
  lima0738, lima1351), pero solo R1-F lo ha ejercitado.

## Pruebas de fallo, traslado y regresión

Pruebas de esta etapa: `local/pruebas_fam02_rutas.py` (b100a9a1…), lanzado
con `supervisar.py` (45,8 s); informe `salidas/fam02/pruebas_02.json`.
- Trabajan sobre copias de `conexion_03` y del piloto, sin cálculo y con los
  comandos.
- Donde el caso es interno (aceptar, leer un registro público) llaman
  directamente a `src/fam02.py`.
- Las pruebas de C de `pruebas_01` siguen vigentes.

| Caso | Resultado |
|---|---|
| A2 sin B3 aceptada en su ejecución | rc 1 `DEPENDENCIA_NO_ACEPTADA_EN_ESTA_EJECUCION` (`SIN_ACEPTACION_EN_ESTA_EJECUCION`), sin carpeta |
| Control: ejecución con B3 copiada a otra carpeta | A2 la consume, rc 0: el enlace relativo viaja |
| Aceptar otra vez una tarea aceptada | `TAREA_YA_ACEPTADA_EN_ESTA_EJECUCION`; enlace sin cambios |
| Producto de B3 alterado tras la aceptación (1 ulp en `extremos_G_d.json`, `C2/G/inf_C2_punto/0`) | rc 1 `PRODUCTO_ALTERADO_TRAS_LA_ACEPTACION`, sin carpeta |
| Enlace que apunta al producto de otra ejecución | rc 1 `ENLACE_AJENO_O_DE_OTRA_EJECUCION` |
| Cálculo real (sin `--salidas-guardadas`) con B3 de una prueba de conexión | rc 1 `DEPENDENCIA_DE_UNA_PRUEBA_DE_CONEXION_EN_UN_CALCULO`, sin carpeta |
| Revalidar B1 sin cálculo | rc 0; `validacion_ruta.json` idéntico al de la unidad |
| Salida del comando de B1 alterada 1 ulp (`C2/G/H_en_a_max`) | rechazada: `SALIDA_DISTINTA_DE_LA_HISTORICA`, 0 salidas validadas |
| Piloto parcial presentado para enlace | no aceptado: `REGISTRO_NO_GENERADO_POR_LA_RUTA`, `UNIDADES_AJENAS_O_DUPLICADAS`, `ESTADO_NO_ADMISIBLE`; sin enlace; el consumo lo rechaza |
| V con F alterada tras su aceptación (`D_dme_gai` 0 → 5e-324) | F rechazada (`PRODUCTO_ALTERADO_TRAS_LA_ACEPTACION`); validación global `rechazada` |
| Registro de lanzamiento público re-serializado (mismo contenido, otros bytes), en la copia trasladada | `fam02-comprobar`: huellas falsas, archivo señalado; `r1_rutas._aut`: `COPIA_PUBLICA_SIN_CORRESPONDENCIA`; `fam02-unidad`: `DEPENDENCIA_AUSENTE_O_ALTERADA` antes de calcular, sin carpeta |

**Traslado.**
- Se copiaron 4.484 archivos en 3,4 s: `reproducir.py`, los `fuentes_*`,
  `src`, `datos`, `nucleo_s6`, `referencias`, la declaración de lecturas y
  `conexion_03`. Carpeta: `local/traslado_fam02_02`.
- Se lanzó desde una tercera carpeta con el mismo `.venv-fam01`.
- Resultados:
  - `fam02-comprobar`: rc 0;
  - una ejecución nueva B3 → A2 (conexión): rc 0 las dos;
  - `fam02-validar` de B1: rc 0, con `validacion_ruta.json` idéntico al del
    sitio;
  - `fam02-comparar` de B1: igual al del sitio salvo los segundos (rc 1,
    porque es conexión);
  - lecturas de la validación: 232 del paquete, 199 del intérprete, 0 fuera.
- Fue en la misma máquina, así que sigue siendo traslado.

**Regresión** (cambiaron `reproducir.py` y `src/fam02.py`; `src/fam01.py`
no):
- C1: ver «Piloto R1-C1».
- R1-F: `comprobar_08`, con AREA-ESCRITURA-v1, es igual a `comprobar_07` salvo
  los segundos. Las pruebas de `pruebas_02` son anteriores a esa adaptación,
  que solo actúa al ejecutar de verdad un comando.
- Tras IGUALDAD-R1F-TIEMPOS-v1 y `--enlazar`:
  - `comprobar_09` (FAM02) es igual a `_08` salvo los tiempos;
  - `fam01-comprobar` (`comprobar_11`) es igual a `_10` salvo los tiempos;
  - la revalidación de B1 queda igual (`pruebas_03`).

  Las pruebas de la corrección están en «Piloto R1-F».
- FAM12: `revisar`, `p7-k1`, `p7-suplemento` y `q-local` (`_08`) son iguales
  a `_07` salvo los segundos.
- FAM01, salidas guardadas sin recalcular:
  - `comprobar_10` es igual a `_09` salvo los segundos;
  - `comparar_R2_11` y `comparar_R3_09` son iguales a `_10` y `_08` salvo
    los segundos.

## Adaptaciones mínimas

No cambian fórmulas, tolerancias, topes, soportes ni criterios. El código
histórico no se edita.

1. **Contexto.** `fam01.Contexto`, con la etiqueta «REPRODUCCION LIMPIA FAM02
   NO OFICIAL» (misma construcción que ContextoS6, sin autoridad viva).
2. **Despliegue.** Solo lo que la pila usa (`raiz_fuentes =
   nucleo_s6/raiz/tmp`; `s6_package`, `d7_tree` y `run_class` de
   `datos/fam01/contexto_s6.json`; `ancla = null`).
3. **Plan R1.** La rama R1 de `corrida_paso4.construir_plan` sobre el
   presupuesto autenticado, sin admisión, diario ni acto.
4. **Tarea C y D.** Los pasos de `tarea_r1.main`, en el mismo orden y con las
   mismas opciones. Para D, las 15 dependencias del plan se toman del enlace
   local.
5. **Registro de asignación parcial** (`registro_r1_parcial`), solo para
   pilotos, nunca enlazado.
6. **`sys.path`.** Primero el núcleo S6 de la instalación, después la raíz
   copiada; nunca `raiz/src`.
7. **Rutas por comando.** Los pasos de `tarea_r1.main` y `ruta_intercambio`
   (`derivar`, `preflight_comandos`, `ejecutar_ruta`, `validar`,
   `generar_r1_ruta` y `generar_r1_opcion`), con dos sustituciones:
   - la opción se activa con la decisión «aprobada» del catálogo instalado
     (00c27b59…), en lugar de `opciones_autorizadas`;
   - los productos aceptados se leen del enlace local, en lugar de
     `aceptaciones_previas`.

   Por eso `intercambio_local`, `b3_local` y la evaluación del par A3 llaman
   a las funciones instaladas sin cambios: `seleccion_c2`, `_leer_b3`,
   `_sred_validados`, `_intercambio`, `_b3_unidades`, `_b3_dictaminar`,
   `a3_contexto` y `a3_evaluar`.
8. **SAN-RUTAS-v1** (saneamiento público, autorizado):
   - Cada registro de lanzamiento se publica con el prefijo absoluto de la
     raíz del proyecto quitado de «cwd» y del lanzador de «comando». Módulo,
     argumentos y demás campos no cambian; `sanear_registro` lo comprueba
     contra el original.
   - `fuentes_fam02.json` declara la huella pública y la de origen de cada
     copia.
   - El adaptador de `r1_rutas._aut` acepta una copia pública solo si sus
     bytes tienen la huella pública declarada y el inventario anclado de su
     entrega lista la de origen. Inventarios y anclas no cambian.
   - De los 113 registros, 112 cambian y 1 no tiene rutas (comando vacío).
9. **Enlace local y prueba de conexión**, descritos arriba.
10. **AREA-ESCRITURA-v1** (fallo rutinario del piloto R1-F).
    - Al cargar los módulos históricos, `r1_rutas` aplica sus sustituciones
      textuales (`GENERICAS`) solo donde aparece el texto exacto.
    - `fam02.pila()` añade una: en el guardián de
      `nucleo_v.write_json_atomic`, el área admitida pasa de la carpeta de la
      entrega (`AREA`) al directorio de trabajo del comando, que es el
      paquete de la ejecución (`Path.cwd()`).
    - El guardián sigue rechazando toda escritura fuera del paquete. No
      cambian formato, contenido ni ubicación relativa de las salidas.
    - Queda registrada en las sustituciones de `ejecucion.json`.
    - `comprobar_08` es igual a `comprobar_07` salvo los segundos.
    - Probada aislada en `pruebas_03`: escribe dentro del paquete y rechaza
      fuera; sin ella, rechaza incluso dentro.
11. **IGUALDAD-R1F-TIEMPOS-v1** (corrección técnica indicada por el autor,
    solo en R1-F).
    - En la igualdad con la salida histórica, además de
      `r1_rutas.OPERATIVOS`, se apartan solo `/contexto_s` y
      `/afirmaciones/<afirmación>/{preparacion_s, rama_y_cota_s,
      por_contexto_s}`.
    - Un campo se aparta solo si está en las dos salidas y es una duración
      (número finito ≥ 0). Si no, la igualdad falla.
    - El resto, con `r1_rutas._sin_operativos`, exige igualdad exacta.
    - Se activa solo mientras se valida R1-F, y solo si la ruta es el
      comando `sensibilidad_q` de lima1958 con su única salida. Se restaura
      siempre.
    - `fam02-comparar` la recalcula sobre los bytes.
    - Validación, comparación y enlace la registran, con cada diferencia de
      tiempo.
12. **Revalidación con enlace** (`fam02-validar --enlazar`, rutas por
    comando).
    - Escribe el enlace en la ejecución de la carpeta nueva solo si el
      cálculo de origen terminó y la revalidación cumple.
    - El enlace registra la revalidación sin cálculo y su origen.
    - La salida de origen no se toca.

## Decisiones y alcance del entorno

1. **Campos de duración de R1-F — resuelta (2026-11-16).** El autor
   indicó la corrección técnica y se aplicó acotada a las cuatro rutas
   exactas de R1-F (adaptación 11). `F_revalidacion_01` está aceptada y
   enlazada; el rechazo de `F_piloto_02` se conserva.
2. **Entorno de FAM02 — aclarado en la revisión.** La regla R1 instalada no
   compara la tupla técnica del entorno. La preparación y los pilotos se
   aceptan bajo esa regla y el perfil documentado. La equivalencia F2 se
   informa como diagnóstico; F2 no se adopta para FAM02. Una extensión de
   esa decisión no es requisito adicional de esta preparación. La
   instalación realmente aislada se comprobará en 2.4.2.
3. **Sin decisión científica nueva.** La diferencia de R1-F es de reloj. La
   corrección de la decisión 1 trata de qué campos de tiempo excluye la
   igualdad, no de valores científicos.
   - No se activó ninguna propuesta por analogía.
   - Las 160 unidades d-sup-N de B3 siguen sin respaldo, como fija R1-B3A2.
   - El par A3 exige U y L nuevos, y lo comprueba.

Saneamiento: las fuentes públicas ya no tienen rutas personales. Las salidas
de ejecución (`salidas/`, fuera de Git) registran rutas absolutas en
`registro_productivo.generado_por.paquete`, en las procedencias del
intercambio y de `dependencias_consumidas.json`, y en `entorno.json`, como en
FAM01. Si se publicaran salidas, necesitarían su propio saneamiento.

## Receta completa (preparada, no ejecutada)

`fam02-receta` → `salidas/fam02/receta_03.json`. Por tarea, en el orden de
ejecución, recoge:
- dependencias, consumo en la ejecución y su regla;
- ids y presupuesto;
- ruta instalada;
- órdenes del paquete;
- en las rutas por comando, la orden de la prueba de conexión, los comandos
  derivados y sus observaciones.

Condiciones:
- el entorno de «Comandos y entorno»;
- un proceso de cálculo a la vez, con el lanzador que termina el árbol;
- `--tope 2400` bajo un lanzador de 2.400 s. Una tarea C completa no cabe en
  600 s (1.289 s central), y B1/B2 tampoco (1.194 s);
- `--tope-afirmacion 300` sin cambios;
- una ejecución = una carpeta, con una subcarpeta nueva por tarea en el orden
  de «orden»; nada se sobrescribe.

Órdenes por tarea:

```text
fam02-unidad   --tarea <T> --salida salidas/fam02/<ejecucion>/<T>
fam02-comparar --tarea <T> --nueva  salidas/fam02/<ejecucion>/<T> --salida salidas/fam02/<ejecucion>/<T>.comparacion.json
```

La U de A3 se compara en su L.

Qué distingue la receta (F1):
- **Reutilizable**: las entradas históricas aceptadas anteriores a R1 que el
  método consume como datos, y los comandos y entradas de las rutas por
  comando con sus inventarios.
- **Solo para comparar**: las referencias.
- **Solo para la prueba de conexión**: las salidas guardadas, nunca como
  reproducción.
- **Se genera en la nueva ejecución**: las salidas de las 18 tareas y todo
  producto que otra tarea consume. Deben ser los aceptados en esa ejecución,
  nunca los históricos.
- **Fuera de alcance**: P7, Q, COV, ENF, T8 y Exp8 (EX-R1-POSTERIORES).

## Siguiente trabajo concreto

1. Continuar la incorporación con FAM03 cuando el autor dé el encargo. No
   se exige otro piloto de A* o B* como ronda previa para cerrar esta etapa.
2. En 2.4.2, comprobar la instalación aislada con pruebas representativas.
   En las ejecuciones autorizadas, registrar las lecturas reales y resolver
   cualquier dependencia que aparezca; las pruebas de conexión no demuestran
   por sí solas que A*/B* funcionen de principio a fin.
3. Ejecutar y validar las 18 tareas en el Paso 3, con la autorización que
   corresponda. A*/B* aún no tienen cálculo real; D/V no tienen un cierre
   global positivo. Las cifras históricas de presupuesto no son una ETA
   actual. La corrección temporal de R1-F no se aplica a otras rutas.

Código de esta etapa:
- `src/fam02.py` fd765026…. `conexion_03` y `pruebas_02` se generaron con
  79b14bac… y 58af5040…; después cambiaron `entradas_en_ejecucion` y
  `receta`, que no tocan unidad, validar ni comparar, y se añadió
  AREA-ESCRITURA-v1, que solo actúa al ejecutar de verdad un comando;
- `F_piloto_02`, su revalidación y su comparación se generaron con
  fd765026…;
- después se añadieron IGUALDAD-R1F-TIEMPOS-v1 y `--enlazar`: `src/fam02.py`
  42fa50d2… y `reproducir.py` 9b2849f9…, con los que se generaron
  `F_revalidacion_01`, `pruebas_03` y `comprobar_09`;
- `local/diagnostico_fam02_F.py` d325fbd4… (diagnóstico, solo lectura);
- `local/pruebas_fam02_r1f.py` a5b04a85… (pruebas de la corrección).
