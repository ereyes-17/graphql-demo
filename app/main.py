
from fastapi import FastAPI
from graphene import Schema
from starlette_graphene3 import GraphQLApp, make_playground_handler

from app.db.database import Session, seed_database
from app.db.models import Employer, Job
from app.gql.mutations import Mutation
from app.gql.queries import Query

schema = Schema(query=Query, mutation=Mutation)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    seed_database()

@app.get("/employers")
def get_employers():
    session = Session()
    employers = session.query(Employer).all()
    session.close()

    return employers

@app.get("/jobs")
def get_jobs():
    session = Session()
    jobs = session.query(Job).all()
    session.close()

    return jobs

app.mount("/graphql", GraphQLApp(schema=schema, on_get=make_playground_handler()))