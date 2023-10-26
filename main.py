import config as _

import json
import time
import random

import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from loguru import logger

email = 'kavyaaggarwal20030000@gmail.com'
password = 'kavya2003'


def main():
    try:
        with open('backup.json', 'r') as f:
            data = json.load(f)
    except:
        data = {
            'Name': [],
            'Code EAN': [],
            'price_colis': [],
            'price_demi_palette': [],
            'price_palette': [],
            'unit_price_colis': [],
            'unit_price_demi_palette': [],
            'unit_price_palette': [],
            'num_uvc_colis': [],
            'num_uvc_demi_palette': [],
            'num_uvc_palette': [],
            'DLC': []
        }


    try:
        with open('visited.json', 'r') as f:
            visited = json.load(f)
    except:
        visited = []

    try:
        with open('product_urls.json', 'r') as f:
            product_urls = json.load(f)
    except:
        product_urls = []
    
    driver = Driver(
        uc=False
    )
    driver.implicitly_wait(10)

    logger.info('Starting scrape.')

    logger.info('Scraping product urls.')

    if not product_urls:
        for page_num in range(1, 95):
            driver.get(f'https://www.miamland.com/grossiste-epicerie-sucree/81?page={page_num}')
            urls = list(map(lambda a: a.get_attribute('href'), driver.find_elements(By.CSS_SELECTOR, '.product-image a')))
            logger.debug(f'Page {page_num}, {len(urls)} product urls found.')
            product_urls += urls

        with open('product_urls.json', 'w') as f:
            json.dump(product_urls, f, indent=4)

    logger.info('Logging in...')
    driver.get('https://www.miamland.com/login')
    driver.find_element(By.CSS_SELECTOR, '#email').send_keys(email)
    time.sleep(0.25)
    driver.find_element(By.CSS_SELECTOR, '#pass').send_keys(password)
    time.sleep(0.25)
    driver.find_element(By.CSS_SELECTOR, '#send2').click()
    logger.info('Logged in successfully.')

    logger.info(f'Total products to scrape: {len(product_urls)}')
    logger.info(f'Scraped already: {len(visited)}')
    
    for url in product_urls:

        if url in visited:
            continue
        
        driver.get(url)
        title = driver.find_elements(By.TAG_NAME, 'h2')[1].text
        code_ean = driver.find_elements(By.TAG_NAME, 'h2')[2].text

        try:
            table = driver.find_element(By.CSS_SELECTOR, '.price-box table')
        
            prices = table.find_elements(By.TAG_NAME, 'h3')
            prices = list(map(lambda h3: h3.text, prices))
            price_colis = prices[0]
            price_demi_palette = prices[1]
            price_palette = prices[2]

            unit_prices = uvcs = list(filter(lambda sp: 'unit' in sp.text, table.find_elements(By.TAG_NAME, 'span')))
            unit_prices = list(map(lambda sp: sp.text, unit_prices))
            unit_prices = list(map(lambda txt: f'{txt.split(" ")[1]} {txt.split(" ")[2]}', unit_prices))
            unit_price_colis = unit_prices[0]
            unit_price_demi_palette = unit_prices[1]
            unit_price_palette = unit_prices[2]

            uvcs = list(filter(lambda sp: 'uvc' in sp.text, table.find_elements(By.TAG_NAME, 'span')))
            uvcs = list(map(lambda sp: sp.text, uvcs))
            uvcs = list(map(lambda txt: txt.split(' ')[-2], uvcs))
            uvc_colis = uvcs[0]
            uvc_demi_palette = uvcs[1]
            uvc_palette = uvcs[2]
        except:
            price_colis = price_demi_palette = price_palette = unit_price_colis = unit_price_demi_palette = unit_price_palette = uvc_colis = uvc_demi_palette = uvc_palette = 'N/A'
        
        dlc = list(filter(lambda p: 'dlc' in p.text.lower(), driver.find_elements(By.CSS_SELECTOR, '.product-info-list p')))
        dlc = f"{dlc[0].text.split(' ')[-2]} {dlc[0].text.split(' ')[-1]}" if len(dlc) > 0 else 'N/A'

        data['Name'].append(title)
        data['Code EAN'].append(code_ean)
        data['price_colis'].append(price_colis)
        data['price_demi_palette'].append(price_demi_palette)
        data['price_palette'].append(price_palette)
        data['unit_price_colis'].append(unit_price_colis)
        data['unit_price_demi_palette'].append(unit_price_demi_palette)
        data['unit_price_palette'].append(unit_price_palette)
        data['num_uvc_colis'].append(uvc_colis)
        data['num_uvc_demi_palette'].append(uvc_demi_palette)
        data['num_uvc_palette'].append(uvc_palette)
        data['DLC'].append(dlc)

        visited.append(url)

        with open('backup.json', 'w') as f:
            json.dump(data, f, indent=4)

        with open('visited.json', 'w') as f:
            json.dump(visited, f, indent=4)

        df = pd.DataFrame(data=data)
        df.to_csv('output.csv')

        logger.debug(f'Scraped url -> {url}')

    logger.info('Scrape complete!')

if __name__ == '__main__':
    main()