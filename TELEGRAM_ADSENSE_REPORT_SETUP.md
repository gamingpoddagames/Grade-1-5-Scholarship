# පුංචි නැණ මඟ — AdSense + Private Telegram reports

## What is actually verified (as of 20 November 2026)
- Blogger website: https://punchinanamaga.blogspot.com/
- Blogger API OAuth working via this repository's existing GitHub secrets.
- Blogger publicly published About, Contact, Privacy, Terms pages; Search Console sitemaps were successful according to owner's screenshots.
- Google Search Console homepage indexing request accepted; this does not mean indexed yet.
- AdSense site list showed **Linked with Blogger**, **Getting ready**, **ads.txt Not found** in last user screenshot. There is **no confirmed AdSense approval, displayed ad, or earnings**.
- Check AdSense Home for all account-level activation tasks, and Sites for **Ready**; do not add unsupported ad scripts or claim approval.

## AdSense: remaining review checklist
1. Open https://www.google.com/adsense/ and check any required identity, account, payment details, consent or site actions directly.
2. In **Sites**, inspect punchinanamaga.blogspot.com. Only **Ready** confirms site review approved. No account credentials are available to this GitHub repo to inspect this private page automatically.
3. In Blogger > Earnings, confirm the same AdSense account is associated. Use Blogger's integration rather than opening another AdSense account.
4. If ads.txt continues to show **Not found**, open https://punchinanamaga.blogspot.com/ads.txt and compare with Blogger > Settings > Monetization. Google's Blogger guidance says custom ads.txt isn't needed when *only* using the built-in Blogger AdSense integration; third-party/manual ads need proper configuration. Do not put a guessed publisher ID into ads.txt.
5. Ensure original useful content, clear navigation, child-appropriate privacy practices, and no deceptive links or forced ad redirects. Keep ads disabled until Google approval.
6. After approval, enable appropriate placement in Blogger's Earnings/Layout or AdSense, follow child-directed privacy/ad targeting requirements, then verify actual displayed ads without clicking your own advertisements.
7. Monitor Google Search Console performance and AdSense earnings in their respective dashboards. A Telegram report using only Blogger OAuth cannot read either dashboard.

Official documentation:
- https://support.google.com/adsense/answer/12170222
- https://support.google.com/adsense/answer/12131223
- https://support.google.com/blogger/answer/1269077

## Private Telegram operations reporting
Workflows now added:
- **School Daily Telegram Operations Report** — each day around 08:30 Sri Lanka (GitHub schedule may be delayed).
- **School Telegram Workflow Failure Alerts** — sends an alert for a confirmed failure/timed-out/action-required run in the website/blog/Facebook/health pipelines.

Both send **only** after the owner configures these two repository-level GitHub Actions **Secrets**:
- `TELEGRAM_BOT_TOKEN`: token for a bot the owner controls, obtained directly from BotFather. Never commit/paste the token into public files or ChatGPT.
- `TELEGRAM_CHAT_ID`: numeric ID of an authorized **private chat** (or private operations group where the bot is a member). Do not use a public school channel for sensitive operations messages.

Set these at:
https://github.com/gamingpoddagames/Grade-1-5-Scholarship/settings/secrets/actions

To obtain the chat ID safely, message your bot first with /start. In a private environment, use Telegram API getUpdates with your token, inspect the `message.chat.id`, and save only that number as GitHub Secret. Never show/share getUpdates JSON or bot token publicly. Another bot may assist with numeric ID but scrutinize its privacy.

Once secrets are saved, manually run:
https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/workflows/school-telegram-report.yml
Choose **Run workflow**, `send=true`, and confirm a successful step **Telegram report delivery confirmed by Telegram API**.

If the secrets are absent, the daily workflow creates a report artifact but sends **nothing**. Status notices do not include Google Search Console traffic metrics or AdSense earnings until separate authorized integrations with those services are available.

Never use or forward an exposed OAuth refresh token. Rotate one if it is accidentally posted to a chat, source code, or logs.
