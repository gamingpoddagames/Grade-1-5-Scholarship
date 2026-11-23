# පුංචි නැණ මඟ – YouTube ස්වයංක්‍රීය Upload Setup (සිංහල)

**ඔයාගේ YouTube Channel:** https://www.youtube.com/channel/UCQ2EM8DjUfg3WgzB8r6hYDQ

GitHub source code, Sinhala Shorts renderer, private upload workflow සහ security tests සකස් කර ඇත. vidIQ channel connection එකත් තහවුරු කර ඇත. නමුත් vidIQ login එකෙන් ලැබුණු අවසර GitHub Actions වෙත ස්වයංක්‍රීයව මාරු නොවේ. Google account එකේ නිල OAuth අවසරය එක් වරක් ලබාදීම අවශ්‍යයි.

## පළමු වතාවට කරන්න ඕනේ

1. Google Cloud Console එකට යන්න: https://console.cloud.google.com/projectcreate
2. **අලුත්** YouTube Upload Project එකක් හදන්න. **Project ID එක `mfk110` අකුරු වලින් ආරම්භ විය යුතුයි** (Made for Kids API policy එක අනුව).
3. YouTube Data API v3 සක්‍රීය කරන්න: https://console.cloud.google.com/apis/library/youtube.googleapis.com
4. Google Auth Platform / Credentials වලින් **OAuth Client – Desktop app** එකක් හදා JSON file එක ඔබේ Windows PC එකට download කරන්න.
5. GitHub CLI නොමැති නම් https://cli.github.com/ වෙතින් install කරන්න. CMD එකේ `gh auth login` කර ඔබේ GitHub account එකට login වෙන්න.
6. CMD එකේ මෙහෙම කරන්න:

```cmd
git clone https://github.com/gamingpoddagames/Grade-1-5-Scholarship.git
cd Grade-1-5-Scholarship
school\setup_youtube_windows.cmd
```

මීට කලින් repository එක clone කරලා තිබුණොත් අලුතින් clone කරන්න අවශ්‍ය නැහැ. Repo folder එකට ගිහින් `git pull` කර `school\setup_youtube_windows.cmd` run කරන්න.

7. CMD එක JSON file එකේ path එක අහන විට file path එක දෙන්න. Google login browser එක විවෘත වෙයි. YouTube channel එකේ Google account එකෙන් authorize කරන්න.
8. Script එක නිවැරදි Channel ID එක පරීක්ෂා කරලා GitHub Actions Secrets තුනක් **ආරක්ෂිතව** save කරනවා. ඔබට token එක copy/paste කරන්න හෝ ChatGPT එකට එවන්න අවශ්‍ය නැහැ.

## පළමු Private Video Test

[YouTube Shorts GitHub Actions](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/workflows/youtube-shorts.yml) වෙත ගිහින් **Run workflow** කරන්න.

- **upload:** true
- **privacy:** private

YouTube Studio එකේ වීඩියෝවේ සිංහල අකුරු, voice, answers සහ audience setting පරීක්ෂා කරන්න.

## ඉදිරි දිනපතා ක්‍රියාකාරීත්වය

- **ශ්‍රී ලංකා වේලාව:** දහවල් 12:45
- **වීඩියෝ:** 1080×1920 Sinhala Quiz Short
- **Audio:** Sinhala voice
- **බ්ලොග් URL:** https://punchinanamaga.blogspot.com/
- **Audience:** Made for Kids
- **Default privacy:** Private

**Public Auto Upload එක දැන් සක්‍රීය නැහැ.** වීඩියෝ ගුණාත්මකභාවය පරීක්ෂා කරලා පසුව Google / YouTube ප්‍රතිපත්ති අනුව එය සක්‍රීය කළ හැකියි.

**අත්‍යවශ්‍ය ආරක්ෂාව:** Google passwords, OTP, client secret JSON, refresh tokens මේ chat එකට, Telegram එකට, Facebook එකට හෝ public GitHub files වලට කිසිවිටක එවන්න එපා.

මෙම පියවර මඟින් සියල්ලම නොමිලේ සහ ස්වයංක්‍රීයව සිදුවන බව සහතික නොවේ: Google API quota, සීමා, credentials expiration, YouTube policies සහ hosting/publishing limits බලපායි. vidIQ හි පළමු private draft එකත් වෙනම පවතින නිසා එකම video එක දෙවරක් publish නොකරන්න.
