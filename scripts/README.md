# A2UI Code Review Performance Analytics

This directory contains automated tooling to monitor, measure, and optimize code review performance across the A2UI repository.

The pipeline is split into **two independent stages**:
1. **Data Pull Stage (`scripts/pull_review_data.py`)**: Fetches full metadata, review timelines, comment timestamps, and commit events for merged Pull Requests directly from GitHub via GraphQL into a gitignored local store (`scripts/data/raw_prs.json`).
2. **Metrics Generation Stage (`scripts/generate_review_metrics.py`)**: Reads the cached raw PR data and generates week-by-week statistical breakdowns (by PR submission time), individual reviewer performance tables, turnaround latencies ("turns"), and exports to Markdown and CSVs (`scripts/reports/`).

---

## Language Choice: Why Python?

- **Zero External Dependencies**: Implemented using pure Python 3 standard library (`json`, `csv`, `statistics`, `datetime`, `argparse`, `math`, `subprocess`). No `pip install` or virtual environment required.
- **GitHub CLI Integration**: Uses the existing authenticated GitHub CLI (`gh api graphql`), eliminating token handling risks or extra API authentication libraries.
- **Instant Experimentation**: Rerunning metrics or testing new statistical models on local JSON data executes in under 0.1 seconds without hitting GitHub rate limits or running slow compilation/build steps (like TypeScript).

---

## Prerequisites

1. **GitHub CLI (`gh`)**: Ensure `gh` is installed and authenticated:
   ```bash
   gh auth status
   ```
2. **Python 3.10+**: Available in PATH as `python3`.

---

## Stage 1: Pulling Raw Review Data

Run `scripts/pull_review_data.py` to pull merged PR metadata. By default, it queries the last 12 weeks (84 days) of merged PRs in `a2ui-project/a2ui`.

```bash
# Pull default 12 weeks of merged PRs
python3 scripts/pull_review_data.py

# Pull custom timeframe (e.g. since 2026-06-01)
python3 scripts/pull_review_data.py --since 2026-06-01

# Filter during pull by author or reviewer
python3 scripts/pull_review_data.py --author nan-yu
python3 scripts/pull_review_data.py --reviewer gspencergoog

# Quick test run (e.g. limit to 10 PRs)
python3 scripts/pull_review_data.py --limit 10
```

### CLI Arguments for `pull_review_data.py`

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--repo` | `a2ui-project/a2ui` | Target GitHub repository (`owner/repo`) |
| `--days` | `84` (12 weeks) | Number of days of PR history to pull |
| `--since` | None | Start date filter (`YYYY-MM-DD`, overrides `--days`) |
| `--until` | None | End date filter (`YYYY-MM-DD`) |
| `--author` | None | Pre-filter PRs by author username |
| `--reviewer` | None | Pre-filter PRs by reviewer username |
| `--limit` | None | Maximum number of PRs to pull |
| `--output` | `scripts/data/raw_prs.json` | Output JSON file path (gitignored) |

### Extracted Metadata per PR
For each merged PR, the raw payload contains:
- `number`, `title`, `url`, `author`, `createdAt` (submission time), `mergedAt`, `isDraft`
- `listed_reviewers`: Users requested via `ReviewRequestedEvent` or active review requests, along with exact request timestamps.
- `other_reviewers`: Users who reviewed or commented without formal assignment.
- `reviews`: All review submissions with state (`APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`) and timestamp.
- `approvals`: All reviewer LGTM events with exact approval timestamps.
- `comments`: All issue and review thread comments with timestamps and authors.
- `commits`: All code update commits with commit author and timestamps.
- `timeline_events`: Chronologically ordered unified event timeline for calculating turn latencies.

---

## Stage 2: Generating Metrics & Reports

Run `scripts/generate_review_metrics.py` to analyze the pulled raw data. Because it operates on the local cache, you can run it repeatedly with different filters or flags in milliseconds.

```bash
# Generate full report (Markdown + CSV)
python3 scripts/generate_review_metrics.py

# Print the report directly to terminal stdout
python3 scripts/generate_review_metrics.py --stdout

# Filter by reviewer across the cached data
python3 scripts/generate_review_metrics.py --reviewer nan-yu --stdout

# Filter by author across the cached data
python3 scripts/generate_review_metrics.py --author polina-c --stdout

# Include bot accounts in metrics (default is human-only)
python3 scripts/generate_review_metrics.py --include-bots
```

### CLI Arguments for `generate_review_metrics.py`

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--input` | `scripts/data/raw_prs.json` | Path to raw JSON data |
| `--markdown` | `scripts/reports/review_report.md` | Path to output Markdown report |
| `--csv-dir` | `scripts/reports` | Directory where CSV files are saved |
| `--author` | None | Filter analysis by PR author |
| `--reviewer` | None | Filter analysis by reviewer |
| `--since` | None | Filter PRs created on or after `YYYY-MM-DD` |
| `--until` | None | Filter PRs created on or before `YYYY-MM-DD` |
| `--include-bots` | `False` | Include bot accounts (`gemini-code-assist`, etc.) |
| `--stdout` | `False` | Print Markdown report to stdout |

### Output Files (in `scripts/reports/` - gitignored)
1. **`review_report.md`**: Formatted Github-Flavored Markdown report containing:
   - Executive Summary with core percentiles.
   - Week-by-Week table grouped by PR submission time.
   - Individual Reviewer Performance table.
   - Individual Author Performance table.
   - Metric definitions and methodology.
2. **`weekly_metrics.csv`**: Weekly aggregated metrics (P50, P90 for all metrics).
3. **`reviewer_metrics.csv`**: Reviewer-level summary (LGTM counts, turnaround percentiles).
4. **`author_metrics.csv`**: Author-level summary (PR counts, LGTM latency, author turnaround percentiles).
5. **`pr_details.csv`**: Granular per-PR breakdown with timestamps and computed latencies.

---

## Metric Definitions

1. **Week Grouping (Submission Time)**:
   - PRs are grouped by `createdAt` into ISO calendar weeks (`YYYY-Www`). This attributes review performance to the cohort of code submitted in that week.
2. **Reviewer Added &rarr; LGTM**:
   - Elapsed time from when a reviewer was requested (`ReviewRequestedEvent`) to when they submitted an `APPROVED` review.
   - If a reviewer was never formally requested, the PR creation timestamp is used as the baseline.
   - Reported as **Median (P50)** and **90th Percentile (P90)**.
3. **Submission &rarr; First Reviewer Added**:
   - Time elapsed from PR opening until the author adds the first reviewer.
4. **Reviewer Turn Time (Ping-Pong Latency)**:
   - Latency between an author action (PR opened, reviewer requested, author pushed new commit, or author replied to comments) and the next reviewer action (submitting review or posting comment).
   - This measures reviewer responsiveness directly.
5. **Author Turn Time**:
   - Latency between a reviewer action (requesting changes or asking questions) and the author's response (new commit or reply).
6. **PR Lifespan**:
   - Total lead time from PR creation (`createdAt`) to `mergedAt`.
7. **Bot Filtering**:
   - Automated accounts (e.g. `gemini-code-assist`, `google-claude-agent`, `*-bot`) are excluded from reviewer turnaround and approvals by default to prevent zero-second automated replies from distorting human review statistics.

---

## Running Unit Tests

Run the test suite to verify calculation and parsing logic:
```bash
python3 -m unittest scripts/test_review_metrics.py
```
