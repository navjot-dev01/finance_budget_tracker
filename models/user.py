class User:
    def __init__(self, user_id, full_name, username, password_hash, created_at=None):
        self.user_id = user_id
        self.full_name = full_name
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "username": self.username,
            "created_at": self.created_at
        }
