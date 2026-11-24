# RESULTADO FAM07 — COORD del lote 2 (variante B)

Fecha: 2026-11-16 (relojes de las salidas en UTC: 2026-11-17). Base:
`reproduccion_limpia` (sin commits). El original se consultó en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Cerrada en su alcance por Codex (2026-11-16). Están en el paquete el código COORD (cinco guiones, copias exactas), el núcleo C0 de FAM05, las entradas (manifiesto B, anexo, fuentes rem120), las referencias rem124 y la receta completa. Cálculo, validación, ensamblado y comparación están conectados. |
| F07-RECALCULO (RN) | Piloto L1-COORD-R1 (2 techos certificados y 16 comparaciones, la tarea histórica completa) calculado en 774,5 s de pared, validado (`completa_validada`) y aceptado: las 16 comparaciones son idénticas byte a byte a la referencia y los 2 techos son iguales salvo `segundos` y el vínculo `alcance_sha256`; con esos dos campos repuestos, los bytes reproducen el producto de referencia (fc31df89…). R2/R3 no se calcularon. |
| F07-REUTILIZADAS (VI) | Verificada sin cálculo: los 20 techos reutilizados (12 rem112 y 8 rem120) se autentican en su fuente y conservan `convergence_estimate`; ninguno se promueve ni se cuenta como recalculado. Las 1.502 comparaciones que dependen de ellos coinciden con las comparaciones rem120 dentro del ensamblado. |
| F07-PREVIAS-192 (VI) | Verificada sin cálculo: las 192 comparaciones previas (9de71ea1…) cuadran con las celdas del lote 1 y los techos rem112 (G = C2 − K1), y son disjuntas de las 1.532: 1.724 celdas declaradas sin duplicados. |
| Ensamblado | Regenerado sobre entradas guardadas (las tres tareas rem124 y las reutilizaciones autenticadas): 1.532 filas idénticas byte a byte a la referencia, con sus recuentos. No acredita F07-RECALCULO. El ensamblado de procedencia mixta (R1 nueva, R2/R3 guardadas) queda aceptado con las 1.532 comparaciones idénticas byte a byte; acredita la conexión de la tarea nueva, no que R2/R3 se hayan ejecutado. |
| Reproducción completa | Pendiente (Paso 3). R2 y R3 no se han calculado; la receta está preparada y no se ha lanzado. |

El piloto cubre 2 de los 6 techos recalculados y 16 de sus 30 comparaciones.
No acredita R2/R3 ni el resto del lote. COL-2024p queda fuera del universo
COORD, pendiente por ausencia de testigos y no NA. FAM07 no cubre ENF
(FAM08).

## Alcance

| Operación | Unidades | Referencia (catálogo) |
|---|---|---|
| F07-RECALCULO (RN) | 6 techos certificados, partición B en tres tareas de dos claves: L1-COORD-R1 (141cd6fb73fd5f82 N y 6f8e6a5a9bb213af G, 16 comparaciones), R2 (417758d2… y b7942a4f…, 12) y R3 (ee2fad1e… y 8ea5c3c2…, 2). | `resultado.json` y productos de cada tarea rem124 (b0985048…, d347d884…, 597ea131…); ensamblado `coord_techos_ensamblados.jsonl` (f1889ee6…) |
| F07-REUTILIZADAS (VI) | 20 techos reutilizados: 12 del lote 1 (rem112) y 8 de rem120, todos `convergence_estimate`, y las 1.502 comparaciones ensambladas que dependen de ellos. | `coord_comparacion_ensamblada.jsonl` (7e45e7e6…) |
| F07-PREVIAS-192 (VI) | 192 comparaciones previas aceptadas del lote 1, aparte de las 1.532. | `coord_comparacion.jsonl` rem112 (9de71ea1…) |

**Recuentos confirmados** desde el manifiesto B (108bf2ed…), el manifiesto
del lote 2 y los productos, sin calcular:
- 26 claves únicas: 6 recalculadas y 20 reutilizadas (12 rem112 + 8 rem120),
  disjuntas y con unión igual a las claves COORD; partición exacta en 2 + 2 + 2;
- 1.532 celdas únicas en el lote 2: 30 de las claves recalculadas (16 + 12 + 2)
  y 1.502 de las reutilizadas, ninguna de otra clave;
- las 30 celdas afectadas iguales a las del lote 2, con K1 y G padre
  autenticados en sus 30 filas padre (referencias de FAM01);
- 192 previas, disjuntas: 1.724 celdas declaradas;
- fuera del lote: COL-E2-2023.2024p (macro y micro), «pendiente (sin
  testigos), no NA», sin celdas en el lote.

## Ruta efectiva

- **Cálculo** (`fam07-unidad`): las sentencias de `tarea_lote.py` del paquete
  COORD (ffd44b60…) en modo `produccion`, ejecutadas desde sus bytes exactos.
  Cada techo pasa por `conexion_coord_cert.techo` (e5776de9…) con
  `model = RUN.provider_for(RUN.RunConfig())`: `ModeloTeorico` del núcleo C0,
  certificado en esta plataforma (`modelo_teorico_v2_2`,
  `ieee754_binary64_rn`), con la configuración fijada en el manifiesto.
  `frontier.capture_ceiling` queda sustituida por una función que falla.
  Se conservan el cierre normalizado 1e-7, los errores en las dos escalas,
  las cotas, los testigos, la garantía, el soporte y los estados. K1 se
  reutiliza sin cambio y G_coord = C2' − K1.
- **Validación** (`fam07-validar`): `validar_lote.py` (070ae81d…) con
  `validar_coord_rec.validar_tarea` (cc83b778…) sobre los bytes guardados:
  conjunto exacto de techos y comparaciones, garantía numérica con
  encierros, atribución por clave y vínculo de cada fila con su tarea, su
  manifiesto y su resultado.
- **Ensamblado** (`fam07-ensamblar`): `ensamblar_coord.py` (fcb40469…).
  Revalida cada tarea con `validar_tarea` y construye las 1.532 filas con
  `validar_ensamblado`: cada celda toma el techo de su clave, conserva K1 y
  aplica G = C2' − K1; las 1.502 reutilizadas se cotejan con las
  comparaciones rem120. Nunca lee el ensamblado de referencia.

## Extracción

`extraccion/extraer_fam07.py copiar <raíz original> [<libro rem125>
[<dictamen>]]` copia bytes exactos, comprueba los objetos del paquete y
rechaza rutas absolutas. Deja en `fuentes_fam07.json` 32 piezas propias:
- **código** (`nucleo_s6/coord/`): `tarea_lote.py`, `conexion_coord_cert.py`,
  `validar_lote.py`, `validar_coord_rec.py` y `ensamblar_coord.py`, copias
  exactas. Son los del paquete COORD, no los de ELAST con el mismo nombre;
- **entradas** (`datos/fam07/`): `MANIFIESTO_COORD_REC_B.json` (108bf2ed…),
  `COBERTURA_COORD_REC_B.json` (a4d8c58e…), `PAQUETE_COORD_REC.json`
  (644876a1…) y `alcance_coord_rec_B.json` (0555825f…; solo cruza huellas);
  las fuentes rem120 de los 8 reutilizados (`rem120/L1-COORD/salida/`:
  techos f6d24054… y comparaciones 6b6baca8…); `pilotos.json` y
  `ejecucion_limpia.json`, datos nuevos sin resultados;
- **referencias** (`referencias/fam07/rem124/`): las tres tareas
  (`resultado.json`, productos, salida de validación y del trabajo) y el
  ensamblado (`coord_comparacion_ensamblada.jsonl` 7e45e7e6…,
  `coord_techos_ensamblados.jsonl` f1889ee6…, `ensamblado_stdout.txt` y
  `ENSAMBLADO.json` en la proyección del catálogo, 962be1dc…, que restituye
  el original 4ef5820d… al reponer la raíz).

Declara 34 piezas **reutilizadas** sin copiarlas otra vez: el manifiesto del
lote 2 (FAM05), los techos y las 192 comparaciones rem112 y el manifiesto del
lote 1 (FAM04), y las 30 filas padre de las celdas afectadas (FAM01). El
**núcleo C0** es el de FAM05 (37 archivos, identidad d0bf5cd6…,
recalculada). Las fuentes rem112 eran los mismos bytes que las copias
existentes; las rem120 de COORD no estaban y se copiaron.

**Libro rem125 y dictamen.** Se usaron solo para localizar y entender las
fuentes; no se leen al ejecutar. `fuentes_fam07.json` guarda un resumen sin
rutas ni transcripciones, y `fam07-comprobar` coteja sus 14 recuentos y sus
productos con los archivos. **Rutas:** 0 rutas personales en las piezas.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1, bajo el supervisor del paquete
fuente:

```text
reproducir.py fam07-listar    --salida salidas/fam07/listar_01.json
reproducir.py fam07-comprobar --salida salidas/fam07/comprobar_02.json
reproducir.py fam07-unidad    --tarea L1-COORD-R1 --tope 2400 --salida salidas/fam07/piloto_01/L1-COORD-R1
reproducir.py fam07-validar   --nueva salidas/fam07/piloto_01/L1-COORD-R1 --salida salidas/fam07/piloto_01/L1-COORD-R1.validacion.json
reproducir.py fam07-comparar  --tarea L1-COORD-R1 --nueva salidas/fam07/piloto_01/L1-COORD-R1 --validacion salidas/fam07/piloto_01/L1-COORD-R1.validacion.json --salida salidas/fam07/piloto_01/L1-COORD-R1.comparacion_02.json
reproducir.py fam07-ensamblar --entrada L1-COORD-R1=guardado --entrada L1-COORD-R2=guardado --entrada L1-COORD-R3=guardado --salida salidas/fam07/regeneracion_01
reproducir.py fam07-comparar  --tarea ENSAMBLADO --nueva salidas/fam07/regeneracion_01 --salida salidas/fam07/regeneracion_01.comparacion.json
reproducir.py fam07-ensamblar --entrada L1-COORD-R1=salidas/fam07/piloto_01/L1-COORD-R1 --entrada L1-COORD-R2=guardado --entrada L1-COORD-R3=guardado --salida salidas/fam07/mixto_01
reproducir.py fam07-comparar  --tarea ENSAMBLADO --nueva salidas/fam07/mixto_01 --salida salidas/fam07/mixto_01.comparacion_02.json
reproducir.py fam07-receta    --salida salidas/fam07/receta_01.json
```

- **Sin cálculo científico**: `fam07-listar`, `fam07-comprobar`,
  `fam07-validar`, `fam07-ensamblar`, `fam07-comparar` y `fam07-receta`. El
  ensamblado es regeneración documental y aritmética (G = C2 − K1).
- **`fam07-unidad`**: una tarea entera de la partición (sus dos techos y sus
  comparaciones). Se niega antes de crear la carpeta si falta o cambió una
  dependencia o si el núcleo C0 no tiene su identidad. Exige
  `PYTHONHASHSEED=0` efectivo. Escribe `resultado.json` y `salida/` (los
  escribe el trabajador), `trabajo_stdout.txt`, `ejecucion.json` y
  `archivos_leidos.json`.
- **`fam07-ensamblar`**: cada tarea se declara con `--entrada
  <tarea>=<carpeta de fam07-unidad|guardado>`. `guardado` es la tarea
  aceptada rem124, autenticada por su huella del catálogo. Una tarea sin
  entrada no se sustituye por su referencia: el ensamblador la rechaza. La
  salida declara su naturaleza: «regeneración sobre entradas guardadas»,
  «procedencia mixta» o «ensamblado sobre salidas nuevas».
- **Separación**: cálculo, validación, ensamblado y comparación son pasos
  aparte; cada uno termina con 0 solo en su caso aceptado.

## Adaptaciones (declaradas en `src/fam07.py`)

No cambian fórmulas, claves, tolerancias, presupuestos ni criterios. Los
cinco guiones se ejecutan desde sus bytes exactos con estas sustituciones de
texto, cada original presente una sola vez:
- **GUION-v1**: ejecución desde `nucleo_s6/coord` con `__file__` en esa
  carpeta, de modo que el código que registra el trabajador y el que exige el
  validador son esos mismos bytes. `validar_coord_rec` se carga desde su
  texto adaptado antes de que lo importen los demás.
- **NUCLEO-C0-v1** (de FAM05): el núcleo es `nucleo_s6/c0`;
  `aprobacion_alcance.identidad_instalacion` la sirve el módulo mínimo de
  FAM05.
- **RUTAS-FUENTES-v1**: el validador lee cada fuente de su ruta en la base
  limpia (tabla de cuatro rutas históricas) y la sigue autenticando por sus
  bytes; una ruta no declarada da FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA.
- **RAIZ-v1**: la raíz del trabajador es la base limpia (solo la usa el modo
  `hasta-seleccion`, que aquí no se ejecuta).
- **PUERTA-v1**: la puerta de producción (alcance v3 verificado y decisión
  humana nativa) no se ejecuta ni se reconstruye. El campo `alcance_sha256`,
  que el validador exige a un resultado real, lleva el sha256 de
  `datos/fam07/ejecucion_limpia.json`, una declaración NO OFICIAL que no es
  un alcance ni una decisión. Las comparaciones tratan ese campo como
  vínculo y lo comprueban en cada lado contra sus propios bytes.
- **ENSAMBLADOR-ENTRADAS-v1**: el ensamblador recibe una carpeta declarada
  por tarea y una salida explícita, y registra directorio y lanzamiento
  relativos a la base (el original guardaba rutas absolutas).
- **RELOJ-PILOTO-v1** (de FAM05): reloj interno = 2400 − 120 = 2280 s, el
  `tope_efectivo_s` histórico; el límite externo lo pone el supervisor.

## Comprobación (`fam07-comprobar`, sin cálculo; 0,27 s)

Cumple en todos sus apartados (`comprobar_01.json`; con el código final, `comprobar_02.json`, y tras actualizar el catálogo, `comprobar_03.json`):
- 32 piezas propias, 34 reutilizadas y 37 del núcleo C0 con sus huellas;
  identidad C0 recalculada igual a d0bf5cd6…;
- procedencia: código igual al índice del paquete y al alcance; manifiesto,
  anexo e identidad C0 iguales al alcance; alcance igual al catálogo;
  manifiesto y alcance no oficiales; variante B; sustituciones únicas;
  declaración de ejecución limpia igual a su regla;
- motor, sin calcular: identidad de código, configuración del proveedor,
  certificación en esta plataforma y garantía iguales a las del manifiesto;
  `tol_converge` 1e-7;
- cobertura, reutilizaciones y previas, con los recuentos de «Alcance»;
- referencias: las tres tareas y el ensamblado iguales al catálogo, con
  1.532 filas (30 recalculadas y 1.502 reutilizadas) y 6 techos;
- revalidación de las tres tareas guardadas: `completa_validada`, igual a la
  validación histórica;
- 14 recuentos y productos del libro rem125 iguales a los archivos; pilotos
  iguales a su regla; receta de 5 pasos.

## Comparación (COMPARACION-FAM07-v1)

Mismo perfil de entorno y mismo núcleo C0 que la referencia rem124, así que
la comparación es exacta:
- **CR-HASH-CANONICO**: cada fila idéntica campo a campo (valores, cotas,
  errores en las dos escalas, testigos, niveles, configuración);
- **CR-DISCRETOS**: claves, celdas, estados, `error_kind`, garantía, cierre
  por escala, motivo, `final_n` y conteos, con precedencia.

En los techos se apartan, visibles, solo dos campos: `segundos` (OPERATIVO,
tiempo de pared del techo) y `alcance_sha256` (VINCULO: en la nueva, la
declaración de ejecución limpia; en la referencia, el alcance histórico; cada
uno comprobado contra los bytes de su lado). La huella derivada repone esos
dos campos desde la referencia y debe reproducir los bytes del producto de
referencia. Las comparaciones dependientes se exigen idénticas byte a byte.
Además se revisan cobertura, certificados (completo, `certified_bound`,
`ieee754_binary64_rn`, error normalizado ≤ 1e-7, cierre en la escala
normalizada), G = C2' − K1 por celda e identidades. La tolerancia interna del
validador es suya y no se usa como tolerancia de reproducción.

## Piloto de F07-RECALCULO (cálculo autorizado)

**Selección**: fijada por el encargo antes de calcular, en `datos/fam07/pilotos.json`
(2cec212a…): la tarea histórica completa L1-COORD-R1, primera de la
partición B, con las claves 141cd6fb73fd5f82 (N, df, 8 celdas) y
6f8e6a5a9bb213af (G, df, 8 celdas). No se redujo el problema.

**Lanzamiento**: `fam07-unidad --tarea L1-COORD-R1 --tope 2400` bajo el
supervisor, con límite externo de 2400 s y reloj interno de 2280 s (el
`tope_efectivo_s` histórico). Fue el único proceso de cálculo; la receta
(sin cálculo, 0,2 s) se emitió mientras corría.
- Supervisor: TERMINO, código 0, 774,5 s de pared, 771,2 s de CPU, 276,9 MB
  de memoria pico del Job y 0 procesos activos al terminar.
- Trabajador: `completa`, sin motivo; 773,1 s de cálculo.

**Techos** (ambos `complete`, `certified_bound`, `ieee754_binary64_rn`,
cierre en R y en la escala normalizada):

| Clave | Diseño | C_2 | error normalizado | error en R | final_n | s (histórico) |
|---|---|---|---|---|---|---|
| 141cd6fb73fd5f82 | N | 0.0016060650647440795 | 4,51e-8 | 8,28e-8 | 5.186 | 395,1 (692,3) |
| 6f8e6a5a9bb213af | G | 0.001609511873008437 | 4,95e-8 | 9,08e-8 | 5.078 | 377,9 (367,4) |

Los valores, las cotas, los errores, los testigos, los niveles y la
configuración son exactamente los de rem124. Los tiempos son antecedentes y
no una estimación: el primer techo tardó 297 s menos que en la referencia.

**Validación** (`L1-COORD-R1.validacion.json`, 0,08 s): `completa_validada`,
sin fallos. El veredicto es igual al histórico salvo las huellas propias de
los bytes validados.

**Comparación** (`L1-COORD-R1.comparacion_02.json`): aceptada.
- `coord_comparacion_rec.jsonl`: 16 filas, mismo orden y líneas idénticas;
  711d6211…, igual a la referencia. G = C2' − K1 en las 16, con el techo
  completo de su clave y K1 sin cambio.
- `coord_techos_rec.jsonl` (d8e0b099…): 2 filas, 0 diferencias discretas y
  0 numéricas. Apartados y visibles: `segundos` (2 filas) y `alcance_sha256`
  (2 filas ligadas en cada lado: la declaración de ejecución limpia
  717cd955… en la nueva y el alcance histórico 0555825f… en la referencia).
  Huella derivada, con esos dos campos repuestos y la serialización del
  trabajador: fc31df89…, igual a los bytes del producto de referencia.
- Resultado igual en tarea, modo, `sintetico`, estado, motivo y
  `tope_efectivo_s`; identidades de manifiesto, código, núcleo C0 y
  producto de comparaciones iguales; 2 de 2 techos certificados y cerrados;
  cobertura exacta de claves y celdas.

**Lecturas reales** (`archivos_leidos.json`): 47 archivos del paquete (37
del núcleo C0 y los 5 guiones COORD, cuyas huellas se comprueban antes de
calcular), 0 fuera del paquete y del intérprete, 0 sin declarar y ninguna
referencia ni fuente de reutilizados. `paper2b` se cargó de
`nucleo_s6/c0/src/paper2b` (identidad d0bf5cd6…); fuera de la biblioteca
estándar solo numpy 2.0.2. Entorno `.venv-fam01` conforme; F2 se informa
(equivalente) y no se extiende a FAM07 ni la necesita su regla.

## Reutilizaciones y comparaciones previas (sin cálculo)

- **F07-REUTILIZADAS**: `validar_coord_rec.reutilizados_autenticados`, con
  las fuentes de la base limpia, devuelve 20 filas y ningún fallo: 12 de
  rem112 y 8 de rem120, todas completas y `convergence_estimate`. Su error
  almacenado es 0 en las 20; no se promueven a `certified_bound` por eso ni
  por estar aceptadas, y no se cuentan como recalculadas. Las fuentes se
  autentican por sus bytes antes de leerlas.
- **F07-PREVIAS-192**: las 192 filas (9de71ea1…, igual al catálogo y al
  manifiesto) cubren exactamente las 192 celdas del lote 1; en todas, K1, G
  padre, C2 y estado cuadran con el lote 1 y los techos rem112, y G = C2 − K1.
  Son disjuntas de las 1.532 (1.724 celdas declaradas).

## Ensamblado

**Regeneración sobre entradas guardadas** (`regeneracion_01`): las tres
tareas rem124 guardadas, autenticadas por su huella, con las reutilizaciones
y el manifiesto del lote 2. El ensamblador revalidó las tres tareas y dio
`completa_validada`: 1.532 filas (30 recalculadas y 1.502 reutilizadas), 0
con techo incompleto y G = C2 − K1 en las 1.532; las 192 previas siguen
disjuntas (1.724) y los dos conjuntos COL-2024p siguen fuera. Los dos
productos son idénticos byte a byte a la referencia (7e45e7e6… y f1889ee6…);
`ENSAMBLADO.json` no tiene diferencias salvo directorio y lanzamiento de cada
tarea (rutas relativas en la nueva, raíz histórica en la referencia), que se
muestran. El veredicto del ensamblador es igual al histórico. Leyó 60
archivos del paquete, 0 fuera, ninguno sin declarar y no el ensamblado
esperado. Esta regeneración no acredita F07-RECALCULO.

**Procedencia mixta** (`mixto_01`): R1 = la salida nueva del piloto
(`salidas/fam07/piloto_01/L1-COORD-R1`), R2 y R3 = tareas guardadas rem124.
La salida lo declara («procedencia mixta (tareas nuevas y tareas
guardadas)») y dice qué acredita: la conexión de la tarea nueva al
ensamblador; R2/R3 no se han ejecutado aquí.
- El ensamblador revalidó las tres tareas y dio `completa_validada`: 1.532
  filas (30 recalculadas y 1.502 reutilizadas), 0 incompletas, G = C2' − K1
  en las 1.532, previas disjuntas (1.724) y COL-2024p fuera.
- `coord_comparacion_ensamblada.jsonl`: idéntico byte a byte (7e45e7e6…).
  Las 16 filas que dependen de R1 salen del techo nuevo y coinciden.
- `coord_techos_ensamblados.jsonl` (3522069c…): 6 filas sin diferencias
  discretas ni numéricas. En las de R2/R3 también `segundos` es idéntico; en
  las 2 de R1 solo difieren `segundos` y el vínculo `alcance_sha256`
  (ligado en cada lado). La huella derivada es f1889ee6…, igual a los bytes
  de la referencia (`mixto_01.comparacion_02.json`).
- `ENSAMBLADO.json`: 0 diferencias. Los vínculos de R1 (`resultado_sha256`,
  producto de techos y alcance) y el del producto de techos ensamblados se
  comprueban contra los bytes de cada lado; directorio y lanzamiento se
  muestran aparte.
- Leyó 57 archivos del paquete, 0 fuera y 0 sin declarar; no leyó el
  ensamblado esperado ni la tarea R1 de referencia (0,09 s).

## Controles (`local/pruebas_fam07.py`, sin cálculo científico)

`controles_02.json`: 29/29 conformes en 9,7 s, con las copias alteradas en
`salidas/fam07/controles_02`. Cada copia recalcula la huella y el recuento
de su `resultado.json`, para que el control llegue al criterio y no se quede
en la autenticación de bytes. Por riesgo:
- **Valor o cota alterados**: C_2 + 1 ulp con sus comparaciones recompuestas
  da DIFERENCIA_NUMERICA en la comparación exacta (la validación se informa
  aparte: decide con sus encierros, que no son tolerancia de reproducción).
  Una cota superior con semiancho de dos veces el error declarado da
  COTA_NO_RESPALDA_EL_VALOR en la validación y no se acepta en la
  comparación.
- **Garantía falsamente elevada**: un techo `certified_bound` con error 0 en
  las dos escalas da COTA_NO_RESPALDA_EL_VALOR (la etiqueta no basta); uno
  completo con `convergence_estimate` da COMPLETO_SIN_COTA_CERTIFICADA. Dos
  reutilizados declarados `certified_bound` o `certificado` dan
  REUTILIZADO_PROMOVIDO_O_SIN_GARANTIA_ORIGINAL.
- **Control positivo**: los 20 reutilizados con `convergence_estimate` y
  error almacenado 0 se aceptan desde sus fuentes autenticadas, sin fallos y
  sin contarse como recalculados.
- **Clave o celda omitida o duplicada**: un techo y sus 8 comparaciones
  omitidos (COBERTURA_DE_TECHOS y COMPARACIONES_NO_CORRESPONDEN); una
  comparación duplicada (duplicadas 1); en el ensamblado, una celda omitida
  (1.531 de 1.532), una duplicada (CELDA_DUPLICADA_EN_EL_MANIFIESTO) y una
  clave reutilizada aportada además como recalculada
  (TECHO_DUPLICADO_ENTRE_FUENTES).
- **Referencia o validación equivocada**: el piloto comparado con R2, con
  la validación de otra carpeta (VALIDACION_DE_OTROS_BYTES) o con una
  referencia alterada (REFERENCIA_ALTERADA_O_AJENA); en el ensamblado, el
  resultado de R2 en la carpeta de R1 (RESULTADO_DE_OTRA_TAREA_EN_SU_DIRECTORIO),
  R1 incompleta (TAREA_NO_VALIDA_EN_EL_ENSAMBLADO: RESULTADO_NO_COMPLETO), R1
  sin entrada (TAREA_SIN_SALIDA_UNICA: no se sustituye por su referencia),
  una tarea guardada alterada (se niega sin crear carpeta) y una fuente con
  ruta no declarada (FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA en los 8
  reutilizados afectados).
- **Otra carpeta y dependencia ausente**: copia fuera del paquete con el
  mismo intérprete. `fam07-comprobar` cumple; el piloto guardado se valida y
  se acepta; la regeneración da los mismos bytes y el ensamblado mixto se
  acepta, todo sin cálculo. Sin `conexion_coord_cert.py`,
  `validar_coord_rec.py` o la fuente rem120 de techos, `fam07-comprobar` no
  cumple e informa la pieza ausente, y `fam07-unidad`, `fam07-validar` y
  `fam07-ensamblar` se niegan antes de calcular, validar o ensamblar
  (DEPENDENCIA_AUSENTE_O_ALTERADA), sin crear salida.

El guion de controles se ejecutó fuera del supervisor, como en FAM06, y no
contiene cálculo científico. **Regresión breve** (`reproducir.py` es
compartido): `revisar` y `fam01-comprobar` a `fam06-comprobar` cumplen con
código 0 (`regresion_fam0*_comprobar.json`).

## Tiempos medidos

| Invocación | Pared (s) | CPU (s) | Memoria pico del Job (MB) |
|---|---|---|---|
| `fam07-unidad` L1-COORD-R1 (piloto; techos 395,1 + 377,9) | 774,5 | 771,2 | 276,9 |
| `fam07-validar` del piloto | 0,3 | 0,2 | 30,1 |
| `fam07-comparar` del piloto | 0,2 | 0,2 | 30,0 |
| `fam07-ensamblar` regeneración / mixto | 0,4 / 0,4 | 0,4 / 0,2 | 32,1 / 33,1 |
| `fam07-comparar` del ensamblado | 0,3 | 0,2 | 30,1 |
| `fam07-comprobar` (final) | 0,5 | 0,4 | 33,9 |
| controles (29, fuera del supervisor) | 9,7 | — | — |

Referencia histórica de L1-COORD-R1: 1.060,0 s de pared (692,3 + 367,4 s
por techo); R2 921,8 s y R3 724,1 s. Son antecedentes, no estimaciones. El
resumen sin rutas está en `salidas/fam07/lanzador.txt`.

## Correcciones rutinarias de esta sesión

- `fam07-listar` se lanzó antes de la extracción y falló por falta del
  manifiesto: se extrajo, se repitió `fam07-listar` (que fija `pilotos.json`
  y `ejecucion_limpia.json`) y se volvió a extraer para registrarlos.
- La comprobación de G en `fam07-comparar` podía fallar con un C2 nulo: se
  añadió `g_ok`, que exige techo completo y valores binary64 antes de
  recomponer G.
- La huella derivada de los techos se comparaba con una reserialización en
  LF y no con los bytes del producto de referencia, que el trabajador
  escribe en modo texto (CRLF en Windows). Ahora usa el fin de línea de los
  bytes nuevos y se compara con los bytes de la referencia: fc31df89…, igual.
  La comparación se repitió sin recalcular (`comparacion_02`). La primera
  (`comparacion.json`) dio el mismo veredicto y se conserva.
- En el ensamblado mixto se añadió la misma huella derivada a los techos
  ensamblados (`mixto_01.comparacion_02.json`, f1889ee6…, igual).
- `fam07-comprobar` se interrumpía con FileNotFoundError si faltaba un
  guion COORD, en lugar de informar la pieza, y el mensaje llevaba una ruta
  absoluta. Ahora no cumple, lista la pieza y registra la interrupción sin
  rutas; `reproducir.py` resume ese caso. La primera corrida de controles,
  que aceptaba esa excepción y guardaba dos rutas privadas, se retiró. Los
  controles se repitieron en `controles_02` con la condición estricta.
- Ningún cambio tocó el cálculo: el piloto no se repitió.

## Límites

- Solo L1-COORD-R1 tiene cálculo nuevo. R2/R3 no se calcularon; en el
  ensamblado mixto entran como tareas guardadas y no se acreditan.
- La puerta de producción histórica no se reproduce (PUERTA-v1); la
  ejecución limpia no es una producción oficial.
- Los registros del supervisor (`lanzador/*.tarea.json`) guardan rutas
  absolutas de esta máquina; `lanzador.txt` es el resumen sin rutas.
- El aislamiento real queda pendiente en 2.4.2. FAM08 no se ha abierto.

## Receta completa (preparada, no ejecutada)

`receta_01.json`: comprobar → L1-COORD-R1 → R2 → R3 (cada una con
`fam07-unidad`, `fam07-validar` y `fam07-comparar`) → ensamblado con las tres
carpetas nuevas y su comparación. Una tarea a la vez, sin reintentos, límite
externo de 2400 s por tarea (reloj interno 2280 s) y 300 s de validación; si
una tarea no queda completa, validada y aceptada, no se lanza la siguiente ni
se ensambla. Una tarea faltante no se sustituye por su referencia. Cubre 6
techos nuevos y 30 comparaciones, 20 reutilizados, 1.532 comparaciones
ensambladas y las 192 previas aparte. No se estima su duración.

## Propuesta de cierre

Propongo cerrar la **preparación** de FAM07 en su alcance:
- las tres operaciones (F07-RECALCULO, F07-REUTILIZADAS y F07-PREVIAS-192)
  están conectadas, con sus entradas y referencias completas en el paquete
  y 0 rutas personales;
- el código COORD específico se ejecuta desde sus bytes con siete
  adaptaciones declaradas que no cambian la ciencia, y el núcleo C0 de
  FAM05 se reutiliza;
- el piloto y los 29 controles son conformes y la receta completa está
  disponible, sin lanzar.

Distinción de lo que acredita cada parte:
- **Cálculo realmente comprobado**: solo L1-COORD-R1, 2 de los 6 techos y
  16 de las 30 comparaciones dependientes, exacto frente a rem124.
- **Verificación sin cálculo**: los 20 reutilizados, con su garantía
  `convergence_estimate`, y las 192 previas.
- **Regeneración sobre entradas guardadas**: el ensamblado de 1.532 filas,
  idéntico byte a byte; no acredita F07-RECALCULO.
- **Procedencia mixta**: la conexión del piloto al ensamblador; no acredita
  R2/R3.
- **Preparación sin ejecución**: R2, R3 y el ensamblado sobre tres salidas
  nuevas (Paso 3).

No hay faltantes de implementación conocidos para la receta. La ruta de
comparación con tres tareas nuevas es la misma que se probó con una, pero no
se ha ejercitado con tres: requiere el cálculo de R2/R3.

## Siguiente trabajo

- Preparación revisada y cerrada en alcance por Codex (véase abajo).
- R2, R3 y el ensamblado sobre salidas nuevas pertenecen al Paso 3.
- El aislamiento efectivo de FAM07 queda para 2.4.2.
- FAM08 (ENF) no se abre sin encargo.

## Revisión de Codex — 2026-11-16

Preparación de FAM07 cerrada en su alcance, sin hallazgos bloqueantes.
Se acepta el piloto L1-COORD-R1, las verificaciones de reutilizaciones y
previas, y los ensamblados guardado y mixto con sus límites declarados.

Se revisaron las adaptaciones, la ruta de cálculo certificado, la
validación y las comparaciones. El cotejo independiente sobre archivos
guardados comprobó las 32 fuentes propias, las 34 reutilizadas y los 37
archivos de C0 contra sus huellas y la identidad fijada de su inventario.

Los dos techos del piloto coinciden en todos los campos salvo el tiempo y
el vínculo de alcance, comprobado contra la declaración limpia y el
alcance histórico respectivamente. Conservan cotas, errores, testigos,
configuración y garantía certificada. Las 16 comparaciones son idénticas
byte a byte. Una nueva validación y comparación del piloto dieron aceptación,
sin repetir el cálculo del modelo.

Desde los manifiestos y las fuentes se cotejaron las 1.532 filas de cada
ensamblado y las 192 previas: claves y celdas completas, K1 y G padre
conservados, y G = C2' − K1 recompuesto en las 1.724 celdas. Las previas
son disjuntas. Los 20 techos reutilizados coinciden con sus fuentes y
conservan convergence_estimate; las 1.502 comparaciones que dependen de
ellos coinciden con rem120. Las dos exclusiones COL-2024p permanecen.

El ensamblado guardado conserva ambos productos históricos byte a byte.
El mixto conserva las 1.532 comparaciones y declara R1 nueva y R2/R3
guardadas; ambas comparaciones vuelven a dar aceptación. Se revisaron los
29 controles guardados y sus motivos, sin repetir la batería general.

Evidencia de revisión: `local/revision_codex_fam07/resumen.json`. No se
modificaron código, entradas, referencias ni salidas del ejecutor. Quedan
el cálculo de R2/R3 y el ensamblado con las tres tareas nuevas (Paso 3), y
el aislamiento real (2.4.2). Los registros privados del supervisor siguen
fuera de los archivos destinados a distribución. No se extiende F2 ni se
abre FAM08 en esta revisión.
