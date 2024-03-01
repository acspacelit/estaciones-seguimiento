import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit_shadcn_ui as ui
from local_components import card_container
import altair as alt

# Configuración inicial de la página
st.set_page_config(page_title="Análisis de Eficiencia Operativa", page_icon="📊")

# URLs de las hojas de Google Sheets
estaciones = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3uglhp1iEb6nz_Rjh6SnKyt0GqaAxOwGIqsQEdgcwJfrSP2wOZqFfrIjKL3KfsLzi4sSq2HJ3nkAt/pub?gid=0&single=true&output=csv"

# Función para cargar los datos desde la URL
def load_data_from_url(url):
    try:
        return pd.read_csv(url, header=0)
    except Exception as e:
        st.error("Error al cargar los datos: " + str(e))
        return None
    
def get_year_for_operation(date):
    return date.year if pd.notnull(date) else None

# Título de la aplicación
st.title('Dashboard de Streamlit')

# Carga los datos
data = load_data_from_url(estaciones)

def to_numeric(column):
    # Remove commas and convert to numeric, coercing errors to NaN
    return pd.to_numeric(column.str.replace(',', '.'), errors='coerce')

# Assume 'KPI' is the column you're having trouble with
data['KPI'] = to_numeric(data['KPI'])
data['AporteFONPLATAVigente'] = to_numeric(data['AporteFONPLATAVigente'])

# Widgets para interactividad
years = data['AÑO'].dropna().astype(int)
min_year, max_year = int(years.min()), int(years.max())
selected_years = st.slider('Selecciona el rango de años:', min_year, max_year, (min_year, max_year))

all_stations = ['Todas'] + list(data['Estaciones'].dropna().unique())
selected_station = st.selectbox('Selecciona una Estación', all_stations)

# Filtro por país con opción "Todos"
all_countries = ['Todos'] + list(data['Pais'].dropna().unique())
selected_countries = st.multiselect('Selecciona Países', all_countries, default='Todos')

# Aplicar filtros al DataFrame
filtered_df = data[
    (data['AÑO'] >= selected_years[0]) &
    (data['AÑO'] <= selected_years[1])
        ]

if selected_station != 'Todas':
    filtered_df = filtered_df[filtered_df['Estaciones'] == selected_station]

        # Modificado para manejar múltiples selecciones de países
    if 'Todos' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]


st.header("         Análisis de la Eficiencia Operativa")
figsize = (7, 5)  # Definir el tamaño de la figura para los gráficos

# Cálculos previos de tus métricas
average_kpi = filtered_df['KPI'].mean()
unique_operation_count = filtered_df['IDEtapa'].nunique()
total_stations = ((filtered_df['AporteFONPLATAVigente'].sum())/1000000).round(2)

Infraestructura = filtered_df[filtered_df['SEC'] == 'INF']
inf_operation = len(Infraestructura)

Social = filtered_df[filtered_df['SEC'] == 'SOC']
soc_operation = len(Social)

Productivo = filtered_df[filtered_df['SEC'] == 'PRO']
pro_operation = len(Productivo)

# Primera fila de tarjetas
row1_cols = st.columns(3)  # Esto crea tres columnas para la primera fila

with row1_cols[0]:
    ui.metric_card(
        title="Tiempo Promedio",
        content=f"{average_kpi:.2f} Meses",
        description="Promedio de KPI",
        key="card_kpi",
    )

with row1_cols[1]:
    ui.metric_card(
        title="Proyectos Totales",
        content=str(unique_operation_count),
        description="Total de proyectos únicos",
        key="card_projects",
    )

with row1_cols[2]:
    ui.metric_card(
        title="Aporte Fonplata",
        content=f"${total_stations}M",
        description="En millones de dólares",
        key="card_aporte",
    )

# Segunda fila de tarjetas
row2_cols = st.columns(3)  # Esto crea tres columnas para la segunda fila

with row2_cols[0]:
    ui.metric_card(
        title="Infraestructura",
        content=str(inf_operation),
        description="Proyectos de Infraestructura",
        key="card_infra",
    )

with row2_cols[1]:
    ui.metric_card(
        title="Socio-Económicos",
        content=str(soc_operation),
        description="Proyectos Socio-Económicos",
        key="card_social",
    )

with row2_cols[2]:
    ui.metric_card(
        title="Productivos",
        content=str(pro_operation),
        description="Proyectos Productivos",
        key="card_productivo",
    )

# Pivotear el DataFrame para obtener el KPI promedio por país y año
kpi_pivot_df = filtered_df.pivot_table(values='KPI', index='Pais', columns='AÑO', aggfunc='mean')

        # Redondear todos los valores numéricos a dos decimales
kpi_pivot_df = kpi_pivot_df.round(2)

        # Opción para reemplazar los valores None/NaN con un string vacío
kpi_pivot_df = kpi_pivot_df.fillna('')

        # Convertir las etiquetas de las columnas a enteros (los años)
kpi_pivot_df.columns = kpi_pivot_df.columns.astype(int)

        # Resetear el índice para llevar 'ESTACIONES' a una columna
kpi_pivot_df.reset_index(inplace=True)

        # Preparar los datos para el gráfico
kpi_avg_by_country_station = filtered_df.groupby(['Pais', 'Estaciones'])['KPI'].mean().reset_index()

        # Definir el esquema de color personalizado
color_scheme = {
        "Aprobacion": "lightgreen",
        "Vigencia": "skyblue",
        "PrimerDesembolso": "salmon",
        "Elegibilidad": "gold"
        }

        # Crear el gráfico de barras apiladas
bar_chart = alt.Chart(kpi_avg_by_country_station).mark_bar().encode(
    x='Pais:N',
    y=alt.Y('sum(KPI):Q', stack='zero', title='KPI Promedio'),
    color=alt.Color('Estaciones:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values()))),
    tooltip=['Pais', 'Estaciones', 'KPI']
)

        # Crear las etiquetas de texto para cada barra
text_chart = alt.Chart(kpi_avg_by_country_station).mark_text(
    align='center',
    baseline='middle',
    color='black',  # Color del texto
    ).encode(
        x='Pais:N',
        y=alt.Y('sum(KPI):Q', stack='zero', title=''),
        text=alt.Text('sum(KPI):Q', format='.2f'),
        color=alt.value('black')  # Esto asegura que el texto sea negro
)

        # Combinar gráficos de barras y texto
final_chart = (bar_chart + text_chart).properties(
    width=600,
    height=400,
    title='KPI Promedio por País y Estación'
)

# Definir la paleta de colores para los países
country_colors = {
    "Argentina": "#36A9E1",
    "Bolivia": "#F39200",
    "Brasil": "#009640",
    "Paraguay": "#E30613",
    "Uruguay": "#27348B"
    }

# Crear el gráfico de pastel (pie chart)
pie_chart = alt.Chart(filtered_df).transform_aggregate(
    # Calcular el total de aportes por país
    total='sum(AporteFONPLATAVigente)',
    groupby=['Pais']
).transform_calculate(
    # Calcular el porcentaje del total para cada país
    porcentaje='datum.total / sum(datum.total) over ()'
).mark_arc().encode(
    # Área del pastel basada en el porcentaje calculado
    theta=alt.Theta(field='porcentaje', type='quantitative', stack=True),
    # Color según el país con mapeo de colores personalizado
    color=alt.Color('Pais:N', scale=alt.Scale(domain=list(country_colors.keys()), range=list(country_colors.values())), legend=alt.Legend(title="País")),
    # Información para tooltip
    tooltip=[alt.Tooltip('Pais:N'), alt.Tooltip('total:Q', title='Aporte FONPLATA Vigente')],
    # Texto para la etiqueta, mostrando el país y el monto en millones formateado
    text=alt.Text('Pais:N')
).properties(
    # Título del gráfico
    title='Distribución de Aportes FONPLATA Vigentes por País'
)

# Mostrar el gráfico
st.altair_chart(pie_chart, use_container_width=True)

