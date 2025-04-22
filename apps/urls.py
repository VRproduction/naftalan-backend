from django.urls import path, include

urlpatterns = [
    path('home/', include('apps.pages.home.urls')),
    path('about/', include('apps.pages.about.urls')),   
    path('sanatoriums/', include('apps.sanatoriums.urls')),   

    # path('packages/', include('apps.packages.urls')),
]