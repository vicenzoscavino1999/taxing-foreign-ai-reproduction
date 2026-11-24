# Estrategia de cálculo y criterio de viabilidad

**CANDIDATO PARA REVISIÓN, SIN ACTIVACIÓN.** Conteos y diseño de algoritmo; no benchmark, simulación ni evaluación del modelo. No se promete duración.

## 1. Costo cartesiano visible

Las nueve dimensiones estructurales primitivas son a,rho,kappa_tilde,beta_tilde,u_theta,z_cost,eta_d,eta_f,phi. L0 tiene tamaños (5,5,6,5,3,3,5,5,5), cuyo producto es **843750**. Bisección anidada de cada eje continuo con n nudos produce 2n−1: L1=(9,9,11,9,5,5,9,9,9), producto **146146275**. Se reproducen por multiplicación entera y por recuento de intervalos; no se enumeran ni evalúan esas combinaciones.

Los conteos son por soporte estructural base, antes de filtros, sin tasas, países, diseños, casos jurídicos, bloques laborales, pi, escala tecnológica, capas externas, coordinación ni sensibilidad. Son tamaños de malla, no probabilidades, escenarios discretos económicos ni tiempos. Filtrar puntos inadmisibles tampoco convierte el soporte restante en discreto. La coordinación por transformaciones no agrega ejes independientes: agrega contextos transformados que pueden compartir puntos exactos; no se presume que todos coincidan.

## 2. Grafo y unidades reutilizables

```text
primitivas estructurales + teoría + normalización + dominio fiscal
  -> theta,delta,kappa0,momentos -> decisiones/regímenes/bases(tau_d,tau_f)
  -> frontera por diseño/menú -> C2 y testigos laterales
a,rho,kappa + cuenta nacional + pi + eta_w,eta_H -> qpot,lambda
grilla externa + crosswalk + gain_share -> K1(lambda)
(C2,lambda,K1) con MISMO omega -> G -> claims
claims + dominios de expansión -> robustez propia / sensibilidad de Q
objetivos + frontera compatible -> despejes / R1 / R2 / puntos fijos
todo -> convergencia por cifra -> auditoría y exportación
```

Las claves normativas exactas están en `contratos/CLAVES_DE_CALCULO.json` y su explicación K1–K5. Omega solo identifica coordenadas comunes; no contiene clave macro ni una clave estructural única. frontier_context contiene la clave de cálculo estructural por diseño/menú, y lambda_pi_envelope la clave macro por país y dependencias nacionales.

El hash macro incluye la proyección macro del omega,estado nacional y dependencias D2/D6/precisión/dominio conjunto,protocolo y huellas técnicas. No se reconstruye de omega_values sola. Un nuevo snapshot cambia ese cache, preservando el estructural si sus primitivas,dominio y huellas técnicas no cambian. Las claves son JSON compactos con decimales exactos en cadenas y órdenes fijos. El anexo especifica campos,normalización y joins; no se eligen al implementar.

C2 no usa país ni datos laborales/tributarios en la ruta estructural declarada si son idénticas las primitivas,topes,diseño y menú. Por eso puede calcularse una vez y enlazarse a los contextos nacionales de cada caso preregistrado; la disponibilidad y sección estatutaria siguen siendo nacionales. Si un futuro contrato introduce calibración nacional o dependencia adicional, la proyección de cache debe ampliarse antes de reutilizar. No se reúnen conditional_full/none ni se convierten en cotas.

Las 1200 celdas externas por caso no obligan a recalcular una misma frontera: K1 y las confrontaciones se construyen después. Las secciones de tasas existentes pueden reutilizar evaluaciones puntuales del mismo régimen, no interpolaciones que atraviesen saltos. La representación detallada se almacena una vez por unidad y se referencia desde contextos; una vista reconstruye sin pérdida las columnas históricas por país/celda.

## 3. Reducciones demostrables y sus condiciones

Para estado estructural fijo, qpot está fijo. Para eta_H fijo, s_L_bar fijo y pi variables, lambda es afín en eta_w y pi, dividida por el positivo 1−qpot. Sus extremos sobre una caja compacta sin cortes internos están en vértices. eta_H se enumera en la escalera discreta pertinente; no se interpola para simular evidencia continua. Si filtros de shares/lambda recortan la caja, se requieren vértices del poliedro recortado y análisis de sus caras abiertas, no solo los ocho vértices pi originales. Las correlaciones de fuente/denominador se conservan: los intervalos de tres shares no son un nuevo producto independiente.

Con N=Q_perp+D_ME_perp*gAI y y=gain_share>0, K1=N/(lambda*y). Para lambda>0: dG/dlambda=N/(lambda²*y), dG/dy=N/(lambda*y²). Si N≥0, G aumenta con ambos; si N<0, disminuye; si N=0, G=C2. La rama aplicable se verifica por celda y dato, no por suposición. Permite evaluar extremos macro/escala **condicionales al mismo estado estructural**, con testigos compatibles. No prueba monotonía de C2 en a,rho,kappa,beta,u_theta,z_cost,eta_d,eta_f o phi. Esos ejes no se colapsan a sus extremos.

La sensibilidad de Q usa un m_Q global o por país, nunca por celda. Condicionado a un omega, G es afín en m_Q si el término D_ME*gAI no escalado se mantiene separado; el umbral escalar puede despejarse y sus cuantificadores se verifican sobre el conjunto compatible. No se sustituye el conjunto de claims por la celda más favorable. Si cambia de celda testigo al variar m_Q, se conserva la envolvente y todos los cambios de tramo. No se interpreta como contrafactual estructural del compañero.

Para todas estas reducciones, primero se prueba algebraicamente la proyección y luego se verifica en fixtures sintéticos independientes. Si hay una dependencia no cubierta, se usa la ruta completa. La reducción de reportes extremos no permite omitir inversiones, geometría, fronteras detalladas, ambas cotas ni las celdas que exige el diseño.

## 4. Ejes que siguen requiriendo cálculo

No hay aquí una reducción demostrada de las nueve dimensiones estructurales. La malla tensorial de referencia sigue siendo el procedimiento de respaldo y el costo de 146146275 unidades L1 sigue visible. Se propone trabajo jerárquico anidado por bloques, evaluación diferida y almacenamiento por contenido. Las unidades existentes no se recalculan al pasar de nivel, pero cambiar tolerancia exige revalidar el resultado reutilizado.

La adaptación prioriza cajas con cambios de régimen, posibles extremos, raíces, tangencias o cotas amplias. **Priorizar no equivale a descartar.** Solo se puede podar una caja mediante una cota validada que demuestre que no altera ninguna cifra/claim requerido dentro de su tolerancia, incluida geometría y todas las inversiones. Una cota de C2 que sirve para un extremo no prueba ausencia de un contorno R1: ese objetivo mantiene su cobertura aparte. Sin cota suficiente, se visita la caja o se marca pendiente. No se reemplaza el continuo por Latin hypercube, muestreo aleatorio o una malla dispersa sin control del error.

No se declara desarrollada una cota global de C2/G: construirla y validarla es trabajo técnico futuro. La estrategia es practicable como ejecución por unidades reanudables y sin multiplicaciones innecesarias por país/celda, pero **no está demostrada su factibilidad temporal a escala L1**. Si la ruta completa no cabe y las cotas no permiten reducirla, la ejecución se detiene como incompleta; no se estrechan soportes ni se omiten países para obtener un PASS.

## 5. Regímenes, R1, R2 y convergencia

Para cada unidad, particionar el dominio fiscal por régimen y evaluar ramas laterales. Los kinks no requieren continuidad del gradiente y los empates conservan la regla formal/no adopción. Optimizar sobre interiores, bordes y límites laterales; un supremo no alcanzado conserva tasas nulas en resumen y su secuencia testigo en tabla hija.

R1 mantiene marching squares por régimen, con vértices y aristas 2D, residuos de la misma rama y registro de cruces discontinuos rechazados. Las componentes ramificadas o puntos aislados se tipan; no se llama curva cerrada a cualquier componente que no toque el borde. R2 mantiene cuatro resúmenes por celda, raíces múltiples y tangencias detectadas por mínimos locales del residuo o intersecciones de R1 validadas. No se declara inexistencia porque no hubo cambio de signo.

T1=1e−12 permanece contable. T2 se mide por familia de algoritmo y unidad de salida; T3 exige error de captura por debajo de1e−4. Coordenadas y longitud de arcos necesitan su error geométrico validado, no se comparan con un número en unidades monetarias. Se conservan controles de estabilidad de n_components,n_roots y etiquetas. Cada cifra publicada tiene fila en convergence_result, con evidencia y cobertura. Dos niveles estables sin cobertura del dominio requerido no justifican una afirmación global.

La malla a/rho/kappa conserva L0/L1/L2 y refinamiento anidado; las demás dimensiones nuevas siguen la regla anidada de DI-04. Se compara el conjunto completo de cifras exigidas, no solo supG. Para nodos nuevos reutilizar únicamente objetos cuyo contexto coincide; no unir C2 y K1 de omega distintos. Al variar tecnología se recalculan derivados según DOMINIOS_Y_FORMULAS.md.

## 6. Orden, almacenamiento y recursos

1. Validar autoridades, schemas, dominios y registry; construir descriptores simbólicos del espacio, sin materializar el producto cartesiano completo en RAM.
2. Crear tareas deterministas por prefijos de ejes y bloques de un máximo configurable de unidades; los tamaños no cambian el conjunto económico. Hash de configuración identifica orden y partición.
3. Calcular y almacenar por unidad estructural: derivados, mapa de régimen, evaluaciones, C2,testigos y convergencia local. Las tablas por contexto referencian ese resultado común.
4. Construir los bloques macro compatibles, aplicar reducciones demostradas y conservar testigos. Procesar la grilla externa por lotes y escribir salidas ordenadas mediante mezcla externa; no acumular toda la tabla en memoria.
5. Construir inversiones y sensibilidad con su cobertura propia; registrar cajas/tareas pendientes. Checkpoints inmutables contienen parámetros,hashes,frontera de trabajo y resultados terminados. Reanudar solo con las mismas autoridades/configuración.
6. Medir recursos y verificar convergencia global por cifra. Publicar solo una versión completa tras gates; los checkpoints parciales quedan diagnósticos, nunca activos/oficiales.

Memoria se controla por lotes y almacenamiento; no garantiza tiempo corto. Las evaluaciones pueden ejecutarse concurrentemente en una futura implementación determinista, pero esta ronda no crea agentes ni ejecuta el modelo. Abortos por tiempo/disco/memoria conservan evidencias, dejan `computation_status=incomplete`, `reason_code=RESOURCE_BUDGET_EXHAUSTED` y readiness=false. No se convierte falta de recursos en `domain_exhausted_no_breakdown`.

## 7. Protocolo de medición futura

Después de aprobación de contratos y autorización específica de validación, fijar entorno canónico,hardware,código,configuración y presupuestos positivos de pared/disco/RAM en `benchmark_plan.json` (campos: plan_id,environment_sha256,code_sha256,contract_sha256,configuration_sha256,selection_rule,unit_count,budget_wall_seconds,budget_disk_bytes,budget_ram_bytes,acceptance_rule). Esos presupuestos son límites operativos declarados antes de medir, no elecciones científicas ni promesas de duración.

Selección determinista: casos sintéticos analíticos y extremos/interiores de las nueve coordenadas, ambos diseños y tres menús, con todas las clases de discontinuidad/tangencia conocidas; después lotes de64,256,1024 y4096 unidades estructurales distintas por orden de hash del identificador en el diseño de benchmark, sin elegir las rápidas. Es una validación futura sintética, no piloto nacional previo al congelamiento. Cada lote registra tiempo total,distribución por régimen,pico de memoria,bytes por unidad,caches acertados y cobertura/convergencia. Las muestras no prueban un límite temporal universal.

Criterio: primero aprobar corrección/convergencia; luego proyectar el costo del respaldo tensorial y del plan de reducción medido con sus supuestos. Exigir que la proyección conservadora documentada (incluida dispersión por regímenes, costo de IO y factor operativo4 explícito) quepa en los presupuestos y que el consumo real por lote respete RAM/disco. El factor4 es margen de planificación, no cota matemática. Si no cabe, optimizar/revalidar manteniendo método, o declarar inviabilidad computacional bajo recursos disponibles. La aprobación de planes acepta este gate futuro; no es confirmación anticipada de que pasará.

## 8. Bloque residual y controles de no activación

El bloque chi_r de robustez es intensidad relativa de pagos y solo existe con momento/crosswalk y D19 admisibles. Bajo D5 actual no se evalúa, se conserva una salida not_applicable_not_identified con motivo. Esta exclusión ya identificada no convierte chi_r en captura reducida ni elimina el bloque del contrato. No se agrega al conteo estructural primario. Su eventual activación requiere sucesión científica/evidencia propias, no una optimización de cómputo.

El conteo de bytes/tiempos futuro se hace en todos los resultados exigidos, incluidos R1/R2 por celda y convergencia; reutilizar C2 no elimina el costo de escritura ni las geometrías con requerimientos distintos. La factura de disco de salidas detalladas debe entrar al benchmark. Sin cota demostrada sobre la búsqueda continua, una pareja de mallas estables no certifica por sí sola ausencia de componentes o extremos entre nudos.

## 9. Cobertura normativa

Esta es la única versión normativa de la estrategia en la entrega. contratos/contract_manifest.json la incluye como review/ESTRATEGIA_DE_CALCULO.md con tamaño y SHA exactos, junto con los tres planes y anexos. Todas esas rutas se resuelven desde raíz de entrega. contract_sha256 autentica el manifiesto completo; no equivale al hash de catálogo solo. No hay aprobación real ni nuevo benchmark.

## 10. Estado de selección y alcance de la primera implementación

A7 y los demás bloques A1–A7 ya tienen selección comunicada. Se mantienen íntegros conteos, soportes y protocolo futuro de recursos. La biblioteca aislada comprueba contratos y metadatos; no ejecuta esta estrategia ni demuestra costo o convergencia. C-A2 ya elegida incorpora metadatos de contextos condicionales por snapshot/escenario en CA2-2. No introduce país en la clave estructural ni permite mezclar snapshots en una cuenta. La conexión candidata de metadatos a macro-ca2-v2 (antes macro-ca2-v1) está implementada y probada aparte; la integración al consumidor numérico y evaluación de costo siguen pendientes, con autoridad S2 propia.

## C-A2 elegida: separación de metadatos y ejecución futura

CA2-2 añade preflight de vectores, evidencia, casos, claims y contexto por hash. E1/E2 fijan cifras/revisiones publicadas completas; E3 requiere precisión aplicable; E4 no tiene dominio numérico en esta versión. Antes de cálculos y de cualquier reuso, el consumidor futuro deberá incluir el hash del bundle C-A2, case_id, escenario, vector y contexto exactos en claves versionadas de la rama condicional. No se reutilizan claves macro-v2 estrictas mediante precision_evidence inventada. La igualdad de las claves previas se preserva para sus consumidores actuales; la conexión condicional productiva está pendiente; validadores/ca2_key.py prepara su clave candidata sin modificar macro-v2.

La variación histórica D2 2015–2023 mantiene vector D6 2023 y contexto fijo por país y comparación pareada; conserva denominadores propios. La comparación de revisiones mantiene las otras coordenadas del claim. El preflight comprueba identificadores, hashes y coincidencias; derivar shares, identidades conjuntas, extremos, robustez universal, convergencia y costos sigue siendo trabajo numérico futuro. El inventario de casos/scenarios se fija por hash externo y no puede reducirse silenciosamente. Ningún resultado de esta ronda es un benchmark ni evidencia de convergencia.
