from django.db import models

class BaseModel(models.Model):
    """All models extends this model"""
    created = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.DateTimeField(auto_now = True, null = True)

    class Meta:
        abstract = True

    @property
    def created_date(self):
        return self.created.strftime('%d/%m/%Y, %H:%M')