from datetime import datetime, timedelta, timezone

import jwt
from graphql import GraphQLError

from app.config.config import ALGORITHM, SECRET_KEY, TOKEN_EXP_IN_MINUTES


def generate_token(contact_email):
    payload = {
        "sub": contact_email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXP_IN_MINUTES)
    }

    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
            raise GraphQLError("Token has expired")

        return payload
        
    except jwt.exceptions.PyJWTError:
        raise GraphQLError("Token invalid")