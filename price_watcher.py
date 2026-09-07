import os
import re
import requests
from bs4 import BeautifulSoup

ASIN = "B0DGHWD7CT"
MAX_PRICE = 99.00

AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def extract_prices(html):
    """
    Estrae tutti i possibili prezzi presenti nell'HTML
    senza decidere quale sia quello corretto.
    """

    candidates = []

    patterns = {
        "priceAmount": r'"priceAmount"\s*:\s*([0-9]+(?:[.,][0-9]+)?)',
        "price": r'"price"\s*:\s*"([0-9]+(?:[.,][0-9]+)?)"',
        "price_whole": r'class="a-price-whole"[^>]*>([0-9]+)',
        "offscreen": r'class="a-offscreen"[^>]*>\s*([0-9.,]+)\s*€',
        "formatted_price": r'([0-9]{1,4}(?:[.,][0-9]{3})*(?:,[0-9]{1,2})?)\s*€',
    }

    for name, pattern in patterns.items():

        matches = re.findall(pattern, html, re.IGNORECASE)

        for value in matches:

            value = value.replace(".", "").replace(",", ".")

            try:
                price = float(value)
            except ValueError:
                continue

            if 1 <= price <= 10000:
                candidates.append((name, price))

    # Elimina duplicati mantenendo l'ordine
    unique = []
    seen = set()

    for source, price in candidates:

        key = (source, price)

        if key not in seen:
            seen.add(key)
            unique.append((source, price))

    return unique


def get_amazon_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
    }

    response = requests.get(
        AMAZON_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def main():

    print("==========================================")
    print("AMAZON PRICE WATCHER - DIAGNOSTICA")
    print("==========================================")
    print(f"ASIN: {ASIN}")
    print(f"Soglia: {MAX_PRICE:.2f} €")
    print(f"URL: {AMAZON_URL}")
    print()

    try:
        html = get_amazon_page()

    except Exception as e:
        print(f"ERRORE AMAZON: {e}")
        return

    print(f"HTML ricevuto: {len(html):,} caratteri")
    print()

    # Titolo
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("#productTitle")

    if title:
        print("Titolo:")
        print(title.get_text(" ", strip=True))
    else:
        print("Titolo non trovato.")

    print()
    print("==========================================")
    print("PREZZI TROVATI NELL'HTML")
    print("==========================================")

    candidates = extract_prices(html)

    if not candidates:
        print("Nessun prezzo trovato.")
        return

    for source, price in candidates:
        print(f"{source:20} -> {price:.2f} €")

    print()
    print("==========================================")
    print("PREZZI UNICI")
    print("==========================================")

    unique_prices = sorted(set(price for _, price in candidates))

    for price in unique_prices:
        print(f"- {price:.2f} €")

    print()
    print("==========================================")
    print("FINE DIAGNOSTICA")
    print("==========================================")
    print("Nessun Telegram inviato.")
    print("Nessun alert generato.")


if __name__ == "__main__":
    main()
