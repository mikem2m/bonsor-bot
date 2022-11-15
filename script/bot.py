import os
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

EDMONDS_TUESDAY_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8607"
)
EDMONDS_THURSDAY_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8614"
)
BONSOR_TUESDAY_BEGINNER_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8633"
)
BONSOR_TUESDAY_INTEMEDIATE_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8642"
)
BONSOR_FRIDAY_INTERMEDIATE_URL = (
    "https://webreg.burnaby.ca/webreg/Activities/ActivitiesDetails.asp?aid=8634"
)
BONSOR_REGISTRATION_TIME_HOUR = 9


class BonsorBot:
    def __init__(self, url):
        # Init driver
        self.driver = webdriver.Chrome("../../chromedriver 2")

        # Init constants
        load_dotenv()
        self.url = url
        self.family_pin = os.getenv('FAMILY_PIN')
        self.member_id = os.getenv('MEMBER_ID')
        self.num_participants = 0

        # Run main
        self.main()

    def navigate_to_website(self):
        self.driver.get(self.url)

        # Wait until webpage loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "toolbar-login"))
        )

    def login(self):
        login_button = self.driver.find_element(
            By.XPATH, "//a[@title='Click here to login.']"
        )
        login_button.click()

        # Wait until User Login dialog pops up
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-login-dialog"))
        )

        client_field = self.driver.find_element(
            By.XPATH, "//input[@id='ClientBarcode']"
        )
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
            sleep(0.1)  # check every 100 ms

        self.driver.refresh()

    def add_participants(self):
        # I added 'last()' in the XPATH to make sure that its the last 'Add' button
        # This was done to avoid the case where this week's intermediate option has an open spot, but we want to sign up for next week's spot instead
        # To avoid selecting this week's session instead, pick the last one available
        # The ones for 2-3 weeks in advance will not have the 'Add' button, so we are good
        ADD_BUTTON_TITLE = "Click here to add the corresponding course to your cart. Once in your cart you can continue shopping or go to checkout and finalized your registration"
        add_button = self.driver.find_element(
            By.XPATH, f'//a[@title=\'{ADD_BUTTON_TITLE}\'][last()]'
        )
        add_button.click()

        # Wait until cart dialog pops up
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "cart"))
        )

        # Find the 'Select A Participant' dropdown
        DROPDOWN_XPATH = "//select[@title='Select a client']"
        dropdown = Select(self.driver.find_element(By.XPATH, DROPDOWN_XPATH))

        # Save all participant names in a hashmap of id and names - retrieves this from the dropdown
        participant_map = {}
        for option in dropdown.options:
            id = option.get_attribute('value')
            name = option.text
            # The dropdown has a default option with value attribute '0' that we should not add to the map
            if id == '0':
                continue
            else:
                participant_map[id] = name

        # TODO: NEED TO WRAP THE BELOW CODE IN TRY / FINALLY BLOCK SO IN THE CASE THAT WE ARE WAITLISTED, THE OTHER SPOTS CAN STILL BE BOOKED

        self.num_participants = len(participant_map)
        for idx, (id, name) in enumerate(participant_map.items()):
            # Select from dropdown
            dropdown.select_by_value(id)

            # Wait until participant is added
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f'//a[@title=\'{name}: Select to view client details.\']',
                    )
                )
            )

            # Add another participant if it's not the last element
            if idx != self.num_participants - 1:
                add_another_participant_button = self.driver.find_element(
                    By.XPATH,
                    "//input[@title='Select to add another client to cart.'][1]",
                )
                add_another_participant_button.click()

                # Re-select 'Select A Participant' dropdown -> this is fine since only one dropdown should show up at a time!
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, DROPDOWN_XPATH))
                )
                dropdown = Select(self.driver.find_element(By.XPATH, DROPDOWN_XPATH))

    def go_to_checkout(self):
        # Navigate to checkout page
        checkout_button = self.driver.find_element(
            By.XPATH,
            "//input[@title='Click here to go to the checkout and pay for the items in your shopping cart.']",
        )
        checkout_button.click()

        # Wait until the payment checkout loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='content']/h2"))
        )

    def pay(self):
        # Check balance: Returns false if insufficient balance
        current_balance = float(
            self.driver.find_element(
                By.XPATH, "//*[@id='current-balance']/div/span[2]"
            ).text.split("$")[1]
        )
        print(current_balance, self.num_participants)
        if current_balance < self.num_participants * 5.25:
            return False

        # Complete transaction if balance is enough
        complete_transaction_button = self.driver.find_element(
            By.ID, "completeTransactionButton"
        )
        complete_transaction_button.click()

        # Wait until the payment is confirmed
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//*[@id='content']/h2"), "Transaction Completed"
            )
        )
        return True

    def logout(self):
        logout_button = self.driver.find_element(
            By.XPATH, "//a[@title='Select to logout.']"
        )
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

        self.go_to_checkout()

        # Log user out if payment is successful, otherwise quit so that the cart won't be removed.
        if self.pay():
            self.logout()

        # Cleanup
        self.exit()


if __name__ == "__main__":
    BonsorBot(BONSOR_FRIDAY_INTERMEDIATE_URL)
