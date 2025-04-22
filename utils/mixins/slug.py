import re
from django.db import models
from django.utils.text import slugify
from transliterate import translit
from unicodedata import normalize

class SlugMixin(models.Model):
    slug = models.SlugField(blank=True)
    slug_source_field = 'title'  # Varsayılan olarak 'title', ancak modeller bunu değiştirebilir

    class Meta:
        abstract = True

    def _generate_slug(self, value):
        value = normalize('NFKC', value)
        value = value.replace('ə', 'e').replace('ı', 'i').replace('ç', 'c')
        value = value.replace('ğ', 'g').replace('ş', 's').replace('ü', 'u').replace('ö', 'o')
        transliterated_text = translit(value, 'ru', reversed=True)
        return slugify(transliterated_text)

    def generate_unique_slug(self):
        # slug kaynağı doğrudan bir alan değilse, ilişkili model üzerinden değeri al
        if '.' in self.slug_source_field:
            related_field, related_attr = self.slug_source_field.split('.')
            source_value = getattr(getattr(self, related_field, None), related_attr, None)
        else:
            source_value = getattr(self, self.slug_source_field, None)

        if not source_value:
            raise ValueError(f"{self.__class__.__name__} must have a valid '{self.slug_source_field}' field for slug generation.")
        
        base_slug = self._generate_slug(source_value)
        slug = base_slug
        model_class = self.__class__

        counter = 1
        while model_class.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        source_value = getattr(self, self.slug_source_field, None)
        if '.' in self.slug_source_field:
            related_field, related_attr = self.slug_source_field.split('.')
            related_instance = getattr(self, related_field, None)
            source_value = getattr(related_instance, related_attr, None)

        new_slug = self.generate_unique_slug() if source_value else None
        if new_slug and (not self.slug or self.slug != new_slug):
            self.slug = new_slug

        super().save(*args, **kwargs)
