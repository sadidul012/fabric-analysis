import glob
import json
import os.path
import sys
from io import BytesIO
import requests
import tqdm
from PIL import Image
import pillow_avif


def download_image(url, location, nth):
    try:
        image_location = location[:-4] + f"-image-{nth}.png"
        print(image_location)
        if not os.path.exists(image_location):
            header = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
                "sec-ch-ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            }

            params = {'page': 0}
            response = requests.get(url, headers=header, params=params)
            img = Image.open(BytesIO(response.content))
            img.save(location[:-4] + f"-image-{nth}.png")
        return 0
    except Exception as e:
        print(url)
        print(e)
        return 1


def main(start=0, end=-1):
    products = list(glob.glob("data/brands/mrporter/**/*.json", recursive=True))
    products.sort()
    progress = tqdm.tqdm(products[start:end])
    error = 0
    total = 0
    for product in progress:
        data = json.load(open(product))
        for i, image in enumerate(data["images"]):
            error += download_image(image, product, i)
            total += 1
            progress.set_postfix(dict(error=error, total=total))


if __name__ == '__main__':
    _start = 0
    _end = -1
    if len(sys.argv) > 1:
        _start = int(sys.argv[1])
    if len(sys.argv) > 2:
        _end = int(sys.argv[2])

    main(_start, _end)
