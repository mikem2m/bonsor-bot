"""
Volleyball Registration Automation (Webreg Burnaby) using Selenium

Classes:
    RegistrationBot

Author:
    Jonathan Aditya @ https://github.com/jo-adithya
    Michael Suriawan @ https://github.com/mikem2m
"""

import os
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from helper import generate_url, BONSOR_REGISTRATION_TIME_HOUR, BONSOR_REGISTRATION_COST


class RegistrationBot:
    """A class to represent the selenium driver automation

    Attributes:
    -----------
    driver : WebDriver
        selenium webdriver
    url : str
        url for the volleyball registration
    member_id : str
        client number for webreg account
    family_pin : str
        identification pin for webreg account
    num_participants : int
        number of participants in the account

    Class Methods
    -------------
    url(url)
        Initialize RegistrationBot with the given url and account identification from dotenv
    identification(url, member_id, family_pin)
        Initialize RegistrationBot with the given URL and account identification
    """

    def __init__(self, _url, member_id, family_pin):
        # Init driver
        self.driver = webdriver.Chrome("../../chromedriver 2")

        # Init constants
        self._url = _url
        self.num_participants = 0
        self.member_id = member_id
        self.family_pin = family_pin

        # Run main
        self.main()

    @classmethod
    def url(cls, _url):
        """Initialize RegistrationBot with the given url and account identification from dotenv

        Parameters
        ----------
        url : string
            url for the volleyball registration
        """
        load_dotenv()
        cls(_url, os.getenv('MEMBER_ID'), os.getenv('FAMILY_PIN'))

    @classmethod
    def identification(cls, _url, member_id, family_pin):
        """Initialize RegistrationBot with the given URL and account identification

        Parameters
        ----------
        url : string
            url for the volleyball registration
        member_id : string
            client number for webreg account
        family_pin : string
            identification pin for webreg account
        """
        cls(_url, member_id, family_pin)

    def navigate_to_website(self):
        """Navigate to the provided url.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.driver.get(self.url)

        # Wait until webpage loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "toolbar-login"))
        )

    def login(self):
        """Login to the webreg account using the provided family_pin and member_id.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
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
        """Wait until the registration time (9 AM) and then refresh the page.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Wait until it's 9 o'clock
        while datetime.now().hour != BONSOR_REGISTRATION_TIME_HOUR:
            sleep(0.1)  # check every 100 ms

        # First Refresh
        self.driver.refresh()

        # Refresh until add button is available
        while not self.__check_add_button_exists():
            self.driver.refresh()

    def add_participants(self):
        """Add all of the participants in the account to the cart."

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # I added 'last()' in the XPATH to make sure that its the last 'Add' button.
        # This was done to avoid the case where this week's intermediate option has
        # an open spot, but we want to sign up for next week's spot instead.
        # To avoid selecting this week's session instead, pick the last one available
        # The ones for 2-3 weeks in advance will not have the 'Add' button, so we are good
        add_button_title = "Click here to add the corresponding course to your cart. Once in your cart you can continue shopping or go to checkout and finalized your registration"
        add_button = self.driver.find_element(
            By.XPATH, f'//a[@title=\'{add_button_title}\'][last()]'
        )
        add_button.click()

        # Wait until cart dialog pops up
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "cart"))
        )

        # Find the 'Select A Participant' dropdown
        dropdown_xpath = "//select[@title='Select a client']"
        dropdown = Select(self.driver.find_element(By.XPATH, dropdown_xpath))

        # Save all participant names in a hashmap of id and names - retrieves this from the dropdown
        participant_map = {}
        for option in dropdown.options:
            _id = option.get_attribute('value')
            name = option.text

            # There is a default option with value attribute '0'that should not add to the map
            if _id == '0':
                continue
            participant_map[_id] = name

        self.num_participants = len(participant_map)
        for idx, (_id, name) in enumerate(participant_map.items()):
            # Select from dropdown
            dropdown.select_by_value(_id)

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

                # Re-select 'Select A Participant' dropdown
                #   -> this is fine since only one dropdown should show up at a time!
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                )
                dropdown = Select(self.driver.find_element(By.XPATH, dropdown_xpath))

    def go_to_checkout(self):
        """Navigate to the checkout page.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
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
        """Complete the transaction if the account balance is sufficient.

        Parameters
        ----------
        None

        Returns
        -------
        bool: state of the transaction (success or fail)
        """
        # Check balance: Returns false if insufficient balance
        current_balance = float(
            self.driver.find_element(By.XPATH, "//*[@id='current-balance']/div/span[2]")
            .text.split("$")[1]
            .replace(')', '')
        )
        if current_balance < self.num_participants * BONSOR_REGISTRATION_COST:
            print("Insufficient Fund")
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
        print(f"Successfully registered Client # {self.member_id}")
        return True

    def logout(self):
        """Logout the webreg account

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        logout_button = self.driver.find_element(
            By.XPATH, "//a[@title='Select to logout.']"
        )
        logout_button.click()

        # Wait until Login button is back -> User has been signed out
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "toolbar-login"))
        )

    def exit(self):
        """Quit the webdriver process

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.driver.quit()

    def main(self):
        """Main control method for the volleyball registration automation process

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Go to website at 8:59
        self.navigate_to_website()

        # Login with client and family pin
        self.login()

        # Refresh at 9:00
        self.wait_and_refresh()

        # Add participants to cart
        self.add_participants()

        # Go to checkout page
        self.go_to_checkout()

        # Log user out if payment is successful, otherwise quit so that the cart won't be removed.
        if self.pay():
            self.logout()

        # Cleanup
        self.exit()

    def __check_add_button_exists(self):
        add_button_title = "Click here to add the corresponding course to your cart. Once in your cart you can continue shopping or go to checkout and finalized your registration"
        add_button_xpath = f'//a[@title=\'{add_button_title}\'][last()]'
        try:
            self.driver.find_element(By.XPATH, add_button_xpath)
        except NoSuchElementException:
            return False
        return True


if __name__ == "__main__":
    if url := generate_url() is not None:
        RegistrationBot.url(url)
    else:
        print('No volleyball registration for today')
