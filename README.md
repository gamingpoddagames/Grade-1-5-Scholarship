# පුංචි නැණ මඟ | Grade 1–5 & Scholarship

**Website:** https://gamingpoddagames.github.io/Grade-1-5-Scholarship/
**Repository:** https://github.com/gamingpoddagames/Grade-1-5-Scholarship

## Working features
- Grade 1–5 Sinhala practice pages, answer reveals and interactive Grade 5 quiz
- 10 printable/downloadable PDF files: one practice paper and one separate answer key for each grade
- Dedicated SEO-friendly grade pages and sitemap
- Deterministic original question generation using Python rules, without an AI API
- Daily Sinhala **branded image-card** publishing at 08:47 Asia/Colombo via GitHub Actions (when valid Page token is set). Card text uses Pillow RAQM and Noto Sinhala to avoid desktop Facebook font shaping problems.
- Grade 5 Sinhala quiz MP4 generated daily with Unicode text and original narration from the MIT-licensed UNICEF Piper Sinhala TTS model (Pillow RAQM + Noto Sinhala).
- Sinhala narrated quiz video uploading via the Meta Page Video API is scheduled at 09:35 Asia/Colombo, after the question card. Verified one-off upload returned video ID `1506927227970103`. Silent videos remain as a local backup only.
- A voiced, playable/downloadable quiz video is included on the website; the silent version remains as a fallback if the free TTS download fails.\n- Site logo, favicon, cover/banner and Facebook social preview are generated from original school branding code without paid AI APIs.\n- Facebook Page logo and cover image uploads were confirmed via API, but Meta rejected the direct profile/cover appearance update with HTTP 400; these settings require manual Page-level permissions or UI action.

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
- Further curriculum-specific question review, diversity and voice pronunciation QA
- Automated analytics/Search Console reporting
- AdSense after website quality and policy review
