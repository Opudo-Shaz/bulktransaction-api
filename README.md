# Bulk Transaction API

A Django REST Framework API that accepts a list of accounts, each with a
nested list of transactions, and inserts everything in a single request
using `bulk_create()`.

## Tech stack
- Python 3.12
- Django 6.0
- Django REST Framework

## Setup

1. Clone the repository:
```bash
   git clone https://github.com/Opudo-Shaz/bulktransaction-api.git
   cd bulktransaction-api
```

2. Create a virtual environment:

   **Linux / macOS:**
```bash
   python3 -m venv venv
   source venv/bin/activate
```

   **Windows (Command Prompt):**
```cmd
   python -m venv venv
   venv\Scripts\activate
```

   **Windows (PowerShell):**
```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
```

   You'll know it worked when your terminal prompt shows `(venv)` at the start.

   > **Note:** On some Linux distributions (Debian/Ubuntu 23.04+), `python3 -m venv`
   > may fail or `pip install` may refuse to run outside a virtual environment
   > with an "externally-managed-environment" error. If `python3 -m venv` itself
   > fails, install the venv module first:
   > ```bash
   > sudo apt install python3-full python3-venv
   > ```
   > Then retry creating the virtual environment above. Always activate the
   > virtual environment (you should see `(venv)` in your prompt) before running
   > `pip install`.

3. Install dependencies (with the virtual environment active):
```bash
   pip install -r requirements.txt
```

4. Run migrations:
```bash
   python manage.py migrate
```

5. Start the dev server:
```bash
   python manage.py runserver
```

   The API is available at `http://127.0.0.1:8000/api/transactions/bulk/`.

## Running tests

With the virtual environment active:
```bash
python manage.py test transactions
```

This runs the automated test suite covering:
- Successful bulk creation of accounts and transactions
- Validation rejection of invalid transaction data
- Rejection of duplicate account numbers
- Graceful handling of unexpected database errors (mocked failure, returns a
  generic 500 response without leaking internal error details)
## API

POST /api/transactions/bulk/

Request body:
{
  "accounts": [
    {
      "name": "John Mwangi",
      "account_number": "KE001234",
      "transactions": [
        {"reference": "TXN-001", "amount": "1500.00", "transaction_type": "credit", "description": "Salary payment"}
      ]
    }
  ]
}

Success response (201):
{"success": true, "accounts_created": 1, "transactions_created": 1}

Validation error response (400):
{"success": false, "errors": {...}}

## Design notes
- Entire payload validated by nested DRF serializers before any DB writes.
- Duplicate account_number values (in-payload or already existing) rejected before writes.
- Accounts and Transactions each inserted with a single bulk_create() call — no per-record loop.
- Writes wrapped in transaction.atomic() so a failure mid-way rolls back everything.