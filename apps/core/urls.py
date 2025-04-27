from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SiteSettingsRetrieveView, 
    SEOByPageView, 
    SEOListCreateView, 
    SEORetrieveUpdateDestroyView,
    CurrencyViewSet,
    WorkingHoursViewSet
)

app_name = 'core'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'working-hours', WorkingHoursViewSet)

# Standard URL patterns for our views
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # SiteSettings endpoint
    path('settings/', SiteSettingsRetrieveView.as_view(), name='site-settings'),
    
    # SEO endpoints
    path('seo/', SEOByPageView.as_view(), name='seo-by-page'),
    path('seo/list/', SEOListCreateView.as_view(), name='seo-list-create'),
    path('seo/<int:pk>/', SEORetrieveUpdateDestroyView.as_view(), name='seo-detail'),
] 