# Raven Corps website

One static page for ravencorps.co.uk. No build step: Vercel serves the files as they are.

- `index.html`: the page
- `assets/`: logo, favicon and the image shown when the link is shared
- `fonts/`: self-hosted Barlow, Barlow Condensed and IBM Plex Mono (SIL Open Font Licence)

## Sign-up form

The sign-up section embeds the HubSpot form "Raven Corps: get involved" (portal 149830763, EU region, form 678d493f-c9ae-4455-b22c-08f94b976ea2). The "Sign up" buttons jump to it (`FORM_URL = "#signup"`). If the HubSpot script doesn't load, a link to the form's share page is shown underneath. Edit the form's fields and wording in HubSpot, not here.

## Meetup dates

The page works out the next meetup itself: the third Saturday of each month. The first one is Saturday 23 January 2027, the fourth Saturday, because January 2027 has five. That exception is `meetupDay()` in `index.html`.
