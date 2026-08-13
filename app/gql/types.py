from typing import Any
from graphene import Field, Int, List, ObjectType, Schema, String
from app.db.models import Job, Employer, Candidate, CandidateApplication

class EmployerObject(ObjectType):
    """GraphQL type representing an employer."""

    id = Int()
    name = String()
    contact_email = String()
    industry = String()
    # Lambda wraps the reference class so Graphene can resolve it lazily.
    # This avoids the NameError caused by JobObject being defined later in the file.
    jobs = List(lambda: JobObject)

    @staticmethod
    def resolve_jobs(root: Employer, info: Any) -> list[Job]:
        """Return the jobs that belong to this employer."""
        return root.jobs


class JobObject(ObjectType):
    """GraphQL type representing a job posting."""

    id = Int()
    title = String()
    description = String()
    employer_id = String()
    employer = Field(lambda: EmployerObject)  # Lambda not necessary here, used for consistency.
    applications = List(lambda: CandidateApplicationObject)

    @staticmethod
    def resolve_employer(root: Job, info: Any) -> Employer | None:
        """Return the employer that posted this job, if any."""
        return root.employer

class CandidateObject(ObjectType):
    id = Int()
    first_name = String()
    last_name = String()
    contact_email = String()
    applications = List(lambda: CandidateApplicationObject)
    role = String()

    @staticmethod
    def resolve_applications(root: Candidate, info: Any) -> list[CandidateApplication] | None:
        return root.applications

class CandidateApplicationObject(ObjectType):
    id = Int()
    candidate_id = Int()
    candidate = Field(lambda: CandidateObject)
    job_id = Int()
    job = Field(lambda: JobObject)

    @staticmethod
    def resolve_job(root: CandidateApplication, info: Any) -> Job:
        return root.job

    @staticmethod
    def resolve_candidate(root: CandidateApplication, info: Any) -> Candidate:
        return root.candidate

