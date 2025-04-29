from django.urls import path
from .views import (
    PackageListView,
    PackageDetailView,
    PackageOrderListCreateView,
    PackageOrderRetrieveUpdateDestroyView
)

app_name = 'packages'

urlpatterns = [
    path('', PackageListView.as_view(), name='package-list'),
    path('<slug:slug>/', PackageDetailView.as_view(), name='package-detail'),
    path('orders/', PackageOrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', PackageOrderRetrieveUpdateDestroyView.as_view(), name='order-detail'),
]
