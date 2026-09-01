import unittest
from unittest.mock import Mock

"""from app.util.requestcontext import (
    get_authenticated_user
)
from app.util.jwtutil import generate_token"""

class TestRequestContext(unittest.TestCase):
    # copy and modify as needed
    context = {
        "request": Mock(
            headers = {
                "Authorization": "Bearer <token>"
            }
        )
    }
    def test_get_authenticated_user(self):
        # TODO: What do I need to make sure database utilities provided for this tes?
        # TODO: Need a candidate created
        # TODO: Need to generate token
        pass