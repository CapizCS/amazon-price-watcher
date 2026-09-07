import os
import re
import requests
from bs4 import BeautifulSoup

ASIN = "B0DGHWD7CT"
MAX_PRICE = 99.00

AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def parse_price(text):
    if not text:
        return None

    text = text.replace("\xa0", " ").strip()

    # Esempi:
    # 119,00 €
    # 119 €
    # €119,00
    match = re.search(r"(\d{1,4}(?:[.\s]\d{3})*(?:,\d{1,2})?)", text)

    if not match:
        return None

    value = match.group(1)
    value = value.replace(" ", "").replace(".", "").replace(",", ".")

    try:
        price = float(value)
    except ValueError:
        return None

    if 1 <= price <= 10000:
        return price

    return None


def get_amazon_data():
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

    soup = BeautifulSoup(response.text, "html.parser")

    title = None

    title_element = soup.select_one("#productTitle")

    if title_element:
        title = title_element.get_text(" ", strip=True)

    # Cerchiamo prima i contenitori del prezzo principale/acquistabile.
    selectors = [
        "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
        "#corePrice_feature_div .a-price .a-offscreen",
        "#apex_desktop .a-price .a-offscreen",
        "#buybox .a-price .a-offscreen",
        "#buybox_feature_div .a-price .a-offscreen",
        "#newBuyBoxPrice",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".priceToPay .a-offscreen",
    ]

    checked = []

    for selector in selectors:
        elements = soup.select(selector)

        for element in elements:
            text = element.get_text(" ", strip=True)
            checked.append((selector, text))

            price = parse_price(text)

            if price is not None:
                return price, title

    # Seconda ricerca più prudente.
    # Cerchiamo il prezzo dentro la zona principale del prodotto,
    # evitando di prendere automaticamente il primo prezzo dell'intera pagina.

    containers = [
        soup.select_one("#corePriceDisplay_desktop_feature_div"),
        soup.select_one("#corePrice_feature_div"),
        soup.select_one("#buybox"),
        soup.select_one("#buybox_feature_div"),
        soup.select_one("#apex_desktop"),
    ]

    for container in containers:
        if not container:
            continue

        elements = container.select(".a-price .a-offscreen")

        for element in elements:
            text = element.get_text(" ", strip=True)
            checked.append(("container", text))

            price = parse_price(text)

            if price is not None:
                return price, title

    print("Prezzo non trovato nei selettori principali.")

    if checked:
        print("Prezzi rilevati durante la ricerca:")

        for selector, text in checked[:20]:
            print(f"  {selector}: {text}")

    return None, title


def send_telegram(message):
    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
        timeout=30,
    )

    response.raise_for_status()


def main():
    print("==========================================")
    print("AMAZON PRICE WATCHER")
    print("==========================================")
    print(f"ASIN: {ASIN}")
    print(f"Soglia: {MAX_PRICE:.2f} €")
    print(f"URL: {AMAZON_URL}")
    print()

    try:
        price, title = get_amazon_data()

    except Exception as e:
        print(f"Errore durante la lettura Amazon: {e}")
        return

    if price is None:
        print()
        print("⚠️ PREZZO NON LEGGIBILE.")
        print("Nessun Telegram inviato.")
        return

    print(f"Titolo: {title or 'Non disponibile'}")
    print(f"Prezzo trovato: {price:.2f} €")
    print(f"Soglia: {MAX_PRICE:.2f} €")

    if price <= MAX_PRICE:

        message = (
            "🚨 PRICE WATCHER\n\n"
            "🔥 PREZZO SOTTO SOGLIA!\n\n"
            f"📦 {title or ASIN}\n"
            f"💰 Prezzo: {price:.2f} €\n"
            f"🎯 Soglia: {MAX_PRICE:.2f} €\n\n"
            f"🛒 {AMAZON_URL}"
        )

        send_telegram(message)

        print()
        print("✅ Telegram inviato.")

    else:
        print()
        print("❌ Prezzo sopra soglia.")
        print("Nessun Telegram.")


if __name__ == "__main__":
    main()
