# RESULTADO FAM05 — lote 2 (ELAST con suplemento histórico y LAMBDA)

Fecha: 2026-11-16. Base: `reproduccion_limpia` (sin commits). El original se
consultó en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Cerrada en su alcance por Codex (2026-11-16). Están presentes el código, el núcleo C0, las entradas, la fuente del suplemento, las referencias, la cobertura y la receta del lote completo. Cálculo, validación y comparación están conectados. |
| Pilotos | Tres pilotos calculados, validados (`completa_validada`) y aceptados por la comparación con líneas idénticas a la referencia: una malla ELAST nueva bidimensional, un par LAMBDA publicado y un par LAMBDA estricto. La unidad SUPLEMENTO (70 filas históricas) se verificó sin recalcular sus valores, y también quedó aceptada. |
| Reproducción completa | Pendiente (Paso 3). El lote no se ha ejecutado; la receta está preparada y no se ha lanzado. |

Los pilotos cubren:
- 25 de los 4.125 nodos nuevos de ELAST (1 de las 393 mallas nuevas);
- las 6 mallas del suplemento con sus 70 filas, como verificación de
  integridad del componente histórico (no es un cálculo nuevo);
- 4 de las 24 filas LAMBDA (2 de los 12 pares; 164 de las 488 llamadas a
  `macro.bridge`).

No acreditan el resto del lote. FAM05 no cubre COORD del lote 2 (FAM07) ni
E4 (FAM06).

## Alcance

Las tareas internas se llaman L1-ELAST y L1-LAMBDA aunque son del lote 2:
son los nombres del código histórico. «Lote 1» solo designa la procedencia
de las 70 filas reutilizadas.

| Operación | Tarea y unidades | Productos de la referencia rem120 |
|---|---|---|
| F05-ELAST-C0 (RN) | L1-ELAST: 393 mallas nuevas (285 de una dimensión y 108 de dos) con 4.125 nodos (`frontier_n = 4`). Cubren 527 fronteras equivalentes; con 39 equivalencias ya aceptadas, 566. | `frontier_result.jsonl`: una fila `point` por nodo, laterales solo si hay kink y la topología del núcleo C0 en cada fila |
| F05-ELAST-HIST (VI) | L1-ELAST, unidad SUPLEMENTO: 6 mallas (4 de una dimensión y 2 de dos) con 70 filas aceptadas del lote 1 (P_elast_lote1, dba33b47…). No se recalculan: se copian, reciben la topología tras comprobar la compatibilidad del estencil y se publica su procedencia. | Las 70 filas dentro de `frontier_result.jsonl`, más `suplemento_procedencia.jsonl` (70 filas) |
| F05-LAMBDA (RN) | L1-LAMBDA: 12 pares `conjunto\|país` × variantes con/sin = 24 filas | `lambda_envolvente.jsonl`, 24 filas; 488 llamadas a `macro.bridge` (4 por estado: dos variantes × testigo de máximo y de mínimo) |

En total, L1-ELAST tiene 399 mallas, 4.195 filas y 572 fronteras cubiertas.

**Referencia ELAST.** Las 4.195 filas son `point` (0 kinks). Su
`reason_code` es BASE_NONPOSITIVE en 1.519, SP_LIMIT_AT_ZERO_RATE en 975 y
ninguno en 1.701. La auditoría da `pass` en las 4.195.

**Estados de LAMBDA**, por par y según el anexo:
- CMP-E1 (seis pares): 9 estados nacionales publicados;
- COL-E2-2023 (cuatro pares): 1 estado;
- PER-E0E3 (dos pares): dominio estricto, con los 32 candidatos que da la
  enumeración de su definición (6c745c5d…; 128 vértices de caja, signo no
  negativo).

Son 232 llamadas publicadas y 256 estrictas, las del presupuesto del
manifiesto.

**Cobertura nacional.** `COBERTURA_NACIONAL_LOTE2.json` (5bea5153…) es el
anexo del manifiesto:
- lleva la huella del manifiesto (b1cf8af5…);
- está preparado sin evaluar λπ;
- corresponde a esta `conexion_lambda`.

El alcance y el paquete rem119 fijan su huella. `validar_lote` exige en cada
fila, en el máximo y en el mínimo, exactamente los estados o candidatos del
anexo, en orden. Si falta un candidato estricto, se rechaza la fila entera:
no se elimina el candidato para aceptar el resto (ver controles).

## Ruta efectiva

La de `tarea_lote.py` del lote 2 en producción, con el núcleo C0:
- **ELAST**: las sentencias de producción desde `calc_elast(fr_)` hasta el
  cierre.
  - Las mallas nuevas pasan por `conexion_frontera` y el `model` de C0.
  - `fuente_suplemento` autentica la fuente por su huella y su número de
    filas.
  - `calc_elast`, con `conexion_frontera.enriquecer_suplemento`, comprueba
    la compatibilidad del estencil y añade la
    topología a las 70 filas sin tocar sus valores. Si alguna es
    incompatible, la tarea queda incompleta y no publica.
- **LAMBDA**: las sentencias desde `est = estrictos(ctx, ml)` hasta el
  cierre.
  - `proveedor_real` usa del contexto solo `ctx.inp.national`.
  - `estrictos` enumera los candidatos de los dominios estrictos.
  - `calc_lambda` y `conexion_lambda` llaman a `macro.bridge` por estado.
- **Productos y cierre**: `producto` y `fin` dan el esquema de
  `resultado.json` y las condiciones de «completa» o «incompleta».

La validación es `validar_lote.py` del lote 2, en modo `produccion` y con el
anexo nacional. Revisa:
- el esquema, el recuento y la huella de cada producto, y la identidad del
  núcleo (NUCLEO_DE_OTRA_IDENTIDAD);
- en ELAST, la cobertura de nodos, las identidades con su tolerancia
  interna T1, los motivos de auditoría y la topología. En el suplemento,
  que los campos históricos no cambien y que la procedencia sea coherente;
- en LAMBDA, la identidad K1/Q = 1/(λ·g), los testigos, θ_W y la cobertura
  nacional exacta.

## Núcleo C0

- Trabajador y validador exigen la instalación del candidato C0 (rem116),
  de 121 archivos e identidad d0bf5cd6….
- Se copia solo `src/paper2b`, 37 archivos, a `nucleo_s6/c0/src/paper2b`.
  Los otros 84 figuran en el inventario declarado (`fuentes_fam05.json`)
  con su huella y no se copian: 68 son iguales a los de
  `nucleo_s6/instalacion` y 5 contienen rutas personales. Ninguno se lee al
  ejecutar.
- La identidad se recalcula desde el inventario (NUCLEO-C0-v1): los
  archivos copiados deben ser exactamente los declarados, con sus bytes.
- Frente al núcleo de FAM04, `src/paper2b` coincide en 36 de 37 archivos y
  difiere en `model.py`. Por eso FAM05 no usa el núcleo de FAM04.
- `preparar` comprueba antes de calcular que `paper2b` se importa de
  `nucleo_s6/c0` (NUCLEO_NO_ES_C0). En el piloto 3 y la verificación, el
  registro `paper2b_importado_de` lo confirma: solo `nucleo_s6/c0`. Los
  pilotos 1 y 2 son anteriores a ese registro, pero pasaron por la misma
  comprobación.

## Extracción

`extraccion/extraer_fam05.py copiar <raíz original> [<libro rem121>]` deja 54
piezas en `fuentes_fam05.json`, con origen, huella y papel, y sin rutas
absolutas:
- **código** (`nucleo_s6/lote2/`): `tarea_lote.py` (dca9d79b…),
  `conexion_lambda.py` (9dbdc732…) y `conexion_frontera.py` (4fb1915d…),
  que son U14, y `validar_lote.py` (d95e2beb…), que es U15. Son los objetos
  del catálogo;
- **núcleo C0**: los 37 archivos de `src/paper2b`;
- **entradas** (`datos/fam05/`):
  - `LOTE2_MANIFIESTO.json` (b1cf8af5…, objeto del catálogo); la selección
    no se re-ejecuta;
  - `COBERTURA_NACIONAL_LOTE2.json` (5bea5153…);
  - el paquete rem119, que conserva el nombre `PAQUETE_LOTE1.json`
    (265c29f4…);
  - `alcance_lote2.json` (ca5afe75…, objeto del catálogo).

  El paquete y el alcance solo cruzan huellas; ninguno es una puerta;
- **fuente del suplemento**: `frontier_result.jsonl` del lote 1
  (P_elast_lote1, dba33b47…), en `datos/fam05/fuente_suplemento/` bajo la
  ruta relativa que declara el manifiesto. Las 70 filas históricas son
  entradas permitidas;
- **referencias** (`referencias/fam05/rem120/<tarea>/`): `resultado.json`,
  la salida de validación y los productos de la ejecución aceptada rem120.
  Los tres productos son byte a byte los objetos del catálogo (007095a9…,
  d6a12af3… y c3ba21a3…);
- `datos/fam05/pilotos.json`, dato nuevo de esta base (sin resultados).

**Libro rem121.** Se usó solo para extraer, nunca al ejecutar.
`fuentes_fam05.json` guarda un resumen sin rutas (a33c0029…): productos,
recuentos, alias y alcance de la decisión. `fam05-comprobar` coteja 12
recuentos del libro con los archivos, y todos coinciden. Los 572 alias son
los del manifiesto.

**Rutas.** Las 54 piezas tienen 0 rutas personales, así que ninguna copia
pública necesitó saneamiento. Los 5 archivos de C0 con rutas personales ni
se copian ni se usan; solo figuran con su huella en el inventario de
identidad.

## Entradas reutilizadas y regeneradas (F1)

- **Se reutiliza**:
  - la selección del lote (el manifiesto);
  - el anexo de cobertura nacional (preparado hasta la selección y la
    enumeración estructural, sin λπ);
  - las 70 filas numéricas aceptadas del lote 1 (fuente autenticada, sin
    recalcular);
  - el núcleo C0, y el D7, los contratos y los datos nacionales de FAM01.
- **Se genera de nuevo**:
  - las filas de las 393 mallas nuevas, con su topología;
  - la topología de las 70 filas del suplemento y su procedencia;
  - las 24 envolventes λπ de los 12 pares (488 llamadas a `macro.bridge`).
- **Solo para comparar**: los productos y resultados rem120. Durante el
  cálculo no se leyó ninguna referencia.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1. Siguen el patrón listar /
comprobar, unidad, validar, comparar y receta:

```text
reproducir.py fam05-listar    --salida salidas/fam05/listar_01.json
reproducir.py fam05-comprobar --salida salidas/fam05/comprobar_02.json
reproducir.py fam05-unidad    --tarea L1-ELAST  --unidad FRN:0163dbf31c02c91fe7e4c79dd86b7582200a4b7d --salida salidas/fam05/piloto_01/L1-ELAST
reproducir.py fam05-unidad    --tarea L1-LAMBDA --unidad "CMP-E1.macro|COL"   --salida salidas/fam05/piloto_02/L1-LAMBDA
reproducir.py fam05-unidad    --tarea L1-LAMBDA --unidad "PER-E0E3.macro|PER" --salida salidas/fam05/piloto_03/L1-LAMBDA
reproducir.py fam05-unidad    --tarea L1-ELAST  --unidad SUPLEMENTO --salida salidas/fam05/verificacion_hist_01/L1-ELAST
reproducir.py fam05-validar   --nueva salidas/fam05/piloto_01/L1-ELAST --salida salidas/fam05/piloto_01/L1-ELAST.validacion.json
reproducir.py fam05-comparar  --tarea L1-ELAST --nueva salidas/fam05/piloto_01/L1-ELAST --validacion salidas/fam05/piloto_01/L1-ELAST.validacion.json --salida salidas/fam05/piloto_01/L1-ELAST.comparacion.json
reproducir.py fam05-receta    --salida salidas/fam05/receta_01.json
```

- **Sin cálculo científico**: `fam05-listar`, `fam05-comprobar`,
  `fam05-validar`, `fam05-comparar` y `fam05-receta`.
- **`fam05-unidad`**: sin `--unidad` calcula la tarea completa. Con
  `--unidad`, calcula una unidad completa: una malla nueva, la unidad
  SUPLEMENTO (las 6 mallas van juntas, porque la fuente se autentica por
  sus 70 filas) o un par con sus dos variantes.
  - Una malla del suplemento suelta no se admite.
  - Se niega antes de crear la carpeta si falta o cambió una dependencia o
    si el núcleo C0 no tiene su identidad.
  - Exige `PYTHONHASHSEED=0` efectivo.
- **Separación**: cálculo, validación y comparación son pasos aparte, y
  cada uno termina con 0 solo en su caso aceptado.

`fam05-comprobar` da `cumple` en 0,74 s. Comprueba:
- las 54 fuentes;
- la procedencia: código, validador, manifiesto, anexo, identidad C0 y D7
  iguales al alcance; piezas y suplemento iguales al paquete; anexo ligado
  al manifiesto, sin evaluar λπ y de esta conexión; despliegue del alcance
  (f293a0a6…, el mismo de FAM04, no copiado); alcance no oficial y con las
  dos tareas; fuente del suplemento igual al objeto del catálogo;
- el núcleo C0: identidad recalculada, 121 en el inventario y 37 copiados;
- la cobertura del manifiesto completo, incluido el total de puntos que la
  selección omite;
- los recuentos del libro rem121;
- las referencias y su revalidación: `completa_validada`, 0 fallos e igual
  a la validación histórica guardada;
- los pilotos y la receta.

## Comparación (COMPARACION-FAM05-v1)

`fam05-comparar` compara la salida nueva con la ejecución aceptada rem120,
limitada a la selección registrada en `ejecucion.json`. La base es la de
FAM04:
- **Requisitos previos**: tarea y selección coherentes; validación de esos
  mismos bytes y aceptada (VALIDACION_AUSENTE, VALIDACION_DE_OTROS_BYTES,
  VALIDACION_NO_ACEPTADA); cálculo completo.
- **Productos**, por fila y puntero:
  - cobertura, discretos con precedencia (CR-DISCRETOS) y numéricos exactos
    (CR-HASH-CANONICO);
  - `resultado.json`: tarea, modo, sintético, estado, motivo y tope;
  - identidades del manifiesto, del código y del núcleo C0.

Añade lo propio de FAM05:
- **Referencia por identificador**: cada producto de referencia debe tener
  la huella de su producto en el catálogo:
  - `frontier_result` → P_elast_lote2;
  - la procedencia → L_rem121:suplemento_procedencia.jsonl;
  - `lambda_envolvente` → P_lambda_lote2.

  No basta el nombre de archivo, porque el `frontier_result` del lote 1
  también está en el catálogo como fuente del suplemento. Si se usa como
  referencia, el resultado es REFERENCIA_ALTERADA_O_AJENA.
- **VINCULO-PROCEDENCIA-v1**: el campo `frontier_result_sha256` de cada
  fila de procedencia apunta al `frontier_result` de su propia ejecución.
  - Por eso no se compara como valor: se comprueba aparte que cada fila
    nueva apunte al producto nuevo y cada fila de referencia al de
    referencia.
  - La diferencia queda visible en el informe (`vinculo` y
    `lineas_identicas: false`).
  - Si el vínculo no se cumple, el resultado es VINCULO_DE_PROCEDENCIA_ROTO.
- **Reutilización** (F05-ELAST-HIST): cada una de las 70 filas nuevas del
  suplemento debe igualar a su fila de la fuente campo a campo, con
  `topology` como único campo añadido (FILAS_HISTORICAS_ALTERADAS si no).
- **Derivados LAMBDA**: llamadas a `macro.bridge` y estados por extremo
  frente al anexo (COBERTURA_NACIONAL_DISTINTA_DEL_ANEXO).
- **Operativo**: `pared_s`, solo informado.

No se aplica CR-OBJETO-OTRO-ENTORNO (el entorno es el mismo) ni se comparan
valores con el núcleo de FAM04. La tolerancia T1 del validador no se
convierte en tolerancia de reproducción: un cambio de 1 ulp lo admite el
validador y lo rechaza la comparación (ver controles).

## Pilotos (cálculo autorizado)

**Regla de elección.** Los pilotos se fijaron por identificador desde el
manifiesto antes de calcular, sin mirar resultados
(`datos/fam05/pilotos.json`):
- **ELAST**: la primera malla nueva bidimensional, sin
  `suplemento_topologia`, en el orden del manifiesto. Es
  `FRN:0163dbf3…`, de la frontera N\|df, con 25 nodos.
- **LAMBDA no estricto**: el primer par de dominio publicado
  (CMP-E1.macro\|COL).
- **LAMBDA estricto**: el primer par PER-E0E3 (PER-E0E3.macro\|PER).
- **Verificación histórica**: la unidad SUPLEMENTO, sin recalcular valores.

**Ejecución.** Un proceso a la vez, con el supervisor que termina el árbol
de procesos y un límite externo de 600 s por invocación. El tope interno de
la tarea es 2280 s (= 2400 − 120), como en la producción.

| Piloto | Unidad | Filas | Pared (supervisor) | Dentro de la tarea | Memoria | Validación | Comparación |
|---|---|---|---|---|---|---|---|
| 1 ELAST | `FRN:0163dbf3…` (N\|df, 25 nodos) | 25 | 0,92 s | 0,24 s (sentencias de la tarea 0,01 s) | 53 MB | 0,40 s | 0,21 s |
| 2 LAMBDA | CMP-E1.macro\|COL (con y sin, 9 estados) | 2 | 1,50 s | 0,98 s (contexto 0,74 s; sentencias 0,01 s) | 78 MB | 0,38 s | 0,20 s |
| 3 LAMBDA estricto | PER-E0E3.macro\|PER (con y sin, 32 candidatos) | 2 | 1,50 s | 0,99 s (contexto 0,73 s; sentencias 0,01 s) | 77 MB | 0,39 s | 0,19 s |
| Verificación | SUPLEMENTO (6 mallas, 70 filas reutilizadas) | 70 + 70 | 0,91 s | 0,25 s (sentencias 0,03 s) | 53 MB | 0,40 s | 0,25 s |

En LAMBDA, entre el contexto y las sentencias de la tarea se cuenta además
el cotejo del contexto con el anexo.

**Resultados.** Los cuatro quedan `completa_validada`, con 0 fallos, y la
comparación los acepta:
- 0 diferencias discretas y 0 numéricas;
- tarea, estado, motivo y tope, iguales.

Por piloto:
- **1 ELAST**: líneas idénticas a la referencia. El `reason_code` es
  BASE_NONPOSITIVE en 20 filas, SP_LIMIT_AT_ZERO_RATE en 1 y ninguno en 4.
- **2 LAMBDA**: líneas idénticas a la referencia, con 36 llamadas a
  `macro.bridge` y los 9 estados del anexo, en huella y orden.
- **3 LAMBDA estricto**: líneas idénticas a la referencia, con 128 llamadas
  y los 32 candidatos. Antes de calcular, el contexto confirmó una
  definición única, igual a la del manifiesto y a la del anexo, con 128
  vértices de caja, signo no negativo y las mismas huellas.
- **Verificación**:
  - las 70 filas de `frontier_result` son idénticas a la referencia;
  - las 70 de procedencia son iguales salvo el vínculo, que en cada lado
    está ligado a su propio producto (70/70). La nueva apunta a bb92b872…,
    el `frontier_result` de esta unidad, y la referencia a 007095a9…;
  - la reutilización es exacta en las 70 filas, con solo la topología
    añadida;
  - la compatibilidad del estencil se cumplió en las 6 mallas.

**Testigos y θ_W.** En los dos pares, la variante sin tiene el testigo de
λ_max en θ_W = 0 y la variante con lo tiene en θ_W = −1/5. El mínimo está en
θ_W = 1 en ambas variantes. Se ejercitan así las dos variantes, los dos
extremos, los dos tipos de dominio y la frontera θ_W = 0.

**Lecturas** (rastro desde el inicio de la invocación):

| Unidad | Archivos del paquete | Archivos del venv (numpy 2.0.2) |
|---|---|---|
| Piloto 1 y verificación | 48 cada uno | 0 |
| Piloto 2 | 293 | 110 |
| Piloto 3 | 294 | 110 |

En los cuatro casos: 0 fuera del paquete y del intérprete, 0 sin declarar y
0 referencias.
- En LAMBDA, 37 de las lecturas son archivos de `nucleo_s6/raiz/src`, que
  el contexto de FAM01 lee para calcular la huella de su `code_manifest`
  (identidad técnica documental), no para importarlos.
- `fuente_del_suplemento_leida` vale `true` en todas las unidades. La
  comprobación previa de dependencias calcula la huella de todas las piezas
  declaradas; solo la unidad SUPLEMENTO usa la fuente en el cálculo.

**Duración.** La ejecución histórica registró `pared_s` de 1,45 s para todo
L1-ELAST y de 149,75 s para todo L1-LAMBDA (12 pares). Aquí un par tardó
alrededor de 1 s dentro de la tarea. Esa diferencia no se investigó; no es
criterio científico ni permite estimar el lote. La comparación no usa el
reloj.

## Controles (`local/pruebas_fam05.py`, sin cálculo científico)

`controles_01.json`: 23/23 conformes, 13,0 s en una sola invocación del
supervisor. No se recalculó ninguna malla ni envolvente: se validan y
comparan bytes guardados. Las copias alteradas recalculan solo la huella
del producto, para que cambie únicamente la ciencia.

- **Diferencial del validador** (5): `validar_lote.py` original, sin
  cambios y en proceso aparte, frente a VALIDADOR-v2 sin selección. Mismo
  código y mismo veredicto en:
  - las referencias rem120 de ELAST y de LAMBDA (aceptadas, código 0);
  - ELAST con una fila histórica del suplemento alterada (R + 1 ulp):
    SUPLEMENTO_CAMPO_HISTORICO_ALTERADO y
    SUPLEMENTO_PROCEDENCIA_INCOHERENTE, código 4;
  - LAMBDA con un candidato estricto menos: COBERTURA_NACIONAL_INEXACTA,
    código 4;
  - LAMBDA sin anexo: COBERTURA_NACIONAL_SIN_ANEXO, código 4.
- **Valor alterado en 1 ulp** (2): `B_d` de la fila P0000_0000 del piloto
  ELAST. La validación lo admite (código 0, T1); la comparación lo rechaza
  con DIFERENCIA_NUMERICA en `/B_d`.
- **λ_max estricto alterado** (1): numerador + 1 en PER-E0E3.macro\|PER.
  La validación lo rechaza (IDENTIDAD_K1Q y TESTIGO_NACIONAL) y la
  comparación también (VALIDACION_NO_ACEPTADA y DIFERENCIA_NUMERICA).
- **Referencia ajena** (1): la referencia ELAST sustituida por el
  `frontier_result` del lote 1 da REFERENCIA_ALTERADA_O_AJENA.
- **Par mal declarado** (1): el piloto PER-E0E3.macro declarado como
  PER-E0E3.micro. La validación da COBERTURA_LAMBDA y la comparación,
  COBERTURA_DISTINTA.
- **Validación ausente** (1): VALIDACION_AUSENTE (unidad SUPLEMENTO).
- **Candidato estricto omitido** (1): sin el último de los 32 en el mínimo
  de la variante sin. La validación da COBERTURA_NACIONAL_INEXACTA (32 → 31)
  y la comparación, DIFERENCIA_DISCRETA y
  COBERTURA_NACIONAL_DISTINTA_DEL_ANEXO. El resto no se acepta.
- **Sin anexo** (1): el par publicado da COBERTURA_NACIONAL_SIN_ANEXO.
- **Fila histórica alterada** (1): R de 0 a 5e-324 en una fila del
  suplemento.
  - La validación da SUPLEMENTO_CAMPO_HISTORICO_ALTERADO.
  - La comparación da DIFERENCIA_NUMERICA en `/R`,
    VINCULO_DE_PROCEDENCIA_ROTO y FILAS_HISTORICAS_ALTERADAS.
- **Procedencia con otra identidad de núcleo** (1): la validación da
  SUPLEMENTO_PROCEDENCIA_INCOHERENTE, y la comparación, DIFERENCIA_DISCRETA
  en `/instalacion_identidad`.
- **Otra carpeta** (8): una copia fuera del paquete, con el mismo
  intérprete.
  - `fam05-comprobar` cumple.
  - Los tres pilotos y la verificación guardados se validan y se aceptan
    sin calcular.
  - Al retirar `conexion_frontera.py`, `fam05-comprobar` lo informa y
    `fam05-unidad` se niega con DEPENDENCIA_AUSENTE_O_ALTERADA sin crear la
    carpeta.
  - Con un byte añadido a `model.py` de C0, la validación da
    NUCLEO_DE_OTRA_IDENTIDAD y `fam05-unidad` se niega sin crear la
    carpeta.

**Límite del diferencial.** La identidad de la instalación C0 completa no
se recalcula desde sus 84 archivos no copiados. El original y el adaptado
usan el mismo módulo de identidad (NUCLEO-C0-v1), que la calcula desde el
inventario declarado y los 37 archivos copiados.

**Regresión** del código compartido (`reproducir.py`), sin recalcular:
- `revisar` conforme (0,17 s);
- `fam01-comprobar` cumple (9,3 s);
- `fam02-comprobar` cumple (5,1 s);
- `fam03-comprobar` cumple (1,2 s);
- `fam04-comprobar` cumple (0,7 s);
- salidas en `salidas/fam05/regresion_*.json`.

Tras actualizar el catálogo se repitieron `revisar` y `fam05-comprobar`
(`comprobar_02`, igual a `comprobar_01` salvo el tiempo). El resumen del
supervisor de cada invocación (código, segundos, CPU, memoria e hijos
vivos) está en `salidas/fam05/lanzador.txt`, sin rutas.

## Correcciones rutinarias de esta sesión

Ninguna cambió la ciencia ni los criterios:
- **Referencia por nombre**: la primera versión elegía la referencia por
  nombre de archivo y habría aceptado el `frontier_result` del lote 1.
  Ahora se elige por identificador de producto del catálogo; un control lo
  cubre.
- **Recuentos del libro**: se comparaban las filas nuevas con los nodos;
  ahora se comparan con las filas de las referencias (12 pares explícitos).
- **Clasificación de lecturas**: el piloto 2 guardó las 37 lecturas de
  huella de `nucleo_s6/raiz/src` bajo la clave `nucleo_de_otra_instalacion`,
  que sugería una importación. La clave pasó a ser
  `src_de_otra_raiz_leidos`, con nota, y se añadió
  `nucleo.paper2b_importado_de`.
  - El piloto 2 no se repitió: sus productos y su comparación no dependen
    de ese campo. Su `ejecucion.json` conserva la clave antigua.
  - El piloto 1 y el 2 no llevan `paper2b_importado_de`.
- **Primera ejecución de los controles**: 18/23. Las rutas relativas,
  resueltas desde otra carpeta de trabajo, duplicaban la ruta del guion
  original, y el informe guardaba el stderr con rutas absolutas. Ahora usa
  rutas resueltas y no guarda el stderr. Se borró esa salida y se repitió:
  23/23.
- **Etiqueta de un control**: el texto esperado del caso `model.py`
  indicaba «rc 4», que es el código del validador; la orden
  `fam05-validar` sale con 1. Se corrigió el texto en
  `local/pruebas_fam05.py`. `controles_01.json` conserva la etiqueta
  antigua; la condición comprobada era la correcta.

## Adaptaciones de interfaz

No cambian fórmulas, mallas, tolerancias, topes, presupuestos ni criterios.
Están declaradas en `src/fam05.py`:
- **TAREA-AST-v2**: `tarea_lote.py` tiene código de entrada al nivel
  superior, así que no se importa. Se compilan desde sus bytes exactos, con
  sus números de línea:
  - las funciones `dom_manifiesto`, `proveedor_real`, `estrictos`,
    `calc_lambda`, `fuente_suplemento`, `calc_elast`, `producto` y `tope`;
  - las sentencias de producción de cada tarea, sin la rama
    `hasta-seleccion`.

  A diferencia de FAM04, también se compilan las sentencias. En el lote 2,
  los proveedores de los dominios estrictos y el bloqueo del suplemento
  incompatible (SUPLEMENTO_INCOMPATIBLE_CON_EL_NUCLEO) están en ellas, no
  en funciones.
- **FIN-v1**: `fin` devuelve estado, motivo y campos al adaptador en lugar
  de escribir `--resultado` y salir. El adaptador escribe `resultado.json`
  con el mismo esquema.
- **PUERTA-v1**: la puerta de producción (alcance más la decisión humana
  nativa) no se ejecuta ni se reconstruye. Los pilotos los autoriza este
  encargo; el lote, el Paso 3. Se usa `modo = produccion`, el que exige el
  validador, con la etiqueta «REPRODUCCION LIMPIA FAM05 NO OFICIAL».
- **CONTEXTO-FAM05-v1** (solo LAMBDA): en lugar del contexto del despliegue
  operativo (f293a0a6…), se usa `fam01.Contexto` con `run_class =
  paso4_operativo_s6` y el núcleo C0 delante. La ruta usa solo
  `ctx.inp.national`. Antes de calcular se informa, sin evaluar λπ, que sus
  estados reproducen el anexo.
- **NUCLEO-C0-v1**: `aprobacion_alcance.identidad_instalacion`, que
  trabajador y validador usan solo para la identidad de la instalación, se
  sirve con un módulo mínimo del mismo nombre. Comprueba que los archivos
  copiados son los del inventario y devuelve su identidad canónica, con la
  misma fórmula. Otro contenido da otra identidad: el validador da
  NUCLEO_DE_OTRA_IDENTIDAD y el cálculo no empieza.
- **RUTA-SUPLEMENTO-v1**: la raíz de las rutas relativas del manifiesto es
  `datos/fam05/fuente_suplemento`. La fuente se sigue autenticando por su
  huella.
- **SELECCION-UNIDAD-v1**: una unidad se calcula pasando a la ruta la parte
  del manifiesto de esa unidad completa.
- **VALIDADOR-v2**: `validar_lote.py` se ejecuta como guion desde sus bytes
  exactos, con 6 sustituciones declaradas, cada una presente una sola vez:
  - NUCLEO-C0-v1, la ubicación del núcleo;
  - SEL-ARGUMENTO, SEL-LAMBDA, SEL-ELAST, SEL-ELAST-TOTAL y
    SEL-SUPLEMENTO, la selección opcional.

  Sin selección se comporta como el original (diferencial de los
  controles). El total de puntos que la selección omite lo comprueba
  `fam05-comprobar`.
- **RELOJ-PILOTO-v1**: reloj interno = tope de trabajo − holgura del
  conductor (2400 − 120 = 2280 s). El límite externo lo pone el supervisor;
  si se agota, la tarea queda incompleta y nada se reduce.

No se trasladaron por analogía los 9 estados de FAM04: los estados de cada
par salen del anexo del lote 2.

## Límites

- **Cobertura de los pilotos**: 1 de 393 mallas nuevas y 2 de 12 pares. El
  resto del lote no tiene cálculo en esta base. El suplemento está
  verificado entero, pero no recalculado.
- **Kinks**: la referencia no tiene ninguno, así que las filas laterales
  (left/right_limit) no se ejercitan con un kink real. La regla está en los
  bytes exactos del trabajador y del validador.
- **Estencil**: la compatibilidad se cumplió en las 6 mallas del
  suplemento. La rama de incompatibilidad (SUPLEMENTO_INCOMPATIBLE_CON_EL_NUCLEO,
  que no combina ni publica) no se ejercita; se conserva en los bytes
  exactos.
- **Contexto**: su identidad (bf0103ed…) difiere de la que registra el
  anexo (5273718d…), porque se construye en esta base (CONTEXTO-FAM05-v1)
  y no con el despliegue histórico. Lo que usa la ruta son los estados
  nacionales, y coinciden con el anexo en huellas; en los estrictos,
  también en definición y enumeración.
- **Selección**: los pilotos se validan con la selección (VALIDADOR-v2). La
  validación sin selección es la del original y se comprobó sobre las
  referencias, no sobre un cálculo nuevo del lote.
- **Puerta**: sin puerta ni decisión de producción (PUERTA-v1); las salidas
  son no oficiales.
- **Traslado**: probado en esta máquina, con el mismo intérprete. El
  aislamiento efectivo queda para 2.4.2.
- **F2**: no se extiende a FAM05. La regla de FAM05 no la necesita; se
  informa en `ejecucion.json` (equivalente).
- **Rutas**: las salidas de FAM05 registran rutas relativas, con 0 rutas
  personales. El resumen del supervisor se guardó sin rutas.

## Receta completa (preparada, no ejecutada)

`salidas/fam05/receta_01.json`:
- **Orden**: L1-ELAST → L1-LAMBDA. Son 399 mallas (393 nuevas y el
  suplemento), 4.195 filas y 572 fronteras, y 12 pares con 24 filas y 488
  llamadas a `macro.bridge`.
- **Órdenes**: cada tarea con `fam05-unidad`, `fam05-validar` y
  `fam05-comparar`, precedidas de `fam05-comprobar`.
- **Ejecución**: una tarea a la vez, sin reintentos, con un tope de trabajo
  de 2400 s por tarea (reloj interno de 2280 s) y 300 s de validación, con
  el mismo supervisor.
- **Parada**: si una tarea no queda completa y validada, no se lanza la
  siguiente.
- **Duración**: no se promete; los pilotos no permiten estimarla.

## Propuesta de cierre

Propongo cerrar la **preparación** de FAM05 en su alcance:
- código, núcleo C0, entradas, fuente del suplemento y referencias están
  dentro del paquete, sin rutas personales;
- cálculo, validación y comparación están conectados para las tres
  operaciones, con la receta completa lista;
- los criterios científicos, la regla del estencil, la cobertura nacional
  exacta y la separación entre lo calculado y lo reutilizado se conservan.

Los **pilotos** (tres calculados y la verificación del suplemento) quedan
aceptados con igualdad exacta. La **reproducción completa** del lote 2 no
está hecha: pertenece al Paso 3 y requiere su autorización.

## Siguiente trabajo

- Preparación revisada y cerrada en alcance por Codex; detalle abajo.
- La ejecución del lote completo pertenece al Paso 3.
- El aislamiento efectivo de FAM05 queda para 2.4.2.
- FAM06 (E4) no se abre sin encargo. COORD del lote 2 es FAM07.

## Revisión de Codex — 2026-11-16

Preparación de FAM05 cerrada en su alcance. Se aceptan los tres pilotos y
la verificación del suplemento. El lote completo sigue pendiente del Paso 3.

Se revisaron las rutas efectivas, las adaptaciones del validador y la
comparación. El cotejo independiente, sin ejecutar cálculos científicos,
comprobó las 54 fuentes y los tres productos de referencia. Autenticó el
inventario C0 de 121 archivos contra su identidad fijada y comprobó los 37
archivos copiados, cuyo único cambio respecto al núcleo de FAM04 es
`model.py`. Esto acredita el núcleo extraído; no afirma que los 121 archivos
estén instalados en la base limpia.

Las 25 filas ELAST del piloto y las dos filas de cada piloto LAMBDA son
idénticas a su selección en rem120. Cada extremo de ambas variantes
conserva los 9 estados publicados o los 32 candidatos estrictos del anexo,
con las mismas huellas y orden. En ambas variantes «sin», el máximo tiene
theta_W = 0.

El suplemento conserva exactamente las 70 filas numéricas de su fuente,
añadiendo solo topología. Sus 70 filas de procedencia coinciden salvo el
enlace con su propio `frontier_result`, comprobado en ambos lados. Una copia
con ese enlace alterado se rechazó por VINCULO_DE_PROCEDENCIA_ROTO, aun
actualizando la huella del producto en el resultado.

`fam05-comprobar` y la nueva validación y comparación de las cuatro
unidades guardadas resultaron conformes. Se revisaron los 23 controles
guardados, incluida la separación entre T1 del validador e igualdad exacta
del comparador. No se modificaron código, datos, referencias ni salidas del
ejecutor. El cotejo está en `local/revision_codex_fam05/resumen.json`.

Los nombres antiguos de campos y la etiqueta de código de salida declarados
no cambian los resultados comprobados. Los límites de kinks y estencil
incompatible permanecen documentados. Quedan la instalación realmente
aislada (2.4.2) y la ejecución completa autorizada; no se extiende F2 ni se
abre otra familia en esta revisión.
