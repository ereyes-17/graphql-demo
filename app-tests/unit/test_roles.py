from unittest.mock import Mock, patch

import pytest
from graphql import GraphQLError

from app.util.roles import admin_user, authenticated_user, user_same_as_candidate


@pytest.fixture
def mock_get_user():
    with patch("app.util.roles.get_authenticated_user") as m:
        yield m


def test_admin_user_allows_admin(mock_get_user):
    mock_get_user.return_value = Mock(role="admin")

    @admin_user
    def resolver(root, info):
        return "success"

    assert resolver(None, Mock()) == "success"


def test_admin_user_rejects_non_admin(mock_get_user):
    mock_get_user.return_value = Mock(role="user")

    @admin_user
    def resolver(root, info):
        return "success"

    with pytest.raises(GraphQLError, match="Not authorized to perform this action"):
        resolver(None, Mock())


def test_authenticated_user_allows_valid_user(mock_get_user):
    mock_get_user.return_value = Mock()

    @authenticated_user
    def resolver(root, info):
        return "success"

    assert resolver(None, Mock()) == "success"


def test_user_same_as_candidate_allows_matching_id(mock_get_user):
    mock_get_user.return_value = Mock(id=42)

    @user_same_as_candidate
    def resolver(root, info, candidate_id):
        return "success"

    assert resolver(None, Mock(), candidate_id=42) == "success"


def test_user_same_as_candidate_rejects_mismatched_id(mock_get_user):
    mock_get_user.return_value = Mock(id=42)

    @user_same_as_candidate
    def resolver(root, info, candidate_id):
        return "success"

    with pytest.raises(GraphQLError, match="Not authorized to perform this action"):
        resolver(None, Mock(), candidate_id=99)