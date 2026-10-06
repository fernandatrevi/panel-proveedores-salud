from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Panel de proveedores de salud",
    page_icon="📦",
    layout="wide",
)

RAIZ = Path(__file__).resolve().parent
archivo = RAIZ / "data" / "processed" / "envios.csv"

st.title("📦 Panel de desempeño de proveedores")
st.caption(
    "Análisis histórico de entregas de productos de salud, 2006–2015."
)

if not archivo.exists():
    st.error("Falta data/processed/envios.csv. Ejecuta la preparación de datos.")
    st.stop()

envios = pd.read_csv(
    archivo,
    dtype={"evaluable": "boolean", "puntual": "boolean"},
)
envios["fecha_entrega"] = pd.to_datetime(
    envios["fecha_entrega"], errors="coerce"
)

st.sidebar.header("Filtros")
st.sidebar.caption("Deja una selección vacía para incluir todos.")

proveedores = st.sidebar.multiselect(
    "Proveedor",
    sorted(envios["proveedor"].dropna().unique()),
)
paises = st.sidebar.multiselect(
    "País de destino",
    sorted(envios["pais"].dropna().unique()),
)
anios = st.sidebar.multiselect(
    "Año de entrega",
    sorted(
        envios["fecha_entrega"].dt.year.dropna().astype(int).unique()
    ),
)

filtrados = envios.copy()

if proveedores:
    filtrados = filtrados[filtrados["proveedor"].isin(proveedores)]
if paises:
    filtrados = filtrados[filtrados["pais"].isin(paises)]
if anios:
    filtrados = filtrados[
        filtrados["fecha_entrega"].dt.year.isin(anios)
    ]

if filtrados.empty:
    st.info("No hay envíos para esta combinación de filtros.")
    st.stop()

evaluables = filtrados.loc[
    filtrados["evaluable"].fillna(False)
].copy()

total = len(filtrados)
cantidad_evaluable = len(evaluables)
pendientes = total - cantidad_evaluable
puntuales = int(evaluables["puntual"].sum())
tardios = cantidad_evaluable - puntuales

c1, c2, c3, c4 = st.columns(4)
c1.metric("Envíos seleccionados", f"{total:,}")
c2.metric("Envíos evaluables", f"{cantidad_evaluable:,}")
c3.metric("Envíos tardíos", f"{tardios:,}")
c4.metric(
    "Puntualidad",
    f"{100 * puntuales / cantidad_evaluable:.2f}%"
    if cantidad_evaluable else "Sin datos",
)

st.caption(
    f"Pendientes de revisión: {pendientes:,}. "
    "Se excluyen del cálculo de puntualidad."
)

with st.expander("Cómo interpretar los indicadores"):
    st.write(
        "Un envío es puntual si llega en la fecha programada o antes. "
        "La puntualidad es el porcentaje de envíos puntuales entre "
        "los envíos evaluables."
    )
    st.write(
        "Los envíos con fechas programadas conflictivas quedan "
        "pendientes de revisión. Cada referencia de envío se cuenta una vez."
    )
    st.write(
        "Los retrasos pueden depender del transporte, el destino y otros "
        "factores. Estos datos no permiten atribuir toda la responsabilidad "
        "al proveedor ni calcular ahorros económicos."
    )

if cantidad_evaluable:
    evaluables["retraso_dias"] = (
        evaluables["diferencia_dias"].clip(lower=0)
    )

    tabla = evaluables.groupby("proveedor").agg(
        envios_evaluables=("referencia_envio", "size"),
        envios_puntuales=("puntual", "sum"),
    )
    tabla["envios_tardios"] = (
        tabla["envios_evaluables"] - tabla["envios_puntuales"]
    )
    tabla["puntualidad_pct"] = (
        100 * tabla["envios_puntuales"] / tabla["envios_evaluables"]
    )

    retrasos = evaluables.loc[
        evaluables["retraso_dias"] > 0
    ].groupby("proveedor")["retraso_dias"].mean()

    tabla["retraso_promedio_tardios_dias"] = retrasos
    tabla = tabla.sort_values("envios_evaluables", ascending=False)

    st.subheader("Puntualidad de los diez proveedores con más envíos")
    st.bar_chart(tabla.head(10)[["puntualidad_pct"]])
    st.caption(
        "La selección se basa en volumen de envíos. "
        "Compara el porcentaje junto con la cantidad de observaciones."
    )

    st.subheader("Indicadores por proveedor")
    st.dataframe(tabla.round(2))

    st.download_button(
        "Descargar indicadores en CSV",
        data=tabla.reset_index().to_csv(index=False).encode("utf-8-sig"),
        file_name="indicadores_filtrados.csv",
        mime="text/csv",
    )
else:
    st.info("Todos los envíos seleccionados están pendientes de revisión.")

st.subheader("Detalle de los envíos seleccionados")
st.dataframe(filtrados)

st.download_button(
    "Descargar envíos seleccionados",
    data=filtrados.to_csv(index=False).encode("utf-8-sig"),
    file_name="envios_filtrados.csv",
    mime="text/csv",
)