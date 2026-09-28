import uuid
import hashlib
import hmac

from django.conf import settings
from django.db import transaction
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from bookings.models import Booking
from .models import Payment, WebhookEvent
from .serializers import PaymentSerializer, WebhookSerializer


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):

        booking_id = self.request.data.get('booking')

        try:
            booking = Booking.objects.select_for_update().get(
                id=booking_id,
                user=self.request.user
            )
        except Booking.DoesNotExist:
            raise serializers.ValidationError(
                "Booking not found."
            )

        # Check if payment already exists
        if Payment.objects.filter(
            booking=booking
        ).exists():

            raise serializers.ValidationError(
                "Payment already exists for this booking."
            )

        # Booking must be pending
        if booking.status != Booking.Status.PENDING:
            raise serializers.ValidationError(
                f"Booking is already {booking.status}."
            )

        # Simulate payment result
        payment_success = True

        if payment_success:
            payment_status = Payment.Status.SUCCESS
            booking_status = Booking.Status.CONFIRMED
        else:
            payment_status = Payment.Status.FAILED
            booking_status = Booking.Status.FAILED

        # Generate transaction ID
        transaction_id = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        # Create payment
        serializer.save(
            booking=booking,
            amount=booking.amount,
            status=payment_status,
            transaction_id=transaction_id
        )

        # Update booking status
        booking.status = booking_status

        booking.save(
            update_fields=[
                'status',
                'updated_at'
            ]
        )


class PaymentWebhookView(generics.GenericAPIView):
    serializer_class = WebhookSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):

        # Verify webhook signature
        received_signature = request.headers.get('X-Webhook-Signature')

        if not received_signature:
            return Response(
                {
                    "error": "Missing webhook signature."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        expected_signature = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            received_signature,
            expected_signature
        ):
            return Response(
                {
                    "error": "Invalid webhook signature."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        event_id = serializer.validated_data['event_id']
        booking_id = serializer.validated_data['booking_id']
        payment_status = serializer.validated_data['status']
        transaction_id = serializer.validated_data['transaction_id']

        # --------------------------------
        # 1. Idempotency check
        # --------------------------------

        if WebhookEvent.objects.filter(
            event_id=event_id
        ).exists():

            return Response(
                {
                    "message": "Webhook already processed.",
                    "event_id": event_id
                },
                status=status.HTTP_200_OK
            )

        # --------------------------------
        # 2. Find booking
        # --------------------------------

        try:
            booking = Booking.objects.select_for_update().get(
                id=booking_id
            )

        except Booking.DoesNotExist:

            raise serializers.ValidationError(
                "Booking not found."
            )

        # --------------------------------
        # 3. Booking must be pending
        # --------------------------------

        if booking.status != Booking.Status.PENDING:

            raise serializers.ValidationError(
                f"Booking is already {booking.status}."
            )

        # --------------------------------
        # 4. Check existing payment
        # --------------------------------

        if Payment.objects.filter(
            booking=booking
        ).exists():

            raise serializers.ValidationError(
                "Payment already exists for this booking."
            )

        # --------------------------------
        # 5. Check duplicate transaction
        # --------------------------------

        if Payment.objects.filter(
            transaction_id=transaction_id
        ).exists():

            raise serializers.ValidationError(
                "Transaction has already been processed."
            )

        # --------------------------------
        # 6. Store webhook event
        # --------------------------------

        WebhookEvent.objects.create(
            event_id=event_id
        )

        # --------------------------------
        # 7. Create payment
        # --------------------------------

        Payment.objects.create(
            booking=booking,
            amount=booking.amount,
            status=payment_status,
            transaction_id=transaction_id
        )

        # --------------------------------
        # 8. Update booking
        # --------------------------------

        if payment_status == Payment.Status.SUCCESS:

            booking.status = Booking.Status.CONFIRMED

        else:

            booking.status = Booking.Status.FAILED

        booking.save(
            update_fields=[
                'status',
                'updated_at'
            ]
        )

        # --------------------------------
        # 9. Return response
        # --------------------------------

        return Response(
            {
                "message": "Webhook processed successfully.",
                "event_id": event_id,
                "booking_id": booking.id,
                "booking_status": booking.status
            },
            status=status.HTTP_200_OK
        )