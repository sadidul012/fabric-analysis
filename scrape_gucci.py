from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from seleniumbase import SB
from selenium.webdriver.common.by import By

from scrape import Scrape
from scrape_gucci_helpers import find_gucci_item_links, extract_gucci


class ScrapeGucci(Scrape):
    def scrape_product_search_results(self, url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=2):
        text = self.load_from_cache(url)
        if text is not None:
            return text

        with SB(**self.sb_params) as sb:
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
                    return sb.driver.page_source

                try:
                    self.save_to_cache(url, sb.driver.page_source)
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
                    return sb.driver.page_source

    def extract_details(self, text, url):
        return extract_gucci(text, url)

    def extract_item_links(self, text):
        return find_gucci_item_links(text)


def main():
    urls = [
        # {
        #     "type": "details",
        #     "url": "https://www.gucci.com/us/en/pr/men/bags-for-men/messengers-crossbody-bags-for-men/gucci-b-large-shoulder-bag-p-801041AZB5Z1060"
        # },
        {
            "type": "details",
            "url": "https://www.gucci.com/us/en/pr/men/bags-for-men/messengers-crossbody-bags-for-men/gucci-b-large-shoulder-bag-p-801041AZB5Z1060"
        },
        {
            "type": "search",
            "url": "https://www.gucci.com/us/en/st/newsearchpage?searchString=bag&search-cat=header-search"
        },
    ]
    scrape = ScrapeGucci(urls)
    scrape.scrape()


if __name__ == '__main__':
    main()
