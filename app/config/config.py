import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_URL = f"postgresql+psycopg://postgres:postgres@{DB_HOST}:5432/graphql_db"
SECRET_KEY = "building-graphql-api-key"
ALGORITHM = "HS256"
TOKEN_EXP_IN_MINUTES = 15