# RESULTADO FAM08 — ENF (contraste eta_f/2 frente al padre)

Fecha: 2026-11-17 (relojes de las salidas en UTC). Base: `reproduccion_limpia`
(sin commits). El original se consultó en solo lectura.

## Estado

| Parte | Estado |
|---|---|
| Preparación | Revisada y cerrada en alcance por Codex (2026-11-17; revisión al final). Están en el paquete los once guiones ENF (copias exactas), el núcleo C0 y el código del lote 2 de FAM05, las entradas (manifiestos de mallas, techos e integración, anexos, índices, certificado y censo), las salidas aceptadas rem127/rem128 guardadas como entradas, las referencias rem127/rem128/rem131 y la receta completa. Cálculo, validación, recuperación, conciliación, integración y comparación están conectados. |
| F08-MALLAS (RN) | Tres mallas piloto (la primera frontera ENF de d, f y df) calculadas, validadas (`completa_validada`) y aceptadas: 5 + 5 + 25 filas con líneas idénticas a la referencia. Las otras 26 mallas no se calcularon. Las 23 mallas padre se reutilizan autenticadas, sin recalcular. |
| F08-PARES (RD) | Regenerada sobre entradas guardadas: 26 pares y 330 puntos idénticos byte a byte (11a9d2d7…), con 12 controles d con igualdad y 1 diferencia de topología. La procedencia mixta con las tres mallas piloto también se acepta; no acredita las otras mallas. |
| F08-TECHOS (RN) | Piloto ABL-ENF-T2 completo (2 techos y 7 comparaciones) calculado, validado y aceptado: comparaciones idénticas byte a byte y techos sin diferencias científicas. T1 y T3–T6 no se calcularon. Caso no alcanzado d59edf8a9d1461d1, sin búsqueda nueva: la T1 guardada se recupera (17 techos), el certificador existente reemite el certificado con el contenido del aceptado y la clave sigue incompleta, sin argmax. |
| F08-INTEGRAL (RD) | Regenerada sobre entradas guardadas: 26 claves (17 + 8 + 1) y 1.724 celdas, los seis productos idénticos byte a byte a rem131. La integración de procedencia mixta (T2 y mallas piloto nuevas) se acepta; no acredita las demás tareas. |
| Reproducción completa | Pendiente (Paso 3). La receta está preparada y no se ha lanzado. |

Los pilotos cubren 3 de las 29 mallas (35 de 365 filas) y 2 de los 26
techos (7 de las 1.724 comparaciones). Una malla no acredita un supremo.
COL-2024p queda fuera, pendiente por falta de testigos y no NA. FAM09 no se
ha abierto.

## Alcance

| Operación | Unidades | Referencia |
|---|---|---|
| F08-MALLAS (RN) | 29 mallas del manifiesto de mallas ENF (26 de rol ENF y 3 padres a evaluar con C0), 365 filas de puntos; 23 mallas padre reutilizadas | producto L_rem128 `frontier_result.jsonl` (11d55c44…), resultado y validación rem127 |
| F08-PARES (RD) | 26 pares padre/ENF, 330 puntos, control d y diferencias de topología | `pares_puntos.jsonl` (11a9d2d7…) y `CONCILIACION_MALLAS_ENF.json` rem128 |
| F08-TECHOS (RN) | seis tareas ABL-ENF-T1…T6 (26 techos certificados; T1 con 18 claves, T2–T4 con 2, T5 y T6 con 1) y el caso no alcanzado (recuperación de T1 y certificado) | tareas rem127 (T1) y rem128 (T2–T6), certificado aceptado (cc1aa49a…), contrastes rem128 |
| F08-INTEGRAL (RD) | 26 claves y 1.724 celdas, 144 de la clave resuelta | ensamblado y conciliación integral rem131 |

**Recuentos confirmados** desde los manifiestos y los productos, sin calcular:
- 29 mallas (26 ENF y 3 padres a evaluar con C0), 365 filas de puntos y 0
  laterales; 23 mallas padre reutilizadas (rem120, núcleo C0);
- 26 pares, 330 puntos, 12 controles d con igualdad y 1 diferencia de
  topología (un punto de PAR-ENF:d59edf8a9d1461d1); padres 23 `C0_rem120` y
  3 `C0_este_lanzamiento`;
- 26 claves = 17 (T1 recuperadas) + 8 (T2–T6 completas) + 1 (resolución del
  caso no alcanzado);
- 1.724 celdas: PER 960, COL 574 y MEX 190; por menú d 575, f 575 y df 574;
  celdas por tarea: T1 1.438, T2 7, T3 7, T4 16, T5 128 y T6 128;
- 144 celdas de la clave resuelta (PER 80, COL 48 y MEX 16);
- G negativo en 870 celdas tanto en ENF como en el padre, sin cambios de
  signo; dG entre 0 y 0,012832670219052933;
- fuera del nivel: COL-E2-2023.2024p, macro y micro, «pendiente (sin
  testigos), no NA».

**Identidades de partida**, iguales al catálogo: manifiesto de mallas
8ae8f1ca…e224, manifiesto de techos 0b27b32a…b3ad, índice integral
43b24726…1673 y manifiesto integral b752249a…0b85. Núcleo C0 d0bf5cd6…,
recalculado.

## Ruta efectiva

- **Mallas** (`fam08-unidad --tarea L1-ELAST`): la ruta L1-ELAST del lote 2
  (la misma `tarea_lote.py` de FAM05/FAM06) con el manifiesto de mallas ENF
  y el núcleo C0. Valida `validar_lote.py` del lote 2 (VALIDADOR-v2 de
  FAM05) con el manifiesto y el anexo ENF.
- **Techos** (`fam08-unidad --tarea ABL-ENF-T*`): las sentencias de
  `tarea_lote.py` de lote_enf en modo `produccion`, ejecutadas desde sus
  bytes; cada techo por `conexion_coord_cert.techo` con el núcleo C0. Se
  conservan cierre normalizado 1e-7, errores en las dos escalas, cotas,
  testigos, garantía, soporte y estados. Valida `validar_lote.py` de
  lote_enf (`validar_coord_rec.validar_tarea`). T1 se valida con la
  recuperación, no con `validar_lote`, porque su estado aceptado es
  incompleta.
- **Pares** (`fam08-conciliar`): `conciliar_mallas_enf.py` (rem126) sobre el
  producto de mallas declarado y las 23 mallas padre reutilizadas; control
  del menú d (R(τ_d, 0) no depende de eta_f) con su T1 = 1e-12 interna.
- **Recuperación** (`fam08-recuperar`): `recuperar_t1.recuperar` sobre los
  bytes de T1; `certificado_salto.main` (el certificador aceptado,
  comprobación aritmética por intervalos) reemite el certificado sobre la
  fila de T1; la recuperación se repite con el certificado guardado y con el
  reemitido; `pruebas_certificado.py` ejecuta los contrastes S1–S7.
- **Integración** (`fam08-integrar`): `ensamblar_integracion.py` y
  `conciliar_integracion.py --techos` por la ruta única
  `validar_integracion.validar_fuentes`, con una entrada declarada por
  tarea, las mallas y, si se da, un certificado reemitido.

## Extracción

`extraccion/extraer_fam08.py copiar <raíz original> <carpeta de los libros>`
copia bytes exactos, comprueba los índices del paquete y rechaza rutas
absolutas. Deja en `fuentes_fam08.json` 75 piezas propias:
- **código** (`nucleo_s6/enf/`, 11): `mallas/conciliar_mallas_enf.py`;
  `techos/tarea_lote.py`, `conexion_coord_cert.py`, `validar_lote.py` y
  `validar_coord_rec.py`; `integracion/ensamblar_integracion.py`,
  `conciliar_integracion.py`, `validar_integracion.py`, `recuperar_t1.py`,
  `certificado_salto.py` y `pruebas_certificado.py`. `recuperar_t1.py` es
  la pieza aceptada 1a5108b2… (rem130), con el diferencial declarado en el
  índice integral;
- **entradas** (`datos/fam08/`, 14): manifiestos, anexos e índices de
  mallas, techos e integración, los dos alcances (solo cruzan huellas), el
  certificado y el censo, más `pilotos.json` y `ejecucion_limpia.json`,
  datos nuevos sin resultados;
- **salidas aceptadas guardadas** (`datos/fam08/guardadas/`, 20): las mallas
  y T1 rem127 y T2–T6 rem128, entradas de las regeneraciones y referencia
  de las comparaciones de cálculo;
- **referencias** (`referencias/fam08/`, 30): rem127 (3), rem128 (17:
  validaciones, conciliación de mallas y diagnóstico del certificado) y
  rem131 (10: ensamblado y conciliación integral).

**Proyecciones saneadas** (SANEADO-v1): el certificado, el censo y tres
documentos de referencia (conciliación de mallas, ensamblado integral y
conciliación integral). Solo se sustituye la procedencia privada por un
marcador; la extracción comprueba que cada proyección restituye su original
al reponerla, y el código autentica por esa correspondencia. La referencia
rem131 `pares_puntos.jsonl` tiene los mismos bytes que la de rem128.

Se declaran 12 piezas **reutilizadas** sin copiarlas otra vez: manifiestos
del lote 1, del lote 2 y E4, las fuentes de mallas padre rem112/rem120/rem121,
la procedencia del suplemento rem120, el índice y los cuatro guiones del
lote 2. El **núcleo C0** es el de FAM05 (37 archivos, identidad d0bf5cd6…).

**Libros rem128, rem129 y rem132 y sus dictámenes.** Solo se consultaron
para localizar las fuentes; no se leen al ejecutar. `fuentes_fam08.json`
guarda un resumen sin rutas ni transcripciones, y `fam08-comprobar` coteja
sus 12 recuentos con los archivos. **Rutas:** 0 rutas personales en las
piezas.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1, bajo el supervisor del paquete
fuente (un proceso a la vez):

```text
reproducir.py fam08-listar    --salida salidas/fam08/listar.json
reproducir.py fam08-comprobar --salida salidas/fam08/comprobar_03.json
reproducir.py fam08-unidad    --tarea L1-ELAST --unidad FRN-ENF:230651ca1f23127881ca --salida salidas/fam08/piloto_02/malla_d
reproducir.py fam08-unidad    --tarea ABL-ENF-T2 --tope 2400 --salida salidas/fam08/piloto_02/ABL-ENF-T2
reproducir.py fam08-validar   --nueva salidas/fam08/piloto_02/ABL-ENF-T2 --salida salidas/fam08/piloto_02/ABL-ENF-T2.validacion.json
reproducir.py fam08-comparar  --tarea ABL-ENF-T2 --nueva salidas/fam08/piloto_02/ABL-ENF-T2 --validacion salidas/fam08/piloto_02/ABL-ENF-T2.validacion.json --salida salidas/fam08/piloto_02/ABL-ENF-T2.comparacion.json
reproducir.py fam08-conciliar --entrada mallas=guardado --salida salidas/fam08/regeneracion_02/pares
reproducir.py fam08-recuperar --entrada ABL-ENF-T1=guardado --salida salidas/fam08/regeneracion_02/recuperacion
reproducir.py fam08-integrar  --entrada ABL-ENF-T1=guardado … --entrada ABL-ENF-T6=guardado --entrada mallas=guardado --salida salidas/fam08/regeneracion_02/integral
reproducir.py fam08-conciliar --entrada mallas=guardado --entrada piloto=salidas/fam08/piloto_02/malla_d --entrada piloto=…/malla_f --entrada piloto=…/malla_df --salida salidas/fam08/mixta_03/pares
reproducir.py fam08-integrar  --entrada ABL-ENF-T2=salidas/fam08/piloto_02/ABL-ENF-T2 (las demás =guardado) --entrada mallas=guardado --entrada piloto=… (tres) --salida salidas/fam08/mixta_03/integral
reproducir.py fam08-comparar  --tarea PARES|RECUPERACION|INTEGRAL --nueva <carpeta> --salida <archivo nuevo>.json
reproducir.py fam08-receta    --salida salidas/fam08/receta_01.json
```

- **Sin cálculo científico**: `fam08-listar`, `fam08-comprobar`,
  `fam08-validar`, `fam08-conciliar`, `fam08-integrar`, `fam08-comparar` y
  `fam08-receta`. `fam08-recuperar` no busca techos: ejecuta el
  certificador aceptado (su comprobación aritmética por intervalos) sobre
  la fila guardada.
- **`fam08-unidad`**: una tarea entera (`L1-ELAST`, con `--unidad` para una
  malla, o `ABL-ENF-T1…T6`). Se niega antes de crear la carpeta si falta o
  cambió una dependencia o si el núcleo C0 no tiene su identidad. Exige
  `PYTHONHASHSEED=0` efectivo.
- **Entradas declaradas**: cada tarea y las mallas entran con `--entrada
  <nombre>=<carpeta nueva|guardado>`; `piloto=<carpeta>` sustituye las
  filas de una malla piloto validada (procedencia mixta) y
  `certificado=<archivo>` da el certificado reemitido. Una entrada que
  falta no se sustituye por su referencia. Cada salida declara su
  naturaleza: «regeneración sobre entradas guardadas», «procedencia mixta»
  o el cálculo nuevo.
- **Separación**: cálculo, validación, recuperación, conciliación,
  integración y comparación son pasos aparte; cada uno termina con 0 solo
  en su caso aceptado.

## Adaptaciones (declaradas en `src/fam08.py`)

No cambian fórmulas, claves, tolerancias, presupuestos, garantías ni
criterios. Cada original se sustituye una sola vez:
- **GUION-v1** (de FAM07): cada guion de `nucleo_s6/enf` se ejecuta desde
  sus bytes exactos con sus sustituciones de texto.
- **MODULOS-v1**: `validar_coord_rec`, `certificado_salto`, `recuperar_t1` y
  `validar_integracion` se cargan como módulos desde su texto adaptado; las
  piezas que antes los cargaban de su archivo usan esos módulos.
- **NUCLEO-C0-v1** (de FAM05): el núcleo es `nucleo_s6/c0`.
- **RUTAS-FUENTES-v1**: toda fuente se lee de su copia en la base (tabla de
  rutas históricas) y se sigue autenticando por sus bytes; una ruta no
  declarada falla.
- **SANEADO-v1**: el certificado y el censo son proyecciones saneadas; se
  autentican por la correspondencia proyección → original, y la huella que
  registran los productos es la del original.
- **PUERTA-v1**: las puertas de producción (alcance v3 verificado y decisión
  humana) no se ejecutan ni se reconstruyen. El `alcance_sha256` lleva el
  sha256 de `datos/fam08/ejecucion_limpia.json` (61ac1d74…), una
  declaración NO OFICIAL; no hay decisión (`decision` = null).
- **PAQUETE-v1**: la integración autentica las cinco piezas copiadas contra
  su índice (43b24726…). Las otras tres del índice (emisión de alcance,
  admisión y guion de receta) son de la autorización histórica y no se
  copian.
- **ENTRADAS-v1 / ENTRADAS-MALLAS-v1**: tareas y mallas desde una carpeta
  declarada. «guardado» usa los pines del manifiesto integral; en una
  salida nueva los pines pasan a ser las huellas de sus propios bytes
  (vínculo declarado).
- **VALIDADOR-ELAST-v1**: el validador ELAST del lote 2 se ejecuta en el
  mismo proceso, con los mismos argumentos y criterio; su ruta se registra
  relativa.
- **RUTA-VISIBLE-v1**: el certificador registra la ruta de su fuente
  relativa a la raíz (el original escribía la absoluta).
- **RELOJ-PILOTO-v1** (de FAM05): reloj interno 2280 s (el
  `tope_efectivo_s` histórico); el límite externo lo pone el supervisor.

## Comprobación (`fam08-comprobar`, sin cálculo; 0,8 s)

Cumple en todos sus apartados (`comprobar_02.json` con el código de los
pilotos y `comprobar_03.json` con el código y el catálogo finales):
- 75 piezas propias, 12 reutilizadas y 37 del núcleo C0 con sus huellas;
  identidad C0 recalculada igual a d0bf5cd6…;
- procedencia: código igual a su índice; tres índices, manifiestos e
  identidades iguales al catálogo; guardadas iguales a sus pines;
  proyecciones con correspondencia; certificado y censo ligados;
  sustituciones únicas; declaración de ejecución limpia igual a su regla;
- motor, sin calcular: identidad de código, configuración, certificación en
  esta plataforma y garantía iguales a las del manifiesto;
- cobertura con los recuentos de «Alcance» y universo igual al del
  manifiesto integral;
- referencias iguales al catálogo;
- revalidación de las guardadas: T2–T6 y mallas `completa_validada`,
  iguales a la validación histórica; T1 `recuperacion_parcial_validada` (17
  reutilizables, 1.294 comparaciones; la clave d59edf8a9d1461d1 pendiente);
- 12 recuentos de los libros rem128/rem129/rem132 iguales a los archivos;
  pilotos iguales a su regla; receta de 10 pasos.

## Comparación (COMPARACION-FAM08-v1)

Mismo perfil de entorno y mismo núcleo C0 que las referencias, así que la
comparación es exacta:
- **CR-HASH-CANONICO**: cada fila idéntica campo a campo (valores, cotas,
  errores en sus escalas, testigos, topología, niveles);
- **CR-DISCRETOS**: claves, celdas, estados, clasificaciones, garantías,
  certificados y recuentos, con precedencia.

Se apartan, visibles, solo campos operativos concretos:
- OPERATIVO: `segundos` y `pared_s`;
- VINCULO: `alcance_sha256` y las huellas de entradas nuevas, comprobadas en
  cada lado contra sus propios bytes;
- PUERTA: `puerta/alcance_sha256` y `decision`;
- UBICACION: carpetas, la ruta del validador ELAST y la ruta de la fuente
  del certificado.

Las huellas derivadas reponen esos campos desde la referencia, usan el fin
de línea de los bytes nuevos (los productores escriben en modo texto) y se
comparan con los bytes de la referencia. Las tolerancias internas de los
validadores (la T1 = 1e-12 del control d, los encierros, el 1e-7) son suyas
y no se usan como tolerancia de reproducción.

## Pilotos (cálculo autorizado)

**Selección**, fijada por el encargo antes de calcular, en
`datos/fam08/pilotos.json`: la primera frontera ENF de cada menú, completa,
y la tarea ABL-ENF-T2 completa (claves 57e622fb22a3ad95 y 29f1e9137a358a6f,
2 techos y 7 comparaciones). No se redujo el problema.

**Mallas** (`piloto_02`, límite externo 600 s cada una):

| Malla | Menú | Filas | Regímenes y topologías | Pared (s) |
|---|---|---|---|---|
| FRN-ENF:230651ca1f23127881ca | d (1D) | 5 | origen 1, esquina_f 4; FF 1, II->IF->FF 4 | 2,8 |
| FRN-ENF:75a283726bb5e755b89d | f (1D) | 5 | origen 1, esquina_d 4; FF 5 | 2,1 |
| FRN-ENF:075cb6d4080fc856e386 | df (2D) | 25 | origen 1, esquinas 4 + 4, interior 9, borde 7; FF 5, II->IF->FF 20 | 2,5 |

Las tres se validaron (`completa_validada`, igual al veredicto histórico) y
se aceptaron: mismas filas, mismo orden y líneas idénticas a las de esa
malla en la referencia. Son mallas, no supremos.

**Tarea ABL-ENF-T2** (`piloto_02`, límite externo 2400 s, reloj interno
2280 s):
- supervisor: TERMINO, código 0, 2.347,8 s de pared, 1.917,7 s de CPU,
  294,8 MB de memoria pico del Job y 0 procesos activos al terminar;
- trabajador: `completa`, sin motivo.

| Clave | Diseño | C_2 | error normalizado | error en R | final_n | s (referencia) |
|---|---|---|---|---|---|---|
| 57e622fb22a3ad95 | N | 0.0022480208932554374 | 4,45e-8 | 8,50e-8 | 4.633 | 1.105,9 (318,6) |
| 29f1e9137a358a6f | N | 0.0011005388264753652 | 4,99e-8 | 8,83e-8 | 6.542 | 1.238,3 (427,8) |

Ambos techos son `complete`, `certified_bound` e `ieee754_binary64_rn`, con
cierre en R y en la escala normalizada. Valores, cotas, errores, testigos y
configuración son exactamente los de rem128.
- **Validación**: `completa_validada`, sin fallos; igual a la histórica
  salvo las huellas propias.
- **Comparación** (`ABL-ENF-T2.comparacion.json`): aceptada.
  - `enf_comparacion.jsonl`: 7 filas idénticas byte a byte (d92e85ce…);
    G = C2' − K1 en las 7.
  - `enf_techos.jsonl`: 0 diferencias discretas y 0 numéricas. Solo se
    apartan `segundos` y el vínculo `alcance_sha256`; la huella derivada
    es 263ecb9c…, igual a los bytes de la referencia.
  - Resultado, identidades (manifiesto, código, núcleo C0) y cobertura de
    claves y celdas iguales.

**Lecturas reales** (`archivos_leidos.json` de cada piloto): 72 archivos del
paquete (37 del núcleo C0, los guiones ENF y las entradas, cuyas huellas se
comprueban antes de calcular), 0 fuera del paquete y del intérprete, 0 sin
declarar. Ninguna salida guardada ni referencia leída
(`guardadas_leidas: []`, `referencias_leidas: []`). Fuera de la biblioteca
estándar solo numpy 2.0.2.

**Primera corrida** (`piloto_01`, conservada): los mismos cálculos con el
código anterior a la corrección de la auditoría (abajo). Dio exactamente
los mismos productos (mismas líneas en las mallas; mismos valores y
comparaciones en T2, con 1.773,8 s de pared), pero su comprobación previa
de dependencias abría las salidas guardadas para autenticarlas.

## Caso no alcanzado (d59edf8a9d1461d1)

La clave tiene cuatro elementos que se mantienen separados
(`RECUPERACION_T1.json`, apartado `separados`):
- **T1 sigue incompleta**: la fila persistida es `incomplete`, con motivo
  `SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE`, `attained` falso y sin argmax.
  Ni la recuperación ni la integración la convierten en completa.
- **Punto factible guardado**: lower_R 8,78074346560998, upper_R
  8,78074346561024 y C_2 0.7982494059645469. Es solo una cota inferior,
  no un maximizador.
- **Recuperación de 17 claves**: `recuperar_t1` valida 17 techos cerrados y
  1.294 comparaciones reutilizables (`recuperacion_parcial_validada`); sin
  certificado, la clave queda `no_decidido`.
- **Certificado y 144 celdas**: `certificado_salto.py` (la pieza aceptada,
  sin otra prueba) reemite el certificado sobre la fila de T1:
  `no_alcanzado_demostrado`, supremo lateral no alcanzado (τ_d desde abajo
  en [0.5937443203343036, 0.5937443203343207], τ_f = 0,6; límite en R en
  [8.780743465609994, 8.780743465610234]; valor en la curva 0). Las 144
  celdas de la clave toman ese estado.

Medido en `regeneracion_02` (T1 guardada; sin búsqueda de techos):
- el certificado reemitido (e738ff01…) es igual a la proyección aceptada
  salvo la ruta de su fuente; al reponerla, la huella es la de la
  proyección (9e2ac472…), que restituye el original cc1aa49a…;
- la salida del certificador es igual a la histórica;
- con el certificado guardado y con el reemitido: `no_alcanzado_demostrado`,
  estado persistido `incomplete`, 17 reutilizables;
- los contrastes S1–S7 dan 7/7, idénticos byte a byte a rem128 (dae67353…);
  el control positivo S7 (la clave real) da `no_alcanzado_demostrado`.

La regla no se generaliza: el certificador se aplica solo a esta clave
exacta y sus hipótesis H0–H6 se comprueban en cada ejecución.

**Ruta de una T1 nueva** (la que usa la receta): se ejercitó sin cálculo en
`controles_02` con la T1 guardada re-ligada a la declaración, como la
escribiría `fam08-unidad`. La recuperación se acepta con el certificado
reemitido. El guardado está ligado a los bytes históricos y sobre bytes
nuevos deja la clave `no_decidido` (fuente no auténtica), como debe. La
comparación de T1 y de la recuperación y la integración con el certificado
reemitido se aceptan, con vínculos ligados en cada lado y huellas derivadas
iguales.

## Regeneraciones y procedencia mixta

**Regeneración sobre entradas guardadas** (`regeneracion_02`, código final):
- **Pares**: 26 pares y 330 puntos, idénticos byte a byte (11a9d2d7…); 12
  controles d con igualdad; 1 punto con cambio de topología, en
  PAR-ENF:d59edf8a9d1461d1; padres 23 `C0_rem120` y 3
  `C0_este_lanzamiento`. `CONCILIACION_MALLAS_ENF.json` igual a su
  proyección salvo la ruta del validador ELAST (ubicación).
- **Recuperación**: la descrita arriba.
- **Integral**: los seis productos idénticos byte a byte a rem131; 26 claves
  (17 + 8 + 1), 1.724 celdas (PER 960, COL 574, MEX 190; d 575, f 575, df
  574), 144 resueltas, G negativo 870/870, 0 cambios de signo, dG máximo
  0,012832670219052933, COL-2024p fuera. `ENSAMBLADO_INTEGRAL.json` y
  `CONCILIACION_INTEGRAL_ENF.json` iguales a sus proyecciones salvo puerta y
  ubicación, que se muestran. Veredictos del ensamblador y del conciliador
  iguales a los históricos.

Ninguna regeneración lee las referencias: solo autentican y usan las
guardadas declaradas como entrada (la conciliación, las mallas; la
recuperación, T1; la integración, las seis tareas y las mallas). Son
regeneraciones y no acreditan F08-MALLAS ni F08-TECHOS. `regeneracion_01`
(código anterior) dio los mismos bytes.

**Procedencia mixta** (`mixta_03`): las tres mallas piloto y T2 de
`piloto_02`; el resto, guardado. La salida lo declara y dice qué acredita:
la conexión de las salidas nuevas, no el cálculo de las demás.
- **Pares**: aceptada, 330 filas idénticas byte a byte y recuentos iguales.
- **Integral**: aceptada.
  - `enf_techos_integrados.jsonl`: 26 filas sin diferencias discretas ni
    numéricas. En las dos filas de T2 se apartan `segundos` y los vínculos
    de origen; la huella derivada es 31ee1d74…, igual a la referencia.
  - Los otros cinco productos, idénticos byte a byte.
  - Recuentos y veredictos iguales.
  - La T2 guardada no se abre.

## Controles (`local/pruebas_fam08.py`, sin cálculo científico)

`controles_02.json`: 35/35 conformes en 27,2 s, con el código final y las
copias alteradas en `salidas/fam08/controles_02`. Por riesgo:
- **Valor o cota alterados**: C_2 + 1 ulp en T2 (comparaciones recompuestas)
  y R + 1 ulp en una fila de la malla d dan DIFERENCIA_NUMERICA en la
  comparación exacta. Una cota superior más ancha que el error declarado da
  COTA_NO_RESPALDA_EL_VALOR en la validación y no se acepta.
- **Clave o celda omitida o duplicada**:
  - en T2, un techo omitido con sus comparaciones (COBERTURA_DE_TECHOS) y
    una comparación duplicada (COMPARACIONES_NO_CORRESPONDEN);
  - una fila omitida en la malla d, que rechazan el validador ELAST y la
    comparación;
  - en la integración, una celda omitida y otra duplicada
    (CELDA_DUPLICADA_EN_EL_MANIFIESTO), rechazadas por la ruta única.
- **Referencia o validación equivocada**:
  - T2 comparada como T3 (SALIDA_DE_OTRA_TAREA);
  - la malla d con la validación de la malla f (VALIDACION_DE_OTROS_BYTES);
  - una T2 guardada alterada (REFERENCIA_ALTERADA_O_AJENA);
  - la carpeta de T3 declarada como T2;
  - la integración sin T3 (rechazada; no se sustituye por su referencia);
  - un piloto sin validación (PILOTO_SIN_VALIDACION_O_SIN_EJECUCION);
  - un censo con ruta no declarada (FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA).
- **Supremo convertido en máximo**:
  - un certificado «alcanzado» con argmax, que la integración rechaza
    (CERTIFICADO_NO_REPRODUCIDO_O_NO_DECIDIDO, porque el recálculo no da un
    máximo);
  - T1 con la fila abierta promovida a completa y alcanzada, que la
    recuperación no acepta como techo cerrado y la integración rechaza;
  - una integración con argmax y `sup_not_attained` falso, que no se
    acepta (DIFERENCIA_DISCRETA y recuento `sin_argmax` distinto).
- **Controles positivos**:
  - la resolución con el certificado guardado y con el reemitido
    (`no_alcanzado_demostrado`, T1 incompleta, 17 reutilizables);
  - la diferencia de topología válida, que se conserva y se acepta;
  - si esa diferencia se borra, el conciliador la acepta, porque solo la
    informa, y la comparación la rechaza;
  - la ruta de una T1 nueva (arriba).
- **Otra carpeta y dependencia ausente** (copia fuera del paquete, mismo
  intérprete):
  - `fam08-comprobar` cumple;
  - los pilotos guardados se validan y se aceptan;
  - las tres regeneraciones y la integración mixta se aceptan.
  - Sin `conexion_coord_cert.py`, `certificado_salto.py`, el `resultado.json`
    de T4 guardada o las filas padre rem120, `fam08-comprobar` no cumple y
    lo informa. `fam08-unidad`, `fam08-recuperar`, `fam08-validar`,
    `fam08-integrar` y `fam08-conciliar` se niegan antes de actuar
    (DEPENDENCIA_AUSENTE_O_ALTERADA), sin crear salida.

El guion de controles se ejecutó fuera del supervisor, como en FAM06 y
FAM07, y no contiene cálculo científico. `controles_01` (34/34, código
anterior) se conserva. **Regresión breve** (`reproducir.py` es compartido):
`revisar` y `fam01-comprobar` a `fam07-comprobar` terminan con código 0
(`regresion_fam0*_comprobar.json`). Tras actualizar el catálogo se
repitieron `revisar`, `fam07-comprobar` y `fam08-comprobar`, también con
código 0.

## Tiempos medidos

| Invocación | Pared (s) | CPU (s) | Memoria pico del Job (MB) |
|---|---|---|---|
| `fam08-unidad` ABL-ENF-T2, `piloto_02` (techos 1.105,9 + 1.238,3) | 2.347,8 | 1.917,7 | 294,8 |
| `fam08-unidad` ABL-ENF-T2, `piloto_01` (techos 715,2 + 1.055,3) | 1.773,8 | 1.591,1 | 293,2 |
| `fam08-unidad` mallas piloto d / f / df (`piloto_02`) | 2,8 / 2,1 / 2,5 | 1,9 / 1,7 / 1,8 | 40–41 |
| `fam08-validar` y `fam08-comparar` de los pilotos | 0,3–1,1 | ≤ 0,8 | ≤ 33 |
| `fam08-conciliar` / `fam08-recuperar` / `fam08-integrar` | 0,6–1,1 | ≤ 0,9 | 48–72 |
| `fam08-comprobar` (final) | 0,8 | 0,6 | 48,4 |
| controles (35, fuera del supervisor) | 27,2 | — | — |

Referencia histórica de T2: 746,7 s de pared (318,6 + 427,8 s por techo);
T3 773,1 s, T4 667,2 s, T5 665,9 s, T6 700,6 s y T1 (incompleta) 135,5 s.
Las dos corridas de T2 tardaron entre 2,4 y 3,1 veces la referencia. En la
segunda había otra instancia ajena con 15 procesos Python que ocupaban las
16 CPU; la proporción CPU/pared bajó a 0,67 en sus primeros minutos. Los
valores no cambiaron. `piloto_02` terminó a 52 s del límite externo: con
esa carga, una tarea completa podría agotarlo. Son antecedentes, no
estimaciones. El resumen sin rutas está en `salidas/fam08/lanzador.txt`.

## Correcciones rutinarias de esta sesión

- **`comprobar_01` no cumplía** por errores de la propia comprobación:
  - el universo se cotejaba con un sufijo `.ABL-ENF` mal quitado;
  - la lista de productos de rem132 estaba incompleta;
  - los excluidos se buscaban en otro apartado del libro.

  Corregido; `comprobar_02` y `comprobar_03` cumplen.
- **Huella derivada del certificado**: se reserializaba en LF y el
  certificador escribe en modo texto (CRLF en Windows). Ahora usa el fin de
  línea de los bytes nuevos, igual que FAM07. `recuperacion.comparacion_02`
  quedó aceptada sin repetir la recuperación; la primera
  (`recuperacion.comparacion.json`, no aceptada por
  HUELLA_DERIVADA_DISTINTA) se conserva.
- **Auditoría de lecturas**: la comprobación previa de dependencias
  autenticaba también las salidas guardadas, que el rastro registraba como
  abiertas. El cálculo y la validación ya no las abren, y las regeneraciones
  solo autentican las guardadas declaradas como entrada. Los pilotos se
  repitieron como `piloto_02` (mismos productos) y las regeneraciones y la
  conexión mixta como `regeneracion_02` y `mixta_03` (mismos bytes).
  `piloto_01`, `regeneracion_01` y `mixta_01` se conservan.
- **Ruta de una T1 nueva**: la comparación de la recuperación exigía que el
  certificado guardado decidiera también sobre una T1 nueva. Ese
  certificado está ligado a los bytes históricos y sobre bytes nuevos no
  decide. Ahora, para una T1 nueva, se exige `no_decidido` con fuente no
  auténtica, y se añadió el control positivo de esa ruta.
- **Inventario**: la descripción de `fuentes_fam08.json` decía «cuatro»
  proyecciones saneadas; son cinco. Se corrigió y se repitió la extracción,
  con los mismos recuentos.
- **Error de lanzamiento en `mixta_02`**: la integración se lanzó sin el
  verbo `fam08-integrar` (argparse, código 2) y su comparación falló por
  falta de salida (`integral.comparacion.json`). Ambos se conservan; la
  integración repetida se aceptó (`integral.comparacion_02.json`).
- Ningún cambio tocó el cálculo científico.

## Límites

- Solo T2 y tres mallas tienen cálculo nuevo. T1, T3–T6 y las otras 26
  mallas no se calcularon; en las conexiones mixtas entran guardadas y no se
  acreditan.
- El caso no alcanzado se trata sobre la T1 guardada: el certificado se
  reemite con el certificador aceptado, pero T1 no se recalculó.
- Las puertas de producción históricas no se reproducen (PUERTA-v1); la
  ejecución limpia no es una producción oficial.
- La duración de T2 dependió de la carga de la máquina; la receta usa el
  mismo límite externo de 2400 s que la historia, sin margen garantizado.
- Los registros del supervisor (`lanzador/*.tarea.json`) guardan rutas
  absolutas de esta máquina; `lanzador.txt` es el resumen sin rutas.
- El aislamiento real queda pendiente en 2.4.2. FAM09 no se ha abierto.

## Receta completa (preparada, no ejecutada)

`receta_01.json`, en este orden:
1. `fam08-comprobar`;
2. las 29 mallas (`fam08-unidad`, `fam08-validar` y `fam08-comparar`);
3. T1 con `fam08-recuperar` sobre la T1 nueva (que reemite el certificado
   sobre su fila) y las comparaciones de T1 y de la recuperación;
4. T2–T6, cada una con `fam08-unidad`, `fam08-validar` y `fam08-comparar`;
5. los pares sobre las mallas nuevas;
6. la integración con las seis tareas nuevas, las mallas nuevas y el
   certificado reemitido, y su comparación.

Condiciones:
- una tarea a la vez, sin reintentos;
- límite externo de 2400 s por tarea (reloj interno 2280 s);
- si una tarea no termina en su estado aceptado (T2–T6 completas y
  validadas; T1 incompleta solo en d59edf8a9d1461d1 y recuperada), no se
  concilia ni se integra;
- una entrada faltante no se sustituye por su referencia.

Cubre 29 mallas, 26 techos, 26 pares y 1.724 celdas, y reutiliza las 23
mallas padre y el censo. No se estima su duración.

## Propuesta de cierre

Propongo cerrar la **preparación** de FAM08 en su alcance:
- las cuatro operaciones están conectadas, con entradas y referencias
  completas en el paquete y 0 rutas personales;
- los guiones ENF se ejecutan desde sus bytes con adaptaciones declaradas
  que no cambian la ciencia, y el núcleo C0 de FAM05 se reutiliza;
- el caso no alcanzado conserva separados certificado, punto factible,
  recuperación y celdas, sin argmax;
- los pilotos, las regeneraciones, la conexión mixta y los 35 controles son
  conformes, y la receta completa está disponible, sin lanzar.

Distinción de lo que acredita cada parte:
- **Cálculo realmente comprobado**: tres mallas (35 filas) y la tarea T2 (2
  techos y 7 comparaciones), exactos frente a la referencia.
- **Ejecución del certificador existente sobre bytes guardados**: el
  certificado reemitido, igual al aceptado; no es un techo nuevo ni una
  prueba nueva.
- **Regeneración sobre entradas guardadas**: 26 pares y 330 puntos, la
  recuperación de T1 y la integración de 26 claves y 1.724 celdas, idénticas
  byte a byte. No acreditan F08-MALLAS ni F08-TECHOS.
- **Procedencia mixta**: la conexión de las mallas piloto y de T2 a los
  pares y a la integración; no acredita lo demás.
- **Preparación sin ejecución**: T1, T3–T6, las otras 26 mallas, y los pares
  y la integración sobre salidas nuevas (Paso 3).

No hay faltantes de implementación conocidos para la receta. La ruta de
una T1 nueva se probó con bytes guardados re-ligados, no con un cálculo de
T1.

## Siguiente trabajo

- Preparación revisada y cerrada en alcance por Codex (véase abajo).
- T1, T3–T6, las 29 mallas y la integración sobre salidas nuevas
  pertenecen al Paso 3.
- El aislamiento efectivo de FAM08 queda para 2.4.2.
- Siguiente familia prevista: FAM11 (COV/B1/B2), según el orden del plan.
  No se abre otra familia en esta revisión.

## Revisión de Codex — 2026-11-17

Preparación de FAM08 cerrada en su alcance, sin hallazgos bloqueantes.
Se aceptan los tres pilotos de mallas y T2, la recuperación y el certificado
reemitido sobre T1 guardada, y las regeneraciones guardadas y mixtas con sus
límites declarados. Esto no declara reproducido el lote completo.

Se revisaron las adaptaciones, las rutas de cálculo y validación, los
comparadores y el tratamiento del caso no alcanzado. El cotejo independiente
comprobó las huellas de las 75 fuentes propias, 12 reutilizadas y 37 archivos
de C0. La transformación eta_f/2 conserva el resto de las entradas padre en
las 26 claves.

Las 35 filas de las tres mallas son idénticas a sus referencias. Los dos
techos de T2 coinciden en los campos científicos, certificados, configuración
y garantías; solo difieren tiempos y vínculo de alcance, comprobado en cada
lado. Las siete comparaciones son idénticas byte a byte. Una nueva validación
y comparación de los cuatro pilotos volvió a dar aceptación, sin repetir
ningún cálculo de mallas ni búsqueda de techos. Sus registros de lecturas no
contienen referencias, resultados guardados ni archivos ajenos al paquete y
al intérprete.

En los ensamblados guardado y mixto se cotejaron las 26 claves y las 1.724
celdas contra el manifiesto, sin duplicados ni faltantes. K1 y G padre se
conservan; G_enf = C2_enf − K1 y dG se recomponen en todas las celdas. Se
confirman 870/870 G negativos y ningún cambio de signo. Los 26 pares/330
puntos coinciden con las referencias y conservan el único cambio de
topología. Los seis productos de la integración guardada son idénticos a
los aceptados.

La clave d59edf8a9d1461d1 conserva T1 incompleta, el punto factible como
cota inferior y el supremo no alcanzado sin argmax. Las 144 celdas resueltas
mantienen su origen explícito. Además del control del ejecutor, se probó la
conexión sobre una copia local de T1 con tiempos y vínculos distintos: el
certificado histórico no decide sobre esos bytes; el reemitido los liga y
la recuperación, comparación e integración resultan aceptadas. Es un
control de interfaz sobre datos guardados, no una ejecución numérica de T1.

Se revisaron los 35 controles guardados y sus causas, sin repetir la batería
general. Evidencia: `local/revision_codex_fam08/resumen.json`. No se modificaron
código científico, adaptador, entradas, referencias ni salidas del ejecutor.

Quedan el lote completo del Paso 3 y el aislamiento real de 2.4.2. T2 terminó
a unos 52 s del límite externo; ese margen se tendrá en cuenta al concretar
los recursos del Paso 3, sin inferir la duración total ni ampliar límites en
esta revisión. F2 no se extiende. Los registros privados del supervisor
siguen fuera de los archivos destinados a distribución.
