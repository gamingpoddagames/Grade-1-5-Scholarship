# Sinhala Scholarship Puzzle Posters

Additional original Grade 5 logic puzzle stream for the existing Punchi Nena Maga Facebook Page and Blogger website.

## What it makes
- 1080 x 1350 original bright blue/purple infographic with Noto Sinhala text and four number-wheel illustrations.
- Three answer options and a natural comment invitation. The correct answer is not revealed in the Facebook image or caption.
- Blogger article with all numbers, a collapsible correct answer, worked calculations and teaching notes. Facebook caption links to the real Blogger article URL.
- Idempotent crossposting through school/crosspost.py, with READY/PENDING/PUBLISHED delivery receipts. Never retry uncertain Facebook sends blindly.
- Daily 18:30 Sri Lanka GitHub Actions scheduled run, with a manual preview mode.

## Maths validation
Each number wheel uses the explicitly stated intended rule: bottom = left x right x (top + 1).
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
