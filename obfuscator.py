"""
obfuscator.py
-------------
String Obfuscation Module
Implements multiple reversible and irreversible obfuscation techniques:
  - Random junk character insertion
  - Character splitting & concatenation (Python string concat form)
  - String reversal
  - Escape-sequence / Unicode obfuscation
  - Case alternation
  - Null-byte interleaving (hex representation)
"""

import random
import string


# ─────────────────────────────────────────────
# 1. Random junk character insertion
# ─────────────────────────────────────────────

def junk_insert(payload: str, junk_chars: str = "!@#$%^&*~`", density: int = 3) -> dict:
    """
    Insert random junk characters into the payload at random positions.

    Parameters
    ----------
    payload    : str  – original string
    junk_chars : str  – pool of junk characters to choose from
    density    : int  – approx. number of junk chars inserted per real char (default 3)

    Returns
    -------
    dict with 'obfuscated' (str) and 'junk_chars_used' (str).
    """
    result = []
    for ch in payload:
        result.append(ch)
        for _ in range(random.randint(1, density)):
            result.append(random.choice(junk_chars))
    obfuscated = "".join(result)
    return {"obfuscated": obfuscated, "junk_chars_used": junk_chars}


def junk_strip(obfuscated: str, junk_chars: str = "!@#$%^&*~`") -> str:
    """Remove all junk characters from an obfuscated string."""
    return "".join(ch for ch in obfuscated if ch not in junk_chars)


# ─────────────────────────────────────────────
# 2. Character splitting / concatenation
# ─────────────────────────────────────────────

def char_split(payload: str) -> dict:
    """
    Split payload into individual characters represented as a Python
    string-concatenation expression.
    
    Example: 'cmd' → '"c"+"m"+"d"'
    """
    split_repr = "+".join(f'"{ch}"' for ch in payload)
    return {
        "obfuscated": split_repr,
        "note": "Reconstruct with: eval(obfuscated) or ''.join(parts)"
    }


def char_split_decode(split_repr: str) -> str:
    """
    Reconstruct original string from char-split representation.
    Extracts characters between quotes.
    """
    parts = split_repr.split("+")
    return "".join(p.strip('"') for p in parts)


# ─────────────────────────────────────────────
# 3. Reversal
# ─────────────────────────────────────────────

def reverse_payload(payload: str) -> dict:
    """Reverse the payload string."""
    return {"obfuscated": payload[::-1], "note": "Restore by reversing again."}


def reverse_decode(reversed_str: str) -> str:
    """Recover the original string by reversing the reversed payload."""
    return reversed_str[::-1]


# ─────────────────────────────────────────────
# 4. Escape-sequence / Unicode obfuscation
# ─────────────────────────────────────────────

def escape_obfuscate(payload: str) -> dict:
    """
    Encode each character as its Unicode escape sequence.
    Example: 'A' → '\\u0041'
    """
    obfuscated = "".join(f"\\u{ord(c):04x}" for c in payload)
    return {
        "obfuscated": obfuscated,
        "note": "Decode with escape_decode() or Python's encode/decode methods."
    }


def escape_decode(escaped: str) -> str:
    """Decode a Unicode-escaped string back to the original payload."""
    try:
        return escaped.encode("utf-8").decode("unicode_escape")
    except Exception as e:
        return f"[ERROR] Escape decode failed: {e}"


# ─────────────────────────────────────────────
# 5. Case alternation
# ─────────────────────────────────────────────

def case_alternate(payload: str) -> dict:
    """
    Alternate upper/lower case for each character.
    Example: 'whoami' → 'WhOaMi'
    """
    result = []
    upper_next = True
    for ch in payload:
        if ch.isalpha():
            result.append(ch.upper() if upper_next else ch.lower())
            upper_next = not upper_next
        else:
            result.append(ch)
    return {
        "obfuscated": "".join(result),
        "note": "Use .lower() on decoded string to restore normalized form."
    }


# ─────────────────────────────────────────────
# 6. Null-byte / hex interleaving
# ─────────────────────────────────────────────

def hex_interleave(payload: str, delimiter: str = "\\x00") -> dict:
    """
    Represent each character as its hex value interleaved with a delimiter.
    Example: 'AB' → '\\x41\\x00\\x42\\x00'
    """
    parts = [f"\\x{ord(c):02x}" for c in payload]
    obfuscated = delimiter.join(parts)
    return {
        "obfuscated": obfuscated,
        "delimiter": delimiter,
        "note": "Strip delimiter and convert hex values to reconstruct."
    }


def hex_interleave_decode(obfuscated: str, delimiter: str = "\\x00") -> str:
    """Decode a hex-interleaved string back to plaintext."""
    try:
        parts = obfuscated.split(delimiter)
        return "".join(chr(int(h, 16)) for h in parts if h)
    except Exception as e:
        return f"[ERROR] Hex-interleave decode failed: {e}"


# ─────────────────────────────────────────────
# Bulk: apply all techniques at once
# ─────────────────────────────────────────────

def apply_all_techniques(payload: str, xor_junk_density: int = 2) -> dict:
    """
    Run every obfuscation technique on the payload and return a summary dict.
    """
    return {
        "junk_insert":      junk_insert(payload, density=xor_junk_density),
        "char_split":       char_split(payload),
        "reversal":         reverse_payload(payload),
        "escape_unicode":   escape_obfuscate(payload),
        "case_alternation": case_alternate(payload),
        "hex_interleave":   hex_interleave(payload),
    }
