import streamlit as st
import random
import time
import requests
from bs4 import BeautifulSoup
from exa_py import Exa
from serpapi import GoogleSearch

# --- CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="Pitcrew | Pre-Audit Intel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Branding
try:
    st.image("pitcrew-1.png", width=250)
except Exception:
    st.markdown("<h1>pitcrew</h1>", unsafe_allow_html=True)

st.markdown("### 🛡️ Automated Pre-Audit Intelligence Agent")
st.markdown("*Live Digital Investigation Demo*")

# --- SIMULATION ENGINE (30-40% Risk Probability) ---
def simulate_internal_discovery():
    """Simulates checking internal CRM and Document systems."""
    time.sleep(1.5) # Simulate processing time
    
    # 35% Chance of finding an issue
    if random.random() < 0.35:
        issues = [
            ("Training Delinquency", "Annual Compliance Meeting not completed"),
            ("Missing Doc", "2024 Outside Business Activity Form not on file"),
            ("Correspondence", "Unresolved email flag from Sep 2024"),
        ]
        issue = random.choice(issues)
        return {"status": "Flagged", "color": "red", "detail": f"⚠️ **{issue[0]}**: {issue[1]}"}
    else:
        return {"status": "Clear", "color": "green", "detail": "✅ All mandatory internal documents present."}

def simulate_regulatory_check():
    """Simulates checking FINRA/IAPD/RegEd."""
    time.sleep(1.2)
    
    # 30% Chance of finding an issue
    if random.random() < 0.30:
        issues = [
            ("License Warning", "Series 63 expiration approaching (60 days)"),
            ("Disclosure Match", "1 Historical Customer Dispute found (Closed/No Action)"),
            ("State Reg", "Client density in FL exceeds de minimis; registration needed"),
        ]
        issue = random.choice(issues)
        return {"status": "Alert", "color": "orange", "detail": f"⚠️ **{issue[0]}**: {issue[1]}"}
    else:
        return {"status": "Clear", "color": "green", "detail": "✅ No active disclosures or license gaps found."}

# --- REAL INTELLIGENCE ENGINE ---
def run_google_test(name, city, api_key):
    """Executes the 'Google Test' via SerpApi."""
    if not api_key:
        return None, "API Key Missing"
        
    try:
        query = f"{name} financial advisor {city}"
        search = GoogleSearch({"q": query, "api_key": api_key, "num": 5})
        return search.get_dict(), None
    except Exception as e:
        return None, str(e)

def run_compliance_crawl(url, api_key):
    """
    Crawls URL via Exa. 
    Falls back to BeautifulSoup if Exa fails.
    """
    if not api_key:
        return None, "API Key Missing"

    # 1. URL Sanitization: Ensure it starts with http/https
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # 2. Try Exa First (The "Smart" Way)
    exa = Exa(api_key)
    try:
        response = exa.get_contents(ids=[url], text=True)
        if response.results:
            return response.results[0], None
    except Exception as e:
        # Just log error internally and move to fallback
        print(f"Exa failed: {e}") 

    # 3. Fallback: BeautifulSoup (The "Manual" Way)
    try:
        # Masquerade as a real browser to avoid 403 blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Check for 404/403/500 errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Kill all script and style elements to clean up text
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        
        # Create a "Mock" object to match Exa's structure so the rest of the app doesn't break
        class MockResult:
            def __init__(self, text):
                self.text = text
                
        return MockResult(text), None

    except Exception as e:
        return None, f"Scraping Failed (Both Exa & Fallback): {str(e)}"

def analyze_risk_keywords(text):
    """Scans text for prohibited keyword clusters."""
    risk_keywords = {
        "Promissory / Guarantees": ["guaranteed return", "risk-free", "no loss", "guaranteed income"], 
        "Unapproved Products": ["crypto", "private equity", "hedge fund", "bitcoin", "ethereum"], 
        "Testimonials (SEC Rule)": ["reviews", "star rating", "5 stars", "testimonials"] 
    }
    
    found_risks = []
    text_lower = text.lower()
    
    for category, keywords in risk_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_risks.append(f"🔴 **{category}**: Found term '{keyword}'")
    
    return found_risks

# --- UI & LOGIC ---

# Sidebar for Inputs
with st.sidebar:
    st.header("Investigation Controls")
    
    # Secure Keys (Frictionless for user)
    serpapi_key = st.secrets.get("SERPAPI_API_KEY")
    exa_api_key = st.secrets.get("EXA_API_KEY")
    
    if not (serpapi_key and exa_api_key):
        st.error("⚠️ API Keys missing in secrets.toml!")
# 1. Create the outer layout: spacer, main_content, spacer
# [1, 4, 1] splits the screen into 6 parts. The center gets 4 parts (2/3rds).
left_spacer, main_content, right_spacer = st.columns([1, 4, 1])

# 2. Use a 'with' block to put everything inside that center column
    # Main Inputs - UPDATED LAYOUT
with main_content:
    
    # 3. Your original code goes here, properly indented
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        advisor_name = st.text_input("Advisor Name", placeholder="e.g. John Smith", value="John Smith")
    with col2:
        city_loc = st.text_input("City / Firm", placeholder="e.g. New York", value="New York")
    with col3:
        # Explicit URL Input
        target_url_input = st.text_input("Target Website URL", placeholder="https://www.example.com")
    
    run_btn = st.button("🚀 Run Audit", type="primary", use_container_width=True)
    
    if run_btn:
        if not (advisor_name and city_loc and target_url_input):
            st.warning("⚠️ Please provide Advisor Name, City, and the Target Website URL.")
            st.stop()
    
        # CONTAINER: Live Process Log
        with st.status("🕵️‍♂️ **Agent Active: Executing Zero-Touch Investigation...**", expanded=True) as status:
            
            # 1. SIMULATION: Internal Data
            st.write("📂 Accessing Internal CRM & Document Repository...")
            internal_result = simulate_internal_discovery()
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ {internal_result['detail']}")
            
            # 2. SIMULATION: Regulatory
            st.write("⚖️ Querying FINRA / IAPD Databases...")
            reg_result = simulate_regulatory_check()
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ {reg_result['detail']}")
    
            # 3. REAL: Google Search (Reputation Check)
            st.write(f"🔍 Executing 'Google Test' for: *{advisor_name}*...")
            search_data, search_err = run_google_test(advisor_name, city_loc, serpapi_key)
            
            if search_data and "organic_results" in search_data:
                count = len(search_data["organic_results"])
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ Found {count} reputation signals.")
            else:
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ Google Search returned no results (Continuing to website audit...)")
    
            # 4. REAL: Website Crawl (Manual Input)
            st.write(f"🕷️ Deploying Exa Crawler to Target: *{target_url_input}*...")
            crawl_data, crawl_err = run_compliance_crawl(target_url_input, exa_api_key)
            
            risk_flags = []
            if crawl_data:
                st.write("&nbsp;&nbsp;&nbsp;&nbsp;✅ Content Extracted Successfully. Analyzing text stream...")
                risk_flags = analyze_risk_keywords(crawl_data.text)
                if risk_flags:
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ **{len(risk_flags)} Compliance Risks Detected.**")
                else:
                    st.write("&nbsp;&nbsp;&nbsp;&nbsp;✅ No Keyword Risks Detected.")
            else:
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ Crawl Failed: {crawl_err}")
    
            status.update(label="✅ Pre-Audit Investigation Complete", state="complete")
    
        # --- RESULTS DASHBOARD (2 Columns) ---
        st.divider()
        
        col_left, col_right = st.columns(2)
    
        # LEFT COLUMN: Digital Footprint (Google Results)
        with col_left:
            st.subheader("🌐 Digital Footprint")
            st.caption(f"Reputation Check: {advisor_name} ({city_loc})")
            
            if search_data and "organic_results" in search_data:
                for res in search_data["organic_results"][:4]:
                    with st.container(border=True):
                        st.markdown(f"**[{res.get('title')}]({res.get('link')})**")
                        st.caption(res.get("snippet"))
                        
                        if "linkedin" in res.get("link", ""):
                            st.info("ℹ️ **OBA Check**: Verify this LinkedIn profile matches CRM records.")
            elif search_err:
                 st.error(f"Search API Error: {search_err}")
            else:
                st.warning("No public search results found.")
    
            # Display Simulated Regulatory Data here as context
            st.markdown("---")
            st.subheader("⚖️ Regulatory Status")
            st.caption("Simulated Data (FINRA/IAPD)")
            if reg_result["status"] == "Clear":
                st.success(reg_result["detail"])
            else:
                st.warning(reg_result["detail"])
    
        # RIGHT COLUMN: Website Content Analysis (Exa Results)
        with col_right:
            st.subheader("📝 Website Compliance Audit")
            st.caption(f"Source: {target_url_input}")
            
            if crawl_data:
                # 1. Risk Flags Section
                if risk_flags:
                    st.error(f"🚩 **{len(risk_flags)} Potential Violations Detected**")
                    for flag in risk_flags:
                        st.markdown(f"- {flag}")
                else:
                    st.success("✅ Clean Scan: No prohibited keywords found.")
    
                # 2. Content Preview Section
                with st.expander("📄 View Scraped Site Content", expanded=False):
                    st.text(crawl_data.text[:2000] + "...")
                    st.caption("... (Truncated for view) ...")
            else:
                st.warning("Website content could not be analyzed. Check the URL and try again.")
    
            # Display Simulated Internal Data here as context
            st.markdown("---")
            st.subheader("📂 Internal Hygiene")
            st.caption("Simulated Data (CRM/Docs)")
            if internal_result["status"] == "Clear":
                st.success(internal_result["detail"])
            else:
                st.error(internal_result["detail"])
