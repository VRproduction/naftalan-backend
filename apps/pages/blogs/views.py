from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Blog, BlogCategory, BlogTag
from .serializers import BlogSerializer, BlogCategorySerializer, BlogTagSerializer
from utils.api.pagination.page_number_pagination import CustomPageNumberPagination
from django_filters import rest_framework as filters
from .filters import BlogFilter

class BlogListAPIView(ListAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = BlogFilter


class BlogDetailAPIView(RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class BlogCategoryListAPIView(ListAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer


class BlogTagListAPIView(ListAPIView):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer


class BlogPopularListAPIView(ListAPIView):
    queryset = Blog.objects.filter(is_popular=True)
    serializer_class = BlogSerializer
    

class BlogFeaturedListAPIView(ListAPIView):
    queryset = Blog.objects.filter(is_featured=True)
    serializer_class = BlogSerializer
