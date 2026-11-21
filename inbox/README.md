# inbox

Drop your CSV exports here (or let Claude save connector pulls here). The refresh turns them into `b2b/data.js`.

Everything in this folder except this README is git-ignored, so your exports never end up in a commit by accident.

| Save as | What it is |
|---|---|
| `crm-contacts.csv` | Contacts who became an MQL or SQL this year |
| `crm-meetings.csv` | Meetings this year, with the contact's record ID |
| `crm-deals.csv` | Deals created this year |
| `crm-attribution.csv` | Contact create attribution report (U-shaped, by campaign) |
| `ga4-traffic.csv` | GA4 traffic acquisition by session source, daily |
| `gsc-dates.csv`, `gsc-queries.csv` | Search Console performance by date, and by query |
| `ads.csv` | Ad platform campaign performance (Google Ads, LinkedIn, Meta…), daily |

Not sure how to export one? Open this folder in Claude and say "set up my dashboard". It walks you through each one.
