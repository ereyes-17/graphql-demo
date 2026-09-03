from unittest.mock import MagicMock, Mock, patch

import pytest
from graphql import GraphQLError

from app.util.requestcontext import get_authenticated_user


@pytest.fixture
def valid_context():
    return {
        "request": Mock(
            headers = {
                "Authorization": "Bearer jwtToken"
            }
        )
    }

@pytest.fixture
def invalid_context():
    return {
        "request": Mock(
            headers = {
                "Authorization": "Bearer"
            }
        )
    }

# fake validate_token result
@patch("app.util.requestcontext.validate_token")
# fake Session obj
@patch("app.util.requestcontext.Session")
def test_get_authenticated_user_returns_user(mock_session: MagicMock, mock_validate_token: MagicMock, valid_context: dict[str, Mock]):
    # pytest passes the mocked objects based on how the names. ex: Session -> mock_session
    
    # setup mocking rules
    user = Mock()
    user.role = "user"

    # direct result of validate_token we want for this test
    mock_validate_token.return_value = {"sub": "user@example.com"}
    # direct result of querying for the user - the query the target function is expected to call
    # we have to use 'return_value' for each stub
    mock_session.return_value.query.return_value.filter.return_value.first.return_value = user

    # call the target function
    result = get_authenticated_user(valid_context)

    # validate
    assert result == user
    mock_validate_token.assert_called_once_with("jwtToken")
    mock_session.return_value.query.assert_called_once()

@patch("app.util.requestcontext.validate_token")
@patch("app.util.requestcontext.Session")
def test_get_authenticated_user_raises_user_exception(mock_session: MagicMock, mock_validate_token: MagicMock, valid_context: dict[str, Mock]):
    mock_validate_token.return_value = {"sub": "unknown-user@example.com"}
    mock_session.return_value.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(GraphQLError, match="Could not authenticate user"):
        get_authenticated_user(valid_context)

# for this test, the code won't hit the session or token logic due to invalid context passed in
def test_get_authenticated_user_raises_invalid_context_exception(invalid_context: dict[str, Mock]):
    with pytest.raises(GraphQLError, match="Missing bearer token"):
        get_authenticated_user(invalid_context)