import pytest
from app.repositories.notification_repo import NotificationRepo
from app.models.notifications import Notification


@pytest.mark.asyncio
async def test_create_and_retrieve(db_session):
    payload = {
        "event_type": "repo_test",
        "channel": "email",
        "recipient": "repo@example.com",
        "content": "Repo test",
    }
    await NotificationRepo.create(db_session, payload)

    fetched = await NotificationRepo.get_by_event_id(db_session, "repo_test")
    assert fetched is not None
    assert fetched.event_type == "repo_test"
    assert fetched.status == "pending"


@pytest.mark.asyncio
async def test_update_status(db_session):
    # Insert
    notif = Notification(
        event_type="status_test",
        channel="sms",
        recipient="+999",
        content="Status",
        status="pending",
    )
    db_session.add(notif)
    await db_session.commit()

    # Update
    await NotificationRepo.update_status(db_session, "status_test", "delivered")

    updated = await NotificationRepo.get_by_event_id(db_session, "status_test")
    assert updated.status == "delivered"