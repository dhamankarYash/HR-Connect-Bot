import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load your data
df = pd.read_csv("contacts.csv")  # Make sure 'LinkedInProfile' column exists

# Configure Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)  # Keeps browser open
service = Service()

driver = webdriver.Chrome(service=service, options=chrome_options)

# Log in to LinkedIn manually first
driver.get("https://www.linkedin.com/login")
input("🔐 Press Enter after logging in...")

# Function to try sending connection request
def try_to_connect(driver, name):
    try:
        # Direct "Connect" button
        connect_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Connect"]'))
        )
        connect_button.click()
        print(f"✅ Sent connection request to {name} via direct button.")
        return
    except (TimeoutException, NoSuchElementException):
        pass

    try:
        # Fallback: "More" button > "Connect"
        more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "More actions")]'))
        )
        more_button.click()
        time.sleep(1)
        connect_option = driver.find_element(By.XPATH, '//span[text()="Connect"]/ancestor::button')
        connect_option.click()
        print(f"✅ Sent connection request to {name} via More > Connect.")
    except Exception as e:
        print(f"⚠️ Could not connect with {name}: {e}")

# Iterate through each row in the CSV
for index, row in df.iterrows():
    try:
        name = row['Name']
        profile_url = row['LinkedInProfile']
        print(f"\n➡️ Opening profile: {name} - {profile_url}")
        driver.get(profile_url)
        time.sleep(5)
        driver.execute_script("window.scrollBy(0, 300);")  # Scroll a bit to load buttons
        try_to_connect(driver, name)
        time.sleep(3)
    except KeyError:
        print("❌ Missing 'LinkedInProfile' column in your CSV.")
        break
    except Exception as e:
        print(f"❌ Unexpected error with {name}: {e}")
        continue
        
driver.quit()
