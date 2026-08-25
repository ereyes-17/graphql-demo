from functools import wraps

from graphql import GraphQLError

from app.util.requestcontext import get_authenticated_user


def admin_user(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = get_authenticated_user(info.context)

        if user.role != "admin":
            raise GraphQLError("Not authorized to perform this action")

        return func(root, info, *args, **kwargs)
    return wrapper

def authenticated_user(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        get_authenticated_user(info.context)
        return func(root, info, *args, **kwargs)
    return wrapper

def user_same_as_candidate(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = get_authenticated_user(info.context)
        candidate_id = kwargs.get("candidate_id") or args[0]

        if user.id != candidate_id:
            raise GraphQLError("Not authorized to perform this action")

        return func(root, info, *args, **kwargs)
    return wrapper