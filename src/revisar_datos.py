from pathlib import Path
import pandas as pd

# Localizar el CSV desde la carpeta del proyecto.
raiz = Path(__file__).resolve().parents[1]
archivo = raiz / "data/raw/Supply_Chain_Shipment_Pricing_Data.csv"

# Leer los datos originales sin modificarlos.
datos = pd.read_csv(archivo)

print(f"Filas: {datos.shape[0]:,}")
print(f"Columnas: {datos.shape[1]}")
print(f"Filas completamente duplicadas: {datos.duplicated().sum()}")

print("\nNombres de las columnas:")
for columna in datos.columns:
    print(f"- {columna}")

print("\nValores faltantes por columna:")
faltantes = datos.isna().sum()
print(faltantes[faltantes > 0].to_string())

print("\nPrimeras tres filas:")
print(datos.head(3).to_string(index=False))

print("\nValidación de fechas:")
for columna in ["scheduled delivery date", "delivered to client date"]:
    fechas = pd.to_datetime(
        datos[columna], format="%d-%b-%y", errors="coerce"
    )
    print(f"{columna}:")
    print(f"  Fechas faltantes o inválidas: {fechas.isna().sum()}")
    print(f"  Desde: {fechas.min()} | Hasta: {fechas.max()}")

print("\nReferencias de envío:")
print(f"Referencias distintas: {datos['asn/dn #'].nunique()}")
print(f"Filas sin referencia: {datos['asn/dn #'].isna().sum()}")
print(
    "Filas adicionales con referencia repetida:",
    datos["asn/dn #"].duplicated().sum()
)

print("\nConsistencia dentro de cada referencia de envío:")
columnas = [
    "vendor",
    "country",
    "scheduled delivery date",
    "delivered to client date",
]

revision = datos.groupby("asn/dn #")[columnas].nunique(dropna=False)

for columna in columnas:
    conflictos = (revision[columna] > 1).sum()
    print(f"Referencias con varios valores en {columna}: {conflictos}")

# Guardar los registros con fechas programadas diferentes.
referencias_conflictivas = revision.index[
    revision["scheduled delivery date"] > 1
]

conflictos = datos[
    datos["asn/dn #"].isin(referencias_conflictivas)
].copy()

salida = raiz / "data/processed"
salida.mkdir(parents=True, exist_ok=True)

conflictos.to_csv(
    salida / "fechas_programadas_conflictivas.csv",
    index=False
)

print("\nDetalle de fechas programadas conflictivas:")
detalle = conflictos[
    [
        "asn/dn #",
        "scheduled delivery date",
        "delivered to client date",
    ]
].drop_duplicates()

print(detalle.sort_values("asn/dn #").to_string(index=False))
