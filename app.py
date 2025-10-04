import streamlit as st
from src.breach_checker import check_mock_breaches, check_password_breaches
from src.document_scanner import extract_text, detect_personal_info

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
                        ["Home", "Email & Password Checker", "Document Scanner", "About"])

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
        text = extract_text(uploaded_file)
        if not text.strip():
            st.warning("⚠️ No readable text found in file.")
        else:
            st.success("✅ File uploaded and processed.")
            results = detect_personal_info(text)
            if results:
                st.error("⚠️ Sensitive Information Detected:")
                for label, matches in results:
                    st.write(f"**{label}:**")
                    for item in matches[:5]:
                        st.code(item)
            else:
                st.success("🎉 No personal information found in this document.")
            if st.checkbox("Show Extracted Text"):
                st.text_area("Document Content", text, height=250)

# --- About ---
elif page == "About":
    st.markdown("## ℹ️ About Privacy Guardian")
    st.write("""
    **Technologies:** Python 3.10+, Streamlit, Pandas, PDFPlumber, Regex  
    **Upcoming Feature:** 🧠 Privacy Policy Summarizer using Hugging Face  
    👩‍💻 Developed by : **Your Name**
    """)

# --- Footer ---
st.markdown("<div class='footer'>🔐 Privacy Guardian | Built with ❤️ using Python & Streamlit</div>", 
            unsafe_allow_html=True)
