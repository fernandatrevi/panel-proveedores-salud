# Healthcare Supplier Performance Dashboard

**Supply Chain Analytics · Python · pandas · Streamlit**

**[Open the live dashboard](https://panel-proveedores-salud-fernandatrevi.streamlit.app/)**

Analyze historical healthcare supply deliveries, supplier performance and purchasing records with an interactive dashboard. The analysis uses **2006–2015** data and does not describe suppliers' current performance.

## Project overview

This project converts shipment-level purchasing records into transparent, reproducible on-time delivery indicators. Users can filter the results by supplier, destination country and delivery year, inspect performance metrics and download CSV results.

## Key results

| Metric | Historical result |
|---|---:|
| Original product line items | 10,324 |
| Original data columns | 33 |
| Distinct shipment references | 7,030 |
| Shipments eligible for punctuality evaluation | 7,020 |
| On-time shipments | 6,222 |
| Late shipments | 798 |
| Overall on-time rate | **88.63%** |
| Shipment references requiring date review | 10 |

An eligible shipment is on time if the actual delivery date is on or before the scheduled delivery date. Shipment references with conflicting scheduled dates are excluded until reviewed. Each shipment is counted **once**, regardless of how many product lines it contains.

**Important:** Late deliveries do not establish that a supplier caused the delay. Customs, transportation, receiving facilities and other factors may contribute.

## Data engineering and validation

1. Retain the original CSV in `data/raw`.
2. Check missing values, identifiers, types, duplicates and date consistency.
3. Group product lines at shipment-reference level (original identifier: `asn/dn #`).
4. Assign supplier, country and dates only when the shipment's source rows are consistent and complete.
5. Flag missing or contradictory dates for review instead of filling them with zero.
6. Export the prepared data to `data/processed/envios.csv` and supplier KPIs to `data/processed/indicadores_proveedores.csv`.

The processed data contains one row per shipment reference. The on-time rate is computed from eligible shipments, **not** by averaging individual supplier percentages.

## Metrics and definitions

| KPI | Definition |
|---|---|
| Eligible shipments | Shipment references with complete, consistent supplier, country and date fields |
| On-time shipments | Eligible shipments received on or before the scheduled date |
| Late shipments | Eligible shipments received after the scheduled date |
| On-time delivery rate | On-time shipments / eligible shipments × 100 |
| Overall delay average | Average positive delay days across eligible shipments; on-time shipments contribute zero |
| Late-only delay average | Average delay days for late shipments only; blank if there are none |

The delivery-date difference is actual minus scheduled. A positive result indicates a delay.

## Dashboard functionality

- Filter by supplier, destination country and actual delivery year.
- Review shipment counts and on-time delivery rates.
- Identify unresolved data-quality issues.
- Compare supplier KPIs through charts and tables.
- Download filtered shipments and indicators as CSV.

An empty filter selection includes all available values. Conflicting scheduled dates are not treated as on-time or late.

**[Explore the live dashboard](https://panel-proveedores-salud-fernandatrevi.streamlit.app/)**

## Reproduce the analysis locally

The documented development environment used Python 3.14.2.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/revisar_datos.py
python src/preparar_datos.py
python src/calcular_indicadores.py
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

On Windows, activate the virtual environment from `.venv\Scripts\activate`. In GitHub Codespaces, open port 8501 from the **Ports** tab and keep the application process running.

The scripts produce derived files under `data/processed`. When switching datasets, revalidate field definitions, counts and dates before using the resulting KPIs.

## Manual dashboard checks documented

| Filter | Eligible shipments | Late shipments | On-time rate |
|---|---:|---:|---:|
| All | 7,020 | 798 | 88.63% |
| SCMS from RDC | 3,440 | 556 | 83.84% |
| SCMS from RDC in 2014 | 421 | 153 | 63.66% |

For Belize, a documented spot check found one eligible, on-time shipment delivered 14 days early; selecting Belize in 2014 correctly returned no matching shipment records. CSV exports were also spot-checked. **These are targeted manual checks, not exhaustive test coverage.**

## Business interpretation

The historical late-delivery share is **11.37%** among evaluated shipments. Filters can help procurement and logistics teams identify where to investigate delivery reliability, review service commitments and prioritize supplier discussions.

The project does **not** establish supplier fault, financial savings, complete deliveries (OTIF), product quality, hospital clinical outcomes or present-day procurement performance.

## Adapting the workflow to another organization

Minimum required data: unique shipment or delivery reference, supplier identifier, receiving location, promised date and actual receipt date.

To adapt:
1. Export purchasing/receiving records to CSV and preserve an original copy.
2. Normalize supplier identifiers and investigate incomplete dates, duplicates and partial deliveries.
3. Update `src/preparar_datos.py` to map the new source schema.
4. Produce the fields `referencia_envio`, `proveedor`, `pais`, `fecha_programada`, `fecha_entrega`, `numero_lineas`, `evaluable`, `diferencia_dias` and `puntual`.
5. If locations are not countries, adjust the destination filter in `app.py`.
6. Manually cross-check a shipment sample and reconcile totals with the source system.

Keep the original promised-date change history: editing a promised date after late delivery can obscure the delay. Use approved environments for internal procurement records; patient data is not needed.

### Data that could extend this analysis

Requested/received quantities (for OTIF), purchase order dates (for lead time), comparable product identifiers and units (for unit prices), currencies and logistics costs, documented delay reasons, stock levels, rush purchase expenses, returns and damages.

These additional KPIs are **not currently implemented** and require new data and code changes. To claim cost savings, compare costs before and after an intervention while controlling for relevant volume and product-mix differences.

## Scope

This is a historical supplier delivery analytics project and a portfolio demonstration of data preparation, KPI integrity and interactive reporting. Results from this dataset should not be generalized to a current hospital or supplier population without validation.
