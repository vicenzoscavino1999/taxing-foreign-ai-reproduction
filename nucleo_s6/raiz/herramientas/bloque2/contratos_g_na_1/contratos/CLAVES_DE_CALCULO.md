# Identidad común y claves de cálculo

**BORRADOR NO APROBADO.** Especificación mecánica de serialización; no cambia parámetros ni ecuaciones. CLAVES_DE_CALCULO.json contiene campos/tipos/listas exactas y predicados. Todas las claves son SHA256 de la preimagen JSON compacta canónica, sin LF. Los números van como cadenas decimales finitas exactas normalizadas; no se redondean. Objetos se ordenan por clave ASCII; filas de valores por parameter_id; dependencias por role; duplicados/campos extras/nulos no previstos se rechazan.

## K1. Estado común

primitive_values_sha256 autentica únicamente primitivas comunes de omega_values: trece estructurales (nueve ejes,gamma,z_m,t,c_legal), coordenadas macro(pi,eta_w,eta_H),gain_share y topes declarados. omega_id=OMG:+H({kind:omega-identity-v2,support_set_id,scenario_id,primitive_values_sha256}). Las etiquetas declarativas no se confunden con autorización. Cambios de snapshot/código/tolerancia no alteran ese estado económico común; sí invalidan caches afectados. Derivados comunes auditables se reconstruyen pero no se incorporan como entradas a este hash. Datos nacionales y C2/lambda/G no son filas de omega_values.

## K2. Estructura

frontier_context.structural_key_payload contiene la proyección de trece primitivas estructurales,design_v,instrument_j,dominio fiscal efectivo,theory_sha256 y las seis huellas técnicas(contract,code,method,tolerances,configuration,environment). structural_key_sha256=H(payload). Las tasas optimizadas son argumentos: point-v2 añade tau_d,tau_f,side,branch_id. Un omega tiene varios contextos por diseño/menú; por eso tampoco se conserva una clave estructural única en omega. País/snapshot no entran a esta clave. Reusar C2 exige dominio efectivo idéntico y verificaciones jurídicas/autoridad del contexto receptor; igualdad de hash no da autorización.

## K3. Macro nacional

lambda_pi_envelope lleva macro_key_sha256,macro_key_payload y national_state_sha256. El payload especifica country_id,eta_w_block,proyección(a,rho,kappa_tilde,pi_iva,pi_otros_productos,pi_produccion,eta_w,eta_H),estado nacional,cuatro dependencias autenticadas,protocolo y seis huellas técnicas. Las dependencias tienen role,manifest_path,manifest_sha256,artifact_path,artifact_sha256,record_pk; roles exactos d2_snapshot,d6_snapshot,precision,joint_domain. Se resuelven en manifests fijados del país; rutas son POSIX relativas al proyecto autenticado. No se consultan punteros mutables.

national_state contiene primitivas fuente completas,cuatro shares y hash del dominio conjunto; éste conserva correlaciones y denominador común. Se comprueba su reproducción con las fuentes, no solo la existencia de un hash. national_state_sha256=H(national_state). Distintos puntos de incertidumbre nacional pueden compartir omega: se distinguen por esta identidad y clave macro. La unicidad macro y de cell_context se amplía para no colapsarlos. Esto representa la incertidumbre ya exigida; no crea escenarios económicos nuevos.


## K3b. Macro condicional (enmienda candidata CA2-4)

Para las filas de la vía condicional (E1/E2) el payload es `macro-ca2-v2` con los campos exactos de `schemas.macro_ca2`:
bundle_sha256, case_id, scenario, preregistration_id, case_type, country_set, country_id, anchor_year, d2_vector_sha256,
d6_vector_sha256, context_sha256, common_values_sha256, eta_w_block, protocol_sha256 y technical. La clave identifica el bundle
C-A2, el caso preregistrado con su contexto de celda (diseño-menú-caso D4), los vectores publicados y el omega común; por eso
una aplicación principal, una comparación internacional y una revisión E2 con las mismas entradas de un país nunca comparten
clave. La validación no se limita a nombres de campos y al hash: resuelve el bundle, la fila de entradas, el caso, los
vectores (familia, año, representación) y el archivo de contexto, y exige igualdad con la celda que enlaza la fila. Esta rama
no afirma precisión institucional; no se reutilizan claves macro-v2 estrictas mediante evidencia de precisión inventada.

## K4. Confrontación y reutilización

cell_context almacena national_state_sha256 y expected_macro_key_sha256. El join a lambda exige país,omega,bloque,run y ambas identidades exactamente iguales; no se acepta otro país aunque produzca el mismo número. El join a techo exige país,omega,diseño,instrumento,caso/hash de disponibilidad y run. Se rehashean los payloads y verifican sus proyecciones. Las dimensiones externas de celda siguen completas y su requerimiento usa esa lambda,gain_share y crosswalk. La estrategia define también payload external y confrontation; ninguna clave se construye mezclando extremos incompatibles.

Un snapshot nacional nuevo siempre cambia su clave macro por los hashes de dependencia, aunque los valores coincidan. Manteniendo las dependencias estructurales constantes, el hash estructural permanece idéntico; cambiar código,método,tolerancias,configuración,entorno o contrato invalida los caches pertinentes. No se duplican cálculos estructurales para resolver una deficiencia de identidad.

## K5. Inventario sin autorreferencia

contract_sha256 autentica bytes exactos de contratos/contract_manifest.json, que enumera los contratos/anexos,los tres planes y review/ESTRATEGIA_DE_CALCULO.md desde una sola raíz: esta entrega. Las referencias escritas aquí son nombres, no valores de una clave calculada dependiente del manifiesto. El manifiesto excluye sí mismo y no incluye resultados con sus propias claves. Aprobación futura debe cubrir su hash y todas sus entradas exactas; no hay aprobación en esta ronda.
