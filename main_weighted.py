from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re  # For better cleaning of the price string
from helper import read_weighted_keywords, read_search_terms
import os

# --- Setup ---
search_terms = read_search_terms('SearchTerms.csv')

keywords_file_path = "data/WeightedKeywords.csv"

opera_path = r"C:\Users\Jereme\AppData\Local\Programs\Opera GX\opera.exe"

chrome_driver = r"C:\Users\Jereme\AppData\Local\Programs\Opera GX\chromedriver\chromedriver.exe"

chrome_options = Options()
chrome_options.binary_location = opera_path
#chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0")
chrome_options.add_argument("--log-level=3")  # Suppress logs: INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3
chrome_options.add_argument("--no-first-run")
service = Service(executable_path=chrome_driver)
driver = webdriver.Chrome(service=service, options=chrome_options)

for search_term in search_terms:
    print(f"\n🔍 Searching: {search_term}")
    url = f"https://www.carousell.sg/search/{search_term}?sort_by=5"
    # Replace with path to your chromedriver if needed
    driver.get(url)

    time.sleep(2)

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if search_term in driver.current_url:
            print(f"✅ Switched to tab: {driver.current_url}")
            break
    else:
        print("❌ Could not find a tab with the search term.")
        
        
    wait = WebDriverWait(driver, 10)


    # CLEARS THE POP UP THAT APPEARS
    try:
        # First "Next" button
        next_button1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="D_pp" and text()="Next"]')))
        next_button1.click()
        print("Clicked first Next")

        # Second "Next" button
        next_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="D_pp" and text()="Next"]')))
        next_button2.click()
        print("Clicked second Next")

        # "Continue Shopping" button
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="D_pp" and text()="Continue browsing"]')))
        continue_button.click()
        print("Clicked Continue Shopping")
        #Scroll back up
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        print("Scrolled to the Top!")
    except Exception as e:
        print("❌ Popup not handled properly:")   
        
        

    # --- Scroll down to load more results ---
    max_scrolls = 10  # Safety limit
    scroll_increment = 400  # Scroll by 800px at a time

    for _ in range(max_scrolls):
        try:
            # Explicit wait for "Show more results" button to become clickable
            show_more = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Show more results']"))
            )

            # Scroll by a small increment instead of jumping to the bottom
            driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(1)  # Give the page time to load

            # Try clicking the "Show more results" button if it appears
            if show_more.is_displayed():
                show_more.click()
                print("Clicked 'Show more results'...")

            else:
                print("Button not visible yet.")

            time.sleep(2)  # Wait for new results to load

        except Exception as e:
            print(f"❌ Error: Unable to show more results")
            break


    # --- Keywords for identifying suspicious/exotic products




    # # --- Extract Listings ---
    items = driver.find_elements(By.XPATH, '//div[starts-with(@data-testid, "listing-card-")]')

    print(f"\nFound {len(items)} listings for '{search_term}':\n")



    # --- Scroll down to load more results ---
    scrolls = 3  # How many times to scroll
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # --- Keywords for identifying suspicious/exotic products
    keyword_weights = read_weighted_keywords(keywords_file_path)


    debugMode = True
    # --- Loop through listings and print out data ---
    for index, item in enumerate(items, start=1):
        try:
            first_div = item.find_element(By.TAG_NAME, 'div')

            # Step 2: Get all <a> tags within that first <div>
            a_tags = first_div.find_elements(By.TAG_NAME, 'a')

            if len(a_tags) < 2:
                print(f"[{index}] Skipped: Less than 2 <a> tags found")
                continue

            # Step 3: Access the second <a> tag
            second_a = a_tags[1]

            # Step 4: Get the two <div> tags inside that <a>
            inner_divs = second_a.find_elements(By.TAG_NAME, 'div')

            if len(inner_divs) < 2:
                print(f"[{index}] Skipped: Less than 2 <div> tags in second <a>")
                continue

            # Extract title and price
            title = inner_divs[0].text.strip()
            price = inner_divs[1].text.strip()
            
            # Clean the price and convert to a numeric value (assuming the price format is in any currency)
            price_cleaned = re.sub(r'[^\d.]', '', price)  # Remove all non-numeric characters except dots (.)
            price_numeric = float(price_cleaned) if price_cleaned else 0.0

            # Extract link
            link = item.find_element(By.TAG_NAME, 'a').get_attribute("href")  # Extract the link from <a> inside div
            
            score = 1
            for keyword, weight in keyword_weights.items():
                if keyword in title.lower():
                    score *= weight        

            # Debug prints, turn on / off using debugMode
            if debugMode:
                print(f"Listing {index}:\n  Title: {title}\n  Price: {price} | Cleaned Price: {price_numeric}\n  Link: {link}\n")
                if price_numeric > 80:
                    print(f"Debug: Price {price_numeric} is above 80.")
                else:
                    print(f"Debug: Price {price_numeric} is NOT above 80.")

                if any(keyword.lower() in title.lower() for keyword in illegal_keywords):
                    print(f"Debug: Found illegal keyword in title.")
                else:
                    print(f"Debug: No illegal keyword found in title.")
            
            if price_numeric > 80 and score >= 4:  # You can tweak this threshold
                print(f"🚨 Flagged (score {score}): {title} | {price}\n  {link}\n")
        
        except Exception as e:
            print(f"❌ Error with listing {index}: {e}")
            continue

        
    time.sleep(5)
driver.quit()