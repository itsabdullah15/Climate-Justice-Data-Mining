import time
from typing import Any
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from mappingfile import IDENS
from datetime import datetime
import requests
from datetime import datetime
import pandas as pd
import os
from io import BytesIO
from PIL import Image
from PIL import Image
import pytesseract

# Configure Firefox options for headless mode
firefox_options = Options()
firefox_options.add_argument("--headless") 
geckodriver_path = IDENS.geckodriver_path #GeckoDriver executable path
service = Service(geckodriver_path) # Set up the service
# driver = webdriver.Firefox(service=service, options=firefox_options) # for headless mode
driver = webdriver.Firefox(service=service) # for non-headless mode

current_datetime = datetime.now() # Get the current date and time

url = IDENS.link
driver.get(url)
driver.maximize_window() #maximize the window
driver.execute_script("window.scrollTo(0, 500);")

''' STEP 1 == Clicking on 20-30 year Total link'''
xpath = '//a[@href="javascript:fetchYearData(\'tot20_30\',1)"]'
wait = WebDriverWait(driver, 20)  # Adjust the timeout as needed
element = wait.until(EC.presence_of_element_located((By.XPATH, xpath))) # Wait until the element is present
element.click() # Click on the element
time.sleep(3)


'''STEP 6 == Download Captcha img for solving'''
def cathcha_solve_loop():
    for _ in range(20):
        current_datetime = datetime.now()
        current_datetime = current_datetime.strftime("%d_%m_%Y_%H_%M_%S")
        img_download_path = f'CaptchaImg/{current_datetime}.png'

        image_element = driver.find_element(By.XPATH, "//img[@id='captcha_image1']")
        location = image_element.location
        size = image_element.size
        screenshot = driver.get_screenshot_as_png() # Capture the screenshot of the entire browser window

        image = Image.open(BytesIO(screenshot)) # Use Pillow to open the screenshot and crop the desired area
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        cropped_image = image.crop((left, top, right, bottom)) # Crop the image to the specified area
        cropped_image.save(img_download_path) # Save the cropped image to a file
        time.sleep(2)


        '''STEP 7 == Solving the Captcha img for solving'''
        if img_download_path is not None:
            image_path = img_download_path
            image = Image.open(image_path)

            text = pytesseract.image_to_string(image) # Perform OCR on the image
            text = text[:5]

            # Print the extracted text
            # print("Extracted Text:", text)
        else:
            print("Not Able to find")

        '''STEP 8 == After Solving the Captcha Filling the data captcha data into input & Submit'''
        captcha_input = driver.find_element("id", "captcha1")
        captcha_input.clear()
        captcha_input.send_keys(text)
        time.sleep(3)

        xpath = '//input[@class="btn btn-success col-auto btn-sm"]'
        wait = WebDriverWait(driver, 20)  # Adjust the timeout as needed
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath))) # Wait until the element is present
        element.click() # Click on the element
        time.sleep(3)
        popup_timeout = 10
        try:
            popup = WebDriverWait(driver, popup_timeout).until(EC.alert_is_present())
            popup.accept()
            time.sleep(3)
        except:
            print("No alert found within the specified timeout.")
            break

def extract_text_loop():
    td_elements = driver.find_elements(By.XPATH, "//td[@class='sorting_1']/a")
    for td_element in td_elements:
        text_content = td_element.text
        Cases.append(text_content)
        print("Extracted Text:", text_content)

def back():
    try:
        back_button = driver.find_element(By.XPATH, "//a[@href='javascript:back(4)']")
        back_button.click()
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted while going back: {e}")
        # Handle the interception issue here if needed

def last_second_back():
    try:
        back_button = driver.find_element(By.XPATH, "//a[@href='javascript:back(3)']")
        back_button.click()
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted while going back: {e}")

def last_third_back():
    try:
        back_button = driver.find_element(By.XPATH, "//a[@href='javascript:back(2)']")
        back_button.click()
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted while going back: {e}")

def last_fourth_back():
    try:
        print("Okay")
        back_button = driver.find_element(By.XPATH, "//a[@href='javascript:back(1)']")
        back_button.click()
        print("Clicked")
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted while going back: {e}")
    except TimeoutException as te:
        print(f"TimeoutException while going back: {te}")

Cases = []

''' STEP 5 == Clicking on 20-30 year Total link'''
def fourth_loop():
    xpath = "(//tbody[@id='est_report_body']/tr/td[4]/a)"
    wait = WebDriverWait(driver, 20)
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    for element in elements:
        time.sleep(0.5)
        element.click()
        time.sleep(1)
        cathcha_solve_loop() 
        extract_text_loop()
        time.sleep(0.5)
        back()
        time.sleep(2)
    last_second_back()

#########Loop#########
''' STEP 4 == Clicking on 20-30 year Total link'''
def third_loop():
    xpath = "(//tbody[@id='dist_report_body']/tr/td[4]/a)"
    wait = WebDriverWait(driver, 20)
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    print("Len", len(elements))
    for element in elements:
        time.sleep(1)
        element.click()
        time.sleep(0.5)
        fourth_loop()
        time.sleep(0.5)
        print("Breaking")
    print("Total Count of Cases: ",len(Cases))


def second_loop_both_button_clicked_single_row_column():
    xpath = "(//tbody[@id='state_report_body']/tr/td[4]/a)"
    element = driver.find_element(By.XPATH, xpath)
    element.click()


''' STEP 2 == Clicking on 20-30 year Total link'''
def first_loop():
    button_xpath = "(//tbody[@id='state_report_body']/tr/td[4]/a)"
    wait = WebDriverWait(driver, 20)
    try:
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, button_xpath)))
        print("Countttt ",len(elements))
        for element in elements:
            element.click()
            time.sleep(3)
            second_loop_both_button_clicked_single_row_column()
            time.sleep(3)
            third_loop()
            time.sleep(3)
            last_third_back()
            time.sleep(3)
            last_fourth_back()
            time.sleep(3)
    except Exception as e:
        print(f"Error clicking the button: {e}")

first_loop()



time.sleep(20)

driver.quit