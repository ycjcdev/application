from flask_script import Command
from todo_list import db


class InitDB(Command):

    def run(self):
        db.create_all()
