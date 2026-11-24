# Cobertura Exp8 × ENF por afirmación (rem147)

Derivado de fuentes existentes autenticadas; no es una corrida aceptada. Enlace exacto (unidad, cell_id).

| ámbito | denominador | ambos | solo sup | solo inf | ninguno |
|---|---:|---:|---:|---:|---:|
| universo T7 | 1728 | 1721 | 4 | 3 | 0 |
| inconclusas | 1712 | 1705 | 4 | 3 | 0 |
| inconclusas descompuestas | 1705 | 1705 | 0 | 0 | 0 |
| inconclusas sin descomposición | 7 | 0 | 4 | 3 | 0 |
| robustas infactibles | 16 | 16 | 0 | 0 | 0 |

## Canal η_f/2 (ABL-ENF) por país: lo que demuestran las cotas de los testigos

| país | universo | inconclusas | inconclusa_preservada | parcial_no_robusta_infactible | parcial_no_robusta_factible | robustez_refutada_por_testigo_sup | en_tolerancia_no_decidida | no_decidida_por_testigos | sin cobertura |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| - | 128 | 128 | 128 | 0 | 0 | 0 | 0 | 0 | 0 |
| COL | 480 | 480 | 477 | 0 | 3 | 0 | 0 | 0 | 0 |
| MEX | 320 | 304 | 300 | 4 | 0 | 0 | 0 | 16 | 0 |
| PER | 800 | 800 | 800 | 0 | 0 | 0 | 0 | 0 | 0 |

## Inconclusas por familia

| familia | inconclusas | ambos | inconclusa preservada |
|---|---:|---:|---:|
| c | 640 | 639 | 639 |
| ci | 944 | 938 | 938 |
| g | 128 | 128 | 128 |

## Testigos y celdas

- Ranuras de testigo: 3456; con filas aceptadas: 3449; enlazadas con ENF: 3449.
- Celdas testigo únicas (unidad, cell_id): 1724 en el universo, 1716 en las inconclusas; celdas ENF: 1724, de ellas testigo: 1724, sin afirmación: 0.
- dG en testigos enlazados: [0.0, 0.012832670219052933]; afirmaciones con cambio de signo en algún testigo ENF: 0.
- Origen de G en testigos enlazados: {'resolucion_no_alcanzado_demostrado': 352, 'techo_cerrado': 3097}.
- Motivos de no enlace: {'testigo sin filas aceptadas (fuera de las 2.276 unidades)': 7}.

Lectura: «inconclusa_preservada» significa que, con η_f/2 y el resto fijo, los dos testigos padre siguen demostrando sup G_enf > −ε y inf G_enf < ε. No identifica el eslabón que provoca el cruce ni ordena canales; tampoco convierte signos puntuales en una clasificación de todo el soporte donde las cotas no bastan.
