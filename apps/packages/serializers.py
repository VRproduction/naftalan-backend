from rest_framework import serializers
from .models import Package, PackageInclusion, PackageOrder
from django.utils.translation import gettext_lazy as _

class PackageInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageInclusion
        fields = ['id', 'name', 'priority']

class PackageSerializer(serializers.ModelSerializer):
    inclusions = PackageInclusionSerializer(many=True, read_only=True)
    sanatorium_name = serializers.CharField(source='sanatorium.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)

    class Meta:
        model = Package
        fields = [
            'id', 'name', 'slug', 'sanatorium', 'sanatorium_name',
            'duration', 'discount_type', 'discount_type_display',
            'discount_value', 'is_active', 'is_featured',
            'original_price', 'discounted_price', 'currency',
            'currency_code', 'currency_symbol', 'occupancy',
            'inclusions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'discounted_price']

class PackageOrderSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)

    class Meta:
        model = PackageOrder
        fields = [
            'id', 'package', 'package_name', 'first_name', 'last_name',
            'email', 'phone', 'check_in', 'check_out', 'adults', 'children',
            'notes', 'status', 'status_display', 'total_price', 'currency',
            'currency_code', 'currency_symbol', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PackageOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageOrder
        fields = [
            'package', 'first_name', 'last_name', 'email', 'phone',
            'check_in', 'check_out', 'adults', 'children', 'notes'
        ]

    def validate(self, data):
        package = data['package']
        adults = data['adults']
        children = data['children']
        check_in = data['check_in']
        check_out = data['check_out']

        # Validate occupancy
        if adults + children > package.occupancy:
            raise serializers.ValidationError({
                'adults': _("Ümumi nəfər sayı paketin tutumundan çox ola bilməz"),
                'children': _("Ümumi nəfər sayı paketin tutumundan çox ola bilməz")
            })

        # Validate dates
        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': _("Gediş tarixi gəliş tarixindən sonra olmalıdır")
            })

        # Calculate total price
        duration = (check_out - check_in).days
        total_price = package.discounted_price * duration * (adults + children)
        data['total_price'] = total_price
        data['currency'] = package.currency

        return data
