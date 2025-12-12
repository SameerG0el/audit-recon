import streamlit as st
from serpapi import GoogleSearch
from exa_py import Exa

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Pre-Audit Recon", page_icon="🛡️")
st.title("🛡️ Pre-Audit Intelligence Agent")
st.markdown("Automated 'Zero-Touch' Digital Investigation")

# Securely get API Keys
# You should add these to your .streamlit/secrets.toml file for Streamlit Cloud
serpapi_key = st.secrets.get("SERPAPI_API_KEY")
exa_api_key = st.secrets.get("EXA_API_KEY")

# Fallback for local testing if secrets aren't set
with st.expander("API Configuration", expanded=not (serpapi_key and exa_api_key)):
    if not serpapi_key:
        serpapi_key = st.text_input("Enter SerpApi Key", type="password")
    if not exa_api_key:
        exa_api_key = st.text_input("Enter Exa API Key", type="password")

# 2. INPUTS (Per PRD Step 2: "Search Strategy Generation")
col1, col2 = st.columns(2)
with col1:
    advisor_name = st.text_input("Advisor Name", placeholder="e.g. John Smith")
with col2:
    city = st.text_input("City/Location", placeholder="e.g. New York")

# 3. MAIN LOGIC
if st.button("Run Pre-Audit Recon") and serpapi_key and exa_api_key and advisor_name:
    
    status_container = st.status("Initializing Investigation...", expanded=True)
    
    try:
        # --- PHASE 1: DIGITAL FOOTPRINT (SerpApi) ---
        # PRD Step 2: "Generate search queries... [First Name] [Last Name] financial advisor [City]" [cite: 30]
        status_container.write("🔍 Phase 1: Executing Google Search Strategy (SerpApi)...")
        
        query = f"{advisor_name} financial advisor {city}"
        search_params = {
            "q": query,
            "api_key": serpapi_key,
            "num": 3  # We only need top results to find the main site
        }
        
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        # Extract the top organic result URL
        if "organic_results" in results and len(results["organic_results"]) > 0:
            top_result = results["organic_results"][0]
            target_url = top_result.get("link")
            site_title = top_result.get("title")
            
            status_container.write(f"✅ Target Identified: {site_title}")
            status_container.write(f"🔗 URL: {target_url}")
        else:
            status_container.update(label="Investigation Failed", state="error")
            st.error("❌ No Google Search results found. Cannot proceed to content analysis.")
            st.stop()

        # --- PHASE 2: COMPLIANCE CRAWL (Exa) ---
        # PRD Step 3: "Automated review of the branch's client-facing website" 
        status_container.write("🕷️ Phase 2: Crawling Website Content (Exa)...")
        
        exa = Exa(exa_api_key)
        
        # Use Exa to get the contents of the specific URL found by SerpApi
        # Note: We use get_contents (retrieve) rather than search here
        exa_response = exa.get_contents(
            ids=[target_url],
            text=True
        )
        
        if not exa_response.results:
            status_container.update(label="Crawl Failed", state="error")
            st.error("❌ Exa could not retrieve content from this URL.")
            st.stop()
            
        page_content = exa_response.results[0].text
        status_container.update(label="Investigation Complete", state="complete")

        # --- PHASE 3: RISK ANALYSIS ---
        # PRD Step 3: Scan for "prohibited keyword clusters" [cite: 57]
        st.divider()
        st.subheader(f"📝 Pre-Audit Intelligence Brief: {advisor_name}")
        st.caption(f"Source: {target_url}")

        # Defined in PRD Step 3 [cite: 58-61]
        risk_keywords = {
            "Promissory / Guarantees": ["Guaranteed returns", "Risk-free", "No loss", "Guaranteed income"], 
            "Unapproved Products": ["Crypto", "Private Equity", "Hedge Fund", "Bitcoin"], 
            "Testimonials (SEC Rule)": ["reviews", "star rating", "5 stars", "testimonials"] 
        }
        
        found_risks = []
        content_lower = page_content.lower()
        
        for category, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    found_risks.append(f"**{category}**: Found term '{keyword}'")

        # Display Results
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.markdown("#### 🚩 Risk Flags")
            if found_risks:
                for risk in found_risks:
                    st.error(risk)
            else:
                st.success("No high-risk keywords detected.")

        with col_b:
            st.markdown("#### 📄 Content Preview")
            with st.expander("View Scraped Text", expanded=True):
                st.text(page_content[:1500] + "...") # Show first 1500 chars

    except Exception as e:
        status_container.update(label="Error", state="error")
        st.error(f"System Error: {str(e)}")

elif st.button("Run Pre-Audit Recon"):
    st.warning("⚠️ Please enter Advisor Name, City, and ensure API keys are set.")
