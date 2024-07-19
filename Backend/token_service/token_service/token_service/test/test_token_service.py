import pytest
import json
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken
from token_app.views import CustomTokenObtainPairView

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
    }

@pytest.fixture
def request_factory(): 
    """
    This is a fixture that returns a RequestFactory object.
    This is a Django object that allows you to create mock requests.
    This is useful for testing views.
    """
    from django.test import RequestFactory
    return RequestFactory()

def test_handle_token_request(mocker, user_data):
    # Mock the publish_message function
    publish_message_mock = mocker.patch('token_app.views.publish_message')
    
    # Prepare the message body
    message_body = json.dumps(user_data)
    
    # Mock RefreshToken to return a fixed value
    with patch('rest_framework_simplejwt.tokens.RefreshToken.for_user') as mock_for_user:
        mock_refresh_token = MagicMock()
        mock_refresh_token.__str__.return_value = 'fixed-refresh-token'
        mock_refresh_token.access_token = 'fixed-access-token'
        mock_for_user.return_value = mock_refresh_token
        
        # Call the handle_token_request method directly
        CustomTokenObtainPairView.handle_token_request(None, None, None, message_body)
    
    # Assert the publish_message was called with correct arguments
    expected_refresh_token = 'fixed-refresh-token'
    expected_access_token = 'fixed-access-token'
    
    publish_message_mock.assert_called_once_with(
        "user_token_response_queue",
        json.dumps({"refresh": expected_refresh_token, "access": expected_access_token})
    )

def test_start_consumer(mocker):
    # Mock the consume_message function
    consume_message_mock = mocker.patch('token_app.views.consume_message')
    
    # Create a test instance of the view
    view = CustomTokenObtainPairView()
    
    # Call the start_consumer method
    view.start_consumer()
    
    # Assert the consume_message was called with correct arguments
    consume_message_mock.assert_called_once_with("user_token_request_queue", view.handle_token_request)
