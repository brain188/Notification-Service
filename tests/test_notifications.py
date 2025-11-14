import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.workers.tasks import send_notification
from unittest.mock import patch

client = TestClient(app)

@pytest.mark.asyncio
async def test_trigger_notification():
    response = client.post("/api/v1/notifications/trigger", json={
        "event_type": "test",
        "channel": "email",
        "recipient": "test@example.com",
        "content": "Hello"
    }, headers={"Authorization": "Bearer valid_token"})  # Mock auth
    assert response.status_code == 202

@patch("app.services.email.send_email")
@pytest.mark.asyncio
async def test_send_task(mock_send):
    mock_send.return_value = True
    result = await send_notification({"channel": "email", "recipient": "test", "content": "Hello", "event_type": "test"})
    assert result is True