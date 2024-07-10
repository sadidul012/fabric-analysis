import json
import os

from seleniumbase import SB
from tqdm import tqdm


class Scrape:
    def __init__(self, urls):
        self.cache_directory = "./data/temp/"
        os.makedirs(self.cache_directory, exist_ok=True)
        # self.sb_params = dict(uc=True, block_images=True, page_load_strategy="none", skip_js_waits=False, maximize=True, uc_subprocess=True)
        self.sb_params = dict(uc=True, maximize=True)

        # self.sb = SB(**self.sb_params)
        self.urls = urls
        self.visited = set()

    def file_name(self, url):
        name = url.split('/')[-1]
        file_name = self.cache_directory + "/" + url.split('/')[-2] + "-" + name + ".html"

        return file_name

    def load_from_cache(self, url):
        file_name = self.file_name(url)
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                return f.read()

        return None

    def save_to_cache(self, url, text):
        file_name = self.file_name(url)
        with open(file_name, "w") as f:
            f.write(text)
            print(f"saved {file_name}")

    def scrape_single_page(self, url, implicitly_wait=5, load_wait=5):
        text = self.load_from_cache(url)
        if text is not None:
            return text

        with SB(**self.sb_params) as sb:
            sb.driver.get(url)
            sb.driver.implicitly_wait(implicitly_wait)
            sb.wait(load_wait)

            self.save_to_cache(url, sb.driver.page_source)
            return sb.driver.page_source

    def scrape_product_search_results(self, url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=None):
        return []

    def extract_details(self, text, url):
        return {}

    def extract_item_links(self, text):
        return []

    def scrape(self):
        progress_bar = tqdm(total=len(self.urls))

        while len(self.urls) > 0:
            url = self.urls.pop(0)
            progress_bar.update()
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
                details = {**self.extract_details(text, url), **details}

                # print(json.dumps(details, indent=4))

                json_location = dataset_location + f"/{details["source"]}/" + "/".join(details["raw_tags"]) + "/"
                os.makedirs(json_location, exist_ok=True)
                json_location = json_location + url.split('/')[-2] + "-" + name + ".json"
                with open(json_location, "w") as f:
                    json.dump(details, f, indent=4)
                print(details)
            if url_type == "search":
                text = self.scrape_product_search_results(url, page=2)
                links = list(self.extract_item_links(text))
                print(links)
                # urls.extend(list(links))
