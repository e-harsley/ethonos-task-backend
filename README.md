# Deji's Wallet API - Backend

A comprehensive Django-based wallet application backend built with Django Ninja for managing finances, cards, and transactions.

## Features

- **User Authentication** (JWT-based)
  - User registration
  - Login/Logout
  - Token refresh
  - Protected routes

- **Wallet Management**
  - View wallet balance
  - Track income and expenses
  - Multiple currency support (default: NGN)

- **Card Management**
  - Link multiple cards (Credit/Debit/Bank Account)
  - Set primary card
  - View all linked cards
  - Update/Delete cards

- **Transactions**
  - Create income/expense transactions
  - Send money to other users
  - Receive money from other users
  - Transaction history with pagination
  - Transaction categories

- **QR Code Functionality**
  - Generate QR codes for receiving money
  - Scan QR codes to send money
  - Set expiration time for QR codes
  - Optional fixed amounts

- **Statistics & Analytics**
  - Income/Expense breakdown
  - Monthly statistics
  - Top spending categories
  - Dashboard with recent transactions

## Tech Stack

- Django 5.1.5
- Django Ninja 1.3.0 (Fast REST API framework)
- PyJWT 2.10.1 (JWT authentication)
- PostgreSQL/SQLite (Database)
- QRCode 8.0 (QR code generation)
- Pillow 11.1.0 (Image processing)

## Installation

### 1. Clone the repository

```bash
cd ethnosdemo
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/openapi.json`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user details (Protected)

### Wallet

- `GET /api/wallet/wallet` - Get wallet details (Protected)

### Cards

- `GET /api/wallet/cards` - List all cards (Protected)
- `POST /api/wallet/cards` - Add a new card (Protected)
- `GET /api/wallet/cards/{id}` - Get card details (Protected)
- `PUT /api/wallet/cards/{id}` - Update card (Protected)
- `DELETE /api/wallet/cards/{id}` - Delete card (Protected)

### Transactions

- `GET /api/wallet/transactions` - List transactions (Protected)
- `GET /api/wallet/transactions/{id}` - Get transaction details (Protected)
- `POST /api/wallet/transactions` - Create transaction (Protected)
- `POST /api/wallet/send-money` - Send money to another user (Protected)

### QR Codes

- `POST /api/wallet/qr-codes/generate` - Generate QR code (Protected)
- `GET /api/wallet/qr-codes` - List all QR codes (Protected)
- `POST /api/wallet/qr-codes/scan` - Scan and pay via QR code (Protected)

### Statistics

- `GET /api/wallet/stats` - Get income/expense statistics (Protected)
- `GET /api/wallet/dashboard` - Get dashboard data (Protected)

## Usage Examples

### 1. Register a New User

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+234 123 456 7890"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Get Current User (with JWT)

```bash
curl -X GET http://127.0.0.1:8000/api/auth/me \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Add a Card

```bash
curl -X POST http://127.0.0.1:8000/api/wallet/cards \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "card_number": "4111111111111111",
    "card_type": "credit",
    "card_holder_name": "John Doe",
    "expiry_date": "12/25",
    "bank_name": "First Bank",
    "is_primary": true
  }'
```

### 5. Create a Transaction

```bash
curl -X POST http://127.0.0.1:8000/api/wallet/transactions \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "transaction_type": "income",
    "amount": 250000.00,
    "description": "Monthly Salary",
    "category": "Salary"
  }'
```

### 6. Send Money

```bash
curl -X POST http://127.0.0.1:8000/api/wallet/send-money \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_email": "recipient@example.com",
    "amount": 5000.00,
    "description": "Payment for services",
    "category": "Transfer"
  }'
```

### 7. Generate QR Code

```bash
curl -X POST http://127.0.0.1:8000/api/wallet/qr-codes/generate \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 1000.00,
    "description": "Payment request",
    "expires_in_hours": 24
  }'
```

### 8. Get Statistics

```bash
curl -X GET http://127.0.0.1:8000/api/wallet/stats?months=6 \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Models

### User
- Email (unique)
- First Name, Last Name
- Phone Number
- Date Joined
- Is Active, Is Staff

### Wallet
- User (OneToOne)
- Balance
- Currency
- Created/Updated timestamps

### Card
- User (Foreign Key)
- Card Number, Card Type
- Card Holder Name
- Expiry Date, Bank Name
- Is Primary flag

### Transaction
- User (Foreign Key)
- Transaction ID (UUID)
- Type (income/expense/transfer_in/transfer_out)
- Amount, Description
- Category, Status
- Recipient/Sender Email
- Created timestamp

### QR Code
- User (Foreign Key)
- QR Code string (unique)
- Amount (optional)
- Description
- Is Active, Expires At
- Created timestamp

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

To add more origins, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

## Environment Variables

For production, create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

Create a superuser:
```bash
python manage.py createsuperuser
```

## Development

### Run Tests

```bash
python manage.py test
```

### Create New Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Populate Test Data

You can use the Django shell to create test data:

```bash
python manage.py shell
```

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper web server (Gunicorn + Nginx)
4. Use environment variables for sensitive data
5. Enable HTTPS
6. Set up proper logging
7. Configure static files serving

## License

This project is built for the Ethnos Technologies assessment.

## Support

For issues and questions, please contact the development team.
