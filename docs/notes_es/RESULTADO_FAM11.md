# RESULTADO FAM11 — COV (26 techos bajo φ/2) y COV12 (B1/B2)

Fecha: 2026-11-17 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original y los libros se consultaron en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Revisada y cerrada en su alcance por Codex. El dictamen figura al final del informe. Están en el paquete los cinco guiones COV y las ocho piezas B1/B2 (copias exactas o proyecciones saneadas), las entradas (índices, manifiestos, alcance, cobertura, censo, ENF por afirmación, conciliación aceptada y fuentes de B2), las seis tareas rem151 guardadas como entradas, las referencias rem151/rem166/rem169/rem170 y la receta completa. El núcleo C0 de FAM05 y el conciliador COV de FAM12 se reutilizan. Cálculo, validación, enlace B1 → B2, ensamblado, conciliación y comparación están conectados. |
| F11-COV26 (RN) | Piloto ABL-COV-T1 completo (18 techos, 1.438 comparaciones) calculado, validado (`completa_validada`) y aceptado. Comparaciones idénticas byte a byte (3b5a877a…); techos sin diferencias científicas (huella derivada e4dd80c7… = referencia). T2–T6 no se calcularon. Ensamblado (1.724 celdas) y conciliación (1.728 afirmaciones) regenerados sobre las seis guardadas, con productos idénticos; la conexión mixta (T1 nueva + T2–T6 guardadas) se acepta. |
| F11-B1 (RN) | Piloto completo (su única solicitud) calculado, validado y aceptado: U_C2 = 0x1.628ed46d42e18p-3, igual a la referencia, y las doce afirmaciones `candidato_B2`. |
| F11-B2 (RN) | Piloto completo sobre el B1 **nuevo** validado (ENLACE-B1-v1), validado y aceptado: 1.920 contextos, 480 puentes y 60 Q; L_K1 y G_hi de los seis grupos iguales a rem170; las doce `robust_infeasible`, igual que la resolución aceptada, con las categorías padre intactas. |
| Reproducción completa | Pendiente (Paso 3). La receta está preparada y no se ha lanzado. |

Los pilotos cubren 18 de los 26 techos (T1, con 1.438 de las 1.724 celdas)
y B1 y B2 enteros. COL-2024p queda fuera del nivel en COV (pendiente por
falta de testigos, no NA), pero pertenece al soporte E2 de la cota B2. No
se tratan los 16 casos mexicanos, la causalidad ni un orden de canales; la
integración en la síntesis corresponde a FAM10. No se ha abierto otra
familia.

## Alcance

| Operación | Unidades | Referencia |
|---|---|---|
| F11-COV26 (RN) | seis tareas ABL-COV-T1…T6 (26 techos: T1 18, T2–T4 2 cada una, T5 y T6 1), ensamblado de 1.724 celdas y conciliación de 1.728 afirmaciones | tareas rem151 (guardadas); ensamblado y conciliación rem151/rem152: `cov_techos_ensamblados.jsonl` 0bae15d4…, `cov_comparacion_ensamblada.jsonl` cad40d17…, `CONCILIACION_COV.jsonl` 5ba01423…, `CONCILIACION_COV.json` 927e77aa… |
| F11-B1 (RN) | una solicitud `c2_normalizado` sobre la raíz D7 COV (diseño G, menú f); 12 afirmaciones en seis grupos | producción rem166 (estado, evidencia, validación y lectura; proyecciones) y libro rem167 |
| F11-B2 (RN) | cota inferior global L_K1 de K1…K6 con la forma acoplada; 12 afirmaciones | producción rem169 (proyecciones) y resolución rem170 (`COV12_RESOLUCION_GLOBAL.jsonl`) |

**Recuentos confirmados** desde los manifiestos y los productos, sin calcular:
- 26 claves (0 reutilizadas); 1.724 celdas (PER 960, COL 574, MEX 190);
  1.728 afirmaciones ENF;
- 26 techos cerrados en la escala normalizada (error ≤ 1e-7). Los 8 con
  error_R > 1e-7 están todos en T1 y no se rechazan por eso;
- conciliación: 1.693 `inconclusa_preservada`, 28
  `no_decidida_por_testigos`, 3 `parcial_no_robusta_factible` y 4
  `parcial_no_robusta_infactible`. En el padre hay 1.712 inconclusas y 16
  robustas. Los 20 cambios de signo certificados no son cambios de categoría;
- B2:
  - contextos: 4.608 antes de deduplicar, 2.304 sumados por grupo (K1 192,
    K2 192, K3 864, K4 864, K5 96, K6 96) y 1.920 efectivos;
  - 480 puentes y 60 Q;
  - grupos solapados: K5 ⊂ K1∩K3 y K6 ⊂ K2∩K4;
  - soporte E2 con 2023p, 2024p y pub;
- fuera del nivel en COV: COL-E2-2023.2024p macro y micro, «pendiente (sin
  testigos), no NA».

**Identidades de partida**, iguales al catálogo:
- COV: índice cd197300…, manifiesto a38f9e95…;
- B1: índice 9244a279…, manifiesto 1194923c…;
- B2: índice 5f7ec64b…, manifiesto 0f1582cc….

El núcleo C0 es d0bf5cd6…, con la identidad recalculada.

## Ruta efectiva

- **Techos COV** (`fam11-unidad --tarea ABL-COV-T*`): `tarea_lote.py` del
  paquete COV i5 en modo `produccion`, ejecutada desde sus bytes. Cada
  techo pasa por `conexion_coord_cert.techo` con el núcleo C0. Se
  conservan:
  - φ/2 con las demás entradas del padre;
  - los presupuestos;
  - el cierre normalizado 1e-7 y los errores en las dos escalas;
  - cotas, testigos, garantía, soporte y estados.

  Valida `validar_lote.py` (`validar_coord_rec.validar_tarea`).
- **Ensamblado y conciliación** (`fam11-ensamblar`):
  - `ensamblar_coord.py` recibe una carpeta declarada por tarea, guardada
    o nueva;
  - `src/conciliar_cov.py` (i5, los bytes del índice COV) lee cada tarea
    desde la carpeta que registró el ensamblador.
- **B1** (`fam11-unidad --tarea B1`): `b1_trabajo.py` en su propio proceso,
  con el cierre C0 cargado de `nucleo_s6/c0/src/paper2b`, hace la única
  solicitud del manifiesto.
  - U_C2 es el extremo superior **certificado** del encierro, con redondeo
    hacia afuera; no es un máximo ni un argmax. B1 solo produce
    candidatos.
  - Valida `validar_b1.py`: evidencia, procedencia local y lectura.
- **B2** (`fam11-unidad --tarea B2 --b1 <carpeta> --validacion-b1 <registro>`):
  `b2_trabajo.py` sobre el manifiesto B2 enlazado. Su bloque `b1` sale de
  los bytes del B1 nuevo validado (`MANIFIESTO_B2_ENLAZADO.json`). Usa:
  - la forma acoplada con q exacto y s_Pi;
  - la regla G_hi = U_C2 − L_K1 ≤ −1/100, exacta y con el borde incluido.

  Valida `validar_b2.py`.
- **Resolución de las doce** (en `fam11-comparar --tarea B2`): G_hi exacto
  por grupo y veredicto. La categoría padre y la conclusión COV histórica
  se conservan aparte de la conclusión transformada.

## Extracción

`extraccion/extraer_fam11.py` copia bytes exactos, comprueba los índices de
los tres paquetes y rechaza rutas absolutas. Deja en `fuentes_fam11.json` 84
piezas propias:
- **código** (13):
  - `nucleo_s6/cov/`: `tarea_lote.py`, `conexion_coord_cert.py`,
    `validar_lote.py`, `validar_coord_rec.py` y `ensamblar_coord.py`;
  - `nucleo_s6/b1/`: `b1_trabajo.py`, `validar_b1.py`, `puerta_b1.py` y
    `comun_b1.py`;
  - `nucleo_s6/b2/`: las cuatro piezas equivalentes de B2.
- **índices de los paquetes B** (2): `PAQUETE_B1.json` y `PAQUETE_B2.json`;
- **entradas** (`datos/fam11/`, 17):
  - `cov/` (6): índice, manifiesto, cobertura, alcance, censo rem147 y
    ENF por afirmación;
  - `b1/` y `b2/`: los manifiestos;
  - `fuentes/` (7): conciliación aceptada (entrada de B1), contexto COL por
    grupo, mapa de soporte derivado, plan mínimo, preparación B1/B2,
    `contexto_s6.py` y `preparar_manifiesto_cov.py`;
  - `pilotos.json` y `ejecucion_limpia.json`, datos nuevos sin resultados;
- **salidas aceptadas guardadas** (`datos/fam11/guardadas/cov_rem151/`, 18):
  las seis tareas rem151. Son entradas de la regeneración y referencia de
  la comparación de cálculo;
- **referencias** (`referencias/fam11/`, 34): rem151 (19: tareas,
  ensamblado y conciliación), rem166 (7), rem169 (7) y rem170 (1).

**Proyecciones saneadas** (SANEADO-v1), 16 en total: `comun_b1/comun_b2`,
los índices y manifiestos B1/B2, el mapa derivado, el `ENSAMBLADO.json` de
referencia y los ocho documentos de producción rem166/rem169. Solo se
sustituye la procedencia privada por un marcador. La extracción comprueba
que cada proyección restituye su original al reponerla, y el código
autentica por esa correspondencia.

Se declaran 10 piezas **reutilizadas** sin copiarlas otra vez:
- el conciliador COV (`src/conciliar_cov.py`, de FAM12);
- el censo remanente de FAM08;
- las fuentes D7 (tres), grilla, CA2 (dos) y D6;
- `nacional.py` (fuente declarada de B2; no se ejecuta).

El **núcleo C0** es el de FAM05: 37 archivos, identidad d0bf5cd6….
`contexto_s6.py` (B2 cita su línea 127) está en `datos/fam11/fuentes` y no
en `nucleo_s6/c0`, para no alterar la identidad de su inventario.

**Libros rem152, rem167 y rem170 (y el cruce de afirmaciones de rem170).**
Solo se consultaron para extraer recuentos y huellas; no se leen al
ejecutar y no son dependencias. `fuentes_fam11.json` guarda un resumen sin
rutas ni transcripciones, y `fam11-comprobar` coteja sus 13 recuentos con
los archivos. Hay 18 fuentes de solo procedencia (dictámenes, inventarios),
autenticadas en la extracción y no copiadas. **Rutas:** 0 rutas personales
en las piezas.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1, bajo el supervisor del paquete
fuente (un proceso a la vez):

```text
reproducir.py fam11-listar    --salida salidas/fam11/listar.json
reproducir.py fam11-comprobar --salida salidas/fam11/comprobar_02.json
reproducir.py fam11-unidad    --tarea ABL-COV-T1 --tope 2400 --salida salidas/fam11/piloto_01/ABL-COV-T1
reproducir.py fam11-unidad    --tarea B1 --salida salidas/fam11/piloto_01/B1
reproducir.py fam11-unidad    --tarea B2 --b1 salidas/fam11/piloto_01/B1 --validacion-b1 salidas/fam11/piloto_01/B1.validacion.json --salida salidas/fam11/piloto_01/B2
reproducir.py fam11-validar   --nueva salidas/fam11/piloto_01/<unidad> --salida salidas/fam11/piloto_01/<unidad>.validacion.json
reproducir.py fam11-comparar  --tarea ABL-COV-T1|B1|B2 --nueva salidas/fam11/piloto_01/<unidad> --validacion <archivo> --salida <archivo nuevo>.json
reproducir.py fam11-ensamblar --entrada ABL-COV-T1=guardado … --entrada ABL-COV-T6=guardado --salida salidas/fam11/regeneracion_01
reproducir.py fam11-ensamblar --entrada ABL-COV-T1=salidas/fam11/piloto_01/ABL-COV-T1 (las demás =guardado) --salida salidas/fam11/mixta_01
reproducir.py fam11-comparar  --tarea ENSAMBLADO --nueva <carpeta> --salida <archivo nuevo>.json
reproducir.py fam11-receta    --salida salidas/fam11/receta_01.json
```

- **Sin cálculo científico**: `fam11-listar`, `fam11-comprobar`,
  `fam11-validar`, `fam11-ensamblar` (ensamblado y conciliación de techos ya
  calculados), `fam11-comparar` y `fam11-receta`.
- **`fam11-unidad`**: una tarea COV entera, B1 o B2. Se niega antes de crear
  la carpeta en cualquiera de estos casos:
  - falta o cambió una dependencia;
  - el núcleo C0 no tiene su identidad;
  - `PYTHONHASHSEED=0` no está en efecto.

  B2 exige `--b1` y `--validacion-b1` y no recurre al B1 histórico.
- **Procesos separados**: COV importa C0 como FAM05–FAM08, y B1/B2 cargan
  su cierre C0 sin `paper2b` precargado. Un proceso B se niega si encuentra
  cargados los módulos COV, y al revés.
- **Entradas declaradas**: cada tarea entra con `--entrada
  <tarea>=<carpeta nueva|guardado>`. Una tarea que falta no se sustituye
  por su referencia. Cada salida declara su naturaleza: «regeneración sobre
  entradas guardadas», «conexión mixta» o el cálculo nuevo.

## Adaptaciones (declaradas en `src/fam11.py`)

No cambian fórmulas, claves, tolerancias, presupuestos, garantías ni
criterios. Cada original se sustituye una sola vez:
- **GUION-v1** y **MODULOS-v1** (de FAM07/FAM08): cada pieza se ejecuta
  desde sus bytes exactos con sus sustituciones de texto. Se cargan como
  módulos desde su texto adaptado:
  - `validar_coord_rec`;
  - `comun_b1`/`puerta_b1`;
  - `comun_b2`/`puerta_b2`.
- **NUCLEO-C0-v1**: el núcleo es `nucleo_s6/c0`. **RAIZ-v1** (solo COV):
  la raíz de `tarea_lote` es la base limpia.
- **RUTAS-FUENTES-v1**: toda fuente leída sale de su copia en la base y se
  sigue autenticando por sus bytes. Una lectura no declarada falla.
- **SANEADO-v1** y **RAIZ-MARCADORES-v1**: las proyecciones se autentican
  por la correspondencia proyección → original, y la huella registrada es
  la del original. Los manifiestos B1/B2 se reconstruyen con los marcadores
  de la proyección en las rutas históricas.
- **PUERTA-v1**: no se ejecutan ni se reconstruyen las puertas de
  producción (alcance verificado y decisión humana nativa). El alcance de
  trabajadores y validadores lleva el sha256 de
  `datos/fam11/ejecucion_limpia.json` (1a3ee737…), una declaración NO
  OFICIAL. No hay decisión.
- **PROCEDENCIA-LOCAL-v1**: B1/B2 no tienen área p3ctl. Su fuente de
  ejecución es el registro local de `fam11-unidad`: `ejecucion.json`, con
  la orden relativa, el código de salida y la última línea, más
  `trabajo_stdout.txt`. La validación solo se admite dentro de la misma
  unidad.
- **PAQUETE-v1**: B1/B2 comprueban sus cuatro piezas copiadas contra su
  índice.
- **ENLACE-B1-v1**: B2 consume los bytes del B1 nuevo con dos
  comprobaciones:
  1. el registro de `fam11-validar` aceptado para esos mismos bytes;
  2. una revalidación en el mismo proceso con las funciones del validador
     B1 (procedencia local, `validar_evidencia` y lectura; sin motor), que
     debe dar la misma lectura y los mismos datos validados.

  Si cambia el registro después de enlazar, la validación de B2 se niega.
- **ENSAMBLADOR-ENTRADAS-v1** y **ENTRADAS-CONCILIADOR-v1** (de FAM07): una
  carpeta declarada por tarea. El conciliador lee la carpeta relativa que
  registró el ensamblador.
- **RELOJ-PILOTO-v1** (de FAM05): reloj interno COV de 2280 s; el límite
  externo lo pone el supervisor.

## Comprobación (`fam11-comprobar`, sin cálculo; 1,0 s)

Cumple en todos sus apartados: `comprobar_01.json` con el código final y
`comprobar_02.json` con el código y el catálogo finales.
- **piezas**: 84 propias, 10 reutilizadas, 16 saneadas, 18 de solo
  procedencia y 37 del núcleo C0, con sus huellas. La identidad C0
  recalculada es d0bf5cd6…;
- **procedencia**:
  - código COV igual a su índice y piezas B igual al suyo;
  - índices, manifiestos e identidades iguales al catálogo;
  - guardadas iguales a sus pines y al libro;
  - proyecciones con correspondencia y sustituciones únicas;
  - conciliación aceptada declarada como entrada de B1;
  - declaración de ejecución limpia igual a su regla;
- **reconstrucción B**: los manifiestos B1 y B2 reconstruidos son iguales a
  sus proyecciones (en B2, con el bloque `b1` documental). La cobertura B2
  es conforme y da los recuentos de «Alcance»;
- **motor**, sin calcular: identidad de código, configuración, certificación
  en esta plataforma y garantía iguales a las del manifiesto;
- **cobertura**: 26 claves, 1.724 celdas iguales al censo y 1.728
  afirmaciones ENF autenticadas;
- **revalidación de las guardadas**: T1–T6 `completa_validada`, iguales a la
  validación histórica. Los 26 techos están cerrados en la escala
  normalizada; 8 cierran solo en ella;
- **referencias**: ensamblado, conciliación, B1, B2 y resolución, iguales
  al catálogo;
- **libros**: 13 recuentos de rem152/rem167/rem170 iguales a los archivos;
- **pilotos**: iguales a su regla. La receta tiene 10 pasos.

## Comparación (COMPARACION-FAM11-v1)

Las referencias usan el mismo perfil de entorno y el mismo núcleo C0, así
que la comparación es exacta:
- **CR-HASH-CANONICO**: cada fila y documento, idéntico campo a campo
  (valores, cotas, errores en sus escalas, testigos, intervalos, G_hi
  exactos);
- **CR-DISCRETOS**, con precedencia: claves, celdas, contextos, estados,
  lecturas, veredictos, categorías y recuentos.

Solo se apartan campos concretos, que quedan visibles:
- **OPERATIVO**: duraciones y relojes medidos (`segundos` en COV; en B1/B2,
  `inicio_utc`/`fin_utc`, los tiempos de la solicitud y `segundos_encierro`);
- **UBICACION**: `pieza/ruta` en B1/B2, las rutas `fuentes/b1_*` del
  manifiesto enlazado y, en el ensamblado, carpeta y lanzamiento de cada
  tarea;
- **PUERTA** (solo B1/B2): `puerta_nativa/alcance_sha256` y el bloque
  `procedencia`. En el manifiesto enlazado se apartan también el acto B1
  histórico, su alcance y su libro;
- **VINCULO**: alcance, manifiesto, índice, evidencia, lectura, la huella
  del ensamblado y, en B2, las huellas `b1/*` y `fuentes/b1_*`. Se
  recomprueban en cada lado contra sus propios bytes: la nueva contra los
  suyos y la referencia contra los originales de rem166/rem169.

Las huellas derivadas reponen esos campos desde la referencia, usan el fin
de línea de los bytes nuevos y se comparan con los bytes de la referencia.
La garantía interna de los validadores (encierros, 1e-7 normalizado) es
suya y no se usa como tolerancia de reproducción.

## Pilotos (cálculo autorizado)

**Selección**, fijada por el encargo antes de calcular, en
`datos/fam11/pilotos.json` (8a12e93c…). No se redujo el problema:
1. la tarea ABL-COV-T1 completa (18 claves, 1.438 comparaciones), con
   límite externo de 2.400 s;
2. B1 completo, con su única solicitud y límite de 600 s;
3. B2 completo sobre el B1 nuevo validado del piloto 2, con límite de
   600 s.

Se lanzaron de uno en uno bajo el supervisor, tras comprobar la carga de
la máquina, sin terminar procesos ajenos. No hubo vencimientos.

**ABL-COV-T1** (`piloto_01`): 141,7 s de pared en el supervisor (139,29 s
según la tarea).
- **Validación**: `completa_validada`, igual en contenido a la histórica
  salvo sus propias huellas.
- **Comparación**: aceptada.
  - `cov_comparacion.jsonl`: idéntico byte a byte (3b5a877a…).
  - `cov_techos.jsonl` (b210862c…): 18 techos sin diferencias discretas ni
    numéricas. Se apartan `segundos` y `alcance_sha256`; la huella derivada
    e4dd80c7… es igual a la referencia.
  - 18 techos cerrados en escala normalizada, 8 de ellos con error_R >
    1e-7, como en la referencia.
  - 1.438 comparaciones con G = C2 − K1, cobertura completa y salida del
    trabajador igual salvo `pared_s`.
- **Lecturas**: ninguna salida guardada ni referencia.

**B1** (`piloto_01`): 1,7 s de pared; cálculo de 1,08 s.
- **Evidencia** (6cdfc790…):
  - U_C2 = 0x1.628ed46d42e18p-3 = 779681131038147/4503599627370496,
    igual al libro rem167 y a la referencia;
  - es un extremo superior certificado, no un máximo.
- **Validación**: `validada` (registro ddf92ca0…; VALIDACION_B1 6ef3a028…,
  LECTURA_B1 5567894d…).
- **Lectura**: los seis grupos y las doce afirmaciones son `candidato_B2`,
  con umbrales exactos iguales al libro.
- **Comparación**: aceptada. Los cuatro documentos son iguales salvo lo
  apartado.

**B2** (`piloto_01`): 0,8 s de pared; cálculo de 0,14 s.
- **Enlace**: el B1 de `piloto_01` y su registro de validación, con la
  revalidación conforme (misma lectura y U_C2).
- **Evidencia** (d9ccb840…; lectura 8ac9f8b5…): llamadas `macro.bridge`
  480, `GridCell.Q` 60, `k1_intervalar` 1.920 y C2 nuevo 0.

| Grupo | Contextos | L_K1 (hex) | G_hi exacto | Lectura |
|---|---|---|---|---|
| K1 y K5 | 192 / 96 | 0x1.b98c85d42628dp-3 | −1530361648395381/36028797018963968 (≈ −0,04248) | certifica G negativo |
| K2 y K6 | 192 / 96 | 0x1.b8c3b85c299c6p-3 | −758281298982359/18014398509481984 (≈ −0,04209) | certifica G negativo |
| K3 | 864 | 0x1.b5da2b3dba041p-3 | −1465328706482729/36028797018963968 (≈ −0,04067) | certifica G negativo |
| K4 | 864 | 0x1.b5130c24fe36ap-3 | −725822591589033/18014398509481984 (≈ −0,04029) | certifica G negativo |

Todo G_hi queda bajo −1/100, con un margen mínimo de unas 0,03.

**Resolución de las doce**, igual fila a fila a `COV12_RESOLUCION_GLOBAL`
(rem170) en grupo, categorías, veredicto, G_hi, L_K1, U_C2, margen,
afirmaciones y contextos del grupo:
- veredicto: 12 `robust_infeasible`;
- conjunto padre: `inconclusa`;
- categoría original: `inconclusa_por_testigos_en_tolerancia`;
- conclusión COV histórica: `no_decidida_por_testigos`, que se conserva
  aparte.

El manifiesto enlazado (6e4015f4…) es igual a la proyección salvo el bloque
`b1` (vínculo y puerta) y las rutas de `fuentes/b1_*` (ubicación). La
comparación aceptada es `B2.comparacion.json`.

## Regeneraciones y conexión mixta

**Regeneración sobre entradas guardadas** (`regeneracion_01`): las seis
tareas guardadas, sin cálculo de techos.
- `cov_techos_ensamblados.jsonl` (0bae15d4…),
  `cov_comparacion_ensamblada.jsonl` (cad40d17…) y `CONCILIACION_COV.jsonl`
  (5ba01423…) son idénticos byte a byte a rem151/rem152.
- `ENSAMBLADO.json` y `CONCILIACION_COV.json` son iguales a su referencia
  salvo carpetas, lanzamiento y la huella del ensamblado, que se muestran.
- Recuentos de las 1.728 afirmaciones, iguales a la referencia y al libro:
  1.693 / 28 / 3 / 4.
- Veredictos del ensamblador y del conciliador iguales a los históricos.

**Conexión mixta** (`mixta_01`): T1 de `piloto_01`, validada; T2–T6
guardadas. La salida se declara «conexión mixta» y acredita la conexión
de la T1 nueva, no el cálculo de T2–T6. Resultado: aceptada.
- `cov_techos_ensamblados.jsonl`: las 18 filas de T1 solo difieren en
  `segundos` y `alcance_sha256`. La huella derivada 0bae15d4… es igual a la
  referencia.
- `cov_comparacion_ensamblada.jsonl` y `CONCILIACION_COV.jsonl`: idénticos
  byte a byte.
- Recuentos y veredictos iguales.
- En la conciliación, 20 cambios de signo certificados no cambian la
  categoría.

Ninguna de las dos lee referencias. Solo autentican y usan las guardadas
declaradas como entrada; en la mixta son 15 archivos de T2–T6.

## Controles (`local/pruebas_fam11.py`)

`controles_02.json`: 40/40 conformes en 28,8 s, con el código final y las
copias alteradas en `salidas/fam11/controles_02`. No hay cálculo COV. B1 y
B2 (unos 1 s cada uno) se recalculan solo en la copia de otra carpeta,
como control de portabilidad. Por riesgo:
- **Valor alterado**:
  - en T1, C_2 + 1 ulp con las comparaciones recompuestas da
    DIFERENCIA_NUMERICA en la comparación exacta;
  - en B1, U_C2 + 1 ulp en la evidencia lo rechaza la validación
    (EVIDENCIA_DISTINTA_DE_LA_EJECUCION) y lo rechaza la comparación.
- **Referencia de otra unidad**:
  - T1 comparada como T2 (SALIDA_DE_OTRA_TAREA…);
  - B1 comparado como B2 (SALIDA_DE_OTRA_UNIDAD…);
  - la carpeta de T3 declarada como T2, rechazada por el ensamblador.
- **Validación ausente o de otros bytes**: T1 con la validación de B1, B1
  sin validación y B2 con la validación de B1 no se aceptan.
- **B2 con un B1 distinto o no validado**: cada caso se niega antes de
  calcular y sin crear carpeta:
  - registro no aceptado (VALIDACION_B1_NO_ACEPTADA);
  - evidencia distinta de la validada (VALIDACION_B1_DE_OTROS_BYTES);
  - registro y documentos de validación fabricados de forma coherente con
    una afirmación menos (LECTURA_O_DATOS_B1_DISTINTOS_DE_SU_REVALIDACION);
  - validación de T1 (VALIDACION_DE_OTRA_UNIDAD);
  - carpeta de T1 como B1 (B1_SIN_EJECUCION_FAM11_COMPLETA);
  - sin `--b1` (uso rechazado, código 2);
  - `fuente_b1` sin enlace o con el B1 histórico rem166 (B1_SIN_ENLACE_VALIDADO
    y VALIDACION_B1_NO_ACEPTADA). El histórico no cuenta como B1 validado.

  Además, en la copia, un registro B1 alterado después de enlazar hace que
  la validación de B2 se niegue (ENLACE_B1_DISTINTO_DEL_REGISTRADO).
- **Borde −1/100 con datos inertes**:
  - `comun_b2.regla` certifica con G_hi = −1/100 exacto y no certifica con
    L 10⁻³⁰ menor;
  - `comun_b1.regla` da `candidato_B2` en el borde y `detener` con U 10⁻³⁰
    mayor;
  - la resolución de las doce da `robust_infeasible` en −1/100 exacto y
    `desconocida` por encima, con la categoría padre intacta.
- **Fila o contexto omitido**:
  - un techo de T1 con sus comparaciones (COBERTURA_DE_TECHOS y
    COMPARACIONES_NO_CORRESPONDEN);
  - el ensamblado sin T3, rechazado como incompleto y no sustituido por su
    referencia;
  - una celda del universo COV (ENSAMBLADO_NO_CUBRE_LAS_CELDAS);
  - una clave de K1 en el manifiesto B2 (CONTEXTOS_DE_GRUPO_DISTINTOS,
    INCLUSION_ROTA_EN_EL_MANIFIESTO);
  - el recuento de contextos de K3 alterado en la evidencia B2, que
    rechazan validación y comparación;
  - un censo con ruta no declarada (FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA).
- **Otra carpeta** (copia fuera del paquete, mismo intérprete):
  - `fam11-comprobar` cumple;
  - los tres pilotos guardados se validan y se aceptan;
  - la regeneración y la conexión mixta se aceptan;
  - B1 y B2 recalculados en la copia, con B2 sobre el B1 de la copia, se
    validan y se aceptan.
- **Dependencia ausente o alterada** (en la copia): se retiraron o
  alteraron estas piezas, una cada vez:
  - `conexion_coord_cert.py`;
  - `comun_b2.py`;
  - `paper2b/cobertura.py` del núcleo C0;
  - `CONTEXTO_COL_POR_GRUPO.json` (alterado);
  - el `resultado.json` de T4 guardada.

  En cada caso, `fam11-comprobar` no cumple y lo informa sin excepción. Las
  órdenes de cálculo, validación o ensamblado se niegan antes de actuar
  (DEPENDENCIA_AUSENTE_O_ALTERADA), sin crear salida.

El guion de controles se ejecutó fuera del supervisor, como en FAM06–FAM08.
`controles_01` (39/40) se conserva; véase «Correcciones rutinarias».

**Regresión breve** (`reproducir.py` es compartido): `revisar` y
`fam01-comprobar` a `fam08-comprobar` terminan con código 0 y todos sus
apartados cumplen (`regresion_fam0*_comprobar.json`). Tras actualizar el
catálogo se repitieron `revisar`, `fam08-comprobar` y `fam11-comprobar`,
también con código 0 (`regresion_fam08_comprobar_final.json`,
`comprobar_02.json`).

**Saneado**: fuera de `salidas/fam11/lanzador/` no hay rutas personales en
`salidas/fam11`, `datos/fam11`, `referencias/fam11`, `nucleo_s6/{cov,b1,b2}`,
`src/fam11.py`, `local/pruebas_fam11.py` ni `fuentes_fam11.json`. Las
órdenes y los enlaces se registran con rutas relativas a la base.

## Tiempos medidos

| Invocación | Pared (s) | CPU (s) | Memoria pico del Job (MB) |
|---|---|---|---|
| `fam11-unidad` ABL-COV-T1 (`piloto_01`) | 141,7 | 132,7 | 253,4 |
| `fam11-unidad` B1 / B2 (`piloto_01`) | 1,7 / 0,8 | 1,5 / 0,7 | 36,2 / 38,5 |
| `fam11-validar` y `fam11-comparar` de los pilotos | 0,3–0,7 | ≤ 0,6 | ≤ 37,5 |
| `fam11-ensamblar` regeneración / mixta | 1,0 / 1,1 | 0,9 / 0,9 | 70,5 / 69,8 |
| `fam11-comparar` del ensamblado | 0,6 | 0,5–0,6 | 45,7–46,5 |
| `fam11-comprobar` | 1,0 | 0,8 | 65,5 |
| controles (40, fuera del supervisor) | 28,8 | — | — |

**Referencias históricas**:
- T1: 70,09 s de pared. Cada techo tardó ahora aproximadamente el doble;
  por ejemplo, d43ee19c… tardó 16,5 s frente a 8,0 s.
- B1: 1,3 s de trabajo (2,64 s de conductor).
- B2: 0,4 s de trabajo bajo supervisor (1,9 s de conductor).

Durante T1 la carga media de la máquina era del 17–22 %, sin procesos
Python ajenos, y la proporción CPU/pared fue 0,94. La causa de la
diferencia no está identificada y los valores no cambiaron. Son
antecedentes, no estimaciones. El resumen sin rutas está en
`salidas/fam11/lanzador.txt`.

## Correcciones rutinarias de esta sesión

- **Comprobaciones previas** (área temporal, no conservadas en el
  paquete): no cumplían por errores de la propia comprobación.
  - La guarda contra procesos mezclados se aplicaba también a la
    comprobación documental. Ahora la relaja una marca explícita
    (`_DOCUMENTAL`).
  - La guarda que impedía tener cargados a la vez `comun_b1` y `comun_b2`
    se retiró, porque la revalidación del enlace necesita ambos.
  - Los productos del catálogo se buscaban solo en `datos_configuracion`;
    están en `productos`.

  Corregido antes de `comprobar_01`, que cumple.
- **Procedencia B2**: la adaptación leía `PLAN_INICIO`, que el original no
  lee, y renombraba un motivo. Se retiró esa lectura y se restituyó el
  nombre original (EVIDENCIA_DISTINTA_DE_LA_DEL_CONDUCTOR) antes de los
  pilotos.
- **Primera comparación de B2** (`B2.comparacion_01_no_aceptada.json`;
  línea `fam11_cmp_01_B2` del lanzador): no se aceptó porque el comparador
  leía `veredicto` en el nivel superior de la fila de referencia, y está en
  `resolucion_global`. Corregido el puntero. La segunda comparación
  (`B2.comparacion.json`) se aceptó sin repetir el cálculo de B2. La
  primera se conserva.
- **Comparador B2 ante otra unidad**: en `controles_01` (39/40), comparar
  el piloto B1 como B2 terminaba con una excepción
  (`TypeError`, por falta de U_C2 enlazado) en vez de con un rechazo. Ahora
  la resolución sin manifiesto enlazado queda como no calculable y la
  comparación da `no_aceptada` con SALIDA_DE_OTRA_UNIDAD…. Se repitieron
  todos los controles (`controles_02`, 40/40).
- **`contexto_s6.py`** se colocó en `datos/fam11/fuentes` y no en
  `nucleo_s6/c0`, para no alterar la identidad del inventario C0.
- Ningún cambio tocó el cálculo científico. Los pilotos se calcularon con el
  código de cálculo final; las correcciones posteriores solo afectan a la
  comparación y a la comprobación.

## Límites

- Solo T1, B1 y B2 tienen cálculo nuevo. T2–T6 no se calcularon; en la
  conexión mixta entran guardadas y no se acreditan.
- **ENLACE-B1-v1** comprueba la validación y la revalida, pero no recalcula
  B1. Una cadena falsificada entera (evidencia, salida del trabajador,
  `ejecucion.json`, validación y registro, todos coherentes) no se detecta
  sin recalcular B1. En la receta, B1 se calcula en la misma ejecución.
- **B1** toma las categorías padre de la conciliación COV aceptada
  (rem152), no de una conciliación nueva. Lo declara su manifiesto, y la
  receta lo mantiene.
- **La resolución de las doce** se recalcula desde la lectura B2 nueva. La
  procedencia histórica, los textos y las huellas de las síntesis
  rem160/rem170 no se recalculan; la integración pertenece a FAM10.
- **Puertas y producción**: las puertas de producción históricas no se
  reproducen (PUERTA-v1), y la ejecución limpia no es una producción
  oficial.
- **Duración**: T1 dependió de la máquina; la receta usa el límite externo
  histórico de 2.400 s, sin margen garantizado.
- **Rutas en los registros**: los registros del supervisor
  (`lanzador/*.tarea.json` y sus logs) guardan rutas absolutas de esta
  máquina y quedan fuera de la distribución. `lanzador.txt` es el resumen
  sin rutas.
- **Aislamiento**: el aislamiento real queda pendiente en 2.4.2.

## Receta completa (preparada, no ejecutada)

`receta_01.json`, en este orden:
1. `fam11-comprobar`;
2. ABL-COV-T1 a T6, cada una con `fam11-unidad`, `fam11-validar` y
   `fam11-comparar`;
3. el ensamblado y la conciliación sobre las seis tareas nuevas
   (`fam11-ensamblar`) y su comparación;
4. B1 (`fam11-unidad`, `fam11-validar`, `fam11-comparar`);
5. B2 sobre el B1 nuevo validado, con su validación y su comparación,
   que incluye la resolución de las doce.

Condiciones:
- un cálculo a la vez, sin reintentos;
- COV y B1/B2 en procesos separados;
- límite externo de 2.400 s por tarea COV (reloj interno 2.280 s) y de
  600 s para B1 y B2;
- si una tarea COV no termina completa y validada, no se ensambla;
- si B1 no se valida, B2 no se lanza;
- una entrada faltante no se sustituye por su referencia.

Cubre 26 techos, 1.724 celdas, 1.728 afirmaciones conciliadas y las 12
afirmaciones B en 6 grupos. Reutiliza el censo, el ENF por afirmación, el
núcleo C0, las fuentes D7/grilla/CA2/D6, los manifiestos y la conciliación
aceptada como entrada de B1. No se estima la duración total.

## Propuesta de cierre

Propongo cerrar la **preparación** de FAM11 en su alcance:
- las tres operaciones están conectadas, con entradas y referencias
  completas en el paquete y 0 rutas personales;
- las piezas COV/B1/B2 se ejecutan desde sus bytes con adaptaciones
  declaradas que no cambian la ciencia, y se reutilizan el núcleo C0 de
  FAM05 y el conciliador de FAM12;
- B2 consume un B1 nuevo validado, nunca el histórico;
- la regla −1/100 es exacta y con el borde incluido;
- las categorías padre se conservan aparte de la conclusión transformada;
- los tres pilotos, la regeneración, la conexión mixta y los 40 controles
  son conformes, y la receta completa está disponible, sin lanzar.

Lo que acredita cada parte:
- **Cálculo comprobado**: T1 (18 techos y 1.438 comparaciones), B1 (U_C2) y
  B2 (L_K1 de los seis grupos y G_hi de las doce), exactos frente a la
  referencia.
- **Regeneración sobre entradas guardadas**: el ensamblado de 1.724 celdas
  y la conciliación de 1.728 afirmaciones, idénticos byte a byte. No
  acreditan T2–T6.
- **Conexión mixta**: la conexión de la T1 nueva al ensamblado y a la
  conciliación; no acredita lo demás.
- **Preparación sin ejecución**: T2–T6, y el ensamblado y la conciliación
  sobre seis tareas nuevas (Paso 3).

No se declara reproducida la familia. No se conocen faltantes de
implementación para la receta.

## Siguiente trabajo

- T2–T6, el ensamblado y la conciliación sobre salidas nuevas pertenecen al
  Paso 3.
- El aislamiento efectivo de FAM11 queda para 2.4.2.
- No se abre otra familia; FAM09 y FAM10 siguen sin abrir.

## Dictamen de Codex

Acepto el cierre de la preparación de FAM11. Volví a ejecutar la comprobación del paquete y la comparación de T1, B1, B2, la regeneración y la conexión mixta sobre sus productos guardados. Las cinco comparaciones quedaron aceptadas.

Contrasté T1 directamente con el libro rem152. Sus 1.438 comparaciones coinciden byte a byte y los 18 techos coinciden en todos los campos científicos. Comprobé los cuatro vínculos de B2 con los archivos del B1 nuevo. A partir de los 1.920 contextos guardados obtuve por separado los seis mínimos de K1 y calculé las seis diferencias exactas con la cota de B1. Coinciden con rem170 y satisfacen G_hi ≤ −1/100 para las doce afirmaciones colombianas bajo φ/2. La categoría padre se conserva.

En la regeneración completa con entradas históricas coinciden los tres archivos de filas (techos, celdas y afirmaciones) con las huellas de rem152. Los documentos que registran carpetas y procedencia se cotejan por contenido. En la conexión mixta solo T1 procede del cálculo nuevo. El agente también recalculó B1 y B2 en su prueba de traslado. El aislamiento sigue pendiente en 2.4.2. T2–T6 y el ensamblado con las seis salidas nuevas corresponden al Paso 3.
