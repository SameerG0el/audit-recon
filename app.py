import streamlit as st
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import time

# --- CONFIGURATION (The "Simulated" CRM) ---
# In a real app, this would query Salesforce.
# Here, we simulate a "Clean" CRM that allows nothing, forcing flags on everything found.
CRM_DATA = {
    "approved_obas": [],  # No outside businesses allowed
    "approved_websites": [], # No websites allowed
    "mandatory_disclosures": ["Member FINRA", "Member SIPC"]
}

# --- HELPER FUNCTIONS ---

def check_google_footprint(name, city, api_key):
    """
    Searches Google for the advisor to find unapproved business links.
    """
    if not api_key:
        return {"error": "API Key Missing"}
    
    query = f"{name} {city} financial advisor"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 5
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        return organic_results
    except Exception as e:
        return {"error": str(e)}

def analyze_website(url):
    """
    Scrapes the target URL for compliance risks.
    """
    findings = []
    status = "Success"
    
    # 1. Attempt to Fetch
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "Blocked", "findings": []}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text().lower()

    # 2. Check Disclosures (Footer)
    # Simple check: does the text exist anywhere on the page?
    missing_disclosures = []
    for disc in CRM_DATA["mandatory_disclosures"]:
        if disc.lower() not in text_content:
            missing_disclosures.append(disc)
    
    if missing_disclosures:
        findings.append(f"❌ **Missing Mandatory Disclosure:** {', '.join(missing_disclosures)}")
    else:
        findings.append(f"✅ **Disclosures:** All mandatory text found.")

    # 3. Check Prohibited Keywords
    risky_keywords = ["guaranteed returns", "risk-free", "crypto", "safe investment"]
    found_risks = [word for word in risky_keywords if word in text_content]
    
    if found_risks:
        findings.append(f"⚠️ **High Risk Keywords Detected:** '{', '.join(found_risks)}'")
    
    return {"status": "Success", "findings": findings}

# --- THE APP UI ---

st.set_page_config(page_title="Pre-Audit Recon Agent", page_icon="🕵️")

st.title("🕵️ Pre-Audit Intelligence Agent")
st.markdown("""
**Automated Reconnaissance for Branch Audits** *Enter a target branch or advisor below. The agent will perform a live 'Zero-Touch' analysis against public data and internal compliance rules.*
""")

# Sidebar for Setup
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter SerpApi Key", type="password", help="Get a free key at serpapi.com")
    st.info("The Agent simulates a check against the 'Internal CRM' (Mock Data).")

# Main Inputs
col1, col2 = st.columns(2)
with col1:
    target_name = st.text_input("Advisor Name", "John Doe")
    target_city = st.text_input("City", "New York")
with col2:
    target_url = st.text_input("Branch Website URL", "https://www.example.com")

if st.button("🚀 Run Pre-Audit Scan"):
    if not api_key:
        st.error("Please enter a SerpApi Key in the sidebar to proceed.")
    else:
        with st.status("Running Intelligence Collection...", expanded=True) as status:
            
            # Step 1: Internal Check
            st.write("📂 Retrieving Internal CRM Profile...")
            time.sleep(1) # Fake processing time for effect
            st.write("✅ CRM Profile Loaded (Strict Supervision Mode).")
            
            # Step 2: Website Scan
            st.write(f"🌐 Crawling Target Website: {target_url}...")
            web_analysis = analyze_website(target_url)
            
            if web_analysis.get("status") == "Success":
                st.write("✅ Website Content Analysis Complete.")
            elif web_analysis.get("status") == "Blocked":
                st.warning("⚠️ Website blocked automated scanning. Skipping Deep Content Analysis.")
            else:
                st.error(f"❌ Website Error: {web_analysis.get('message')}")

            # Step 3: Google Search
            st.write("🔍 Executing 'Google Test' for undisclosed OBAs...")
            search_results = check_google_footprint(target_name, target_city, api_key)
            st.write("✅ Digital Footprint Analyzed.")
            
            status.update(label="Audit Scan Complete!", state="complete", expanded=False)

        # --- REPORT OUTPUT ---
        st.divider()
        st.subheader("📋 Pre-Audit Intelligence Brief")
        
        # Section 1: Web Compliance
        st.markdown("### 1. Website Compliance Review")
        if web_analysis.get("status") == "Success":
            for item in web_analysis["findings"]:
                st.markdown(item)
            
            # The "Trick": Always flag the URL if it works
            st.markdown(f"🚩 **Unapproved Domain:** The URL `{target_url}` is active but NOT listed in the Approved CRM Website field.")
        else:
            st.info(f"Could not verify website content due to security settings ({web_analysis.get('status')}). Manual review recommended.")

        # Section 2: Google / OBA Check
        st.markdown("### 2. Digital Footprint & OBA Detection")
        if isinstance(search_results, list):
            found_potential_oba = False
            for result in search_results:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Logic: If the snippet contains "Board", "Owner", "Founder" it's a risk
                if any(x in snippet.lower() for x in ["board", "owner", "founder", "partner"]):
                    st.markdown(f"⚠️ **Potential Undisclosed OBA:** Found '{title}'")
                    st.markdown(f"> *{snippet}*")
                    st.markdown(f"[View Source]({link})")
                    found_potential_oba = True
            
            if not found_potential_oba:
                 st.success("No high-confidence OBA violations found in top search results.")
        else:
            st.error("Search API Error.")

        st.caption("Generated by The Recon Specialist Agent v1.0")
