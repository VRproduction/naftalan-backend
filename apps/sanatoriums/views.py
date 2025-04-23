from django.shortcuts import render
from rest_framework import generics, filters, status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import (
    Location, Sanatorium, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage
    )
from .serializers import (
    LocationSerializer, SanatoriumSerializer, 
    SanatoriumListSerializer, NaftalanSanatoriumsPageSerializer, OtherCitiesSanatoriumsPageSerializer
)
from utils.api.pagination.page_number_pagination import CustomPageNumberPagination


# Create your views here.

class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['region', 'country']

class SanatoriumListView(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True)
    serializer_class = SanatoriumListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'location_type', 'in_home']
    search_fields = ['name', 'short_description', 'address']
    ordering_fields = ['rating', 'price', 'created_at']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        location_type = self.request.query_params.get('location_type', None)
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        return queryset

class SanatoriumDetailView(generics.RetrieveAPIView):
    queryset = Sanatorium.objects.filter(is_active=True)
    serializer_class = SanatoriumSerializer
    lookup_field = 'slug'


class NaftalanSanatoriumsPageView(generics.RetrieveAPIView):
    serializer_class = NaftalanSanatoriumsPageSerializer

    def get_object(self):
        return NaftalanSanatoriumsPage.objects.first()

class OtherCitiesSanatoriumsPageView(generics.RetrieveAPIView):
    serializer_class = OtherCitiesSanatoriumsPageSerializer

    def get_object(self):
        return OtherCitiesSanatoriumsPage.objects.first()


class NaftalanSanatoriums(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True, location_type='naftalan')
    serializer_class = SanatoriumListSerializer


class OtherCitiesSanatoriums(generics.ListAPIView):
    queryset = Sanatorium.objects.filter(is_active=True, location_type='other_cities')
    serializer_class = SanatoriumListSerializer