import unittest

# TODO: Test exceptions like JWT expiration
from app.util.jwtutil import generate_token, validate_token


class TestJwtUtil(unittest.TestCase):
    def test_generate_token(self):
        contact_email = "admin@example.com"

        result = generate_token(contact_email=contact_email)

        self.assertIsNotNone(result)

    def test_validate_token(self):
        contact_email = "admin@example.com"
        
        token = generate_token(contact_email=contact_email)

        result = validate_token(token=token)

        self.assertEqual(result["sub"], contact_email)
        self.assertTrue(type(result["exp"]) == int)
