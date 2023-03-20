from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.color import Color
from time import sleep


class Scraper:
    def __init__(self, url):
        self.url = url
        self.data_dict = {}
        self.count = 1
        self.browser = self._initialize_browser()

    def _initialize_browser(self):
        options = Options()
        options.add_argument("--start-maximized") # Maximize the browser window
        browser = webdriver.Chrome('/home/tushar/Downloads/chromedriver_linux64/chromedriver', options=options)
        return browser

    def _wait_for_element(self, locator_type, locator_value, timeout=20,is_clickable=False):
        """
        Wait for the specified element to be located on the web page

        :param locator_type: The type of the locator (e.g. By.CSS_SELECTOR, By.XPATH)
        :param locator_value: The value of the locator (e.g. '#id', '//div[@class="class"]')
        :param timeout: The maximum amount of time to wait for the element to be located (default is 20 seconds)
        :param is_clickable: Whether the element needs to be clickable (default is False)
        :return: The located element
        """
            
        if is_clickable:
            return WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((locator_type, locator_value)))
        return WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((locator_type, locator_value)))

    def _is_next_button_disabled(self):
        """
        Check whether the 'Next' button on the web page is disabled

        :return: True if the 'Next' button is disabled, False otherwise
        """
        
        next_button = self._wait_for_element(By.CSS_SELECTOR, '[id="id_prevnext_next"]')
        return Color.from_string(next_button.value_of_css_property('background-color')).hex == '#6c757d'

    def _click_on_next_button(self):
        """
        Click on the 'Next' button on the web page
        """
        next_button = self._wait_for_element(By.CSS_SELECTOR, '[id="id_prevnext_next"]')
        next_button.click()

    def scrape_data(self, pages=10):
        """
        Scrape data from the web page

        :param pages: The number of pages to scrape (default is 10)
        """
        try:
            self.browser.get(self.url)
            
            # Wait for the page to load
            print("[*] Page Loaded")
            self._wait_for_element(By.CSS_SELECTOR, "[id='table_id']")
            
            # Click on the first posting to access project details
            select_posting = self._wait_for_element(By.XPATH, "//table[@id='table_id']/tbody/tr[1]/td[2]",is_clickable=True)
            select_posting.click()
            self._wait_for_element(By.CSS_SELECTOR, '[id="id_prevnext_prev"]')
            
            # Begin scraping data from each page
            print("[*] Data Available to Scrap")
            while self.count <= pages:
                print("Scanning Page : " + str(self.count))
                title = self._get_title()
                closing_date = self._get_closing_date()
                value_note = self._get_value_note()
                description = self._get_description()
                
                # Store scraped data in a dictionary
                self.data_dict[title] = {
                    'Closing Date': closing_date,
                    'Value Note': value_note,
                    'Description': description
                }

                # Check if there is a next page and click on it
                if self._is_next_button_disabled():
                    break
                self._click_on_next_button()
                self.count += 1

        finally:
            # Close the browser when done
            self.browser.quit()

    def _get_title(self):
        """
        Gets the title of the current project.

        :return: The title of the current project
        """

        while True:
            # Wait for the title to load
            new_title = self._wait_for_element(By.CSS_SELECTOR, '[class="mb-10"]').text

            try:
                # Check the last title in the dictionary
                old_title = list(self.data_dict.keys())[-1]
            except IndexError:
                 # If there are no titles in the dictionary, return the current title
                return new_title

            # If the current title is different from the last title, return the current title
            if old_title != new_title:
                return new_title
            
            # If the current title is the same as the last title, wait for the title to change
            sleep(3)

    def _get_closing_date(self):
        """
        Extracts and returns the closing date of the current project from the web page

        :return: The closing date of the current project
        """
        locator = (By.XPATH, '//*[@id="current_project"]/div/div[2]/div/table/tbody/tr[1]/td[2]')
        return self._wait_for_element(*locator).text

    def _get_value_note(self):
        """
        Extracts and returns the value note of the current project from the web page

        :return: The value note of the current project
        """
        locator = (By.XPATH, '//*[@id="current_project"]/div/div[2]/div/table/tbody/tr[3]/td[2]')
        return self._wait_for_element(*locator).text

    def _get_description(self):
        """
        Extracts and returns the description of the current project from the web page

        :return: The description of the current project
        """
        locator = (By.XPATH, '//*[@id="current_project"]/div/div[3]/div/table/tbody/tr[2]/td[2]')
        return self._wait_for_element(*locator).text


url = "https://qcpi.questcdn.com/cdn/posting/?group=1950787&provider=1950787"
scraper = Scraper(url)
scraper.scrape_data(pages=10)
print(scraper.data_dict)

scraper._wait_for_element
