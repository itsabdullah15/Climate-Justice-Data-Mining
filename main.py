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
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from mappingfile import IDENS
from datetime import datetime
import csv
import os
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import re
import numpy as np

# Configure Firefox options for headless mode
firefox_options = Options()
firefox_options.add_argument("--headless") 
geckodriver_path = IDENS.geckodriver_path #GeckoDriver executable path
service = Service(geckodriver_path) # Set up the service
# driver = webdriver.Firefox(service=service, options=firefox_options) # for headless mode
driver = webdriver.Firefox(service=service) # for non-headless mode

current_datetime = datetime.now() # Get the current date and time
current_date = datetime.now().strftime("%Y-%m-%d") #Assign Current Dates

url = IDENS.link
driver.get(url)
driver.maximize_window() #maximize the window
driver.execute_script("window.scrollTo(0, 500);")
time.sleep(1)

''' STEP 1 == Clicking on 20-30 year Total link'''
xpath = '//a[@href="javascript:fetchYearData(\'tot20_30\',1)"]'
wait = WebDriverWait(driver, 20)  # Adjust the timeout as needed
element = wait.until(EC.presence_of_element_located((By.XPATH, xpath))) # Wait until the element is present
element.click() # Click on the element
time.sleep(3)


'''STEP 6 == Download Captcha img for solving'''
def captcha_solve_loop():
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
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.bilateralFilter(gray, 9, 75, 75)
            text = pytesseract.image_to_string(blur) 
            # image = Image.open(image_path)
            # text = pytesseract.image_to_string(image) # Perform OCR on the image
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

def second_captcha_solver():
    iframe = driver.find_element(By.XPATH,'//iframe[@id="case_history"]')
    driver.switch_to.frame(iframe)
    has_executed = False 
    for _ in range(20):
        time.sleep(3)
        current_datetime = datetime.now()
        current_datetime = current_datetime.strftime("%d_%m_%Y_%H_%M_%S")
        img_download_path = f'CaptchaImg/{current_datetime}.png'

        image_element = driver.find_element(By.XPATH, "//img[@id='captcha_image']")
        location = image_element.location
        size = image_element.size
        screenshot = driver.get_screenshot_as_png() # Capture the screenshot of the entire browser window

        image = Image.open(BytesIO(screenshot)) # Use Pillow to open the screenshot and crop the desired area
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        # print(left,top,right,bottom)

        # cropped_image = image.crop((left, top, right, bottom)) # Crop the image to the specified area
        if not has_executed:
            cropped_image = image.crop(((580, 620, 695, 660)))
            cropped_image.save(img_download_path) # Save the cropped image to a file
            has_executed = True
        else:  
            crop_box = (580, 640, 695, 685)
            cropped_image = image.crop(crop_box)
            cropped_image.save(img_download_path) # Save the cropped image to a file
         
        time.sleep(2)

        '''STEP 7 == Solving the Captcha img for solving'''
        if img_download_path is not None:
            image_path = img_download_path
            # image = Image.open(image_path)
            # text = pytesseract.image_to_string(image) # Perform OCR on the image
            # text = text[:5] # Perform OCR on the image
            # print(text)
            # text = text[:5]

            def enhance_image(image_path, image_path_download,color_correction_factor=1.5):
                img = cv2.imread(image_path) # Read the image
                color_corrected_img = np.clip(img * color_correction_factor, 0, 255).astype(np.uint8)      # Apply color correction
                cv2.imwrite(image_path_download, color_corrected_img)  # Save the enhanced image
                text = pytesseract.image_to_string(image_path_download)  # Or use 'thresh' if you applied thresholding
                text = re.sub(r'[^a-zA-Z0-9]', '', text)
                print(text)
                return color_corrected_img

            image_path = 'CaptchaImg/26_02_2024_15_25_43.png'
            image_path_download = 'CaptchaImg/enhanced_one.png'
            enhanced_image = enhance_image(image_path)

            print("Extracted Text:",text) # Print the extracted text
        else:
            print("Not Able to find the img Path")
        
        captcha_input = driver.find_element("id", "captcha")
        captcha_input.clear()
        captcha_input.send_keys(text)
        time.sleep(2)
        
        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'guestlogin')))
            button.click()
        except Exception as e:
            print(f"Click issue:{e}")            

        time.sleep(12)

        try:
            element = driver.find_element(By.XPATH, '//span[@class="error"]')
            print("Checking Error Element")
            if element:
                continue
        except:
            print("There is no Captcha Error")
            driver.switch_to.default_content()
            break

def click_back_button_in_csv_file():
    try:
        backButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@id="iframe_back"]')))
        backButton.click()
    except Exception as e:
        print(f"An error occurred: {e}")
    
def csv_file(data):
    # CRNNumber_for_file_name = CRNNumber[0]
    csv_file_path = f'Output/Audit_{current_date}.csv' #Assign CSV Paths
    CRNNumber.clear()
    if not os.path.isfile(csv_file_path):         # Check if the CSV file existss
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file: # If it doesn't exist, create the file and write header
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                             'Cases',
                             'Case Type',
                             'Filing Number',
                             'Filing Date',
                             'Registration Number',
                             'Registration Date',
                             'CNR Number',
                             'First Hearing Date',
                             'Next Hearing Date',
                             'Stage of Case',
                             'Court Number and Judge',
                             'Petitioner and Advocate',
                             'Respondent and Advocate',
                             'Under Act(s)',
                             'Under Section(s)',
                             'Date of data scraping'
                             ]) 
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data)

CRNNumber = []

def error_log_file(error_log):
    error_file_path = f'Output/Error_log_{current_date}.csv'
    if not os.path.isfile(error_log_file):
        with open(error_file_path, 'w', newline='', encoding= 'utf-8') as csv:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                            'Cases',
                            'Error',
                            'Date'
                            ])
    with open(error_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(error_log)

def data_extract_from_csv_file():
    iframe = driver.find_element(By.ID, 'case_history')     # Find the iframe element
    driver.switch_to.frame(iframe)
    time.sleep(0.5)
    try:
        element = driver.find_element(By.XPATH,"//h1[@class='title-text' and text()='Secure Connection Failed']")
        if element:
            print("Secure Connection Failed. Exiting without processing further.")
            error_log = [
                case[0],
                'Secure Connection Failed Error',
                current_date    
            ]
            error_log_file(error_log)
            case.clear()
            driver.switch_to.default_content()
            return
    except Exception as e:
        print(f'No Secure Connection Failed: {e}')
    
    def case_type(): # Extract the "Case Type" values
        try:
            case_type_element = driver.find_element(By.XPATH, "(//span[@class='case_details_table'])[1]")
            case_type = case_type_element.text.split(':')[-1].strip()
            return case_type
        except Exception as e:
            print(f"An error occurred while fetching Case Type: {str(e)}")
            return None
        
    def filing_number():  # Filling Number 
        try:
            # Locate the element containing filing information using XPath
            filing_number_element = driver.find_element(By.XPATH, "(//span[@class='case_details_table'])[2]")
            # Get the text content of the located element
            filing_info_text = filing_number_element.text
            # Print the original filing number information
            # print("Original Filing Information:", filing_info_text)
            # Use regular expression to extract the filing number
            filing_number_match = re.search(r'Filing\s*Number\s*:\s*(\d+/\d+)', filing_info_text)
            # Check if a match is found
            if filing_number_match:
                filing_number = filing_number_match.group(1).lstrip()
                # print("Extracted Filing Number:", filing_number)
                return filing_number
            else:
                print("Filing number not found.")

            
        except Exception as e:
            print(f"An error occurred while fetching Filling Number: {str(e)}")
            return None

    def filing_date(): # Extract the filing date value
        try:
            filing_date_label = driver.find_element(By.XPATH, "(//span[@class='case_details_table'])[2]")
            filing_date_value = filing_date_label.text.split(':')[-1].strip()
            print("FILINGGGG DATE:",filing_date_value)
            return filing_date_value
        except Exception as e:
            print(f"An error occurred while fetching Filling Date Value: {str(e)}")
            return None

    def registration_number(): # Registration Number
        try:
            registration_number_element = driver.find_element(By.XPATH, "(//span[@class='case_details_table'])[3]")
            registration_number = registration_number_element.text
            # Using regular expression to extract Registration Number
            registration_number_match = re.search(r'Registration Number\s*:\s*(\d+/\d+)', registration_number)
            if registration_number_match:
                registration_number = registration_number_match.group(1).lstrip()
                print("Registration Number:", registration_number)
                return registration_number
            else:
                print("Registration number not found.")
        except Exception as e:
            print(f"An error occurred while fetching Registration Number: {str(e)}")
            return None

    def crn_number(): # CRN Number
        try:
            CRN_Number_element = driver.find_element(By.XPATH, "(//span[@class='case_details_table'])[4]")
            CRN_Number = CRN_Number_element.text.split(':')[-1].strip()
            CRNNumber.append(CRN_Number)
            return CRN_Number
        except Exception as e:
            print(f"An error occurred while fetching CRN Number: {str(e)}")
            return None

    def registration_date():  #Registration Date 
        try:
            registration_date_element = driver.find_element(By.XPATH, '//*[@id="part1"]/div[1]/span[4]/span[2]/label[2]')
            registration_date = registration_date_element.get_attribute("textContent").strip()
            if ':' in registration_date:
                registration_date = registration_date.replace(':', '')
            registration_date = registration_date.lstrip()
            return registration_date
        except Exception as e:
            print(f"An error occurred while fetching Registration Date: {str(e)}")
            return None

    def first_hearing_date():   #First Hearing Date 
        try:
            first_hearing_date_element = driver.find_element(By.XPATH,'(//div//span//label//strong)[2]')
            first_hearing_date = first_hearing_date_element.get_attribute("textContent").strip()
            if ':' in first_hearing_date:
                first_hearing_date = first_hearing_date.replace(':', '')
            first_hearing_date = first_hearing_date.lstrip()
            return first_hearing_date
        except Exception as e:
            print(f"An error occurred while fetching First Hearing Date: {str(e)}")
            return None

    def next_hearing():  # Next Hearing Date 
        try:
            next_hearing_date_element = driver.find_element(By.XPATH,'(//div//span//label//strong)[4]')
            next_hearing_date = next_hearing_date_element.get_attribute("textContent").strip()
            if ':' in next_hearing_date:
                next_hearing_date = next_hearing_date.replace(':', '')
            next_hearing_date = next_hearing_date.lstrip()
            return next_hearing_date
        except Exception as e:
            print(f"An error occurred while fetching Next Hearing Date: {str(e)}")
            return None

    def stage_of_case(): #Stage of Case 
        try:
            Stage_of_Case_element = driver.find_element(By.XPATH,'(//div//span//label//strong)[6]')
            Stage_of_Case = Stage_of_Case_element.get_attribute("textContent").strip()
            if ':' in Stage_of_Case:
                Stage_of_Case = Stage_of_Case.replace(':', '')
            Stage_of_Case = Stage_of_Case.lstrip()
            return Stage_of_Case
        except Exception as e:
                print(f"An error occurred while fetching Stage of Case: {str(e)}")
                return None

    def court_number_and_judge():  #Court Number and Judge
        try:
            Court_Number_and_Judge_element = driver.find_element(By.XPATH,'(//div//span//label//strong)[8]')
            Court_Number_and_Judge = Court_Number_and_Judge_element.get_attribute("textContent").strip()
            if ':' in Court_Number_and_Judge:
                Court_Number_and_Judge = Court_Number_and_Judge.replace(':', '')  
            Court_Number_and_Judge = Court_Number_and_Judge.lstrip()  
            return Court_Number_and_Judge
        except Exception as e:
            print(f"An error occurred while fetching Court Number and Judge: {str(e)}")
            return None

    def petitioner_and_Advocate():  #Petitioner and Advocates
        try:
            Petitioner_and_Advocate_element = driver.find_element(By.CLASS_NAME, 'Petitioner_Advocate_table')
            Petitioner_and_Advocate = Petitioner_and_Advocate_element.text.replace('\n', '')
            return Petitioner_and_Advocate
        except Exception as e:
            print(f"An error occurred while fetching Petitioner and Advocate: {str(e)}")
            return None

    def respondent_and_advocate(): #Respondent and Advocate
        try:
            respondent_advocate_table_element = driver.find_element(By.CLASS_NAME, 'Respondent_Advocate_table')
            respondent_advocate_text = respondent_advocate_table_element.text.replace('\n', '')
            return respondent_advocate_text
        except Exception as e:
            print(f"An error occurred while fetching Respondent and Advocate: {str(e)}")
            return None

    def under_act():  # Under Act(s)
        try:
            Under_Act_element = driver.find_element(By.XPATH, '//table[@id="act_table"]//tbody//tr[2]//td[1]')
            Under_Act_text = Under_Act_element.text
            return Under_Act_text
        except Exception as e:
            print(f"An error occurred while fetching Under Act(s): {str(e)}")

    def under_section():  # Under Section(s)
        try:
            Under_Section_element = driver.find_element(By.XPATH, '//table[@id="act_table"]//tbody//tr[2]//td[2]')
            Under_Section_text = Under_Section_element.text
            return Under_Section_text
        except Exception as e:
            print(f"An error occurred while fetching Under Section(s): {str(e)}")
            return None

    case_type_data = case_type() #1
    filing_number_data = filing_number() #2
    registration_number_data = registration_number() #3
    crn_number_data = crn_number() #4
    filing_date_data = filing_date() #5
    registration_date_data = registration_date() #5
    first_hearing_date_data = first_hearing_date() #6
    next_hearing_date_data = next_hearing() #7
    stage_of_case_data = stage_of_case() #8
    court_number_and_judge_data = court_number_and_judge() #9
    petitioner_and_Advocate_data = petitioner_and_Advocate() #10
    respondent_and_advocate_data = respondent_and_advocate() #11
    under_act_data = under_act() #12
    under_section_data = under_section() #13

    print("CASE TYPE ",case_type_data)
    print("FILING NUMBER ",filing_number_data)
    print("FILING DATE ", filing_date_data)
    print("REGISTRATION NUMBER ",registration_number_data)
    print("REGISTRATION DATE ", registration_date_data)
    print("CRN NUMBER ", crn_number_data)
    print("FIRST HEARING DATE ", first_hearing_date_data)
    print("NEXT HEARING DATE ", next_hearing_date_data)
    print("STAGE OF CASTE DATA ", stage_of_case_data)
    print("COURT NUMBER AND JUDGE DATA ", court_number_and_judge_data)
    print("PETITIONER AND ADVOCATE DATA ", petitioner_and_Advocate_data)
    print("RESPONDENT AND ADVOCATE DATA ", respondent_and_advocate_data)
    print("UNDER ACT ", under_act_data)
    print("UNDER SECTION ", under_section_data)
    print("CURRENT DATE ", current_date)

    # Example usage:
    data_to_save = [
                    case[0],
                    case_type_data,
                    filing_number_data,
                    filing_date_data,
                    registration_number_data,
                    registration_date_data,
                    crn_number_data,
                    first_hearing_date_data,
                    next_hearing_date_data,
                    stage_of_case_data,
                    court_number_and_judge_data,
                    petitioner_and_Advocate_data,
                    respondent_and_advocate_data,
                    under_act_data,
                    under_section_data,
                    current_date
                    ]
    csv_file(data_to_save)
    case.clear()
    driver.switch_to.default_content()

case = []
def extract_text_loop():
    case_elements = driver.find_elements(By.XPATH, "//td[@class='sorting_1']/a")
    for case_element in case_elements:
        case_text = case_element.text
        case.append(case_text)
        case_element.click()
        time.sleep(1)
        second_captcha_solver()
        time.sleep(1)
        print("After Second Captcha")
        data_extract_from_csv_file()
        time.sleep(1)
        click_back_button_in_csv_file()

def back():
    try:
        back_button = driver.find_element(By.XPATH, "//a[@href='javascript:back(4)']")
        back_button.click()
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted while going back: {e}")

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

''' STEP 5 == Fourth Loop'''
def fourth_loop():
    try:
        xpath = "(//tbody[@id='est_report_body']/tr/td[4]/a)"
        wait = WebDriverWait(driver, 20)
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        count = 1
        for element in elements:
            if count == 1:
                count += 1
                continue
            try:
                time.sleep(0.5)
                element.click()
                time.sleep(1)
                captcha_solve_loop()
                extract_text_loop()
                time.sleep(0.5)
                back()
                time.sleep(2)
            except NoSuchElementException as e:
                print(f"Element not found: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                time.sleep(2)
        last_second_back()

    except TimeoutException as te:
        print(f"Timeout waiting for elements to be present: {te}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
        # print("Breaking")
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
        skip = 1
        elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, button_xpath)))
        print("Countttt ",len(elements))
        for element in elements:
            # if skip<=3:
            #     skip+=1
            #     continue
            element.click()
            time.sleep(1)
            second_loop_both_button_clicked_single_row_column()
            time.sleep(1)
            third_loop()
            time.sleep(1)
            last_third_back()
            time.sleep(1)
            last_fourth_back()
            time.sleep(0.5)
    except Exception as e:
        print(f"Error clicking the button: {e}")

first_loop()

time.sleep(20)

driver.quit