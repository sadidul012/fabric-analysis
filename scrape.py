import hashlib
import json
import os
import types

import selenium
from seleniumbase import SB
from tqdm import tqdm
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By


class Scrape:
    def __init__(self, urls, image_slider_container=None, image_slider_next=None, product_page_removes=None, n_slides=0):
        self.urls = urls
        self.image_slider_container = image_slider_container
        self.image_slider_next = image_slider_next
        self.product_page_removes = product_page_removes
        self.n_slides = n_slides

        self.visited = set()

        self.cache_directory = "./data/temp/"
        # self.sb_params = dict(uc=True, maximize=True)
        self.sb_params = dict(uc=True, maximize=True, uc_subprocess=True)

        self.result_dict = {
            "attributes": [],
            "images": []
        }

    def scrape_product_search_results(self, url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=None):
        return []

    def extract_details(self, text, url):
        return {}

    def extract_item_links(self, text):
        return []

    def add_raw_tags(self, tags):
        self.result_dict["raw_tags"] = tags

    def add_name(self, name):
        self.result_dict["name"] = name

    def add_price(self, price):
        self.result_dict["price"] = price

    def add_description(self, description):
        self.result_dict["description"] = description

    def add_size(self, size):
        self.result_dict["size"] = size

    def append_attribute(self, attribute):
        self.result_dict["attributes"].append(attribute)

    def add_subtitle(self, subtitle):
        self.result_dict["subtitle"] = subtitle

    def add_style_number(self, style_number):
        self.result_dict["style_number"] = style_number

    def add_metadata(self, metadata):
        self.result_dict["metadata"] = metadata

    def append_image(self, image):
        if image[:2] == "//":
            image = "https:" + image
        self.result_dict["images"].append(image)

    def file_name(self, url):
        # name = url.split('/')[-1]
        file_name = self.cache_directory + "/" + hashlib.sha256(url.encode("ascii"), usedforsecurity=True).hexdigest() + ".html"
        return file_name

    def load_from_cache(self, url):
        file_name = self.file_name(url)
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                return f.read()

        return None

    def save_to_cache(self, url, text):
        os.makedirs(self.cache_directory, exist_ok=True)
        file_name = self.file_name(url)
        with open(file_name, "w") as f:
            f.write(text)

    def scrape_single_page(self, url, implicitly_wait=5, load_wait=5):
        text = self.load_from_cache(url)
        if text is not None:
            return text
        try:
            with SB(**self.sb_params) as sb:
                sb.driver.get(url)
                sb.driver.implicitly_wait(implicitly_wait)
                sb.wait(load_wait)

                if self.product_page_removes is not None:
                    for remove in self.product_page_removes:
                        sb.driver.execute_script("[...document.querySelectorAll('" + remove + "')].map(el => el.parentNode.removeChild(el))")

                if self.image_slider_container is not None:
                    next_image = sb.driver.find_element(By.CSS_SELECTOR, self.image_slider_container)
                    next_image = next_image.find_element(By.CSS_SELECTOR, self.image_slider_next)
                    sb.driver.execute_script("arguments[0].scrollIntoView();", next_image)
                    WebDriverWait(sb.driver, implicitly_wait).until(ExpectedConditions.element_to_be_clickable(next_image))

                    for i in range(self.n_slides):
                        next_image.click()
                        sb.wait(load_wait)

                self.save_to_cache(url, sb.driver.page_source)
                return sb.driver.page_source
        except selenium.common.exceptions.TimeoutException:
            return self.scrape_single_page(url, implicitly_wait, load_wait)
        except Exception as e:
            return None

    def scrape(self):
        progress_bar = tqdm(total=1000)

        while len(self.urls) > 0:
            url = self.urls.pop(0)
            progress_bar.update()
            progress_bar.set_postfix({"total": len(self.urls)})
            if url["url"] in self.visited:
                continue

            self.visited.add(url["url"])
            url_type = url["type"]
            url = url["url"]
            source = url.split("/")[2].split(".")[1]
            name = url.split('/')[-1]
            dataset_location = "./data/brands/"

            if url_type == "details":
                details = {
                    "url": url,
                    "source": source
                }
                text = self.scrape_single_page(url)
                if text is not None:
                    details = {**self.extract_details(text, url), **details}

                    json_location = dataset_location + f"/{details["source"]}/" + "/".join(details["raw_tags"]) + "/"
                    os.makedirs(json_location, exist_ok=True)
                    json_location = json_location + url.split('/')[-2] + "-" + name + ".json"
                    with open(json_location, "w") as f:
                        json.dump(details, f, indent=4)
            if url_type == "search":
                text = self.scrape_product_search_results(url)

                if type(text) is str:
                    self.urls.extend(list(self.extract_item_links(text)))
                elif isinstance(text, types.GeneratorType):
                    for txt in text:
                        txt = list(self.extract_item_links(txt))
                        self.urls.extend(txt)
                        progress_bar.set_postfix({"total": len(self.urls)})


class ScrapeMultiPageSearch(Scrape):
    def scrape_product_search_results(self, url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=20, current_page=0):
        if current_page != 0:
            new_url = url + "&pageNumber=" + str(current_page + 1)
        else:
            new_url = url

        text = self.load_from_cache(new_url)
        if text is None:
            try:
                with SB(**self.sb_params) as sb:
                    sb.driver.get(new_url)
                    sb.driver.implicitly_wait(implicitly_wait)
                    sb.wait(load_wait)
                    self.save_to_cache(new_url, sb.driver.page_source)
                    yield sb.driver.page_source
            except selenium.common.exceptions.TimeoutException:
                yield from self.scrape_product_search_results(url, implicitly_wait, load_wait, scroll_wait, page, current_page)
            except Exception as e:
                print(e)
                return None
        else:
            yield text

        if current_page < page - 1:
            yield from self.scrape_product_search_results(url, implicitly_wait, load_wait, scroll_wait, page, current_page+1)

        return None
