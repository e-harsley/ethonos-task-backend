from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List
import qrcode
import io
import base64
import uuid

from .models import Wallet, Card, Transaction, QRCode as QRCodeModel
from .schemas import (
    WalletSchema, CardCreateSchema, CardSchema, CardUpdateSchema,
    TransactionCreateSchema, TransactionSchema, QRCodeCreateSchema,
    QRCodeSchema, QRCodeScanSchema, SendMoneySchema, StatsSchema,
    DashboardSchema, MessageSchema, MonthlyStatsSchema
)
from accounts.models import User
from accounts.auth import JWTAuth

router = Router()


# ============ Wallet Endpoints ============
@router.get("/wallet", response=WalletSchema, auth=JWTAuth())
def get_wallet(request):
    """Get user's wallet details"""
    wallet, created = Wallet.objects.get_or_create(user=request.auth)
    return wallet


# ============ Card Endpoints ============
@router.get("/cards", response=List[CardSchema], auth=JWTAuth())
def list_cards(request):
    """Get all user's cards"""
    cards = Card.objects.filter(user=request.auth)
    return list(cards)


@router.post("/cards", response={201: CardSchema, 400: MessageSchema}, auth=JWTAuth())
def create_card(request, payload: CardCreateSchema):
    """Add a new card"""
    try:
        card = Card.objects.create(
            user=request.auth,
            **payload.dict()
        )
        return 201, card
    except Exception as e:
        return 400, {"message": f"Error creating card: {str(e)}"}


@router.get("/cards/{card_id}", response=CardSchema, auth=JWTAuth())
def get_card(request, card_id: int):
    """Get a specific card"""
    card = get_object_or_404(Card, id=card_id, user=request.auth)
    return card


@router.put("/cards/{card_id}", response={200: CardSchema, 400: MessageSchema}, auth=JWTAuth())
def update_card(request, card_id: int, payload: CardUpdateSchema):
    """Update a card"""
    card = get_object_or_404(Card, id=card_id, user=request.auth)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(card, attr, value)

    card.save()
    return 200, card


@router.delete("/cards/{card_id}", response={200: MessageSchema, 404: MessageSchema}, auth=JWTAuth())
def delete_card(request, card_id: int):
    """Delete a card"""
    card = get_object_or_404(Card, id=card_id, user=request.auth)
    card.delete()
    return 200, {"message": "Card deleted successfully"}


# ============ Transaction Endpoints ============
@router.get("/transactions", response=List[TransactionSchema], auth=JWTAuth())
def list_transactions(request, limit: int = 50, offset: int = 0):
    """Get user's transactions"""
    transactions = Transaction.objects.filter(user=request.auth)[offset:offset+limit]
    # Convert UUID to string for each transaction
    for txn in transactions:
        txn.transaction_id = str(txn.transaction_id)
    return list(transactions)


@router.get("/transactions/{transaction_id}", response=TransactionSchema, auth=JWTAuth())
def get_transaction(request, transaction_id: str):
    """Get a specific transaction"""
    txn = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.auth)
    txn.transaction_id = str(txn.transaction_id)
    return txn


@router.post("/transactions", response={201: TransactionSchema, 400: MessageSchema}, auth=JWTAuth())
def create_transaction(request, payload: TransactionCreateSchema):
    """Create a new transaction (income/expense)"""
    try:
        with transaction.atomic():
            # Create transaction
            txn = Transaction.objects.create(
                user=request.auth,
                **payload.dict()
            )

            # Update wallet balance
            wallet = request.auth.wallet
            if payload.transaction_type in ['income', 'transfer_in']:
                wallet.balance += payload.amount
            elif payload.transaction_type in ['expense', 'transfer_out']:
                if wallet.balance < payload.amount:
                    return 400, {"message": "Insufficient balance"}
                wallet.balance -= payload.amount

            wallet.save()

            # Convert UUID to string for response
            txn.transaction_id = str(txn.transaction_id)
            return 201, txn
    except Exception as e:
        return 400, {"message": f"Error creating transaction: {str(e)}"}


# ============ Send/Receive Money Endpoints ============
@router.post("/send-money", response={200: TransactionSchema, 400: MessageSchema, 404: MessageSchema}, auth=JWTAuth())
def send_money(request, payload: SendMoneySchema):
    """Send money to another user"""
    try:
        # Check if recipient exists
        recipient = User.objects.filter(email=payload.recipient_email).first()
        if not recipient:
            return 404, {"message": "Recipient not found"}

        if recipient.id == request.auth.id:
            return 400, {"message": "Cannot send money to yourself"}

        with transaction.atomic():
            # Check sender balance
            sender_wallet = request.auth.wallet
            if sender_wallet.balance < payload.amount:
                return 400, {"message": "Insufficient balance"}

            # Create sender transaction (debit)
            sender_txn = Transaction.objects.create(
                user=request.auth,
                transaction_type='transfer_out',
                amount=payload.amount,
                description=payload.description,
                category=payload.category,
                recipient_email=payload.recipient_email,
                status='completed'
            )

            # Create recipient transaction (credit)
            Transaction.objects.create(
                user=recipient,
                transaction_type='transfer_in',
                amount=payload.amount,
                description=f"Received from {request.auth.email}",
                category=payload.category,
                sender_email=request.auth.email,
                status='completed'
            )

            # Update balances
            sender_wallet.balance -= payload.amount
            sender_wallet.save()

            recipient_wallet, created = Wallet.objects.get_or_create(user=recipient)
            recipient_wallet.balance += payload.amount
            recipient_wallet.save()

            # Convert UUID to string for response
            sender_txn.transaction_id = str(sender_txn.transaction_id)
            return 200, sender_txn
    except Exception as e:
        return 400, {"message": f"Error sending money: {str(e)}"}


# ============ QR Code Endpoints ============
def generate_qr_code_image(data: str) -> str:
    """Generate QR code image and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


@router.post("/qr-codes/generate", response={201: QRCodeSchema, 400: MessageSchema}, auth=JWTAuth())
def generate_qr_code(request, payload: QRCodeCreateSchema):
    """Generate a QR code for receiving money"""
    try:
        # Generate unique QR code string
        qr_code_str = f"{request.auth.email}:{uuid.uuid4()}"

        # Calculate expiration if provided
        expires_at = None
        if payload.expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=payload.expires_in_hours)

        # Create QR code record
        qr_code_record = QRCodeModel.objects.create(
            user=request.auth,
            qr_code=qr_code_str,
            amount=payload.amount,
            description=payload.description,
            expires_at=expires_at
        )

        # Generate QR code image
        qr_code_image = generate_qr_code_image(qr_code_str)

        # Return response
        return 201, {
            "id": qr_code_record.id,
            "qr_code": qr_code_record.qr_code,
            "qr_code_image": qr_code_image,
            "amount": qr_code_record.amount,
            "description": qr_code_record.description,
            "is_active": qr_code_record.is_active,
            "expires_at": qr_code_record.expires_at,
            "created_at": qr_code_record.created_at
        }
    except Exception as e:
        return 400, {"message": f"Error generating QR code: {str(e)}"}


@router.get("/qr-codes", response=List[QRCodeSchema], auth=JWTAuth())
def list_qr_codes(request):
    """Get all user's QR codes"""
    qr_codes = QRCodeModel.objects.filter(user=request.auth)

    result = []
    for qr_code_record in qr_codes:
        qr_code_image = generate_qr_code_image(qr_code_record.qr_code)
        result.append({
            "id": qr_code_record.id,
            "qr_code": qr_code_record.qr_code,
            "qr_code_image": qr_code_image,
            "amount": qr_code_record.amount,
            "description": qr_code_record.description,
            "is_active": qr_code_record.is_active,
            "expires_at": qr_code_record.expires_at,
            "created_at": qr_code_record.created_at
        })

    return result


@router.post("/qr-codes/scan", response={200: TransactionSchema, 400: MessageSchema, 404: MessageSchema}, auth=JWTAuth())
def scan_qr_code(request, payload: QRCodeScanSchema):
    """Scan a QR code and send money"""
    try:
        # Find QR code
        qr_code_record = QRCodeModel.objects.filter(qr_code=payload.qr_code, is_active=True).first()

        if not qr_code_record:
            return 404, {"message": "QR code not found or inactive"}

        if qr_code_record.is_expired():
            return 400, {"message": "QR code has expired"}

        # Determine amount to send
        amount = payload.amount if payload.amount else qr_code_record.amount

        if not amount:
            return 400, {"message": "Amount is required"}

        # Cannot send money to yourself
        if qr_code_record.user.id == request.auth.id:
            return 400, {"message": "Cannot send money to yourself"}

        with transaction.atomic():
            # Check sender balance
            sender_wallet = request.auth.wallet
            if sender_wallet.balance < amount:
                return 400, {"message": "Insufficient balance"}

            # Create sender transaction (debit)
            sender_txn = Transaction.objects.create(
                user=request.auth,
                transaction_type='transfer_out',
                amount=amount,
                description=qr_code_record.description or f"Payment via QR code",
                recipient_email=qr_code_record.user.email,
                status='completed'
            )

            # Create recipient transaction (credit)
            Transaction.objects.create(
                user=qr_code_record.user,
                transaction_type='transfer_in',
                amount=amount,
                description=f"Received from {request.auth.email} via QR code",
                sender_email=request.auth.email,
                status='completed'
            )

            # Update balances
            sender_wallet.balance -= amount
            sender_wallet.save()

            recipient_wallet = qr_code_record.user.wallet
            recipient_wallet.balance += amount
            recipient_wallet.save()

            # Convert UUID to string for response
            sender_txn.transaction_id = str(sender_txn.transaction_id)
            return 200, sender_txn
    except Exception as e:
        return 400, {"message": f"Error scanning QR code: {str(e)}"}


# ============ Statistics and Analytics ============
@router.get("/stats", response=StatsSchema, auth=JWTAuth())
def get_statistics(request, months: int = 6):
    """Get income/expense statistics"""
    from django.db.models.functions import TruncMonth
    from collections import defaultdict

    user = request.auth

    # Get total income and expense
    total_income = Transaction.objects.filter(
        user=user,
        transaction_type__in=['income', 'transfer_in']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_expense = Transaction.objects.filter(
        user=user,
        transaction_type__in=['expense', 'transfer_out']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    net_balance = total_income - total_expense

    # Get monthly stats
    start_date = datetime.now() - timedelta(days=30 * months)
    monthly_transactions = Transaction.objects.filter(
        user=user,
        created_at__gte=start_date
    ).annotate(month=TruncMonth('created_at'))

    monthly_data = defaultdict(lambda: {'income': Decimal('0'), 'expense': Decimal('0')})

    for txn in monthly_transactions:
        month_key = txn.month.strftime('%Y-%m')
        if txn.transaction_type in ['income', 'transfer_in']:
            monthly_data[month_key]['income'] += txn.amount
        else:
            monthly_data[month_key]['expense'] += txn.amount

    monthly_stats = [
        {
            "month": month,
            "income": data['income'],
            "expense": data['expense'],
            "net": data['income'] - data['expense']
        }
        for month, data in sorted(monthly_data.items())
    ]

    # Get top spending categories
    top_categories = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        category__isnull=False
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "monthly_stats": monthly_stats,
        "top_categories": list(top_categories)
    }


@router.get("/dashboard", response=DashboardSchema, auth=JWTAuth())
def get_dashboard(request):
    """Get dashboard data with wallet, recent transactions, and stats"""
    wallet, created = Wallet.objects.get_or_create(user=request.auth)

    recent_transactions = Transaction.objects.filter(user=request.auth)[:10]

    # Convert UUID to string for each transaction
    for txn in recent_transactions:
        txn.transaction_id = str(txn.transaction_id)

    stats = get_statistics(request, months=6)

    return {
        "wallet": wallet,
        "recent_transactions": list(recent_transactions),
        "stats": stats
    }
