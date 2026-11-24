# Dominios, primitivas y recomputación

**BORRADOR NO APROBADO.** Es parte normativa de DI-04/DI-07 y del contrato D7 propuesto. No modifica la teoría original.

## Tres conjuntos distintos

- Dominio teórico: S4 permite rho∈[0,1]; los resultados derivados con parámetros interiores y el límite rho↓0 se tratan según S18. S6 exige theta>1 y S18 los momentos requeridos de orden menor que a.
- Soporte primario propuesto: rho∈[0.4,1], junto con los soportes de DI-04. Continúa sujeto a aprobación A4. No se cambia a un conjunto discreto.
- Dominio de sensibilidad: expansión direccional del soporte propio, intersectada con el dominio demostrado y admisibilidad. No se evalúa rho>1. El extremo rho=0 se documenta como límite: no se llama una fórmula interior en cero sin validación de esa fórmula límite.

Para un soporte aritmético [L,U], c=(L+U)/2 y h=(U−L)/2. Expansión inferior: [c−r*h,U]; superior: [L,c+r*h], con r≥1. Para escala logarítmica se aplica la misma regla a log(L),log(U). No se desplazan simultáneamente ambos extremos al pedir una dirección. La expansión conjunta declara qué extremos cambian y conserva el mismo r, con testigos de todas las primitivas involucradas.

Para rho, c=0.7,h=0.3. En dirección superior, rho=1 ya es frontera en r=1: no existe tramo adicional demostrable. En dirección inferior, el límite rho↓0 se alcanza cuando r↑7/3. La existencia de otras restricciones puede detener antes la trayectoria. Nunca se recorta un intento rho>1 a 1 y se cuenta como evaluación nueva; se registra la frontera solicitada y la efectivamente cubierta.

## Estado y reporte al detenerse

Si la afirmación primaria ya es inconclusa, se conserva `not_applicable_baseline_inconclusive`. Si ni siquiera terminó su cálculo, se usa `incomplete_search`, no un estado de robustez. Solo si la afirmación está verificada sobre el dominio declarado efectivamente cubierto puede emitirse `theoretical_boundary_no_breakdown` en la dirección superior de rho, con `reason_code=RHO_UPPER_S4`, `boundary_kind=theoretical`, `domain_edge_reached=rho_upper_S4`, `boundary_value=1`, `reached_expansion_factor=1`, `r_critical=null`. Su lectura es «no se amplió el soporte: se alcanzó el límite de la teoría», no «robusto para rho>1».

En la dirección inferior, el motivo es `RHO_ZERO_LIMIT`, frontera0, factor7/3 si no se encontró antes otro límite o quiebre. Informar cobertura por aproximación lateral y si la fórmula límite fue validada; sin cobertura suficiente, `incomplete_search`. Un valor de r crítico solo existe si se encuentra el quiebre con sus testigos dentro del dominio cubierto.

Se añade `admissibility_boundary_no_breakdown` cuando solo se llega al borde de una trayectoria/bloque, sin prueba de haber agotado todo el dominio relevante. El estado histórico `domain_exhausted_no_breakdown` se reserva para cobertura completa del dominio admisible al que se refiere el claim; no se infiere por tocar una restricción en un único omega. Las fronteras abiertas qpot=1,lambda=0,a=1,kappa=0 no se evalúan como puntos interiores válidos. Se reportan su valor límite y el último dominio cubierto.

Se mantienen los estados separados de escalera eta_H agotada, hueco entre bloques eta_w y búsqueda fallida. `no_solution` en robustez sigue siendo fallo del solver; en inversión se sustituye la ambigüedad por un `result_status` y un booleano `no_solution` solo para inexistencia demostrada. Agotamiento de recursos o topología inestable nunca equivale a inexistencia.

## Primitivas fijas y derivados

Las nuevas primitivas son `u_theta` y `z_cost`; theta y delta_tilde no son ejes independientes. En una variación tecnológica se fijan beta_tilde,u_theta,z_cost,eta_d,eta_f,phi,gamma,z_m,los pi,los datos nacionales,el bloque laboral,el requerimiento y el caso jurídico, salvo que el escenario conjunto declare otra variación. Se cambia la coordenada tecnológica solicitada (a,rho,kappa_tilde), no sus equivalentes dimensionales a la vez.

| Variación | Primitivas que no cambian | Derivados que obligatoriamente cambian/revalidan |
|---|---|---|
| a | rho,kappa_tilde,u_theta,z_cost y demás primitivas | theta=1+u_theta(a−1); delta_tilde=z_cost^(1−theta); delta dimensional; momentos Pareto, qpot,lambda,conjuntos de adopción,E0,bases,frontera,C2,G e inversiones |
| rho | a,kappa_tilde,u_theta,z_cost y demás primitivas | kappa0=kappa_tilde*gamma*z_m^(1−rho),momento de pagos,qpot,lambda,adopción/bases/C2/G; theta y delta permanecen iguales |
| kappa_tilde | a,rho,u_theta,z_cost y demás primitivas | kappa0,qpot,lambda,pagos,adopción/bases/C2/G; theta y delta iguales |
| u_theta o z_cost (soporte primario/refinamiento) | a,rho,kappa_tilde y demás coordenadas no declaradas | theta si cambia u_theta; delta_tilde/delta; informalidad,adopción,E0 y frontera. No confundirlos con cambios de a |

No se mantiene C2 fijo al cambiar a/rho/kappa. Tampoco se congela delta_tilde artificialmente cuando cambia a: eso alteraría la convención económica propuesta de costo relativo. La propuesta define primitivas fijas y así evita dos sensibilidades distintas con el mismo nombre. Si el autor quisiera mantener theta o delta constantes al variar a, sería otra sensibilidad A4, que no se adopta aquí.

Formulas: beta=beta_tilde*gamma; theta=1+u_theta(a−1); delta_tilde=z_cost^(1−theta); delta=delta_tilde*gamma*z_m^(1−theta); kappa0=kappa_tilde*gamma*z_m^(1−rho); qpot=kappa_tilde*(a−1)/(a−rho); theta_W=(eta_w+eta_H)/(1+eta_H); s_L_marg=s_L_bar*theta_W; s_T_marg=Σ pi_j*s_bar_j; s_Pi_marg=1−s_L_marg−s_T_marg; lambda=s_Pi_marg/(1−qpot). Aplicar condiciones antes de divisiones/potencias; gamma>0,z_m>0,z_cost>0,a>1,0<u_theta<1,0<rho≤1 en evaluación interior,0<kappa_tilde,(a−rho)>0,qpot<1,eta_H>−1,s_T_marg≥0,s_Pi_marg>0. La frontera s_Pi=0 es incompatible con lambda>0 aunque la restricción individual no negativa la incluyera.

El tramo rho>1 permanece solo como alternativa A4: demostrar nuevamente proposiciones/regímenes/integrabilidad, adaptar validaciones y aprobar antes de habilitarlo. Ni este catálogo ni un flag de sensibilidad autorizan ese tramo.

## Precisión del bloque residual y escalas

chi_r es intensidad relativa de pagos, no una captura reducida. El rango condicional[0,1] pertenece al contrato D19 y no habilita por sí mismo un momento. Con D3/D5 actuales se conserva rama no identificada y estado not_applicable_not_identified; no se evalúa esta expansión ni se la presenta como agotada. La fórmula condicional exacta y entradas inactivas constan en formulas.json. La etiqueta chi_R de la entrega anterior se normaliza a chi_r.

La bisección usa logaritmos en kappa_tilde,beta_tilde,z_cost,eta_d y eta_f; aritmética en a,rho,u_theta,phi y pi. Los conteos 2n−1 son idénticos para ambas escalas, pero sus coordenadas no lo son. gamma,z_m son unidades, t=0 y c_legal=1 constantes de alcance; ninguna se calibra con WBES.

## Declaración de C_2 y fase de cálculo

formulas.json registra C_2 como numerical_operator con formula_id=C_2 e inputs R,B_pot,bar_tau_d,bar_tau_f. R está registrado como numerical_function; sus argumentos y primitivas son declaraciones, no puntos evaluados al construir D7. C_2=sup_T R/B_pot conserva dominio y método del diseño, sin prometer argmax. Su result_binding apunta al esquema B.capture_ceiling_result.C_2, no a una fila que deba existir en D7. Las unidades flow de R/B_pot se corresponden con normalized_flow en almacenamiento mediante gamma*z_m; el cociente share no cambia. Los campos de supremo no alcanzado,disponibilidad,laterales,error y testigos se mantienen. Las fórmulas algebraicas existentes no se cambian.
