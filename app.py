from flask import Flask, request, jsonify

from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import uuid
import json
import hashlib
import os
import redis
from functools import wraps
from datetime import datetime, date
from models import db, User, Transaction
from controllers.notification import Notification

# JWT config
# Replace with .env var in production/Vault/...
JWT_SECRET = os.getenv("JWT_SECRET", "Tyme-Secret-Key-Dev")
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 600
DB_URL = os.getenv('DB_URL')

app = Flask(__name__)
# Config
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_EXP_DELTA_SECONDS
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db.init_app(app)
jwt = JWTManager(app)

# Redis setup
redis_url = os.getenv("REDIS_URL", "localhost")
r = redis.Redis(host=redis_url, port=6379, db=0, decode_responses=True)

IDEMPOTENCY_TTL_SECONDS = 60
LOCK_TTL_SECONDS = 5


# Lock Idempotency Key in Redis
def acquire_lock(lock_key):
    return r.set(lock_key, '1', nx=True, ex=LOCK_TTL_SECONDS)


@app.route('/generate-token', methods=['POST'])
def generate_token():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({"error": "Missing Params"}), 400
    hash_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = User.query.filter_by(username=username).first()
    if not user or user.password != hash_password:
        return jsonify({'error': 'Invalid credentials'}), 401
    identity = f"{username}:{str(uuid.uuid4())}"
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route('/payment', methods=['POST'])
@jwt_required()
def create_payment():
    current_profile_id = get_jwt_identity()
    idempotency_key = request.headers.get('Idempotency-Key')
    if not idempotency_key:
        return jsonify({'error': 'Idempotency-Key header is required'}), 400

    request_key = f"req:{idempotency_key}:{current_profile_id}"
    response_key = f"res:{idempotency_key}:{current_profile_id}"

    # Check response_key existed in Redis
    if r.exists(response_key):
        saved_response = json.loads(r.get(response_key))
        return jsonify(saved_response), 200

    if not acquire_lock(request_key):
        return jsonify({'error': 'Request is already being processed'}), 409

    try:
        # Get user information, it can be use to check some constraint/notification
        username = current_profile_id.split(':')[0]
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'Cannot find user.'}), 400
        request_body = request.get_json()
        r.setex(request_key, IDEMPOTENCY_TTL_SECONDS, json.dumps(request_body))

        # Extract and validate fields
        amount = request_body.get("amount")
        account_number = request_body.get("account_number")
        transaction_type = request_body.get("transaction_type", "payment")

        if not account_number or amount is None:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create new transaction
        new_transaction = Transaction(
            account_number=account_number,
            transaction_amount=amount,
            transaction_type=transaction_type,
            booking_date=date.today(),
            entry_date=datetime.now(),
            user_id=user.id
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Send notification
        for key in ['email', 'application', 'sms']:
            if getattr(user, f"{key}_notification"):
                getattr(Notification, f'send_{key}_notification')(
                    f'Transaction {str(new_transaction.transaction_id)} is success.')

        response_data = {
            "payment_id": str(new_transaction.transaction_id),
            "status": "success",
            "amount": float(amount),
            "account_number": account_number,
        }
        # Save response_key in Redis
        r.setex(response_key, IDEMPOTENCY_TTL_SECONDS,
                json.dumps(response_data))

        return jsonify(response_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        r.delete(request_key)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run('0.0.0.0', 4000, debug=True)
