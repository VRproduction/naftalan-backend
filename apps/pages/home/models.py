from django.db import models


class HeroSlider(models.Model):
    image = models.ImageField(upload_to='hero-slider')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return f'Image {self.id}'

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                HeroSlider.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['priority']
        verbose_name = 'Slider bölümü'
        verbose_name_plural = 'Slider bölümü'


class AboutSection(models.Model):
    sub_title = models.CharField(max_length=255, verbose_name='Alt Başlıq')
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')
    image = models.ImageField(upload_to='home/about-section', verbose_name='Şəkil')
    content_title = models.CharField(
        max_length=255, verbose_name='Məlumatın başlığı'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Haqqımızda'
        verbose_name_plural = 'Haqqımızda bölümü'


class AboutPunkt(models.Model):
    section = models.ForeignKey(
        AboutSection,
        on_delete=models.CASCADE,
        related_name='punkts',
        verbose_name='Bölüm',
    )
    icon = models.FileField(upload_to='home/about-punkts', verbose_name='Ikon')
    title = models.CharField(max_length=255, verbose_name='Başlığı')
    description = models.TextField(verbose_name='Haqqında məlumat')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                AboutPunkt.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Haqqımızda punkt'
        verbose_name_plural = 'Haqqımızda punktlar'
        ordering = ['priority']


class SanatoriesSection(models.Model):
    sub_title = models.CharField(max_length=255, verbose_name='Alt Başlıq')
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Sanatoriyalar'
        verbose_name_plural = 'Sanatoriyalar bölümü'


class TreatmentsSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Müalicə növləri bölümü'
        verbose_name_plural = 'Müalicə növləri bölümü'


class PackagesSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Hazır paketlər'
        verbose_name_plural = 'Hazır paketlər bölümü'


class CustomerCommentsSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Müştəri rəyləri'
        verbose_name_plural = 'Müştəri rəyləri bölümü'


class CustomerComments(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Adı və soyadı')
    address = models.TextField(verbose_name='Adrəss')
    comment = models.TextField(verbose_name='Rəy')
    priority = models.IntegerField(default=1)
    rating = models.IntegerField(default=5, verbose_name='Reytinq')

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                CustomerComments.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Müştəri rəyləri'
        verbose_name_plural = 'Müştəri rəyləri'


class FAQSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Tez-tez verilən suallar suallar bölümü'
        verbose_name_plural = 'Tez-tez verilən suallar suallar bölümü'


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name='Sual')
    answer = models.TextField(verbose_name='Cavab')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.pk:
            last_priority = (
                FAQ.objects.aggregate(models.Max('priority'))['priority__max'] or 0
            )
            self.priority = last_priority + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Tez-tez verilən suallar suallar'
        verbose_name_plural = 'Tez-tez verilən suallar suallar'
        ordering = ['priority']


class BlogSection(models.Model):
    title = models.CharField(max_length=255, verbose_name='Əsas başlıq')
    section_description = models.TextField(verbose_name='Bölüm haqqında məlumat')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Bloqlar bölümü'
        verbose_name_plural = 'Bloqlar bölümü'


class ContactSection(models.Model):
    left_section_title = models.CharField(max_length=255, verbose_name='Başlıq')
    left_section_description = models.TextField(
        verbose_name='Haqqında məlumat'
    )

    right_section_title = models.CharField(
        max_length=255, verbose_name='Başlıq'
    )
    right_section_description = models.TextField(
        verbose_name='Haqqında məlumat'
    )

    def __str__(self):
        return self.left_section_title

    class Meta:
        verbose_name = 'Əlaqə məlumatları bölümü'
        verbose_name_plural = 'Əlaqə məlumatları bölümü'