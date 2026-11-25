# Web Scraping con BeautifulSoup y Streamlit

Scraping de los 1000 libros de [Books to Scrape](https://books.toscrape.com) y dashboard interactivo para analizarlos.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python scraper.py        # genera libros.csv y categorias.csv (~1 min)
streamlit run app.py     # abre el dashboard en el navegador
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `scraper.py` | Parte 1: descarga las páginas, extrae los datos con BeautifulSoup y los guarda con Pandas |
| `app.py` | Parte 2: dashboard de Streamlit con filtros y gráficos |
| `libros.csv` | Un libro por fila: título, categoría, precio, rating, stock, portada, fecha de extracción |
| `categorias.csv` | Resumen por categoría: nº de libros, precio medio y rating medio |

## Flujo de datos

1. Leo el menú lateral de la portada para sacar las 50 categorías y sus enlaces.
2. Entro en cada categoría y recorro sus páginas siguiendo el botón **next** hasta que no hay más.
3. De cada `<article class="product_pod">` saco los datos y los limpio en el mismo script.
4. Pandas guarda `libros.csv` y, con un `groupby`, `categorias.csv`.
5. `app.py` carga los CSV, aplica los filtros y pinta los gráficos.

## Ética y buenas prácticas

- **robots.txt**: el script lo comprueba al empezar. Devuelve 404, así que no hay restricciones; además la web está hecha para practicar scraping.
- **User-Agent**: me identifico con `PracticaDAM-Scraper/1.0 (proyecto educativo)`.
- **Retardos**: `time.sleep(0.5)` después de cada petición para no saturar el servidor. Son ~70 peticiones en total.
- No hay login ni datos personales: solo información pública de productos.

## Decisiones y problemas resueltos

- **Por qué recorro por categorías y no la lista general**: el listado general no dice el género del libro. Entrando por categoría lo sé sin abrir la ficha de cada libro (70 peticiones en vez de más de 1000).
- **Título**: el texto del enlace sale cortado con "...", así que uso el atributo `title`, que tiene el título completo.
- **Precio**: viene como `"£51.77"`. Quito el símbolo y lo convierto a `float` para poder filtrar y hacer medias.
- **Símbolo £ roto**: salía como `Â£` porque `requests` detectaba mal la codificación. Lo arreglé forzando `r.encoding = "utf-8"`.
- **Rating**: no es texto visible, está en la clase CSS (`star-rating Three`). Lo paso a número con un diccionario.
- **Stock**: lo guardo como booleano (`True`/`False`) en vez de texto.
- **Fecha**: la web no tiene fechas, así que guardo la fecha de extracción para saber cuándo se tomaron los datos.
- **Enlaces relativos**: los `href` son relativos (`../../media/...`), así que uso `urljoin` para construir la URL completa.

## Conclusiones del análisis

- La correlación entre precio y rating es **0.03**: el precio **no** influye en la valoración.
- Los precios están repartidos de forma bastante uniforme entre £10 y £60.
- Las categorías más grandes son "Default" (152) y "Nonfiction" (110). "Default" y "Add a comment" no son géneros reales: son categorías de relleno de la propia web.
- 11 categorías tienen solo 1 o 2 libros, así que sus medias no son fiables.
