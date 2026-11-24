# Fase 4b — Modelo baseline formal, versión 2.2

**Versión canónica: 2.2.**

## QUÉ CAMBIA vs v1.2

| Objeto | v1.2 | v2 | Consecuencia |
|---|---|---|---|
| Renta previa | La firma sólo existía al adoptar IA | $y_0(z)=\beta z$ y existe un estatus fiscal previo | La adopción puede formalizar o desformalizar una firma y revelar base previa |
| Reporte doméstico | Factor reducido $x_d^{\eta_d}$ aplicado después de las decisiones reales | Elección $r\in[0,1]$ con costo convexo; $r^*=x_d^{\eta_d}$ y carga privada $\widetilde\tau_d$ | El reporte altera los umbrales reales; no es un factor contable añadido ex post |
| Reporte extranjero | $q=x_f^\eta$ reducido | Elección microfundada del remisor; $q^*=x_f^{\eta_f}$ | Reporte y gross-up quedan separados y auditables |
| Incidencia extranjera | $K=\kappa(1+\phi\tau_f)$ común a formales e informales | La coalición minimiza obligación más ocultamiento; el usuario soporta $\phi\widetilde\tau_f$ y el proveedor $(1-\phi)\widetilde\tau_f$ | El término mecánico $-\phi$ permanece en $\varepsilon_{ff}$ y $k_F'$ queda no negativo |
| Trazabilidad | La antigua base de pagos incluía a todos los adoptantes | Sólo pagos de adoptantes formales son retenibles | Aparece $\varepsilon_{fd}$ y puede morir el máximo G histórico |
| Demanda | Una unidad por adoptante; $\rho>0$ era robustez | $\kappa(z)=\kappa_0z^\rho$, $\rho\in[0,1]$, es central | La base de pagos transfronterizos trazables es un momento truncado de orden $\rho$ |
| Escudo G | $\varepsilon_{df}^G=0$ en Ulyssea | El gross-up diferencial mueve el corte formal-informal | El escudo sólo reaparece si el costo formal e informal coincide |
| Equivalente recaudatorio | Denominadores dependientes del diseño | $B_{pot}=\int\gamma z\,dF$, independiente de tasas y diseño | G y N se comparan contra un único potencial tecnológico |
| Frontera institucional | Máximo o supremo sobre dominios variables | $\sup$ sobre $[0,\bar\tau_d]\times[0,\bar\tau_f]$ | No se presupone que una discontinuidad por desempate alcance el supremo |

La v1.2 queda como referencia histórica. Ninguna ecuación de v2 debe interpretarse como una edición retroactiva de ella.

## TABLA DELTA: v2.1 → v2.2

| Resultado u objeto v2.1 | Cambio v2.2 | Consecuencia exacta |
|---|---|---|
| Costo extranjero formal $k_F=\kappa_0[1+q(x_f^{-\phi}-1)]$ | El costo de ocultamiento entra en $\widetilde\tau_f=\min_q\{w_fq+c_f(1-q)\}$ y $k_F=\kappa_0(1+\phi\widetilde\tau_f)$ | Las ganancias privadas incluyen toda la carga de la coalición y la reparten entre usuario y proveedor |
| Envolvente sólo doméstica | $\widetilde\tau_f'=q^*\partial w_f/\partial\tau_f$ | El movimiento de los cortes reales por $\tau_f$ queda ligado al mismo problema que genera $q^*$ |
| Signo de $k_F'$ ambiguo | $k_F'=\kappa_0\phi\widetilde\tau_f'\geq0$ | En un corte superior regular, $\varepsilon_{df}^G\geq0$; el escudo reaparece exactamente con $\phi=0$ |
| P5 con costo privado incompleto | La FOC fiscal con $W_F$ fijo no cambia; los términos reales sí cambian por el nuevo $k_F$ | $1/(1+\eta_f-\phi)$ y el amortiguador sobreviven sólo en el caso de momento formal fijo |
| Ventanas contra $1/(1+\eta_d)$ | Ventanas contra $\widetilde\tau_d(\bar\tau_d)$ | La existencia se decide dentro del compacto institucional, no en un límite estatutario inalcanzable |
| Interioridad N sin distinguir dominios | Máximo no restringido en $[0,1]$ y condición separada para $[0,\bar\tau_d]$ | Si el máximo no restringido queda fuera, la esquina se diagnostica con la derivada lateral en $\bar\tau_d$ |
| $B_f$ llamada base extranjera | $B_f$ es la **base de pagos transfronterizos reportados y trazables** | N2 impide leer $B_f$ como utilidades o renta mundial del proveedor |
| Captura de rentas implícita en $\phi$ | $s_P=(x_f^\phi-x_f)/\tau_f$ | La incidencia sobre rentas se reporta aparte de la base fiscal y converge a $1-\phi$ cuando $\tau_f\downarrow0$ |

## 0. Supuestos

**S1 (economía pequeña y proveedor con rentas).** El proveedor de IA es extranjero, no tiene nexus fiscal local y puede absorber con sus rentas la fracción $1-\phi$ de la carga extranjera efectiva. El precio mundial $\kappa_0z^\rho$ es el pago contractual sin impuesto. La base fiscal bruta reportada puede diferir de ese pago por gross-up.

**S2 (heterogeneidad).** Hay una masa uno de firmas con $z\in[z_m,\infty)$, $z_m>0$, y

\[
F(z)=1-\left(\frac{z_m}{z}\right)^a,
\qquad
f(z)=az_m^az^{-a-1},
\qquad a>1.
\tag{0.1}
\]

**S3 (renta previa y ganancia de IA).** Antes de adoptar, la firma obtiene

\[
y_0(z)=\beta z,
\qquad \beta\geq0.
\tag{0.2}
\]

La adopción añade

\[
g(z)=\gamma z,
\qquad \gamma>0.
\tag{0.3}
\]

$\beta=0$ elimina la renta previa, pero no deshace por sí solo los demás cambios de arquitectura.

**S4 (demanda de IA).** El pago mundial no gravado es

\[
K_I(z)=\kappa_0z^\rho,
\qquad
\kappa_0>0,\qquad \rho\in[0,1].
\tag{0.4}
\]

Como $a>1\geq\rho$, los momentos de pago son finitos.

**S5 (instrumentos y soporte institucional).** Las tasas pertenecen a

\[
(\tau_d,\tau_f)
\in[0,\bar\tau_d]\times[0,\bar\tau_f],
\qquad
0<\bar\tau_d<1,\qquad0<\bar\tau_f<1.
\tag{0.5}
\]

Defina

\[
x_d\equiv1-\tau_d,
\qquad
x_f\equiv1-\tau_f.
\tag{0.6}
\]

**S6 (informalidad de firma).** Una firma informal oculta su actividad y soporta

\[
c_I(z)=\delta z^\theta,
\qquad
\delta>0,\qquad\theta>1.
\tag{0.7}
\]

La sección 5.5 sustituye localmente (0.7) por una penalidad proporcional.

**S7 (estatus previo).** Sin IA, la firma compara formalidad e informalidad. La formal paga $\tau_dy_0$; la informal no paga ese impuesto y soporta $c_I$. El estatus previo es una elección económica, no una etiqueta exógena.

**S8 (dos diseños domésticos).** El diseño G grava el incremento bruto $g(z)$. El diseño N grava el incremento neto $g(z)-K_F(z)$, siempre que sea positivo en el régimen considerado. La deducción de N sigue el costo económico formal para aislar la elección gross-versus-net de la trazabilidad de la retención.

**S9 (ETI doméstica).** Una firma formal elige $r\in[0,1]$, la fracción reportada del incremento gravable. El ocultamiento cuesta $c_d(1-r)$ por unidad de base. $c_d(0)=0$, $c_d'>0$ para ocultamiento positivo y $c_d''>0$.

**S10 (reporte extranjero y coalición).** La coalición usuario formal--proveedor elige $q\in[0,1]$, la fracción reportada del pago. El costo de ocultamiento extranjero es convexo, proporcional al pago mundial y separable de la elección de estatus. La carga total de la coalición incluye tanto la obligación sobre lo reportado como el costo real de ocultar; ninguna de las dos piezas desaparece de las ganancias privadas.

**S11 (gross-up e incidencia de la carga efectiva).** La base bruta de una unidad reportada es

\[
K_R(z)=\kappa_0z^\rho x_f^{-\phi},
\qquad \phi\in[0,1].
\tag{0.8}
\]

$\phi=0$ significa absorción completa por el proveedor y $\phi=1$ gross-up completo. La obligación por unidad mundial reportada es $w_f(\tau_f)=\tau_fx_f^{-\phi}$. Una unidad no reportada usa la base neta $K_I(z)$ y escapa de la retención. Una vez minimizada obligación más ocultamiento, el adoptante formal soporta la fracción $\phi$ de $\widetilde\tau_f$ y el proveedor la fracción $1-\phi$ mediante sus rentas.

**S12 (base de pagos transfronterizos reportados y trazables).** Sólo los pagos de adoptantes formales son potencialmente retenibles. $B_f$ es la base bruta de pagos transfronterizos que son simultáneamente reportados y trazables; no representa utilidades contables ni renta económica mundial del proveedor. Los pagos de firmas informales no dejan la trazabilidad necesaria y se tratan como no reportados.

**S13 (elección y desempate).** La firma compara no adopción con adopción formal e informal. Si la mejor adopción empata con no adoptar, no adopta. Si las dos formas de adopción empatan estrictamente por encima de no adoptar, el desempate es formal. Los límites laterales se reportan cuando esta convención crea una discontinuidad puntual.

**S14 (base incremental).** La recaudación asociada a IA se mide respecto del estatus fiscal previo. La renta $y_0$ entra positivamente sólo si la adopción formaliza una firma y negativamente si la adopción la desformaliza. El impuesto ya pagado por una firma previamente formal no se atribuye a IA.

**S15 (destino de lo ocultado).** El baseline importador usa $t=0$. La proposición del amortiguador permite $t\in[0,1)$ sobre pagos no reportados.

**S16 (equilibrio parcial).** No hay entrada, salarios endógenos, dinámica de productividad, elección pública de enforcement ni respuesta del precio mundial fuera del reparto de incidencia resumido por $\phi$.

**S17 (regiones suaves).** Las fórmulas de elasticidad se aplican donde las bases son positivas, los cortes son simples y las bases son continuamente diferenciables. En tangencias y kinks se usan derivadas laterales.

**S18 (integrabilidad y límites).** Todos los momentos utilizados tienen orden menor que $a$. Los límites $\eta_d\downarrow0$, $\rho\downarrow0$ o $\beta\downarrow0$ se toman después de derivar el modelo con parámetros interiores.

## 1. Reporte microfundado e incidencia

### 1.1 ETI doméstica exacta

Sea

\[
u_d\equiv1-r
\tag{1.1}
\]

la fracción ocultada. Se busca un costo que produzca

\[
r^*(\tau_d)=x_d^{\eta_d},
\qquad \eta_d>0.
\tag{1.2}
\]

De (1.1)–(1.2):

\[
u_d^*=1-x_d^{\eta_d}.
\tag{1.3}
\]

Despejando (x_d):

\[
1-u_d^*=x_d^{\eta_d},
\tag{1.4}
\]

\[
x_d=(1-u_d^*)^{1/\eta_d}.
\tag{1.5}
\]

Como $\tau_d=1-x_d$:

\[
\tau_d
=1-(1-u_d^*)^{1/\eta_d}.
\tag{1.6}
\]

La condición de primer orden del problema

\[
\min_{r\in[0,1]}
\left\{\tau_dr+c_d(1-r)\right\}
\tag{1.7}
\]

es

\[
\tau_d-c_d'(1-r)=0.
\tag{1.8}
\]

Por (1.6), el costo requerido debe satisfacer

\[
c_d'(u)
=1-(1-u)^{1/\eta_d}.
\tag{1.9}
\]

Integrando desde cero y usando (c_d(0)=0):

\[
c_d(u)
=\int_0^u\left[1-(1-v)^{1/\eta_d}\right]dv,
\tag{1.10}
\]

\[
c_d(u)
=u-\int_0^u(1-v)^{1/\eta_d}dv,
\tag{1.11}
\]

\[
\int_0^u(1-v)^{1/\eta_d}dv
=\frac{\eta_d}{1+\eta_d}
\left[1-(1-u)^{(1+\eta_d)/\eta_d}\right].
\tag{1.12}
\]

Por tanto,

\[
\boxed{
c_d(u)
=u-\frac{\eta_d}{1+\eta_d}
\left[1-(1-u)^{(1+\eta_d)/\eta_d}\right].
}
\tag{1.13}
\]

Derivando (1.9):

\[
c_d''(u)
=\frac{1}{\eta_d}(1-u)^{1/\eta_d-1}>0.
\tag{1.14}
\]

La FOC es suficiente. Sustituyendo (1.9) en (1.8):

\[
\tau_d=1-(1-u_d^*)^{1/\eta_d},
\tag{1.15}
\]

\[
1-\tau_d=(1-u_d^*)^{1/\eta_d},
\tag{1.16}
\]

\[
(1-\tau_d)^{\eta_d}=1-u_d^*=r^*.
\tag{1.17}
\]

Así se obtiene exactamente

\[
\boxed{r^*(\tau_d)=x_d^{\eta_d}.}
\tag{1.18}
\]

Defina la carga privada efectiva por unidad de base:

\[
\widetilde\tau_d(\tau_d)
\equiv
\min_r\{\tau_dr+c_d(1-r)\}.
\tag{1.19}
\]

En el óptimo, $r=x_d^{\eta_d}$ y $u=1-x_d^{\eta_d}$. Primero:

\[
\tau_dr^*
=(1-x_d)x_d^{\eta_d}
=x_d^{\eta_d}-x_d^{1+\eta_d}.
\tag{1.20}
\]

Por (1.13):

\[
c_d(1-x_d^{\eta_d})
=1-x_d^{\eta_d}
-\frac{\eta_d}{1+\eta_d}
\left(1-x_d^{1+\eta_d}\right).
\tag{1.21}
\]

Sumando (1.20) y (1.21):

\[
\widetilde\tau_d
=1-x_d^{1+\eta_d}
-\frac{\eta_d}{1+\eta_d}
\left(1-x_d^{1+\eta_d}\right),
\tag{1.22}
\]

\[
\boxed{
\widetilde\tau_d(\tau_d)
=\frac{1-x_d^{1+\eta_d}}{1+\eta_d}.
}
\tag{1.23}
\]

El teorema de envolvente aplicado a (1.19) da

\[
\widetilde\tau_d'(\tau_d)
=\left.\frac{\partial}{\partial\tau_d}
[\tau_dr+c_d(1-r)]\right|_{r=r^*},
\tag{1.24}
\]

\[
\boxed{
\widetilde\tau_d'(\tau_d)=r^*(\tau_d)=x_d^{\eta_d}.
}
\tag{1.25}
\]

También se verifica directamente:

\[
\frac{d}{d\tau_d}
\frac{1-(1-\tau_d)^{1+\eta_d}}{1+\eta_d}
=\frac{(1+\eta_d)(1-\tau_d)^{\eta_d}}{1+\eta_d}
=x_d^{\eta_d}.
\tag{1.26}
\]

El límite $\eta_d\downarrow0$ produce $r^*\to1$ y $\widetilde\tau_d\to\tau_d$.

### 1.2 Reporte extranjero exacto

La obligación por unidad de pago mundial reportado, antes de normalizar por $\kappa_0z^\rho$, es

\[
w_f(\tau_f)
=\tau_fx_f^{-\phi}.
\tag{1.27}
\]

El remisor elige

\[
\min_{q\in[0,1]}
\left\{w_f(\tau_f)q+c_f(1-q)\right\}.
\tag{1.28}
\]

Se desea

\[
q^*(\tau_f)=x_f^{\eta_f},
\qquad \eta_f>0.
\tag{1.29}
\]

Sea $u_f=1-q$. De (1.29):

\[
x_f=(1-u_f)^{1/\eta_f}.
\tag{1.30}
\]

Como $w_f=(1-x_f)x_f^{-\phi}$, el costo marginal requerido es

\[
\boxed{
c_f'(u)
=\left[1-(1-u)^{1/\eta_f}\right]
(1-u)^{-\phi/\eta_f}.
}
\tag{1.31}
\]

Equivalentemente,

\[
c_f(u)
=\int_0^u
\left[1-(1-v)^{1/\eta_f}\right]
(1-v)^{-\phi/\eta_f}dv.
\tag{1.32}
\]

Para verificar convexidad, escriba $x=(1-u)^{1/\eta_f}$. Entonces

\[
c_f'(u)=(1-x)x^{-\phi}.
\tag{1.33}
\]

Derivando respecto de $x$:

\[
\frac{d[(1-x)x^{-\phi}]}{dx}
=-x^{-\phi}-\phi(1-x)x^{-\phi-1},
\tag{1.34}
\]

\[
\frac{d[(1-x)x^{-\phi}]}{dx}
=-x^{-\phi-1}[\phi+(1-\phi)x]<0.
\tag{1.35}
\]

Además,

\[
\frac{dx}{du}
=-\frac{1}{\eta_f}x^{1-\eta_f}<0.
\tag{1.36}
\]

Multiplicando (1.35) y (1.36):

\[
\boxed{c_f''(u)>0.}
\tag{1.37}
\]

La FOC de (1.28) es

\[
w_f(\tau_f)-c_f'(1-q)=0.
\tag{1.38}
\]

Por (1.31), esta igualdad se cumple si y sólo si

\[
1-\tau_f=(1-(1-q))^{1/\eta_f}=q^{1/\eta_f},
\tag{1.39}
\]

\[
\boxed{q^*(\tau_f)=x_f^{\eta_f}.}
\tag{1.40}
\]

Defina ahora la carga efectiva extranjera de la coalición por unidad de pago mundial:

\[
\boxed{
\widetilde\tau_f(\tau_f)
\equiv
\min_{q\in[0,1]}
\{w_f(\tau_f)q+c_f(1-q)\}.
}
\tag{1.40a}
\]

En $q^*=x_f^{\eta_f}$, la obligación reportada es

\[
w_fq^*
=\tau_fx_f^{-\phi}x_f^{\eta_f}
=\tau_fx_f^{\eta_f-\phi}.
\tag{1.40b}
\]

El costo de ocultamiento óptimo se obtiene de (1.32). Cambiando variable de $v$ a $y=1-v$:

\[
c_f(1-q^*)
=\int_{q^*}^{1}
\left[y^{-\phi/\eta_f}
-y^{(1-\phi)/\eta_f}\right]dy.
\tag{1.40c}
\]

Sea $\alpha\equiv\eta_f-\phi$. Si $\alpha\neq0$:

\[
c_f(1-q^*)
=\frac{\eta_f}{\alpha}(1-x_f^\alpha)
-\frac{\eta_f}{\alpha+1}(1-x_f^{\alpha+1}).
\tag{1.40d}
\]

Sumando (1.40b) y (1.40d):

\[
\boxed{
\widetilde\tau_f
=\tau_fx_f^\alpha
+\frac{\eta_f}{\alpha}(1-x_f^\alpha)
-\frac{\eta_f}{\alpha+1}(1-x_f^{\alpha+1}),
\qquad \alpha\neq0.
}
\tag{1.40e}
\]

Si $\alpha=0$, la primera integral de (1.40c) es logarítmica y

\[
\boxed{
\widetilde\tau_f
=(1-\eta_f)(1-x_f)-\eta_f\ln x_f,
\qquad \eta_f=\phi.
}
\tag{1.40f}
\]

Por el teorema de envolvente aplicado a (1.40a):

\[
\widetilde\tau_f'(\tau_f)
=q^*(\tau_f)\frac{\partial w_f(\tau_f)}{\partial\tau_f}.
\tag{1.40g}
\]

Como $w_f=\tau_fx_f^{-\phi}$:

\[
\frac{\partial w_f}{\partial\tau_f}
=x_f^{-\phi}+\phi\tau_fx_f^{-\phi-1}
=x_f^{-\phi-1}(x_f+\phi\tau_f).
\tag{1.40h}
\]

Por tanto:

\[
\boxed{
\widetilde\tau_f'
=q^*x_f^{-\phi-1}(x_f+\phi\tau_f)
=x_f^{\eta_f-\phi-1}(x_f+\phi\tau_f)>0.
}
\tag{1.40i}
\]

La identidad contable privada queda cerrada:

\[
\boxed{
\widetilde\tau_f
=\underbrace{w_fq^*}_{\text{obligación}}
+\underbrace{c_f(1-q^*)}_{\text{recurso real de ocultamiento}}.
}
\tag{1.40j}
\]

### 1.3 Pago formal medio y consistencia del gross-up

La coalición soporta $\widetilde\tau_f$ por unidad de pago mundial. S11 asigna la fracción $\phi$ al adoptante formal y $1-\phi$ al proveedor. Por tanto, el costo privado del usuario formal es

\[
K_F(z)
=\kappa_0z^\rho
\left[1+\phi\widetilde\tau_f(\tau_f)\right],
\tag{1.41}
\]

\[
\boxed{
K_F(z)=k_F(\tau_f)z^\rho,
\qquad
k_F(\tau_f)
=\kappa_0[1+\phi\widetilde\tau_f(\tau_f)].
}
\tag{1.42}
\]

La carga absorbida por las rentas del proveedor es $\kappa_0z^\rho(1-\phi)\widetilde\tau_f$. Las dos cargas suman exactamente la obligación más el costo de ocultamiento:

\[
\kappa_0z^\rho
\left[\phi\widetilde\tau_f+(1-\phi)\widetilde\tau_f\right]
=\kappa_0z^\rho\widetilde\tau_f
=\kappa_0z^\rho[w_fq^*+c_f(1-q^*)].
\tag{1.42a}
\]

La diferencia formal--informal de costo para el usuario es

\[
\boxed{
\Delta k_f(\tau_f)
\equiv k_F(\tau_f)-\kappa_0
=\kappa_0\phi\widetilde\tau_f(\tau_f).
}
\tag{1.43}
\]

Derivando (1.42) y usando la envolvente (1.40i):

\[
 k_F'(\tau_f)
=\kappa_0\phi\widetilde\tau_f'(\tau_f),
\tag{1.44}
\]

\[
\boxed{
k_F'
=\kappa_0\phi q^*x_f^{-\phi-1}
(x_f+\phi\tau_f)\geq0.
}
\tag{1.47}
\]

El signo ya no es ambiguo. Es estrictamente positivo si $\phi>0$ y $\tau_f<1$, y es cero si $\phi=0$. Éste es el cierre que faltaba en v2.1: $c_f$ determina simultáneamente reporte, costo privado e incidencia.

**Remark N2 — base fiscal versus captura de rentas.** $B_f$ es la base de pagos transfronterizos reportados y trazables. No es una medida de utilidades del proveedor. La incidencia sobre sus rentas se mide aparte. Por unidad reportada, la base bruta es $\kappa_0z^\rho x_f^{-\phi}$, la recaudación es $\kappa_0z^\rho\tau_fx_f^{-\phi}$ y el ingreso neto del proveedor es $\kappa_0z^\rho x_f^{1-\phi}$. Su pérdida de renta es

\[
L_P
=\kappa_0z^\rho[1-x_f^{1-\phi}].
\tag{1.48}
\]

Dividiendo por la recaudación de esa transacción:

\[
s_P(\tau_f,\phi)
=\frac{1-x_f^{1-\phi}}{\tau_fx_f^{-\phi}},
\tag{1.49}
\]

\[
\boxed{
s_P(\tau_f,\phi)
=\frac{x_f^\phi-x_f}{\tau_f}.
}
\tag{1.50}
\]

Las esquinas son

\[
s_P(\tau_f,0)=1,
\qquad
s_P(\tau_f,1)=0.
\tag{1.51}
\]

Usando $x_f^\phi=(1-\tau_f)^\phi=1-\phi\tau_f+o(\tau_f)$:

\[
\boxed{
\lim_{\tau_f\downarrow0}s_P(\tau_f,\phi)=1-\phi.
}
\tag{1.52}
\]

$s_P$ es la participación del recaudo estatutario soportada por el proveedor debido al gross-up incompleto; $1-\phi$ es, además, la regla de reparto de la carga efectiva total de la coalición. Ambos objetos coinciden marginalmente cuando $\tau_f\downarrow0$, pero no son la misma razón a tasas finitas. Esta separación implementa la Nota de Alcance N2 de `PREGUNTA_CONGELADA.md`.

## 2. Estatus previo, adopción y particiones

### 2.1 Las cuatro ganancias privadas

Sin adoptar y siendo formal:

\[
\pi_{F0}(z)
=y_0(z)-\tau_dy_0(z),
\tag{2.1}
\]

\[
\boxed{\pi_{F0}(z)=x_d\beta z.}
\tag{2.2}
\]

Sin adoptar y siendo informal:

\[
\boxed{\pi_{I0}(z)=\beta z-\delta z^\theta.}
\tag{2.3}
\]

El valor sin IA es

\[
\boxed{V_0(z)=\max\{\pi_{F0}(z),\pi_{I0}(z)\}.}
\tag{2.4}
\]

En G, la adoptante formal paga el costo de IA y la carga efectiva sobre $\gamma z$:

\[
\pi_{F1}^G
=x_d\beta z+\gamma z-k_Fz^\rho
-\widetilde\tau_d\gamma z,
\tag{2.5}
\]

\[
\boxed{
\pi_{F1}^G
=x_d\beta z+(1-\widetilde\tau_d)\gamma z-k_Fz^\rho.
}
\tag{2.6}
\]

En N:

\[
\boxed{
\pi_{F1}^N
=x_d\beta z
+(1-\widetilde\tau_d)(\gamma z-k_Fz^\rho).
}
\tag{2.7}
\]

La adoptante informal no reporta la transacción, no soporta pass-through y oculta la firma:

\[
\boxed{
\pi_{I1}(z)
=\beta z+\gamma z-\kappa_0z^\rho-\delta z^\theta.
}
\tag{2.8}
\]

La elección final es

\[
J(z)
=\arg\max\{V_0(z),\pi_{F1}^v(z),\pi_{I1}(z)\},
\qquad v\in\{G,N\},
\tag{2.9}
\]

con la regla S13.

### 2.2 Estatus previo

La diferencia previa formal-informal es

\[
\Delta_0(z)
\equiv\pi_{F0}(z)-\pi_{I0}(z),
\tag{2.10}
\]

\[
\Delta_0(z)
=x_d\beta z-\beta z+\delta z^\theta,
\tag{2.11}
\]

\[
\boxed{
\Delta_0(z)=\delta z^\theta-\tau_d\beta z.
}
\tag{2.12}
\]

Para $\beta>0$ y $\tau_d>0$, el cruce satisface

\[
\delta z^\theta=\tau_d\beta z,
\tag{2.13}
\]

\[
\delta z^{\theta-1}=\tau_d\beta,
\tag{2.14}
\]

\[
\boxed{
z_0(\tau_d)
=\left(\frac{\tau_d\beta}{\delta}\right)^{1/(\theta-1)}.
}
\tag{2.15}
\]

Por tanto,

\[
[z_m,z_0):I0,
\qquad
[\max\{z_m,z_0\},\infty):F0.
\tag{2.16}
\]

Si $\beta=0$, ambas ganancias previas son cero y S13 asigna todas las firmas a F0. Éste es un cierre, no una afirmación de que toda firma real sea formal.

### 2.3 Umbrales de adopción condicionales

Una firma previamente informal compara I1 con I0:

\[
\pi_{I1}-\pi_{I0}
=\gamma z-\kappa_0z^\rho.
\tag{2.17}
\]

Para $0\leq\rho<1$, el corte satisface

\[
\gamma z=\kappa_0z^\rho,
\tag{2.18}
\]

\[
z^{1-\rho}=\frac{\kappa_0}{\gamma},
\tag{2.19}
\]

\[
\boxed{
z_{AI}
=\left(\frac{\kappa_0}{\gamma}\right)^{1/(1-\rho)}.
}
\tag{2.20}
\]

Una firma previamente formal compara F1 con F0. En G:

\[
\pi_{F1}^G-\pi_{F0}
=(1-\widetilde\tau_d)\gamma z-k_Fz^\rho.
\tag{2.21}
\]

El corte es

\[
(1-\widetilde\tau_d)\gamma z=k_Fz^\rho,
\tag{2.22}
\]

\[
\boxed{
z_{AF}^G
=\left[
\frac{k_F}{(1-\widetilde\tau_d)\gamma}
\right]^{1/(1-\rho)}.
}
\tag{2.23}
\]

En N:

\[
\pi_{F1}^N-\pi_{F0}
=(1-\widetilde\tau_d)(\gamma z-k_Fz^\rho).
\tag{2.24}
\]

Como $1-\widetilde\tau_d>0$, el corte satisface

\[
\gamma z=k_Fz^\rho,
\tag{2.25}
\]

\[
\boxed{
z_{AF}^N
=\left(\frac{k_F}{\gamma}\right)^{1/(1-\rho)}.
}
\tag{2.26}
\]

Así, $z_{AF}^N$ sigue siendo independiente de $\tau_d$ condicional en estatus previo, pero depende de $\tau_f$, $q$, $\phi$ y $\rho$.

En el extremo (\rho=1), las potencias de (z) se cancelan. Las tres diferencias relevantes son

\[
\pi_{I1}-\pi_{I0}
=(\gamma-\kappa_0)z,
\tag{2.26a}
\]

\[
\pi_{F1}^G-\pi_{F0}
=[(1-\widetilde\tau_d)\gamma-k_F]z,
\tag{2.26b}
\]

\[
\pi_{F1}^N-\pi_{F0}
=(1-\widetilde\tau_d)(\gamma-k_F)z.
\tag{2.26c}
\]

Por tanto, el pago no genera un corte interior de productividad: cada comparación produce adopción de todas o de ninguna de las firmas del estatus previo correspondiente. Los cortes de estatus de (2.29) y (2.34) aún pueden existir porque (\theta>1).

### 2.4 Formal versus informal después de adoptar

En G:

\[
\Delta_G(z)
\equiv\pi_{F1}^G(z)-\pi_{I1}(z),
\tag{2.27}
\]

\[
\Delta_G
=x_d\beta z+(1-\widetilde\tau_d)\gamma z-k_Fz^\rho
-\beta z-\gamma z+\kappa_0z^\rho+\delta z^\theta,
\tag{2.28}
\]

\[
\boxed{
H_G(z)
\equiv\Delta_G(z)
=\delta z^\theta
-(\tau_d\beta+\widetilde\tau_d\gamma)z
-\Delta k_f z^\rho.
}
\tag{2.29}
\]

En N:

\[
\Delta_N(z)
\equiv\pi_{F1}^N(z)-\pi_{I1}(z),
\tag{2.30}
\]

\[
\Delta_N
=x_d\beta z+(1-\widetilde\tau_d)(\gamma z-k_Fz^\rho)
-\beta z-\gamma z+\kappa_0z^\rho+\delta z^\theta,
\tag{2.31}
\]

\[
\Delta_N
=\delta z^\theta
-(\tau_d\beta+\widetilde\tau_d\gamma)z
+[\kappa_0-(1-\widetilde\tau_d)k_F]z^\rho.
\tag{2.32}
\]

Defina

\[
C_N(\tau_d,\tau_f)
\equiv\kappa_0-(1-\widetilde\tau_d)k_F.
\tag{2.33}
\]

Entonces

\[
\boxed{
H_N(z)
\equiv\Delta_N(z)
=\delta z^\theta
-(\tau_d\beta+\widetilde\tau_d\gamma)z
+C_Nz^\rho.
}
\tag{2.34}
\]

Formal domina si $H_v(z)\geq0$; informal domina si $H_v(z)<0$.

### 2.5 ¿Sobrevive $N\to F\to I\to F$?

Defina $z_L^N<z_U^N$ como dos raíces simples de $H_N(z)=0$. Una condición suficiente para la topología de adopción

\[
N\to F\to I\to F
\tag{2.35}
\]

es la conjunción:

\[
z_{AF}^N\geq\max\{z_m,z_0\},
\tag{2.36}
\]

\[
H_N(z_{AF}^N)>0,
\tag{2.37}
\]

\[
\min_{z>z_{AF}^N}H_N(z)<0,
\tag{2.38}
\]

\[
\lim_{z\to\infty}H_N(z)=+\infty,
\tag{2.39}
\]

y que no exista otro cruce de las ganancias con $V_0$ dentro de cada intervalo. Bajo estas condiciones:

\[
[z_m,z_{AF}^N):N,
\tag{2.40}
\]

\[
[z_{AF}^N,z_L^N):F,
\tag{2.41}
\]

\[
[z_L^N,z_U^N):I,
\tag{2.42}
\]

\[
[z_U^N,\infty):F.
\tag{2.43}
\]

La renta previa hace frágil (2.35). De (2.15):

\[
\frac{\partial z_0}{\partial\beta}>0.
\tag{2.44}
\]

De (2.34), manteniendo tasas y (z) fijos:

\[
\boxed{
\frac{\partial H_N(z)}{\partial\beta}
=-\tau_dz<0.
}
\tag{2.45}
\]

Así, elevar $\beta$ expande el conjunto previamente informal y reduce la ventaja de formalizarse al adoptar. Puede fallar (2.36) o (2.37), desaparecer la primera franja formal y emerger

\[
N\to I\to F.
\tag{2.46}
\]

Sin embargo, como $\theta>1\geq\rho$:

\[
\lim_{z\to\infty}
\frac{\delta z^\theta}
{(\tau_d\beta+\widetilde\tau_d\gamma)z+|C_N|z^\rho}
=+\infty.
\tag{2.47}
\]

Por (2.34) y (2.47), una $\beta$ finita no elimina la formalidad de la cola cuando la adopción formal sigue siendo rentable allí. La topología $N\to F\to I\to F$ sobrevive sólo como régimen paramétrico, no como predicción global.

## 3. Bases, recaudación y matriz suficiente

### 3.1 Indicadores y base incremental

Sea $D_0(z)\in\{0,1\}$ el indicador de estatus previo formal. Sean $D_F^v,D_I^v,D_N^v$ los indicadores de adopción formal, adopción informal y no adopción. Por construcción:

\[
D_F^v+D_I^v+D_N^v=1.
\tag{3.1}
\]

El indicador formal después de la elección es

\[
D_1^v(z)
=D_F^v(z)+D_N^v(z)D_0(z).
\tag{3.2}
\]

La base previa revelada o perdida por el cambio de estatus es

\[
\boxed{
E_0^v
\equiv
\int_{z_m}^\infty
y_0(z)[D_1^v(z)-D_0(z)]dF(z).
}
\tag{3.3}
\]

La base real del incremento de IA es

\[
A_G^v
\equiv
\int_{z_m}^\infty\gamma zD_F^G(z)dF(z),
\tag{3.4}
\]

\[
A_N^v
\equiv
\int_{z_m}^\infty
[\gamma z-k_Fz^\rho]D_F^N(z)dF(z).
\tag{3.5}
\]

Escriba $A_v=A_G^v$ en G y $A_v=A_N^v$ en N. Como sólo el incremento está sujeto a la elección $r$, la base doméstica reportada es

\[
\boxed{
B_d^v
=E_0^v+r^*(\tau_d)A_v.
}
\tag{3.6}
\]

La base de pagos transfronterizos reportados y trazables usa el bruto estatutario y sólo adoptantes formales:

\[
B_f^v
=\int_{z_m}^\infty
q\kappa_0x_f^{-\phi}z^\rho D_F^v(z)dF(z),
\tag{3.7}
\]

\[
\boxed{
B_f^v
=q\kappa_0x_f^{-\phi}W_F^v,
\qquad
W_F^v\equiv\int z^\rho D_F^v(z)dF(z).
}
\tag{3.8}
\]

La recaudación incremental asociada a IA es

\[
\boxed{
R^v(\tau_d,\tau_f)
=\tau_dB_d^v+\tau_fB_f^v.
}
\tag{3.9}
\]

### 3.2 Normalización de elasticidades

Se mantiene la normalización respecto del neto de impuesto:

\[
\boxed{
\varepsilon_{ij}^v
\equiv
\frac{\partial\ln B_i^v}
{\partial\ln x_j},
\qquad i,j\in\{d,f\}.
}
\tag{3.10}
\]

Como

\[
\frac{\partial\ln x_j}{\partial\tau_j}
=-\frac{1}{x_j},
\tag{3.11}
\]

se sigue que

\[
\frac{1}{B_i}
\frac{\partial B_i}{\partial\tau_j}
=-\frac{\varepsilon_{ij}}{x_j},
\tag{3.12}
\]

\[
\boxed{
\frac{\partial B_i}{\partial\tau_j}
=-\frac{\varepsilon_{ij}B_i}{x_j}.
}
\tag{3.13}
\]

### Proposición 1 — suficiencia local

> **Proposición 1.** Bajo S1–S17, dentro de una región suave con $B_d^v>0$ y $B_f^v>0$, la matriz $\boldsymbol\varepsilon^v=\{\varepsilon_{dd}^v,\varepsilon_{df}^v,\varepsilon_{fd}^v,\varepsilon_{ff}^v\}$, junto con tasas y niveles de bases, determina el gradiente local de $R^v$. Un óptimo conjunto interior satisface (3.24). La proposición no garantiza concavidad ni caracteriza kinks.

**Demostración.** Derivando (3.9) respecto de $\tau_d$:

\[
R_d
=B_d+\tau_d\frac{\partial B_d}{\partial\tau_d}
+\tau_f\frac{\partial B_f}{\partial\tau_d}.
\tag{3.14}
\]

Usando (3.13):

\[
R_d
=B_d
-\tau_d\frac{\varepsilon_{dd}B_d}{x_d}
-\tau_f\frac{\varepsilon_{fd}B_f}{x_d},
\tag{3.15}
\]

\[
\boxed{
R_d
=B_d-
\frac{\tau_d\varepsilon_{dd}B_d
+\tau_f\varepsilon_{fd}B_f}{x_d}.
}
\tag{3.16}
\]

Análogamente:

\[
R_f
=B_f+\tau_f\frac{\partial B_f}{\partial\tau_f}
+\tau_d\frac{\partial B_d}{\partial\tau_f},
\tag{3.17}
\]

\[
\boxed{
R_f
=B_f-
\frac{\tau_f\varepsilon_{ff}B_f
+\tau_d\varepsilon_{df}B_d}{x_f}.
}
\tag{3.18}
\]

En un óptimo interior:

\[
R_d=0,
\qquad R_f=0.
\tag{3.19}
\]

Multiplicando (3.16) por (x_d/B_d):

\[
x_d-\tau_d\varepsilon_{dd}
-\tau_f\varepsilon_{fd}\frac{B_f}{B_d}=0.
\tag{3.20}
\]

Multiplicando (3.18) por (x_f/B_f):

\[
x_f-\tau_f\varepsilon_{ff}
-\tau_d\varepsilon_{df}\frac{B_d}{B_f}=0.
\tag{3.21}
\]

Como $x_d=1-\tau_d$:

\[
1
=\tau_d(1+\varepsilon_{dd})
+\tau_f\varepsilon_{fd}\frac{B_f}{B_d}.
\tag{3.22}
\]

Como $x_f=1-\tau_f$:

\[
1
=\tau_f(1+\varepsilon_{ff})
+\tau_d\varepsilon_{df}\frac{B_d}{B_f}.
\tag{3.23}
\]

Por tanto,

\[
\boxed{
\begin{cases}
\displaystyle
\tau_d
=\frac{1}{1+\varepsilon_{dd}
+\varepsilon_{fd}\dfrac{\tau_fB_f}{\tau_dB_d}},\\[10pt]
\displaystyle
\tau_f
=\frac{1}{1+\varepsilon_{ff}
+\varepsilon_{df}\dfrac{\tau_dB_d}{\tau_fB_f}}.
\end{cases}
}
\tag{3.24}
\]

Cada igualdad es implícita y se evalúa en el óptimo. Esto prueba la suficiencia. $\square$

### 3.3 ETI y agregabilidad

Por (3.6):

\[
B_d=E_0+rA.
\tag{3.25}
\]

Derivando respecto de $\ln x_d$:

\[
\frac{\partial B_d}{\partial\ln x_d}
=\frac{\partial E_0}{\partial\ln x_d}
+r\frac{\partial A}{\partial\ln x_d}
+A\frac{\partial r}{\partial\ln x_d}.
\tag{3.26}
\]

De $r=x_d^{\eta_d}$:

\[
\frac{\partial r}{\partial\ln x_d}
=\eta_dr.
\tag{3.27}
\]

Defina

\[
\varepsilon_{dd}^{real}
\equiv
\frac{1}{B_d}
\left[
\frac{\partial E_0}{\partial\ln x_d}
+r\frac{\partial A}{\partial\ln x_d}
\right],
\tag{3.28}
\]

\[
\omega_A
\equiv\frac{rA}{B_d}.
\tag{3.29}
\]

Dividiendo (3.26) por (B_d) y usando (3.27):

\[
\boxed{
\varepsilon_{dd}
=\varepsilon_{dd}^{real}+\omega_A\eta_d.
}
\tag{3.30}
\]

Cuando $\beta=0$, $E_0=0$, $B_d=rA$ y $\omega_A=1$. Entonces:

\[
\boxed{
\varepsilon_{dd}
=\eta_d+\varepsilon_{dd}^{real}.
}
\tag{3.31}
\]

Si además $\varepsilon_{fd}=0$, la primera ecuación de (3.24) da

\[
\tau_d^*
=\frac{1}{1+\varepsilon_{dd}},
\tag{3.32}
\]

\[
\boxed{
\tau_d^*
=\frac{1}{1+\eta_d+\varepsilon_{dd}^{real}}.
}
\tag{3.33}
\]

Éste es el resultado ETI. En el caso general con exposición previa y término cruzado:

\[
\boxed{
\tau_d^*
=\frac{1}{1+\omega_A\eta_d+\varepsilon_{dd}^{real}
+\varepsilon_{fd}\dfrac{\tau_fB_f}{\tau_d^*B_d}}.
}
\tag{3.34}
\]

### Proposición 2 — agregabilidad corregida

> **Proposición 2.** Bajo S1–S18, una región suave, un óptimo interior y una factorización exacta de la base real en componentes iso-elásticos, las elasticidades reales se suman. La fórmula $1/(1+\sum\varepsilon)$ emerge sólo si $E_0=0$ o toda la base comparte el mismo margen ETI, $\varepsilon_{fd}=0$ y no hay interacción residual. Con exposición previa o trazabilidad de pagos transfronterizos condicionada al estatus, la fórmula correcta es (3.34).

**Demostración.** Si

\[
A=A_0\prod_{m=1}^M X_m(x_d),
\tag{3.35}
\]

entonces

\[
\ln A=\ln A_0+\sum_{m=1}^M\ln X_m,
\tag{3.36}
\]

\[
\frac{\partial\ln A}{\partial\ln x_d}
=\sum_{m=1}^M
\frac{\partial\ln X_m}{\partial\ln x_d}.
\tag{3.37}
\]

Si $E_0=0$, (3.31) añade $\eta_d$. Si también $\varepsilon_{fd}=0$, (3.33) sigue de P1. Si alguna condición falla, (3.30) o (3.34) conserva exactamente el share, el residuo real o el término cruzado omitido. $\square$

**Comparación con §5.3 de v1.2.** Allí $q_d=x_d^{\eta_d}$ multiplicaba una base real cuyos umbrales no respondían a $q_d$. Aquí $\widetilde\tau_d$ entra en (2.6), (2.7), (2.29) y (2.34). Por ello $\eta_d$ entra dos veces en objetos distintos: directamente mediante $r$, e indirectamente dentro de $\varepsilon_{dd}^{real}$ a través de $\widetilde\tau_d$. Sumarlos no es doble conteo porque uno es reporte intensivo y el otro respuesta real inducida por la carga efectiva.

## 4. Formas Pareto y crossovers G

### 4.1 Lema de momentos

> **Lema 1 (momentos truncados).** Bajo S2, para cualquier $m<a$ y $z_c\geq z_m$, el momento de orden $m$ por encima de $z_c$ es (4.5). Si $z_c=Cx^{-\chi}$, su elasticidad respecto de $x$ es $\chi(a-m)$. En particular, masa, base doméstica lineal y pagos con demanda $z^\rho$ tienen elasticidades $a\chi$, $(a-1)\chi$ y $(a-\rho)\chi$.

**Demostración.** Por S2:

\[
M_m(z_c)
\equiv\int_{z_c}^{\infty}z^m dF(z),
\tag{4.1}
\]

\[
M_m(z_c)
=az_m^a\int_{z_c}^{\infty}z^{m-a-1}dz.
\tag{4.2}
\]

Como (m-a<0):

\[
\int z^{m-a-1}dz
=\frac{z^{m-a}}{m-a}.
\tag{4.3}
\]

Evaluando límites:

\[
M_m(z_c)
=az_m^a
\left[
0-\frac{z_c^{m-a}}{m-a}
\right],
\tag{4.4}
\]

\[
\boxed{
M_m(z_c)
=\frac{az_m^a}{a-m}z_c^{m-a}.
}
\tag{4.5}
\]

Si $z_c=Cx^{-\chi}$:

\[
M_m(x)
=\frac{az_m^a}{a-m}
C^{m-a}x^{-\chi(m-a)},
\tag{4.6}
\]

\[
M_m(x)
=\frac{az_m^a}{a-m}
C^{m-a}x^{\chi(a-m)}.
\tag{4.7}
\]

Tomando logaritmos y derivando:

\[
\boxed{
\frac{\partial\ln M_m}{\partial\ln x}
=\chi(a-m).
}
\tag{4.8}
\]

Sustituir $m=0,1,\rho$ produce los tres casos. $\square$

### 4.2 Crossover G con ETI, gross-up y trazabilidad

Para obtener una forma cerrada auditable, esta subsección añade

\[
\beta=0,
\qquad \rho=0.
\tag{4.9}
\]

Escriba

\[
u_d\equiv1-\widetilde\tau_d,
\qquad
d_f\equiv k_F-\kappa_0.
\tag{4.10}
\]

El corte de participación formal G de (2.23) es

\[
\boxed{
z_{AF}^G
=\frac{k_F}{u_d\gamma}.
}
\tag{4.11}
\]

La indiferencia formal-informal (2.29) se vuelve

\[
\boxed{
H_G(z)
=\delta z^\theta-\widetilde\tau_d\gamma z-d_f=0.
}
\tag{4.12}
\]

En el crossover se imponen simultáneamente (4.11) y (4.12). De (4.11):

\[
k_F=u_d\gamma z.
\tag{4.13}
\]

Sustituyendo $d_f=k_F-\kappa_0$ en (4.12):

\[
\delta z^\theta-\widetilde\tau_d\gamma z-k_F+\kappa_0=0.
\tag{4.14}
\]

Usando (4.13):

\[
\delta z^\theta
-\widetilde\tau_d\gamma z
-u_d\gamma z
+\kappa_0=0.
\tag{4.15}
\]

Como $u_d=1-\widetilde\tau_d$:

\[
\widetilde\tau_d\gamma z+u_d\gamma z=\gamma z.
\tag{4.16}
\]

Por tanto, la productividad de crossover satisface

\[
\boxed{
\delta z_c^\theta-\gamma z_c+\kappa_0=0.
}
\tag{4.17}
\]

El gross-up no desaparece: entra al mapear (z_c) a una tasa estatutaria. De (4.13):

\[
1-\widetilde\tau_d
=\frac{k_F}{\gamma z_c},
\tag{4.18}
\]

\[
\boxed{
\widetilde\tau_d(\tau_d^c)
=1-\frac{k_F(\tau_f)}{\gamma z_c}.
}
\tag{4.19}
\]

Por (1.23), una raíz estatutaria estrictamente interior al compacto institucional existe sólo si

\[
\widetilde\tau_d(\bar\tau_d)
=\frac{1-(1-\bar\tau_d)^{1+\eta_d}}{1+\eta_d},
\tag{4.19a}
\]

\[
0<1-\frac{k_F}{\gamma z_c}
<\widetilde\tau_d(\bar\tau_d)
=\frac{1-(1-\bar\tau_d)^{1+\eta_d}}{1+\eta_d}.
\tag{4.20}
\]

La igualdad derecha coloca la raíz exactamente en $\bar\tau_d$; no autoriza llamarla interior.

Para $\theta=2$, (4.17) es

\[
\delta z_c^2-\gamma z_c+\kappa_0=0.
\tag{4.21}
\]

El discriminante es

\[
\mathcal D_G
=\gamma^2-4\delta\kappa_0.
\tag{4.22}
\]

Hay dos raíces distintas si y sólo si

\[
\boxed{
\frac{4\delta K_I}{\gamma^2}
=\frac{4\delta\kappa_0}{\gamma^2}<1.
}
\tag{4.23}
\]

La desigualdad es estricta. Con igualdad existe una raíz doble, no dos regímenes adyacentes. Las productividades son

\[
\boxed{
z_c^{\ell,u}
=\frac{\gamma\mp\sqrt{\gamma^2-4\delta\kappa_0}}
{2\delta}.
}
\tag{4.24}
\]

Cada (z_c^j) genera una tasa $\tau_d^j$ mediante (4.19) si cumple (4.20).

### 4.3 Derivadas laterales exactas

Considere la raíz formal-informal superior (z_F) de (4.12), con

\[
H_z(z_F)
=\delta\theta z_F^{\theta-1}
-\widetilde\tau_d\gamma>0.
\tag{4.25}
\]

Diferenciando (H_G(z_F)=0) respecto de $\tau_d$:

\[
H_z(z_F)\frac{dz_F}{d\tau_d}
-\widetilde\tau_d'(\tau_d)\gamma z_F=0.
\tag{4.26}
\]

Por (1.25):

\[
H_z(z_F)\frac{dz_F}{d\tau_d}
-r\gamma z_F=0,
\tag{4.27}
\]

\[
\boxed{
\frac{1}{z_F}\frac{dz_F}{d\tau_d}
=\frac{r\gamma}{H_z(z_F)}>0.
}
\tag{4.28}
\]

En el régimen donde (z_F) es el corte formal activo, el Lema 1 da

\[
B_d^{G,-}
=r\frac{\gamma az_m^a}{a-1}z_F^{1-a},
\tag{4.29}
\]

\[
B_f^{G,-}
=q\kappa_0x_f^{-\phi}
\left(\frac{z_m}{z_F}\right)^a.
\tag{4.30}
\]

Como

\[
\frac{r'}{r}=-\frac{\eta_d}{x_d},
\tag{4.31}
\]

la derivada logarítmica de (B_d^{G,-}) es

\[
\frac{1}{B_d^{G,-}}
\frac{dB_d^{G,-}}{d\tau_d}
=-\frac{\eta_d}{x_d}
+(1-a)\frac{r\gamma}{H_z},
\tag{4.32}
\]

\[
\frac{1}{B_d^{G,-}}
\frac{dB_d^{G,-}}{d\tau_d}
=-\frac{\eta_d}{x_d}
-(a-1)\frac{r\gamma}{H_z}.
\tag{4.33}
\]

Para la base de pagos transfronterizos trazables:

\[
\frac{1}{B_f^{G,-}}
\frac{dB_f^{G,-}}{d\tau_d}
=-a\frac{r\gamma}{H_z}.
\tag{4.34}
\]

Derivando $R=\tau_dB_d+\tau_fB_f$:

\[
R_d^-
=B_d^{G,-}
\left[
1-\frac{\tau_d\eta_d}{x_d}
-\tau_d(a-1)\frac{r\gamma}{H_z}
\right]
-\tau_fB_f^{G,-}a\frac{r\gamma}{H_z}.
\tag{4.35}
\]

Por tanto,

\[
\boxed{\Gamma^-(\tau_d,\tau_f)\equiv R_d^-}
\tag{4.36}
\]

está dado exactamente por el lado derecho de (4.35).

En el régimen de participación formal, (4.11) implica

\[
\ln z_{AF}^G
=\ln k_F-\ln\gamma-\ln u_d.
\tag{4.37}
\]

Con $\tau_f$ fija, (k_F) es constante y

\[
u_d'= -\widetilde\tau_d'=-r.
\tag{4.38}
\]

Así:

\[
\boxed{
\frac{1}{z_{AF}^G}
\frac{dz_{AF}^G}{d\tau_d}
=\frac{r}{u_d}.
}
\tag{4.39}
\]

Repitiendo (4.29)–(4.35) con $r\gamma/H_z$ reemplazado por (r/u_d):

\[
\boxed{
\Gamma^+(\tau_d,\tau_f)
=B_d^{G,+}
\left[
1-\frac{\tau_d\eta_d}{x_d}
-\tau_d(a-1)\frac{r}{u_d}
\right]
-\tau_fB_f^{G,+}a\frac{r}{u_d}.
}
\tag{4.40}
\]

### Proposición 3A-v2 — máximo local condicional, no teorema de $\theta>a$

> **Proposición 3A-v2.** Bajo S1–S18, $\beta=\rho=0$, un crossover G que cumple (4.17)–(4.20), cortes simples y continuidad de las bases, el crossover es un máximo local respecto de los regímenes adyacentes si y sólo si $\Gamma^-\geq0\geq\Gamma^+$. Es estricto si $\Gamma^->0>\Gamma^+$. La condición histórica $\theta>a$ no es suficiente cuando $B_f$ contiene sólo formales o cuando $\eta_d>0$.

**Demostración.** Por definición, un máximo en un kink requiere

\[
R_d^-\geq0,
\qquad R_d^+\leq0.
\tag{4.41}
\]

Las derivaciones (4.35) y (4.40) demuestran que

\[
R_d^-=\Gamma^-,
\qquad
R_d^+=\Gamma^+.
\tag{4.42}
\]

Sustituir (4.42) en (4.41) prueba necesidad y suficiencia lateral. $\square$

Para ver por qué $\theta>a$ dejó de bastar, apague ETI y el diferencial extranjero sólo como cálculo de comparación: $r=1$, $\widetilde\tau_d=\tau_d$, $d_f=0$. Entonces, en el corte formal-informal,

\[
\delta z_F^{\theta-1}=\tau_d\gamma.
\tag{4.43}
\]

Por (4.25):

\[
H_z
=\delta\theta z_F^{\theta-1}-\tau_d\gamma,
\tag{4.44}
\]

\[
H_z
=\theta\tau_d\gamma-\tau_d\gamma
=(\theta-1)\tau_d\gamma.
\tag{4.45}
\]

El componente doméstico de (4.35) se vuelve proporcional a

\[
1-\frac{a-1}{\theta-1}
=\frac{\theta-a}{\theta-1}.
\tag{4.46}
\]

Pero v2 conserva además

\[
-\tau_fB_fa\frac{\gamma}{H_z}<0
\tag{4.47}
\]

porque la base de pagos transfronterizos trazables pierde firmas formales cuando $\tau_d$ sube. Éste es el término que v1.2 no tenía.

### 4.4 Condición global y nuevo $\lambda_f$

En el régimen AF-bajo, el corte es (4.11). Defina

\[
C
\equiv
\frac{\gamma az_m^a}{a-1}
\left(\frac{k_F}{\gamma}\right)^{1-a}>0,
\tag{4.48}
\]

\[
D
\equiv
\tau_fq\kappa_0x_f^{-\phi}
\left(\frac{z_m\gamma}{k_F}\right)^a\geq0.
\tag{4.49}
\]

Por el Lema 1:

\[
B_d^{AF\ell}=rCu_d^{a-1},
\tag{4.50}
\]

\[
\tau_fB_f^{AF\ell}=Du_d^a.
\tag{4.51}
\]

La recaudación es

\[
\boxed{
R^{AF\ell}
=C\tau_dru_d^{a-1}+Du_d^a.
}
\tag{4.52}
\]

Derivando el primer término:

\[
\frac{d}{d\tau_d}[C\tau_dru_d^{a-1}]
=C\left[ru_d^{a-1}
+\tau_dr'u_d^{a-1}
+\tau_dr(a-1)u_d^{a-2}u_d'\right].
\tag{4.53}
\]

Usando $r'=-\eta_dr/x_d$ y (u_d'=-r):

\[
\frac{d}{d\tau_d}[C\tau_dru_d^{a-1}]
=Cru_d^{a-2}
\left[u_d-\frac{\tau_d\eta_du_d}{x_d}
-\tau_d(a-1)r\right].
\tag{4.54}
\]

Para el segundo término:

\[
\frac{d}{d\tau_d}[Du_d^a]
=Da u_d^{a-1}u_d',
\tag{4.55}
\]

\[
\frac{d}{d\tau_d}[Du_d^a]
=-aDru_d^{a-1}.
\tag{4.56}
\]

Sumando:

\[
\frac{dR^{AF\ell}}{d\tau_d}
=ru_d^{a-2}
\left\{
C\left[u_d\left(1-\frac{\tau_d\eta_d}{x_d}\right)
-\tau_d(a-1)r\right]
-aDu_d
\right\}.
\tag{4.57}
\]

El nuevo cociente es

\[
\lambda_f^{v2}
\equiv\frac{aD}{C}.
\tag{4.58}
\]

Sustituyendo (4.48)–(4.49) y cancelando términos:

\[
\boxed{
\lambda_f^{v2}
=(a-1)
\frac{\tau_fq\kappa_0x_f^{-\phi}}{k_F}.
}
\tag{4.59}
\]

Dividiendo el corchete de (4.57) por (C):

\[
\boxed{
G_\ell^{v2}(\tau_d)
=u_d
\left(1-\lambda_f^{v2}
-\frac{\tau_d\eta_d}{x_d}\right)
-\tau_d(a-1)r.
}
\tag{4.60}
\]

Una condición suficiente fácil de auditar para que (4.60) sea no negativa en $[0,\tau_d^\ell]$ es

\[
G_\ell^{v2}(\tau_d^\ell)\geq0,
\tag{4.61}
\]

y

\[
\boxed{
a-\lambda_f^{v2}
-a\eta_d\frac{\tau_d^\ell}{1-\tau_d^\ell}
\geq0.
}
\tag{4.62}
\]

Para justificar (4.62), derive (4.60). Sea

\[
A(\tau_d)
=1-\lambda_f^{v2}
-\eta_d\frac{\tau_d}{x_d}.
\tag{4.63}
\]

Como $d(\tau_d/x_d)/d\tau_d=1/x_d^2$:

\[
A'(\tau_d)=-\frac{\eta_d}{x_d^2}.
\tag{4.64}
\]

Además (u_d'=-r) y $r'=-\eta_dr/x_d$. Por tanto:

\[
(G_\ell^{v2})'
=-rA-u_d\frac{\eta_d}{x_d^2}
-(a-1)r
+(a-1)\tau_d\frac{\eta_dr}{x_d}.
\tag{4.65}
\]

Agrupando los términos en (r):

\[
(G_\ell^{v2})'
=-r
\left[
a-\lambda_f^{v2}
-a\eta_d\frac{\tau_d}{x_d}
\right]
-u_d\frac{\eta_d}{x_d^2}.
\tag{4.66}
\]

Si (4.62) vale en el extremo derecho, también vale antes porque $\tau_d/x_d$ es creciente. Entonces (4.66) es no positiva, y (4.61) implica $G_\ell^{v2}\geq0$ en todo el intervalo.

Si $z_{AF}^G\leq z_m$, la masa formal es uno y

\[
R^{masa\ 1}
=\tau_dr\mathbb E[\gamma z]
+\tau_fq\kappa_0x_f^{-\phi}\mathbb E[z^\rho].
\tag{4.67}
\]

El segundo término no responde a $\tau_d$. El primero satisface

\[
\frac{d}{d\tau_d}[\tau_dr]
=r+\tau_dr',
\tag{4.68}
\]

\[
\frac{d}{d\tau_d}[\tau_dr]
=r\left(1-\frac{\tau_d\eta_d}{x_d}\right),
\tag{4.69}
\]

que es positivo si y sólo si

\[
\boxed{
\tau_d<\frac{1}{1+\eta_d}.
}
\tag{4.70}
\]

La masa constante ya no garantiza crecimiento automático.

> **Corolario 3A-G-v2 (suficiencia global).** Añada a P3A-v2: (i) continuidad en los crossovers; (ii) (4.61)–(4.62), o (4.70) en cada tramo de masa uno, para AF-bajo; (iii) $\Gamma^-(\tau_d,\tau_f)\geq0$ en todo el régimen formal-informal intermedio, no sólo en su extremo; y (iv) la derivada total es no positiva en todo AF-alto. Entonces la raíz superior es un maximizador global en $\tau_d$ para la $\tau_f$ fija. Si cualquiera falla, el corolario no aplica.

**Demostración.** (4.57)–(4.66) dan crecimiento en AF-bajo. La condición (iii) da crecimiento débil hasta el crossover. La condición (iv) da decrecimiento débil después. La continuidad concatena los regímenes. $\square$

El run de v2 muestra por qué la condición (iii) es indispensable: (4.61)–(4.62) se cumplen, pero $\Gamma^-<0$ junto al crossover; el supremo numérico ocurre antes de él.

## 5. Variante N, penalidad proporcional y escudo

### 5.1 Tangencia N con carga efectiva

Antes de especializar, defina

\[
A_N(\tau_d)
\equiv\tau_d\beta+\widetilde\tau_d\gamma.
\tag{5.0a}
\]

Por (2.34):

\[
H_N(z)=\delta z^\theta-A_Nz+C_Nz^\rho.
\tag{5.0b}
\]

Una tangencia general satisface

\[
\delta z_T^\theta-A_Nz_T+C_Nz_T^\rho=0,
\tag{5.0c}
\]

\[
\delta\theta z_T^{\theta-1}
-A_N+\rho C_Nz_T^{\rho-1}=0.
\tag{5.0d}
\]

Multiplicando (5.0d) por (z_T):

\[
A_Nz_T
=\delta\theta z_T^\theta
+\rho C_Nz_T^\rho.
\tag{5.0e}
\]

Sustituyendo (5.0e) en (5.0c):

\[
\delta(1-\theta)z_T^\theta
+(1-\rho)C_Nz_T^\rho=0.
\tag{5.0f}
\]

Para (\rho<1):

\[
\boxed{
C_N
=\frac{\delta(\theta-1)}{1-\rho}
z_T^{\theta-\rho},
\qquad
A_N
=\delta\theta z_T^{\theta-1}
+\rho C_Nz_T^{\rho-1}.
}
\tag{5.0g}
\]

(5.0g), la definición de (C_N) en (2.33) y (1.23) determinan conjuntamente (z_T) y la tasa estatutaria. (\beta) entra en (A_N); (\rho) entra en ambos términos. Para (\rho=1), (5.0f) exige (\delta(1-\theta)z_T^\theta=0), imposible con (z_T>0) y (\theta>1): no hay tangencia doble interior de esta forma, aunque puede haber un único cruce de estatus.

Bajo $\beta=\rho=0$, (2.34) es

\[
\boxed{
H_N(z)
=\delta z^\theta
-\widetilde\tau_d\gamma z
+C_N,
\qquad
C_N=\kappa_0-(1-\widetilde\tau_d)k_F.
}
\tag{5.1}
\]

Una tangencia satisface

\[
H_N(z_T)=0,
\tag{5.2}
\]

\[
H_N'(z_T)=0.
\tag{5.3}
\]

De (5.3):

\[
\delta\theta z_T^{\theta-1}
-\widetilde\tau_d\gamma=0,
\tag{5.4}
\]

\[
\boxed{
\widetilde\tau_d
=\frac{\delta\theta z_T^{\theta-1}}{\gamma}.
}
\tag{5.5}
\]

Sustituyendo (5.5) en (5.2):

\[
\delta z_T^\theta
-\delta\theta z_T^{\theta-1}z_T
+C_N=0,
\tag{5.6}
\]

\[
\delta(1-\theta)z_T^\theta+C_N=0,
\tag{5.7}
\]

\[
\boxed{
C_N(\widetilde\tau_d,\tau_f)
=\delta(\theta-1)z_T^\theta.
}
\tag{5.8}
\]

(5.5) y (5.8) son el sistema general. Como (C_N) depende de $\widetilde\tau_d$ y de (k_F), puede haber cero, una o varias tangencias estatutarias.

Si $\phi=0$, entonces $k_F=\kappa_0$ y

\[
C_N=\kappa_0-(1-\widetilde\tau_d)\kappa_0
=\widetilde\tau_d\kappa_0.
\tag{5.9}
\]

Sustituyendo (5.5) en (5.8):

\[
\frac{\delta\theta z_T^{\theta-1}}{\gamma}\kappa_0
=\delta(\theta-1)z_T^\theta.
\tag{5.10}
\]

Dividiendo por $\delta z_T^{\theta-1}>0$:

\[
\frac{\theta\kappa_0}{\gamma}
=(\theta-1)z_T,
\tag{5.11}
\]

\[
\boxed{
z_T
=\frac{\theta\kappa_0}{\gamma(\theta-1)}.
}
\tag{5.12}
\]

Por (5.5):

\[
\boxed{
\widetilde\tau_{d,N}^{tan}
=\frac{\delta\theta}{\gamma}
\left[
\frac{\theta\kappa_0}{\gamma(\theta-1)}
\right]^{\theta-1}.
}
\tag{5.13}
\]

La tasa estatutaria existe en el interior del compacto institucional sólo si

\[
0<\widetilde\tau_{d,N}^{tan}
<\widetilde\tau_d(\bar\tau_d)
=\frac{1-(1-\bar\tau_d)^{1+\eta_d}}{1+\eta_d}
\tag{5.14}
\]

y la solución de

\[
\widetilde\tau_d(\tau_{d,N}^{tan})
=\widetilde\tau_{d,N}^{tan}
\tag{5.15}
\]

satisface

\[
\boxed{\tau_{d,N}^{tan}\in(0,\bar\tau_d)\subset(0,1).}
\tag{5.16}
\]

### Proposición 3B-v2 — tangencia no equivale a Laffer

> **Proposición 3B-v2.2.** Bajo S1–S18 y una solución de (5.5)–(5.8) que satisface (5.14)–(5.16), la tangencia sólo crea o destruye un intervalo informal y no identifica en general un máximo de recaudación. Puede haber más de una tangencia porque $C_N$ depende de $\widetilde\tau_d$ y del nuevo $k_F(\widetilde\tau_f)$. Si $E_0=0$, $\eta_d>0$, la base real N es continua, acotada y positiva en alguna tasa, el problema no restringido extendido a $[0,1]$ tiene un máximo interior. En el compacto $[0,\bar\tau_d]$, la cota no liga si $\tau_d^u<\bar\tau_d$. Bajo unimodalidad y diferenciabilidad lateral, una derivada izquierda estrictamente negativa en $\bar\tau_d$ es una condición suficiente equivalente para un máximo restringido estrictamente interior; una derivada débilmente no positiva sitúa un maximizador débilmente antes de la cota y exige comparación directa en el caso de igualdad. Si $\tau_d^u\geq\bar\tau_d$ y la derivada lateral es positiva, el máximo restringido es la esquina $\bar\tau_d$.

**Demostración.** En una región toda formal con $\beta=0$, el conjunto real N está fijado por (2.26). Si $\eta_d=0$:

\[
B_d^N
=\int_{z_{AF}^N}^{\infty}
(\gamma z-k_Fz^\rho)dF(z),
\tag{5.17}
\]

y (5.17) no contiene $\tau_d$. Por tanto:

\[
\frac{\partial B_d^N}{\partial\tau_d}=0,
\tag{5.18}
\]

\[
\frac{\partial(\tau_dB_d^N)}{\partial\tau_d}
=B_d^N>0.
\tag{5.19}
\]

La tangencia puede existir y, aun así, no ser un máximo. Con $\eta_d>0$, P2 disciplina la recaudación mediante reporte, pero la FOC resultante no coincide en general con (5.5)–(5.8). $\square$

### 5.2 Interioridad ETI en N

Si (E_0=0), la recaudación doméstica es

\[
R_d^N
=\tau_drA_N.
\tag{5.20}
\]

Como (A_N) está acotada por un momento Pareto finito, existe $\overline A<\infty$ tal que

\[
0\leq A_N(\tau_d,\tau_f)\leq\overline A.
\tag{5.21}
\]

En $\tau_d=0$:

\[
R_d^N(0,\tau_f)=0.
\tag{5.22}
\]

Si $\eta_d>0$:

\[
0\leq
\lim_{\tau_d\uparrow1}\tau_dx_d^{\eta_d}A_N
\leq
\overline A
\lim_{\tau_d\uparrow1}\tau_dx_d^{\eta_d}=0.
\tag{5.23}
\]

Extienda la función a $\tau_d=1$ por su límite cero. Si la base es positiva en alguna tasa interior, continuidad sobre $[0,1]$ implica un máximo no restringido $\tau_d^u\in(0,1)$.

El compacto institucional requiere un paso adicional. Si

\[
\tau_d^u<\bar\tau_d,
\tag{5.23a}
\]

el mismo máximo es interior al compacto. Sin resolver primero el problema no restringido, bajo unimodalidad y diferenciabilidad lateral basta verificar

\[
\left.
\frac{\partial\mathcal R_d^N}{\partial\tau_d}
\right|_{\bar\tau_d^-}
\leq0.
\tag{5.23b}
\]

Con desigualdad estricta, el máximo queda estrictamente antes de $\bar\tau_d$; con igualdad, la esquina puede co-maximizar y debe compararse. Si $\tau_d^u\geq\bar\tau_d$ y la derivada izquierda es positiva:

\[
\boxed{
\tau_d^{*,inst}=\bar\tau_d.
}
\tag{5.23c}
\]

Así, ETI garantiza interioridad en $[0,1]$, pero no dentro de cualquier techo institucional truncado. Esta conclusión fortalece §5.3 de v1.2 y evita confundir un máximo no restringido con una recomendación factible.

### 5.3 El nuevo término cruzado $\varepsilon_{fd}$

En la topología (2.40)–(2.43):

\[
W_F
=\int_{z_{AF}}^{z_L}z^\rho dF(z)
+\int_{z_U}^{\infty}z^\rho dF(z).
\tag{5.24}
\]

Derivando respecto de $\tau_d$:

\[
\frac{\partial W_F}{\partial\tau_d}
=z_L^\rho f(z_L)z_{L,d}
-z_{AF}^\rho f(z_{AF})z_{AF,d}
-z_U^\rho f(z_U)z_{U,d}.
\tag{5.25}
\]

Como el factor $q\kappa_0x_f^{-\phi}$ no depende de $\tau_d$:

\[
\varepsilon_{fd}
=-\frac{x_d}{W_F}
\frac{\partial W_F}{\partial\tau_d},
\tag{5.26}
\]

\[
\boxed{
\varepsilon_{fd}
=\frac{x_d}{W_F}
\left[
z_{AF}^\rho f(z_{AF})z_{AF,d}
+z_U^\rho f(z_U)z_{U,d}
-z_L^\rho f(z_L)z_{L,d}
\right].
}
\tag{5.27}
\]

Éste es el término cruzado creado al condicionar al estatus la base de pagos transfronterizos trazables. No existía cuando $B_f$ incluía a todos los adoptantes.

En G con un único corte formal-informal superior y $\beta=\rho=0$, (4.28) implica

\[
\frac{\partial W_F}{\partial\tau_d}
=-f(z_F)\frac{dz_F}{d\tau_d}<0,
\tag{5.28}
\]

\[
\boxed{
\varepsilon_{fd}^G
=\frac{x_df(z_F)}{W_F}
\frac{r\gamma z_F}{H_z}>0.
}
\tag{5.29}
\]

Subir $\tau_d$ reduce pagos formales retenibles: el costo de la tasa doméstica incluye recaudación extranjera perdida de primer orden.

### 5.4 ¿Sobrevive el escudo G?

Diferencie (2.29) respecto de $\tau_f$ manteniendo $\tau_d$ fija. En un corte simple $z_F$:

\[
H_z(z_F)z_{F,f}
-\Delta k_f'(\tau_f)z_F^\rho=0,
\tag{5.30}
\]

\[
\boxed{
z_{F,f}
=\frac{k_F'(\tau_f)z_F^\rho}{H_z(z_F)}.
}
\tag{5.31}
\]

El reporte doméstico $r$ no depende de $\tau_f$, pero el estatus sí. Con $\beta=0$:

\[
B_d^G
=r\int_{z_F}^{\infty}\gamma z,dF(z).
\tag{5.32}
\]

Por Leibniz:

\[
\frac{\partial B_d^G}{\partial\tau_f}
=-r\gamma z_Ff(z_F)z_{F,f},
\tag{5.33}
\]

\[
\varepsilon_{df}^G
=-\frac{x_f}{B_d^G}
\frac{\partial B_d^G}{\partial\tau_f},
\tag{5.34}
\]

\[
\boxed{
\varepsilon_{df}^G
=\frac{x_fr\gamma z_Ff(z_F)}{B_d^G}
\frac{k_F'z_F^\rho}{H_z}.
}
\tag{5.35}
\]

Por (1.47), $k_F'\geq0$. En el corte superior regular, $H_z>0$, de modo que

\[
\boxed{
\varepsilon_{df}^G\geq0,
\quad
\varepsilon_{df}^G>0
\text{ si }\phi>0.
}
\tag{5.35a}
\]

La retención contrae la base doméstica G al elevar la carga efectiva que soporta el usuario formal. La ambigüedad de signo de v2.1 desaparece al incluir $c_f$ en las ganancias privadas.

> **Proposición 4-v2.2 (escudo como resultado de incidencia).** Bajo S1–S18, un régimen G con base positiva, un único corte formal--informal superior simple y $H_z>0$, $\varepsilon_{df}^G$ está dado por (5.35) y es no negativo. Es estrictamente positivo si $\phi>0$. El escudo $\varepsilon_{df}^G=0$ reaparece si $\phi=0$, si $k_F'=0$ por otra restricción, o si formales e informales soportan exactamente el mismo costo de transacción y éste se cancela de su comparación. Que $r$ responda sólo a $\tau_d$ no salva por sí solo el escudo.

Si $\phi=0$, $x_f^{-\phi}=1$, luego

\[
k_F=\kappa_0[1+0\cdot\widetilde\tau_f]=\kappa_0,
\tag{5.36}
\]

\[
k_F'=0,
\tag{5.37}
\]

y el escudo reaparece dentro del régimen. Ésta es una condición económica de incidencia, no una propiedad automática de la base G.

### 5.5 Penalidad proporcional y techo estatutario

Para aislar el resultado, imponga $\beta=\rho=0$, $\phi=0$ y sustituya S6 por

\[
c_I^{A}(z)=p\gamma z,
\qquad p\in(0,1).
\tag{5.38}
\]

La diferencia G formal-informal es

\[
\Delta_G^{prop}(z)
=p\gamma z-\widetilde\tau_d\gamma z,
\tag{5.39}
\]

\[
\boxed{
\Delta_G^{prop}(z)
=(p-\widetilde\tau_d)\gamma z.
}
\tag{5.40}
\]

El kink ya no satisface $\tau_d=p$, sino

\[
\widetilde\tau_d(\tau_p)=p.
\tag{5.41}
\]

Usando (1.23):

\[
\frac{1-(1-\tau_p)^{1+\eta_d}}{1+\eta_d}=p,
\tag{5.42}
\]

\[
(1-\tau_p)^{1+\eta_d}
=1-(1+\eta_d)p.
\tag{5.43}
\]

Si

\[
p<\frac{1}{1+\eta_d},
\tag{5.44}
\]

entonces

\[
\boxed{
\tau_p
=1-[1-(1+\eta_d)p]^{1/(1+\eta_d)}.
}
\tag{5.45}
\]

Antes del kink, el corte de participación es $z_{AF}=\kappa_0/(u_d\gamma)$. Por el Lema 1:

\[
B_d^{G,prop}
=A_Gr u_d^{a-1},
\qquad A_G>0.
\tag{5.46}
\]

La recaudación es

\[
R_d^{G,prop}
=A_G\tau_dru_d^{a-1}.
\tag{5.47}
\]

Derivando como en (4.53)–(4.54):

\[
\boxed{
\frac{dR_d^{G,prop}}{d\tau_d}
=A_Gru_d^{a-2}
\left[
u_d-\frac{\tau_d\eta_du_d}{x_d}
-\tau_d(a-1)r
\right].
}
\tag{5.48}
\]

Sea $\tau_L$ la primera raíz interior del corchete de (5.48), si existe. Para $\tau_d>\tau_p$, informal domina y la base doméstica G es cero. Bajo unimodalidad a la izquierda:

\[
\boxed{
\tau_d^{*,G,prop}
=\min\{\tau_L,\tau_p\}.
}
\tag{5.49}
\]

> **Corolario 1-v2.** Bajo S1–S5 y S7–S18, sustituyendo S6 por (5.38), e imponiendo $\beta=\rho=\phi=0$, unimodalidad de (5.47) a la izquierda y desempate formal, la penalidad proporcional limita la carga efectiva en $p$, no la tasa estatutaria en $p$. El kink estatutario es (5.45) y el óptimo es (5.49). Sólo en el límite $\eta_d=0$ se recupera $\tau_p=p$, $\tau_L=1/a$ y $\tau_d^*=\min\{p,1/a\}$. El techo exacto $\tau_d^*=p$ de v1.2 requiere además $p\leq1/a$.

Para N, el mismo $p$ no genera un techo estatutario universal porque la base neta, la deducción y el término $C_N$ alteran simultáneamente la franja formal. Debe resolverse P2 con la partición N correspondiente.

## 6. Base de pagos transfronterizos trazables, elasticidades no solapadas y amortiguador

### 6.1 Elasticidad extranjera completa

Por (3.8):

\[
B_f
=\kappa_0q x_f^{-\phi}W_F.
\tag{6.1}
\]

Tomando logaritmos:

\[
\ln B_f
=\ln\kappa_0+\ln q-\phi\ln x_f+\ln W_F.
\tag{6.2}
\]

Derivando respecto de $\ln x_f$:

\[
\varepsilon_{ff}
=\frac{\partial\ln q}{\partial\ln x_f}
-\phi
+\frac{\partial\ln W_F}{\partial\ln x_f}.
\tag{6.3}
\]

Como $q=x_f^{\eta_f}$:

\[
\frac{\partial\ln q}{\partial\ln x_f}=\eta_f.
\tag{6.4}
\]

Por tanto:

\[
\boxed{
\varepsilon_{ff}
=\eta_f-\phi+\varepsilon_{W,f},
\qquad
\varepsilon_{W,f}
\equiv\frac{\partial\ln W_F}{\partial\ln x_f}.
}
\tag{6.5}
\]

El término $-\phi$ es mecánico: aumentar $x_f$ reduce el gross-up de cada pago reportado y, por ello, reduce la base bruta por transacción. No es una elasticidad conductual. El costo $c_f$ no añade otro multiplicador directo a $B_f$: ya determina $q^*$ y, mediante $\widetilde\tau_f$ y $k_F$, mueve $W_F$. Por ello cambia $\varepsilon_{part,f}$ y $\varepsilon_{status,f}$, no la identidad contable $\eta_f-\phi$.

### 6.2 Descomposición exacta por fronteras

Considere la topología $N\to F\to I\to F$, donde

\[
W_F
=\int_{z_{AF}}^{z_L}z^\rho dF(z)
+\int_{z_U}^{\infty}z^\rho dF(z).
\tag{6.6}
\]

Derivando respecto de $\tau_f$:

\[
\frac{\partial W_F}{\partial\tau_f}
=z_L^\rho f(z_L)z_{L,f}
-z_{AF}^\rho f(z_{AF})z_{AF,f}
-z_U^\rho f(z_U)z_{U,f}.
\tag{6.7}
\]

Multiplicando por (-x_f/W_F):

\[
\varepsilon_{W,f}
=\frac{x_f}{W_F}
z_{AF}^\rho f(z_{AF})z_{AF,f}
+\frac{x_f}{W_F}
\left[
z_U^\rho f(z_U)z_{U,f}
-z_L^\rho f(z_L)z_{L,f}
\right].
\tag{6.8}
\]

Defina la contribución de participación formal:

\[
\boxed{
\varepsilon_{part,f}
\equiv
\frac{x_f}{W_F}
z_{AF}^\rho f(z_{AF})z_{AF,f}.
}
\tag{6.9}
\]

Defina la contribución de estatus formal-informal:

\[
\boxed{
\varepsilon_{status,f}
\equiv
\frac{x_f}{W_F}
\left[
z_U^\rho f(z_U)z_{U,f}
-z_L^\rho f(z_L)z_{L,f}
\right].
}
\tag{6.10}
\]

(6.9) contiene exclusivamente la frontera entre no adoptar y adoptar formal. (6.10) contiene exclusivamente las dos fronteras entre adoptar formal e informal. No comparten ningún corte. Por (6.8):

\[
\boxed{
\varepsilon_{W,f}
=\varepsilon_{part,f}+\varepsilon_{status,f}.
}
\tag{6.11}
\]

Sustituyendo en (6.5):

\[
\boxed{
\varepsilon_{ff}
=\underbrace{\eta_f}_{reporte}
-\underbrace{\phi}_{gross\text{-}up\ mecánico}
+\underbrace{\varepsilon_{part,f}}_{participación}
+\underbrace{\varepsilon_{status,f}}_{estatus}.
}
\tag{6.12}
\]

Si una frontera no existe, su contribución es cero; no se toma el logaritmo de una masa vacía. En un régimen con un solo corte activo, ese corte se asigna a participación o a estatus según las dos opciones que iguala, nunca a ambas.

Para $\rho=0$, $W_F$ es masa formal. Para $\rho>0$, (6.9)–(6.10) ponderan correctamente cada firma marginal por su pago $z^\rho$. Sustituir una elasticidad de masa sería incorrecto.

### Proposición 5-v2.2 — tasa extranjera y amortiguador

> **Proposición 5-v2.2.** Bajo S1–S17, una región suave interior, bases positivas y $\varepsilon_{df}=0$, la tasa extranjera satisface $\tau_f^*=1/[1+\varepsilon_{ff}(\tau_f^*)]$, con $\varepsilon_{ff}$ dado por (6.12) y fronteras reales generadas por $k_F=\kappa_0(1+\phi\widetilde\tau_f)$. Si $W_F$ es fijo, $t=0$ y $\eta_f>\phi$, la solución interior sigue siendo $\tau_f^*=1/(1+\eta_f-\phi)$: la carga privada afecta el estatus, pero no altera la base fiscal por transacción reportada. Con $t\in[0,1)$ y $W_F$ fijo, la FOC es (6.27) y la recuperación eleva débilmente la tasa mientras la raíz permanezca interior. Si $W_F$ es endógeno, $\varepsilon_{df}\neq0$, $\eta_f\leq\phi$, o la raíz sale de $[0,\bar\tau_f]$, se usa (6.30) y se comparan las esquinas.

**Demostración de la FOC suficiente.** Por P1, si $\varepsilon_{df}=0$:

\[
R_f
=B_f-\frac{\tau_f\varepsilon_{ff}B_f}{x_f}.
\tag{6.13}
\]

En una solución interior:

\[
1-\frac{\tau_f\varepsilon_{ff}}{x_f}=0,
\tag{6.14}
\]

\[
x_f=\tau_f\varepsilon_{ff},
\tag{6.15}
\]

\[
1-\tau_f=\tau_f\varepsilon_{ff},
\tag{6.16}
\]

\[
\boxed{
\tau_f^*
=\frac{1}{1+\varepsilon_{ff}(\tau_f^*)}.
}
\tag{6.17}
\]

Si (W_F) es fijo, $\varepsilon_{part,f}=\varepsilon_{status,f}=0$. Por (6.12):

\[
\varepsilon_{ff}=\eta_f-\phi.
\tag{6.18}
\]

Sustituyendo (6.18) en (6.17):

\[
\boxed{
\tau_f^*(t=0)
=\frac{1}{1+\eta_f-\phi}.
}
\tag{6.19}
\]

La condición $\eta_f>\phi$ asegura una elasticidad positiva y una raíz estrictamente menor que uno.

**Demostración del amortiguador.** Con (W_F) fijo, normalice por $\kappa_0W_F$. La recaudación sobre reportado y recuperación sobre no reportado es

\[
\mathcal R_f(\tau_f;t)
=\tau_fq x_f^{-\phi}+t(1-q).
\tag{6.20}
\]

Sustituyendo $q=x_f^{\eta_f}$:

\[
\mathcal R_f
=\tau_fx_f^{\eta_f-\phi}
+t(1-x_f^{\eta_f}).
\tag{6.21}
\]

Derivando el primer término:

\[
\frac{d}{d\tau_f}
[\tau_fx_f^{\eta_f-\phi}]
=x_f^{\eta_f-\phi}
-(\eta_f-\phi)\tau_fx_f^{\eta_f-\phi-1}.
\tag{6.22}
\]

Derivando el segundo:

\[
\frac{d}{d\tau_f}[t(1-x_f^{\eta_f})]
=t\eta_fx_f^{\eta_f-1}.
\tag{6.23}
\]

La FOC es

\[
x_f^{\eta_f-\phi}
-(\eta_f-\phi)\tau_fx_f^{\eta_f-\phi-1}
+t\eta_fx_f^{\eta_f-1}=0.
\tag{6.24}
\]

Multiplicando por $x_f^{1-\eta_f+\phi}>0$:

\[
x_f-(\eta_f-\phi)\tau_f
+t\eta_fx_f^\phi=0.
\tag{6.25}
\]

Usando $x_f=1-\tau_f$:

\[
1-\tau_f-(\eta_f-\phi)\tau_f
+t\eta_f(1-\tau_f)^\phi=0,
\tag{6.26}
\]

\[
\boxed{
1-(1+\eta_f-\phi)\tau_f
+t\eta_f(1-\tau_f)^\phi=0.
}
\tag{6.27}
\]

Con (t=0), (6.27) reproduce (6.19). Con $\phi=0$:

\[
1-(1+\eta_f)\tau_f+t\eta_f=0,
\tag{6.28}
\]

\[
\boxed{
\tau_f^*(t;\phi=0)
=\frac{1+\eta_ft}{1+\eta_f},
}
\tag{6.29}
\]

que es la fórmula de v1.2. Con gross-up, el amortiguador sobrevive, pero deja de ser lineal en (t) salvo casos especiales. $\square$

Cuando $\varepsilon_{df}\neq0$, como ocurre genéricamente en P4-v2, la tasa conjunta usa la segunda ecuación de (3.24):

\[
\boxed{
\tau_f^*
=\frac{1}{1+\varepsilon_{ff}
+\varepsilon_{df}\dfrac{\tau_dB_d}{\tau_f^*B_f}}.
}
\tag{6.30}
\]

## 7. Curvatura del crossover

Bajo $\beta=\rho=0$, fije una raíz (z_c) de (4.17). El locus estatutario satisface

\[
L(\tau_d,\tau_f)
\equiv
\widetilde\tau_d(\tau_d)
+\frac{k_F(\tau_f)}{\gamma z_c}-1=0.
\tag{7.1}
\]

Derivando respecto de $\tau_d$:

\[
L_d
=\widetilde\tau_d'(\tau_d),
\tag{7.2}
\]

\[
\boxed{L_d=r>0.}
\tag{7.3}
\]

Derivando respecto de $\tau_f$:

\[
\boxed{
L_f
=\frac{k_F'(\tau_f)}{\gamma z_c}.
}
\tag{7.4}
\]

Si $\tau_d=k(\tau_f)$, diferenciación implícita da

\[
L_dk'(\tau_f)+L_f=0,
\tag{7.5}
\]

\[
\boxed{
k'(\tau_f)
=-\frac{k_F'(\tau_f)}{\gamma z_cr(\tau_d)}.
}
\tag{7.6}
\]

Por (1.47), la pendiente es no positiva y es estrictamente negativa cuando $\phi>0$ y el locus es regular. El cierre de incidencia elimina la ambigüedad de orientación de v2.1, pero no impone la curvatura tangente ni los signos normales de P6.

Sea

\[
v_T=(k'(\tau_f^*),1)
\tag{7.7}
\]

un vector tangente y

\[
v_N=(1,-k'(\tau_f^*))
\tag{7.8}
\]

un vector normal. Defina la recaudación restringida al locus:

\[
\mathcal R_T(\tau_f)
\equiv R(k(\tau_f),\tau_f),
\tag{7.9}
\]

y su curvatura tangencial:

\[
\boxed{
D_{TT}R
\equiv\mathcal R_T''(\tau_f^*).
}
\tag{7.10}
\]

### Proposición 6-v2.2 — filo normal y concavidad tangente

> **Proposición 6-v2.2.** Bajo S1–S18, suponga un punto interior del locus (7.1), bases continuas, $R^-$ y $R^+$ dos veces diferenciables a cada lado, derivadas normales laterales estrictamente no nulas y de signos opuestos,
> 
> \[
> D_NR^-\equiv\nabla R^-\cdot v_N>0,
> \qquad
> D_NR^+\equiv\nabla R^+\cdot v_N<0,
> \tag{7.11}
> \]
> 
> y curvatura tangencial estricta $D_{TT}R<0$. Entonces una desviación que cruza el locus pierde recaudación en primer orden en su distancia normal, mientras una desviación a lo largo del locus pierde en segundo orden. Si además $|k'|\ll1$, el eje $\tau_f$ es casi tangente y el eje $\tau_d$ casi normal.

**Demostración.** Para (h>0), una expansión desde cada lado en dirección normal da

\[
R(\tau^*-hv_N)
=R(\tau^*)-hD_NR^-+O(h^2),
\tag{7.12}
\]

\[
R(\tau^*+hv_N)
=R(\tau^*)+hD_NR^++O(h^2).
\tag{7.13}
\]

Por (7.11):

\[
R(\tau^*)-R(\tau^*-hv_N)
=hD_NR^-+O(h^2)>0,
\tag{7.14}
\]

\[
R(\tau^*)-R(\tau^*+hv_N)
=-hD_NR^++O(h^2)>0.
\tag{7.15}
\]

Ambas pérdidas son de primer orden y tienen coeficiente estrictamente positivo.

Sobre el locus, la condición de primer orden tangente es

\[
\mathcal R_T'(\tau_f^*)=0.
\tag{7.16}
\]

Taylor da

\[
\mathcal R_T(\tau_f^*+h)
=\mathcal R_T(\tau_f^*)
+\frac12D_{TT}R\,h^2+o(h^2).
\tag{7.17}
\]

Como (D_{TT}R<0):

\[
\mathcal R_T(\tau_f^*)
-\mathcal R_T(\tau_f^*+h)
=-\frac12D_{TT}R\,h^2+o(h^2)>0.
\tag{7.18}
\]

La pérdida tangente es de segundo orden. Finalmente, si $|k'|\ll1$, (7.7) es cercano al eje extranjero y (7.8) al doméstico. $\square$

Las tres condiciones estrictas de P6-v2 son necesarias para afirmar la geometría. En v2.2 la curvatura tangente puede satisfacer $D_{TT}R<0$ y, aun así, fallar la proposición si las dos derivadas normales laterales tienen el mismo signo. Ninguna de las condiciones se infiere de la otra.

## 8. Equivalente recaudatorio respecto de ganancias potenciales de IA

El potencial tecnológico no depende del diseño ni de las tasas:

\[
B_{pot}
\equiv\int_{z_m}^{\infty}\gamma z\,dF(z).
\tag{8.1}
\]

Usando el Lema 1 con (m=1) y (z_c=z_m):

\[
B_{pot}
=\gamma\frac{az_m^a}{a-1}z_m^{1-a},
\tag{8.2}
\]

\[
\boxed{
B_{pot}
=\gamma\frac{az_m}{a-1}.
}
\tag{8.3}
\]

El equivalente recaudatorio puntual —se conserva el símbolo histórico $CS$— es

\[
\boxed{
CS^v(\tau_d,\tau_f)
\equiv\frac{R^v(\tau_d,\tau_f)}{B_{pot}}.
}
\tag{8.4}
\]

El headline comparable con cuentas nacionales es

\[
\boxed{
H^v(\tau_d,\tau_f)
\equiv\frac{R^v(\tau_d,\tau_f)}{PIB}.
}
\tag{8.5}
\]

La frontera institucional se define con supremo:

\[
\boxed{
\overline{CS}^{\,v}
\equiv
\sup_{(\tau_d,\tau_f)
\in[0,\bar\tau_d]\times[0,\bar\tau_f]}
\frac{R^v(\tau_d,\tau_f)}{B_{pot}}.
}
\tag{8.6}
\]

Se escribe $\sup$, no $\max$, porque S13 puede producir discontinuidades puntuales cuando cambia el desempate. Si se añade continuidad de (R^v) en todo el compacto, el teorema del valor extremo permite reemplazar el supremo por un máximo alcanzado.

El script reporta por separado el mínimo y máximo sobre todo el soporte de $\tau_f$ y los del plateau local de cinco nodos alrededor del supremo de grilla. Por tanto, el $\tau_f$ seleccionado por una grilla localmente plana **no es una recomendación**. El objeto de política es el rango de recaudación y su curvatura, no la coordenada numérica de un plateau.

(B_{pot}) es valor tecnológico potencial bajo adopción plena y sin impuestos; no es una base fiscal observada, PIB ni suma de bases de diseños distintos. La exposición incremental de (y_0) puede hacer que (CS^v) exceda la fracción de (g) gravada directamente; por eso (R/PIB) se reporta como headline separado.

## 9. Tabla de supervivencia histórica actualizada a v2.2

| Resultado v1.2 | Veredicto v2.2 | Razón exacta | Chequeo del script |
|---|---|---|---|
| P1: matriz suficiente | **Sobrevive igual** | Es una identidad de derivadas de dos bases | Gradiente directo y matriz coinciden |
| P2: agregabilidad | **Sobrevive con correcciones** | ETI suma $\eta_d$ sólo si (E_0=0); $\varepsilon_{fd}$ entra ponderada | FOC sintética coincide con (3.33) |
| P3A(i): kink G local bajo $\theta>a$ | **Muere como afirmación suficiente** | La base de pagos transfronterizos trazables cae con $\tau_d$ y añade (4.47) | En el sanity, $\Gamma^-<0$ y $\Gamma^+<0$ |
| Corolario global P3A | **Cambia** | (4.61)–(4.62) sólo controlan AF-bajo; además se requiere $\Gamma^-\geq0$ en todo el tramo intermedio | La condición baja pasa, pero el supremo queda antes del kink |
| P3B: tangencia N no garantiza óptimo | **Sobrevive con $\widetilde\tau_d$ y dominio explícito** | La tangencia puede ser múltiple; interioridad en $[0,1]$ no excluye esquina en $[0,\bar\tau_d]$ | El script verifica un máximo interior y un compacto truncado con esquina |
| §5.3: reporte N disciplina la frontera | **Sobrevive y se microfunda** | (r) surge de (1.7) y $\widetilde\tau_d$ altera decisiones reales | Minimización directa y envolvente coinciden |
| Lema 1: masa (a), primer momento (a-1) | **Sobrevive y se amplía** | El momento de pagos tiene elasticidad $a-\rho$ | Los tres momentos coinciden numéricamente |
| Corolario $\tau_d^*=p$ | **Muere para $\eta_d>0$** | (p) limita $\widetilde\tau_d$, no $\tau_d$; el kink es (5.45) | El óptimo/kink estatutario es distinto de (p) |
| P4: escudo G | **Muere para $\phi>0$; revive para $\phi=0$** | $k_F'=\kappa_0\phi\widetilde\tau_f'\geq0$ | $\varepsilon_{df}^G>0$ con incidencia positiva |
| Signo N ambiguo | **Sobrevive** | Intensidad, participación y dos fronteras de estatus siguen compitiendo | La partición cambia con $\beta$ y $\rho$ |
| P5: amortiguador | **Sobrevive con $W_F$ fijo; cambia con estatus endógeno** | Gross-up resta $\phi$ directamente y $\widetilde\tau_f$ mueve las fronteras mediante $k_F$ | El caso fijo coincide con $1/(1+\eta_f-\phi)$ |
| Observabilidad diferencial | **Se vuelve endógena** | El reporte ya no es un multiplicador que deja fija la partición | $r^*=x_d^{\eta_d}$ se recupera desde la minimización |
| Demanda no unitaria | **Pasa a central** | (B_f) usa $W_F=\int z^\rho dF$ | Se chequean $\rho=0$ y (0.5) |
| P6: filo/plano | **Sobrevive sólo como teorema condicional** | Requiere (7.11) y (D_{TT}R<0) | Las premisas fallan en el sanity central |
| Cotas de externalidad fiscal | **Sobreviven algebraicamente** | Deben usar la nueva descomposición no solapada y matrices laterales | No identifican bienestar sin una SWF |
| Estáticas de $\phi$ | **El signo de $k_F'$ queda cerrado** | La envolvente da $k_F'=\kappa_0\phi q^*w_f'\geq0$ | Obligación, costo y reparto suman numéricamente |

### Mapeo del $\phi$ histórico

La parametrización vieja y la nueva no están anidadas globalmente. Para igualar el nivel del pago reportado en una tasa de referencia $\tau_f^0$, defina $\phi_{map}$ por

\[
\kappa_0(1+\phi_{old}\tau_f^0)
=\kappa_0(1-\tau_f^0)^{-\phi_{map}}.
\tag{9.1}
\]

Cancelando $\kappa_0$ y tomando logaritmos:

\[
\ln(1+\phi_{old}\tau_f^0)
=-\phi_{map}\ln(1-\tau_f^0),
\tag{9.2}
\]

\[
\boxed{
\phi_{map}
=\frac{\ln(1+\phi_{old}\tau_f^0)}
{-\ln(1-\tau_f^0)}.
}
\tag{9.3}
\]

Este mapeo iguala únicamente el nivel de la base bruta de una transacción reportada. No iguala $\widetilde\tau_f$, $k_F$, sus derivadas, la recaudación total ni $s_P$. Por ello $\beta=\rho=0$ con (9.3) es un puente contable de comparación, no una prueba de que v1.2 esté anidado exactamente.

## 10. Verificación numérica

`baseline_check_v2.py` implementa las cuatro ganancias, el estatus previo, ambos reportes microfundados, $\widetilde\tau_f$, el reparto usuario--proveedor, gross-up, demanda $z^\rho$, la base de pagos transfronterizos reportados y trazables, bases incrementales, G, N, tangencias, crossovers, matriz, momentos, penalidad proporcional, amortiguador, curvatura y el equivalente recaudatorio institucional. Las integrales de base son momentos Pareto exactos sobre intervalos cuyas fronteras se obtienen por raíces de todas las comparaciones de ganancias.

La grilla del equivalente recaudatorio es una aproximación determinista al supremo definido en (8.6); sus tasas no son resultados de política ni calibración país.

La salida final se reproduce verbatim:

```text
=== BASELINE V2.2 CHECK START ===
PARAMETERS a=1.50 z_m=0.50 gamma=1.00 delta=0.08 theta=2.00 kappa=0.60 eta_d=0.02 eta_f=8.00 phi=1.00 bars=(0.98,0.80)
ETI direct-minimization r_closed=0.9908018550 r_numeric=0.9908018550 r_error=3.282e-11 q_closed=0.2044140859 q_numeric=0.2044140828 q_error=3.102e-09
ETI envelope point=0.41 tilde_prime_numeric=0.9895028290 r_star=0.9895028291 error=7.394e-11
FOREIGN-ETI tau_f=0.18 phi=0.50 q=0.2044140859 obligation=0.0406327670 hiding_cost=0.0589197368 tilde_tau_f=0.0995525038 burden_error=6.939e-17 envelope_numeric=0.2505136720 envelope_closed=0.2505136720 envelope_error=3.291e-11
INCIDENCE-SPLIT adopter=0.0497762519 provider=0.0497762519 allocated_sum=0.0995525038 obligation_plus_cost=0.0995525038 allocation_error=6.939e-17
N2 RENT-CAPTURE tau_f=0.18 phi=0.50 sP_numeric=0.4752139656 sP_closed=0.4752139656 abs_error=3.886e-16 limit_tau0=0.5000000000 corner_phi0=1.0000000000 corner_phi1=0.0000000000
P1 sufficient-gradient point=(0.35,0.02) direct=(0.22112054,-0.06705234) matrix=(0.22112054,-0.06705235) max_abs_error=6.334e-09
P2 ETI-aggregation eta_d=0.50 epsilon_real=0.20896869 numeric_tau=0.58514806 formula_tau=0.58514823 abs_error=1.645e-07
P3A G-crossovers strict_discriminant=True lower_tau=0.03304120 lower_z=0.63194874 upper_tau=0.96522161 upper_z=11.86805126 left_derivative=-0.00869021 right_derivative=-2.39767150
P3A global lambda_new=0.00852050 endpoint=0.94156043 monotone=1.49045439 low_AF_condition=True full_condition=False grid_sup_tau=0.96325082 kink_R=0.27795884 sup_R=0.27796730
P3B N-tangencies count=2
  tangent=1 tau_d=0.02021808 tilde_tau=0.02021396 z=0.12633726 topology_below=N->F topology_above=N->F
  tangent=2 tau_d=0.17565814 tilde_tau=0.17533016 z=1.09581347 topology_below=N->F topology_above=N->F->I->F
DOMAIN N unrestricted_tau=0.96266300 institutional_bar=0.98000000 institutional_tau=0.96266286 derivative_at_bar=-0.13061624 interior_supported=True tilde_at_bar=0.96225996 low_bar=0.50000000 low_tau=0.50000000 low_derivative=0.19996826 low_corner=True
LEMMA moments mass=1.50000000 expected_a=1.50000000 first=0.50000000 expected_a_minus_1=0.50000000 rho_half=1.00000000 expected_a_minus_rho=1.00000000
COROLLARY proportional-ETI eta_d=0.50 p=0.25000000 statutory_kink=0.26899557 numeric_tau=0.26899370 R_d=0.27273094 exact_p_survives=False
COROLLARY mapped-case tau_f=0.02 p=0.25000000 numeric_tau=0.23676300 R_d_plus_R_f=0.28439909 exact_p_survives=False
SHIELD G-status-dependent point=(0.50,0.10) epsilon_df=0.03969092 epsilon_fd=1.45121630 zero_shield=False
FOREIGN gross-up phi=phi_map(0.98019671) eta_minus_phi=7.01980329 analytic_t0_tau=0.12469134 numeric_t0_tau=0.12469240 t0_value=0.04895753 t20_tau=0.27103757 t20_value=0.21351423
CURVATURE kink_tau_d=0.96621969 kink_tau_f=0.00000484 slope=-0.05302726 D_TT_R=-0.04758779 normal_left=-0.01363414 normal_right=-2.44641562 strict_conditions=False
BETA-RHO status-and-base sanity point=(0.35,0.10) variant=N
  beta=0.0 rho=0.0 topology=N->I->F prior_formal_mass=1.00000000 formal_adopters=0.04851458 informal_adopters=0.65525782 B_d=0.51137423 B_f=0.01392262 R=0.18037324
  beta=0.0 rho=0.5 topology=I->F prior_formal_mass=1.00000000 formal_adopters=0.06559917 informal_adopters=0.93440083 B_d=0.48949356 B_f=0.04950974 R=0.17627372
  beta=0.5 rho=0.0 topology=N->I->F prior_formal_mass=0.10927804 formal_adopters=0.02300758 informal_adopters=0.73771819 B_d=0.26300576 B_f=0.00660267 R=0.09271228
  beta=0.5 rho=0.5 topology=I->F prior_formal_mass=0.10927804 formal_adopters=0.02672556 informal_adopters=0.97327444 B_d=0.24968713 B_f=0.02720881 R=0.09011138
  beta=1.0 rho=0.0 topology=N->I->F prior_formal_mass=0.03863562 formal_adopters=0.01435091 informal_adopters=0.74637486 B_d=0.20964141 B_f=0.00411840 R=0.07378633
  beta=1.0 rho=0.5 topology=I->F prior_formal_mass=0.03863562 formal_adopters=0.01582162 informal_adopters=0.98417838 B_d=0.20008262 B_f=0.01918341 R=0.07194726
LEGACY phi-map tau_f=0.02 phi_old=1.00 phi_new=0.98019671 K_old=0.61200000 K_reported=0.61200000 level_error=0.000e+00
SURVIVAL TABLE numeric mapped_case=beta0-rho0-phiold-level
  result=P1-sufficiency classification=same check=PASS
  result=P2-aggregation classification=same-with-ETI-and-cross-corrections check=PASS
  result=P3A-local classification=dies-in-sanity-foreign-formal-base check=PASS
  result=P3A-global classification=old-low-condition-insufficient check=PASS
  result=P3B-tangency classification=same-logic-with-tilde check=PASS
  result=Lemma-moments classification=survives-generalized check=PASS
  result=Corollary-tau-equals-p classification=dies-under-microfounded-ETI check=PASS
  result=P4-G-shield classification=incidence-positive-and-restored-at-phi0 check=PASS
  result=P5-foreign-buffer classification=fixed-W-form-survives-real-margin-changes check=PASS
  result=P6-curvature classification=conditional-premises-fail-in-sanity check=PASS
  result=Foreign-effective-burden classification=obligation-plus-concealment-cost check=PASS
  result=Institutional-domain classification=interior-or-corner-at-declared-bar check=PASS
  result=N2-rent-capture classification=exact-provider-share check=PASS
CAPTURE-SUP variant=G tau_d_grid=0.94733333 tau_f_grid=0.00000000 sup_grid_R=0.27759671 B_pot=1.50000000 share=0.18506448 R_tf_full_min=0.27651527 R_tf_full_max=0.27759671 R_tf_full_range=1.08144409e-03 R_tf_plateau_min=0.27744212 R_tf_plateau_max=0.27759671 R_tf_plateau_range=1.54593784e-04
CAPTURE-SUP variant=N tau_d_grid=0.94733333 tau_f_grid=0.00000000 sup_grid_R=0.28122291 B_pot=1.50000000 share=0.18748194 R_tf_full_min=0.27947191 R_tf_full_max=0.28122291 R_tf_full_range=1.75100504e-03 R_tf_plateau_min=0.28044881 R_tf_plateau_max=0.28122291 R_tf_plateau_range=7.74106360e-04
LEGACY mapped-case beta=0 rho=0 topology=N->I->F B_d=0.50193461 B_f=0.02001948
=== BASELINE V2.2 CHECK END ===
```

### 10.1 La esquina $\tau_f=0$ del vector de diagnóstico (nota de auditoría, 2026-07-17)

En la línea `CAPTURE-SUP`, ambas variantes reportan $\tau_f=0$. Conviene separar dos causas distintas, porque sólo una es económica.

**(i) En G la esquina es genuina.** Evaluando (3.18) en $\tau_f=0$, donde $x_f=1$:

\[
\left.\frac{\partial R}{\partial\tau_f}\right|_{\tau_f=0}
=B_f(0)-\tau_d\varepsilon_{df}B_d .
\tag{10.1}
\]

Por tanto, el supremo está en la esquina inferior si y sólo si

\[
\boxed{
\tau_d\,\varepsilon_{df}\,B_d\;\geq\;B_f\big|_{\tau_f=0}.
}
\tag{10.2}
\]

En el vector de diagnóstico y a la tasa doméstica del supremo, $B_f(0)=0.005337$ y $\tau_d\varepsilon_{df}B_d=0.007675$, de modo que (10.2) se cumple y $\partial R/\partial\tau_f=-0.002337<0$. Una búsqueda unidimensional fina confirma el óptimo exactamente en cero.

El mecanismo es el término cruzado cuyo signo quedó fijado en v2.2: con $k_F'\geq0$, la retención encarece la adopción formal, expulsa firmas del estatus formal y erosiona simultáneamente la base doméstica y la propia base de pagos trazables. Cuando la tasa doméstica es casi confiscatoria, la masa formal —y con ella $W_F$— es pequeña, de modo que la retención tiene poca base que gravar y mucha base doméstica que dañar. **Los dos instrumentos son sustitutos a través del margen de estatus formal**, y la condición (10.2) delimita la región donde el instrumento extranjero es dominado. No es un artefacto de $\eta_f$ grande: $\eta_f$ reduce $B_f$, pero la desigualdad la decide la comparación entre base de pagos y pérdida doméstica ponderada por $\tau_d$.

**(ii) En N no hay esquina; hay resolución de grilla insuficiente.** Aquí $\partial R/\partial\tau_f|_{0}=+0.001425>0$ y el óptimo es interior en $\tau_f\simeq0.00131$, con una ganancia sobre $\tau_f=0$ de orden $9\times10^{-7}$. La grilla de `CAPTURE-SUP` usa 31 nodos sobre $[0,\bar\tau_f]$, es decir un paso de $0.027$, y no puede resolver un óptimo dos órdenes de magnitud menor. La línea reporta por ello el nodo cero.

En consecuencia: (a) la grilla de `CAPTURE-SUP` es una cota inferior del supremo y sus tasas nunca deben leerse como óptimos, y menos como política; (b) la Fase 5 debe resolver el instrumento extranjero con optimización continua, no con grilla; y (c) la comparación entre variantes en esa línea sólo es informativa sobre niveles de recaudación, no sobre la mezcla óptima de instrumentos.

## 11. QUÉ SE ROMPE

1. **v1.2 no está anidado sólo con $\beta=\rho=0$.** También cambiaron la incidencia, la trazabilidad y el papel conductual del reporte.

2. **$q_d=x_d^{\eta_d}$ ya no es un multiplicador inocuo.** Su costo genera $\widetilde\tau_d$, que entra en todos los umbrales reales.

3. **La tasa estatutaria y la carga privada se separan.** $\widetilde\tau_d<\tau_d$ para $\eta_d>0$ y $\lim_{\tau_d\uparrow1}\widetilde\tau_d=1/(1+\eta_d)$.

4. **El techo proporcional exacto en (p) muere.** (p) limita la carga efectiva; el kink estatutario es (5.45) y puede ni existir si $p\geq1/(1+\eta_d)$.

5. **El escudo G muere con trazabilidad diferencial.** Aunque (r) no responde a $\tau_f$, el costo formal $k_Fz^\rho$ sí y mueve el estatus.

6. **$\varepsilon_{fd}=0$ muere.** Sólo pagos formales son retenibles; una tasa doméstica que informaliza firmas erosiona (B_f) en primer orden.

7. **$\theta>a$ ya no basta para P3A.** La derivada extranjera negativa de (4.47) puede dominar el crecimiento doméstico.

7b. **La retención puede ser un instrumento dominado.** Por (10.2), si $\tau_d\varepsilon_{df}B_d\geq B_f$ en $\tau_f=0$, el supremo en $\tau_f$ está en la esquina inferior. Ocurre cuando la tasa doméstica deja poca masa formal: la base de pagos trazables se encoge y el daño cruzado sobre la base doméstica la excede. La existencia de un $\tau_f^*>0$ es por tanto un resultado condicional, no una propiedad del modelo.

7c. **Las tasas de la línea `CAPTURE-SUP` no son óptimos.** Su grilla de 31 nodos tiene paso $0.027$ y no resuelve óptimos menores; en N el óptimo verdadero es interior en $\tau_f\simeq0.0013$ y la grilla reporta cero. La Fase 5 debe optimizar el instrumento extranjero de forma continua.

8. **La condición AF-bajo no basta para globalidad.** El run satisface el nuevo $\lambda_f$ y aun así alcanza el supremo antes del crossover porque falla la monotonía intermedia.

9. **La geometría filoso-plano no es automática.** Requiere derivadas normales laterales estrictamente no nulas y (D_{TT}R<0); el sanity central viola ambas condiciones de signo.

10. **El gross-up puede reducir la elasticidad observada.** El término mecánico $-\phi$ compensa parte de $\eta_f$.

11. **La ambigüedad de $k_F'$ de v2.1 era un artefacto.** Al incluir obligación y costo de ocultamiento en $\widetilde\tau_f$, (1.47) implica $k_F'\geq0$.

12. **La topología N $N\to F\to I\to F$ no es global.** $\beta$ grande eleva (z_0), baja (H_N) y elimina la primera franja formal.

13. **Con $\rho>0$, masa y base de pagos dejan de ser equivalentes.** La elasticidad correcta es $a-\rho$ sólo cuando un único corte proporcional domina.

14. **El discriminante debe ser estricto.** $4\delta K_I/\gamma^2=1$ produce una raíz doble; no autoriza hablar de dos crossovers.

15. **La base doméstica incremental puede ser negativa localmente.** Ocurre si una adopción induce desformalización y la pérdida de (y_0) excede el incremento reportado. P1 exige bases positivas en su región de aplicación.

16. **La fórmula ETI sin share requiere (E_0=0).** Con exposición previa, el término directo es $\omega_A\eta_d$, no $\eta_d$ completo.

17. **La fórmula extranjera cerrada requiere $\varepsilon_{df}=0$.** Cuando muere el escudo, la tasa usa la corrección ponderada de (6.30).

18. **El amortiguador lineal de v1.2 requiere $\phi=0$.** Con gross-up, la FOC es implícita y no lineal en (t).

19. **El equivalente recaudatorio no es una medida de bienestar.** Puede incluir base previa revelada y no descuenta costos reales de ocultamiento, adopción ni incidencia sobre rentas.

20. **Compacto no implica máximo sin continuidad.** La regla de desempate puede dejar sólo un supremo; por eso (8.6) no presume alcanzabilidad.

21. **Interioridad en $[0,1]$ no implica interioridad institucional.** Si $\bar\tau_d$ queda antes del máximo no restringido y la derivada izquierda es positiva, la solución restringida es la esquina.

22. **$B_f$ no mide utilidades del proveedor.** Es una base de pagos reportados y trazables; la renta capturada se informa mediante $s_P$.

23. **$1-\phi$ sólo es la incidencia marginal exacta del recaudo.** A tasas finitas, la participación exacta es (1.50), aunque S11 use $1-\phi$ para repartir la carga efectiva total.

24. **Ocultar consume recursos.** Tratar $c_f$ como si sólo seleccionara $q$ y luego desapareciera de las ganancias privadas subestimaba el costo formal y movía incorrectamente las fronteras reales.

## 12. Decisiones de cierre

1. **Deducción N.** El baseline deduce el pago económico medio $K_F$; la alternativa de deducir sólo $qK_R$ queda como sensibilidad declarada de Fase 5.
2. **Base doméstica.** El headline usa la base incremental de S14; la base total post-adopción se reserva para una descomposición suplementaria y nunca se atribuye íntegramente a la IA.
3. **Costo de ocultamiento extranjero.** La coalición usuario formal--proveedor elige el reporte y soporta obligación más costo real; el usuario carga $\phi\widetilde\tau_f$ y el proveedor $(1-\phi)\widetilde\tau_f$.
4. **Absorción del proveedor.** En el modelo estático, la carga $(1-\phi)\widetilde\tau_f$ se financia con rentas de superstar; entrada, calidad y dinámica quedan fuera del baseline.
5. **Trazabilidad informal.** S12 mantiene probabilidad cero de retención para pagos informales; una probabilidad positiva se tratará como sensibilidad acotada en Fase 5.
6. **Visibilidad informal.** El baseline conserva $c_I(z)=\delta z^\theta$ después de adoptar; una penalidad reescalada por la ganancia de IA será robustez, no especificación central.
7. **Soporte de $\eta_d$.** No se fuerza un soporte que garantice el crossover: si falla (4.20), se reportará que el crossover no existe en el soporte calibrado.
8. **Mapeo de incidencia.** $\phi_{map}$ iguala únicamente la base bruta reportada en la tasa de referencia; no se interpreta como equivalencia de $\widetilde\tau_f$, $k_F$, $s_P$, derivadas ni recaudación.
9. **Equivalentes recaudatorios negativos.** Se conservan sin truncar porque la desformalización de base previa es parte del objeto; cualquier presentación truncada se mostrará sólo como gráfico auxiliar y se etiquetará.
10. **P3A en el paper.** Se mantiene como proposición lateral condicional y se presenta, junto a ella, el resultado central de que la trazabilidad puede destruir el máximo en el kink.
11. **Separación empírica.** El baseline empírico identifica $\varepsilon_{part,f}+\varepsilon_{status,f}$; sólo se separan sus componentes con microdatos enlazados y, en otro caso, se reportan cotas.
12. **Destino de pagos no reportados.** El destino potencial grava la base neta $\kappa_0z^\rho$ de (6.20), no un bruto contrafactual.
