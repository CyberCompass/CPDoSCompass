import socket
import ssl
import re
import hashlib
import sys

from cpdos_constants import BROWSER_HEADERS, CACHE_BYPASS_HEADERS

def send_raw_http_request(target_url, headers=None, verbose=False, validate=False):
    """
    Sends a raw HTTP GET request. Returns:
        (status_code, length_of_body, md5_hash_of_body, raw_response, x_cache_value)
    We only do a single recv(4096), as in the original code.
    """
    import urllib.parse  # local import to avoid cross-module issues

    parsed_url = urllib.parse.urlparse(target_url)
    host = parsed_url.hostname
    path = parsed_url.path if parsed_url.path else "/"
    port = parsed_url.port if parsed_url.port else (443 if target_url.lower().startswith("https") else 80)

    sock = socket.create_connection((host, port))
    if port == 443:
        context = ssl.create_default_context()
        try:
            sock = context.wrap_socket(sock, server_hostname=host)
        except ssl.SSLCertVerificationError as e:
            if verbose:
                print(f"[!] SSL certificate verification failed: {e}", file=sys.stderr)
            return None, None, None, b"", "N/A"
        except Exception as e:
            if verbose:
                print(f"[!] SSL wrapping failed: {e}", file=sys.stderr)
            return None, None, None ,b"", "N/A"

    try:
        request_lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}"
        ]
        merged_headers = {**BROWSER_HEADERS, **CACHE_BYPASS_HEADERS, **(headers or {})}
        for k, v in merged_headers.items():
            request_lines.append(f"{k}: {v}")
        request_lines.append("\r\n")

        raw_request = "\r\n".join(request_lines).encode("utf-8")
        sock.sendall(raw_request)

        # NOTE: Original code only does one .recv(4096). This may be partial.
        raw_response = sock.recv(4096)
        response_str = raw_response.decode("utf-8", errors="ignore")

        status_match = re.search(r"HTTP/\d\.\d (\d+)", response_str)
        status_code = int(status_match.group(1)) if status_match else 0

        body_start = response_str.find("\r\n\r\n") + 4
        headers_part = response_str[:body_start]
        response_body = response_str[body_start:]
        response_length = len(response_body)
        response_hash = hashlib.md5(response_body.encode()).hexdigest()

        x_cache_match = re.search(r"x-cache:\s*([^\r\n]+)", headers_part, re.IGNORECASE)
        x_cache_value = x_cache_match.group(1) if x_cache_match else "N/A"

        # Additional info
        age_match = re.search(r"age:\s*(\d+)", headers_part, re.IGNORECASE)
        cache_control_match = re.search(r"cache-control:\s*([^\r\n]+)", headers_part, re.IGNORECASE)

        age_value = age_match.group(1) if age_match else "N/A"
        cache_control_value = cache_control_match.group(1) if cache_control_match else "N/A"

        # Print detail if:
        #   - verbose; or
        #   - there's a non-empty X-Cache and we're NOT validating
        if verbose or (not validate and x_cache_value != "N/A"):
            print(f"\n--- Response for {target_url} ---")
            print(f"Status: {status_code} | Length: {response_length}")
            print(f"Body Hash: {response_hash} | X-Cache: {x_cache_value}")
            print(f"Age: {age_value} | Cache-Control: {cache_control_value}\n")

        return status_code, response_length, response_hash, raw_response, x_cache_value

    except Exception as e:
        if verbose:
            print(f"[!] Request failed: {e}", file=sys.stderr)
        return None, None, None, b"", "N/A"
    finally:
        sock.close()
