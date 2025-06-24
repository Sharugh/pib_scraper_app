import streamlit as st
from playwright.sync_api import sync_playwright
import pandas as pd
import io
from urllib.parse import urljoin

# Define the target URL and base URL for absolute link conversion
url = "https://www.pib.gov.in/allRel.aspx?lang=1®=38"
base_url = "https://www.pib.gov.in"

# Function to scrape press release links
def scrape_links():
    with sync_playwright() as p:
        # Launch a headless Chromium browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to the URL and wait for the page to fully load
        page.goto(url)
        page.wait_for_load_state('networkidle')
        # Extract all anchor tags
        links = page.query_selector_all('a')
        # Filter links containing '/PressReleasePage.aspx' and convert to absolute URLs
        press_release_links = [
            urljoin(base_url, link.get_attribute('href')) 
            for link in links 
            if link.get_attribute('href') and '/PressReleasePage.aspx' in link.get_attribute('href')
        ]
        browser.close()
    return press_release_links

# Streamlit app interface
st.title("Press Release Scraper")
st.write("Click the button below to scrape press release links from the PIB website and download them as an Excel file.")

# Button to trigger scraping
if st.button("Scrape Press Releases"):
    with st.spinner("Scraping in progress..."):
        # Scrape the links
        links = scrape_links()
        # Store links in a pandas DataFrame
        df = pd.DataFrame(links, columns=["Press Release Links"])
        # Create an in-memory Excel file
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
    
    # Display success message and provide download button
    st.success("Scraping completed successfully!")
    st.download_button(
        label="Download Excel File",
        data=excel_file,
        file_name="press_releases.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
