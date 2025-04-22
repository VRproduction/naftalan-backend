from django.urls import path, include

from .views import BlogListAPIView, BlogDetailAPIView, BlogCategoryListAPIView, BlogTagListAPIView, BlogPopularListAPIView, BlogFeaturedListAPIView

urlpatterns = [
    path("", BlogListAPIView.as_view()),
    path("categories/", BlogCategoryListAPIView.as_view()),
    path("tags/", BlogTagListAPIView.as_view()),
    path("popular/", BlogPopularListAPIView.as_view()),
    path("featured/", BlogFeaturedListAPIView.as_view()),
    path("<slug:slug>/", BlogDetailAPIView.as_view())   
]