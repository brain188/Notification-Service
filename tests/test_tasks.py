import pytest
from unittest.mock import AsyncMock, patch

from app.workers.tasks import send_notification
from app.workers.celery_app import celery_app
from app.models.notifications import Notification
from app.repositories.notification_repo import NotificationRepo


# Helper to insert a notification record 
async def _insert_pending(db_session, payload):

    notif = Notification(**payload, status="pending", attempts=0)
    db_session.add(notif)
    await db_session.commit()
    await db_session.refresh(notif)
    return notif


# 1. Email path – success
@pytest.mark.asyncio
@patch("app.services.email.send_email", new_callable=AsyncMock)
async def test_email_success(mock_send_email, db_session):
    mock_send_email.return_value = True
    payload = {
        "event_type": "email_test",
        "channel": "email",
        "recipient": "a@b.c",
        "content": "Hi",
    }

    await _insert_pending(db_session, payload)

    # Run task (eager mode)
    await send_notification(payload)

    mock_send_email.assert_awaited_once_with("a@b.c", "Hi")
    repo = await NotificationRepo.get_by_event_id(db_session, "email_test")
    assert repo.status == "sent"
    assert repo.attempts == 1


# 2. Email path – failure → retry → final failure
@pytest.mark.asyncio
@patch("app.services.email.send_email", new_callable=AsyncMock)
async def test_email_retry_exhaust(mock_send_email, db_session, mocker):
    mock_send_email.side_effect = [False, False, False]  # always fail

    payload = {
        "event_type": "email_retry",
        "channel": "email",
        "recipient": "x@y.z",
        "content": "Retry me",
    }
    await _insert_pending(db_session, payload)

    # Patch Celery retry to raise MaxRetriesExceededError after 3 attempts
    with patch.object(send_notification, "retry", side_effect=send_notification.MaxRetriesExceededError):
        with pytest.raises(send_notification.MaxRetriesExceededError):
            await send_notification.bind(celery_app).apply_async(args=(payload,))

    repo = await NotificationRepo.get_by_event_id(db_session, "email_retry")
    assert repo.status == "failed"
    assert repo.attempts == 3


# 3. SMS path
@pytest.mark.asyncio
@patch("app.services.sms.send_sms", new_callable=AsyncMock)
async def test_sms_success(mock_send_sms, db_session):
    mock_send_sms.return_value = True
    payload = {
        "event_type": "sms_test",
        "channel": "sms",
        "recipient": "+1234567890",
        "content": "SMS",
    }
    await _insert_pending(db_session, payload)

    await send_notification(payload)

    mock_send_sms.assert_awaited_once()
    repo = await NotificationRepo.get_by_event_id(db_session, "sms_test")
    assert repo.status == "sent"


# 4. Push path
@pytest.mark.asyncio
@patch("app.services.push.send_push", new_callable=AsyncMock)
async def test_push_success(mock_send_push, db_session):
    mock_send_push.return_value = True
    payload = {
        "event_type": "push_test",
        "channel": "push",
        "recipient": "device-token-123",
        "content": "Push",
    }
    await _insert_pending(db_session, payload)

    await send_notification(payload)

    mock_send_push.assert_awaited_once()
    repo = await NotificationRepo.get_by_event_id(db_session, "push_test")
    assert repo.status == "sent"


# 5. Invalid channel
@pytest.mark.asyncio
async def test_invalid_channel(db_session):
    payload = {
        "event_type": "bad",
        "channel": "fax",
        "recipient": "123",
        "content": "Nope",
    }
    await _insert_pending(db_session, payload)

    with pytest.raises(ValueError, match="Invalid channel"):
        await send_notification(payload)

    repo = await NotificationRepo.get_by_event_id(db_session, "bad")
    assert repo.status == "pending"  # task never updates on exception