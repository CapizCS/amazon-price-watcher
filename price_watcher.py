import os
import re
from playwright.sync_api import sync_playwright

ASIN = "B0DGHWD7CT"
MAX_PRICE = 99.00

AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}?th=1"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def parse_price(text):
    if not text:
        return None

    match = re.search(
        r"(\d{1,4}(?:\.\d{3})*(?:,\d{1,2})?)",
        text
    )

    if not match:
        return None

    value = match.group(1)
    value = value.replace(".", "").replace(",", ".")

    try:
        price = float(value)
    except ValueError:
        return None

    if 1 <= price <= 10000:
        return price

    return None


def get_amazon_price():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            locale="it-IT",
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        print("Apertura pagina Amazon...")

        page.goto(
            AMAZON_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print(f"Titolo pagina: {page.title()}")

        # Prezzo principale visualizzato
        selectors = [
            ".apex-pricetopay-value .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-offscreen",
            "#corePrice_feature_div .a-offscreen",
            "#buybox .a-offscreen",
            "#newBuyBoxPrice",
        ]

        for selector in selectors:

            try:
                element = page.locator(selector).first

                if element.count() > 0:

                    text = element.inner_text()

                    print(
                        f"Elemento trovato: {selector}"
                    )
                    print(
                        f"Testo prezzo: {text}"
                    )

                    price = parse_price(text)

                    if price is not None:
                        browser.close()
                        return price

            except Exception:
                pass

        # Fallback: cerca il prezzo base nel DOM
        try:

            element = page.locator(
                "#attach-base-product-price"
            ).first

            if element.count() > 0:

                value = element.get_attribute("value")

                print(
                    "attach-base-product-price:"
                    f" {value}"
                )

                price = parse_price(value)

                if price is not None:
                    browser.close()
                    return price

        except Exception:
            pass

        print("Prezzo non trovato nella pagina.")

        browser.close()

        return None


def send_telegram(message):

    import requests

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
        print(f"Errore: {e}")
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

        print("✅ Telegram inviato.")

    else:

        print("❌ Prezzo sopra soglia.")
        print("Nessun Telegram.")


if __name__ == "__main__":
    main()
