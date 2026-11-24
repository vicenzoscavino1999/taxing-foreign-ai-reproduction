# Plan de reproducción integrado — propuesta para revisión

**CANDIDATO PARA REVISIÓN, SIN ACTIVACIÓN.** Especifica la ruta posterior e incluye una primera implementación contractual aislada. S1 MEX ya está incorporado y verificado; este candidato S2 no autoriza ejecución productiva ni revalida A/A-ter.

**Selección comunicada por el autor:** A1–A7 y C-A2 ya elegidas para formalización e implementación candidata. Perú principal; CHL/COL/MEX comparadores; precisión documentada como vía principal y E1/E2 condicionados; revisión completa y versionada D2 2015–2023; D6 exclusivamente 2023; rho≤1, soportes, resultados y limitaciones auditados. La elección no equivale a firma, incorporación, congelamiento, admisión de fuentes reales ni autorización de corrida. C-A2 se incorpora a este candidato según `review/CONTINGENCIA_A2.md` y el catálogo único CA2-2; sus validadores de metadatos se conservan y se amplían con lectores institucionales candidatos acotados; evaluación numérica y admisión siguen pendientes.

## RE-01. Autoridad, herencia y separación de estados

S1 fue emitido el 19/09/2026: paquete `3bac05fd56b710899c1822aebb125435bacf65d24cfa917d646702ae6babd439`, manifiesto `b7ab84b3589d5f5e3b0c47a2deeb1c8742d4102208df7f5cd230b1dd9f07cc96`, cadena de 45 paquetes, 11 suites/1030 pruebas efectivas y consumidor estricto V2 aceptado. El alcance sigue siendo MEX histórico, sin elegibilidad cuantitativa. v49 conserva bytes, autor y fecha aprobados; no es un borrador pendiente. S2 se integra y prueba sobre una copia de ese S1 real. La emisión aislada usa consentimiento ficticio de fixture; en el original no se emite S2 ni se atribuye consentimiento nuevo. Los planes anteriores quedan como historia; la futura selección S2 identifica exactamente estos tres planes.

| Cláusula | Antecedente | Modificación propuesta / motivo | Decisión |
|---|---|---|---|
| RE-02 | v49 §§2–8; v48 restauración de pins | Separar incorporación MEX de posteriores sucesiones integradas | A1 |
| RE-03 | v46 entorno y contratos A/A-ter | Programar verificación canónica pendiente sin afirmar que ocurrió | A7 |
| RE-04 | D1–D6/PRE-D7-A | Ordenar recepción, revisiones, compatibilidad y construcción | A2/A3/A6 |
| RE-05 | B/D8 previstos; diseño §§19–20 | Completar validaciones por contrato y distinguir pruebas sintéticas de resultados | A5/A7 |
| RE-06 | Diseño §8; paquetes de reproducción | Definir artefactos finales con llaves, hashes y límites de divulgación | A6/A7 |
| RE-07 | Compuertas de fases y publicación | Separar plan cerrado, implementación validada y corrida habilitada | A7 |
| RE-08 | Regla de defecto material | Conservación, incidencias y alcance de esta entrega | A7 |

Este borrador consume DI para semántica/método y DB para esquemas/elegibilidad. No redefine fórmulas tributarias, soportes o precision. Toda selección activa debe identificar exactamente un plan por función; los antecedentes históricos no compiten como planes activos.

Estado actual: D2 publicado; D3/D4/D5 publicados con limitaciones explícitas; D6 con contrato, código, staging/rechazos y sin producto habilitante; PRE-D7-A implementado en preparador/tests y especificación, sin registro productivo D7; B/D8 con contratos completos propuestos en esta revisión e implementación integrada pendiente; A/A-ter con historia de validación preservada y comprobación canónica local pendiente. Las 11 suites y 1030 pruebas de S1 corresponden a su emisión real documentada en s1/cierre.json; no son una corrida científica nacional.

## RE-02. Sucesiones mínimas y compatibilidad MEX

**S1 — completado.** S1 fue emitido el 19/09/2026: paquete `3bac05fd56b710899c1822aebb125435bacf65d24cfa917d646702ae6babd439`, manifiesto `b7ab84b3589d5f5e3b0c47a2deeb1c8742d4102208df7f5cd230b1dd9f07cc96`, cadena de 45 paquetes, 11 suites/1030 pruebas efectivas y consumidor estricto V2 aceptado. El alcance sigue siendo MEX histórico, sin elegibilidad cuantitativa. v49 conserva bytes, autor y fecha aprobados; no es un borrador pendiente. S2 se integra y prueba sobre una copia de ese S1 real. La emisión aislada usa consentimiento ficticio de fixture; en el original no se emite S2 ni se atribuye consentimiento nuevo.

**S2 — candidato integrado.** La presente entrega prepara los tres planes completos, protocolo, contratos, compatibilidad específica y lectores/validadores. `validadores/s2_compat.py` verifica la integridad normativa, llama al contexto histórico estricto de V2 contra S1 autenticado y construye/comprueba una propuesta aislada únicamente con consentimiento nuevo por hash externo. Los tests positivos usan aprobaciones ficticias explícitas en temporales; el candidato real carece de aprobación y debe rechazar activación.

La política vincula exactamente D31/D39, los dos mappings, V2 y payload MEX. PER mantiene su autoridad candidata independiente. El publicador, despacho D6, selección, compuerta y recuperación están implementados en la copia aislada; sus pruebas y emisión CLI constan en el expediente. Solo la aprobación real y la incorporación al original están pendientes.

**S3 y activaciones posteriores, cuando sean necesarias.** Una vez construida la revisión D2, la autoridad del consumidor D6 debe fijar el nuevo producto/puntero y compatibilidad de reuso D3–D5. Si S2 ocurre antes de existir esos bytes, se requiere una sucesión posterior para fijarlos; no se predeclaran hashes desconocidos ni se promete cerrar toda ejecución con dos paquetes. Si se producen primero los datos en staging bajo un contrato previo aprobado y S2 puede fijar sus bytes verificados, se pueden consolidar actos documentales compatibles, siempre respetando el permiso previo de construcción. La ruta recomendada no fusiona S1 con nuevas elecciones científicas.

Tras publicar D6/D7, toda autoridad de B/D8 que consuma esos nuevos productos también necesita selección y pines válidos. Cada paquete posterior que consuma V2 requiere la vía explícita que lo cubra; no se propaga por herencia tácita. Se conserva la historia y no se redatan aprobaciones para pasar la regla temporal.

## RE-03. Entorno y Paquete A/A-ter

El contrato canónico heredado fija CPython **3.12.4**, Windows 11 build 22621 AMD64, NumPy 2.0.2, OpenBLAS 0.3.27 ILP64 y pins/hashes de `requirements.lock`, con runtime de NumPy y unittest conforme al entorno aprobado. Se preservan asimismo las especificaciones de pip y ruedas del manifiesto de entorno. No instalar el proyecto por una vía que cambie dependencias fuera del lock ni añadir SciPy/pandas/contourpy al runtime de B por conveniencia sin sucesión autorizada.

Esta ronda utiliza exclusivamente Python 3.12.10 para verificaciones documentales y contractuales; **no revalidó A/A-ter**. Su existencia no satisface el requisito 3.12.4. Los diez reportes científicos históricos y sus hashes se conservan como historia, no se regeneran para hacerlos coincidir con un entorno distinto.

Elección A7 comunicada: preparar un entorno separado 3.12.4 con ruedas autenticadas, registrar ejecutable/versión/arquitectura/BLAS/lock/locale y revalidar los contratos autorizados A y A-ter en una ejecución futura específicamente aprobada. Comparar semántica y bytes según el contrato, registrando diferencias ambientales y sin sobrescribir reportes históricos. Si no se puede reproducir ese entorno, alternativa: aprobar explícitamente un nuevo entorno canónico y su estudio de equivalencia; no llamarlo revalidación en el entorno original.

Los cambios de B no heredan automáticamente epsilon_num=1e−12 de un fixture histórico. T2 aplicable a nuevos problemas/regímenes se debe medir como exige DI-08. T1 permanece separado.

## RE-04. Orden por dependencias

| Etapa futura | Entradas y precondición | Trabajo | Salida verificable |
|---|---|---|---|
| 1. S1 completado | v49 aprobado intacto; cierre.json | Incorporación y compuerta efectivamente ejecutadas | Paquete 3bac05…; 45 paquetes; V2 estricto; cuantitativo false |
| 2. Formalización de elecciones | A1–A7 y C-A2 ya elegidas; DI/DB/RE | Revisar los bytes candidatos y formalizar S2 con compatibilidad propia | Autoridad posterior de planes y contratos, incluidos CA2-2; aún sin resultados |
| 3. Contratos y lectores | Selección A1–A7 y autorización de esta ronda | Primera biblioteca aislada de integridad, claves, referencias y definiciones; ampliar consumidores después | Publicador y consumo S2 probados en aislamiento; autoridad real y productores científicos siguen pendientes |
| 4. Recepción/adquisición | DB-02 aprobado | Incorporar fuentes oficiales/adjuntos y evidencia de precisión/crosswalk | Catálogo, recibos y snapshots autenticados, sin PII pública |
| 5. Revisión D2 | Snapshot contable completo por país/año, precisión D2 para E0/E3 o evidencia condicional CA2-2 para E1/E2; sensibilidad 2015–2023 sin requerimiento D6 histórico | Construir cuenta completa, tabla de revisión e identidad; versionar | D2 nuevo con gates, preservando output anterior |
| 6. Reuso D3–D5 | Versiones históricas, nuevos planes/D2 | Auditar dependencias y emitir certificado de compatibilidad | Valores conservados o reconstrucción motivada, nunca automática |
| 7. Activación de entradas | Nuevos bytes y autoridad posterior necesaria | Fijar D2, contratos y consumidores, comprobar V2 | Contexto D6 válido sin editar pre_network histórico |
| 8. D6 | Snapshots completos de 2023 de los miembros de cada caso preregistrado y contrato nuevo aprobado | Validar observaciones, intervalos y reconciliación; construir 3 componentes/país | Producto D6 estricto de la aplicación PER (3/3) o producto condicional diferenciado por caso preregistrado con tres componentes por miembro; ambos requieren validación económica y autoridad |
| 9. D7 | D6 elegible, registry/support_set aprobados; D3–D5 compatibles | Construir fuentes/soportes/escenarios, validar PK/FK y admisibilidad | Producto D7 versionado listo para B |
| 10. B y auditoría previa D8 | Entorno canónico, A/A-ter y D7; tests sintéticos B | Validar frontera, integración, solver, requerimiento e inversiones; auditar insumos | Reportes de validación y readiness completo |
| 11. Freeze-run y corrida | Todo gate previo aprobado y conjunto congelado | Una sola corrida integral sobre soportes reales | Artefactos RE-06 y auditoría posterior |
| 12. Reproducción y entrega | Artefactos finales y manifest | Verificar reconstrucción, cobertura y cifras exportadas | Paquete reproducible, con límites y sin PII |

Los lectores y pruebas de metadatos ya pueden avanzar por autorización de esta ronda. Otros frentes independientes, bajo autorización futura apropiada, son: precisiones/crosswalk de cada país; especificación de registry; diseño y pruebas sintéticas de B; preparación del entorno 3.12.4; lectura de A6; verificación jurídica adicional opcional. No pueden adelantarse D6 productivo sin autoridad, D7 nacional sin gate conjunto ni resultados reales antes de freeze-run. Una dependencia externa pendiente no impide cerrar fórmulas/esquemas o preparar pruebas.

## RE-05. Contratos y validación de B/D8

Paquete B consumirá un manifiesto D7 y sus árboles fijados, esquema de soportes, teoría/protocolo y grilla externa autenticados, mapa de disponibilidad y configuración numérica validada. No descubrirá automáticamente «el archivo más reciente». Cada ejecución tendrá rutas y hashes explícitos y un manifest de configuración inmutable.

La implementación debe dividirse por fronteras: normalización/admisibilidad → decisiones y bases → frontera/captura → lambda → requerimiento → confrontación → raíces/inversiones → auditoría/exportación. D8 previo verifica el grafo de entradas y validaciones; D8 posterior comprueba salidas. No se exige un resultado nacional inexistente para preparar el auditor.

| Bloque | Evidencia de aceptación futura |
|---|---|
| Autoridad | Negativos por hash alterado, lineage incompleto, fecha inválida, sucesor fuera del alcance y plan activo ambiguo; positivo con el paquete realmente aprobado |
| Datos | Fixtures de signos, ceros documentados/no exactos, redondeo asimétrico, unidades, netos brutos equivalentes, cancelación de primitivas y discrepancia de vintage |
| D2/reuso | Identidad completa, remuneración doméstica correcta, manifest legado preservado, invalidación del consumidor afectado y reuso exacto de los no afectados |
| Registry | Campos obligatorios, unidades y normalización; parámetro oculto, rango inválido, FK inexistente, dependencia circular y centro prohibido deben fallar |
| Teoría | Particiones, empates, E0, G/N, incidencia exacta, límites eta_d→0 y tau_f→0, independencia de esquina respecto eta_f, restricciones S4/S6/S18 |
| B numérico | Problemas analíticos y sintéticos, laterales/kinks, múltiples raíces/tangencias, supremum no alcanzado, refinamiento de malla y T2 medido <1e−4 |
| Puente externo | Reconstrucción Q a T1, Ffix una vez, dos cotas, D_ME y condición de eliminación del índice; escala local independiente |
| D8/exportación | Cobertura completa de llaves, ningún readiness=false exportado, casos jurídicos separados, estabilidad de cifras publicadas y trazabilidad de cada claim |
| Publicación | Relocalización, reproducción desde manifest, verificación de tipos/hash, promoción fallida sin cambio de activo y conservación histórica |

Las pruebas deberán ser independientes de los resultados deseados. No se construyen expected leyendo la salida bajo prueba ni se ajustan soportes para que una prueba científica pase. La suite auditada de MEX se toma como antecedente; solo se vuelve a ejecutar lo exigido por la compuerta de la incorporación efectiva o por cambios concretos. La compuerta exterior S2 ejecuta las once suites históricas junto con la suite contractual y las pruebas de publicación. Ocurre en la copia aislada y no reemite S1 operativo.

## RE-06. Contratos finales de B y D8 y artefactos de ejecución

Esta sección sustituye RE-06 anterior en su totalidad. `contratos/catalogo_contratos.json` es la especificación estructurada completa; su render legible y correspondencia histórica forman parte de los planes, no son tareas diferidas a implementación. Las listas siguientes son exactas. Todos los campos,PK,FK,dominios,nulos y reglas condicionales están cerrados en ese catálogo propuesto. Una divergencia entre render y JSON bloquea aprobación/publicación.

### B

- `B/omega.csv`
- `B/omega_values.csv`
- `B/cell_context.csv`
- `B/frontier_context.csv`
- `B/frontier_result.csv`
- `B/capture_ceiling_result.csv`
- `B/sup_witness.csv`
- `B/lambda_pi_envelope.csv`
- `B/confrontation_result.csv`
- `B/inversion_result.csv`
- `B/inversion_targets.csv`
- `B/r1_summary.csv`
- `B/r1_components.csv`
- `B/r1_vertices.csv`
- `B/r1_edges.csv`
- `B/r1_rejected_crossings.csv`
- `B/r2_sections.csv`
- `B/r2_roots.csv`
- `B/claims.csv`
- `B/support_breakdown_result.csv`
- `B/breakdown_witnesses.csv`
- `B/external_requirement_sensitivity_result.csv`
- `B/convergence_result.csv`
- `B/computation_coverage.csv`
- `B/witness_sets.csv`
- `B/scalar_inversion_roots.csv`
- `B/scalar_inversion_intervals.csv`
- `B/numerical_evidence.csv`
- `B/run_manifest.json`
- `B/b_manifest.json`
- `B/active_product.json`
- `B/promotion_receipt.json`

### D8_pre

- `D8_pre/input_audit_report.csv`
- `D8_pre/double_counting_audit.csv`
- `D8_pre/admissibility_report.csv`
- `D8_pre/evidence_records.csv`
- `D8_pre/d8_pre_phase_report.json`
- `D8_pre/d8_pre_manifest.json`
- `D8_pre/active_product.json`
- `D8_pre/promotion_receipt.json`

### D8_post

- `D8_post/d8_claim_audit.csv`
- `D8_post/d8_coverage.csv`
- `D8_post/d8_post_audit.csv`
- `D8_post/result_references.csv`
- `D8_post/d8_post_evidence_records.csv`
- `D8_post/d8_post_phase_report.json`
- `D8_post/d8_post_manifest.json`
- `D8_post/active_product.json`
- `D8_post/promotion_receipt.json`

Las rutas son relativas al producto de cada familia. active_product.json y promotion_receipt.json están fuera del árbol inmutable; no se cuentan como salidas científicas dentro de ese árbol. El manifest enumera todos los demás archivos exactos, se autentica por separado y no se hashea a sí mismo. Las fuentes externas y la preparación PRE-D7-A se referencian por hash; no se incluyen cuerpos de correos ni microdatos.

La llave científica heredada está normalizada en run_manifest,cell_context y frontier_context. run_manifest lleva conjunto de casos jurídicos y desglose; cada fila recupera un caso singular mediante FK. C2 y lambda usados por G deben coincidir en omega completo y país/contexto, aunque sus unidades de cálculo compartan caches. Ningún extremo de un estado se combina con requerimiento de otro.

R1 se representa por resumen,componentes,vértices2D y aristas, con ramas/lados,residuos,error geométrico,intersecciones y rechazos. R2 tiene cuatro resúmenes por celda y cero o más raíces identificadas por sección e índice, incluidas tangencias. Inversiones algebraicas conservan todos sus valores requeridos y banderas; las endógenas tienen hijos para soluciones múltiples. No se sustituye una curva por root_low/root_high.

Los cuatro bloques de robustez y la sensibilidad reducida Q tienen tablas/estados distintos. La frontera rho=1 agrega estado y motivo específicos según DI-07.R, sin prometer robustez más allá. Convergencia tiene una fila por cifra/raíz/geometría/claim, y computation_coverage conserva dominio pendiente y agotamiento de recursos.

D8_pre verifica entradas y validación sintética B; D8_post verifica B oficial y claims, sin depender circularmente de sí mismo ni modificar D8_pre. Todas las afirmaciones tienen referencias exactas a archivo/PK/hash y cadenas de evidencia. Solo una ejecución completa, convergente y autorizada habilita exportación. Los schemas no son productores; no se ejecuta nada de esto en esta ronda.

La estrategia de cálculo,proyecciones de reutilización,reducciones analíticas condicionales,refinamiento y protocolo futuro de recursos están en `review/ESTRATEGIA_DE_CALCULO.md`, incorporado como parte de RE-04–07. No se promete tiempo ni se degrada el método para que la ejecución quepa.

### Ajuste contractual consolidado — 2026-09-12

Estado común, cálculo estructural y contexto macro nacional se distinguen según contratos/CLAVES_DE_CALCULO.json y K1–K5 de su explicación. Omega no contiene clave macro ni una clave estructural única; frontier_context conserva la estructural por dominio/diseño/menú. lambda_pi_envelope lleva macro_key_sha256 y payload con país,estado nacional,dependencias D2/D6/precisión/dominio conjunto y huellas técnicas. cell_context incorpora estado nacional y clave macro esperada; se rechaza cualquier enlace de país/omega/contexto incompatible. No se duplican evaluaciones estructurales por cambiar un snapshot nacional.

C_2 tiene formula_id=C_2 registrado como numerical_operator: supremo de R/B_pot en el dominio fiscal admisible. R es función declarada con sus dependencias. D7 valida definiciones sin exigir resultados B; B produce capture_ceiling_result, conserva disponibilidad,supremo no alcanzado,laterales,errores y testigos. Declaración de destino no es dependencia circular ni forma cerrada nueva.

contratos/contract_manifest.json usa exclusivamente rutas relativas a raíz de esta entrega; incluye todos los contratos/anexos,estos tres planes y la única review/ESTRATEGIA_DE_CALCULO.md normativa. Se excluye a sí mismo. contract_sha256 es el hash de sus bytes exactos; una aprobación futura debe cubrir ese hash y todas sus entradas. Las correcciones contractuales auditadas se preservan. A1–A7 tienen selección comunicada; sus actos formales siguen pendientes. Los validadores aislados de esta entrega comprueban metadatos, sin habilitar ejecución.

## RE-07. Tres cierres diferentes

**Cierre de planes:** A1–A7 y C-A2 tienen selección comunicada. Se entrega su formalización candidata con reglas de metadatos implementadas; revisión e incorporación formal siguen pendientes. No queda una elección C-A2 por solicitar. La vía estricta conserva sus gates y la condicional tiene requisitos propios de completitud/evidencia. El revisor comprueba correspondencia DI/DB/RE, catálogo y código; esta revisión no certifica precisión, resultados ni entorno canónico.

**Cierre de implementación:** contratos/código, entorno, suites pertinentes y validaciones sintéticas aceptados; faltantes de fuentes no se reemplazan con números sintéticos en el producto nacional. El código aprobado y sus entradas exactas quedan autenticados.

**Habilitación de corrida:** recepción/procedencia y evidencia completas según vía; D2 revisado y compatible; D6 estricto 3/3 de la aplicación PER para E0/E3, o los miembros de cada caso preregistrado con tres componentes validados bajo el contrato condicional para E1/E2; D7 completo; B validado; D8 previo pasa; selección activa, consumidor versionado y V2 válidos; congelamiento conjunto y autorización real. La vía condicional no reclama precisión institucional. Solo entonces freeze-run y una corrida integral. La corrida y sus exportaciones nunca se anuncian como realizadas al revisar documentos.

## RE-08. Preservación, fallos y límite de esta ronda

Conservar staging, rechazos, journals, bundles, entornos, reportes y versiones. Un fallo produce evidencia y deja el puntero anterior; no se remedia editando en sitio un manifiesto. Modificaciones después del congelamiento solo por defecto material verificable según diseño §19.5, con nueva versión y evaluación de consumidores.

No se envían solicitudes externas automáticamente. Si precisión/crosswalk sigue faltando, se prepara una petición específica en una ronda autorizada, dirigida solo a ese dato. Esta entrega completa la integración documental S2 y su emisión de prueba aislada. La incorporación S2 real, construcción de datos y resultados requieren sus autorizaciones posteriores.

## RE-09. Implementación aislada de esta ronda

`validadores/core.py` y su CLI reutilizan y refactorizan verificaciones de la entrega contractual anterior. Consumen el mismo catálogo, fórmulas y esquemas de claves, preservados byte a byte. Implementan integridad del manifiesto normativo, JSON/CSV y tipos estructurales, PK/UK/FK, claves y proyecciones, contexto país/omega/diseño/menú, resolución de referencias por bytes/PK/unidad, objetos técnicos por roles y grafo de declaraciones C_2/R sin filas de resultados B. Alcance exacto y partes pendientes: `review/COBERTURA_IMPLEMENTACION.md`.

La CLI es de solo lectura y exige el hash esperado del manifiesto. Las pruebas usan metadatos ficticios y temporales dentro de comprobaciones/tmp; no llaman synthetic del proyecto ni evalúan R,C_2,lambda o G. Su PASS no es aprobación de autoridad, exactitud de fuentes, solver validado, benchmark o producto D7/B/D8. La contingencia no está implementada como admisión: su aprobación y traducción a contratos versionados serían pasos posteriores expresos.

La ruta operativa única está en `review/RUTA_DE_CIERRE.md`: revisión de la implementación candidata C-A2 ya elegida; S1 MEX acotada ya cerrada; integración S2 demostrada en aislamiento, pendiente de aprobación e incorporación; incorporación versionada de datos y desarrollo restante; validación del entorno, métodos y recursos; congelamiento y corrida posterior. Las respuestas tardías se tramitan según CONTINGENCIA_A2 §6 y CA2-20, sin editar antecedentes ni elegir la revisión favorable.



## RE-10. Reproducción del candidato C-A2

El runtime de esta ronda es `tmp/venv-authoritative-new-laptop/Scripts/python.exe`, Python 3.12.10 documental. Bytecode desactivado; temporales en `comprobaciones/tmp`. No se ejecutan synthetic, TST, A/A-ter, freeze-run, run ni el modelo. Los comandos, logs y hashes de bytes efectivamente probados constan en comprobaciones/.

El manifiesto normativo autentica todos los archivos de contratos salvo sí mismo, los tres planes, la estrategia y el anexo C-A2. Su número de entradas responde a esas superficies, sin mantener artificialmente las 14 anteriores. La huella esperada se proporciona desde `review/anclas_externas.json`; el código y tests están además en el inventario final independiente. No hay hash del manifiesto dentro de sus propios documentos normativos.

Se repiten las 77 pruebas anteriores sin editar sus métodos; se preserva la adaptación histórica de identidad del catálogo y los bytes de fórmulas y claves. El fixture C-A2 incorpora los campos de relación, los enlaces explícitos y common_conflicts exigidos por CA2-2. Las ocho pruebas de desbordamiento JSON permanecen intactas. Las nuevas pruebas usan archivos inventados temporales y ejercitan admisibilidad, alcance, precisión, revisiones, denominadores y preservación de evidencia. Ningún PASS equivale a validación de robustez numérica, extremos, convergencia o canon 3.12.4.

## Corrección CA2-2: requisitos de evidencia y sucesión exacta

C-A2 sigue elegida y sin activación. Se distingue integridad de registros, evidencia común y evidencia adicional por escenario. Todos los registros presentes se autentican por archivo/hash/scope y estructura; sus resultados se conservan en evidence_outcomes. La precisión desconocida no bloquea E1/E2 por sí sola, aunque los mismos vectores también alimenten E0/E3 pendientes. E0/E3 mantienen la regla aplicable; E2 mantiene comparabilidad de las familias revisadas. Los cinco roles comunes siguen siendo indispensables. common_conflicts comunica contradicciones comunes extraídas por el adaptador, incluso si aparecen en un documento de precisión: bloquean todas las vías afectadas. No se duplican vectores ni se eliminan registros desfavorables para obtener pase.

El catálogo CA2-2 define relación initial, successor o independent. Initial se admite solo en ámbito nuevo (rol, familia, país, año) y es único; successor exige predecessor_id explícito, ámbito compatible y fecha estrictamente posterior. Independent requiere referencias explícitas y prueba por archivo/hash, contrastada por adaptador confiable, que vincule el nuevo artefacto con hashes de los antecedentes; una etiqueta no basta. En transición debe cubrir todos los antecedentes de su ámbito en el bundle anterior. Una evidencia independiente descubierta después puede tener fecha anterior si su independencia está acreditada; no se impone cronología de sucesión a esa raíz.

Se preservan todas las filas y el hash externo del bundle anterior. IDs nuevos o predecesor nulo no evaden el ámbito previo. Se rechazan ciclos, referencias incompatibles, sustituciones y borrados. Los instantes se comparan en UTC como racionales exactos, conservando fracciones incluso inferiores al microsegundo, sin float. Fechas inválidas, nulas o sin zona producen ContractError. La función temporal se adapta del helper MEX auditado, sin importar ni ejecutar maquinaria MEX.

Estas reglas no acreditan resultados ni admisión. La presente entrega añade lectores institucionales acotados y pruebas con bytes reales en solo lectura, además de fixtures aisladas. La independencia documental no se presume: el adaptador específico debe aportar su prueba autenticada cuando se use esa relación; la cadena INEI se trata como sucesión. D2 2015–2023, D6 2023, dominio de datos de cuatro países con consumo por caso preregistrado, denominadores, soportes y límites numéricos permanecen intactos.


## Antecedente S1 cerrado

La preparación S1 descrita en entregas anteriores quedó superada por la emisión real del 19/09/2026 identificada en RE-01. Sus plantillas no se reutilizan ni se reabre ese acto. v49, recibos y cadena originales permanecen intactos.

## Integración S2 de 19/09/2026 — cláusula coordinada

S1 fue emitido el 19/09/2026: paquete `3bac05fd56b710899c1822aebb125435bacf65d24cfa917d646702ae6babd439`, manifiesto `b7ab84b3589d5f5e3b0c47a2deeb1c8742d4102208df7f5cd230b1dd9f07cc96`, cadena de 45 paquetes, 11 suites/1030 pruebas efectivas y consumidor estricto V2 aceptado. El alcance sigue siendo MEX histórico, sin elegibilidad cuantitativa. v49 conserva bytes, autor y fecha aprobados; no es un borrador pendiente. S2 se integra y prueba sobre una copia de ese S1 real. La emisión aislada usa consentimiento ficticio de fixture; en el original no se emite S2 ni se atribuye consentimiento nuevo.

El catálogo CA2-2, sus 60 tablas, 16 contratos JSON, fórmulas y claves estrictas se conservan byte a byte. Los anexos `contratos/EXTENSIONES_S2.md`, `contratos/EVIDENCIA_INSTITUCIONAL_S2.md`, `contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md` y `contratos/AUTORIDAD_PER_CANDIDATA.json` forman parte del nuevo manifiesto normativo. La evidencia no es admisión; los lectores candidatos no son productores D2/D6; una aprobación documental S2 tampoco autoriza correr el modelo.

La compatibilidad propia conserva una política candidata sin aprobación interna y exige un recibo S2 separado, anclado externamente junto con la identidad esperada del autor. El publicador `herramientas/congelamiento/s2_publicador.py`, integrado al CLI `congelar.py`, prepara el manifiesto completo heredando los campos y pines S1 y sustituyendo únicamente los metadatos de la sucesión S2. Selecciona exactamente estos tres planes activos; los planes anteriores conservan rol histórico. El consumidor D6 despacha S2 a la verificación estricta de archivos instalados, recibo, manifiesto, selección y cadena. La integración técnica se demuestra exclusivamente en aislamiento mediante CLI y compuerta exterior real de once suites históricas más descubrimiento S2. La aprobación real e incorporación operativa permanecen pendientes; el PASS técnico no habilita admisión ni ejecución científica.

La toolchain enumera los módulos instalados y sus dependencias de prueba. El orden de derivación es código/contratos/planes → manifiesto normativo y toolchain → política → recibo real externo → paquete y arista. Ningún nodo se incluye a sí mismo. Se preserva el orden documental S1 y se añaden miembros S2 ordenados, sin duplicados. Una modificación produce otra política por contenido. La promoción prepara y verifica todos los bytes, revalida las entradas después de la compuerta y antes de promover, registra una transacción recuperable y sustituye el JSON al final. Una transacción pendiente bloquea consumo; la recuperación restaura JSON, Markdown, selección y ledger anteriores. No se afirma atomicidad física de múltiples archivos.

`validadores/institucional.py` extrae las proyecciones de los cinco snapshots fijados y los hechos institucionales por hash; comprueba identidades publicadas y propaga intervalos racionales desde primitivas. El lector conserva GOS/MI combinado en Chile y el cero semántico PER sin escribir raw. `validadores/ca2_key.py` conecta los metadatos CA2 validados con la clave candidata macro-ca2-v1: bundle, caso, escenario, vectores D2/D6, contexto, país, bloque laboral, coordenadas comunes, protocolo y huellas técnicas. No cambia omega ni la clave estructural; no inventa precision_evidence para E1/E2. El productor numérico que consumirá estas claves es trabajo futuro.

La matriz de pendientes está en `review/MATRIZ_PAISES.md`; la secuencia y destinos exactos en `review/INCORPORACION_FUTURA_S2.md`. A1–A7 y C-A2 permanecen elegidas; no se solicita otra elección científica. La revisión requerida es de los bytes candidatos, correspondencias y autoridad PER propuesta. No se envían consultas ni se repiten las tres preguntas PER resueltas. D2 conserva primaria 2023 y sensibilidad 2015–2023 por vintage; D6 conserva exclusivamente 2023.
