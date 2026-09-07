import requests

ASIN = "B0DGHWD7CT"
AMAZON_URL = f"https://www.amazon.it/dp/{ASIN}"


def main():
    print("==========================================")
    print("AMAZON RESPONSE TEST")
    print("==========================================")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept": "text/html,application/xhtml+xml,"
                  "application/xml;q=0.9,*/*;q=0.8",
    }

    response = requests.get(
        AMAZON_URL,
        headers=headers,
        timeout=30,
        allow_redirects=True,
    )

    print(f"HTTP status: {response.status_code}")
    print(f"URL finale: {response.url}")
    print(f"Dimensione HTML: {len(response.text):,} caratteri")
    print()

    print("==========================================")
    print("INIZIO RISPOSTA AMAZON")
    print("==========================================")

    print(response.text[:3000])

    print()
    print("==========================================")
    print("FINE TEST")
    print("==========================================")


if __name__ == "__main__":
    main()
