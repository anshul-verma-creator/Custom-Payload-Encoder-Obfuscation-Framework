"""
evasion_tester.py
-----------------
Evasion Testing Module

Simulates a basic static-analysis / signature-based detection engine.
The "detector" maintains a list of known malicious signatures (keywords,
patterns) and checks whether a given payload triggers any of them.

This module:
  - Defines a default signature database
  - Accepts custom signatures
  - Tests original vs. encoded/obfuscated payloads
  - Returns structured detection results for reporting
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────────────────────────────
# Default Signature Database
# ─────────────────────────────────────────────

DEFAULT_SIGNATURES: List[str] = [
    # Shell commands / recon
    "whoami",
    "net user",
    "net localgroup",
    "ipconfig",
    "ifconfig",
    "nmap",
    "netstat",
    "tasklist",
    "ps -aux",
    # Download / execution cradles
    "powershell",
    "cmd.exe",
    "wget",
    "curl",
    "Invoke-Expression",
    "IEX",
    "DownloadString",
    "DownloadFile",
    # Web shells / common payloads
    "eval(",
    "exec(",
    "system(",
    "passthru(",
    "shell_exec(",
    "base64_decode",
    # Reverse-shell indicators
    "/bin/sh",
    "/bin/bash",
    "bash -i",
    "nc -e",
    "ncat",
    # Scripting / injection markers
    "<script>",
    "alert(",
    "document.cookie",
    "SELECT * FROM",
    "UNION SELECT",
    "DROP TABLE",
    "OR 1=1",
    # Malware-family keywords
    "mimikatz",
    "meterpreter",
    "metasploit",
    "cobalt strike",
    "empire",
]


# ─────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────

@dataclass
class DetectionResult:
    payload_label: str
    payload_preview: str          # First 80 chars
    detected: bool
    matched_signatures: List[str] = field(default_factory=list)
    total_checked: int = 0

    @property
    def status(self) -> str:
        return "[DETECTED]" if self.detected else "[BYPASSED]"


@dataclass
class EvasionReport:
    original: DetectionResult
    variants: List[DetectionResult] = field(default_factory=list)

    @property
    def bypass_rate(self) -> float:
        """Percentage of variants that successfully bypassed detection."""
        if not self.variants:
            return 0.0
        bypassed = sum(1 for v in self.variants if not v.detected)
        return round((bypassed / len(self.variants)) * 100, 1)

    @property
    def detection_rate(self) -> float:
        return round(100.0 - self.bypass_rate, 1)


# ─────────────────────────────────────────────
# Detection Engine
# ─────────────────────────────────────────────

class SignatureDetector:
    """
    A simple keyword / regex signature-based detection engine.
    Case-insensitive by default.
    """

    def __init__(self, signatures: Optional[List[str]] = None, case_sensitive: bool = False):
        self.signatures = signatures if signatures is not None else list(DEFAULT_SIGNATURES)
        self.case_sensitive = case_sensitive

    def add_signature(self, sig: str) -> None:
        """Add a new signature to the detection database."""
        if sig not in self.signatures:
            self.signatures.append(sig)

    def remove_signature(self, sig: str) -> None:
        """Remove a signature from the detection database."""
        self.signatures = [s for s in self.signatures if s != sig]

    def scan(self, payload: str, label: str = "payload") -> DetectionResult:
        """
        Scan a single payload against all signatures.

        Returns
        -------
        DetectionResult with detection status and matched signatures.
        """
        matched = []
        text = payload if self.case_sensitive else payload.lower()

        for sig in self.signatures:
            needle = sig if self.case_sensitive else sig.lower()
            if needle in text:
                matched.append(sig)

        return DetectionResult(
            payload_label=label,
            payload_preview=payload[:80] + ("..." if len(payload) > 80 else ""),
            detected=bool(matched),
            matched_signatures=matched,
            total_checked=len(self.signatures),
        )

    def compare(
        self,
        original_payload: str,
        variants: dict,          # {label: encoded_or_obfuscated_string}
    ) -> EvasionReport:
        """
        Scan the original payload AND all variants.
        Returns a full EvasionReport.
        """
        original_result = self.scan(original_payload, label="Original")
        variant_results = []

        for label, payload in variants.items():
            result = self.scan(payload, label=label)
            variant_results.append(result)

        report = EvasionReport(original=original_result, variants=variant_results)
        return report


# ─────────────────────────────────────────────
# Convenience helpers
# ─────────────────────────────────────────────

def quick_scan(payload: str) -> DetectionResult:
    """Quickly scan a single payload against the default signature set."""
    detector = SignatureDetector()
    return detector.scan(payload, label="Quick Scan")


def format_detection_result(result: DetectionResult) -> str:
    """Return a human-readable string for a DetectionResult."""
    lines = [
        f"  Label   : {result.payload_label}",
        f"  Status  : {result.status}",
        f"  Preview : {result.payload_preview}",
        f"  Sigs    : {result.total_checked} checked",
    ]
    if result.matched_signatures:
        lines.append(f"  Matches : {', '.join(result.matched_signatures)}")
    return "\n".join(lines)
