# පුංචි නැණ මඟ — Blogger Visual Refresh

The Blogger website https://punchinanamaga.blogspot.com/ uses a separate **Blogger XML theme**, not the HTML/CSS from the GitHub Pages site.

## Planned design
- Match the GitHub Pages site's blue/teal color palette, the actual `assets/school-hero-hd.webp` artwork, logo and rounded learning cards.
- Responsive navigation and grade 1–5 resource shortcuts that **stay on Blogger** (homepage anchors and Blogger grade-label archives), instead of navigating to the GitHub website.
- Preserve Blogger's `Blog1` and `PageList1` widgets for blog posts and page navigation.
- PDF assets, Grade 5 interactive quiz iframe and narrated video may load from the existing GitHub Pages resource hosting, but the main address and navigation remain on Blogger. No third-party ad scripts, analytics, or child data collection added.

## Applying a custom theme (one-time owner action)
This cannot be applied through the Blogger v3 Posts/Pages publishing API. Blogger dashboard ownership is required.

1. In Blogger dashboard **Theme**, click the arrow next to **Customize**, then **Backup** and save the existing theme.
2. Then **Restore**, and upload the custom `punchi-nena-maga-theme-v2.xml` file supplied in this ChatGPT conversation.
3. Inspect homepage and post/page navigation on mobile and desktop. If it doesn't render correctly, restore the backup.
4. In **Layout**, configure the `PageList` widget to show the About, Contact, Privacy and Terms pages. Those pages are already published.
5. Keep ads disabled until Google AdSense approval and appropriate child-privacy compliance settings are verified.

Official Blogger reference: https://support.google.com/blogger/answer/1227173

Note: GitHub Actions automates **content** via Blogger API but does not modify Blogger's theme. The XML file must be restored in Blogger by an authorized session.
