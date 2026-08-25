from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from graphene import Boolean, Field, Int, Mutation, ObjectType, String
from graphql import GraphQLError

from app.db.database import Session
from app.db.models import Candidate, CandidateApplication, Employer, Job
from app.gql.objs import (
    CandidateApplicationObject,
    CandidateObject,
    EmployerObject,
    JobObject,
)
from app.util.jwtutil import generate_token
from app.util.roles import admin_user, user_same_as_candidate

ph = PasswordHasher()

class AddJob(Mutation):
    class Arguments:
        title = String(required=True)
        description = String(required=True)
        employer_id = Int(required=True)

    job = Field(lambda: JobObject)

    @staticmethod
    @admin_user
    def mutate(root, info, title, description, employer_id):
        session = Session()

        job = Job(title=title, description=description, employer_id=employer_id)

        session.add(job)
        session.commit()
        session.refresh(job) # refresh job instance with updated job record in the db

        return AddJob(job=job)

class UpdateJob(Mutation):
    class Arguments:
        title = String()
        description = String()
        employer_id = Int()
        job_id = Int(required=True)

    job = Field(lambda: JobObject)

    @staticmethod
    @admin_user
    def mutate(root, info, job_id, title=None, description=None, employer_id=None):
        session = Session()

        job = session.query(Job).filter(job_id == Job.id).first()

        if job is None:
            raise GraphQLError("job not found")

        job.title = title if title is not None else job.title
        job.description = description if description is not None else job.description
        job.employer_id = employer_id if employer_id is not None else job.employer_id

        session.commit()
        session.refresh(job)

        return UpdateJob(job=job)
    
class DeleteJob(Mutation):
    class Arguments:
        job_id = Int(required=True)

    success = Field(Boolean)

    @staticmethod
    @admin_user
    def mutate(root, info, job_id):
        session = Session()

        job = session.query(Job).filter(job_id == Job.id).first()

        if job is None:
            raise GraphQLError("job not found")

        session.delete(job)
        session.commit()

        return DeleteJob(success=True)

class AddEmployer(Mutation):
    class Arguments:
        name = String(required=True)
        contact_email = String(required=True)
        industry = String(required=False)

    employer = Field(lambda: EmployerObject)

    @staticmethod
    @admin_user
    def mutate(root, info, name, contact_email, industry=None):

        session = Session()

        employer = Employer(name=name, contact_email=contact_email, industry=industry)

        session.add(employer)
        session.commit()
        session.refresh(employer)

        return AddEmployer(employer=employer)

class UpdateEmployer(Mutation):
    class Arguments:
        name = String()
        contact_email = String()
        industry = String()
        employer_id = Int(required=True)

    employer = Field(lambda: EmployerObject)

    @staticmethod
    @admin_user
    def mutate(root, info, employer_id, name=None, contact_email=None, industry=None):
        session = Session()

        employer = session.query(Employer).filter(employer_id == Employer.id).first()

        if employer is None:
            raise GraphQLError("employer not found")

        employer.name = name if name is not None else employer.name
        employer.contact_email = contact_email if contact_email is not None else employer.contact_email
        employer.industry = industry if industry is not None else employer.industry

        session.commit()
        session.refresh(employer)

        return UpdateEmployer(employer=employer)
    
class DeleteEmployer(Mutation):
    class Arguments:
        employer_id = Int(required=True)

    success = Field(Boolean)

    @staticmethod
    @admin_user
    def mutate(root, info, employer_id):
        session = Session()

        employer = session.query(Employer).filter(employer_id == Employer.id).first()

        if employer is None:
            raise GraphQLError("employer not found")

        session.delete(employer)
        session.commit()

        return DeleteEmployer(success=True)

class AddCandidate(Mutation):
    class Arguments:
        first_name = String(required=True)
        last_name = String(required=True)
        contact_email = String(required=True)
        password = String(required=True)
        role = String(required=False)

    candidate = Field(lambda: CandidateObject)

    @staticmethod
    def mutate(root, info, first_name, last_name, contact_email, password, role="user"):
        session = Session()

        existing_candidate = session.query(Candidate).filter(contact_email == Candidate.contact_email).first()

        if existing_candidate:
            raise GraphQLError("candidate already exists")

        candidate = Candidate(first_name=first_name, 
                              last_name=last_name, 
                              contact_email=contact_email, 
                              password_hash=ph.hash(password),
                              role=role)

        session.add(candidate)
        session.commit()
        session.refresh(candidate)

        return AddCandidate(candidate=candidate)

class AddCandidateApplication(Mutation):
    class Arguments:
        candidate_id = Int(required=True)
        job_id = Int(required=True)

    candidate_application = Field(lambda: CandidateApplicationObject)

    @staticmethod
    @user_same_as_candidate
    def mutate(root, info, candidate_id, job_id):

        session = Session()

        candidate = session.query(Candidate).filter(candidate_id == Candidate.id).first()

        if candidate is None:
            raise GraphQLError("candidate does not exist")

        job = session.query(Job).filter(job_id == Job.id).first()

        if job is None:
            raise GraphQLError("job does not exist")

        candidate_application = CandidateApplication(candidate_id=candidate.id, job_id=job.id)

        session.add(candidate_application)
        session.commit()
        session.refresh(candidate_application)

        return AddCandidateApplication(candidate_application=candidate_application)

class LoginCandidate(Mutation):
    class Arguments:
        contact_email = String(required=True)
        password = String(required=True)

    token = String()

    @staticmethod
    def mutate(root, info, contact_email, password):
        session = Session()

        candidate = session.query(Candidate).filter(contact_email == Candidate.contact_email).first()

        # not a way to do password validation
        if not candidate:
            raise GraphQLError("invalid credentials")

        try:
            ph.verify(candidate.password_hash, password)
        except VerificationError:
            raise GraphQLError("invalid credentials")

        token = generate_token(contact_email)

        return LoginCandidate(token=token)
        

class Mutation(ObjectType):
    add_job = AddJob.Field()
    update_job = UpdateJob.Field()
    delete_job = DeleteJob.Field()
    add_employer = AddEmployer.Field()
    update_employer = UpdateEmployer.Field()
    delete_employer = DeleteEmployer.Field()
    add_candidate = AddCandidate.Field()
    add_candidate_application = AddCandidateApplication.Field()
    login_candidate = LoginCandidate.Field()