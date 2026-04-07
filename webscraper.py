from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # run in background
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

BASE_URL = "https://www.buco.co.za/departments/building-materials/structural-steel?p={}"

products = []

def extract_details(name):
    size = None
    length = None
    thickness = None

    size_match = re.search(r'(\d+x\d+(?:x\d+)?\.?\d*)', name)
    if size_match:
        size = size_match.group(1)

    thickness_match = re.search(r'(\d+\.?\d*)mm', name)
    if thickness_match:
        thickness = thickness_match.group(1)

    length_match = re.search(r'(\d+\.?\d*)m', name)
    if length_match:
        length = length_match.group(1)

    return size, thickness, length


for page in range(1, 6):
    url = BASE_URL.format(page)
    print(f"Scraping page {page}...")

    driver.get(url)
    time.sleep(5)  # wait for JS to load

    items = driver.find_elements(By.CLASS_NAME, "product-item")

    print(f"Found {len(items)} items on page {page}")

    for item in items:
        try:
            name = item.find_element(By.CLASS_NAME, "product-item-link").text
        except:
            name = None

        try:
            price = item.find_element(By.CLASS_NAME, "price").text
        except:
            price = None

        if not name:
            continue

        size, thickness, length = extract_details(name)

        products.append({
            "name": name,
            "material": "Steel",
            "size": size,
            "thickness_mm": thickness,
            "length_m": length,
            "price": price
        })

driver.quit()

print(f"\n✅ Total products scraped: {len(products)}")

if len(products) == 0:
    print("❌ Still no data. Website may require login or stronger protection.")
    exit()

# Convert to DataFrame
df = pd.DataFrame(products)

# Clean price safely
if "price" in df.columns:
    df["price"] = df["price"].astype(str).str.replace("R", "", regex=False)
    df["price"] = df["price"].str.replace(",", "", regex=False)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

# Convert numeric fields
df["length_m"] = pd.to_numeric(df["length_m"], errors="coerce")
df["thickness_mm"] = pd.to_numeric(df["thickness_mm"], errors="coerce")

# Price per meter
df["price_per_meter"] = df["price"] / df["length_m"]

# Save
df.to_csv("clean_metal_data.csv", index=False)

print("✅ Done! Data saved.")