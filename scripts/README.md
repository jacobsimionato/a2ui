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

### Extracted Metadata
The raw dataset (`scripts/data/raw_prs.json`) contains two normalized tables:
- **`prs`**: PR-level attributes including `number`, `title`, `url`, `author`, `createdAt` (submission time), `mergedAt`, `additions`, `deletions`, `changed_files`, `total_loc`, `listed_reviewers`, `other_reviewers`, `reviews`, `approvals`, `comments`, `commits`, and unified `timeline_events`.
- **`reviews`**: Reviewer-level latency records tracking each reviewer's time added to time LGTM, turns count, and whether they were formally requested.

---

## Stage 2: Dimension-Agnostic Metrics & Reporting

Run `scripts/generate_review_metrics.py` to analyze the pulled raw data across arbitrary dimensions (time intervals, PR complexity/LoC, or opt-in author/reviewer groupings).

```bash
# Default: Week-by-week cohort breakdown across all PRs
python3 scripts/generate_review_metrics.py --stdout

# Month-by-month breakdown for the last 4 months
python3 scripts/generate_review_metrics.py --interval month --months 4 --stdout

# Breakdown by month split by LoC threshold (< 1000 LoC vs >= 1000 LoC)
python3 scripts/generate_review_metrics.py --interval month --months 4 --loc-split 1000 --stdout

# Group by standard PR size tiers (<100 LoC, 100-500, 500-1000, 1000+)
python3 scripts/generate_review_metrics.py --group-by size --stdout

# Filter by PR size
python3 scripts/generate_review_metrics.py --min-loc 500 --max-loc 1500 --stdout

# Opt-in author or reviewer grouping
python3 scripts/generate_review_metrics.py --group-by author --stdout
python3 scripts/generate_review_metrics.py --group-by reviewer --stdout
```

### CLI Arguments for `generate_review_metrics.py`

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--input` | `scripts/data/raw_prs.json` | Path to raw JSON data |
| `--interval` | `week` | Time cohort grouping: `week` or `month` |
| `--months` | None | Filter to the last N calendar months (e.g. `--months 4`) |
| `--weeks` | None | Filter to the last N weeks |
| `--loc-split` | None | Split PRs into binary size tiers around a threshold (e.g. `--loc-split 1000`) |
| `--min-loc` | None | Filter PRs with total LoC >= min_loc |
| `--max-loc` | None | Filter PRs with total LoC <= max_loc |
| `--group-by` | `interval` | Comma-separated grouping dimensions: `interval`, `size`, `author`, `reviewer` |
| `--author` | None | Filter analysis by PR author |
| `--reviewer` | None | Filter analysis by reviewer |
| `--since` | None | Filter PRs created on or after `YYYY-MM-DD` |
| `--until` | None | Filter PRs created on or before `YYYY-MM-DD` |
| `--include-bots` | `False` | Include bot accounts (`gemini-code-assist`, etc.) |
| `--markdown` | `scripts/reports/review_report.md` | Path to output Markdown report |
| `--csv-dir` | `scripts/reports` | Directory where CSV files are saved |
| `--stdout` | `False` | Print Markdown report to stdout |

### Output Files (in `scripts/reports/` - gitignored)
1. **`review_report.md`**: Formatted Github-Flavored Markdown report with Executive Summary and multi-dimensional Cohort Breakdown.
2. **`metrics.csv`**: Aggregated metrics table across the requested dimensions.
3. **`prs.csv`**: Granular per-PR breakdown with timestamps, LoC, and computed latencies.

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
