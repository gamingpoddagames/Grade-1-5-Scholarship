# GitHub → Blogger automatic posting ($0 workflow)

**Blogger:** https://punchinanamaga.blogspot.com/  
**Expected Blog ID:** `1195814952260080161`  
**Repository:** gamingpoddagames/Grade-1-5-Scholarship  
**GitHub Actions:** `.github/workflows/blogger-publish.yml`

## Status
The GitHub code builds 15 **original practice-post drafts** and four Blogger-specific About/Contact/Privacy/Terms page drafts. A Blogger API publisher handles UTF-8 Sinhala, Google access-token refresh, blog-host/ID verification, duplicate-title prevention, preview mode, draft mode and public posting. **It cannot post until the blog owner securely authorizes their Google account.** It does not configure AdSense or promise approval/income.

## One-time Google authorization (must be done by blog owner)
1. Open https://console.cloud.google.com/ and create/select a Google Cloud project. Enable **Blogger API v3** in APIs & Services → Library. Usually no paid service is needed for modest Blogger API usage; do not attach billing unless an unrelated Google service specifically requires it.
2. Configure Google Auth Platform OAuth consent. Select the correct app audience. Use your own Google account as test user while Testing. Grant **Blogger API manage scope** `https://www.googleapis.com/auth/blogger`. Do not share passwords or verification codes.
3. Create an **OAuth 2.0 Client ID**, Application type **Desktop app**. Note its Client ID and Client Secret **privately**.
4. On your own Windows computer (not in a public terminal), run:
   ```cmd
   py -m pip install google-auth-oauthlib
   py school\blogger_oauth_local.py
   ```
   The browser shows Google's consent page. Review and authorize only the requested Blogger access. The helper displays a refresh token **locally**; never commit or send it in chat. An External/Testing OAuth consent project may issue Blogger refresh tokens that expire in 7 days. Google may require additional OAuth verification before broad public availability; creating an OAuth app does not imply approval.
5. Open GitHub repository **Settings → Secrets and variables → Actions → Secrets → New repository secret**. Add:
   - `BLOGGER_CLIENT_ID` (Desktop OAuth client ID)
   - `BLOGGER_CLIENT_SECRET` (Desktop OAuth client secret)
   - `BLOGGER_REFRESH_TOKEN` (refresh token from local OAuth helper)
   **NEVER** use plaintext repo files, workflow variables, issue comments, ChatGPT messages, or console logs for secrets.
6. In GitHub **Actions → Blogger Auto Publisher (Google OAuth) → Run workflow**, choose **draft** and **posts**, limit `1`. This performs your first authenticated test and creates **one private draft** if permissions are valid; a run showing “success” in preview mode is **not** a published article.
7. Review the draft manually in Blogger, correct spelling and curriculum issues, and publish it there. Then review four policy-page drafts before making them public. For Blogger API `pages`, draft mode is blocked because safe drafting is not uniformly documented; `publish` explicitly creates a public page.
8. **Only after reviewing and approving the prepared content**, use GitHub **Actions → Variables → New repository variable** to set:
   - `BLOGGER_ALLOW_PUBLICATION=true` (permits public posts through this workflow)
   - `BLOGGER_AUTOMATION_ENABLED=true` (enables scheduled public posts)
   Without **both**, scheduled jobs do nothing; without valid Secrets, authenticated jobs fail closed.
9. Runs daily at **11:15 AM Sri Lanka** (05:45 UTC); GitHub scheduled jobs may be delayed or skipped. Each successful scheduled run publishes **at most one previously unpublished** article and stops when the prepared 15 titles already exist. It does not generate endless new content or recycle duplicates. No ads are inserted.
10. Monitor the workflow history. A successful action can mean “no changes” (e.g., no new posts); confirm a `PUBLISHED: ...` line in logs for every actual post. Facebook scheduling is separate.

## Risk and privacy
- Do not grant publishing until content is reviewed for factual accuracy, Sinhala spelling, grade suitability, originality, and privacy. This content is *independent practice*, not official examination or Ministry of Education content.
- Children-directed blogging requires special attention to privacy, Google policies and non-personalized ads. **Blogger API authorization does not approve AdSense.**
- If an OAuth refresh token is revoked, expires or API permissions are disabled, the job fails; renew authorization securely.
- If Blogger contains an existing post with the same *title*, this automation skips it rather than overwriting. Title-based checks do not detect duplicates with different titles.
- Never allow this repository or workflow to print or store credentials in published artifacts.
- The free blog is https://punchinanamaga.blogspot.com/; the separate PDF resource site remains https://gamingpoddagames.github.io/Grade-1-5-Scholarship/.

## Official developer documentation
- Blogger posts.insert: https://developers.google.com/blogger/docs/3.0/reference/posts/insert
- Blogger pages.insert: https://developers.google.com/blogger/docs/3.0/reference/pages/insert
- Blogger posts.list: https://developers.google.com/blogger/docs/3.0/reference/posts/list
- OAuth offline access: https://developers.google.com/identity/protocols/oauth2/web-server
- Blogger–AdSense: https://support.google.com/blogger/answer/1269077
