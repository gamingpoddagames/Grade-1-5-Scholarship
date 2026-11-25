"""Expand printed Sinhala currency abbreviations for narration."""
import re

def expand_currency(text):
    return re.sub(r"(?<!\w)රු\s*\.\s*(?=\d)", "රුපියල් ", str(text))
