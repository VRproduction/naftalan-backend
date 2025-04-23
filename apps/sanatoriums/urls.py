from django.urls import path
from . import views


urlpatterns = [
    path('', views.SanatoriumListView.as_view(), name='sanatoriums'),
    path('naftalan-page/', views.NaftalanSanatoriumsPageView.as_view(), name='naftalan-sanatoriums'),
    path('other-cities-page/', views.OtherCitiesSanatoriumsPageView.as_view(), name='other-cities-sanatoriums'),
    path('naftalan-sanatoriums/', views.NaftalanSanatoriums.as_view(), name='naftalan-sanatoriums'),
    path('other-cities-sanatoriums/', views.OtherCitiesSanatoriums.as_view(), name='other-cities-sanatoriums'),
    path('<slug:slug>/', views.SanatoriumDetailView.as_view(), name='sanatorium-detail'),

]