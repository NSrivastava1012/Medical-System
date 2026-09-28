from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    centre = serializers.CharField(
        source='test.centre.name',
        read_only=True
    )

    test_name = serializers.CharField(
        source='test.name',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'test',
            'test_name',
            'centre',
            'appointment_datetime',
            'amount',
            'status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'amount',
            'status',
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        appointment_datetime = data.get('appointment_datetime')

        if appointment_datetime:
            from django.utils import timezone

            if appointment_datetime <= timezone.now():
                raise serializers.ValidationError(
                    "Appointment date and time must be in the future."
                )

        return data