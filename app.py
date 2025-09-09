import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://www.decolar.com/pacotes/"

def scrape_pacotes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        ))

        page = context.new_page()

        page.goto(url, wait_until="networkidle")

        time.sleep(10)

        try:
            page.wait_for_selector("div[data-testid='offer-card']", timeout=60000, state="visible")
        except:
            print("⛔ Não foi possível encontrar os pacotes na página.")
            browser.close()
            return []

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        pacotes = []
        for card in soup.select("div[data-testid='offer-card']"):
            destino = card.select_one("h3")
            destino = destino.get_text(strip=True) if destino else "Destino"
            
            preco = card.select_one("span.amount")
            preco = preco.get_text(strip=True) if preco else "N/A"
            
            img = card.select_one("img")
            img = img["src"] if img else ""
            
            link = card.select_one("a")
            link = link["href"] if link else "#"
            
            pacotes.append({
                "destino": destino,
                "preco": preco.replace("R$", "").replace(".", "").strip(),
                "imagem": img,
                "descricao": "Pacote extraído automaticamente da Decolar",
                "link": "https://www.decolar.com" + link,
                "dataInicio": "2025-09-30",
                "dataFim": "2025-10-05",
                "dias": 5
            })
        
        browser.close()
        return pacotes

if __name__ == "__main__":
    pacotes = scrape_pacotes()
    if pacotes:
        with open("pacotes.json", "w", encoding="utf-8") as f:
            json.dump(pacotes, f, ensure_ascii=False, indent=4)
        print("✅ pacotes.json atualizado com", len(pacotes), "pacotes")
    else:
        print("⚠️ Nenhum pacote encontrado.")
