import json
import hashlib
import requests

# Function 1: Local mock checker
def check_mock_breaches(email):
    """Check if email is found in mock JSON data."""
    with open("data/mock_breaches.json", "r") as file:
        data = json.load(file)
    return data.get(email.lower(), None)


# Function 2: Pwned Passwords checker (free API, no key needed)
def check_password_breaches(password):
    """Check if password hash appears in known breaches using Pwned Passwords API."""
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    hashes = (line.split(":") for line in response.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)

    return 0
