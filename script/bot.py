from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
import unittest
import os


class BonsorBot:
    def __init__(self, url):
        load_dotenv()
        self.driver = webdriver.Chrome('/Users/jonathanadithya/Documents/scripts/chromedriver 2')
        self.url = url
        self.main()

    def navigate_to_website(self):
        self.driver.get(self.url)
        sleep(1)

    def login(self):
        login_button = self.driver.find_element(By.XPATH, "//a[@title='Click here to login.']")
        login_button.click()
        sleep(1)
        client_field = self.driver.find_element(By.XPATH, "//*[@id='ClientBarcode']")
        pin_field = self.driver.find_element(By.XPATH, "//*[@id='AccountPIN']")
        # client_field.send_keys(os.environ.get('CLIENT'))
        # pin_field.send_keys(os.environ.get('PIN'))
        client_field.send_keys('372843')
        pin_field.send_keys('329843')
        sleep(1)
        
    def refresh(self):
        # Wait until it's 9 o'clock
        while datetime.now().hour != 9:
            sleep(0.1)
        self.driver.refresh()

    def exit(self):
        self.driver.quit()

    def main(self):
        # Go to website at 8:59
        self.navigate_to_website()

        # Login with client and family pin
        self.login()

        # Refresh at 9:00
        # self.refresh()

        # Cleanup
        self.exit()


if __name__ == "__main__":
    BonsorBot('https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8634')
