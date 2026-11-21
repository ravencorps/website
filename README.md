# Raven Corps website

One static page for ravencorps.co.uk. No build step: Vercel serves the files as they are.

- `index.html`: the page
- `assets/`: logo, favicon and the image shown when the link is shared
- `fonts/`: self-hosted Barlow, Barlow Condensed and IBM Plex Mono (SIL Open Font Licence)

## Turning on the sign-up form

Near the bottom of `index.html`, set `FORM_URL` to the Google Form link:

```js
var FORM_URL = "https://forms.gle/your-form-id";
```

Until it is set, every "Sign up" button opens an email to hq@ravencorps.co.uk.

## Meetup dates

The page works out the next meetup itself: the third Saturday of each month. The first one is Saturday 23 January 2027, the fourth Saturday, because January 2027 has five. That exception is `meetupDay()` in `index.html`.
