# panel-proveedores-salud
Análisis de entregas, precios y compras de productos de salud con Python.

# Ver el panel en línea

[Abrir el panel de proveedores de salud](https://panel-proveedores-salud-fernandatrevi.streamlit.app/)

Explora la puntualidad de las entregas con filtros por proveedor, país y año, y descarga los resultados en CSV. Puedes utilizarlo desde el navegador sin instalar Python.

El análisis utiliza datos históricos de 2006–2015.
# Preparación de datos

Los datos son históricos y contienen fechas de entrega de 2006 a 2015.
El análisis describe ese periodo y no representa el desempeño actual
de los proveedores.

# Revisión de calidad

- 10,324 líneas de productos y 33 columnas.
- Ninguna fila completamente duplicada.
- 7,030 referencias de envío distintas.
- 7,020 referencias evaluables para puntualidad.
- 10 referencias con fechas programadas contradictorias, conservadas
  sin calificación de puntualidad.

# Reglas del análisis

Se conserva el CSV original en `data/raw`.

La tabla `data/processed/envios.csv` contiene una fila por referencia
`asn/dn #`. El proveedor, país y fechas se asignan únicamente cuando
todos los registros de esa referencia coinciden y no tienen faltantes.

Una entrega se considera puntual si ocurre en la fecha programada
o antes. La diferencia en días es la fecha real menos la programada:
un valor positivo indica retraso.

Los datos faltantes no se sustituyen por cero. Los retrasos observados
no demuestran por sí solos responsabilidad del proveedor.

# Cómo reproducir la preparación

Entorno utilizado: Python 3.14.2.

Desde la terminal, en la raíz del proyecto, ejecutar en este orden:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python src/revisar_datos.py
    python src/preparar_datos.py

Los scripts generan los archivos derivados en `data/processed`.
Si se utilizan otros datos, deben revisarse nuevamente los conteos,
las fechas y la consistencia de las referencias.

# Indicadores de entrega

Los indicadores se calculan por referencia de envío y por el nombre
de proveedor registrado en la base.

| Indicador | Definición |
| --- | --- |
| Envíos evaluables | Referencias con proveedor, país y fechas completos y consistentes. |
| Envíos puntuales | Entregas realizadas en la fecha programada o antes. |
| Envíos tardíos | Entregas realizadas después de la fecha programada. |
| Puntualidad (%) | Envíos puntuales / envíos evaluables × 100. |
| Retraso promedio general | Promedio de días de retraso entre todos los envíos evaluables; las entregas puntuales aportan cero. |
| Retraso promedio de tardíos | Promedio de días de retraso únicamente entre las entregas tardías. Queda vacío si no hubo entregas tardías. |

# Resultados generales

- Envíos evaluables: 7,020.
- Envíos puntuales: 6,222.
- Envíos tardíos: 798.
- Puntualidad global: 88.63%.
- Referencias pendientes de revisión: 10, excluidas del cálculo de puntualidad.

La puntualidad global se calcula sobre todos los envíos evaluables;
no es el promedio simple de los porcentajes de los proveedores.

# Interpretación y limitaciones

Los resultados permiten identificar entregas que requieren seguimiento
y describir la frecuencia y magnitud de los retrasos históricos.

La comparación entre proveedores debe considerar el número de envíos,
el periodo, el país, los productos y las condiciones logísticas.
Los nombres de proveedor todavía no se han normalizado.

Un retraso observado no demuestra responsabilidad del proveedor.
Estos indicadores tampoco miden entregas completas, calidad del producto
ni ahorros económicos.

# Reproducir los indicadores

Después de preparar los datos, ejecutar:

    python src/calcular_indicadores.py

El resultado se guarda en:

    data/processed/indicadores_proveedores.csv
# Panel interactivo

El panel permite explorar la puntualidad de las entregas por proveedor, país de destino y año de entrega. Los indicadores se recalculan según los filtros seleccionados.

Incluye:
- Total de envíos seleccionados y evaluables.
- Número de envíos tardíos y porcentaje de puntualidad.
- Registros pendientes de revisión.
- Gráfico y tabla de indicadores por proveedor.
- Descarga de los resultados filtrados en CSV.

# Cómo ejecutarlo

Desde la raíz del repositorio, con el entorno virtual `.venv` creado:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/preparar_datos.py
.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

En Codespaces, abrir el puerto 8501 desde la pestaña Ports.
Dejar el proceso activo mientras se utiliza el panel.

# Interpretación

Una selección vacía incluye todos los valores. El filtro de año utiliza la fecha real de entrega.

La puntualidad se calcula únicamente sobre los envíos evaluables. Los registros con fechas programadas conflictivas quedan pendientes de revisión.

Los datos corresponden al periodo histórico 2006–2015. Las diferencias de puntualidad ayudan a identificar casos para investigar, pero no demuestran por sí solas responsabilidad del proveedor ni ahorros económicos.

# Resultados del análisis

La base contiene 10,324 líneas de productos, agrupadas en 7,030 referencias de envío. Cada referencia se cuenta una sola vez para evitar que los envíos con varios productos tengan más peso en los indicadores.

| Indicador | Resultado |
|---|---:|
| Referencias de envío | 7,030 |
| Envíos evaluables para puntualidad | 7,020 |
| Envíos puntuales | 6,222 |
| Envíos tardíos | 798 |
| Puntualidad global | 88.63% |
| Referencias con fechas programadas conflictivas | 10 |

Un envío se considera puntual cuando llega en la fecha programada o antes. Las diez referencias con fechas programadas conflictivas se excluyen del cálculo hasta que puedan revisarse.

## Interpretación y utilidad

El 11.37% de los envíos evaluables llegó después de la fecha programada. El panel permite identificar en qué proveedores, destinos y años se concentran esos retrasos para priorizar su investigación.

El área de compras y logística puede utilizarlo para preparar revisiones de servicio, dar seguimiento a compromisos de entrega y detectar dónde conviene investigar alternativas de abastecimiento.

Estos resultados describen entregas históricas de 2006–2015. No representan el desempeño actual de los proveedores ni demuestran que un retraso sea responsabilidad exclusiva de ellos. También pueden intervenir el transporte, las aduanas y la recepción en destino.

La categoría SCMS from RDC corresponde a distribución desde centros regionales y debe analizarse teniendo en cuenta esa función.

# Beneficios que podrían evaluarse en un hospital

Con datos propios y seguimiento de las acciones tomadas, este análisis podría apoyar la reducción de compras urgentes, interrupciones del suministro y tiempo dedicado a elaborar reportes.

Para demostrar un ahorro económico se deben medir los costos antes y después de una intervención, considerando los cambios en volumen y tipo de productos. Este proyecto no calcula ahorros ni mide efectos sobre la atención clínica o la reputación del hospital.

# Cómo adaptar el análisis a otro hospital

La metodología puede replicarse con registros propios de compras y recepción. Los resultados de esta base no deben trasladarse directamente a otro hospital.

# Datos mínimos necesarios

| Dato | Para qué se utiliza |
|---|---|
| Identificador de envío o entrega | Contar cada entrega una sola vez |
| Identificador y nombre del proveedor | Agrupar entregas del mismo proveedor |
| Destino o sede receptora | Comparar resultados por ubicación |
| Fecha de entrega comprometida | Establecer el plazo acordado |
| Fecha real de recepción | Determinar si la entrega llegó a tiempo |

Debe definirse qué representa cada registro: una orden de compra puede tener varias entregas parciales. El identificador elegido debe distinguir esas entregas.

# Pasos de adaptación

1. Exportar los registros del sistema de compras o recepción a CSV.
2. Conservar una copia de los datos originales.
3. Unificar los identificadores de proveedores y revisar fechas faltantes, duplicados y entregas parciales.
4. Adaptar `src/preparar_datos.py` a los nombres y formatos de las columnas del hospital. El script actual espera la estructura del archivo original.
5. Generar una tabla compatible con `data/processed/envios.csv`, con las columnas `referencia_envio`, `proveedor`, `pais`, `fecha_programada`, `fecha_entrega`, `numero_lineas`, `evaluable`, `diferencia_dias` y `puntual`.
6. Si se utilizan sedes en lugar de países, adaptar también el campo `pais` y el filtro de destino en `app.py`.
7. Comprobar manualmente una muestra de entregas y comparar los totales con el sistema de origen antes de utilizar el panel.

La fecha comprometida debe conservarse con su historial de modificaciones. Cambiarla después de una entrega tardía puede ocultar incumplimientos.

Para uso interno, incluir únicamente datos necesarios de compras y logística. Los datos del hospital deben almacenarse en un entorno autorizado; no se necesitan datos de pacientes para este análisis.

# Datos adicionales para mejorar el análisis

| Datos adicionales | Mejora que permiten |
|---|---|
| Cantidad solicitada y recibida por producto | Medir entregas completas y calcular OTIF: a tiempo y completas |
| Fecha de emisión de la orden | Calcular el tiempo desde la compra hasta la recepción |
| Producto, presentación y unidad de medida | Comparar precios de productos equivalentes |
| Precio, moneda y costos logísticos | Analizar costos comparables de abastecimiento |
| Motivo del retraso y responsable registrado | Investigar causas y definir acciones |
| Inventario, consumo y días sin existencias | Evaluar la relación entre retrasos y disponibilidad |
| Compras urgentes y sus sobrecostos | Medir el impacto económico de problemas de suministro |
| Rechazos, daños y devoluciones | Complementar la puntualidad con calidad de entrega |

Actualmente, el panel mide puntualidad. Para incorporar estos indicadores adicionales se requieren nuevos datos y cambios en los scripts.

# Validación manual del panel

Se comprobaron los siguientes casos:

- Resultados generales: 7,020 envíos evaluables, 798 tardíos y 88.63% de puntualidad.
- Filtro SCMS from RDC: 3,440 envíos evaluables, 556 tardíos y 83.84% de puntualidad.
- SCMS from RDC en 2014: 421 envíos evaluables, 153 tardíos y 63.66% de puntualidad.
- Belize: un envío evaluable, puntual y entregado 14 días antes de la fecha programada.
- Descargas de envíos e indicadores para Belize: contenido consistente con el panel.
- Belize en 2014: mensaje de ausencia de envíos para esa combinación de filtros.

Estas comprobaciones cubren los casos indicados; no constituyen una validación exhaustiva de todas las combinaciones.