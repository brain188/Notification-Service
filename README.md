# Notification Service

A scalable, asynchronous notification service built with FastAPI, designed to handle email, SMS, and push notifications. It leverages Celery for background task processing, SQLAlchemy for database interactions, and Prometheus for metrics monitoring.

## Features

- **Multi-Channel Notifications**: Support for email (SendGrid), SMS (Twilio), and push notifications (Firebase).
- **Asynchronous Processing**: Uses Celery with Redis/RabbitMQ for queuing and retrying failed notifications.
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic for migrations.
- **Rate Limiting**: Implemented with SlowAPI to prevent abuse.
- **Authentication**: Placeholder JWT-based authentication.
- **Metrics and Monitoring**: Prometheus integration for application metrics.
- **Webhooks**: Handles status updates from external services.
- **Docker Support**: Containerized for easy deployment.
- **Testing**: Comprehensive test suite with pytest.

## Prerequisites

- Python 3.12+
- PostgreSQL database
- Redis or RabbitMQ for Celery broker
- API keys for SendGrid, Twilio, and Firebase
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/brain188/Notification-Service.git
   cd Backend/Notification_Service
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Ensure PostgreSQL is running.
   - Run Alembic migrations:
     ```bash
     alembic upgrade head
     ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/notification_db
RABBITMQ_BROKER_URL=amqp://guest:guest@localhost:5672//
REDIS_URL=redis://localhost:6379/0
SENDGRID_API_KEY=your_sendgrid_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
FIREBASE_CREDENTIALS_PATH=path/to/firebase/credentials.json
DEFAULT_FROM_EMAIL=your_default_email@example.com
SECRET_KEY=your_secret_key_for_jwt
LOG_LEVEL=INFO
```

## Running the Application

### Locally

1. Start Celery worker:
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the API at `http://localhost:8000`.

### With Docker

1. Build the Docker image:
   ```bash
   docker build -t notification-service .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env notification-service
   ```

## API Endpoints

- `GET /`: Health check endpoint.
- `POST /api/v1/notifications/trigger`: Trigger a notification (requires auth, rate-limited).
- `GET /api/v1/notifications/reports/{event_id}`: Get notification report (requires auth).
- `POST /api/v1/notifications/webhook`: Handle webhook for status updates.


## Testing

Run the test suite with pytest:

```bash
pytest
```

Tests include unit tests for services, repositories, and API endpoints, using pytest-asyncio for async support.

## Deployment

- Use the provided Dockerfile for containerization.
- Deploy to cloud platforms like AWS, GCP, or Azure.
- Ensure environment variables are set securely.
- Monitor with Prometheus and Grafana.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -am 'Add your feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.