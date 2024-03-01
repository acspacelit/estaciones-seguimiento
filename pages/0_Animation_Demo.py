import streamlit as st
import pandas as pd
import altair as alt
from local_components import card_container
import streamlit_shadcn_ui as ui

# Configuración inicial de la página
def setup_page():
    st.set_page_config(page_title="Análisis de Eficiencia Operativa", page_icon="📊")

# Función para cargar los datos desde la URL
def load_data_from_url(url):
    try:
        return pd.read_csv(url, header=0)
    except Exception as e:
        st.error("Error al cargar los datos: " + str(e))
        return None

# Función para convertir valores a numéricos
def to_numeric(column):
    return pd.to_numeric(column.str.replace(',', '.'), errors='coerce')

# Función para crear los widgets de interactividad
def create_interactive_widgets(data):
    years = data['AÑO'].dropna().astype(int)
    min_year, max_year = int(years.min()), int(years.max())
    selected_years = st.slider('Selecciona el rango de años:', min_year, max_year, (min_year, max_year))

    all_stations = ['Todas'] + list(data['Estaciones'].dropna().unique())
    selected_station = st.selectbox('Selecciona una Estación', all_stations)

    all_countries = ['Todos'] + list(data['Pais'].dropna().unique())
    selected_countries = st.multiselect('Selecciona Países', all_countries, default='Todos')

    return selected_years, selected_station, selected_countries

# Función para filtrar el DataFrame según la selección del usuario
def filter_data(data, selected_years, selected_station, selected_countries):
    filtered_df = data[
        (data['AÑO'] >= selected_years[0]) &
        (data['AÑO'] <= selected_years[1])
    ]

    if selected_station != 'Todas':
        filtered_df = filtered_df[filtered_df['Estaciones'] == selected_station]

    if 'Todos' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]
    return filtered_df

# Función para crear métricas y gráficos basada en los datos filtrados
def create_metrics_and_charts(filtered_df):
    st.header("Análisis de la Eficiencia Operativa")
    
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

# Función principal de la aplicación
def main():
    setup_page()

    # Título de la aplicación
    st.title('Dashboard de Streamlit')

    # Carga los datos
    data = load_data_from_url("https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3uglhp1iEb6nz_Rjh6SnKyt0GqaAxOwGIqsQEdgcwJfrSP2wOZqFfrIjKL3KfsLzi4sSq2HJ3nkAt/pub?gid=0&single=true&output=csv")

    # Aplicar filtros al DataFrame
    filtered_df = filter_data(data)

    # Mostrar gráficos y métricas
    show_metrics(filtered_df)
    create_bar_chart(filtered_df)
    create_pie_chart(filtered_df)

# Función para filtrar datos
def filter_data(data):
    years = data['AÑO'].dropna().astype(int)
    min_year, max_year = int(years.min()), int(years.max())
    selected_years = st.slider('Selecciona el rango de años:', min_year, max_year, (min_year, max_year))

    all_stations = ['Todas'] + list(data['Estaciones'].dropna().unique())
    selected_station = st.selectbox('Selecciona una Estación', all_stations)

    all_countries = ['Todos'] + list(data['Pais'].dropna().unique())
    selected_countries = st.multiselect('Selecciona Países', all_countries, default='Todos')

    filtered_df = data[
        (data['AÑO'] >= selected_years[0]) &
        (data['AÑO'] <= selected_years[1])
    ]

    if selected_station != 'Todas':
        filtered_df = filtered_df[filtered_df['Estaciones'] == selected_station]

    if 'Todos' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]

    return filtered_df

# Función para mostrar métricas
def show_metrics(filtered_df):
    st.header("Análisis de la Eficiencia Operativa")

    average_kpi = filtered_df['KPI'].mean()
    unique_operation_count = filtered_df['IDEtapa'].nunique()
    total_stations = ((filtered_df['AporteFONPLATAVigente'].sum())/1000000).round(2)

    Infraestructura = filtered_df[filtered_df['SEC'] == 'INF']
    inf_operation = len(Infraestructura)

    Social = filtered_df[filtered_df['SEC'] == 'SOC']
    soc_operation = len(Social)

    Productivo = filtered_df[filtered_df['SEC'] == 'PRO']
    pro_operation = len(Productivo)

    row1_cols = st.columns(3)

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

    row2_cols = st.columns(3)

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

# Función para crear gráfico de barras
def create_bar_chart(filtered_df):
    kpi_avg_by_country_station = filtered_df.groupby(['Pais', 'Estaciones'])['KPI'].mean().reset_index()

    color_scheme = {
        "Aprobacion": "lightgreen",
        "Vigencia": "skyblue",
        "PrimerDesembolso": "salmon",
        "Elegibilidad": "gold"
    }

    bar_chart = alt.Chart(kpi_avg_by_country_station).mark_bar().encode(
        x='Pais:N',
        y=alt.Y('sum(KPI):Q', stack='zero', title='KPI Promedio'),
        color=alt.Color('Estaciones:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values()))),
        tooltip=['Pais', 'Estaciones', 'KPI']
    )

    text_chart = alt.Chart(kpi_avg_by_country_station).mark_text(
        align='center',
        baseline='middle',
        color='black',
    ).encode(
        x='Pais:N',
        y=alt.Y('sum(KPI):Q', stack='zero', title=''),
        text=alt.Text('sum(KPI):Q', format='.2f'),
        color=alt.value('black')
    )

    final_chart = (bar_chart + text_chart).properties(
        width=600,
        height=400,
        title='KPI Promedio por País y Estación'
    )

    st.altair_chart(final_chart)

# Función para crear gráfico de pastel
def create_pie_chart(filtered_df):
    country_colors = {
        "Argentina": "#36A9E1",
        "Bolivia": "#F39200",
        "Brasil": "#009640",
        "Paraguay": "#E30613",
        "Uruguay": "#27348B"
    }

    pie_chart = alt.Chart(filtered_df).transform_aggregate(
        total='sum(AporteFONPLATAVigente)',
        groupby=['Pais']
    ).transform_calculate(
        porcentaje='datum.total / sum(datum.total) over ()'
    ).mark_arc().encode(
        theta=alt.Theta(field='porcentaje', type='quantitative', stack=True),
        color=alt.Color('Pais:N', scale=alt.Scale(domain=list(country_colors.keys()), range=list(country_colors.values())), legend=alt.Legend(title="País")),
        tooltip=[alt.Tooltip('Pais:N'), alt.Tooltip('total:Q', title='Aporte FONPLATA Vigente')],
        text=alt.Text('Pais:N')
    ).properties(
        title='Distribución de Aportes FONPLATA Vigentes por País'
    )

    st.altair_chart(pie_chart, use_container_width=True)

if __name__ == "__main__":
    main()
