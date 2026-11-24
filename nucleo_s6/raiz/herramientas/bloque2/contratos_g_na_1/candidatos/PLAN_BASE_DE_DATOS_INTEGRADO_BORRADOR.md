# Plan de base de datos integrado — propuesta para revisión

**CANDIDATO PARA REVISIÓN, SIN ACTIVACIÓN.** No activa fuentes, productos, punteros ni cambios de autoridad. Las rutas de productos descritas son diseño de implementación futura, no archivos publicados en esta ronda.

**Selección comunicada por el autor:** A1–A7 y C-A2 ya elegidas para formalización e implementación candidata. Perú principal; casos preregistrados A1-E v2 (aplicación PER, comparación E1 {PER, MEX, COL}, sensibilidad individual E2 COL 2023); CHL fuera del alcance cuantitativo; precisión documentada como vía principal y E1/E2 condicionados; revisión completa y versionada D2 2015–2023; D6 exclusivamente 2023; rho≤1, soportes, resultados y limitaciones auditados. La elección no equivale a firma, incorporación, congelamiento, admisión de fuentes reales ni autorización de corrida. C-A2 se incorpora a este candidato según `review/CONTINGENCIA_A2.md` y el catálogo único CA2-2; sus validadores de metadatos se conservan y se amplían con lectores institucionales candidatos acotados; evaluación numérica y admisión siguen pendientes.

## DB-01. Antecedentes y cambios coordinados

Antecedente: `fase6_planes/PLAN_BASE_DE_DATOS_v4_1_33.md`, SHA `2ac5acc1fadbf0bd38cb70816915a1712eea55ccf147921f0e94b000752c2d85`. Se conservan por referencia sus contratos de catálogo/adquisición, D1–D5, M3, V5, PRE-D6 v3 y PRE-D7-A salvo las sustituciones explícitas siguientes. La historia de aprobaciones no se traslada al estatus de este borrador.

| Cláusula | Antecedente afectado | Cambio propuesto y razón | Decisión |
|---|---|---|---|
| DB-02 | D1/adquisición y contrato D6 source_url | Recepción institucional trazable sin URL ficticia ni PII publicada | A2 |
| DB-03 | D2 output; diseño §10.8; protocolo v1.2.7 | Versionar revisiones nacionales completas y no reemplazar denominador aislado | A3 |
| DB-04 | PRE-D6-P; contrato schema1 con seis conceptos | Añadir representación neta equivalente y crosswalk explícito, conservando tres componentes económicos | A2 |
| DB-05 | PRE-D6 v3, precisión y reconciliación | Mantener precisión documentada; separar cero semántico de exactitud; generalizar intervalos del consumidor | A2 |
| DB-06 | D3/D4/D5 y hashes de consumidores | Propagación por valor, hash, versión y autoridad; conservar productos válidos | A3 |
| DB-07 | PRE-D7-A y D7 previsto | Completar registry, soportes y contratos de productos, sin transporte numérico falso | A4/A6 |
| DB-08 | Revisión PRE-D7-A §§4.3–4.4 | Evitar doble conteo WBES y separar tasas estatutarias de shares | A6 |
| DB-09 | Publicación de D6 y familias D3–D5 | Especificar versiones inmutables, manifiestos y promoción | A6 |
| DB-10 | Elegibilidad D6→D7→B→D8 | Mantener los snapshots completos del dominio de cuatro países y evaluar cada caso preregistrado sobre exactamente sus miembros | A1/A6/A7 |

El significado económico y los extremos propuestos pertenecen exclusivamente a DI-02–DI-08. Los comandos y validaciones futuras se rigen por RE-01–RE-08; este documento define el contrato que deberán materializar.

## DB-02. Adquisición y recepción institucional

Se preservan source_catalog, acquisition_manifest, payloads por contenido, diagnósticos, rechazos y staging existentes. Un correo no aprobado no sustituye retroactivamente una adquisición anterior. Tampoco se borran los intentos rechazados ahora que hay evidencia posterior.

Propuesta de extensión de procedencia: `source_kind={official_public,institutional_attachment}`. Para adjuntos, `official_url` es null si no hay una URL de descarga exacta del archivo; `related_publication_url` es un campo distinto. Se añade un recibo no personal con estos campos exactos: `receipt_id,institution_id,institutional_reference,response_date,message_sha256,attachment_sha256,attachment_bytes,attachment_media_type,attachment_role,received_at,verification_status,related_publication_url,source_evidence_id,claim_scope`. No se guardan remitentes, destinatarios, direcciones, firmas ni cuerpos de correo en el producto o en el catálogo público. Los originales permanecen en su ubicación privada y solo se verifican por hash.

El registro de evidencia tendrá una fila por afirmación: `evidence_id,receipt_id,claim_code,scope_country,scope_year,scope_vintage,scope_sheet,scope_cell_or_range,claim_summary,verified_at,evidence_status`. `claim_summary` es síntesis institucional sin cita extensa ni PII. Un mismo correo que confirma unidad no adquiere por eso autoridad para precisión. `received_at` solo se rellena con dato observado; de no existir se registra null y motivo, sin inventarlo.

La futura admisión exige verificar origen institucional, correspondencia de adjunto y solicitud, hash, tamaño, tipo real de contenido, relación con publicación/vintage y alcance de cada respuesta. Se conserva el archivo adjunto estadístico autenticado, no el EML en entregas públicas. Este canal requiere enmienda del contrato D6 y de adquisición; la lista actual de hosts HTTPS no debe eludirse construyendo una URL nominal para un adjunto.

## DB-03. Revisión versionada de D2 y situación por país

### DB-03.1 Regla común

Se propone una familia `d2_cuentas_nacionales/versions/<tree_sha256>/` con tabla primaria, sensibilidad, manifiesto, auditoría, gates y tabla de revisión. El output histórico actual permanece byte a byte. Un nuevo `active_product.json` apuntará a la versión aprobada; el primer predecessor referencia explícitamente el manifiesto legado, no inventa un tree hash antiguo.

Por país se exige el mismo conjunto contable: PIB a mercado, remuneración doméstica generada, excedente bruto más ingreso mixto y D2−D3 de una misma revisión estadística, año, moneda/unidad, base y cobertura. Se conserva el desglose GOS/MI cuando existe; si la fuente publica B.2b/B.3b combinado, se consume ese total sin inventar una apertura. Se usan niveles originales y después cocientes; no reconstruir impuestos desde un share serializado. La remuneración recibida por residentes no sustituye la generada domésticamente. Los subtotales por sector no sustituyen el total de economía/PIB a mercado.

La tabla `d2_revision_bridge.csv` propuesta contiene `country_id,year,concept_id,old_manifest_sha256,new_source_snapshot_id,old_value,new_value,unit,multiplier,old_vintage,new_vintage,delta,reason,evidence_id,precision_id`. Su nombre no significa que un puente entre vintages ya esté probado: documenta la revisión; un puente conciliatorio que permita mezclar vintages necesita otra evidencia explícita.

La tabla primaria añade a las columnas científicas vigentes `source_snapshot_id,source_vintage,source_status,source_evidence_id,precision_id,domestic_or_resident,valuation_basis`. D2 conserva 2023 primario y 2015–2023 de sensibilidad contable/laboral, incluidos impuestos netos totales; D6 conserva exclusivamente el corte 2023 y sus tres componentes tributarios. No se exige D6 histórico para completar D2 o habilitar la primaria 2023; los años no actualizados conservan su vintage y limitación, sin etiquetarlos como una serie revisada homogénea. La sensibilidad MEX 2015–2022 no hereda el pase de precisión de 2023.

### DB-03.2 Perú, caso principal

Adjunto PBI_Imp_2023_CEIyCOU_R.xlsx: dca6ebf37c2c0865a7d579cf73ade2358a459ea51441e2a2ee9d6b4412f158e3, recibido con 3434; cadena 3434→3598→respuesta 16/09/2026. El último correo dice 3916 en el asunto y 3918 en el cuerpo. Hash del EML final: 90994661e8f21fbaa189067472fc8b3b23be5f79540fb8057476ea38775a0137. Se conserva la discrepancia, sin corregir documentos institucionales.

CEI_2023!A3 y COU_2023!A3 indican millones de nuevos soles; año 2023P, revisión octubre 2025 del conjunto 1950–2024. La respuesta acredita redondeo a la unidad más cercana para los importes consultados PIB y D211/D21/D31/D29/D39. No determina desempate en media unidad. Una envolvente cerrada de media unidad a cada lado es un dominio exterior conservador; no afirma una regla concreta de desempate ni cubre todo error estadístico. D39 en DL390 es cero exacto institucional, aunque la celda original permanezca vacía. Devengo explícito: D211,D21,D31,D29. No extender esa respuesta a remuneración/GOS/MI ni a 2015–2022.

Lectura reproducible: CEI E19=1003439 PIB, E21=284345 remuneración doméstica, E27=428595 GOS, E28=207653 MI, E24=82846 impuestos netos. La identidad es exacta sobre los literales publicados. P21=284344 pertenece a otra cuenta.

Resumen identifica D19=K376 (D211), D20=F376 (D212), D21=I376 (D214), D18=D19+D21+D20 (D21 agregado). F376=1423, I376=9580, K376=66351; suma 77354. D25=J376=-1505 (D31), D22=DL389=6997 (D29), D26=DL390, con caché cero. Los headers de COU F9/I9/J9/K9 y códigos del Resumen se guardan en PER_componentes_D21.json.

La correspondencia técnica candidata puede aplicar la regla institucional a las primitivas almacenadas de D21, explicitando que la respuesta nombra el concepto agregado y que la descomposición procede del adjunto; esa aplicación se revisa internamente y no se atribuye como una nueva cita institucional por selector. Si ese vínculo no se acepta, queda pendiente solo la precisión de esas primitivas; no se vuelve a preguntar por redondeo, cero ni devengo ya contestados. No asignar ±0.5 independiente a la suma D21: tres primitivas de media unidad propagan ±1.5. D21−D211 cancela exactamente la primitiva K376 antes de propagar. Con D31 normalizado positivo, otros=F376+I376+J376=9498; producción=6997; IVA=66351; total=82846. Ruta candidata D-02 (DB-04 net_equivalent): V=K376, N=DL389+DL390 (cero exacto), P=E24−N, otros=P−V, PIB=E19; F376, I376 y J376 son contrastes publicados, no primitivas de precisión. La igualdad del total D2–D6 es por construcción (E24 compartido) y no es una prueba independiente. Autoridad PER propia candidata, pendiente de aprobación: D31 cambia signo y D39 usa la evidencia de cero exacto, sin editar raw ni extender V2 COL/MEX.

### DB-03.3 México

Se consultaron los archivos staging autenticados y documentación local disponible. No se localizaron respuestas nuevas en esas superficies; el buzón remoto no pudo verificarse. Esto no equivale a afirmar que no existen respuestas nuevas.

MEX XLSX hash 077a64fe4272a7163f47fbeb3835428838f89460537480222b7f5d0d5abbf6f6, Tabulado: año2023, CSI base2018 serie2003–2024 revisada, precios corrientes en millones de pesos. M34=S34=31871088.604 PIB; L36=R36=9102482.904 remuneración doméstica; L60=R60=13460447.819 GOS; L61=R61=7167692.458 MI. Tax net=2140465.423; identidad exacta. R46 D21=2002987.333, R47 D211=1366582.569, R53 D29=238902.655, R55 D31=-88879.305, R59 D39=-12545.26. La coincidencia L/R de generación está verificada, no se intercambia remuneración de residentes. V2 y S1 solo cubren orientación histórica MEX; falta precisión aplicable y admisión/revisión D2 completa. No combinar con PIB antiguo 31855566.301.

### DB-03.4 Colombia

Se consultaron los archivos staging autenticados y documentación local disponible. No se localizaron respuestas nuevas en esas superficies; el buzón remoto no pudo verificarse. Esto no equivale a afirmar que no existen respuestas nuevas.

COL XLSX hash fa799bfe8e087ba1921a7c9623490748d0b24985fdf14acb0e53e155c125da5c, hoja2023p, miles de millones de pesos, base2015, publicación17/02/2025. A29=1584562 PIB directamente publicado (etiqueta K29); Q35=1429920 VA, no PIB. A36=D36=524069 remuneración doméstica; A47=D47=525308 GOS; A48=D48=333827 MI. Q53=527488 está en asignación de ingreso primario, no debe sustituir remuneración doméstica. Q63=154642 D21,Q64=102414 D211,Q68=46954 D29,Q70=0 D31,Q71=-238 D39. Otros netos52228, producción46716, total201358; identidad exacta con PIB. El cero publicado D31 no prueba cero exacto. Orientación histórica cubierta; precisión/alcance de respuesta y admisión siguen pendientes. Para D2 2015–2022 no extrapolar evidencia 2023.


### DB-03.5 Chile

COU 2023 hash 4fa4dc3da102ec26a07d2215d0f4fabea2be1a348077f6c5aee2b805d69ed058; CEI hash 84f025caad43d5df78e5197bf038bb8e790aa3e4e0beb4972503771f11da0460. URLs oficiales y lector XLS se conservan en lectura_y_conciliacion.json y consulta_bde.json. XLS almacena IEEE754: la representación decimal del lector no es precisión económica.

Respuesta 17/09 a BCCHGCRFAO18898, presentada 07/09: equivalencia de total CEI D2−D3 con suma de cuatro componentes COU, mismo cierre para publicaciones consultadas, precisión al sexto decimal. EML hash 6412f38aa7be728b286d74871d88b6674c523270277ef6ffe8df24e60f851fb1. No reproduce en el material accesible los hashes/años/URLs originales completos de la pregunta. No prueba por sí sola que todo archivo BCCh de 2023 tenga ese cierre. No especifica redondeo, truncamiento o cota de error.

COU hoja2: F29=2743.912399520677 impuestos indirectos sobre bienes y servicios; G29=1541.570625957791 derechos de importación; J29=24331.99890063512 IVA; fila29 Total. Hoja23: P16=253479.1641309069 VA; P20=114601.5649773946 remuneraciones; P23=134717.9418046389 excedente según su etiqueta; P29=4159.657348873267 netos producción. Unidad literal: miles de millones de pesos de 2023. P26 no es el neto nacional completo de productos; no usarlo solo. No abrir D29/D39 brutos.

Suma tributaria COU=32777.139274986855. CEI D30=32777.139275, residuo 0.000000013145 miles de millones. PIB COU derivado por VA+productos netos=282096.646057020488. PIB CEI derivado por remuneración+GOS_MI+netos=282096.64605703278; residuo 0.000000012292 miles de millones (12.292 pesos). Son diagnósticos, no reconciliación aprobada ni tolerancia. La fila CEI D24 está etiquetada B.2b/B.3b: conservar agregado GOS/MI sin inventar apertura.

Consulta pública BDE realizada a las 15:00:59 UTC: PIB a precios corrientes, referencia 2018, unidad miles de millones de pesos, 2023 mostrado como 282.097 (separador de miles). La pantalla redondeada no demuestra igualdad exacta ni vintage común con los XLS/XLSX. HTML de investigación guardado con hash/procedencia; no incorporado a adquisición.

Búsqueda de solicitud original: documentos md/json/txt/csv de fase2/tmp, adjuntos pertinentes y EML relevantes en Downloads. Inventario adicional de Downloads encuentra esos cinco EML y un EML ajeno sobre un manuscrito, que no fue leído. No se encontró la solicitud original que vincule inequívocamente los snapshots. Gmail devolvió oauth_token_invalid_grant; no se pudo comprobar Enviados/Recibidos remoto. Pregunta mínima pendiente: recuperar la copia YA ENVIADA de BCCHGCRFAO18898 con enlaces/año/archivos para verificar su alcance; solo si no resuelve el vínculo, pedir confirmación sobre esos snapshots y PIB del mismo cierre. Para E0/E3 se necesita además saber si sexto decimal significa redondeo o truncamiento, en qué unidad y con qué alcance; no se envió nada.

## DB-04. Extensión de representación de D6

Contrato actual: seis conceptos D211,D21,D31,D29,D39,PIB para cada uno de cuatro snapshots. No admite el sustituto neto chileno. La propuesta crea schema2, con `representation={gross_components,net_equivalent}` y requisitos mutuamente excluyentes por snapshot. No relaja los estimandos de DI-05.

Ruta bruta: conservar los seis conceptos y orientación específica por evidencia. Ruta neta: exigir IVA V, neto de productos P=D21−D31, neto de producción N=D29−D39 y PIB G. La transformación es `[V,P−V,N]/G`; la suma es `(P+N)/G`. No reconstruir D21,D31,D29,D39 individualmente ni rellenar sus campos como ceros. En ruta neta esas columnas no existen como observaciones; su ausencia es estructural con `not_observed_net_route`, no elegibilidad ficticia de seis códigos.

El crosswalk propuesto usa `mapping_id,source_snapshot_id,source_label,source_code,source_selector,target_concept,formula_id,input_evidence_ids,accounting_framework,recording_basis,valuation,coverage,vintage,orientation_authority_id,mapping_status`. source_code es null cuando no existe; mapping_status debe pasar de proposed a approved después de verificación. Una fórmula compuesta enumera cada celda y su signo, sin sumar dos veces F29/P26. Coincidencia numérica sola no demuestra equivalencia conceptual.

Condiciones comunes de admisión: organismo oficial, economía nacional completa, año 2023, precios corrientes y PIB a mercado, SNA2008/devengo o equivalencia explícita aprobada, moneda/multiplicador comunes, vintage compatible, cobertura de subvenciones documentada, crosswalk aprobado y reconciliación con D2. La vía estricta E0/E3 añade precisión de cada primitiva consumida. E1/E2 requieren evidencia condicional CA2-2 según DB-12; no exactitud inventada. No se admiten caja fiscal ni recaudación central como sustituto de cuentas nacionales sin puente probado.

Las observaciones raw conservan valor/signo/código o etiqueta nativa. Para brutos, `normalized_value=orientation_multiplier*raw_value`; no usar abs. Una autoridad de signo va ligada a país, hash, selector y concepto, no a todos los archivos de un organismo. Una ruta neta no requiere fingir autoridades de orientación de componentes brutos no observados.

## DB-05. Precisión, ceros y reconciliación

Las reglas de intervalos y precision_evidence de esta sección corresponden a la vía estricta E0/E3. E1/E2 conservan cifras publicadas y usan el contrato condicional DB-12; no rellenan estos intervalos ni los pasan como acreditados. La conciliación necesaria y la completitud de los miembros de cada caso preregistrado siguen siendo obligatorias en ambas vías.

Se mantienen las categorías de PRE-D6 v3: positivo si L>0; cero documentado exacto si [L,U]=[0,0] y hay autoridad; signo no resuelto si 0 pertenece al intervalo sin exactitud; subsidio neto si U<0. No trasladar pi=0 de una excepción de escenario a un cero observado, ni usar el valor puntual para eludir el intervalo.

`precision_evidence` debe contener `precision_id,source_snapshot_id,selector,unit,multiplier,rounding_rule,rounding_unit,interval_low,interval_high,exactness_status,evidence_id,evidence_scope`. Las reglas admitidas son redondeo documentado al múltiplo, truncamiento documentado o exactitud documentada. No se deduce precisión del formato Excel, cantidad de decimales, suma que coincide o nota de otra publicación. Ningún intervalo es inventado en esta propuesta.

Para intervalos brutos orientados, la multiplicación por −1 invierte extremos. Si X=[l,u], Y=[p,q], X−Y=[l−q,u−p]. Se mantienen identificadores de primitivas compartidas para simplificar cancelaciones: en ruta neta V+(P−V)+N=P+N; la incertidumbre de V no se cuenta dos veces en el total. Numeradores/PIB se evalúan con los cuatro cocientes de extremos si G_low>0, y se toma mínimo/máximo. La incertidumbre de fuente no se confunde con T1/T2 del solver.

Reconciliación contra niveles D2 del mismo vintage: `I_residual=I_tax_source−I_tax_D2`, con aceptación si contiene cero y todas las correspondencias conceptuales pasan. El PIB también se contrasta como intervalos de ambas fuentes, no únicamente el punto D2 contra el intervalo D6. Si se propone puente de vintage, debe especificar niveles/conceptos cubiertos, residual y evidencia oficial; no tolerancia libre para absorber diferencias. Los extremos de las participaciones y dependencia de denominador se conservan en el producto para consumo conjunto; no asumir independencia de tres shares que comparten PIB.

Hallazgo de implementación: `_build_country_quantitative` en `herramientas/d6/construir_d6.py` alrededor de líneas 4990–5100 usa PIB D2 puntual, semiamplitudes en reconciliación total, residual_low=high y no materializa puente de vintage. La ampliación propuesta necesita intervalos generales y compartición de primitivas. La biblioteca candidata nueva verifica propagación e identidades de lectura; la integración al productor cuantitativo sigue siendo posterior y no se ejecuta aquí.

### Información indispensable y alcance de la dependencia

Para elegibilidad estricta se necesita evidencia suficiente de precisión para **cada** primitiva efectivamente consumida en la representación elegida y para D2; no necesariamente otra carta si una fuente primaria aplicable la acredita. PER tiene unidad/revisión, regla de redondeo de los conceptos consultados, cero D39 exacto y devengo acotado confirmados; la propagación del D21 derivado exige identificar sus primitivas. MEX y COL tienen orientación histórica acotada; CHL tiene equivalencia y cierre declarados, pendientes de vínculo con snapshots, y precisión al sexto decimal sin regla de redondeo. Ninguna de esas piezas por sí sola resuelve toda la precisión. La admisión condicional requiere los controles comunes y CA2-2, sin atribuir precisión estricta.

La vía estricta exige intervalos de publicación sustentados, aunque no sean errores de muestreo. Si falta esa evidencia no hay elegibilidad estricta. C-A2 elegida permite preparar E1/E2 mediante una vía condicional distinta: vectores completos, procedencia, correspondencia, cobertura, orientación y conciliación acreditadas, sin afirmar precisión exacta ni fabricar intervalos [x,x]. E3 exige regla por archivo, selector, periodo y vintage; E4 queda sin dominio numérico en esta versión. `contratos/catalogo_contratos.json` (CA2-2) es la definición única de campos, relaciones y reglas; `contratos/CONTRATO_CA2.md` la presenta para revisión. El PASS de metadatos no abre D7 productivo.

## DB-06. Propagación de D2 por tipo de dependencia

| Consumidor | Dependencia observada | Consecuencia propuesta |
|---|---|---|
| Diseño §10.8 y protocolo v1.2.7 | Valores nacionales y hashes D2 incrustados | Nueva versión del protocolo y tablas de valores enlazadas al nuevo D2; preservar versiones previas |
| D3 | Universo, fuentes, planes aprobados y paquete; no dependencia numérica D2 identificada en el constructor | Mantener árbol activo y datos, revisión de compatibilidad por autoridad. Su preflight busca un único plan por prefijo: múltiples planes históricos pueden requerir selección explícita, no recálculo de WBES |
| D4 | Puntero/árbol D3, V5, evidencia jurídica | Mantener valores, 16 pares y corte; certificar compatibilidad con nueva autoridad. D2 no altera hechos jurídicos |
| D5 | Punteros/árboles D3/D4 y seis convenciones | Mantener cero filas de Ptarget y limitaciones. Cambiar PIB no identifica pagos ni kappa |
| PRE-D7-A | Pin duro del manifiesto D2 `78791...` y planes 30/33/44 | Nueva versión del preparador/contrato que acepte selección explícita de autoridad; no nuevo transporte bibliográfico por cambiar PIB |
| D6 | PIB y tax share/precisión D2; contrato y fotografía previa de red | Nuevo contexto de entrada por versión. Mantener intacta la fotografía histórica pre_network; nunca reescribirla con cifras nuevas |
| D7/B | Participación laboral, impuestos, lambda y referencias a productos | Reconstruir futuros productos que sí consumen valores; aún no hay resultados oficiales que recalcular |
| Congelador/documentación dependiente | Selección, compatibilidad, hashes y linaje | Nueva sucesión declarada y certificados de reuso; no restaurar pins antiguos como si fueran actuales |

Certificado propuesto de reuso: `reuse_id,consumer_product_type,consumer_tree_sha256,old_authority_package,new_authority_package,dependency_path,old_hash,new_hash,dependency_kind,value_changed,action,justification,evidence_sha256`. `action={reuse_bytes,rebuild_consumer,revise_contract}`. Se revisan manifests y lectores; cualquier dependencia adicional detectada se clasifica antes de promover. Un hash diferente no implica automáticamente valores diferentes, ni mismos valores autorizan consumir un paquete incompatible.

## DB-07. Contrato D7 completo, sin referencias ambiguas

Esta sección sustituye íntegramente DB-07 de la entrega anterior. Su especificación completa, archivos, columnas,tipos,unidades,nulos,PK,UK,FK,estados y reglas condicionales se encuentra en `contratos/catalogo_contratos.json`; `contratos/CONTRATOS_D7_B_D8.md` es su representación legible generada. Ambos son parte normativa de los tres borradores y se aprueban juntos por hash. No se deja al implementador elegir campos esenciales ni se mantienen simultáneamente tablas antiguas contradictorias. La incorporación por referencia del plan vigente no reintroduce el antiguo support_id ambiguo ni las salidas mínimas sustituidas.

Decisión mecánica resuelta: support_id es globalmente único, con estructura SUP:<support_set_id>:<parameter_id>:<variant_id>. Los tres componentes son IDs sin dos puntos. PK=support_id; UK=(support_set_id,parameter_id,variant_id). support_set_id tiene FK al índice support_sets. Cada FK a support_id resuelve una única fila y debe concordar con set/parámetro del binding consumidor. No se resuelve por parámetro, nombre corto, orden de archivos ni último conjunto visto. Base,coordinación y robustez tienen IDs de conjunto distintos y pueden conservar el mismo parameter_id sin ambigüedad. No es una nueva decisión científica.

parameter_registry contiene definiciones globales, sin repetir low/high por país; parameter_bindings contiene contexto,set,país/tipo/valor/soporte/procedencia. Los límites y nudos pertenecen a support_set. formula_registry y formula_inputs definen dependencias explícitas y sin ciclos. joint_constraints y constraint_inputs fijan dominios,fronteras y motivos. Las referencias a fuentes PRE-D7-A y D4/D6 se resuelven contra los manifiestos autenticados, no contra un activo que pueda cambiar a mitad de cálculo.

`contratos/formulas.json` registra las nueve primitivas estructurales incluidas u_theta,z_cost; escalas gamma,z_m; restantes parámetros macro/de escenario; derivados y transformaciones. DOMINIOS_Y_FORMULAS.md define las recomputaciones al variar tecnología. Theta y delta_tilde no vuelven a entrar como ejes libres. Ningún país ficticio GLOBAL: alcance global usa scope_id y country_id=null.

Se conservan PRE-D7-A:14obras,13usos limitados,1rechazado,0transportes numéricos nacionales. Las fuentes públicas se referencian en la entrega anterior por ruta y hash; no se descargan ni duplican. No se consume Ptarget inexistente ni se reactivan Hill,masa empresarial,cola–cuerpo o De Loecker. Inversiones por factor compuesto no identificadas llevan ese estado específico sin impedir las demás.

Las compuertas conservan G01 esquema/PK/FK;G02 autoridades;G03 miembros exactos del caso preregistrado/D6 3×|country_set| componentes;G04 dimensiones;G05 soportes y decisiones;G06 fórmulas sin ciclos;G07 admisibilidad;G08 transporte;G09 V5;G10 limitaciones aceptadas;G11 anticircularidad/doble conteo;G12 publicación y no divulgación. La verificabilidad de la propuesta no significa que existan productos elegibles.

Se mantienen la distinción cero semántico/exactitud y los requisitos de DB-05. Una decisión interpretativa del autor puede documentarse como supuesto aceptado, pero no se etiqueta como respuesta institucional adicional ni como prueba de precisión que la fuente no proporcionó.

### Ajuste contractual consolidado — 2026-09-12

Estado común, cálculo estructural y contexto macro nacional se distinguen según contratos/CLAVES_DE_CALCULO.json y K1–K5 de su explicación. Omega no contiene clave macro ni una clave estructural única; frontier_context conserva la estructural por dominio/diseño/menú. lambda_pi_envelope lleva macro_key_sha256 y payload con país,estado nacional,dependencias D2/D6/precisión/dominio conjunto y huellas técnicas. cell_context incorpora estado nacional y clave macro esperada; se rechaza cualquier enlace de país/omega/contexto incompatible. No se duplican evaluaciones estructurales por cambiar un snapshot nacional.

C_2 tiene formula_id=C_2 registrado como numerical_operator: supremo de R/B_pot en el dominio fiscal admisible. R es función declarada con sus dependencias. D7 valida definiciones sin exigir resultados B; B produce capture_ceiling_result, conserva disponibilidad,supremo no alcanzado,laterales,errores y testigos. Declaración de destino no es dependencia circular ni forma cerrada nueva.

contratos/contract_manifest.json usa exclusivamente rutas relativas a raíz de esta entrega; incluye todos los contratos/anexos,estos tres planes y la única review/ESTRATEGIA_DE_CALCULO.md normativa. Se excluye a sí mismo. contract_sha256 es el hash de sus bytes exactos; una aprobación futura debe cubrir ese hash y todas sus entradas. Las correcciones contractuales auditadas se preservan. A1–A7 tienen selección comunicada; sus actos formales siguen pendientes. Los validadores aislados de esta entrega comprueban metadatos, sin habilitar ejecución.

## DB-08. WBES, Pareto, margen y tasas

Se conserva distinción establecimiento/empresa legal, topcode desconocido, ausencia de M_c y de pesos nacionales de empresas. No construir Hill ni cola–cuerpo bajo M3. Los pesos WBES son de establecimientos de la encuesta; no se rebautizan como empresa ni resuelven cobertura internacional de masa.

La fórmula antigua candidata `d2−n2a−n2a2−n2e−n2i` tiene riesgo concreto: n2a incluye costos laborales amplios y n2a2 identifica una parte de esos costos. Propuesta A6: usar residuo `(d2−n2a−n2e−n2i)/d2` **solo** cuando el diccionario de cada vintage confirme que n2a contiene n2a2 y que los otros sumandos son disjuntos. Si no, la fila de plausibilidad queda no construida; no se deduce un costo alternativo por intuición. No añadir n2b solo en tres países.

Para futura plausibilidad, estimando principal: razón de sumas ponderadas de residuo y ventas, con wmedian, sobre establecimientos elegibles y ventas positivas. Informe auxiliar: media ponderada de ratios individuales, que es otro estimando. Documentar la selección wmedian frente a wstrict/wweak y mostrar ambos como sensibilidad; si el diseño de la encuesta impide esa selección común, se requiere regla explícita por vintage. Códigos especiales/faltantes no son cero; se usan casos completos del mismo conjunto de costos, se reporta cobertura ponderada/no ponderada y no se winsoriza silenciosamente. No divulgar observaciones o identificadores. El resultado es residuo operativo construido, no beneficio observado ni gamma nacional. Si no se construye, no bloquea la normalización ni la ruta primaria estructural.

A5 UN sectorial adquirido es histórico (CHL hasta 2014, COL 2016, MEX/PER 2011); sirve para plausibilidad histórica, no medición 2023 de gamma. A6 legislación CIT y OECD ETR conservan usos distintos: la primera alimenta tau_d_statutory con selector, régimen, fecha de vigencia y unidad; la segunda es evidencia auxiliar, no recaudación sobre PIB. No se fijan tasas actuales por memoria ni se trasladan automáticamente a 2023. La sección estatutaria se bloquea específicamente si falta ese mapeo; no se inventa para completar una tabla.

## DB-09. Versiones, manifiestos y punteros

Para D7/B/D8 gobiernan exclusivamente los objetos JSON y reglas canónicas del catálogo contractual revisado. Las convenciones siguientes se conservan para la propuesta D2 y para la familia D6 en su ámbito; no crean un segundo contrato D7. Los archivos de D8 posterior tienen evidencia propia y no añaden filas a un D8 previo inmutable.

Se preservan las convenciones canónicas ya implementadas de cada familia histórica. Para nuevos D2/D7, la propuesta fija JSON canónico UTF-8 LF, claves ordenadas y serialización sin espacios superfluos; CSV encabezado y orden por PK. Hash de árbol: SHA-256 de la lista JSON canónica ordenada de `{path,sha256,bytes}` de archivos científicos y auditorías, excluyendo manifiesto y puntero. Manifiesto separado enumera esos archivos, incluye tree_sha256 y es hasheado por su consumidor. No hash autorreferente.

Manifiesto propuesto: `schema_version,product_type,run_id,created_at,producer_path,producer_sha256,authority_package_sha256,authority_manifest_sha256,contract_sha256,input_dependencies,files,tree_sha256,phase_status`. Cada dependencia contiene `role,path,sha256,tree_sha256,version,authority_package_sha256`; null explícito cuando una fuente raw no tiene tree. El manifest no llama activo a un producto que aún está en staging.

Puntero propuesto D2/D7: `schema_version,product_type,active_tree_sha256,active_relative_path,active_manifest_sha256,predecessor_reference,promotion_receipt_sha256,immutable_tree_sha256s`. El recibo de promoción registra autorización real y verificaciones; nunca se rellena en este borrador. Publicación: construir staging aislado → verificar completamente → mover versión a destino inmutable → verificar bytes → sustituir puntero de manera atómica. No afirmar atomicidad conjunta de directorio y puntero; si falla el último paso, la versión permanece no activa y el puntero previo sigue válido. No borrar versiones ni cambiar manifiestos para «hacerlos coincidir».

D6 conserva sus siete archivos y su formato ya normado en PRE-D6-P, salvo nuevas columnas/contrato schema2 expresamente aprobados; su manifiesto enumera los seis archivos no manifiesto. No se sustituye silenciosamente su algoritmo de árbol por el de otra familia. Toda migración tiene versionado y verificador específico.

## DB-10. Admisión conjunta y fronteras de consumo

El dominio de datos conserva cuatro snapshots completos según su representación aprobada. Cada caso preregistrado exige tres filas por miembro: 3 en la aplicación principal PER (E0/E3 2023 por la ruta neta), 9 en la comparación E1 {PER, MEX, COL} y 3 en la sensibilidad individual COL. Por país, tres filas cuantitativas o ninguna. En E0/E3 solo la aplicación principal PER 2023 con 3/3 filas elegibles puede abrir D7-B por la vía estricta; no hay comparación estricta registrada. E1/E2 tienen la vía separada DB-12: misma completitud económica, evidencia condicional, consumidor versionado y validación económica previa, sin reutilizar el pase estricto. `complete_with_limitations` puede describir un cierre administrativo y no habilita ninguna vía productiva.

D7 requiere sus parámetros activos completos y limitaciones compatibles con la rama primaria. B requiere D7 válido, A/A-ter canónicos, requerimiento externo y contratos/solver validados. D8 audita insumos y validación de B antes de freeze-run; después audita productos de la corrida sin volver a definir parámetros. Esta separación evita el ciclo «B necesita D8 que solo existe después de resultados». Los artefactos de salida y orden se especifican en RE-06.

La enmienda A1-E v2 fija antes de cualquier resultado, por criterios de evidencia, los casos preregistrados con sus tipos, miembros, años y revisiones. Cada caso exige exactamente sus miembros; un fallo posterior lo bloquea y ningún país se retira después de ver resultados. Una sensibilidad individual no exige a Perú. Un cambio de conjunto requiere una nueva enmienda revisada. La falta conceptual de Chile no se resuelve ampliando un margen.

## DB-11. Expedientes pendientes y frontera de la contingencia

Según comunicación del encargo, el revisor envió complementos el 2026-09-12 a INEI (remuneración, excedente, ingreso mixto y precisión histórica), DANE (mismas partidas y hojas 2015–2022; radicado 202620018777) e INEGI (precisión de cinco componentes contables 2015–2022). Chile mantiene consulta sobre precisión, correspondencia y revisiones. Se registra el hecho comunicado de envío; no se verifican ni copian EML, datos personales o cabeceras. No son respuestas ni pases de admisión ni solicitudes de un D6 histórico completo. No se envían nuevas consultas.

La matriz por faltante, evidencia existente y fuente adicional aplicable está en CONTINGENCIA_A2 §§2–3. Documentación genérica de cuentas nacionales o sensibilidad no acredita el quantum de estos archivos. El escenario de vector publicado preservaría cifras y procedencia, pero no generaría precision_evidence exacta ficticia. Los escenarios por revisión conservarían vectores D2 contables completos por año/vintage, sin mínimos/máximos independientes ni mezcla de vintages. La sensibilidad histórica cambia el ancla laboral D2 con D6 2023 fijo y desfase explícito, según CONTINGENCIA_A2 §2.1; no exige desagregación D6 histórica. En la primaria 2023 se conserva el denominador compartido de la cuenta contemporánea. Un residuo inexplicado sigue siendo discrepancia, no error tolerado inventado.

CA2-2 separa `ca2_cases.admissibility`, `ca2_claims.technical_status` y `ca2_claims.interpretation`. Los lectores verifican seis tablas, hashes, alcance, referencias y cadena de evidencia. `strict_metadata` y `conditional_metadata` son estados de preflight candidato; no admisión nacional. Sin adaptadores registrados queda `pending_evidence`; evidencia obligatoria ausente o negativa impide la vía condicional. El consumidor D6 productivo y las claves macro-v2 estrictas conservan sus contratos: no se les inyecta una dependencia precision_evidence ficticia. La conexión de CA2-2 a nuevos consumidores y claves de ejecución condicionada exige desarrollo/versionado explícitos y S2 antes de producción.



## DB-12. Contrato candidato de admisión C-A2

El catálogo integrado CA2-2 añade `ca2_vectors`, `ca2_members`, `ca2_evidence`, `ca2_cases`, `ca2_inputs` y `ca2_claims`, sin redefinir las 54 tablas anteriores. `CA2Validator.read_bundle` exige hash esperado externo y JSON canónico; `Contracts.read_csv` reutiliza las mismas columnas y PK/FK para lecturas tabulares. Las seis tablas se validan juntas. Los snapshots y evidencias se leen bajo una raíz explícita por ruta contenida y hash; los miembros deben coincidir con año, vintage, unidad, multiplicador y denominador de su vector.

La admisión condicional candidata exige exactamente los miembros del caso preregistrado (A1-E v2), afirmaciones de un tipo preregistrado con exactamente sus años y vectores con la representación preregistrada; D2 contable completo y D6 2023 completo según representación; cinco roles de evidencia por vector (concepto, cobertura, orientación, procedencia, conciliación); conciliación conjunta de las dos cuentas primarias; adaptadores que contrasten hechos extraídos del archivo. Los tres componentes D6 se derivarán con las fórmulas vigentes después de validar su identidad y signos: la biblioteca de esta ronda no los calcula. No se reutiliza la etiqueta del gate estricto para casos condicionales. Un caso incompleto respecto de sus miembros no produce una comparación reducida.

E0/E3 añaden una regla de publicación acreditada para todos los selectores; su construcción/intersección numérica sigue pendiente. E1/E2 no crean precision_evidence ni intervalos. E2 exige revisiones completas de al menos una cuenta de cada pareja por país/año y evidencia de comparabilidad de cada familia que cambia; la otra cuenta puede permanecer fija. E4 no admite bandas o distribuciones: `measurement_domain` es null en CA2-2. Una versión futura que fundamente otro dominio requerirá revisión explícita.

Las respuestas posteriores añaden IDs de vector/evidencia/caso/claim y enlazan predecesores. `validate_transition` autentica el bundle anterior por hash y exige conservar todas sus filas; en esta versión la inmutabilidad vale también antes de congelar. No publica ni promueve archivos. Los lectores candidatos de los snapshots identificados y la identidad puntual publicada están implementados en institucional.py. La admisión semántica completa, certificación de compatibilidad productiva D2/D6 y consumo D7/B siguen pendientes. Un adaptador ficticio de tests no acredita al INEI, INEGI, DANE ni BCCh.

## Corrección CA2-2: requisitos de evidencia y sucesión exacta

C-A2 sigue elegida y sin activación. Se distingue integridad de registros, evidencia común y evidencia adicional por escenario. Todos los registros presentes se autentican por archivo/hash/scope y estructura; sus resultados se conservan en evidence_outcomes. La precisión desconocida no bloquea E1/E2 por sí sola, aunque los mismos vectores también alimenten E0/E3 pendientes. E0/E3 mantienen la regla aplicable; E2 mantiene comparabilidad de las familias revisadas. Los cinco roles comunes siguen siendo indispensables. common_conflicts comunica contradicciones comunes extraídas por el adaptador, incluso si aparecen en un documento de precisión: bloquean todas las vías afectadas. No se duplican vectores ni se eliminan registros desfavorables para obtener pase.

El catálogo CA2-2 define relación initial, successor o independent. Initial se admite solo en ámbito nuevo (rol, familia, país, año) y es único; successor exige predecessor_id explícito, ámbito compatible y fecha estrictamente posterior. Independent requiere referencias explícitas y prueba por archivo/hash, contrastada por adaptador confiable, que vincule el nuevo artefacto con hashes de los antecedentes; una etiqueta no basta. En transición debe cubrir todos los antecedentes de su ámbito en el bundle anterior. Una evidencia independiente descubierta después puede tener fecha anterior si su independencia está acreditada; no se impone cronología de sucesión a esa raíz.

Se preservan todas las filas y el hash externo del bundle anterior. IDs nuevos o predecesor nulo no evaden el ámbito previo. Se rechazan ciclos, referencias incompatibles, sustituciones y borrados. Los instantes se comparan en UTC como racionales exactos, conservando fracciones incluso inferiores al microsegundo, sin float. Fechas inválidas, nulas o sin zona producen ContractError. La función temporal se adapta del helper MEX auditado, sin importar ni ejecutar maquinaria MEX.

Estas reglas no acreditan resultados ni admisión. La presente entrega añade lectores institucionales acotados y pruebas con bytes reales en solo lectura, además de fixtures aisladas. La independencia documental no se presume: el adaptador específico debe aportar su prueba autenticada cuando se use esa relación; la cadena INEI se trata como sucesión. D2 2015–2023, D6 2023, dominio de datos de cuatro países con consumo por caso preregistrado, denominadores, soportes y límites numéricos permanecen intactos.

## Integración S2 de 19/09/2026 — cláusula coordinada

S1 fue emitido el 19/09/2026: paquete `3bac05fd56b710899c1822aebb125435bacf65d24cfa917d646702ae6babd439`, manifiesto `b7ab84b3589d5f5e3b0c47a2deeb1c8742d4102208df7f5cd230b1dd9f07cc96`, cadena de 45 paquetes, 11 suites/1030 pruebas efectivas y consumidor estricto V2 aceptado. El alcance sigue siendo MEX histórico, sin elegibilidad cuantitativa. v49 conserva bytes, autor y fecha aprobados; no es un borrador pendiente. S2 se integra y prueba sobre una copia de ese S1 real. La emisión aislada usa consentimiento ficticio de fixture; en el original no se emite S2 ni se atribuye consentimiento nuevo.

El catálogo CA2-2, sus 60 tablas, 16 contratos JSON, fórmulas y claves estrictas se conservan byte a byte. Los anexos `contratos/EXTENSIONES_S2.md`, `contratos/EVIDENCIA_INSTITUCIONAL_S2.md`, `contratos/PROTOCOLO_ENVOLVENTE_LAMBDA_PI_S2.md` y `contratos/AUTORIDAD_PER_CANDIDATA.json` forman parte del nuevo manifiesto normativo. La evidencia no es admisión; los lectores candidatos no son productores D2/D6; una aprobación documental S2 tampoco autoriza correr el modelo.

La compatibilidad propia conserva una política candidata sin aprobación interna y exige un recibo S2 separado, anclado externamente junto con la identidad esperada del autor. El publicador `herramientas/congelamiento/s2_publicador.py`, integrado al CLI `congelar.py`, prepara el manifiesto completo heredando los campos y pines S1 y sustituyendo únicamente los metadatos de la sucesión S2. Selecciona exactamente estos tres planes activos; los planes anteriores conservan rol histórico. El consumidor D6 despacha S2 a la verificación estricta de archivos instalados, recibo, manifiesto, selección y cadena. La integración técnica se demuestra exclusivamente en aislamiento mediante CLI y compuerta exterior real de once suites históricas más descubrimiento S2. La aprobación real e incorporación operativa permanecen pendientes; el PASS técnico no habilita admisión ni ejecución científica.

La toolchain enumera los módulos instalados y sus dependencias de prueba. El orden de derivación es código/contratos/planes → manifiesto normativo y toolchain → política → recibo real externo → paquete y arista. Ningún nodo se incluye a sí mismo. Se preserva el orden documental S1 y se añaden miembros S2 ordenados, sin duplicados. Una modificación produce otra política por contenido. La promoción prepara y verifica todos los bytes, revalida las entradas después de la compuerta y antes de promover, registra una transacción recuperable y sustituye el JSON al final. Una transacción pendiente bloquea consumo; la recuperación restaura JSON, Markdown, selección y ledger anteriores. No se afirma atomicidad física de múltiples archivos.

`validadores/institucional.py` extrae las proyecciones de los cinco snapshots fijados y los hechos institucionales por hash; comprueba identidades publicadas y propaga intervalos racionales desde primitivas. El lector conserva GOS/MI combinado en Chile y el cero semántico PER sin escribir raw. `validadores/ca2_key.py` conecta los metadatos CA2 validados con la clave candidata macro-ca2-v1: bundle, caso, escenario, vectores D2/D6, contexto, país, bloque laboral, coordenadas comunes, protocolo y huellas técnicas. No cambia omega ni la clave estructural; no inventa precision_evidence para E1/E2. El productor numérico que consumirá estas claves es trabajo futuro.

La matriz de pendientes está en `review/MATRIZ_PAISES.md`; la secuencia y destinos exactos en `review/INCORPORACION_FUTURA_S2.md`. A1–A7 y C-A2 permanecen elegidas; no se solicita otra elección científica. La revisión requerida es de los bytes candidatos, correspondencias y autoridad PER propuesta. No se envían consultas ni se repiten las tres preguntas PER resueltas. D2 conserva primaria 2023 y sensibilidad 2015–2023 por vintage; D6 conserva exclusivamente 2023.
