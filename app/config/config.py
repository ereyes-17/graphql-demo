import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", None)
DB_PASSWORD = os.environ.get("DB_PASSWORD", None)
DB_NAME = os.environ.get("DB_NAME", "graphql_db")
DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SECRET_KEY = "building-graphql-api-key" # TODO: alternative solutions to jwt secret key
ALGORITHM = "HS256"
TOKEN_EXP_IN_MINUTES = 15 # TODO: make configurable