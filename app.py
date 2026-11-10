from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Healthcare Supplier Performance Dashboard",
    page_icon="📦",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
data_file = ROOT / "data" / "processed" / "envios.csv"

st.title("📦 Healthcare Supplier Performance Dashboard")
st.caption("Historical healthcare product delivery analysis, 2006–2015.")

if not data_file.exists():
    st.error("Missing data/processed/envios.csv. Run the data preparation scripts first.")
    st.stop()

shipments = pd.read_csv(
    data_file,
    dtype={"evaluable": "boolean", "puntual": "boolean"},
)
shipments["fecha_entrega"] = pd.to_datetime(
    shipments["fecha_entrega"], errors="coerce"
)

# The source CSV keeps its original Spanish column names for compatibility
# with the existing data-processing scripts.
DISPLAY_COLUMNS = {
    "referencia_envio": "Shipment reference",
    "proveedor": "Supplier",
    "pais": "Destination country",
    "fecha_programada": "Scheduled delivery date",
    "fecha_entrega": "Actual delivery date",
    "numero_lineas": "Product line items",
    "evaluable": "Eligible for evaluation",
    "diferencia_dias": "Delivery difference (days)",
    "puntual": "On time",
    "retraso_dias": "Delay (days)",
}
KPI_COLUMNS = {
    "envios_evaluables": "Eligible shipments",
    "envios_puntuales": "On-time shipments",
    "envios_tardios": "Late shipments",
    "puntualidad_pct": "On-time delivery rate (%)",
    "retraso_promedio_tardios_dias": "Average delay of late shipments (days)",
}

st.sidebar.header("Filters")
st.sidebar.caption("Leave a selection empty to include all values.")

suppliers = st.sidebar.multiselect(
    "Supplier",
    sorted(shipments["proveedor"].dropna().unique()),
    placeholder="Select suppliers",
)
countries = st.sidebar.multiselect(
    "Destination country",
    sorted(shipments["pais"].dropna().unique()),
    placeholder="Select countries",
)
years = st.sidebar.multiselect(
    "Delivery year",
    sorted(shipments["fecha_entrega"].dt.year.dropna().astype(int).unique()),
    placeholder="Select years",
)

filtered = shipments.copy()

late_only = st.sidebar.checkbox(
    "Show late shipments only",
    value=False,
    help="Includes only eligible shipments received after their scheduled date.",
)

if suppliers:
    filtered = filtered[filtered["proveedor"].isin(suppliers)]
if countries:
    filtered = filtered[filtered["pais"].isin(countries)]
if years:
    filtered = filtered[filtered["fecha_entrega"].dt.year.isin(years)]

if late_only:
    filtered = filtered.loc[
        filtered["evaluable"].fillna(False)
        & filtered["puntual"].eq(False).fillna(False)
    ]

if filtered.empty:
    st.info("No shipments match the selected filters.")
    st.stop()

eligible = filtered.loc[filtered["evaluable"].fillna(False)].copy()

selected_count = len(filtered)
eligible_count = len(eligible)
pending_count = selected_count - eligible_count
on_time_count = int(eligible["puntual"].sum())
late_count = eligible_count - on_time_count

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected shipments", f"{selected_count:,}")
col2.metric("Eligible shipments", f"{eligible_count:,}")
col3.metric("Late shipments", f"{late_count:,}")
col4.metric(
    "On-time delivery rate",
    f"{100 * on_time_count / eligible_count:.2f}%"
    if eligible_count else "No data",
)

st.caption(
    f"Pending data review: {pending_count:,}. "
    "These shipments are excluded from on-time delivery calculations."
)

with st.expander("How to interpret these indicators"):
    st.write(
        "A shipment is on time when it arrives on or before the scheduled "
        "delivery date. The on-time delivery rate is the share of eligible "
        "shipments delivered on time."
    )
    st.write(
        "Shipments with conflicting scheduled delivery dates are flagged "
        "for review. Each shipment reference is counted only once."
    )
    st.write(
        "Delays may also be influenced by transportation, destination, "
        "and other factors. These data do not establish supplier fault "
        "or quantify cost savings."
    )

if eligible_count:
    eligible["retraso_dias"] = eligible["diferencia_dias"].clip(lower=0)

    supplier_kpis = eligible.groupby("proveedor").agg(
        envios_evaluables=("referencia_envio", "size"),
        envios_puntuales=("puntual", "sum"),
    )
    supplier_kpis["envios_tardios"] = (
        supplier_kpis["envios_evaluables"] - supplier_kpis["envios_puntuales"]
    )
    supplier_kpis["puntualidad_pct"] = (
        100 * supplier_kpis["envios_puntuales"]
        / supplier_kpis["envios_evaluables"]
    )

    mean_late_delay = eligible.loc[
        eligible["retraso_dias"] > 0
    ].groupby("proveedor")["retraso_dias"].mean()

    supplier_kpis["retraso_promedio_tardios_dias"] = mean_late_delay
    supplier_kpis = supplier_kpis.sort_values(
        "envios_evaluables", ascending=False
    )

    st.subheader("On-time delivery rate: 10 suppliers with the most shipments")
    chart_data = supplier_kpis.head(10)[["puntualidad_pct"]].rename(
        columns=KPI_COLUMNS
    )
    chart_data.index.name = "Supplier"
    st.bar_chart(chart_data)
    st.caption(
        "Suppliers are selected by shipment volume. Consider each "
        "percentage alongside the number of observations."
    )

    st.subheader("Supplier performance indicators")
    displayed_kpis = supplier_kpis.rename(columns=KPI_COLUMNS)
    displayed_kpis.index.name = "Supplier"
    st.dataframe(displayed_kpis.round(2))

    st.download_button(
        "Download supplier indicators (CSV)",
        data=displayed_kpis.reset_index().to_csv(index=False).encode("utf-8-sig"),
        file_name="supplier_performance_indicators.csv",
        mime="text/csv",
    )
else:
    st.info("All selected shipments are pending data review.")

st.subheader("Selected shipment details")
displayed_shipments = filtered.rename(columns=DISPLAY_COLUMNS)
st.dataframe(displayed_shipments)

st.download_button(
    "Download selected shipments (CSV)",
    data=displayed_shipments.to_csv(index=False).encode("utf-8-sig"),
    file_name="selected_shipments.csv",
    mime="text/csv",
)
