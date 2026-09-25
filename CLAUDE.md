# Movie Marathon Tracker — Project Context

## Overview
A web-based tracker for Nadia's monthly movie marathons: one movie per day
for a full month (28–31 days), usually organized around a theme. She adds
movies **as she goes** — this is not a pre-planned lineup — and the month's
list fills in behind her, day by day.

Not every month is a marathon. Films watched in ordinary months are logged
too, but kept separate: each month carries a **marathon toggle** (see Data
model), and marathons are grouped apart from ordinary months and counted
separately.

## Users & devices
- **Nadia — primary user.** Almost always **iPad + Safari**. Design targets
  her: touch-first, portrait-friendly, app-like (works well as an
  Add-to-Home-Screen web app).
- **Chad — full access too.** Same app, same dataset, full capabilities
  (add/edit/delete marathons, run the import, manage the notebook). Likely
  also accessed from **desktop**, so the layout shouldn't hard-assume iPad —
  it should hold up on a wider screen, even if the iPad is the priority.
- **No login, no accounts, no roles.** There's a single shared PAT (Chad's
  GitHub), so both people inherently have full access. "Full access for
  Chad" is a fact of the single-secret setup, not a permission system to
  build.

## Architecture
Same pattern as the Two Spins app (which is actually **two repos**:
public `two-spins` app + private `two-spins-data`, because GitHub Pages
can't serve a private repo on the free plan):
- Single-file HTML/CSS/JS. **No build step.**
- App lives in the **public** repo `clwesterl/movie-months`, hosted on
  **GitHub Pages**.
- Data stored as **JSON in a private repo** (`clwesterl/movie-months-data`),
  read/written via the **GitHub Contents API**.
- Auth via a **fine-grained PAT** (Contents read/write on the data repo).

## Layout — two tabs
1. **Marathon** — the current month. Primary action is *add today's movie*;
   the calendar/list fills in as the month progresses.
2. **Notebook** — a freeform, persistent space for ideas, not tied to any
   single marathon. Directors, decades, genres, countries, "been meaning to
   watch," loose thoughts. A running list of short entries, newest on top,
   tap to delete. **No forced categories or structure** — it's a scratchpad,
   not a filterable menu.

## Data model / storage
Two separate concerns, stored separately:

1. **Marathons** — one JSON file per month (so past months are browsable).
   Each marathon holds an optional theme, its month/start date, a
   `marathon` flag, and a list of day entries.

   `marathon` is **true unless explicitly false**, so month files written
   before the toggle existed (and any month not yet loaded) read as
   marathons — no migration was needed. New months default to marathon;
   untick *Marathon month* to make one an ordinary viewing log. An ordinary
   month drops the "N days / today is day X" framing, which only means
   something when the goal is a film a day. Each day entry is a movie she added that day:
   - `dateWatched` (live entries default to today; **optional** for
     backfilled entries — falls back to sequence order. Editable.)
   - `title`, `year`, `country`, `director`, `genre`
   - `format` — how it was watched: Streaming / DVD / Theater (dropdown,
     optional; not sourced from Wikidata, she sets it per film)
   - `watchType` — New / Rewatch (dropdown, optional; also not from
     Wikidata). Single adds default to **New**; bulk-imported entries are
     left blank. Only *Rewatch* is shown in the list row — "New" is the
     common case and would just be noise.
   - `imdbId` / IMDb link

   Deleting the **last movie** in a month prompts whether to delete the
   whole month file too (theme included); declining keeps an empty month.

2. **Notebook** — its own JSON file, persists across all marathons. A simple
   list of short text entries.

## Movie data source — Wikidata
Lookup and autopopulation use **Wikidata**.

Note: IMDb has **no usable public API** (the official one is enterprise-priced,
and imdb.com can't be scraped from a client-side app due to CORS). "IMDb data"
therefore comes via a proxy. Wikidata is chosen because it is **keyless,
CORS-enabled, and CC0** — no API key, no signup, no daily cap to manage — and
its structured properties supply every required field, including the IMDb ID
for the link:

- P577 publication date → **year**
- P495 country of origin → **country**
- P57 director → **director**
- P136 genre → **genre** (multi-valued and uses Wikidata's own ontology, so it
  can be patchy — e.g. "psychological thriller" vs. "film based on a novel";
  fine since fields are editable)
- P345 IMDb ID → build `imdb.com/title/{imdb_id}/` link

Resolving P57/P495/P136 means following entity IDs to their labels — a little
more client-side work than a flat JSON API, but no key to manage.

### Lookup flow (avoids blind best-match)
A cinephile's library is full of ambiguous titles (e.g. *Solaris* — Tarkovsky
'72 vs. Soderbergh '02), so never auto-resolve by title alone:
1. She types a title → app queries Wikidata search.
2. App shows candidate results with disambiguating descriptions (e.g. "1972
   film by Andrei Tarkovsky") so she can pick the right one.
3. She taps the right one → app resolves the properties above and
   autopopulates all fields.
4. **All fields remain editable** after autopopulate (in case data is thin
   or wrong).

### Posters (deferred)
Cover art is **out of scope for now** (see Non-goals). If it's ever wanted,
Wikidata is a poor poster source (inconsistent, and real posters are usually
copyright-blocked on Commons); the moment to revisit is a switch to **TMDb**,
which has excellent poster coverage but reintroduces an API key.

## Canon lists — 1001 Movies & Sight & Sound 250
Films carry two tick marks next to the title when they appear on a canon list:
- **Green ✓** — on the *1001 Movies You Must See Before You Die* list (the
  fandom wiki's full cross-edition list, 1245 entries).
- **Red ✓** — in the *Sight & Sound* 2022 critics' poll (264 films; ties
  share a rank). Its **rank** is a hover tooltip on desktop, and tapping the
  red tick toasts it — the iPad has no hover, so a tooltip alone would be
  invisible to the primary user.

Both lists are **embedded in `index.html`** as normalised title → year
indexes (~46KB) and matched **at render time**, deliberately *not* stored as
flags on each entry. That means every existing film is covered with no data
migration, and anything added later ticks itself with no extra step.

**Filtering by list:** three checkboxes under the search bar — *1001 Movies*,
*Sight & Sound*, *Both*. They behave as one filter, not three independent
ones: ticking one clears the others, and ticking the active one clears the
filter. (Two independent boxes could express the same three states, but a
box literally labelled "Both" alongside them would be ambiguous.) The filter
stacks with everything else — the month/all-months scope and any typed
search both still apply.

Matching notes:
- Key on normalised title (diacritics, punctuation, articles and part
  numbers folded) **plus year within ±1** — sources disagree on release years
  (*Black Narcissus* 1946 vs 1947, *Beau Travail* 1998 vs 1999).
- A year is **required** to match, so a film with a blank year never ticks —
  better than guessing on title alone, where *The Magnificent Seven* and
  *The Magnificent Ambersons* are one fuzzy step apart.
- The 1001 list's own **alternate titles are indexed** (331 of them), which
  is what catches *Yi Yi* → "A One and a Two", *Ikiru* → "To Live".
- `EXTRA` in `tools/build-canon-lists.py` holds hand-added aliases for the
  rest; so far only *Ugetsu* → "Tales of Ugetsu". Add to it if a film that
  should tick doesn't, then re-run the script — it rewrites the two index
  lines in `index.html` in place. The source lists live in `tools/` beside
  it, so the embedded blob is always reproducible.

## Search & filter
- All movie data is searchable and filterable across every field:
  title, year, country, director, genre, format, watch type, date watched.
- **Type-ahead (prefix) matching, not substring:** each typed term must start
  a *word* somewhere in the searched fields, so "r" → Rashomon / The Red
  Shoes / Mamma Roma, and "ra" narrows it. Word-start rather than
  field-start, so a leading "The" doesn't hide a title. Multiple terms all
  have to match and may land in different fields ("kur ik" → Ikiru).
- **Filtering should be extensible** — new fields may be added later, so don't
  hard-code the filter set.

## Historical data & browsing past months
- A **completed-months dropdown is required** — Nadia will backfill past
  marathons, and will want to browse back through them.
- Selecting a month loads that marathon for browsing.
- **Marathons and ordinary months are grouped separately** in the dropdown
  (`Marathons` / `Other months`), and the summary line counts them apart —
  "3 movies · 184 in marathons · 187 all time". Both the grouping and the
  split total only appear once a mix actually exists, so nothing changes
  until the first ordinary month is created.
- **Past months with no films are hidden from the dropdown** — a marathon
  that never happened is clutter. The current month always shows (it's where
  today's film goes), as does the month currently open, and a month whose
  file hasn't loaded yet is never hidden on a guess.
- Backfill happens through **"＋ Start another month…"** in the dropdown:
  open any earlier month and add movies **one at a time** through the same
  lookup flow as live entry.

### Historical backfill — done once, by script (July 2026)
The past marathons lived in an Excel file (`movie list history.xlsx`, four
month tabs plus a wishlist). Rather than a paste-and-resolve UI, they were
resolved **once** by a throwaway script and written straight to the data
repo: March 2024, June 2025, November 2025, February 2026 — 124 films, 120
auto-matched against Wikidata. The four unmatched films were saved with
their spreadsheet title and director so they're visible and fixable in-app.

The in-app bulk importer that previously existed **was removed**: it filed
every batch under the wrong month (see Gotchas), and with the backfill done
there's no remaining need for it. Recover it from git history if a second
bulk import ever comes up.

August 2024 was added later, by hand through the normal add flow, and the
few films Wikidata couldn't match were corrected in-app. The spreadsheet's
**wishlist tab is deliberately not imported** — decided, not pending.

Matching notes worth keeping, if a similar import is ever needed: the sheet's
**director column is the key disambiguator** (title alone is hopeless for
short or duplicated titles), Wikidata's fuzzy search operator (`term~`)
absorbs spelling slips in the source list, and film titles must be scored
against **aliases** as well as labels (Wikidata's English label for *El Sur*
is "The South").

### Gotchas hit in practice (don't re-learn these)
- **Safari has no `<input type="month">`.** It silently degrades to a text
  box, so a prefilled default gets submitted as-is — this is what made every
  bulk import land in one wrong month. Use month + year `<select>`s instead.
- **Wikidata statement ranks matter.** Deprecated statements (e.g. a
  cancelled release date) must be filtered out or *Dune: Part Two* resolves
  to 2023; a `preferred` statement wins when present.
- **Many person items have no English label**, only a multilingual (`mul`)
  one — an en-only lookup silently yields a raw Q-id in the Director field.
  Always request `en|mul` and fall back.

### Dates for historical entries
- Past months likely have **no reliable per-day dates** — and for a completed
  marathon that's fine; the value is the list + theme under that month.
- So `dateWatched` is **optional**; when absent, entries fall back to
  **sequence order** (order pasted / resolved). Live entries still default
  `dateWatched` to today.

## Secrets / config
- **GitHub fine-grained PAT** — Contents read/write, scoped to
  `movie-months-data` only — same as Two Spins.
- **No movie-API key needed** — Wikidata is keyless. The PAT is the only
  secret to manage on the iPad.

## Non-goals
- No per-user accounts, login, or permission roles. The app is shared
  between Nadia and Chad and unauthenticated behind the single PAT — that's
  intentional, not a feature gap.
- No pre-planned monthly lineups (day-by-day only).
- No structured/categorized notebook — freeform by design.
- No streaming-service integration or availability lookups.
- No cover art / poster thumbnails for now (deferred; would mean switching
  the data source to TMDb and taking on an API key).

## Open questions
- **Filter extensibility.** A lightweight tag/field system vs. just adding
  columns as needs arise — currently leaning add-as-needed to avoid
  over-engineering.
