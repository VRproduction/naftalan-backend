"""
Fixed version of the serializers.py file with proper handling of child ages
that don't match any available age group
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
import logging
from apps.sanatoriums.pricing_helper import get_price_details, get_extra_bed_price_details
from datetime import datetime, date
from apps.sanatoriums.models import Season
from django.db.models import Q

from .models import (
    Location, Sanatorium, SanatoriumImage, 
    Facility, SanatoriumFacility,
    RoomType, RoomImage, Review, NaftalanSanatoriumsPage, OtherCitiesSanatoriumsPage,
    Season, RoomPrice, AgeGroup, ExtraBedPrice, TreatmentOption
)
from utils.api.mixins.translation import TranslationMixin

from apps.core.models import Currency


def get_season_from_request(request):
    check_in_str = request.query_params.get('check_in') if request else None
    check_out_str = request.query_params.get('check_out') if request else None
    if check_in_str and check_out_str:
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            season = Season.objects.filter(start_date__lte=check_in, end_date__gte=check_out).first()
            return season
        except Exception:
            return None
    return None

def _get_current_season(today):
    return Season.objects.filter(start_date__lte=today, end_date__gte=today).first()

class SEOSerializer(serializers.ModelSerializer):
    """SEO məlumatları üçün ayrı serializer"""
    og_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Sanatorium
        fields = (
            'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image',
            'canonical_url', 'no_index', 'no_follow'
        )
    
    def get_og_image(self, obj):
        """OG Image üçün tam URL qaytarır"""
        request = self.context.get('request')
        if obj.og_image and hasattr(obj.og_image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.og_image.url)
            return obj.og_image.url
        return None

class LocationSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'region', 'country']


class CurrencySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']


class SeasonSerializer(TranslationMixin, serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Season
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']


class TreatmentOptionSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = TreatmentOption
        fields = ['id', 'name', 'description']


class AgeGroupSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = ['id', 'name', 'min_age', 'max_age']


class FacilitySerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name', 'icon']

class SanatoriumImageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = SanatoriumImage
        fields = ['id', 'image', 'is_main', 'priority']

class RoomImageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'priority']


class RoomPriceSerializer(TranslationMixin, serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    treatment_option = TreatmentOptionSerializer(read_only=True)
    
    class Meta:
        model = RoomPrice
        fields = [
            'id', 'season', 'occupancy', 'with_treatment', 'treatment_option', 'price', 'currency',
            'discount_type', 'discount_value', 'discounted_price'
        ]


class ExtraBedPriceSerializer(TranslationMixin, serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    age_group = AgeGroupSerializer(read_only=True)
    treatment_option = TreatmentOptionSerializer(read_only=True)
    discounted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ExtraBedPrice
        fields = [
            'id', 'season', 'age_group', 'with_treatment', 'treatment_option', 'price', 'currency',
            'discount_type', 'discount_value', 'discounted_price'
        ]
    
    def get_discounted_price(self, obj):
        return obj.discounted_price


class RoomTypeSerializer(TranslationMixin, serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    prices = RoomPriceSerializer(many=True, read_only=True)
    extra_bed_prices = ExtraBedPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'description', 'min_capacity', 'max_capacity', 'max_extra_beds', 'size',
            'images', 'prices', 'extra_bed_prices'
        ]

class SanatoriumListSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    class Meta:
        model = Sanatorium
        fields = ['id', 'name', 'location']

class MatchedRoomsRoomTypeSerializer(TranslationMixin, serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'description', 'min_capacity', 'max_capacity', 'max_extra_beds', 'size', 'images'
        ]


class ReviewSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'full_name', 'sanatorium', 'rating', 'content', 'date']
        read_only_fields = ['created_at']

class SanatoriumFacilitySerializer(TranslationMixin, serializers.ModelSerializer):
    facility = FacilitySerializer(read_only=True)
    
    class Meta:
        model = SanatoriumFacility
        fields = ['id', 'facility']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Sanatorium list',
            summary='List of sanatoriums',
            description='This is a list of sanatoriums',
            value={
                'id': 1,
                'name': 'Sanatorium 1',
                'slug': 'sanatorium-1',
                'location': {
                    'id': 1,
                    'region': 'Baku',
                    'country': 'Azerbaijan'
                },
                'location_type': 'city',
                'short_description': 'Short description',
                'rating': 4.5,
                'min_price': 100.0,
                'min_price_currency': {
                    'id': 1,
                    'code': 'AZN',
                    'name': 'Azerbaijani Manat',
                    'symbol': '₼'
                },
                'total_price': 200.0,
                'min_price_details': {
                    'selected_room': 'Room 1',
                    'occupancy': 2,
                    'children_ages': [5, 10],
                    'season': 'Summer',
                    'season_type': 'current',
                    'base_price': 100.0,
                    'base_price_currency': 'AZN',
                    'extra_bed_prices': [
                        {
                            'child_age': 5,
                            'price_added': 20.0,
                            'is_default': False
                        },
                        {
                            'child_age': 10,
                            'price_added': 30.0,
                            'is_default': False
                        }
                    ],
                    'total_price': 200.0,
                    'room_capacity': {
                        'min': 2,
                        'max': 4
                    },
                    'max_extra_beds': 2,
                    'with_treatment': True,
                    'treatment_option': 'Treatment 1'
                },
                'is_active': True,
                'in_home': True,
                'main_image': {
                    'id': 1,
                    'image': 'image.jpg',
                    'is_main': True,
                    'priority': 1
                },
                'facilities': [
                    {
                        'id': 1,
                        'facility': {
                            'id': 1,
                            'name': 'Facility 1',
                            'icon': 'icon.jpg'
                        }
                    }
                ],
                'images': [
                    {
                        'id': 1,
                        'image': 'image.jpg',
                        'is_main': True,
                        'priority': 1
                    }
                ]
            }
        )
    ]
)
class SanatoriumSearchSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    min_price_details = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'location', 'location_type',
            'short_description', 'rating', 'min_price_details',
            'is_active', 'in_home', 'main_image', 'facilities', 'images'
        ]
    
    def get_min_price_details(self, obj):
        request = self.context.get('request')
        season = get_season_from_request(request)
        if not season:
            today = self._get_today()
            season = _get_current_season(today)
        if not season:
            from apps.sanatoriums.models import RoomPrice
            standard_price = RoomPrice.objects.filter(is_standard=True).order_by('season').first()
            if standard_price and standard_price.season:
                season = standard_price.season
       
        occupancy = self._get_occupancy()
        children_ages = self._get_children_ages()
        logger = logging.getLogger(__name__)
        min_price_data = self._find_min_price(obj, season, occupancy, children_ages, logger)
        if not min_price_data:
            return None
        base_price, room_type, season, price_obj, currency = min_price_data
        final_price, extra_bed_price_details = self._add_extra_bed_prices(room_type, season, children_ages, base_price, logger)
        min_price_details = self._get_price_details(obj, room_type, price_obj, season, final_price, occupancy, children_ages)
        # total_price ve total_discount_price hesapla
        nights = self._get_nights()
        total_price = final_price * nights if nights else None
        discount_type, discount_value = self._get_discount_info_from_details(min_price_details)
        total_discount_price = None
        if total_price is not None and discount_type and discount_value:
            from decimal import Decimal
            discounted = final_price
            if discount_type == 'percentage' and discount_value <= 100:
                discounted = float(Decimal(str(final_price)) * (Decimal('1') - Decimal(str(discount_value))/Decimal('100')))
            elif discount_type == 'fixed':
                discounted = float(Decimal(str(final_price)) - Decimal(str(discount_value)))
            total_discount_price = discounted * nights
        # pricing altına ekle
        if min_price_details is not None:
            min_price_details = dict(min_price_details)
            pricing = dict(min_price_details.get('pricing', {}))
            pricing['total_price'] = total_price
            pricing['total_discount_price'] = total_discount_price
            min_price_details['pricing'] = pricing
            min_price_details.pop('result', None)
        return min_price_details

    def _get_discount_info_from_details(self, min_price_details):
        discount_type = None
        discount_value = 0
        if min_price_details and 'pricing' in min_price_details and 'discount' in min_price_details['pricing']:
            discount = min_price_details['pricing']['discount']
            discount_type = discount.get('type')
            discount_value = discount.get('value', 0)
        return discount_type, discount_value

    def get_main_image(self, obj):
        request = self.context.get('request')
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return SanatoriumImageSerializer(main_image, context={'request': request}).data
        first_image = obj.images.first()
        if first_image:
            return SanatoriumImageSerializer(first_image, context={'request': request}).data
        return None
        
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_matched_room_types(self, obj):
        from django.db.models import Q
        request = self.context.get('request')
        if not request:
            return []
        occupancy = None
        try:
            occupancy = int(request.query_params.get('occupancy')) if request.query_params.get('occupancy') else None
        except (ValueError, TypeError):
            pass
        children_ages = []
        try:
            children_ages = [int(age) for age in request.query_params.get('children_ages', '').split(',') if age.strip()]
        except (ValueError, TypeError):
            pass
        today = date.today()
        season = get_season_from_request(request)
        if not season:
            season = _get_current_season(today)
        if not season:
            from apps.sanatoriums.models import RoomPrice
            standard_price = RoomPrice.objects.filter(is_standard=True).order_by('season').first()
            if standard_price and standard_price.season:
                season = standard_price.season
        nights = None
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        if check_in_str and check_out_str:
            try:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                nights = (check_out - check_in).days
                if nights <= 0:
                    nights = None
            except Exception:
                nights = None
        matched = []
        for room_type in obj.room_types.all():
            max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
            if children_ages and len(children_ages) > max_extra_beds:
                continue
            # children_ages varsa, her biri için uygun extra_bed_price olmalı
            if children_ages:
                if season:
                    extra_bed_prices = room_type.extra_bed_prices.filter(
                        Q(season=season) | Q(season__isnull=True, is_standard=True)
                    )
                else:
                    extra_bed_prices = room_type.extra_bed_prices.all()
                if not extra_bed_prices.exists() and not season:
                    extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
                if not extra_bed_prices.exists() and not season:
                    extra_bed_prices = room_type.extra_bed_prices.all()
                all_children_matched = True
                for age in children_ages:
                    matched_extra = None
                    for ebp in extra_bed_prices:
                        if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                            matched_extra = ebp
                            break
                    if not matched_extra:
                        all_children_matched = False
                        break
                if not all_children_matched:
                    continue
            # Fiyat arama mantığı
            if season:
                prices = room_type.prices.filter(
                    Q(season=season) | Q(season__isnull=True, is_standard=True)
                )
            else:
                prices = room_type.prices.all()
            for with_treatment_value in [True, False]:
                if season:
                    price_candidates = list(prices.filter(with_treatment=with_treatment_value))
                else:
                    price_candidates = list(prices.filter(is_standard=True, with_treatment=with_treatment_value))
                    price_candidates += list(prices.filter(with_treatment=with_treatment_value))
                if occupancy:
                    price_candidates = [p for p in price_candidates if p.occupancy >= occupancy]
                if not price_candidates:
                    continue
                best_price = min(price_candidates, key=lambda p: p.price)
                extra_bed_total = 0
                extra_bed_details = []
                if children_ages:
                    if season:
                        extra_bed_prices = room_type.extra_bed_prices.filter(
                            Q(season=season) | Q(season__isnull=True, is_standard=True)
                        )
                    else:
                        extra_bed_prices = room_type.extra_bed_prices.all()
                    if not extra_bed_prices.exists() and not season:
                        extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
                    if not extra_bed_prices.exists() and not season:
                        extra_bed_prices = room_type.extra_bed_prices.all()
                    for age in children_ages:
                        matched_extra = None
                        for ebp in extra_bed_prices:
                            if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                                matched_extra = ebp
                                break
                        if matched_extra:
                            extra_bed_total += matched_extra.price
                            extra_bed_details.append({
                                'child_age': age,
                                'price_added': matched_extra.price,
                                'currency': CurrencySerializer(matched_extra.currency).data if matched_extra.currency else None
                            })
                discount_type = getattr(best_price, 'discount_type', None)
                discount_value = getattr(best_price, 'discount_value', 0)
                from decimal import Decimal
                discounted_base = float(best_price.price)
                if discount_type and discount_value:
                    if discount_type == 'percentage' and discount_value <= 100:
                        discounted_base = float(Decimal(str(best_price.price)) * (Decimal('1') - Decimal(str(discount_value))/Decimal('100')))
                    elif discount_type == 'fixed':
                        discounted_base = float(Decimal(str(best_price.price)) - Decimal(str(discount_value)))
                discounted_total_price = discounted_base + float(extra_bed_total)
                total_price = None
                total_discounted_price = None
                if nights is not None:
                    total_price = (float(best_price.price) + float(extra_bed_total)) * nights
                    total_discounted_price = discounted_total_price * nights
                discount_amount = None
                if discount_type == 'percentage':
                    discount_amount = float(best_price.price) - discounted_base
                elif discount_type == 'fixed':
                    discount_amount = float(best_price.price) - discounted_base
                else:
                    if float(best_price.price) != discounted_base:
                        discount_amount = float(best_price.price) - discounted_base
                    else:
                        discount_amount = None
                discount_info = {
                    'discount_type': discount_type,
                    'discount_value': discount_value,
                    'discount_amount': discount_amount,
                    'discounted_price': discounted_total_price
                }
                price = float(best_price.price) + float(extra_bed_total)
                final_discounted_price = price
                final_discount_amount = 0
                if discount_type and discount_value:
                    if discount_type == 'percentage' and discount_value <= 100:
                        final_discounted_price = float(Decimal(str(price)) * (Decimal('1') - Decimal(str(discount_value))/Decimal('100')))
                    elif discount_type == 'fixed':
                        final_discounted_price = float(Decimal(str(price)) - Decimal(str(discount_value)))
                    final_discount_amount = price - final_discounted_price
                total_price = price * nights if nights is not None else None
                total_discounted_price = final_discounted_price * nights if nights is not None else None
                discount_info = {
                    'discount_type': discount_type,
                    'discount_value': discount_value,
                    'discount_amount': final_discount_amount,
                    'discounted_price': final_discounted_price
                }
                matched.append({
                    'room_type': MatchedRoomsRoomTypeSerializer(room_type, context=self.context).data,
                    'currency': CurrencySerializer(best_price.currency).data if best_price.currency else None,
                    'season': best_price.season.id if best_price.season else None,
                    'extra_bed_total': float(extra_bed_total),
                    'extra_bed_details': extra_bed_details,
                    'price': price,
                    'nights': nights,
                    'total_price': total_price,
                    'total_discounted_price': total_discounted_price,
                    'discount': discount_info,
                    'occupancy': occupancy,
                    'extra_bed_count': len(children_ages) if children_ages else 0,
                    'with_treatment': getattr(best_price, 'with_treatment', None),
                })
        def sort_key(x):
            return x['total_price'] if x['total_price'] is not None else float('inf')
        return sorted(matched, key=sort_key)

    # --- Helper Methods ---
    def _get_today(self):
        from datetime import date
        return date.today()

    def _get_occupancy(self):
        request = self.context.get('request')
        try:
            return int(request.query_params.get('occupancy')) if request and request.query_params.get('occupancy') else None
        except (ValueError, TypeError):
            return None

    def _get_children_ages(self):
        request = self.context.get('request')
        try:
            return [int(age) for age in request.query_params.get('children_ages', '').split(',') if age.strip()]
        except (ValueError, TypeError):
            return []

    def _get_nights(self):
        from datetime import datetime
        request = self.context.get('request')
        if not request:
            return None
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        if not check_in_str or not check_out_str:
            return None
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            nights = (check_out - check_in).days
            return nights if nights > 0 else None
        except (ValueError, TypeError):
            return None

    def _find_min_price(self, obj, season, occupancy, children_ages, logger):
        from django.db.models import Q
        min_price = None
        min_room_type = None
        min_price_season = None
        selected_price = None
        min_currency = None
        # Try current season first
        if season:
            for room_type in obj.room_types.all():
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                # YENİ: children_ages varsa, her biri için uygun extra_bed_price olmalı
                if children_ages:
                    extra_bed_prices = room_type.extra_bed_prices.filter(
                        Q(season=season) | Q(season__isnull=True, is_standard=True)
                    )
                    if not extra_bed_prices.exists():
                        extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
                    if not extra_bed_prices.exists():
                        extra_bed_prices = room_type.extra_bed_prices.all()
                    all_children_matched = True
                    for age in children_ages:
                        matched_extra = None
                        for ebp in extra_bed_prices:
                            if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                                matched_extra = ebp
                                break
                        if not matched_extra:
                            all_children_matched = False
                            break
                    if not all_children_matched:
                        continue
                room_prices = room_type.prices.filter(
                    Q(season=season) | Q(season__isnull=True, is_standard=True)
                )
                if occupancy:
                    room_prices = room_prices.filter(occupancy__gte=occupancy)
                if not room_prices.exists():
                    continue
                for price in room_prices:
                    if min_price is None or price.price < min_price:
                        min_price = price.price
                        min_room_type = room_type
                        min_price_season = season
                        selected_price = price
                        min_currency = price.currency
        # If not found, try all seasons
        if min_price is None:
            for room_type in obj.room_types.all():
                max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
                if children_ages and len(children_ages) > max_extra_beds:
                    continue
                # YENİ: children_ages varsa, her biri için uygun extra_bed_price olmalı
                if children_ages:
                    extra_bed_prices = room_type.extra_bed_prices.all()
                    all_children_matched = True
                    for age in children_ages:
                        matched_extra = None
                        for ebp in extra_bed_prices:
                            if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                                matched_extra = ebp
                                break
                        if not matched_extra:
                            all_children_matched = False
                            break
                    if not all_children_matched:
                        continue
                room_prices = room_type.prices.all()
                if occupancy:
                    room_prices = room_prices.filter(occupancy__gte=occupancy)
                if not room_prices.exists():
                    continue
                for price in room_prices:
                    if min_price is None or price.price < min_price:
                        min_price = price.price
                        min_room_type = room_type
                        min_price_season = price.season
                        selected_price = price
                        min_currency = price.currency
        if min_price is None or min_room_type is None:
            logger.debug(f"No suitable room found for sanatorium {obj.id}")
            return None
        return min_price, min_room_type, min_price_season, selected_price, min_currency

    def _add_extra_bed_prices(self, room_type, season, children_ages, base_price, logger):
        from django.db.models import Q
        final_price = base_price
        extra_bed_price_details = []
        if not children_ages:
            return final_price, extra_bed_price_details
        if season is not None:
            extra_bed_prices = room_type.extra_bed_prices.filter(
                Q(season=season) | Q(season__isnull=True, is_standard=True)
            )
            if not extra_bed_prices.exists():
                extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
        else:
            extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
        if not extra_bed_prices.exists():
            extra_bed_prices = room_type.extra_bed_prices.all()
        if extra_bed_prices.exists():
            age_groups = set(ebp.age_group for ebp in extra_bed_prices if ebp.age_group)
            if age_groups:
                for age in children_ages:
                    best_extra_bed_price = None
                    for extra_bed_price in extra_bed_prices:
                        age_group = extra_bed_price.age_group
                        if age_group and age_group.min_age <= age <= age_group.max_age:
                            best_extra_bed_price = extra_bed_price
                            break
                    if best_extra_bed_price:
                        final_price += best_extra_bed_price.price
                        # Fiyat detaylarını ekle (opsiyonel, fonksiyon dışı tanımlıysa)
                        if 'get_extra_bed_price_details' in globals():
                            extra_bed_price_detail = get_extra_bed_price_details(
                                room_type=room_type, 
                                child_age=age, 
                                extra_bed_price=best_extra_bed_price, 
                                price_added=best_extra_bed_price.price, 
                                is_default=False
                            )
                            extra_bed_price_details.append(extra_bed_price_detail)
                    else:
                        logger.debug(f"No matching age group found for child age {age} - no price added")
            else:
                logger.debug(f"No age groups defined in extra bed prices for room {room_type.id}")
        else:
            logger.debug(f"No extra bed prices found for room {room_type.id} - not adding any extra price for children")
        return final_price, extra_bed_price_details

    def _get_price_details(self, obj, room_type, price, season, min_price, occupancy, children_ages):
        if 'get_price_details' in globals():
            is_current_season = (season == _get_current_season(self._get_today()))
            return get_price_details(
                sanatorium=obj,
                room_type=room_type,
                price=price,
                is_current_season=is_current_season,
                season=season,
                min_price=min_price,
                occupancy=occupancy,
                children_ages=children_ages
            )
        return None
            
    def _get_discount_info(self, obj):
        discount_type = None
        discount_value = 0
        if hasattr(self, '_min_price_details') and self._min_price_details:
            try:
                if 'pricing' in self._min_price_details and 'discount' in self._min_price_details['pricing']:
                    discount = self._min_price_details['pricing']['discount']
                    discount_type = discount.get('type')
                    discount_value = discount.get('value', 0)
            except (KeyError, AttributeError):
                pass
        return discount_type, discount_value

    def _apply_discount(self, min_price, discount_type, discount_value):
        from decimal import Decimal
        min_price_decimal = Decimal(str(min_price))
        discount_amount = Decimal('0')
        if discount_type and discount_value:
            if discount_type == 'percentage':
                if discount_value <= 100:
                    discount_percentage = Decimal(str(discount_value))
                    discount_amount = (min_price_decimal * discount_percentage) / Decimal('100')
            else:
                discount_amount = Decimal(str(discount_value))
        discounted_price = max(Decimal('0'), min_price_decimal - discount_amount)
        return discounted_price

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Sanatorium detail',
            summary='Detail of a sanatorium',
            description='Complete information about a specific sanatorium',
            value={
                'id': 1,
                'name': 'Chinar Hotel & Spa Naftalan',
                'slug': 'chinar-hotel-spa-naftalan',
                'description': 'Chinar Hotel & Spa Naftalan is a luxury hotel located in the heart of Naftalan city, famous for its healing oil treatments.',
                'treatments': 'The hotel offers various treatments including Naftalan oil baths, mud therapy, and other balneological procedures.',
                'location': {
                    'id': 1,
                    'region': 'Naftalan',
                    'country': 'Azerbaijan'
                },
                'location_type': 'naftalan',
                'map_iframe': '<iframe src="https://maps.google.com/maps?q=40.6461,46.8311&z=15&output=embed"></iframe>',
                'address': 'Naftalan city, Azerbaijan',
                'rating': 4.8,
                'facilities': [
                    {
                        'id': 1,
                        'facility': {
                            'id': 1,
                            'name': 'Swimming Pool',
                            'icon': 'pool-icon.svg'
                        }
                    },
                    {
                        'id': 2,
                        'facility': {
                            'id': 2,
                            'name': 'Spa Center',
                            'icon': 'spa-icon.svg'
                        }
                    }
                ],
                'room_types': [
                    {
                        'id': 1,
                        'name': 'Standard Room',
                        'description': 'Comfortable standard room with all necessary amenities',
                        'min_capacity': 1,
                        'max_capacity': 2,
                        'max_extra_beds': 1,
                        'size': 25,
                        'images': [
                            {
                                'id': 1,
                                'image': 'room1.jpg',
                                'priority': 1
                            }
                        ],
                        'prices': [
                            {
                                'id': 1,
                                'season': {
                                    'id': 1,
                                    'name': 'Summer 2023',
                                    'start_date': '2023-06-01',
                                    'end_date': '2023-08-31',
                                    'is_current': True
                                },
                                'occupancy': 2,
                                'with_treatment': True,
                                'treatment_option': {
                                    'id': 1,
                                    'name': 'Naftalan Oil Bath',
                                    'description': 'Traditional naftalan oil treatment'
                                },
                                'price': 150.0,
                                'currency': {
                                    'id': 1,
                                    'code': 'AZN',
                                    'name': 'Azerbaijani Manat',
                                    'symbol': '₼'
                                },
                                'discount_type': 'percentage',
                                'discount_value': 10,
                                'discounted_price': 135.0
                            }
                        ],
                        'extra_bed_prices': [
                            {
                                'id': 1,
                                'season': {
                                    'id': 1,
                                    'name': 'Summer 2023',
                                    'start_date': '2023-06-01',
                                    'end_date': '2023-08-31',
                                    'is_current': True
                                },
                                'age_group': {
                                    'id': 1,
                                    'name': 'Children 3-11',
                                    'min_age': 3,
                                    'max_age': 11
                                },
                                'with_treatment': False,
                                'treatment_option': None,
                                'price': 50.0,
                                'currency': {
                                    'id': 1,
                                    'code': 'AZN',
                                    'name': 'Azerbaijani Manat',
                                    'symbol': '₼'
                                },
                                'discount_type': None,
                                'discount_value': None,
                                'discounted_price': 50.0
                            }
                        ]
                    }
                ],
                'reviews': [
                    {
                        'id': 1,
                        'full_name': 'Ali Mammadov',
                        'sanatorium': 1,
                        'rating': 5,
                        'content': 'Great hotel with excellent service',
                        'date': '2023-07-15'
                    }
                ],
                'in_home': True,
                'created_at': '2023-01-01T12:00:00Z',
                'updated_at': '2023-05-10T15:30:00Z',
                'images': [
                    {
                        'id': 1,
                        'image': 'hotel-main.jpg',
                        'is_main': True,
                        'priority': 1
                    },
                    {
                        'id': 2,
                        'image': 'hotel-pool.jpg',
                        'is_main': False,
                        'priority': 2
                    }
                ],
                'similar_sanatoriums': [
                    {
                        'id': 2,
                        'name': 'Qarabag Resort & Spa',
                        'slug': 'qarabag-resort-spa',
                        'location': {
                            'id': 1,
                            'region': 'Naftalan',
                            'country': 'Azerbaijan'
                        },
                        'location_type': 'naftalan',
                        'short_description': 'Premium resort with comprehensive treatment facilities',
                        'rating': 4.5,
                        'min_price': 120.0,
                        'min_price_currency': {
                            'id': 1,
                            'code': 'AZN',
                            'name': 'Azerbaijani Manat',
                            'symbol': '₼'
                        },
                        'total_price': 840.0,
                        'min_price_details': {
                            'room_type': 'Double Room',
                            'occupancy': 2,
                            'with_treatment': True,
                            'price_per_night': 120.0,
                            'nights': 7,
                            'discount_applied': True,
                            'discount_type': 'percentage',
                            'discount_value': 10
                        },
                        'is_active': True,
                        'in_home': True,
                        'main_image': {
                            'id': 3,
                            'image': 'qarabag-main.jpg',
                            'is_main': True,
                            'priority': 1
                        },
                        'facilities': []
                    }
                ],
                'min_price': 135.0,
                'min_price_currency': {
                    'id': 1,
                    'code': 'AZN',
                    'name': 'Azerbaijani Manat',
                    'symbol': '₼'
                },
                'total_price': 945.0,
                'min_price_details': {
                    'room_type': 'Standard Room',
                    'occupancy': 2,
                    'with_treatment': True,
                    'price_per_night': 135.0,
                    'nights': 7,
                    'discount_applied': True,
                    'discount_type': 'percentage',
                    'discount_value': 10
                },
                'seo': {
                    'meta_title': 'Chinar Hotel & Spa Naftalan - Luxury Hotel with Naftalan Oil Treatments',
                    'meta_description': 'Discover the healing properties of Naftalan oil in our luxury hotel. Book your stay today for a rejuvenating experience.',
                    'meta_keywords': 'naftalan, spa, hotel, azerbaijan, treatment, healing oil',
                    'og_title': 'Chinar Hotel & Spa - Premium Naftalan Treatments',
                    'og_description': 'Experience the best of Naftalan oil treatments in our luxury hotel.',
                    'og_image': 'https://example.com/images/chinar-og.jpg',
                    'canonical_url': 'https://example.com/sanatoriums/chinar-hotel-spa-naftalan',
                    'no_index': False,
                    'no_follow': False
                }
            }
        )
    ]
)
class SanatoriumSerializer(TranslationMixin, serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    images = SanatoriumImageSerializer(many=True, read_only=True)
    facilities = SanatoriumFacilitySerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    similar_sanatoriums = serializers.SerializerMethodField()
    min_price_details = serializers.SerializerMethodField()
    matched_room_types = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Sanatorium
        fields = [
            'id', 'name', 'slug', 'description', 'treatments', 'location', 'location_type',
            'map_iframe', 'address',
            'rating', 'facilities', 'room_types', 'reviews',
            'in_home', 'created_at', 'updated_at', 'images', 'similar_sanatoriums', 
            'min_price_details', 'seo', 'matched_room_types'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_min_price_details(self, obj):
        list_serializer = SanatoriumSearchSerializer(context=self.context)
        return list_serializer.get_min_price_details(obj)

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_matched_room_types(self, obj):
        request = self.context.get('request')
        if not request:
            return []
        occupancy = None
        try:
            occupancy = int(request.query_params.get('occupancy')) if request.query_params.get('occupancy') else None
        except (ValueError, TypeError):
            pass
        children_ages = []
        try:
            children_ages = [int(age) for age in request.query_params.get('children_ages', '').split(',') if age.strip()]
        except (ValueError, TypeError):
            pass
        today = date.today()
        season = get_season_from_request(request)
        if not season:
            season = _get_current_season(today)
        if not season:
            from apps.sanatoriums.models import RoomPrice
            standard_price = RoomPrice.objects.filter(is_standard=True).order_by('season').first()
            if standard_price and standard_price.season:
                season = standard_price.season
      
        nights = None
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        if check_in_str and check_out_str:
            try:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                nights = (check_out - check_in).days
                if nights <= 0:
                    nights = None
            except Exception:
                nights = None
        matched = []
        for room_type in obj.room_types.all():
            max_extra_beds = room_type.max_extra_beds if room_type.max_extra_beds is not None else float('inf')
            if children_ages and len(children_ages) > max_extra_beds:
                continue
            # children_ages varsa, her biri için uygun extra_bed_price olmalı
            if children_ages:
                if season:
                    extra_bed_prices = room_type.extra_bed_prices.filter(
                        Q(season=season) | Q(season__isnull=True, is_standard=True)
                    )
                else:
                    extra_bed_prices = room_type.extra_bed_prices.all()
                if not extra_bed_prices.exists() and not season:
                    extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
                if not extra_bed_prices.exists() and not season:
                    extra_bed_prices = room_type.extra_bed_prices.all()
                all_children_matched = True
                for age in children_ages:
                    matched_extra = None
                    for ebp in extra_bed_prices:
                        if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                            matched_extra = ebp
                            break
                    if not matched_extra:
                        all_children_matched = False
                        break
                if not all_children_matched:
                    continue
            # Fiyat arama mantığı
            if season:
                prices = room_type.prices.filter(
                    Q(season=season) | Q(season__isnull=True, is_standard=True)
                )
            else:
                prices = room_type.prices.all()
            for with_treatment_value in [True, False]:
                if season:
                    price_candidates = list(prices.filter(with_treatment=with_treatment_value))
                else:
                    price_candidates = list(prices.filter(is_standard=True, with_treatment=with_treatment_value))
                    price_candidates += list(prices.filter(with_treatment=with_treatment_value))
                if occupancy:
                    price_candidates = [p for p in price_candidates if p.occupancy >= occupancy]
                if not price_candidates:
                    continue
                best_price = min(price_candidates, key=lambda p: p.price)
                extra_bed_total = 0
                extra_bed_details = []
                if children_ages:
                    if season:
                        extra_bed_prices = room_type.extra_bed_prices.filter(
                            Q(season=season) | Q(season__isnull=True, is_standard=True)
                        )
                    else:
                        extra_bed_prices = room_type.extra_bed_prices.all()
                    if not extra_bed_prices.exists() and not season:
                        extra_bed_prices = room_type.extra_bed_prices.filter(is_standard=True)
                    if not extra_bed_prices.exists() and not season:
                        extra_bed_prices = room_type.extra_bed_prices.all()
                    for age in children_ages:
                        matched_extra = None
                        for ebp in extra_bed_prices:
                            if ebp.age_group and ebp.age_group.min_age <= age <= ebp.age_group.max_age:
                                matched_extra = ebp
                                break
                        if matched_extra:
                            extra_bed_total += matched_extra.price
                            extra_bed_details.append({
                                'child_age': age,
                                'price_added': matched_extra.price,
                                'currency': CurrencySerializer(matched_extra.currency).data if matched_extra.currency else None
                            })
                discount_type = getattr(best_price, 'discount_type', None)
                discount_value = getattr(best_price, 'discount_value', 0)
                from decimal import Decimal
                discounted_base = float(best_price.price)
                if discount_type and discount_value:
                    if discount_type == 'percentage' and discount_value <= 100:
                        discounted_base = float(Decimal(str(best_price.price)) * (Decimal('1') - Decimal(str(discount_value))/Decimal('100')))
                    elif discount_type == 'fixed':
                        discounted_base = float(Decimal(str(best_price.price)) - Decimal(str(discount_value)))
                discounted_total_price = discounted_base + float(extra_bed_total)
                total_price = None
                total_discounted_price = None
                if nights is not None:
                    total_price = (float(best_price.price) + float(extra_bed_total)) * nights
                    total_discounted_price = discounted_total_price * nights
                discount_amount = None
                if discount_type == 'percentage':
                    discount_amount = float(best_price.price) - discounted_base
                elif discount_type == 'fixed':
                    discount_amount = float(best_price.price) - discounted_base
                else:
                    if float(best_price.price) != discounted_base:
                        discount_amount = float(best_price.price) - discounted_base
                    else:
                        discount_amount = None
                discount_info = {
                    'discount_type': discount_type,
                    'discount_value': discount_value,
                    'discount_amount': discount_amount,
                    'discounted_price': discounted_total_price
                }
                price = float(best_price.price) + float(extra_bed_total)
                final_discounted_price = price
                final_discount_amount = 0
                if discount_type and discount_value:
                    if discount_type == 'percentage' and discount_value <= 100:
                        final_discounted_price = float(Decimal(str(price)) * (Decimal('1') - Decimal(str(discount_value))/Decimal('100')))
                    elif discount_type == 'fixed':
                        final_discounted_price = float(Decimal(str(price)) - Decimal(str(discount_value)))
                    final_discount_amount = price - final_discounted_price
                total_price = price * nights if nights is not None else None
                total_discounted_price = final_discounted_price * nights if nights is not None else None
                discount_info = {
                    'discount_type': discount_type,
                    'discount_value': discount_value,
                    'discount_amount': final_discount_amount,
                    'discounted_price': final_discounted_price
                }
                matched.append({
                    'room_type': MatchedRoomsRoomTypeSerializer(room_type, context=self.context).data,
                    'currency': CurrencySerializer(best_price.currency).data if best_price.currency else None,
                    'season': best_price.season.id if best_price.season else None,
                    'extra_bed_total': float(extra_bed_total),
                    'extra_bed_details': extra_bed_details,
                    'price': price,
                    'nights': nights,
                    'total_price': total_price,
                    'total_discounted_price': total_discounted_price,
                    'discount': discount_info,
                    'occupancy': occupancy,
                    'extra_bed_count': len(children_ages) if children_ages else 0,
                    'with_treatment': getattr(best_price, 'with_treatment', None),
                })
        def sort_key(x):
            return x['total_price'] if x['total_price'] is not None else float('inf')
        return sorted(matched, key=sort_key)

    @extend_schema_field(SEOSerializer)
    def get_seo(self, obj):
        """SEO məlumatlarını ayrı bir obyekt kimi qaytarır"""
        serializer = SEOSerializer(obj, context=self.context)
        return serializer.data
    
    @extend_schema_field(SanatoriumSearchSerializer(many=True))
    def get_similar_sanatoriums(self, obj):
        queryset = Sanatorium.objects.filter(
            location_type=obj.location_type
        ).exclude(id=obj.id)[:3]
        return SanatoriumSearchSerializer(queryset, many=True, context=self.context).data

class ReviewCreateSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['sanatorium', 'full_name', 'rating', 'content']
        extra_kwargs = {
            'sanatorium': {'write_only': True}
        }


class NaftalanSanatoriumsPageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = NaftalanSanatoriumsPage
        fields = [
            'id', 'hero_section_title', 'hero_section_description',
            'main_section_title', 'main_section_description', 'main_section_image',
            'sanatoriums_section_title', 'sanatoriums_section_description',
            'contact_section_title', 'contact_section_description'
        ]


class OtherCitiesSanatoriumsPageSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = OtherCitiesSanatoriumsPage
        fields = [
            'id', 'hero_section_title', 'hero_section_description',
            'main_section_title', 'main_section_description', 'main_section_image',
            'sanatoriums_section_title', 'sanatoriums_section_description',
            'contact_section_title', 'contact_section_description'
        ]



class SanatoriumRoomDetailSerializer(TranslationMixin, serializers.ModelSerializer):
    price_info = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    requested_occupancy = serializers.SerializerMethodField()
    requested_children_ages = serializers.SerializerMethodField()
    sanatorium = serializers.SerializerMethodField()
    price_options = serializers.SerializerMethodField()
    max_capacity = serializers.SerializerMethodField()
    max_extra_beds = serializers.SerializerMethodField()

    class Meta:
        model = RoomType
        fields = (
            "id",
            "name",
            "description",
            "min_capacity",
            "max_capacity",
            "max_extra_beds",
            "size",
            "images",
            "price_info",
            "requested_occupancy",
            "requested_children_ages",
            "price_options",
            "sanatorium",
        )

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_images(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]

    def get_requested_occupancy(self, obj):
        occupancy_str = self.context.get("occupancy")
        return int(occupancy_str) if occupancy_str and occupancy_str.isdigit() else 1

    def get_requested_children_ages(self, obj):
        children_ages_str = self.context.get("children_ages", "")
        if not children_ages_str:
            return []
        return [int(age) for age in children_ages_str.split(',') if age.strip().isdigit()]

    @extend_schema_field(serializers.DictField())
    def get_price_info(self, obj):
        context = self.context
        occupancy = self.get_requested_occupancy(obj)
        children_ages = self.get_requested_children_ages(obj)
        with_treatment = context.get("with_treatment")
        if with_treatment is not None:
            # String olarak gelirse bool'a çevir
            if isinstance(with_treatment, str):
                with_treatment = with_treatment.lower() in ["true", "1", "yes"]
        sanatorium = obj.sanatorium
        search_serializer = SanatoriumSearchSerializer(instance=sanatorium, context=context)
        matched_rooms = search_serializer.get_matched_room_types(sanatorium)
        for room in matched_rooms:
            if room['room_type']['id'] == obj.id:
                if with_treatment is None or room.get('with_treatment') == with_treatment:
                    price_info = room.copy()
                    price_info.pop('room_type', None)
                    return price_info
        return None

    @extend_schema_field(SanatoriumSerializer)
    def get_sanatorium(self, obj):
        return SanatoriumSerializer(obj.sanatorium, context=self.context).data

    @extend_schema_field(
        serializers.ListField(
            child=serializers.DictField(
                child=serializers.BooleanField()
            ),
            help_text="Her bir mevcut with_treatment seçeneği için obje döner."
        )
    )
    def get_price_options(self, obj):
        from datetime import date
        try:
            from apps.sanatoriums.models import Season
            today = date.today()
            current_season = Season.objects.filter(start_date__lte=today, end_date__gte=today).first()
        except Exception:
            current_season = None
        request = self.context.get("request")
        occupancy_str = request.query_params.get("occupancy") if request else None
        occupancy = int(occupancy_str) if occupancy_str and occupancy_str.isdigit() else 1
        options = []
        for with_treatment in [True, False]:
            if current_season:
                price = obj.prices.filter(with_treatment=with_treatment, occupancy__gte=occupancy, season=current_season).order_by('occupancy').first()
            else:
                price = obj.prices.filter(with_treatment=with_treatment, occupancy__gte=occupancy).order_by('occupancy').first()
            if price:
                options.append({"with_treatment": with_treatment})
        return options

    @extend_schema_field(serializers.IntegerField())
    def get_max_capacity(self, obj):
        from datetime import date
        try:
            from apps.sanatoriums.models import Season
            today = date.today()
            current_season = Season.objects.filter(start_date__lte=today, end_date__gte=today).first()
        except Exception:
            current_season = None
        # Find max occupancy from prices for current season
        max_by_room_type = None
        if hasattr(obj, 'sanatorium') and hasattr(obj.sanatorium, 'room_types'):
            found = obj.sanatorium.room_types.filter(id=obj.id).first()
            if found and hasattr(found, 'prices'):
                if current_season:
                    price_occupancies = [p.occupancy for p in found.prices.filter(season=current_season) if p.occupancy is not None]
                else:
                    price_occupancies = [p.occupancy for p in found.prices.all() if p.occupancy is not None]
                if price_occupancies:
                    max_by_room_type = max(price_occupancies)
        if obj.max_capacity is not None and max_by_room_type is not None:
            return min(obj.max_capacity, max_by_room_type)
        elif obj.max_capacity is None and max_by_room_type is not None:
            return max_by_room_type
        return obj.max_capacity

    @extend_schema_field(serializers.IntegerField())
    def get_max_extra_beds(self, obj):
        from datetime import date
        try:
            from apps.sanatoriums.models import Season
            today = date.today()
            current_season = Season.objects.filter(start_date__lte=today, end_date__gte=today).first()
        except Exception:
            current_season = None
        # Find if there are extra_bed_prices for this room in current season
        has_extra_bed = False
        if hasattr(obj, 'sanatorium') and hasattr(obj.sanatorium, 'room_types'):
            found = obj.sanatorium.room_types.filter(id=obj.id).first()
            if found and hasattr(found, 'extra_bed_prices'):
                if current_season:
                    if found.extra_bed_prices.filter(season=current_season).exists():
                        has_extra_bed = True
                else:
                    if found.extra_bed_prices.exists():
                        has_extra_bed = True
        if obj.max_extra_beds is not None and has_extra_bed:
            return obj.max_extra_beds
        return 0

