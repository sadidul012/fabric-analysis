import re

from bs4 import BeautifulSoup
from scrape import ScrapeMultiPageSearch


class ScrapeMrPorter(ScrapeMultiPageSearch):
    def extract_details(self, text, url):
        soup = BeautifulSoup(text, "html.parser")
        basic_info = soup.find("div", {"class": "ProductDetails88__basicInfo"})

        metas = soup.find_all('meta')
        metadata = {}
        for m in metas:
            if m.get('name') is not None:
                metadata[m.get('name')] = m.get('content')

            if m.get('property') is not None:
                metadata[m.get('property')] = m.get('content')

        self.add_metadata(metadata)

        self.add_name(basic_info.select_one("h1.ProductInformation88__designer.ProductInformation88__designer--stickyCta").text)
        self.add_subtitle(basic_info.select_one("p.ProductInformation88__name.ProductInformation88__name--stickyCta").text)
        self.add_price(basic_info.select_one("span.PriceWithSchema10__value.PriceWithSchema10__value--details").text)
        self.add_raw_tags(url.split("product")[1].split("/")[1:-1])

        info = soup.select_one("div.EditorialAccordion88.EditorialAccordion88--pdpAccordion.ProductDetails88__editorialAccordion")
        self.add_description(info.select_one("div.AccordionSection3#EDITORS_NOTES div.content").text)
        self.add_style_number(soup.select_one("div.ProductDetails88 div.PartNumber88.ProductDetails88__partNumber").text)

        sources = soup.select("div.ImageCarousel88__viewport li.ImageCarousel88__slide img")
        for source in sources:
            self.append_image(source["src"])

        # print(len(soup.select("div.ImageCarousel88__viewport li.ImageCarousel88__slide img[src]")))
        lis = info.select("div.AccordionSection3#SIZE_AND_FIT div.content li") + info.select("div.AccordionSection3#DETAILS_AND_CARE div.content li")
        for li in lis:
            if re.match("Model measures(.)*", li.text):
                self.add_size(li.text)
            else:
                self.append_attribute(li.text)

        # print(json.dumps(self.result_dict, indent=4))
        return self.return_result_dict()

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
                    "url": "https://www.mrporter.com" + result["href"] if result["href"][0] == "/" else result["href"]
                }
        return None


def main(urls):
    scrape = ScrapeMrPorter(
        urls,
        image_slider_container="div.ImageCarousel88__mainCarousel.ImageCarousel88__mainCarousel--allow2ndLevelZoom",
        image_slider_next="button.ImageCarousel88__next",
        n_slides=10
    )
    scrape.scrape()


if __name__ == '__main__':
    main([
        {
            "type": "search",
            "url": "https://www.mrporter.com/en-us/mens/clothing?facet=ads_f11001_ntk_cs%253A%2522ACNE%2BSTUDIOS%2522&facet=ads_f11001_ntk_cs%253A%2522A.P.C.%2522&facet=ads_f11001_ntk_cs%253A%2522AMI%2BPARIS%2522&facet=ads_f11001_ntk_cs%253A%2522AMIRI%2522&facet=ads_f11001_ntk_cs%253A%2522BALENCIAGA%2522&facet=ads_f11001_ntk_cs%253A%2522BODE%2522&facet=ads_f11001_ntk_cs%253A%2522BOTTEGA%2BVENETA%2522&facet=ads_f11001_ntk_cs%253A%2522BRUNELLO%2BCUCINELLI%2522&facet=ads_f11001_ntk_cs%253A%2522LEMAIRE%2522&facet=ads_f11001_ntk_cs%253A%2522OUR%2BLEGACY%2522"
        },
        # {
        #     "type": "details",
        #     "url": "https://www.mrporter.com/en-us/mens/product/brunello-cucinelli/clothing/plain-t-shirts/silk-and-cotton-blend-jersey-t-shirt/1647597341958447"
        # }
    ])

