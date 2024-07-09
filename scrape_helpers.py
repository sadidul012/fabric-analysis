import re
from bs4 import BeautifulSoup


def extract_details(details):
    details_dict = {
        "style_number": details.find("div", {"class": "style-number-title"}).text.strip().encode("ascii",
                                                                                                 "ignore").decode(
            "ascii")
    }

    detail = details.find("div", {"class": "product-detail"})
    details_dict["description"] = detail.find("p").text.strip()
    lis = detail.find_all("li")
    details_list = {"attributes": []}
    for li in lis:
        if re.match("(.)*W(.)*H(.)*D(.)*", li.text):
            details_list["size"] = li.text
        elif re.match("Made in(.)*", li.text):
            details_list["country"] = li.text
        elif re.match("Weight(.)*", li.text):
            details_list["weight"] = li.text
        else:
            details_list["attributes"].append(li.text)

    details_dict["attributes"] = details_list
    return details_dict


def extract_product_box(product_info_box):
    details_dict = {}
    header = product_info_box.find("div", {"class": "productnameandprice-container-standard"})
    details_dict["name"] = header.find("h1", {"class": "product-detail-product-name"}).text.strip()
    details_dict["price"] = header.find("div", {"class": "product-detail-price-column"}).text.strip().encode("ascii",
                                                                                                             "ignore").decode(
        "ascii")

    shipping = product_info_box.find("div", {"class": "shipping-info"})
    details_dict["shipping_title"] = shipping.find("p", {"class": "title"}).text.strip()
    details_dict["shipping_subtitle"] = shipping.find("div", {"class": "subtitle"}).text.strip()

    return details_dict


def extract_product_details(text):
    soup = BeautifulSoup(text, "html.parser")
    details_dict = extract_details(soup.find(id="accordion-product-details"))

    details_dict = {**details_dict, **extract_product_box(soup.find("div", {"class": "product-info-box"}))}
    details_dict["images"] = []
    for p in soup.find("div", {"class": "slick-track"}).find_all("picture"):
        details_dict["images"].append("https:" + p.find("img")["srcset"].replace("490x490", "2400x2400"))

    details_dict["tags"] = [x.text.strip().encode("ascii", "ascii").decode("ascii") for x in
                            soup.find("div", "breadcrumb-icons-bg").find("nav", {"class": "breadcrumb"}).find_all("li")]

    links = soup.find_all("a", href=True)
    urls = []

    for link in links:
        split = link["href"].split("/")
        if len(split) < 4:
            continue

        if split[3] in ["ca", "pr"]:
            urls.append({
                "type": split[3],
                "url": "https://www.gucci.com" + link["href"]
            })

    return details_dict, urls


def find_links(text):
    soup = BeautifulSoup(text, "html.parser")
    result_grid = soup.find("div", {"class": "SearchResultGrid_productsGrid"})
    result_grid = result_grid.find_all("div", {"class": "SearchResultGrid_productsCell"})
    for result in result_grid:
        result = result.find("a", {"class": "ProductCard_productCard"})
        split = result["href"].split("/")

        if split[3] in ["ca", "pr"]:
            yield {
                "type": split[3],
                "url": "https://www.gucci.com" + result["href"] if result["href"][0] == "/" else result["href"]
            }

    return None
