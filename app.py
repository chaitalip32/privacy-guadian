import streamlit as st
from src.breach_checker import check_mock_breaches, check_password_breaches
from src.document_scanner import extract_text, detect_personal_info

st.markdown("<style>#MainMenu {visibility:hidden;} header {visibility:hidden;} footer {visibility:hidden;}</style>", unsafe_allow_html=True)
st.set_page_config(page_title="Privacy Guardian", page_icon="🛡️", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
.main {background-color:#f8f9fa;}
.title {text-align:center;color:#2C3E50;}
.footer {position:fixed;left:0;bottom:0;width:100%;
         background-color:#2C3E50;color:white;text-align:center;
         padding:10px;font-size:14px;}
.stButton>button{background-color:#2E86C1;color:white;border-radius:10px;
                height:3em;width:12em;font-weight:bold;}
.stButton>button:hover{background-color:#1B4F72;color:#F8F9F9;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>🛡️ Privacy Guardian Dashboard</h1>", unsafe_allow_html=True)
st.write("### Protect your digital identity — Check, Scan and Stay Safe Online.")

# --- Sidebar Navigation ---
page = st.sidebar.radio("🧭 Navigate", 
                        ["Home", "Email & Password Checker", "Document Scanner", "Privacy Policy Summarizer", "About"])

# --- Home ---
if page == "Home":
    st.info("""
    **Privacy Guardian** helps you:
    - Detect if your email or password was breached  
    - Scan documents for personal info (Aadhaar, emails etc.)  
    - Summarize privacy policies (coming soon)
    """)

# --- Email & Password Checker ---
elif page == "Email & Password Checker":
    st.markdown("## 🔐 Breach Checker")
    tab1, tab2 = st.tabs(["📧 Email Checker", "🔑 Password Checker"])

    with tab1:
        email = st.text_input("Enter your email:")
        if st.button("Check Email Breaches"):
            if email:
                breaches = check_mock_breaches(email)
                if breaches is None:
                    st.warning("⚠️ Email not found in our dataset.")
                elif len(breaches) == 0:
                    st.success("✅ No breaches found for this email.")
                else:
                    st.error(f"❌ Found in {len(breaches)} breaches:")
                    for site in breaches:
                        st.markdown(f"- {site}")
            else:
                st.warning("Please enter an email.")

    with tab2:
        password = st.text_input("Enter password:", type="password")
        if st.button("Check Password Breach"):
            if password:
                count = check_password_breaches(password)
                if count is None:
                    st.error("⚠️ Error connecting to API.")
                elif count == 0:
                    st.success("✅ This password has NOT been found in any breaches.")
                else:
                    st.error(f"⚠️ This password appeared {count:,} times in breaches!")
            else:
                st.warning("Please enter a password.")

# --- Document Scanner ---
elif page == "Document Scanner":
    st.markdown("## 📄 Document Scanner")
    st.write("Upload PDF, DOCX or TXT files to detect sensitive personal information.")

    uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])

    if uploaded_file:
        text, is_scanned = extract_text(uploaded_file)

        if is_scanned:
            # 📄 File is scanned or image-based
            st.warning("⚠️ Scanned or image-based documents are not supported for text extraction.")
        elif not text.strip():
            st.warning("⚠️ No readable text found in file.")
        else:
            # ✅ Normal text-based document
            st.success("✅ File uploaded and processed.")
            results = detect_personal_info(text)

            if results:
                has_sensitive = any(label != "✅ Status" for label, _ in results)
                if has_sensitive:
                    st.error("⚠️ Sensitive Information Detected:")
                else:
                    st.success("🎉 No personal information found in this document.")

                for label, matches in results:
                    st.write(f"**{label}:**")
                    for item in matches[:5]:
                        st.code(item)

            if st.checkbox("Show Extracted Text"):
                st.text_area("Document Content", text, height=250)

# --- About ---
elif page == "About":
    st.markdown("## ℹ️ About Privacy Guardian")
    st.write("""
    **Privacy Guardian** helps you protect your personal information and stay safe online.

    In today’s digital world, our data is constantly at risk — from online breaches to apps collecting private details.  
    **Privacy Guardian** makes it easy to understand and control how your data is used.

    ### What You Can Do:
    - 🔐 **Check Data Breaches:** Find out if your email or password has been leaked in any known cyber breaches.  
    - 📄 **Scan Documents:** Upload files to automatically detect sensitive details like Aadhaar numbers, phone numbers, or emails.  
    - 🧠 **Summarize Privacy Policies:** Instantly understand how websites use your data and identify potential risks.

    ### Why Use It:
    - Simple, fast, and completely secure.  
    - Helps you make informed decisions about your digital privacy.  
    - Designed for everyone — no technical knowledge required.

    **Your privacy, simplified.**
    """)

# --- Privacy Policy Summarizer ---
elif page == "Privacy Policy Summarizer":
    st.markdown("## 🧠 Privacy Policy Summarizer")
    st.write("Paste a privacy policy text or enter a link to summarize and detect potential risks.")

    option = st.radio("Input Type:", ["Text", "URL"])
    if option == "Text":
        text_input = st.text_area("Paste Privacy Policy Text:", height=250)
        if st.button("Summarize Policy"):
            if text_input.strip():
                from src.privacy_policy_summarizer import analyze_privacy_policy
                with st.spinner("Analyzing policy..."):
                    summary, risks = analyze_privacy_policy(text_input, is_url=False)
                st.subheader("🔍 Summary")
                st.write(summary)
                st.subheader("⚠️ Detected Risks")
                for r in risks:
                    st.warning(r)
            else:
                st.warning("Please enter some text.")
    else:
        url_input = st.text_input("Enter Privacy Policy URL:")
        if st.button("Fetch & Summarize"):
            if url_input.strip():
                from src.privacy_policy_summarizer import analyze_privacy_policy
                with st.spinner("Fetching and summarizing policy..."):
                    summary, risks = analyze_privacy_policy(url_input, is_url=True)
                st.subheader("🔍 Summary")
                st.write(summary)
                st.subheader("⚠️ Detected Risks")
                for r in risks:
                    st.warning(r)
            else:
                st.warning("Please enter a valid URL.")

# --- Footer ---
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #2C3E50;
    color: #ECF0F1;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    letter-spacing: 0.3px;
}
</style>

<div class='footer'>
    © 2025 Privacy Guardian — Powered by Python & Streamlit
</div>
""", unsafe_allow_html=True)
