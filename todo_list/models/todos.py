from todo_list import db
from datetime import datetime


class Todo(db.Model):
    # テーブル名
    __tablename__ = 'todos'

    # カラム定義
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique=True)
    created_at = db.Column(db.DateTime)
    list_id = db.Column(db.Integer)
    is_checked = db.Column(db.Boolean)
    deadline = db.Column(db.DateTime)

    # イニシャライザ
    def __init__(self, name=None, list_id=None, is_checked=False, deadline=None):
        self.name = name
        self.created_at = datetime.utcnow()
        self.list_id = list_id
        self.is_checked = is_checked
        self.deadline = deadline
