from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.conf import settings
from ckeditor.fields import RichTextField

class Currency(models.Model):
    code = models.CharField(_("Valyuta kodu"), max_length=3, unique=True)  # AZN, USD, EUR, etc.
    name = models.CharField(_("Valyuta adı"), max_length=50)
    symbol = models.CharField(_("Simvol"), max_length=5)
    
    def __str__(self):
        return f"{self.code} ({self.symbol})"
    
    class Meta:
        verbose_name = _("Valyuta")
        verbose_name_plural = _("Valyutalar")
        # db_table = 'main_currency'  # tablo adı korunuyor

class DayOfWeek(models.TextChoices):
    """Days of the week for working hours"""
    MONDAY = 'monday', _('Bazar ertəsi')
    TUESDAY = 'tuesday', _('Çərşənbə axşamı')
    WEDNESDAY = 'wednesday', _('Çərşənbə')
    THURSDAY = 'thursday', _('Cümə axşamı')
    FRIDAY = 'friday', _('Cümə')
    SATURDAY = 'saturday', _('Şənbə')
    SUNDAY = 'sunday', _('Bazar')

class WorkingHours(models.Model):
    """Working hours for a specific day of the week"""
    site_settings = models.ForeignKey('SiteSettings', on_delete=models.CASCADE, related_name='working_hours_set')
    day = models.CharField(_("Gün"), max_length=20, choices=DayOfWeek.choices)
    is_working_day = models.BooleanField(_("İş günüdür"), default=True)
    opening_time = models.TimeField(_("Açılış vaxtı"), null=True, blank=True)
    closing_time = models.TimeField(_("Bağlanış vaxtı"), null=True, blank=True)
    lunch_start = models.TimeField(_("Nahar fasiləsi başlanğıcı"), null=True, blank=True)
    lunch_end = models.TimeField(_("Nahar fasiləsi bitişi"), null=True, blank=True)
    order = models.SmallIntegerField(_("Sıra"), default=0)
    note = models.CharField(_("Qeyd"), max_length=255, null=True, blank=True)
    
    def __str__(self):
        if not self.is_working_day:
            return f"{self.get_day_display()}: {_('İstirahət günü')}"
        
        times = f"{self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        if self.lunch_start and self.lunch_end:
            times += f" ({_('Nahar')}: {self.lunch_start.strftime('%H:%M')} - {self.lunch_end.strftime('%H:%M')})"
        
        return f"{self.get_day_display()}: {times}"
    
    class Meta:
        verbose_name = _("İş saatı")
        verbose_name_plural = _("İş saatları")
        ordering = ['order', 'day']
        unique_together = ['site_settings', 'day']

class SiteSettings(models.Model):
    """Site-wide settings and configuration model"""
    # Basic Site Information
    site_name = models.CharField(_("Sayt adı"), max_length=100)
    site_tagline = models.CharField(_("Sayt sloqanı"), max_length=200, null=True, blank=True)
    site_description = models.TextField(_("Sayt haqqında qısa məlumat"), null=True, blank=True)
    
    # Contact Information
    contact_email = models.EmailField(_("Əsas e-poçt"))
    contact_email_secondary = models.EmailField(_("Əlavə e-poçt"), null=True, blank=True)
    contact_phone = models.CharField(_("Əsas telefon"), max_length=20)
    contact_phone_secondary = models.CharField(_("Əlavə telefon"), max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(_("WhatsApp nömrəsi"), max_length=20, null=True, blank=True)
    telegram_username = models.CharField(_("Telegram istifadəçi adı"), max_length=50, null=True, blank=True)
    
    # Location
    address = models.TextField(_("Ünvan"), null=True, blank=True)
    map_latitude = models.DecimalField(_("Xəritə enliyi"), max_digits=10, decimal_places=7, null=True, blank=True)
    map_longitude = models.DecimalField(_("Xəritə uzunluğu"), max_digits=10, decimal_places=7, null=True, blank=True)
    map_zoom = models.PositiveSmallIntegerField(_("Xəritə yaxınlaşması"), default=15, null=True, blank=True)
    
    # Legacy working hours field (will be deprecated)
    working_hours = models.TextField(_("İş saatları (köhnə)"), null=True, blank=True, 
                                    help_text=_("Məsələn: Bazar ertəsi-Cümə: 9:00-18:00, Şənbə: 10:00-15:00"))
    
    # Company Information
    company_name = models.CharField(_("Şirkət adı"), max_length=100, null=True, blank=True)
    tax_number = models.CharField(_("VÖEN"), max_length=50, null=True, blank=True)
    foundation_year = models.PositiveSmallIntegerField(_("Quruluş ili"), null=True, blank=True)
    
    # Visual Assets
    logo = models.ImageField(_("Logo"), upload_to="site/", null=True, blank=True)
    logo_dark = models.ImageField(_("Tünd fon üçün logo"), upload_to="site/", null=True, blank=True)
    footer_logo = models.ImageField(_("Alt logo"), upload_to="site/", null=True, blank=True)
    favicon = models.ImageField(_("Favicon"), upload_to="site/", null=True, blank=True)
    mobile_app_icon = models.ImageField(_("Mobil tətbiq ikonu"), upload_to="site/", null=True, blank=True)
    
    # Header & Footer
    primary_color = models.CharField(_("Əsas rəng"), max_length=20, default="#0062cc", null=True, blank=True,
                                    help_text=_("HEX kod (məs. #0062cc)"))
    secondary_color = models.CharField(_("İkinci rəng"), max_length=20, default="#6c757d", null=True, blank=True,
                                     help_text=_("HEX kod (məs. #6c757d)"))
    accent_color = models.CharField(_("Vurğu rəngi"), max_length=20, default="#fd7e14", null=True, blank=True,
                                  help_text=_("HEX kod (məs. #fd7e14)"))
    
    # Footer options
    footer_text = models.TextField(_("Alt mətn"), null=True, blank=True)
    copyright_text = models.CharField(_("Müəllif hüquqları mətni"), max_length=200, null=True, blank=True,
                                     help_text=_("Məsələn: © 2023 Şirkət Adı. Bütün hüquqlar qorunur."))
    show_social_in_footer = models.BooleanField(_("Alt hissədə sosial ikonları göstər"), default=True)
    
    # Social Media
    social_facebook = models.URLField(_("Facebook"), null=True, blank=True)
    social_instagram = models.URLField(_("Instagram"), null=True, blank=True)
    social_twitter = models.URLField(_("Twitter"), null=True, blank=True)
    social_youtube = models.URLField(_("YouTube"), null=True, blank=True)
    social_linkedin = models.URLField(_("LinkedIn"), null=True, blank=True)
    social_tiktok = models.URLField(_("TikTok"), null=True, blank=True)
    social_pinterest = models.URLField(_("Pinterest"), null=True, blank=True)
    
    # SEO Settings
    default_meta_title = models.CharField(_("Varsayılan meta başlıq"), max_length=100, null=True, blank=True)
    default_meta_description = models.TextField(_("Varsayılan meta təsviri"), null=True, blank=True)
    default_meta_keywords = models.TextField(_("Varsayılan meta açar sözlər"), null=True, blank=True)
    default_og_image = models.ImageField(_("Varsayılan OG şəkli"), upload_to="site/", null=True, blank=True,
                                       help_text=_("Sosial paylaşımlar üçün varsayılan şəkil"))
    
    # Analytics & Tracking
    google_analytics_id = models.CharField(_("Google Analytics ID"), max_length=50, null=True, blank=True)
    google_tag_manager_id = models.CharField(_("Google Tag Manager ID"), max_length=50, null=True, blank=True)
    google_site_verification = models.CharField(_("Google Site Verification"), max_length=100, null=True, blank=True)
    facebook_pixel_id = models.CharField(_("Facebook Pixel ID"), max_length=50, null=True, blank=True)
    
    # reCAPTCHA
    recaptcha_site_key = models.CharField(_("reCAPTCHA site key"), max_length=100, null=True, blank=True)
    recaptcha_secret_key = models.CharField(_("reCAPTCHA secret key"), max_length=100, null=True, blank=True)
    
    # Cookie & Privacy
    cookie_policy_popup = models.BooleanField(_("Cookie bildirişini göstər"), default=True)
    cookie_popup_text = models.TextField(_("Cookie popup mətni"), null=True, blank=True)
    privacy_policy_page = models.URLField(_("Məxfilik siyasəti səhifəsi"), null=True, blank=True)
    terms_page = models.URLField(_("İstifadə şərtləri səhifəsi"), null=True, blank=True)
    
    # About Section
    about_short = RichTextField(_("Haqqımızda qısa mətn"), null=True, blank=True)
    
    # Additional Settings
    maintenance_mode = models.BooleanField(_("Təmir rejimi"), default=False)
    maintenance_message = models.TextField(_("Təmir rejimi mesajı"), null=True, blank=True)
    show_language_selector = models.BooleanField(_("Dil seçicisini göstər"), default=True)
    default_language = models.CharField(_("Varsayılan dil"), max_length=10, default="az", null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)
    
    def save(self, *args, **kwargs):
        # Clear cache on save
        cache.delete('site_settings')
        super().save(*args, **kwargs)
        
        # Create default working hours if this is a new instance
        if not self.pk or not self.working_hours_set.exists():
            self._create_default_working_hours()
    
    def _create_default_working_hours(self):
        # Only create if we have a primary key and no existing working hours
        if self.pk and not self.working_hours_set.exists():
            # Create working days (Monday to Friday)
            for i, day in enumerate([
                DayOfWeek.MONDAY, 
                DayOfWeek.TUESDAY, 
                DayOfWeek.WEDNESDAY, 
                DayOfWeek.THURSDAY, 
                DayOfWeek.FRIDAY
            ]):
                WorkingHours.objects.create(
                    site_settings=self,
                    day=day,
                    is_working_day=True,
                    opening_time='09:00',
                    closing_time='18:00',
                    lunch_start='13:00',
                    lunch_end='14:00',
                    order=i
                )
            
            # Create non-working days (Saturday and Sunday)
            for i, day in enumerate([DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]):
                WorkingHours.objects.create(
                    site_settings=self,
                    day=day,
                    is_working_day=False,
                    order=i+5
                )
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name = _("Sayt tənzimləməsi")
        verbose_name_plural = _("Sayt tənzimləmələri")

class PageType(models.TextChoices):
    """Static page types for the site"""
    HOME = 'home', _('Ana səhifə')
    ABOUT = 'about', _('Haqqımızda')
    HISTORY = 'history', _('Tarix')
    TREATMENTS = 'treatments', _('Müalicə üsulları')
    CONTACT = 'contact', _('Əlaqə')
    ASK_DOCTOR = 'ask_doctor', _('Həkimdən soruş')
    BLOG = 'blog', _('BloQ')
    HOW_TO_COME = 'how_to_come', _('Necə gəlməli')
    RESERVATION = 'reservation', _('Rezervasiya')
    SANATIUMS = 'sanatoriums', _('Sanatoriumlar')
    TERMS = 'terms', _('İstifadə şərtləri')
    PRIVACY = 'privacy', _('Məxfilik siyasəti')
    CUSTOM = 'custom', _('Fərdi səhifə')

class SEO(models.Model):
    """SEO settings for pages"""
    page_type = models.CharField(
        _("Səhifə növü"), 
        max_length=50, 
        choices=PageType.choices,
        default=PageType.CUSTOM,
        unique=True
    )
    page_slug = models.SlugField(_("Səhifə slug"), max_length=100, null=True, blank=True)
    meta_title = models.CharField(_("Meta başlıq"), max_length=100)
    meta_description = models.TextField(_("Meta təsvir"))
    meta_keywords = models.TextField(_("Meta açar sözlər"), null=True, blank=True)
    og_title = models.CharField(_("OG Başlıq"), max_length=100, null=True, blank=True, 
                               help_text=_("Open Graph başlıq (sosial şəbəkələr üçün). Boş buraxsanız, meta başlıq istifadə olunacaq."))
    og_description = models.TextField(_("OG Təsvir"), null=True, blank=True, 
                                     help_text=_("Open Graph təsvir (sosial şəbəkələr üçün). Boş buraxsanız, meta təsvir istifadə olunacaq."))
    og_image = models.ImageField(_("OG Şəkil"), upload_to="seo/", null=True, blank=True, 
                                help_text=_("Open Graph şəkil (sosial şəbəkələrdə paylaşmaq üçün)"))
    no_index = models.BooleanField(_("İndeksləməmək"), default=False, 
                                  help_text=_("Axtarış motorlarının bu səhifəni indeksləməsinə mane olmaq"))
    no_follow = models.BooleanField(_("İzləməmək"), default=False, 
                                   help_text=_("Axtarış motorlarının bu səhifədəki linkləri izləməsinə mane olmaq"))
    canonical_url = models.URLField(_("Kanonizasiya URL"), null=True, blank=True, 
                                   help_text=_("Eyni məzmuna sahib səhifələrdən hansının əsas olduğunu göstərmək üçün"))
    structured_data = models.JSONField(_("Strukturlaşdırılmış data"), null=True, blank=True, 
                                      help_text=_("JSON formatında strukturlaşdırılmış data"))
    created_at = models.DateTimeField(_("Yaradılma tarixi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yenilənmə tarixi"), auto_now=True)
    
    def __str__(self):
        if self.page_type == PageType.CUSTOM and self.page_slug:
            return f"SEO: {self.page_slug}"
        return f"SEO: {self.get_page_type_display()}"
    
    class Meta:
        verbose_name = _("SEO tənzimləməsi")
        verbose_name_plural = _("SEO tənzimləmələri")
        unique_together = ('page_type', 'page_slug')