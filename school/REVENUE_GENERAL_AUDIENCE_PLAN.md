# Punchi Nena Maga: General Audience + Sustainable Revenue

Status verified 2026-11-24. **The channel name alone never determines a "Made for Kids" label.**

## What we actually verified
- **YouTube channel**: `UCQ2EM8DjUfg3WgzB8r6hYDQ`.
- Read-only YouTube OAuth audit [run 45416963142](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45416963142) found:
  - Channel-level `status.selfDeclaredMadeForKids = false` and `status.madeForKids = false`.
  - Original four primary-school quiz videos (IDs `3m3lRvYFS9A`, `fWKUmHpr74E`, `aLKKLApwkeA`, `fDnsXHmhlg4`) were **individually** set `Made for Kids = true`.
  - No channel or video settings were changed by this read-only check.
- Google/YouTube's designation depends on actual intended content and child-directed factors, not whether adults happen to watch or what the channel is named. Other general-audience videos can use `selfDeclaredMadeForKids=false` when this is genuinely accurate.
- To handle mixed content, YouTube Studio > Settings > Channel > Advanced settings > Audience > **review this setting for every video**. Do not blanket-mark child-directed primary-school content as not for kids just to obtain ads.
- YouTube's `Made for Kids` flag does **not** mean adults are forbidden to watch. Contextual ads may still appear, but personalized ads and some platform features are unavailable.

Google references:
https://support.google.com/youtube/answer/9528076
https://support.google.com/youtube/answer/9527654

## Separate adult-oriented creator content

Added `school/adult_general_quiz.py` and the independent GitHub workflow
`.github/workflows/adult-general-learning.yml`. It does not modify the prior
Facebook voice/video process for original Grade 1–5 questions.

- **Target viewers**: parents, teachers, working adults, small business owners.
- **Educational topics**: household budgeting, everyday discounts, margin/profit
  arithmetic, adult practical saving calculations. All multiple-choice answers
  are checked with formula-derived values. Adult titles and screens do **not**
  use elementary-school grade banners.
- **True general-audience metadata** on this independent series only:
  `selfDeclaredMadeForKids=false`. **No global MFK toggle or mass-relabelling.**
- Tuesday, Thursday, Saturday at **20:45 Sri Lanka time**:
  source-specific video, matched Blogger article and Facebook Page post when
  authorized, verified-channel private YouTube Short while public publication
  review is disabled.
- Default Github source-push triggers are **preview only**.
- This is a new editorial stream and does not alter any existing FB video.

Example original adult topic (24 Nov): monthly income LKR 68,000 less monthly
expenses LKR 49,500 = **LKR 18,500 left**. All four options checked. Private
preview QA: [run 45416241143](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45416241143).

## Practical, real monetization plan

1. **Blogger website**: Our current verified Adsterra account has an approved
   `punchinanamaga.blogspot.com` website and existing optional Social Bar
   unit. Keep educational answers free; route relevant adults to *the actual
   original Blogger article*, not an ad redirect. Show clearly labeled,
   reviewed advertising only. See `ADSTERra_SETUP.md`.
2. **Organic traffic**: Publish genuinely useful original content adults search
   for (household budgets, price comparisons, vocational math, parent teaching
   techniques), with correct Sinhala, topic images, substantive answer and
   descriptive Blogger link. Avoid high-volume nearly-identical Shorts that
   could trigger spam or repetitious-content issues.
3. **YouTube monetization**: Sri Lanka is eligible for the standard YouTube
   Partner Program. Ad revenue eligibility normally requires 1,000 subscribers
   plus 4,000 qualified *public* long-form watch hours in 12 months or
   10 million qualified *public* Shorts views in 90 days. It does **not**
   follow from Adsterra status alone. Private videos do not count.
   The current owner config is `YOUTUBE_PRIVACY=private`, so public release
   after video review is a separate necessary step for YouTube discoverability.
4. **Measure**: Adsterra `Statistics` for this approved Blogger property
   (impressions, clicks, earnings), Blogger referral traffic, Facebook reach,
   YouTube Studio `Analytics/Earn` and subscriber growth.
   Without those numbers, do not claim actual ad income.
5. **Do not** use arbitrary SmartLinks, automatic popunders, redirect tricks,
   click incentives, code obfuscation, adult advertising in child-directed
   lessons, or automatic ad-refresh loops. They create compliance and user
   safety problems, jeopardize the project, and do not guarantee money.
6. **OAuth longevity**: the project's External/Testing Google OAuth refresh
   token may expire after seven days for YouTube scopes; review publishing
   status and any required verification to make scheduled uploading durable.

Official references:
- https://support.google.com/youtube/answer/7101720
- https://support.google.com/youtube/answer/72851
- https://support.google.com/youtube/answer/9528076
- https://support.google.com/adsense/answer/1269077

No earnings, guaranteed reach or guaranteed YouTube approval are claimed.
