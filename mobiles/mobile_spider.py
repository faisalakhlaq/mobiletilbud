from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
import io
from PIL import Image
import requests
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementNotVisibleException
)
from .models import Mobile
from core.models import MobileBrand

def configure_driver():
    # Add additional Options to the webdriver
    firefox_options = FirefoxOptions()
    # add the argument and make the browser Headless.
    firefox_options.add_argument("--headless")
    try:
        driver = webdriver.Firefox(options=firefox_options,
                                    executable_path=GeckoDriverManager().install())
    except:
        driver = webdriver.Firefox(options=firefox_options,
                                    executable_path='/usr/local/bin/geckodriver')
    return driver


class HuawaiMobileSpider():
    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.url = 'https://consumer.huawei.com/en/phones/'

    def close_webdriver(self, firefox_driver):
        if firefox_driver:
            firefox_driver.close()
            firefox_driver.quit()

    def fetch_mobiles(self):
        firefox_driver = configure_driver()
        try:
            firefox_driver.get(self.url)
            devices = WebDriverWait(firefox_driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-block__background"))
            )
            try:
                load_more_button = firefox_driver.find_element(By.XPATH, "//*[text()='Load More']")
                load_more_button.send_keys(Keys.RETURN)
            except Exception as e:
                print(e)

            soup = BeautifulSoup(firefox_driver.page_source, "html.parser")
            p_rows = soup.find_all('div', {'class', 'product-row row'})
            rows = p_rows[0].find_all('div', {'class', 'product-col'})
            print("ROWS == ", len(p_rows))
            for row in rows:
                mobile_box = row.find('div', {'class', 'product-block'})
                mobile_info_box = mobile_box.find('div', {'class', 'product-block__details'})
                mobile_name_a = mobile_info_box.find('div', {'class', 'heading product-block__title'}).find('a')
                
                full_name = mobile_name_a.text.strip()
                name = full_name.split(" ", 1)[1]
                mobile_url = mobile_name_a['href']
                image_box = row.find('div',{'class','product-block__in js-product-block'})
                image_a = image_box.find('div', {'class','product-block__holder js-img-holder'}).find('a')
                images = image_a.find_all('img')
                image = None
                for img in images:
                    try:
                        img_src = img['data-src']
                        if img_src and len(img_src.strip()) > 5:
                            img_src = 'https://consumer.huawei.com' + img_src
                            # image_content = requests.get(img_src).content
                            response = requests.get(img_src, stream=True).content
                            # image_file = io.BytesIO(response.raw)
                            image_file = io.BytesIO(response)
                            image = Image.open(image_file)

                            # response = requests.get(img_src, stream=True)
                            # image_file = io.BytesIO(response)
                            # image_file = io.BytesIO(image_content)
                            # image = Image.open(image_file)
                            break
                    except (KeyError, Exception) as e:
                        print('Exception: ', e)
                        continue
                self.save_huawei_mobile(
                    name=name,
                    full_name=full_name,
                    image=image,
                    url=mobile_url,
                )
            self.close_webdriver(firefox_driver)
        except (TimeoutException, ElementNotVisibleException, Exception) as e:
            print('TIMEOUT - ', e)
            self.close_webdriver(firefox_driver)

    # def download_image(self):
    #     img_src = 'https://consumer.huawei.com/content/dam/huawei-cbg-site/common/mkt/pdp/phones/mate40/list-img/silver.png'
    #     response = requests.get(img_src, stream=True).content
    #     # image_file = io.BytesIO(response.raw)
    #     image_file = io.BytesIO(response)
    #     image = Image.open(image_file)
    #     self.save_huawei_mobile(name='Mate 40', image=image)

    def save_huawei_mobile(self, name, full_name=None, url=None, image=None):
        try:
            # brand = MobileBrand.objects.filter(name__iexact='huawei')
            # if brand: 
            #     brand = brand[0]
            mobile = Mobile.objects.filter(name__iexact=name)[0]
            thumb_io = io.BytesIO()
            image.save(thumb_io, image.format, quality=90)
            mobile.image.save(image.filename, ContentFile(thumb_io.getvalue()), save=False)
            mobile.save()
            print("Saved a new mobile: ", mobile.full_name)
        except Exception as e:
            print("Exception while saving Mobile: ", e)
