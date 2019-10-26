from rest_framework import serializers

from .models import Observation
from gatekeeper.models import Thing, Datastream


class ObservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Observation
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        """
        If there is select query params in the request. Select
        only the fields specified in the query params. E.g
        /api/observations?select=time,id,description is the request
        then return only time, id and description fields on the
        response. However, if there is no query params then default
        to the normal fields. i.e. __all__.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        select_query_params = request.query_params.get('select')
        if select_query_params:
            new_fields = {}
            query_params_list = select_query_params.split(',')
            for key in query_params_list:
                if key in self.fields.keys():
                    new_fields[key] = self.fields[key]
            self.fields = new_fields


class ThingSerializer(serializers.ModelSerializer):


    class Meta:
        model = Thing
        fields = '__all__'


class DatastreamSerializer(serializers.ModelSerializer):
    thing = ThingSerializer()


    class Meta:
        model = Datastream
        fields = '__all__'


class ObservationExpandedSerializer(ObservationSerializer):
    """
    This serializer class is almost identical to ObservationSerializer
    except for one difference. Instead of displaying datastream
    as integer, it expands the fields of the datastream.
    """
    datastream = DatastreamSerializer()


    class Meta:
        model = Observation
        fields = '__all__'
