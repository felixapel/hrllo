import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from image_scrapper import ImageScrapper

# Function to apply theme and font size dynamically
def apply_custom_styles(font_size, theme):
    custom_css = f"""
    <style>
    html, body, [class*="css"] {{
        font-size: {font_size}px !important;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    if theme == "Dark":
        st.markdown(
            """
            <style>
            .css-1d391kg, .css-1fv8s86, .css-14xtw13, .css-2trqyj { background-color: #0E1117; color: #FAFAFA; }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .css-1d391kg, .css-1fv8s86, .css-14xtw13, .css-2trqyj { background-color: #FFFFFF; color: #262730; }
            </style>
            """,
            unsafe_allow_html=True
        )

# Streamlit app
def main():
    st.set_page_config(
        page_title="Web Image Scraper",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Web Image Scraper")

    # Sidebar settings
    with st.sidebar:
        url_start = st.text_input("Enter the URL of the website to scrape images from:")
        num_images = st.number_input("Number of images to display (up to the specified number):", min_value=1, max_value=100, value=10)
        theme = st.selectbox("Choose theme:", ["Light", "Dark"])
        font_size = st.slider("Select font size:", 12, 24, 16)

    # Apply the custom styles
    apply_custom_styles(font_size, theme)

    if st.button("Scrape Images"):
        if url_start:
            with st.spinner('Scraping images...'):
                try:
                    images_data = ImageScrapper.all_image_from_url(url_start)
                    if images_data:
                        st.success(f"Found {len(images_data)} images")
                        images_displayed = 0
                        for img in images_data:
                            if images_displayed >= num_images:
                                break
                            try:
                                img_bytes = BytesIO(img["img_data"])
                                image = Image.open(img_bytes)
                                st.image(image, caption=img["img_desc"], width=200)
                                st.markdown(f"[Download Image]({img['img_url']})")
                                images_displayed += 1
                            except Exception as e:
                                st.warning(f"Error displaying image: {e}")
                    else:
                        st.warning("No images found at the provided URL.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
