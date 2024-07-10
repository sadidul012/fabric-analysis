import re

from bs4 import BeautifulSoup
from seleniumbase import SB

from scrape import Scrape


class ScrapeNetAPorter(Scrape):
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
            except Exception as e:
                print(e)
                return None
        else:
            yield text

        if current_page < page - 1:
            yield from self.scrape_product_search_results(url, implicitly_wait, load_wait, scroll_wait, page, current_page+1)

        return None

    def extract_details(self, text, url):
        soup = BeautifulSoup(text, "html.parser")
        basic_info = soup.find("div", {"class": "ProductDetails87__basicInfo"})

        metas = soup.find_all('meta')
        metadata = {}
        for m in metas:
            if m.get('name') is not None:
                metadata[m.get('name')] = m.get('content')

            if m.get('property') is not None:
                metadata[m.get('property')] = m.get('content')

        self.add_metadata(metadata)
        self.add_raw_tags(url.split("product")[1].split("/")[1:-1])

        self.add_name(basic_info.select_one("h1.ProductInformation87__designer").text)
        self.add_subtitle(basic_info.select_one("p.ProductInformation87__name").text)
        self.add_price(basic_info.select_one("span.PriceWithSchema10__value.PriceWithSchema10__value--details").text)

        info = soup.select_one("div.EditorialAccordion87.EditorialAccordion87--pdpAccordion.ProductDetails87__editorialAccordion")
        self.add_description(info.select_one("div.AccordionSection3#EDITORS_NOTES div.content").text)
        self.add_style_number(soup.select_one("div.ProductDetails87 div.PartNumber87.ProductDetails87__partNumber").text)

        sources = soup.select("div.ImageCarousel87__viewport li.ImageCarousel87__slide img")
        for source in sources:
            self.append_image(source["src"])

        # # print(len(soup.select("div.ImageCarousel87__viewport li.ImageCarousel87__slide img[src]")))
        lis = info.select("div.AccordionSection3#SIZE_AND_FIT div.content li") + info.select("div.AccordionSection3#DETAILS_AND_CARE div.content li")
        for li in lis:
            if re.match("Model measures(.)*", li.text):
                self.add_size(li.text)
            else:
                self.append_attribute(li.text)

        return self.result_dict

    def extract_item_links(self, text):
        soup = BeautifulSoup(text, "html.parser")
        result_grid = soup.find("div", {"class": "ProductGrid53"})
        result_grid = result_grid.find_all("div", {"class": "ProductList0__productItemContainer"})
        for result in result_grid:
            result = result.find("a")
            split = result["href"].split("/")
            if split[3] == "product":
                yield {
                    "type": "details",
                    "url": "https://www.net-a-porter.com" + result["href"] if result["href"][0] == "/" else result["href"]
                }
        return None


def main():
    urls = [
        {
            "type": "search",
            "url": "https://www.net-a-porter.com/en-us/shop/clothing?facet=ads_f10003_ntk_cs%253A%2522BOTTEGA%2BVENETA%2522&facet=ads_f10003_ntk_cs%253A%2522BRUNELLO%2BCUCINELLI%2522&facet=ads_f10003_ntk_cs%253A%2522CHLO%25C3%2589%2522&facet=ads_f10003_ntk_cs%253A%2522CULT%2BGAIA%2522&facet=ads_f10003_ntk_cs%253A%2522ELIE%2BSAAB%2522&facet=ads_f10003_ntk_cs%253A%2522GANNI%2522&facet=ads_f10003_ntk_cs%253A%2522JACQUEMUS%2522&facet=ads_f10003_ntk_cs%253A%2522THE%2BROW%2522&facet=ads_f10003_ntk_cs%253A%2522MARNI%2522&facet=ads_f10003_ntk_cs%253A%2522MAX%2BMARA%2522"
        },
        # {
        #     "type": "details",
        #     "url": "https://www.net-a-porter.com/en-us/shop/product/the-row/clothing/blazers/marina-oversized-wool-blazer/1647597332737226"
        # }
    ]
    # &pageNumber=2
    scrape = ScrapeNetAPorter(
        urls,
        image_slider_container="div.ImageCarousel87__mainCarousel.ImageCarousel87__mainCarousel--allow2ndLevelZoom",
        image_slider_next="button.ImageCarousel87__next",
        n_slides=10,
        product_page_removes=[".Overlay9__cover.Overlay9__cover--recentlyViewed"]
    )
    scrape.scrape()


if __name__ == '__main__':
    main()

