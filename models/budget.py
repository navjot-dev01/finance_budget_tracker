class Budget:
    def __init__(self, budget_id, user_id, category_id, month, limit_amount, category_name=None):
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.month = month  # YYYY-MM
        self.limit_amount = limit_amount
        self.category_name = category_name  # helper field for displays

    def to_dict(self):
        return {
            "budget_id": self.budget_id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category_name or "Unknown",
            "month": self.month,
            "limit_amount": self.limit_amount
        }
