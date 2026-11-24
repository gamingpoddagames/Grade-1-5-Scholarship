# පුංචි නැණ මඟ — Sinhala End Card: Subscribe + Follow

Implemented 24 Nov 2026 at the owner's request.

## Exactly what changes

Every **newly generated/published video in the integrated video pipelines** gets
one short original Sinhala-voiced **outro**, with channel brand and a mobile
friendly 9:16 card. The answer and main video stay exactly as the original.

- **YouTube school/Grade 1–5 videos:** `පුංචි නැණ මඟ`; **SUBSCRIBE · LIKE · SHARE**. No COMMENT prompt on these videos because YouTube may disable comments on Made-for-Kids videos.
- **YouTube genuinely general-audience videos:** `පුංචි නැණ මඟ`; **SUBSCRIBE · LIKE · COMMENT · SHARE**.
- **Facebook school/general videos:** `පුංචි නැණ මඟ`; **FOLLOW · LIKE · COMMENT · SHARE**.

The full Sinhala spoken call to action is intentionally a **separate last
segment**, never superimposed on the question, answer, photo, or narrator.
All end-cards include the owned free-learning Blogger destination
`punchinanamaga.blogspot.com`. There is no Adsterra script on the card and no
ad click/forced redirect or misleading button; the CTA is merely part of the video.

All artwork and voice are original code-based assets. Noto Sinhala RAQM + a Latin
fallback font are used with readability/overflow checks. The helper detects
720×1280 and 1080×1920 source formats, preserves the original MP4 on disk and
writes a separate `-facebook-cta.mp4` or `-youtube-cta.mp4`.

## Applied to new future releases

1. `school/daily_reel_quiz.py` (three daily Facebook image-led narrated Reels)
2. `school/three_reels.py` (three original daily Facebook/Blogger Reels)
3. `school/publish_ocean_quiz_video.py` (daily Blogger/Facebook quiz Reel)
4. `school/voice-video.yml` (the Piper Sinhala voiced quiz, now adding a Facebook outro)
5. `school/website_promo_publish.py` (Facebook narrated Blogger website invitation)
6. `school/youtube_shorts.py` (YouTube daily Short)
7. `school/youtube_social_mirror.py` (Facebook/Blogger content mirrored to YouTube)
8. `school/youtube_poll_shorts.py` (YouTube companion Short to FB/Blogger polls)
9. `school/adult_general_quiz.py` (adult/parent content — separate platform-specific outros)

Photo-only Facebook/Blogger posts have no appended video outro because they are
not video files. Their photo posts and captions are left untouched.
Previously published videos are **not automatically modified or re-uploaded**.

## QA and troubleshooting

- Run `python -m unittest discover -s school -p 'test_video_cta.py' -v`.
- Preview card only: `python school/video_cta.py --card-only --platform facebook --audience general --output school/output/facebook-cta.png`.
- Preview full original+CTA video: `python school/video_cta.py --video YOUR_ORIGINAL.mp4 --platform youtube --audience school`.
- Full safe GitHub workflow:
  `.github/workflows/video-cta-preview.yml`, triggered by
  `school/video-cta-preview-request.txt` or manual dispatch.
  It does **not** publish to any channel.
- A missing Google TTS response, absent audio stream, unknown video dimensions,
  missing Sinhala font, clipped text or unusual duration **fails closed**;
  do not publish a silently malformed video.
- The original video generator is not changed. Combining the original source
  with the outro re-encodes the final copy at high visual quality (CRF 18).

The channel-wide audience setting is never changed. Each YouTube video keeps its
existing per-video content-specific audience classification and privacy.
