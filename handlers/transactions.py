from models.transaction import Transaction
from utils import json_response, read_json_body, jwt_required

@jwt_required
def handle_add_transaction(handler):
    """POST /transactions/ - Create a new transaction"""
    sender_id = handler.user_id 

    data = read_json_body(handler)
    txn_id, error = Transaction.create(
        sender_id=sender_id,
        receiver_id=data.get('receiverId'),
        amount=data.get('amount'),
        transaction_type=data.get('type', 'transfer')
    )
    
    if txn_id:
        return json_response(handler, 201, {"id": txn_id, "message": "Transaction successful"})
    return json_response(handler, 400, {"message": error or "Transaction failed"})

def format_transaction_response(txn, user_name):
    """Replace 'Me' with the user's actual name in transaction record"""
    if not txn:
        return txn
    
    formatted = txn.copy()
    if formatted.get('sender') == 'Me':
        formatted['sender'] = user_name
    if formatted.get('receiver') == 'Me':
        formatted['receiver'] = user_name
    return formatted

@jwt_required
def handle_get_transactions(handler):
    """GET /transactions/ - Get all transactions"""
    transactions = Transaction.get_all()
    formatted_txns = [format_transaction_response(txn, handler.user_name) for txn in transactions]
    return json_response(handler, 200, formatted_txns)

@jwt_required
def handle_get_transaction_by_id(handler, txn_id):
    """GET /transactions/<id> - Get a specific transaction by ID"""
    transaction = Transaction.get_by_id(txn_id)
    
    if transaction:
        formatted_txn = format_transaction_response(transaction, handler.user_name)
        return json_response(handler, 200, formatted_txn)
    return json_response(handler, 404, {"message": "Transaction not found"})

@jwt_required
def handle_get_transaction_by_id_indexed(handler, txn_id):
    """GET /indexed_transactions/<id> - Get a specific transaction by ID using dictionary"""
    transaction = Transaction.get_by_id_indexed(txn_id)
    
    if transaction:
        formatted_txn = format_transaction_response(transaction, handler.user_name)
        return json_response(handler, 200, formatted_txn)
    return json_response(handler, 404, {"message": "Transaction not found"})

@jwt_required
def handle_get_my_transactions(handler):
    """GET /transactions/me - Get current user's transactions"""
    user_id = handler.user_id
    transactions = Transaction.get_by_user(user_id)
    formatted_txns = [format_transaction_response(txn, handler.user_name) for txn in transactions]

    return json_response(handler, 200, formatted_txns)

@jwt_required
def handle_update_transaction(handler, txn_id):
    """PUT /transactions/<id> - Update a transaction"""
    user_id = handler.user_id
    role = getattr(handler, 'user_role', 'USER')
    data = read_json_body(handler)
    
    updated_txn, error = Transaction.update(
        txn_id=txn_id,
        user_id=user_id,
        role=role,
        type=data.get('type')
    )
    
    if updated_txn:
        return json_response(handler, 200, {"message": "Transaction updated", "transaction": updated_txn})
    return json_response(handler, 400, {"message": error or "Update failed"})

@jwt_required
def handle_delete_transaction(handler, txn_id):
    """DELETE /transactions/<id> - Delete a transaction"""
    user_id = handler.user_id
    role = getattr(handler, 'user_role', 'USER')
    
    success, result = Transaction.delete(txn_id, user_id, role)
    
    if success:
        return json_response(handler, 200, {"message": "Transaction deleted", "transaction": result})
    return json_response(handler, 400, {"message": result})
