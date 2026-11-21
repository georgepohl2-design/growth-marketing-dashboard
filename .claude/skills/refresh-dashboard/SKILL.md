---
name: refresh-dashboard
description: Refresh the B2B Growth Marketing Dashboard with the latest numbers. Use when the user says "refresh the dashboard", "update the numbers", or when the scheduled morning run fires. Pulls fresh data from connectors or inbox/ exports, rebuilds b2b/data.js safely, checks it, and reports what moved.
---

# Refresh the dashboard

Runs unattended on a schedule, so be safe and quiet: never leave a broken `data.js`, and never ask questions mid-run. If something is missing, keep the old values and say so in the summary.

1. **Read `dashboard.config.json`.** If it doesn't exist, stop and suggest running `setup-dashboard` first.
2. **Pull fresh data.**
   - For each source marked `"connector"`, pull from 1 January to yesterday using the connector tools available in this session, and save the result into `inbox/` under the file name in the config.
   - For each source marked `"csv"`, use the newest matching file in `inbox/`. If it is older than the last refresh, note that the source is stale.
   - If a connector fails (expired login, no access), don't stop the run. Keep that source's previous values and flag it.
3. **Build.** Run `python3 scripts/build_data.py`. It writes to a temporary file, checks it with `scripts/check_data.py`, backs up the current `b2b/data.js` to `b2b/backups/`, and replaces it. If the check fails, leave the current `data.js` untouched and report the error.
4. **Tidy.** Keep the newest 14 files in `b2b/backups/` and delete older ones.
5. **Report**, in 3–5 lines a marketer can read on their phone:
   - period covered ("data to Tue 24 Sep");
   - this month vs target: MQLs, meetings, SQLs, pipeline, with ↑/↓ vs yesterday's version;
   - any card that went red or green since the last refresh;
   - anything stale or missing, and the one action that would fix it.

Don't commit or push as part of a scheduled run unless the user asked for that during setup, and never to a public repo once `data.js` holds real data.
