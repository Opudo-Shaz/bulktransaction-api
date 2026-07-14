from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.account_number})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    description = models.CharField(max_length=255, blank=True, default="")
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    def __str__(self):
        return f"{self.reference} - {self.amount}"