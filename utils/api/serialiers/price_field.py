from rest_framework import serializers
from djmoney.money import Money

class PriceField(serializers.Field):
    """Custom serializer field to handle price as {amount, currency}"""

    def to_representation(self, value):
        """Convert MoneyField to JSON format"""
        return {
            "amount": float(value.amount),
            "currency": value.currency
        }

    def to_internal_value(self, data):
        """Convert JSON to MoneyField format"""
        if not isinstance(data, dict) or "amount" not in data or "currency" not in data:
            raise serializers.ValidationError("Price must be a dictionary with 'amount' and 'currency' keys.")

        try:
            amount = float(data["amount"])  # Sayıyı float olarak al
            currency = str(data["currency"]).upper()  # Para birimini büyük harfe çevir
        except (ValueError, TypeError):
            raise serializers.ValidationError("Amount must be a number and currency must be a string.")

        return Money(amount, currency)