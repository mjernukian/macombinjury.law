# macombinjury.law

Static site. No build step. No dependencies. No server.

This is a scaffold: the structure is in place and every piece of content is a
`[BRACKETED]` placeholder (highlighted on the page with a dashed underline).

## Files

- `index.html`: main page (hero, experience, results, answers, practice areas,
  for attorneys, reviews, contact)
- `es/index.html`, `ar/index.html`: Spanish and Arabic home pages, GENERATED from
  `index.html` by `python3 tools/build-translations.py` (all translations live in
  that script). After any change to the English home page, run it again.
- `llm-info/index.html`: AI & LLM fact sheet, the first-party facts page for
  AI assistants and search engines
- `llms.txt`: plain-text summary for LLMs
- `answers/index.html`: list of articles
- `_templates/answer.html`: template for a new article (not public)
- `assets/site.css`: all styles; palette tokens in `:root` come from the MJ logo
- `assets/site.js`: header shadow, scroll reveals, footer year
- `assets/img/`: logo assets (green and cream monogram, full lockup, share image)
- `fonts/`: self-hosted Playfair Display (headings) and Montserrat (body)
- `netlify.toml`, `_redirects`, `robots.txt`, `sitemap.xml`: hosting and crawler config

## Deploy (Netlify)

1. app.netlify.com -> Add new site -> Import an existing project -> GitHub
2. Select `mjernukian/macombinjury.law`, branch `main`
   - Build command: (none)
   - Publish directory: `.`
3. Review on the generated netlify.app preview URL
4. Domain management -> add `macombinjury.law` as the primary domain
   (`www` redirects to the bare domain via `_redirects`)
5. Set DNS at the registrar per Netlify's instructions; SSL is automatic

Every push to `main` deploys automatically.

## "Do I have a case?" leads (Netlify Forms)

The four-question intake on the home page (`#intake`, logic in `assets/site.js`)
posts only when a visitor leaves a phone number. Submissions go to the Netlify
form named `case-check`.

1. Netlify -> Project configuration -> Forms: make sure form detection is on.
2. Forms -> Form notifications -> Add notification -> Email notification ->
   form `case-check` -> Michael's email.
3. Submissions also appear under the project's Forms tab.

## Launch checklist

1. Replace every `[BRACKETED]` placeholder. Find them with `grep -rn '\[' --include=*.html --include=*.txt .`
2. Remove the `ph` highlight spans once the content is real.
3. Delete the `X-Robots-Tag = "noindex, nofollow"` line in `netlify.toml`.
   Until then, search engines are told not to index the site.
4. Headshot lives at `assets/img/michael-640/960` (WebP + JPEG); replace both sizes to change it.
5. Confirm every result, review, and claim complies with the Michigan Rules of
   Professional Conduct (MRPC 7.1). The compliance footer stays on every page.
