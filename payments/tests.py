from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
import hmac
import hashlib
import json

from bookings.models import Booking
from diagnostics.models import DiagnosticCentre, DiagnosticTest
from payments.models import Payment


class PaymentWebhookTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # Create diagnostic centre first
        self.centre = DiagnosticCentre.objects.create(
            name="Test Diagnostic Centre",
            location="Test Location"
        )

        # Create diagnostic test linked to centre
        self.test = DiagnosticTest.objects.create(
            centre=self.centre,
            name="Blood Test",
            description="Basic blood test",
            price=500
        )

        self.booking = Booking.objects.create(
            user=self.user,
            test=self.test,
            appointment_datetime="2026-10-01T10:00:00Z",
            amount=500,
            status=Booking.Status.PENDING
        )

        self.secret = "medical-system-webhook-secret-123"

    def generate_signature(self, data):
        body = json.dumps(
            data,
            separators=(",", ":")
        )

        signature = hmac.new(
            self.secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature, body

    def test_valid_webhook(self):

        data = {
            "event_id": "test-event-1",
            "booking_id": self.booking.id,
            "status": "SUCCESS",
            "transaction_id": "TXN-TEST-001"
        }

        signature, body = self.generate_signature(data)

        response = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE=signature
        )

        self.assertEqual(response.status_code, 200)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED
        )

        self.assertTrue(
            Payment.objects.filter(
                transaction_id="TXN-TEST-001"
            ).exists()
        )

    def test_duplicate_webhook(self):

        data = {
            "event_id": "test-event-2",
            "booking_id": self.booking.id,
            "status": "SUCCESS",
            "transaction_id": "TXN-TEST-002"
        }

        signature, body = self.generate_signature(data)

        # First request
        response1 = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE=signature
        )

        self.assertEqual(response1.status_code, 200)

        # Second request with the exact same event
        response2 = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE=signature
        )

        self.assertEqual(response2.status_code, 200)

        self.assertEqual(
            response2.data["message"],
            "Webhook already processed."
        )

        # Only one payment should exist
        self.assertEqual(
            Payment.objects.filter(
                transaction_id="TXN-TEST-002"
            ).count(),
            1
        )

    def test_invalid_webhook_signature(self):

        data = {
            "event_id": "test-event-3",
            "booking_id": self.booking.id,
            "status": "SUCCESS",
            "transaction_id": "TXN-TEST-003"
        }

        _, body = self.generate_signature(data)

        response = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE="invalid-signature"
        )

        self.assertEqual(
            response.status_code,
            401
        )

        self.assertEqual(
            response.data["error"],
            "Invalid webhook signature."
        )

        # No payment should have been created
        self.assertFalse(
            Payment.objects.filter(
                transaction_id="TXN-TEST-003"
            ).exists()
        )

    def test_missing_webhook_signature(self):

        data = {
            "event_id": "test-event-4",
            "booking_id": self.booking.id,
            "status": "SUCCESS",
            "transaction_id": "TXN-TEST-004"
        }

        _, body = self.generate_signature(data)

        response = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            401
        )

        self.assertEqual(
            response.data["error"],
            "Missing webhook signature."
        )

        self.assertFalse(
            Payment.objects.filter(
                transaction_id="TXN-TEST-004"
            ).exists()
        )

    def test_failed_webhook(self):

        data = {
            "event_id": "test-event-5",
            "booking_id": self.booking.id,
            "status": "FAILED",
            "transaction_id": "TXN-TEST-005"
        }

        signature, body = self.generate_signature(data)

        response = self.client.post(
            "/api/payments/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE=signature
        )

        self.assertEqual(response.status_code, 200)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.FAILED
        )

        payment = Payment.objects.get(
            transaction_id="TXN-TEST-005"
        )

        self.assertEqual(
            payment.status,
            Payment.Status.FAILED
        )