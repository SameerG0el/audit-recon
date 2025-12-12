import streamlit as st
import random
import time
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
# We try to load the logo; if it fails (file missing), we just show text.
try:
    st.image("pitcrew-1.png", width=250)
except Exception:
    st.markdown("<h1>pitcrew</h1>", unsafe_allow_html=True)

st.markdown("### 🛡️ Automated Pre-Audit Intelligence Agent")
st.markdown("*Live Digital Investigation Demo*")

# --- SIMULATION ENGINE (30-40% Risk Probability) ---
def simulate_internal_discovery():
    [cite_start]"""Simulates checking internal CRM and Document systems [cite: 14-26]."""
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
    [cite_start]"""Simulates checking FINRA/IAPD/RegEd [cite: 62-69]."""
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
    [cite_start]"""Executes the 'Google Test' via SerpApi [cite: 27-33]."""
    if not api_key:
        return None, "API Key Missing"
        
    try:
        query = f"{name} financial advisor {city}"
        search = GoogleSearch({"q": query, "api_key": api_key, "num": 5})
        return search.get_dict(), None
    except Exception as e:
        return None, str(e)

def run_compliance_crawl(url, api_key):
    [cite_start]"""Crawls the website for risk keywords via Exa [cite: 42-61]."""
    if not api_key:
        return None, "API Key Missing"
        
    exa = Exa(api_key)
    try:
        # Get clean text content
        response = exa.get_contents(ids=[url], text=True)
        return response.results[0], None
    except Exception as e:
        return None, str(e)

def analyze_risk_keywords(text):
    [cite_start]"""Scans text for prohibited keyword clusters [cite: 58-61]."""
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

# Main Inputs
col_input1, col_input2, col_btn = st.columns([2, 2, 1])
with col_input1:
    advisor_name = st.text_input("Advisor Name", placeholder="e.g. John Doe", value="John Smith")
with col_input2:
    city_loc = st.text_input("City / Firm", placeholder="e.g. New York", value="New York")
with col_btn:
    st.write("") # Spacing
    st.write("") 
    run_btn = st.button("🚀 Run Audit", type="primary", use_container_width=True)

if run_btn:
    if not (advisor_name and city_loc):
        st.warning("Please enter Advisor Name and Location.")
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

        # 3. REAL: Google Search
        st.write(f"🔍 Executing 'Google Test' for: *{advisor_name}*...")
        search_data, search_err = run_google_test(advisor_name, city_loc, serpapi_key)
        
        target_url = None
        if search_data and "organic_results" in search_data:
            # We pick the first result that looks like a real website (basic logic)
            top_result = search_data["organic_results"][0]
            target_url = top_result.get("link")
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ Target Identity Found: [{top_result.get('title')}]({target_url})")
        else:
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ Search Failed: {search_err}")
            status.update(label="Investigation Halted: Target Not Found", state="error")
            st.stop()

        # 4. REAL: Website Crawl
        st.write(f"🕷️ Deploying Exa Crawler to: *{target_url}*...")
        crawl_data, crawl_err = run_compliance_crawl(target_url, exa_api_key)
        
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
        st.caption("Live Search Results (SerpApi)")
        
        if search_data and "organic_results" in search_data:
            for res in search_data["organic_results"][:4]:
                with st.container(border=True):
                    st.markdown(f"**[{res.get('title')}]({res.get('link')})**")
                    st.caption(res.get("snippet"))
                    
                    # Quick logic to flag obvious social media
                    if "linkedin" in res.get("link", ""):
                        st.info("ℹ️ **OBA Check**: Verify this LinkedIn profile matches CRM records.")
        else:
            st.warning("No search data available.")

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
        st.caption(f"Source: {target_url}")
        
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
            st.warning("Website content could not be analyzed.")

        # Display Simulated Internal Data here as context
        st.markdown("---")
        st.subheader("📂 Internal Hygiene")
        st.caption("Simulated Data (CRM/Docs)")
        if internal_result["status"] == "Clear":
            st.success(internal_result["detail"])
        else:
            st.error(internal_result["detail"])
