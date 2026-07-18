# Movie Months

A tracker for monthly movie marathons — one movie per day for a full month,
usually organized around a theme.

Single-file web app (`index.html`), no build step, hosted on GitHub Pages.
Marathon and notebook data live as JSON in a separate **private** repo
(`movie-months-data`), read and written from the browser via the GitHub
Contents API with a shared fine-grained token. Movie lookup and
autopopulation come from Wikidata (keyless, CORS-enabled, CC0).

See `CLAUDE.md` for the full spec and `TASKS.md` for the build sequence.
