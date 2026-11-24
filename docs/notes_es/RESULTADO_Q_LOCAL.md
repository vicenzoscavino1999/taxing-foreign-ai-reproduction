# Resultado Q local: m = 1/2, versiones contrato y conservadora

**Fecha:** 2026-11-16. **Resultado:** las dos versiones se regeneran en racionales exactos desde las posiciones guardadas. Coinciden campo a campo con sus referencias aceptadas: 3.456 posiciones y 1.728 afirmaciones por versión. La conciliación entre ambas versiones no muestra diferencias.

**Revisión de Codex (2026-11-16): conforme en ese alcance.** Se cotejaron las
entradas con el manifiesto aceptado y las salidas directamente con los dos
productos de rem158: todas las posiciones y afirmaciones coinciden con sus
referencias respectivas. Las cinco funciones científicas extraídas de comun_q.py
coinciden en su AST con el código de origen autenticado. No se repitió el cálculo.

La igualdad entre versiones se refiere a categorías, canales y regiones: las
cotas g_lo/g_hi difieren en 3.449 posiciones. Cada versión conserva sus propias
cotas aceptadas. P7 aparece exactamente en siete posiciones, sin duplicados.

Alcance: aritmética G(m) = C_2 − m·K1 sobre entradas guardadas. No se recalculan el modelo, K1, bridge, `GridCell.Q`, supremos ni techos. Los K1 de P7 se calculan aparte (`RESULTADO_P7.md`); aquí entran como valores guardados.

## Comando y tiempo

```text
python -B -I -X utf8 <base>/reproducir.py q-local --salida <base>/salidas/q_local_01
```

Se lanzó desde la carpeta temporal del usuario, como un único proceso, con un límite de 600 s:
- código de salida 0;
- 0,517 s en total, de ellos 0,324 s de cálculo interno;
- nada en stderr.

La salida es una carpeta nueva con tres archivos:

| Archivo | Tamaño | sha256 |
|---|---|---|
| `q_local_contrato.jsonl` | 2.690.763 B | 535ea651… |
| `q_local_conservadora.jsonl` | 2.705.959 B | e4c326fb… |
| `resumen.json` | 3.455 B | 131f2cf4… |

## Entradas y código

- **`datos/q_local.jsonl`:** las 3.456 posiciones del manifiesto Q de producción rem158 (22346317…), una por afirmación y lado (sup, inf).
  - 3.449 posiciones proceden de filas padre aceptadas.
  - 7 son los lados padre faltantes del suplemento P7.
  - Cada posición guarda C_2, e_C2, e_G, K1, la categoría original y el conjunto.
- **m = 1/2:** valor de la producción rem158 (documento de elección 1b95216b…).
- **Versiones:** `contrato` usa e_C2. `conservadora` usa e_G cuando está declarado, y e_C2 en las 7 posiciones P7, que no lo tienen.
- **`src/q_local.py`:**
  - `cotas`, `lado_m`, `afirmaciones`, `evaluar` y `contar` están copiados sin cambios de `comun_q.py` rem157 (a63cb2a7…), el código que usó la producción rem158.
  - Las dos comprobaciones de `conciliar_q.py` se trasladan como adaptación de interfaz.
  - La regla (eps = 1/100, desigualdades estrictas, `canal_phi`) es la del conciliador COV i5, en copia exacta.
- **No se trasladan** las partes del arnés histórico que requieren rutas o transcripciones privadas: puerta nativa, bloqueo de importaciones y validación de tareas.

## Comparación con las referencias

| Control | Contrato | Conservadora |
|---|---|---|
| Posiciones (3.456) | 3.456, 0 distintas | 3.456, 0 distintas |
| Afirmaciones (1.728) | 1.728, 0 distintas | 1.728, 0 distintas |
| Inconclusas: `inconclusa_preservada` | 1.712 de 1.712 | 1.712 de 1.712 |
| Robustas padre: `robustez_refutada_por_testigo_sup` | 16 de 16 | 16 de 16 |
| Región `ambos` | 1.728 | 1.728 |
| Conteos iguales a la referencia | sí | sí |
| Cuerpo idéntico en bytes a la referencia | sí | sí |
| Categorías originales intactas | sí | sí |

- **Referencias:** `referencias/q_local_contrato.jsonl` y `referencias/q_local_conservadora.jsonl` contienen los campos científicos de los resultados aceptados Q-MAT-CONTRATO (95cfa83d…) y Q-MAT-CONSERVADORA (248193c2…). No incluyen la puerta nativa ni las rutas, que son privadas. La identidad en bytes se refiere a esas extracciones.
- **Conciliación:** no hay diferencias de canal o región entre contrato y conservadora, y las categorías originales siguen intactas. El resultado es igual a `CONCILIACION_Q` aceptada (38f99a45…).
- **Las 16 robustas:** las 16 afirmaciones robustas conservan su categoría original, `robusta_infactible_certificada`. Que se informen aparte como `robustez_refutada_por_testigo_sup` es una lectura diagnóstica del contraste en m = 1/2, no un cambio de categoría.
- **P7 se incorpora una sola vez:**
  - hay 7 posiciones P7, en 7 afirmaciones distintas;
  - coinciden con las siete del suplemento y ocupan su lado faltante;
  - ninguna posición padre está repetida.
- **Dependencias:** solo se cargaron `conciliar_cov` y `q_local` del paquete; no se cargaron los módulos de K1 (`external`, `macro`, `p7_calculo`). No hubo módulos fuera de la biblioteca estándar.

## Portabilidad

En la copia de los archivos de ejecución, lanzada desde otra carpeta, el comando terminó con código 0 en 0,464 s. Los dos `.jsonl` resultaron idénticos en bytes a los de la base. La prueba se hizo solo en esta máquina; la instalación aislada queda pendiente del Paso 2.4.

## Propuesta

Se propone cerrar Q local, m = 1/2, en este alcance, junto con P7. Quedan fuera:
- la elección de m como decisión científica;
- otros valores de m;
- la síntesis Exp8;
- el recálculo de techos y K1 de las 3.449 posiciones padre, que entran como valores aceptados.
