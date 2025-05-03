import re

# Fake-Domain-Muster für einfache Phishing-Erkennung
phishy_domains = [
    "paypai", "goog1e", "micr0soft", "instagrarn",
    "faceb00k", "amaz0n", "sparkassse", "kundencenter",
    "dhl-paket", "securelogin"
]

def scan_links(text):
    links = re.findall(r'(https?://[^\s]+)', text)
    feedback = []

    for link in links:
        is_phishy = any(phish in link for phish in phishy_domains)
        if is_phishy:
            feedback.append(f"🚨 Verdächtiger Link erkannt: {link} enthält ein typisches Phishing-Muster.")
        else:
            feedback.append(f"✅ Link geprüft: {link} sieht unauffällig aus.")

    return feedback if feedback else []
