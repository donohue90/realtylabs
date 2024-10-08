from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

SEARCH_URL = "https://taxrecords-nj.com/pub/cgi/prc6.cgi?&ms_user=ctb02&passwd=&district=0200&srch_type=0&out_type=0&adv=1"
RESULTS_URL = "https://taxrecords-nj.com/pub/cgi/inf.cgi"

def scrape_property_data(block, lot, qualifier, location):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Error setting up Chrome driver: {str(e)}")
        return []

    try:
        driver.get(SEARCH_URL)
        print(f"Accessed URL: {SEARCH_URL}")

        # Fill out the form
        driver.find_element(By.NAME, "block").send_keys(block)
        driver.find_element(By.NAME, "lot").send_keys(lot)
        driver.find_element(By.NAME, "qual").send_keys(qualifier)
        driver.find_element(By.NAME, "location").send_keys(location)
        print("Form filled out")

        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        print("Form submitted")

        # Wait for the results table to load
        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table[cellpadding='1'][cellspacing='1'][width='100%']"))
            )
            print("Results table found")
        except Exception as e:
            print(f"Error waiting for results table: {str(e)}")
            print("Current URL:", driver.current_url)
            print("Page source:")
            print(driver.page_source[:1000])  # Print first 1000 characters of page source
            return []

        # Extract the data
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row

        properties = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 8:
                property_data = {
                    'Block': cells[0].text.strip(),
                    'Lot': cells[1].text.strip(),
                    'Qual': cells[2].text.strip(),
                    'Location': cells[3].text.strip(),
                    'Owner': cells[4].text.strip(),
                    'Land Value': cells[5].text.strip(),
                    'Improvement Value': cells[6].text.strip(),
                    'Total Value': cells[7].text.strip()
                }
                properties.append(property_data)

        print(f"Found {len(properties)} properties")
        return properties

    except Exception as e:
        print(f"An error occurred while fetching data: {str(e)}")
        print("Current URL:", driver.current_url)
        print("Page source:")
        print(driver.page_source[:1000])  # Print first 1000 characters of page source
        return []

    finally:
        driver.quit()

if __name__ == "__main__":
    block = input("Block (leave blank if not applicable): ").strip()
    lot = input("Lot (leave blank if not applicable): ").strip()
    qualifier = input("Qualifier (leave blank if not applicable): ").strip()
    location = input("Location: ").strip()

    print(f"\nSearching with parameters: block={block}, lot={lot}, qualifier={qualifier}, location={location}")
    properties = scrape_property_data(block, lot, qualifier, location)
    
    if properties:
        print(f"Found {len(properties)} properties:")
        for i, prop in enumerate(properties, 1):
            print(f"\nProperty {i}:")
            for key, value in prop.items():
                print(f"{key}: {value}")
    else:
        print("No properties found for these parameters.")