# Job Search Tracker CLI

A command-line tool designed to help you organize and track your job search. It features automated job data extraction from LinkedIn job posts, AI-powered fit analysis, interview tracking, and Google Calendar integration.

## Table of Contents

- [Job Search Tracker CLI](#job-search-tracker-cli)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
  - [Configuration](#configuration)
    - [User Profile](#user-profile)
    - [Google Calendar](#google-calendar)
  - [Usage](#usage)
    - [Adding Jobs](#adding-jobs)
      - [Interactive Add](#interactive-add)
      - [Automated Add (LinkedIn)](#automated-add-linkedin)
    - [Viewing Jobs](#viewing-jobs)
      - [Filter Syntax](#filter-syntax)
    - [Editing Jobs](#editing-jobs)
    - [Deleting Jobs](#deleting-jobs)
    - [Statistics \& Analytics](#statistics--analytics)
  - [Advanced Usage](#advanced-usage)
    - [Bulk Adding](#bulk-adding)
    - [Customizing UI](#customizing-ui)
    - [Database Schema](#database-schema)

## Features

- **Automated Scraping**: Extract company, role, location, and recruiter details directly from LinkedIn job post URLs.
- **AI Enrichment**: Uses OpenAI to calculate a "Fit" and "Rating" score based on your personal profile.
- **Calendar Sync**: Automatically creates and manages Google Calendar events for interviews.
- **Powerful Filtering**: SQL-like query syntax for filtering and sorting your applications.
- **Detailed Analytics**: Dashboard with conversion rates, response times, and funnel metrics.

## Installation

### Prerequisites

- Python 3.8+
- SQLite (included with Python)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ricardofig016/job-search-tracker-cli.git
   cd job-search-tracker-cli
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment variables:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Configuration

### User Profile

To get accurate AI-powered "Fit" and "Rating" scores, update `user_profile.md` with your skills, experience, and career preferences. The LLM reads this file whenever you add a job via URL.

### Google Calendar

To enable interview syncing:

1. Obtain a `credentials.json` file from the [Google Cloud Console](https://console.cloud.google.com/).
2. Place it in the project root.
3. The first time you run a command that triggers a sync, it will open your browser for authentication and save a `token.json` file.

## Usage

The application is run as a Python module:

```bash
python -m job_tracker.main [COMMAND]
```

### Adding Jobs

#### Interactive Add

```bash
python -m job_tracker.main add
```

Prompts you for all job details step-by-step.

#### Automated Add (LinkedIn)

```bash
python -m job_tracker.main add --url "https://www.linkedin.com/jobs/view/0123456789/"
```

Fetches details automatically. You can still override any field during the confirmation prompts.

### Viewing Jobs

Display your applications in a formatted table.

```bash
# Basic view (last 10)
python -m job_tracker.main view --limit 10

# Filter by company
python -m job_tracker.main view company~google

# Complex filtering
python -m job_tracker.main view "rating>=4 AND level:senior"

# Multi-Level Sorting
python -m job_tracker.main view --sort date:desc --sort rating:desc

# Showing/Hiding columns
python -m job_tracker.main view --show salary,recruiter --hide level
```

#### Filter Syntax

- `~` or `:`: Substring search (e.g., `role~engineer`)
- `==`, `!=`, `>=`, `<=`, `>`, `<`: Standard operators
- `col:[min-max]`: Range search (e.g., `rating:[3-5]`)
- `AND`, `OR`: Logical operators

### Editing Jobs

Update details for an existing application.

```bash
python -m job_tracker.main edit [JOB_ID]
```

This opens an interactive menu where you can select fields to change. Updating interview related fields will automatically trigger a Google Calendar sync.

### Deleting Jobs

```bash
python -m job_tracker.main delete [JOB_ID]
```

### Statistics & Analytics

View your recruitment funnel and performance.

```bash
python -m job_tracker.main stats

# View stats for a specific subset
python -m job_tracker.main stats "status==rejected"
```

Includes:

- **Application Funnel**: Total counts and percentages for each stage.
- **Conversion Rates**: App -> Interview, Int -> Offer, etc.
- **Response Times**: Average days to hear back.
- **Fit vs. Success**: Analysis of how your AI-calculated "Fit" correlates with landing interviews.

## Advanced Usage

### Bulk Adding

Place multiple LinkedIn URLs (one per line) in `scripts/bulk_urls.txt`, then run:

```bash
python ./scripts/bulk_add.py
```

This script will process all URLs, automatically accepting all scraped/AI-enriched values.

### Customizing UI

Most columns in the `view` command are mapped to aliases. You can find the mapping in `job_tracker/utils.py`. For example, `company` maps to `company_name` in the database.

### Database Schema

You can add custom columns to the database without manual SQL:

```bash
python -m job_tracker.main config add-column --name "referral_name" --type "TEXT"
```

_Note: You may need to add this new column to `COLUMN_MAPPING` in `job_tracker/utils.py` to use it in filters._
