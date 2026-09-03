
from fastapi import FastAPI
from graphene import Schema
from starlette_graphene3 import GraphQLApp, make_playground_handler

from app.db.database import init_db, seed_database
from app.gql.mutations import Mutation
from app.gql.queries import Query

schema = Schema(query=Query, mutation=Mutation)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()
    seed_database()

@app.get("/health")
def get_employers():
    return "I will survive!"

app.mount("/graphql", GraphQLApp(schema=schema, on_get=make_playground_handler()))