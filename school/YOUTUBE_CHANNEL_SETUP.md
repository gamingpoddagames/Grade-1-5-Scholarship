# Punchi Nena Maga YouTube Channel Setup

## Verified destination from channel owner

- Channel: https://www.youtube.com/channel/UCQ2EM8DjUfg3WgzB8r6hYDQ
- Permanent ID: UCQ2EM8DjUfg3WgzB8r6hYDQ
- Intended brand name: පුංචි නැණ මඟ
- English name: Punchi Nena Maga – Grade 1–5 & Scholarship
- Recommended handle: @PunchiNenaMaga (only if YouTube says available; not verified)
- Website: https://punchinanamaga.blogspot.com/
- Video category: Education (27)
- Spoken language: Sinhala (si)
- Intended audience: primary-school learners; quiz uploads marked Made for Kids.
- Brand images: existing owner-approved profile image, cover banner and thumbnail.
- Playlist suggestions: "5 ශ්‍රේණිය ශිෂ්‍යත්ව බුද්ධි පරීක්ෂණ", "ගණිත ගැටලු", "සාමාන්‍ය දැනුම", "Grade 1–5 කෙටි පාඩම්", "YouTube Shorts". Playlists require a YouTube login to create.

## Channel description (paste into YouTube Studio > Customization > Profile)

පුංචි නැණ මඟ වෙත සාදරයෙන් පිළිගනිමු!

1 සිට 5 ශ්‍රේණිය දක්වා දරුවන්ගේ දැනුම, සිතීමේ හැකියාව සහ විභාග සූදානම වැඩිදියුණු කිරීමට නිර්මාණය කළ සිංහල අධ්‍යාපනික YouTube නාලිකාවකි.

අපගේ වීඩියෝවලින් ශිෂ්‍යත්ව බුද්ධි පරීක්ෂණ, ගණිත ගැටලු, රූප රටා, සාමාන්‍ය දැනුම සහ පිළිතුරු පැහැදිලි කිරීම් ලබාගන්න.

තවත් නොමිලේ ප්‍රශ්න සහ පාඩම්:
https://punchinanamaga.blogspot.com/

මෙය ස්වාධීන අධ්‍යාපනික ව්‍යාපෘතියකි. මෙහි අභ්‍යාස නිල විභාග ප්‍රශ්න නොවේ.

## Current implemented GitHub automation

- `school/youtube_shorts.py`: reuses the current quiz bank and renderer. Original vertical 1080x1920 MP4 with Sinhala voice, A–D choices and answer-reveal, plus YouTube Shorts metadata. 
- `.github/workflows/youtube-shorts.yml`: daily 12:45 PM Sri Lanka time, with safe manual workflow dispatch, MP4 artifact and metadata report.
- `school/test_youtube_shorts.py`: tests matching channel ID, Made for Kids status, private-by-default visibility, duplicate markers and missing authorization.
- Each Short links to the **owned Blogger homepage** without Adsterra popunder or redirect.
- No live upload occurs until the user completes Google OAuth authorization and deliberately enables uploading.
- Default visibility is **private**. Changing it to public/unlisted requires a separate deliberate variable `YOUTUBE_PUBLICATION_REVIEWED=true`.
- Duplicate checking looks for a matching title or unique date marker in the channel uploads list. Do not delete or rerun an already-uploaded Short to bypass those safeguards.

## One-time secure Windows setup (new)

The owner has connected the exact channel through vidIQ. That connection is usable
inside ChatGPT, but does **not** transfer the Google OAuth refresh token to GitHub
Actions. This owner-only setup handles Google authorization in the local browser
without pasting secrets into any chat or committing them to Git.

1. Open [Google Cloud Console](https://console.cloud.google.com/projectcreate)
   with the Google account that owns the channel. Create a **dedicated Upload
   Project** whose project ID **begins with mfk110** (for example,
   `mfk110-punchi-uploads`, subject to ID availability). YouTube's Made for Kids
   Developer Policies require this prefix for uploading the owner's own
   child-directed videos through a non-child-directed API client.
2. Enable [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com).
3. In Google Auth Platform, configure the owner OAuth audience/consent, then
   create a **Desktop app** OAuth Client. Download the JSON file onto the PC.
   Do not upload this JSON to GitHub or ChatGPT.
4. On Windows, install [GitHub CLI](https://cli.github.com/) if needed, then
   use the official browser sign-in once with `gh auth login`.
5. In Windows Command Prompt, run:
   ```cmd
   git clone https://github.com/gamingpoddagames/Grade-1-5-Scholarship.git
   cd Grade-1-5-Scholarship
   school\setup_youtube_windows.cmd
   ```
   If the repository was cloned already, run `git pull` inside it and launch
   `school\setup_youtube_windows.cmd`. Enter the path to the downloaded
   Google OAuth JSON file when prompted.
6. The wizard verifies that the account authorized **exactly**
   `UCQ2EM8DjUfg3WgzB8r6hYDQ`, then saves **three encrypted GitHub Actions
   Secrets** through `gh secret set` using stdin. It sets workflow
   `YOUTUBE_UPLOAD_ENABLED=true`, `YOUTUBE_PRIVACY=private`, and
   `YOUTUBE_PUBLICATION_REVIEWED=false`. No credentials are printed,
   stored as plain-text files, or committed to the repository.
7. Open the [YouTube Shorts GitHub Actions workflow](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/workflows/youtube-shorts.yml),
   choose **Run workflow**, set **upload=true**, and leave **privacy=private**.
   Check the generated `youtube-upload-receipt.json` and inspect the video in
   YouTube Studio before approving any wider publication.

The scheduled workflow runs at **12:45 Sri Lanka time**. After this
setup it uploads **private** Shorts; daily public posts are **not** enabled.
To enable public scheduling later, the owner must deliberately set
`YOUTUBE_PRIVACY=public` and
`YOUTUBE_PUBLICATION_REVIEWED=true` under GitHub Actions Variables after
checking videos and applicable platform policies.

**Important:** Google Cloud Personal mode may be useful for a project that
only authorizes its owner's Google Account. If using a Google OAuth Testing
audience, refresh tokens may expire and require reauthorization; follow the
current Google Auth Platform guidance for the chosen audience. The site and
channel do not receive direct third-party ad redirects.

## vidIQ test upload draft

The connected account was verified as the exact channel ID above. The first
Grade 4 Sinhala quiz MP4 was prepared as a **private vidIQ draft**. The
GitHub Actions OAuth uploader is an independent pipeline and will not inherit
vidIQ's connection. Do not publish the same video twice through the two
methods; check the channel before completing the first test.

## Required Google login / YouTube API authorization

**Important:** A public Channel ID is not authorization. Neither GitHub access nor a channel link can grant YouTube upload rights.

Current YouTube API Developer Policies have a special section for videos marked Made for Kids (section III.J). The channel owner should use a separate non-child-directed **Upload Project** to upload their own children's videos, with the project ID prefixed as Google specifies with `mfk110`. Review https://developers.google.com/youtube/terms/developer-policies/ before setting it up; do not use a child-directed API client to perform write actions.

1. Sign in to https://console.cloud.google.com/ with the Google account owning the YouTube channel. Create an upload project suitable for YouTube's current Made for Kids API policy.
2. Enable **YouTube Data API v3** at https://console.cloud.google.com/apis/library/youtube.googleapis.com.
3. Set up **OAuth consent screen** and register a **Desktop application OAuth Client** at https://console.cloud.google.com/apis/credentials.
4. Approve exactly these OAuth scopes for a desktop owner-authorized upload tool:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube.readonly`
5. Complete the owner Google authorization in your own browser (do not share passwords, verification codes or OAuth tokens in ChatGPT messages).
6. Save resulting OAuth **client ID, client secret and refresh token** directly into repository Settings > Secrets and variables > Actions > **Repository secrets**:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`
7. The public channel ID is already hard-coded and checked before upload: `UCQ2EM8DjUfg3WgzB8r6hYDQ`. Do not replace it with an unrelated Google account's channel ID.
8. Start with **Actions variable** `YOUTUBE_UPLOAD_ENABLED=true` and `YOUTUBE_PRIVACY=private` to permit private tests. Leave `YOUTUBE_PUBLICATION_REVIEWED` unset until the owner verifies the output on YouTube Studio and explicitly wants broader publication.
9. Use the workflow's manual Run action to render or perform the authorized private test. Review the confirmed video ID and privacy status in the uploaded artifact file `youtube-upload-receipt.json`.
10. To schedule public uploads, review YouTube child-directed policies and content quality and select a visibility setting intentionally. Made for Kids changes YouTube features, including comment availability.

Use the official Google OAuth instructions: https://developers.google.com/youtube/data/guides/authentication

## Quality and privacy cautions

- Sinhala spelling, spoken pronunciation and the answer reveal still require a real MP4 QA check before declaring the uploader ready for public posts.
- The OAuth client consent application may need additional Google authorization/verification before routine use.
- Google may adjust developer rules, quota or upload visibility; consult the current official API documentation.
- YouTube commenters cannot be solicited on child-directed videos if comments are unavailable; educational comment discussions can remain on the associated Facebook Page under platform rules.
- This integration does not change the existing Facebook or Blogger automatic publishing. YouTube is additive.
- No credential must be committed to GitHub source files or pasted into the public channel description.
