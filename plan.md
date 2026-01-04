# Implementation Plan: LinkedIn Job Post Scraper & LLM Integration

This plan outlines the steps to implement a feature that allows adding job posts via a LinkedIn URL. The system will scrape the page for structured data and use an LLM (ChatGPT) to extract unstructured information, infer missing fields, and generate personalized insights (notes, rating, fit).

## 1. Prerequisites & Dependencies

We need to add libraries for HTTP requests, HTML parsing, and LLM interaction.

- **`requests`**: For fetching the LinkedIn job page (unauthenticated).
- **`beautifulsoup4`**: For parsing the HTML content.
- **`openai`**: For interacting with the ChatGPT API.
- **`python-dotenv`**: To manage the OpenAI API key (if not already present).

### Action Items

- Update `requirements.txt` to include:
  - `requests`
  - `beautifulsoup4`
  - `openai`
  - `python-dotenv` (if needed)

## 2. Configuration & User Profile

To calculate `fit` and `rating`, the LLM needs context about the user. We will introduce a user profile file.

### Action Items

- **Create `user_profile.md`**: A file in the project root where the user can paste their resume, skills, and experience.
- **Environment Variable**: Ensure `OPENAI_API_KEY` is set in a `.env` file or the environment.

## 3. Architecture Changes

We will introduce two new modules to keep the logic clean and separated from the CLI commands.

- **`job_tracker/scraper.py`**: Handles HTTP requests and HTML parsing using BeautifulSoup.
- **`job_tracker/llm.py`**: Handles constructing the prompt, calling the OpenAI API, and parsing the structured JSON response.

## 4. Step-by-Step Implementation

### Step 1: Implement `job_tracker/scraper.py`

This module will be responsible for fetching the URL and extracting fields that can be reliably found in the HTML structure.

**Functions:**

1.  `fetch_job_page(url: str) -> str`:

    - Perform a GET request to the provided URL.
    - Use a standard User-Agent header to avoid immediate blocking (e.g., mimicking a browser).
    - Return the HTML content.

2.  `extract_html_data(html: str) -> dict`:
    - Parse HTML with BeautifulSoup.
    - Initialize a dictionary for extracted data.
    - **Extraction Logic (per user specs):**
      - **`company_name`**:
        - Try: `a.topcard__org-name-link` text.
        - Fallback: Parse `<title>` tag or URL path.
      - **`company_linkedin`**:
        - Try: `a.topcard__org-name-link['href']`.
      - **`role_name`**:
        - Try: `h1.top-card-layout__title` text OR `h3.sub-nav-cta__header` text.
      - **`location`**:
        - Try: `span.sub-nav-cta__meta-text` text OR 2nd `span.topcard__flavor--bullet` text.
      - **`type`**:
        - Find `h3` containing "Employment type", get following `span.description__job-criteria-text`.
        - If missing, mark as None (to be handled by LLM).
      - **`level`**:
        - Find `h3` containing "Seniority level", get following `span.description__job-criteria-text`.
        - If missing or "Not Applicable", mark as None (to be handled by LLM).
      - **`recruiter_name`**:
        - Try: `div.message-the-recruiter a.base-card__full-link span.sr-only` text.
        - If missing, mark as None (to be handled by LLM).
      - **`recruiter_linkedin`**:
        - Try: `div.message-the-recruiter a.base-card__full-link['href']`.
        - If missing, mark as None (to be handled by LLM).
      - **`date_posted_raw`**:
        - Extract text from `span.posted-time-ago__text` (e.g., "2 days ago").
      - **`job_description`**:
        - Extract the full text of the job description container (usually `div.description__text` or `div.show-more-less-html__markup`). This is crucial for the LLM.

### Step 2: Implement `job_tracker/llm.py`

This module will handle the single LLM call required to process the job post.

**Functions:**

1.  `enrich_job_data(html_data: dict, user_profile_text: str) -> dict`:
    - **Prepare Context**:
      - Current Date (YYYY-MM-DD).
      - `date_posted_raw` from HTML.
      - `job_description` text.
      - `user_profile_text`.
      - List of fields that _failed_ HTML extraction (e.g., if `type` was null).
    - **Construct Prompt**:
      - **System**: "You are a career assistant. Extract job details and analyze fit based on the user's profile."
      - **User**: Provide the context and ask for a JSON response.
    - **Define Schema (Structured Output)**:
      - `arrangement` (string: Remote, Hybrid, Onsite)
      - `recruiter_email` (string or null)
      - `expected_salary` (string or null)
      - `date_posted` (string, YYYY-MM-DD format, calculated from `date_posted_raw` + current date)
      - `notes` (string, concise summary)
      - `rating` (integer, 1-5)
      - `fit` (integer, 1-5)
      - **Conditional Fields**: Include `type`, `level`, `recruiter_name`, `recruiter_linkedin` in the schema. The prompt should instruct the LLM to fill these _only if_ they are not provided or if specifically asked (or we can just always ask and overwrite if HTML failed, or prefer HTML if present). _Decision: Always ask for them in the schema to keep the schema static, but in the prompt, tell the LLM to extract them from the description._
    - **Call OpenAI**: Use `client.chat.completions.create` with `response_format={"type": "json_object"}` or structured outputs.
    - **Return**: Parsed JSON dictionary.

### Step 3: Update `job_tracker/commands/add.py`

Modify the `add` command to accept the URL and orchestrate the flow.

**Changes:**

1.  **Arguments**:

    - Add `url: str = typer.Option(None, "--url", help="LinkedIn job post URL")` to the `add` function signature.

2.  **Logic Flow (if URL is provided)**:
    - **Fetch & Parse**: Call `scraper.fetch_job_page(url)` and `scraper.extract_html_data(html)`.
    - **Load Profile**: Read `user_profile.md`. If it doesn't exist, warn the user that "fit" and "rating" might be inaccurate or skip those specific LLM instructions.
    - **LLM Enrichment**: Call `llm.enrich_job_data`.
    - **Merge Data**:
      - Start with `html_data`.
      - Update with `llm_data` (LLM fills gaps like `arrangement`, `notes`, etc., and resolves `date_posted`).
      - Set `role_url` = `url`.
      - Set `source` = "linkedin".
    - **Interactive Confirmation/Completion**:
      - The `add` command currently prompts for fields. We need to change this to _pre-fill_ the defaults with our extracted data.
      - For fields NOT extracted (e.g., `status`, `date_applied`, `interview_...`), prompt the user as normal.
      - For extracted fields (`company`, `role`, `location`, etc.), we can either:
        - Skip prompting (trust the scraper).
        - Prompt with the extracted value as the `default`. _Recommendation: Prompt with default so the user can verify._
    - **Save**: Proceed with the existing logic to save to the database.

### Step 4: Update `job_tracker/models.py` (if necessary)

- Ensure `JobPost` model (or the dict passed to DB) can handle the new fields if they aren't already there.
- Check if `recruiter_linkedin`, `expected_salary`, `notes`, `rating`, `fit` exist in the DB schema.
  - _Note_: The user instructions imply these fields are desired. We need to check `initialize_db` in `database.py`. If these columns don't exist, we need to add them or use `add_new_column` logic if the app supports dynamic schema updates, or manually update the schema.
  - _Assumption_: Based on "add a new feature", we likely need to ensure the DB has these columns.
  - **Action**: Check `job_tracker/database.py` schema. If columns are missing, create a migration function or update `initialize_db` and instruct the user to run a migration (or handle it automatically).

## 5. Detailed Field Mapping & Logic

| Field                | Source   | Logic                                              |
| :------------------- | :------- | :------------------------------------------------- |
| `company_name`       | HTML     | `a.topcard__org-name-link`                         |
| `company_linkedin`   | HTML     | `a.topcard__org-name-link['href']`                 |
| `role_name`          | HTML     | `h1.top-card-layout__title`                        |
| `location`           | HTML     | `span.sub-nav-cta__meta-text`                      |
| `arrangement`        | LLM      | Extracted from description (Remote/Hybrid/Onsite)  |
| `type`               | HTML/LLM | `Employment type` section or LLM fallback          |
| `level`              | HTML/LLM | `Seniority level` section or LLM fallback          |
| `recruiter_name`     | HTML/LLM | `div.message-the-recruiter` or LLM fallback        |
| `recruiter_email`    | LLM      | Extracted from description                         |
| `recruiter_linkedin` | HTML/LLM | `div.message-the-recruiter` or LLM fallback        |
| `expected_salary`    | LLM      | Extracted from description                         |
| `date_posted`        | HTML+LLM | HTML relative string -> LLM converts to YYYY-MM-DD |
| `role_url`           | Input    | Direct from CLI arg                                |
| `source`             | Constant | "linkedin"                                         |
| `notes`              | LLM      | Generated summary                                  |
| `rating`             | LLM      | Calculated (1-5) based on profile                  |
| `fit`                | LLM      | Calculated (1-5) based on profile                  |

## 6. Verification & Testing

1.  **Unit Test Scraper**: Create a test with a saved LinkedIn HTML file to verify selector logic without hitting the network constantly.
2.  **Integration Test**: Run `python -m job_tracker.main add --url <URL>` and verify:
    - Data is fetched.
    - LLM is called.
    - Prompts appear with pre-filled values.
    - Database is updated correctly.
