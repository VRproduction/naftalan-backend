from django.shortcuts import render
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from .models import Booking, GuestDetail, ExtraBedBooking
from .serializers import (
    BookingSerializer, BookingCreateSerializer,
    GuestDetailSerializer, ExtraBedBookingSerializer
)
from apps.sanatoriums.models import RoomType, Sanatorium, Season
from utils.api.pagination.page_number_pagination import CustomPageNumberPagination


class AvailabilityCheckView(generics.GenericAPIView):
    """
    Check room availability for a given date range
    """
    def post(self, request, *args, **kwargs):
        # Get parameters from request
        sanatorium_id = request.data.get('sanatorium_id')
        check_in_date = request.data.get('check_in_date')
        check_out_date = request.data.get('check_out_date')
        guests = request.data.get('guests', 1)
        
        if not all([sanatorium_id, check_in_date, check_out_date]):
            return Response(
                {"detail": _("Sanatorium ID, giriş və çıxış tarixləri tələb olunur")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sanatorium = Sanatorium.objects.get(id=sanatorium_id)
        except Sanatorium.DoesNotExist:
            return Response(
                {"detail": _("Belə bir sanatorium tapılmadı")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all room types for this sanatorium
        room_types = RoomType.objects.filter(sanatorium=sanatorium)
        
        # Check if any room is available
        available_rooms = []
        
        for room_type in room_types:
            # Check capacity
            if room_type.min_capacity <= guests <= room_type.max_capacity:
                # Check existing bookings for overlap
                bookings_count = Booking.objects.filter(
                    room_type=room_type,
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date
                ).count()
                
                # TODO: Add inventory management to check how many rooms of each type are available
                # For now, we'll just assume there's only one room per type
                if bookings_count == 0:
                    from apps.sanatoriums.serializers import RoomTypeSerializer
                    available_rooms.append(RoomTypeSerializer(room_type).data)
        
        return Response({
            "available_room_types": available_rooms,
            "sanatorium_id": sanatorium_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "guests": guests
        })


class PriceCalculatorView(generics.GenericAPIView):
    """
    Calculate price for a booking based on selected options
    """
    def post(self, request, *args, **kwargs):
        # Get parameters from request
        room_type_id = request.data.get('room_type_id')
        check_in_date = request.data.get('check_in_date')
        check_out_date = request.data.get('check_out_date')
        adults = int(request.data.get('adults', 1))
        children = int(request.data.get('children', 0))
        with_treatment = request.data.get('with_treatment', True)
        treatment_option_id = request.data.get('treatment_option_id')
        extra_beds = request.data.get('extra_beds', [])
        
        if not all([room_type_id, check_in_date, check_out_date]):
            return Response(
                {"detail": _("Otaq növü ID, giriş və çıxış tarixləri tələb olunur")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            room_type = RoomType.objects.get(id=room_type_id)
            # Find the current season
            from datetime import datetime
            check_in_date_obj = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            season = Season.objects.filter(
                start_date__lte=check_in_date_obj,
                end_date__gte=check_in_date_obj
            ).first()
                
        except RoomType.DoesNotExist:
            return Response(
                {"detail": _("Belə bir otaq növü tapılmadı")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate number of nights
        from datetime import datetime
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        nights = (check_out - check_in).days
        
        if nights <= 0:
            return Response(
                {"detail": _("Çıxış tarixi giriş tarixindən sonra olmalıdır")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find room price
        total_price = 0
        currency = None
        room_price = None
        
        # Get room price based on occupancy and treatment
        if season:
            # Try to find price for current season first
            room_price = room_type.prices.filter(
                season=season,
                occupancy=adults,
                with_treatment=with_treatment
            ).first()
        
        # If no season or no price found for the season, try to find standard price
        if not room_price:
            room_price = room_type.prices.filter(
                season__isnull=True,
                is_standard=True,
                occupancy=adults,
                with_treatment=with_treatment
            ).first()
        
        if not room_price:
            return Response(
                {"detail": _("Seçilmiş parametrlər üçün qiymət tapılmadı")},
                status=status.HTTP_404_NOT_FOUND
            )
            
        currency = room_price.currency
        total_price = room_price.price * nights
        
        # Calculate extra bed prices
        extra_bed_prices = []
        
        for extra_bed in extra_beds:
            age_group_id = extra_bed.get('age_group_id')
            quantity = extra_bed.get('quantity', 1)
            with_treatment_bed = extra_bed.get('with_treatment', False)
            treatment_option_id_bed = extra_bed.get('treatment_option_id')
            
            extra_bed_price = None
            
            # Try to find extra bed price for current season first
            if season:
                extra_bed_price = room_type.extra_bed_prices.filter(
                    season=season,
                    age_group_id=age_group_id,
                    with_treatment=with_treatment_bed
                ).first()
            
            # If no price found for the season, try to find standard price
            if not extra_bed_price:
                extra_bed_price = room_type.extra_bed_prices.filter(
                    season__isnull=True,
                    is_standard=True,
                    age_group_id=age_group_id,
                    with_treatment=with_treatment_bed
                ).first()
            
            if not extra_bed_price:
                continue
                
            bed_price = extra_bed_price.price * quantity * nights
            total_price += bed_price
            
            extra_bed_prices.append({
                'age_group_id': age_group_id,
                'quantity': quantity,
                'with_treatment': with_treatment_bed,
                'treatment_option_id': treatment_option_id_bed,
                'price_per_night': extra_bed_price.price,
                'total_price': bed_price
            })
        
        return Response({
            'room_type_id': room_type_id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'nights': nights,
            'adults': adults,
            'children': children,
            'with_treatment': with_treatment,
            'treatment_option_id': treatment_option_id,
            'room_price_per_night': room_price.price,
            'currency': {
                'id': currency.id,
                'code': currency.code,
                'symbol': currency.symbol
            },
            'extra_beds': extra_bed_prices,
            'total_price': total_price
        })


class BookingCreateView(generics.CreateAPIView):
    """
    Create a new booking
    """
    serializer_class = BookingCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Return full booking details
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class BookingDetailView(generics.RetrieveAPIView):
    """
    Retrieve a booking by reference number
    """
    serializer_class = BookingSerializer
    lookup_field = 'booking_reference'
    queryset = Booking.objects.all()


class BookingListView(generics.ListAPIView):
    """
    List all bookings with filters (admin only)
    """
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'sanatorium', 'room_type', 'check_in_date', 'check_out_date']
    search_fields = ['booking_reference', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'check_in_date', 'check_out_date']
