import re

# Liste bekannter gefährlicher Muster (einfach erweiterbar)
PHISHING_PATTERNS = [
    r"paypai\.de",         # Typosquatting von PayPal
    r"secure-login",       # häufige Fake-Login-Pfade
    r"update-verifizierung", 
    r"konto-sperrung", 
    r"login-\w+\.com", 
    r"\.ru",               # ggf. für Tests auffällig
    r"bit\.ly",            # Kurzlinks (können verschleiern)
]

# Whitelist vertrauenswürdiger Domains
TRUSTED_DOMAINS = [
    "https://www.tagesschau.de",
    "https://heise.de",
    "https://netzpolitik.org",
    "https://www.bsi.bund.de"
]

def is_trusted(url):
    for trusted in TRUSTED_DOMAINS:
        if url.startswith(trusted):
            return True
    return False

def looks_phishy(url):
    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True, f"enthält ein typisches Phishing-Muster ({pattern})"
    return False, ""

def scan_links(urls):
    results = []
    for url in urls:
        url = url.strip(".,;!?\"'")
        if is_trusted(url):
            results.append({
                "url": url,
                "risk": False,
                "reason": "sieht unauffällig aus."
            })
        else:
            is_phishy, reason = looks_phishy(url)
            results.append({
                "url": url,
                "risk": is_phishy,
                "reason": reason if is_phishy else "scheint unbedenklich."
            })
    return results
