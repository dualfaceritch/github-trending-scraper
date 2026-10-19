# GitHub Trending Scraper

A Playwright-based scraper that extracts the current [GitHub Trending](https://github.com/trending) repositories and saves them to a clean, analysis-ready CSV.

## What it does

- Opens GitHub Trending in a headless browser
- Waits for the dynamic content to render (no `sleep()` calls)
- Extracts repo name, URL, description, language, total stars, and stars today
- Normalizes the data (numbers become integers, missing fields become `"Unknown"`)
- Saves everything to a CSV file

## Why Playwright (and not `requests`)

GitHub's Trending page loads some content dynamically. A plain `requests.get()` would return HTML before the repo cards are populated. Playwright waits for the DOM to be ready, so we always see the fully-rendered page.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

The `playwright install` step downloads the Chromium browser binary. It only needs to be run once.

## Usage

```bash
# Scrape all trending repos → trending.csv
python portfolio_2nd.py

# Only the top 5 repos
python portfolio_2nd.py --limit 5

# Save to a custom file
python portfolio_2nd.py -o my_repos.csv

# Combine flags
python portfolio_2nd.py --limit 10 -o today.csv

# See all options
python portfolio_2nd.py --help
```

## Output

A CSV with one row per repository:

| name | url | description | language | stars | stars_today |
|---|---|---|---|---|---|
| MadsLorentzen/ai-job-search | https://github.com/MadsLorentzen/ai-job-search | The job search that runs on your machine... | Python | 54806 | 2232 |
| anthropics/claude-plugins-official | https://github.com/anthropics/claude-plugins-official | Official, Anthropic-managed directory... | Python | 42988 | 1175 |

A full sample is included in `sample_output.csv`.

## Design decisions

- **Event-driven waits**: Uses `wait_for_selector()` instead of `time.sleep()`. Sleeping is a race condition — too short and the page isn't ready, too long and you waste time.
- **Scoped selectors**: Each field is queried *inside* its parent card (`card.query_selector(...)`), not from the whole page. Without this, every card would return the first repo's data.
- **Defensive extraction**: Every field is optional. If a repo has no description or language, the scraper stores `None` and the cleaner converts it to a safe default.
- **Data normalization**: Raw scraped data contains strings like `"225,233"` and `"41,187 stars today"`. `clean_repos()` converts these to integers so the CSV is analysis-ready.

## Compliance

- Scrapes a public page — no login, no authentication
- One page load per run — well within any reasonable rate limit
- No personal data collected
- Respects GitHub's public content availability

## Requirements

- Python 3.10+
- Playwright + Chromium
- pandas 
