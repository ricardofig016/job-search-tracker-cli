import requests
from bs4 import BeautifulSoup
import re


def fetch_job_page(url: str) -> str:
    """
    Fetches the LinkedIn job page content.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def extract_html_data(html: str) -> dict:
    """
    Extracts structured data from the LinkedIn job page HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # company_name
    company_link = soup.select_one("a.topcard__org-name-link")
    if company_link:
        data["company_name"] = company_link.get_text(strip=True)
    else:
        # Fallback: Parse <title> tag
        title_tag = soup.title.string if soup.title else ""
        # Expected format: "Role Name at Company Name in Location | LinkedIn"
        # Or "Hiring Role Name in Location: Company Name..."
        # Let's try a simple regex or just leave it for LLM if really needed,
        # but the plan suggests parsing title or URL.
        # Let's try to extract from title if " at " exists.
        if " at " in title_tag:
            parts = title_tag.split(" at ")
            if len(parts) > 1:
                # Take the part after " at " and before " |" or " in "
                rest = parts[1]
                if " in " in rest:
                    data["company_name"] = rest.split(" in ")[0]
                elif " |" in rest:
                    data["company_name"] = rest.split(" |")[0]
                else:
                    data["company_name"] = rest

        if not data.get("company_name"):
            # Fallback: URL path? Not available here as we only have HTML.
            # We could pass URL to this function if needed, but let's stick to HTML for now.
            pass

    # company_linkedin
    if company_link and company_link.has_attr("href"):
        data["company_linkedin"] = company_link["href"].split("?")[0]  # Clean query params

    # role_name
    role_title = soup.select_one("h1.top-card-layout__title")
    if role_title:
        data["role_name"] = role_title.get_text(strip=True)
    else:
        role_title_alt = soup.select_one("h3.sub-nav-cta__header")
        if role_title_alt:
            data["role_name"] = role_title_alt.get_text(strip=True)

    # location
    location_span = soup.select_one("span.sub-nav-cta__meta-text")
    if location_span:
        data["location"] = location_span.get_text(strip=True)
    else:
        # 2nd span.topcard__flavor--bullet
        bullets = soup.select("span.topcard__flavor--bullet")
        if len(bullets) >= 1:
            # Usually the first one is company (if not a link), second is location.
            # But if company is a link, it might be different.
            # Let's look for the one that is NOT the company name if we have it.
            # Actually, the plan says "2nd span.topcard__flavor--bullet".
            # Let's try to find the one that looks like a location.
            # Often structure is: Company (bullet) Location (bullet) Time
            if len(bullets) >= 2:
                data["location"] = bullets[1].get_text(strip=True)
            elif len(bullets) == 1:
                data["location"] = bullets[0].get_text(strip=True)

    # Helper to find criteria text based on header
    def get_criteria(header_text):
        header = soup.find("h3", string=lambda t: t and header_text.lower() in t.lower())
        if header:
            # The value is usually in a following span or div
            # Structure: <li> <h3>Header</h3> <span>Value</span> </li>
            # Or similar.
            # Plan says: span.description__job-criteria-text
            # Let's look for the next sibling or parent's find.
            parent = header.find_parent("li")
            if parent:
                span = parent.select_one("span.description__job-criteria-text")
                if span:
                    return span.get_text(strip=True)
        return None

    # type
    data["type"] = get_criteria("Employment type")

    # recruiter_name
    recruiter_name_elem = soup.select_one("div.message-the-recruiter a.base-card__full-link span.sr-only")
    if recruiter_name_elem:
        data["recruiter_name"] = recruiter_name_elem.get_text(strip=True).replace("View ", "").replace("’s profile", "")

    # recruiter_linkedin
    recruiter_link_elem = soup.select_one("div.message-the-recruiter a.base-card__full-link")
    if recruiter_link_elem and recruiter_link_elem.has_attr("href"):
        data["recruiter_linkedin"] = recruiter_link_elem["href"].split("?")[0]

    # date_posted_raw
    posted_time = soup.select_one("span.posted-time-ago__text")
    if posted_time:
        data["date_posted_raw"] = posted_time.get_text(strip=True)

    # job_description
    description_div = soup.select_one("div.description__text")
    if not description_div:
        description_div = soup.select_one("div.show-more-less-html__markup")

    if description_div:
        # Get text with some structure (newlines)
        data["job_description"] = description_div.get_text(separator="\n", strip=True)

    return data
