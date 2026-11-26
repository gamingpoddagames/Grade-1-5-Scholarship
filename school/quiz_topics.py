#!/usr/bin/env python3
"""Reviewed Sinhala general-knowledge quizzes for screenshot-style reels."""
import datetime as dt
import random

QUIZZES = [
    ("රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද?",
     ["සිකුරු", "බ්‍රහස්පති", "අඟහරු", "සෙනසුරු"], 2, "අභ්‍යවකාශය"),
    ("ලෝකයේ විශාලතම සාගරය කුමක්ද?",
     ["අත්ලාන්තික් සාගරය", "පැසිෆික් සාගරය", "ඉන්දියානු සාගරය", "ආක්ටික් සාගරය"], 1, "පෘථිවිය"),
    ("පෘථිවියේ ස්වාභාවික උපග්‍රහයා කුමක්ද?",
     ["සූර්යයා", "චන්ද්‍රයා", "සිකුරු", "අඟහරු"], 1, "අභ්‍යවකාශය"),
    ("සෞරග්‍රහ මණ්ඩලයේ විශාලතම ග්‍රහලෝකය කුමක්ද?",
     ["පෘථිවිය", "බ්‍රහස්පති", "සෙනසුරු", "බුධ"], 1, "අභ්‍යවකාශය"),
    ("වළලු සඳහා ප්‍රසිද්ධ ග්‍රහලෝකය කුමක්ද?",
     ["අඟහරු", "පෘථිවිය", "සිකුරු", "සෙනසුරු"], 3, "අභ්‍යවකාශය"),
    ("ලෝකයේ විශාලතම සත්වයා කුමක්ද?",
     ["අලියා", "නිල් තල්මසා", "ජිරාෆ්", "හිපපොටේමස්"], 1, "සත්ව ලෝකය"),
    ("කෘමීන්ට සාමාන්‍යයෙන් පාද කීයක් තිබේද?",
     ["හතරක්", "පහක්", "හයක්", "අටක්"], 2, "සත්ව ලෝකය"),
    ("පෘථිවියට ආලෝකය හා තාපය සපයන තාරකාව කුමක්ද?",
     ["චන්ද්‍රයා", "සූර්යයා", "අඟහරු", "සෙනසුරු"], 1, "විද්‍යාව"),
    ("ශාක බොහොමයක් ආහාර නිපදවන්නේ ප්‍රධාන වශයෙන් කුමන කොටසෙහිද?",
     ["මුල්වල", "පත්‍රවල", "මල්වල", "බීජවල"], 1, "විද්‍යාව"),
    ("සතියකට දින කීයක් තිබේද?",
     ["පහක්", "හයක්", "හතක්", "අටක්"], 2, "සාමාන්‍ය දැනුම"),
    ("ලෝකයේ උසම කඳු මුදුන කුමක්ද?",
     ["කේ ටූ", "කන්චන්ජංගා", "එවරස්ට්", "ෆුජි"], 2, "භූගෝල විද්‍යාව"),
    ("ජලය හිමාංකයට පත් වන්නේ සෙල්සියස් අංශක කීයකදීද?",
     ["බින්දුව", "දහය", "පනහ", "සියය"], 0, "විද්‍යාව"),
]

def select(day, offset=0):
    """Four different reels/day, with no recycled static questions for at least a month.

    After the reviewed and existing school bank is exhausted, generate
    fresh arithmetic questions with computed, verified answers.
    """
    if isinstance(day, str):
        day = dt.date.fromisoformat(day)
    if not 0 <= offset < 4:
        raise ValueError("Only reel offsets 0..3 are supported")
    index = (day - dt.date(2026, 11, 22)).days * 4 + 7 + offset
    if index < 0:
        raise ValueError("Quiz date is before the generation start")
    if index < len(QUIZZES):
        question, choices, answer, topic = QUIZZES[index]
        return {
            "grade": 5, "topic": topic, "q": question,
            "choices": list(choices), "answer": answer,
            "explanation": "නිවැරදි පිළිතුර: " + choices[answer] + "."
        }

    # The existing education question bank is reused without repeating prompts.
    from build_resources import all_questions
    seen = {q for q, _, _, _ in QUIZZES}
    bank = []
    for item in all_questions():
        if item["q"] not in seen and len(item["choices"]) == 4:
            seen.add(item["q"])
            bank.append(item)
    # Interleave distinct topics rather than exhausting a single subject at once.
    buckets = {}
    for item in bank:
        buckets.setdefault(item.get('topic', 'සාමාන්‍ය දැනුම'), []).append(item)
    bank = []
    while any(buckets.values()):
        for items in buckets.values():
            if items:
                bank.append(items.pop(0))
    remaining = index - len(QUIZZES)
    if remaining < len(bank):
        return dict(bank[remaining])

    # Keep each date/offset reproducible across platforms and retries.
    serial = remaining - len(bank)
    rng = random.Random(serial)
    number = 45 + serial
    step = rng.randint(3, 12)
    kind = rng.randrange(5)

    if kind == 0:
        question = f"{number} + {step} = කීයද?"
        result = number + step
    elif kind == 1:
        question = f"{number} − {step} = කීයද?"
        result = number - step
    elif kind == 2:
        question = f"{number} × {step} = කීයද?"
        result = number * step
    elif kind == 3:
        question = f"{number} බැගින් ඇති කණ්ඩායම් {step}ක එකතුව කීයද?"
        result = number * step
    else:
        question = f"{number}, {number + step}, {number + 2 * step}, ... ඊළඟ සංඛ්‍යාව කුමක්ද?"
        result = number + 3 * step

    options = [result, result + 2, result + 5, result - 3]
    rng.shuffle(options)
    return {
        "grade": 5, "topic": "ශිෂ්‍යත්ව ගණිතය",
        "q": question,
        "choices": [str(n) for n in options],
        "answer": options.index(result),
        "explanation": f"නිවැරදි පිළිතුර {result}යි."
    }
