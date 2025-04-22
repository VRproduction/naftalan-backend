from django.urls import path, include

urlpatterns = [
    path('home/', include('apps.pages.home.urls')),
    path('about/', include('apps.pages.about.urls')),   
    # path('packages/', include('apps.packages.urls')),
]