from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


# Wallet Schemas
class WalletSchema(BaseModel):
    id: int
    balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Card Schemas
class CardCreateSchema(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19)
    card_type: str
    card_holder_name: str
    expiry_date: Optional[str] = None
    bank_name: str
    is_primary: bool = False


class CardSchema(BaseModel):
    id: int
    card_number: str
    card_type: str
    card_holder_name: str
    expiry_date: Optional[str]
    bank_name: str
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CardUpdateSchema(BaseModel):
    card_holder_name: Optional[str] = None
    expiry_date: Optional[str] = None
    is_primary: Optional[bool] = None


# Transaction Schemas
class TransactionCreateSchema(BaseModel):
    transaction_type: str
    amount: Decimal = Field(..., gt=0)
    description: str
    category: Optional[str] = None
    recipient_email: Optional[str] = None


class TransactionSchema(BaseModel):
    id: int
    transaction_id: str
    transaction_type: str
    amount: Decimal
    description: str
    category: Optional[str]
    status: str
    recipient_email: Optional[str]
    sender_email: Optional[str]
    created_at: datetime

    @field_serializer('transaction_id')
    def serialize_transaction_id(self, value, _info):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True


# QR Code Schemas
class QRCodeCreateSchema(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    expires_in_hours: Optional[int] = None


class QRCodeSchema(BaseModel):
    id: int
    qr_code: str
    qr_code_image: str
    amount: Optional[Decimal]
    description: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class QRCodeScanSchema(BaseModel):
    qr_code: str
    amount: Optional[Decimal] = None


# Send Money Schema
class SendMoneySchema(BaseModel):
    recipient_email: str
    amount: Decimal = Field(..., gt=0)
    description: str
    category: Optional[str] = None


# Statistics Schemas
class MonthlyStatsSchema(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class StatsSchema(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    monthly_stats: List[MonthlyStatsSchema]
    top_categories: List[dict]


class DashboardSchema(BaseModel):
    wallet: WalletSchema
    recent_transactions: List[TransactionSchema]
    stats: StatsSchema


# Message Schema
class MessageSchema(BaseModel):
    message: str
