from rest_framework import generics

from .models import Airplane
from .serializers import (
    AirplaneSerializer,
)


class AirplaneCreateAPIView(generics.CreateAPIView):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirplaneUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    lookup_field = 'airplane_id'


class AirlineAPIView(generics.ListAPIView):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
