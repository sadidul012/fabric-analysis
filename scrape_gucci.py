import json
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from seleniumbase import SB
from time import time
from datetime import timedelta
from selenium.webdriver.common.by import By
from scrape_helpers import extract_product_details, find_links


def scrape_website(url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=None):
    # noinspection PyArgumentList
    with SB(uc=True, maximize=True) as sb:
        # with SB(uc=True, block_images=True, page_load_strategy="none", skip_js_waits=False, maximize=True, uc_subprocess=True) as sb:
        sb.driver.get(url)
        sb.driver.implicitly_wait(implicitly_wait)
        sb.wait(load_wait)

        try:
            print("clicking cookies ok..")
            # elems = sb.find_elements(by=By.XPATH, value="//a[@href]")
            ok = sb.driver.find_element(By.CSS_SELECTOR, "button#onetrust-accept-btn-handler")
            sb.driver.execute_script("arguments[0].scrollIntoView();", ok)
            WebDriverWait(sb.driver, scroll_wait).until(ExpectedConditions.element_to_be_clickable(ok))
            ok.click()
            # sb.driver.implicitly_wait(3)
            sb.wait(load_wait)
        except Exception as e:
            print(e)

        try:
            sb.driver.execute_script("[...document.querySelectorAll('.ReactModal__Overlay.ReactModal__Overlay--after-open')].map(el => el.parentNode.removeChild(el))")
            sb.driver.execute_script("[...document.querySelectorAll('.Header-styles__FixedContainer-sc-6ebd2a32-1.hvNSQV')].map(el => el.parentNode.removeChild(el))")
            sb.driver.execute_script("[...document.querySelectorAll('.FilterAndSortByBar_controls')].map(el => el.parentNode.removeChild(el))")
        except Exception as e:
            print(e)

        i = 0
        while True:
            i += 1
            if page is not None and i > page:
                break

            try:
                yield sb.driver.page_source
                sb.wait(load_wait)

                load_more = sb.driver.find_element(By.CSS_SELECTOR, "div.SearchResults_loadMoreBar")
                load_more = load_more.find_element(By.CSS_SELECTOR, "g-cta")
                sb.driver.execute_script("arguments[0].scrollIntoView();", load_more)
                WebDriverWait(sb.driver, scroll_wait).until(ExpectedConditions.element_to_be_clickable(load_more))
                sb.wait(scroll_wait)
                load_more.click()
                sb.wait(scroll_wait)
            except Exception as e:
                print(e)
                break

        return None


def main():
    urls = [
        # {
        #     "type": "pr",
        #     "url": "https://www.gucci.com/us/en/pr/men/bags-for-men/messengers-crossbody-bags-for-men/gucci-b-large-shoulder-bag-p-801041AZB5Z1060"
        # },
        {
            "type": "pr",
            "url": "https://www.gucci.com/us/en/pr/men/bags-for-men/messengers-crossbody-bags-for-men/gucci-b-large-shoulder-bag-p-801041AZB5Z1060"
        },
        # {
        #     "type": "search",
        #     "url": "https://www.gucci.com/us/en/st/newsearchpage?searchString=bag&search-cat=header-search"
        # }
    ]
    visited = set()
    while len(urls) > 0:
        url = urls.pop(0)

        if url["url"] in visited:
            continue

        visited.add(url["url"])
        t = url["type"]
        url = url["url"]
        name = url.split('/')[-1]
        file_name = "./data/temp/"
        dataset_location = "./data/brands/"
        os.makedirs(file_name, exist_ok=True)
        file_name += url.split('/')[-2] + "-" + name + ".html"
        print(file_name)

        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                text = f.read()
        else:
            print("scraping " + url)
            start_time = time()
            text = scrape_website(url)
            for t in text:
                with open(file_name, "w") as f:
                    f.write(t)
                    print("saved")
            print(timedelta(seconds=time() - start_time))

        if t == "pr":
            details, _ = extract_product_details(text)
            details["raw_tags"] = url.split("pr")[1].split("/")[1:-1]
            details["url"] = url
            details["source"] = url.split("/")[2].split(".")[1]
            # print(json.dumps(details, indent=4))

            json_location = dataset_location + f"/{details["source"]}/" + "/".join(details["raw_tags"]) + "/"
            os.makedirs(json_location, exist_ok=True)
            json_location = json_location + url.split('/')[-2] + "-" + name + ".json"
            with open(json_location, "w") as f:
                json.dump(details, f, indent=4)

        if t == "search":
            links = find_links(text)
            # urls.extend(list(links))
            print(len(list(links)))


if __name__ == '__main__':
    main()
