# RESULTADO FAM13 — Tablas y validaciones históricas (T1/T2/T7, E1235, E1_i2, matriz v4 de Exp0) e integridad S1

Fecha: 2026-11-18 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original y los libros del revisor se consultaron en solo
lectura durante la extracción. La orden pública usa solo piezas del paquete.

## Estado

| Parte | Estado |
|---|---|
| Preparación | **Revisada y cerrada en su alcance documental por Codex el 18 de noviembre de 2026**. El paquete contiene el código de las dos operaciones, las entradas extraídas, las referencias y la receta. Las cinco etapas, sus validaciones y sus comparaciones están conectadas en una sola orden y probadas. |
| F13-HISTORICAS (**VI** desde el 2026-11-18; antes RD) | Por decisión del autor (L-F13-VALIDADOR-REM191), la acreditación formal de la fila es la integridad de los siete productos. Se conserva como evidencia lo que hace la orden: 5 de los 7 productos se regeneraron y sus bytes son los aceptados (T1, T2, T7.csv, T7_anexo.json y MATRIZ_REVISADA_v4). Las dos validaciones evalúan el modelo: se autentican por huella y prerregistro, y su aritmética se recalcula desde los valores guardados (85/85 y 21/21 campos iguales). |
| F13-S1 (VI) | Integridad conforme: 40/40 públicos con nombre, tamaño y SHA-256 aceptados, el mapa rem187 (062f8d9b…) y la fe de erratas rem188 (proyección 32892f0a… ligada al original 283fffd5…). Los 19 internos se cotejaron en el origen y no están en el paquete. |
| U60 | **No localizado** tras una búsqueda acotada en 23 candidatos. Las salidas nuevas tienen comprobaciones independientes (ver «U60: búsqueda y lo comprobado»). **L-F13-VALIDADOR-REM191 adoptada por el autor el 2026-11-18**: la fila pasa de RD a VI (ver «Decisión del autor sobre U60»). |
| Orden única | `fam13-reproducir`: código 0 y `cumple: true` en 9,8 s (`salidas/fam13/reproducir_02`). |
| Reproducción completa | Fuera de este encargo: Paso 3, aislamiento 2.4.2 y FAM14. |

## Orden única probada

Desde la base, con el intérprete de `.venv-fam01` y `PYTHONHASHSEED=0`:

```
<python de .venv-fam01> -B -P -s -X utf8 reproducir.py fam13-reproducir --salida salidas/fam13/reproducir_02
```

- No admite `--entrada`: todas las piezas están en el paquete. La salida debe
  ser una carpeta nueva dentro de la base.
- Antes de crear la carpeta comprueba las huellas de las 214 piezas de
  `fuentes_fam13.json` usadas para calcular y de las 1.730 filas de unidad de
  FAM01 que lee T7. Si falta o cambió alguna, se niega sin escribir
  (`DEPENDENCIA_AUSENTE_O_ALTERADA`). Las referencias y las piezas S1 no
  entran en esa comprobación previa: las juzgan la comparación y la etapa S1.
- Corre en cadena T1T2 → T7 → VALIDACIONES → MATRIZ_V4 → S1. Cada etapa
  escribe en su carpeta, con `ejecucion.json` (lecturas, productos, código)
  y `archivos_leidos.json`, y se valida enseguida sin leer referencias
  (`<etapa>.validacion.json`).
- Solo después abre las referencias para las comparaciones
  (`<etapa>.comparacion.json`) y escribe `resumen.json` con los pasos, los
  estados, el balance por producto, S1 y U60.
- Código 0 solo si F13-HISTORICAS cumple y F13-S1 es conforme; en otro caso,
  código 1 con el motivo en `resumen.json`.

Órdenes auxiliares: `fam13-comprobar --salida <archivo nuevo>.json` (sin
cálculo) y `fam13-receta --salida <archivo nuevo>.json` (los pasos, sin
ejecutar).

## Balance por producto (F13-HISTORICAS)

| Producto | Qué se regeneró | Qué se comprobó por huella | Pendiente |
|---|---|---|---|
| T1.csv (rem107), f20d0e92… | Sí: `tablas_diseno` de U59 (`generar_matriz_rem107.py`, c6a96856…) sobre §6.2–§6.3 del plan y D7 2a25893b…, escrito con el bloque exacto de rem107. | Bytes = f20d0e92… (aceptado y referencia). 9/9 filas idénticas por `n`; 0 diferencias científicas. | Nada en su alcance. |
| T2.csv (rem107), bce470b6… | Sí, en la misma etapa y con el mismo bloque. | Bytes = bce470b6…. 8/8 filas idénticas por `fila`; 0 diferencias científicas. | Nada en su alcance. |
| T7.csv (rem108), 504255e1… | Sí: `unidades`, `analizar_claim` y `ensamblajes` de U59 (`generar_matriz_rem108.py`, 8954fdd4…) sobre el paquete pv12, el registro v4 y `cell_selection`, escrito con el bloque exacto de rem108. | Bytes = 504255e1…. 224/224 filas idénticas por la clave de seis columnas, en el mismo orden; 0 diferencias científicas. | Nada en su alcance. |
| T7_anexo.json (rem108), 070f3c8e… | Sí, en la misma etapa. | Bytes = 070f3c8e…, el anexo aceptado que ya tenía FAM10. 1.728/1.728 filas idénticas por afirmación (categorías originales, G y huellas de los testigos); 0 diferencias científicas. | Nada en su alcance. |
| resultados_E1235_i1.json, f05c2ba4… | No: evalúa el modelo. | El archivo es el aceptado y su prerregistro está ligado (`prerregistro_sha256`). Además, 85/85 campos recalculados desde los valores guardados son iguales. Se conserva E1 i1 **no conforme**. | Regenerar los valores del modelo (lista en «VALIDACIONES»). |
| resultados_E1_i2.json, 59f98aa2… | No: evalúa el modelo. | El archivo es el aceptado; su prerregistro está ligado y se basa en el de E1235, fijado tras observar i1. 21/21 campos recalculados son iguales. Se conserva E1 i2 (Romberg) **conforme**. | Regenerar `B_f0` y `D_por_eta`, que salen del modelo. |
| MATRIZ_REVISADA_v4.json (rem134, salida_a2), e020cff2… | Sí: versión A2 ejecutada de `derivar_h4_h30_r1` (3305e831…) sobre la matriz A3 de rem133. | Bytes = e020cff2…. 42/42 requisitos idénticos por `requisito`; 0 diferencias científicas. Los otros 5 documentos A2 son idénticos byte a byte a rem134, salvo `segundos` en el resumen. | Nada en su alcance. |

Resumen: 5 productos regenerados con los bytes aceptados; 2 autenticados por
huella con su aritmética recalculada; 0 diferencias científicas; ningún
producto queda pendiente por discrepancia.

## Balance S1 (F13-S1)

Fuentes de la aceptación: el cierre `review_20261114_rem188_S1_cerrado.json`
(aa6810dd…) y la aceptación a la que remite,
`review_20261114_rem188_S1_acceptance.json` (4bb43a2e…). Durante la
extracción se autenticaron por huella; no se copian al paquete. Las huellas
aceptadas, sin rutas, quedan en `datos/fam13/s1/HUELLAS_ACEPTADAS_S1.json`.

| Pieza | Resultado |
|---|---|
| 40 archivos públicos (`datos/fam13/s1/publico`, copia de rem197/paquete/S1/publico) | 40 presentes, 40 iguales en nombre, tamaño y SHA-256; 0 faltan, 0 ajenos, 0 distintos. |
| Mapa rem187 `MAPA_COBERTURA_VISTAS_REM187.json` | 062f8d9b…, igual al aceptado. |
| Fe de erratas rem188 | La proyección pública es 32892f0a…, igual a la aceptada. Remite al mapa 062f8d9b… y su `source_path` lleva el marcador `@@R_FS@@`, una sola vez. Al restituir el marcador se obtiene el original 283fffd5…, comprobado en la extracción. Se conservan las dos identidades; el original no está en el paquete. |
| 19 internos | Sus huellas aceptadas se cotejaron con el origen durante la extracción (19/19). No están en el paquete ni son dependencia de la orden pública. |

Es una verificación de integridad: no reconstruye las vistas ni repite las
baterías históricas. Si falta un público, alguno cambió o aparece uno ajeno,
la integridad no es conforme y nombra el archivo (ver «Controles»).

## U60: búsqueda y lo comprobado

**Búsqueda acotada** en los orígenes de los siete productos y sus revisiones
(`fuentes_fam13.json`, `u60_busqueda`). Se buscó en cada candidato la huella
completa de los siete productos o sus 16 primeros caracteres:

- 8 piezas del origen:
  - rem107: `pruebas/prueba_rem107.py`, `pruebas/reproducir_revisor.py` y
    `conciliacion/prueba_entregas.py`;
  - rem108: `pruebas/prueba_ensamblajes.py`, `conciliacion/prueba_entregas.py`
    y `lote/verificar_lote.py`;
  - rem134: `b_lambda/prueba_entrada_lambda_rem134.py` y
    `c_captura/pruebas_fila_c.py`.
- 15 guiones del revisor: los `review_*` de rem107 (audit, probes,
  supplement y update), rem108 (audit, probes, science, details, supplement y
  update), rem133 (audit y update) y rem134 (audit, audit_i1 y update).

Ninguno cita una huella aceptada de los siete productos, así que no se puede
acreditar qué producto validaba U60 ni con qué versión. **U60 sigue sin
localizarse.** L-F13-VALIDADOR-REM191 se conserva como propuesta sin adoptar.
*(Adoptada por el autor el 2026-11-18: ver «Decisión del autor sobre U60».)*

**Lo comprobado de forma independiente sobre las salidas nuevas** (validación
de cada etapa, sin leer referencias):

- T1T2 (6/6): T1 tiene los nueve números 1–9 con parámetros presentes en D7
  y soportes JSON; T2 tiene las ocho ecuaciones a–h con estado asignado; las
  columnas siguen la regla de orden de rem107.
- T7 (6/6):
  - el bloque T7 de `prueba_ensamblajes.py` de rem108 (63e965b1…), ejecutado
    tal cual sobre el anexo nuevo: 11/11 casos. Cubre cobertura exacta,
    categorías originales contra el registro, familias c/ci/g 640/960/128,
    forma de cada familia, las 16 robustas y tres claves ajenas rechazadas;
  - T7.csv recalculado desde el anexo nuevo (recuentos por clave y G mín/máx);
  - total 1.728;
  - G y huella de cada testigo contra sus filas aceptadas: 3.449 posiciones
    en 1.724 archivos;
  - testigos contados (3.449 con filas + 7 sin filas = 2 × 1.728);
  - cobertura sin omitidas ni ajenas.
- VALIDACIONES (4/4): autenticación, recálculo igual a lo guardado, E1 i1
  no conforme conservado y E1 i2 conforme conservado.
- MATRIZ_V4 (6/6):
  - la ejecución termina sin fallos;
  - hay 42 requisitos en el orden de A3;
  - las 39 filas ajenas a H4/H30/R1 son idénticas a A3;
  - en H4/H30/R1 solo cambian `clase_evidencia`, `resultado`, `evidencia` y
    `accion_minima`;
  - las clases son H4 retrospectiva con hallazgo, H30 contemporánea y R1
    retrospectiva;
  - el informe de entradas fuera de esas tres filas está intacto.

Estas comprobaciones no acreditan U60. `prueba_ensamblajes.py` es un
candidato examinado: su bloque T7 se usa como comprobación, pero no liga
bytes aceptados.

Evidencia del revisor, que no es U60 y no se repitió aquí:
`review_20261029_rem108_science.py` volvió a ejecutar las validaciones
sintéticas con el modelo. En `synthetic_matches_saved` registró E2, E3 y E5
iguales a lo guardado y E1 distinto. También comparó un oráculo algebraico
de E1 con la Romberg de i2. FAM13 no evalúa el modelo.

## Resultado de cada etapa

### T1T2 (rem107)

`tablas_diseno(R)` lee el extracto §6.2–§6.3 del plan
`PLAN_DISENO_v2_2_30.md`. El extracto corresponde a las líneas 1.028–1.153,
ligadas a la huella del plan completo 08fc6295…, y queda en
`datos/fam13/t1t2/`. También lee el registro de parámetros D7 2a25893b….
T1 y T2 se escriben con el bloque exacto de `main()` de rem107.

### T7 (rem108)

- `Entregas` autentica los paquetes con sus inventarios proyectados (huella
  del original más las entradas consultadas): 16/16 conformes.
- `unidades` acepta 1.730 unidades, leídas de las copias exactas de FAM01.
  Rechaza por AUSENTE 546 unidades de pv12 sin copia en FAM01; ninguna es
  testigo de una afirmación (la extracción lo comprueba: 0 testigos sin
  copia).
- Registro v4 4cf24bc0… y `cell_selection` dd86e55c…, comprobados por huella.
- `ensamblajes` termina tras T7 (ENSAMBLAJE-T7-v1). T8 y la admisibilidad
  no son de FAM13.
- El bloque exacto de rem108 escribe T7.csv, T7_anexo.csv, T7_anexo.json y
  COBERTURA.json (parte T7).
- Recuentos: 1.728 afirmaciones (c 640, ci 960, g 128); 1.524 cambios de
  signo certificados, 188 inconclusas por testigos en tolerancia y 16
  robustas infactibles; 224 filas de T7.
- COBERTURA (parte T7) no tiene diferencias frente a la de rem108.

### VALIDACIONES (rem107: E1235 i1 y E1 i2)

Se revisaron los prerregistros (`prerregistro_E1235.json`,
`prerregistro_E1_i2.json`) y los guiones `validaciones_sinteticas.py`
(d09c7d4c…) y `e1_romberg.py` (289b5d94…). Los guiones solo se autentican
como procedencia: evalúan el modelo y no se ejecutan. Sus fórmulas se citan
por línea en `src/fam13.py`.

Se recalcula desde los valores guardados, sin evaluar el modelo:

- **i1, 85 campos**:
  - E1: Richardson O(h²) y sus criterios, incluido el no conforme;
  - E2: formas cerradas, CS por diseño y presentación;
  - E3: referencia decimal con precisión 50;
  - E5: búsqueda ternaria sobre la muestra guardada;
  - el estado global.
- **i2, 21 campos**: tabla de Romberg de tres niveles, dispersiones
  relativas por h, razones sucesivas, dispersión de Romberg y criterios.

Solo autenticado (sale del modelo o no se guardó):

- i1:
  - E1: `B_f0_por_eta`, `dRdtauf0_por_eta`, ingredientes exactos de
    tilde_f, dispersión por h (i1 no guardó D(h)) y topología en τ_f = 0;
  - E2: `B_pot`, momentos Pareto exactos y, de `delta_CS`, R,
    `CS_solo_viables`, primer z formal y topología;
  - E3: `s_P` finitos y la sucesión frente al núcleo;
  - E5: r* y tilde_d fuera de la muestra, brechas y errores sobre la
    rejilla completa, y el límite fuera del criterio (η_d = 0);
  - global: `fuentes_verificadas` y `ejecutado_utc`.
- i2: `B_f0`, `D_por_eta` y `ejecutado_utc`.

Se conservan el resultado original de E1 en i1 (**no conforme**:
Richardson O(h²) con tolerancia 1e-9) y el de la revisión Romberg en i2
(**conforme**).

### MATRIZ_V4 (rem134, salida_a2)

- La A2 corre como `__main__` con
  `[nucleo_s6/raiz, nucleo_s6/raiz/tmp/<rem134>, <etapa>/salida_a2]`.
- Sigue su enlace a la matriz A3 de rem133: inventario b635d0b3… y tres
  archivos de `salida_a3`.
- H4 recorre el núcleo de 14 entregas: 45 archivos de una sola versión y
  629 posiciones, cada una contra el inventario original de su entrega.
- Resultados: R1 da 2.520 `coincide_con_rango_documentado` y H4 da 43.
- Clases de evidencia:
  - A3: 18 retrospectiva comprobada, 9 obligación de fase posterior, 9
    contemporánea, 3 pendiente técnica, 2 limitación no recuperable y 1
    reconstrucción rem133;
  - v4: 19 retrospectiva comprobada, 1 retrospectiva comprobada con
    hallazgo, 10 contemporánea, 9 obligación, 2 limitación y 1
    reconstrucción.
- Las tres pendientes técnicas de A3 pasan a:
  - H4: retrospectiva comprobada con hallazgo;
  - H30: **contemporánea**;
  - R1: retrospectiva comprobada.

  Se mantiene así la distinción entre reconstrucción retrospectiva y
  evidencia contemporánea. Las otras 39 filas conservan estado y clase de
  A3.

### S1

`integridad_s1()` escribe `INTEGRIDAD_S1.json` (balance anterior). La etapa
lee 43 archivos: los 40 públicos, el mapa, la fe de erratas y el resumen de
huellas.

## Referencias y entradas con doble papel

- **T7_anexo de FAM10** (`nucleo_s6/exp8/.../T7_anexo.json`, 070f3c8e…):
  aquí es solo la referencia del anexo nuevo. En FAM10 es entrada de
  F10-ENF-AFIRMACION (U41, `conciliar_exp8_rem147.py`) junto con sus filas
  padre. La orden lo trata como referencia prohibida durante la producción
  y la validación.
- **Filas de unidad de FAM01** (`referencias/fam01/originales/*_filas.json`):
  en FAM01 son referencias de comparación; aquí son entradas de T7 (1.730
  leídas) y de su validación (1.724 archivos de testigo).
- **`referencias/fam13/`**: rem107 (T1.csv y T2.csv), rem108 (T7.csv y
  COBERTURA.json) y rem134 (los seis documentos de `salida_a2`). Solo se leen
  al comparar. En las cinco etapas y sus validaciones el registro de lecturas
  da `referencia_esperada_leida: false`.
- La matriz A3 de rem133 es entrada de la A2 y base de la validación, no
  referencia de un producto.

## Insumos y piezas (`fuentes_fam13.json`)

`extraccion/extraer_fam13.py` (2,7 s) copia o proyecta cada pieza y
autentica cada huella contra el original o contra su inventario histórico.

- **141 archivos (57,8 MB)**:
  - 80 en `nucleo_s6/raiz`:
    - los dos U59 y la A2;
    - `prueba_ensamblajes.py`;
    - el índice pv12 y 15 paquetes (inventario e1538d3a…);
    - el inventario y la salida A3 de rem133;
    - 45 archivos de código H4;
    - 3 de la cadena S5, CERT3 y 7 de D3.
  - 51 en `datos/fam13`:
    - el extracto del plan;
    - los inventarios proyectados de T7 y el mapa de filas FAM01;
    - el núcleo H4 por entrega;
    - las 4 validaciones guardadas;
    - los 40 públicos S1, el mapa, la fe de erratas proyectada y el resumen
      de huellas.
  - 10 referencias en `referencias/fam13`.
- **73 piezas reutilizadas**, cada una contra su declaración en otro
  `fuentes_*.json` y contra el original:
  - D7 2a25893b…, el registro v4 y `cell_selection` (FAM02);
  - `claims.py` y `__init__.py` de la instalación;
  - el T7_anexo de FAM10;
  - `nacional.py`, `ejecutar_b.py`, `formulas.json`, D7 10a0bd5b…, los
    manifiestos y archivos de D2/D6 y CA2.
- **2 proyecciones saneadas** ligadas a su original:
  - `vectores.json` de D2: 8d6aa531… → 2060afc6…, para `HF` de la A2;
  - la fe de erratas: 32892f0a… → 283fffd5….
- **Solo procedencia** (autenticados, no copiados): los dos guiones de
  validación, el cierre S1, la aceptación S1 y la fe de erratas original.
- Las rutas guardadas son relativas a la base o usan `<directorio de los
  libros>`. Los 19 internos S1 no se copian.

## Adaptaciones (declaradas en `src/fam13.py`)

No cambian fórmulas, claves, criterios ni la serialización. Cada original se
autentica por su huella, y cada sustitución es única y se fija por texto
exacto.

- **GUION-v1**: cada guion corre desde sus bytes, en el proceso, con
  cwd = la base. U59 se carga como módulo y la A2 como `__main__`.
  `generar_matriz_rem107.py` tiene finales CRLF: las anclas y los sustitutos
  usan los del archivo, y un archivo con finales mixtos se rechaza.
- **ESCRITURA-v1**: T1/T2 y T7 se escriben con el bloque exacto de `main()`
  de su guion, fijado por su primera y su última línea.
- **PLAN-EXTRACTO-v1** (rem107): el plan se lee del extracto ligado a
  08fc6295….
- **INVENTARIO-PROYECTADO-v1, FILAS-FAM01-v1, NUCLEO-INSTALADO-v1 y
  ENSAMBLAJE-T7-v1** (rem108):
  - inventarios proyectados con la huella del original;
  - filas de unidad desde FAM01;
  - `claims.py` del núcleo instalado (el del original);
  - ensamblaje cortado tras T7.
- **INVENTARIO-H4-v1 y HUELLA-SANEADA-v1** (A2): el bucle H4 recorre la
  lista proyectada de cada entrega, y `HF` devuelve la huella del original
  solo para la proyección declarada de `vectores.json`.
- **MODULOS-AISLADOS**: el paper2b del núcleo instalado (T7) y el de la
  entrega de referencia (R1 de la A2) no se mezclan en `sys.modules`.

## Reglas de comparación (COMPARACION-FAM13-v1)

- Se ejecuta después de producir y validar. Compara filas por su clave: `n`,
  `fila`, las seis columnas de T7, `afirmacion` y `requisito`. Informa
  faltantes, ajenas, duplicadas y orden.
- El contenido científico debe ser exacto: categorías y clasificaciones de
  G, valores de G, estados, clases de evidencia y recuentos.
- Una diferencia de procedencia se nombra y se comprueba:
  - tiempo (`segundos` del resumen);
  - ruta, si solo cambia el separador y el archivo existe;
  - huella, si está ligada a un archivo nuevo o a una pieza del paquete.
- Cada producto exige además bytes iguales a la huella aceptada. Una
  diferencia científica deja el producto pendiente.

## Controles (`local/pruebas_fam13.py`, `salidas/fam13/pruebas_fam13_03.json`: 20/20)

Riesgos distintos y breves. Nada fuera de FAM13 se recalcula.

- **Fila histórica cambiada**, sobre copias de las etapas aceptadas
  (validación y comparación en el proceso):
  - T1 con la clave `n` 9 → 10: faltan 9 y sobra 10; la validación falla.
  - T7.csv con un `total` + 1: la validación falla (T7 ≠ recálculo) y hay 1
    diferencia científica (`total`).
  - T7_anexo con un `sup_G` + 1 ulp (valor): falla la validación de G de
    testigos; 1 diferencia científica en esa afirmación.
  - T7_anexo con una categoría original cambiada (clasificación de G): falla
    el bloque T7 de rem108; 1 diferencia científica.
  - Matriz v4 con H30 retrospectiva en lugar de contemporánea (estado y
    clase): falla la validación de clases; 1 diferencia científica
    (`clase_evidencia`, H30).
  - E1_i2 con una dispersión de Romberg + 1 ulp: el recálculo señala ese
    único campo.

  En todos los casos la reproducción queda `no_aceptada`.
- **S1**: un público ausente, uno alterado en un byte, uno ajeno, o la fe de
  erratas sin remitir al mapa aceptado: la integridad no es conforme y nombra
  el archivo.
- **Otra carpeta**: copia mínima fuera del paquete, con el mismo intérprete y
  sin el original, el espacio del revisor ni los 19 internos.
  - `fam13-comprobar` cumple.
  - `fam13-reproducir` cumple con los 14 productos iguales a los del paquete y
    0 lecturas fuera de la copia o del intérprete.
  - Con un público S1 ausente o alterado, la orden termina con código 1,
    F13-S1 no es conforme y nombra el archivo, y F13-HISTORICAS cumple.
- **Dependencias en la copia**: un archivo de filas FAM01 retirado, la A2
  alterada o `resultados_E1_i2.json` alterado. `fam13-comprobar` no cumple y
  la nombra. `fam13-reproducir` se niega sin crear la salida
  (`DEPENDENCIA_AUSENTE_O_ALTERADA`).

## Comprobación, regresión y saneado

- `salidas/fam13/comprobar_02.json` (final): cumple. Comprueba 214 piezas
  sin alteraciones y 1.730 filas FAM01. Los 3 guiones con sus sustituciones
  y los 3 bloques exactos compilan, el código está ligado a su original, las 11 referencias están
  íntegras y S1 es conforme. U60: 23 candidatos, ninguno con huella citada.
- Regresión (`reproducir.py` es compartido): `revisar` y `fam01-comprobar` …
  `fam11-comprobar` terminan con código 0 y cumplen
  (`salidas/fam13/regresion_fam*_comprobar.json`). Después de editar
  `catalogo.json` se repitieron los `comprobar` de FAM03–FAM11 y FAM13, todos
  con código 0 (`salidas/fam13/tras_catalogo_*_comprobar.json`).
- Saneado, revisado sobre los archivos finales: 0 rutas personales, nombres
  de usuario o correos en:
  - `src/fam13.py`, `local/pruebas_fam13.py`, `reproducir.py` y
    `extraccion/extraer_fam13.py`;
  - `fuentes_fam13.json`, `datos/fam13` y `referencias/fam13`;
  - `salidas/fam13`.

  Las copias de otra carpeta quedaron fuera del paquete.

## Tiempos medidos (pared, s; `reproducir_02`)

| Etapa | Etapa | Validación | Comparación |
|---|---:|---:|---:|
| T1T2 | 0,06 | 0,02 | 0,02 |
| T7 | 2,77 | 2,66 | 0,55 |
| VALIDACIONES | 0,02 | 0,00 | 0,01 |
| MATRIZ_V4 | 2,48 | 0,02 | 0,60 |
| S1 | 0,22 | 0,00 | 0,00 |

Orden completa: 9,8 s. Los controles tardaron 49,0 s, incluida la copia de
otra carpeta.

## Correcciones rutinarias de esta sesión

1. `comprobar_01` no cumplía: `SUSTITUCION_NO_UNICA` en
   `generar_matriz_rem107.py`, que tiene finales CRLF. `adaptado()` aplica
   ahora las anclas con los finales del archivo y rechaza los finales mixtos.
   `comprobar_02` cumple.
2. El balance de VALIDACIONES daba el recuento combinado (106/106) para los
   dos productos; ahora da 85/85 y 21/21 por producto. `reproducir_02`
   repite la orden: los 14 productos son idénticos byte a byte a los de
   `reproducir_01`.
3. Guion de controles:
   - `pruebas_01/` quedó interrumpida, sin informe, porque la copia a otra
     carpeta encontró `src/` ya creada;
   - `pruebas_fam13_02.json` (19/20) esperaba que el resumen A2 difiriera en
     `segundos`, pero las dos ejecuciones midieron 2,4 s;
   - `pruebas_fam13_03.json`: 20/20.

## Límites concretos

- **U60 no localizado** (ver arriba). L-F13-VALIDADOR-REM191 fue adoptada por
  el autor el 2026-11-18 y F13-HISTORICAS es VI. Los dos productos del modelo
  se comprobaron sobre valores guardados; su ejecución del modelo no se
  repite.
- **Validaciones no regeneradas**: evalúan el modelo. Quedan autenticadas y
  con su aritmética recalculada; los campos que salen del modelo están
  listados en «VALIDACIONES».
- **546 unidades de pv12 sin copia en FAM01**: no son testigo de ninguna
  afirmación. U59 las rechaza por AUSENTE y T7 no las usa. La etapa exige
  que el número de rechazadas sea exactamente ese y que ninguna sea testigo.
- **7 posiciones de testigo sin filas** (4 celdas que no están en pv12): T7
  las cuenta como «sin filas», igual que la cobertura de rem108.
- **Resumen A2**: `segundos` es la duración de esta ejecución (2,4 s frente a
  0,9 s en rem134). Es una diferencia de procedencia de tiempo, ligada.
- **Separador de rutas**: `H30_INDICE_DERIVACION.json` guarda dos campos
  `ruta` con el separador del sistema. En Windows coinciden byte a byte con
  rem134. En otro sistema la comparación los clasificaría como procedencia
  de ruta y comprobaría el archivo. MATRIZ_REVISADA_v4 no contiene rutas y
  su huella no depende del sistema.
- **Productos sin referencia propia**: `T7_anexo.csv` no tiene referencia en
  el catálogo y solo se registra su huella. COBERTURA.json se compara solo en
  su parte T7, porque T8 no es de FAM13.
- **Intérprete**: se usa `.venv-fam01`, como en FAM01–FAM12. Su Python base
  reside en una carpeta de entorno del árbol original. Sus lecturas (la
  biblioteca estándar) se cuentan como del intérprete; la orden no lee datos
  ni código del original. El aislamiento real pertenece a 2.4.2.

## Propuesta de cierre

Se propone cerrar la preparación de FAM13 en su alcance:

- F13-HISTORICAS: 5 productos regenerados con los bytes aceptados y 2
  autenticados con su aritmética recalculada, sin diferencias científicas.
- F13-S1: integridad conforme de los 40 públicos, el mapa y la fe de
  erratas.
- Una orden pública probada desde otra carpeta, con controles 20/20.

Se mantienen U60 sin localizar y L-F13-VALIDADOR-REM191 sin adoptar.
*(Adoptada por el autor el 2026-11-18: ver «Decisión del autor sobre U60».)*

## Lo que falta

- ~~La decisión sobre L-F13-VALIDADOR-REM191 (U60).~~ Tomada el 2026-11-18
  (ver «Decisión del autor sobre U60»).
- La ejecución general del Paso 3 y el aislamiento de 2.4.2.
- FAM14, la edición del manuscrito y la publicación (otros encargos).

## Dictamen de Codex

El 18 de noviembre de 2026 cierro la preparación de FAM13 en su alcance de regeneración documental e integridad. Ejecuté `fam13-reproducir` en una carpeta nueva y cotejé directamente los siete archivos con las rutas y huellas de la matriz F1 adoptada.

T1 (9 filas), T2 (8), T7 (224), su anexo (1.728 afirmaciones) y la matriz v4 (42 requisitos) coinciden byte a byte con sus originales. Contrasté las 3.449 posiciones de testigos T7 con el valor G y la huella de sus 1.724 archivos históricos. En la matriz v4 comprobé que se conservan 39 filas de A3. H30 queda como evidencia contemporánea, H4 como retrospectiva comprobada con hallazgo y R1 como retrospectiva comprobada.

Para E1235 i1 y E1 i2 confirmé la identidad de los archivos y de sus prerregistros, y cotejé las 85 y 21 comparaciones aritméticas registradas. Recalculé por separado la dispersión de E1 en i1 y los tres niveles Romberg de i2 a partir de los valores guardados. La i1 conserva su resultado no conforme y la i2 el conforme. La ejecución del modelo que produjo esos valores queda pendiente. U60 sigue sin identificarse y su limitación propuesta queda pendiente de decisión.

Contrasté los 40 archivos públicos de S1 y los 19 internos en origen con la aceptación rem188. Verifiqué el mapa y comprobé que restituir la ruta original en la fe de erratas pública recupera los bytes de la original. En una copia detecté que el cotejo público omitía los archivos adicionales en subcarpetas. Corregí la enumeración para comprobar las rutas relativas en todo el árbol público y amplié el caso de archivo ajeno. La entrega revisada contiene los 40 archivos esperados.

Con esa corrección repetí la orden completa en `salidas/fam13/dictamen_20261118192322904_final`. Terminó con código 0 en 9,8 s y las cinco etapas se aceptaron. Los 20 controles pasaron, incluido el traslado con el mismo intérprete y el rechazo de archivos ajenos tanto en la raíz como en subcarpetas. La instalación aislada queda para 2.4.2 y la corrida general para el Paso 3.

## Decisión del autor sobre U60 (2026-11-18, 2.1.2)

Texto adoptado por el autor:

> Para U60, adopto L-F13-VALIDADOR-REM191. F13-HISTORICAS pasa a VI. Se
> conserva la evidencia de los cinco productos regenerados y se identifica
> que los dos productos del modelo se comprobaron sobre valores guardados.

**Regla aplicada.** Es el punto 9 del §7 de F1: una fila RD cuyo validador no
está documentado pasa a VI con una limitación nueva sujeta a decisión. Así se
había propuesto en rem191. La búsqueda dirigida no encontró ninguna pista
nueva. La aceptación histórica de los siete productos se apoya en punteros
de huella (rem176), y ninguno de los 23 candidatos cita esas huellas.

**Alcance formal y lo que la base hace.**

- La fila VI acredita la integridad de los siete productos frente a las
  huellas aceptadas.
- `fam13-reproducir` no cambia y sigue haciendo más que eso:
  - regenera los cinco productos documentales;
  - autentica los dos del modelo y recalcula su aritmética desde los valores
    guardados.

  Si algo de eso falla, la orden no cumple y el balance general no da la fila
  por completa. La evidencia adicional no eleva la fila a RD.
- Ninguna otra llamada consume salidas de FAM13, así que el cambio no afecta
  a operaciones posteriores.

**Lo aplicado:**

- `catalogo.json`:
  - la fila pasa a `operacion: VI`;
  - disponibilidad `COPIADA_CON_LIMITE_ADOPTADO`, sin residuos;
  - límite `L-F13-VALIDADOR-REM191`, con el texto del autor.
- `src/general.py`: los recuentos esperados pasan a 17 RN, 12 RD y 10 VI.
- `src/fam13.py`: solo los textos de U60 (`limitacion_adoptada` en lugar de
  `limitacion_propuesta`). La lógica no cambia.

**Comprobado:**

- `fam13-reproducir` en `salidas/fam13/reproducir_03` (6,5 s):
  - código 0 y `cumple: true`;
  - las cinco comparaciones aceptadas;
  - los cinco productos regenerados con las huellas aceptadas;
  - S1 conforme;
  - el bloque U60 declara la limitación adoptada.
- `local/pruebas_fam13.py` con el código nuevo
  (`salidas/fam13/pruebas_fam13_04.json`, 33,7 s) da 20/20. Entre ellos, una
  fila de T1, T7, T7_anexo o la matriz cambiada, una dispersión de E1_i2 + 1
  ulp, S1 alterado y `resultados_E1_i2.json` alterado en otra carpeta: todos
  siguen rechazados.
- El balance general (`salidas/u42_u60/`):
  - la fila aparece como VI «verificada por integridad» y «completa» con
    todas las llamadas aceptadas, con el límite al pie;
  - con `fam13-reproducir` rechazada u omitida, queda «no conforme» y
    «pendiente».
