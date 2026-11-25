#!/usr/bin/env python3
"""Send a single private Telegram warning for a failed trusted school workflow.

Requires TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID set in this repository's Secrets.
No third-party PR payload is executed or credentials are echoed.
"""
import os
from telegram_report import telegram_send

ALLOWED={
  "Punchi Nena Maga Daily Education",
  "Blogger Auto Publisher (Google OAuth)",
  "Publish Scholarship Website",
  "School Daily Content (No AI)",
  "Test Sinhala Voiceover (No Paid AI)",
  "School Website Visitor Promotion (FB Photo and Sinhala Video)",
  "Weekly Blogger Growth Health Check",
  "Build Blogger Starter Kit",
}

def make_alert(name, conclusion, url):
    if name not in ALLOWED:raise ValueError("Unexpected workflow")
    if conclusion not in ("failure","timed_out","action_required"):return ""
    if not url.startswith("https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/runs/"):
        raise ValueError("Workflow URL is not in the owned GitHub repository")
    return "\n".join((
        "⚠️ පුංචි නැණ මඟ — GitHub Automation Alert",
        "Workflow: "+name,
        "Status: "+conclusion,
        "🔎 Run details: "+url,
        "Check GitHub Actions logs; this alert does not mean the Blogger website is offline."
    ))

def main():
    msg=make_alert(os.getenv("WORKFLOW_NAME",""),os.getenv("WORKFLOW_CONCLUSION",""),
                   os.getenv("WORKFLOW_URL",""))
    if not msg:
        print("No Telegram alert required.")
        return
    bot=os.getenv("TELEGRAM_BOT_TOKEN","")
    chat=os.getenv("TELEGRAM_CHAT_ID","")
    if not bot or not chat:
        print("::warning::Telegram failure alert cannot be sent: add private TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets.")
        return
    telegram_send(msg,bot,chat)
if __name__=="__main__":main()
