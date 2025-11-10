import re
import requests
from bs4 import BeautifulSoup

# --- Fetch text from URL ---
def fetch_policy_text(url):
    """Fetch privacy policy text from a given URL."""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"Error fetching URL: {e}"

# --- Smarter summarizer ---
def summarize_policy(text):
    """Create a short, natural summary of what the policy does."""
    lower = text.lower()
    summary_parts = []

    if any(k in lower for k in ["collect", "gather", "obtain"]):
        summary_parts.append("collects personal data")
    if any(k in lower for k in ["email", "name", "contact"]):
        summary_parts.append("includes contact details")
    if any(k in lower for k in ["location", "gps"]):
        summary_parts.append("uses or tracks location")
    if any(k in lower for k in ["cookie", "tracking", "analytics"]):
        summary_parts.append("uses cookies or tracking tools")
    if any(k in lower for k in ["advertis", "marketing", "third-party"]):
        summary_parts.append("shares data with third parties or advertisers")
    if any(k in lower for k in ["store", "retain", "save"]):
        summary_parts.append("stores user data for some time")

    if summary_parts:
        summary = "This policy " + ", ".join(summary_parts) + "."
    else:
        summary = "This policy describes how the service handles user data."

    return summary.capitalize()

# --- Risk keyword extraction ---
def extract_risks(text):
    """Detect potential privacy risks using keyword search."""
    risks = []
    lower = text.lower()
    if any(k in lower for k in ["location", "gps"]):
        risks.append("📍 Shares or collects location data.")
    if any(k in lower for k in ["advertis", "marketing", "third-party"]):
        risks.append("🧩 Shares data with advertisers or third parties.")
    if "cookie" in lower or "tracking" in lower:
        risks.append("🍪 Uses cookies or tracking technologies.")
    if "retain" in lower or "store" in lower:
        risks.append("💾 Stores your data for retention.")
    if not risks:
        risks.append("✅ No obvious risks found.")
    return risks

# --- Main driver for Streamlit ---
def analyze_privacy_policy(input_text_or_url, is_url=False):
    if is_url:
        text = fetch_policy_text(input_text_or_url)
    else:
        text = input_text_or_url
    summary = summarize_policy(text)
    risks = extract_risks(text)
    return summary, risks
