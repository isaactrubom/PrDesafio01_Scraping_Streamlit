# Parte 2: dashboard con Streamlit
# Ejecutar con: streamlit run app.py

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Libros - Books to Scrape", page_icon="📚", layout="wide")
st.title("📚 Análisis de libros de Books to Scrape")
st.caption("Datos extraídos con BeautifulSoup. Usa los filtros de la izquierda para explorarlos.")

# 1. Cargar los CSV generados por scraper.py
libros = pd.read_csv("libros.csv", parse_dates=["fecha_extraccion"])
categorias = pd.read_csv("categorias.csv")

# 2. Filtros en la barra lateral
st.sidebar.header("Filtros")

lista_categorias = sorted(libros["categoria"].unique())
cats = st.sidebar.multiselect("Categorías", lista_categorias, placeholder="Todas")

precio_min, precio_max = st.sidebar.slider(
    "Precio (£)",
    float(libros["precio"].min()), float(libros["precio"].max()),
    (float(libros["precio"].min()), float(libros["precio"].max())),
)

rating_min, rating_max = st.sidebar.slider("Rating (estrellas)", 1, 5, (1, 5))

busqueda = st.sidebar.text_input("Buscar título")

# Aplicamos los filtros sobre el DataFrame
df = libros[
    libros["precio"].between(precio_min, precio_max)
    & libros["rating"].between(rating_min, rating_max)
    & libros["titulo"].str.contains(busqueda, case=False, regex=False)
]
if cats:  # si no se elige ninguna categoría, se muestran todas
    df = df[df["categoria"].isin(cats)]

if df.empty:
    st.warning("Ningún libro cumple los filtros. Prueba a ampliarlos.")
    st.stop()

# Métricas rápidas
c1, c2, c3 = st.columns(3)
c1.metric("Libros", len(df))
c2.metric("Precio medio", f"£{df['precio'].mean():.2f}")
c3.metric("Rating medio", f"{df['rating'].mean():.2f} ⭐")

# 3. Tabla interactiva con los resultados filtrados
st.subheader("Libros filtrados")
st.dataframe(
    df,
    hide_index=True,
    column_config={
        "url_portada": st.column_config.ImageColumn("Portada"),
        "precio": st.column_config.NumberColumn("Precio", format="£%.2f"),
        "fecha_extraccion": st.column_config.DateColumn("Extraído"),
    },
)

# 4. Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("¿Cuántos libros hay de cada rating?")
    st.bar_chart(df["rating"].value_counts().sort_index(), x_label="Estrellas", y_label="Nº de libros")

with col2:
    st.subheader("¿Cómo se reparten los precios?")
    rangos = pd.cut(df["precio"], bins=[0, 20, 30, 40, 50, 60], labels=["<20", "20-30", "30-40", "40-50", "50-60"])
    st.bar_chart(rangos.value_counts().sort_index(), x_label="Precio (£)", y_label="Nº de libros")

# Pregunta de análisis: ¿influye el precio en la valoración?
st.subheader("¿Los libros más caros tienen mejor valoración?")
precio_por_rating = df.groupby("rating")["precio"].mean()
st.bar_chart(precio_por_rating, x_label="Estrellas", y_label="Precio medio (£)")

correlacion = df["precio"].corr(df["rating"])
if pd.isna(correlacion) or abs(correlacion) < 0.1:
    conclusion = "No hay relación: el precio **no** influye en la valoración."
elif correlacion > 0:
    conclusion = "Hay una relación positiva: los libros caros tienden a tener mejor valoración."
else:
    conclusion = "Hay una relación negativa: los libros caros tienden a tener peor valoración."
st.info(f"Correlación precio-rating: **{correlacion:.2f}**. {conclusion}")

# Gráfico con el segundo CSV: categorías más grandes
st.subheader("Top 10 categorías con más libros")
top = categorias.sort_values("num_libros", ascending=False).head(10)
st.bar_chart(top, x="categoria", y="num_libros", x_label="Categoría", y_label="Nº de libros", horizontal=True)
st.dataframe(top, hide_index=True)
