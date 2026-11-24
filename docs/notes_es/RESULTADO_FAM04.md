# RESULTADO FAM04 — lote 1 (ELAST, LAMBDA y COORD)

Fecha: 2026-11-16. Base: `reproduccion_limpia` (sin commits). El original se
consultó en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Cerrada en su alcance por Codex (2026-11-16). Entradas, referencias, cobertura y receta del lote completo presentes. Cálculo, validación y comparación conectados. |
| Pilotos | Tres pilotos calculados, validados (`completa_validada`) y aceptados por la comparación con líneas idénticas a la referencia: una frontera ELAST, un conjunto LAMBDA con ambas variantes y una clave COORD con su techo y sus comparaciones. |
| Reproducción completa | Pendiente (Paso 3). El lote no se ha ejecutado; la receta está preparada y no se ha lanzado. |

Los pilotos cubren:
- 25 de los 70 nodos ELAST (1 de las 6 fronteras);
- 2 de las 4 filas LAMBDA (1 de los 2 conjuntos; 36 de las 72 llamadas a
  `macro.bridge`);
- 1 de los 12 techos COORD y 16 de las 192 comparaciones.

No acreditan el resto del lote. FAM04 no cierra FAM05 ni FAM07.

## Alcance

No se deben confundir unidades, filas y llamadas:

| Tarea | Unidades | Productos de la referencia rem112 |
|---|---|---|
| L1-ELAST | 6 fronteras (clave `diseño\|j`): G\|d, G\|f, N\|d y N\|f con 5 nodos cada una; G\|df y N\|df con 25 (`frontier_n = 4`). Total 70 nodos. | `frontier_result.jsonl`, 70 filas: una `point` por nodo y laterales solo si hay kink (en este lote no hay ninguno) |
| L1-LAMBDA | 2 conjuntos (PER-E1.macro y PER-E1.micro) × variantes con/sin. Cada conjunto tiene 9 estados nacionales (`NationalState`, iguales para todo ω). | `lambda_envolvente.jsonl`, 4 filas; 72 llamadas a `macro.bridge` (9 estados × testigo de máximo y de mínimo × 2 variantes × 2 conjuntos) |
| L1-COORD | 12 claves transformadas (escenario COORD-HALF: η_f/2 y φ/2) y 192 celdas padre, 16 por clave | `coord_techos.jsonl`, 12 techos C2′; `coord_comparacion.jsonl`, 192 filas `G_COORD = C2′ − K1` frente a `G_padre` |

La referencia ELAST tiene `reason_code` BASE_NONPOSITIVE en 35 filas,
SP_LIMIT_AT_ZERO_RATE en 15 y ninguno en 20.

**Cobertura nacional.** `COBERTURA_NACIONAL_LOTE1.json` es el anexo del
manifiesto:
- `kind = cobertura-nacional-lote1`;
- `manifiesto_sha256` igual al del manifiesto (19ecd7d3…);
- preparado hasta la selección, con 0 llamadas a `macro.bridge` y a
  `strict_vertices`.

El alcance y el paquete fijan su huella (268a63d5…). `validar_lote` exige
que la evidencia de cada fila LAMBDA tenga, en orden, exactamente los 9
estados del anexo, en el máximo y en el mínimo.

**COORD.** Fuera del lote queda la clasificación de afirmaciones sobre
todo el Ω COORD, que exigiría elegir testigos en el soporte COORD; es
alcance de FAM07.

## Ruta efectiva

La de `tarea_lote.py` en producción:
- **ELAST**: `calc_elast` → `conexion_frontera.filas_frontera` →
  `model.frontier_grid` con `RunConfig().frontier_n = 4`.
- **LAMBDA**: `proveedor_real` (contexto S6; usa solo
  `ctx.inp.national`) → `calc_lambda` → `conexion_lambda.envolvente`, con
  `macro.bridge` sobre los estados nacionales.
- **COORD**: `calc_coord` → `supremum.capture_ceiling(st, diseño, j,
  tau_d_upper, tau_f_upper, True, cfg.sup)` por clave, y `G_COORD = C2′ −
  K1` en cada celda padre.
- **Productos y cierre**: `producto` y `fin` dan el esquema de
  `resultado.json` y las condiciones de «completa» o «incompleta».

La validación es `validar_lote.py`, en modo `produccion` y con el anexo
nacional. Revisa:
- el esquema, el recuento y la huella de cada producto;
- en ELAST, la cobertura de nodos, las identidades R, CS y s_P (con su
  tolerancia interna T1) y los motivos de auditoría;
- en LAMBDA, la identidad K1/Q = 1/(λ·g), el vértice de cada testigo, θ_W y
  la cobertura nacional exacta;
- en COORD, los techos de la selección, las celdas padre del manifiesto y
  la identidad `G_COORD`.

## Extracción

`extraccion/extraer_fam04.py copiar <raíz original>` copia exactos 19
archivos. Su relación con origen, huella y papel está en
`fuentes_fam04.json`, sin rutas absolutas:
- **código** (`nucleo_s6/lote1/`): `tarea_lote.py` (331a23c9…),
  `conexion_lambda.py` (bc498b81…) y `conexion_frontera.py` (cac8b7ec…),
  que son U11, y `validar_lote.py` (d12d3e76…), U12. Proceden del lote de
  la entrega rem111;
- **entradas** (`datos/fam04/`): `LOTE1_MANIFIESTO.json` (selección rem109;
  no se re-ejecuta), `COBERTURA_NACIONAL_LOTE1.json`, `PAQUETE_LOTE1.json`
  y `alcance_lote1.json`. Los dos últimos solo cruzan huellas; ninguno es
  una puerta;
- **referencias** (`referencias/fam04/rem112/<tarea>/`): `resultado.json`,
  la salida de validación y los productos de la ejecución aceptada rem112.
  Los cuatro productos son byte a byte los objetos del catálogo F04-LOTE1;
- `datos/fam04/pilotos.json`, dato nuevo de esta base (sin resultados).

Se comprueba además:
- **núcleo**: el `paper2b` de la instalación (FAM01) es 37/37 igual al del
  candidato rem107 que exigen el trabajador y el validador;
- **filas padre**: las 192 de COORD ya estaban en
  `referencias/fam01/originales` por FAM01. Se autentican por la huella
  `filas_sha256` del manifiesto y por su K1 y G, sin copiarlas otra vez. En
  un caso (ac29c74f…) FAM01 copió los mismos bytes desde otra carpeta de la
  misma entrega; se registra en `otra_ruta`.

Las 19 piezas no contienen rutas personales.

## Entradas reutilizadas y regeneradas (F1)

- **Se reutiliza**:
  - la selección del lote (el manifiesto; no se vuelve a seleccionar);
  - el anexo de cobertura nacional;
  - el K1 de cada celda padre, que no cambia con η_f ni φ, y su `G_padre`
    histórico, con el que se contrasta;
  - el núcleo, D7, contratos y datos nacionales de FAM01.
- **Se genera de nuevo**:
  - las filas de las 6 fronteras;
  - las 4 envolventes λπ (72 llamadas a `macro.bridge`);
  - los 12 techos C2′ (un techo histórico no sustituye a uno recalculado:
    cada techo C2′ es nuevo por clave y se calcula);
  - las 192 comparaciones.
- **Solo para comparar**: los productos y resultados rem112. Durante el
  cálculo de los pilotos no se leyó ninguna referencia.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1. Siguen el patrón listar /
comprobar, unidad, validar, comparar y receta:

```text
reproducir.py fam04-listar    --salida salidas/fam04/listar_02.json
reproducir.py fam04-comprobar --salida salidas/fam04/comprobar_02.json
reproducir.py fam04-unidad    --tarea L1-ELAST --unidad FRN:09c72876468fe62aaf395071c1c2825d22435ff9 --salida salidas/fam04/pilotos_03/L1-ELAST
reproducir.py fam04-validar   --nueva salidas/fam04/pilotos_03/L1-ELAST --salida salidas/fam04/pilotos_03/L1-ELAST.validacion.json
reproducir.py fam04-comparar  --tarea L1-ELAST --nueva salidas/fam04/pilotos_03/L1-ELAST --validacion salidas/fam04/pilotos_03/L1-ELAST.validacion.json --salida salidas/fam04/pilotos_03/L1-ELAST.comparacion.json
reproducir.py fam04-receta    --salida salidas/fam04/receta_01.json
```

- **Sin cálculo científico**: `fam04-listar`, `fam04-comprobar`,
  `fam04-validar`, `fam04-comparar` y `fam04-receta`.
- **`fam04-unidad`**: sin `--unidad` calcula la tarea completa; con
  `--unidad`, una unidad completa.
  - Se niega antes de crear la carpeta si falta o cambió una dependencia,
    o si una fila padre de COORD no se autentica.
  - Exige `PYTHONHASHSEED=0` efectivo.
- **Separación**: cálculo, validación y comparación son pasos aparte, y
  cada uno termina con 0 solo en su caso aceptado.

`fam04-comprobar` da `cumple` en 0,35 s. Comprueba:
- las 19 fuentes;
- la procedencia: código, validador, manifiesto y anexo iguales al alcance
  y al paquete; anexo ligado al manifiesto y sin evaluar λπ; alcance no
  oficial;
- el núcleo, 37/37;
- la cobertura: 70 nodos, 4 filas LAMBDA, 9 estados por conjunto, 12
  techos y 192 comparaciones;
- las 192 filas padre y las referencias;
- los pilotos;
- la revalidación de las tres referencias: `completa_validada`, 0 fallos e
  igual a la validación histórica guardada.

## Comparación (COMPARACION-FAM04-v1)

`fam04-comparar` compara la salida nueva con la ejecución aceptada rem112,
limitada a la selección registrada en `ejecucion.json`:
- **Requisitos previos**:
  - la salida es de la tarea pedida y su selección es coherente
    (SALIDA_DE_OTRA_TAREA, SELECCION_INCOHERENTE);
  - la validación es de esos mismos bytes (resultado y productos) y está
    aceptada (VALIDACION_AUSENTE, VALIDACION_DE_OTROS_BYTES,
    VALIDACION_NO_ACEPTADA);
  - el cálculo terminó completo (CALCULO_NO_COMPLETO);
  - cada producto de referencia tiene la huella del objeto del catálogo
    F04-LOTE1 (REFERENCIA_ALTERADA_O_AJENA), y cada producto nuevo, la que
    declara su `resultado.json` (PRODUCTO_AUSENTE_O_ALTERADO).
- **Productos**, por fila (clave natural de cada producto) y por puntero:
  - cobertura: filas que faltan, ajenas, duplicadas y orden;
  - discretos con precedencia (CR-DISCRETOS), incluido valor frente a nulo;
  - numéricos exactos (CR-HASH-CANONICO). Como FAM04 compara en el mismo
    contexto canónico, no se aplica CR-OBJETO-OTRO-ENTORNO.
- **`resultado.json`**: tarea, modo, sintético, estado, motivo y tope
  efectivo, iguales. Identidades del manifiesto y del código, iguales.
- **Derivados**: llamadas a `macro.bridge` de la unidad frente a la suma de
  sus filas y a la referencia de la unidad.
- **Operativo**: `pared_s`, solo informado.

La tolerancia T1 del validador no se convierte en tolerancia de
reproducción. Un cambio de 1 ulp en `B_d` lo admite el validador y lo
rechaza la comparación (ver controles).

## Pilotos (cálculo autorizado)

**Regla de elección.** Fijados por identificador desde el manifiesto antes
de calcular, sin mirar resultados (`datos/fam04/pilotos.json`):
- **ELAST**: la primera frontera bidimensional (τ_d y τ_f).
- **LAMBDA**: el primer conjunto. En su variante sin, el testigo de
  λ_max del manifiesto está en la frontera θ_W = 0.
- **COORD**: la primera clave con j = df, en el orden de las celdas.

**Ejecución.** Un proceso a la vez, con el supervisor que termina el árbol
de procesos y un límite externo de 600 s por invocación. El tope interno de
la tarea es 2280 s (= 2400 − 120), como en la producción.

| Piloto | Unidad | Filas | Pared (supervisor) | Dentro de la tarea | Memoria | Validación | Comparación |
|---|---|---|---|---|---|---|---|
| ELAST | `FRN:09c72876…` (G\|df, 25 nodos) | 25 | 0,83 s | 0,20 s (cálculo 0,01 s) | 47 MB | 0,33 s | 0,16 s |
| LAMBDA | PER-E1.macro (con y sin, 9 estados) | 2 | 1,42 s | 0,94 s (contexto 0,74 s, cálculo 0,01 s) | 73 MB | 0,33 s | 0,15 s |
| COORD | `19dabac4b3fe72f8` (N\|df; 1 techo, 16 celdas padre) | 1 + 16 | 5,18 s | 4,57 s (cálculo 4,38 s) | 50 MB | 0,32 s | 0,17 s |

**Resultados.** Los tres quedan `completa_validada`, con 0 fallos, y la
comparación los acepta:
- líneas idénticas a las filas de la referencia, en el mismo orden;
- 0 diferencias discretas y 0 numéricas;
- tarea, estado, motivo y tope, iguales.

Por piloto:
- **ELAST**: `reason_code` BASE_NONPOSITIVE en 20 filas, SP_LIMIT_AT_ZERO_RATE
  en 1 y ninguno en 4.
- **LAMBDA**: 36 llamadas a `macro.bridge`, igual que la referencia de esa
  unidad. Los 9 estados nacionales del contexto coinciden con el anexo en
  huella e identidad.
- **COORD**: las 16 filas padre se autentican antes de calcular.

**Lecturas** (rastro desde el inicio de la invocación):
- ELAST, 30 archivos del paquete;
- LAMBDA, 280 del paquete y 110 del venv (numpy 2.0.2);
- COORD, 46 del paquete, entre ellos sus 16 filas padre.

En los tres casos: 0 fuera del paquete y del intérprete, 0 sin declarar y
0 referencias.

**Historial de las ejecuciones.** Los productos son byte a byte iguales en
las tres rondas:
- `pilotos_01`: el rastro empezaba después de las comprobaciones previas y
  no registraba esas lecturas. Se adelantó al inicio.
- `pilotos_02`: el rastro registró 10 referencias leídas por la
  comprobación de huellas de las fuentes. Ahora la unidad solo comprueba
  entradas y código.
- `pilotos_03`: la ronda vigente, con sus validaciones y comparaciones.

**Duración.** La ejecución histórica registró `pared_s` de 0,33 s en ELAST,
84,09 s en LAMBDA y 10,25 s en COORD, para las tareas completas. Los
pilotos no permiten estimar la duración del lote:
- en LAMBDA, un conjunto tardó aquí 1,4 s frente a los 84 s históricos de
  dos; esa diferencia no se investigó;
- la comparación no usa el reloj.

## Controles (`local/pruebas_fam04.py`, sin cálculo científico)

`controles_01.json`: 29/29 conformes, 10,1 s en una sola invocación del
supervisor. No se recalculó ninguna malla, envolvente ni techo: se validan y
comparan bytes guardados (las copias alteradas recalculan solo la huella del
producto, para que cambie únicamente la ciencia).

- **Diferencial del validador** (7): `validar_lote.py` original, sin
  cambios y en proceso aparte, frente a VALIDADOR-v1 sin selección. Mismo
  código y mismo veredicto en:
  - las tres referencias rem112 (aceptadas);
  - ELAST con `B_d` + 1 ulp (aceptada por ambos);
  - LAMBDA con un estado nacional menos (COBERTURA_NACIONAL_INEXACTA);
  - LAMBDA sin anexo (COBERTURA_NACIONAL_SIN_ANEXO);
  - COORD con una comparación menos (COMPARACIONES_NO_CORRESPONDEN).
- **Positivos** (3): los tres pilotos guardados se validan y la comparación
  los acepta.
- **Valor científico alterado** (4):
  - ELAST `B_d` + 1 ulp en la fila P0000_0000: la validación lo admite
    (T1); la comparación lo rechaza con DIFERENCIA_NUMERICA en `/B_d`.
  - LAMBDA `lambda_max` con el numerador + 1: la validación lo rechaza
    (IDENTIDAD_K1Q y TESTIGO_NACIONAL) y la comparación también
    (VALIDACION_NO_ACEPTADA y DIFERENCIA_NUMERICA).
- **Referencia ajena** (2):
  - el piloto ELAST (G\|df) declarado como la frontera N\|df: rechazado por
    FRONTERAS_AJENAS y COBERTURA_FRONTERA, y en la comparación por
    COBERTURA_DISTINTA;
  - el producto de referencia de ELAST sustituido por el de LAMBDA:
    REFERENCIA_ALTERADA_O_AJENA.
- **Validación ausente o ajena** (2): VALIDACION_AUSENTE;
  VALIDACION_DE_OTROS_BYTES (validación del piloto sin alterar aplicada a la
  copia alterada).
- **Cobertura nacional omitida** (3):
  - un estado menos en la evidencia del mínimo de la variante sin:
    COBERTURA_NACIONAL_INEXACTA, comparación no aceptada;
  - piloto LAMBDA validado sin anexo: COBERTURA_NACIONAL_SIN_ANEXO;
  - piloto LAMBDA validado como tarea completa: COBERTURA_LAMBDA, porque
    falta PER-E1.micro. La selección no se infiere.
- **Clave COORD omitida** (2):
  - sin el techo de la clave: TECHOS_NO_CORRESPONDEN_A_LA_SELECCION;
  - sin una de las 16 comparaciones: COMPARACIONES_NO_CORRESPONDEN y, en la
    comparación, COBERTURA_DISTINTA.
- **Otra carpeta** (6): copia fuera del paquete (106 MB) con `reproducir.py`,
  catálogo, fuentes, `src`, `datos`, `nucleo_s6`, `referencias/fam04` y las
  192 filas padre. No lleva venv, salidas ni el resto de referencias, y se
  usa el mismo intérprete.
  - `fam04-comprobar` cumple.
  - Los tres pilotos guardados se validan y se aceptan.
  - Al retirar `conexion_frontera.py`, `fam04-comprobar` lo informa
    (código 1) y `fam04-unidad` se niega con DEPENDENCIA_AUSENTE_O_ALTERADA
    sin crear la carpeta.

**Regresión** del código compartido (`reproducir.py`), sin recalcular:
- `revisar` conforme (0,16 s);
- `fam01-comprobar` cumple (7,3 s);
- `fam02-comprobar` cumple (5,1 s);
- `fam03-comprobar` cumple (0,8 s);
- salidas en `salidas/fam04/regresion_*.json`.

Tras los cambios finales de `src/fam04.py` se repitieron `fam04-comprobar`
(`comprobar_02`) y `fam04-listar` (`listar_02`), ambos conformes. El resumen
del supervisor de cada invocación (código, segundos, CPU, memoria, hijos
vivos) está en `salidas/fam04/lanzador.txt`, sin rutas.

## Adaptaciones de interfaz

No cambian fórmulas, mallas, tolerancias, topes, presupuestos ni criterios.
Están declaradas en `src/fam04.py`:
- **TAREA-AST-v1**: `tarea_lote.py` tiene código de entrada al nivel
  superior (argumentos, puerta, cierre), así que no se importa como módulo
  inerte. Sus funciones `dom_manifiesto`, `proveedor_real`, `calc_lambda`,
  `calc_elast`, `calc_coord` y `producto` se compilan desde sus bytes
  exactos, con sus números de línea, en un espacio con los mismos nombres.
  `resultado.json` sigue el esquema y las condiciones de su cierre.
- **PUERTA-v1**: la puerta de producción (alcance v3 más la decisión humana
  leída de la transcripción) no se ejecuta ni se reconstruye. No hay lector
  de conversación ni decisión ficticia. Los pilotos los autoriza este
  encargo; el lote, el Paso 3. Se usa `modo = produccion` porque el
  validador lo exige para el manifiesto real. La etiqueta de esta base es
  «REPRODUCCION LIMPIA FAM04 NO OFICIAL».
- **CONTEXTO-FAM04-v1** (solo LAMBDA): `fam01.Contexto` (RunInputs sin la
  capa administrativa, como el modo portable del candidato) con `run_class
  = paso4_operativo_s6`, el del despliegue de producción (f293a0a6…). La
  ruta solo usa `ctx.inp.national`.
- **SELECCION-UNIDAD-v1**: una unidad se calcula pasando a `calc_*` la parte
  del manifiesto de esa unidad completa: todos sus nodos, variantes,
  estados o celdas padre.
- **VALIDADOR-v1**: `validar_lote.py` se ejecuta como guion desde sus bytes
  exactos con 8 sustituciones de texto declaradas, cada una presente una
  sola vez:
  - NUCLEO-v1, el núcleo de esta base;
  - SEL-ARGUMENTO, SEL-LAMBDA, SEL-ELAST, SEL-ELAST-TOTAL,
    SEL-COORD-TECHOS, SEL-COORD-UNICOS y SEL-COORD-CELDAS, que restringen
    los conjuntos esperados a la selección.

  Sin selección se comporta como el original (diferencial de los
  controles). Las dos comprobaciones de todo el manifiesto que la selección
  omite (total de nodos y techos nuevos únicos) las hace `fam04-comprobar`.
- **RELOJ-PILOTO-v1**: reloj interno = tope de trabajo − holgura del
  conductor (2400 − 120 = 2280 s). El límite externo lo pone el supervisor;
  si se agota, la tarea queda incompleta y nada se reduce.

## Límites

- **Cobertura de los pilotos**: 1 de 6 fronteras, 1 de 2 conjuntos y 1 de
  12 claves. El resto del lote no tiene cálculo en esta base.
- **Kinks**: el lote no tiene ninguno, así que las filas laterales
  (left/right_limit) no se ejercitan con un kink real. La regla del
  validador sí se comprueba.
- **Contexto**: su identidad (7b3ebac1…) difiere de la que registra el
  anexo (5273718d…), porque incluye la etiqueta y la huella del entorno de
  esta base. Lo que usa la ruta, los 9 estados nacionales por conjunto,
  coincide con el anexo.
- **Selección**: los pilotos se validan con la selección (VALIDADOR-v1). La
  validación de la tarea completa sin selección es la del original; se
  comprobó sobre las referencias, no sobre un cálculo nuevo del lote.
- **Puerta**: sin puerta ni decisión de producción (PUERTA-v1); las salidas
  son no oficiales.
- **Traslado**: se probó en esta máquina, con el mismo intérprete. El
  aislamiento efectivo queda para 2.4.2.
- **F2**: no se extiende a FAM04. La regla de FAM04 no la necesita; se
  informa en `ejecucion.json`.
- **Rutas**: las salidas de FAM04 registran rutas relativas, con 0 rutas
  personales. El resumen del supervisor se guardó sin rutas.

## Receta completa (preparada, no ejecutada)

`salidas/fam04/receta_01.json`:
- **Orden**: L1-ELAST → L1-LAMBDA → L1-COORD (6 fronteras, 2 conjuntos, 12
  claves). Cada tarea con sus órdenes `fam04-unidad`, `fam04-validar` y
  `fam04-comparar`, precedidas de `fam04-comprobar`.
- **Ejecución**: una tarea a la vez, sin reintentos, con un tope de trabajo
  de 2400 s por tarea (reloj interno de 2280 s) y 300 s de validación,
  con el mismo supervisor.
- **Parada**: si una tarea no queda completa y validada, no se lanza la
  siguiente.
- **Duración**: no se promete; los pilotos no la permiten estimar.

## Siguiente trabajo

- Preparación y pilotos revisados por Codex; detalle abajo.
- La ejecución del lote completo pertenece al Paso 3 y requiere su
  autorización.
- El aislamiento efectivo de FAM04 queda para 2.4.2.
- FAM05 (lote 2) no se abre sin encargo. El alcance adicional de COORD es
  FAM07.

## Revisión de Codex — 2026-11-16

Preparación de FAM04 cerrada en su alcance. Los tres pilotos quedan
aceptados; el lote completo no se declara reproducido.

Se revisaron la ruta de cálculo, las adaptaciones del validador, la selección
de unidades y la comparación. Sin repetir cálculos científicos, el cotejo
independiente comprobó las 19 fuentes y los cuatro productos de referencia
contra sus huellas, y comparó las líneas guardadas con la selección exacta
de rem112: 25 ELAST, 2 LAMBDA, 1 techo y 16 comparaciones COORD, todas
idénticas. En cada variante y extremo de LAMBDA están los nueve estados
nacionales del anexo, con sus huellas y orden.

`fam04-comprobar` y la nueva validación y comparación de los tres pilotos
resultaron conformes. Se revisaron los 29 controles guardados y se comprobó
de nuevo que un cambio de 1 ulp en B_d se detecta como diferencia numérica:
la tolerancia interna T1 no se usa para aceptar la reproducción.

La identidad distinta del contexto no altera los estados nacionales usados
por esta ruta ni extiende F2. La duración de LAMBDA no es criterio científico
ni permite proyectar el lote. La ausencia de kinks en este lote limita la
prueba de esa rama, sin bloquear su preparación.

Quedan la instalación realmente aislada (2.4.2) y la ejecución completa
autorizada del Paso 3. Esta revisión no modifica código, datos ni referencias.
El cotejo local se conserva en `local/revision_codex_fam04/resumen.json`.
