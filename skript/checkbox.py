import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import json
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import os

load_dotenv()
imei_array = []

with open('imei.txt', 'r') as imei_file:
    for line in imei_file:
        imei = line.strip()  # Entfernt Leerzeichen und Zeilenumbrüche
        imei_array.append(imei)

for imei in imei_array:
    while True:
        try:
            print(imei)
            process = subprocess.Popen(['python', 'mailSwipe.py'])

            # Create a new Chrome browser instance
            driver = webdriver.Chrome()

            driver.implicitly_wait(10)

            url = "https://al-support.apple.com/#/additional-support"
            driver.get(url)
            print("Opened the URL")

            # Find the checkbox element by ID
            checkbox = driver.find_element("id", "0")
            # Scroll to the checkbox element
            driver.execute_script("arguments[0].scrollIntoView();", checkbox)
            print("Scrolled to the checkbox")

            # Click the checkbox using JavaScript
            driver.execute_script("arguments[0].click();", checkbox)
            print("Clicked the checkbox")

            # Find the div containing the "Continue" button
            continue_div = driver.find_element("class name", "continue-button")

            # Locate the "Continue" button within the div and click it
            continue_button = continue_div.find_element("tag name", "button")
            continue_button.click()
            print("Clicked the 'Continue' button")

            # Load data from email.json
            with open("email.json", "r") as email_file:
                email_data = json.load(email_file)

            # Fill Email Address Field
            email_input = driver.find_element("id", "email")
            email_input.send_keys(email_data["email"])
            print("Filled email address")

            # Fill Serial Number Field
            serial_input = driver.find_element("id", "serial")
            serial_input.send_keys(imei)
            print("Filled serial number")

            image_element = driver.find_element(
                "css selector", "div.code_img_wrapper img")
            image_width = image_element.size["width"]
            image_height = image_element.size["height"]
            image_screenshot = image_element.screenshot_as_png

            with open("image.png", "wb") as image_file:
                image_file.write(image_screenshot)

            print("Image screenshot captured and saved")

            time.sleep(2)

            print(os.getenv('TwoCaptcha'))
            solver = TwoCaptcha(os.getenv('TwoCaptcha'))
            id = solver.send(file='image.png')
            time.sleep(30)

            code = solver.get_result(id)

            code_input = driver.find_element("id", "code_input")
            code_input.send_keys(code)

            time.sleep(2)

            continue_button = driver.find_element(
                By.XPATH, "//button[contains(., 'Continue')]")
            continue_button.click()

            global_urls = []

            class MyHandler(FileSystemEventHandler):
                def __init__(self, observer):
                    self.observer = observer

                def on_modified(self, event):
                    if event.src_path.endswith('.txt'):
                        print(f"Datei {event.src_path} wurde geändert.")

                        # Suche den ersten Link in der geänderten Datei
                        first_link = find_first_link(event.src_path)
                        if first_link:
                            print(f"Erster gefundener Link: {first_link}")
                            delete_file(event.src_path)  # Lösche die Datei
                            self.observer.stop()  # Stoppe den Observer
                        else:
                            print("Keine Links in der Datei gefunden.")

            def find_first_link(file_path):
                global global_urls

                with open(file_path, 'r') as file:
                    content = file.read()
                    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                    urls = re.findall(url_pattern, content)

                    if urls:
                        global_urls.extend(urls)
                        return urls[0]
                    else:
                        return None

            def delete_file(file_path):
                try:
                    os.remove(file_path)
                    print(f"Datei {file_path} wurde gelöscht.")
                except Exception as e:
                    print(f"Fehler beim Löschen der Datei {file_path}: {e}")

            if __name__ == "__main__":
                folder_to_watch = "all_mails"  # Ersetze durch den Pfad deines Ordners
                observer = Observer()
                event_handler = MyHandler(observer)
                observer.schedule(
                    event_handler, folder_to_watch, recursive=False)
                observer.start()

                try:
                    while observer.is_alive():
                        time.sleep(1)
                except KeyboardInterrupt:
                    observer.stop()
                observer.join()
                print("Programm beendet")

            # Open the website
            driver.get(global_urls[0])

            time.sleep(2)

            button_div = driver.find_element(By.CLASS_NAME, "btn-group")
            buttons = button_div.find_elements(By.TAG_NAME, "button")

            for button in buttons:
                if "Continue" in button.text:
                    button.click()
                    print("Clicked the 'Continue' button")
                    break

            time.sleep(5)
            process.terminate()
            # Baue den API-Link mit der IMEI
            api_key = os.getenv('sickw')
            service = "30"
            api_url = f"https://sickw.com/api.php?format=HTML&key={api_key}&imei={imei}&service={service}"

            new_tab_script = "window.open('https://sickw.com/api.php?format=HTML&key={}&imei={}&service={}', '_blank');"
            new_tab_script = new_tab_script.format(api_key, imei, service)
            driver.execute_script(new_tab_script)
            driver.switch_to.window(driver.window_handles[1])
            # Wartezeit, um sicherzustellen, dass die Seite geladen wurde
            time.sleep(20)

            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'swip_screens')
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)

            driver.save_screenshot('swip_screens/' + imei + '.png')
            screenshot_path = os.path.join(final_directory, imei + '.png')

            time.sleep(2)
            body_content = driver.page_source
            start_index = body_content.find(
                "Estimated Purchase Date:") + len("Estimated Purchase Date:")
            end_index = body_content.find("iCloud Lock:")
            estimated_purchase_date = body_content[start_index:end_index].strip().replace(
                "<br>", "")

            print("Estimated Purchase Date:", estimated_purchase_date)

            driver.switch_to.window(driver.window_handles[0])

            print("Estimated Purchase Date:", estimated_purchase_date)
            input_field = driver.find_element(By.ID, "Q209907")
            input_field.send_keys("Helmut")
            time.sleep(2)
            last_name_input = driver.find_element(By.ID, "Q209909")
            last_name_input.send_keys("Gottschalk")
            time.sleep(2)
            date_input = driver.find_element(By.NAME, "Q205897")
            date_input.send_keys(estimated_purchase_date)
            time.sleep(2)
            input_element = driver.find_element(By.ID, "Q205899")
            input_element.send_keys("Vodafone")
            time.sleep(2)
            input_element = driver.find_element(By.ID, "Q221896")
            input_element.send_keys("Wittener Str. 21")
            time.sleep(2)
            input_element = driver.find_element(By.ID, "Q221898")
            input_element.send_keys("Castrop-Rauxel")
            time.sleep(2)
            input_element = driver.find_element(By.ID, "Q221899")
            input_element.send_keys("Nordrhein")
            time.sleep(2)
            input_element = driver.find_element(By.ID, "Q221900")
            input_element.send_keys("44575")
            time.sleep(2)
            textarea_element = driver.find_element(By.ID, "textarea-Q235245")
            textarea_element.send_keys(
                "bought from ebay, icloud status clean, please help me i wanna use apple")
            time.sleep(5)
            file_input_element = driver.find_element(By.ID, "files")
            file_input_element.send_keys(screenshot_path)

            time.sleep(5)
            continue_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, "customer-form__continue_btn"))
            )

            # Klicken Sie auf den "Continue"-Button
            continue_button.click()

            time.sleep(5)
            edit_info_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(., 'Continue')]"))
            )
            edit_info_button.click()

            time.sleep(8)
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'all_screens')
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)

            driver.save_screenshot('all_screens/' + imei + '.png')
            time.sleep(3)

            driver.quit()
            break
        except Exception as e:
            print(f"Fehler bei IMEI {imei}: {e}")
            # Führe hier Schritte aus, um den Fehler zu behandeln
            # Zum Beispiel: driver.refresh()
            # Du kannst hier auch warten oder andere Maßnahmen ergreifen
