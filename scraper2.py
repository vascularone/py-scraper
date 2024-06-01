from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import codecs
from webdriver_manager.chrome import ChromeDriverManager
import json
from selenium.webdriver.support.expected_conditions import url_changes
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import random
entries = []    

def scrape_data(url):
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
                    wrapperPrice = item.find_element(By.CSS_SELECTOR, 'span.currency-value').text
                    wrapperIconUrl = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    link = item.find_element(By.CSS_SELECTOR, 'a.img-container.position-relative.animation')
                    time.sleep(random.uniform(1.2, 2.2))
                    if link:
                            driver.execute_script("arguments[0].scrollIntoView();", link) 
                            driver.execute_script("arguments[0].click();", link)

                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.item div.rate.visible')))

                            item_elements = driver.find_elements(By.CSS_SELECTOR, "cw-box-slot cw-item div.item")
                            print('item_elements', len(item_elements))
                            if item_elements:
                                with codecs.open('article_scraping.txt', 'a+', encoding='utf-8') as file:
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
                                                description = description_element.text
                                                other_categories = driver.find_elements(By.CSS_SELECTOR, "div.box.cursor-pointer.ng-star-inserted")
                                                entry = {
                                                        "Box": {
                                                            "Name": wrapperName,
                                                            "Category": wrapperCategory,
                                                            "Price": wrapperPrice,
                                                            "Icon URL": wrapperIconUrl
                                                        },
                                                        "Name": name,
                                                        "Brand": brand,
                                                        "Cost": price,
                                                        "Rate": rate,
                                                        "Outcome": outcome,
                                                        "Image URL": img_src,
                                                        "Description": description,
                                                        "Category": []
                                                }
                                                for category in other_categories:
                                                    category_name = category.find_element(By.CSS_SELECTOR, "div.text.ng-star-inserted").text
                                                    category_element = category.find_element(By.CSS_SELECTOR, "img")
                                                    entry["Category"].append({"name": category_name, "image_url": category_element.get_attribute("src")})
                                                file.write(f"Box: {entry}\n")
                                                entries.append(entry)

                                                close_button = driver.find_element(By.CSS_SELECTOR, "button.mat-focus-indicator.close.mat-icon-button.mat-button-base")
                                                driver.execute_script("arguments[0].click();", close_button)
                                                time.sleep(random.uniform(1, 2))
                                                # driver.back()
                                time.sleep(2)
                                driver.back()
                                wait.until(EC.url_to_be(url))
                                time.sleep(2)
                    index += 1

                    print("done")

                    wait = WebDriverWait(driver, 4)
        else:
            print("url bad")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    urls_to_scrape = [
        "https://www.hypedrop.com/en/boxes/eu/list/",
        "https://www.hypedrop.com/en/boxes/eu/list/hot",
        "https://www.hypedrop.com/en/boxes/eu/list/updated",
        "https://www.hypedrop.com/en/boxes/eu/list/streetwear",
        "https://www.hypedrop.com/en/boxes/eu/list/tech",
        "https://www.hypedrop.com/en/boxes/eu/list/gaming"
    ]

    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scrape_data, url): url for url in urls_to_scrape}

        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()  # get the result of the function
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")

def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def parse_entries(lines):
    entries = []
    current_entry = {}
    for line in lines:
        line = line.strip()
        if line:
            key, value = line.split(': ', 1)
            current_entry[key] = value
        else:
            entries.append(current_entry)
            current_entry = {}
    entries.append(current_entry) 
    return entries

def remove_duplicates(entries):
    unique_entries = []
    seen_names = set()
    for entry in entries:
        name = entry.get('Name')
        if name not in seen_names:
            unique_entries.append(entry)
            seen_names.add(name)
    return unique_entries

def write_to_file(unique_entries, output_file):
    with open(output_file, 'w') as file:
        for entry in unique_entries:
            for key, value in entry.items():
                file.write(f"{key}: {value}\n")
            file.write('\n')

def remove_duplicates_from_file(input_file, output_file):
    lines = read_file(input_file)
    entries = parse_entries(lines)
    unique_entries = remove_duplicates(entries)
    write_to_file(unique_entries, output_file)

input_file = "article_scraping.txt"
output_file = "article_scraping_pure.txt"
remove_duplicates_from_file(input_file, output_file)

def write_to_json_file(unique_entries, output_file):
    with open(output_file, 'w') as file:
        json.dump(unique_entries, file, indent=4)

unique_entries = remove_duplicates(entries)
write_to_json_file(unique_entries, "article_scraping.json")