# පුංචි නැණ මඟ | Grade 1–5 & Scholarship

**Website:** https://gamingpoddagames.github.io/Grade-1-5-Scholarship/
**Repository:** https://github.com/gamingpoddagames/Grade-1-5-Scholarship

## Working features
- Grade 1–5 Sinhala practice pages, answer reveals and interactive Grade 5 quiz
- 10 printable/downloadable PDF files: one practice paper and one separate answer key for each grade
- Dedicated SEO-friendly grade pages and sitemap
- Deterministic original question generation using Python rules, without an AI API
- Daily Sinhala Facebook text publishing at 08:47 Asia/Colombo via GitHub Actions (when valid Page token is set)
- Daily Grade 5 quiz-video MP4 renderer added; see the Actions artifact after the video job completes. The video is silent and is **not** automatically published to Facebook yet.

## Links
- PDFs: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/downloads/grade-5-paper.pdf
- Answers: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/downloads/grade-5-answers.pdf
- Grade 5 topic page: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/grade-5/
- Daily workflow: .github/workflows/school-daily.yml
- Website workflow: .github/workflows/pages.yml

## Secrets
Set `FB_PAGE_ID` = `61596326146776`, and a valid `FB_PAGE_ACCESS_TOKEN`, in **this repository's** Actions secrets. Do not commit your token or paste it publicly.

Manual runs default to publish=false. Scheduled runs publish only if both secrets exist.
A successful workflow run alone is not proof of Facebook publishing; verify `Facebook post published:` in the logs.

## Content integrity
The arithmetic question sets are auto-generated and reviewed by deterministic answer computation. Sinhala spelling and grade-level suitability still need editorial review. These are independent practice materials, not official government exam papers.

## Growth and ads
Use original educational content and useful teacher/parent explanations to earn organic traffic. Submit `sitemap.xml` to Google Search Console. AdSense approval and revenue are not guaranteed. Children-targeted advertising requires extra privacy care and compliance.

## Pending enhancements
- Better curriculum coverage and professionally reviewed scholarship papers
- Sinhala narration and automated video publishing
- Automated analytics/Search Console reporting
- AdSense after website quality and policy review
