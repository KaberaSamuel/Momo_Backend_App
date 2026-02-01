import database
import datetime

TRANSACTION_TYPES = ['transfer', 'payment', 'withdrawal', 'deposit']

class Transaction:
    @staticmethod
    def create(sender_id, receiver_id, amount, transaction_type='transfer'):
        sender = database.users.get(sender_id)
        receiver = database.users.get(receiver_id)
        
        if not sender or not receiver:
            return None, "Invalid sender or receiver"
        
        if sender['balance'] < amount:
            return None, "Insufficient balance"
        
        # Update balances
        sender['balance'] -= amount
        receiver['balance'] += amount
        
        # Log transaction
        txn_id = database.transaction_id_counter
        database.transaction_id_counter += 1
        
        transaction = {
            'id': txn_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'type': transaction_type,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        database.transactions.append(transaction)
        database.transactions_dictionary[txn_id] = transaction
        
        return txn_id, None

    @staticmethod
    def get_all():
        return database.transactions.copy()

    @staticmethod
    def get_by_id(txn_id):
        for txn in database.transactions:
            if txn['id'] == txn_id:
                return txn
        return None

    @staticmethod
    def get_by_id_indexed(txn_id):
        """Get transaction by ID using the dictionary index"""
        return database.transactions_dictionary.get(txn_id)

    @staticmethod
    def get_by_user(user_id):
        """Get all transactions where user is sender or receiver"""
        return [txn for txn in database.transactions if txn['sender_id'] == user_id or txn['receiver_id'] == user_id]

    @staticmethod
    def update(txn_id, user_id, role, **kwargs):
        """Update a transaction. Only Admins can update a transaction."""
        if role != 'ADMIN':
            return None, "Only Admins can update transactions"

        for i, txn in enumerate(database.transactions):
            if txn['id'] == txn_id:
                # Only allow updating certain fields
                allowed_fields = ['type']
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        if key == 'type' and value not in TRANSACTION_TYPES:
                            return None, f"Invalid transaction type. Must be one of: {', '.join(TRANSACTION_TYPES)}"
                        database.transactions[i][key] = value
                
                # Update dictionary as well
                database.transactions_dictionary[txn_id] = database.transactions[i]
                
                return database.transactions[i], None
        return None, "Transaction not found"

    @staticmethod
    def delete(txn_id, user_id, role):
        """Delete a transaction. Only Admins can delete a transaction."""
        if role != "ADMIN":
            return False, "Only Admins can delete transactions"

        for i, txn in enumerate(database.transactions):
            if txn['id'] == txn_id:
                deleted_txn = database.transactions.pop(i)
                # Remove from dictionary as well
                if txn_id in database.transactions_dictionary:
                    del database.transactions_dictionary[txn_id]
                return True, deleted_txn
        return False, "Transaction not found"
