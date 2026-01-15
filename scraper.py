import asyncio
import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

URL = "https://poweron.loe.lviv.ua/"
STATE_FILE = "state/group_4_1_last.txt"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("=== SCRAPER STARTED ===")

async def get_group_4_1_text():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(URL, wait_until="networkidle", timeout=60000)

        # Ждём появления хотя бы одного p с "Група"
        await page.wait_for_function(
            """() => [...document.querySelectorAll('p')]
            .some(p => p.innerText.includes('Група'))""",
            timeout=60000
        )

        paragraphs = await page.locator("p").all()

        for p in paragraphs:
            text = (await p.inner_text()).strip()
            if re.match(r"^Група\s*4\.1\.", text):
                await browser.close()
                return text

        await browser.close()
        raise ValueError("Строка 'Група 4.1.' не найдена")


def load_previous():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_current(value):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(value)


def send_telegram(text):
    import requests
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=10
    )


async def main():
    current_text = await get_group_4_1_text()
    previous_text = load_previous()

    if previous_text is None:
        save_current(current_text)
        return

    if current_text != previous_text:
        message = (
            f"Стало:\n{current_text}\n\n"
            "⚡ Зміна графіка для Групи 4.1\n\n"
            f"Було:\n{previous_text}\n\n"
            f"{URL}"
        )
        print("TEXT FOUND:", current_text)
        print("SENDING MESSAGE TO TELEGRAM")

        send_telegram(message)

        print("MESSAGE SENT")

        save_current(current_text)


if __name__ == "__main__":
    asyncio.run(main())
