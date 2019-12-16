from flask_script import Manager
from todo_list import app

from todo_list.scripts.db import InitDB

if __name__ == "__main__":
    manager = Manager(app)

    # init_dbという名前でInitDBを実行可能にする
    manager.add_command('init_db', InitDB())
    manager.run()
