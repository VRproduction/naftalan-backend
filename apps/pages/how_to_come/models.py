from django.db import models


class Hero(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Hero bölümü'
        verbose_name_plural = 'Hero bölümü'


class Location(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Haqqında məlumat')
    map_iframe = models.TextField(verbose_name='Map iframe')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Location bölümü'
        verbose_name_plural = 'Location bölümü'


# class 