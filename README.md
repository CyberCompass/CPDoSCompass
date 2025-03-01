
# CyberCompass CPDoS Attack Tool (`cccpdos`)

A command-line tool for detecting **Cache Poisoned Denial of Service (CPDoS)** vulnerabilities across web resources delivered by CDNs or caching proxies. It operates in single-target or batch mode, supports optional extension rewriting for advanced cache poisoning tests, and can optionally save raw HTTP responses to an output directory.

---

## **🚀 One-Step Installation**

> **Prerequisites**:  
> - Python 3.8+  
> - A POSIX-like system (macOS, Linux, *BSD, or Windows WSL)

Run this **one command** to fetch all necessary files directly from **raw.githubusercontent.com**, place them into `/usr/local/share/cccpdos`, and create the `cccpdos` launcher under `/usr/local/bin`:

```bash
sudo mkdir -p /usr/local/share/cccpdos && \
sudo curl -sSL "https://raw.githubusercontent.com/CyberCompass/CPDoSCompass/main/cpdos_constants.py" -o /usr/local/share/cccpdos/cpdos_constants.py && \
sudo curl -sSL "https://raw.githubusercontent.com/CyberCompass/CPDoSCompass/main/cpdos_utils.py" -o /usr/local/share/cccpdos/cpdos_utils.py && \
sudo curl -sSL "https://raw.githubusercontent.com/CyberCompass/CPDoSCompass/main/cpdos_requests.py" -o /usr/local/share/cccpdos/cpdos_requests.py && \
sudo curl -sSL "https://raw.githubusercontent.com/CyberCompass/CPDoSCompass/main/cpdos_attacks.py" -o /usr/local/share/cccpdos/cpdos_attacks.py && \
sudo curl -sSL "https://raw.githubusercontent.com/CyberCompass/CPDoSCompass/main/main.py" -o /usr/local/share/cccpdos/main.py && \
sudo bash -c 'echo "#!/usr/bin/env bash
exec python3 /usr/local/share/cccpdos/main.py \"\$@\"" > /usr/local/bin/cccpdos' && \
sudo chmod +x /usr/local/bin/cccpdos
```

You can then run **`cccpdos`** from anywhere. All `.py` files are stored in `/usr/local/share/cccpdos`, and no local clone is needed.

---

## **📌 Usage**

### **1. Single-Target Scan**
```bash
cccpdos -u https://example.com -a HHO
```
- **`-u`**: Single URL  
- **`-a`**: Attack type (**HHO**, **HMC**, **HMO**, or **ALL**)  
- Runs an **HTTP Header Oversize** (HHO) attack against `https://example.com`.

### **2. File Mode**
```bash
cccpdos -f urls.txt -a ALL --validate
```
- **`-f`**: File input mode  
- **`-a ALL`**: Performs **all** CPDoS attacks sequentially  
- **`--validate`**: Sends **baseline** + **post-attack** requests to confirm if the CDN cache was actually poisoned.

### **3. Reading from STDIN**
```bash
cat subdomains.txt | cccpdos -a HHO --verbose
```
- Reads URLs from `subdomains.txt` (via pipe)  
- Attacks each with **HHO** and prints full details (`--verbose`).

---

## **Key Flags & Options**

| Flag                          | Description                                                                    |
|-------------------------------|--------------------------------------------------------------------------------|
| **`-u, --url`**              | Single target URL (e.g. `https://victim.com`).                                 |
| **`-f, --file`**             | File with multiple URLs (one per line).                                        |
| **`-a, --attack`**           | Attack type: `HHO`, `HMC`, `HMO`, or `ALL`.                                    |
| **`--validate`**             | Compare baseline & post-attack responses (sends **3 requests**).              |
| **`--verbose`**              | Print full request/response details.                                          |
| **`--ext1/--ext2`**          | Rewrite path extensions for baseline vs. attack requests.                      |
| **`--all-urls-per-domain`**  | By default, only 1 URL per domain is processed; use this to allow them all.    |
| **`--output-dir`**           | Directory to save raw HTTP responses (baseline, attack, etc.).                |

---

## **Attack Types Explained (`-a, --attack`)**  

| Attack Type  | Description |
|-------------|------------|
| **HHO** *(HTTP Header Oversize)* | Exploits CDNs that cannot handle large headers by injecting oversized headers, forcing cache poisoning or errors. |
| **HMC** *(HTTP Meta Character Injection)* | Injects newline characters (`\r\n`) inside headers to manipulate CDN caching logic and cause misinterpretation. |
| **HMO** *(HTTP Method Override)* | Uses HTTP method override headers (e.g., `X-HTTP-Method-Override: DELETE`) to attempt cache poisoning or response manipulation. |
| **ALL** | Runs all three attack types sequentially on each target. |

---

## **Why `cccpdos`?**

- **Detects CPDoS vulnerabilities** capable of forcing cached error pages or hijacking content.
- **Extension rewriting** (`--ext1`, `--ext2`) to test advanced web cache deception or partial object caching.
- **Validation mode** (`--validate`) to confirm actual CDN cache poisoning.
- **Minimal external dependencies** → easily runs on most Unix-like environments.

---

## **Examples**

1. **All Attacks, Single URL, Validation + Save Responses**  
   ```bash
   cccpdos -u https://shop.example.com -a ALL --validate --output-dir cpdos_out
   ```
   Sends baseline → attack → post-attack for each CPDoS vector (HHO, HMC, HMO), saves raw responses in `cpdos_out`.

2. **Batch Mode (File), HMC Attack**  
   ```bash
   cccpdos -f domains.txt -a HMC --verbose
   ```
   Tests **HTTP Meta Character** injection on every URL in `domains.txt`, printing all details.

3. **STDIN + Extension Rewriting**  
   ```bash
   cat subdomains.httpx | cccpdos -a HHO --ext1 css
   ```
   Reads subdomains from `subdomains.httpx`, rewrites each path to `.css`, then runs an **HHO** attack.

---

## **Project Layout**

- **`main.py`** – CLI entry point.  
- **`cpdos_attacks.py`** – Attack logic (baseline, post-attack, saving responses).  
- **`cpdos_requests.py`** – Raw HTTP request & response parsing.  
- **`cpdos_utils.py`** – Helpers (extension rewriting, cachebusters, domain-limiting).  
- **`cpdos_constants.py`** – Attack mapping & default headers.

> Files are copied into `/usr/local/share/cccpdos`, with the launcher script at `/usr/local/bin/cccpdos`.

---

## **Disclaimer**
This tool is intended for **authorized security testing**. Always obtain permission before scanning any target. **Use responsibly and at your own risk.**

---

### **Happy CPDoS Hunting!**  
For questions or contributions, open an issue or pull request on GitHub.