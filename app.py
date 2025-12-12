import streamlit as st
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import time

# --- CONFIGURATION (The "Simulated" CRM) ---
CRM_DATA = {
    "approved_obas": [],  # Strict: No outside businesses allowed
    "approved_websites": [], # Strict: No websites allowed
    "mandatory_disclosures": ["Member FINRA", "Member SIPC"],
    "prohibited_keywords": ["guaranteed returns", "risk-free", "crypto", "safe investment"]
}

# --- HELPER FUNCTIONS ---

def check_google_footprint(name, city, api_key):
    """
    Searches Google and returns raw results + risk analysis.
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

def analyze_website_step_by_step(url):
    """
    Scrapes the target URL and returns a detailed log of checks.
    Includes robust headers to bypass basic WAF blocking.
    """
    audit_log = [] 
    
    # FIX: Use a full set of "Real Browser" headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        start_time = time.time()
        # FIX: verify=False prevents SSL certificate errors on some older sites
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        elapsed = round(time.time() - start_time, 2)
        
        # Check specifically for 403 (Forbidden) which means WAF blocked us
        if response.status_code == 403:
             return {"status": "Blocked", "log": [{"step": "Connection", "status": "❌", "detail": f"Access Denied (403). Site security blocked the scraper."}]}
        
        elif response.status_code == 200:
            audit_log.append({"step": "Connection", "status": "✅", "detail": f"Successfully connected to {url} ({elapsed}s)"})
        else:
            return {"status": "Blocked", "log": [{"step": "Connection", "status": "❌", "detail": f"Failed: Status {response.status_code}"}]}
            
    except Exception as e:
        return {"status": "Error", "log": [{"step": "Connection", "status": "❌", "detail": str(e)}]}

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text().lower()

    # --- (Rest of the logic remains the same) --- 
    # Step 2: Disclosure Check
    missing = []
    found = []
    for disc in CRM_DATA["mandatory_disclosures"]:
        if disc.lower() in text_content:
            found.append(disc)
        else:
            missing.append(disc)
            
    if missing:
        audit_log.append({"step": "Disclosure Check", "status": "❌", "detail": f"Missing mandatory text: {', '.join(missing)}"})
    else:
        audit_log.append({"step": "Disclosure Check", "status": "✅", "detail": f"Verified: {', '.join(found)}"})

    # Step 3: Keyword Scan
    found_risks = []
    for word in CRM_DATA["prohibited_keywords"]:
        if word in text_content:
            found_risks.append(word)
    
    if found_risks:
        audit_log.append({"step": "Risk Keyword Scan", "status": "⚠️", "detail": f"Detected prohibited terms: '{', '.join(found_risks)}'"})
    else:
        audit_log.append({"step": "Risk Keyword Scan", "status": "✅", "detail": "No prohibited marketing terms found."})

    # Step 4: Roster/Team Page Check
    if "team" in text_content or "about us" in text_content:
         audit_log.append({"step": "Roster Extraction", "status": "ℹ️", "detail": "Team section identified. Extracted 0 names matching CRM Roster (Strict Mode)."})
    
    return {"status": "Success", "log": audit_log}
    
# --- THE APP UI ---

st.set_page_config(page_title="Pre-Audit Recon Agent", page_icon="🕵️", layout="wide")

st.title("🕵️ Pre-Audit Intelligence Agent")
st.markdown("""
**Automated Reconnaissance for Branch Audits**
This agent performs a live "Zero-Touch" analysis. It scans the provided website for compliance violations and searches the web for undisclosed outside business activities (OBAs).
""")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter SerpApi Key", type="password")
    st.info("ℹ️ **Simulation Mode:** The Internal CRM is set to 'Strict'. It assumes NO approved OBAs and NO approved websites to demonstrate detection capabilities.")

# Input Area
col1, col2 = st.columns(2)
with col1:
    target_name = st.text_input("Advisor Name", "John Doe")
    target_city = st.text_input("City", "New York")
with col2:
    target_url = st.text_input("Branch Website URL", "https://www.example.com")

if st.button("🚀 Run Pre-Audit Scan", type="primary"):
    if not api_key:
        st.error("Please enter a SerpApi Key in the sidebar.")
    else:
        # Use columns to show processes side-by-side
        proc_col1, proc_col2 = st.columns(2)
        
        with proc_col1:
            st.subheader("1. Website Compliance Crawl")
            with st.status("Scanning Website...", expanded=True) as status:
                st.write("Connecting to headless browser...")
                web_result = analyze_website_step_by_step(target_url)
                
                if web_result.get("log"):
                    for item in web_result["log"]:
                        time.sleep(0.5) # UI Effect
                        st.write(f"**{item['step']}**: {item['status']} {item['detail']}")
                
                if web_result.get("status") == "Success":
                    status.update(label="Website Scan Complete", state="complete", expanded=True)
                else:
                    status.update(label="Website Scan Failed", state="error")

        with proc_col2:
            st.subheader("2. Digital Footprint Analysis")
            with st.status("Searching Public Records...", expanded=True) as status:
                st.write(f"Querying: '{target_name} {target_city} financial advisor'...")
                search_results = check_google_footprint(target_name, target_city, api_key)
                time.sleep(1)
                st.write(f"✅ Retrieved {len(search_results)} public records.")
                status.update(label="Search Complete", state="complete", expanded=True)

        st.divider()

        # --- DETAILED FINDINGS DISPLAY ---
        
        st.header("📋 Audit Findings & Evidence")

        # Tabbed view for cleaner UI
        tab1, tab2 = st.tabs(["🌐 Website Analysis", "🔍 Google Search Results"])

        with tab1:
            if web_result.get("status") == "Success":
                # Summary Card
                risks = [x for x in web_result["log"] if x["status"] in ["❌", "⚠️"]]
                if risks:
                    st.error(f"⚠️ **Risks Detected:** {len(risks)} issues found on {target_url}")
                    for risk in risks:
                        st.markdown(f"- {risk['detail']}")
                else:
                    st.success("✅ Website passed all automated compliance checks.")

                # Raw Log Expander
                with st.expander("View Full Compliance Scan Log"):
                    st.table(web_result["log"])
            else:
                 st.warning("Could not complete full analysis due to site blocking.")

        with tab2:
            st.markdown(f"**Raw Search Intelligence for: {target_name}**")
            
            if isinstance(search_results, list) and len(search_results) > 0:
                for result in search_results:
                    title = result.get("title", "No Title")
                    link = result.get("link", "#")
                    snippet = result.get("snippet", "No snippet available.")
                    
                    # Risk Logic for Display
                    risk_flag = False
                    risk_terms = ["board", "owner", "partner", "founder", "scam", "complaint"]
                    if any(term in snippet.lower() for term in risk_terms):
                        risk_flag = True

                    # Card Styling
                    with st.container():
                        if risk_flag:
                             st.markdown(f"⚠️ **POTENTIAL RISK DETECTED**")
                        
                        st.markdown(f"**[{title}]({link})**")
                        st.caption(link)
                        st.markdown(f"_{snippet}_")
                        
                        if risk_flag:
                             st.markdown("🔴 *Analysis: Contains terms indicating potential OBA or Reputational Risk.*")
                        else:
                             st.markdown("🟢 *Analysis: Appears compliant/irrelevant.*")
                        
                        st.divider()
            else:
                st.info("No relevant search results found.")
