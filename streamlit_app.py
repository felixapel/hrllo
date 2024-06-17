import streamlit as st
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import time
import random
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

# Base URL and starting point
url_base = "https://www.lag-sb-rlp.de/"

# Maximum time to sleep between requests
time_sleep_max = 2

# Function to scrape images from a given URL
def scrape_images(url_start):
    response_start = requests.get(url_start)
    soup = BeautifulSoup(response_start.text, "html.parser")
    category_containers = soup.find_all('div', class_='pg-legend')

    all_links = []
    # Extract all category links
    for category in category_containers:
        links = category.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(url_base, href)
                all_links.append(full_url)

    final_data = []

    # Process each category link
    for sub_cat_link in all_links[:2]:  # Limiting to first two for demo
        response_category = requests.get(sub_cat_link)
        soup_category = BeautifulSoup(response_category.text, "html.parser")
        try:
            max_pages = int(soup_category.find('div', class_='counter pull-right').text.split()[-1])
            pages_to_fetch = range(max_pages)
        except Exception:
            pages_to_fetch = [0]

        # Fetch each page in the category
        for page_number in pages_to_fetch:
            page_url = f"{sub_cat_link}?start={page_number * 50}"  # Assuming 50 items per page
            response_page = requests.get(page_url)
            soup_page = BeautifulSoup(response_page.text, "html.parser")
            h1_title = soup_page.find('h1').text.strip() if soup_page.find('h1') else "No title"

            entries = soup_page.find_all('div', class_='pg-box3')
            for entry in entries:
                entry_links = entry.find_all('a')
                for link in entry_links:
                    href = link.get('href')
                    if href and not href.startswith('http'):
                        full_url = urljoin(url_base, href)
                        response_detail = requests.get(full_url)
                        soup_detail = BeautifulSoup(response_detail.text, "html.parser")

                        desc_div = soup_detail.find('div', class_='pg-dv-desc no-popup')
                        desc_title = desc_div.get_text(strip=True) if desc_div else "No description title"
                        desc_p = desc_div.find('p') if desc_div else None
                        desc = desc_p.get_text(strip=True) if desc_p else "No description"
                        image_tag = soup_detail.find('div', id='phocaGalleryImageBox').find('img')
                        image_link = urljoin(url_base, image_tag['src']) if image_tag and 'src' in image_tag.attrs else "No image found"

                        final_data.append({
                            'Title': h1_title,
                            'Description Title': desc_title,
                            'Description': desc,
                            'Link': full_url,
                            'Image Link': image_link
                        })
                        time.sleep(random.uniform(1, time_sleep_max))  # Random sleep to avoid being blocked

    return final_data

# Streamlit app
def main():
    # Page title
    st.title("Web Image Scraper")

    # URL input box
    url_start = st.text_input("Enter the URL of the website to scrape images from:", "https://www.lag-sb-rlp.de/projekte/bildergalerie-leichte-sprache")

    # Theme selection
    theme = st.selectbox("Choose theme:", ["Light", "Dark"])

    # Apply theme
    if theme == "Dark":
        st.write('<style>body{background-color: #0E1117; color: #FAFAFA;}</style>', unsafe_allow_html=True)
    else:
        st.write('<style>body{background-color: #FAFAFA; color: #0E1117;}</style>', unsafe_allow_html=True)

    # Scrape images and display gallery
    if st.button("Scrape Images"):
        if url_start:
            with st.spinner('Scraping images...'):
                final_data = scrape_images(url_start)
                if final_data:
                    st.success(f"Found {len(final_data)} images")
                    for data in final_data:
                        st.image(data['Image Link'], caption=f"{data['Description Title']}\n{data['Description']}")
                else:
                    st.warning("No images found at the provided URL.")
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
