# Resultado P7: cuatro K1 y suplemento de siete afirmaciones

**Fecha:** 2026-11-16. **Resultado:**
- Los cuatro K1 de P7 se recalculan desde entradas ligadas guardadas y coinciden en binary64 con sus referencias: 18 valores.
- El suplemento de siete afirmaciones se regenera desde esos K1 y los techos COV/ENF aceptados. Es idéntico, campo a campo y en bytes, a `SUPLEMENTO_P7.jsonl` de producción rem154.

Alcance: es una prueba local de FAM12/P7 que parte de entradas ligadas. No reconstruye la selección de entradas desde los datos nacionales originales ni recalcula techos COV/ENF. No reproduce el paper.

## Comandos y tiempos

Intérprete: CPython 3.12.4 de 64 bits (tags/v3.12.4:8e8a4ba, MSC v.1940), solo biblioteca estándar, con `-B -I -X utf8`.

Cada comando se lanzó desde la carpeta temporal del usuario, no desde la base, como un único proceso, con un límite de 600 s que ningún comando alcanzó. La duración se cronometró de principio a fin, incluido el arranque del intérprete. Ninguna ejecución escribió en stderr.

```text
python -B -I -X utf8 <base>/reproducir.py revisar
python -B -I -X utf8 <base>/reproducir.py p7-k1 --salida <base>/salidas/p7_k1_01.json
python -B -I -X utf8 <base>/reproducir.py p7-suplemento --salida <base>/salidas/p7_suplemento_01.json
python -B -I -X utf8 <base>/reproducir.py p7 --salida <base>/salidas/p7_02.json
```

| Comando | Código | Duración total | Cálculo interno | Salida | sha256 |
|---|---|---|---|---|---|
| `revisar` | 0 | 0,230 s | — | — | — |
| `p7-k1` | 0 | 0,267 s | 0,074 s | `p7_k1_01.json` (1.951 B) | 4c613e2b… |
| `p7-suplemento` | 0 | 0,260 s | 0,084 s | `p7_suplemento_01.json` (21.333 B) | 0074721b… |
| `p7` (piloto original) | 0 | 0,234 s | — | `p7_02.json` (892 B) | 8db07d40… |

`p7_02.json` es idéntico en bytes a `p7_01.json`, que se conserva: el piloto original no cambió.

## Los cuatro K1

Todos se calculan con `derivar_k1` sin cambios, a partir de `GridCell.Q`, `macro.bridge` y `external.K1`. Los cuatro tienen `macro_admisible = true` y ninguna razón macro.

| Unidad | Celda externa | K1 | K1 (hex) | Q | lambda_pi | gain_share |
|---|---|---|---|---|---|---|
| S1-N-df | EXT:MEX:GMI:GMI_ideal_aggregate:r0:debt_consistent:0.0 | 7.525385905044281 | 0x1.e19fec33fc738p+2 | 0.046329926945256984 | 0.6156485199543313 | 0.01 |
| S1-G-df | EXT:MEX:GMI:GMI_ideal_aggregate:r4:debt_consistent:0.0 | 7.541397402519062 | 0x1.e2a6414a7d5bbp+2 | 0.04642992694525696 | 0.615667421660446 | 0.01 |
| S1-N-f | EXT:COL:PEN:r4:baseline:0.05 | 0.07264204216247487 | 0x1.298ab3b67091bp-4 | 0.011206155833979763 | 1.542654295003919 | 0.1 |
| S1-G-d | EXT:COL:PEN:r4:baseline:0.05 | 0.07046704938855368 | 0x1.20a20e891c7cbp-4 | 0.011206155833979763 | 1.5902689173473519 | 0.1 |

Comparación hexadecimal exacta, 18 valores en total:
- S1-N-df y S1-G-df: K1, Q, lambda_pi, gain_share y dme_gai, 5 cada uno.
- S1-N-f y S1-G-d: K1, Q, lambda_pi y gain_share, 4 cada uno. dme_gai no tiene referencia guardada para estas celdas. La entrada ligada vale 0 por el binding D7, y no se inventa una referencia para ella.

Referencias de los dos casos nuevos:
- **K1:** el resultado P7 aceptado de rem154 (P7-K1-S1-N-f 5e5732d3…, P7-K1-S1-G-d ade869e0…).
- **Q, lambda_pi y gain_share:** la equivalencia guardada en `MANIFIESTO_P7.json` (f3d4a848…).

### Cómo se ligaron las entradas de S1-N-f y S1-G-d

Se reutilizó el método de ligadura de rem153 (`ligar_entradas_p7.py`, 4b4e5d40…), con su mismo código importado por huella. Solo cambian el conjunto (`CMP-E1.micro`) y el país (COL):
- **omega:** se toma de `Run.omega_points` con los nueve parámetros estructurales del padre y se identifica por `omega_id`. Hubo 96 puntos candidatos.
- **shares y estado nacional:** salen de `Providers.national` y se identifican por `national_state_sha256`. Hubo 9 estados candidatos.
- **grid y bound:** proceden de la rejilla efectiva (b94b9eed…), en la celda `EXT:COL:PEN:r4:baseline:0.05`, con `addback_completo` y capa sensibilidad.
- **dme_gai:** vale 0, por el binding D7.

Para validar las entradas sin leer K1, se cruzaron con las filas de origen S1-f y S1-d (`cell_context`, `lambda_pi_envelope`). Los espías registraron cero llamadas a K1, supremos o techos. Ninguna entrada se ajustó al K1 esperado.

La ligadura tardó 1,2 s y la herramienta queda en `extraccion/`.

Única adaptación: la tabla de capas de `entradas_p7.py` solo conoce `guardrail_deuda` y `nucleo_contable`. Para estas dos celdas, la capa se comprobó contra la que declara la rejilla (sensibilidad).

## Suplemento de siete afirmaciones

Las siete filas se generan en `src/p7_suplemento.py`, a partir del bucle de `conciliar_p7.py` de rem153 (6c9fb4a5…), sin cambio de fórmula:
- K1 recalculados en la misma ejecución.
- Techos COV/ENF/padre aceptados, tomados del manifiesto P7 y sin recalcular.
- Regla del conciliador COV i5 (`src/conciliar_cov.py`, copia exacta fef92f1c…), con `cotas_G`, `lado`, `canal_phi` y `signo`.
- eps = 1/100, desigualdades estrictas y fracciones exactas.
- La preservación no exige signos opuestos en los dos testigos.

La referencia `SUPLEMENTO_P7.jsonl` solo se lee después de calcular, para comparar.

| Afirmación (sin prefijo CLM) | Unidad | Lado faltante | K1 | Categoría original | Lado presente ENF |
|---|---|---|---|---|---|
| historical_anchor:c:COL:conditional_none:G:…:micro:sensibilidad | S1-G-d | sup | reutilizado | cambio_de_signo_certificado | techo ENF completo |
| historical_anchor:ci:COL:d:domestic_unchanged:G:…:micro:sensibilidad | S1-G-d | sup | reutilizado | cambio_de_signo_certificado | techo ENF completo |
| historical_anchor:ci:MEX:df:conditional_full:G:…:guardrail_deuda | S1-G-df | inf | confrontación | cambio_de_signo_certificado | resolución aceptada rem148 |
| historical_anchor:ci:MEX:df:conditional_full:N:…:guardrail_deuda | S1-N-df | inf | confrontación | cambio_de_signo_certificado | techo ENF completo |
| primary:ci:COL:f:conditional_full:N:…:micro:sensibilidad | S1-N-f | sup | reutilizado | inconclusa_por_testigos_en_tolerancia | techo ENF completo |
| primary:ci:MEX:df:conditional_full:G:…:guardrail_deuda | S1-G-df | inf | confrontación | cambio_de_signo_certificado | resolución aceptada rem148 |
| primary:ci:MEX:df:conditional_full:N:…:guardrail_deuda | S1-N-df | inf | confrontación | cambio_de_signo_certificado | techo ENF completo |

Comparación y cobertura:
- 7 filas y 0 filas distintas en la comparación campo a campo. La serialización es idéntica en bytes a la referencia aceptada (a450014b…).
- 7 afirmaciones y 4 unidades.
- `canal_COV` y `canal_ENF` valen `inconclusa_preservada` en las 7. El lado faltante queda `demostrado` en COV, ENF y padre en las 7. La cobertura es `ambos` en COV y ENF.
- Las categorías originales se conservan (6 `cambio_de_signo_certificado`, 1 `inconclusa_por_testigos_en_tolerancia`), igual que los canales aceptados `canal_eta_f_aceptado` y `canal_phi_COV_aceptado`.
- El lado presente COV procede de la fila COV aceptada en las 7. El lado presente ENF procede del techo ENF completo en 5 filas y de la resolución aceptada rem148 (clave d59edf8a…) en 2.
- **Limitación histórica que se mantiene:** en esas 2 filas S1-G-df, el techo ENF histórico sigue incompleto. Se usan las cotas exactas de la resolución aceptada, marcadas como tales, sin promover ni recalcular el techo.
- El padre informa del lado faltante y no fabrica el canal combinado (`canal: null`), como en la referencia.

## Qué se recalculó, qué se regeneró y qué se reutilizó

- **Recalculado:** los cuatro K1 y Q, lambda_pi, gain_share y dme_gai de cada celda.
- **Regenerado:** las siete filas del suplemento: intervalos G exactos, lados, signos y canales.
- **Reutilizado como entrada aceptada:**
  - techos COV, ENF y padre, con sus C_2 y errores certificados;
  - lado presente COV y resolución ENF rem148;
  - categorías originales y canales aceptados;
  - entradas ligadas de las cuatro celdas.
- **Código:**
  - `external.py`, `macro.py` y `conciliar_cov.py` son copias exactas.
  - `derivar_k1` y el bucle del suplemento están extraídos sin cambio de fórmula.
  - Adaptaciones de interfaz, declaradas en cada archivo y en `fuentes_fam12.json`: las entradas llegan como datos, el K1 llega como argumento, y se quitaron la puerta nativa y la escritura del arnés histórico.

## Portabilidad

Para la prueba se copiaron a una carpeta fuera del repositorio solo los archivos de ejecución:
- `reproducir.py`, `fuentes_p7.json`, `fuentes_fam12.json` y `README.md`;
- `src/` (6 archivos), `datos/` (4) y `referencias/` (6).

Los cinco comandos se lanzaron desde una tercera carpeta, y todos terminaron con código 0:

| Comando | Duración |
|---|---|
| `revisar` | 0,195 s |
| `p7` | 0,260 s |
| `p7-k1` | 0,240 s |
| `p7-suplemento` | 0,241 s |
| `q-local` | 0,464 s |

Salvo la versión de Python y los tiempos, las salidas son iguales a las de la base.

Cada salida registra los módulos cargados fuera de la biblioteca estándar y del paquete. La lista quedó vacía.

Ninguno de los archivos copiados contiene rutas privadas, nombres de usuario ni identificadores de transcripciones.

Alcance real: el traslado se probó en esta máquina y con el mismo intérprete. La instalación aislada final queda pendiente del Paso 2.4.

## Cambios realizados en esta sesión

- **Nuevos:**
  - `datos/p7_k1_reutilizados.json`, `datos/p7_suplemento.json`;
  - `referencias/p7_k1_reutilizados.json`, `referencias/p7_suplemento.jsonl`;
  - `src/conciliar_cov.py`, `src/p7_suplemento.py`;
  - `fuentes_fam12.json`;
  - herramientas de extracción en `extraccion/`, que no forman parte de la ejecución.
- **`reproducir.py`:** comandos `p7-k1`, `p7-suplemento` y `q-local`. `revisar` comprueba también `fuentes_fam12.json`. El piloto `p7` no cambia.
- **Sin cambios:** `fuentes_p7.json`, `datos/p7.json`, `referencias/p7.json` y los tres archivos de `src/` del piloto.
- Se actualizaron `README.md` y `catalogo.json` (F12-P7-K1 y F12-P7-G).
- **Este archivo:** se reescribe el encabezado. El registro del piloto se conserva abajo, sin la ruta local del intérprete.

## Propuesta

Se propone cerrar P7 dentro del alcance probado: los cuatro K1 desde entradas ligadas y el suplemento desde techos aceptados, con traslado local. Quedan fuera:
- la reconstrucción de entradas desde datos nacionales (FAM01);
- el recálculo de techos COV/ENF;
- la instalación aislada (Paso 2.4).

---

## Registro del piloto (dos K1, 2026-11-16)

Entorno: CPython 3.12.4 de 64 bits (MSC v.1940), biblioteca estándar, `-B -I -X utf8`. Hubo un solo proceso cada vez, con un límite de 60 s que no se alcanzó.

| Paso | Inicio (UTC) | Duración | Código de salida | Salida en consola |
|---|---|---|---|---|
| `revisar` | 12:02:50.216Z | 0,18 s | 0 | «Archivos y sintaxis conformes. Ningún cálculo ejecutado.» |
| `p7` | 12:02:58.919Z | 0,302 s | 0 | `{"salida": "…\\salidas\\p7_01.json", "concordante": true}` |
| `revisar` (tras el cálculo) | — | 0,158 s | 0 | igual que la primera |

| Caso | Campo | Obtenido | Referencia (hex) |
|---|---|---|---|
| S1-N-df | K1 | 7.525385905044281 | 0x1.e19fec33fc738p+2 |
| S1-N-df | Q | 0.046329926945256984 | 0x1.7b88e621ca535p-5 |
| S1-N-df | lambda_pi | 0.6156485199543313 | 0x1.3b36486611be8p-1 |
| S1-N-df | gain_share | 0.01 | 0x1.47ae147ae147bp-7 |
| S1-N-df | dme_gai | 0.0 | 0x0.0p+0 |
| S1-G-df | K1 | 7.541397402519062 | 0x1.e2a6414a7d5bbp+2 |
| S1-G-df | Q | 0.04642992694525696 | 0x1.7c5a9d3923353p-5 |
| S1-G-df | lambda_pi | 0.615667421660446 | 0x1.3b38c2a27d0f5p-1 |
| S1-G-df | gain_share | 0.01 | 0x1.47ae147ae147bp-7 |
| S1-G-df | dme_gai | 0.0 | 0x0.0p+0 |

`salidas/p7_01.json`: 892 B, sha256 `8db07d40e6ba6677e6e2061bee4abfc8eb2c94d1301504e4cc32414bad2c02ae`. Antes y después del cálculo, las huellas de `src/external.py`, `src/macro.py`, `src/p7_calculo.py`, `datos/p7.json` y `referencias/p7.json` coincidían con `fuentes_p7.json`. No se generó bytecode.

En Git, el repositorio no tenía commits: el estado inicial se añadió al índice con `git add -A`, sin commit, para ver los cambios con `git diff`. El primer commit queda para el autor.

## Revisión de Codex — 2026-11-16

Salida guardada revisada sin repetir cálculos: exactamente dos casos, diez valores
binary64 idénticos a las referencias, resumen coherente y SHA-256 de salida
coincidente con el declarado. Los cinco archivos de código, entradas y referencias
coinciden con las huellas de extracción. El piloto queda conforme en ese alcance.
La duración de 0,302 s es la registrada por el ejecutor; no se volvió a medir.

Las dos fuentes de los K1 reutilizados existen y coinciden con las huellas citadas.
Sus contextos identifican omega y estado nacional; todavía hay que reunir las
entradas completas para recalcularlos. Este cotejo no certifica la reproducción
completa de P7 ni una instalación independiente.

## Revisión de la ampliación por Codex — 2026-11-16

Conforme en el alcance declarado: cuatro K1 desde entradas ligadas y suplemento
desde techos aceptados. Se cotejaron los 18 valores binary64 y las siete filas
contra las referencias y el suplemento original de rem154, conservando categorías,
las cuatro unidades y las resoluciones ENF. Se leyeron la ligadura de entradas y
la adaptación del bucle del conciliador; la regla COV es copia exacta.

Se comprobó la integridad de los 16 archivos declarados entre ambos manifiestos.
El cotejo no repitió el cálculo ni la ligadura histórica. Las duraciones y la
prueba de traslado son las informadas por el ejecutor; no se reinterpretan como
una instalación aislada. Esta revisión amplía la del piloto inicial y conserva
los límites declarados sobre datos nacionales y techos.
