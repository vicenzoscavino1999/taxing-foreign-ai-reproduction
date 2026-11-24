# Correspondencia con el diseño vigente

**BORRADOR NO APROBADO.** La matriz CSV adjunta contiene una fila por campo de §§18.1–18.8 y expande las claves de celda de §8.1 para las inversiones/R1/R2. Se extrajo del archivo fuente autenticado, no de una lista recordada. Columnas: fuente, hash, sección, tabla/campo histórico, acción, tabla/campo destino, join y justificación. El comprobador exige que cada destino exista y que ningún campo fuente quede sin mapping.

Las salidas D3 de §§18.9 y posteriores siguen perteneciendo a su producto histórico, fijado por manifiesto; no se reespecifican como D7/B/D8. Los antecedentes científicos de §7.9 permanecen salvo cambios expresos documentados en esta revisión. El esquema §18 sustituido no es un segundo contrato vigente de esta propuesta.

R1 conserva extremos, longitud, componentes, contacto con borde y bandera de cierre; agrega grafo bidimensional r1_vertices/r1_edges y rechazos por salto. Una caja de extremos no reemplaza la curva. R2 separa resumen de sección y raíces, para conservar secciones sin raíz e identificar múltiples raíces y tangencias. Ninguna fila representa un par fiscal único universal. Los resultados no aplicables quedan presentes con su estado y sus nulos; las tablas hijas quedan vacías con cobertura justificada.

Cambios semánticos explícitos A5: closed_curve requiere un lazo cerrado real; no_solution de inversión significa inexistencia y no fracaso del método. Los fallos históricos de robustez conservan el literal no_solution, con computation_status=failed. El quiebre de rho usa la frontera demostrada. Las inversiones escalares endógenas tienen tablas de raíces aisladas e intervalos de soluciones demostradas, evitando escoger una sola raíz. La aprobación de estas precisiones se integra a A4/A5/A6.

Campos nuevos sin homólogo histórico: support_id global; primitives u_theta/z_cost; estados/motivos y valores de frontera; computation_coverage; convergencia por cifra; fuentes y autoridades; testigos detallados; evidence/result references y auditorías posteriores. Todos se enumeran en el catálogo. Los IDs de método se fijan por algoritmo/configuración autenticados, no por selección posterior a resultados.

La matriz adicional CORRESPONDENCIA_PROPUESTA_ANTERIOR.csv cubre los 165 campos del DB-07 y mínimos RE-06 de la entrega anterior. Se suma a las 212 correspondencias del diseño vigente; incluye soporte global, parámetros/bindings, listas de primitivas compartidas, estados y sustitución de root_low/root_high para geometría R1. Los destinos se verifican contra el catálogo.

Esta corrección conserva las 212+165 correspondencias; sus destinos permanecen resolubles. CORRESPONDENCIA_AJUSTE_ACTUAL.csv añade los campos/ubicaciones que cambiaron respecto de la revisión recibida. Las claves de cell_context y macro preservan la multiplicidad de estados nacionales; ninguna salida científica histórica se elimina.
