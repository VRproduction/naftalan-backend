from django.urls import path
from . import views


urlpatterns = [
    path('', views.SanatoriumListView.as_view(), name='sanatoriums'),
    path('naftalan-page/', views.NaftalanSanatoriumsPageView.as_view(), name='naftalan-sanatoriums'),
    path('other-cities-page/', views.OtherCitiesSanatoriumsPageView.as_view(), name='other-cities-sanatoriums'),
    path('naftalan-sanatoriums/', views.NaftalanSanatoriums.as_view(), name='naftalan-sanatoriums'),
    path('other-cities-sanatoriums/', views.OtherCitiesSanatoriums.as_view(), name='other-cities-sanatoriums'),
    path('locations/', views.LocationListView.as_view(), name='locations'),
    path('currencies/', views.CurrencyListView.as_view(), name='currencies'),
    path('seasons/', views.SeasonListView.as_view(), name='seasons'),
    path('age-groups/', views.AgeGroupListView.as_view(), name='age-groups'),
    path('treatment-options/', views.TreatmentOptionListView.as_view(), name='treatment-options'),
    path('room-types/', views.RoomTypeListView.as_view(), name='room-types'),
    path('room-types/<int:pk>/', views.RoomTypeDetailView.as_view(), name='room-type-detail'),
    path('room-prices/', views.RoomPriceListView.as_view(), name='room-prices'),
    path('<slug:slug>/', views.SanatoriumDetailView.as_view(), name='sanatorium-detail'),
]