class Category:
    def __init__(self, category_id, user_id, name, type):
        self.category_id = category_id
        self.user_id = user_id
        self.name = name
        self.type = type  # 'income' or 'expense'

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type
        }
