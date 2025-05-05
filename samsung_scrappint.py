import requests
from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_jumia_samsung_prices():
    print("🔎 Scraping Jumia...")
    url = 'https://www.jumia.co.ke/mobile-phones/samsung/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    for item in soup.select('article.prd'):
        name = item.select_one('h3.name')
        price = item.select_one('div.prc')
        if name and price:
            products.append({
                'Product Name': name.text.strip(),
                'Price': price.text.strip(),
                'Source': 'Jumia'
            })
    return products


def get_kilimall_samsung_prices():
    print("🔎 Scraping Kilimall...")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Enable for background runs

    driver = None
    soup = None

    try:
        driver = uc.Chrome(options=options)
        driver.get("https://www.kilimall.co.ke/search?q=samsung")

        # Scroll to trigger lazy-loaded content
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "goods-card"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

    except Exception as e:
        print("❌ Error scraping Kilimall:", e)
        return []

    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except OSError as quit_err:
                print("⚠️ Suppressed OSError while quitting browser:", quit_err)
            except Exception as other_err:
                print("⚠️ Suppressed error while quitting browser:", other_err)

    products = []
    if soup:
        for item in soup.select("div.goods-card"):
            name = item.select_one("div.title.ellipsis-2") or item.select_one("p.title")
            price = item.select_one("div.price")
            if name and price:
                products.append({
                    'Product Name': name.text.strip(),
                    'Price': price.text.strip(),
                    'Source': 'Kilimall'
                })

    return products


def get_mophones_samsung_prices():
    print("🔎 Scraping Mophones...")
    url = 'https://mophone.co.ke/collections/samsung'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    for item in soup.select('div.grid-product'):
        name = item.select_one('div.grid-product__title')
        price = item.select_one('span.grid-product__price--new') or item.select_one('span.grid-product__price')
        if name and price:
            products.append({
                'Product Name': name.text.strip(),
                'Price': price.text.strip(),
                'Source': 'Mophones'
            })
    return products


def compare_and_export_to_excel():
    jumia_products = get_jumia_samsung_prices()
    kilimall_products = get_kilimall_samsung_prices()
    mophones_products = get_mophones_samsung_prices()

    all_products = jumia_products + kilimall_products + mophones_products

    if not all_products:
        print("⚠️ No products fetched. Check network or site structure.")
        return

    df = pd.DataFrame(all_products)
    filename = 'Samsung_Price_Comparison.xlsx'
    df.to_excel(filename, index=False)
    print(f"✅ Excel file exported: {filename}")


if __name__ == '__main__':
    compare_and_export_to_excel()
