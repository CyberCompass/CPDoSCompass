#!/usr/bin/env python3
import sys
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

from cpdos_constants import CPDOS_ATTACKS
from cpdos_utils import extract_urls
from cpdos_attacks import process_urls
import math

async def main():
    """
    The main CLI for Compass CPDoS Attack Tool, with:
      - Baseline/post validation
      - Extension rewriting (ext1, ext2)
      - One-URL-per-domain or all-urls
      - Optional file saving via --output-dir
    """
    parser = argparse.ArgumentParser(description="Compass CPDoS Attack Tool")
    parser.add_argument("-u", "--url", help="Target URL (single mode)")
    parser.add_argument("-f", "--file", help="File containing URLs (batch mode)")
    parser.add_argument("-a", "--attack", help="Attack type (HHO, HMC, HMO, ALL)", default="ALL")
    parser.add_argument("--verbose", action="store_true", help="Show all request details")
    parser.add_argument("--validate", action="store_true", help="Compare baseline vs. post-attack responses")
    parser.add_argument("--ext1", help="Path extension for baseline (also used by attack if ext2 not given)", default=None)
    parser.add_argument("--ext2", help="Path extension for attack/post (only used if ext1 is also set)", default=None)
    parser.add_argument("--all-urls-per-domain", action="store_true",
                        help="By default only one URL per domain. Use this to allow all.")
    parser.add_argument("--output-dir", help="Directory to save HTTP responses", default=None)
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use for processing URLs")
    args = parser.parse_args()

    # Validate attack type
    attack_choice = args.attack.upper()
    if attack_choice not in CPDOS_ATTACKS and attack_choice != "ALL":
        print(f"[!] Invalid attack type: {attack_choice}. "
              f"Choose from: {', '.join(CPDOS_ATTACKS.keys())}, or ALL.", file=sys.stderr)
        sys.exit(1)

    # Gather URLs from file, URL arg, or stdin
    collected_urls = []
    if args.file:
        try:
            with open(args.file, "r") as f:
                lines = f.read().splitlines()
            collected_urls = extract_urls(lines, single_per_domain=not args.all_urls_per_domain)
        except Exception as e:
            print(f"[!] Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.url:
        collected_urls = [args.url.strip()]
    else:
        # check if stdin is piped
        if not sys.stdin.isatty():
            stdin_lines = sys.stdin.read().splitlines()
            collected_urls = extract_urls(stdin_lines, single_per_domain=not args.all_urls_per_domain)

    if not collected_urls:
        print("[!] No valid URLs found. Provide -u or -f, or pipe URLs via STDIN.", file=sys.stderr)
        sys.exit(1)


    # Split the collected URLs into chunks for each thread
    num_threads = args.threads if len(collected_urls) > args.threads else 1
    chunk_size = math.ceil(len(collected_urls) / num_threads)
    url_chunks = [collected_urls[i:i + chunk_size] for i in range(0, len(collected_urls), chunk_size)]

    tasks = [
        asyncio.create_task(
            process_urls(
                urls=chunk,
                attack_type=attack_choice,
                verbose=args.verbose,
                validate=args.validate,
                ext1=args.ext1,
                ext2=args.ext2,
                output_dir=args.output_dir
            )
        )
        for chunk in url_chunks
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
