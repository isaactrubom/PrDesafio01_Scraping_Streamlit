# Parte 1: scraping de https://books.toscrape.com con BeautifulSoup
# Recorre todas las categorías (así sabemos el género de cada libro)
# y guarda el resultado en libros.csv y categorias.csv

import time
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

# Nos identificamos con un User-Agent propio (buena práctica)
HEADERS = {"User-Agent": "PracticaDAM-Scraper/1.0 (proyecto educativo)"}

# Segundos de espera entre peticiones para no saturar el servidor
PAUSA = 0.5

# El rating viene como texto en la clase CSS ("star-rating Three"), lo pasamos a número
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def comprobar_robots():
    """Mira el robots.txt antes de empezar."""
    r = requests.get(BASE_URL + "robots.txt", headers=HEADERS)
    if r.status_code == 404:
        print("No hay robots.txt -> no hay restricciones. La web está hecha para practicar scraping.")
    else:
        print("Contenido de robots.txt:\n", r.text)


def descargar(url):
    """Descarga una página, espera un poco y devuelve el HTML parseado."""
    r = requests.get(url, headers=HEADERS)
    r.encoding = "utf-8"  # sin esto el símbolo £ sale como 'Â£'
    time.sleep(PAUSA)
    return BeautifulSoup(r.text, "html.parser")


def obtener_categorias():
    """Lee el menú lateral de la portada: nombre y enlace de cada categoría."""
    soup = descargar(BASE_URL)
    enlaces = soup.select("div.side_categories ul li ul li a")
    return [(a.text.strip(), urljoin(BASE_URL, a["href"])) for a in enlaces]


def extraer_libros(categoria, url):
    """Recorre todas las páginas de una categoría y devuelve sus libros."""
    libros = []
    while url:
        soup = descargar(url)

        # Cada libro está dentro de un <article class="product_pod">
        for libro in soup.select("article.product_pod"):
            titulo = libro.h3.a["title"]  # el texto del <a> sale cortado con "...", el atributo title no
            precio = libro.select_one("p.price_color").text
            rating = libro.select_one("p.star-rating")["class"][1]
            stock = libro.select_one("p.instock.availability").text.strip()
            portada = urljoin(url, libro.img["src"])

            libros.append({
                "titulo": titulo,
                "categoria": categoria,
                # Limpieza: "£51.77" -> 51.77 (número, no texto)
                "precio": float(precio.replace("£", "")),
                "rating": RATINGS[rating],
                "en_stock": stock == "In stock",
                "url_portada": portada,
                "fecha_extraccion": date.today(),
            })

        # Si hay botón "next" seguimos con la siguiente página, si no, paramos
        siguiente = soup.select_one("li.next a")
        url = urljoin(url, siguiente["href"]) if siguiente else None

    return libros


def main():
    comprobar_robots()

    todos = []
    for nombre, url in obtener_categorias():
        libros = extraer_libros(nombre, url)
        print(f"{nombre}: {len(libros)} libros")
        todos.extend(libros)

    # CSV 1: un libro por fila
    df = pd.DataFrame(todos)
    df["fecha_extraccion"] = pd.to_datetime(df["fecha_extraccion"])
    df.to_csv("libros.csv", index=False)

    # CSV 2: resumen por categoría
    resumen = df.groupby("categoria").agg(
        num_libros=("titulo", "count"),
        precio_medio=("precio", "mean"),
        rating_medio=("rating", "mean"),
    ).round(2).reset_index()
    resumen.to_csv("categorias.csv", index=False)

    print(f"\nGuardados {len(df)} libros en libros.csv y {len(resumen)} categorías en categorias.csv")


if __name__ == "__main__":
    main()
