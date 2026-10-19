import asyncio
from playwright.async_api import async_playwright
import  pandas as pd

def clean_repos(repos: list[dict]) -> list[dict]:
    """ Normalize raw scraped data into a consistent, analyst-ready shape."""
    cleaned = []
    
    for r in repos:
        # 'morluto / rea' --> 'morluto/rea'
        name = (r["name"] or "").replace(" ","")

        # "225,233" -> 225223
        stars = int(r['stars'].replace(",", "")) if r["stars"] else None
        
        description = r["description"] or ""

        # "41,187 stars today" --> 41187
        if r["stars_today"]:
            stars_today = int(
                r["stars_today"].replace(",", "").replace("stars today", "").strip()
        )
        else:
            stars_today = None

        # None --> "Unknown"
        language = r['language'] or "Unknown"

        cleaned.append({
            "name": name,
            "urls": r['url'],
            "description": description,
            "language": language,
            "star": stars,
            "stars_today": stars_today,
            })
    return cleaned

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        print("opening Github Trending...")
        await page.goto("https://github.com/trending", wait_until="domcontentloaded")

        # wait for at least one repo card to appear
        await page.wait_for_selector("article.Box-row", timeout=10_000)
        await page.wait_for_timeout(1500)   # let the rest render

        # DEBUG: how many cards does the browser really see?
        count = await page.eval_on_selector_all(
                    "article.Box-row", "elements => elements.length"
            )
        print(f"DEBUG: browser sees {count} cards")
        print("Page Loaded. Extracting repos...")


        # find all repo cards
        cards = await page.query_selector_all('article.Box-row')
        print(f"Found {len(cards)} repos.\n")

        repos = []

        for card in cards:
            # for each field, try to find its element. If missing, Use None.
            name_el = await card.query_selector("h2 a")
            desc_el = await card.query_selector("p.col-9")
            lang_el = await card.query_selector('span[itemprop="programmingLanguage"]')
            stars_el = await card.query_selector('a[href$="/stargazers"]')
            today_el = await card.query_selector("span.float-sm-right")

            repos.append({
            "name": (await name_el.inner_text()).strip() if name_el else None,
            "url": f"https://github.com{await name_el.get_attribute('href')}" if name_el else None,
            "description": (await desc_el.inner_text()).strip() if desc_el else None,
            "language" : (await lang_el.inner_text()).strip() if lang_el else None,
            "stars": (await stars_el.inner_text()).strip() if stars_el else None,
            "stars_today" : (await today_el.inner_text()).strip() if today_el else None
             })

        await browser.close()   
    
        # Clean raw data before saving
        cleaned = clean_repos(repos)

        df = pd.DataFrame(cleaned)

        df.to_csv("trending.csv", index=False)
        
        preview = df.copy()
        preview['description'] = preview['description'].str.slice(0, 50) + "..."
        print(preview.to_string(index=False))

        print(f"saved {len(repos)} repos to trending.csv\n")
        

asyncio.run(main())

