from django.urls import path
from . import views


urlpatterns = [
    path('availability/', views.AvailabilityCheckView.as_view(), name='availability-check'),
    path('calculate-price/', views.PriceCalculatorView.as_view(), name='calculate-price'),
    path('create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('list/', views.BookingListView.as_view(), name='booking-list'),
    path('<str:booking_reference>/', views.BookingDetailView.as_view(), name='booking-detail'),
]