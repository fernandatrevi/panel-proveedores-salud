from pathlib import Path
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
entrada = raiz / "data/raw/Supply_Chain_Shipment_Pricing_Data.csv"
salida = raiz / "data/processed"
salida.mkdir(parents=True, exist_ok=True)

datos = pd.read_csv(entrada)

if datos["asn/dn #"].isna().any():
    raise ValueError("Hay filas sin referencia de envío; revisar antes de agrupar.")

# Convertir fechas sin modificar el archivo original.
for columna in ["scheduled delivery date", "delivered to client date"]:
    datos[columna] = pd.to_datetime(
        datos[columna], format="%d-%b-%y", errors="coerce"
    )

# Usar un valor solo cuando todas las filas del envío coinciden.
def valor_unico(serie):
    if serie.isna().any() or serie.nunique() != 1:
        return pd.NA
    return serie.iloc[0]

envios = datos.groupby("asn/dn #", sort=True).agg(
    proveedor=("vendor", valor_unico),
    pais=("country", valor_unico),
    fecha_programada=("scheduled delivery date", valor_unico),
    fecha_entrega=("delivered to client date", valor_unico),
    numero_lineas=("id", "size"),
).reset_index().rename(columns={"asn/dn #": "referencia_envio"})

for columna in ["fecha_programada", "fecha_entrega"]:
    envios[columna] = pd.to_datetime(envios[columna], errors="coerce")

envios["evaluable"] = envios[
    ["proveedor", "pais", "fecha_programada", "fecha_entrega"]
].notna().all(axis=1)

# Diferencia positiva: entrega después de la fecha programada.
envios["diferencia_dias"] = (
    envios["fecha_entrega"] - envios["fecha_programada"]
).dt.days.astype("Int64")

envios["puntual"] = pd.Series(
    pd.NA, index=envios.index, dtype="boolean"
)
evaluables = envios["evaluable"]
envios.loc[evaluables, "puntual"] = (
    envios.loc[evaluables, "diferencia_dias"] <= 0
)

envios.to_csv(salida / "envios.csv", index=False)

print(f"Referencias totales: {len(envios):,}")
print(f"Evaluables para puntualidad: {evaluables.sum():,}")
print(f"Pendientes de revisión: {(~evaluables).sum():,}")
print("Archivo generado: data/processed/envios.csv")
