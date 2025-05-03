import re
import requests

# Liste verdächtiger Domainmuster (einfach erweiterbar)
SUSPICIOUS_PATTERNS = [
    r"paypal\.(?!com)",       # z. B. paypal-login.net
    r"paypai\.",              # häufige Falschschreibung von PayPal
    r"login[-.]?secure",      # typisches Muster
    r"(web|login)[\.-]?account", 
    r"banking[-.]?verify"
]

# Liste vertrauenswürdiger Domains (Whitelist)
TRUSTED_DOMAINS = [
    "tagesschau.de",
    "zeit.de",
    "spiegel.de",
    "bund.de",
    "europa.eu"
]

def extract_links(text):
    # Extrahiert http(s)-Links aus dem Text
    return re.findall(r"https?://[^\s]+", text)

def is_suspicious_link(link):
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, link, re.IGNORECASE):
            return True
    return False

def is_trusted(link):
    for domain in TRUSTED_DOMAINS:
        if domain in link:
            return True
    return False

def scan_links(text):
    results = []
    links = extract_links(text)
    
    for link in links:
        if is_suspicious_link(link):
            results.append({
                "link": link,
                "result": f"🚨 Verdächtiger Link erkannt: {link} enthält ein typisches Phishing-Muster."
            })
        elif is_trusted(link):
            results.append({
                "link": link,
                "result": f"✅ Link geprüft: {link} scheint unbedenklich."
            })
        else:
            results.append({
                "link": link,
                "result": f"ℹ️ Link gefunden: {link} konnte nicht eindeutig verifiziert werden."
            })
    return results
