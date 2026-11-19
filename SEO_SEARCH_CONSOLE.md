# පුංචි නැණ මඟ — Google Search සහ Organic Traffic ($0)

## Current sites
- Primary educational blog: https://punchinanamaga.blogspot.com/
- Static PDF / quiz resource library: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/
- Blogger's real, published legal pages:
  - Privacy: https://punchinanamaga.blogspot.com/p/blog-page_574.html
  - Terms: https://punchinanamaga.blogspot.com/p/blog-page_360.html
  - About: https://punchinanamaga.blogspot.com/p/blog-page.html

## Completed in GitHub
- Site homepage includes Sinhala search-intent title, descriptive meta summary, canonical URL, `WebSite` JSON-LD, and crawlable learning section links.
- School website links clearly to the Blogger articles; content links back to the original PDFs/quizzes without duplicating full blog articles.
- GitHub Actions regenerates the sitemap for the resource site and runs `school/seo_audit.py` before deploying.
- Blogger's daily post publisher already uses original Sinhala content and prevents publishing duplicate titles. Each scheduled run publishes at most one new post; the initial content set is limited and does **not** run indefinitely when exhausted.

## One-time Google Search Console account action
These steps must be completed by the owner in the appropriate Google Search Console account. The repository OAuth credentials are for **Blogger API**, not Search Console, so GitHub cannot submit these sitemaps or verify the property with its current tokens.

1. Open https://search.google.com/search-console and add a **URL-prefix** property: `https://punchinanamaga.blogspot.com/`
2. Verify ownership by the offered Blogger-compatible method, using the same Google account that owns the blog.
3. Go to **Sitemaps** and submit:
   - `sitemap.xml` (Blogger auto-generated post sitemap)
   - `sitemap-pages.xml` (Blogger auto-generated static-pages sitemap)
   Check the status says **Success** or inspect reported errors. Do NOT attempt to upload these XML files as blog posts.
4. Also check the already-verified resource-site property `https://gamingpoddagames.github.io/Grade-1-5-Scholarship/` and its `sitemap.xml`.
5. In **URL Inspection**, enter the blog homepage URL and one newly published article. If eligible but not indexed, use **Request indexing** sparingly. There is no guarantee of immediate indexing.
6. Blogger > Settings: enable **Visible to search engines** and **Meta tags > Enable search description** with the following accurate description:
   `පුංචි නැණ මඟ: 1–5 ශ්‍රේණි සඳහා ගණිතය, සිංහල, පරිසරය සහ 5 ශ්‍රේණිය ශිෂ්‍යත්ව පුහුණුව. නොමිලේ පාඩම්, PDF ප්‍රශ්න පත්‍ර, Online Quiz සහ දෙමාපිය උපදෙස්.`
7. Unless you have a specific diagnosed indexing issue, leave Blogger **custom robots.txt** and **custom robots header tags** disabled: Blogger provides suitable default robots and auto-generated sitemaps.
8. Monitor **Performance → Search results** weekly for impressions, clicks, CTR, and individual search queries. Improve poorly matching titles and write genuinely useful answers for real parent/teacher questions.

## Original content roadmap (avoid thin/duplicated content)
- Sinhala guide: how to practise Grade 5 Scholarship past papers, with link to the Department of Examinations; **do not present our custom PDFs as official past papers**.
- Sinhala guide: helping a Grade 1 pupil learn number bonds safely with objects (original sample activities).
- Sinhala guide: how to check Grade 5 results privately at the official results site, **do not collect student index numbers**.
- Sinhala guide: weekly parents' reading plan with age-appropriate book recommendations and links to legitimate publishers.
- A real, helpful FAQ for each grade/subject. Use school-relevant search phrases naturally, never keyword stuffing.

## Restrictions and expectations
- Google crawling/indexing usually takes days or weeks and is not guaranteed; Google Search ranking and traffic are not guaranteed.
- The **Google Indexing API is NOT for ordinary school articles** (limited to eligible job posting/live broadcast pages). Do not abuse it or use fake ping/indexing services.
- Paid ads, bought backlinks, mass low-quality AI articles and fake reviews are not part of this $0 strategy.
- AdSense shows **Getting ready** in the owner's latest screenshot, so no approval or earnings are claimed. Check that independently and observe child-directed ad policies before enabling ads.

Official references:
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://support.google.com/webmasters/answer/7451001
- https://support.google.com/blogger/answer/9691230
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
