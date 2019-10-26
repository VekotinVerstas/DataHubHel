from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DatastreamObservationView,
    ObservationViewSet
)

app_name = 'sta'
router = DefaultRouter(trailing_slash=False)

router.register('observations', ObservationViewSet, basename='observation')

urlpatterns = [
    path(
        '<int:datastream_id>/observations',
        DatastreamObservationView.as_view(),
        name='datastream-observation'
    )
]+ router.urls
