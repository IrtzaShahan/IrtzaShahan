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
