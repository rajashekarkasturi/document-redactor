# core/redaction_config.py
import re

"""
This module defines the configuration for PII (Personally Identifiable Information)
redaction. It contains regular expression patterns for common sensitive data types.
The patterns are compiled for efficiency.
"""

# Dictionary of PII types and their corresponding regex patterns
PII_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE_NUMBER": re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # Example for financial data (e.g., simple credit card numbers)
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b")
}

# Configuration for redaction appearance
REDACTION_CONFIG = {
    "placeholder_text": "[REDACTED]",
    "fill_color": (0.0, 0.0, 0.0),  # Black
}