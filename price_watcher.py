import os
import re
import requests

ASIN = "B0DGHWD7CT"
AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}"


def main():
    print("==========================================")
    print("AMAZON PRICE WATCHER - TEST 119")
    print("==========================================")
    print(f"ASIN: {ASIN}")
    print(f"URL: {AMAZON_URL}")
    print()

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

    try:
        response = requests.get(
            AMAZON_URL,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

    except Exception as e:
        print(f"ERRORE: {e}")
        return

    html = response.text

    print(f"HTML ricevuto: {len(html):,} caratteri")
    print()

    # Cerca esattamente 119 nel documento
    patterns = [
        r"119",
        r"119[,.]00",
        r"119[,.]0{1,2}",
        r"119,00\s*€",
        r"119\.00\s*€",
        r"€\s*119",
    ]

    found = False

    print("==========================================")
    print("RICERCA PREZZO 119 €")
    print("==========================================")

    for pattern in patterns:

        matches = list(re.finditer(pattern, html, re.IGNORECASE))

        if matches:
            found = True

            print()
            print(f"Pattern: {pattern}")
            print(f"Occorrenze: {len(matches)}")

            for match in matches[:10]:

                start = max(0, match.start() - 180)
                end = min(len(html), match.end() + 180)

                context = html[start:end]

                print("------------------------------------------")
                print(context)

    if not found:
        print("❌ Il valore 119 non compare nell'HTML ricevuto da GitHub.")

    print()
    print("==========================================")
    print("RICERCA PREZZI AMAZON")
    print("==========================================")

    price_patterns = [
        r'"priceAmount"\s*:\s*([0-9]+(?:[.,][0-9]+)?)',
        r'"price"\s*:\s*"([0-9]+(?:[.,][0-9]+)?)"',
        r'([0-9]{1,4}(?:[.,][0-9]{3})*(?:,[0-9]{1,2})?)\s*€',
    ]

    prices = []

    for pattern in price_patterns:

        matches = re.findall(pattern, html, re.IGNORECASE)

        for value in matches:

            try:
                value = value.replace(".", "").replace(",", ".")
                price = float(value)

                if 1 <= price <= 10000:
                    prices.append(price)

            except ValueError:
                pass

    unique_prices = sorted(set(prices))

    for price in unique_prices:
        print(f"{price:.2f} €")

    print()
    print("==========================================")
    print("FINE TEST")
    print("==========================================")


if __name__ == "__main__":
    main()
