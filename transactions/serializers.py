from decimal import Decimal
from rest_framework import serializers
from .models import Account, Transaction


class TransactionInputSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    transaction_type = serializers.ChoiceField(choices=Transaction.TransactionType.choices)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class AccountBulkSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    account_number = serializers.CharField(max_length=50)
    transactions = TransactionInputSerializer(many=True)

    def validate_transactions(self, value):
        if not value:
            raise serializers.ValidationError("Each account must include at least one transaction.")
        return value


class BulkTransactionRequestSerializer(serializers.Serializer):
    accounts = serializers.ListField(child=AccountBulkSerializer(), allow_empty=False)