import streamlit as st
from serpapi import GoogleSearch
from exa_py import Exa

# ------------------------------------------------------------------
# 1) CONFIG & KEYS (Hardcoded as requested)
# ------------------------------------------------------------------
st.set_page_config(page_title="Pitcrew Branch Pre-Audit", layout="wide")

# SECURITY WARNING: Never share this file publicly if it contains real keys.
# It is better to use st.secrets for production apps.
SERPAPI_KEY = "4313693d5ad95021cc2a32adbdd30b0f3f7dfc8796a5b1994869e755ab6c93f6"
EXA_API_KEY = "1ce305cb-0592-4558-9512-1cddb4868694" 

# Initialize Exa
exa = Exa(api_key=EXA_API_KEY)

# ------------------------------------------------------------------
# 2) LOGO (Top-Left Sidebar)
# ------------------------------------------------------------------
# This places the logo at the top of the sidebar, which is the standard
# "top-left" position for Streamlit branding.
try:
    st.sidebar.image("pitcrew-1.png", width=200) 
except Exception as e:
    st.sidebar.warning("Logo not found. Make sure 'pitcrew-1.png' is in the folder.")

st.title("Pitcrew Research Assistant")
st.markdown("---")

# ------------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    query = st.text_input("Search Query", "Financial strategies for wealth")
    
    # Input for specific URL scraping (to test the difficult sites)
    url_to_scrape = st.text_input("Target URL to Scrape (Optional)", 
                                  "https://www.strategiesforwealth.com/")
    
    trigger = st.button("Run Search & Scrape")

# ------------------------------------------------------------------
# 3 & 4) TWO-COLUMN LAYOUT & EXA SCRAPING
# ------------------------------------------------------------------
if trigger:
    # Create two columns: Left for Search Results, Right for Scraped Content
    col_search, col_scrape = st.columns(2)

    # --- COLUMN 1: GOOGLE SEARCH (SerpAPI) ---
    with col_search:
        st.subheader("🔍 Search Results")
        try:
            search_params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": 5
            }
            search = GoogleSearch(search_params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])

            if organic_results:
                for result in organic_results:
                    with st.expander(result.get("title", "No Title")):
                        st.write(result.get("snippet", "No snippet"))
                        st.markdown(f"[Link]({result.get('link')})")
            else:
                st.info("No search results found.")
                
        except Exception as e:
            st.error(f"SerpAPI Error: {e}")

    # --- COLUMN 2: WEB SCRAPING (Exa.ai) ---
    with col_scrape:
        st.subheader("📄 Scraped Content (Exa.ai)")
        
        target_url = url_to_scrape if url_to_scrape else (organic_results[0]['link'] if organic_results else None)

        if target_url:
            st.info(f"Scraping: {target_url}")
            try:
                # Exa is much better at handling bot-protected sites like opesone.com
                # We use get_contents to retrieve clean text
                response = exa.get_contents(
                    [target_url],
                    text=True  # Asks for clean text
                )
                
                if response and response.results:
                    scraped_text = response.results[0].text
                    st.success("Successfully scraped!")
                    st.text_area("Content", scraped_text, height=600)
                else:
                    st.warning("Exa returned no content.")
                    
            except Exception as e:
                st.error(f"Exa Error: {e}")
                st.caption("Ensure your Exa API key is valid.")
        else:
            st.warning("No URL provided to scrape.")
