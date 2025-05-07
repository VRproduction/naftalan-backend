from rest_framework import serializers
from .models import Booking, GuestDetail, ExtraBedBooking, BookingNote, Season
from apps.sanatoriums.serializers import (
    SanatoriumSearchSerializer, RoomTypeSerializer,
    SeasonSerializer, TreatmentOptionSerializer, CurrencySerializer, ExtraBedPriceSerializer
)
from utils.api.mixins.translation import TranslationMixin
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta

class GuestDetailSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = GuestDetail
        fields = ['id', 'first_name', 'last_name', 'gender', 'date_of_birth', 'age_category', 'is_main_guest']

class ExtraBedBookingSerializer(TranslationMixin, serializers.ModelSerializer):
    treatment_option_detail = TreatmentOptionSerializer(source='treatment_option', read_only=True)
    extra_bed_price_detail = ExtraBedPriceSerializer(source='extra_bed_price', read_only=True)
    
    class Meta:
        model = ExtraBedBooking
        fields = ['id', 'quantity', 'for_adult', 'with_treatment', 'treatment_option', 
                 'treatment_option_detail', 'price_per_night', 'extra_bed_price', 'extra_bed_price_detail']
        extra_kwargs = {
            'treatment_option': {'write_only': True},
            'extra_bed_price': {'write_only': True}
        }

class BookingNoteSerializer(TranslationMixin, serializers.ModelSerializer):
    class Meta:
        model = BookingNote
        fields = ['id', 'note', 'created_at']
        read_only_fields = ['created_at']

class BookingSerializer(TranslationMixin, serializers.ModelSerializer):
    guests = GuestDetailSerializer(many=True, read_only=True)
    extra_beds = ExtraBedBookingSerializer(many=True, read_only=True)
    notes = BookingNoteSerializer(many=True, read_only=True)
    
    sanatorium_detail = SanatoriumSearchSerializer(source='sanatorium', read_only=True)
    room_type_detail = RoomTypeSerializer(source='room_type', read_only=True)
    season_detail = SeasonSerializer(source='season', read_only=True)
    treatment_option_detail = TreatmentOptionSerializer(source='treatment_option', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    days_of_stay = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'first_name', 'last_name', 'email', 'phone',
            'sanatorium', 'sanatorium_detail', 'room_type', 'room_type_detail', 
            'season', 'season_detail', 'check_in_date', 'check_out_date',
            'adults', 'children', 'special_requests', 'with_treatment', 
            'treatment_option', 'treatment_option_detail', 'status',
            'total_price', 'currency', 'currency_detail', 'created_at', 'updated_at',
            'days_of_stay', 'guests', 'extra_beds', 'notes'
        ]
        read_only_fields = ['booking_reference', 'created_at', 'updated_at', 'days_of_stay']
        extra_kwargs = {
            'sanatorium': {'write_only': True},
            'room_type': {'write_only': True},
            'season': {'write_only': True},
            'treatment_option': {'write_only': True},
            'currency': {'write_only': True},
        }
        
    def get_days_of_stay(self, obj):
        return (obj.check_out_date - obj.check_in_date).days

class BookingCreateSerializer(TranslationMixin, serializers.ModelSerializer):
    guests = GuestDetailSerializer(many=True, required=False)
    extra_beds = ExtraBedBookingSerializer(many=True, required=False)

    class Meta:
        model = Booking
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'sanatorium', 'room_type', 'season', 'check_in_date', 'check_out_date',
            'adults', 'children', 'special_requests', 'with_treatment', 'treatment_option',
            'total_price', 'currency', 'guests', 'extra_beds'
        ]
        extra_kwargs = {
            'season': {'required': False}
        }
    
    def validate(self, data):
        # Check if check_out_date is after check_in_date
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError({"check_out_date": _("Çıxış tarixi giriş tarixindən sonra olmalıdır")})

        # Check if check_in_date is not in the past
        if data['check_in_date'] < date.today():
            raise serializers.ValidationError({"check_in_date": _("Giriş tarixi keçmiş tarixdə ola bilməz")})

        # Ensure check_in_date is at least a day from now
        if data['check_in_date'] < date.today() + timedelta(days=1):
            raise serializers.ValidationError({"check_in_date": _("Rezervasiya ən azı bir gün əvvəldən olmalıdır")})

        # Try to determine season if not provided
        if 'season' not in data or data['season'] is None:
            check_in_date = data['check_in_date']
            season = Season.objects.filter(
                start_date__lte=check_in_date,
                end_date__gte=check_in_date
            ).first()
            if season:
                data['season'] = season

        return data
    
    def create(self, validated_data):
        guests_data = validated_data.pop('guests', [])
        extra_beds_data = validated_data.pop('extra_beds', [])
        
        # Set default status to pending
        validated_data['status'] = 'new'
        
        # Generate booking reference
        import random
        import string
        
        # Generate a random 10-character reference
        chars = string.ascii_uppercase + string.digits
        reference = ''.join(random.choice(chars) for _ in range(10))
        
        # Make sure reference is unique
        while Booking.objects.filter(booking_reference=reference).exists():
            reference = ''.join(random.choice(chars) for _ in range(10))
            
        validated_data['booking_reference'] = reference
        
        # Create the booking
        booking = Booking.objects.create(**validated_data)
        
        # Create guests
        for guest_data in guests_data:
            GuestDetail.objects.create(booking=booking, **guest_data)
        
        # Create extra beds
        for extra_bed_data in extra_beds_data:
            ExtraBedBooking.objects.create(booking=booking, **extra_bed_data)
        
        return booking 