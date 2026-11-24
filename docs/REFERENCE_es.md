# Technical reference (in Spanish)

This is the detailed technical reference of the package, in Spanish, as it was written while the package was prepared:
the organization of the folders, the environment, and every command of `reproducir.py` with its options and outputs.
To run the package, start with [README.md](../README.md); `run.ps1` wraps the commands described here.

Notes for reading it:

- It reproduces the sections «Organización», «Entorno» and «Comandos» of the earlier Spanish README, with the changes
  listed at the end of these notes. The other sections of that README (quick start, inputs, sources, status by family
  and work plan) are replaced by [README.md](../README.md), [DATA_SOURCES.md](DATA_SOURCES.md) and
  [FULL_RUN_HISTORY.md](FULL_RUN_HISTORY.md).
- Paths `salidas/...` name development outputs kept in the author's working copy (plans, pilots, tests and the
  outputs of the full run). They are not part of the public archive, which has no `salidas/` folder; every command
  writes its own new `salidas/...` folder when it runs.
- Section names cited in the text («Inicio rápido», «Qué se descarga y qué viene incluido», «Fuentes, cita y
  condiciones de distribución») are those of the earlier README; their content is now in README.md (Installation,
  Inputs) and DATA_SOURCES.md.
- The files `RESULTADO_*.md` and `familias.md` cited here and in the code are in [notes_es/](notes_es/). They are the
  development notes of each family, with the status at their dates; the current status is in
  [FULL_RUN_HISTORY.md](FULL_RUN_HISTORY.md). The internal work plan of the preparation (`PLAN_TRABAJO.txt`) is not
  part of the public package.
- Changes to the text of the earlier README: (1) `familias.md` points to `docs/notes_es/`; (2) `fam01-receta` no longer
  says that the full route is not authorized; (3) the full run uses the interpreter of the installation in README.md;
  (4) the paragraph on the order prepared for the full run of Paso 3 points to `run.ps1` and FULL_RUN_HISTORY.md;
  (5) the duration states the measured one; (6) the FAM01 groups are 23 keys, 290 units and 29 processes with
  TECHO-FRIO-MEDIDO-F01R2-v1, and every process asks for high priority (PRIORIDAD-ALTA-v1), as in version 1.0.0.
- The notes in `notes_es/` are copied unchanged.

---

## Organización

- `catalogo.json`: mapa de operaciones, fuentes y límites heredados.
- `docs/notes_es/familias.md`: resumen de las familias que se incorporaron, con el estado de
  su fecha.
- `src/`: código científico. `external.py`, `macro.py` y `conciliar_cov.py` son
  copias exactas; `p7_calculo.py`, `p7_suplemento.py` y `q_local.py` contienen
  funciones extraídas sin cambio de fórmula. Cada archivo dice qué es copia y
  qué es adaptación de interfaz.
- `datos/`: entradas, separadas de los resultados.
  - `p7.json`, `p7_k1_reutilizados.json`: entradas ligadas de los cuatro K1.
  - `p7_suplemento.json`: afirmaciones, lado presente y techos COV/ENF/padre
    aceptados de las cuatro celdas.
  - `q_local.jsonl`: las 3.456 posiciones guardadas de Q local.
- `referencias/`: valores aceptados con los que comparar. Solo se leen después
  del cálculo y nunca sustituyen una salida.
- `src/fam01.py`: adaptador de interfaz de FAM01.
  - Construye el contexto S6 con los valores fijos de
    `datos/fam01/contexto_s6.json`, sin la capa de autorización.
  - Llama al productor, a los validadores productivos y al comparador
    originales. Las adaptaciones de interfaz están declaradas en el archivo.
  - Contiene el formato comparable R2 (FMT-R2-v1), la comparación limpia
    (E2/E3 con el nivel real, historial operativo y correspondencia del
    saneamiento) y la comprobación F2 con el registro de su adopción.
- `src/fam02.py`: adaptador de interfaz de FAM02 (R1). Contiene:
  - el plan de las 18 tareas y la selección del piloto;
  - el contexto S6 de FAM01 y la pila R1 instalada;
  - la comprobación sin cálculo;
  - las tareas C y D (orquestador), las rutas por comando y la validación
    global V;
  - el enlace local de aceptación y la prueba de conexión con salidas
    guardadas;
  - la revalidación, la comparación y la receta;
  - la lectura SAN-RUTAS-v1 de los registros públicos.

  Llama a `tarea_r1`, `r1_s6`, `r1_rutas`, `opciones_p1`,
  `registro_productivo` y a la pila histórica de lima1351 sin editarlos.
- `src/fam03.py`: adaptador de interfaz de FAM03. Contiene:
  - los datos sin cálculo y el plan limpio, con su verificación y la
    comparación con el plan histórico;
  - la comprobación y la cobertura de unidades, tareas y árboles;
  - el cálculo de una tarea con los pasos de `tarea_prod.main`;
  - la revalidación, la comparación (COMPARACION-FAM03-v1) y la receta.

  Llama a `tarea_prod`, `evaluadores_ra`, `validador_prod`,
  `registro_productivo` y a los módulos R-A sin editarlos. Sus adaptaciones
  están declaradas en el archivo.
- `src/fam04.py`: adaptador de interfaz de FAM04. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, núcleo, cobertura,
    filas padre y referencias;
  - las unidades del lote y la regla de los pilotos;
  - el cálculo de una tarea o de una unidad con las funciones de
    `tarea_lote`;
  - la validación con `validar_lote`, la comparación (COMPARACION-FAM04-v1)
    y la receta.

  No edita `tarea_lote` ni `validar_lote`. Sus adaptaciones están declaradas
  en el archivo, incluidas las 8 sustituciones de texto del validador.
- `src/fam05.py`: adaptador de interfaz de FAM05 (lote 2), con la misma
  estructura que `fam04.py`. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, núcleo C0,
    cobertura, libro rem121 y referencias;
  - las unidades (393 mallas nuevas, SUPLEMENTO y 12 pares) y la regla de
    los pilotos;
  - el cálculo con la ruta de producción de `tarea_lote` compilada desde sus
    bytes;
  - la validación con `validar_lote`, la comparación (COMPARACION-FAM05-v1)
    y la receta.

  No edita `tarea_lote` ni `validar_lote`. Sus adaptaciones están declaradas
  en el archivo, incluidas las 6 sustituciones de texto del validador.
- `src/fam06.py`: adaptador de interfaz de FAM06 (E4). Reutiliza `fam05.py`
  sin cambiarlo. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, núcleo C0,
    cobertura E4, libro rem122 y referencias;
  - las 383 mallas y la regla de los pilotos;
  - el cálculo con la ruta de FAM05 y el manifiesto E4;
  - la validación, la conciliación G/N, las dos comparaciones
    (COMPARACION-FAM06-MALLAS-v1 y COMPARACION-FAM06-CONCILIACION-v1) y la
    receta.

  No edita `tarea_lote`, `validar_lote` ni `conciliacion_e4_rem121`. Sus
  adaptaciones están declaradas en el archivo, incluidas las 8
  sustituciones de texto del conciliador.
- `src/fam07.py`: adaptador de interfaz de FAM07 (COORD del lote 2).
  Reutiliza `fam05.py` sin cambiarlo. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, motor
    certificado, cobertura, reutilizaciones, 192 previas, libro rem125 y
    referencias;
  - la regla de los pilotos y la declaración de ejecución limpia;
  - el cálculo con la ruta de producción de `tarea_lote` COORD, la
    validación, el ensamblado, la comparación (COMPARACION-FAM07-v1) y la
    receta.

  No edita los guiones COORD. Sus adaptaciones están declaradas en el
  archivo, con las sustituciones de texto de cada guion.
- `src/fam08.py`: adaptador de interfaz de FAM08 (ENF). Reutiliza
  `fam05.py` y `fam07.py` sin cambiarlos. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, núcleo C0, motor,
    cobertura, referencias, revalidación de las guardadas y libros
    rem128/rem129/rem132;
  - la regla de los pilotos y la declaración de ejecución limpia;
  - el cálculo de mallas y techos, la validación, la recuperación de T1 con
    el certificado, la conciliación de pares, la integración, la
    comparación (COMPARACION-FAM08-v1) y la receta.

  No edita los guiones ENF. Sus adaptaciones están declaradas en el
  archivo, con las sustituciones de texto de cada guion.
- `src/fam11.py`: adaptador de interfaz de FAM11 (COV/B1/B2). Reutiliza
  `fam05.py`, `fam07.py` y `fam08.py` sin cambiarlos. Contiene:
  - la comprobación sin cálculo de fuentes, procedencia, reconstrucción de
    los manifiestos B, núcleo C0, motor, cobertura, revalidación de las
    guardadas, referencias y libros rem152/rem167/rem170;
  - la regla de los pilotos y la declaración de ejecución limpia;
  - el cálculo COV, B1 y B2 (con el enlace al B1 nuevo validado), la
    validación, el ensamblado y la conciliación, la comparación
    (COMPARACION-FAM11-v1) con la resolución de las doce, y la receta.

  No edita los guiones COV ni las piezas B1/B2. Sus adaptaciones están
  declaradas en el archivo, con las sustituciones de texto de cada pieza.
- `src/fam09.py`: adaptador de interfaz de FAM09 (T8). Reutiliza
  `fam05.py` y `fam08.py` sin cambiarlos. Contiene:
  - la comprobación sin cálculo (fuentes, sustituciones, declaración,
    pilotos, referencias y libros);
  - la regla del piloto y la declaración de ejecución limpia;
  - las seis etapas (HIST, LAMBDA, CAPTURA, TESTIGO, INCORPORACION, C5B),
    la validación con el verificador histórico de cada etapa (U36 en el
    testigo), la comparación y la receta.

  No edita los guiones T8. Sus adaptaciones están declaradas en el
  archivo, con las sustituciones de texto de cada pieza.
- `src/fam10.py`: adaptador de interfaz de FAM10 (Exp8). Contiene:
  - la comprobación sin cálculo (fuentes, sustituciones, autoridad y
    referencias);
  - las tres etapas (ENF con U41, SINTESIS con U44 e INTEGRACION con U47),
    cada una con sus entradas ligadas a un registro aceptado;
  - la validación sin referencias (ENF con la parte científica de la
    auditoría rem148, porque U42 no está localizado; límite adoptado
    L-ENF-AFIRMACION-AUDITORIA-REM148);
  - la comparación COMPARACION-FAM10-v1, la orden única `fam10-tabla` y la
    receta.

  No edita U41. U44 y U47 son proyecciones saneadas; las sustituciones de
  texto de cada pieza están declaradas en el archivo.
- `src/fam13.py`: adaptador de interfaz de FAM13 (tablas y validaciones
  históricas; integridad S1). Contiene:
  - la comprobación sin cálculo (fuentes, sustituciones, código,
    referencias y S1);
  - las cinco etapas: T1T2 y T7 con U59 de rem107 y rem108, VALIDACIONES
    (autenticación y recálculo aritmético), MATRIZ_V4 con la A2 de rem134,
    y S1;
  - la validación sin referencias (en T7, el bloque T7 de
    `prueba_ensamblajes.py`, porque U60 no está localizado);
  - la comparación COMPARACION-FAM13-v1, la orden única `fam13-reproducir`
    y la receta.

  No edita U59 ni la A2. Sus sustituciones de texto y los bloques exactos
  que ejecuta están declarados en el archivo.
- `src/fam14.py`: adaptador de interfaz de FAM14 (conciliaciones G/N,
  §18.7 y adopción rem176). Contiene:
  - la comprobación sin cálculo (fuentes, sustituciones, código,
    referencias e integridades);
  - las cuatro etapas: GN_REGEN con U62, y GN, LOC_187 y ADOPCION_176 de
    integridad;
  - la validación de GN_REGEN sin referencias, con la ligadura G/N de U63
    (líneas 549–846) y recuentos propios desde las filas;
  - la comparación COMPARACION-FAM14-v1, la orden única
    `fam14-reproducir` y la receta.

  No edita U62 ni U63. Sus sustituciones de texto y el bloque que ejecuta
  de U63 están declarados en el archivo.
- `src/general.py`: el comando general (`reproducir.py general`).
  - Construye el plan desde las recetas y el catálogo.
  - Ejecuta cada llamada en su proceso, con su límite, y bloquea a los
    consumidores de salidas ausentes, alteradas o no aceptadas.
  - Escribe el balance por clave.

  No calcula nada por sí mismo: todo lo hacen las órdenes de las familias.
  Sus controles locales son `local/pruebas_general.py` (salida alterada,
  validación retirada, discrepancia, límite, entrada preexistente,
  marcadores e interfaz) y `local/lecturas_guardadas.py` (la lectura del
  balance sobre los informes guardados de todas las familias).
- `nucleo_s6/`: copia del núcleo S6.
  - `raiz/`: `src/paper2b`, datos nacionales, D7, contratos y perfil de
    entorno.
    - `raiz/tmp/<entrega>/`: las 17 entregas históricas que lee la ruta R1
      (FAM02), con su ruta relativa e inventario. Sus registros de
      lanzamiento están en copia pública SAN-RUTAS-v1.
    - Para FAM13, en `raiz/`, todo en copia exacta:
      - en `tmp/<entrega>/`: U59 de rem107 y rem108, la A2 de rem134 y
        `prueba_ensamblajes.py`; el índice y los 15 paquetes pv12; el
        inventario y la salida A3 de rem133; los 45 archivos del núcleo H4
        (una copia por archivo);
      - las piezas S5, CERT3 y D3 que lee la A2.
    - Para FAM14, en `raiz/tmp/<entrega>/`:
      - U62 y U63 como proyecciones rem197, ligadas a su original;
      - el mapa rem117 como proyección, con un marcador en
        `nucleo_corregido_src`, ligado a su original;
      - los inventarios de seis entregas y los 399 registros de techo, en
        copia exacta.
  - `instalacion/`: productor R2/R3, Verificador S6, validador R3, registro
    productivo, comparador v3-S6, regla DR-1, listas y reglas selladas.
    - Para FAM02, también la ruta R1 instalada (`tarea_r1`, `r1_s6`,
      `r1_rutas`, `opciones_p1`, `comparar_tarea`, `opciones_r1.json`) y su
      núcleo `src/paper2b`, idéntico al de `raiz/`.
    - Para FAM03:
      - la ruta PROD (`tarea_prod`, `validador_prod`, `evaluadores_ra`,
        `plan_prod`, `decision_d4`, `calendario_paso4`,
        `rebalanceo_paso4` y `datos/paso4/lista_PROD.json`);
      - el área `ra/`: `puerto_ra.py`, los módulos históricos y portados y
        `R_A_dependencias.json` en copia pública;
      - en `raiz/tmp/`, la entrega lima1958 y las entradas que leen sus
        módulos.
  - `lote1/` (FAM04): `tarea_lote.py`, `conexion_lambda.py`,
    `conexion_frontera.py` y `validar_lote.py`, copias exactas. Usan el
    núcleo `src/paper2b` de `instalacion/`.
  - `lote2/` (FAM05): las mismas cuatro piezas del lote 2 (rem119), copias
    exactas. Usan el núcleo de `c0/`.
  - `c0/src/paper2b` (FAM05): el núcleo C0 del lote 2 (identidad
    d0bf5cd6…), copia exacta. Solo difiere del de `instalacion/` en
    `model.py`. El inventario de la instalación C0 está en
    `fuentes_fam05.json`.
  - `e4/` (FAM06): `conciliacion_e4_rem121.py`, el productor de la
    conciliación G/N, copia exacta. FAM06 usa el código de `lote2/` y el
    núcleo de `c0/`.
  - `coord/` (FAM07): `tarea_lote.py`, `conexion_coord_cert.py`,
    `validar_lote.py`, `validar_coord_rec.py` y `ensamblar_coord.py` del
    paquete COORD, copias exactas. Usan el núcleo de `c0/`.
  - `enf/` (FAM08): `mallas/conciliar_mallas_enf.py`; `techos/` con
    `tarea_lote.py`, `conexion_coord_cert.py`, `validar_lote.py` y
    `validar_coord_rec.py` de lote_enf; `integracion/` con
    `ensamblar_integracion.py`, `conciliar_integracion.py`,
    `validar_integracion.py`, `recuperar_t1.py`, `certificado_salto.py` y
    `pruebas_certificado.py`. Copias exactas; usan el núcleo de `c0/` y,
    para las mallas, el código de `lote2/`.
  - `cov/`, `b1/` y `b2/` (FAM11): `tarea_lote.py`,
    `conexion_coord_cert.py`, `validar_lote.py`, `validar_coord_rec.py` y
    `ensamblar_coord.py` del paquete COV i5; y, en `b1/` y `b2/`, el
    trabajador, el validador, la puerta, `comun_b*.py` (proyección saneada)
    y el índice del paquete. Usan el núcleo de `c0/`; B1/B2 cargan su
    cierre C0 en un proceso propio.
  - `t8/` (FAM09): espejo de `tmp/<área>/<rel>` con los paquetes de
    emisión λ, captura (candidato_v3), testigo alto (testigo_alto_v3 y
    manifiesto v2), conexión del testigo y conexión C5B; el anexo T8, las
    fuentes de cada etapa, el certificado C5B, el núcleo histórico lima1855
    y los inventarios de entrega de cada área. Copias exactas salvo 12
    proyecciones saneadas. El testigo carga paper2b de lima1855; las demás
    etapas, el de `instalacion/`.
  - `exp8/` (FAM10): espejo de `tmp/<área>/<rel>` con:
    - U41 (copia exacta) y U44/U47 (proyecciones saneadas);
    - T7_anexo y EXP8_TABLA de rem108;
    - las 16 filas padre que U41 lee para las robustas;
    - el esquema declarado de rem170.

    `auditoria/` contiene las líneas 49–116 de la auditoría rem148, en
    copia exacta.
  - Es copia exacta salvo:
    - trece archivos con la procedencia saneada; nueve de ellos se leen al
      ejecutar;
    - los tres manifiestos que los listan, derivados de los históricos;
    - una línea de `nacionales.py`, que admite la huella pública del
      registro de snapshots.
- `datos/fam01/`:
  - marco R3, propuesta B y fuentes del vínculo;
  - 1.767 definiciones de unidad y contexto S6;
  - clasificación de manifiesto de las unidades R2, que alimenta el formato
    comparable;
  - proyección de referencia de F2 (adoptada para FAM01).
- `referencias/fam01/`: índice y documentos y filas originales de las 1.767
  unidades, más `ausentes.json` (vacío). `manifiestos_historicos/` guarda los
  tres manifiestos históricos con que se comprueba el saneamiento.
- `datos/fam02/piloto.json`: selección del piloto FAM02, fijada antes de
  calcular.
- `datos/fam03/`: despliegue sin rutas ni autor, contexto esperado, plan
  limpio y pilotos. Los fija `fam03-preparar`, sin cálculo.
- `referencias/fam03/`: los 136 árboles aceptados (manifiestos y miembros)
  y el plan histórico en copia pública. Solo se usan para comparar.
- `datos/fam04/`: manifiesto del lote, anexo de cobertura nacional, paquete
  y alcance (los dos últimos solo cruzan huellas) y `pilotos.json`, fijado
  antes de calcular.
- `referencias/fam04/rem112/`: la ejecución aceptada de las tres tareas
  (`resultado.json`, salida de validación y productos). Solo se usan para
  comparar.
- `datos/fam05/`: manifiesto del lote 2, anexo de cobertura nacional,
  paquete rem119, alcance y `pilotos.json`. `fuente_suplemento/` guarda las
  70 filas aceptadas del lote 1 en la ruta que declara el manifiesto. Es una
  entrada del suplemento, no una referencia.
- `referencias/fam05/rem120/`: la ejecución aceptada de L1-ELAST y L1-LAMBDA
  del lote 2. Se usan para comparar. En FAM06, el producto L1-ELAST es además
  el lado de origen guardado de la conciliación.
- `datos/fam06/`: manifiesto E4, anexo E4, alcance (solo cruza huellas) y
  `pilotos.json`, fijado antes de calcular.
- `referencias/fam06/rem121/`: la ejecución aceptada de E4 (L1-ELAST) y la
  conciliación aceptada. Se usan para comparar. El producto E4 es además una
  entrada guardada de la regeneración documental.
- `datos/fam07/`: manifiesto B, anexo, índice del paquete y alcance (los
  dos últimos solo cruzan huellas), fuentes rem120 de los 8 techos
  reutilizados, `pilotos.json` y `ejecucion_limpia.json` (declaración NO
  OFICIAL que ocupa el vínculo de alcance; no es un alcance ni una
  decisión).
- `referencias/fam07/rem124/`: la ejecución aceptada de las tres tareas y
  el ensamblado. Se usan para comparar; las tres tareas son además las
  entradas guardadas de la regeneración y del ensamblado mixto.
- `datos/fam08/`: manifiestos, anexos e índices de mallas, techos e
  integración, los alcances (solo cruzan huellas), el certificado y el
  censo (proyecciones saneadas), `pilotos.json` y `ejecucion_limpia.json`
  (declaración NO OFICIAL). `guardadas/`: las mallas y T1 rem127 y T2–T6
  rem128 aceptadas, entradas de las regeneraciones y referencia de las
  comparaciones de cálculo.
- `referencias/fam08/`: rem127, rem128 (validaciones, conciliación de mallas
  y diagnóstico del certificado) y rem131 (integración). Solo se usan para
  comparar.
- `datos/fam11/`: índice, manifiesto, cobertura, alcance, censo rem147 y ENF
  por afirmación de COV; manifiestos B1 y B2 (proyecciones saneadas);
  `fuentes/` (conciliación aceptada como entrada de B1, contexto COL por
  grupo, mapa de soporte derivado, plan mínimo, preparación B1/B2,
  `contexto_s6.py` y `preparar_manifiesto_cov.py`); `pilotos.json` y
  `ejecucion_limpia.json` (declaración NO OFICIAL). `guardadas/cov_rem151/`:
  las seis tareas rem151 aceptadas, entradas de la regeneración y
  referencia de la comparación de cálculo.
- `referencias/fam11/`: rem151 (tareas, ensamblado y conciliación), rem166
  (B1), rem169 (B2) y rem170 (resolución de las doce). Solo se usan para
  comparar.
- `datos/fam09/`: `pilotos.json` y `ejecucion_limpia.json` (declaración NO
  OFICIAL), fijados antes de calcular; `autoridad/` con el resumen sin
  rutas de la aceptación técnica C5B rem145, ligado a su original.
- `referencias/fam09/`: rem141 (RESULTADO, VALIDACION e INICIO del testigo
  alto), rem147 (vista final) y las verificaciones rem138/rem140/rem144/
  rem147 (proyecciones). Solo se usan para comparar.
- `datos/fam10/autoridad/`: resúmenes sin rutas de los siete libros que
  cargan U44 y U47 (ENF rem148, COV, P7, Q, Q_DIAG, ENF_ORIGEN y elección
  m_Q). Solo llevan los campos que lee el código y cada uno está ligado a
  la huella de su original.
- `referencias/fam10/`: contiene
  - rem147: cobertura y resumen por país;
  - rem148, rem161 y rem171: resúmenes de los libros;
  - rem160 y rem171: filas, resumen y manifiesto.

  Además usa las referencias de FAM11 e0670acc… y rem170 (COV12). Todas
  solo se usan para comparar.
- `datos/fam13/`:
  - `t1t2/`: el extracto §6.2–§6.3 del plan, ligado a la huella del plan
    completo;
  - `t7/`: los inventarios de entrega proyectados (huella del original y
    entradas consultadas) y el mapa de las filas de unidad de FAM01 que lee
    T7;
  - `v4/`: el núcleo H4 por entrega;
  - `validaciones/`: los dos resultados y los dos prerregistros, en copia
    exacta;
  - `s1/`: los 40 públicos, el mapa rem187, la fe de erratas proyectada y
    el resumen de huellas aceptadas (sin los 19 internos).
- `referencias/fam13/`: rem107 (T1 y T2), rem108 (T7 y cobertura) y rem134
  (los seis documentos de `salida_a2`). El T7_anexo de FAM10 sirve de
  referencia del anexo. Solo se usan para comparar.
- `datos/fam14/`:
  - `autoridad/`: resúmenes sin rutas de los libros rem118 (líneas 11 y
    32 del dictamen y los certificados de las unidades del mapa) y rem122,
    de las raíces de fuentes rem174/rem175 y del esquema rem175, cada uno
    con la huella de su original;
  - `187/`: la proyección pública del registro §18.7;
  - `176/`: el derivado público de la referencia de adopción rem176.
- `referencias/fam14/`: COBERTURA_GN_REM174.json, que es también el objeto
  de F14-GN, y PARES_GN_REM174.json. Solo se usan para comparar. La
  conciliación E4 de `referencias/fam06/` es entrada de FAM14.
- `fuentes_p7.json`, `fuentes_fam12.json`, `fuentes_fam01.json`,
  `fuentes_fam02.json`, `fuentes_fam03.json`, `fuentes_fam04.json`,
  `fuentes_fam05.json`, `fuentes_fam06.json`, `fuentes_fam07.json`,
  `fuentes_fam08.json`, `fuentes_fam11.json`, `fuentes_fam09.json`,
  `fuentes_fam10.json`, `fuentes_fam13.json`, `fuentes_fam14.json`: origen y huellas de cada archivo. `revisar` comprueba los dos primeros y cada
  `famXX-comprobar` el de su familia.
  - En `fuentes_fam01.json`, las 17 entradas con `sha256_origen` son
    copias públicas y no son idénticas a su fuente: 13 con la procedencia
    saneada, 3 manifiestos derivados y un lector adaptado.
  - En `fuentes_fam02.json`, las 113 entradas con `sha256_origen` son los
    registros de lanzamiento en copia pública (112 saneados; uno no tenía
    rutas). `lecturas_en_ejecucion` declara la lista de entradas en
    ejecución, salidas guardadas y referencias A3
    (`extraccion/registro/lecturas_ejecucion_fam02.json`).
- `requisitos_fam01.txt`: remite al lock completo del perfil de FAM01.
- `reproducir.py`: revisión de archivos y comandos de cálculo.
- `extraccion/`: herramientas de desarrollo que extrajeron las entradas desde
  el proyecto original. No hacen falta para ejecutar y no van al paquete público,
  salvo `registro/lecturas_ejecucion_fam02.json`, que exige `fam02-comprobar`.
- `salidas/`: resultados nuevos, excluidos de Git.

## Entorno

**Entorno público (2026-11-18).** Es el que crea el «Inicio rápido en
Windows» y sirve para las 14 familias.

- **Intérprete base.** CPython 3.12.4 de 64 bits oficial:
  `python-3.12.4-amd64.zip` de python.org.
  - Es la entrada `pythoncore-3.12-64` de `index-windows-recent.json`.
  - Huellas: zip `35b4ac3b…`, `python.exe` `fd5c46d7…` y `python312.dll`
    `21700f0b…`, las mismas que exigen la receta y el manifiesto del perfil.
  - Firma Authenticode válida de la Python Software Foundation.
- **Venv.** Se crea en `%LOCALAPPDATA%\reproduccion-paper2\venv`, fuera del
  paquete, con la receta
  `nucleo_s6/raiz/environment/sucesor_b3/crear_entorno.ps1`, el perfil
  «integracion» y su `requirements.lock` (`942a4138…`), sin cambios.
  - Su `pyvenv.cfg` apunta al intérprete descargado, no a ningún Python
    de la máquina.
  - La receta termina con `ENTORNO_OK 10 paquetes exactamente del lock`.
- **Comprobaciones con este entorno** (`salidas/entorno_publico_01`):
  - `revisar`, `fam01-listas`, los 13 `famXX-comprobar` y `p7` terminan con
    código 0 y cumplen.
  - Ninguna registra lecturas fuera del paquete y del intérprete.
  - En FAM01 el entorno cumple el perfil y F2 da `equivalente: true`. En
    FAM02, `entorno_conforme: true`.
  - El plan y el piloto del Inicio rápido son conformes desde la base
    (`salidas/inicio_20261118_181045`) y desde una copia sin `salidas/`
    (`salidas/entorno_publico_01/copia_sin_salidas`).
- **Por qué fuera del paquete.** El registro de lecturas cuenta como «del
  paquete» todo lo que hay bajo su carpeta, y solo reconoce como venv propio
  `.venv-fam01/`.
  - Con el intérprete dentro, sus `.pyc` aparecían como archivos sin
    manifiesto en FAM08 y FAM11 (`salidas/inicio_20261118_180445` y
    `_180557`, antecedentes).
  - Fuera del paquete, esas lecturas cuentan como del intérprete, igual que
    con `.venv-fam01`.
- **Equivalencia con `.venv-fam01`.** Donde este README o las recetas dicen
  `<python de .venv-fam01>`, vale el Python del entorno público: es la
  misma receta y el mismo perfil, con las mismas opciones y variables.
  `.venv-fam01` se conserva; su intérprete base está en el árbol original y
  solo sirve en esta máquina.
- **Plataforma.** El perfil está validado solo para Windows 11 build 26200.
  - En otra build de Windows, el piloto general no depende de esa
    comprobación.
  - En cambio, la F2 de FAM01 y `fam02-comprobar` informarían el entorno
    como no conforme.
  - La prueba en la VM cubre la compilación 26200.

CPython 3.12.4 de 64 bits. FAM12 usa solo la biblioteca estándar: sus comandos
se ejecutaron con `-B -I -X utf8`. Cada salida registra los módulos cargados
fuera de la biblioteca estándar y del paquete; en FAM12 la lista quedó vacía.

FAM01 necesita el entorno `.venv-fam01`, que cumple el perfil aprobado
completo. Es el perfil «integracion» del lock de origen, con los 10 paquetes
con versión y sha256 de rueda, pip 26.1.2 incluido. Se crea con la receta
del perfil copiada en el núcleo, que:
- exige un CPython 3.12.4 oficial (comprueba python.exe y python312.dll);
- instala solo con hashes;
- comprueba que el conjunto instalado es exactamente el del lock.

xlrd 2.0.2 va vendorizado dentro del núcleo.

```text
powershell -File nucleo_s6\raiz\environment\sucesor_b3\crear_entorno.ps1 -BasePython <python.exe de CPython 3.12.4> -Perfil integracion -Venv .venv-fam01
```

`fam01-comprobar` informa si el entorno cumple el perfil y si es equivalente
por F2, adoptada para FAM01. F2 solo admite otra ubicación del venv dentro
de este perfil (Windows, CPython 3.12.4 oficial). El `.venv` anterior, con solo cuatro paquetes y
pip 24.0, no cumple el perfil y se conserva como antecedente.

Los comandos de FAM01 se lanzan con el Python de `.venv-fam01`, con
`-B -P -s -X utf8`, sin `-I`. El entorno debe fijar:
- `PYTHONHASHSEED=0`;
- `TZ=UTC`;
- valor 1 en `BLIS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`,
  `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` y `VECLIB_MAXIMUM_THREADS`.

Así lo hacían los lanzadores de origen. Con `-I` Python ignoraría la semilla,
y `fam01-unidad` se niega a calcular sin ella.

FAM02 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno; solo carga numpy 2.0.2 fuera de la biblioteca estándar.
`fam02-unidad` también exige la semilla. F2 se informa en cada salida, pero
no está adoptada para FAM02 (ver `RESULTADO_FAM02.md`).

FAM03 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno; también carga solo numpy 2.0.2. `fam03-unidad` exige la semilla.
F2 se informa, pero la regla de FAM03 no la necesita.

FAM04 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno. Solo LAMBDA carga numpy 2.0.2. `fam04-unidad` exige la semilla. F2
se informa, pero no se extiende a FAM04 ni la necesita su regla.

FAM05 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno; ELAST y LAMBDA cargan numpy 2.0.2. `fam05-unidad` exige la
semilla. F2 se informa, pero no se extiende a FAM05 ni la necesita su regla.

FAM06 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno, y el núcleo C0 de FAM05. `fam06-unidad` exige la semilla. F2 se
informa, pero no se extiende a FAM06 ni la necesita su regla.

FAM07 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno, y el núcleo C0 de FAM05; solo carga numpy 2.0.2. `fam07-unidad`
exige la semilla. F2 se informa, pero no se extiende a FAM07 ni la necesita
su regla.

FAM08 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno, el núcleo C0 y el código del lote 2 de FAM05; solo carga numpy
2.0.2. `fam08-unidad` exige la semilla. F2 no se extiende a FAM08.

FAM11 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno, y el núcleo C0 de FAM05. Los procesos COV solo cargan numpy 2.0.2.
B1 y B2 corren en procesos propios, cuyo cierre C0 rechaza `paper2b`
precargado; en ellos F2 no se evalúa. `fam11-unidad` exige la semilla. F2
no se extiende a FAM11.

FAM09 usa el mismo `.venv-fam01`, con las mismas opciones y el mismo
entorno (Python 3.12.4, el mismo intérprete base que la corrida histórica
del testigo). El testigo y su validación corren en procesos propios sin
paper2b precargado y cargan el núcleo lima1855; λ, captura, emisión y C5B
cargan el paper2b de la instalación de FAM01 a través del finalizador.
`fam09-etapa` exige la semilla. F2 no se evalúa ni se extiende a FAM09.

FAM10 usa el mismo `.venv-fam01`, con las mismas opciones. U41, U44, U47 y
el bloque de la auditoría rem148 importan solo la biblioteca estándar y
corren en el mismo proceso. `fam10-etapa` y `fam10-tabla` exigen
`PYTHONHASHSEED=0`. F2 no se evalúa ni se extiende a FAM10.

FAM13 usa el mismo `.venv-fam01`, con las mismas opciones. U59 y la A2
corren en el mismo proceso. T7 carga el paper2b de la instalación de FAM01 y
la A2, el de su entrega de referencia; no se mezclan en `sys.modules`.
`fam13-reproducir` exige `PYTHONHASHSEED=0`. F2 no se evalúa ni se extiende
a FAM13.

FAM14 usa el mismo `.venv-fam01`, con las mismas opciones. U62 y el bloque
de U63 importan solo la biblioteca estándar y corren en el mismo proceso.
`fam14-reproducir` exige `PYTHONHASHSEED=0`. F2 no se evalúa ni se extiende
a FAM14.

Las demás familias pueden requerir otros núcleos y entornos; no se presupone
que estos entornos sirvan para todo el paper.

## Comandos

Todos resuelven sus recursos respecto de la carpeta de `reproducir.py`, así que
se pueden lanzar desde cualquier carpeta. `--salida` debe ser una ruta nueva:
no se sobrescribe nada. Una ruta relativa se interpreta desde la carpeta
actual. Cada comando revisa antes las huellas y devuelve un código distinto de
cero si hay discrepancias.

```text
python -B -I -X utf8 reproducir.py revisar
python -B -I -X utf8 reproducir.py p7 --salida salidas/p7_03.json
python -B -I -X utf8 reproducir.py p7-k1 --salida salidas/p7_k1_02.json
python -B -I -X utf8 reproducir.py p7-suplemento --salida salidas/p7_suplemento_02.json
python -B -I -X utf8 reproducir.py q-local --salida salidas/q_local_02
```

- `revisar`: huellas y sintaxis, sin ejecutar ningún cálculo.
- `p7`: el piloto original de dos K1 (S1-N-df, S1-G-df), sin cambios.
- `p7-k1`: los cuatro K1 con `GridCell.Q`, `macro.bridge` y `external.K1`
  (`derivar_k1`). Compara K1, Q, lambda_pi y gain_share, y además dme_gai en los
  dos casos del piloto, en representación hexadecimal exacta.
- `p7-suplemento`: recalcula los cuatro K1 y genera las siete filas con la regla
  del conciliador COV i5 (eps = 1/100, desigualdades estrictas, fracciones
  exactas). Compara campo a campo con `referencias/p7_suplemento.jsonl` y
  controla la cobertura.
- `q-local`: G(m) = C_2 − m·K1 en racionales exactos sobre las posiciones
  guardadas, versiones contrato y conservadora. Escribe en la carpeta de salida
  un `.jsonl` por versión y `resumen.json`. No carga el modelo, K1, bridge,
  `GridCell.Q` ni supremos.

Las salidas ya guardadas en esta base son `p7_01.json` y `p7_02.json`,
`p7_k1_01.json` y `_02`, `p7_suplemento_01.json` y `_02`, `q_local_01/` y
`_02/`. Cada ejemplo debe usar un nombre de salida nuevo.

FAM01 (con el Python de `.venv-fam01`, opciones y entorno como en «Entorno»):

```text
reproducir.py fam01-listas    --salida salidas/fam01/listas_02.json
reproducir.py fam01-comprobar --salida salidas/fam01/comprobar_09.json
reproducir.py fam01-unidad    --seleccion R2 --unidad <id> [--unidad <id> ...] --salida salidas/fam01/<carpeta nueva>
reproducir.py fam01-comparar  --seleccion R2 --unidad <id> --nueva salidas/fam01/<carpeta> --salida salidas/fam01/<archivo>.json
reproducir.py fam01-na        --unidad <id NA de R3> --salida salidas/fam01/<archivo>.json
reproducir.py fam01-receta    --salida salidas/fam01/receta_08.json
```

- `fam01-listas`: integridad de las listas R2 y R3, del marco R3 de 536 y de
  su separación. Recalcula la identidad B y la muestra de 27 desde el marco.
  Sin cálculo científico.
- `fam01-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam01.json`;
  - el contexto S6 y el entorno (perfil y F2);
  - la correspondencia de los manifiestos públicos con los históricos;
  - la carga del productor, de los validadores fijados, del comparador y de
    la ruta nacional.
- `fam01-unidad`: calcula y valida una o más unidades numéricas de la misma
  lista.
  - Rechaza las NA, las unidades fuera de la lista y las salidas existentes.
  - Escribe los documentos nativos y las filas, el documento comparable R2,
    el registro y el dictamen de validación, `entorno.json`,
    `archivos_leidos.json` y `ejecucion.json`. Este último lleva los estados
    por unidad, los tiempos separados de cálculo y validación, la técnica, el
    entorno y las dependencias.
  - Termina con 0 solo si todo queda calculado y validado.
- `fam01-comparar`: comparador v3-S6 en tres comparaciones separadas.
  - Histórica: reglas vigentes y selladas del plan, DR-1 tal cual.
  - Limpia: además, E2/E3 con el nivel R1 real, el historial operativo como
    procedencia y la correspondencia del saneamiento; entorno estricto.
  - Limpia con F2, adoptada para FAM01.
  - Autentica el registro de validación productiva y separa los estados de
    cálculo, validación, cada comparación y reproducción. La reproducción
    dice con qué comparación se acepta.
  - Termina con 0 si la reproducción queda aceptada con la comparación
    histórica, con la limpia o con la limpia con F2, y con 1 en otro caso.
- `fam01-na`: comprobación documental de una NA de R3 (clase, marco,
  original, validación y mapa D4). No calcula.
- `fam01-receta`: escribe la receta del recorrido completo, que no se
  ejecuta, con una variante agrupada que comparte techos. El recorrido
  completo lo ejecuta `general --modo completo` (`run.ps1 full`).

FAM02 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam02-listar    --salida salidas/fam02/listar_03.json
reproducir.py fam02-comprobar --salida salidas/fam02/comprobar_10.json
reproducir.py fam02-unidad    --tarea <R1-…> [--hoja <afirmación> ...] [--tope 2400] [--salidas-guardadas] --salida salidas/fam02/<ejecucion>/<tarea>
reproducir.py fam02-validar   --tarea <R1-…> --nueva <salida> --salida <carpeta nueva> [--enlazar]
reproducir.py fam02-comparar  --tarea <R1-…> --nueva <salida> --salida <archivo>.json
reproducir.py fam02-receta    --salida salidas/fam02/receta_04.json
```

- `fam02-listar`: las 18 tareas con dependencias expandidas, consumos, ids y
  ruta, más el piloto recalculado frente al fijado. Sin modelo.
- `fam02-comprobar`: sin cálculo. Comprueba:
  - las huellas de `fuentes_fam02.json` (si fallan, se detiene e informa);
  - `opciones_r1`, el plan y el piloto;
  - el plan del orquestador bajo S6 frente al histórico;
  - por cada tarea, referencias y productores autenticados y el preflight
    de la pila; en las rutas por comando, derivación, importación y
    entradas;
  - la correspondencia de las copias públicas, que no haya rutas
    personales y que estén las entradas en ejecución;
  - el entorno y F2.
- `fam02-unidad`: una tarea en la subcarpeta nueva de su ejecución.
  - Las dependencias se toman del enlace local de la misma ejecución,
    antes de crear nada.
  - Separa cálculo y validación: C y D por el orquestador, las rutas por
    comando con sus comandos históricos y su validación, y V sin cálculo.
  - Si la validación cumple, escribe el enlace
    `<ejecucion>/aceptaciones/<tarea>.json`. Termina con 0 solo si todo
    queda calculado y validado.
  - Con `--salidas-guardadas` (solo rutas por comando) hace la prueba de
    conexión: no ejecuta comandos y la salida nunca cuenta como
    reproducción.
- `fam02-validar`: repite la validación de una salida en una carpeta nueva,
  sin calcular. Con `--enlazar` (rutas por comando, `--salida
  <ejecucion>/<tarea>`), si el cálculo de origen terminó y la revalidación
  cumple, escribe el enlace en esa ejecución nueva.
- `fam02-comparar`: comprueba la ligadura y compara cada tarea por su regla:
  - C, con la referencia citada y la medición histórica;
  - B1/B2/F, igualdad con la salida histórica del mismo comando. En R1-F,
    además, quedan fuera solo sus cuatro campos de reloj
    (IGUALDAD-R1F-TIEMPOS-v1);
  - B3, por unidad; A1/A2, por testigos; A3, el par en L;
  - D y V, por su verificación.

  Termina con 0 solo si la reproducción queda aceptada, lo que una prueba de
  conexión nunca consigue.
- `fam02-receta`: receta de las 18 tareas, sin ejecutar.

Salidas guardadas:
- piloto `C1_piloto_01`, con sus revalidaciones y comparaciones;
- piloto R1-F:
  - `F_piloto_01`: fallo de escritura, corregido;
  - `F_piloto_02`: calculado y rechazado, con `F_piloto_02_validar_01`,
    `F_piloto_02/R1-F.comparacion.json` y `F_piloto_02.diagnostico.json`;
  - `F_revalidacion_01`: revalidación aceptada, enlace y comparación;
  - pruebas de la corrección en `pruebas_03.json`;
- pruebas de conexión `conexion_01` a `_03` (la vigente es `_03`);
- pruebas de fallo y traslado en `pruebas_01.json` (C) y `pruebas_02.json`
  (enlace y rutas);
- `listar_01` y `_02`, `comprobar_01` a `_09` y `receta_01` a `_03`.

FAM03 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam03-preparar  --salida salidas/fam03/preparar_03.json
reproducir.py fam03-listar    --salida salidas/fam03/listar_02.json
reproducir.py fam03-comprobar --salida salidas/fam03/comprobar_04.json
reproducir.py fam03-unidad    --tarea <PROD…-T…> [--tope 2400] --salida salidas/fam03/<ejecucion>/<tarea>
reproducir.py fam03-validar   --nueva <carpeta de fam03-unidad> --salida <carpeta nueva>
reproducir.py fam03-comparar  --tarea <PROD…-T…> --nueva <carpeta> --salida <archivo>.json
reproducir.py fam03-receta    --salida salidas/fam03/receta_02.json
```

- `fam03-preparar`: fija `datos/fam03` sin cálculo; solo construye el
  contexto. No sobrescribe un dato distinto.
- `fam03-listar`: las 136 tareas con sus unidades y su árbol de referencia,
  más los pilotos.
- `fam03-comprobar`: sin cálculo ni contexto. Comprueba:
  - las huellas de `fuentes_fam03.json`;
  - el plan, verificado y comparado con el histórico;
  - la cobertura de 152 unidades, 136 tareas y 136 árboles autenticados;
  - los módulos R-A y el inventario anclado;
  - los pilotos.
- `fam03-unidad`: una tarea del plan en una carpeta nueva.
  - Calcula con `evaluadores_ra` y valida con el validador instalado.
  - Escribe el árbol de la tarea, `ejecucion.json` (tiempos separados,
    entorno y lecturas) y `archivos_leidos.json`.
  - Se niega antes de crear nada si falta o cambió una dependencia.
  - `--tope` es el tope interno de la tarea, 2400 s como en el plan; el
    límite externo lo pone el supervisor.
- `fam03-validar`: revalidación sin cálculo de los bytes guardados.
- `fam03-comparar`: comparación con el árbol aceptado de la tarea.
  - Contenido científico exacto y clasificación y D4 exactos.
  - Tiempos, identidades y huellas derivadas separados por objeto y
    puntero, y visibles.
  - Termina con 0 solo si la reproducción queda aceptada.
- `fam03-receta`: las 136 tareas con sus órdenes, sin ejecutar.

Salidas guardadas de FAM03:
- `pilotos_01/` con PROD1-T001, PROD2-T006 y PROD3-T121, y sus
  comparaciones `_01` y `_02` (la vigente es `_02`);
- `preparar_01` (fallo de interfaz, corregido) y `_02`;
- `comprobar_01` a `_03`, `listar_01` y `receta_01`;
- controles `pruebas_01.json` (16/17, defecto corregido) y `pruebas_02.json`
  (17/17);
- regresión `regresion_fam01_comprobar.json` y
  `regresion_fam02_comprobar.json`;
- registros del supervisor en `lanzador/`.

FAM04 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam04-listar    --salida salidas/fam04/listar_03.json
reproducir.py fam04-comprobar --salida salidas/fam04/comprobar_03.json
reproducir.py fam04-unidad    --tarea <L1-ELAST|L1-LAMBDA|L1-COORD> [--unidad <frontera|conjunto|clave>] [--tope 2400] --salida salidas/fam04/<ejecucion>/<tarea>
reproducir.py fam04-validar   --nueva <carpeta de fam04-unidad> --salida <archivo nuevo>.json
reproducir.py fam04-comparar  --tarea <L1-…> --nueva <carpeta> --validacion <archivo de fam04-validar> --salida <archivo nuevo>.json
reproducir.py fam04-receta    --salida salidas/fam04/receta_02.json
```

- `fam04-listar`: las unidades de cada tarea (6 fronteras, 2 conjuntos, 12
  claves) y los pilotos fijados. Sin cálculo.
- `fam04-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam04.json`;
  - la procedencia: código, validador, manifiesto y anexo iguales al
    alcance y al paquete, y el anexo ligado al manifiesto;
  - el núcleo paper2b (37/37);
  - la cobertura: 70 nodos, 4 filas LAMBDA con sus estados nacionales, 12
    techos y 192 comparaciones;
  - las 192 filas padre y las referencias;
  - la revalidación de las tres referencias, igual a la histórica;
  - los pilotos.
- `fam04-unidad`: una tarea completa o, con `--unidad`, una unidad completa
  (una frontera con todos sus nodos, un conjunto con sus dos variantes y
  todos sus estados nacionales, o una clave con su techo y sus 16
  comparaciones).
  - Se niega antes de crear nada si falta o cambió una dependencia, o si
    una fila padre de COORD no se autentica.
  - Escribe los productos, `resultado.json` (esquema de `tarea_lote`),
    `ejecucion.json` y `archivos_leidos.json`.
  - `--tope` es el tope de trabajo de la tarea, 2400 s como en el paquete:
    reloj interno de 2280 s. El límite externo lo pone el supervisor.
- `fam04-validar`: `validar_lote` sobre los bytes guardados, con la
  selección registrada y el anexo de cobertura nacional.
- `fam04-comparar`: comparación con la ejecución aceptada rem112, limitada a
  la selección.
  - Exige una validación aceptada de esos mismos bytes.
  - Productos por fila y puntero, con valores exactos.
  - Identidades y llamadas a bridge visibles; el reloj, solo informado.
  - Termina con 0 solo si la reproducción queda aceptada.
- `fam04-receta`: las tres tareas con sus órdenes, sin ejecutar.

Salidas guardadas de FAM04:
- pilotos: `pilotos_01` y `_02`, con defectos del registro de lecturas
  (corregidos; mismos productos), y `pilotos_03`, el vigente, con sus
  validaciones y comparaciones;
- `listar_01` y `_02`, `comprobar_01` y `_02`, `receta_01`;
- controles `controles_01.json` (29/29), con sus copias en `controles_01/`;
- regresión `regresion_fam01_comprobar.json`, `_fam02_` y `_fam03_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`.

FAM05 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam05-listar    --salida salidas/fam05/listar_02.json
reproducir.py fam05-comprobar --salida salidas/fam05/comprobar_03.json
reproducir.py fam05-unidad    --tarea <L1-ELAST|L1-LAMBDA> [--unidad <frontier_id|SUPLEMENTO|conjunto|país>] [--tope 2400] --salida salidas/fam05/<ejecucion>/<tarea>
reproducir.py fam05-validar   --nueva <carpeta de fam05-unidad> --salida <archivo nuevo>.json
reproducir.py fam05-comparar  --tarea <L1-…> --nueva <carpeta> --validacion <archivo de fam05-validar> --salida <archivo nuevo>.json
reproducir.py fam05-receta    --salida salidas/fam05/receta_02.json
```

- `fam05-listar`: las unidades (393 mallas nuevas, la unidad SUPLEMENTO
  con las 6 mallas históricas y 12 pares) y los pilotos fijados. Sin
  cálculo.
- `fam05-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam05.json`;
  - la procedencia: código, validador, manifiesto, anexo, identidad C0 y D7
    iguales al alcance y al paquete rem119, y la fuente del suplemento
    igual al catálogo;
  - el núcleo C0: identidad recalculada desde su inventario;
  - la cobertura: mallas, nodos, fronteras cubiertas y equivalencias;
    estados por par, la enumeración de los dominios estrictos y el
    presupuesto de bridge (232 + 256);
  - los recuentos del libro rem121 frente a los archivos;
  - las referencias y su revalidación, igual a la histórica;
  - los pilotos.
- `fam05-unidad`: una tarea completa o, con `--unidad`, una unidad
  completa. La unidad es una malla nueva con todos sus nodos, la unidad
  SUPLEMENTO (las 6 mallas históricas juntas) o un par con sus dos variantes
  y todos sus estados o candidatos.
  - Se niega antes de crear nada si falta o cambió una dependencia o si el
    núcleo C0 no tiene su identidad.
  - Escribe los productos, `resultado.json` (esquema de `tarea_lote`),
    `ejecucion.json` y `archivos_leidos.json`.
  - `--tope` como en FAM04: reloj interno de 2280 s; el límite externo lo
    pone el supervisor.
- `fam05-validar`: `validar_lote` del lote 2 sobre los bytes guardados, con
  la selección registrada y el anexo.
- `fam05-comparar`: comparación con la ejecución aceptada rem120, limitada
  a la unidad.
  - Exige una validación aceptada de esos mismos bytes.
  - Productos por fila y puntero, con valores exactos.
  - En la procedencia, el vínculo con `frontier_result` se comprueba por
    separado: cada lado apunta a su propio producto.
  - En el suplemento, las 70 filas deben conservar los campos de la fuente
    y añadir solo la topología.
  - Llamadas a bridge y estados por extremo frente al anexo.
  - Termina con 0 solo si la reproducción queda aceptada.
- `fam05-receta`: las dos tareas con sus órdenes, sin ejecutar.

Salidas guardadas de FAM05:
- pilotos `piloto_01` (ELAST), `piloto_02` y `piloto_03` (LAMBDA) y
  `verificacion_hist_01` (SUPLEMENTO), con sus validaciones y comparaciones;
- `listar_01`, `comprobar_01` y `_02` (código final, igual salvo el tiempo)
  y `receta_01`;
- controles `controles_01.json` (23/23), con sus copias en `controles_01/`;
- regresión `regresion_fam01_comprobar.json` a `_fam04_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`.

FAM06 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam06-listar    --salida salidas/fam06/listar_02.json
reproducir.py fam06-comprobar --salida salidas/fam06/comprobar_03.json
reproducir.py fam06-unidad    [--unidad <FRN-E4:…>] [--tope 2400] --salida salidas/fam06/<ejecucion>/L1-ELAST
reproducir.py fam06-validar   --nueva <carpeta de fam06-unidad> --salida <archivo nuevo>.json
reproducir.py fam06-comparar  --tarea L1-ELAST --nueva <carpeta> --validacion <archivo de fam06-validar> --salida <archivo nuevo>.json
reproducir.py fam06-conciliar --e4 <carpeta|guardado> [--validacion-e4 <archivo>] --lote2 <carpeta L1-ELAST de FAM05|guardado> [--validacion-lote2 <archivo>] --salida salidas/fam06/<ejecucion>/conciliacion
reproducir.py fam06-comparar  --tarea CONCILIACION --nueva <carpeta de fam06-conciliar> --salida <archivo nuevo>.json
reproducir.py fam06-receta    --salida salidas/fam06/receta_02.json
```

- `fam06-listar`: las 383 mallas y los pilotos fijados. Sin cálculo.
- `fam06-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam06.json`, las piezas reutilizadas de FAM05 y
    el núcleo C0;
  - la procedencia: código igual al de FAM05 y al alcance; validador,
    manifiesto, anexo, identidad C0 y D7 iguales al alcance; conciliador
    igual al extraído, con cada sustitución presente una sola vez;
  - la cobertura: mallas, nodos, instrumentos, vínculo con la malla de
    origen, pares, puntos emparejados y universo padre;
  - los 16 recuentos del libro rem122 frente a los archivos;
  - las referencias y la revalidación de E4, igual a la histórica;
  - los pilotos y la receta.
- `fam06-unidad`: las 383 mallas o, con `--unidad`, una malla entera.
  - Se niega antes de crear nada si falta o cambió una dependencia o si el
    núcleo C0 no tiene su identidad.
  - Escribe `frontier_result.jsonl`, `resultado.json` (esquema de
    `tarea_lote`), `ejecucion.json` y `archivos_leidos.json`.
  - `--tope` como en FAM05: reloj interno de 2280 s; el límite externo lo
    pone el supervisor.
- `fam06-validar`: `validar_lote` del lote 2 sobre los bytes guardados, con
  la selección registrada y el manifiesto y el anexo E4.
- `fam06-conciliar`: la conciliación G/N con el productor histórico. Cada
  lado se declara siempre:
  - una carpeta nueva con su validación aceptada (para el lote 2, la tarea
    L1-ELAST completa de FAM05);
  - o `guardado`: el producto aceptado del paquete, autenticado por su
    huella del catálogo.

  Con un lado E4 parcial, solo concilia sus pares. Nunca lee la
  conciliación esperada.
- `fam06-comparar --tarea L1-ELAST`: comparación con la ejecución aceptada
  rem121, limitada a la selección. Exige una validación aceptada de esos
  mismos bytes; compara filas por puntero con valores exactos.
- `fam06-comparar --tarea CONCILIACION`: comparación exacta con la
  conciliación aceptada.
  - Por par y hoja, con totales derivados del detalle.
  - Los vínculos de cada lado se comprueban contra sus propios bytes.
  - Las diferencias de topología G/N deben conservarse.
  - Termina con 0 solo si la reproducción queda aceptada.
- `fam06-receta`: los tres pasos (mallas E4, lado de origen con la receta
  de FAM05 y conciliación de las dos salidas nuevas), sin ejecutar.

Salidas guardadas de FAM06:
- pilotos `piloto_01` (d), `piloto_02` (f) y `piloto_03` (df), cada uno con
  `L1-ELAST/`, su validación y comparación, y `conciliacion/` con su
  comparación;
- `regeneracion_01/conciliacion` (391 pares sobre entradas guardadas) y su
  comparación;
- `listar_01`, `comprobar_01`, `_02` (código final) y `_03` (tras
  actualizar el catálogo), iguales salvo el tiempo, y `receta_01`;
- controles `controles_01.json` (26/26), con sus copias en `controles_01/`;
- regresión `regresion_fam01_comprobar.json` a `_fam05_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`. Los registros de
  `lanzador/` guardan rutas absolutas de esta máquina.

FAM07 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam07-listar    --salida salidas/fam07/listar_02.json
reproducir.py fam07-comprobar --salida salidas/fam07/comprobar_04.json
reproducir.py fam07-unidad    --tarea L1-COORD-R1|R2|R3 [--tope 2400] --salida salidas/fam07/<ejecucion>/<tarea>
reproducir.py fam07-validar   --nueva <carpeta de fam07-unidad> --salida <archivo nuevo>.json
reproducir.py fam07-comparar  --tarea <tarea> --nueva <carpeta> --validacion <archivo de fam07-validar> --salida <archivo nuevo>.json
reproducir.py fam07-ensamblar --entrada L1-COORD-R1=<carpeta|guardado> --entrada L1-COORD-R2=<…> --entrada L1-COORD-R3=<…> --salida salidas/fam07/<ejecucion>
reproducir.py fam07-comparar  --tarea ENSAMBLADO --nueva <carpeta de fam07-ensamblar> --salida <archivo nuevo>.json
reproducir.py fam07-receta    --salida salidas/fam07/receta_02.json
```

- `fam07-listar`: las 26 claves, la partición y los pilotos fijados. Sin
  cálculo.
- `fam07-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam07.json`, las piezas reutilizadas y el
    núcleo C0;
  - la procedencia (código igual al índice del paquete y al alcance) y el
    motor certificado, sin calcular;
  - la cobertura (26 claves, 1.532 celdas, 30 afectadas), los 20
    reutilizados con su garantía y las 192 previas;
  - los 14 recuentos del libro rem125, las referencias y la revalidación de
    las tres tareas guardadas, igual a la histórica;
  - los pilotos y la receta.
- `fam07-unidad`: una tarea entera (dos techos y sus comparaciones).
  - Se niega antes de crear nada si falta o cambió una dependencia o si el
    núcleo C0 no tiene su identidad.
  - Escribe `resultado.json` y `salida/` (del trabajador), `ejecucion.json`
    y `archivos_leidos.json`.
  - `--tope` como en FAM05: reloj interno de 2280 s; el límite externo lo
    pone el supervisor.
- `fam07-validar`: `validar_lote` COORD sobre los bytes guardados.
- `fam07-ensamblar`: el ensamblador histórico con una entrada declarada por
  tarea, carpeta nueva de `fam07-unidad` o `guardado` (tarea aceptada
  rem124, autenticada por su huella). Una tarea sin entrada no se sustituye:
  el ensamblado se rechaza. Declara si es regeneración, mixto o nuevo, y
  nunca lee el ensamblado esperado.
- `fam07-comparar`: exacta frente a rem124 (CR-HASH-CANONICO y
  CR-DISCRETOS). En los techos aparta, visibles, `segundos` y el vínculo
  `alcance_sha256`, y comprueba la huella derivada contra los bytes de la
  referencia. Termina con 0 solo si la reproducción queda aceptada.
- `fam07-receta`: comprobar, las tres tareas una a una y el ensamblado de
  las tres salidas nuevas, sin ejecutar.

Salidas guardadas de FAM07:
- piloto `piloto_01/L1-COORD-R1`, con su validación y sus comparaciones
  (`comparacion_02`, con la huella derivada final);
- `regeneracion_01` (1.532 sobre entradas guardadas) y `mixto_01` (R1 nueva
  y R2/R3 guardadas), con sus comparaciones;
- `listar_01`, `comprobar_01`, `_02` (código final) y `_03` (tras actualizar el catálogo), iguales salvo
  el tiempo, y `receta_01`;
- controles `controles_02.json` (29/29), con sus copias en `controles_02/`;
- regresión `regresion_fam01_comprobar.json` a `_fam06_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`. Los registros de
  `lanzador/` guardan rutas absolutas de esta máquina.

FAM08 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam08-listar    --salida salidas/fam08/<archivo nuevo>.json
reproducir.py fam08-comprobar --salida salidas/fam08/<archivo nuevo>.json
reproducir.py fam08-unidad    --tarea L1-ELAST [--unidad <FRN-ENF:…>] | ABL-ENF-T1…T6 [--tope 2400] --salida salidas/fam08/<ejecucion>/<tarea>
reproducir.py fam08-validar   --nueva <carpeta de fam08-unidad> --salida <archivo nuevo>.json
reproducir.py fam08-recuperar --entrada ABL-ENF-T1=<carpeta|guardado> --salida salidas/fam08/<ejecucion>/recuperacion
reproducir.py fam08-conciliar --entrada mallas=<carpeta|guardado> [--entrada piloto=<carpeta>]… --salida salidas/fam08/<ejecucion>/pares
reproducir.py fam08-integrar  --entrada ABL-ENF-T1=<…> … --entrada ABL-ENF-T6=<…> --entrada mallas=<…> [--entrada piloto=<…>]… [--entrada certificado=<archivo>] --salida salidas/fam08/<ejecucion>/integral
reproducir.py fam08-comparar  --tarea L1-ELAST|ABL-ENF-T* --nueva <carpeta> --validacion <archivo> --salida <archivo nuevo>.json
reproducir.py fam08-comparar  --tarea PARES|RECUPERACION|INTEGRAL --nueva <carpeta> --salida <archivo nuevo>.json
reproducir.py fam08-receta    --salida salidas/fam08/<archivo nuevo>.json
```

- `fam08-listar`: mallas, claves, tareas y pilotos fijados. Sin cálculo.
- `fam08-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam08.json`, las reutilizadas y el núcleo C0;
  - la procedencia (índices, manifiestos, guardadas y proyecciones) y el
    motor certificado, sin calcular;
  - la cobertura (29 mallas, 26 pares, 26 claves, 1.724 celdas, 144 de la
    clave no alcanzada) y las referencias;
  - la revalidación de las guardadas (T1 por la recuperación) y los 12
    recuentos de los libros;
  - los pilotos y la receta.
- `fam08-unidad`: una tarea entera, o una malla con `--unidad`. Se niega
  antes de crear nada si falta o cambió una dependencia o si el núcleo C0 no
  tiene su identidad. No abre salidas guardadas ni referencias.
- `fam08-validar`: `validar_lote` del lote 2 (mallas) o de lote_enf (T2–T6).
  T1 se valida con `fam08-recuperar`.
- `fam08-recuperar`: recuperación de T1 y certificado reemitido con el
  certificador aceptado; T1 sigue incompleta, sin argmax.
- `fam08-conciliar` y `fam08-integrar`: los guiones históricos con entradas
  declaradas. Una entrada que falta no se sustituye por su referencia.
  Declaran si son regeneración, mixtas o nuevas, y nunca leen el producto
  esperado.
- `fam08-comparar`: exacta frente a las referencias (CR-HASH-CANONICO y
  CR-DISCRETOS), con los campos operativos, de vínculo, de puerta y de
  ubicación apartados y visibles, y las huellas derivadas recomprobadas.
- `fam08-receta`: comprobar, las mallas, T1–T6, los pares y la integración
  sobre salidas nuevas, sin ejecutar.

Salidas guardadas de FAM08:
- pilotos `piloto_02` (malla_d, malla_f, malla_df y ABL-ENF-T2), con
  validación y comparación; `piloto_01`, corrida anterior con los mismos
  productos;
- `regeneracion_02` (pares, recuperación e integral sobre entradas
  guardadas) y `mixta_03` (mallas piloto y T2 nuevas), con sus
  comparaciones; `regeneracion_01`, `mixta_01` y `mixta_02`, corridas
  anteriores;
- `listar`, `comprobar_01` (no cumplía; corregido), `_02` y `_03` (código y
  catálogo finales), y `receta_01`;
- controles `controles_02.json` (35/35), con sus copias en `controles_02/`;
  `controles_01.json` (34/34, código anterior);
- regresión `regresion_fam01_comprobar.json` a `_fam07_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`.

FAM11 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam11-listar    --salida salidas/fam11/<archivo nuevo>.json
reproducir.py fam11-comprobar --salida salidas/fam11/<archivo nuevo>.json
reproducir.py fam11-unidad    --tarea ABL-COV-T1…T6 [--tope 2400] | B1 --salida salidas/fam11/<ejecucion>/<tarea>
reproducir.py fam11-unidad    --tarea B2 --b1 <carpeta B1> --validacion-b1 <su registro de fam11-validar> --salida salidas/fam11/<ejecucion>/B2
reproducir.py fam11-validar   --nueva <carpeta de fam11-unidad> --salida <archivo nuevo>.json
reproducir.py fam11-ensamblar --entrada ABL-COV-T1=<carpeta|guardado> … --entrada ABL-COV-T6=<…> --salida salidas/fam11/<ejecucion>/<carpeta>
reproducir.py fam11-comparar  --tarea ABL-COV-T*|B1|B2 --nueva <carpeta> --validacion <archivo> --salida <archivo nuevo>.json
reproducir.py fam11-comparar  --tarea ENSAMBLADO --nueva <carpeta> --salida <archivo nuevo>.json
reproducir.py fam11-receta    --salida salidas/fam11/<archivo nuevo>.json
```

- `fam11-listar`: tareas, claves, grupos y pilotos fijados. Sin cálculo.
- `fam11-comprobar`: sin cálculo científico. Comprueba:
  - las huellas de `fuentes_fam11.json`, las reutilizadas y el núcleo C0;
  - la procedencia (índices, manifiestos, guardadas y proyecciones), la
    reconstrucción de los manifiestos B1/B2 y el motor certificado, sin
    calcular;
  - la cobertura (26 claves, 1.724 celdas, 1.728 afirmaciones; en B2,
    4.608 / 2.304 / 1.920 contextos, 480 puentes, 60 Q) y las referencias;
  - la revalidación de las seis guardadas y los 13 recuentos de los libros;
  - los pilotos y la receta.
- `fam11-unidad`: una tarea COV entera, B1 o B2. Se niega antes de crear
  nada si falta o cambió una dependencia, si el núcleo C0 no tiene su
  identidad o, en B2, si el B1 dado no tiene un registro de validación
  aceptado para sus bytes que su revalidación confirme. No abre salidas
  guardadas ni referencias.
- `fam11-validar`: `validar_lote` de COV, `validar_b1` o `validar_b2`
  (en B2 recomprueba además el enlace registrado).
- `fam11-ensamblar`: ensamblado y conciliación COV con una entrada
  declarada por tarea. Una tarea que falta no se sustituye por su
  referencia. Declara si es regeneración, mixta o nueva, y nunca lee el
  producto esperado.
- `fam11-comparar`: exacta frente a las referencias (CR-HASH-CANONICO y
  CR-DISCRETOS), con los campos operativos, de vínculo, de puerta y de
  ubicación apartados y visibles, y las huellas derivadas recomprobadas. En
  B2 incluye la resolución de las doce frente a rem170.
- `fam11-receta`: comprobar, T1–T6, el ensamblado y la conciliación, B1 y
  B2 sobre salidas nuevas, sin ejecutar.

Salidas guardadas de FAM11:
- pilotos `piloto_01` (ABL-COV-T1, B1 y B2), con validación y comparación;
  `B2.comparacion_01_no_aceptada.json`, primera comparación de B2 (puntero
  corregido, sin repetir el cálculo);
- `regeneracion_01` (seis guardadas) y `mixta_01` (T1 nueva, T2–T6
  guardadas), con sus comparaciones;
- `listar`, `comprobar_01` y `comprobar_02` (catálogo final), y
  `receta_01`;
- controles `controles_02.json` (40/40), con sus copias en `controles_02/`;
  `controles_01.json` (39/40, código anterior);
- regresión `regresion_fam01_comprobar.json` a `_fam08_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`. Los registros de
  `lanzador/` guardan rutas absolutas de esta máquina.

FAM09 (mismo Python, opciones y entorno que FAM01):

```text
reproducir.py fam09-listar    --salida salidas/fam09/<archivo nuevo>.json
reproducir.py fam09-comprobar --salida salidas/fam09/<archivo nuevo>.json
reproducir.py fam09-etapa     --tarea HIST|LAMBDA --salida salidas/fam09/<carpeta nueva>
reproducir.py fam09-etapa     --tarea CAPTURA --entrada lambda=<carpeta> --entrada validacion_lambda=<registro> --salida <carpeta nueva>
<supervisar.py> TESTIGO 600 <registro> --cwd <base> -- reproducir.py fam09-etapa --tarea TESTIGO --salida <carpeta nueva>
reproducir.py fam09-etapa     --tarea INCORPORACION --entrada captura=<carpeta> --entrada validacion_captura=<registro> \
                              --entrada testigo=<carpeta> --entrada validacion_testigo=<registro> --salida <carpeta nueva>
reproducir.py fam09-etapa     --tarea C5B --entrada testigo_vista=<carpeta INCORPORACION> --entrada validacion_testigo_vista=<registro> --salida <carpeta nueva>
reproducir.py fam09-validar   --nueva <carpeta de fam09-etapa> --salida <archivo nuevo>.json
reproducir.py fam09-comparar  --tarea HIST|LAMBDA|CAPTURA|TESTIGO|INCORPORACION|C5B --nueva <carpeta> --validacion <registro> --salida <archivo nuevo>.json
reproducir.py fam09-receta    --salida salidas/fam09/<archivo nuevo>.json
```

- `fam09-listar`: recuento del anexo, manifiestos y piloto; fija
  `pilotos.json` y la declaración. Sin cálculo.
- `fam09-comprobar`: sin cálculo. Huellas de `fuentes_fam09.json` y de las
  reutilizadas, unicidad de las sustituciones, declaración, pilotos,
  referencias, libros y receta. Si falta una pieza, no cumple y la nombra.
- `fam09-etapa`: una etapa en una carpeta nueva. Se niega antes de crearla
  si falta o cambió una dependencia, o si una entrada no es una etapa
  completa con un registro de validación aceptado para sus bytes. No abre
  referencias.
- `fam09-validar`: el verificador histórico de la etapa sobre los bytes
  de la carpeta; en el testigo, `validar_testigo.py` (U36), el estado de la
  ejecución y el inventario de la entrega.
- `fam09-comparar`: frente a los libros y las referencias. Campos
  científicos exactos; campos locales y de vínculo nombrados y comprobados
  contra los archivos nuevos; transición frente a la etapa anterior; en
  C5B, la partición recontada desde las filas, la identidad de las
  preservadas y los recuentos outside_support.
- `fam09-receta`: las 20 órdenes en su orden, sin ejecutar.

Salidas guardadas de FAM09:
- etapas `hist`, `lambda`, `captura`, `testigo`, `incorporacion` y `c5b`,
  cada una con su `.validacion.json` y su `.comparacion.json`;
- `listar`, `comprobar` (anterior a la extracción final),
  `comprobar_02` (final: 276 piezas, ninguna alterada; cumple) y
  `receta_01`;
- controles `pruebas_01.json` (25/25), con sus copias en `pruebas_01/`;
- regresión `regresion_fam01_comprobar.json` a `_fam08_` y `_fam11_`;
- resumen del supervisor, sin rutas, en `lanzador.txt`. Los registros de
  `lanzador/` guardan rutas absolutas de esta máquina.

FAM10 (mismo Python, opciones y entorno que FAM01; `PYTHONHASHSEED=0`):

```text
reproducir.py fam10-comprobar --salida salidas/fam10/<archivo nuevo>.json
reproducir.py fam10-tabla     --entrada enf_integral=<carpeta de fam08-integrar> --entrada registro_enf_integral=<su fam08-comparar INTEGRAL> \
                              --entrada cov=<carpeta de fam11-ensamblar> --entrada registro_cov=<su fam11-comparar ENSAMBLADO> \
                              --entrada p7=<archivo de p7-suplemento> --entrada q_local=<carpeta de q-local> \
                              --entrada b1=<carpeta B1> --entrada validacion_b1=<su fam11-validar> \
                              --entrada b2=<carpeta B2 sobre ese B1> --entrada validacion_b2=<su fam11-validar> \
                              --salida salidas/fam10/<carpeta nueva>
reproducir.py fam10-etapa     --tarea ENF --entrada enf_integral=<carpeta> --entrada registro_enf_integral=<registro> --salida <carpeta nueva>
reproducir.py fam10-etapa     --tarea SINTESIS --entrada enf=<carpeta ENF> --entrada validacion_enf=<registro> --entrada cov=<carpeta> \
                              --entrada registro_cov=<registro> --entrada p7=<archivo> --entrada q_local=<carpeta> --salida <carpeta nueva>
reproducir.py fam10-etapa     --tarea INTEGRACION --entrada sintesis=<carpeta SINTESIS> --entrada validacion_sintesis=<registro> \
                              --entrada b1=… --entrada validacion_b1=… --entrada b2=… --entrada validacion_b2=… --salida <carpeta nueva>
reproducir.py fam10-validar   --nueva <carpeta de fam10-etapa> --salida <archivo nuevo>.json
reproducir.py fam10-comparar  --tarea ENF|SINTESIS|INTEGRACION --nueva <carpeta> --validacion <registro> --salida <archivo nuevo>.json
reproducir.py fam10-receta    --salida salidas/fam10/<archivo nuevo>.json
```

- `fam10-comprobar`: sin cálculo. Comprueba:
  - las huellas de `fuentes_fam10.json` y de las piezas reutilizadas;
  - la unicidad y la compilación de las sustituciones;
  - el código ligado a su original;
  - los resúmenes de autoridad y las referencias.

  Si falta una pieza, no cumple y la nombra.
- `fam10-tabla`: la orden única. Antes de crear la carpeta comprueba las
  dependencias y las diez entradas. Las entradas deben estar dentro de la
  base, cada una con su registro aceptado para sus bytes.

  Encadena ENF, SINTESIS e INTEGRACION, cada una con su validación. Solo
  después abre las referencias para las tres comparaciones. Escribe
  `tabla.json` con los pasos, los estados y la tabla final:
  `integracion/sintesis/EXP8_POR_AFIRMACION.jsonl`, `RESUMEN_EXP8.json` y
  `COV12_RESOLUCION_GLOBAL.jsonl`.
- `fam10-etapa`: una etapa en una carpeta nueva, con las mismas
  comprobaciones. No abre referencias.
- `fam10-validar`: validación sin referencias.
  - ENF: la parte científica de la auditoría rem148 y la estructura.
  - SINTESIS: 17 comprobaciones derivadas de las filas y las entradas
    (enlaces, recuentos, regla ±ε, P7 una vez y m*).
  - INTEGRACION: 12 comprobaciones. Exactamente doce líneas cambian, las
    1.716 restantes quedan idénticas byte a byte y la aritmética B2 es
    exacta.
- `fam10-comparar`: compara por clave y escenario frente a rem147/rem148,
  rem160/rem161 y rem170/rem171. Los campos científicos deben ser exactos.
  Las diferencias de ruta, huella, huella de código, hora, tiempo y tamaño
  se nombran y se comprueban contra los archivos nuevos.
- `fam10-receta`: las órdenes en su orden, sin ejecutar. Incluye cómo
  obtener las entradas con las recetas de FAM08, FAM11 y FAM12.

Salidas guardadas de FAM10:
- `tabla_03` (final, 31,9 s) con sus tres etapas, `.validacion.json` y
  `.comparacion.json`. `tabla_01` y `tabla_02` son ejecuciones anteriores
  a las correcciones rutinarias; difieren de la final solo en rutas y
  huellas de vínculo.
- `comprobar_01` y `comprobar_02` (final: 45 piezas, ninguna alterada;
  cumple) y `receta_01`.
- Controles:
  - `pruebas_03.json` (28/28, con el código final) y sus copias en
    `pruebas_03/`;
  - `pruebas_02.json`, del código anterior a la comprobación por país;
  - `pruebas_01/`, una ejecución parcial interrumpida por un error del
    guion de controles.
- Regresión: de `regresion_fam01_comprobar.json` a `_fam09_`, más
  `_fam11_`. Tras editar el catálogo se guardan `tras_catalogo_famXX_comprobar.json`
  (FAM03–FAM11), todos con código 0.

FAM13 (mismo Python, opciones y entorno que FAM01; `PYTHONHASHSEED=0`):

```text
reproducir.py fam13-comprobar  --salida salidas/fam13/<archivo nuevo>.json
reproducir.py fam13-reproducir --salida salidas/fam13/<carpeta nueva>
reproducir.py fam13-receta     --salida salidas/fam13/<archivo nuevo>.json
```

- `fam13-comprobar`: sin cálculo. Comprueba:
  - las huellas de `fuentes_fam13.json`, de las piezas reutilizadas y de las
    1.730 filas de unidad de FAM01 que lee T7;
  - la unicidad y la compilación de las sustituciones y de los bloques
    exactos;
  - el código ligado a su original;
  - las referencias y la integridad S1;
  - el registro de la búsqueda de U60.

  Si falta una pieza, no cumple y la nombra.
- `fam13-reproducir`: la orden única. No admite `--entrada`. Antes de crear
  la carpeta comprueba las dependencias de cálculo; si falta una, se niega
  sin escribir.
  - Encadena T1T2, T7, VALIDACIONES, MATRIZ_V4 y S1. Cada etapa se valida
    sin referencias.
  - Solo después abre las referencias para comparar y escribe
    `resumen.json` con el balance de los siete productos, S1 y U60.
  - Termina con código 0 solo si F13-HISTORICAS cumple y F13-S1 es
    conforme.
- `fam13-receta`: las órdenes en su orden, sin ejecutar.

Salidas guardadas de FAM13:
- `reproducir_02` (final, 9,8 s) con sus cinco etapas, `.validacion.json`,
  `.comparacion.json` y `resumen.json`. `reproducir_01` es anterior a la
  separación del recálculo por producto; sus 14 productos son idénticos
  byte a byte.
- `comprobar_01` (no cumplía: anclas con finales CRLF en rem107),
  `comprobar_02` (final: 214 piezas, ninguna alterada; cumple) y
  `receta_01`.
- Controles:
  - `pruebas_fam13_03.json` (20/20, con el código final) y sus copias en
    `pruebas_03/`;
  - `pruebas_fam13_02.json` (19/20): esperaba una diferencia de `segundos`
    que no se produjo;
  - `pruebas_01/`, una ejecución parcial interrumpida por un error del
    guion de controles.
- Regresión: de `regresion_fam01_comprobar.json` a `_fam11_`. Tras editar el
  catálogo se guardan `tras_catalogo_famXX_comprobar.json` (FAM03–FAM11 y
  FAM13), todos con código 0.

FAM14 (mismo Python, opciones y entorno que FAM01; `PYTHONHASHSEED=0`):

```text
reproducir.py fam14-comprobar  --salida salidas/fam14/<archivo nuevo>.json
reproducir.py fam14-reproducir --salida salidas/fam14/<carpeta nueva>
reproducir.py fam14-receta     --salida salidas/fam14/<archivo nuevo>.json
```

- `fam14-comprobar`: sin cálculo. Comprueba:
  - las huellas de `fuentes_fam14.json` y de las piezas reutilizadas;
  - la unicidad y la compilación de las sustituciones de U62 y del bloque
    de U63;
  - el código ligado a su original;
  - las referencias;
  - las tres integridades (F14-GN, F14-187 y F14-176).

  Si falta una pieza, no cumple y la nombra.
- `fam14-reproducir`: la orden única. No admite `--entrada`. Antes de crear
  la carpeta comprueba las 416 piezas de cálculo; si falta una, se niega
  sin escribir.
  - Encadena GN_REGEN, GN, LOC_187 y ADOPCION_176. GN_REGEN se valida sin
    referencias, con U63 y recuentos propios.
  - Solo después compara por par y lado con las referencias y escribe
    `resumen.json` con las cuatro operaciones y el balance.
  - Termina con código 0 solo si la regeneración se acepta y las tres
    integridades son conformes.
- `fam14-receta`: las órdenes en su orden, sin ejecutar.

Salidas guardadas de FAM14:
- `reproducir_02` (final, 2,4 s) con sus cuatro etapas,
  `.validacion.json`, `gn_regen.comparacion.json` y `resumen.json`.
  `reproducir_01` terminó con código 1 por una expectativa errónea de la
  validación (399 + 8 lados en lugar de 399); sus productos ya eran
  idénticos a los aceptados.
- `comprobar_01` y `comprobar_02` (final: 420 piezas, ninguna alterada;
  cumple) y `receta_01`.
- Controles:
  - `pruebas_fam14_02.json` (22/22, con el código final) y sus copias en
    `pruebas_02/`;
  - `pruebas_fam14_01.json` (21/22): el arnés recortaba el mensaje de
    rechazo; la orden sí se había negado.
- Regresión: `regresion_famXX_comprobar.json` (FAM01–FAM11 y FAM13). Tras
  editar el catálogo se guardan `tras_catalogo_famXX_comprobar.json`
  (FAM03–FAM11, FAM13 y FAM14). Todos dan código 0.

Comando general: las 14 familias en una orden. Usa el mismo Python, las
mismas opciones y el mismo entorno que FAM01, con `PYTHONHASHSEED=0`
obligatorio.

```text
reproducir.py general --modo plan     --salida salidas/general/<carpeta nueva>
reproducir.py general --modo piloto   --salida salidas/general/<carpeta nueva>
reproducir.py general --modo completo [--procesos-fam01 N] --salida salidas/general/<carpeta nueva>
reproducir.py general --modo ensayo-fam01 --unidad <id> [--unidad <id> …] [--limite-ensayo-s S] [--procesos-fam01 N] --salida salidas/general/<carpeta nueva>
reproducir.py general --reanudar --salida <carpeta de una corrida ya empezada> [--procesos-fam01 N]
```

`--procesos-fam01 N` (de 1 a 12; por omisión 1, una llamada a la vez)
permite hasta N llamadas de FAM01 a la vez. Cada una corre en su proceso,
con un hilo numérico, y se lanza cuando sus dependencias quedaron
resueltas: la comparación de cada unidad espera a su productor. Las demás
familias siguen una a una, en el orden del plan.

`--reanudar` continúa una corrida cortada (apagado, cierre del proceso,
Ctrl+C) sobre la misma carpeta (regla REANUDACION-PASO3-v1):

- Un solo ejecutor por corrida. Si otro la ocupa, se niega con
  `CORRIDA_EN_USO_POR_OTRA_INSTANCIA`.
- Primero termina las llamadas que el ejecutor anterior dejó vivas.
- Comprueba que no cambiaron:
  - la versión del paquete (huella del inventario de ejecución);
  - el entorno (intérprete, opciones, variables y distribuciones);
  - el plan (`plan.json` y las recetas intactos, y el plan reconstruido
    ahora con el paquete, igual).
  - Si algo cambió, se niega sin tocar nada.
- Reutiliza cada llamada aceptada cuya salida conserva las huellas que se
  registraron al aceptarla, siempre que todo aquello de lo que depende se
  reutilice también. Las ampliaciones que hace una validación aceptada
  forman parte de esas huellas.
- Repite las demás, con la misma orden y el mismo límite: las que quedaron
  a medias, las no aceptadas y las que tienen insumos cambiados.
- Lo que dejaron va a `intentos/<sesión>/`.
- `--modo`, si se da, debe ser el de la corrida.
- Sin `--procesos-fam01`, usa el número de procesos con que empezó la
  corrida.

Orden exacta con la que se guardó `piloto_05`:

```text
<python de .venv-fam01> -B -P -s -X utf8 reproducir.py general --modo piloto --salida salidas/general/piloto_05
```

La corrida completa usa el intérprete y las variables de la instalación
(`README.md`, Installation), no `.venv-fam01`, que está dentro de la
carpeta del paquete. `run.ps1 full` la lanza así:

```powershell
& $py -B -P -s -X utf8 reproducir.py general --modo completo --procesos-fam01 12 --salida "salidas/<carpeta nueva>/completo"
```

`run.ps1 full -Processes 12` lanza esta orden en una carpeta nueva, tras un
plan previo; `run.ps1 resume -Run <carpeta>` la reanuda. La corrida
completa del Paso 3 (2026-11-19/21) y su cierre, 3.708 de 3.708 llamadas,
se describen en `FULL_RUN_HISTORY.md` (en inglés).

- Con `run.ps1`, el número de procesos de FAM01 se da con `-Processes` (1 a 12).
- `--modo` no tiene valor por omisión: el modo completo hay que elegirlo
  expresamente. La salida debe ser una carpeta nueva dentro de la base.
- Antes de lanzarla:
  - En una copia pública, obtenga primero las hojas que no vienen en el
    paquete con `insumos_externos/obtener_insumos.py`. Ver «Qué se descarga
    y qué viene incluido». Sin `PER_2023.xlsx`, FAM01 no corre completa.
  - El paquete tiene que estar en una unidad con espacio, porque la salida
    queda dentro de él. La estimación es de 1 a 3 GB, sin medir.
  - La corrida completa del Paso 3 duró unas 17 h con 12 procesos de
    FAM01 (`FULL_RUN_HISTORY.md`). En serie, las 1.762 unidades de FAM01
    ocuparían 57–134 h con los tiempos de los pilotos.
  - Si la corrida se interrumpe, se continúa con `--reanudar` sobre la
    misma carpeta. Las llamadas aceptadas e intactas no se recalculan.
  - Mantenga el equipo encendido, sin suspensión ni reinicios.
  - Las dos operaciones que el catálogo dejaba pendientes de decisión (U42
    y U60) se decidieron el 2026-11-18 (2.1.2). F10-ENF-AFIRMACION sigue
    RD con el límite L-ENF-AFIRMACION-AUDITORIA-REM148, y F13-HISTORICAS
    pasa a VI por L-F13-VALIDADOR-REM191. Ninguna clave queda pendiente
    de decisión: si todas las llamadas se aceptan, las 39 claves pueden
    quedar completas. Un producto rechazado o una llamada que falte siguen
    dejando su clave sin completar (`salidas/u42_u60/`).
- Código 0 si el resultado es conforme y 1 si no lo es. Un error de la
  interfaz da 2.

Qué hace cada modo:

- `plan`: sin cálculo.
  - Lanza las 13 recetas y convierte sus órdenes en llamadas de esta
    carpeta.
  - Agrega `fam01-listas`, `fam02-comprobar`, `p7-suplemento` y `q-local`
    desde el catálogo. No repite las llamadas que dos recetas comparten.
  - Las ordena por datos y liga cada una de las 39 claves a sus llamadas y a
    la comparación o verificación de sus productos.
- `piloto`: corre las mismas llamadas para FAM08 + FAM11 + FAM12 → FAM10,
  con las diez entradas de `fam10-tabla` que da RESULTADO_FAM10.md.
  - El integral ENF y el ensamblado COV toman las tareas guardadas del
    paquete (`<tarea>=guardado`, regla ENTRADA-GUARDADA-PILOTO-v1).
  - B1 → B2, P7 y Q local se calculan enteros. B2 usa el B1 validado de
    esta misma ejecución.
- `completo`: todas las llamadas del plan, con los límites de sus recetas.
  - En FAM01, las unidades de una misma clave estructural cara van en un
    mismo proceso (GRUPOS-TECHO-C2-v1): 23 claves y 290 unidades R2 en 29
    procesos de hasta 20 unidades. Para dos de esas claves, cuyos
    originales no registran el techo en frío, se usa el medido en la
    recuperación aceptada (TECHO-FRIO-MEDIDO-F01R2-v1); sus grupos, GT28 y
    GT29, van al final. El techo C₂ se calcula una vez por
    proceso y las demás unidades lo reutilizan en memoria.
  - Cada grupo tiene su propio límite, de 1.920 a 11.460 s, que cubre el
    techo en frío, la fase macro y sus unidades. Las demás unidades siguen
    una por proceso, con 600 s.
  - Cada unidad conserva su salida y su comparación.
  - En Windows, cada proceso de `reproducir.py` pide no ser estrangulado
    por ahorro de energía (PRIORIDAD-ALTA-v1). No cambia ningún cálculo.
- `ensayo-fam01`: las unidades nombradas, en un mismo proceso
  `fam01-unidad`, con `fam01-listas` antes y una comparación por unidad
  después. Varias unidades solo si comparten selección y clave de techo
  caro. El límite es el de la regla de grupos, salvo que la orden fije
  otro con `--limite-ensayo-s`.
- En los modos que ejecutan:
  - cada llamada corre en su propio proceso y, si agota su límite, se
    termina el árbol de procesos;
  - una llamada no se lanza si su productor no fue aceptado o si una de sus
    entradas falta o cambió; queda bloqueada y el balance lo dice.

Dónde leer el balance, dentro de la carpeta de salida:

- `BALANCE.md`: legible.
  - Tiene una fila por clave, con lo que se calculó, regeneró, verificó o
    quedó sin ejecutar, de dónde vienen las entradas y qué comparación se
    aplicó.
  - Una columna dice si la reproducción completa de esa clave está hecha o
    qué falta.
  - Incluye el resultado Exp8 y, al pie, los criterios y límites del
    catálogo (U42, U60…).
- `balance.json`: el detalle.
- `plan.json`: las llamadas, sus dependencias, límites, sustituciones e
  insumos históricos.
- `ejecucion.jsonl`: una línea por llamada, escrita al terminar cada una.
  Sirve para seguir el avance, por ejemplo con
  `Get-Content ejecucion.jsonl -Tail 3 -Wait`. El balance solo se escribe
  al final.
- `registro/`: la salida de cada llamada.
- Para reanudar, en los modos que ejecutan:
  - `control.json`: versión, entorno, huella del plan y una fila por sesión
    (inicio y cada reanudación, también las rechazadas);
  - `estado_llamadas.jsonl`: una línea por llamada cerrada, con su estado y
    las huellas de su salida si quedó aceptada, forzada a disco;
  - `en_curso.json`: los procesos de las llamadas en curso;
  - `intentos/<sesión>/`: lo apartado al reanudar;
  - `reanudaciones/<sesión>/`: el plan reconstruido para comprobarlo.

Salidas guardadas del comando general:

- `plan_05` (cumple, 6,8 s) y `piloto_05` (conforme, 51,3 s), con el código
  final.
- `traslado_03`: plan y piloto lanzados desde una copia del paquete sin
  `salidas/`, conformes, con 0 lecturas fuera del paquete.
- `salidas/paso3_preparacion_01`: preparación de la corrida completa
  (2.4.3). Incluye el plan con el entorno público (cumple: 3.955 llamadas y
  39 claves), el inventario de ejecución, la instrucción
  `INSTRUCCION_PASO3.md` y sus herramientas de copia y lanzamiento.
  - El inventario vigente es `9c7d6047…`, desde la reanudación (3.2) del
    2026-11-20. Sustituye a `244e831b…` (preparación 3.1, que a su vez
    sustituyó a `d061f885…`). Cambiaron `reproducir.py` (`--reanudar`) y
    `src/general.py` (cerrojo, diario de llamadas y reanudación).
  - `lanzar.ps1` espera esa huella y admite `-ProcesosFam01` (1 a 12). Con
    `-Reanudar <carpeta de la corrida>` repite las comprobaciones previas
    y reanuda. Su modo plan con 12 procesos, sobre una copia nueva en D:,
    cumple: 3.708 llamadas y 39 claves (17 RN, 12 RD y 10 VI).
- `salidas/u42_u60`: control del balance para U42 y U60
  (`local/pruebas_balance_u42_u60.py`, sin cálculo):
  - el estado antes de las decisiones;
  - el estado con las decisiones;
  - variantes con una fila pendiente y con una llamada rechazada u omitida;
  - `famXX-comprobar` de las familias que leen el catálogo, repetidos tras
    el cambio: 11/11 con código 0.
- Controles:
  - `pruebas_general_05.json` (7/7) y sus ejecuciones en `pruebas_05/`;
  - `lecturas_guardadas_01.json`: el balance lee los informes guardados de
    todas las familias.
- `regresion_01`: 17 órdenes con código 0.
- Antecedentes: las salidas `_01` a `_04` y `traslado_02`.
  - `plan_01` no cumplía por un campo ausente.
  - `piloto_01` quedó bloqueado en B1 antes de admitir las escrituras de
    `fam11-validar` en sus entradas.
  - `pruebas_01` dio 6/7.
