# Especificación previa G-NA-1 — propuesta técnica candidata

Escrita antes de modificar productor/consumidores. Alcance: ensayo aislado, sin adopción científica de NA165, sin R3 ni sucesión oficial.

Una fila G por cell_id conserva quantity_id G:<cell_id>, niveles 0/1, result_ref a la confrontación y evidence_ref. Estado nuevo not_applicable, método instrument_unavailable_authenticated, coverage_complete=false, valores/cota/topologías nulos y verdict_changes=0. La tolerancia original se conserva como parámetro del método; no afirma una medición. Evidencia kind=convergence/status=limitation, error_bound=null, tabla/PK de la misma confrontación. Nunca pass numérico.

Autoridad: producto D7 íntegro y su dependencia d4_model_case_map autenticada por SHA-256; EV.D4.MATRIX del source_evidence autenticado de D7 fija availability_matrix_hash. El mapa debe resolver exactamente una fila país/menú/caso conditional_none, con quantitative_use conditional_scenario_no_foreign_leg y availability_assumed=true. No se deduce indisponibilidad de la mera ausencia de magnitudes. Las fuentes sintéticas continúan siendo sintéticas, ligadas al mundo de prueba y al freeze-run.

Relaciones: celda única, confrontación única, techo único y frontera única; cruce de país, omega, run, diseño, instrumento, caso y matriz; disponibilidad falsa en celda/techo y metadatos concordantes con D4. Confrontación y techo not_applicable/INSTRUMENT_NOT_AVAILABLE; C2/K1/G/error/argumentos del supremo nulos y no_verdict. Referencias/evidencia únicas exactas. Ausencia, duplicación, autoridad alterada, referencias rotas, datos numéricos contradictorios o incomplete real se rechazan.

Contrato: copia nueva herramientas/bloque2/contratos_g_na_1, manifiesto propio con antecedente CA2-4; catálogo y documento de reglas actualizados exclusivamente allí. Autoridad ficticia del candidato referencia este manifiesto. Autoridades S3/S4/S5 congeladas y contratos oficiales permanecen intactos. Productor emite NA solo con contrato candidato; validador común comprueba autoridad y relaciones; D8 Q07 permite exclusivamente NA verificada y conserva su distinción semántica. Readiness/exportación dependen además de todos los demás gates. Los contratos antiguos conservan incomplete para esa ruta.

Preparación S5: histórico autenticado con tres diferencias y cobertura separada del código actual. Productos nacionales: contexto de prueba explícito con predecesores verificables y autoridad separada; no eliminar versiones, tolerar colisiones ni fingir un puntero histórico ausente.

Geometría: registrar nivel configurado y efectivo calculado por la función existente; no cambiar matemática/configuración.
