import time
from dataclasses import dataclass
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
import requests
from slugify import slugify
from requests_html import HTML
import pprint
import re


def get_user_agent():
    return UserAgent(verify_ssl=False).random  # creates a random browser agent when the instance is started


def extract_price_from_string(value: str, regex=r"[\$]{1}[\d,]+\.?\d{0,2}"):
    x = re.findall(regex, value)
    val = x[0] if len(x) == 1 else None
    return val


@dataclass
class Scraper:
    """
    basic class for scrapping
    """
    url: str = None
    asin: str = None
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    driver: WebDriver = None  # check the type
    html_obj: HTML = None

    def __post_init__(self):
        if self.asin:
            self.url = f"https://www.amazon.com/dp/{self.asin}/"
        if not self.asin or not self.url:
            raise Exception('asin or url required')

    def get_driver(self):
        if self.driver is None:
            user_agent = get_user_agent()
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument(f"user-agent={user_agent}")
            driver = webdriver.Chrome(options=options)
            self.driver = driver
        return self.driver

    def perform_endless_scroll(self, driver=None):
        if driver is None:
            return
        if self.endless_scroll:
            current_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(self.endless_scroll_time)
                iter_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == iter_height:
                    break
                current_height = iter_height
        return


    def extract_element_text(self, element_id):
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id, first=True)
        return el.text if el else ""


    def extract_tables(self):
        html_obj = self.get_html_obj()
        return html_obj.find("table")

    def extract_table_dataset(self, tables) -> dict:
        dataset = {}
        for table in tables:
            for tbody in table.element.getchildren():
                for tr in tbody.getchildren():
                    row = []
                    for col in tr.getchildren():
                        content = ""
                        try:
                            content = col.text_content()
                        except:
                            pass
                        if content != "":
                            _content = content.strip()
                            row.append(_content)
                    if len(row) != 2:
                        continue
                    key = row[0]
                    value = row[1]

                    # print(key, value)
                    data = {}
                    key = slugify(key)
                    key = key.replace("-", "_")
                    if key not in dataset:
                        if "$" in value:
                            new_key = key
                            old_key = f'{key}_raw'
                            new_value = extract_price_from_string(value)
                            old_value = value
                            dataset[new_key] = new_value
                            dataset[old_key] = old_value
                        else:
                            dataset[key] = value
        return dataset

    def get_html_obj(self):
        if self.html_obj is None:
            html_str = self.get()
            self.html_obj = HTML(html=html_str)
        return self.html_obj

    def get(self):
        driver = self.get_driver()
        driver.get(self.url)
        if self.endless_scroll:
            self.perform_endless_scroll(driver=driver)
        else:
            time.sleep(10)
        return driver.page_source

    def scrape(self):
        html_obj = self.get_html_obj()
        price = self.extract_element_text(
                                     '#corePrice_desktop > div > table > tbody > tr:nth-child(2) > td.a-span12 > '
                                     'span.a-price.a-text-price.a-size-medium.apexPriceToPay > span.a-offscreen')
        title = self.extract_element_text("#productTitle")
        tables = self.extract_tables()
        dataset = self.extract_table_dataset(tables)
        return {
            "price_str": price,
            "title_str": title,
            "title": title,
            **dataset
        }