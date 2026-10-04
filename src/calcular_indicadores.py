from pathlib import Path
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
carpeta = raiz / "data/processed"

envios = pd.read_csv(
    carpeta / "envios.csv",
    dtype={"evaluable": "boolean", "puntual": "boolean"},
)

# Los registros pendientes quedan fuera del cálculo de puntualidad.
evaluables = envios.loc[envios["evaluable"].fillna(False)].copy()
evaluables["retraso_dias"] = evaluables["diferencia_dias"].clip(lower=0)

indicadores = evaluables.groupby("proveedor").agg(
    envios_evaluables=("referencia_envio", "size"),
    envios_puntuales=("puntual", "sum"),
    retraso_promedio_dias=("retraso_dias", "mean"),
)

indicadores["envios_tardios"] = (
    indicadores["envios_evaluables"] - indicadores["envios_puntuales"]
)

indicadores["puntualidad_pct"] = (
    100 * indicadores["envios_puntuales"]
    / indicadores["envios_evaluables"]
)

# Promedio solo entre entregas tardías; queda vacío si no hubo retrasos.
tardios = evaluables.loc[evaluables["retraso_dias"] > 0]
indicadores["retraso_promedio_tardios_dias"] = (
    tardios.groupby("proveedor")["retraso_dias"].mean()
)

indicadores = indicadores.reset_index()
indicadores.to_csv(carpeta / "indicadores_proveedores.csv", index=False)

print(f"Envíos evaluables: {len(evaluables):,}")
print(f"Puntualidad global: {evaluables['puntual'].mean() * 100:.2f}%")
print(f"Envíos tardíos: {len(tardios):,}")
print("\nDiez proveedores con más envíos evaluables:")
print(
    indicadores.sort_values("envios_evaluables", ascending=False)
    .head(10).round(2).to_string(index=False)
)
