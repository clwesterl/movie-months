# Movie Months

A tracker for monthly movie marathons — one movie per day for a full month,
usually organized around a theme.

- Add today's movie via Wikidata lookup (pick the right match, fields
  autopopulate, everything stays editable) — including how it was watched
  (streaming / DVD / theater) and whether it's a new watch or a rewatch.
- Backfill earlier months two ways: paste-and-resolve bulk import, or
  "Start another month" to add films one at a time.
- Browse completed months from the dropdown; search and filter across
  every field, in one month or all of them.
- Freeform notebook for ideas, not tied to any month.
- Removing a month's last movie offers to delete the whole month.

Single-file web app (`index.html`), no build step, hosted on GitHub Pages.
Marathon and notebook data live as JSON in a separate **private** repo
(`movie-months-data`), read and written from the browser via the GitHub
Contents API with a shared fine-grained token. Movie lookup and
autopopulation come from Wikidata (keyless, CORS-enabled, CC0).

See `CLAUDE.md` for the full spec and `TASKS.md` for the build sequence.
