import streamlit as st
from requests_html import HTMLSession
import pandas as pd
from datetime import datetime
import os

# Keywords of interest
KEYWORDS = [
    "energy", "refinery", "oil", "gas", "petroleum", "power", "electricity",
    "LNG", "coal", "renewable", "solar", "wind", "thermal", "exploration", "E&P",
    "production", "downstream", "upstream", "biofuel", "hydrocarbon", "ethanol", "pipeline"
]

# Ministries of interest
TARGET_MINISTRIES = [
    "Ministry of Petroleum & Natural Gas",
    "Ministry of Power",
    "Ministry of New and Renewable Energy",
    "Ministry of Chemicals and Fertilizers",
    "Ministry of Planning",
    "Ministry of Road Transport and Highways"
]

BASE_URL = "https://pib.gov.in/PressReleasePage.aspx"

# Load previous data
def load_previous_data():
    if os.path.exists("press_releases.xlsx"):
        return pd.read_excel("press_releases.xlsx")
    else:
        return pd.DataFrame(columns=["Date", "Title", "Link", "Ministry", "Matched Keywords"])

# Save to Excel
def save_data(df):
    df.to_excel("press_releases.xlsx", index=False)

# Extract press releases using requests-html
def scrape_press_releases():
    releases = []
    session = HTMLSession()

    for page_num in range(1, 5):  # Scrape first 4 pages
        url = f"{BASE_URL}?PRID=&Page={page_num}&MenuId=3"
        response = session.get(url)
        response.html.render(timeout=20, sleep=1)  # render JS, wait a bit

        press_items = response.html.find("div.content-area")

        for item in press_items:
            try:
                title_tag = item.find("a", first=True)
                title = title_tag.text.strip()
                link = "https://pib.gov.in/" + title_tag.attrs["href"]
                date = item.find("span.date", first=True).text.strip()
                ministry = item.find("div.ministry", first=True).text.strip()

                if ministry in TARGET_MINISTRIES:
                    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in title.lower()]
                    if matched_keywords:
                        releases.append({
                            "Date": date,
                            "Title": title,
                            "Link": link,
                            "Ministry": ministry,
                            "Matched Keywords": ", ".join(matched_keywords)
                        })
            except Exception:
                continue

    return releases

# Streamlit UI
def main():
    st.title("🔎 PIB Energy Press Release Tracker")
    st.markdown("Scrapes the Indian Government's PIB website for energy-related updates.")

    if st.button("Scrape PIB Now"):
        st.info("Scraping latest data...")
        old_df = load_previous_data()
        scraped = scrape_press_releases()
        new_df = pd.DataFrame(scraped)

        if new_df.empty:
            st.warning("No new press releases found.")
            return

        combined_df = pd.concat([new_df, old_df]).drop_duplicates(subset=["Link"])
        new_items = pd.merge(new_df, old_df, how='outer', indicator=True).query('_merge == "left_only"')
        
        save_data(combined_df)

        st.success(f"✅ {len(new_df)} relevant press releases scraped.")
        st.subheader("📌 New Items Found:")
        st.dataframe(new_items[["Date", "Title", "Ministry", "Link", "Matched Keywords"]])

        with st.expander("🔁 Full Dataset"):
            st.dataframe(combined_df)

        st.download_button(
            "📥 Download Excel",
            combined_df.to_excel(index=False, engine='openpyxl'),
            file_name="press_releases.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()

