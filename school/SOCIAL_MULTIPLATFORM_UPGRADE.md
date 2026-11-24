# Punchi Nena Maga — Multi-platform content upgrade (24 November 2026)

## What stays unchanged

The owner explicitly likes the current Facebook Sinhala video appearance and narration. **Do not modify** `school/daily_reel_quiz.py`, `school/quiz_reel_renderer.py`, `school/three_reels.py`, `school/visual_quiz.py`, or their Facebook publishing schedules to enable YouTube mirroring. The new programs import the same verified question selections and original render functions.

## New additive workflows

| Content | Owner Facebook/Blogger source | YouTube behavior | Automation |
|---|---|---|---|
| One existing daily original quiz | `quiz_topics.select(day, 0)` | existing 12:45 PM Sri Lanka Short | `youtube-shorts.yml` |
| Three original Sinhala Facebook + Blogger Reels | `three_reels.py`: `quiz_topics.select(day, 1..3)` + unchanged `build_resources.video` | distinct Shorts on same authorized channel; duplicate marker checks | `youtube-social-mirror.yml`, 16:15 SL time |
| Text quiz/poll-style post | `social_poll_pack.py`, validated four-choice original mathematics or general-knowledge question | same artwork and narrated Short; YouTube Community *draft* prepared for eligible channels | `social-poll-pack.yml`, 19:45 SL time; `youtube-poll-shorts.yml`, 22:00 SL time |
| Image poll-style post | licensed Wikimedia Commons photo + matching approved `visual_quiz` question | same photo artwork, separate answer-reveal Short; draft of Community poll | alternating with text poll |

The original `school-daily.yml` Facebook photo quiz and `daily-scholarship-puzzle.yml` remain independently scheduled and unchanged. These are additive **source-driven** mirrors, not direct account scrapers. A Blogger-only long-form post does not automatically become a YouTube video without separate editorial adaptation; existing older content is not retroactively uploaded.

### Quality and duplicates

- Question, four distinct choices, answer index, grade and matching Facebook/YouTube images checked.
- Noto Sinhala RAQM + DejaVu Latin fallback; no unsupported symbols, square-tofu characters or missing fonts.
- Facebook photo: 1080×1350. YouTube companion: 1080×1920, question/reveal, Sinhala narration, verified local MP4.
- Existing Facebook videos are not regenerated differently by these changes.
- Facebook/Blogger matching article ledger blocks repeat posts and uncertain retries.
- YouTube private uploader confirms authorized channel `UCQ2EM8DjUfg3WgzB8r6hYDQ`, scans prior markers/titles, and stops if quota/OAuth errors occur.
- Repository push triggers are always PREVIEW-ONLY. Scheduled runs require user-configured secrets and flags.
- **No guarantee** that an external TTS voice is linguistically flawless, every ad creative is child-appropriate, or every scheduled service will always be available. Inspect samples and failure logs.

### YouTube Community post limits

YouTube Studio can create text, image, poll and quiz posts if the channel/account is eligible. **The standard video-upload credentials and API code here do not auto-create native community poll or quiz posts**. YouTube's Posts API has limited access and does not currently support all native poll formats; these native posts may also be unavailable on a channel designated Made for Kids. The workflow instead creates a reviewable `youtube-community-draft.txt` and matching `.png`, and a video Short companion. Do not mislabel ordinary caption voting as a platform-counted poll.

Official references:
- https://developers.google.com/youtube/data/reference/rest/v3/posts
- https://support.google.com/youtube/answer/7124474
- https://support.google.com/youtube/answer/9527654

### Adsterra placement: keep educational content free

The approved **Adsterra website** is the *owned* Blogger property `https://punchinanamaga.blogspot.com/`, with the optional, opt-in `SocialBar_1` described in `ADSTERra_SETUP.md`. **Do not** use `https://bicea.org/14/3777aa5b8fbe2c3a7513a1e6dc0637c5` as a website URL: it is a vendor JavaScript loader, not a user destination. Do not insert scripts, popunders, click-through blockers or forced redirects into Facebook, YouTube, Telegram or TikTok posts.

- YouTube Shorts descriptions contain the direct Blogger learning link.
- Facebook quiz captions link directly to the actual corresponding Blogger educational article; the HTML answer is free without viewing ads.
- Blogger's separately labeled optional ad gadget remains opt-in for adults/parents and is **not** duplicated in each post.
- The independent `ADSTERRA_SPONSORED_LINK_ENABLED` and `ADSTERRA_AGE_APPROPRIATE_REVIEWED` safeguards remain in place; no unverified Direct Link or extra sponsored claims are added.
- Third-party ad network creatives cannot be guaranteed safe for children; review platform policies, privacy and adult ad restrictions before broadening monetization. No ad revenue is guaranteed.

### Authorization and cadence

The owner already completed Google OAuth and confirmed GitHub Secrets; [private GitHub YouTube test run 45409155504](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45409155504) succeeded. A successful test does not mean public YouTube uploads are approved. The owner configured `YOUTUBE_PRIVACY=private`, `YOUTUBE_UPLOAD_ENABLED=true`, `YOUTUBE_PUBLICATION_REVIEWED=false`; public publishing remains blocked until separately reviewed.

**Google OAuth External/Testing refresh tokens typically expire after seven days for YouTube scopes.** Before relying on indefinite unattended uploads, arrange an eligible publishing status and any necessary Google verification, then reauthorize and test. Upload quotas and spam/quality controls may require reducing the volume.

Only YouTube is currently connected to vidIQ for this education brand. Adding new Instagram/TikTok accounts requires their own explicit account connection and platform-supported permissions; these integrations are not claimed as configured.

## Confirmed real-world crossposting on 24 November 2026

These were actual server-confirmed results, not just prepared drafts:

- [First Sinhala text quiz on Blogger](https://punchinanamaga.blogspot.com/2026/11/2026-11-24_0758378445.html), with matching Facebook Page publication confirmed by GitHub [run 45413803714](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45413803714).
- Matching [YouTube Private text-poll companion](https://www.youtube.com/watch?v=fWKUmHpr74E), exact destination channel confirmed by that run.
- The first full three-Facebook-Reel mirror [run 45414137233](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45414137233) skipped an existing private video without reposting it, and uploaded two more original videos privately:
  [Reel 2](https://www.youtube.com/watch?v=aLKKLApwkeA) and
  [Reel 3](https://www.youtube.com/watch?v=fDnsXHmhlg4).
- Both new poll graphics and narrated video companions were rendered and tested in GitHub preview runs
  [45413110771](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45413110771) and
  [45412679214](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/45412679214).

No public YouTube video has been published by these new workflows. YouTube Made-for-Kids restrictions and YouTube API limitations continue to apply. Facebook video generation and existing source workflows were not changed.

