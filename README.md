# panel-proveedores-salud
Análisis de entregas, precios y compras de productos de salud con Python.
## Preparación de datos

Los datos son históricos y contienen fechas de entrega de 2006 a 2015.
El análisis describe ese periodo y no representa el desempeño actual
de los proveedores.

### Revisión de calidad

- 10,324 líneas de productos y 33 columnas.
- Ninguna fila completamente duplicada.
- 7,030 referencias de envío distintas.
- 7,020 referencias evaluables para puntualidad.
- 10 referencias con fechas programadas contradictorias, conservadas
  sin calificación de puntualidad.

### Reglas del análisis

Se conserva el CSV original en `data/raw`.

La tabla `data/processed/envios.csv` contiene una fila por referencia
`asn/dn #`. El proveedor, país y fechas se asignan únicamente cuando
todos los registros de esa referencia coinciden y no tienen faltantes.

Una entrega se considera puntual si ocurre en la fecha programada
o antes. La diferencia en días es la fecha real menos la programada:
un valor positivo indica retraso.

Los datos faltantes no se sustituyen por cero. Los retrasos observados
no demuestran por sí solos responsabilidad del proveedor.

### Cómo reproducir la preparación

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

## Indicadores de entrega

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

### Resultados generales

- Envíos evaluables: 7,020.
- Envíos puntuales: 6,222.
- Envíos tardíos: 798.
- Puntualidad global: 88.63%.
- Referencias pendientes de revisión: 10, excluidas del cálculo de puntualidad.

La puntualidad global se calcula sobre todos los envíos evaluables;
no es el promedio simple de los porcentajes de los proveedores.

### Interpretación y limitaciones

Los resultados permiten identificar entregas que requieren seguimiento
y describir la frecuencia y magnitud de los retrasos históricos.

La comparación entre proveedores debe considerar el número de envíos,
el periodo, el país, los productos y las condiciones logísticas.
Los nombres de proveedor todavía no se han normalizado.

Un retraso observado no demuestra responsabilidad del proveedor.
Estos indicadores tampoco miden entregas completas, calidad del producto
ni ahorros económicos.

### Reproducir los indicadores

Después de preparar los datos, ejecutar:

    python src/calcular_indicadores.py

El resultado se guarda en:

    data/processed/indicadores_proveedores.csv
## Panel interactivo

El panel permite explorar la puntualidad de las entregas por proveedor, país de destino y año de entrega. Los indicadores se recalculan según los filtros seleccionados.

Incluye:
- Total de envíos seleccionados y evaluables.
- Número de envíos tardíos y porcentaje de puntualidad.
- Registros pendientes de revisión.
- Gráfico y tabla de indicadores por proveedor.
- Descarga de los resultados filtrados en CSV.

### Cómo ejecutarlo

Desde la raíz del repositorio, con el entorno virtual `.venv` creado:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/preparar_datos.py
.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

En Codespaces, abrir el puerto 8501 desde la pestaña Ports.
Dejar el proceso activo mientras se utiliza el panel.

### Interpretación

Una selección vacía incluye todos los valores. El filtro de año utiliza la fecha real de entrega.

La puntualidad se calcula únicamente sobre los envíos evaluables. Los registros con fechas programadas conflictivas quedan pendientes de revisión.

Los datos corresponden al periodo histórico 2006–2015. Las diferencias de puntualidad ayudan a identificar casos para investigar, pero no demuestran por sí solas responsabilidad del proveedor ni ahorros económicos.