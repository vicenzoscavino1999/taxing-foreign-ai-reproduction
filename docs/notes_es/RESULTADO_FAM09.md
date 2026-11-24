# RESULTADO FAM09 — T8 (preservadas, λ, captura, testigo alto, C5B)

Fecha: 2026-11-18 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original y los libros se consultaron en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Preparación revisada y cerrada en su alcance por Codex el 18 de noviembre de 2026. El dictamen figura al final. El paquete contiene el código histórico de las cinco operaciones (copias exactas o proyecciones saneadas en `nucleo_s6/t8`), el núcleo lima1855 y la configuración del testigo, las entradas, las referencias rem138/rem140/rem141/rem144/rem147 y la receta completa. Las seis etapas, sus validaciones y sus comparaciones están conectadas y probadas. |
| F09-HIST (VI) | Integridad comprobada sin cálculo: 9.434 filas preservadas con su clave, de 13.656 claves únicas. |
| F09-LAMBDA (RD) | Regenerada. Producto idéntico byte a byte a rem138 (1b4881c3…). |
| F09-CAPTURA (RD) | Regenerada sobre el λ **nuevo**. Vista idéntica byte a byte a rem140 (66891b45…): 2.071 resueltas, cada una con su procedencia, y 40 pendientes. |
| F09-TESTIGO (RN) | **Cálculo**: techo alto e8b1f7fd… ejecutado una vez bajo el supervisor (600 s): 1,0 s. Sus 15 campos científicos son iguales a rem141 (C2 = 0.7651580128158672, tau_d = tau_f = 0,6). **U36**: `validar_testigo.py` se ejecutó hoy sobre los bytes nuevos (complete, garantía cumplida). **Emisión**: las mismas 35 filas cubiertas y las mismas 5 pendientes. |
| F09-C5B (RD) | Regenerada sobre la vista del testigo nueva. Certificado **reutilizado**; su derivación no se regenera. Vista final `3cf3d99d…` con 13.656 filas y 0 pendientes. Frente a rem147 no hay diferencias científicas; 40 filas difieren solo en campos de vínculo nombrados. |
| Reproducción completa | Pendiente (Paso 3). La receta está lista y no se ha lanzado como ejecución general. |

## Qué se preservó, qué se regeneró y qué se calculó de nuevo

| Tipo | Filas | Origen en esta reproducción |
|---|---:|---|
| Preservadas (insumo) | 9.434 | Del anexo T8 rem108 (e63ae329…), autenticado por su inventario. Las 14 corridas históricas **no** se vuelven a correr (límite L-T8). En la vista final son idénticas a su fila del anexo. |
| Regeneradas: λ | 2.111 | Con `materializar_lambda.py` sobre la entrada λ autenticada (rem134). Mismos bytes que rem138. |
| Regeneradas: captura | 2.071 | Con `materializar_captura.py` sobre el λ nuevo, con las pruebas por fila aceptadas (PRUEBAS_FILA_v3). Mismos bytes que rem140. |
| Emitidas a partir de un techo recalculado | 35 | El techo alto se **recalculó** con el trabajador auténtico y el núcleo lima1855. Las 35 filas se emiten desde ese techo nuevo, validado por la U36, con cobertura exacta y la regla aceptada. |
| Regeneradas: C5B | 5 | Exclusión estricta con el certificado C5B **reutilizado** (fc403d40…) sobre la vista del testigo nueva. |
| **Total** | **13.656** | 0 pendientes en la vista final. |

## Orden mínima para repetir la prueba

Desde la base, con el intérprete de `.venv-fam01` y `PYTHONHASHSEED=0`
(`py` abrevia `<python de .venv-fam01> -B -P -s -X utf8 reproducir.py`; `S`
es una carpeta nueva bajo `salidas/fam09/`):

```
py fam09-comprobar --salida S/comprobar.json
py fam09-etapa --tarea HIST --salida S/hist
py fam09-validar --nueva S/hist --salida S/hist.validacion.json
py fam09-etapa --tarea LAMBDA --salida S/lambda
py fam09-validar --nueva S/lambda --salida S/lambda.validacion.json
py fam09-etapa --tarea CAPTURA --entrada lambda=S/lambda --entrada validacion_lambda=S/lambda.validacion.json --salida S/captura
py fam09-validar --nueva S/captura --salida S/captura.validacion.json
<supervisar.py> TESTIGO 600 <registro> --cwd <base> -- py fam09-etapa --tarea TESTIGO --salida S/testigo
py fam09-validar --nueva S/testigo --salida S/testigo.validacion.json          (U36)
py fam09-etapa --tarea INCORPORACION --entrada captura=S/captura --entrada validacion_captura=S/captura.validacion.json \
               --entrada testigo=S/testigo --entrada validacion_testigo=S/testigo.validacion.json --salida S/incorporacion
py fam09-validar --nueva S/incorporacion --salida S/incorporacion.validacion.json
py fam09-etapa --tarea C5B --entrada testigo_vista=S/incorporacion --entrada validacion_testigo_vista=S/incorporacion.validacion.json --salida S/c5b
py fam09-validar --nueva S/c5b --salida S/c5b.validacion.json
py fam09-comparar --tarea <ETAPA> --nueva S/<etapa> --validacion S/<etapa>.validacion.json --salida S/<etapa>.comparacion.json   (las seis)
```

`fam09-receta` escribe la misma secuencia de 20 pasos (`salidas/fam09/receta_01.json`).
Cada etapa consume la salida **nueva** de la anterior junto con su registro de
validación aceptado, y lo comprueba antes de crear su carpeta. Ninguna etapa
recurre a un producto histórico por su cuenta.

## Ruta efectiva

```
anexo T8 (rem108) ──► HIST (integridad; 9.434 preservadas)
entrada λ rem134 ──► LAMBDA ──[registro]──► CAPTURA ──[registro]──┐
manifiesto v2 + lima1855 ──► TESTIGO (cálculo, 600 s) ──► U36 ──[registro]──┤
                                                                            ▼
             INCORPORACION: incorporación → lector → cobertura exacta → materializar_t8_testigo
                                                                            │ [registro]
                                                                            ▼
                                  C5B: materializar_t8_c5b (certificado reutilizado) ──► vista final
```

- Separación de procesos: el trabajador y el validador del testigo cargan
  paper2b del núcleo lima1855 (36 archivos leídos) en un proceso sin paper2b
  precargado. λ, captura, emisión y C5B cargan el paper2b de
  `nucleo_s6/instalacion` (FAM01) a través del finalizador a8aded1d…;
  `conexion_testigo` aísla el lector del finalizador.
- Lecturas reales: cada carpeta registra `archivos_leidos.json`. En todas
  las etapas `fuera_del_paquete_y_del_interprete = []`,
  `sin_manifiesto = []` y ninguna referencia leída. El RESULTADO del testigo
  guarda además en `evidencia_real` los 20 módulos paper2b cargados, con su
  huella; son iguales a rem141.
- Separación de referencias, insumos y salidas: `referencias/fam09`
  (rem138/rem140/rem141/rem144/rem147) solo lo leen `fam09-comparar` y
  `fam09-comprobar`. Los insumos están en `nucleo_s6/t8` y `datos/fam09`; las
  salidas, en `salidas/fam09`.

## Extracción

`extraccion/extraer_fam09.py copiar <original> <directorio de los libros>`
genera `fuentes_fam09.json` (602ea643…), con estas piezas:

- **Archivos**: 274 en 32 áreas, espejo de `tmp/<área>/<rel>` en
  `nucleo_s6/t8`. Cada uno está en el inventario de su área con su huella
  (`fuera_del_inventario_de_su_area = []`).
- **Proyecciones saneadas**: 12, cada una ligada a su original y restituible
  (FUENTES_CAPTURA, CONGELAMIENTO_TESTIGO_v3, CARGA_NUCLEO, lector,
  conexion_testigo y conexion_c5b con sus manifiestos, guiones C3/M2 y
  referencias del testigo).
- **Reutilizadas de FAM01/FAM02**: finalizador `unidades.py` a8aded1d…,
  `model.py` 24af1c42… y D7 10a0bd5b….
- **Solo procedencia**: 12 actos de autoridad (notas y dictámenes
  rem135/rem137/rem142/rem145, despliegue y acta P3, aceptaciones, ledger
  rem144). Se autenticaron por huella y **no** se copian. De la aceptación
  técnica rem145 se guarda solo un resumen sin rutas, ligado a su original
  a816420c….
- **Datos nuevos**: `datos/fam09/pilotos.json` (290be1f0…) y la declaración
  NO OFICIAL `datos/fam09/ejecucion_limpia.json` (fc484fd6…). Los fijó
  `fam09-listar` antes de calcular.

## Adaptaciones (declaradas en `src/fam09.py`)

No cambian fórmulas, claves, tolerancias, garantías ni criterios. Cada
original se sustituye una sola vez (`fam09-comprobar`: 10/10 únicas).

- **GUION-v1 / MODULOS-v1**: los guiones se ejecutan desde sus bytes exactos.
  Los módulos importados por nombre o por ruta y huella pasan por `_MODULO9`,
  con la misma huella.
- **RAIZ-T8-v1**: la raíz es `nucleo_s6/t8`. `paso4/instalacion` →
  `nucleo_s6/instalacion`, `fase2_datos` → `nucleo_s6/raiz/fase2_datos`.
- **NUCLEO-C0-v1**: la identidad del C0 (d0bf5cd6…) es la de FAM05.
- **SANEADO-v1**: una proyección cuenta con la huella de su original.
- **PAQUETE-v1**: solo se comprueban las piezas copiadas. No se copian las
  recetas `.sh`, los emisores de alcance ni los ensayos.
- **MODO-CANDIDATA-v1**: λ, captura, emisión y C5B corren en modo candidata,
  sin alcance ni decisión. El producto es el mismo.
- **PUERTA-v1**: la puerta de producción (alcance v3 y decisión humana) no se
  ejecuta ni se reconstruye. El testigo corre en modo produccion con la
  declaración NO OFICIAL como alcance. Esa declaración fija antes de
  calcular las entradas esperadas (`entradas_esperadas` del código
  histórico), las asignaciones y los límites (1 proceso, 600 s). Nunca hay
  decisión.
- **AUTORIDAD-EXTRAIDA-v1**: los actos de autoridad se cotejan por la huella
  registrada en la extracción; la aceptación rem145, por su resumen.
- **PROCEDENCIA-LOCAL-v1**: la entrega del testigo es la carpeta local. El
  «dictamen» que cita la incorporación es el **registro de fam09-validar**,
  no un dictamen de Codex.
- **ENLACE-v1**: una salida nueva sustituye a su homóloga histórica solo si
  tiene la misma huella fijada (λ 1b4881c3… → captura; captura 66891b45… →
  lector y emisión).
- **ENLACE-TESTIGO-v1 / ENLACE-C5B-v1**: la autoridad de `conexion_testigo` y
  de `conexion_c5b` se enlaza a las salidas nuevas validadas, con
  `ENLACE_T8_*.json` en cada carpeta. El manifiesto histórico indexado se
  sigue cotejando con la autoridad histórica. La aceptación técnica rem142 la
  ocupa una **aceptación local por cobertura exacta**
  (`ACEPTACION_TESTIGO_FAM09.json`, no oficial).

## Resultado de cada operación

### F09-HIST

Origen: `salidas/fam09/hist`. Validación aceptada (recuento independiente
9.434). Comparación aceptada frente al libro rem138.

- Anexo e63ae329…; inventario b6ccab3d….
- 13.656 filas con 13.656 claves únicas.
- 9.434 preservadas (`FILAS_PRESERVADAS.jsonl` fbe05d07…). Por estado:
  computed 804, no_feasible_solution 2.059, not_identified 4.222,
  outside_support 1.359 y undefined_denominator 990. Las 4.222 filas por
  unidad son 2.111 λ y 2.111 de captura.
- 5.580 banderas históricas outside_support, sin incoherencias entre bandera
  y estado.

### F09-LAMBDA

Origen: `salidas/fam09/lambda`.

- `PRODUCTO_T8_LAMBDA.jsonl` **1b4881c3…**, idéntico al aceptado.
- `verificar_producto_lambda.py`: conforme, sin fallos.
- Iguales al libro rem138: 2.111 finalizadas (2.042 outside_support y 69
  computed), 68 cambios, 9.434 preservadas, 2.111 de captura pendientes; en
  total 11.545 definitivas.

### F09-CAPTURA

Origen: `salidas/fam09/captura`. Entrada: el λ nuevo (ENLACE-v1 registrado
en `ejecucion.json`).

- `VISTA_T8_CAPTURA.jsonl` **66891b45…**, idéntica a la aceptada.
- `verificar_captura.py`: conforme.
- Iguales al libro rem140: 2.071 resueltas (365 misma corrida, 563
  transferidas, 264 por 33/10, 879 por U) y 40 pendientes
  `SIN_PRUEBA_POR_FILA`.
- Procedencia: las 2.071 tienen tipo y huella de prueba y las cinco huellas
  (λ base = el nuevo, certificación, fuentes, plan y pruebas).
- Transición: cambian exactamente las 2.111 seleccionadas; 11.545 líneas
  idénticas; mismas claves y mismo orden.

### F09-TESTIGO — cálculo del techo (aparte de la emisión)

Origen: `salidas/fam09/testigo`. Supervisor:
`TESTIGO: estado=TERMINO rc=0 segundos=1.0 cpu_s=0.8 pico_memoria_job_MB=45.3 procesos_activos_al_terminar=0 limite_s=600.0`.

`RESULTADO.json` 31b5ec4e…, comparado con rem141 **después** del cálculo y
de su validación:

| Campo | Nuevo = rem141 |
|---|---|
| C2 | 0.7651580128158672 |
| sup_lower / sup_upper / sup_R | 8.416738140974505 / 8.41673834128583 / 8.416738140974532 |
| numerical_error_share (escala normalizada) | 1.8210118968298165e-08 |
| numerical_error_R (escala R) | 2.0031130865127964e-07 |
| B_pot | 10.999999999999991 |
| error_kind / computation_status | certified_bound / complete |
| converged / attained / sup_not_attained | true / true / false |
| tau_d_at_sup / tau_f_at_sup | 0.6 / 0.6 |
| final_n | 24 |
| Garantía (VALIDACION) | complete, cumple_garantia = true |

Diferencias, solo locales:
- **RESULTADO**: `inicio_utc`, `fin_utc`, `pared_s`,
  `evidencia_real.ejecutable` (ruta relativa del intérprete),
  `puerta.alcance_sha256` (la declaración local) y
  `puerta.ejecutado.{receta_testigo.sh, emitir_alcance_testigo.py}`, que no
  se ejecutan.
- **VALIDACION**: `validada_utc`, `resultado_sha256` y los mismos tres de
  `puerta_validador`.

### F09-TESTIGO — validación U36

- **Límite documentado** (catálogo, L-T8-TESTIGO-VALIDADOR, rem181): validar
  contra VALIDACION.json mientras no se localizara el validador.
- **Ejecutado hoy**: `validar_testigo.py` (69989e41…, copia exacta del
  testigo_alto_v3) **corre sin cambios** sobre los bytes nuevos. Rehace la
  puerta, las fijaciones del manifiesto v2 y las comprobaciones numéricas
  (encierro de C2 en sup_R / B_pot, error que cubre los dos extremos
  normalizados, cota inferior b64, módulos reales). Resultado: clase
  complete, garantía cumplida, sin fallos. Solo se adapta `testigo_comun`
  en puerta, rutas y procedencia; `comprobar_numeros`, `comprobar_modulos` y
  `clasificar` no se tocan. No es un cotejo de VALIDACION.json.
- **Alcance real de la U36** (control de pruebas): un C2 + 1 ulp queda dentro
  del encierro y la U36 lo **acepta**; lo rechaza la comparación exacta con
  rem141. La U36 garantiza la cota, no la identidad bit a bit.
- Tras validar, `fam09-validar` escribe el estado de la ejecución y el
  inventario de la entrega (`audit/entrega.json` 6d821d17…). El registro
  `testigo.validacion.json` (44acbf2d…) cita el inventario y el RESULTADO por
  su huella.

### F09-TESTIGO — emisión de las 35 filas (rem143/rem144)

Origen: `salidas/fam09/incorporacion`. Entradas: la captura nueva y el
testigo nuevo, cada uno con su registro.

1. `construir_incorporacion.py` → `INCORPORACION_TESTIGO.json` c7a3ab44…
   (fuente = la entrega local; dictamen = el registro de validación; sin
   decisión).
2. `lector_fuente_testigo.py` sobre esa fuente: 40 filas, 35
   `computed_candidato` y 5 pendientes (evidencia a151062c…).
3. Cobertura exacta independiente con la regla aceptada (C2_inf + err_inf ≤ v
   ≤ C2_sup − err_sup): inferior CEI:dc4e1ba9… =
   83037518495931418279937/151115727451828646838272; superior C2 − err =
   231254813940860032385023/302231454903657293676544. Cubre **las mismas 35**
   (6884 … 9686) y deja **las mismas 5** (7028, 7208, 8144, 8186, 9578), igual
   que el lector (`ACEPTACION_TESTIGO_FAM09.json` 0493de66…).
4. `materializar_t8_testigo.py` y `verificar_t8_testigo.py` (conforme): vista
   c24f9fab…, 13.651 definitivas y 5 pendientes; captura computed 963.
   Transición: cambian exactamente las 35; 13.621 líneas idénticas a la
   captura.
5. Frente a rem147: 13.616 líneas idénticas. Las 35 emitidas difieren solo en
   17 campos de vínculo, todos derivados exactamente de las salidas nuevas
   (incorporación, RESULTADO, inventario, declaración, evidencia, aceptación
   local, registro, `prueba_sha256` recalculada). `decision_origen_uuid` es
   null porque no hay decisión. Ninguna diferencia científica.

### F09-C5B

Origen: `salidas/fam09/c5b`. Entrada: la vista del testigo nueva y su
registro (que ocupa el ledger rem144).

- **Certificado reutilizado**: `CERTIFICADO_C5B_CANDIDATO.json` fc403d40… y
  `C5B_MASA_M2.json` 05c10ea6… (rem144), autenticados por su inventario. La
  derivación (guiones C3/M2) **no** se regenera; los guiones solo se
  autentican por huella.
- Regla `Fraction(v) > U_global_hi + banda`, aplicada por el código histórico
  (`desigualdad_c5b`): las cinco filas tienen holgura exacta positiva. El
  borde se probó aparte: en la igualdad no excluye.
- `verificar_t8_c5b.py`: conforme.
- Transición: cambian solo las cinco; 13.651 líneas idénticas a la vista del
  testigo.

## Vista final

- **Huella**: `salidas/fam09/c5b/producto/VISTA_T8_CAPTURA.jsonl`
  **3cf3d99d8fd51daba4ba85237af3d90a154913135cfc03cb6553230c323d8eb7**
  (rem147: 12826a05…).
- **Recuento desde las filas**: 13.656 filas y 13.656 claves; partición 9.434
  preservadas + 2.111 λ + 2.071 captura + 35 testigo
  (`pertenencia_testigo_alto`) + 5 C5B (`exclusion_cota_U_global`) = 13.656;
  0 pendientes. Las 35 y las 5 son exactamente las listas aceptadas.
- **Identidad de las preservadas**: 9.434/9.434 iguales a su fila del anexo
  (`historico`, `estado_sucesor` = `result_status`, `preservada`).
- **outside_support**: 5.580 banderas históricas y 4.549 estados vigentes.
  Las 1.031 filas que dejan outside_support son 963 de captura y 68 de λ;
  ninguna entra en outside_support.
- **Categorías**: las cinco originales del anexo (computed,
  no_feasible_solution, not_identified, outside_support,
  undefined_denominator). La exclusión del soporte conserva su significado.
- **Frente a rem147 por clave y contenido**: mismas claves; 13.616 líneas
  idénticas; 40 filas (las 35 y las 5) que difieren **solo** en estos 20
  campos de vínculo:
  - 35 filas: `captura_c2.procedencia.{incorporacion,aceptacion,dictamen,evidencia_filas}_sha256`,
    `captura_c2.procedencia.testigo_superior.{alcance_origen_sha256, decision_origen_uuid, fuente_base, fuente_inventario_sha256, resultado_sha256, run_origen}`,
    `captura_c2.prueba.testigo_superior_nuevo.{incorporacion_sha256, fuente_base, fuente_inventario_sha256, resultado_sha256, validacion_recalculada_sha256, run_origen}`
    y `captura_c2.prueba_sha256`;
  - 5 filas: `captura_c2.procedencia.{base_vista_sha256, base_vista_inventario_sha256, ledger_sha256}`.

  Cada vínculo se comprobó contra la huella del archivo nuevo al que apunta.
  La nueva corrida es `TRUN-b516d894043875a6c5919be6`.

## Controles (`local/pruebas_fam09.py`, `salidas/fam09/pruebas_01.json`: 25/25)

El techo no se recalcula en los controles. Las negativas se niegan antes de
calcular o actúan sobre copias reselladas de forma coherente.

- **Fila cambiada u omitida con el total conservado** (cada caso, rechazado
  por el verificador histórico de su etapa):
  - λ con las clasificaciones de dos filas permutadas;
  - captura con dos resoluciones de clase opuesta permutadas;
  - vista final con dos preservadas de categorías intercambiadas (también
    la señalan la transición y la comparación con rem147);
  - vista final con una fila omitida y otra duplicada, 13.656 líneas
    (transición: 1 omitida);
  - vista final con dos líneas permutadas (orden distinto).
- **Testigo ajeno o sin validar**: la emisión se niega sin crear carpeta con
  la validación de CAPTURA como registro del testigo, con la carpeta de
  captura como testigo, con un registro no aceptado y con un testigo cuyo
  RESULTADO cambió después de validarse (`PRODUCTO_CAMBIADO_DESPUES_DE_VALIDAR`).
  Un techo con C2 + 1 ulp pasa la U36 y la comparación exacta lo rechaza
  (diferencia científica en C2).
- **Borde estricto C5B** (en proceso, `desigualdad_c5b` del código):
  v = U_global_hi + banda no excluye; + 10^-60 excluye; − 10^-60 no. Las cinco
  filas finales tienen holgura positiva.
- **Entradas explícitas**: CAPTURA sin `--entrada`, o con HIST como λ, se
  niega sin carpeta.
- **Otra carpeta** (copia del paquete fuera de la base, mismo intérprete):
  - `fam09-comprobar` cumple;
  - HIST, LAMBDA y CAPTURA se regeneran, se validan y se aceptan;
  - la U36 corre en la copia sobre el cálculo guardado, sin recalcularlo;
  - INCORPORACION y C5B se aceptan;
  - la vista final de la copia (a6d9f75e…) tiene, por clave, 13.616 líneas
    idénticas a la del paquete. Las 40 emitidas difieren solo en 11 campos
    de vínculo, porque VERIFICACION.json y los registros llevan su hora y su
    duración.
- **Dependencias** (en la copia): con el `__init__.py` de lima1855 retirado,
  el anexo alterado, el certificado C5B retirado o `validar_testigo.py`
  retirado, `fam09-comprobar` no cumple y las nombra. TESTIGO, HIST, C5B y la
  validación se niegan sin salida (`DEPENDENCIA_AUSENTE_O_ALTERADA`).

**Comprobación final** (`salidas/fam09/comprobar_02.json`, después de todas
las correcciones): cumple; 276 piezas sin alteraciones, sustituciones 10/10,
declaración y pilotos conformes, referencias íntegras y receta de 20 pasos.
`comprobar.json` es anterior a la extracción final.

**Regresión breve** (`reproducir.py` es compartido): `revisar` y
`fam01-comprobar` … `fam08-comprobar` y `fam11-comprobar` terminan con código
0 y cumplen (`salidas/fam09/regresion_fam*_comprobar.json`).

**Saneado**: fuera de `salidas/fam09/lanzador/` (registro local del
supervisor) no hay rutas personales en `salidas/fam09`, `datos/fam09`,
`referencias/fam09`, `nucleo_s6/t8`, `src/fam09.py`,
`local/pruebas_fam09.py`, `fuentes_fam09.json` ni en la herramienta de
extracción.

## Tiempos medidos (pared, s)

| Etapa | Etapa | Validación | Comparación |
|---|---:|---:|---:|
| HIST | 0,27 | 0,41 | 0,01 |
| LAMBDA | 0,62 | 1,15 | 0,20 |
| CAPTURA | 1,25 | 2,28 | 0,75 |
| TESTIGO (supervisor: 1,0; trabajador: 0,43) | 0,44 | 0,31 (U36) | 0,00 |
| INCORPORACION | 1,76 | 1,63 | 1,02 |
| C5B | 1,01 | 1,20 | 1,41 |

Los controles completos tardaron 48,7 s, incluida la copia de otra carpeta.

## Correcciones rutinarias de esta sesión

- **Extracción idempotente**: al repetirse, `extraer_fam09.py` saltaba los
  archivos ya presentes sin anotarlos (8 lecturas «sin manifiesto»). Ahora
  decide por lo copiado en la misma corrida. Vuelve a dar 274 archivos y HIST
  se repitió.
- **Final normal = código 0**: `_ejecutar` daba rc = None cuando un guion
  terminaba sin `SystemExit`; LAMBDA se repitió. El producto ya era el mismo.
- **Criterio de transición de CAPTURA**: cambian las 2.111 seleccionadas, no
  solo las 2.071. Se añadió la comprobación de procedencia por resolución.
- **Saneado de la última línea**: una ruta escapada en JSON pasaba al
  registro de INCORPORACION. Se repitió la etapa con las mismas huellas.
- **Partición explícita** en la comparación final, recontada desde las filas,
  y conservación de las categorías.
- **Robustez de `fam09-comprobar`**: con una pieza del núcleo ausente lanzaba
  una excepción; ahora informa que no cumple. La primera corrida de los
  controles (24/25) dejó además una ruta privada recortada en su informe; se
  borró y `pruebas_01` se repitió con el saneado antes del recorte.

El techo alto se calculó **una sola vez**. Ninguna corrección lo afectó.

## Límites

- **L-T8**: las 14 corridas históricas no se recalculan; las 9.434 son
  insumo con integridad comprobada.
- **U36**: ver arriba. Valida la garantía, no la identidad bit a bit; la
  identidad la da la comparación con rem141.
- **C5B**: certificado y M2 reutilizados; no se regenera su derivación.
- **Puertas**: no se reconstruyen alcances v3 ni decisiones humanas. La
  declaración NO OFICIAL fija entradas, asignaciones y límites; la
  aceptación local y el registro de validación ocupan los papeles de los
  actos rem142/rem144 y **no son actos de Codex**.
- **Vínculos locales**: VERIFICACION.json (escrito por los verificadores
  históricos) y los registros llevan su hora. Por eso las huellas de vínculo
  de las 40 filas emitidas cambian en cada ejecución; el contenido científico
  no cambia.
- Todo en modo candidata, salvo el testigo (produccion con la declaración).
  No hay emisión oficial.

## Propuesta de cierre

Propongo cerrar la preparación de FAM09 en su alcance:
- las cinco operaciones conectadas en orden, cada una con validación
  histórica ejecutada y comparación aceptada;
- λ y captura idénticas byte a byte;
- techo alto recalculado una vez con los 15 campos científicos iguales a
  rem141, y la U36 ejecutada hoy;
- las mismas 35 y 5;
- vista final 3cf3d99d… sin diferencias científicas frente a rem147 y con
  los vínculos nombrados;
- 25/25 controles y regresión breve conforme.

No se declara reproducción completa (Paso 3). El dictamen corresponde a
Codex.

## Lo que falta

- Paso 3 (ejecución general con la receta) y aislamiento 2.4.2.
- FAM10 (síntesis Exp8) sigue pendiente; no se abrió.
- Si Codex lo pide: la derivación del certificado C5B (C3/M2) como
  regeneración aparte.

## Dictamen de Codex

El 18 de noviembre de 2026 cierro la preparación de FAM09 en el alcance de las cinco operaciones. Volví a ejecutar la comprobación del paquete y las seis comparaciones sobre los productos guardados. Las seis etapas quedaron aceptadas.

Contrasté las salidas directamente con el anexo T8 y los libros rem138, rem140, rem142, rem144, rem145 y rem147. Los productos λ y captura coinciden byte a byte con sus referencias. Comprobé la huella del validador U36 y su vínculo al RESULTADO del piloto. Los 15 campos científicos del techo coinciden exactamente. Al aplicar los extremos del testigo a los valores de las filas se recuperan las mismas 35 claves. Las otras cinco cumplen la desigualdad estricta del certificado C5B reutilizado.

La vista final tiene la huella 3cf3d99d8fd51daba4ba85237af3d90a154913135cfc03cb6553230c323d8eb7. Verifiqué el orden, las 13.656 claves únicas y el contenido histórico de cada fila. Frente a rem147, 13.616 líneas son idénticas. En cada una de las otras 40 comprobé los campos de vínculo aplicables contra los archivos locales y las huellas derivadas. Los valores científicos y las clasificaciones coinciden en las 13.656. El recuento independiente da 5.580 banderas históricas de fuera de soporte y 4.549 estados vigentes en esa categoría.

Esta revisión utilizó el cálculo guardado de un solo techo. El certificado C5B y las 9.434 filas preservadas siguen siendo insumos. Quedan pendientes la instalación aislada de 2.4.2 y la ejecución general del Paso 3.
