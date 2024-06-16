import codecs
import json
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_data(url):
    entries = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        time.sleep(random.uniform(1.2, 2))
        driver.get(url)

        wait.until(EC.url_to_be(url))

        if driver.current_url == url:
            index = 0
            while True:
                time.sleep(random.uniform(1.2, 2))
                box_items = driver.find_elements(By.CSS_SELECTOR, "cw-box-grid-item-ecommerce.ng-star-inserted")
                if index >= len(box_items):
                    print("No more box items to scrape. Exiting the loop.")
                    break

                item = box_items[index]
                print('index', index)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'name')))
                wrapperName = item.find_element(By.CSS_SELECTOR, 'a.name').text
                wrapperCategory = item.find_element(By.CSS_SELECTOR, 'div.category').text
                tags = [{"name": tag.strip()} for tag in wrapperCategory.split(',')]
                wrapperPrice = item.find_element(By.CSS_SELECTOR, 'span.currency-value').text
                wrapperIconUrl = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                link = item.find_element(By.CSS_SELECTOR, 'a.img-container.position-relative.animation')
                box = {
                    "name": wrapperName,
                    "tags": tags,
                    "cost": wrapperPrice,
                    "iconUrl": wrapperIconUrl
                }
                box_slots = []
                time.sleep(random.uniform(1.2, 2.2))
                if link:
                    driver.execute_script("arguments[0].scrollIntoView();", link)
                    driver.execute_script("arguments[0].click();", link)

                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.item div.rate.visible')))

                    item_elements = driver.find_elements(By.CSS_SELECTOR, "cw-box-slot cw-item div.item")
                    print('item_elements', len(item_elements))
                    if item_elements:
                        with codecs.open('ARTICLE.txt', 'a+', encoding='utf-8') as file:
                            for item_element in item_elements:
                                time.sleep(random.uniform(1.5, 2))
                                button = item_element.find_element(By.CSS_SELECTOR, "button.mat-focus-indicator.view-btn.mat-flat-button.mat-button-base")
                                driver.execute_script("arguments[0].click();", button)
                                rate = item_element.find_element(By.CSS_SELECTOR, "div.rate").text
                                name_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.body h2")))
                                brand_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.body div.details")))
                                price_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "mat-dialog-actions cw-pretty-balance.ng-star-inserted span.currency-value")))
                                outcome_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.outcome.ng-star-inserted")))
                                description_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.description.whitespace-pre-wrap")))
                                name = name_element.text
                                img_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.img-container div.item-images img")))
                                img_src = img_element.get_attribute("src")
                                brand = brand_element.text
                                price = price_element.text
                                outcome = outcome_element.text
                                min_outcome = outcome.split('-')[0].strip()
                                max_outcome = outcome.split('-')[1].strip()
                                # Remove all quotes from description
                                description = description_element.text.replace('"', '').replace("'", '')
                                
                                other_categories = driver.find_elements(By.CSS_SELECTOR, "div.box.cursor-pointer.ng-star-inserted")
                                box_slot = {
                                    "rate": rate,
                                    "item": {
                                        "name": name,
                                        "description": description,
                                        "iconUrl": img_src,
                                        "brand": brand,
                                        "category": wrapperCategory,
                                        "price": price,
                                        "displayValue": outcome,
                                        "minDisplayValue": min_outcome,
                                        "maxDisplayValue": max_outcome,
                                        'category': []
                                    }
                                }
                                for category in other_categories:
                                    category_name = category.find_element(By.CSS_SELECTOR, "div.text.ng-star-inserted").text
                                    box_slot["item"]['category'].append({"name": category_name })
                                box_slots.append(box_slot)

                                close_button = driver.find_element(By.CSS_SELECTOR, "button.mat-focus-indicator.close.mat-icon-button.mat-button-base")
                                driver.execute_script("arguments[0].click();", close_button)
                                time.sleep(random.uniform(1, 2))

                            entry = {
                                "Box": box,
                                "BoxSlots": box_slots
                            }
                            # Write entry to file, remove single quotes
                            file.write(json.dumps(entry).replace("'", "") + "\n")
                            entries.append(entry)
                        time.sleep(2)
                        driver.back()
                        wait.until(EC.url_to_be(url))
                        time.sleep(2)
                index += 1

                print("done")

                js_script = open('loadmore.js', 'r').read()
                load_more_clicked = driver.execute_script(js_script)
                if not load_more_clicked:
                    break

                wait = WebDriverWait(driver, 4)
        else:
            print("url bad")
            return entries
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()
    return entries

urls_to_scrape = [
    "https://www.hypedrop.com/en/boxes/eu/list/",
    "https://www.hypedrop.com/en/boxes/eu/list/hot",
    "https://www.hypedrop.com/en/boxes/eu/list/updated",
    "https://www.hypedrop.com/en/boxes/eu/list/streetwear",
    "https://www.hypedrop.com/en/boxes/eu/list/tech",
    "https://www.hypedrop.com/en/boxes/eu/list/gaming"
]

for url in urls_to_scrape:
    scrape_data(url)
