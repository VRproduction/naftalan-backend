from django.utils.translation import get_language_from_request, activate, get_language
from django.conf import settings
from rest_framework import serializers


class TranslationMixin(serializers.ModelSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        
        # Request olmadığı halda default dili istifadə et
        if not request:
            lang = settings.LANGUAGE_CODE
        else:
            # Accept-Language başlığından dili al
            accept_language = request.headers.get('Accept-Language', '')
            # Əgər Accept-Language başlığı varsa, ondan dili çıxar
            if accept_language:
                # İlk dil kodunu al (məsələn, "az-AZ,az;q=0.9,en-US;q=0.8,en;q=0.7" -> "az-AZ")
                lang_code = accept_language.split(',')[0].split(';')[0].strip()
                # Əgər dil kodu varsa və "-" işarəsi varsa, ilk hissəni götür (məsələn, "az-AZ" -> "az")
                if '-' in lang_code:
                    lang_code = lang_code.split('-')[0]
                
                # Əgər dil kodu sistemdə mövcud olan dillərdən biridisə, onu istifadə et
                if lang_code in dict(settings.LANGUAGES).keys():
                    lang = lang_code
                else:
                    # Əks halda default dili istifadə et
                    lang = settings.LANGUAGE_CODE
            else:
                # Accept-Language başlığı yoxdursa, default dili istifadə et
                lang = settings.LANGUAGE_CODE
        
        activate(lang)  # İlgili dili etkinleştir
        
        representation = super().to_representation(instance)
        
        # Çeviri alanlarını filtrelerken yalnızca istemci dilindeki alanı bırak
        for field in list(representation.keys()):
            if any(field.endswith(f"_{l}") for l in settings.MODELTRANSLATION_LANGUAGES):
                del representation[field]
        
        # Başlangıçta aktif olan dile geri dön
        activate(get_language())
        
        return representation
