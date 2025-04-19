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
# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def stamp_and_rename(img_path):
    """Update EXIF to now and rename to PXL_YYYYMMDD_HHMMSSmmm.jpg"""
    now  = datetime.now()
    exif_fmt = now.strftime("%Y:%m:%d %H:%M:%S")
    new_fname = f"PXL_{now.strftime('%Y%m%d_%H%M%S')}{now.microsecond//1000:03d}.jpg"
    new_path  = os.path.join(os.path.dirname(img_path), new_fname)

    # ----- EXIF -----
    try:
        exif = piexif.load(img_path)
    except Exception:
        exif = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    exif["0th"][piexif.ImageIFD.DateTime] = exif_fmt.encode()
    exif["Exif"][piexif.ExifIFD.DateTimeOriginal]  = exif_fmt.encode()
    exif["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_fmt.encode()

    Image.open(img_path).save(img_path, exif=piexif.dump(exif))
    os.rename(img_path, new_path)
    return new_path                           # ← use this for upload


def capture_and_upload_photo(driver, file_path):
    wait = WebDriverWait(driver, 10)
    file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    file_input.send_keys(file_path)


# ------------------------------------------------------------------
# main loop – 10 folders, 60‑minute spacing
# ------------------------------------------------------------------
if __name__ == "__main__":
    LOGIN_URL = "https://www.patrolx.ca"
    USERNAME  = "irtza"
    PASSWORD  = "Group1234@"

    driver = setup_browser()
    driver.get(LOGIN_URL)
    if not login(driver, USERNAME, PASSWORD):
        raise SystemExit("Login failed")

    base_folder = r"C:\Users\Irtza\OneDrive\Documents\Python Scripts\fun projects\group_security_automation\combined_output"

    for idx in range(1, 11):                                # set_1 … set_10
        folder_path = os.path.join(base_folder, f"set_{idx}")
        print(f"\n=== Processing {folder_path} ===")

        driver.get("https://patrolx.ca/reporting/5828%20GRANVILLE%20ST%20VANCOUVER")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        select_first_option(driver)

        # ------- upload every image in the folder -------
        images = sorted(
            [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
            key=os.path.getmtime
        )
        for img in images:
            try:
                new_img = stamp_and_rename(img)             # EXIF + rename
                capture_and_upload_photo(driver, new_img)
                click_submit(driver)
                os.remove(new_img)
                print(f"{datetime.now():%H:%M:%S}  Uploaded & deleted {os.path.basename(new_img)}")
                time.sleep(randint(10, 80))                 # natural delay
            except Exception as e:
                print(f"{datetime.now():%H:%M:%S}  ERROR {e}")

        # ------- wait 60 minutes before next folder -------
        if idx < 10:
            print(f"Waiting 60 min for next folder …")
            time.sleep(60 * 60)

    driver.quit()
