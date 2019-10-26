from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from .models import Observation
from .serializers import (
    ObservationExpandedSerializer,
    ObservationSerializer)


class ObservationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']

    def get_queryset(self):
        return Observation.objects.all()

    def get_serializer_class(self):
        query_params = self.request.query_params
        if query_params.get('expand') == 'Datastream':
            return ObservationExpandedSerializer
        return ObservationSerializer


class DatastreamObservationView(ListAPIView):
    """
    This view is for observations associated with certain
    datastream. So it lists observations for the given
    datasteam.
    """
    lookup_url_kwarg = 'datastream_id'

    def get_queryset(self):
        datastream_id = self.kwargs.get(self.lookup_url_kwarg)
        return Observation.objects.filter(datastream_id=datastream_id)

    def get_serializer_class(self):
        return ObservationSerializer
