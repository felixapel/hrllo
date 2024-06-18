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
def scrape_images(url_start, num_images):
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
    image_count = 0
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
            if image_count >= num_images:  # Check if we have enough images
                break

            page_url = f"{sub_cat_link}?start={page_number * 50}"  # Assuming 50 items per page
            soup_page = establish_connection(page_url)
            if not soup_page:
                continue

            h1_title = soup_page.find('h1').text.strip() if soup_page.find('h1') else "No title"

            entries = soup_page.find_all('div', class_='pg-box3')
            for entry in entries:  # No limit here, we will handle the limit outside
                if image_count >= num_images:  # Check if we have enough images
                    break

                entry_links = entry.find_all('a')
                for link in entry_links:
                    if image_count >= num_images:  # Check if we have enough images
                        break

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
                        image_count += 1
                        if image_count >= num_images:  # Check if we have enough images
                            return final_data
                        time.sleep(random.uniform(1, time_sleep_max))  # Random sleep to avoid being blocked

    return final_data

# Function to create a mosaic gallery
def create_mosaic_gallery(image_data):
    images_html = ""
    for data in image_data:
        if data['Image Link'] != "No image found":
            images_html += f"""
            <div class="gallery-item">
                <img src="{data['Image Link']}" alt="{data['Description Title']}" title="{data['Description']}" />
                <div class="desc">{data['Description Title']}</div>
            </div>
            """
    gallery_css = """
    <style>
    .gallery {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .gallery-item {
        flex: 1 0 21%; /* Adjust the percentage to control the number of items per row */
        box-sizing: border-box;
        padding: 5px;
        border: 1px solid #ddd;
    }
    .gallery-item img {
        width: 100%;
        height: auto;
    }
    .gallery-item .desc {
        text-align: center;
        padding: 5px;
    }
    </style>
    """
    st.components.v1.html(f"{gallery_css}<div class='gallery'>{images_html}</div>", height=600, scrolling=True)

# Streamlit app
def main():
    st.title("Web Image Scraper")

    url_start = st.text_input("Enter the URL of the website to scrape images from:", "https://www.lag-sb-rlp.de/projekte/bildergalerie-leichte-sprache")
    num_images = st.number_input("Enter the number of images to scrape:", min_value=1, max_value=100, value=10)

    if st.button("Scrape Images"):
        if url_start:
            with st.spinner('Scraping images...'):
                final_data = scrape_images(url_start, num_images)
                if final_data:
                    st.success(f"Found {len(final_data)} images")
                    create_mosaic_gallery(final_data)
                else:
                    st.warning("No images found at the provided URL.")
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
