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
- [ ] Create the private repo `clwesterl/movie-months` (data + app).
- [ ] Single-file `index.html` skeleton (HTML/CSS/JS, no build step).
- [ ] GitHub Pages serving the app.
- [ ] Fine-grained PAT wired in; confirm authenticated read/write to the repo.
- [ ] Two-tab shell: **Marathon** and **Notebook** (empty for now).
- [ ] iPad-first layout that also holds up on desktop (see Users & devices).

## Milestone 1 — Storage layer
_The riskiest plumbing; build and test it before any feature sits on it._
- [ ] Read/write JSON via the GitHub Contents API.
- [ ] Marathon file schema (one file per month; optional theme; day entries
      with optional `dateWatched`).
- [ ] Notebook file schema (running list of short text entries).
- [ ] Handle the known gotchas from Two Spins (PAT scope, commit hygiene —
      no stray `.DS_Store`, sane commit messages).
- [ ] Graceful error handling on read/write failures.

## Milestone 2 — Wikidata lookup module
_Self-contained; reused by both Milestone 3 and Milestone 7._
- [ ] Search Wikidata by title → candidate list **with disambiguating
      descriptions** (e.g. "1972 film by Andrei Tarkovsky").
- [ ] On pick, resolve properties → year (P577), country (P495),
      director (P57), genre (P136), IMDb ID (P345).
- [ ] Build the `imdb.com/title/{imdb_id}/` link from P345.
- [ ] Test against ambiguous titles (e.g. *Solaris*) before wiring to UI.

## Milestone 3 — Marathon tab: live add-a-movie (MVP)
_A marathon can run on just this._
- [ ] "Add today's movie": type title → pick candidate → autopopulate fields.
- [ ] `dateWatched` defaults to today; **all fields editable** after populate.
- [ ] Save the entry into the current month's marathon file.
- [ ] Current-month list/calendar view that fills in as days are added.

## Milestone 4 — Notebook tab
_Small and independent; can land any time after Milestone 1._
- [ ] Running list of short entries, newest on top.
- [ ] Add an entry; tap to delete. Freeform, no categories.
- [ ] Persist to the notebook JSON file.

## Milestone 5 — Completed-months browsing
- [ ] **Completed-months dropdown** (required).
- [ ] Selecting a month loads that marathon for browsing.
- [ ] Entries without `dateWatched` fall back to sequence order.

## Milestone 6 — Search & filter
- [ ] Search + filter across all fields: title, year, country, director,
      genre, date watched.
- [ ] Build it **extensibly** — don't hard-code the filter set; new fields
      may be added later.

## Milestone 7 — Bulk import (backfill)  ⚠️ BLOCKED
**Blocked on a sample of the real past-months notes.** Do not finalize the
parser or let this milestone hold up Milestones 0–6.
- [ ] Paste a block of text for a past month.
- [ ] Forgiving parser extracts candidate titles (default: split on line
      breaks and commas; strip "Day N:" prefixes and parenthetical notes).
      **Tune to the actual sample before finalizing.**
- [ ] Each candidate runs through the Milestone 2 pick-and-autopopulate flow.
- [ ] Save resolved films into that month's marathon file (sequence order;
      `dateWatched` optional).

---

## Parked / later (not in scope now)
- **Poster / cover art.** Deferred. Would mean switching the data source from
  Wikidata to TMDb and taking on an API key. Revisit only if wanted.
