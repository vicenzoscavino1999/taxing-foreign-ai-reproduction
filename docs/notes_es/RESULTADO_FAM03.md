# RESULTADO FAM03 — quiebres históricos (PROD1/PROD2) y Q histórica (PROD3)

Fecha: 2026-11-16. Base: `reproduccion_limpia` (sin commits). El original se
consultó en solo lectura.

## Estado

**Revisión Codex, 2026-11-16: preparación de FAM03 cerrada en su alcance.**
Revisé el adaptador, la comparación, las referencias y los resultados
guardados. No ejecuté búsquedas ni recalculé los pilotos.

Comprobaciones realizadas en esta revisión:
- 800 fuentes coinciden con su manifiesto; 136 árboles y sus 576 miembros
  están íntegros. Sus miembros, incluidas las proyecciones públicas,
  coinciden byte a byte con el paquete fuente rem197.
- El recuento independiente de las referencias da 84 unidades completas y
  68 `incompleta_validada` declaradas D4.
- `fam03-comprobar` vuelve a dar conforme, código 0; se conservan las 136
  tareas, las 152 unidades y las decisiones Q/D4.
- Repetí las tres comparaciones sobre las salidas guardadas: aceptadas,
  sin diferencias científicas y con la misma clasificación.
- Dos controles en copias se rechazan: promover T006 de D4 a completa y
  cambiar `reloj/tope_busqueda_s` actualizando la huella del documento.
  El presupuesto no queda oculto como tiempo operativo.
- Leí los resultados de los 17 controles del ejecutor, todos conformes;
  no declaro una repetición de esa batería ni de las regresiones anteriores.

T006 reproduce el resultado limitado por D4; no demuestra un quiebre
completo ni elimina ese límite. El cierre es de preparación y pilotos:
siguen pendientes la ejecución completa (Paso 3), el aislamiento (2.4.2)
y el saneamiento de las salidas que se decida distribuir. No se extiende F2.

| Parte | Estado |
|---|---|
| Preparación | Cerrada en alcance por Codex. Entradas, referencias y receta del alcance completo presentes. Cálculo, validación y comparación conectados. |
| Pilotos | Tres pilotos calculados, validados y aceptados por la comparación: PROD1-T001, PROD2-T006 y PROD3-T121. |
| Reproducción completa | Pendiente (Paso 3). Las 136 tareas no se han ejecutado; la receta está preparada y no se ha lanzado. |

La preparación queda revisada y cerrada en su alcance. Los pilotos
cubren 4 de las 152 unidades (1 PROD1, 1 PROD2 y 2 salidas Q) y no
acreditan las demás.

## Alcance

No se deben confundir unidades, tareas y árboles:

| Familia | Unidades (`lista_PROD.json`) | Tareas del plan | Árboles aceptados |
|---|---|---|---|
| PROD1, quiebres estructurales (EQ) | 40 | 40 (una unidad cada una) | 40 |
| PROD2, quiebres macro (EQM) | 80 | 80 (una unidad cada una) | 80 |
| PROD3, Q histórica (QSEN2) | 32 salidas Q (16 afirmaciones × ámbito global y país) | 16 (dos unidades cada una) | 16 |
| **Total** | **152** | **136** | **136** |

Cada árbol tiene `dictamen_validacion.json`, `registro_productivo.json` y,
por cada unidad, un documento y sus filas. Los estados de las referencias
son:
- PROD1: 24 `completa_validada` y 16 `incompleta_validada` declaradas D4;
- PROD2: 28 `completa_validada` y 52 declaradas D4;
- PROD3: 32 `completa_validada`.

En total: 84 completas y 68 declaradas por D4.

Esta Q es la de `codigo.sensibilidad_q` con la decisión sellada
`Q-CONTINUO-COTA-SUPERIOR-v2`. No es R1-F de FAM02 ni la Q local m=1/2 de
FAM12.

## Ruta efectiva

El punto de partida es U08 `tarea_prod.py` (3204ebe5…) con U09
`validador_prod.py` (88918191…). `tarea_prod.main` no llama a `buscar()` ni
a `q_ambito()`, que conservan una ruta anterior. Calcula con
`evaluadores_ra.py` (db962e34…):
- PROD1: `evaluadores_ra.estructural`, con el cuerpo de
  `codigo.ensayo_quiebres`;
- PROD2: `evaluadores_ra.macro`, con el cuerpo de
  `codigo.ensayo_quiebres_macro`;
- PROD3: `evaluadores_ra.q_afirmacion`, con el cuerpo de
  `codigo.sensibilidad_q`, y después `mapear_q` con la decisión Q del plan.

Los módulos R-A se cargan con el importador instalado (`ra/puerto_ra.py`).
Autentica cada módulo por el inventario anclado de su entrega (lima1958) y
ejecuta su puerto. El ensamblado usa `ensamblar_quiebre` y `ensamblar_q` de
`tarea_prod`. La validación usa `ValidadorProdS6` de U09 con
`registro_productivo.generar_prod`, con D4 activa en quiebres porque el plan
la sella.

`src/fam03.py` repite esos pasos de `main` en el mismo orden y con las
mismas comprobaciones. Llama a las funciones instaladas sin editarlas.

## Extracción

`extraccion/extraer_fam03.py` (instalar, lecturas, copiar) deja 800 piezas
en `fuentes_fam03.json` (281356c1…), con origen y huella:
- **Ruta PROD instalada** (copias exactas): `tarea_prod`, `validador_prod`,
  `evaluadores_ra`, `plan_prod`, `decision_d4`, `calendario_paso4`,
  `rebalanceo_paso4` y `datos/paso4/lista_PROD.json` (42fe8914…).
  `registro_productivo` y `r1_rutas` ya estaban, sin cambios.
- **Área R-A**: `ra/puerto_ra.py`, los 17 módulos históricos y los 17
  portados (copias exactas), y `ra/R_A_dependencias.json` en copia pública
  (393db759…; origen 70dcf6d5…). Solo cambia el valor `historico`, que era
  una ruta absoluta del equipo de origen y pasa a `tmp/<entrega>`.
- **Entregas que leen los módulos R-A**: los módulos de lima1958 y lo que
  esos módulos pueden leer. El análisis estático
  (`extraccion/registro/lecturas_fam03.json`) halló 19 archivos: 10
  entradas y los inventarios de sus 9 entregas. De ellos, 5 se copiaron
  nuevos y 14 ya estaban en la base.
- **Referencias**, en `referencias/fam03/` y solo para comparar:
  - los 136 manifiestos de árbol, autenticados con el `tree_sha256` del
    catálogo, y sus 576 miembros;
  - el plan histórico en copia pública (`plan_prod_historico.json`), con la
    procedencia en rutas relativas.
- **Datos nuevos** de la base limpia, sin resultados, en `datos/fam03/`:
  despliegue, identidad y contexto esperado, plan limpio y pilotos.

Quedan 0 rutas personales en las piezas y referencias. No se copiaron:
- `corrida_paso4.py`: coordinador con autorización y rutas de
  transcripciones;
- `despliegue_operativo.json`: rutas, autor y anclas de autorización.

## Plan, decisiones y entradas de PROD3 (F1)

`fam03-preparar` fija sin cálculo `datos/fam03/`. Construye el contexto S6
una vez (0,95 s) y no ejecuta ninguna búsqueda:
- `contexto_esperado.json`: identidad 496135b0… y despliegue cd87e715…;
- `plan_prod.json`: `plan_prod.construir(None, contexto_esperado,
  decision_q, decisiones)` con las decisiones del plan histórico. Su
  `plan_sha256` es 9a93f041…, frente a 244e443d… del histórico.

El plan se verifica con la rama de producción de
`corrida_paso4.verificar_plan`, reimplementada sin cambiar el criterio:
- huella del cuerpo;
- banderas oficiales en falso;
- D4 admitida;
- cuerpo igual al derivado.

Comparado con el histórico, es igual en las 136 tareas, en los límites, en
el calendario y en las decisiones. Solo difiere en:
- `contexto_esperado`, el de esta base;
- `evaluadores_ra/dependencias/sha256`, la copia pública. Su huella de origen
  es la del plan histórico;
- `plan_sha256`, que se deriva de los dos anteriores.

Decisiones conservadas tal cual:
- `decision_q = Q-CONTINUO-COTA-SUPERIOR-v2`;
- `QUIEBRES-D4` (0494f042…).

Ninguna se fabrica ni se modifica.

Entradas de PROD3 según F1:
- **Reutiliza el piloto y reutilizará la ejecución completa**: la lista
  instalada, las decisiones selladas, la línea base certificada (registro
  candidato v4 de lima1941, autenticado por su inventario), los módulos R-A
  ensayados y el núcleo, D7 y contratos de FAM01.
- **Resumen de detalle**: el plan efectivo tiene `resumen_q = null`, y la
  ruta ejecutada (`q_afirmacion`) no lo consume. Solo lo usaba `q_ambito`,
  que `main` no llama. Ni el piloto ni la ejecución completa necesitan un
  resumen de detalle.
- **Produce la ejecución completa**: los 136 árboles nuevos (documentos y
  filas de las 152 unidades, registro y dictamen por tarea).
- **Solo para comparar**: los árboles aceptados y el plan histórico. Durante
  el cálculo de los pilotos no se leyó ninguna referencia. La réplica de
  arnés (`--replica-arnes`) no forma parte de la receta.

## Comandos

Usan el Python de `.venv-fam01` con `-B -P -s -X utf8`, `PYTHONHASHSEED=0`,
`TZ=UTC` y las seis variables de hilos en 1:

```text
reproducir.py fam03-preparar  --salida salidas/fam03/preparar_03.json
reproducir.py fam03-listar    --salida salidas/fam03/listar_02.json
reproducir.py fam03-comprobar --salida salidas/fam03/comprobar_04.json
reproducir.py fam03-unidad    --tarea <PROD…-T…> [--tope 2400] --salida salidas/fam03/<ejecucion>/<tarea>
reproducir.py fam03-validar   --nueva <carpeta de fam03-unidad> --salida <carpeta nueva>
reproducir.py fam03-comparar  --tarea <PROD…-T…> --nueva <carpeta> --salida <archivo nuevo>.json
reproducir.py fam03-receta    --salida salidas/fam03/receta_02.json
```

- `fam03-preparar`: fija los datos de `datos/fam03`. No sobrescribe un dato
  distinto. Solo construye el contexto.
- `fam03-comprobar`: sin cálculo ni contexto. Comprueba:
  - las huellas de `fuentes_fam03.json`;
  - el plan, verificado y comparado con el histórico;
  - el contexto esperado;
  - la cobertura (unidades, tareas y árboles; árboles autenticados;
    miembros esperados; documento de referencia de su unidad y tarea;
    estados y D4);
  - los módulos R-A en sus tres lugares, el inventario anclado y el
    adaptador del plan;
  - los pilotos frente a la regla.
- `fam03-unidad`: una tarea del plan en una carpeta nueva, con los pasos de
  `tarea_prod.main`.
  - Se niega antes de crear nada si falta o cambió una dependencia.
  - Escribe el árbol de la tarea más `resultado.json`, `ejecucion.json`
    (vínculo, run_id y sus entradas, tiempos separados, entorno y lecturas)
    y `archivos_leidos.json`.
  - Exige la semilla.
- `fam03-validar`: revalidación sin cálculo de los bytes guardados en una
  carpeta nueva.
- `fam03-comparar`: comparación con el árbol aceptado de la tarea. Termina
  con 0 solo si la reproducción queda aceptada.
- `fam03-receta`: las 136 tareas con sus órdenes. No se ejecuta.

## Comparación (COMPARACION-FAM03-v1)

Se aplican los criterios del contrato de comparadores para F03-QUIEBRES y
F03-Q:
- **CR-HASH-CANONICO**: igualdad exacta del contenido científico;
- **CR-DISCRETOS**: estados, clasificación y D4 exactos, con precedencia;
  una coincidencia numérica no compensa un cambio de clasificación.

CR-OBJETO-OTRO-ENTORNO no se aplica, porque se usa el mismo entorno. Las
filas de árbol del contrato estaban sin comparador de tarea; este es el
comparador de la tarea.

Se compara cada miembro del árbol. Las exclusiones van por objeto y por
puntero exacto, nunca por nombre de clave. Todas quedan visibles en la
salida:
- **operativos**: son mediciones `time.time()` de `evaluadores_ra` y se
  muestran sin comparar.
  - En el documento de quiebre: `reloj/{inicio_busqueda_t,
    limite_efectivo_t, limite_global_t}`, `preparacion_s`, `busqueda_s` y
    `evaluaciones/*/{segundos, acumulado_s}`.
  - En el documento Q: `preparacion_s`, `rama_y_cota_s`, `por_contexto_s`,
    `Phi_estrella/segundos` y `codigo_universo_nudos/segundos`.
  - `reloj/tope_busqueda_s` y `reloj/limitada_por_global` son presupuesto y
    **sí se comparan**.
- **identidad**: contexto, despliegue, plan, dependencias R-A, encargo,
  productor, autoridad y ruta del paquete. Se comprueban contra las de cada
  lado: el vínculo nuevo es el de su ejecución, la referencia cita el plan
  histórico y las dependencias R-A guardan correspondencia de origen.
- **derivados**: huellas de filas, documentos y dictamen, y `run_id`.
  - Cada huella se recalcula en cada lado.
  - El `run_id` se recalcula con la fórmula de `paper2b.run` y las entradas
    de la ejecución. Con la huella histórica del contrato da el run_id de la
    referencia; solo cambia la huella del contrato público de FAM01.

No hay cambio de método, tolerancia, soporte ni criterio.

## Pilotos (cálculo autorizado)

Regla fijada antes de calcular (`datos/fam03/pilotos.json`): la primera
tarea de cada familia en el orden del plan. Las tareas de PROD1 y PROD2 se
intercalan, así que el primer PROD2 es T006. PROD1 y PROD2 recorren rutas
distintas (EQ y EQM), por eso hay un piloto de cada una. Una tarea PROD3 es
la unidad mínima separable: sus dos salidas comparten la caché de Φ*.

Cada piloto se lanzó solo, con el supervisor que termina el árbol de
procesos (límite externo de 600 s), en `salidas/fam03/pilotos_01/`. El reloj
interno usa el tope del plan (RELOJ-PILOTO-v1).

| Piloto | Unidades | Pared (supervisor) | Cálculo | Contexto | Validación | Estado validado | Comparación |
|---|---|---|---|---|---|---|---|
| PROD1-T001 (eje a, inferior) | 1 | 18,6 s | 16,73 s | 0,9 s | 0,01 s | `completa_validada` (`theoretical_boundary_no_breakdown`, A_GT1_OPEN) | aceptada: 0 científicas; 10 operativas, 11 de identidad y 5 derivadas, todas recomprobadas |
| PROD2-T006 (eta_w, superior) | 1 | 9,6 s | 7,75 s | 1,0 s | 0,01 s | `incompleta_validada`, declarada D4 (igual que la referencia) | aceptada: 0 científicas; 10, 11 y 5 |
| PROD3-T121 (global y MEX) | 2 | 12,9 s | 11,07 s | 0,9 s | 0,03 s | ambas `completa_validada` | aceptada: 0 científicas; 9, 17 y 9 |

- **Lecturas reales** (rastro de aperturas), iguales en los tres:
  - 331 archivos del paquete, 110 de ellos de `.venv-fam01`;
  - 61 aperturas del intérprete;
  - **0 fuera del paquete y del intérprete, 0 sin manifiesto y 0
    referencias leídas** durante el cálculo.
- **Entorno**: perfil conforme. F2 se informa como equivalente, pero no es
  requisito de FAM03. Fuera de la biblioteca estándar solo se carga numpy
  2.0.2.
- **Presupuestos sin cambios**: 420 s por búsqueda, 120 s por evaluación,
  300 s por rama y cota Q, tope de tarea 2400 s y margen de 180 s. El
  `limitada_por_global` nuevo es igual al histórico.
- **Tiempos operativos frente a la referencia** (no se usan para estimar):
  - T001: `busqueda_s` 16,4 frente a 16,2;
  - T006: evaluaciones acumuladas 7,0 frente a 7,1 s;
  - T121: Φ* 4,4 frente a 9,4 s.

  La pared de la producción fue 101,0 s en T001 (84,0 s de contexto) y
  182,2 s en T121 (158,3 s de contexto). La diferencia está casi toda en la
  construcción del contexto; aquí no se analiza su causa.
- **Fallo de interfaz** corregido en la sesión: `calendario_paso4` importa
  `rebalanceo_paso4`, que faltaba (`preparar_01`, antes de calcular). Se
  extrajo con su huella y solo se repitió `fam03-preparar`.
- Las comparaciones vigentes son `*.comparacion_02.json`, con el código
  final. Las `_01` dieron el mismo resultado.

## Controles (`local/pruebas_fam03.py`, sin cálculo científico)

`salidas/fam03/pruebas_02.json`: 17/17 conformes (10,7 s). Los casos:
- **Control positivo**: el piloto PROD1 frente a su árbol queda aceptado.
- **Resultado científico alterado** (1 ulp, con las huellas recalculadas
  para que solo cambie la ciencia):
  - PROD1, `reached_expansion_factor` en la fila: la comparación lo rechaza
    solo por `DIFERENCIA_CIENTIFICA`. La revalidación lo admite, porque la
    regla instalada solo liga a la evidencia el estado, el crítico y los
    testigos; se informa como tal.
  - PROD3, `m_Q_critical`: la revalidación lo rechaza
    (`Q_DESLIGADO_DE_LA_EVIDENCIA`, porque la fila se recalcula desde la
    evidencia), y la comparación también.
- **Referencia de otra unidad**:
  - el piloto T001 frente al árbol de T002 se rechaza
    (`SALIDA_DE_OTRA_TAREA` y miembros ausentes);
  - un miembro de referencia sustituido por el de otra tarea da
    `MIEMBRO_DE_REFERENCIA_ALTERADO`;
  - un manifiesto sustituido da `ARBOL_DE_REFERENCIA_ALTERADO`.
- **Validación ausente**:
  - sin registro ni dictamen: no se acepta (miembros ausentes, clasificación
    distinta y validación ausente);
  - con la ejecución marcada sin éxito: no se acepta.
- **Otra carpeta** (copia sin entorno ni salidas, fuera del paquete, con el
  mismo intérprete):
  - `fam03-comprobar` cumple, con el área R-A resuelta dentro de la copia;
  - la revalidación del piloto PROD1 cumple y su comparación queda
    aceptada.
- **Dependencia ausente o alterada** (en la copia):
  - un módulo portado retirado aparece como ausente en `fam03-comprobar`;
  - `fam03-unidad` se niega antes de calcular, sin crear la carpeta;
  - un módulo alterado en su entrega lo rechaza el importador instalado al
    cargarse (`PUERTO_O_FUENTE_ALTERADO`), sin pasar por
    `fuentes_fam03.json`;
  - restaurado, carga dentro de la copia.

`pruebas_01` dio 16/17. El caso no conforme detectó un defecto:
`fam03-comprobar` se detenía con `FileNotFoundError` en vez de informar la
ausencia. Se corrigió y se repitieron solo `comprobar`, las comparaciones y
los controles.

**Regresión** del código compartido (`reproducir.py`), sin recalcular:
- `revisar` conforme;
- `fam01-comprobar` cumple (6,4 s; perfil y F2);
- `fam02-comprobar` cumple (4,7 s);
- salidas en `salidas/fam03/regresion_*.json`.

## Adaptaciones de interfaz

No cambian fórmulas, tolerancias, topes, presupuestos ni criterios:
- **Contexto**: `fam01.Contexto` con `run_class = paso4_operativo_s6` (el de
  la producción, que registra cada documento histórico) y etiqueta NO
  OFICIAL. El despliegue nuevo no tiene rutas ni autor, y tampoco acto
  (`ancla = null`).
- **Plan limpio**: derivado por `plan_prod.construir` y comparado con el
  histórico, como se describe arriba.
- **CO-CANON-v1**: de `corrida_paso4`, `tarea_prod` solo usa `canon`,
  `REGISTRO` y `DICTAMEN`. Se exponen con la misma serialización.
- **RA-AREA-v1**: el área R-A, relativa en la copia pública, se resuelve en
  `nucleo_s6/raiz` al cargar.
- **RAIZ-CONTRATOS-v1**: `validador_prod.raiz_contratos` busca la raíz entre
  los padres de la instalación; aquí es la hermana `nucleo_s6/raiz`.
- **RELOJ-PILOTO-v1**: el reloj interno usa el tope del plan (2400 s) y el
  límite externo lo pone el supervisor. Con un tope interno de 600 s, el
  límite global (inicio + 600 − 180) acortaría el presupuesto de 420 s por
  búsqueda y cambiaría `limitada_por_global`. Por eso no se reduce.

## Límites

- Solo hay 3 tareas calculadas, 4 de las 152 unidades: 1 completa de
  quiebre, 1 declarada D4 y 2 Q completas. Las otras 133 tareas no tienen
  cálculo en esta base.
- El registro nuevo guarda en `generado_por/paquete` la ruta absoluta de la
  salida, que escribe el código instalado como en FAM01. Está separada como
  identidad y hay que sanearla antes del paquete público, igual que los
  registros del supervisor.
- `encargo_procedencia_sha256` es nulo, porque no hay acto de autorización;
  en la referencia tiene valor. Está separado como identidad.
- El traslado se probó en esta máquina con el mismo intérprete. El
  aislamiento efectivo queda para 2.4.2.
- F2 no se extiende a FAM03. La regla de FAM03 no la necesita.

## Receta completa (preparada, no ejecutada)

`salidas/fam03/receta_01.json`:
- las 136 tareas en el orden del plan, cada una con su orden de cálculo y de
  comparación;
- una tarea a la vez, con un límite externo de 2400 s por tarea y el mismo
  supervisor;
- sin dependencias entre tareas de FAM03.

La conciliación PROD4 es otra familia. No se promete duración total: los
pilotos no la representan, y las tareas D4 y las de búsqueda larga pueden
agotar sus presupuestos.

## Siguiente trabajo

- La ejecución de las 136 tareas pertenece al Paso 3 y requiere su
  autorización.
- El aislamiento efectivo de FAM03 queda para 2.4.2.
- Antes del paquete público, sanear las rutas absolutas que escriben el
  registro productivo y el supervisor en las salidas.
- FAM04 no se abre sin encargo.
