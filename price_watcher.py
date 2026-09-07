import os
import re
import requests

ASIN = "B0DGHWD7CT"
MAX_PRICE = 99.00

AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def get_amazon_price():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
        "Accept-Language": "it-IT,it;q=0.9",
    }

    response = requests.get(
        AMAZON_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()
    html = response.text

    patterns = [
        r'"priceAmount"\s*:\s*([0-9]+[.,]?[0-9]*)',
        r'"price"\s*:\s*"([0-9]+[.,]?[0-9]*)"',
        r'class="a-price-whole"[^>]*>([0-9]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, html)

        if match:
            value = match.group(1).replace(",", ".")
            price = float(value)

            if 1 <= price <= 10000:
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
        print("Prezzo non leggibile.")
        return

    print(f"Prezzo trovato: {price:.2f} €")

    if price <= MAX_PRICE:
        message = (
            "🚨 PRICE WATCHER\n\n"
            "🔥 PREZZO SOTTO SOGLIA!\n\n"
            f"💰 Prezzo: {price:.2f} €\n"
            f"🎯 Soglia: {MAX_PRICE:.2f} €\n"
            f"📦 ASIN: {ASIN}\n\n"
            f"🛒 {AMAZON_URL}"
        )

        send_telegram(message)
        print("✅ Telegram inviato.")
    else:
        print("❌ Prezzo sopra soglia. Nessun Telegram.")


if __name__ == "__main__":
    main()
