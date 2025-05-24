import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    email_notification = db.Column(db.Boolean, nullable=False)
    phone = db.Column(db.String(128), unique=True, nullable=False)
    sms_notification = db.Column(db.Boolean, nullable=False)
    application_notification = db.Column(db.Boolean, nullable=False)


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = db.Column(db.String(50), nullable=False)
    transaction_amount = db.Column(db.Numeric(19, 4), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    entry_date = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
