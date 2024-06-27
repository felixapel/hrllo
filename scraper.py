import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import time
import random
from urllib.parse import urljoin
import pandas as pd

# Base URL and starting point
url_base = "https://www.lag-sb-rlp.de/"

def scrape_images(url_start):
    time_sleep_max = 2
    response_start = requests.get(url_start)
    soup = BeautifulSoup(response_start.text, "html.parser")
    category_containers = soup.find_all('div', class_='pg-legend')

    all_links = []
    # Extract all category links
    for category in tqdm(category_containers, desc='Gathering Categories'):
        links = category.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(url_base, href)
                all_links.append(full_url)
                print(f"Found category link: {full_url}")

    final_data = []

    # Process each category link
    for sub_cat_link in tqdm(all_links[:2], desc='Processing Categories'):  # Limiting to first two for demo
        response_category = requests.get(sub_cat_link)
        soup_category = BeautifulSoup(response_category.text, "html.parser")
        try:
            max_pages = int(soup_category.find('div', class_='counter pull-right').text.split()[-1])
            pages_to_fetch = range(max_pages)
        except Exception:
            pages_to_fetch = [0]

        # Fetch each page in the category
        for page_number in tqdm(pages_to_fetch, desc='Processing Pages'):
            page_url = f"{sub_cat_link}?start={page_number * 50}"  # Assuming 50 items per page
            response_page = requests.get(page_url)
            soup_page = BeautifulSoup(response_page.text, "html.parser")
            h1_title = soup_page.find('h1').text.strip()

            entries = soup_page.find_all('div', class_='pg-box3')
            for entry in tqdm(entries, desc='Processing Entries'):
                entry_links = entry.find_all('a')
                for link in entry_links:
                    href = link.get('href')
                    if href and not href.startswith('http'):
                        full_url = urljoin(url_base, href)
                        response_detail = requests.get(full_url)
                        soup_detail = BeautifulSoup(response_detail.text, "html.parser")

                        desc_title = soup_detail.find('div', class_='pg-dv-desc no-popup').get_text(strip=True)
                        desc = soup_detail.find('div', class_='pg-dv-desc no-popup').find('p').get_text(strip=True)
                        image_tag = soup_detail.find('div', id='phocaGalleryImageBox').find('img')
                        if image_tag and 'src' in image_tag.attrs:
                            image_link = urljoin(url_base, image_tag['src'])
                        else:
                            image_link = "No image found"

                        final_data.append({
                            'Title': h1_title,
                            'Description Title': desc_title,
                            'Description': desc,
                            'Link': full_url,
                            'Image Link': image_link
                        })
                        print(f"Collected data for: {desc_title}")

            time.sleep(random.uniform(1, time_sleep_max))  # Random sleep to avoid being blocked

    # Save the final data to an Excel file
    df = pd.DataFrame(final_data)
    excel_file = 'Scraped-Images_DataFrame.xlsx'
    df.to_excel(excel_file, index=False)
    print(f"Data successfully exported to {excel_file}")
    return final_data
