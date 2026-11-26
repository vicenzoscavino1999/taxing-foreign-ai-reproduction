# Cómo reproducir los resultados

Abre Windows PowerShell y sigue las instrucciones para [extraer el ZIP](../README.md#start-here) e [instalar el entorno](../README.md#installation). Si ya usaste la versión 1.0.0, puedes reutilizar el mismo entorno.

## Empezar por la Tabla 2

Desde la carpeta que contiene `run.ps1`, ejecuta:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 check
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 sensitivities
~~~

Abre `table3.md` en la carpeta que indica la consola. Las dos últimas columnas muestran qué porcentaje del techo combinado alcanza el impuesto doméstico solo. Cada menú se evalúa en su propio punto favorable. La columna de la regla lineal y la de incidencia estatutaria permiten comparar las dos formas de repartir la retención entre comprador y proveedor.

## Reproducir la Tabla 4

Desde la carpeta extraída, ejecuta `table6`, el nombre que conserva el paquete para esta tabla. El comando lee los certificados incluidos en el ZIP.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 table6
~~~

En la carpeta que indica la consola, abre `table6.md` para ver la Tabla 4 o `table4_claims.csv` para consultar las cotas de cada afirmación. La brecha es la capacidad fiscal menos el requisito, como fracción de las ganancias potenciales de la IA.

La Tabla 4 agrupa las 1.728 afirmaciones por instrumento y alcance. Las tres subfilas de países desglosan la retención sola. En las **1.712 afirmaciones inconclusas**, la brecha supera +0,01 en un punto admisible y cae por debajo de −0,01 en otro, tanto con la regla lineal (E11) como con la incidencia estatutaria. Las **16 insuficiencias robustas** corresponden a México: la retención sola queda por debajo del requisito compatible con la deuda en todo el rango de supuestos. La sección S6 del suplemento explica cómo se aplican los certificados con ambas reglas.

## Seguir la pregunta que te interesa

Para explorar otro resultado, usa la acción correspondiente con `run.ps1`.

- **Techos de la Tabla 3.** El [comando de la Tabla 4](#reproducir-la-tabla-4) también genera `table4_stored.md` con los techos de cada menú y diseño.
- **Las dos pruebas de Colombia.** `pilot` reproduce la clasificación al variar conjuntamente incidencia y costo de ocultamiento. `extensions` comprueba las 12 insuficiencias al reducir la incidencia a la mitad y conservar el costo original.
- **Informalidad, declaración del ingreso previo y cotas por país.** En la misma ejecución de `extensions`, abre `results.md`. Allí encontrarás la comparación de menús en un punto común por diseño, el piloto al 15 %, la retención sola y las dos cotas de México.

Estas acciones funcionan con los archivos del ZIP. Para recalcular los seis techos favorables desde sus insumos o ejecutar toda la base, sigue los [pasos de la corrida completa](../README.md#full-base-reproduction).
