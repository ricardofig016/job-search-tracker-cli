import re
from typing import List, Tuple, Any, Dict

from datetime import date

def validate_date(date_str: str) -> bool:
    """Validates if a string is in YYYY-MM-DD format."""
    if not date_str:
        return True
    try:
        date.fromisoformat(date_str)
        return True
    except ValueError:
        return False

# Mapping of short names used in CLI to actual database column names
COLUMN_MAPPING = {
    "id": "id",
    "company": "company_name",
    "company_url": "company_url",
    "company_linkedin": "company_linkedin",
    "role": "role_name",
    "role_url": "role_url",
    "location": "location",
    "arrangement": "arrangement",
    "type": "type",
    "level": "level",
    "source": "source",
    "recruiter": "recruiter_name",
    "recruiter_email": "recruiter_email",
    "recruiter_linkedin": "recruiter_linkedin",
    "salary": "expected_salary",
    "notes": "notes",
    "status": "status",
    "date_posted": "date_posted",
    "date": "date_applied",
    "followup": "followup_date",
    "response": "response_date",
    "interview": "interview_date",
    "interview_type": "interview_type",
    "offer": "offer",
    "rating": "rating",
    "fit": "fit",
    "feedback": "feedback",
    "method": "application_method"
}

def parse_filter_string(filter_str: str) -> Tuple[str, List[Any]]:
    """
    Parses a filter string into a SQL WHERE clause and parameters.
    Supports: ==, !=, >=, <=, >, <, ~, : (substring), AND, OR, and [min-max] ranges.
    Example: "rating>=4 AND company~google OR status==offered"
    """
    if not filter_str:
        return "", []

    # Split by AND/OR but keep them to maintain logic
    # Using regex to split while preserving the delimiters
    parts = re.split(r'(\s+AND\s+|\s+OR\s+)', filter_str, flags=re.IGNORECASE)
    
    sql_parts = []
    params = []
    
    for part in parts:
        clean_part = part.strip()
        if not clean_part:
            continue
            
        upper_part = clean_part.upper()
        if upper_part in ("AND", "OR"):
            sql_parts.append(upper_part)
            continue
        
        # Try to match range first: col:[min-max]
        range_match = re.match(r'(\w+):\[(.*)-(.*)\]', clean_part)
        if range_match:
            col_short, min_val, max_val = range_match.groups()
            col = COLUMN_MAPPING.get(col_short.lower(), col_short)
            sql_parts.append(f"({col} >= ? AND {col} <= ?)")
            params.extend([min_val.strip(), max_val.strip()])
            continue

        # Match other operators: ==, !=, >=, <=, >, <, ~, :
        # We use a regex that captures the column, operator, and value
        match = re.match(r'(\w+)\s*(==|!=|>=|<=|>|<|~|:)\s*(.*)', clean_part)
        if not match:
            # If it doesn't match any operator, maybe it's just a keyword search on company/role?
            # But the requirement says "filter data for more than one thing... using OR/AND"
            # So we expect col op val format.
            continue
            
        col_short, op, val = match.groups()
        col = COLUMN_MAPPING.get(col_short.lower(), col_short)
        val = val.strip().strip("'\"")
        
        if op == "==":
            sql_parts.append(f"{col} = ?")
            params.append(val)
        elif op == "!=":
            sql_parts.append(f"{col} != ?")
            params.append(val)
        elif op == ">=":
            sql_parts.append(f"{col} >= ?")
            params.append(val)
        elif op == "<=":
            sql_parts.append(f"{col} <= ?")
            params.append(val)
        elif op == ">":
            sql_parts.append(f"{col} > ?")
            params.append(val)
        elif op == "<":
            sql_parts.append(f"{col} < ?")
            params.append(val)
        elif op in ("~", ":"):
            sql_parts.append(f"{col} LIKE ?")
            params.append(f"%{val}%")
                
    return " ".join(sql_parts), params

def parse_sort_string(sort_list: List[str]) -> str:
    """
    Converts a list of sort strings into a SQL ORDER BY clause.
    Example: ['date:desc', 'rating:asc'] -> "date_applied DESC, rating ASC"
    """
    if not sort_list:
        return ""
    
    sort_parts = []
    for s in sort_list:
        if ":" in s:
            col_short, direction = s.split(":", 1)
            col = COLUMN_MAPPING.get(col_short.lower(), col_short)
            dir_sql = "DESC" if direction.lower() == "desc" else "ASC"
            sort_parts.append(f"{col} {dir_sql}")
        else:
            col = COLUMN_MAPPING.get(s.lower(), s)
            sort_parts.append(f"{col} ASC")
            
    return ", ".join(sort_parts)

def get_visible_columns(show: str = None, hide: str = None, all_cols: bool = False) -> List[str]:
    """
    Determines which columns should be displayed based on show/hide flags.
    """
    default_cols = ["id", "company", "role", "status", "date"]
    
    if all_cols:
        return list(COLUMN_MAPPING.keys())
    
    # Start with defaults
    cols = default_cols.copy()
    
    if show:
        show_list = [c.strip().lower() for c in show.split(",")]
        for c in show_list:
            if c in COLUMN_MAPPING and c not in cols:
                cols.append(c)
    
    if hide:
        hide_list = [c.strip().lower() for c in hide.split(",")]
        for c in hide_list:
            if c in cols:
                cols.remove(c)
                
    return cols
