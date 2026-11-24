# Variante de incidencia estatutaria (formulada, sin ejecutar)

Encargo del autor (2026-11-22): formular la variante que sustituiría a E11 y dejarla sin ejecutar. No se escribió código de la variante ni se calculó ningún techo con ella.

Notación del manuscrito:
- x_f = 1 − τ_f;
- q* = x_f^{η_f};
- τ̃_f = τ_f x_f^{η_f−φ} + c_f(1 − x_f^{η_f}) es la carga efectiva de la coalición usuario–proveedor por unidad de pago mundial (ecuación foreign-burden-sum);
- s_P = (x_f^φ − x_f)/τ_f (provider-share).

## 1. Qué sustituye

Con E11, el adoptante formal soporta la fracción φ de la carga de la coalición y el proveedor la fracción 1 − φ:

    k_F^{E11}(τ_f) = κ0 (1 + φ τ̃_f).                                         (kf)

## 2. Variante: quién soporta qué

Por unidad de pago mundial κ0 z^ρ:

- **Fracción reportada q*.** Rige la cláusula de gross-up.
  - El usuario paga el bruto κ0 x_f^{−φ}.
  - El Estado retiene τ_f κ0 x_f^{−φ}.
  - El proveedor recibe κ0 x_f^{1−φ}.
  - Respecto del pago sin impuesto, el usuario soporta κ0 (x_f^{−φ} − 1) y el proveedor κ0 (1 − x_f^{1−φ}). Su suma es la recaudación τ_f κ0 x_f^{−φ}, de la que el usuario soporta la fracción 1 − s_P y el proveedor la fracción s_P.
- **Fracción no reportada 1 − q*.** Se paga el neto κ0, sin retención. El coste real de ocultamiento c_f(1 − q*) no lo reparte ninguna norma; se reparte por supuesto: el usuario soporta χ_U y el proveedor 1 − χ_U.
- **Elección de q*.** Sigue siendo conjunta: la coalición minimiza su carga total q τ_f x_f^{−φ} + c_f(1 − q), que la cláusula de gross-up no cambia. Por eso q* = x_f^{η_f} y τ̃_f no cambian, y tampoco B_f = q* κ0 x_f^{−φ} W_F, B_d, R ni s_P. **Solo cambia el pago que entra en las decisiones reales.**

Forma general:

    k_F^{S}(τ_f) = κ0 [ 1 + q* (x_f^{−φ} − 1) + χ_U c_f(1 − q*) ].          (E11-S general)

**Variante recomendada.** El ocultamiento se reparte en la misma proporción que el impuesto que evita: χ_U = 1 − s_P. Así, toda la carga de la coalición se reparte con la fracción estatutaria del usuario:

    ω(τ_f, φ) ≡ 1 − s_P(τ_f, φ) = (1 − x_f^φ)/τ_f,   ω(0, φ) = φ,

    k_F^{S}(τ_f) = κ0 [ 1 + ω(τ_f, φ) τ̃_f(τ_f) ].                            (E11-S)

El proveedor soporta (1 − ω) τ̃_f = s_P τ̃_f. La variante es (kf) con φ sustituido por ω(τ_f, φ).

Para el código conviene la forma φ · E(φ l_f) / E(l_f), con l_f = log1p(−τ_f) y E(y) = expm1(y)/y. No tiene singularidad en τ_f = 0, y E > 0 en toda la recta. Se comprobó en `cargo_usuario.py` que coincide con la definición.

## 3. Pago que entra en la decisión de adopción

El adoptante formal paga k_F^S z^ρ; el informal sigue pagando κ0 z^ρ, porque su pago no es rastreable. En el modelo:

- **Beneficios formales con adopción:** π_F1^G = x_d β z + (1 − τ̃_d) γ z − k_F^S z^ρ y π_F1^N = x_d β z + (1 − τ̃_d)(γ z − k_F^S z^ρ).
- **Funciones de estado H_G y H_N:** usan k_F^S − κ0 = κ0 ω τ̃_f en lugar de κ0 φ τ̃_f.
- **Base real del diseño neto:** A_N = ∫ (γ z − k_F^S z^ρ) D_F^N dF, que deduce el pago económico de la variante.

Lo demás no cambia: la elección de reporte, la base rastreable, la recaudación y s_P.

## 4. Propiedades y casos límite

- **Orden:** ω ∈ [φ, 1], porque x^φ es cóncava en x, y por tanto k_F^S ≥ k_F^{E11}. Con la variante, la retención grava más la formalidad que con E11.
- **Monotonía en la tasa:** ω no decrece en τ_f, porque 1 − x_f^φ es convexa en τ_f y vale 0 en τ_f = 0. Además, dk_F^S/dτ_f = κ0 (ω' τ̃_f + ω τ̃_f') ≥ 0, con ω' = [φ x_f^{φ−1} τ_f − (1 − x_f^φ)]/τ_f².
- **Primer orden:** k_F^S − k_F^{E11} = κ0 (ω − φ) τ̃_f = O(τ_f²). Las dos asignaciones coinciden a primer orden en la tasa.
- **φ = 0 (absorción del proveedor):** ω = 0 y k_F^S = κ0. La retención no altera las decisiones reales, igual que con E11.
- **φ = 1 (gross-up completo):** ω = 1 y k_F^S = κ0 (1 + τ̃_f), igual que con E11.
- **Condición de esquinas en la forma general:** la parte reportada coincide sola en las esquinas, porque x^0 − 1 = 0 y x^{−1} − 1 = τ_f x_f^{−1}. Las dos esquinas se recuperan si y solo si χ_U(τ_f, 0) = 0 y χ_U(τ_f, 1) = 1.
  - χ_U = 1 − s_P cumple esa condición, y también χ_U = φ, que reparte el ocultamiento como E11.
  - χ_U = 1, en cambio, no recupera φ = 0, porque cargaría el ocultamiento al usuario aun cuando el proveedor absorbe el impuesto.
  - El ocultamiento es de segundo orden en τ_f, así que la elección de χ_U solo afecta a ese orden.
- **Sin ocultamiento (η_f ↓ 0, q* = 1):** k_F^S = κ0 x_f^{−φ}, que es exactamente el gross-up estatutario. En ese límite se midieron el 5 % y el 12 % de la Observación rem:E11-statutory.
- **Cociente de cargos:** con la variante recomendada, el cargo E11 al usuario dividido por el estatutario es exactamente φ/ω, con o sin ocultamiento. En los testigos (cargo_usuario.json):

| Testigo | φ | τ_f = 0,60 | τ_f = 0,30 | τ_f = 0,15 |
|---|---|---|---|---|
| Diseño bruto (G) | 0,8755 | E11 cobra 4,78 % menos | 2,07 % | 0,98 % |
| Diseño neto (N) | 0,667 | 12,48 % | 5,49 % | 2,61 % |

Son diferencias en el cargo al usuario por unidad reportada, no en el techo. **El efecto sobre el techo queda por calcular.** Su signo no está garantizado en general: un k_F mayor reduce la adopción formal y W_F, pero también cambia E_0 y la deducción del diseño neto.

## 5. ¿Admite el certificador actual la variante?

**No tal como está; la adaptación es acotada.** La maquinaria de certificación es genérica en el pago formal y no necesita cambios: rama y cota, aritmética de intervalos con redondeo hacia afuera, curvas de salto, encierros de momentos y control del error. E11 está codificada en pocos sitios; el resto del código consume `kF`.

Para el techo en un punto estructural fijo, que es lo que usa este piloto, son cinco sitios:
- `model.py`:
  - `k_formal` (l. 164–165);
  - `pair_trinomials`: `kF` (l. 300) y el coeficiente κ0 φ τ̃_f de «F1-I1» del diseño G (l. 310).
- `encierros_modelo.py`:
  - `tax`: `kF` (l. 242);
  - `trinomials`: `phitf` (l. 260).

Para los encierros sobre cajas de parámetros estructurales, que se necesitan para un máximo sobre el soporte, hay dos sitios más en `motor_theta.py`: `tax_ad` (l. 96) y `trinomials` (l. 114).

Qué habría que hacer:
1. **ω en aritmética puntual y encierrada.**
   - Puntual: −expm1(φ l)/τ, con ω(0) = φ.
   - Encierrada: φ · E(φ l)/E(l), con los operadores `ad_E` y `div` ya existentes, que propagan el gradiente respecto de (τ_d, τ_f, φ).
   - En los dos casos, sustituir φ por ω en los siete sitios.
2. **Hacerlo aditivo.** La variante va en un módulo o paquete aparte, como copia derivada de los archivos tocados. Los archivos actuales de `paper2b` y sus huellas quedan idénticos byte a byte. Eso mantiene válidas las 3.708 llamadas del Paso 3 sin repetirlas. Además, la regla se marca en la clave estructural (por ejemplo, `incidence_rule = statutory_proportional`) para que sus techos no se mezclen con los de E11 en ninguna caché.
3. **Pruebas.**
   - La ruta E11 queda intacta: mismas huellas y los techos guardados de los testigos se reproducen bit a bit.
   - La variante es idéntica a E11 en φ ∈ {0, 1}, y la diferencia es O(τ_f²) cerca de 0.
   - El encierro de ω es correcto: puntos aleatorios dentro de cajas caen dentro de su encierro.
4. **Teoría.** Revisar los resultados que usan la forma lineal (kfprime). El signo k_F' ≥ 0 se mantiene; las expresiones cerradas, como las elasticidades y la derivada de k_F, cambian.

**Coste esperado.** Con la variante escrita, un techo en un testigo fijo cuesta lo mismo que en este piloto: unos 0,05 s. El máximo sobre el soporte es otra escala de cálculo y no se ha medido.
