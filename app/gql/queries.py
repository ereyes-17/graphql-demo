from graphene import Field, Int, List, ObjectType, Schema, String
from app.gql.objs import JobObject, EmployerObject, CandidateObject, CandidateApplicationObject
from app.db.models import Job, Employer, Candidate, CandidateApplication
from app.db.database import Session
from app.util.roles import admin_user, authenticated_user
from typing import Any

class Query(ObjectType):
    """Root GraphQL query type."""

    jobs = List(JobObject)
    job = Field(JobObject, id=Int(required=True))

    employers = List(EmployerObject)
    employer = Field(EmployerObject, id=Int(required=True))

    candidates = List(CandidateObject)
    candidate = Field(CandidateObject, id=Int(required=True))

    applications = List(CandidateApplicationObject)

    @staticmethod
    def resolve_jobs(root: None, info: Any) -> list[Job]:
        """Return all jobs."""
        return Session().query(Job).all()

    @staticmethod
    def resolve_job(root, info: Any, id: Int) -> Job:
        return Session().query(Job).filter(id == Job.id).first()

    @staticmethod
    def resolve_employers(root: None, info: Any) -> list[Employer]:
        """Return all employers."""
        return Session().query(Employer).all()

    @staticmethod
    def resolve_employer(root, info: Any, id: Int) -> Employer:
        return Session().query(Employer).filter(id == Employer.id).first()

    @staticmethod
    @admin_user
    def resolve_candidates(root: None, info: Any) -> list[Candidate]:
        return Session().query(Candidate).all()

    @staticmethod
    @authenticated_user
    def resolve_candidate(root: None, info: Any, id: Int) -> Candidate:
        return Session().query(Candidate).filter(id == Candidate.id).first()