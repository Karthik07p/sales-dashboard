# AXIS Sales Dashboard (sample data)

A single-page sales dashboard I built to show how a CRM-driven weekly review can look: calls, connect rate, meetings, pipeline, and one tab per region (North, South, West, East, USA, Canada, Australia, Europe, RoW).

**Live demo:** https://karthik07p.github.io/projects/sales-dashboard/app/ · **Case study:** https://karthik07p.github.io/projects/sales-dashboard/

Every person, organisation and number in it is synthetic. The page works out all figures in the browser from a dated CRM history for whatever period you pick (this week, last month, a custom range, and so on), and every tile and chart opens the records behind it.

## Rebuild

```bash
python generate_history.py   # writes history.json (seeded, so the output is repeatable)
python build.py              # embeds it into template_portfolio.html -> index.html
```

Open `index.html` directly in a browser; there is no server or build step.

Karthik Pandurangan
