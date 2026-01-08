from enum import Enum


class Arrangement(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobType(str, Enum):
    FULLTIME = "fulltime"
    CONTRACT = "contract"
    PART_TIME = "part-time"
    FREELANCE = "freelance"


class ExperienceLevel(str, Enum):
    INTERNSHIP = "internship"
    JUNIOR = "junior"
    MID_LEVEL = "mid level"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"


class Source(str, Enum):
    LINKEDIN = "linkedin"
    COMPANY_WEBSITE = "company website"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    REFERRAL = "referral"
    RECRUITER_OUTREACH = "recruiter outreach"
    OTHER = "other"


class Status(str, Enum):
    APPLIED = "applied"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    GHOSTED = "ghosted"
