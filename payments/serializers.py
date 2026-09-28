from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            'id',
            'booking',
            'amount',
            'status',
            'transaction_id',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'amount',
            'status',
            'transaction_id',
            'created_at',
        ]

class WebhookSerializer(serializers.Serializer):

    event_id = serializers.CharField(
        max_length=100
    )

    booking_id = serializers.IntegerField()

    status = serializers.ChoiceField(
        choices=['SUCCESS', 'FAILED']
    )

    transaction_id = serializers.CharField(
        max_length=100
    )