import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def enrich_job_data(html_data: dict, user_profile_text: str) -> dict:
    """
    Uses an LLM to extract missing fields, infer data, and generate insights.
    """
    current_date = datetime.date.today().isoformat()

    # Prepare context
    context = {"current_date": current_date, "date_posted_raw": html_data.get("date_posted_raw"), "job_description": html_data.get("job_description"), "user_profile": user_profile_text, "extracted_data": {k: v for k, v in html_data.items() if k != "job_description"}}  # Exclude large text from this summary

    instructions = "You are a career assistant. Your goal is to extract structured job details from a job description " "and analyze the fit based on the user's profile.\n" "You will be provided with the job description, some already extracted data, and the user's profile.\n" "Respond in strict JSON only, matching the provided schema."

    user_prompt = f"Here is the job and user context:\n{json.dumps(context, default=str)}"

    try:
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "name": "JobPostFields",
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "arrangement": {
                                "type": ["string", "null"],
                                "enum": ["remote", "hybrid", "onsite", None],
                                "description": "Work arrangement. Null if inconclusive.",
                            },
                            "expected_salary": {
                                "type": ["string", "null"],
                                "description": "Expected salary range or amount. This does not need to be a value, it can be anything, like '[amount] to [amount] (salary base) + [allowance] + [benefits]'. Null if inconclusive.",
                            },
                            "date_posted": {
                                "type": "string",
                                "description": "Calculated exact date (YYYY-MM-DD) based on 'date_posted_raw' and 'current_date'.",
                            },
                            "notes": {
                                "type": "string",
                                "description": "A hyper concise summary of the job, highlighting key tech stack and responsibilities. What makes this job unique? What is super important about this post that isn't already in the title or in the other fields? Maximum of 10 words.",
                            },
                            "rating": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "General opportunity rating, based on how good the job seems and how good the company is to work at. How much do I want to work here compared to other opportunities? Note that how I fit the job description has nothing to do with this rating. Imagine that I am already hired for this position, how would i rate my day to day life doing this job in this company? 5 is best, 1 is worst.",
                            },
                            "fit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Fit with user profile. How well does the job match the user's skills, experience, and preferences? Consider skills required, amount of experience, and other relevant factors. Put yourself in the shoes of the recruiter analysing my application for this job post. How well does this candidate fit? 5 is good match, 1 is poor match.",
                            },
                            "type": {
                                "type": ["string", "null"],
                                "enum": ["fulltime", "contract", "part-time", "freelance", None],
                                "description": "Employment type. Null if inconclusive.",
                            },
                            "level": {
                                "type": ["string", "null"],
                                "enum": ["internship", "junior", "mid level", "senior", "lead", "manager", None],
                                "description": "Seniority level. Null if inconclusive.",
                            },
                            "recruiter_name": {"type": ["string", "null"]},
                            "recruiter_email": {"type": ["string", "null"]},
                            "recruiter_linkedin": {"type": ["string", "null"]},
                            "recruiter_phone_number": {"type": ["string", "null"]},
                        },
                        "required": ["arrangement", "recruiter_email", "expected_salary", "date_posted", "notes", "rating", "fit", "type", "level", "recruiter_name", "recruiter_linkedin", "recruiter_phone_number"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
                # "verbosity": "low",
            },
        )

        content = response.output_text
        if content:
            return json.loads(content)
        return {}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {}
