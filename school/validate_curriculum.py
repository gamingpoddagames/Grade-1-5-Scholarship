#!/usr/bin/env python3
"""Quality gates for generated primary materials; standard-library only."""
import argparse
from collections import Counter
from pathlib import Path
from curriculum_bank import get_questions,SUBJECTS
from curriculum_pages import verify

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--site-dir")
    args=p.parse_args()
    items=get_questions()
    stats=verify(items)
    assert len(items)==180,(len(items),stats)
    for grade in range(1,6):
        assert stats[(grade,"math")]==20
        assert stats[(grade,"sinhala")]==8
        assert stats[(grade,"environment")]==8
        for subject in SUBJECTS:
            choices=[q for q in items if q["grade"]==grade and q["subject"]==subject]
            assert all(q["choices"][q["answer"]] not in [v for i,v in enumerate(q["choices"]) if i!=q["answer"]] for q in choices)
    if args.site_dir:
        folder=Path(args.site_dir)
        for grade in range(1,6):
            for subject in SUBJECTS:
                stem=f"grade-{grade}-{subject}"
                for suffix in ("paper","answers"):
                    pdf=folder/"downloads"/f"{stem}-{suffix}.pdf"
                    assert pdf.exists(),pdf
                    with open(pdf,"rb") as f:
                        assert f.read(4)==b"%PDF",pdf
                    assert pdf.stat().st_size>1500,pdf
                page=folder/"practice"/f"grade-{grade}"/subject/"index.html"
                assert page.exists(),page
                text=page.read_text(encoding="utf-8")
                assert "window.PRACTICE_QUESTIONS" in text
                assert "පිළිතුර පරීක්ෂා කරන්න" in text
                assert f"{stem}-answers.pdf" in text
    print("PASS: 180 independent exercises across 15 grade+subject sets; answer choices, 30 PDFs and 15 quizzes verified.")

if __name__=="__main__":main()
