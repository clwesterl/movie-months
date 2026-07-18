# Movie Marathon Tracker — Build Sequence

Companion to `CLAUDE.md` (the spec and the reasoning behind each decision).
This file is the **order of operations**. Work top-down; each milestone
depends on the ones above it. Check items off as they land.

**Ordering logic:** scaffolding and storage before any feature UI (don't build
screens against storage that doesn't exist yet) → the Wikidata lookup module
next, since both live-add and the importer reuse it → the core add-a-movie
loop (the MVP a marathon can actually run on) → secondary features → the bulk
importer **last**, because it's blocked on a real notes sample.

---

## Milestone 0 — Scaffolding & deploy
- [x] Repos created — split like Two Spins, since Pages can't serve a private
      repo on the free plan: **public** `clwesterl/movie-months` (app) +
      **private** `clwesterl/movie-months-data` (data). CLAUDE.md updated.
- [x] Single-file `index.html` skeleton (HTML/CSS/JS, no build step).
- [x] GitHub Pages serving the app → https://clwesterl.github.io/movie-months/
- [ ] Fine-grained PAT wired in; confirm authenticated read/write to the repo.
      _App side done (settings ⚙ stores the token; Contents read/write on the
      data repo confirmed via API). Remaining: create the fine-grained token
      (Contents read/write, only `movie-months-data`) and paste it into ⚙ on
      each device._
- [x] Two-tab shell: **Marathon** and **Notebook**.
- [x] iPad-first layout that also holds up on desktop (see Users & devices).

## Milestone 1 — Storage layer
_The riskiest plumbing; build and test it before any feature sits on it._
- [x] Read/write JSON via the GitHub Contents API (sha-tracked; refetch-once
      on write conflicts).
- [x] Marathon file schema (`marathons/YYYY-MM.json`; optional theme; day
      entries with optional `dateWatched`).
- [x] Notebook file schema (`notebook.json`, running list of short entries).
- [x] Handle the known gotchas from Two Spins (PAT scope, commit hygiene —
      `.DS_Store` gitignored, per-action commit messages, pretty-printed JSON).
- [x] Graceful error handling on read/write failures (auth vs. missing-repo
      vs. offline get distinct messages; toasts elsewhere).

## Milestone 2 — Wikidata lookup module
_Self-contained; reused by both Milestone 3 and Milestone 7._
- [x] Search Wikidata by title → candidate list **with disambiguating
      descriptions** (film-described results float to the top).
- [x] On pick, resolve properties → year (P577, earliest), country (P495),
      director (P57), genre (P136), IMDb ID (P345); entity IDs → EN labels.
- [x] Build the `imdb.com/title/{imdb_id}/` link from P345.
- [x] Test against ambiguous titles — *Solaris* returns Tarkovsky '72 and
      Soderbergh '02 as the top two candidates; '72 resolves fully.

## Milestone 3 — Marathon tab: live add-a-movie (MVP)
_A marathon can run on just this._
- [x] "Add today's movie": type title → pick candidate → autopopulate fields
      (plus a manual-entry escape hatch when Wikidata has nothing).
- [x] `dateWatched` defaults to today; **all fields editable** after populate.
- [x] Save the entry into the current month's marathon file.
- [x] Current-month list view with day numbers that fills in as days are
      added; tap an entry to edit or delete it.

## Milestone 4 — Notebook tab
_Small and independent; can land any time after Milestone 1._
- [x] Running list of short entries, newest on top.
- [x] Add an entry; tap to delete (with confirm). Freeform, no categories.
- [x] Persist to the notebook JSON file.

## Milestone 5 — Completed-months browsing
- [x] **Completed-months dropdown** (from the `marathons/` directory listing;
      current month always present).
- [x] Selecting a month loads that marathon for browsing (and editing).
- [x] Entries without `dateWatched` fall back to sequence order for their
      day number.

## Milestone 6 — Search & filter
- [x] Search + filter across all fields: title, year, country, director,
      genre, date watched. Scope: this month or **all months** (grouped hits).
- [x] Built **extensibly** — one `FIELDS` config array drives the form, the
      field-scope dropdown, and matching; add a field there and it's wired.

## Milestone 7 — Bulk import (backfill)  ⚠️ parser not final
Built with the **default** rules; still needs tuning against a sample of the
real past-months notes before it's trusted.
- [x] Paste a block of text for a past month (month + optional theme).
- [ ] Forgiving parser extracts candidate titles — default rules implemented
      (split on line breaks and commas; strip "Day N:"/numbered/bulleted
      prefixes and (parenthetical)/[bracketed] notes).
      **Remaining: tune to the actual sample before finalizing.**
- [x] Each candidate runs through the Milestone 2 pick-and-autopopulate flow
      (per-title Find/Redo/Skip in a review list; nothing saves unconfirmed).
- [x] Save resolved films into that month's marathon file (sequence order;
      no `dateWatched`).

---

## Parked / later (not in scope now)
- **Poster / cover art.** Deferred. Would mean switching the data source from
  Wikidata to TMDb and taking on an API key. Revisit only if wanted.
