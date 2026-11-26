"""Expand printed Sinhala currency abbreviations for narration."""
import re

def expand_currency(text):
    text = re.sub(r"(?<!\d)500\s*න්(?!\w)", "පන්සියයෙන්", str(text))
    text = re.sub(r"(?<!\d)500\s*කින්(?!\w)", "පන්සියයකින්", text)
    return re.sub(r"(?<!\w)රු\s*\.\s*(?=\d)", "රුපියල් ", str(text))
