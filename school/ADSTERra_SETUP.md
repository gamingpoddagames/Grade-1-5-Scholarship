# Blogger advertising: current installation

Checked 2026-11-22 in the owner's signed-in Adsterra dashboard and Blogger editor.

| Item | Observed state |
| --- | --- |
| Public destination | https://punchinanamaga.blogspot.com/ |
| Adsterra website | 6219537, Approved |
| Existing Social Bar | SocialBar_1, 32413123, Active |
| Exact code | `https://bicea.org/14/3777aa5b8fbe2c3a7513a1e6dc0637c5` |
| Adult ads setting | OFF for this Social Bar unit |
| Existing Popunder | 32413124; not installed by this change |
| Blogger placement | Footer HTML/JavaScript gadget `HTML1`, title `විකල්ප දැන්වීම්` |
| Privacy page | https://punchinanamaga.blogspot.com/p/blog-page_574.html |

## Behavior

`blogger_optional_adsterra_widget.html` preserves the existing vendor URL and loads it only after a visitor explicitly selects the optional ads button. Educational content remains available without this choice. It requests no ad on initial page load, prevents duplicate loaders, and displays readable Sinhala status and failure messages. It adds no redirect, timer that navigates, click interception, or ad-gated download.

Social Bar is a vendor-controlled display format, not a fixed banner. The wrapper cannot certify every future creative, enforce all vendor behavior, or replace a consent-management platform. The optional choice applies to this Adsterra loader; Blogger/Google and embedded resources have their own behavior. Adult ads OFF does not prove that every creative suits children. For broader automatic ad serving, ask Adsterra to confirm appropriate category exclusions and whether a contextual banner unit can meet this site's audience requirements. Do not enable the existing Popunder.

Blogger escapes some non-ASCII characters inside gadget scripts. Keep JavaScript status literals as Unicode escapes; ordinary HTML remains readable Sinhala. `test_ad_widget.js` checks the loader without contacting Adsterra.

## Verification and limits

- Verified the installed footer, opt-in button and exact code on the public Blogger site.
- Verified zero copies of the external Social Bar script before the choice, and one loader afterwards; onload completed and the page stayed on Blogger.
- The dashboard Statistics view, filtered to this exact website and SocialBar_1, showed recorded impressions and clicks. This establishes reported activity for the unit; it does not identify which visitor caused it or prove this browser test earned revenue. A rendered creative was not visually confirmed in this browser. A script onload event alone is not proof of a paid impression.
- No paid creative was clicked, no automated impression loop was run, and no income is inferred from website approval.
- Confirm real traffic reporting in Adsterra Statistics filtered to this website and unit. Empty reporting can mean no qualifying impressions, reporting delay, inventory or delivery restrictions; investigate with Adsterra rather than repeatedly refreshing/clicking ads.
- Desktop footer verified, including links to the four published Privacy, About, Contact and Terms pages; real mobile creative delivery remains to be checked.

## Facebook destinations

Photo, text and video publishers call `blogger_link_safety.validate_blogger_links` before any Facebook API request. Captions must contain HTTPS links to the exact owned Blogger host. Extra external URLs, GitHub Pages destinations, spoofed hosts and redirect query destinations are rejected. Normal article links and campaign UTM parameters work. PDF files and the quiz can still be served from the existing GitHub resource host inside Blogger.

## Maintenance and rollback

1. Edit the existing `විකල්ප දැන්වීම්` HTML/JavaScript gadget in Blogger Layout; do not add duplicate copies.
2. Keep the Adsterra source URL unchanged unless a newly issued dashboard code replaces it.
3. To stop future Adsterra loading, remove or disable that one gadget and save Layout. Already-open pages should be reloaded; removing the gadget cannot erase third-party cookies already stored by a browser.
4. Keep the privacy page aligned with actual operation. Its source addition is `blogger_adsterra_disclosure.html`, included in future Blogger exports. The publisher skips existing pages and does not automatically overwrite the live disclosure.
5. Run `python -m unittest discover -s school -p 'test_*.py' -v` and `node school/test_ad_widget.js` after relevant changes. The dedicated offline GitHub workflow requests no ads and needs no account credentials.

The older `blogger_sponsored_entry.html` is a template only and is not used as a required entry page. `adsterra_user_provided_snippet.html` archives the raw vendor tag: do not paste it alongside the optional gadget, which would defeat opt-in behavior.
