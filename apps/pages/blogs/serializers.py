from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from utils.api.mixins.translation import TranslationMixin

from .models import Blog, BlogTag, BlogCategory



class SEOSerializer(serializers.ModelSerializer):
    """SEO məlumatları üçün ayrı serializer"""
    og_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image',
                 'canonical_url', 'no_index', 'no_follow')
    
    def get_og_image(self, obj):
        """OG Image üçün tam URL qaytarır"""
        request = self.context.get('request')
        if obj.og_image and hasattr(obj.og_image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.og_image.url)
            return obj.og_image.url
        return None


class BlogTagSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ('id', 'title')


class BlogCategorySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ('id', 'title')


class BlogSerializer(TranslationMixin, serializers.ModelSerializer):
    other_blogs = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = BlogTagSerializer(many=True)
    
    class Meta:
        model = Blog
        fields = ('id', 'title', 'category', 'slug', 'short_description', 'description', 'date',
                 'image', 'view_count', 'created', 'updated', 'is_popular', 'is_featured',
                 'seo', 'other_blogs', 'tags')
        
    @extend_schema_field(SEOSerializer)
    def get_seo(self, obj):
        """SEO məlumatlarını ayrı bir obyekt kimi qaytarır"""
        serializer = SEOSerializer(obj, context=self.context)
        return serializer.data

    @extend_schema_field({"type": "array", "items": {"type": "object"}})
    def get_other_blogs(self, obj):
        request = self.context.get('request')
        # Exclude current blog and limit to avoid recursion
        other_blogs = Blog.objects.exclude(id=obj.id)[:3]  # Limit to 3 related blogs
        serializer = BlogSerializer(other_blogs, many=True, context={'request': request})
        # Remove other_blogs field from nested serializer to prevent infinite recursion
        serializer.child.fields.pop('other_blogs', None)
        return serializer.data
    
    def get_category(self, obj):
        return obj.category.title
