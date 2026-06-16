# Custom Payload Encoder & Obfuscation Framework

> **⚠ DISCLAIMER — FOR EDUCATIONAL USE ONLY**  
> This framework is designed exclusively for academic study, authorized red-team research, and lab environments. Never use this tool against systems you do not own or have explicit written permission to test.

---

## Project Overview

A practical payload encoding and obfuscation framework built to study how offensive payloads are transformed to evade signature-based detection systems (AV, EDR, IPS, firewalls).

### What it does

| Module | Capability |
|--------|-----------|
| **Encoder** | Base64, XOR (user-defined key), ROT13, multi-layer chaining |
| **Obfuscator** | 6 distinct string obfuscation techniques |
| **Evasion Tester** | Simulated signature-based detection engine with 35+ default signatures |
| **Report Generator** | Full comparison report with bypass rates |

---

## Project Structure

```
payload encoder/
├── main.py               ← Entry point (interactive + CLI)
├── encoder.py            ← Encoding module (Base64 / XOR / ROT13)
├── obfuscator.py         ← String obfuscation module
├── evasion_tester.py     ← Detection engine + evasion comparison
├── report_generator.py   ← Report builder
├── samples/
│   └── sample_payloads.txt   ← Example test payloads
├── reports/              ← Auto-created, stores generated .txt reports
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.8 or higher  
- No external dependencies — uses only the Python standard library

### Run (Interactive Mode)

```bash
python main.py
```

### Run (CLI Mode)

```bash
# Single payload
python main.py --payload "whoami"

# Custom XOR key
python main.py --payload "net user" --xor-key 77

# Multi-layer encoding (base64 → then xor)
python main.py --payload "ipconfig" --layer base64,xor --xor-key 33

# Load payload from file
python main.py --file samples/sample_payloads.txt

# Quiet mode (suppress console, still saves report)
python main.py --payload "mimikatz" --quiet --output-dir ./results
```

---

## Modules

### `encoder.py` — Encoding Module

| Function | Description |
|----------|-------------|
| `base64_encode(payload)` | Base64-encode a string |
| `base64_decode(encoded)` | Decode Base64 back to plaintext |
| `xor_encode(payload, key)` | XOR each character with key (0–255), returns hex string |
| `xor_decode(hex_str, key)` | Reverse XOR encoding |
| `rot13_encode(payload)` | Apply ROT13 substitution cipher |
| `rot13_decode(encoded)` | Reverse ROT13 (self-inverse) |
| `layered_encode(payload, methods, xor_key)` | Chain multiple encoding steps |

### `obfuscator.py` — String Obfuscation Module

| Technique | Description |
|-----------|-------------|
| Junk insertion | Injects random characters between payload characters |
| Char split | Represents string as `"c"+"m"+"d"` concatenation |
| Reversal | Reverses the payload string |
| Unicode escape | Converts each character to `\u00XX` form |
| Case alternation | Alternates UPPER/lower case (e.g. `WhOaMi`) |
| Hex interleave | Converts characters to hex with null-byte delimiter |

### `evasion_tester.py` — Detection Engine

- 35+ default signatures covering: shell commands, download cradles, reverse-shell patterns, SQL injection, XSS, and known malware names
- `SignatureDetector.scan(payload)` — scan a single payload
- `SignatureDetector.compare(original, variants)` — compare original vs. all encoded/obfuscated variants
- Returns structured `EvasionReport` with bypass rates

### `report_generator.py` — Reporting Engine

Produces a structured `.txt` report containing:
- Encoded payload outputs
- Obfuscated payload outputs  
- Per-variant detection results
- Bypass rate / detection rate statistics
- Decode verification section

---

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║    CUSTOM PAYLOAD ENCODER & OBFUSCATION FRAMEWORK v1.0      ║
╚══════════════════════════════════════════════════════════════╝

STEP 1 — ENCODING
  [Base64]  d2hvYW1p
  [XOR k=42] 5d 46 52 47 52 4b
  [ROT13]   jubnzv

STEP 2 — STRING OBFUSCATION
  [Junk Insert]      w!@#h#$o$%a%^m^&i…
  [Char Split]       "w"+"h"+"o"+"a"+"m"+"i"
  [Reversal]         imaohw
  [Unicode Escape]   \u0077\u0068\u006f\u0061\u006d\u0069
  [Case Alternation] WhOaMi
  [Hex Interleave]   \x77\x00\x68\x00\x6f…

STEP 3 — EVASION TESTING
  Original                       → 🔴 DETECTED
  Base64 encoded                 → 🟢 BYPASSED
  XOR encoded                    → 🟢 BYPASSED
  ROT13 encoded                  → 🟢 BYPASSED
  …
  Bypass rate   : 88.9%
  Detection rate: 11.1%
```

---

## Workflow Architecture

```
START
  │
  ▼
Load Payload (string / file)
  │
  ▼
Select Encoding Methods (Base64 / XOR / ROT13 / Layered)
  │
  ▼
Apply String Obfuscation (6 techniques)
  │
  ▼
Run Evasion Test (signature matching on original + all variants)
  │
  ▼
Generate Report → ./reports/evasion_report_<timestamp>.txt
  │
  ▼
END
```

---

## Learning Outcomes

- How payloads are transformed to evade static signature detection
- Why XOR / Base64 encoding bypasses simple pattern matching
- How obfuscation complicates malware analysis
- Why layered security and behavioral detection are necessary
- How red teams hide malicious content in real engagements

---

## License & Ethics

This project is intended solely for:
- Academic coursework and study
- Authorized penetration testing in lab environments
- Security research with explicit written permission

**Misuse of this framework is illegal and unethical. Always obtain written permission before testing any system.**
