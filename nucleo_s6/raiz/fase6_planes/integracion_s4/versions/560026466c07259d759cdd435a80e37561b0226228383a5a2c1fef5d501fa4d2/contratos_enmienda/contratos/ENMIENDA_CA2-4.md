# Enmienda candidata CA2-4 (2026-09-29) — SIN ACTIVACIÓN

## Motivo

CA2-3 (`eda3d6e5…`) describe en `lambda_pi_envelope` solo la clave macro estricta `macro-v2`, mientras que la rama
condicional elegida en C-A2 (E1/E2) produce `macro-ca2-v2` (validadores/ca2_key.py, extensiones_s2.json). El paquete B del
bloque 2 ya producía esas filas; el catálogo no las cubría. Esta enmienda integra la rama condicional en el contrato sin
tocar la rama estricta.

## Alcance exacto

1. `catalogo_contratos.json`: las reglas de `lambda_pi_envelope` distinguen la rama estricta (texto anterior, sin cambios de
   fondo) y la rama condicional con sus uniones semánticas obligatorias. `catalog_version` y `ca2.version` nuevas.
2. `CLAVES_DE_CALCULO.json`: esquema `macro_ca2` (campos, orden y tipos) y formas `country_list`, `scenario_conditional`,
   `d2_year`. `macro-v2` no cambia.
3. Representación legible coordinada: `CONTRATOS_D7_B_D8.md` (mismas reglas, nota de enmienda) y `CLAVES_DE_CALCULO.md`
   (sección K3b).
4. `CORRESPONDENCIA_CA2-3_CA2-4.csv`: hash de cada archivo antes y después.

No cambia columnas, tipos, PK/FK, datos, soportes, ecuaciones, países, cuantificadores ni criterios de aceptación.

## Compatibilidad

- CA2-3 conserva sus bytes y su hash; sus consumidores actuales (S3, D2, D6 v2, bundles) no cambian.
- Un consumidor que produzca o lea filas `macro-ca2-v2` debe autenticar ESTE manifiesto (hash propio); el hash de CA2-3 no
  cubre estos bytes.
- La autoridad sucesora S4 candidata fija el hash de esta enmienda como contrato de D7/B/D8.
- La rama condicional no afirma precisión: la separación entre precisión estricta (E0/E3) y datos publicados condicionados
  (E1/E2) se mantiene.
