# B2B Growth Marketing Dashboard: notes for Claude

This folder is a one-page marketing dashboard for B2B acquisition teams. The person working with you is probably a marketer, not a developer. Explain what you are about to do in plain English before you do it, and show them the result in the browser rather than describing code.

## How the project fits together

- `b2b/index.html` draws the dashboard. **Do not edit it to change numbers.** Only edit it when the user asks for a layout or wording change.
- `b2b/data.js` holds every number, name and setting the dashboard shows. Refreshing the dashboard means rewriting this file. The comment at its top lists each block.
- `scripts/check_data.py` checks `data.js` has the shape the page expects. **Run it after every change to `data.js`**, and never leave the user with a file that fails it.
- `dashboard.config.json` (created during setup from `dashboard.config.example.json`) records the user's sources, targets, brand terms, card choices and refresh schedule.
- `scripts/build_data.py` (created during setup, tailored to the user's sources) turns the latest exports in `inbox/` into a new `data.js`.
- `inbox/` is where CSV exports and connector pulls land before they are processed.

## Skills in this project

- **setup-dashboard**: first-time setup. Use it when the user says "set up my dashboard", "connect my CRM", "use my own data" or similar.
- **refresh-dashboard**: pulls fresh numbers and rebuilds `data.js`. Use it when the user says "refresh the dashboard", and for the scheduled morning run.

## Rules

1. **Keep the data shapes exactly as they are.** The page reads blocks by name and position (see the field guide in `.claude/skills/setup-dashboard/SKILL.md`). Change the values, not the structure.
2. **Back up before you overwrite.** Copy `b2b/data.js` to `b2b/backups/data-YYYY-MM-DD.js` before every rewrite, and keep the last 14 backups.
3. **Real data stays private.** The sample data is fictional. Once `data.js` holds the user's real numbers, check `git remote -v` and the repo's visibility before any commit or push. If the repo is public, stop and warn the user. Suggest a private repo, or keep real data out of git with `.gitignore`.
4. **Never put secrets in files.** API keys and tokens go in the user's connector settings or environment variables, never in `data.js`, the config or a commit.
5. **Ask before anything outward-facing:** pushing, publishing, scheduling, or sending a message.
6. **Say what you could not fill.** If a source isn't connected and there is no export for it, keep the previous values, mark the card stale (`P.<period>.<field> = null` greys it out), and tell the user which export would fix it.
