# Raven Corps website

The static site for ravencorps.co.uk. Vercel serves the files at the top of this repo as they are; there's no build step on Vercel. The pages are generated from `source/` by a small Python script, and both the source and the generated pages are committed.

- `index.html`, `meetups/`, `skills/`, `start-a-chapter/`, `faq/`, `about/`: generated pages (don't edit these by hand)
- `sitemap.xml`, `robots.txt`, `llms.txt`, `vercel.json`: also generated
- `source/`: the page source, the stylesheet and `build.py` (kept off the live site by `.vercelignore`)
- `assets/`: logo, favicon and the image shown when a link is shared
- `fonts/`: self-hosted Barlow, Barlow Condensed and IBM Plex Mono (SIL Open Font Licence)

## Editing a page

1. Edit the page in `source/pages/` (for example `source/pages/skills/grid-references.html`), or `source/style.css`.
2. Run `python3 source/build.py` (Python 3, no packages needed).
3. Commit the source and the regenerated pages together, and push. Vercel deploys `main`.

Each page file starts with a meta block, then the page's `<main>`:

```
<!--meta
{"path": "/skills/grid-references/", "type": "guide",
 "title": "...", "description": "...", "h1": "...",
 "crumbs": [["Home", "/"], ["Skills guides", "/skills/"], ["Grid references", "/skills/grid-references/"]],
 "steps": [["Step name", "Step text"]],
 "faq": [["Question?", "Answer."]],
 "sources": [["Source name", "https://..."]]}
meta-->
<main id="top"> ... {{crumbs}} ... {{steps}} ... {{faq}} ... {{cta}} ... {{sources}} ... </main>
```

- `type` is `home`, `page` or `guide`. Guides become an Article in the structured data, and a HowTo when they have `steps`.
- `{{crumbs}}`, `{{steps}}`, `{{faq}}`, `{{sources}}` and `{{cta}}` are filled in from the meta block. The build stops with an error if one is left unfilled.
- `faq` also becomes FAQPage structured data, and `event` (on the meetups page) becomes an Event.
- `title` is the browser tab and search result title; `description` is the search snippet and the summary in `llms.txt`, so make it answer the question in a sentence or two.

To add a page, add a file under `source/pages/` and, if it should be in the menu, add it to `NAV` in `build.py`. New skills guides also need a card on `source/pages/skills.html`. Change `UPDATED` in `build.py` and the "Last updated" line on a guide when you revise it.

## Sign-up form

The home page's sign-up section embeds the HubSpot form "Raven Corps: get involved" (portal 149830763, EU region, form 678d493f-c9ae-4455-b22c-08f94b976ea2). Every "Sign up" button goes to `/#signup`. If the HubSpot script doesn't load, a link to the form's share page shows underneath. Edit the form's fields and wording in HubSpot, not here.

## Meetup dates

The home page works out the next meetup itself: the third Saturday of each month. The first one is Saturday 23 January 2027, the fourth Saturday, because January 2027 has five. That exception is `meetupDay()` in `source/pages/home.html`. The meetups page lists the dates written into `source/pages/meetups.html` and hides any that have passed, so add new dates there.
