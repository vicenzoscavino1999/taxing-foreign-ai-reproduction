# RESULTADO FAM14 — Conciliaciones G/N rem174, localización §18.7 y adopción rem176

Fecha: 2026-11-18 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original y los libros del revisor se consultaron en solo
lectura durante la extracción. La orden pública usa solo piezas del paquete.

## Estado

| Parte | Estado |
|---|---|
| Preparación | **Preparación documental revisada y cerrada por Codex el 18 de noviembre de 2026.** El paquete contiene el código, las entradas extraídas, las referencias, los tres objetos de integridad y la receta. Las cuatro operaciones están en una sola orden, probada de principio a fin. |
| F14-GN-REGEN (RD) | Se regeneraron los 391 pares G/N desde las entradas del paquete con U62. La ligadura G/N de U63 (rem175) los validó sin hallazgos. La comparación con la referencia da 391/391 filas idénticas, con ambos lados iguales (G 391/391, N 391/391). COBERTURA_GN_REM174.json tiene los bytes aceptados (3ef08df8…). |
| F14-GN (VI) | Integridad conforme. La cobertura aceptada (3ef08df8…, 276.923 bytes) es la misma copia que sirve de referencia a la regeneración. Recontada desde sus filas da 8/383/0. |
| F14-187 (VI) | Integridad conforme. Proyección pública 98bffc5d… (verificable con el paquete); identidad histórica 429dd087… (cotejada solo en el origen). 14 corridas T8: el objeto buscado no se localizó en ninguna. Queda abierto si el auditor llegó a ejecutarse. |
| F14-176 (VI) | Integridad conforme. Derivado público nuevo db0e96e1… con huella propia, cotejado en el origen con a975e3f9…. Conserva el sentido de las cinco transiciones. La proyección rem197 (63039f37…) conserva identificadores de la conversación y no se distribuye. |
| Orden única | `fam14-reproducir`: código 0 y `cumple: true` en 2,4 s (`salidas/fam14/reproducir_02`). |
| Fuera de este encargo | Integración general, instalación aislada (2.4.2), corridas del Paso 3, D8, nuevos supremos, manuscrito, publicación y commits. |

## Orden única probada

Desde la base, con el intérprete de `.venv-fam01` y `PYTHONHASHSEED=0`:

```
<python de .venv-fam01> -B -P -s -X utf8 reproducir.py fam14-reproducir --salida salidas/fam14/reproducir_02
```

- No admite `--entrada`: todas las piezas están en el paquete. La salida debe
  ser una carpeta nueva dentro de la base.
- Antes de crear la carpeta comprueba las huellas de las 416 piezas de
  `fuentes_fam14.json` que lee la regeneración. Si falta o cambió alguna, se
  niega sin escribir (`DEPENDENCIA_AUSENTE_O_ALTERADA`).
  - Quedan fuera de esa comprobación previa las dos referencias y los
    objetos de F14-187 y F14-176. Los juzgan la comparación y las etapas de
    integridad.
- Corre en cadena GN_REGEN → GN → LOC_187 → ADOPCION_176.
  - Cada etapa escribe en su carpeta, con `ejecucion.json` (lecturas,
    productos y código) y `archivos_leidos.json`.
  - Cada etapa se valida enseguida (`<etapa>.validacion.json`). GN_REGEN se
    valida sin leer ninguna referencia.
- Solo después compara GN_REGEN con las referencias
  (`gn_regen.comparacion.json`). Luego escribe `resumen.json` con los pasos,
  las cuatro operaciones y el balance por producto.
- Termina con código 0 solo si la regeneración se acepta y las tres
  integridades son conformes; en otro caso, código 1.

Funciona también desde otra carpeta: en una copia mínima del paquete fuera de
la base, comprobar y reproducir cumplen, con los mismos bytes y 0 lecturas
fuera (ver «Controles»).

## Resultado de las cuatro operaciones

### F14-GN-REGEN: regeneración de los 391 pares (`gn_regen/`)

Productor: U62 `pares_gn_rem174.py`, original 01653ca6…. Corre desde la
proyección rem197 a5b8b82d…, que en el paquete restituye ese original. Lee:

- el mapa de impacto rem117 aceptado por el dictamen rem118 §3 y los 399
  registros de techo que nombra (techo-persistente-v2), cada uno autenticado
  por el inventario de su entrega;
- los certificados rem118 de las 2.111 unidades del mapa;
- la conciliación E4 rem121, miembro del inventario b5e1e941… que fija
  L_rem122. Es la misma copia que usa FAM06;
- los manifiestos LOTE2 y LOTE2E4 (los de FAM05 y FAM06), fijados por la
  raíz rem174.

Cada par se forma por la identidad exacta de las primitivas racionales, del
dominio τ con bordes, del menú y del diseño (`Fraction`), nunca por
proximidad numérica. Escribe tres archivos en `gn_regen/salida_1`:

| Producto | Huella nueva | Referencia | Resultado |
|---|---|---|---|
| COBERTURA_GN_REM174.json (catálogo) | 3ef08df8… | 3ef08df8… (aceptada) | bytes idénticos; 391/391 filas idénticas, mismo orden; lados G 391/391 y N 391/391; resumen y regla de contrapartes iguales; 0 diferencias científicas |
| PARES_GN_REM174.json (hermano; no es producto del catálogo) | c6a3ee7a… | c6a3ee7a… (miembro del inventario rem174 d35d4690…) | bytes idénticos; 8/8 filas idénticas; lados G 8/8 y N 8/8; 0 diferencias científicas |
| FUENTES_BLOQUE_A_REM174.json | 9559cabf… | sin referencia | 409 fuentes con clave relativa a la raíz; la histórica tiene claves absolutas (rutas privadas) |

Validación independiente (`gn_regen.validacion.json`, aceptada; ninguna
referencia leída):

- **U63, validador vigente.** De `verificar_relaciones_rem175.py` (original
  d0040eb6…, proyección rem197 32f87cfe…) se ejecutó solo la ligadura G/N:
  las líneas 549–846, desde `_INVF = {}` hasta antes de
  `# ---- localización §18.7`.
  - `_ligadura_gn` re-deriva desde las mismas entradas, por su cuenta, los
    registros del mapa, las 391 filas y los 8 pares completos.
  - `_resumen_esperado` da RES_GN.
  - `_gn_pares(PARES nuevo)` y `_gn_cobertura(COBERTURA nueva)` dan **0
    hallazgos**.
  - No se ejecutó el resto de U63 (matriz rem175, enlaces, ligadura §18.7
    contra su corpus, correspondencia rem174), porque juzga productos que
    FAM14 no regenera.
- **Recuentos propios desde las filas** (no desde el resumen):
  - 391 pares únicos: 8 con techo certificado en ambos diseños, 383 con
    techo en uno y 0 sin techo.
  - Los 8 completos por menú: d=6, f=2. Los 383 por menú: d=172, f=101,
    df=110.
  - Los seis pares d (existente:0, 3, 4, 5, 6 y 7) tienen intervalos
    disjuntos con G > N. Los intervalos se recalculan como C2 ± error
    normalizado con `Fraction` y son iguales a los publicados.
  - Los dos pares f (existente:1 y 2) comparten el C2 almacenado y sus
    intervalos se solapan: el orden de sus supremos queda indeterminado.
  - Los 383 lados de malla conservan su etiqueta: frontera
    `FRN-E4:<diseño>:…`, LOTE2E4_MANIFIESTO y ningún registro. El
    identificador del par es `E4:<frontera de la malla>`. Ningún lado de
    malla tiene registro.
- **Ligadura de cada lado con su fuente por clave.** Los 399 lados con techo
  (383 + 2×8) apuntan a un registro de ese diseño (`design_v`) y de ese menú
  (`instrument_j`), certificado (`certified_bound`); 399/399.
- `pares_con_diferencias_tecnicas` (existente:0 y 1) se conserva tal como
  está en la referencia.

### F14-GN: integridad de la cobertura aceptada (`gn/INTEGRIDAD_GN.json`)

Se informa por separado de la regeneración. Juzga la misma copia que sirve de
referencia (`referencias/fam14/COBERTURA_GN_REM174.json`):

- huella 3ef08df8… igual a la aceptada en el catálogo y a la declarada en
  `fuentes_fam14.json`; 276.923 bytes;
- recuento desde sus filas: 391; 8/383/0; d=6 y f=2; d=172, f=101 y df=110;
  383 lados de malla sin registro y etiquetados. El resumen interno coincide
  con el recuento.

Resultado: conforme.

### F14-187: registro de localización §18.7 (`loc_187/INTEGRIDAD_18_7.json`)

| Identidad | Huella | Bytes | Quién la verifica |
|---|---|---|---|
| Pública (proyección rem197, `datos/fam14/187/`) | 98bffc5d… | 50.171 | Cualquiera, con el paquete |
| Histórica (aceptada en el catálogo) | 429dd087… | 50.433 | Solo en el origen: en la extracción, la proyección restituyó el original byte a byte al cambiar sus 9 marcadores (8 `@@R_BS2@@`, 1 `@@W_BS2@@`) por las rutas privadas. El original es miembro del inventario rem174 d35d4690…. |

Contenido comprobado en la proyección:

- `kind` registro-localizacion-18-7-rem174. El objeto buscado es §18.7
  (l.2458–2460) con sus seis campos de diseño.
- 14 corridas T8 con 14 `run_id` distintos. Las 14 dicen «no localizado en
  el corpus revisado».
- 0 copias del auditor D8 en las entregas y 0 tablas con los seis campos.
- El resumen da 14/0/14/0, igual al recuento.
- La naturaleza declara que una ausencia significa «no localizado en el
  corpus revisado», no inexistencia.

El registro cita el código original del auditor D8 (`herramientas/d8/auditor.py`)
solo por huella. **Si el auditor llegó a ejecutarse queda abierto**: el registro
no lo establece y esta comprobación no lo decide.

Resultado: conforme.

### F14-176: referencia documental de la adopción rem176 (`adopcion_176/INTEGRIDAD_176.json`)

La proyección rem197 63039f37… se revisó antes de distribuirla y conserva:

- el identificador de sesión en el nombre de la transcripción;
- `uuid` y `parent_uuid`;
- la línea nativa y su huella;
- los campos de la aplicación y la hora exacta.

Por eso **no se distribuye**. En su lugar se distribuye un derivado público
nuevo, `datos/fam14/176/REFERENCIA_ADOPCION_REM176.publica.json` (db0e96e1…,
2.890 bytes), que conserva solo lo necesario:

- el texto del autor (251 bytes, ddbad730…) y su posición;
- la fecha de la adopción (2026-11-09);
- la identidad (nombre, huella y bytes) del documento adoptado
  PROPUESTAS_ALCANCE_LIMITACION_REM175.md y del dictamen rem176;
- las cinco transiciones y su estado previo (`pendiente_de_localizacion`):

| Obligación | Estado adoptado |
|---|---|
| C3.supremos_G_N | satisfecho_en_alcance |
| E4.supremos_G_N | parcial_con_limite_adoptado |
| EXP2.supremos_G_N | parcial_con_limite_adoptado |
| T4.valores_supremos | parcial_con_limite_adoptado |
| AUD.double_counting_audit_18_7 | limitacion_adoptada |

Cotejado en el origen durante la extracción:

- el original a975e3f9… es miembro del inventario rem176 250d1411…;
- la proyección rem197 lo restituye. El directorio del marcador de la
  transcripción se toma del propio original;
- texto, huella, bytes y posición del texto del autor;
- nombre, huella y bytes del documento adoptado y del dictamen;
- las cinco transiciones son las del esquema de integración rem176
  (32f44a12…) e iguales a los estados de la matriz final rem176 (4a057da1…).

**Qué bytes verifica un tercero con el paquete:**

- la huella del derivado (db0e96e1…, declarada en `fuentes_fam14.json`);
- la huella y los bytes del texto del autor, recalculados desde el propio
  texto (ddbad730…, 251);
- que el texto nombra C3, E4, Exp. 2, T4 y §18.7;
- las cinco transiciones y el estado previo;
- que no hay identificadores de la conversación ni rutas: ningún UUID,
  `.jsonl`, marcador ni ruta absoluta.

**Solo en el origen** (límite expreso):

- la identidad íntegra del original a975e3f9… y de la proyección 63039f37…;
- las huellas del esquema y de la matriz rem176;
- las huellas del documento adoptado y del dictamen, cuyos archivos no están
  en el paquete;
- que el texto del autor es el prefijo del mensaje registrado. La huella del
  mensaje completo y la identidad del encargo que lo acompañaba se omiten.

Resultado: conforme.

## Lo que pudo verificar un tercero usando solo el paquete

1. **Regeneración**:
   - `fam14-reproducir` regenera los 391 pares desde las entradas del
     paquete, sin leer referencias;
   - la ligadura G/N de U63 los re-deriva desde las mismas entradas y no
     encuentra hallazgos;
   - la comparación da bytes iguales a 3ef08df8… (catálogo) y a c6a3ee7a…,
     y 391/391 filas con ambos lados iguales.

   Se comprobó en otra carpeta, fuera de la base, con los mismos bytes.
2. **Entradas**:
   - cada uno de los 399 registros es miembro, por huella y tamaño, del
     inventario de su entrega (los seis inventarios están en copia exacta);
   - la conciliación E4 es miembro del inventario rem121, cuya huella es la
     que cita el resumen de L_rem122;
   - los registros y los manifiestos tienen la huella que fija el resumen de
     la raíz rem174.
3. **F14-GN**: la huella 3ef08df8… y el recuento desde las filas.
4. **F14-187**:
   - la huella pública 98bffc5d…, que es el identificador del objeto en el
     paquete fuente;
   - el contenido: 14 corridas no localizadas, sin copias del auditor.
5. **F14-176**: lo indicado arriba.

Lo que el tercero **no** puede verificar sin el origen:

- las identidades históricas 429dd087… y a975e3f9…;
- la restitución del mapa rem117 (ver Límites);
- la correspondencia de los resúmenes de autoridad con los libros del
  revisor, que no están en el paquete.

## Referencias y entradas con doble papel

- `referencias/fam06/rem121/conciliacion/CONCILIACION_E4_REM121.json`
  (52a8f959…) es la referencia de F06-CONCILIACION. Aquí es **entrada** de
  U62 y de U63: es la conciliación aceptada (L_rem122), como pide el encargo.
  - Es la única lectura en `referencias/` durante GN_REGEN y su validación.
  - Está en la comprobación previa: alterada, la orden se niega.
- `referencias/fam14/COBERTURA_GN_REM174.json` es la referencia de la
  comparación y, a la vez, el objeto que juzga F14-GN. Solo la lee la etapa
  GN y, después, la comparación.
- `referencias/fam14/PARES_GN_REM174.json` solo se lee al comparar. Se
  autenticó en la extracción contra el inventario rem174.

## Insumos y piezas (`fuentes_fam14.json`)

Herramienta: `extraccion/extraer_fam14.py` (8694fc95…). Extracción con código
0: 417 archivos, 3 piezas reutilizadas y 4 proyecciones con correspondencia;
18.246.831 bytes.

- **Espejo** (`nucleo_s6/raiz/tmp/<área>/<rel>`):
  - U62 y U63 como proyecciones rem197. Cada una restituye su original con
    un solo marcador: la línea del directorio de los libros.
  - El mapa rem117, como proyección hecha en la extracción (5358abe5…,
    3.209.013 bytes; original 9dd9cacc…, 3.209.040). Lleva un marcador
    `@@R_BS2@@` en `nucleo_corregido_src`, el único campo con ruta absoluta,
    y es el único campo que cambia. Se comprobó en los originales de U62 y
    U63 que ninguno lo lee.
  - Los inventarios de las seis áreas: rem117, rem121, rem114, lima2201,
    lima1533 y lima2330.
  - Los 399 registros de techo, en copia exacta.
- **Reutilizadas** (misma huella que su miembro histórico, sin copiarlas otra
  vez):
  - la conciliación E4 (FAM06, referencia);
  - LOTE2_MANIFIESTO (FAM05);
  - LOTE2E4_MANIFIESTO (FAM06).
- **Autoridades** (`datos/fam14/autoridad`): resúmenes sin rutas, cada uno
  con la huella de su original y solo lo que lee el código.
  - D118_LINEAS: líneas 11 y 32 del dictamen rem118 y el total, 80.
  - CERT_REM118: `failures`, `units` y las filas de las 2.111 unidades del
    mapa (`unit`, `contract`, `record`, `checks`).
  - L122: `inventory_sha256`.
  - RAICES_FIJADAS: la sección `source_files_sha256` de las raíces rem174
    (196b4e24…) y rem175 (ef581a7a…), restringida a las fuentes que lee la
    ruta y con clave relativa.
    - Cada huella fijada se cotejó con el archivo copiado o reutilizado.
    - La raíz rem175 fija todas las fuentes que lee la ligadura.
  - ESQUEMA_REM175: el origen histórico declarado por la ligadura.
- **Integridad**: la proyección §18.7 (`datos/fam14/187`) y el derivado
  rem176 (`datos/fam14/176`).
- **Solo procedencia**, sin copiar:
  - los originales de U62 y U63, con la ruta de los libros;
  - el original y la proyección rem197 de la adopción;
  - el esquema y la matriz rem176, con rutas;
  - los inventarios rem174 y rem176.
- Rutas personales en el paquete: 0. Se barrieron los archivos nuevos, las
  salidas y los controles: ni rutas de usuario o del original, ni correo, ni
  el identificador de la sesión.

## Adaptaciones (declaradas en `src/fam14.py`)

Ninguna cambia fórmulas, claves, criterios ni la serialización. Cada original
se autentica por su huella antes de adaptarlo.

- **GUION-v1**: U62 corre desde sus bytes como `__main__`, en el proceso y con
  cwd en la base. La raíz histórica es `nucleo_s6/raiz`.
- **BLOQUE-U63-v1**: de U63 se ejecuta solo la ligadura G/N (líneas
  549–846). Las globales que toma del resto de U63 se inyectan: `sha`,
  `_bytes`, `TT`, `PINF` y `E175`.
- **RAIZ-PROYECTADA-v1**: las raíces rem174 y rem175 se leen de su resumen,
  con clave relativa a la raíz.
- **LIBROS-PROYECTADOS-v1**: el dictamen rem118, los certificados rem118 y
  L_rem122 se leen de sus resúmenes. En el dictamen, las líneas no
  distribuidas quedan vacías.
- **LECTURA-PAQUETE-v1**:
  - la conciliación y los manifiestos se leen de su copia en el paquete;
  - las claves de FUENTES_BLOQUE_A son relativas.
- **HUELLA-SANEADA-v1**: solo para la proyección declarada del mapa. Al
  autenticarlo contra el inventario rem117 y las raíces, su huella y su
  tamaño son los del original declarado.

## Reglas de comparación (COMPARACION-FAM14-v1)

- La clave es `par`. Se exige igualdad exacta de cada hoja de la fila:
  ambos lados, fronteras, manifiestos, registros, intervalos racionales,
  resultados y emparejamiento.
- Además se cuentan los lados iguales por separado (G y N).
- El resumen y la regla de contrapartes se comparan aparte.
- Los bytes deben coincidir con la huella aceptada.
- Una diferencia de huella solo se acepta como procedencia si está ligada a
  una pieza del paquete o de la salida. No hubo ninguna: todas las
  diferencias fueron 0.

## Controles (`local/pruebas_fam14.py`, `salidas/fam14/pruebas_fam14_02.json`: 22/22)

Asignación G/N equivocada con los totales intactos (copias de GN_REGEN,
validación U63 y comparación en el proceso):

- **Una contraparte d con sus lados G y N intercambiados.** Los recuentos
  siguen siendo 8/383/0 con el mismo reparto. La señalan:
  - U63 (`_gn_cobertura`);
  - la ligadura del lado con su registro;
  - la etiqueta de la malla;
  - la comparación: G 390/391 y N 390/391.

  Ni validada ni aceptada.
- **Un par completo d con sus lados intercambiados.** Siguen siendo 8 pares,
  d=6 y f=2. La señalan:
  - U63 (`GN_DISENO_REGISTRO`);
  - el recuento propio (fila inconsistente);
  - la comparación: G 7/8 y N 7/8.

Malla presentada como techo:

- **El lado de malla de una contraparte con un registro.** El recuento da 1
  lado de malla con registro y 9 pares completos. También la señalan U63 y
  la ligadura.
- **El lado de malla sin la etiqueta LOTE2E4_MANIFIESTO**, con los totales
  intactos. La señalan el recuento (contraparte mal etiquetada) y U63.

Archivo de integridad ausente o alterado (copias). Cada uno de estos objetos,
alterado o ausente, deja la integridad no conforme. Alterado, falla la huella
y se señala el contenido:

- la cobertura aceptada, con una fila G/N intercambiada;
- la proyección §18.7, con una corrida «localizado»;
- el derivado 176, con T4 como satisfecho_en_alcance.

Otra carpeta: copia mínima fuera de la base, con el mismo intérprete y sin el
original ni el espacio del revisor.

- `fam14-comprobar` cumple.
- `fam14-reproducir` cumple: los tres productos tienen los mismos bytes que
  en el paquete y hay 0 lecturas fuera en las cuatro etapas.
- **Con el derivado 176 alterado**: código 1. F14-176 no es conforme y
  F14-GN-REGEN cumple.
- **Con la cobertura aceptada alterada**: código 1. F14-GN no es conforme y
  F14-GN-REGEN no se acepta, porque es también su referencia.
- **Un registro de techo retirado, o la conciliación E4, el resumen
  CERT_REM118 o el mapa alterados**: `fam14-comprobar` no cumple y nombra la
  pieza. `fam14-reproducir` se niega sin salida
  (`DEPENDENCIA_AUSENTE_O_ALTERADA`).

## Comprobación, regresión y saneado

- `fam14-comprobar` (`comprobar_02`, con el código final) cumple:
  - 420 piezas, ninguna alterada;
  - la sustitución de U62 y el bloque U63 compilan;
  - U62 y U63 están ligados a 01653ca6… y d0040eb6…;
  - las dos referencias están íntegras;
  - las tres integridades son conformes.

  `comprobar_01` dio el mismo resultado con el código anterior a la
  corrección del recuento de lados.
- `receta_01`: comprobar → `fam14-reproducir`.
- Regresión tras editar el punto de entrada compartido (`reproducir.py`):
  - `revisar` es conforme;
  - FAM01–FAM11 y FAM13 `comprobar` dan código 0 y `cumple: true`
    (`salidas/fam14/regresion_famXX_comprobar.json`).
- Tras editar el catálogo: `tras_catalogo_famXX_comprobar.json` (FAM03–FAM11,
  FAM13 y FAM14), todos con código 0.
- Finales de línea LF en los documentos y en el código nuevo.

## Tiempos medidos (pared, s; `reproducir_02`)

| Paso | s |
|---|---|
| Orden completa (`resumen.json`) | 2,4 |
| GN_REGEN (U62) | 1,23 |
| Validación de GN_REGEN (U63 y recuentos) | 0,87 |
| Comparación | 0,23 |
| GN, LOC_187, ADOPCION_176 | < 0,01 cada una |
| Controles (22) | 20,5 |

## Correcciones rutinarias de esta sesión

- **Extracción**:
  - el mapa rem117 tenía una ruta absoluta, que no estaba prevista. Ahora va
    proyectado, con la HUELLA-SANEADA-v1;
  - la restitución de la proyección rem197 de la adopción necesitaba además
    el marcador de la transcripción;
  - había un error de tipos en el diccionario de marcadores.

  La extracción final dio código 0.
- **`reproducir_01`** (conservada): código 1. La validación esperaba 399 + 8
  lados con registro y son 383 + 2×8 = 399. Era un error de la expectativa,
  no de los datos. Los productos de esa ejecución ya eran idénticos a los
  aceptados. `reproducir_02` es la final.
- **`pruebas_fam14_01.json`** (21/22): el arnés cortaba el mensaje de error
  por la cola y, con la ruta larga del registro retirado, se perdía el
  prefijo `DEPENDENCIA_`. La orden sí se había negado sin salida. Corregido:
  `pruebas_fam14_02.json` da 22/22.

## Límites concretos

1. **Identidades solo en el origen**:
   - F14-187 se verifica con el paquete en su identidad pública (98bffc5d…).
     La histórica (429dd087…) se cotejó en la extracción.
   - F14-176 se verifica en su derivado (db0e96e1…). El original
     (a975e3f9…), el esquema y la matriz rem176 se cotejaron solo en el
     origen.
   - En la restitución de la proyección rem197 de la adopción, el directorio
     del marcador de la transcripción se toma del propio original, así que
     ese marcador no se contrasta con una fuente independiente.
2. **Mapa rem117 proyectado.** U62 y U63 lo autentican con la identidad del
   original declarada en `fuentes_fam14.json` (HUELLA-SANEADA-v1). Un tercero
   comprueba la huella de la proyección, pero no puede restituir el original
   sin la ruta privada.
3. **Resúmenes de autoridad.** Un tercero comprueba sus huellas declaradas,
   no su correspondencia con los libros del revisor ni con las raíces, que no
   están en el paquete.
   - Las expectativas de la validación son los hechos aceptados que fija el
     encargo: 8/383/0, d/f/df, 6 + 2 y el sentido de las cinco transiciones.
     Se recuentan desde las filas.
   - U63 deriva lo suyo desde las entradas, sin esas expectativas.
4. **U63 parcial.** Solo se ejecutó la ligadura G/N. La ligadura §18.7 de
   U63 necesita el corpus de las 14 corridas, que no está en el paquete, y el
   catálogo trata F14-187 como integridad.
5. **El auditor D8**: no se sabe si llegó a ejecutarse; queda abierto, como
   pide el encargo.
6. **FUENTES_BLOQUE_A_REM174.json** no tiene referencia: la histórica lleva
   claves absolutas.
7. **Intérprete.** `.venv-fam01` tiene su intérprete base en el árbol
   original, igual que en las familias anteriores. El rastro cuenta sus
   aperturas aparte. El aislamiento real pertenece a 2.4.2.

## Propuesta de cierre

Propongo cerrar la preparación de FAM14 en su alcance documental:

- la regeneración de los 391 pares es idéntica byte a byte a la aceptada;
- la validó el validador vigente (U63, ligadura G/N) sin hallazgos;
- las tres integridades son conformes;
- los límites anteriores quedan registrados.

El dictamen figura al pie.

## Lo que falta

- Integración general (2.2.3), instalación aislada (2.4.2) y corridas del
  Paso 3, fuera de este encargo.

## Dictamen de Codex

El 18 de noviembre de 2026 acepté las cuatro operaciones y cerré la preparación documental de FAM14. Repetí la orden pública con el código final en `salidas/fam14/dictamen_20261118_final`. Terminó con código 0 en 2,42 s. Comparé directamente los bytes nuevos de COBERTURA y PARES con los originales de rem174. Reconté los 391 pares desde los lados, los 383 de una sola cota por instrumento y los 8 de dos cotas. La comparación racional de estos últimos certifica G > N en seis y deja el orden indeterminado en dos.

Contrasté en origen los 14 identificadores de corrida y sus resultados de localización. En las 14 corridas examinadas quedó sin localizar el registro de §18.7. Para rem176 comprobé la huella de la referencia histórica, el texto de adopción y las cinco transiciones del derivado público contra la matriz original. El paquete permite verificar las dos versiones públicas por su propia huella. El cotejo con los originales requiere acceso al archivo histórico.

Ajusté el manejo de dos errores de la orden pública. La ruta de salida se valida antes de crearla y, si falta una referencia de G/N o su huella difiere, la orden escribe el balance identificando el producto afectado. Los 24 controles pasaron, incluidos los dos casos añadidos y el traslado con el mismo intérprete (`salidas/fam14/dictamen_20261118_controles.json`).

Con esta revisión quedan preparadas las 14 familias en sus alcances documentados. El siguiente subpaso es integrar los comandos en 2.2.3. La instalación aislada de 2.4.2 y los lotes completos del Paso 3 siguen pendientes.
