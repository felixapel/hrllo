import streamlit as st
from scrapper import scrape_images  # Import the scrape_images function
from PIL import Image
from io import BytesIO
import requests

# Streamlit app
def main():
    st.title("Web Image Scraper")

    url_start = st.text_input("Enter the URL of the website to scrape images from:", "https://www.lag-sb-rlp.de/projekte/bildergalerie-leichte-sprache")

    theme = st.selectbox("Choose theme:", ["Light", "Dark"])

    if theme == "Dark":
        st.markdown(
            """
            <style>
            .css-18e3th9 {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .stButton button {
                background-color: #5c6bc0;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            .css-18e3th9 {
                background-color: #FAFAFA;
                color: #0E1117;
            }
            .stButton button {
                background-color: #5c6bc0;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)

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
