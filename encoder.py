"""
encoder.py
----------
Payload Encoding Module
Supports: Base64, XOR (with user-defined key), ROT13
Each method provides both encode and decode functions.
"""

import base64
import codecs


# ─────────────────────────────────────────────
# Base64
# ─────────────────────────────────────────────

def base64_encode(payload: str) -> str:
    """Encode a string payload using Base64."""
    encoded_bytes = base64.b64encode(payload.encode("utf-8"))
    return encoded_bytes.decode("utf-8")


def base64_decode(encoded: str) -> str:
    """Decode a Base64-encoded string back to plaintext."""
    try:
        decoded_bytes = base64.b64decode(encoded.encode("utf-8"))
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        return f"[ERROR] Base64 decode failed: {e}"


# ─────────────────────────────────────────────
# XOR
# ─────────────────────────────────────────────

def xor_encode(payload: str, key: int) -> str:
    """
    XOR-encode each character of the payload with the given integer key.
    Returns a hex string (e.g. '41 62 3f ...').
    """
    if not (0 <= key <= 255):
        raise ValueError("XOR key must be an integer between 0 and 255.")
    xored = [ord(c) ^ key for c in payload]
    return " ".join(f"{b:02x}" for b in xored)


def xor_decode(hex_str: str, key: int) -> str:
    """
    Decode an XOR-encoded hex string back to plaintext using the same key.
    """
    if not (0 <= key <= 255):
        raise ValueError("XOR key must be an integer between 0 and 255.")
    try:
        bytes_list = [int(h, 16) for h in hex_str.strip().split()]
        return "".join(chr(b ^ key) for b in bytes_list)
    except Exception as e:
        return f"[ERROR] XOR decode failed: {e}"


# ─────────────────────────────────────────────
# ROT13
# ─────────────────────────────────────────────

def rot13_encode(payload: str) -> str:
    """Apply ROT13 substitution cipher to the payload."""
    return codecs.encode(payload, "rot_13")


def rot13_decode(encoded: str) -> str:
    """
    Decode a ROT13-encoded string.
    ROT13 is its own inverse — applying it twice restores the original.
    """
    return codecs.encode(encoded, "rot_13")


# ─────────────────────────────────────────────
# Layered / Chained encoding
# ─────────────────────────────────────────────

def layered_encode(payload: str, methods: list, xor_key: int = 42) -> dict:
    """
    Apply multiple encoding steps in sequence.

    Parameters
    ----------
    payload : str
        The raw payload string.
    methods : list of str
        Ordered list of methods: 'base64', 'xor', 'rot13'.
    xor_key : int
        Key used for XOR encoding (default 42).

    Returns
    -------
    dict with keys 'steps' (list of intermediate results) and 'final' (str).
    """
    current = payload
    steps = []

    for method in methods:
        method = method.lower().strip()
        if method == "base64":
            current = base64_encode(current)
            steps.append({"method": "Base64", "output": current})
        elif method == "xor":
            current = xor_encode(current, xor_key)
            steps.append({"method": f"XOR (key={xor_key})", "output": current})
        elif method == "rot13":
            current = rot13_encode(current)
            steps.append({"method": "ROT13", "output": current})
        else:
            raise ValueError(f"Unknown encoding method: '{method}'. Use base64, xor, or rot13.")

    return {"steps": steps, "final": current}
