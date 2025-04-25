from django.db import models
from django.utils.translation import gettext_lazy as _

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