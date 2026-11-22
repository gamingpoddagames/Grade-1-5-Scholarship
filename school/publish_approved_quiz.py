#!/usr/bin/env python3
"""Publish an approved, original Sinhala quiz image to the authorized Page."""
import os
from pathlib import Path
from facebook_card import create_card, publish
from blogger_link_safety import FACEBOOK_LANDING_URL

QUESTION = {
    "grade": 5,
    "topic": "සාමාන්‍ය දැනුම",
    "q": "ලෝකයේ විශාලතම සාගරය කුමක්ද?",
    "choices": ["අත්ලාන්තික් සාගරය", "පැසිෆික් සාගරය", "ඉන්දියානු සාගරය", "ආක්ටික් සාගරය"],
    "answer": 1,
    "explanation": "ලෝකයේ විශාලතම සාගරය පැසිෆික් සාගරයයි."
}
CAPTION = (
    "පුංචි නැණ මඟ | අද දැනුම පරීක්ෂාව!\n\n"
    "ලෝකයේ විශාලතම සාගරය කුමක්ද?\n\n"
    "A) අත්ලාන්තික් සාගරය\n"
    "B) පැසිෆික් සාගරය\n"
    "C) ඉන්දියානු සාගරය\n"
    "D) ආක්ටික් සාගරය\n\n"
    "ඔබේ පිළිතුර A, B, C හෝ D ලෙස Comment කරන්න.\n\n"
    f"තවත් නොමිලේ අධ්‍යාපනික ප්‍රශ්න: {FACEBOOK_LANDING_URL}\n"
    "#PunchiNenaMaga #SinhalaQuiz"
)
if __name__ == "__main__":
    output=Path("school/output/approved-ocean-quiz.png")
    create_card(QUESTION, output)
    if not os.getenv("FB_PAGE_ID") or not os.getenv("FB_PAGE_ACCESS_TOKEN"):
        raise RuntimeError("Facebook Page credentials unavailable: quiz generated but NOT published")
    publish(output, CAPTION)
