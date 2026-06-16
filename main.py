"""
main.py
-------
Custom Payload Encoder & Obfuscation Framework
Main entry point — interactive CLI

Usage:
    python main.py                        # Interactive guided mode
    python main.py --payload "whoami"     # Quick non-interactive run
    python main.py --help                 # Show all options

Workflow:
    1. Load payload (from argument, file, or interactive prompt)
    2. Apply selected encoding methods
    3. Apply string obfuscation techniques
    4. Run evasion testing (original + all variants)
    5. Generate & save report
"""

import argparse
import os
import sys
import datetime
import io

# ── Fix Windows console UTF-8 output ────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Local modules ────────────────────────────
from encoder import (
    base64_encode, base64_decode,
    xor_encode,    xor_decode,
    rot13_encode,  rot13_decode,
    layered_encode,
)
from obfuscator import apply_all_techniques
from evasion_tester import SignatureDetector
from report_generator import ReportGenerator


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

BANNER = r"""
+==============================================================+
|   CUSTOM PAYLOAD ENCODER & OBFUSCATION FRAMEWORK v1.0       |
|   ----------------------------------------------------       |
|   FOR EDUCATIONAL & AUTHORIZED RED-TEAM RESEARCH ONLY       |
+==============================================================+
"""

ENCODING_CHOICES = {
    "1": "base64",
    "2": "xor",
    "3": "rot13",
    "4": "all",
}

EVASION_DISCLAIMER = (
    "\n[!] DISCLAIMER: This tool is intended SOLELY for educational use in\n"
    "   controlled lab environments. Do NOT use against systems you do\n"
    "   not own or have explicit written authorisation to test.\n"
)


def _separator(char: str = "-", width: int = 64) -> str:
    return char * width


def _print_section(title: str) -> None:
    print(f"\n{_separator()}\n  {title}\n{_separator()}")


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _load_payload_from_file(path: str) -> str:
    """Read raw payload from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────
# Core pipeline
# ─────────────────────────────────────────────

def run_pipeline(
    payload: str,
    xor_key: int = 42,
    layered_methods: list = None,
    verbose: bool = True,
    output_dir: str = ".",
) -> dict:
    """
    Execute the full encode → obfuscate → test → report pipeline.

    Returns a dict with all results.
    """

    if verbose:
        print(BANNER)
        print(EVASION_DISCLAIMER)

    # ── Step 1: Encoding ──────────────────────
    if verbose:
        _print_section("STEP 1 — ENCODING")

    b64_encoded  = base64_encode(payload)
    xor_encoded  = xor_encode(payload, xor_key)
    rot13_encoded = rot13_encode(payload)

    encoding_results = {
        "base64": b64_encoded,
        "xor":    {"output": xor_encoded, "key": xor_key},
        "rot13":  rot13_encoded,
    }

    if layered_methods:
        layered_result = layered_encode(payload, layered_methods, xor_key=xor_key)
        encoding_results["layered"] = layered_result

    if verbose:
        trunc = lambda s: s[:70] + ('...' if len(s) > 70 else '')
        print(f"  [Base64] {trunc(b64_encoded)}")
        print(f"  [XOR k={xor_key}] {trunc(xor_encoded)}")
        print(f"  [ROT13]  {trunc(rot13_encoded)}")
        if layered_methods:
            print(f"  [Layered ({'+'.join(layered_methods)})] {trunc(encoding_results['layered']['final'])}")

    # ── Step 2: Obfuscation ───────────────────
    if verbose:
        _print_section("STEP 2 — STRING OBFUSCATION")

    obf_results = apply_all_techniques(payload)

    if verbose:
        for name, data in obf_results.items():
            label = name.replace("_", " ").title()
            val   = data.get("obfuscated", "?") if isinstance(data, dict) else str(data)
            print(f"  [{label}] {val[:65]}{'...' if len(val) > 65 else ''}")

    # ── Step 3: Evasion Testing ───────────────
    if verbose:
        _print_section("STEP 3 — EVASION TESTING")

    # Collect all variants to test
    variants = {
        "Base64 encoded":          b64_encoded,
        "XOR encoded":             xor_encoded,
        "ROT13 encoded":           rot13_encoded,
        "Junk insert":             obf_results["junk_insert"]["obfuscated"],
        "Char split":              obf_results["char_split"]["obfuscated"],
        "Reversed":                obf_results["reversal"]["obfuscated"],
        "Unicode escape":          obf_results["escape_unicode"]["obfuscated"],
        "Case alternation":        obf_results["case_alternation"]["obfuscated"],
        "Hex interleave":          obf_results["hex_interleave"]["obfuscated"],
    }

    if layered_methods:
        variants[f"Layered ({'+'.join(layered_methods)})"] = encoding_results["layered"]["final"]

    detector    = SignatureDetector()
    evasion_rpt = detector.compare(payload, variants)

    if verbose:
        orig = evasion_rpt.original
        print(f"  Original -> {orig.status}")
        if orig.matched_signatures:
            sigs_preview = orig.matched_signatures[:3]
            ellipsis = '...' if len(orig.matched_signatures) > 3 else ''
            print(f"    Matched: {', '.join(sigs_preview)}{ellipsis}")

        print()
        for v in evasion_rpt.variants:
            print(f"  {v.payload_label:<30} -> {v.status}")

        print(f"\n  Bypass rate   : {evasion_rpt.bypass_rate}%")
        print(f"  Detection rate: {evasion_rpt.detection_rate}%")

    # ── Step 4: Report ────────────────────────
    if verbose:
        _print_section("STEP 4 — GENERATING REPORT")

    rpt_gen = ReportGenerator(payload)
    rpt_gen.add_encoding_results(encoding_results)
    rpt_gen.add_obfuscation_results(obf_results)
    rpt_gen.add_evasion_report(evasion_rpt)

    # Decoding verification section
    xor_decoded_check = xor_decode(xor_encoded, xor_key)
    b64_decoded_check = base64_decode(b64_encoded)
    decode_section = (
        f"  Base64 decoded : {b64_decoded_check[:60]}\n"
        f"  XOR decoded    : {xor_decoded_check[:60]}\n"
        f"  ROT13 decoded  : {rot13_decode(rot13_encoded)[:60]}"
    )
    rpt_gen.add_custom_section("DECODE VERIFICATION", decode_section)

    # Save report
    os.makedirs(output_dir, exist_ok=True)
    report_filename = os.path.join(output_dir, f"evasion_report_{_timestamp()}.txt")
    saved_path = rpt_gen.save(report_filename)

    if verbose:
        print(f"\n  [OK] Report saved to: {saved_path}")

    return {
        "encoding":     encoding_results,
        "obfuscation":  obf_results,
        "evasion":      evasion_rpt,
        "report_path":  saved_path,
    }


# ─────────────────────────────────────────────
# Interactive mode
# ─────────────────────────────────────────────

def interactive_mode() -> None:
    print(BANNER)
    print(EVASION_DISCLAIMER)

    # ── Payload input ─────────────────────────
    _print_section("PAYLOAD INPUT")
    print("  [1] Enter payload directly")
    print("  [2] Load from file")
    choice = input("\n  Select option [1/2]: ").strip()

    if choice == "2":
        fpath = input("  File path: ").strip()
        if not os.path.isfile(fpath):
            print(f"  [ERROR] File not found: {fpath}")
            sys.exit(1)
        payload = _load_payload_from_file(fpath)
        print(f"  [OK] Loaded {len(payload)} characters from file.")
    else:
        payload = input("  Enter payload string: ").strip()
        if not payload:
            print("  [ERROR] Payload cannot be empty.")
            sys.exit(1)

    # ── XOR key ───────────────────────────────
    _print_section("XOR KEY")
    raw_key = input("  Enter XOR key (integer 0–255) [default: 42]: ").strip()
    try:
        xor_key = int(raw_key) if raw_key else 42
        if not (0 <= xor_key <= 255):
            raise ValueError
    except ValueError:
        print("  [WARN] Invalid key, using default 42.")
        xor_key = 42

    # ── Layered encoding ──────────────────────
    _print_section("LAYERED ENCODING (optional)")
    print("  Apply multiple encoding steps in sequence.")
    print("  Enter methods in order separated by commas (e.g. base64,xor,rot13)")
    print("  Leave blank to skip.")
    raw_layer = input("  Layered methods: ").strip()
    layered_methods = [m.strip() for m in raw_layer.split(",") if m.strip()] if raw_layer else None

    # ── Output directory ──────────────────────
    _print_section("OUTPUT DIRECTORY")
    out_dir = input("  Save report to directory [default: ./reports]: ").strip()
    if not out_dir:
        out_dir = "./reports"

    # ── Run pipeline ──────────────────────────
    run_pipeline(
        payload=payload,
        xor_key=xor_key,
        layered_methods=layered_methods,
        verbose=True,
        output_dir=out_dir,
    )


# ─────────────────────────────────────────────
# CLI argument parser
# ─────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="payload_encoder",
        description="Custom Payload Encoder & Obfuscation Framework — Educational Use Only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --payload \"whoami\"\n"
            "  python main.py --payload \"net user\" --xor-key 77 --layer base64,xor\n"
            "  python main.py --file payload.txt --output-dir ./results\n"
            "  python main.py  (no args = interactive mode)\n"
        ),
    )

    parser.add_argument(
        "--payload", "-p",
        type=str,
        default=None,
        help="Raw payload string to encode/obfuscate.",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Path to a text file containing the payload.",
    )
    parser.add_argument(
        "--xor-key", "-k",
        type=int,
        default=42,
        help="XOR key (integer 0–255). Default: 42.",
    )
    parser.add_argument(
        "--layer", "-l",
        type=str,
        default=None,
        help="Comma-separated layered encoding methods (e.g. base64,xor,rot13).",
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./reports",
        help="Directory to save the generated report. Default: ./reports",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress console output (report still saved).",
    )
    return parser


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    # No arguments → interactive mode
    if args.payload is None and args.file is None:
        interactive_mode()
        return

    # Load payload
    if args.file:
        if not os.path.isfile(args.file):
            print(f"[ERROR] File not found: {args.file}")
            sys.exit(1)
        payload = _load_payload_from_file(args.file)
    else:
        payload = args.payload

    # Layered methods
    layered_methods = (
        [m.strip() for m in args.layer.split(",") if m.strip()]
        if args.layer else None
    )

    run_pipeline(
        payload=payload,
        xor_key=args.xor_key,
        layered_methods=layered_methods,
        verbose=not args.quiet,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
