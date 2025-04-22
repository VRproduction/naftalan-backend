from django.urls import path
from . import views


urlpatterns = [
    path('', views.SanatoriumListView.as_view(), name='sanatoriums'),
    path('<slug:slug>/', views.SanatoriumDetailView.as_view(), name='sanatorium-detail'),

]