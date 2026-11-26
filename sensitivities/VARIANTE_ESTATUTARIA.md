# Incidencia estatutaria y pago formal

La sensibilidad de la sección 5.1 cambia la fracción de la carga que asume el usuario formal. Con la asignación lineal (E11) el usuario paga la fracción φ. Bajo la cláusula estatutaria de *gross-up*, paga la fracción ω del impuesto sobre un pago declarado. En esta sensibilidad se supone que también asume esa misma fracción del costo real de ocultar un pago.

Sea `x = 1 − τ_f`. Por unidad de pago neto, el comprador entrega `x^(−φ)`, el Estado retiene `τ_f x^(−φ)` y el proveedor recibe `x^(1−φ)`. La participación del comprador en la retención es

    ω(τ_f, φ) = (1 − x^φ) / τ_f,     ω(0, φ) = φ.

Si la carga conjunta por unidad de pago es `τ̃_f`, el costo formal pasa de `κ₀(1 + φ τ̃_f)` a `κ₀(1 + ω τ̃_f)`. El costo informal sigue siendo `κ₀`. Para φ = 0 y φ = 1, las dos reglas coinciden.

Al cambiar quién soporta la carga, la declaración óptima de la coalición sigue siendo `q* = x^η_f`. El pago formal sí cambia para valores interiores de φ. Así puede cambiar la decisión de adoptar formalmente y, en el diseño neto, la deducción de ese pago en la base doméstica. El modelo vuelve a evaluar las decisiones de las empresas y la recaudación en cada par de tasas.

`incidencia_estatutaria.py` evalúa ω y sus cotas. `construir_variante.py` aplica la regla al núcleo utilizado por el certificador. La [guía de escenarios](README.md) indica cómo reproducir la comparación. El ejercicio de la sección S6.2 que modifica el costo de ocultamiento en un contrato de *gross-up* completo está en las [extensiones](extensions/README.md).
