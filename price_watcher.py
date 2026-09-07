import os
import re
import requests

ASIN = "B0DGHWD7CT"
MAX_PRICE = 99.00

AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}?th=1"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def parse_price(value):
    if not value:
        return None

    value = value.strip().replace("€", "").strip()

    try:
        if "," in value:
            value = value.replace(".", "").replace(",", ".")
        price = float(value)
    except ValueError:
        return None

    if 1 <= price <= 10000:
        return price

    return None


def get_amazon_price():
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
            "application/xml;q=0.9,image/avif,image/webp,"
            "*/*;q=0.8"
        ),
    }

    response = requests.get(
        AMAZON_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    html = response.text

    print(f"HTML ricevuto: {len(html):,} caratteri")

    # Metodo principale:
    # <input type="hidden"
    #        id="attach-base-product-price"
    #        value="119.0" />

    match = re.search(
        r'id=["\']attach-base-product-price["\']'
        r'[^>]*value=["\']([0-9.,]+)["\']',
        html,
        re.IGNORECASE,
    )

    if match:
        price = parse_price(match.group(1))

        if price is not None:
            print(
                "🎯 Prezzo trovato tramite "
                "attach-base-product-price."
            )
            return price

    print("❌ attach-base-product-price non trovato.")

    # Fallback:
    # <span class="a-offscreen">119,00€</span>

    match = re.search(
        r'class=["\'][^"\']*a-offscreen[^"\']*["\']'
        r'[^>]*>\s*([0-9.,]+)\s*€',
        html,
        re.IGNORECASE,
    )

    if match:
        price = parse_price(match.group(1))

        if price is not None:
            print(
                "Prezzo trovato tramite "
                "a-offscreen."
            )
            return price

    return None


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
        price = get_amazon_price()

    except Exception as e:
        print(f"Errore durante la lettura Amazon: {e}")
        return

    if price is None:
        print()
        print("⚠️ PREZZO NON LEGGIBILE.")
        print("Nessun Telegram inviato.")
        return

    print()
    print(f"💰 Prezzo trovato: {price:.2f} €")
    print(f"🎯 Soglia: {MAX_PRICE:.2f} €")

    if price <= MAX_PRICE:
        message = (
            "🚨 PRICE WATCHER\n\n"
            "🔥 PREZZO SOTTO SOGLIA!\n\n"
            "📦 Apple AirPods 4\n"
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
