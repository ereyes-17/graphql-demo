from app.util.jwtutil import validate_token
from app.db.database import Session
from app.db.models import Candidate
from graphql import GraphQLError

def get_authenticated_user(context) -> Candidate:
    request_object = context.get('request')
    auth_header = request_object.headers.get('Authorization')

    auth_value = [None]
    if auth_header:
        auth_value = auth_header.split(" ")

    if auth_header and auth_value[0] == "Bearer" and len(auth_value) == 2:
        token = auth_header.split(" ")[1]

        payload = validate_token(token)

        
        session = Session()
        user = session.query(Candidate).filter(payload.get('sub') == Candidate.contact_email).first()

        if not user:
            raise GraphQLError("Could not authenticate user")

        return user
    else:
        raise GraphQLError("Missing bearer token")