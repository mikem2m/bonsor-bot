from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from time import sleep
import unittest
import os


class CourseFinder(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        # service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome('/Users/jonathanadithya/Documents/scripts/chromedriver 2')

    def test_finding_cpsc121_lab(self):
        self.driver.get("https://courses.students.ubc.ca/cs/courseschedule")

        login = self.driver.find_element(By.XPATH, '//*[@id="cwl"]/form/input')
        login.click()
        self.assertEqual(self.driver.title, "CWL Authentication")
        login_name = self.driver.find_element(By.XPATH, '//*[@id="username"]')
        password = self.driver.find_element(By.XPATH, '//*[@id="password"]')
        submit = self.driver.find_element(
            By.XPATH, '//*[@id="fm1"]/section[5]/input[4]'
        )
        login_name.send_keys(os.environ["USERNAME"])
        password.send_keys(os.environ["PASSWORD"])
        submit.click()

        sleep(2.5)
        worklist = self.driver.find_element(
            By.XPATH, '/html/body/div[2]/div[4]/div/ul/li[2]/a'
        )
        worklist.click()
        sleep(2)

        courses = [1, 2, 4] + [i for i in range(6, 14)] + [15, 16, 17, 18, 22, 23]
        print('\n---------- COURSES ----------')
        for i in courses:
            status = self.driver.find_element(
                By.XPATH,
                f'/html/body/div[2]/div[4]/form[2]/table[2]/tbody/tr[{i}]/td[2]',
            ).text
            name = self.driver.find_element(
                By.XPATH,
                f'/html/body/div[2]/div[4]/form[2]/table[2]/tbody/tr[{i}]/td[3]/a',
            ).text
            print(name + '\t' + status)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
