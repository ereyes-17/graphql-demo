from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Employer(Base):
    # This entity we defined is part of the DDL (Database Definition Language)
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_email = Column(String)
    industry = Column(String)
    # so the jobs attribute is a list of Job objects
    # the first param is the object the relationship is to 
    # back_populates is the field in that object that 'this' object gets mapped to
    jobs = relationship("Job", back_populates="employer")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    # employer_id foreign key
    employer_id = Column(Integer, ForeignKey("employers.id"))
    # so the employer attribute is an Employer object
    employer = relationship("Employer", back_populates="jobs")
    applications = relationship("CandidateApplication", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_email = Column(String)
    password_hash = Column(String)
    role = Column(String, nullable=True)
    applications = relationship("CandidateApplication", back_populates="candidate")

class CandidateApplication(Base):
    __tablename__ = "candidate_applications"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    candidate = relationship("Candidate", back_populates="applications")
    job_id = Column(Integer, ForeignKey("jobs.id"))
    job = relationship("Job", back_populates="applications")