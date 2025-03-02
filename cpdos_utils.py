import re
import urllib.parse
import random

def adjust_extension(url: str, new_ext: str) -> str:
    """
    If the URL's path has an extension, replace it with new_ext;
    if not, append new_ext. Example:
      /path/image.png -> /path/image.jpg
      /path/endpoint  -> /path/endpoint.css
    """
    if not new_ext.startswith("."):
        new_ext = "." + new_ext

    parsed = urllib.parse.urlparse(url)
    path = parsed.path or "/"

    if "/" in path:
        base_dir, filename = path.rsplit("/", 1)
    else:
        base_dir, filename = "", path

    filename = filename.strip("/")
    if "." in filename:
        filename = filename[:filename.rfind(".")]
    filename += new_ext

    if base_dir:
        if not base_dir.startswith("/"):
            base_dir = "/" + base_dir
        new_path = f"{base_dir}/{filename}"
    else:
        new_path = f"/{filename}"

    return parsed._replace(path=new_path).geturl()


def add_cachebuster(url: str, cb_value: str) -> str:
    """
    Append a query param 'cb=cb_value' to the given URL.
    E.g., https://site.com/path -> https://site.com/path?cb=123456
    """
    parsed = urllib.parse.urlparse(url)
    query = parsed.query
    new_param = f"cb={cb_value}"
    new_query = f"{query}&{new_param}" if query else new_param
    return parsed._replace(query=new_query).geturl()


def random_cachebuster() -> str:
    """Generate a random 6-digit string for cache-busting."""
    return str(random.randint(100000, 999999))


def extract_urls(lines, single_per_domain=True):
    """
    Find valid http(s) URLs in each line.
    If single_per_domain=True, returns only one URL per domain.
    If multiple URLs for a domain exist, the preference is:
      - third occurrence if present,
      - else second,
      - else first.
    """
    domain_urls = {}
    for line in lines:
        match = re.search(r"https?://[^\s]+", line)
        if match:
            url = match.group()
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            domain_urls.setdefault(domain, []).append(url)

    if single_per_domain:
        selected = []
        for urls in domain_urls.values():
            if len(urls) >= 3:
                selected.append(urls[2])
            elif len(urls) >= 2:
                selected.append(urls[1])
            else:
                selected.append(urls[0])
        return selected
    else:
        # Return all found URLs
        return [url for urls in domain_urls.values() for url in urls]


def generate_filename(url: str, suffix: str) -> str:
    """
    Build a filename from the URL's domain+path, replacing '/' with '.'.
    Then append an extra suffix (e.g., baseline/attack/post) plus '.txt'.
    """
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    path = parsed.path.replace("/", ".")
    if not path:
        path = ".root"  # If the path is '/', we just say '.root'
    # Example: domain=cdn.shopify.com, path=.s.files.1.1040.0152.files.image.png
    # Suffix might be 'baseline', 'attack', or 'post'
    return f"{domain}{path}.{suffix}.txt"
