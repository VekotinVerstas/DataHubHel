from rest_framework import generics, permissions, serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from .authentication import SensorKeyAuthentication, SensorUser
from .ul20 import UltraLight20Parser, UltraLight20Renderer


class QueryParametersSerializer(serializers.Serializer):
    t = serializers.DateTimeField(
        label="time", help_text="timestamp", required=False)
    getCmd = serializers.BooleanField(  # noqa: N815
        default=True, initial=True, required=False,
        label="get_command", help_text="request for receive commands")


class SensorDataSerializer(serializers.Serializer):
    n = serializers.FloatField(
        label="level", help_text="sound pressure level")
    o = serializers.NullBooleanField(
        label="overload", help_text="overload", required=False)
    u = serializers.NullBooleanField(
        label="underrange", help_text="underrange", required=False)
    b = serializers.FloatField(
        label="battery", help_text="battery level", required=False)
    p = serializers.NullBooleanField(
        label="power", help_text="power supply status", required=False)
    w = serializers.FloatField(
        label="wifi_strength", help_text="wi-fi strength", required=False)
    m = serializers.FloatField(
        label="modem_strength", help_text="modem strength", required=False)
    s = serializers.CharField(
        label="laeq1s_registers", help_text="LAeq1s registers", required=False)


class Endpoint(generics.GenericAPIView):
    parser_classes = [
        UltraLight20Parser,
        FormParser,
        MultiPartParser,
    ]
    renderer_classes = [
        UltraLight20Renderer,
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    authentication_classes = [SensorKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SensorDataSerializer

    def post(self, request, format=None):
        params_parser = QueryParametersSerializer(data=request.query_params)
        params_parser.is_valid(raise_exception=True)
        params = params_parser.validated_data

        body_parser = self.get_serializer(data=request.data)
        body_parser.is_valid(raise_exception=True)
        data = body_parser.validated_data

        # TODO: Consume the sensor readings here

        # TODO: Remove the following debugging code
        print(params)
        print(data)
        assert isinstance(request.user, SensorUser)
        sensor = request.user.sensor
        print(sensor.pk, sensor.sensor_id, sensor)

        # TODO: Design how to implement sensor configuration changes
        if 0:
            return Response()
        else:
            # Parameters of the sensor can be changed in the response,
            # e.g. something like this (to set averaging time to 30 secs):
            return Response({
                '{.sensor_id}@setConfig'.format(sensor): 't=0030',
            })
