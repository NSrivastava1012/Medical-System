from rest_framework import serializers

from .models import DiagnosticCentre, DiagnosticTest


class DiagnosticTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiagnosticTest
        fields = [
            'id',
            'name',
            'description',
            'price',
            'centre',
            'created_at'
        ]


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    tests = DiagnosticTestSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosticCentre
        fields = [
            'id',
            'name',
            'location',
            'tests',
            'created_at'
        ]