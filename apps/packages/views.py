from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from utils.api.pagination.page_number_pagination import CustomPageNumberPagination


from .models import Package, PackageOrder
from .serializers import PackageSerializer, PackageOrderSerializer, PackageOrderCreateSerializer

class PackageListView(generics.ListAPIView):
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sanatorium', 'is_featured', 'currency']
    search_fields = ['name', 'sanatorium__name']
    ordering_fields = ['name', 'original_price', 'discounted_price', 'created_at']
    ordering = ['-is_featured', '-created_at']
    pagination_class = CustomPageNumberPagination

class PackageDetailView(generics.RetrieveAPIView):
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    lookup_field = 'slug'

class PackageOrderListCreateView(generics.ListCreateAPIView):
    queryset = PackageOrder.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'package']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'check_in', 'check_out', 'total_price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PackageOrderCreateSerializer
        return PackageOrderSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsAdminUser()]
        return []

class PackageOrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PackageOrder.objects.all()
    serializer_class = PackageOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PackageOrderCreateSerializer
        return PackageOrderSerializer
