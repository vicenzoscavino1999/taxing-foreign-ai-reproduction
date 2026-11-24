# RESULTADO FAM06 — E4 (mallas G/N del lote 2 y su conciliación)

Fecha: 2026-11-16. Base: `reproduccion_limpia` (sin commits). El original se
consultó en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Cerrada en su alcance por Codex (2026-11-16). Están presentes el código (el de FAM05), el núcleo C0 (el de FAM05), las entradas E4, el productor de la conciliación, las referencias, la cobertura y la receta completa. Cálculo, validación, conciliación y comparación están conectados. |
| F06-MALLAS (RN) | Tres pilotos, uno por instrumento (d, f y df): cada uno es una malla E4 completa. Los tres quedan calculados, validados (`completa_validada`) y aceptados con líneas idénticas a la referencia rem121. |
| F06-CONCILIACION (RD) | Los pares de los tres pilotos se conciliaron con su malla de origen autenticada: el lado E4 es el recalculado y el del lote 2, el producto guardado. Los tres quedan aceptados. Los 391 pares se regeneraron como «regeneración sobre entradas guardadas», idénticos byte a byte a la conciliación aceptada (52a8f959…). Esa regeneración no acredita F06-MALLAS. |
| Reproducción completa | Pendiente (Paso 3). Las 383 mallas no se han calculado; la receta está preparada y no se ha lanzado. |

Los pilotos cubren 35 de los 4.115 nodos de E4 (3 de las 383 mallas) y 3 de
los 391 pares. No acreditan el resto del lote. FAM06 no cubre COORD (FAM07)
ni búsquedas de supremos.

## Alcance

| Operación | Tarea y unidades | Producto de la referencia rem121 |
|---|---|---|
| F06-MALLAS (RN) | L1-ELAST con `LOTE2E4_MANIFIESTO.json`: 383 mallas nuevas (172 d, 101 f y 110 df; 191 G y 192 N; 273 de una dimensión y 110 de dos) con 4.115 nodos (`frontier_n = 4`). Cada malla tiene un solo diseño y su contraparte es una malla de origen del lote 2. Sin suplemento ni λπ. | `frontier_result.jsonl` (cf711acc…): una fila `point` por nodo, laterales solo si hay kink y la topología del núcleo C0 en cada fila |
| F06-CONCILIACION (RD) | 391 pares G/N: 383 contrapartes E4 (malla E4 frente a su malla de origen del producto L1-ELAST del lote 2) y 8 pares existentes del manifiesto E4 (las dos mallas en el lote 2). Son 4.155 puntos emparejados (4.115 + 40). | `CONCILIACION_E4_REM121.json` (52a8f959…) |

**Recuentos confirmados** desde los productos y los manifiestos:
- 383 mallas y 4.115 filas, todas `point` (0 kinks). El `reason_code` es
  BASE_NONPOSITIVE en 1.480, SP_LIMIT_AT_ZERO_RATE en 951 y ninguno en
  1.684. La auditoría da `pass` en las 4.115;
- 391 pares (383 + 8) y 4.155 puntos; por instrumento, d 178, f 103 y
  df 110;
- 17 pares y 36 puntos con topología distinta entre G y N. Son resultados
  legítimos del contraste: se conservan y no se tratan como errores;
- universo padre de 572 fronteras, sin padres nuevos. Las 442 fronteras de
  origen de E4 están entre las 572 cubiertas por el lote 2.

**Anexo E4.** `COBERTURA_NACIONAL_LOTE2E4.json` (6015226d…) está ligado al
manifiesto, no tiene conjuntos λπ (0 llamadas a `macro.bridge`) y lo fija
el alcance. El validador solo lo usa en L1-LAMBDA, que E4 no tiene.

## Ruta efectiva

- **F06-MALLAS**: la misma ruta que FAM05 para L1-ELAST, es decir, las
  sentencias de producción de `tarea_lote.py` del lote 2 (U17), con
  `conexion_frontera` y el `model` del núcleo C0. Solo cambia el manifiesto:
  se usa el de E4 (MANIFIESTO-E4-v1). E4 no declara rutas relativas, así
  que la tarea no lee nada a través de su raíz.
- **Validación**: `validar_lote.py` del lote 2 (U18) en modo `produccion`,
  con el manifiesto y el anexo E4 (VALIDADOR-v2, las mismas sustituciones de
  FAM05).
- **F06-CONCILIACION**: el productor histórico
  `conciliacion_e4_rem121.py` (5ccb9f8f…), ejecutado desde sus bytes
  exactos (CONCILIADOR-v1). Por par revisa:
  - el vínculo: clave estructural, instrumento, dominio τ y diseños G y N;
  - que los puntos sean los mismos;
  - los campos comunes y los que difieren, las topologías, los kinks y los
    nulos.

  No impone igualdad numérica entre G y N, no trata un kink como error ni
  convierte un nulo en cero. No es otro cálculo del modelo.

## Extracción

`extraccion/extraer_fam06.py copiar <raíz original> [<libro rem122>
[<dictamen>]]` comprueba que el código U17/U18 del original es igual a los
objetos del paquete y a las copias de FAM05, y no lo vuelve a copiar. Deja
en `fuentes_fam06.json` 9 piezas copiadas (copias exactas, sin rutas
absolutas):
- **entradas** (`datos/fam06/`):
  - `LOTE2E4_MANIFIESTO.json` (d430b39d…, objeto del catálogo);
  - `COBERTURA_NACIONAL_LOTE2E4.json` (6015226d…; no es objeto del catálogo,
    pero lo fija el alcance);
  - `alcance_lote2e4.json` (5471d1d3…, objeto del catálogo). Solo cruza
    huellas; no es una puerta;
- **productor de la conciliación**: `nucleo_s6/e4/conciliacion_e4_rem121.py`
  (5ccb9f8f…). No es objeto del catálogo; su huella la cruza el libro;
- **referencias** (`referencias/fam06/rem121/`): `L1-ELAST/resultado.json`
  (0a788b1f…), `validacion_stdout.txt` (e37790b3…), `salida/frontier_result.jsonl`
  (cf711acc…) y `conciliacion/CONCILIACION_E4_REM121.json` (52a8f959…);
- `datos/fam06/pilotos.json` (abf20499…), dato nuevo de esta base (sin
  resultados).

Declara además 8 piezas **reutilizadas de FAM05**, sin copiarlas de nuevo:
- el código U17 (`tarea_lote.py`, `conexion_lambda.py` y
  `conexion_frontera.py`) y el U18 (`validar_lote.py`);
- `datos/fam05/LOTE2_MANIFIESTO.json`, como entrada de la conciliación
  (mallas de origen y pares existentes);
- `referencias/fam05/rem120/L1-ELAST/` (`resultado.json`,
  `frontier_result.jsonl` 007095a9… y `suplemento_procedencia.jsonl`
  d6a12af3…), como entrada guardada del lado de origen.

El **núcleo C0** es el auténtico de FAM05: los mismos 37 archivos de
`nucleo_s6/c0/src/paper2b`, declarados en `fuentes_fam05.json`, con
identidad d0bf5cd6…. No se copió otro núcleo.

**Libro rem122.** Se usó solo para extraer, nunca al ejecutar.
`fuentes_fam06.json` guarda un resumen sin rutas ni transcripciones:
recuentos E4, productos, huella del alcance de la decisión, COORD nuevo
aceptado (0) y huella del dictamen, que se consultó para confirmar el
alcance y no se copió.

**Rutas.** Las piezas tienen 0 rutas personales; ninguna necesitó
saneamiento. El conciliador histórico tenía rutas fijas del área de
rem121, que se sustituyen por rutas explícitas (CONCILIADOR-v1).

## Entradas reutilizadas y regeneradas

- **Se reutiliza**:
  - la selección E4 (el manifiesto) y el anexo E4;
  - el código U17/U18, el núcleo C0 y el manifiesto del lote 2, de FAM05;
  - el producto L1-ELAST aceptado del lote 2 y su suplemento, como lado de
    origen guardado de la conciliación (autenticado por su huella del
    catálogo, sin recalcular).
- **Se genera de nuevo**:
  - las filas de las mallas piloto, con su topología;
  - la conciliación de los pares de los pilotos;
  - la conciliación completa de los 391 pares, sobre entradas guardadas.
- **Solo para comparar**: `frontier_result.jsonl` de rem121 y
  `CONCILIACION_E4_REM121.json`. Durante el cálculo no se leyó ninguna
  referencia, y el conciliador nunca leyó la conciliación esperada.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1. Siguen el patrón de FAM05:

```text
reproducir.py fam06-listar    --salida salidas/fam06/listar_01.json
reproducir.py fam06-comprobar --salida salidas/fam06/comprobar_02.json
reproducir.py fam06-unidad    --unidad FRN-E4:N:45044919d27cdb437994 --salida salidas/fam06/piloto_01/L1-ELAST
reproducir.py fam06-validar   --nueva salidas/fam06/piloto_01/L1-ELAST --salida salidas/fam06/piloto_01/L1-ELAST.validacion.json
reproducir.py fam06-comparar  --tarea L1-ELAST --nueva salidas/fam06/piloto_01/L1-ELAST --validacion salidas/fam06/piloto_01/L1-ELAST.validacion.json --salida salidas/fam06/piloto_01/L1-ELAST.comparacion.json
reproducir.py fam06-conciliar --e4 salidas/fam06/piloto_01/L1-ELAST --validacion-e4 salidas/fam06/piloto_01/L1-ELAST.validacion.json --lote2 guardado --salida salidas/fam06/piloto_01/conciliacion
reproducir.py fam06-comparar  --tarea CONCILIACION --nueva salidas/fam06/piloto_01/conciliacion --salida salidas/fam06/piloto_01/conciliacion.comparacion.json
reproducir.py fam06-conciliar --e4 guardado --lote2 guardado --salida salidas/fam06/regeneracion_01/conciliacion
reproducir.py fam06-comparar  --tarea CONCILIACION --nueva salidas/fam06/regeneracion_01/conciliacion --salida salidas/fam06/regeneracion_01/conciliacion.comparacion.json
reproducir.py fam06-receta    --salida salidas/fam06/receta_01.json
```

- **Sin cálculo científico**: `fam06-listar`, `fam06-comprobar`,
  `fam06-validar`, `fam06-comparar`, `fam06-receta` y `fam06-conciliar`. La
  conciliación es regeneración documental y aritmética, no cálculo del
  modelo.
- **`fam06-unidad`**: sin `--unidad` calcula las 383 mallas; con
  `--unidad`, una malla entera. Se niega antes de crear la carpeta si falta
  o cambió una dependencia o si el núcleo C0 no tiene su identidad. Exige
  `PYTHONHASHSEED=0` efectivo.
- **`fam06-conciliar`**: cada lado se declara siempre, sin valor por
  defecto:
  - una carpeta nueva con su validación. Para E4, una salida de
    `fam06-unidad` validada y aceptada; para el lote 2, la tarea L1-ELAST
    completa de FAM05, también validada;
  - o `guardado`: el producto aceptado del paquete, autenticado por su
    huella del catálogo.

  Con un lado E4 parcial (piloto), solo se concilian sus pares.
- **Separación**: cálculo, validación, conciliación y comparación son pasos
  aparte, y cada uno termina con 0 solo en su caso aceptado.

## Comprobación (`fam06-comprobar`, sin cálculo)

`comprobar_02.json` da `cumple` en 0,58 s (0,8 s con el supervisor). Es
igual a `comprobar_01` salvo el tiempo. Revisa:
- las 9 piezas propias, las 8 reutilizadas y los 37 archivos de C0;
- la procedencia, en 19 puntos:
  - código igual al de FAM05 y al alcance;
  - validador, manifiesto, anexo, identidad C0 y D7 iguales al alcance;
  - manifiesto, alcance y resultado de referencia iguales al catálogo;
  - despliegue del alcance; alcance no oficial y solo con L1-ELAST;
  - anexo ligado al manifiesto, sin conjuntos ni evaluaciones y de esta
    conexión;
  - manifiesto del lote 2 ligado;
  - conciliador igual al extraído, con cada sustitución presente una sola
    vez;
- el núcleo C0: identidad recalculada e igual a la del alcance, con
  `paper2b` cargado de `nucleo_s6/c0`;
- la cobertura del manifiesto E4: mallas, nodos, instrumentos, diseños,
  dimensiones, vínculo con la malla de origen, pares, puntos emparejados y
  universo padre;
- las referencias:
  - el resumen de la conciliación aceptada (391 pares, 0 pendientes, 17/36
    de topología distinta);
  - la revalidación del producto E4 completo: `completa_validada`, 0 fallos
    e igual a la validación histórica guardada;
- los 16 recuentos del libro rem122, todos iguales a los archivos;
- los pilotos (iguales a la regla) y la receta (3 pasos).

## Comparación

**COMPARACION-FAM06-MALLAS-v1** (`fam06-comparar --tarea L1-ELAST`). Es la
de FAM05 sin el suplemento:
- **Requisitos previos**: validación de esos mismos bytes y aceptada;
  cálculo completo.
- **Producto**: cobertura, discretos con precedencia (CR-DISCRETOS) y
  numéricos exactos (CR-HASH-CANONICO), fila a fila y campo a campo,
  incluida `topology`.
- **`resultado.json`**: tarea, modo, sintético, estado, motivo y tope;
  identidades del manifiesto, del código y del núcleo C0.
- **Referencia por identificador**: la referencia debe ser P_e4_frontier.
  Otro `frontier_result` del catálogo (por ejemplo P_elast_lote2) da
  REFERENCIA_ALTERADA_O_AJENA.
- **Operativo**: `pared_s`, solo informado.

**COMPARACION-FAM06-CONCILIACION-v1** (`fam06-comparar --tarea
CONCILIACION`). Todo el objeto es discreto, así que se compara exacto:
- **Cobertura de pares**: mismos pares, en el mismo orden y sin repetidos.
- **Detalle**: cada hoja de cada par, frente a la referencia (con
  selección, restringida a los mismos pares).
- **Totales**: todos con la conciliación completa; con selección, el
  universo padre. Los totales de la nueva deben derivarse de su propio
  detalle.
- **Vínculos por lado**: las huellas `producto_e4_sha256` y
  `producto_elast_aceptado_sha256` se comprueban contra los bytes de su
  propio lado y contra la ejecución. La de la referencia se comprueba
  contra el catálogo. Así, un lado recalculado puede tener otra huella (la
  de su selección) sin que eso cuente como diferencia.
- **Topología G/N**: control positivo. Las diferencias legítimas deben
  conservarse, con su número de pares y puntos.
- **Bytes idénticos**: se informa si el producto es byte a byte el de
  referencia.

No se añadieron tolerancias. La T1 interna del validador no se convierte en
tolerancia de reproducción: un cambio de 1 ulp lo admite el validador y lo
rechaza la comparación (ver controles).

## Pilotos de F06-MALLAS (cálculo autorizado)

**Regla de elección.** Los pilotos se fijaron por identificador desde el
manifiesto E4 antes de calcular, sin mirar resultados
(`datos/fam06/pilotos.json`): la primera malla de cada instrumento d, f y
df en el orden del manifiesto. Cada piloto es la malla entera.

**Ejecución.** Un proceso a la vez, con el supervisor del paquete fuente
(`supervisar.py`), que termina el árbol de procesos, y un límite externo de
600 s por invocación. El tope interno de la tarea es 2280 s (= 2400 − 120),
como en la producción.

| Piloto | Malla | Origen (lote 2) | Filas | Pared (supervisor) | Dentro de la tarea | Memoria | Validación | Comparación |
|---|---|---|---|---|---|---|---|---|
| 1 d | `FRN-E4:N:45044919…` (N\|d, dim. 1) | G\|d\|`FRN:bfe55344…` | 5 | 1,0 s | 0,23 s (cálculo 0,00 s) | 40,5 MB | 0,4 s | 0,3 s |
| 2 f | `FRN-E4:N:daf7cba5…` (N\|f, dim. 1) | G\|f\|`FRN:ef796dd0…` | 5 | 0,9 s | 0,22 s (cálculo 0,02 s) | 40,5 MB | 0,4 s | 0,3 s |
| 3 df | `FRN-E4:G:fe634bc9…` (G\|df, dim. 2) | N\|df\|`FRN:25b337fb…` | 25 | 0,8 s | 0,22 s (cálculo 0,01 s) | 40,5 MB | 0,4 s | 0,3 s |

**Resultados.** Los tres quedan `completa_validada`, con 0 fallos, y la
comparación los acepta:
- líneas idénticas a la referencia (huellas de las filas f171d3d6…,
  0691e5ee… y ef6caae8…);
- 0 diferencias discretas y 0 numéricas;
- tarea, modo, estado, motivo y tope iguales; identidades iguales.

El `reason_code` es SP_LIMIT_AT_ZERO_RATE en las 5 filas del piloto d. En
el f es ninguno en 4 y SP_LIMIT_AT_ZERO_RATE en 1; en el df, ninguno en 20 y
SP_LIMIT_AT_ZERO_RATE en 5. No hay kinks.

**Lecturas** (rastro desde el inicio de la invocación), en cada piloto:
- 47 archivos del paquete, de ellos 37 del núcleo C0;
- 0 fuera del paquete y del intérprete, 0 sin declarar, 0 del venv y 0
  referencias;
- 0 de `datos/fam05`: el manifiesto del lote 2 solo lo usa la
  conciliación.

El entorno es conforme: Python 3.12.4, semilla 0, `TZ=UTC` e hilos en 1. F2
se informa (equivalente), pero no se extiende a FAM06.

**Duración.** La ejecución histórica registró `pared_s` de 1,52 s para las
383 mallas. Aquí el `pared_s` de cada malla fue de 0,21 s, casi todo de
preparación. Esa cifra no permite estimar el lote; la comparación no usa el
reloj.

## Conciliación de los pilotos

Cada piloto se concilió con su malla de origen autenticada. Es una
«conciliación mixta»:
- **lado E4 recalculado**: la salida nueva del piloto, validada y aceptada;
- **lado del lote 2 reutilizado**: el producto L1-ELAST aceptado guardado
  (`referencias/fam05/rem120/L1-ELAST`, P_elast_lote2 y su suplemento),
  autenticado por su huella del catálogo y sin recalcular.

| Piloto | Par | Conciliación | Total | Pared (supervisor) | Comparación |
|---|---|---|---|---|---|
| 1 d | `E4:FRN-E4:N:45044919…` | 0,036 s | 0,094 s | 0,3 s | 0,2 s, aceptada |
| 2 f | `E4:FRN-E4:N:daf7cba5…` | 0,057 s | 0,107 s | 0,3 s | 0,2 s, aceptada |
| 3 df | `E4:FRN-E4:G:fe634bc9…` | 0,053 s | 0,094 s | 0,3 s | 0,2 s, aceptada |

En los tres:
- el par queda conciliado, con 0 pendientes y 0 diferencias discretas
  frente al mismo par de la referencia;
- el universo padre es 572, igual a la referencia;
- estos tres pares no tienen diferencias de topología (0 de 17);
- el vínculo `producto_e4_sha256` apunta a los bytes del piloto, distintos
  de los del producto completo (visible en el informe). El del lote 2
  coincide con la referencia y con el catálogo;
- los bytes no son los de la referencia, como corresponde a un solo par;
- 53 archivos del paquete leídos, incluidas las 3 piezas del lado de origen
  guardado. La conciliación esperada no se leyó.

## Regeneración documental de la conciliación

`regeneracion_01`, etiquetada «regeneración sobre entradas guardadas». Los
dos lados son reutilizados: el producto E4 aceptado (P_e4_frontier) y el
L1-ELAST aceptado del lote 2. Ninguna malla se recalcula, y la regeneración
no acredita F06-MALLAS.

- **Producto**: `CONCILIACION_E4.json` idéntico byte a byte a
  `CONCILIACION_E4_REM121.json` (52a8f959…).
- **Pares**: 391 conciliados (383 contrapartes y 8 existentes), 0
  pendientes; 4.115 puntos de contraparte; d 178, f 103 y df 110; 0 pares
  con kink.
- **Orígenes**: 379 «C0 (rem120 aceptado)», 4 «histórico lote 1 + topología
  C0» y, en los existentes, 6 «G C0 / N C0», 1 «G C0 / N histórico» y 1 «G
  histórico / N C0». Todos iguales a la referencia.
- **Topología**: igual en todos los puntos en 374 pares; distinta en 17
  pares y 36 puntos, conservada.
- **Universo padre**: 572, derivado de los manifiestos; antes era una
  constante del productor.
- **Tiempos**: conciliación 0,116 s y total 0,148 s; 0,4 s y 52,7 MB con el
  supervisor. La comparación tardó 0,2 s y la aceptó.
- **Lecturas**: 55 archivos del paquete (los 5 de los dos lados guardados).
  La conciliación esperada no se leyó: solo la abre la comparación.

## Controles (`local/pruebas_fam06.py`, sin cálculo científico)

`controles_01.json`: 26/26 conformes, en 9,9 s. Se ejecutaron una sola
vez, en una invocación directa del guion, sin el supervisor, porque no
calculan. Sus órdenes corren una a una. No se recalculó ninguna malla: se
validan, concilian y comparan bytes guardados, en copias dentro de
`salidas/fam06/controles_01`. Las copias alteradas recalculan la huella del
producto declarada, para que cambie solo la ciencia.

- **Valor alterado** (3):
  - `B_d` + 1 ulp en la fila P0000_0000 del piloto df (dos casos): la
    validación lo admite (código 0, T1) y la comparación lo rechaza con
    DIFERENCIA_NUMERICA en `/B_d`;
  - un par con topología distinta «igualado» (G = N forzado): la
    comparación da DIFERENCIA_DISCRETA_EN_EL_DETALLE y
    TOTALES_NO_DERIVADOS_DEL_DETALLE.
- **Control positivo** (1): la regeneración guardada se acepta y conserva
  17 pares y 36 puntos de topología distinta.
- **Validación o referencia equivocadas** (3):
  - el piloto d con la validación del f: VALIDACION_DE_OTROS_BYTES;
  - la referencia E4 sustituida por P_elast_lote2:
    REFERENCIA_ALTERADA_O_AJENA;
  - la conciliación de referencia con un par menos:
    REFERENCIA_ALTERADA_O_AJENA y COBERTURA_DE_PARES_DISTINTA.
- **Lados mal declarados** (3):
  - el lado de origen como piloto parcial de FAM05: LOTE2_PARCIAL;
  - el lado E4 nuevo sin validación: VALIDACION_AUSENTE;
  - un lado sin declarar: la orden se niega (código 2); no hay sustitución
    por defecto.
- **Punto omitido o duplicado** (4):
  - un nodo omitido en el piloto df. La validación da COBERTURA_FRONTERA y
    la comparación, VALIDACION_NO_ACEPTADA y COBERTURA_DISTINTA;
  - el mismo producto con el conciliador directo, sin la guarda del
    adaptador: el par queda pendiente (`mismos_puntos: false`, 24 puntos);
  - con `fam06-conciliar`: se niega por VALIDACION_NO_ACEPTADA (E4);
  - una fila duplicada en el piloto d: FILA_POINT_NO_UNICA en la
    validación, y VALIDACION_NO_ACEPTADA y COBERTURA_DISTINTA en la
    comparación.
- **Clave o dominio equivocados** (3):
  - el dominio τ de una malla cambiado en el manifiesto E4 (0,6 → 0,5):
    PAREJA_CON_CLAVE_DOMINIO_O_MALLA_DISTINTOS;
  - la malla de origen con otro `phi`, con el conciliador directo:
    `misma_clave: false` y par no conciliado;
  - el lado de origen guardado alterado (una fila de procedencia menos,
    declaración rehecha): LOTE2_GUARDADO_ALTERADO_O_AJENO.
- **Otra carpeta** (9): una copia fuera del paquete, con el mismo
  intérprete.
  - `fam06-comprobar` cumple.
  - Los tres pilotos guardados se revalidan, se comparan y se compara su
    par conciliado, sin calcular.
  - La regeneración da los mismos bytes y la comparación la acepta.
  - Con el manifiesto del lote 2 alterado (un byte más), `fam06-conciliar`
    se niega con DEPENDENCIA_AUSENTE_O_ALTERADA.
  - Al retirar `conciliacion_e4_rem121.py`, `fam06-comprobar` lo informa y
    `fam06-conciliar` se niega.
  - Sin `conexion_frontera.py`, `fam06-unidad` se niega sin crear la
    carpeta.

**Regresión** del código compartido (`reproducir.py`), sin recalcular:
- `revisar` conforme;
- `fam01-comprobar` cumple (6,6 s), `fam02-comprobar` (4,8 s),
  `fam03-comprobar` (0,7 s), `fam04-comprobar` (0,5 s) y `fam05-comprobar`
  (0,9 s);
- salidas en `salidas/fam06/regresion_fam0*_comprobar.json`.

Tras actualizar los tableros y el catálogo se repitieron `revisar`
(conforme) y `fam06-comprobar` (`comprobar_03`, igual a `comprobar_02`
salvo el tiempo).

`revisar` y el guion de controles se ejecutaron sin el supervisor. Todo lo
demás pasó por él: 27 invocaciones, todas con código 0 y 0 procesos activos
al terminar. Su resumen está en `salidas/fam06/lanzador.txt`, sin rutas:
código, segundos, CPU, memoria y procesos activos al terminar.

## Correcciones rutinarias de esta sesión

Ninguna cambió la ciencia ni los criterios. Se hicieron antes de los
controles:
- **Conciliador ausente**: sin el archivo, `fam06-comprobar` habría fallado
  con una excepción no controlada. Ahora lo informa como ausente
  (CONCILIADOR_AUSENTE) y `fam06-conciliar` se niega. Un control lo cubre.
- **Orden de una comprobación**: con un lado de origen parcial de FAM05, el
  primer rechazo era el de los productos. Ahora la selección se comprueba
  antes y el motivo es LOTE2_PARCIAL.
- **Dos controles** se ajustaron antes de ejecutarlos. El del manifiesto
  del lote 2 añade un byte en lugar de una sustitución de texto que podía
  no coincidir. En el del dominio τ, el texto esperado era demasiado
  específico.

Estos cambios son posteriores a `comprobar_01` y a los pilotos, pero solo
afectan a ramas de error. `comprobar_02`, la otra carpeta y los controles
usan el código final.

## Adaptaciones de interfaz

No cambian fórmulas, mallas, tolerancias, topes, presupuestos ni criterios.
Están declaradas en `src/fam06.py`:
- **De FAM05, sin cambios**: TAREA-AST-v2, FIN-v1, PUERTA-v1 (etiqueta
  «REPRODUCCION LIMPIA FAM06 NO OFICIAL»), NUCLEO-C0-v1,
  SELECCION-UNIDAD-v1, VALIDADOR-v2 (las mismas 6 sustituciones) y
  RELOJ-PILOTO-v1 (2400 − 120 = 2280 s).
- **MANIFIESTO-E4-v1**: la misma ruta, con el manifiesto y el anexo E4
  explícitos (`datos/fam06`). La raíz de las rutas relativas es
  `datos/fam06`; E4 no declara ninguna.
- **CONCILIADOR-v1**: `conciliacion_e4_rem121.py` se ejecuta desde sus
  bytes exactos con 8 sustituciones declaradas. Cada original debe estar
  presente una sola vez:
  - RUTAS-EXPLICITAS, RUTAS-PRODUCTOS y RUTAS-MANIFIESTOS: rutas
    explícitas de manifiestos y productos en lugar de la raíz y el área de
    rem121. Se conserva la huella fija del manifiesto E4 (d430b39d…);
  - HUELLAS-DECLARADAS-LOTE2: las huellas fijas del producto del lote 2 se
    sustituyen por las que declara su `resultado.json`, como el original ya
    hacía con E4. La autenticación de cada lado pasa al adaptador: huella
    del catálogo si es guardado, y validación aceptada de esos bytes si es
    nuevo;
  - SEL-PARES-E4 y SEL-PARES-EXISTENTES: selección opcional de pares
    (pilotos);
  - PADRES-DERIVADOS y PADRES-SALIDA: el universo padre, que era la
    constante 572, se deriva de los manifiestos (fronteras cubiertas por el
    lote 2 más orígenes de E4) y da 572.

  El texto adaptado tiene la huella e25bd75d…. Nunca lee la conciliación
  esperada.

## Límites

- **Cobertura de los pilotos**: 3 de 383 mallas y 3 de 391 pares. El resto
  de E4 no tiene cálculo en esta base. La conciliación completa se regeneró
  sobre productos guardados, no sobre salidas nuevas.
- **Topología distinta**: ninguno de los tres pilotos está entre los 17
  pares con topología distinta. Su conservación se comprobó en la
  regeneración y con el control positivo, no con un par recalculado.
- **Kinks**: la referencia no tiene ninguno; las filas laterales no se
  ejercitan con un kink real.
- **Lado de origen**: en los pilotos se reutiliza el producto guardado del
  lote 2. La receta usa el recalculado de FAM05; esa combinación no se ha
  ejecutado.
- **Selección**: los pilotos se validan con la selección (VALIDADOR-v2). La
  validación completa se comprobó sobre la referencia, no sobre un cálculo
  nuevo.
- **Puerta**: sin puerta ni decisión de producción (PUERTA-v1); las salidas
  son no oficiales.
- **Traslado**: probado en esta máquina, con el mismo intérprete. El
  aislamiento efectivo queda para 2.4.2.
- **F2**: no se extiende a FAM06; se informa en `ejecucion.json`
  (equivalente).
- **Rutas**: las salidas de FAM06 registran rutas relativas, con 0 rutas
  personales, salvo los registros del supervisor
  (`salidas/fam06/lanzador/*.tarea.json`), que guardan rutas absolutas de
  esta máquina. El resumen `lanzador.txt` no tiene rutas.

## Receta completa (preparada, no ejecutada)

`salidas/fam06/receta_01.json`, en 3 pasos precedidos de `fam06-comprobar`:
1. **F06-MALLAS**: `fam06-unidad` sin `--unidad` (las 383 mallas, 4.115
   nodos), después `fam06-validar` y `fam06-comparar --tarea L1-ELAST`.
2. **Lado de origen**: L1-ELAST del lote 2 con la receta de FAM05
   (`fam05-unidad`, `fam05-validar` y `fam05-comparar`).
3. **F06-CONCILIACION**: `fam06-conciliar` con las dos salidas nuevas
   validadas, y `fam06-comparar --tarea CONCILIACION` frente a los 391
   pares.

- **Ejecución**: un paso a la vez, sin reintentos, con un tope de trabajo
  de 2400 s por tarea (reloj interno de 2280 s), 300 s de validación y el
  mismo supervisor.
- **Parada**: si un paso no queda completo, validado y aceptado, no se
  lanza el siguiente.
- **Duración**: no se promete; los pilotos no permiten estimarla.

## Propuesta de cierre

Propongo cerrar la **preparación** de FAM06 en su alcance:
- código, núcleo C0, entradas, productor de la conciliación y referencias
  están en el paquete, sin rutas personales. Lo común con FAM05 se
  reutiliza sin copiar otro núcleo;
- cálculo, validación, conciliación y comparación están conectados, con la
  receta completa lista;
- se conservan los criterios, la conciliación sin G = N ni nulo → 0, las
  diferencias de topología y la separación entre lo recalculado y lo
  reutilizado.

Los **pilotos** de F06-MALLAS y sus pares conciliados quedan aceptados con
igualdad exacta. La conciliación completa se regeneró sobre entradas
guardadas, idéntica byte a byte; eso no acredita F06-MALLAS. La
**reproducción completa** de las 383 mallas no está hecha: pertenece al
Paso 3.

## Siguiente trabajo

- Preparación revisada y cerrada en alcance por Codex (véase abajo).
- La ejecución completa de E4 y su conciliación sobre salidas nuevas
  pertenecen al Paso 3.
- El aislamiento efectivo de FAM06 queda para 2.4.2.
- FAM07 (COORD del lote 2) no se abre sin encargo.

## Revisión de Codex — 2026-11-16

Preparación de FAM06 cerrada en su alcance, sin hallazgos bloqueantes.
Se aceptan los tres pilotos y sus conciliaciones mixtas, así como la
regeneración de los 391 pares sobre entradas guardadas. Esta última no
acredita el cálculo completo de E4.

La revisión de las rutas efectivas, las adaptaciones y las comparaciones
se complementó con un cotejo independiente sin cálculo científico:

- Las 9 fuentes propias, las 8 reutilizadas y los 37 archivos de C0
  coinciden con sus huellas. El inventario C0 conserva la identidad fijada.
- Las 5, 5 y 25 filas de los pilotos son idénticas a sus filas de referencia.
  Su nueva validación y comparación resultan aceptadas. Los registros de
  cálculo declaran cero lecturas externas, sin declarar o de referencias.
- Se reconstruyó la correspondencia de los 391 pares desde ambos
  manifiestos y se cotejaron las filas de sus dos lados: 4.155 puntos,
  178 pares d, 103 f y 110 df. Se conservan exactamente los 17 pares y
  36 puntos con topología distinta; no se exige igualdad de valores G/N.
- Las tres conciliaciones mixtas y la regeneración completa vuelven a
  pasar la comparación. Esta última conserva la huella histórica
  `52a8f9592c8f934e9769ed5788bf8926f7fa4c79fcb95cdcb31559f4cd5cc2eb`.
- Se revisaron los 26 controles guardados, incluida la separación entre
  la tolerancia interna del validador y la igualdad exacta del comparador.

El cotejo está en `local/revision_codex_fam06/resumen.json`. No se
modificaron el código científico, las entradas, las referencias ni las
salidas del ejecutor. Quedan la ejecución completa de las 383 mallas y su
conciliación sobre salidas nuevas (Paso 3), y el aislamiento real (2.4.2).
Los límites de kinks, topología y publicación de registros del supervisor
siguen declarados. No se extiende F2 ni se abre FAM07 en esta revisión.
