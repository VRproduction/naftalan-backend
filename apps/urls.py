from django.urls import path, include

urlpatterns = [
    path('core/', include('apps.core.urls')),  # Core endpoints should be accessible at the API root
    path('home/', include('apps.pages.home.urls')),
    path('about/', include('apps.pages.about.urls')),   
    path('sanatoriums/', include('apps.sanatoriums.urls')),   
    path('blogs/', include('apps.pages.blogs.urls')),
    path('booking/', include('apps.booking.urls')),
    path('how-to-come/', include('apps.pages.how_to_come.urls')),
    # path('packages/', include('apps.packages.urls')),
]