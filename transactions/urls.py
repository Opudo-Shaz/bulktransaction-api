from django.urls import path
from .views import BulkTransactionCreateView

urlpatterns = [
    path("transactions/bulk/", BulkTransactionCreateView.as_view(), name="bulk-transactions"),
]