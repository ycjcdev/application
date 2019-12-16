from todo_list import db
from datetime import datetime

class TodoList(db.Model):

    # テーブル名
    __tablename__ = 'todolists'

    # カラム定義
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique=True)
    created_at = db.Column(db.DateTime)

    # イニシャライザ
    def __init__(self, name=None):
        self.name = name
        self.created_at = datetime.utcnow()
