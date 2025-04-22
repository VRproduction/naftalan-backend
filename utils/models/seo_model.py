from django.db import models


class SEOModel(models.Model):
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name="Meta Başlıq")
    meta_description = models.TextField(max_length=160, blank=True, null=True, verbose_name="Meta Təsvir")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name="Meta Açar Sözlər")
    og_title = models.CharField(max_length=70, blank=True, null=True, verbose_name="OG Başlıq")
    og_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="OG Təsvir")
    og_image = models.ImageField(upload_to="seo/og-images/", blank=True, null=True, verbose_name="OG Şəkil")
    canonical_url = models.URLField(blank=True, null=True, verbose_name="Canonical URL")
    no_index = models.BooleanField(default=False, verbose_name="No Index")
    no_follow = models.BooleanField(default=False, verbose_name="No Follow")

    class Meta:
        abstract = True