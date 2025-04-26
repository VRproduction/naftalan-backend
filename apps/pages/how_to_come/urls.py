from django.urls import path
from . import views


urlpatterns = [
    path('hero/', views.HeroView.as_view(), name='hero'),
    path('location/', views.LocationView.as_view(), name='location'),
    path('transport-option-section/', views.TransportOptionSectionView.as_view(), name='transport-option-section'),
    path('visa-section/', views.VisaSectionView.as_view(), name='visa-section'),
]