from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  # Added import
from webdriver_manager.chrome import ChromeDriverManager
import time
from random import randint
import piexif
from PIL import Image
from datetime import datetime

def update_image_datetime_to_now(image_path):
    # Format current datetime as EXIF string: "YYYY:MM:DD HH:MM:SS"
    now_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    
    try:
        exif_dict = piexif.load(image_path)
    except Exception:
        # Create a minimal EXIF structure if none exists
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "Interop":{}, "1st":{}, "thumbnail": None}

    # Update the necessary EXIF tags
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = now_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = now_str.encode("utf-8")
    exif_dict["0th"][piexif.ImageIFD.DateTime] = now_str.encode("utf-8")
    
    # Dump and save back the new EXIF data into the image
    exif_bytes = piexif.dump(exif_dict)
    img = Image.open(image_path)
    img.save(image_path, exif=exif_bytes)

def setup_browser():
    chrome_options = webdriver.ChromeOptions()
    
    # Mobile emulation configuration
    mobile_emulation = {
        "deviceMetrics": {"width": 412, "height": 915, "pixelRatio": 3.5},
        "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--auto-open-devtools-for-tabs")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def login(driver, username, password):
    try:
        # Wait for login elements
        wait = WebDriverWait(driver, 20)
        # Locate username field by checking for a text input or common username attribute
        username_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@class, 'mantine-Input-input') and contains(@class, 'mantine-TextInput-input')]")
            )
        )
        username_field.send_keys(USERNAME)
        
        # Locate password field by checking for a password input or a common password attribute
        password_field = wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//input[contains(@class, 'm_f2d85dd2') and contains(@class, 'mantine-PasswordInput-innerInput')]"
            ))
        )
        password_field.send_keys(PASSWORD)
    
        password_field.send_keys(Keys.ENTER)    
        return True
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def select_first_option(driver):
    wait = WebDriverWait(driver, 10)
    # Click the dropdown to expand options
    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@class, 'm_8fb7ebe7 mantine-Input-input mantine-Select-input')]")
        )
    )
    dropdown.click()

    # Select the first option
    first_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@role='option'][1]")
        )
    )
    first_option.click()

def get_latest_image(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)
    
    # Filter for image files (add more extensions if needed)
    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [
        f for f in files
        if f.lower().endswith(image_extensions) and os.path.isfile(os.path.join(folder_path, f))
    ]
    
    if not image_files:
        raise FileNotFoundError("No image files found in the directory")
    
    # Sort images by modification time (oldest to newest)
    sorted_images = sorted(
        image_files,
        key=lambda x: os.path.getmtime(os.path.join(folder_path, x))
    )
    return os.path.join(folder_path, sorted_images[-1])

def capture_and_upload_photo(driver, file_path):
    # Wait for file input and send file path
    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(file_path)

def click_submit(driver):
    wait = WebDriverWait(driver, 10)
    # Click the dropdown to expand options
    submit_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )
    )
    submit_button.click()

if __name__ == "__main__":
    # Configuration
    LOGIN_URL = "https://www.patrolx.ca"
    USERNAME = "irtza"
    PASSWORD = "Group1234@"

    # Initialize browser
    driver = setup_browser()
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)
    # Perform login
    if login(driver, USERNAME, PASSWORD):
        print("Login successful!")
    else:
        print("Login failed")
    time.sleep(5)

    site_url = "https://patrolx.ca/reporting/5828%20GRANVILLE%20ST%20VANCOUVER"
    driver.get(site_url)
    time.sleep(5)

    select_first_option(driver)
    time.sleep(10)
    

    folder_path = r"C:\Users\Irtza\OneDrive\Documents\Python Scripts\fun projects\group_security_automation\combined_output\set_1"
    try:
        # Get all image files sorted by modification time (oldest first)
        image_files = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) 
            and os.path.isfile(os.path.join(folder_path, f))
        ]
        image_files.sort(key=lambda x: os.path.getmtime(x))

        # Process all images in sequence
        for image_path in image_files:
            image_name = os.path.basename(image_path)
            try:
                # Upload the image
                update_image_datetime_to_now(image_path)
                capture_and_upload_photo(driver, image_path)
                print(f"{datetime.now().strftime('%H:%M:%S')} Uploaded '{image_name}'")
            
                # Short pause before deletion
                time.sleep(5) 
                click_submit(driver)
                
                # Delete the uploaded file
                try:
                    os.remove(image_path)
                    print(f"{datetime.now().strftime('%H:%M:%S')} Deleted '{image_name}'")
                except Exception as e:
                    print(f"{datetime.now().strftime('%H:%M:%S')} Deletion failed: {str(e)}")

            except Exception as e:
                print(f"{datetime.now().strftime('%H:%M:%S')} Failed to process '{image_name}': {str(e)}")
                continue  # Continue to next image even if one fails
            time.sleep(randint(10,80))

    except FileNotFoundError as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} Folder error: {str(e)}")
    except Exception as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} Critical error: {str(e)}")
    # finally:
        # input("Press Enter to exit...")
