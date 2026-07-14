from django.db import transaction as db_transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Account, Transaction
from .serializers import BulkTransactionRequestSerializer


class BulkTransactionCreateView(APIView):

    def post(self, request):
        # 1. Validate everything first, before touching the database
        serializer = BulkTransactionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        accounts_data = serializer.validated_data["accounts"]

        # 2. Reject duplicate account numbers (already in DB, or repeated in payload)
        incoming_numbers = [acc["account_number"] for acc in accounts_data]
        duplicates_in_payload = {n for n in incoming_numbers if incoming_numbers.count(n) > 1}
        existing_numbers = set(
            Account.objects.filter(account_number__in=incoming_numbers)
            .values_list("account_number", flat=True)
        )

        if duplicates_in_payload or existing_numbers:
            return Response(
                {
                    "success": False,
                    "errors": {
                        "duplicate_account_numbers_in_request": list(duplicates_in_payload),
                        "account_numbers_already_exist": list(existing_numbers),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Write everything inside one atomic transaction
        with db_transaction.atomic():
            account_objs = [
                Account(name=acc["name"], account_number=acc["account_number"])
                for acc in accounts_data
            ]
            created_accounts = Account.objects.bulk_create(account_objs)

            accounts_by_number = {
                a.account_number: a
                for a in Account.objects.filter(account_number__in=incoming_numbers)
            }

            transaction_objs = []
            for acc in accounts_data:
                account_obj = accounts_by_number[acc["account_number"]]
                for tx in acc["transactions"]:
                    transaction_objs.append(
                        Transaction(
                            reference=tx["reference"],
                            amount=tx["amount"],
                            transaction_type=tx["transaction_type"],
                            description=tx.get("description", ""),
                            account=account_obj,
                        )
                    )

            Transaction.objects.bulk_create(transaction_objs)

        # 4. Meaningful response
        return Response(
            {
                "success": True,
                "accounts_created": len(created_accounts),
                "transactions_created": len(transaction_objs),
            },
            status=status.HTTP_201_CREATED,
        )
