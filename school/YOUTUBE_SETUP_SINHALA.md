## අලුත් CODE-FIRST Setup — දැන් මේකෙන් පටන්ගන්න

ඔයාට Google Cloud Project එක අතින් හදන්න අවශ්‍ය නැහැ. අපි සකස් කළ
Windows CMD launcher එක ඒක **code මඟින්** කරනවා. YouTube channel:
`UCQ2EM8DjUfg3WgzB8r6hYDQ`.

**PC එකේ මුලින්ම CMD එක විවෘත කර පහත commands යොදන්න:**

```cmd
git clone https://github.com/gamingpoddagames/Grade-1-5-Scholarship.git
cd Grade-1-5-Scholarship
school\setup_youtube_cloud_windows.cmd
```

Repository එක කලින්ම download කරලා තිබේ නම් අලුත් clone කිරීම
වෙනුවට එහි folder එකේ `git pull` කර අවසන් command එක පමණක් දාන්න.

Script එකෙන් සිදු වන්නේ:

- Google Cloud CLI නැත්නම් Windows `winget` හරහා install කිරීමට
  මුලින් ඔයාගේ අනුමැතිය ඉල්ලනවා.
- Google Cloud CLI login එක browser එකෙන් ලබාගන්නවා.
- `mfk110` prefix සහිත වෙනම YouTube Upload Project ID එකක්
  සකස් කරනවා; ඒ ID එක local file එකක සුරකිමින් නැවත run කළත්
  project එක අලුතින් නිර්මාණය නොකර පරණ project එක යොදාගන්නවා.
- `youtube.googleapis.com` API එක enable කරලා තහවුරු කරනවා.
- Google Auth Platform / OAuth Clients පිටුව එම project එක සමඟම
  browser එකේ විවෘත කරනවා.
- **Google OAuth Desktop Client එක නිර්මාණය කර JSON download කිරීම**
  Google ගිණුම් හිමිකරු විසින් Google Auth Platform UI එකේ කළ යුතුයි.
  එය automate කළ බව නොකියයි.
- JSON file එකේ **path** එක CMD තුළ දුන් පසු, script එක ඒක නිවැරදි
  project එකට අදාළදැයි බලලා browser OAuth consent හරහා නිවැරදි
  YouTube channel එක තහවුරු කරනවා.
- GitHub CLI (`gh auth login`) සම්බන්ධ කර තිබේ නම්
  අවසර ලත් OAuth data GitHub encrypted Actions Secrets වලට
  කෙළින්ම save කරනවා. දිනපතා **Private** upload පමණක් සක්‍රීය කරනවා.

සුරක්ෂිතතාව: Google password, OTP, downloaded JSON, client secret,
refresh token **ChatGPT / Telegram / Facebook වෙත එවන්න එපා**.
JSON එක පෞද්ගලික PC එකේම තබන්න.

අනිවාර්යයෙන් browser එකෙන් කරන්න ඉතිරිවෙන්නේ **Google login හා
OAuth Desktop Client එකට consent ලබාදීම**යි.
Public Shorts ස්වයංක්‍රීයව upload කිරීම වෙනම QA අනුමැතියක් තෙක් off.

[Google Cloud setup Python script](youtube_cloud_bootstrap.py) ·
[Windows launcher](setup_youtube_cloud_windows.cmd) ·
[GitHub YouTube workflow](https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/workflows/youtube-shorts.yml)

---

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
