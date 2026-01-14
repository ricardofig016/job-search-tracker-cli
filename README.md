# Job Search Tracker CLI

A command-line tool designed to help you organize and track your job search. It features automated job data extraction from LinkedIn job posts, AI-powered fit analysis, interview tracking, transcript management, and Google Calendar integration.

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
      - [Sorting](#sorting)
      - [Column Management](#column-management)
      - [CSV Export](#csv-export)
    - [Editing Jobs](#editing-jobs)
    - [Interview Transcripts](#interview-transcripts)
    - [Deleting Jobs](#deleting-jobs)
    - [Statistics \& Analytics](#statistics--analytics)
  - [Advanced Usage](#advanced-usage)
    - [Bulk Adding](#bulk-adding)
    - [Maintenance Tasks](#maintenance-tasks)
    - [Database Schema](#database-schema)

## Features

- **Automated Scraping**: Extract company, role, location, and recruiter details directly from LinkedIn job post URLs.
- **AI Enrichment**: Uses OpenAI to calculate a "Fit" and "Rating" score based on your personal profile.
- **Calendar Sync**: Automatically creates and manages Google Calendar events for interviews and follow-ups.
- **Transcript Storage**: Keep all your interview notes and transcripts associated with specific applications.
- **Powerful Filtering**: SQL-like query syntax for filtering and sorting your applications.
- **Detailed Analytics**: Dashboard with conversion rates, response times, and funnel metrics.
- **Smart Maintenance**: Automatically marks applications as "Ghosted" if no response is received within 30 days.

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

To enable interview and follow-up syncing:

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

Prompts you for all job details step-by-step. You can clear fields or skip optional ones by typing `null`, `none`, or `-`.

#### Automated Add (LinkedIn)

```bash
python -m job_tracker.main add --url "https://www.linkedin.com/jobs/view/0123456789/"
```

Fetches details automatically. You can still override any field during the confirmation prompts.

### Viewing Jobs

Display your applications in a beautifully formatted table with clickable links for URLs.

```bash
# Basic view (last 10)
python -m job_tracker.main view --limit 10

# Filter by company (substring search)
python -m job_tracker.main view company~google

# Complex filtering with SQL-like syntax
python -m job_tracker.main view "rating>=4 AND level:senior"
```

#### Filter Syntax

- `~` or `:`: Substring search (e.g., `role~engineer`)
- `==`, `!=`, `>=`, `<=`, `>`, `<`: Standard operators
- `col:[min-max]`: Range search (e.g., `rating:[3-5]`)
- `AND`, `OR`: Logical operators

#### Sorting

Multi-level sorting is supported:

```bash
python -m job_tracker.main view --sort date:desc --sort rating:desc
```

#### Column Management

Customize which columns are displayed in the terminal:

```bash
# Showing/Hiding specific columns
python -m job_tracker.main view --show salary,recruiter --hide level

# Show all available database columns
python -m job_tracker.main view --all
```

#### CSV Export

Export your current view (including filters and sorting) to a CSV file:

```bash
python -m job_tracker.main view -e
python -m job_tracker.main view --export --output my_search.csv
```

### Editing Jobs

Update details for an existing application.

```bash
python -m job_tracker.main edit [JOB_ID]
```

This opens an interactive menu where you can select fields to change. Updating interview-related fields (date, time, status) will automatically trigger a Google Calendar sync.

### Interview Transcripts

Store or view interview transcripts for specific applications.

```bash
# Store a transcript from a file
python -m job_tracker.main transcript [JOB_ID] --file path/to/transcript.txt

# View a stored transcript
python -m job_tracker.main transcript [JOB_ID] --view

# Clear a transcript
python -m job_tracker.main transcript [JOB_ID] --clear

# Interactive management (prompts for file path or manual pasting)
python -m job_tracker.main transcript [JOB_ID]
```

### Deleting Jobs

```bash
python -m job_tracker.main delete [JOB_ID]
```

### Statistics & Analytics

View a comprehensive dashboard of your recruitment metrics.

```bash
python -m job_tracker.main stats

# Filter stats for a specific subset
python -m job_tracker.main stats "status==rejected"
```

Includes:

- **Application Funnel**: Visual breakdown of applications from applied to offer.
- **Conversion Rates**: Realistic rates calculated using settled applications (App -> Interview, Int -> Offer, etc.).
- **Response Times**: Average duration between application and first response or interview.
- **Success by Fit Level**: AI-powered analysis of how your "Fit" score correlates with interview success.
- **Top Companies & Sources**: Breakdown of where you are applying most.
- **Trends**: Weekly and monthly application volume.

## Advanced Usage

### Bulk Adding

Place multiple LinkedIn URLs (one per line) in `scripts/bulk_urls.txt`, then run:

```bash
python ./scripts/bulk_add.py
```

This script will process all URLs and automatically accept all scraped values.

### Maintenance Tasks

The CLI automatically performs maintenance on every run:

- **Database Initialization**: Ensures all tables and columns are up to date.
- **Ghosting Detection**: Any application marked as `applied` that is older than 30 days is automatically updated to `ghosted`.

### Database Schema

You can add custom columns to the database without manual SQL:

```bash
python -m job_tracker.main config add-column --name "referral_name" --type "TEXT"
```

_Note: You must also add this new column to `COLUMN_MAPPING` and `EDIT_COLUMN_ORDER` in `job_tracker/utils.py` to make it visible in filters and the editor._
