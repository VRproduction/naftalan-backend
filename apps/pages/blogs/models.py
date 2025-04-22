from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField

from utils.models.base_model import BaseModel
from utils.models.seo_model import SEOModel
from utils.mixins.slug import SlugMixin


class BlogCategory(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Başlıq")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Bloq kategoriyası"
        verbose_name_plural = "Bloq kategoriyaları"

class BlogTag(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Başlıq")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Bloq teq"
        verbose_name_plural = "Bloq teqləri"

class Blog(BaseModel, SEOModel, SlugMixin):
    slug_source_field = 'title'

    title = models.CharField(max_length=255, verbose_name="Başlıq")
    description = RichTextUploadingField(verbose_name="Məzmun")
    short_description = models.TextField(verbose_name="Qısa məzmun")
    image = models.ImageField(upload_to="blog/", verbose_name="Şəkil")
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name="blogs", verbose_name="Kategoriya")
    tags = models.ManyToManyField(BlogTag, related_name="blogs", verbose_name="Teqlər", blank=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name="Baxış sayı")
    in_home = models.BooleanField(default=True, verbose_name="Ana səhifədə göstər")
    is_popular = models.BooleanField(default=False, verbose_name="Populyar")    
    is_featured = models.BooleanField(default=False, verbose_name="Təqdim olunan")
    date = models.DateField(verbose_name="Tarix", null = True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Bloq"
        verbose_name_plural = "Bloqlar"
        ordering = ['-created']

    def save(self, *args, **kwargs):
        # SEO məlumatlarını avtomatik doldur
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.short_description[:160]
        if not self.og_title:
            self.og_title = self.title
        if not self.og_description:
            self.og_description = self.short_description[:200]
        if not self.og_image:
            self.og_image = self.image
            
        super().save(*args, **kwargs)
