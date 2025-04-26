from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import (
    Hero,
    Location,
    TransportOptionSection,
    VisaSection
)
from .serializers import (
    HeroSerializer,
    LocationSerializer,
    TransportOptionSectionSerializer,
    VisaSectionSerializer
)


class HeroView(RetrieveAPIView):
    serializer_class = HeroSerializer

    def get_object(self):
        return Hero.objects.first()

class LocationView(RetrieveAPIView):
    serializer_class = LocationSerializer

    def get_object(self):
        return Location.objects.first()

class TransportOptionSectionView(RetrieveAPIView):
    serializer_class = TransportOptionSectionSerializer

    def get_object(self):
        return TransportOptionSection.objects.first()


class VisaSectionView(RetrieveAPIView):
    serializer_class = VisaSectionSerializer

    def get_object(self):
        return VisaSection.objects.first()
