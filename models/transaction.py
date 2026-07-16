class Transaction:
    def __init__(self, transaction_id, user_id, category_id, amount, type, note, date, category_name=None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.type = type  # 'income' or 'expense'
        self.note = note
        self.date = date
        self.category_name = category_name  # helper field for displays

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category_name or "Unknown",
            "amount": self.amount,
            "type": self.type,
            "note": self.note or "",
            "date": self.date
        }
