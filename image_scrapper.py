import requests
from bs4 import BeautifulSoup
import random

class ImageScrapper:

    @staticmethod
    def all_image_from_url(url):
        try:
            request = requests.get(url)
            html_content = request.content
            soup = BeautifulSoup(html_content, "html.parser")
            elements = soup.find_all("img")
            images_data = []

            for i, element in enumerate(elements):
                img_url = element.get("src")
                if img_url and img_url.startswith("http"):
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img_data = response.content
                        img_desc = element.get("alt", "No description available")
                        images_data.append({
                            "img_data": img_data,
                            "img_url": img_url,
                            "img_desc": img_desc
                        })
            return images_data
        except Exception as e:
            raise e
