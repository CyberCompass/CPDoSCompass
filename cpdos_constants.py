# Known CPDoS attack types
CPDOS_ATTACKS = {
    "HHO": "HTTP Header Oversize",
    "HMC": "HTTP Meta Character",
    "HMO": "HTTP Method Override"
}

# Minimal cache bypass header
CACHE_BYPASS_HEADERS = {
    "Cache-Control": "no-cache"
}

# Realistic browser-like headers
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}
