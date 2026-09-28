# EVE Healthcare — Diagnostic Test Booking API

A Django REST API for diagnostic test bookings and simulated payments.

The project provides JWT-based authentication, diagnostic centres and tests,
test bookings, simulated payments, and an idempotent payment webhook with
HMAC signature verification.

## Features

- User signup and login
- JWT-based authentication
- Diagnostic centre and test management
- Authenticated diagnostic test bookings
- Booking status management
- Simulated payment processing
- Payment webhook with HMAC signature verification
- Idempotent webhook processing
- Payment and booking validation
- Automated tests for payment and webhook edge cases

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite
- HMAC-SHA256 for webhook signature verification

## Project Structure

```text
Medical-System/
│
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── diagnostics/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── bookings/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── payments/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md

Setup
1. Clone the repository
git clone https://github.com/NSrivastava1012/Medical-System.git
cd Medical-System
2. Create a virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file in the project root:

WEBHOOK_SECRET=medical-system-webhook-secret-123

The .env file is excluded from Git using .gitignore.

5. Run migrations
python manage.py migrate
6. Start the development server
python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/
Authentication APIs
Signup
POST /api/auth/signup/

Example:

{
    "username": "testuser",
    "password": "testpass123"
}
Login
POST /api/auth/login/

Example:

{
    "username": "testuser",
    "password": "testpass123"
}

The login response provides JWT access and refresh tokens.

For authenticated endpoints, send:

Authorization: Bearer <access_token>
Diagnostic APIs

Diagnostic centres and tests can be created and retrieved through the
diagnostics API.

Typical resources include:

/api/diagnostics/centres/
/api/diagnostics/tests/

A diagnostic test contains:

Diagnostic centre
Test name
Description
Price
Booking API

Authenticated users can create diagnostic test bookings.

POST /api/bookings/

Example:

{
    "test": 1,
    "appointment_datetime": "2026-10-10T10:00:00Z"
}

The authenticated user is automatically associated with the booking.

A booking contains:

Patient/user
Diagnostic test
Diagnostic centre through the selected test
Appointment date/time
Amount
Booking status

Supported booking states:

PENDING
CONFIRMED
FAILED
CANCELLED
Simulated Payment

The project uses a simulated payment service rather than a real payment
gateway.

POST /api/payments/

Example:

{
    "booking": 6
}

A successful payment creates a payment record and updates the booking to:

CONFIRMED

A failed payment updates the booking to:

FAILED

Each payment receives a unique transaction ID.

Payment Webhook

The simulated payment provider can send payment status updates through:

POST /api/payments/webhook/

Example request body:

{
    "event_id": "evt_7001",
    "booking_id": 7,
    "status": "SUCCESS",
    "transaction_id": "TXN-WEBHOOK-7001"
}

The webhook requires the following header:

X-Webhook-Signature: <HMAC-SHA256 signature>

The signature is generated using the configured WEBHOOK_SECRET and the
exact raw request body.

Webhook Idempotency

Each webhook contains a unique event_id.

Processed event IDs are stored in the WebhookEvent table.

If the same webhook is received again, the API returns a successful response
without creating another payment or changing the booking again.

This prevents duplicate payment processing.

Webhook Validation

The webhook handles:

Missing signatures
Invalid signatures
Invalid booking IDs
Duplicate webhook events
Duplicate payments
Duplicate transaction IDs
Invalid booking states
Successful payments
Failed payments
Database Design
DiagnosticCentre

Stores diagnostic centre information.

id
name
location
created_at
DiagnosticTest

Stores tests offered by diagnostic centres.

id
centre
name
description
price
created_at

Each diagnostic test belongs to one diagnostic centre.

Booking

Stores diagnostic test appointments.

id
user
test
appointment_datetime
amount
status
created_at
updated_at
Payment

Stores simulated payment information.

id
booking
amount
status
transaction_id
created_at

A booking can have at most one payment.

WebhookEvent

Stores processed webhook event IDs to provide idempotency.

id
event_id
created_at

event_id is unique.

Running Tests

Run the complete test suite with:

python manage.py test

The test suite covers payment and webhook scenarios including:

Valid webhook
Duplicate webhook
Invalid webhook signature
Missing webhook signature
Failed payment webhook
Important Assumptions
Payments are simulated and do not connect to a real payment provider.
Webhook authentication is handled using an HMAC-SHA256 signature.
JWT authentication is used for user-facing authenticated APIs.
A booking can have only one payment.
A webhook event can be processed only once.
Diagnostic test price is used as the booking amount.
The current implementation uses SQLite for local development.
Future Improvements

If more development time were available, the project could be extended with:

PostgreSQL for production deployment
Swagger/OpenAPI documentation
Docker and docker-compose
Redis caching
Celery background processing
Structured logging
API pagination
Rate limiting
Webhook retry handling
More comprehensive integration tests
Production deployment configuration
Testing Tools

The APIs can be tested using tools such as Thunder Client or Postman.

For webhook testing, the request body must remain unchanged when generating
the HMAC signature because the signature is calculated from the exact raw
request body.

Repository

GitHub:

https://github.com/NSrivastava1012/Medical-System