import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Disney", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("data/disney_base.xlsx")
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df['duration_time'] = pd.to_numeric(df['duration_time'], errors='coerce')
    # Normalizar país (solo primer país si hay múltiples)
    df['country'] = df['country'].astype(str).apply(lambda x: x.split(",")[0].strip())
    return df.dropna(subset=['release_year'])

df = load_data()
st.title("🎬 Dashboard Interactivo de Producciones Disney")

# Filtros
with st.sidebar:
    st.header("Filtros")
    years = st.slider("Año de lanzamiento", int(df.release_year.min()), int(df.release_year.max()), (2010, 2020))
    selected_type = st.multiselect("Tipo de Producción", options=df['type'].unique(), default=df['type'].unique())
    selected_country = st.multiselect("País", options=df['country'].dropna().unique(), default=df['country'].dropna().unique())

# Aplicar filtros
filtered_df = df[
    (df['release_year'].between(years[0], years[1])) &
    (df['type'].isin(selected_type)) &
    (df['country'].isin(selected_country))
]

# --------------------
# Primera Capa
# --------------------
st.header("Primera Capa: Volumetría general de las producciones")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución por tipo de producción")
    fig_type = px.histogram(filtered_df, x='type', color='type')
    st.plotly_chart(fig_type, use_container_width=True)

with col2:
    st.subheader("Clasificación de contenido")
    fig_rating_pie = px.pie(
        filtered_df,
        names='rating',
        title='Proporción de clasificaciones',
        hole=0.4,
        width=700,
        height=500
    )
    st.plotly_chart(fig_rating_pie, use_container_width=True)

st.subheader("Distribución de duración de producciones")
fig_duration_hist = px.histogram(
    filtered_df,
    x='duration_time',
    nbins=30,
    title="Histograma de duración (minutos)",
    color_discrete_sequence=["#636EFA"]
)
st.plotly_chart(fig_duration_hist, use_container_width=True)

st.subheader("Evolución de lanzamientos por año")
fig_years = px.histogram(filtered_df, x='release_year', color='type', barmode='group')
st.plotly_chart(fig_years, use_container_width=True)


# --------------------
# Segunda Capa
# --------------------
st.header("Segunda Capa: Exploración de producciones específicas")

# 1. Distribución de duración por clasificación
st.subheader("Distribución de duración por clasificación")
fig_box_rating = px.box(
    filtered_df,
    x='rating',
    y='duration_time',
    color='rating',
    title="Boxplot de duración por clasificación"
)
st.plotly_chart(fig_box_rating, use_container_width=True)


# 2. Frecuencia de categorías por tipo
st.subheader("Frecuencia de categorías temáticas (listed_in)")
category_counts = (
    filtered_df['listed_in']
    .astype(str)
    .str.split(', ')
    .explode()
    .value_counts()
    .reset_index()
)

category_counts.columns = ['Categoria', 'Frecuencia']  # Renombrado correcto

fig_categories = px.bar(
    category_counts.head(15),
    x='Categoria',
    y='Frecuencia',
    title="Top 15 categorías más comunes"
)
st.plotly_chart(fig_categories, use_container_width=True)


# 3. Producción por país y tipo
st.subheader("Producción por país y tipo")
country_type = filtered_df.groupby(['country', 'type']).size().reset_index(name='count')
fig_country_type = px.bar(country_type, x='country', y='count', color='type', title="Producciones por país y tipo", barmode='stack')
st.plotly_chart(fig_country_type, use_container_width=True)

# 4. Diferencias entre películas y series en duración
st.subheader("Comparativa de duración entre películas y series")
fig_box = px.box(filtered_df, x='type', y='duration_time', color='type', title="Distribución de duración por tipo")
st.plotly_chart(fig_box, use_container_width=True)

# 5. Producciones con duración atípica
st.subheader("Producciones atípicas por duración")
outliers_df = filtered_df.sort_values(by='duration_time', ascending=False).head(10)
st.dataframe(outliers_df[['title', 'duration_time', 'rating', 'type', 'release_year']])

# 6. Evolución del tipo y clasificación combinada
st.subheader("Evolución tipo + clasificación")
grouped = filtered_df.groupby(['release_year', 'type', 'rating']).size().reset_index(name='count')
fig_evo = px.bar(grouped, x='release_year', y='count', color='rating', facet_col='type',
                 title="Evolución del tipo y clasificación combinada")
st.plotly_chart(fig_evo, use_container_width=True)
