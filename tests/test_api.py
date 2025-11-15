import json
from http import HTTPStatus

import pytest
from fastapi import HTTPException

from app.schemas.notification import NotificationCreate
from app.repositories.notification_repo import NotificationRepo
from app.models.notifications import Notification


# Trigger endpoint
def test_trigger_notification_success(
    client, auth_headers, notification_payload, mocker
):
    # Mock Celery delay so we don't need a real broker
    mock_delay = mocker.patch("app.workers.tasks.send_notification.delay")
    response = client.post(
        "/api/v1/notifications/trigger",
        json=notification_payload,
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json() == {"message": "Notification queued"}
    mock_delay.assert_called_once_with(notification_payload)


def test_trigger_missing_auth(client, notification_payload):
    response = client.post(
        "/api/v1/notifications/trigger", json=notification_payload
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_trigger_invalid_channel(client, auth_headers, notification_payload):
    payload = notification_payload.copy()
    payload["channel"] = "invalid"
    response = client.post(
        "/api/v1/notifications/trigger", json=payload, headers=auth_headers
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_trigger_rate_limit(client, auth_headers, notification_payload, mocker):
    mocker.patch("app.workers.tasks.send_notification.delay")
    # Send 11 requests – limiter is 10/minute
    for _ in range(10):
        r = client.post(
            "/api/v1/notifications/trigger",
            json=notification_payload,
            headers=auth_headers,
        )
        assert r.status_code == HTTPStatus.ACCEPTED

    r = client.post(
        "/api/v1/notifications/trigger",
        json=notification_payload,
        headers=auth_headers,
    )
    assert r.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert "rate limit" in r.json()["detail"].lower()



# 2. Report endpoint
@pytest.mark.asyncio
async def test_get_report_not_found(client, auth_headers, db_session):
    response = client.get(
        "/api/v1/notifications/reports/unknown_event", headers=auth_headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_report_success(
    client, auth_headers, notification_payload, db_session, mocker
):

    # Insert a record directly
    notif = Notification(**notification_payload, status="sent", attempts=1)
    db_session.add(notif)
    await db_session.commit()
    await db_session.refresh(notif)

    response = client.get(
        f"/api/v1/notifications/reports/{notification_payload['event_type']}",
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["event_type"] == notification_payload["event_type"]
    assert data["status"] == "sent"



# 3. Webhook endpoint
@pytest.mark.asyncio
async def test_webhook_updates_status(
    client, notification_payload, db_session, mocker
):

    # Pre-populate DB
    notif = Notification(**notification_payload, status="pending")
    db_session.add(notif)
    await db_session.commit()

    webhook_payload = {
        "event_id": notification_payload["event_type"],
        "status": "delivered",
    }
    response = client.post("/api/v1/notifications/webhook", json=webhook_payload)
    assert response.status_code == HTTPStatus.OK

    # Verify DB update
    updated = await NotificationRepo.get_by_event_id(
        db_session, notification_payload["event_type"]
    )
    assert updated.status == "delivered"