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

# Function to establish connection and get BeautifulSoup object
def establish_connection(link):
    try:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup
    except Exception as e:
        st.error(f"Connection to {link} cannot be established. Error: {e}")
        return None

# Function to save data to a file and provide download option
def save_to_file(data, fname):
    if data:
        st.download_button(
            label="Download Data",
            data='\n'.join(data),
            file_name=fname,
            key="download_button",
        )
    else:
        st.write("No data found.")

# Function to print data on button click
def button_print(data, statement):
    if data:
        if st.button(statement):
            st.write(data)

# Function to scrape images and descriptions
def scrape_images(url_start):
    soup_start = establish_connection(url_start)
    if not soup_start:
        return []

    category_containers = soup_start.find_all('div', class_='pg-legend')

    all_links = []
    for category in category_containers:
        links = category.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(url_base, href)
                all_links.append(full_url)

    final_data = []
    for sub_cat_link in all_links[:2]:  # Limiting to first two for demo
        soup_category = establish_connection(sub_cat_link)
        if not soup_category:
            continue

        try:
            max_pages = int(soup_category.find('div', class_='counter pull-right').text.split()[-1])
            pages_to_fetch = range(min(max_pages, 2))  # Limit pages to fetch to avoid excessive data
        except Exception:
            pages_to_fetch = [0]

        for page_number in pages_to_fetch:
            page_url = f"{sub_cat_link}?start={page_number * 50}"  # Assuming 50 items per page
            soup_page = establish_connection(page_url)
            if not soup_page:
                continue

            h1_title = soup_page.find('h1').text.strip() if soup_page.find('h1') else "No title"

            entries = soup_page.find_all('div', class_='pg-box3')
            for entry in entries[:10]:  # Limit entries per page to 10
                entry_links = entry.find_all('a')
                for link in entry_links:
                    href = link.get('href')
                    if href and not href.startswith('http'):
                        full_url = urljoin(url_base, href)
                        soup_detail = establish_connection(full_url)
                        if not soup_detail:
                            continue

                        desc_div = soup_detail.find('div', class_='pg-dv-desc no-popup')
                        desc_title = desc_div.get_text(strip=True) if desc_div else "No description title"
                        desc_p = desc_div.find('p') if desc_div else None
                        desc = desc_p.get_text(strip=True) if desc_p else "No description"

                        image_tag = soup_detail.find('div', id='phocaGalleryImageBox')
                        image_link = "No image found"
                        if image_tag:
                            img = image_tag.find('img')
                            if img and 'src' in img.attrs:
                                image_link = urljoin(url_base, img['src'])

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
    st.title("Web Image Scraper")

    url_start = st.text_input("Enter the URL of the website to scrape images from:", "https://www.lag-sb-rlp.de/projekte/bildergalerie-leichte-sprache")

    if st.button("Scrape Images"):
        if url_start:
            with st.spinner('Scraping images...'):
                final_data = scrape_images(url_start)
                if final_data:
                    st.success(f"Found {len(final_data)} images")
                    displayed_count = 0
                    for data in final_data:
                        if displayed_count >= 10:  # Limit the number of displayed images to 10
                            break
                        if data['Image Link'] == "No image found":
                            continue
                        try:
                            image_response = requests.get(data['Image Link'])
                            img = Image.open(BytesIO(image_response.content))
                            st.image(img, caption=f"{data['Description Title']}\n{data['Description']}")
                            displayed_count += 1
                        except Exception as e:
                            st.error(f"Error loading image: {e}")
                else:
                    st.warning("No images found at the provided URL.")
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
