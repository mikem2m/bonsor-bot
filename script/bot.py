from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
import os


BONSOR_INTERMEDIATE_URL = "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8634"
BONSOR_REGISTRATION_TIME_HOUR = 9


class BonsorBot:
    def __init__(self, url):
        # Init driver
        self.driver = webdriver.Chrome("../../chromedriver.exe")

        # Init constants
        load_dotenv()
        self.url = url
        self.family_pin = os.getenv('FAMILY_PIN')
        self.member_id = os.getenv('MEMBER_ID')

        # Run main
        self.main()


    def navigate_to_website(self):
        self.driver.get(self.url)

        # Wait until webpage loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "toolbar-login"))
        )


    def login(self):
        login_button = self.driver.find_element(By.XPATH, "//a[@title='Click here to login.']")
        login_button.click()

        # Wait until User Login dialog pops up
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-login-dialog"))
        )

        client_field = self.driver.find_element(By.XPATH, "//input[@id='ClientBarcode']")
        pin_field = self.driver.find_element(By.XPATH, "//input[@id='AccountPIN']")

        client_field.send_keys(self.member_id)
        pin_field.send_keys(self.family_pin)

        # Login
        pin_field.send_keys(Keys.ENTER)

        # Wait until User Login dialog disappears 
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element((By.ID, "user-login-dialog"))
        )
        

    def wait_and_refresh(self):
        # Wait until it's 9 o'clock
        
        while datetime.now().hour != BONSOR_REGISTRATION_TIME_HOUR:
            sleep(0.1) # check every 100 ms

        self.driver.refresh()


    def add_participants(self):
        pass #TODO: Continue Here!


    def logout(self):
        logout_button = self.driver.find_element(By.XPATH, "//a[@title='Select to logout.']")
        logout_button.click()

        # Wait until Login button is back -> User has been signed out
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "toolbar-login"))
        )


    def exit(self):
        self.driver.quit()


    def main(self):
        # Go to website at 8:59
        self.navigate_to_website()

        # Login with client and family pin
        self.login()

        # Refresh at 9:00
        self.wait_and_refresh()

        # Add participants to cart
        self.add_participants()

        # Log user out
        self.logout()

        # Cleanup
        self.exit()


if __name__ == "__main__":
    BonsorBot(BONSOR_INTERMEDIATE_URL)
    