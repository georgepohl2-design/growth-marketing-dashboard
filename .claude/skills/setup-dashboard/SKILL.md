---
name: setup-dashboard
description: First-time setup of the B2B Growth Marketing Dashboard with the user's own data. Use when the user says "set up my dashboard", "connect my CRM / GA4 / Search Console", "use my own numbers", or opens this project for the first time and asks what to do. Walks a non-technical marketer through connecting sources, customising the cards, building the first real version, and scheduling a daily morning refresh.
---

# Set up the dashboard

You are helping a marketer swap the fictional sample data for their own and keep it fresh. Go one step at a time, in plain English. After each step, say what you did and what's next. Don't dump code on them. Show them the dashboard in the browser.

## Step 1: Get to know their setup (ask, don't assume)

Ask a few short questions, all at once if your interface supports it:

1. **Company and currency.** Name (for the page title, optional) and currency (£ / $ / €).
2. **CRM.** HubSpot, Salesforce, Pipedrive, or something else? What do they call an MQL and an SQL (lifecycle stage, a property, a list)?
3. **Channels to show.** The channel cards ship as placeholders: Channel 1 (e.g. paid media · Google Ads), Channel 2 (e.g. search & AI), Channel 3 (e.g. Reddit or Spotify Ads), Channel 4 (e.g. report downloads), Channel 5 (e.g. events). Ask what their five channels really are, then set each card's `title` and clear its `hint`. Which do they run? Which should be renamed or hidden?
4. **Targets.** MQLs per month, meetings per month, the share of MQLs that should become SQLs, demo requests per month, and the North Star goal (pipeline generated from MQLs per month, e.g. £475K).
5. **Brand terms.** Words that mean someone searched their brand (used to split branded vs non-branded Search Console clicks).
6. **Refresh.** Would they like it refreshed automatically each morning? What time, and weekdays only or every day?

Copy `dashboard.config.example.json` to `dashboard.config.json` and fill it in with their answers.

## Step 2: Connect each source

For each source, first check whether **a connector for it is available in this Claude session** (look at your available tools/MCP servers, e.g. HubSpot, Google Analytics, Search Console, LinkedIn). Then:

- **Connector available:** confirm with the user which account or property to use. Do a small test pull (last 7 days) and show them a one-line summary ("found 41 MQLs and 6 meetings last week") so they can sanity-check it.
- **No connector:** tell them their two options:
  1. Add one in Claude's connector settings, if one exists for that tool, then restart this step.
  2. Use exports: give them the exact steps below, and ask them to save each CSV into `inbox/` with the name shown.

| Source | Export steps | Save as |
|---|---|---|
| CRM contacts | Contacts filtered to anyone who became an MQL or SQL this year. Include: record ID, name, company, job title, MQL date, SQL date, first conversion, recent conversion, latest traffic source. | `inbox/crm-contacts.csv` |
| CRM meetings | Meeting activities this year with date, outcome, and the associated contact's record ID. | `inbox/crm-meetings.csv` |
| CRM deals | Deals this year with record ID, name, amount, create date, associated contact. | `inbox/crm-deals.csv` |
| CRM attribution | HubSpot: Reports → Attribution → Contact create attribution, model U-shaped, grouped by campaign. | `inbox/crm-attribution.csv` |
| Google Analytics 4 | Reports → Acquisition → Traffic acquisition, daily, Session source dimension, this year. | `inbox/ga4-traffic.csv` |
| Search Console | Performance → Search results → Dates tab, plus Queries tab, this year. | `inbox/gsc-dates.csv`, `inbox/gsc-queries.csv` |
| Ad platform (Google Ads, LinkedIn, Meta, Reddit, Spotify…) | The platform's campaign performance report, daily, with lead-form columns (LinkedIn: Campaign Manager → Analyze; Google Ads: Campaigns → Download). | `inbox/ads.csv` |

Record in `dashboard.config.json` which route each source uses (`"connector"` or `"csv"`).

## Step 3: Write the build script

Create `scripts/build_data.py`, tailored to *their* sources and column names. It must:

- read the latest data from `inbox/` (connector pulls should be saved there first as CSV/JSON, so every run is reproducible);
- compute every block in `b2b/data.js` using the field guide below;
- write the new `data.js` to a temporary file, run `scripts/check_data.py` on it, and only then replace `b2b/data.js`, after backing up the old one to `b2b/backups/`;
- print a short summary (period covered, MQLs, meetings, SQLs, pipeline, anything it couldn't fill).

Use only the Python standard library so it runs anywhere. Run it, fix any errors, then open `b2b/index.html` in the browser (or a simple local server) and click through the period buttons with the user.

## Step 4: Customise the cards

Walk them through the `CARDS` block in `data.js`: rename (`title`), change or clear the grey example line (`hint`), change the source label (`source`), change a channel goal (`goal`), or hide (`show:false`). Make the changes they asked for in Step 1, then show them. Put their monthly goals in `TARGETS`. The "Biggest recommendations" panel is written HTML in `index.html`. Offer to rewrite it from their real numbers, or to remove it.

## Step 5: Schedule the morning refresh (only with their OK)

Explain what will happen: "every weekday at 7am, Claude pulls yesterday's numbers, rebuilds the data file, checks it, keeps a backup and tells you what changed". Then set it up with whatever scheduling this Claude offers:

- **Claude desktop app:** create a scheduled task in this project that runs the `refresh-dashboard` skill at their chosen time. It runs while the computer is awake and the app is open.
- **Claude Code in the terminal:** offer a cloud routine with `/schedule`, which runs even when their laptop is off. It needs the project in a GitHub repo (private if it holds real data), and connectors rather than CSV exports. Or offer a local cron / launchd job that runs `claude -p "/refresh-dashboard"` in this folder.
- **Sources on CSV exports** can't be refreshed unattended. Say so plainly, and suggest a connector or a scheduled export (many CRMs can email or drop a report on a schedule).

Save the schedule in `dashboard.config.json`, then do one refresh now so they see it work.

## Step 6: Privacy check

Add `dashboard.config.json`, `inbox/*` (except `inbox/README.md`) and `b2b/backups/` to `.gitignore`. If `b2b/data.js` now holds real data and the git remote is public, warn them and suggest a private repo. Never commit or push without asking.

---

## Field guide: the shapes `data.js` must keep

Dates are `"YYYY-MM-DD"` strings. `0` means "none".

- **`DAILY`**: `{start, end, mql:[], meet:[], sql:[], sqlex:[], pipe:[], dealn:[]}`. One value per calendar day from `start` (1 January) to `end` (last full day of data), weekends included. `mql` = new MQLs that day. `meet` = meetings held/booked that day by contacts **after** they became an MQL, counted on the day they became an MQL. `sql` = all new SQLs. `sqlex` = new SQLs that were an MQL first. `pipe` = new deal value created that day. `dealn` = number of deals created.
- **`MQL_INBOUND` / `MQL_OUTBOUND`**: MQLs per month. Inbound = they came to you (forms, downloads, demo requests, event sign-ups, paid and organic). Outbound = you went to them (prospecting, imported lists, badge scans, partner lists). Ask the user how their CRM tells the two apart (usually original source, or a lead-source field). One value per entry in `MONTHS`.
- **`MONTHS`, `MONTH_NOTES`**: month labels and a one-line story for each (shown on hover).
- **`DEALS`**: `[id, "Deal name", amount, "create date"]`.
- **`PEOPLE.mql`**: `[id, "Name", "Company", "MQL date", "SQL date" or 0, "first meeting after MQL" or 0]`.
- **`PEOPLE.sql`**: `[id, "Name", "Company", "SQL date", "MQL date" or 0]`. `0` means sales entered them straight at SQL.
- **`MB`** (Money Board): `{n: name, c: company, conv: first conversion, lconv: latest conversion or omitted, lt: latest traffic source, d: SQL date, v: deal value, t: job title, why: "How did we get this deal?" or omitted}`. Add `noMql: true` for marketing-sourced SQLs that skipped MQL.
- **`TARGETS`**: `{mqlPerMonth, meetPerMonth, sqlShareOfMQL, demoPerMonth, pipelinePerMonth}`. Share values are fractions (0.10 = 10%); `pipelinePerMonth` is the North Star target in your currency (e.g. 475000).
- **`P`**: channel figures per preset period: `weekly, monthly, quarterly, h1, h2, annual`. Each has `label, fm` (months in the period), `demos, demosRaw, gsc` (non-branded clicks), `ai` (AI-referral sessions), `bc, bcSubs` (Channel 3 meetings / ad responses), `content, contentMql` (Channel 4 downloads, and how many of those downloaders became MQLs), and `li: {leads, subs, opens, spend, clicks, cpc, cpql, note}`. Use `null` for anything unknown: the card greys out instead of showing a wrong number.
- **`EVENTS`**: `{name, bucket:'owned'|'sponsored', date, when, mql, held, booked, sql, cost, ceiling, goal, tip}`. `notracked:true` for events with no data yet.
- **`ATTRIB_MQL` / `ATTRIB_CUST`**: `[["Campaign or form", points], ...]`, largest first.
- **`CAMPAIGNS`**: `{name, ch, metric, mtype:'mql'|'sql'|'gbp'|'meet'|'other', val, goal, money?:true, ended?:true, tip}`. `ch` is the channel card it belongs to (1–5); the Money Board breakdown uses it to group touches named after the campaign.
- **`VERIFIED`**: date the channel numbers were last checked.
- **`CARDS`**: per-card `show, emoji, title, source, goal` (see the comment in the file).
