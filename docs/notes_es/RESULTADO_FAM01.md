# FAM01: base detallada S1/S2/S3/C2 y preparación de R2/R3

**Estado vigente, 2026-11-16:** F2 adoptada por el autor y preparación de
FAM01 cerrada en su alcance. Los pilotos revisados quedan aceptados bajo ese
criterio. El lote completo y la instalación aislada siguen pendientes.
La entrega y las revisiones siguientes se conservan como historial; la
adopción y su alcance constan al final de este archivo.

## Adopción de F2 en el comparador (ejecutor, 2026-11-16)

La decisión literal del autor y su alcance constan al final del archivo, en
«Adopción de F2 y cierre de preparación». Después se actualizó el comparador
para que las comparaciones nuevas registren la adopción. No se reescribió
ninguna salida anterior ni se recalculó el modelo.

Lo adoptado es la propuesta F2-CANDIDATA-ENTORNO-PORTABLE-v1 de la sección
«Decisión F2», sin cambios de contenido. En el código se llama
F2-ENTORNO-PORTABLE-v1:
- mismos campos de ubicación;
- misma proyección de referencia (`entorno_f2_referencia.json`, b6db2964…),
  cuyo texto interno conserva el nombre de la propuesta;
- mismo alcance: Windows con CPython 3.12.4 oficial, dos ubicaciones de venv
  y una máquina. No acredita otra plataforma ni una instalación aislada.

No cubre cambios de código, contrato, configuración, tolerancias ni
criterios científicos. Tampoco autoriza el lote ni su tiempo de máquina
(Paso 3).

Cambios en el código, solo de etiqueta y de código de salida:
- `src/fam01.py` registra la decisión en `ADOPCION_F2`. La pasada
  `limpia_f2_candidata` pasa a `limpia_f2`, y su estado a
  `comparacion_limpia_f2`. La reproducción aceptada con ella se llama
  `aceptada_comparacion_limpia_con_F2`.
- `fam01-comparar` termina con 0 en esa reproducción. La comparación
  histórica y la limpia con entorno estricto siguen informándose aparte, con
  su rechazo.
- La comprobación F2, E2/E3, el historial, el saneamiento y la validación no
  cambian.
- La receta ya no lista F2 entre lo que falta; queda solo la autorización
  del Paso 3.

Comprobaciones posteriores, sin recalcular el modelo:

| Comprobación | Resultado |
|---|---|
| `fam01-comprobar` (`comprobar_08.json`) | cumple; 3.869 archivos sin diferencias; F2 equivalente; tres correspondencias de saneamiento comprobadas |
| Pilotos `_03`: `comparar_R2_09.json` y `comparar_R3_07.json` | histórica y limpia estricta `correspondencia_incorrecta`; limpia con F2 `aceptada`; reproducción `aceptada_comparacion_limpia_con_F2`, código 0 |
| Frente a `comparar_R2_08` y `comparar_R3_06` | idénticas salvo las etiquetas y el registro de la adopción |
| Salida `_02` (contrato histórico, `.venv-fam01`) | aceptada con F2 |
| Salida `_01` (`.venv` antiguo, sin registro) | no aceptada, código 1; F2 no equivalente |
| Sin documento de entorno; numpy cambiado en él; entorno no conforme | F2 no equivalente; no aceptada |
| Validación ausente | `pendiente_validacion` |
| C_2 + 1 ulp con todo rehecho | `corrida_nueva_invalida`; no aceptada |
| FAM12 (cambió `reproducir.py`) | `revisar` y `_06` de `p7-k1`, `p7-suplemento` y `q-local` concordantes |
| Receta (`receta_07.json`) | preparada y sin ejecutar; solo falta autorizar el lote (Paso 3) |

Las pruebas sobre copias están en `pruebas_dirigidas_03.json`.

Las secciones siguientes describen la tercera entrega, anterior a la
adopción. Allí, «candidata», `aceptada_bajo_criterio_candidato_F2` y el
código 2 corresponden a las salidas guardadas `comparar_R2_08` y
`comparar_R3_06`, que no se reescriben.

## Tercera entrega: ajustes finales

Fecha: 2026-11-16 (tercera entrega del día: ajustes finales pedidos en la
revisión de Codex de la segunda).

Alcance de esta entrega:
- corregir E2/E3 en el comparador limpio;
- separar el historial operativo de 195 originales R2;
- sanear los nueve archivos de ejecución con rutas privadas;
- repetir los dos pilotos con salidas nuevas.

No se ejecutaron los lotes de 1.740 ni de 27, ni R1, quiebres o Q histórica.
La entrega no adoptaba F2/F3/F4 ni editaba ninguna regla histórica, y no
abría FAM02/FAM03.

## Resumen

| Fila | Antes (segunda entrega, revisada) | Ahora |
|---|---|---|
| F01-R3-MARCO | Cerrado en alcance documental, 21/21. | Sin cambios. |
| F01-R2 | Referencias de las 1.740 unidades. Piloto calculado y validado, con valores iguales. Comparación con F2: un texto R1 fuera de E2. 195 originales con historial sin tratar. Contrato y registro con rutas privadas. | E2/E3 con el nivel real de la unidad. Historial separado como procedencia. Contrato y registro saneados, con correspondencia comprobada. Piloto `_03` calculado, validado y aceptado **solo bajo F2**. F2 adoptada después para FAM01. |
| F01-R3 | Referencias de las 27 unidades. Piloto calculado y validado. 5 NA comprobadas. | Piloto `_03` igual que R2: aceptado solo bajo F2. Las 5 NA revalidadas, 9/9. F2 adoptada después para FAM01. |

Respuestas a las cinco preguntas del encargo:

1. **E2/E3 con el nivel real.** Sí, en el comparador limpio (regla
   E2E3-NIVEL-R1-v1).
   - El k declarado debe ser el que da `r1_level` del núcleo para el dominio
     de la propia unidad. No basta una cifra del rango.
   - Cubre E2 (certificado) y E3 (incompleto) sin cruzarlos.
   - En los pilotos, k esperado 7 y declarado 7.
2. **Dos campos de historial.** Sí, como procedencia operativa:
   `tramo_anterior` (183) y `recuperacion_de` (12).
   - Solo en esas dos rutas de primer nivel.
   - Estados, validación, cifras, veredictos y cualquier otra clave se
     siguen comparando.
3. **Nueve archivos saneados.** Sí. La ruta funciona con las copias
   públicas: comprobación, cálculo, validación y comparación de los dos
   pilotos.
   - Contratos y registro con huellas públicas propias; la histórica queda
     como referencia.
   - La correspondencia se comprueba en cada carga.
4. **Pilotos.** Ambos calculan y validan con los mismos valores.
   - Comparación limpia con F2 candidata: `aceptada`, sin diferencias.
   - Reproducción: `aceptada_bajo_criterio_candidato_F2` (código 2).
   - Comparación histórica (DR-1 tal cual): `correspondencia_incorrecta`
     por la identidad técnica (entorno y contrato).
   - Comparación limpia con el entorno estricto: `correspondencia_incorrecta`
     solo por el entorno.
5. **¿Solo F2?** Sí. No queda ningún ajuste técnico concreto de FAM01. La
   autorización de los lotes y de su tiempo de máquina pertenece al Paso 3.

Comparación de los pilotos (`comparar_R2_08.json` y `comparar_R3_06.json`):

| | R2 00305608… | R3 S2:02193cdff172d31c:1 |
|---|---|---|
| Cálculo | terminado | terminado |
| Validación productiva | verificada (`completa_validada`) | verificada (`completa_validada`) |
| Valores frente al original | iguales: estado, C_2, error, G, K_comp_1, veredicto, estado de cómputo, filas por tabla | iguales |
| Histórica: vigentes + selladas, DR-1 tal cual | correspondencia_incorrecta | correspondencia_incorrecta |
| Limpia: E2/E3, historial y saneamiento; entorno estricto | correspondencia_incorrecta (DR-1: entorno) | correspondencia_incorrecta (DR-1: entorno) |
| Limpia + F2 candidata | aceptada, 0 diferencias sin regla | aceptada, 0 diferencias sin regla |
| Reproducción | aceptada_bajo_criterio_candidato_F2 | aceptada_bajo_criterio_candidato_F2 |

En la pasada limpia con F2, cada piloto tiene 16 diferencias, todas
cubiertas por R-SUCESION-S6:
- claves de identidad técnica y sus derivadas;
- los textos de evidencia G (E1) y R1 (E2 con k = 7).

No se aplicó ninguna tolerancia numérica.

El resultado histórico no cambia: el comparador histórico no acepta ninguno
de los dos pilotos.

## Decisión F2 (adoptada por el autor para FAM01, 2026-11-16)

Texto que se presentó a decisión y que el autor adoptó sin cambios: ¿se
adopta F2-CANDIDATA-ENTORNO-PORTABLE-v1 como equivalencia de ubicación del
entorno para DR-1, con este alcance?

- **Propiedades que conserva:**
  - perfil aprobado cumplido sin discrepancias;
  - lock completo: 10 paquetes con su versión y el sha256 de su rueda,
    pip 26.1.2 y ningún paquete adicional;
  - CPython 3.12.4 oficial: python.exe, python312.dll y lanzador del venv
    con sus sha256;
  - Windows-11-build-26200, AMD64;
  - OpenBLAS 0.3.27 ILP64, LAPACK y `blas.max_threads` 24;
  - las seis variables de hilos a 1, locale C, TZ UTC y semilla 0.

  Cada ejecución conserva su huella real.
- **Campos de ubicación que pueden diferir**, los únicos:
  - `fingerprint.executable.path` y `base_path`;
  - en el RECORD de cada paquete, las líneas de los lanzadores
    `Scripts/*.exe`; su `record_sha256` se recalcula sin ellas;
  - `fingerprint_sha256`, que deriva de los anteriores.
- **Alcance probado:** Windows con CPython 3.12.4 oficial, en esta máquina,
  con dos ubicaciones de venv: `.venv-fam01` (4cc5b9a8…) y un venv creado
  con la misma receta en otra carpeta (a7351b2c…).
  - No se extiende a otra plataforma, intérprete, versión de paquete o
    máquina.
  - Una diferencia en cualquier propiedad conservada rechaza la
    equivalencia.
- **No cubre el saneamiento.** Los cambios de contrato, registro y lector
  tienen su propia correspondencia comprobada (SAN-RUTAS-v1). F2 no admite
  ningún cambio de código, contrato, configuración ni tolerancia.
- **Efecto.** La comparación limpia con F2 es la referencia de FAM01. El
  dictamen histórico se conserva como antecedente y sigue sin aceptar los
  pilotos.

## Lo que falta y límites

Con F2 adoptada, la preparación de FAM01 no tiene pendientes técnicos.
Queda:
- **Paso 3:** autorización de los lotes y de su tiempo de máquina. No hay
  estimación de coste. Los pilotos de esta entrega tardaron unas 1,9 veces
  más que los de la segunda en la misma máquina. No había otro proceso de
  Python, y la carga de la máquina no se midió. La variante agrupada no se
  ha medido.
- **Paso 2.4:** instalación aislada. El traslado se hizo en esta máquina
  (ver «Revalidaciones»).

Límites conocidos, sin efecto en la ruta de FAM01:
- La carpeta de la recepción nacional conserva su nombre histórico
  (`866aa139…`) como ubicación. Su manifiesto público tiene otro árbol
  (61d79411…), por lo que `verify_reception`, que fija el árbol histórico,
  no lo aceptaría. FAM01 no lo usa.
- `nacionales.py` cambió una línea (ver «Saneamiento»). No entra en los
  patrones de código de la tupla técnica, así que `code_sha256` no cambia.
  Su huella nueva está declarada en `fuentes_fam01.json` junto a la de
  origen.
- Los manifiestos del contrato S3 y de D2 siguen listando la huella de
  origen de las cuatro copias saneadas en la entrega anterior, que no se
  leen al ejecutar. Igual que antes.

## E2/E3: nivel R1 real (E2E3-NIVEL-R1-v1)

- La regla histórica (R-SUCESION-S6 v2: sufijo «; nivel configurado=6,
  efectivo=k» con 0 ≤ k ≤ 6) no se edita. Sigue activa en la comparación
  histórica, y sus resultados se conservan.
- En las pasadas limpias, `definicion_equivalente` conserva E1 y aplica
  E2/E3 con un único k esperado.
  - k es `run.Run.r1_level` del núcleo con la configuración fijada
    (`RunConfig()`).
  - Se evalúa sobre `instrument_j` y las cotas superiores τ_d y τ_f del
    `frontier_context` estructural de la unidad.
  - Se calcula en el original y en la nueva, y debe coincidir.
  - Sin dominio, no hay k y E2/E3 no se aplican.
- El texto nuevo debe ser el original más el sufijo con ese k. Lo demás
  sigue igual:
  - E2 solo sustituye evidencia certificada y E3 solo evidencia
    incompleta; una incompleta no pasa a certificada ni al revés;
  - no cambian configuración, tolerancias, cotas, estados ni algoritmo.

Funciones, con k esperado 7 (`pruebas_dirigidas_02.json`):

| Caso | Limpia | Regla histórica |
|---|---|---|
| E2 con k = 7 | admite | rechaza |
| E2 con k = 6 | rechaza | admite |
| E2 con k = 8; configurado = 7; k ausente | rechaza | — |
| E3 con k = 7 | admite | rechaza |
| E3 con k = 8; E3 con otra cota | rechaza | — |
| Incompleta → texto certificado; certificada → texto incompleto | rechaza | — |

En los 1.767 originales k = 7. Los 1.181 con R1 certificado tienen k > 6:
con la regla histórica, su texto nuevo quedaría fuera de E2. Ningún original
tiene el texto que cubre E3, de modo que E3 solo se probó con casos
construidos.

## Historial operativo de 195 originales R2 (HIST-OPERATIVO-v1)

Alcance, comprobado documentalmente sin recalcular:
- `tramo_anterior` en 183 originales; subcampos: causa de la repetición,
  dónde se conserva, `doc_sha256` y `estado_final` del intento anterior;
- `recuperacion_de` en 12; subcampos: entrega, suite, trabajador, fase,
  motivo, nota, tiempo y `doc_sha256`;
- disjuntos, todos de R2 y solo en primer nivel: 0 apariciones anidadas en
  los 1.767 originales;
- sin esas claves, las 195 tienen las mismas claves de primer nivel que el
  resto de R2.

Tratamiento en las pasadas limpias:
- Esas dos rutas de primer nivel se añaden a los campos operativos del
  comparador, que solo se comparan en primer nivel.
- Se informan aparte, en `procedencia_operativa_del_original` y
  `procedencia_operativa_distinta`.
- No se excluye ninguna otra clave ni la misma clave en otro nivel.
- El estado actual, la validación, el motivo de una incompletitud, las
  cifras y los veredictos se siguen comparando.

Controles sobre los 195 originales guardados, cada uno comparado con el
mismo documento sin su historial:
- histórica: 195/195 con diferencia científica solo en esa clave;
- limpia: 195/195 sin diferencia científica y con el historial listado
  como procedencia.

Controles negativos, uno por clave (`tramo_anterior` y `recuperacion_de`):
- `estado_final` alterado, también con el historial copiado: discrepancia;
- `resultado.estado` alterado: discrepancia;
- historial anidado en `resultado`: discrepancia.

## Saneamiento de los nueve archivos de ejecución (SAN-RUTAS-v1)

Transformación explícita, solo en las cadenas de procedencia, en sus tres
grafías (barra invertida, barra y JSON escapado):
- prefijo absoluto de la raíz del proyecto original → ruta relativa;
- carpeta de descargas del usuario → `<descargas>`.

`extraccion/extraer_fam01.py` la aplica contra los archivos de origen y
comprueba:
- que hay algo que sanear;
- que en el Markdown solo difieren las líneas con ruta privada;
- que no queda ninguna ruta absoluta.

Solo sobrescribe un destino si contiene exactamente los bytes de origen.
Las fuentes históricas no se tocaron.

| Archivo | Se lee en | Pública | Origen (histórica) |
|---|---|---|---|
| `contratos/CORRESPONDENCIA_AJUSTE_ACTUAL.csv` (G-NA-1 y CA2-4) | cálculo y comparador | ea464e1e… | c2107339… |
| `contratos/CORRESPONDENCIA_HISTORICA.csv` (ambos) | cálculo y comparador | a30f9296… | 433f194a… |
| `contratos/CORRESPONDENCIA_PROPUESTA_ANTERIOR.csv` (ambos) | cálculo y comparador | 38920334… | a43a2a60… |
| `candidatos/PLAN_REPRODUCCION_INTEGRADO_BORRADOR.md` (ambos) | cálculo y comparador | d2cbb6aa… | 7481f8fc… |
| `evidencia/registro_snapshots.json` (recepción nacional) | cálculo (ruta nacional) | cd986a5c… | 2d15e6a8… |

Identidades del paquete público y su referencia histórica:

| Identidad | Pública | Histórica (referencia) |
|---|---|---|
| Contrato G-NA-1 (tupla técnica de la corrida nueva) | f3dd49eb… (`contract_sha256`) | 7bde9f15… (`contract_sha256_historico`) |
| Contrato CA2-4 (validación de los originales) | 8e44cfa7… (`contract_publico_sha256`) | 4d7e676a… (`contract_sha256`, el que declaran los originales) |
| Manifiesto de la recepción nacional | 61d79411… | a049c27f… |
| `herramientas/nacionales/nacionales.py` | 23ed94aa… | 1820bc86… |

- Los tres manifiestos públicos derivan del histórico. Solo cambian los
  bytes y el sha256 de las entradas saneadas y, en la recepción, el árbol
  que deriva de ellas.
- Los históricos se conservan en `referencias/fam01/manifiestos_historicos/`.
- En `nacionales.py` cambió solo la línea del pin del registro, que admite
  la huella histórica y la pública (`cd986a5c…`).
- `fuentes_fam01.json` declara 17 entradas con `sha256_origen`:
  - 13 copias saneadas (4 de la entrega anterior y estas 9);
  - 3 manifiestos derivados;
  - 1 lector adaptado.
- El paquete no contiene ni necesita las copias privadas.

Las corridas nuevas declaran la huella pública del contrato. Por eso su
run_id cambia respecto de `_02` (la fórmula incluye `contract_sha256`).
`ejecucion.json` registra las dos huellas. A los bytes nuevos nunca se les
asigna la huella histórica.

`correspondencia_saneamiento()` (`src/fam01.py`) se ejecuta en
`fam01-comprobar` y en cada comparación. Compara cada manifiesto público con
su histórico y exige:
- mismas entradas en el mismo orden;
- que cada entrada que cambia sea una copia saneada declarada en
  `fuentes_fam01.json`, con `sha256_origen` igual a la entrada histórica y
  con sha256 y bytes iguales a los del archivo;
- que nada más del manifiesto cambie;
- en la recepción, que el árbol derive de los archivos.

Solo con esa correspondencia comprobada:
- el comparador carga el contrato CA2-4 público para validar los
  originales;
- la pasada limpia trata el contrato público como el G-NA-1 histórico en
  las condiciones de DR-1.

Sin ella, DR-1 mantiene «técnica nueva no admitida». La transformación se
comprueba al extraer, contra los archivos de origen; al ejecutar, se
comprueba que el resto del contenido no cambió.

Saneamiento disfrazado (`pruebas_dirigidas_02.json`), todos rechazados:
- `formulas.json` cambiado, con el manifiesto rehecho;
- un CSV saneado con otra celda cambiada, con el manifiesto rehecho;
- otro campo del manifiesto cambiado;
- un registro de snapshots cambiado sin declararlo.

## Pilotos con salidas nuevas (`_03`)

Un cálculo a la vez, con el lanzador acotado: 600 s, terminación del árbol
de procesos y 0 procesos vivos al terminar. Python de `.venv-fam01` con
`-B -P -s -X utf8`, `PYTHONHASHSEED=0`, `TZ=UTC` y las seis variables de
hilos a 1.

| | R2 00305608… | R3 S2:02193cdff172d31c:1 |
|---|---|---|
| Salida | `R2_00305608_03` | `R3_S2_02193cdf_1_03` |
| rc / pared / CPU / memoria máx. | 0 / 273,1 s / 254,2 s / 282 MB | 0 / 225,2 s / 212,1 s / 337 MB |
| contexto / cálculo / validación / total (s) | 0,98 / 269,84 / 0,72 / 271,59 | 0,98 / 222,71 / 0,05 / 223,78 |
| documento nativo / filas | f53f7273… / d339b205… | 84536534… / 104e41e6… |
| comparable R2 | a660d341… | — |
| registro productivo | 4676f818… | 811afdc1… |
| run_id | BRUN-a72183b90c16abea0c23c5d7 | BRUN-a72183b90c16abea0c23c5d7 |
| entorno | conforme, F2 equivalente (4cc5b9a8…) | conforme, F2 equivalente |

El cálculo tardó unas 1,9 veces más que en `_02` (142,5 s y 117,3 s). No
había otro proceso de Python. Se informa tal cual y no se usa como medida
del coste.

La comparación de las salidas `_02` con el código actual da los mismos
estados: `comparar_R2_07.json` y `comparar_R3_05.json`.

## Pruebas dirigidas (`pruebas_dirigidas_02.json`)

Sobre copias de las salidas `_03` en una carpeta temporal, sin recalcular.

| Caso | Reproducción | Comparación limpia + F2 |
|---|---|---|
| Control R2 y R3 | aceptada_bajo_criterio_candidato_F2 | aceptada |
| Nivel efectivo 8 en lugar de 7 | no_aceptada | corrida_nueva_invalida |
| Nivel efectivo 6 (admitido por la regla histórica) | no_aceptada | corrida_nueva_invalida |
| Evidencia R1 certificada pasada a limitación | no_aceptada | corrida_nueva_invalida |
| C_2 + 1 ulp | no_aceptada | corrida_nueva_invalida |
| Veredicto invertido | no_aceptada | corrida_nueva_invalida |
| Historial añadido en primer nivel, sin otro cambio | aceptada_bajo_criterio_candidato_F2, con `procedencia_operativa_distinta` = [`tramo_anterior`] | aceptada |
| `estado_final` alterado junto al historial | no_aceptada | discrepancia |
| `tramo_anterior` anidado en `resultado` | no_aceptada | discrepancia |
| Validación ausente | pendiente_validacion | pendiente_validacion_productiva |

En los casos de nivel alterado, la validación propia de la corrida nueva ya
detecta que la referencia de la evidencia no es el hash de su contenido. Por
eso la regla E2/E3 se prueba aparte, a nivel de función (sección
«E2/E3»).

Las condiciones de DR-1 en la pasada limpia dan:
- con F2 y saneamiento comprobado: se cumplen;
- sin saneamiento comprobado: «técnica nueva no admitida»;
- sin F2: además, «environment/tolerances distintos».

## Revalidaciones

- **NA:** las 5 conformes, 9/9 cada una (`na_*_02.json` y, para la
  piloto, `na_S2_306ff8f9_0_04.json`).
- **Comprobación:** `fam01-comprobar` (`comprobar_07.json`) cumple:
  - 3.869 archivos de `fuentes_fam01.json` sin ausencias ni diferencias;
  - entorno conforme y F2 equivalente;
  - las tres correspondencias de saneamiento comprobadas.

  Frente a la tupla S6 admitida solo difieren `contract_sha256` (copia
  pública) y `environment_sha256`.
- **Traslado** (`traslado_fam01_03`, sin aislamiento real):
  - copia de los archivos de ejecución sin venv, extracción, `local` ni
    salidas, salvo las dos `_03`;
  - lanzada desde una tercera carpeta con el Python de `.venv-fam01`;
  - el venv no se volvió a crear, porque su receta no cambió.

  Resultados:
  - `revisar`: rc 0;
  - `fam01-comprobar`: cumple, con 0 archivos ausentes o distintos y las
    tres correspondencias comprobadas;
  - las dos comparaciones: idénticas a las hechas en sitio salvo segundos y
    rastro;
  - rastro de lecturas: ningún archivo fuera del paquete y del intérprete.

  Fue en la misma máquina.
- **Rutas personales:** ninguna en los archivos del paquete (búsqueda de
  rutas absolutas y de marcas de carpetas personales).
- **FAM12**, porque cambió `reproducir.py`: `revisar` y `p7-k1`,
  `p7-suplemento` y `q-local` concordantes (`p7_k1_05.json`,
  `p7_suplemento_05.json` y `q_local_05/`).
- **Receta** (`receta_06.json`), preparada y sin ejecutar:
  - 1.767 unidades: 1.762 numéricas y 5 NA;
  - 130 tareas en la variante agrupada;
  - «lo que falta»: la decisión F2 y la autorización del Paso 3.

## Entradas y referencias

- `extraccion/extraer_fam01.py`, herramienta de desarrollo fuera del
  paquete público, extrae los originales con `Vinculo.original` del índice
  de paquetes de autoridad. Comprueba la huella del paquete y que el
  documento corresponde a su unidad (`id` y `cell_id` E12).
- `referencias/fam01/originales/` contiene 3.534 archivos (152 MB).
- `datos/fam01/clasificacion_manifiesto.json` guarda, por unidad R2:
  - familia, ruta y estrato de la entrada del manifiesto de bloque, la misma
    fuente que su testigo;
  - y, en las 6 unidades del productor piloto, `clave_estructural_lima1913`.

  Es la fuente del formato comparable.
- `fuentes_fam01.json` registra 3.869 archivos con su origen y sha256.
  `fam01-comprobar` los verifica todos. Las entradas con `sha256_origen` no
  son idénticas a su fuente: ver «Saneamiento».
- Se copiaron además las piezas de la validación:
  - `paquete_seleccion.py`, el Verificador S6 (a70cf904…);
  - `validador_r3.py` (d2a5cbb6…) y su histórico
    `validar_detallado_lima1533.py` (871b1d7f…);
  - el resto del código del productor que entra en su manifiesto.

  El núcleo de la instalación se comprobó idéntico al copiado: 37 archivos.

## Comandos

Con el Python de `.venv-fam01`, `-B -P -s -X utf8` y, en el entorno del
proceso, `PYTHONHASHSEED=0`, `TZ=UTC` y las seis variables de hilos a 1:

```text
reproducir.py fam01-unidad   --seleccion R2 --unidad <id> --salida salidas/fam01/R2/<id>        (cálculo + validación)
reproducir.py fam01-comparar --seleccion R2 --unidad <id> --nueva salidas/fam01/R2/<id> --salida salidas/fam01/R2/<id>.comparacion.json
reproducir.py fam01-na       --unidad <id NA> --salida salidas/fam01/R3/<id>.na.json
reproducir.py fam01-receta   --salida salidas/fam01/receta_08.json
```

**`fam01-unidad`** recorre una tarea: una o más `--unidad` de la misma
lista. Pasos:

1. Contexto S6.
2. Cálculo:
   - R2 como `tarea_paso4`: selección SEL-PASO4-REPRO-v1 con el Verificador
     S6, plan por grupos CA2 y `unidades.EjecutorSeleccion` (comparte
     techos entre las unidades del proceso);
   - R3 con `ProductorR3`.
3. Validación productiva: `registro_productivo.generar` (`verificar_paquete`
   del Verificador) en R2, y `generar_r3` con `ValidadorR3S6` en R3.
4. Productos por unidad: documento nativo, filas y, en R2, documento
   comparable con su relación.

Escribe:
- `ejecucion.json`: estados por unidad (cálculo, estado del generador,
  validación), tiempos separados (contexto, cálculo, validación, total,
  CPU), técnica, huellas pública e histórica del contrato, entorno, F2 y
  dependencias;
- `entorno.json`: el documento de entorno de la huella real;
- `archivos_leidos.json`: rastro de aperturas;
- el registro y el dictamen de validación.

Termina con 0 solo si todas las unidades quedan calculadas **y** validadas
y el dictamen del validador cumple (`exito_global`). Con la validación
ausente o pendiente, nunca.

**`fam01-comparar`** compara una unidad de esa salida con su original.

Autentica el registro productivo con las mismas comprobaciones que el
comparador v3-S6:
- validador fijado por selección;
- generador `registro_productivo.py` instalado;
- dictamen íntegro y coherente.

En lugar del inventario `audit/entrega.json` de la ruta administrativa, el
registro se liga al sha256 declarado en `ejecucion.json`. No es un sello.

Comprueba también que el comparable deriva exactamente del nativo y la
correspondencia del saneamiento. Hace cuatro pasadas del comparador v3-S6:

| Pasada | Reglas |
|---|---|
| `historico_vigentes` | vigentes; DR-1 tal cual |
| `historico_vigentes_y_selladas` | vigentes y selladas del plan; DR-1 tal cual (da `comparacion_historica`) |
| `limpia` | además, E2E3-NIVEL-R1-v1, HIST-OPERATIVO-v1 y SAN-RUTAS-v1; entorno estricto |
| `limpia_f2` | la limpia con F2 (F2-ENTORNO-PORTABLE-v1, adoptada para FAM01) |

Separa los estados:
- `calculo`;
- `validacion_productiva`: verificada, pendiente o inválida;
- `comparacion_historica`, `comparacion_limpia` y `comparacion_limpia_f2`;
- `reproduccion`: aceptada (histórica), aceptada_comparacion_limpia,
  aceptada_comparacion_limpia_con_F2, pendiente_validacion o no_aceptada.

También informa los valores comparados, el nivel R1 esperado y el
declarado, la procedencia operativa, el registro de la adopción de F2 y el
rastro de lecturas.

Códigos de salida:
- 0 si la reproducción queda aceptada con la comparación histórica, con la
  limpia o con la limpia con F2 (el estado dice con cuál);
- 1 en otro caso.

Hasta la adopción de F2, la aceptación solo bajo F2 terminaba con 2.

Rechaza por código cualquier aceptación sin validación verificada.

**`fam01-receta`** escribe la receta sin ejecutarla.
- Recorrido: 1.767 unidades (1.762 numéricas y 5 NA), R2 y después R3, por
  identificador estable; cada numérica lleva su `fam01-unidad` y su
  `fam01-comparar`, y cada NA su `fam01-na`.
- Variante agrupada: 130 tareas de hasta 20 unidades del mismo grupo
  (preregistro, país, diseño, menú en R2; conjunto, país, diseño, menú en
  R3), para compartir techos con el mismo ejecutor y sus claves. Está
  preparada y no probada a escala: los pilotos solo ejecutaron tareas de una
  unidad.
- La receta lista también sus condiciones y lo que falta.

## Formato del documento R2 (FMT-R2-v1, en el adaptador)

El documento nativo de `registro_productivo.ensamblar` se conserva en
`unidades/`. El documento comparable se escribe en `comparables/`, y su
relación (nativo, comparable y filas, con sus sha256) en
`comparables/relacion.json`.

| Campo del comparable | Origen |
|---|---|
| familia, ruta (si existe), estrato; `clave_estructural_lima1913` (6 unidades del productor piloto) | entrada del manifiesto de bloque de la unidad (`clasificacion_manifiesto.json`), como hacían los trabajadores históricos |
| estado_generador | `resultado.estado` del cálculo nuevo |
| estado_final | `FINAL_C[resultado.estado]` de los trabajadores históricos: «completo» = generador terminado con estado ok. No significa validado: la validación es el registro productivo |
| resultado.etiqueta | `id[:16]`, rótulo que el trabajador histórico pasaba a `Generador.celda` (el rótulo S6 queda en el nativo) |
| filas | {archivo, sha256, tablas} de las mismas filas (mismos bytes) |
| ensamblado | solo en el nativo |

No cambia ningún valor, estado de celda ni fila, ni se excluye ninguna clave
por nombre. Se comprobó documentalmente sobre los 1.740 originales:
- etiqueta = id[:16] en todos;
- familia, ruta y estrato iguales a su entrada;
- estado «completo».

En los pilotos el grupo «formato del documento» queda vacío. En R3 el
documento ya coincidía y no hay comparable aparte.

## Entorno: cumplimiento y F2

`.venv-fam01` se creó con `crear_entorno.ps1`:
- receta del perfil, copiada en `nucleo_s6/raiz/environment/sucesor_b3`;
- perfil `integracion`;
- intérprete base CPython 3.12.4 oficial (python.exe fd5c46d7…,
  python312.dll 21700f0b…);
- caché de ruedas local;
- sin tocar el Python global ni ningún entorno histórico.

`entorno.assessment` con el perfil aprobado (manifiesto a44e3c8e…, lock
942a4138…) da `conforms = true` y `mismatches = []`. Se cumple:
- CPython 3.12.4, AMD64, plataforma Windows-11-build-26200;
- pip 26.1.2;
- OpenBLAS 0.3.27 ILP64;
- las seis variables de hilos = 1, locale C, TZ UTC, semilla 0;
- los 10 paquetes del lock con su versión y el sha256 de su rueda, y ningún
  paquete adicional.

`requisitos_fam01.txt` remite a ese lock completo.

Comprobado con el código existente:

| Entorno | conforms | environment_sha256 | F2 |
|---|---|---|---|
| venv histórico de la tupla admitida (en su ruta) | sí | 41b467a1… (admitida) | referencia |
| `.venv-fam01` | sí, 0 discrepancias | 4cc5b9a8… | equivalente |
| venv del traslado de la segunda entrega (otra carpeta) | sí, 0 discrepancias | a7351b2c… | equivalente |
| `.venv` anterior | no: pip 24.0, faltan pandas, python-dateutil, pytz, six y tzdata | c148ab2f… | no equivalente |

**F2-ENTORNO-PORTABLE-v1.** Se propuso como
F2-CANDIDATA-ENTORNO-PORTABLE-v1 y el autor la adoptó para FAM01 el
2026-11-16 sin cambios de contenido. No sustituye DR-1. Un entorno E′
equivale al entorno E de la tupla S6 admitida si:

1. **Perfil.** `entorno.assessment` de E′ con el perfil aprobado da
   `conforms = true` y `mismatches = []`.
2. **Huellas de software.** El documento de entorno de E′ es idéntico al de
   E salvo los campos de ubicación. Entre otras cosas, se conservan:
   - el sha256 del lanzador del venv (41123879…), del python.exe base y de
     python312.dll;
   - la versión y el sha256 de rueda de cada paquete;
   - BLAS y LAPACK, hilos, locale, zona horaria y semilla.
3. **Campos de ubicación**, los únicos que se excluyen:
   - `fingerprint.executable.path` y `base_path`;
   - en el RECORD de cada paquete, las líneas de los lanzadores
     `Scripts/*.exe`, que contienen la ruta absoluta del intérprete; el
     `record_sha256` se sustituye por el sha256 del RECORD sin esas líneas;
   - `fingerprint_sha256`, que deriva de los anteriores.
4. **Comprobación.**
   - El documento de E′ debe ser el de la huella real de la ejecución:
     sha256(canon + salto) = `environment_sha256` de sus filas.
   - Su proyección (el documento sin los campos de 3) debe ser igual a la de
     E.
   - La de E está en `datos/fam01/entorno_f2_referencia.json` (b6db2964…).
     Se regeneró ejecutando `entorno.assessment` con el venv histórico que
     dio 41b467a1, y se comprobó contra la tupla admitida.
5. **Lo que no cambia.**
   - Cada ejecución conserva su huella real y sus claves derivadas; nunca se
     copia 41b467a1.
   - DR-1 sigue exigiendo todo lo demás: la técnica nueva es la tupla S6
     admitida salvo `environment_sha256`, con tolerancias idénticas
     (0fc40e7d…), cargas y claves recalculadas y definiciones E1–E3.
   - No se amplía ninguna tolerancia.

   Aplicación: si DR-1 falla solo por «técnica nueva no admitida»
   o por «environment/tolerances distintos», y se cumplen 1–4, esos dos
   motivos quedan cubiertos.

Implementación: `equivalencia_f2`, `_rd1_limpia` y `ADOPCION_F2` en
`src/fam01.py`. F2 se usa solo en la pasada `limpia_f2`.

Límite: la proyección conserva `blas.max_threads` (24, leído de la
configuración de compilación de OpenBLAS) y la compilación de Windows del
perfil. Ese valor no mide los núcleos físicos disponibles. Una diferencia en
los campos conservados rechaza la equivalencia. Solo se probó en esta máquina,
con dos ubicaciones de venv; no se acredita portabilidad a cualquier sistema.

## Validación productiva (pilotos)

- **R2:** Verificador S6 instalado (`paquete_seleccion.py`) sobre los bytes
  finales del paquete; dictamen «completo», `cumple = true`, sin códigos.
  Adaptaciones declaradas (`ADAPTACIONES_VERIFICADOR`):
  - construcción sin `puerta_autoridad` ni `puerta_dependencias`, porque no
    hay autoridad viva ni nombres de despliegue;
  - `validar_lista_reproduccion` contra la lista R2 fijada y las
    definiciones extraídas, en vez de las entregas históricas;
  - `verificar_identidad` con el productor de esta corrida y la misma
    fórmula del run_id.

  El resto es el código instalado sin cambios: selección, plan, E12, techo,
  λ_π, K1, C2, G, inversiones, geometría, evidencia, Checker, R1/R2 y
  resumen canónico.
- **R3:** `ValidadorR3S6`, construido antes del cálculo como en
  `tarea_paso4`, y `generar_r3`. Dictamen `cumple = true`.
- La validación no requirió cálculo científico adicional.

## Historial breve de entregas anteriores

Las salidas anteriores se conservan como antecedente.

**Primera entrega (mañana).** Salidas `_01`, `comparar_R2_02` y
`comparar_R3_01`:
- R2 con el `.venv` incompleto: 143,5 s;
- R3: 140,9 s;
- NA piloto: 9/9.

El rechazo se atribuía al entorno de DR-1 y al formato del documento R2.

Valores (iguales en binary64 en las tres entregas):

| | C_2 | error | G | K_comp_1 | veredicto |
|---|---|---|---|---|---|
| R2 | 0.7916532465350333 | 1.0687565277223145e-09 | 0.5760531893748697 | 0.21560005716016362 | factible |
| R3 | 0.2333333327770233 | 2.3368936952206102e-08 | -0.7614596828306021 | 0.9947930156076253 | infactible |

**Segunda entrega.** Avances:
- referencias de las 1.767 unidades;
- formato R2 resuelto;
- validación productiva conectada;
- `.venv-fam01` conforme y propuesta F2.

Pilotos `_02`:
- cálculo 142,5 s (R2) y 117,3 s (R3);
- documentos 48680a51… y bcd8f3dc…;
- run_id BRUN-7f507d12…, con el contrato histórico.

Comparaciones `comparar_R2_06.json` y `comparar_R3_04.json`:
- histórica: `correspondencia_incorrecta`;
- candidata F2: una diferencia por unidad, el texto R1 con k = 7 fuera de
  0..6;
- diagnóstico no vinculante F2 + «E2 ampliada a 6 ≤ k ≤ 10»: aceptada.

Esta entrega sustituye la E2 ampliada por la regla del k exacto. Las
pruebas `pruebas_dirigidas_01.json` comprobaron alteraciones de valores,
registros y entorno. El traslado se hizo con un venv nuevo (a7351b2c…), y la
regresión de FAM12 dio `_03` y `_04`.

Para las rutas privadas se ofrecían tres opciones: distribuir los archivos,
sanear con una regla nueva o excluirlos. La revisión de Codex lo resolvió
como saneamiento, aplicado en esta entrega. La extrapolación de tiempo de
dos unidades que se dio entonces no es una estimación del lote (revisión de
Codex).

## Revisión de Codex — 2026-11-16

Revisión de las salidas guardadas y del código pertinente, sin recalcular el
modelo ni modificar reglas científicas:

- Las 327 huellas de `fuentes_fam01.json` coinciden; las 325 copias también
  coinciden con los archivos originales. Las otras dos piezas son derivadas.
- Las 21 comprobaciones de listas pasan. Se recalcularon además las 536
  identidades B y se comprobaron las 1.767 definiciones sin duplicados.
  F01-R3-MARCO queda cerrado como comprobación documental de marco y muestra.
- Los archivos de ambos pilotos coinciden con las huellas registradas. Las
  19 tablas de cada uno conservan sus cardinalidades. Todos sus valores
  numéricos coinciden exactamente: 14.867 en R2 y 66 en R3; los float se
  compararon por representación hexadecimal. Los veredictos también coinciden.
  Esto no equivale a identidad de todos los campos ni a validación productiva.
- La comprobación NA guardada es conforme (9/9). En R3 quedan 21 unidades
  numéricas y 4 NA sin ejecutar; la muestra tiene 22 numéricas en total.

Precisiones para continuar:

1. El hash de entorno incorpora la ruta, por lo que la igualdad literal impide
   trasladarlo. Pero los pilotos también difieren del perfil aprobado en
   paquetes y pip; R2, además, en tres variables de hilos. Ignorar la ruta por
   sí solo no resuelve esas diferencias. Preparar el entorno portable y una
   propuesta concreta de equivalencia para F2, conservando la huella real de
   cada ejecución; no sustituirla por la histórica ni ampliar tolerancias.
2. Las diferencias de documento R2 proceden del ensamblado y de la etiqueta
   suministrada por el adaptador. Primero resolver la compatibilidad de salida
   con los datos de selección y del resultado nuevo: no hace falta trasladar
   al autor cada clave o etiqueta. Conservar los bytes originales. Si alguna
   correspondencia afecta al significado científico o a una regla adoptada,
   presentar solo esa diferencia concreta para decisión.
3. Incorporar las comprobaciones científicas del validador y las referencias
   restantes. Son trabajos de implementación pendientes, no decisiones del autor.
4. Antes del paquete público, resolver las rutas personales incluidas en datos
   copiados. Una proyección pública debe conservar valores y relaciones y
   declarar sus nuevas huellas; no se editarán las fuentes históricas.

FAM01 sigue parcial. El entorno todavía no se declara equivalente, el comparador
histórico mantiene su rechazo y no se ha ejecutado el lote completo. La revisión
puntual queda en `local/revisar_fam01_20261116.py`, fuera del paquete público.

## Revisión de la segunda entrega — Codex, 2026-11-16

Se cotejaron archivos y código, sin ejecutar de nuevo el modelo:

- 3.866 huellas locales conformes y 3.861 fuentes cotejadas; las cuatro
  proyecciones saneadas declaran su huella de origen por separado.
- Las 1.767 unidades tienen sus 3.534 archivos de referencia, con huellas,
  identificador de unidad e identidad E12 coincidentes con el índice.
- Ambos pilotos conservan todos los valores numéricos de sus 19 tablas
  (14.867 valores en R2 y 66 en R3, con igualdad hexadecimal para float).
  Los registros ligados a sus salidas dan completa_validada. Las cinco NA
  tienen comprobaciones documentales conformes.
- Los documentos de entorno cumplen el perfil y sus proyecciones coinciden
  con la referencia F2 candidata. Esto no adopta F2 ni prueba otro sistema.
- La función r1_level es idéntica por AST en el núcleo histórico lima1738 y
  el actual. La geometría histórica ya la utilizaba. Con la configuración
  fijada, su intervalo es 6..10: el límite 0..6 del texto E2/E3 no describe
  correctamente esa implementación. Es una corrección del comparador, no un
  aumento nuevo de profundidad. Su implementación debe comprobar el k que
  corresponde a las entradas, preservar el resto del texto y no alterar las
  cotas, estados o garantías. La regla histórica no se ha editado.
- Se confirman 183 originales con tramo_anterior y 12 con recuperacion_de.
  Esas dos rutas documentan intentos históricos. Procede conservarlas como
  procedencia y separarlas de la comparación científica, de forma explícita;
  no ocultar cambios en estados o resultados de la corrida actual.

Continuación recomendada: terminar en el adaptador las correcciones E2/E3 y
el tratamiento de esos dos campos históricos, y sanear los nueve archivos
que aún contienen rutas privadas, con huellas nuevas y correspondencia
científica comprobada. El saneamiento ya forma parte del encargo de paquete
público; no requiere optar por publicar rutas personales ni por excluir los
datos necesarios. No reconstruir infraestructura de autoridad histórica.

F2 sigue siendo la decisión explícita de entorno pendiente. Recomiendo su
equivalencia de ubicación dentro del perfil comprobado, con el alcance
Windows/CPython y las demás propiedades que conserva la propuesta, sin
extenderla automáticamente a otras plataformas. La autorización del lote
pertenece al Paso 3 y no impide terminar esta preparación.

La cifra de 70 h es una extrapolación hipotética de dos unidades; no se toma
como estimación ni como presupuesto del lote. El coste se concretará con
antecedentes y mediciones pertinentes, considerando la reutilización por
soporte. No se lanza ahora el lote ni se cambia la selección.

Estado: referencias, formato R2 y validación de los pilotos revisados; marco
R3 conservado cerrado; FAM01 parcial por comparación y preparación pública.
FAM12 sigue comprobada y las otras 12 familias siguen pendientes. Cotejo
puntual en local/revisar_fam01_ampliacion.py; no es una pieza pública.

## Revisión final de preparación — Codex, 2026-11-16

Acepto la preparación técnica en el alcance comprobado, condicionada a la
decisión de entorno F2. No adopto F2 en nombre del autor ni declaro ejecutado
el lote completo.

Se cotejaron las 3.869 huellas locales y las 3.861 fuentes correspondientes,
además de los 3.534 archivos de referencia de las 1.767 unidades. En las
salidas nuevas `_03`, los 14.867 valores numéricos de R2 y los 66 de R3
coinciden exactamente con los originales (hexadecimal para float). Sus
registros de validación están ligados a los archivos y dan completa_validada.
Las cinco NA conservan sus nueve comprobaciones conformes.

La lectura del comparador confirma que E2/E3 exige el nivel que calcula el
núcleo para la unidad y conserva la distinción certificado/incompleto. Los
dos campos históricos se separan solo en el primer nivel; los estados y el
contenido de resultado siguen comparándose. La prueba E3 es de función,
no un nuevo piloto productivo incompleto.

Se reconstruyeron desde las fuentes las trece copias saneadas: sus bytes
coinciden exactamente al sustituir únicamente los prefijos de ruta declarados.
Se cotejaron también los tres manifiestos públicos contra los históricos y
sus archivos, y se revisó la adaptación del pin en el lector nacional. Estas
correspondencias pertenecen al saneamiento; no amplían la decisión F2.

Se ejecutó de nuevo fam01-comparar sobre ambos pilotos guardados, sin modelo
ni validación científica nueva: ambos devolvieron código 2 y
aceptada_bajo_criterio_candidato_F2. La comparación histórica y la limpia
con entorno estricto conservan su rechazo. No se aplicó tolerancia numérica.

Recomiendo adoptar F2 para FAM01 con el perfil exacto documentado: permitir
solo las diferencias de ubicación del venv y los registros derivados de sus
lanzadores, conservando versiones, binarios, dependencias, plataforma, BLAS,
hilos, locale, zona horaria y semilla. El alcance probado es Windows con
CPython 3.12.4, dos ubicaciones y una máquina; no acredita otra plataforma ni
una instalación aislada. La adopción no autoriza el lote del Paso 3.

No encuentro otro bloqueo técnico en este alcance de preparación. La prueba
aislada del paquete completo sigue en 2.4.2. Estado del tablero: FAM12
comprobada en alcance; FAM01 revisada técnicamente bajo criterio candidato,
pendiente de F2; otras doce familias pendientes. La siguiente incorporación
es FAM02. El cotejo puntual y las dos comparaciones quedan en local/, fuera
del paquete público. No se modificaron cálculos, referencias ni reglas durante
esta revisión.

## Adopción de F2 y cierre de preparación — 2026-11-16

El autor comunicó en este chat la siguiente adopción literal:

> Adopto F2 para FAM01 conforme a la propuesta revisada en RESULTADO_FAM01.md, sin modificar criterios científicos ni autorizar todavía el lote completo.

La decisión cubre la equivalencia de ubicación del entorno para FAM01 con
el perfil revisado, incluidos los registros derivados de los lanzadores.
Se conservan las demás condiciones descritas en la revisión final. No se
extiende automáticamente a otras familias, máquinas o plataformas.

Codex da por cerrada la preparación técnica de FAM01 en ese alcance. Los
pilotos R2/R3 ya revisados quedan aceptados bajo F2 adoptada; sus archivos
conservan la etiqueta candidata y el código 2 registrados antes de esta
decisión. No se reescribieron esos resultados ni se ejecutó cálculo nuevo.

La instalación aislada corresponde al Paso 2.4 y los lotes completos al
Paso 3, todavía sin autorizar. F2 no adopta F3/F4 ni cierra el Paso 2 global.
La siguiente familia prevista es FAM02.

## Revisión de la implementación de F2 adoptada — Codex, 2026-11-16

Cambio conforme. Se revisaron la comprobación de equivalencia, la selección
del estado aceptado, el código de salida y las condiciones de la receta.
Se cotejaron completas comparar_R2_09/comparar_R3_07 frente a sus anteriores:
salvo las claves y etiquetas de adopción, el registro de la decisión y la
duración, no hay diferencias. Los valores, la validación y el rechazo
histórico se conservan.

Se ejecutó de nuevo únicamente fam01-comparar: los dos pilotos `_03` dan
aceptada_comparacion_limpia_con_F2 con código 0; la salida R2 `_01` del
entorno antiguo sigue no_aceptada con código 1. Se revisaron también los
resultados guardados de los controles de entorno, validación ausente y
cambio de C_2. No se recalculó el modelo ni se ejecutó el lote.

El cierre de preparación de FAM01 se mantiene. La etiqueta candidata y el
código 2 describen las salidas anteriores a la adopción, que siguen intactas;
las nuevas comparaciones ya reflejan F2 adoptada. No se requiere otra
corrección para continuar con FAM02. Instalación aislada y lotes completos
permanecen en 2.4.2 y Paso 3, respectivamente.
