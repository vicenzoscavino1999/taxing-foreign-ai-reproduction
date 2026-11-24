# Familias de resultados

FAM12 está comprobada y revisada en el alcance de entradas ligadas guardadas:
cuatro K1, suplemento P7 y Q local. Reutiliza techos aceptados; no reconstruye
la selección de entradas desde los datos nacionales originales. La instalación
aislada sigue pendiente.

FAM01: preparación técnica cerrada en su alcance, revisada por Codex y con
F2 adoptada por el autor (2026-11-16).
- el marco R3 de 536 y la muestra quedan cerrados en alcance documental;
- referencias de las 1.767 unidades presentes;
- cálculo, validación productiva y comparación conectados, y receta
  preparada sin ejecutar;
- comparación limpia separada de la histórica: E2/E3 con el nivel R1 real y
  los dos campos de historial de 195 originales R2 como procedencia;
- nueve archivos de ejecución saneados, con correspondencia comprobada;
- los pilotos R2 y R3, repetidos con las copias públicas, quedan calculados
  y validados con valores iguales; las 5 NA están comprobadas.

Los pilotos revisados quedan aceptados bajo F2 adoptada. Sus archivos
conservan la etiqueta candidata previa a la decisión y el rechazo del
comparador histórico. El comparador registra ahora la adopción: las
comparaciones nuevas de los mismos pilotos dan
`aceptada_comparacion_limpia_con_F2`, con código 0. Los lotes completos esperan el Paso 3; la instalación
aislada sigue pendiente en 2.4.2.
Detalle en `RESULTADO_FAM01.md`.

FAM02 (R1, 18 tareas): preparación cerrada en alcance por Codex (2026-11-16).
Las 18 tareas están conectadas. Solo los dos pilotos tienen cálculo; la
reproducción completa no está ejecutada.
- **Extracción**: código, entradas y referencias de la ruta R1 instalada
  (466 piezas). Los 113 registros de lanzamiento están en copia pública
  SAN-RUTAS-v1, sin rutas personales.
- **Conectadas**: las 18 tareas, con el enlace local de aceptación entre
  tareas de una misma ejecución (ENLACE-LOCAL-FAM02-v1, sin reconstruir la
  autorización histórica).
- **Probadas sin cálculo**:
  - las 10 rutas por comando, con salidas guardadas (prueba de conexión,
    nunca reproducción);
  - D, rechazada antes de calcular sin C1–C6;
  - V, rechazada con 10 de 17 fuentes;
  - 11 casos de fallo y control, el traslado y la regresión.
- **Probado con cálculo**:
  - una hoja de R1-C1 (61,7 s), igual a la referencia citada;
  - la tarea R1-F (14,3 s), sin lecturas externas ni dependencias
    faltantes. La regla instalada la rechazó por 4 campos de reloj, y el
    rechazo se conserva. Con la corrección técnica limitada a esos campos
    (IGUALDAD-R1F-TIEMPOS-v1), la revalidación sin cálculo está aceptada y
    enlazada.

Pendiente: instalación aislada (2.4.2) y ejecución completa (Paso 3).
A*/B* no tienen cálculo real y D/V no tienen aceptación global positiva.
No se exige otra ronda de pilotos para cerrar esta preparación. F2 no se
extiende a FAM02; la regla R1 no exige esa adopción para aceptar lo comprobado.
Detalle en `RESULTADO_FAM02.md`.

FAM03 (quiebres PROD1/PROD2 y Q histórica PROD3): preparación cerrada
en alcance por Codex (2026-11-16). Son 152 unidades, 136
tareas y 136 árboles: 40 PROD1, 80 PROD2 y 16 tareas PROD3 con 32 salidas
Q.
- **Extracción**: la ruta PROD instalada (`tarea_prod` U08 y
  `validador_prod` U09, con `evaluadores_ra`), el área R-A y los 136 árboles
  de referencia. Son 800 piezas, con 0 rutas personales.
- **Plan limpio** igual al histórico salvo las identidades de esta base,
  con las decisiones Q y D4 selladas. La ruta ejecutada de PROD3 no consume
  un resumen de detalle (`resumen_q` nulo).
- **Probado con cálculo**: tres pilotos, PROD1-T001 (18,6 s), PROD2-T006
  (9,6 s, declarado D4) y PROD3-T121 (12,9 s, dos salidas Q).
  - Validados, y aceptados con igualdad exacta del contenido científico y
    la misma clasificación.
  - 0 lecturas fuera del paquete.
- **Controles**: 17/17 sin cálculo científico; regresión de FAM01/FAM02
  conforme.

Pendiente: la ejecución de las 136 tareas (Paso 3) y el aislamiento
(2.4.2). Detalle en `RESULTADO_FAM03.md`.

FAM04 (lote 1: ELAST, LAMBDA y COORD): preparación cerrada en alcance por
Codex (2026-11-16). Son 3 tareas: ELAST con 6 fronteras y 70 nodos;
LAMBDA con 2 conjuntos × con/sin = 4 filas y 9 estados nacionales por
conjunto; COORD con 12 claves, 12 techos y 192 comparaciones.
- **Extracción**: `tarea_lote` y sus dos conexiones (U11), `validar_lote`
  (U12), el manifiesto, el anexo de cobertura nacional ligado a él, el
  paquete, el alcance y las tres referencias rem112 (iguales a los objetos
  del catálogo). Son 19 piezas, con 0 rutas personales. Núcleo paper2b de
  la instalación 37/37 igual al candidato; las 192 filas padre de COORD,
  autenticadas en las referencias de FAM01.
- **Conectada** la ruta de `tarea_lote`: sus funciones de cálculo desde los
  bytes exactos, `validar_lote` con la selección de unidad declarada (sin
  selección da el mismo veredicto que el original) y la comparación exacta
  COMPARACION-FAM04-v1.
- **Probado con cálculo**: tres pilotos, la frontera ELAST G|df (25 filas,
  0,8 s), el conjunto LAMBDA PER-E1.macro (con y sin, 9 estados; 1,4 s) y
  la clave COORD 19dabac4b3fe72f8 (1 techo y 16 comparaciones; 5,2 s).
  - Validados, y aceptados con líneas idénticas a la referencia.
  - 0 lecturas fuera del paquete.
- **Controles**: 29/29 sin cálculo científico, con traslado a otra carpeta;
  regresión de FAM01/FAM02/FAM03 conforme.

Pendiente: la ejecución completa del lote (Paso 3) y el aislamiento
(2.4.2). No cubre FAM05 ni FAM07. Detalle en `RESULTADO_FAM04.md`.

FAM05 (lote 2: ELAST y LAMBDA con el núcleo C0): preparación cerrada en
alcance por Codex (2026-11-16). Las tareas internas se
llaman L1-ELAST y L1-LAMBDA aunque son del lote 2.
- **Unidades**:
  - F05-ELAST-C0: 393 mallas nuevas (4.125 nodos), que cubren 527
    fronteras; con 39 equivalencias ya aceptadas, 566 fronteras cubiertas.
  - F05-ELAST-HIST: 6 mallas con 70 filas aceptadas del lote 1, que se
    reutilizan sin recalcular y reciben la topología del núcleo; 70 filas
    de procedencia. En total, 399 mallas, 4.195 filas y 572 fronteras.
  - F05-LAMBDA: 12 pares × con/sin = 24 filas. Estados por par: 9
    (CMP-E1), 1 (COL-E2-2023) o 32 candidatos estrictos (PER-E0E3); 488
    llamadas a bridge.
- **Extracción**: `tarea_lote` y sus dos conexiones (U14), `validar_lote`
  (U15), manifiesto, anexo 5bea5153… ligado al manifiesto y al alcance,
  paquete rem119,
  alcance, fuente del suplemento y referencias rem120 (iguales a los objetos
  del catálogo). Del núcleo C0 se copia `src/paper2b` y se declara el
  inventario de sus 121 archivos (identidad d0bf5cd6… recalculada). Son 54
  piezas, con 0 rutas personales. El núcleo de FAM04 no se usa: difiere en
  `model.py`.
- **Conectada** la ruta de producción de `tarea_lote` desde sus bytes
  exactos, con el cierre del suplemento. `validar_lote` se conecta con la
  selección; sin selección da el mismo veredicto que el original. La
  comparación es exacta (COMPARACION-FAM05-v1), con el vínculo de la
  procedencia comprobado aparte.
- **Probado con cálculo**: la malla ELAST 2D FRN:0163dbf3… (25 filas), el
  par CMP-E1.macro|COL (9 estados) y el par estricto PER-E0E3.macro|PER (32
  candidatos), de 0,2 a 1,0 s cada uno. Además, la unidad SUPLEMENTO (70
  filas reutilizadas, sin recalcular sus valores).
  - Validados, y aceptados con líneas idénticas a la referencia.
  - 0 lecturas fuera del paquete.
- **Controles**: 23/23 sin cálculo científico, con el diferencial del
  validador y el traslado a otra carpeta; regresión de FAM01–FAM04
  conforme.

Pendiente: la ejecución completa del lote (Paso 3) y el aislamiento
(2.4.2). No cubre COORD del lote 2 (FAM07) ni E4 (FAM06). Detalle en
`RESULTADO_FAM05.md`.

FAM06 (E4: mallas G/N del lote 2 y su conciliación): preparación cerrada
en alcance por Codex (2026-11-16).
- **Unidades**:
  - F06-MALLAS (RN): 383 mallas nuevas con 4.115 nodos (172 d, 101 f y
    110 df; 273 de una dimensión y 110 de dos), cada una con un solo diseño
    y contraparte de una malla de origen del lote 2.
  - F06-CONCILIACION (RD): 391 pares G/N (383 contrapartes y 8 existentes)
    con 4.155 puntos; d 178, f 103 y df 110. Son 17 pares y 36 puntos con
    topología distinta (resultados legítimos) y un universo padre de 572
    fronteras, sin padres nuevos.
- **Extracción**: manifiesto y anexo E4, alcance, productor de la
  conciliación (`conciliacion_e4_rem121.py`) y referencias rem121 de E4 y
  de la conciliación (iguales a los objetos del catálogo). Son 9 piezas,
  más 8 reutilizadas de FAM05 (código U17/U18, manifiesto del lote 2 y su
  producto L1-ELAST aceptado) y el mismo núcleo C0; 0 rutas personales.
- **Conectada** la ruta de FAM05 con el manifiesto E4 (MANIFIESTO-E4-v1) y
  `validar_lote` con la selección. El conciliador se ejecuta desde sus bytes
  con 8 sustituciones declaradas (CONCILIADOR-v1). Las comparaciones son
  exactas (COMPARACION-FAM06-MALLAS-v1 y COMPARACION-FAM06-CONCILIACION-v1),
  con el vínculo de cada lado comprobado contra sus propios bytes.
- **Probado con cálculo**: la primera malla d (5 filas), f (5) y df (25) del
  manifiesto, de 0,8 a 1,0 s cada una.
  - Validadas, y aceptadas con líneas idénticas a la referencia.
  - 0 lecturas fuera del paquete.
- **Conciliación**: el par de cada piloto, con el lado E4 recalculado y el
  del lote 2 reutilizado, aceptado. Los 391 pares se regeneraron sobre
  entradas guardadas, idénticos byte a byte (no acredita F06-MALLAS).
- **Controles**: 26/26 sin cálculo científico, con traslado a otra carpeta;
  regresión de FAM01–FAM05 conforme.

Pendiente: las 383 mallas y su conciliación sobre salidas nuevas (Paso 3) y
el aislamiento (2.4.2). No cubre COORD del lote 2 (FAM07). Detalle en
`RESULTADO_FAM06.md`.

FAM07 (COORD del lote 2, variante B): preparación cerrada en alcance por
Codex (2026-11-16).
- **Unidades**:
  - F07-RECALCULO (RN): 6 techos certificados, partición B en
    L1-COORD-R1/R2/R3 (dos claves por tarea), y sus 30 comparaciones
    dependientes (16 + 12 + 2).
  - F07-REUTILIZADAS (VI): 20 techos reutilizados (12 rem112 y 8 rem120)
    con su garantía `convergence_estimate`, nunca promovida, y las 1.502
    comparaciones que dependen de ellos.
  - F07-PREVIAS-192 (VI): 192 comparaciones previas del lote 1, disjuntas
    de las 1.532 (1.724 celdas). COL-2024p queda fuera, pendiente y no NA.
- **Extracción**: los cinco guiones COORD (copias exactas), manifiesto B,
  anexo, índice del paquete, alcance, fuentes rem120 y referencias rem124
  (iguales a los objetos del catálogo). Son 32 piezas, más 34 reutilizadas
  (FAM05, FAM04 y 30 filas padre de FAM01) y el mismo núcleo C0; 0 rutas
  personales.
- **Conectada** la ruta de producción de `tarea_lote` COORD con
  `conexion_coord_cert` y el ModeloTeorico certificado, `validar_coord_rec`
  y el ensamblador, con siete adaptaciones declaradas (sin puerta de
  producción: PUERTA-v1). La comparación es exacta (COMPARACION-FAM07-v1) y
  comprueba la huella derivada contra los bytes de la referencia.
- **Probado con cálculo**: la tarea L1-COORD-R1 completa (dos techos y 16
  comparaciones), 774,5 s bajo el supervisor.
  - Validada, y aceptada: comparaciones idénticas byte a byte; techos
    iguales salvo `segundos` y el vínculo de alcance.
  - 0 lecturas fuera del paquete y ninguna referencia.
- **Sin cálculo**: reutilizados y previas verificados; ensamblado de 1.532
  regenerado sobre entradas guardadas, idéntico byte a byte (no acredita
  F07-RECALCULO); ensamblado mixto aceptado (no acredita R2/R3).
- **Controles**: 29/29 sin cálculo científico, con traslado a otra carpeta;
  regresión de FAM01–FAM06 conforme.

Pendiente: R2, R3 y el ensamblado sobre tres salidas nuevas (Paso 3) y el
aislamiento (2.4.2). No cubre ENF (FAM08). Detalle en `RESULTADO_FAM07.md`.

FAM08 (ENF: contraste eta_f/2 frente al padre): preparación revisada y cerrada
en alcance por Codex (2026-11-17; véase RESULTADO_FAM08.md).
- **Unidades**:
  - F08-MALLAS (RN): 29 mallas (26 ENF y 3 padres a evaluar con C0), 365
    filas de puntos; 23 mallas padre reutilizadas, no recalculadas. Una
    malla no acredita un supremo.
  - F08-PARES (RD): 26 pares, 330 puntos, 12 controles d con igualdad y 1
    diferencia de topología (PAR-ENF:d59edf8a9d1461d1).
  - F08-TECHOS (RN): seis tareas ABL-ENF-T1…T6 (26 techos) y el caso no
    alcanzado d59edf8a9d1461d1: T1 incompleta, sin argmax; 17 techos
    recuperados y certificado del supremo lateral no alcanzado.
  - F08-INTEGRAL (RD): 26 claves (17 + 8 + 1) y 1.724 celdas (PER 960, COL
    574, MEX 190), 144 de la clave resuelta; G negativo 870 en ambos lados,
    sin cambios de signo. COL-2024p queda fuera, pendiente y no NA.
- **Extracción**: once guiones ENF (copias exactas), manifiestos, anexos,
  índices, certificado y censo, salidas aceptadas rem127/rem128 guardadas
  como entradas y referencias rem127/rem128/rem131. Son 75 piezas (cinco
  proyecciones saneadas con correspondencia comprobada), más 12
  reutilizadas y el mismo núcleo C0; 0 rutas personales.
- **Conectados** el cálculo de mallas (ruta del lote 2) y de techos
  (`tarea_lote` de lote_enf con `conexion_coord_cert`), las validaciones, la
  recuperación de T1 con el certificador aceptado, la conciliación de pares
  y la integración por la ruta única, con adaptaciones declaradas (sin
  puerta de producción: PUERTA-v1). La comparación es exacta
  (COMPARACION-FAM08-v1) y recomprueba las huellas derivadas.
- **Probado con cálculo**: la primera malla ENF de d, f y df (5 + 5 + 25
  filas) y la tarea ABL-ENF-T2 completa (dos techos y 7 comparaciones,
  2.347,8 s con la máquina cargada; referencia 746,7 s).
  - Validados y aceptados: líneas de mallas y comparaciones idénticas;
    techos iguales salvo `segundos` y el vínculo de alcance.
  - Ninguna lectura fuera del paquete, de salidas guardadas ni de
    referencias.
- **Sin cálculo**: certificado reemitido sobre la T1 guardada con el
  contenido del aceptado; pares, recuperación e integración regenerados
  sobre entradas guardadas, idénticos byte a byte; conexión mixta (mallas
  piloto y T2 nuevas) aceptada. No acreditan las tareas no calculadas.
- **Controles**: 35/35 sin cálculo científico, con traslado a otra carpeta
  y la ruta de una T1 nueva; regresión de FAM01–FAM07 conforme.

Pendiente: T1, T3–T6, las otras 26 mallas y la integración sobre salidas
nuevas (Paso 3) y el aislamiento (2.4.2). Detalle en `RESULTADO_FAM08.md`.

FAM11 (COV y B1/B2) tiene la preparación revisada y cerrada en su alcance.
El dictamen consta en RESULTADO_FAM11.md.
- **Unidades**:
  - F11-COV26 (RN): seis tareas ABL-COV-T1…T6 (26 techos: T1 18, T2–T4 2,
    T5 y T6 1), ensamblado de 1.724 celdas y conciliación de 1.728
    afirmaciones: 1.693 `inconclusa_preservada`, 28
    `no_decidida_por_testigos`, 3 `parcial_no_robusta_factible` y 4
    `parcial_no_robusta_infactible`. La aceptación es en la escala
    normalizada; 8 techos tienen error_R > 1e-7. Un cambio de signo
    certificado no es un cambio de categoría.
  - F11-B1 (RN): una solicitud `c2_normalizado`. U_C2 es el extremo
    superior certificado del encierro (redondeo hacia afuera), no un
    máximo; B1 solo produce candidatos.
  - F11-B2 (RN): cota inferior global L_K1 de K1…K6 con la forma acoplada,
    q exacto y s_Pi. Contextos: 4.608 / 2.304 / 1.920; 480 puentes y 60
    Q. Los grupos se solapan y COL-2024p pertenece al soporte E2. Regla
    exacta G_hi = U_C2 − L_K1 ≤ −1/100, con el borde incluido; las
    categorías padre se conservan aparte de la conclusión transformada.
- **Extracción**: cinco guiones COV y ocho piezas B1/B2, índices,
  manifiestos, alcance, cobertura, censo, ENF por afirmación, conciliación
  aceptada y fuentes de B2, las seis tareas rem151 guardadas como entradas y
  las referencias rem151/rem166/rem169/rem170. Son 84 piezas (16
  proyecciones saneadas con correspondencia comprobada), más 10
  reutilizadas y el mismo núcleo C0; 0 rutas personales.
- **Conectados** el cálculo COV (`tarea_lote` con `conexion_coord_cert`),
  B1 y B2 en procesos propios, las validaciones, el ensamblado y la
  conciliación, con adaptaciones declaradas (sin puerta de producción:
  PUERTA-v1). B2 consume el B1 nuevo validado (ENLACE-B1-v1), nunca el
  histórico. La comparación es exacta (COMPARACION-FAM11-v1), recomprueba
  las huellas derivadas e incluye la resolución de las doce.
- **Probado con cálculo**: la tarea ABL-COV-T1 completa (18 techos y 1.438
  comparaciones, 141,7 s; referencia 70,09 s), B1 (U_C2 =
  0x1.628ed46d42e18p-3) y B2 sobre ese B1 (los seis L_K1 y G_hi exactos
  iguales a rem170; las doce `robust_infeasible`).
  - Validados y aceptados: comparaciones de T1 idénticas byte a byte;
    techos iguales salvo `segundos` y el vínculo de alcance.
  - Ninguna lectura fuera del paquete, de salidas guardadas ni de
    referencias.
- **Sin cálculo**: ensamblado y conciliación regenerados sobre las seis
  guardadas, idénticos byte a byte; conexión mixta (T1 nueva, T2–T6
  guardadas) aceptada. No acreditan T2–T6.
- **Controles**: 40/40, con traslado a otra carpeta, borde −1/100 con datos
  inertes y B2 con un B1 distinto o no validado; regresión de FAM01–FAM08
  conforme.

Pendiente: T2–T6 y el ensamblado y la conciliación sobre salidas nuevas
(Paso 3) y el aislamiento (2.4.2). No cubre los 16 casos mexicanos, la
causalidad, el orden de canales ni la integración en la síntesis (FAM10).
Detalle en `RESULTADO_FAM11.md`.

FAM09 (T8, 13.656 filas) tiene la preparación revisada y cerrada en alcance por Codex.
- **Unidades**:
  - F09-HIST (VI): 9.434 filas preservadas del anexo rem108 (insumo con
    integridad comprobada; las 14 corridas históricas no se recalculan).
  - F09-LAMBDA (RD, rem138): 2.111 filas λ (2.042 outside_support, 69
    computed); 11.545 definitivas y 2.111 de captura pendientes.
  - F09-CAPTURA (RD, rem140): 2.071 resueltas (928 computed, 1.143
    outside_support) y 40 pendientes, con la procedencia de cada una.
  - F09-TESTIGO (RN, rem141–rem144): cálculo del techo alto e8b1f7fd…
    (EQ-TECHO-T8-1), validación U36 y, aparte, emisión de 35 filas por
    cobertura exacta; 5 quedan pendientes.
  - F09-C5B (RD, rem145/rem147): las 5 restantes por
    `Fraction(v) > U_global_hi + banda` (la igualdad no excluye), con el
    certificado reutilizado.
- **Extracción**: 274 piezas (12 proyecciones saneadas con su original) en
  `nucleo_s6/t8`, más el finalizador, `model.py` y el D7 de FAM01/FAM02;
  12 actos de autoridad solo por huella; 0 rutas personales.
- **Conectados**: seis etapas encadenadas por salidas nuevas con su registro
  de validación aceptado; el verificador histórico de cada etapa; la U36
  (`validar_testigo.py`) ejecutada sin cambios sobre el piloto nuevo; la
  comparación exacta con campos locales y de vínculo nombrados.
- **Probado con cálculo**: el techo alto, una vez, bajo el supervisor
  (600 s; 1,0 s). Sus 15 campos científicos son iguales a rem141
  (C2 = 0.7651580128158672, tau_d = tau_f = 0,6). Las mismas 35 cubiertas
  y las mismas 5 pendientes.
- **Regenerado**: λ y captura idénticas byte a byte a rem138/rem140. Vista
  final 3cf3d99d…: 13.656 filas, 0 pendientes, partición 9.434 + 2.111 +
  2.071 + 35 + 5, 5.580 banderas y 4.549 estados outside_support. Frente a
  rem147, 13.616 líneas idénticas y 40 que difieren solo en 20 campos de
  vínculo.
- **Controles**: 25/25 (fila cambiada u omitida con el total conservado,
  testigo ajeno o sin validar, borde C5B, traslado y dependencias);
  regresión de FAM01–FAM08 y FAM11 conforme.

Pendiente: la ejecución general (Paso 3) y el aislamiento (2.4.2). La U36
valida la garantía (encierro), no la identidad bit a bit; esta la da la
comparación con rem141. Detalle en `RESULTADO_FAM09.md`.

FAM10 (Exp8, 1.728 afirmaciones) tiene la preparación hecha (2026-11-18).
Codex cerró la preparación documental y aritmética en su alcance el 18 de noviembre de 2026.
- **Unidades**:
  - F10-ENF-AFIRMACION (RD, rem147/rem148): U41 sobre el integral ENF de
    FAM08, con T7 y EXP8_TABLA de rem108 y las 16 filas padre. Recuentos
    1.705 / 4 / 3 / 16, 3.449 posiciones y 1.724 celdas. U42
    (validador) no está localizado. Límite adoptado por el autor el
    2026-11-18: L-ENF-AFIRMACION-AUDITORIA-REM148. El bloque científico de la
    auditoría rem148 es la validación del ENF regenerado, y la fila sigue RD.
  - F10-SINTESIS (RD, rem160/rem161): U44 aplica P7 una vez (7
    afirmaciones, 4 unidades). Da ENF 1.712/16, COV 1.700/28 (12 COL + 16
    MEX, con la regla ±ε) y Q 1.712/16 por versión. La sensibilidad
    m = 1/2 va separada del diagnóstico 0 < m ≤ 1.
  - F10-INTEGRACION (RD, rem170/rem171): U47 aplica G_hi = U_C2 − L_K1 ≤
    −1/100 a las doce COL y deja la vista final COV en 1.700 / 12 / 16.
- **Extracción**: 42 archivos y 3 piezas reutilizadas de FAM11, con 7
  proyecciones saneadas ligadas a su original. Hay 7 resúmenes de libros
  que lee el código, 24 actos autenticados solo por huella y 0 rutas
  personales.
- **Conectados**: la orden única `fam10-tabla` encadena las tres etapas
  sobre salidas nuevas o validadas de FAM08, FAM11 y FAM12, cada una con
  su registro aceptado. Cada etapa se valida sin referencias y después se
  compara exactamente por clave y escenario. ENF se valida con la parte
  científica de la auditoría rem148.
- **Regenerado**:
  - ENF ed2e098b…, sin diferencias científicas frente a e0670acc…: 8 líneas
    difieren solo en la duración de la T2 nueva;
  - síntesis con 0 diferencias científicas frente a rem160;
  - integración con 0 diferencias científicas frente a rem171. Cambian
    exactamente las doce y las otras 1.716 líneas quedan idénticas byte a
    byte.
- **Controles**: 28/28 (cruce de clave y de escenario, P7 aplicado dos
  veces, B2 con la cota alterada o sin validar, traslado y dependencias).
  La regresión de FAM01–FAM09 y FAM11 es conforme.

Pendiente:
- las entradas totalmente nuevas (Paso 3); hoy la procedencia es mixta;
- el aislamiento (2.4.2).

Detalle en `RESULTADO_FAM10.md`.

FAM13 (tablas y validaciones históricas; integridad S1) tiene la preparación
revisada y cerrada en su alcance documental por Codex el 18 de noviembre de 2026.
- **Unidades**:
  - F13-HISTORICAS (VI desde el 2026-11-18 por L-F13-VALIDADOR-REM191,
    adoptada por el autor; antes RD): U59 de rem107 (T1, T2) y de rem108 (T7.csv,
    T7_anexo.json) y la A2 de rem134 (MATRIZ_REVISADA_v4). Las dos
    validaciones (E1235 i1 y E1 i2) evalúan el modelo y no se regeneran.
    U60 (validador) no está localizado: 23 candidatos examinados, ninguno
    cita las huellas aceptadas. La regeneración de los cinco productos
    documentales y la comprobación de los dos del modelo sobre valores
    guardados se conservan como evidencia; la acreditación formal de la
    fila es la integridad.
  - F13-S1 (VI): los 40 públicos, el mapa rem187 y la fe de erratas rem188,
    contra las huellas de la aceptación S1. Los 19 internos quedan fuera.
- **Extracción**: 141 archivos y 73 piezas reutilizadas, con 2 proyecciones
  saneadas ligadas a su original (`vectores.json` de D2 y la fe de erratas)
  y 0 rutas personales.
- **Conectados**: la orden única `fam13-reproducir`, sin entradas externas,
  encadena T1T2, T7, VALIDACIONES, MATRIZ_V4 y S1. Cada etapa se valida sin
  referencias y después se compara exactamente por clave. T7 se valida con
  el bloque T7 de `prueba_ensamblajes.py` de rem108.
- **Regenerado**:
  - T1 (9/9), T2 (8/8), T7.csv (224/224), T7_anexo.json (1.728/1.728) y la
    matriz v4 (42/42), con los bytes aceptados y 0 diferencias científicas;
  - la matriz conserva las 39 filas de A3 y pasa H4, H30 y R1 de pendiente
    técnica a retrospectiva con hallazgo, contemporánea y retrospectiva;
  - las validaciones quedan autenticadas por huella y prerregistro, con
    85/85 y 21/21 campos recalculados iguales. Se conservan E1 i1 no
    conforme y E1 i2 conforme.
- **S1**: 40/40, mapa 062f8d9b… y fe de erratas (proyección 32892f0a…,
  original 283fffd5…) conformes.
- **Controles**: 20/20 (clave, valor, clasificación y estado cambiados;
  público S1 ausente, alterado o ajeno; traslado y dependencias). La
  regresión de FAM01–FAM11 es conforme.

Pendiente:
- la regeneración de los valores del modelo de las validaciones, fuera de
  este alcance;
- el Paso 3 y el aislamiento (2.4.2).

Detalle en `RESULTADO_FAM13.md`.

FAM14 (conciliaciones G/N rem174, localización §18.7 y adopción rem176)
tiene la preparación documental revisada y cerrada el 18 de noviembre de 2026.
- **Unidades**:
  - F14-GN-REGEN (RD): U62 `pares_gn_rem174.py`, con la ligadura G/N de
    U63 `verificar_relaciones_rem175.py` (validador vigente, líneas 549–846)
    como comprobación independiente.
  - F14-GN, F14-187 y F14-176 (VI): la cobertura aceptada, el registro
    §18.7 y la referencia de adopción rem176.
- **Extracción**: 417 archivos y 3 piezas reutilizadas (la conciliación E4 de
  FAM06 y los manifiestos de FAM05/FAM06), con 4 proyecciones ligadas a su
  original: U62, U63, el mapa rem117 y §18.7. A eso se suma un derivado
  público nuevo de la adopción rem176. 0 rutas personales.
- **Conectados**: la orden única `fam14-reproducir`, sin entradas externas,
  encadena GN_REGEN → GN → LOC_187 → ADOPCION_176. GN_REGEN se valida sin
  referencias y después se compara por par y lado.
- **Regenerado**: los 391 pares desde las entradas del paquete.
  - COBERTURA_GN_REM174.json (3ef08df8…) y PARES_GN_REM174.json
    (c6a3ee7a…) son idénticos byte a byte a los aceptados: 391/391 filas,
    con ambos lados iguales.
  - U63 no da hallazgos.
  - Recuentos desde las filas:
    - 8/383/0, con d=6, f=2 y d=172, f=101, df=110;
    - seis pares d disjuntos con G > N;
    - dos pares f con el mismo C2 y orden indeterminado;
    - 383 lados de malla etiquetados y sin registro.
- **Integridad**:
  - F14-GN: cobertura 3ef08df8… conforme.
  - F14-187: proyección pública 98bffc5d… conforme. La identidad histórica
    429dd087… solo se cotejó en el origen. Las 14 corridas, sin
    localización. Queda abierto si el auditor se ejecutó.
  - F14-176: derivado db0e96e1… conforme, con las cinco transiciones. La
    proyección rem197 63039f37… conserva identificadores de la conversación
    y no se distribuye. El original a975e3f9… solo se cotejó en el origen.
- **Controles**: 22/22.
  - Asignación G/N equivocada con los totales intactos.
  - Malla presentada como techo o sin su etiqueta.
  - Archivo de integridad ausente o alterado.
  - Traslado a otra carpeta y dependencias retiradas.

  La regresión de FAM01–FAM11 y FAM13 es conforme.

Pendiente:
- la integración general (2.2.3), el aislamiento (2.4.2) y el Paso 3.

Detalle en `RESULTADO_FAM14.md`.

Balance: FAM12 comprobada en alcance; FAM01 con preparación cerrada y F2
adoptada; FAM02 con preparación cerrada en alcance, las 18 tareas conectadas
y dos pilotos calculados y aceptados (R1-F tras revalidarla; sin reproducción
completa); FAM03 con preparación cerrada en alcance y tres pilotos
calculados y aceptados (sin reproducción completa); FAM04 con preparación
cerrada en alcance y tres pilotos calculados y aceptados (sin reproducción
completa); FAM05 con preparación cerrada en alcance, tres pilotos
calculados y aceptados y el suplemento verificado (sin reproducción
completa); FAM06 con preparación cerrada en alcance, tres pilotos
calculados y aceptados y la conciliación regenerada sobre entradas guardadas
(sin reproducción completa); FAM07 con preparación cerrada en alcance,
un piloto calculado y aceptado y el ensamblado regenerado sobre entradas
guardadas (sin reproducción completa); FAM08 con preparación revisada y
cerrada en alcance por Codex, cuatro pilotos calculados y
aceptados y pares e integración regenerados sobre entradas guardadas (sin
reproducción completa); FAM11 con preparación revisada en alcance,
tres pilotos calculados y aceptados y el
ensamblado y la conciliación regenerados sobre entradas guardadas (sin
reproducción completa); FAM09 con preparación revisada y cerrada en alcance, el techo
alto calculado y aceptado, y λ, captura, emisión y C5B regenerados en cadena
(sin reproducción completa). Las 14 familias tienen la preparación revisada en su alcance.
En FAM10 las tres operaciones se regeneraron en una orden única sobre
salidas de FAM08, FAM11 y FAM12, sin reproducción completa, y U42 no está
localizado (límite L-ENF-AFIRMACION-AUDITORIA-REM148 adoptado por el autor el
2026-11-18).
La revisión de FAM13 confirmó cinco productos
regenerados con los bytes aceptados, dos validaciones autenticadas con su
aritmética recalculada e integridad S1 conforme; U60 no está localizado y,
por L-F13-VALIDADOR-REM191 (adoptada el 2026-11-18), F13-HISTORICAS es VI.
En FAM14 se regeneraron los 391 pares G/N con los bytes aceptados y se validaron con el bloque G/N de U63. Las tres comprobaciones de integridad pública son conformes.
RN: cálculo numérico; RD: regeneración documental o aritmética; VI: integridad.
Las referencias del catálogo son relativas al paquete fuente rem197.

| Familia | Contenido | Operaciones | Preparación |
|---|---|---| --- |
| FAM01 | 2.276 unidades detalladas de 3.7 (S1-d/f/df, S2, S3, C2): R2 1.740 testigos + marco R3 536 | F01-R2, F01-R3, F01-R3-MARCO | Cerrada en alcance |
| FAM02 | R1 salidas globales (afirmaciones/extremos) | F02-R1 | Cerrada en alcance |
| FAM03 | Quiebres (120) y Q (32) | F03-QUIEBRES, F03-Q | Cerrada en alcance |
| FAM04 | Lote 1 (ELAST 70, LAMBDA, COORD 12 + 192 comparaciones) | F04-LOTE1 | Cerrada en alcance |
| FAM05 | Lote 2 ELAST (4.195) y LAMBDA (24) | F05-ELAST-C0, F05-ELAST-HIST, F05-LAMBDA | Cerrada en alcance |
| FAM06 | E4 (4.115 filas, 391 pares) | F06-MALLAS, F06-CONCILIACION | Cerrada en alcance |
| FAM07 | COORD (1.532 + 192) | F07-RECALCULO, F07-REUTILIZADAS, F07-PREVIAS-192 | Cerrada en alcance |
| FAM08 | ENF (mallas, pares, techos, integral 1.724) | F08-MALLAS, F08-PARES, F08-TECHOS, F08-INTEGRAL | Cerrada en alcance |
| FAM09 | T8 (lambda, captura, testigo alto, C5B) | F09-HIST, F09-LAMBDA, F09-CAPTURA, F09-TESTIGO, F09-C5B | Cerrada en alcance |
| FAM10 | Exp8 ENF por afirmación, síntesis e integración | F10-ENF-AFIRMACION, F10-SINTESIS, F10-INTEGRACION | Cerrada en alcance. U42 sigue sin localizarse; límite L-ENF-AFIRMACION-AUDITORIA-REM148 adoptado (2026-11-18). |
| FAM11 | COV (26 techos bajo φ/2) y COV12 (B1/B2) | F11-COV26, F11-B1, F11-B2 | Cerrada en alcance |
| FAM12 | P7 (siete casos) y Q local | F12-P7-K1, F12-P7-G, F12-QLOCAL | Comprobada en su alcance |
| FAM13 | Tablas y validaciones históricas (T1/T2/T7, E1235, E1I2, matriz v4 Exp0) | F13-HISTORICAS, F13-S1 | Cerrada en alcance documental. U60 sigue sin localizarse; L-F13-VALIDADOR-REM191 adoptada (2026-11-18): F13-HISTORICAS es VI. |
| FAM14 | Conciliaciones G/N, §18.7 y adopción rem176 | F14-GN, F14-GN-REGEN, F14-187, F14-176 | Preparación documental revisada y cerrada en alcance |
