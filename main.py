from bs4 import BeautifulSoup
from scrape_mrpoter import main as mr_porter
from scrape_netaporter import main as net_a_porter
import sys


if __name__ == '__main__':
    start = 0
    end = -1
    if len(sys.argv) > 1:
        start = int(sys.argv[1])
    if len(sys.argv) > 2:
        end = int(sys.argv[2])

    with open("data/ProductLinks.html") as file:
        text = file.read()
        soup = BeautifulSoup(text, "html.parser")
        links = list(soup.find_all("a"))[start:end]
        total = len(links)
        for i, link in enumerate(links):
            print("{}/{}".format(i+1, total))
            url = link["href"][29:].split("&")[0]
            brand = url.split("/")[2]
            print(url)
            if brand == "www.mrporter.com":
                print("collecting from mrporter...")
                # mr_porter([
                #     {
                #         "type": "search",
                #         "url": url
                #     }
                # ])
            elif brand == "www.net-a-porter.com":
                print("collecting from net-a-porter...")
                net_a_porter([
                    {
                        "type": "search",
                        "url": url
                    }
                ])
            else:
                print("not a valid brand name")
