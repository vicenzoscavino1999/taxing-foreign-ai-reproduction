## 6.2 Los nueve números adimensionales

`(a, θ, ρ, β̃, δ̃, κ̃_0, η_d, η_f, φ)`, con `β̃=β/γ`, `δ̃=δz_m^{θ−1}/γ`, `κ̃_0=κ_0z_m^{ρ−1}/γ`.

| # | Parámetro | Gobierna | Naturaleza |
|---|---|---|---|
| 1 | `a` | Cola Pareto de tamaños | Declarado con soporte |
| 2 | `θ` | Curvatura del ocultamiento | Declarado |
| 3 | `ρ` | Elasticidad del pago al tamaño; la de pagos es `a−ρ` | Declarado, conjunto con `κ̃_0` |
| 4 | `β̃` | Nivel del costo de ocultamiento | Declarado |
| 5 | `δ̃` | Escala del ocultamiento, normalizada | Declarado |
| 6 | `κ̃_0` | Nivel de gasto en IA, normalizado | Declarado, conjunto con `a`, `ρ` |
| 7 | `η_d` | Elasticidad de reporte doméstico | Declarado |
| 8 | `η_f` | Elasticidad de reporte transfronterizo | Declarado |
| 9 | `φ` | Incidencia proveedor→usuario | Escenario recorrido |

**Dos objetos para `a`, sin sustitución silenciosa.**
`a_structural_support=[1.1,2.5]` pertenece al escenario estructural Pareto
global. El rango Hill país se representa con
`a_empirical_diagnostic_status`, `a_empirical_low` y `a_empirical_high`, y se
deriva únicamente de umbrales admisibles. TC-1 asigna
`excluded_unknown_topcoding` y dos nulos cuando `topcode_status=unknown`, sin
alterar el soporte estructural; D20 gobierna solo el diagnóstico empírico.

Las opciones de top-coding se rotulan **TC-1/TC-2/TC-3** para no colisionar con
las tolerancias numéricas T1/T2/T3. Esta versión adopta TC-1; TC-2 exigiría
documentación fuente-específica y TC-3 un estimador censurado validado en una
sucesión futura.

**Compuerta de unidades, obligatoria.** `δ̃ ≠ δ`. Con `z_m=0.5` y `θ=2`, `δ̃=δ/2`. Toda tabla que reporte uno de los dos **debe** reportar el otro, o ninguno. Esta compuerta existe porque el error ya ocurrió: una tabla de soportes tenía la columna rotulada `δ̃` conteniendo el primitivo `δ`.

## 6.3 Las ocho ecuaciones de observación y su estado asignado

Estados permitidos, exhaustivos y excluyentes. **Son cuatro**:

1. **MEDIDO** — fuente con universo, unidad, denominador y horizonte declarados.
2. **OBJETIVO DE MEDICIÓN** — ruta de medición identificada pero **no ejecutada**; lleva fallback obligatorio.
3. **ESCENARIO** — rango declarado sin ancla externa, recorrido por envolvente.
4. **LIMITACIÓN** — no se resuelve, y **la afirmación dependiente se retira del paper**.

| Fila | Objeto | Ecuación | Estado asignado | Justificación |
|---|---|---|---|---|
| **a** | `λ_π` | `s_Π/(1−q_{pot})` | **ESCENARIO** — cota estructural ejecutable | Se construye con componentes de tres naturalezas —`s̄_L` medido, `q_{pot}` y `φ_F^Y` internos, `η_w`/`η_H`/`s_T^{marg}` declarados— pero **la fila entera hereda el estado del componente más débil**. Una cota construida con un declarado es una cota, no una medición |
| **b** | `s_AI` | `Pagos_IA = Pagos_{digitales}·s_AI` | **ESCENARIO** | BaTIS mide servicios digitales, no IA. No existe clasificación que separe IA del agregado |
| **c** | `s_FN` | `Pagos_{IA,no-nexus} = Pagos_IA·s_FN` | **ESCENARIO** | Compra directa contra filial, reseller o facturación local no es observable por país sin participación por proveedor |
| **d** | **Disponibilidad institucional del instrumento** — y nada más | ¿Está disponible la retención para ese par fuente–residencia? → determina si `j=f` y `j=df` entran en `\mathcal T_{c,j}` | **OBJETIVO DE MEDICIÓN**, con fallback en §6.3.1 | **La fila ya NO mide `c_{legal}`** (§4.1). Lo verificable en fuente primaria es la **existencia** del instrumento, que es una pregunta discreta. **La evidencia de trazabilidad NO es un segundo estado de esta fila:** vive en el protocolo de `η_f` (§10.11), que es donde se decide si calibra, ordena o no hace nada |
| **e** | `φ` | `φ_c = Σ_{p,h}ω_{cph}φ_{cph}` | **ESCENARIO** | Cláusulas clasificables, pesos de mercado no disponibles |
| **f** | `(κ̃_0,ρ,adopción)` | `Pagos/B_{pot} = κ̃_0E[ζ^ρ1\{adopta\}]/E[ζ]` | **LIMITACIÓN con la evidencia vigente; ESCENARIO conjunto restringido solo si en una sucesión futura el crosswalk y D19 son admisibles** | La adopción es **endógena**; no admite división directa, y una masa residual no acota pagos sin la ruta A o B de D19 |
| **g** | Pareto global | `F(z)=1-(z_m/z)^a`, `a_structural_support=[1.1,2.5]` | **ESCENARIO estructural (`pass_scenario`)** | TC-1 separa el soporte estructural del diagnóstico empírico; con top-coding `unknown`, fija `a_empirical_diagnostic_status=excluded_unknown_topcoding` y extremos nulos. M3 retira la dimensión cola–cuerpo: `mixture_status=not_applicable_m3`, `omega_tail=null`, `body_dist_id=null` |
| **h** | Universo y pesos | `M_c = Σ_h w_{ch}M_{ch}` | **LIMITACIÓN** mientras no exista mapeo documentado establecimiento→empresa legal | WBES es `establishment_only_unmapped`: no identifica `M_c`, pesos de firmas ni cobertura nacional |

**El cuarto estado.** Se añade **OBJETIVO DE MEDICIÓN** porque las filas (d) y (h) no están medidas: son la **ruta prevista**, condicionada a que el plan de datos la complete. Llamarlas MEDIDO antes de medirlas es exactamente el tipo de sobredeclaración que este plan prohíbe en otros lados.

**Regla de fallback, obligatoria.** Toda fila en OBJETIVO DE MEDICIÓN lleva un fallback declarado:

| Fila | Si el plan de datos la cierra | Si no la cierra |
|---|---|---|
| **d** | MEDIDO *(disponibilidad del instrumento)* | Ver **§6.3.1** — el fallback es **asimétrico** y no se resume en una línea |
| **h** | MEDIDO, únicamente tras documentar el mapeo establecimiento→empresa legal en una sucesión futura | **LIMITACIÓN**, con las afirmaciones retiradas abajo |

**Diagnóstico PRE-D3.** La evidencia adquirida no permite hoy construir
`source_mass`, `mapped_mass_in_target_unit`, `target_mass`, `M_c`, cobertura y
residual sobre empresas legales de manera homogénea en los cuatro países. En
consecuencia, (f) queda en LIMITACIÓN mientras no exista un crosswalk productivo
y D19 admisible; (g) conserva Pareto global como escenario estructural, pero
TC-1 excluye el diagnóstico Hill si el top-coding es `unknown` y M3 elimina la
mezcla ejecutable; y (h) queda en LIMITACIÓN. No se degrada ni se rellena una
ausencia en silencio.

**Afirmaciones retiradas exactamente.** Para (f) se retiran una
`κ̃_0` específica de país, un momento de pagos corregido por residual y una
afirmación de adopción representativa de empresas legales mientras falten el
crosswalk productivo y D19. Para (g) se retiran un rango Hill empírico de país
cuando `topcode_status=unknown` y toda sensibilidad cola–cuerpo ejecutable; no
se retira el escenario Pareto global ni su soporte estructural. Para (h) se
retiran `M_c` medido, pesos de empresas, cobertura nacional de empresas,
comparabilidad internacional de masa empresarial y toda reponderación posterior
que consuma esos objetos.
### 6.3.1 Disponibilidad del instrumento — lectura económica

La unidad bilateral, los dominios jurídicos y la regla de clasificación no se
definen aquí. Gobiernan V5 §§3–6 y el esquema normalizado del plan de datos
§§0.PRE-D4.2–0.PRE-D4.4.

La lectura económica es que un indicador nacional único puede ocultar
heterogeneidad por residencia y categoría jurídica. La disponibilidad sigue
siendo discreta: D-4 no estima una fracción de cobertura. Cuando la evidencia
no identifica el estado real, los escenarios condicionales no permiten un
titular sobre el país.

### 6.3.2 De la disponibilidad al modelo — lectura económica

El mapeo normativo a j=d/f/df gobierna exclusivamente en V5 §7 y su
materialización gobierna en el plan de datos §0.PRE-D4.5. Para interpretar
resultados basta una precaución: conditional_full y conditional_none no son
cotas. Ampliar el alcance jurídico puede ampliar el menú fiscal y, a la vez,
cambiar adopción y formalidad; sin monotonicidad demostrada no se ordena C_2.

Por la misma razón, promediar filas MIXED o UNKNOWN introduciría una cobertura
continua no identificada. La extensión con cobertura parcial queda fuera del
baseline. Los campos, hashes y estados de salida pertenecen solo al plan de
datos; su ejecución pertenece solo al plan de reproducción.


**Nota sobre la exclusividad de los estados.** Un estado se asigna **a nivel de fila**, no de componente. Una fila construida con componentes medidos, internos y declarados **hereda el estado del componente más débil**. La v2 asignaba `MEDIDO + ESCENARIO` a la fila (a), violando la regla de exclusividad en la misma tabla que la enunciaba.

**Objetivo de pagos `P^{target}`, construido con las filas (b) y (c) — y solo con ellas:**

$$P^{target}_{c}=Pagos_{digitales,c}\;s_{AI,c}\;s_{FN,c}$$

**No es "la base trazable" ni incluye la fila (d).** La v2 lo llamaba base trazable de las filas (b)–(d) y le multiplicaba `c_{legal}` y `c_{trace}`. Ninguno de los dos pertenece aquí:

- **`c_{trace}` no es factor.** La teoría ya tiene el reporte transfronterizo endógeno `q^*(\tau_f)=x_f^{\eta_f}`; un factor externo contaría dos veces la misma fricción (compuerta H13). Lo que la trazabilidad observada puede hacer con `η_f` sigue la **regla condicional** de §10.11.
- **`c_{legal}` no está activo** en el baseline: `c_{legal}=1` (§7.3.2, compuerta H22).

`P^{target}` es el **lado izquierdo del momento de calibración (10)**, no una base gravable. Es un objetivo construido con dos escenarios, no un dato observado.

**La fila (e) queda deliberadamente fuera de esta ecuación.** `φ` es incidencia, no tamaño de base. Mezclarla dentro confundiría **cuánto se puede gravar** con **quién soporta la carga**, que es exactamente la distinción exigida por N2.

---

# 7. Ecuaciones operativas del diseño

Esta sección es la especificación contra la que se escribe el código. Cada ecuación se numera y el código la referencia por número.

## 7.1 Normalización
