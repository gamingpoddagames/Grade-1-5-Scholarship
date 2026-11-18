# පුංචි නැණ මඟ | Grade 1–5 & Scholarship

Official project repository: https://github.com/gamingpoddagames/Grade-1-5-Scholarship

**Site (after Pages setup):** https://gamingpoddagames.github.io/Grade-1-5-Scholarship/

## Features
- Sinhala Grade 1–5 practice questions and answer sheets
- Grade 5 scholarship-style online quiz
- Print/Save as PDF with browser print dialog
- Deterministic, no-AI daily Facebook question post generator with printable worksheet output
- No paid AI API, no student data collection, no advertisements enabled

## Set up hosting
Settings → Pages → Source: GitHub Actions.
Actions → Publish Scholarship Website → Run workflow.
Check the run before treating the website as live.

## Enable Facebook daily publishing
In **THIS repository**, create GitHub Actions secrets:
- `FB_PAGE_ID` = `61596326146776`
- `FB_PAGE_ACCESS_TOKEN` = your valid Meta Page access token

**Secrets from other repositories do not automatically transfer.**
After configuring them, Actions → School Daily Content (No AI) → Run workflow (publish=true).
A successful Graph API response returns a Facebook post ID in GitHub Actions logs.

The workflow has 14 demo questions, rotating daily. Daily output is available as a workflow artifact.
It does not create new questions without adding validated questions to the bank.
Video production and automatic PDF hosting are not implemented yet.

## Notes
- All material is independent practice, not official past examination papers.
- Only original or licensed resources should be published.
- Review Meta publishing permissions and child-directed advertising policies before monetization.
