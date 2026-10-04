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