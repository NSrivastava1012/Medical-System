from django.urls import path

from .views import (
    DiagnosticCentreListCreateView,
    DiagnosticCentreDetailView,
    DiagnosticTestListCreateView,
    DiagnosticTestDetailView,
)


urlpatterns = [
    path(
        'centres/',
        DiagnosticCentreListCreateView.as_view(),
        name='centre-list-create'
    ),
    path(
        'centres/<int:pk>/',
        DiagnosticCentreDetailView.as_view(),
        name='centre-detail'
    ),
    path(
        'tests/',
        DiagnosticTestListCreateView.as_view(),
        name='test-list-create'
    ),
    path(
        'tests/<int:pk>/',
        DiagnosticTestDetailView.as_view(),
        name='test-detail'
    ),
]