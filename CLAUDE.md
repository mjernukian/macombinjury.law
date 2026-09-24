# macombinjury.law

Michael Jernukian's personal site. He is a trial attorney at Morgan & Morgan's
Detroit office; this is not an official Morgan & Morgan site. Static HTML/CSS/JS,
no build step, hosted on Netlify. Every push to `main` goes live.

## The site is in three languages. Every change goes into all three.

| Language | Page | How it is made |
|---|---|---|
| English | `index.html` | Edited by hand. The source of truth. |
| Spanish | `es/index.html` | Generated. Do not edit directly. |
| Arabic (right-to-left) | `ar/index.html` | Generated. Do not edit directly. |

When you add or change anything a visitor can read on the home page:

1. Make the change in English in `index.html`.
2. Add the Spanish and Arabic versions of every new or changed line to
   `tools/build-translations.py` (the `ES` and `AR` `pairs`, plus the `i18n`
   blocks for text that lives in `assets/site.js`). Write the translations
   yourself; do not leave English in the translated pages.
3. Run `python3 tools/build-translations.py`. It stops and names any English
   line it can no longer find. Fix the pair and run it again until it writes
   both files.
4. Text inside `assets/site.js` (the "Do I have a case?" intake and the
   Ask-an-AI returning-visitor text) comes from the `EN` object there, and the
   `ES`/`AR` `i18n` objects in the build script. Change all three together.
5. Check the Arabic page in a browser: it is `dir="rtl"`. Wrap phone numbers,
   emails, addresses and dollar figures in `<bdi dir="ltr">…</bdi>`. Never add
   letter-spacing, uppercase or italics to Arabic text (the CSS already
   disables them under `html[lang="ar"]`). Anything using `left`/`right`
   needs an `[dir="rtl"]` override in `assets/site.css`.
6. New pages (for example an article under `/answers/`) need Spanish and
   Arabic versions too, `hreflang` links between all three, and entries in
   `sitemap.xml`. Ask the user before publishing a page in only one language.

Leads from the intake always reach Michael in English, tagged with the page
language. Keep it that way.

## Before every push

- Bump the `?v=` number on `site.css` / `site.js` in every HTML file that
  loads them (including `_templates/answer.html`), then rerun the build
  script. Browsers otherwise keep the old file.
- Check at phone and desktop widths (320px to 1440px) in all three
  languages. No page may scroll sideways.

## Content rules

- Every page keeps the attorney-advertising disclaimer in the footer and says
  Michael is an attorney at Morgan & Morgan and that this is his personal site.
- Only publish facts about Michael that the user or Michael has confirmed.
  Michigan Rules of Professional Conduct 7.1 applies to every claim, result
  and review. Use "focuses on", never "specializes".
- Callers are told to ask for **MJ**. Keep that next to the phone number
  wherever it appears. Do not add a pronunciation guide or an Arabic-script
  spelling of his name unless Michael supplies it.
- Do not claim Spanish- or Arabic-speaking staff unless the user confirms it.
- Voice: short, plain sentences. No em dashes. "Collision" in body copy,
  "accident" only in titles, headings and search text where people type it.
- The Results, Answers and Reviews sections are intentionally small or hidden
  until Michael has real content. `/answers/` redirects home until then
  (`_redirects`).
- `netlify.toml` sends `X-Robots-Tag: noindex` until launch. Remove it only
  when the user says to.

## Other files

- `llm-info/index.html` and `llms.txt`: first-party facts for AI assistants
  (English only). Update them when facts on the site change.
- Netlify form `case-check` receives intake leads. The hidden form lives in
  `index.html`; do not rename it.
- `README.md`: deploy steps and launch checklist.
