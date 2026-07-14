from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from transactions.models import Account, Transaction


class BulkTransactionCreateTests(APITestCase):

    def setUp(self):
        self.url = reverse("bulk-transactions")

    def test_successful_bulk_creation(self):
        payload = {
            "accounts": [
                {
                    "name": "John Mwangi",
                    "account_number": "KE001234",
                    "transactions": [
                        {"reference": "TXN-001", "amount": "1500.00", "transaction_type": "credit", "description": "Salary"},
                        {"reference": "TXN-002", "amount": "200.00", "transaction_type": "debit", "description": "Airtime"},
                    ],
                }
            ]
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["accounts_created"], 1)
        self.assertEqual(response.data["transactions_created"], 2)

        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_invalid_transaction_type_rejected(self):
        payload = {
            "accounts": [
                {
                    "name": "Bad Actor",
                    "account_number": "KE999999",
                    "transactions": [
                        {"reference": "TXN-BAD", "transaction_type": "not_a_real_type"}
                    ],
                }
            ]
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

        # Nothing should have been saved
        self.assertEqual(Account.objects.count(), 0)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_duplicate_account_number_rejected(self):
        Account.objects.create(name="Existing Person", account_number="KE001234")

        payload = {
            "accounts": [
                {
                    "name": "Duplicate Guy",
                    "account_number": "KE001234",
                    "transactions": [
                        {"reference": "TXN-DUP", "amount": "10.00", "transaction_type": "credit"}
                    ],
                }
            ]
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("KE001234", response.data["errors"]["account_numbers_already_exist"])

        # Still just the one pre-existing account, no transaction added
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 0)