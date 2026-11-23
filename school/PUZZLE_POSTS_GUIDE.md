# Sinhala Scholarship Puzzle Posters

Additional original Grade 5 logic puzzle stream for the existing Punchi Nena Maga Facebook Page and Blogger website.

## What it makes
- 1080 x 1350 original bright blue/purple infographic with Noto Sinhala text and four number-wheel illustrations.
- Three answer options and a natural comment invitation. The correct answer is not revealed in the Facebook image or caption.
- Blogger article with all numbers, a collapsible correct answer, worked calculations and teaching notes. Facebook caption links to the real Blogger article URL.
- Idempotent crossposting through school/crosspost.py, with READY/PENDING/PUBLISHED delivery receipts. Never retry uncertain Facebook sends blindly.
- Daily 18:30 Sri Lanka GitHub Actions scheduled run, with a manual preview mode.

## Maths validation
The daily generator rotates four original, deterministic rules for greater question variety: left x right x (top+1); (left+right) x (top+2); left x top + right x right; and (left+top) x right + top. The chosen rule and numerical derivation appear ONLY in the Blogger solution, never the Facebook image.
Launch question 29: (left,top,right,bottom) = (2,3,5,40), (4,2,3,36), (3,4,2,30), (5,3,4,?). Answer 80, which is option (2).
Other dates choose different original numeric wheel values and compute all solutions deterministically. The tests check 120 dates and poster output.

## Files
- Generator: school/puzzle_posts.py
- Workflow: .github/workflows/daily-scholarship-puzzle.yml
- Tests: school/test_puzzle_posts.py
- Outputs: school/output/logic-puzzle/puzzle-poster.png, quiz.json, caption.txt, blogger-preview.html

## Local and GitHub Actions usage
Preview: python school/puzzle_posts.py --date 2026-11-23
Offline tests: python -m unittest discover -s school -p test_puzzle_posts.py -v
Publish paired Facebook and Blogger: python school/puzzle_posts.py --publish
Required GitHub Actions secrets: FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN.
To disable publication explicitly, set BLOGGER_ALLOW_PUBLICATION=false.

Keep original educational value and realistic expectations: comments, referrals, organic traffic, AdSense approval and income are not guaranteed.
These are reasoning exercises, not official government examination questions. Parent or teacher review remains useful.

## Six different poster types, not repetitive number wheels (23 November 2026 upgrade)

Starting 2026-11-24, daily posts rotate through **six genuinely different puzzle types with matching original artwork**: increasing-difference number sequences, 3x3 magic number grids, circle/square equation problems, dot-array picture patterns, analogue clock time patterns, and number pyramids. Every day uses a different category from yesterday; bonus and on-demand posts choose an independent type for the same date. The new-format launch sample on 2026-11-23 is a dot-array picture puzzle, distinct from the archived wheel posts for #29 and #30.

Original content and six specialized layouts: `school/diverse_puzzles.py`. Integration into existing Blogger-first publishing: `school/puzzle_posts.py`. The paired Blogger article now carries a text-readable description of all relevant visual puzzle data, an answer hidden behind a disclosure control, and a worked explanation. This means someone can solve the quiz on the website even if the Facebook image itself has not been embedded.

All numeric answers are calculated by the generator, with 90-day tests verifying every type, each problem's logic, distinct same-day categories and original 1080x1350 poster output. The legacy 2026-11-23 wheel questions remain unchanged to prevent duplicate posting or altering published solutions. Code changes do not prove a successful GitHub Actions run or public Facebook/Blogger post; review run results.
