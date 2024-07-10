import json
import re

from bs4 import BeautifulSoup
from seleniumbase import SB

from scrape import Scrape


class ScrapeMrPorter(Scrape):
    def scrape_product_search_results(self, url, implicitly_wait=5, load_wait=5, scroll_wait=5, page=2, current_page=0):
        if current_page != 0:
            new_url = url + "&pageNumber=" + str(current_page + 1)
        else:
            new_url = url

        text = self.load_from_cache(new_url)
        if text is None:
            with SB(**self.sb_params) as sb:
                sb.driver.get(new_url)
                sb.driver.implicitly_wait(implicitly_wait)
                sb.wait(load_wait)
                self.save_to_cache(new_url, sb.driver.page_source)
                yield sb.driver.page_source
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

        self.add_name(basic_info.select_one("h1.ProductInformation87__designer.ProductInformation87__designer--stickyCta").text)
        self.add_subtitle(basic_info.select_one("p.ProductInformation87__name.ProductInformation87__name--stickyCta").text)
        self.add_price(basic_info.select_one("span.PriceWithSchema10__value.PriceWithSchema10__value--details").text)
        self.add_raw_tags(url.split("product")[1].split("/")[1:-1])

        info = soup.select_one("div.EditorialAccordion87.EditorialAccordion87--pdpAccordion.ProductDetails87__editorialAccordion")
        self.add_description(info.select_one("div.AccordionSection3#EDITORS_NOTES div.content").text)
        self.add_style_number(soup.select_one("div.ProductDetails87 div.PartNumber87.ProductDetails87__partNumber").text)
        lis = info.select("div.AccordionSection3#SIZE_AND_FIT div.content li") + info.select("div.AccordionSection3#DETAILS_AND_CARE div.content li")

        # sources = soup.select("div.ImageCarousel87__viewport li.ImageCarousel87__slide img")
        # # print(sources["srcset"].split())
        # print(len(sources))
        # for source in sources:
        #     print(source)

        # print(len(soup.select("div.ImageCarousel87__viewport li.ImageCarousel87__slide img[src]")))
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
                    "url": "https://www.mrporter.com/" + result["href"] if result["href"][0] == "/" else result["href"]
                }
        return None


def main():
    urls = [
        # {
        #     "type": "search",
        #     "url": "https://www.mrporter.com/en-us/mens/clothing?facet=ads_f11001_ntk_cs%253A%2522ACNE%2BSTUDIOS%2522&facet=ads_f11001_ntk_cs%253A%2522A.P.C.%2522&facet=ads_f11001_ntk_cs%253A%2522AMI%2BPARIS%2522&facet=ads_f11001_ntk_cs%253A%2522AMIRI%2522&facet=ads_f11001_ntk_cs%253A%2522BALENCIAGA%2522&facet=ads_f11001_ntk_cs%253A%2522BODE%2522&facet=ads_f11001_ntk_cs%253A%2522BOTTEGA%2BVENETA%2522&facet=ads_f11001_ntk_cs%253A%2522BRUNELLO%2BCUCINELLI%2522&facet=ads_f11001_ntk_cs%253A%2522LEMAIRE%2522&facet=ads_f11001_ntk_cs%253A%2522OUR%2BLEGACY%2522"
        # },
        {
            "type": "details",
            "url": "https://www.mrporter.com/en-us/mens/product/brunello-cucinelli/clothing/plain-t-shirts/silk-and-cotton-blend-jersey-t-shirt/1647597341958447"
        }
    ]
    # &pageNumber=2
    scrape = ScrapeMrPorter(urls)
    scrape.scrape()


if __name__ == '__main__':
    main()

