import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from image_scrapper import ImageScrapper

# Set the initial page config
st.set_page_config(
    page_title="Web Image Scraper",
    page_icon="🖼️",
    layout="wide"
)

# Function to switch theme
def switch_theme(theme):
    if theme == "Light":
        st.config.set_option("theme.base", "light")
        st.config.set_option("theme.primaryColor", "#FF4B4B")
        st.config.set_option("theme.backgroundColor", "#FFFFFF")
        st.config.set_option("theme.secondaryBackgroundColor", "#F0F2F6")
        st.config.set_option("theme.textColor", "#31333F")
    else:
        st.config.set_option("theme.base", "dark")
        st.config.set_option("theme.primaryColor", "purple")
        st.config.set_option("theme.backgroundColor", "#1e1e1e")
        st.config.set_option("theme.secondaryBackgroundColor", "#2e2e2e")
        st.config.set_option("theme.textColor", "#e0e0e0")

# Function to inject custom CSS for font size
def apply_font_size(font_size):
    font_size_style = f"""
        <style>
        html, body, [class*="css"] {{
            font-size: {font_size}px;
        }}
        </style>
    """
    st.markdown(font_size_style, unsafe_allow_html=True)

# Streamlit app
def main():
    # Display the TUM logo next to the title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://www.pngfind.com/pngs/m/667-6671010_technical-university-of-munich-tum-logo-hd-png.png", width=100)
    with col2:
        st.title("Web Image Scraper")

    url_start = st.text_input("Enter the URL of the website to scrape images from:")
    num_images = st.number_input("Number of images to display (up to the specified number):", min_value=1, max_value=100, value=10)
    theme = st.selectbox("Choose theme:", ["Light", "Dark"])
    font_size = st.slider("Select font size:", 12, 24, 16)

    # Apply the custom styles
    switch_theme(theme)
    apply_font_size(font_size)

    if st.button("Scrape Images"):
        with st.status("Scraping images...", expanded=True) as status:
            if url_start:
                with st.spinner('Scraping images...'):
                    try:
                        st.write("Searching for images...")
                        images_data = ImageScrapper.all_image_from_url(url_start)
                        if images_data:
                            st.write("Images found. Displaying images...")
                            status.update(label="Images found!", state="complete")
                            st.success(f"Found {len(images_data)} images")
                            images_displayed = 0
                            columns = st.columns(3)  # Adjust the number of columns as needed
                            for img in images_data:
                                if images_displayed >= num_images:
                                    break
                                try:
                                    img_bytes = BytesIO(img["img_data"])
                                    image = Image.open(img_bytes)
                                    col = columns[images_displayed % 3]
                                    with col:
                                        st.image(image, caption=img["img_desc"], width=200)
                                        st.markdown(f"[Download Image]({img['img_url']})")
                                    images_displayed += 1
                                except Exception as e:
                                    st.warning(f"Error displaying image: {e}")
                        else:
                            st.warning("No images found at the provided URL.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        status.update(label="Error occurred", state="error")
            else:
                st.error("Please enter a valid URL.")
                status.update(label="Invalid URL", state="error")

if __name__ == "__main__":
    main()
