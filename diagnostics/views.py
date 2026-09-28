from rest_framework import generics

from .models import DiagnosticCentre, DiagnosticTest
from .serializers import (
    DiagnosticCentreSerializer,
    DiagnosticTestSerializer
)


class DiagnosticCentreListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer


class DiagnosticCentreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer


class DiagnosticTestListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer


class DiagnosticTestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer