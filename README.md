# පුංචි නැණ මඟ | Grade 1–5 & Scholarship

**Website:** https://punchinanamaga.blogspot.com/
**PDF/quiz resource hosting:** https://gamingpoddagames.github.io/Grade-1-5-Scholarship/
**Repository:** https://github.com/gamingpoddagames/Grade-1-5-Scholarship

## Working features
- Grade 1–5 Sinhala practice pages, answer reveals and interactive Grade 5 quiz
- 10 printable/downloadable PDF files: one practice paper and one separate answer key for each grade
- Dedicated SEO-friendly grade pages and sitemap
- Deterministic original question generation using Python rules, without an AI API
- Daily Sinhala **branded image-card** publishing at 08:47 Asia/Colombo via GitHub Actions (when valid Page token is set). Card text uses Pillow RAQM and Noto Sinhala to avoid desktop Facebook font shaping problems.
- Grade 5 Sinhala quiz MP4s use a screenshot-style navy-card renderer with Noto Sinhala/RAQM text and gTTS narration; a separate website stage may additionally add Piper voice.
- Daily screenshot-style Facebook Reel is scheduled at 11:45 Asia/Colombo; three additional Reels at 10:30 (conditional publication). A previous one-off upload returned video ID `1506927227970103`.
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

## Blogger monetization
The verified existing Adsterra Social Bar is an optional footer gadget on Blogger. Facebook lesson links stay on the owned Blogger domain and are validated before publishing. See [the installation and rollback notes](school/ADSTERra_SETUP.md). Ad creatives and earnings are not established by script loading alone.

## Visual-first picture quiz (22 November 2026)
The Facebook image card and original Sinhala quiz Reel now share a single daily, curated photograph and the same grade-5 question, selected by Asia/Colombo date. Nature, wildlife, ocean life, space and Sri Lankan heritage are the primary visual niches. Eight vetted images and two question variants per image provide 16 distinct daily questions before repeating; the previous one-off ocean question script now selects the current picture question. Photos are credited in the artwork and captions; source links and licences are documented in [the visual quiz image rights file](school/VISUAL_QUIZ_IMAGE_RIGHTS.md). Missing images block publishing, rather than allowing irrelevant photos. The original Grade 1–5 mathematics/PDF resources are unchanged.

Run `python -m unittest discover -s school -p 'test_visual_quiz.py' -v` for the offline question bank. A live GitHub Action run is still needed to confirm Wikimedia downloads, rendered cards and actual Facebook publishing.


## Facebook and Blogger paired publishing (22 November 2026)

The current quiz publisher uses `school/crosspost.py` to pair all active Facebook quiz publishing routes with the authorized Blogger site.

- Daily image card and manually approved image card: create the matching Blogger article first, then publish the Facebook photo with the **exact returned Blogger article URL**.
- Daily narrated Reel and three additional Reels: publish corresponding Blogger articles first, post Facebook videos containing the matching article URLs, then embed the verified Facebook video URL in Blogger.
- Stand-alone daily text quiz publishing uses the same Blogger-first procedure.
- Each Blogger article contains the full question, A-D options, explanation, and an appropriately credited curated Commons photo if one exists.

Only a verified Meta public permalink is embedded via the Facebook video or post widget. Blogger does not physically host the generated MP4. If a public permalink is unavailable, the Blogger article still contains the matching quiz but has no video embed until the link becomes available.

To avoid accidental reposts, Blogger stores a READY/PENDING/PUBLISHED state marker. An uncertain Facebook send stays PENDING for manual reconciliation, rather than being retried blindly. Preexisting Blogger articles without a managed marker are not overwritten. The Facebook caption always links directly to the owned Blogger article, never an intermediary redirect.

Required Actions secrets: BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN, FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN. Set BLOGGER_ALLOW_PUBLICATION=false to explicitly opt out of paired publishing; missing credentials or an explicit opt-out prevents unmatched Facebook-only quiz posts.

Offline regression tests: `python -m unittest discover -s school -p test_crosspost.py -v`.

The older picture-first image workflow remains separate from the new screenshot-style narrated Reel bank. A code commit or Actions trigger does not confirm a Facebook or Blogger post; examine actual run logs and the destination pages.

## Colourful Grade 5 scholarship logic puzzle photo posts (23 November 2026)

A separate daily **18:30 Asia/Colombo** GitHub Actions workflow now generates an original vivid Sinhala number-wheel infographic, three computed answer choices, and a friendly guess-in-comments caption. The photo deliberately hides the answer; the matching Blogger article offers a collapsible solution, the arithmetic steps, and extra teaching notes. Facebook links directly to that exact Blogger article via the existing duplicate-aware Blogger-first publisher. The generator and its tests are in `school/puzzle_posts.py` and `school/test_puzzle_posts.py`; workflow: `.github/workflows/daily-scholarship-puzzle.yml`. See [Puzzle posts guide](school/PUZZLE_POSTS_GUIDE.md). A workflow commit is not evidence of successful public posting; inspect GitHub Actions logs and the two destination sites.


## Sinhala Facebook web/mobile text and visual-source clean-up (23 November 2026)

The publishing flow now uses `school/social_text.py` to normalize UTF-8/NFC, strip accidental copy/paste invisibles, keep essential Sinhala joiners, and replace confusing ` | ` title separators with readable lines. All active photo, quiz, puzzle, standalone text, Blogger crosspost, and video upload paths apply that sanitization. `school/test_social_text.py` runs before automated publishing in the five corresponding Actions workflows. Images continue to use Noto Sinhala with Pillow RAQM, so essential heading text is already part of the graphic independent of Facebook's chosen UI font.

For curated Wikimedia photographs, the small artist/source footer on **Facebook image cards** is replaced by an original Punchi Nena Maga graphic label; the **actual copyright credit and licence** remain in the same Facebook post's caption and matching Blogger article. Embedded source watermarks in third-party images are never erased or concealed. The screenshot-style Quiz Reels and original logic-puzzle graphics use their own illustrations, not third-party downloaded video footage. Facebook desktop's browser-controlled Sinhala typeface cannot be forced by repository code; shortening and normalizing captions improves consistency but does not guarantee identical glyph rendering on every browser.

Legacy Blogger title matching remains in `school/crosspost.py` to avoid duplicate publishing on the day of the format change. A successful source commit does not prove a completed upload. Inspect the scheduled Actions tests and the resulting post on desktop and mobile before treating this as fully verified.

## Fresh Sinhala scholarship puzzle styles (23 Nov 2026)

The logic-puzzle system now alternates **six distinct original question and image types**: ascending number sequences, magic-square number grids, circle/square balance equations, dot-array picture patterns, analogue-clock puzzles and additive number pyramids. These are actual different mathematical tasks and different original illustrations, not number-wheel questions with fresh numbers. The on-demand post for 23 Nov 2026 uses dot-array artwork; the normal series starts 24 Nov 2026 and rotates daily without using the same visual format on consecutive days. Bonus and on-demand posts use different types from the scheduled post.

Python files: `school/diverse_puzzles.py`, `school/puzzle_posts.py`, and `school/test_puzzle_posts.py`. The matching Blogger post includes a readable representation of the same diagram and a worked solution; Facebook asks the audience to guess first and links directly to Blogger. Old confirmed posts and their answers are retained. Every generated answer is checked by test calculations; the updated workflow runs these tests before any live publishing attempt. Code push and workflow trigger do not alone establish a successful Facebook or Blogger upload.


## Educational comment prompts and Adsterra link safety (23 Nov 2026)

- All paired Facebook image, Reel and text quiz captions automatically receive an educational, format-specific **"explain your answer"** discussion prompt from `school/engagement_monetization.py`. Prompts ask for arithmetic reasoning instead of promising a reward or demanding comments to unlock the answer. The real matching Blogger article URL remains direct and unmodified.
- Adsterra ad scripts and Adsterra SmartLink/Direct Link **are different**. The supplied `bicea.org` JavaScript source is not an HTTP destination for quiz readers and must not be pasted into Facebook captions or used as an answer-page redirect.
- The HTML article renderer has an **opt-in separate Sponsor/Advertisement area** after the lesson. It is intentionally OFF by default because this is a child-facing education site with an AdSense review pending. Enabling needs both explicit suitability review and a real HTTPS Direct Link; an invalid script URL fails closed.
- Controlled settings for future *new* Blogger-first posts: GitHub Actions variable `ADSTERRA_SPONSORED_LINK_ENABLED=true`, GitHub Actions variable `ADSTERRA_AGE_APPROPRIATE_REVIEWED=true`, and secret `ADSTERRA_DIRECT_LINK` containing the actual verified direct link (not the ad script). The second toggle must not be set before carefully checking advertiser categories, privacy consent and age suitability.
- **No automatic redirects, hidden intermediary ads, ad-gated answers, pop-unders, or mislabeled sponsored links**. In particular the Facebook post's educational Blogger link always opens Blogger. The separate optional link is clearly labeled sponsored, does not stand between visitors and the solution, and never appears in the Facebook caption.
- The five publishing workflows now run `school/test_engagement_monetization.py` along with prior Unicode and duplicate-safety checks. Existing published Blogger posts are not rewritten. No Facebook or Blogger publish is confirmed merely by these commits.


## YouTube channel integration — owner-supplied ID (24 November 2026)

- **Official target:** https://www.youtube.com/channel/UCQ2EM8DjUfg3WgzB8r6hYDQ
- Owner-provided permanent ID: `UCQ2EM8DjUfg3WgzB8r6hYDQ`. The uploader blocks OAuth sessions aimed at any other channel ID.
- New original **Sinhala YouTube Short** uploader: `school/youtube_shorts.py`. It reuses the reviewed A–D question, voice, answer reveal and 1080×1920 MP4 from the existing school project, plus Education category metadata and the owned Blogger link.
- New GitHub Actions workflow: `.github/workflows/youtube-shorts.yml`. Scheduled at **12:45 Asia/Colombo** with MP4 preview artifacts; no upload unless Google OAuth and an explicit authorization flag are configured.
- Safety: Videos directed at primary-school children are marked `selfDeclaredMadeForKids=true`. Default is **private**. Google account owner must authorize upload and channel read scopes; no token or personal login is stored in source files. Duplicates and wrong-channel uploads are blocked.
- End-user instructions and Google Cloud OAuth security steps: [YouTube channel setup](school/YOUTUBE_CHANNEL_SETUP.md).
- Offline tests: `python -m unittest discover -s school -p test_youtube_shorts.py -v`.
- Project commits and GitHub Actions previews are not proof that a YouTube video was uploaded or that the owner installed the profile/banner images; verify a confirmed video receipt and the exact destination in YouTube Studio before claiming this is live.
