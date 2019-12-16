from flask import request, redirect, url_for, render_template, flash, session
from todo_list import app
from todo_list import db
from todo_list.models.todolists import TodoList
from todo_list.models.todos import Todo
import datetime
from sqlalchemy import exc
from functools import wraps


def login_required(view):
    @wraps(view)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return inner

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('ユーザ名が異なります')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('パスワードが異なります')
        else:
            session['logged_in'] = True
            flash('ログインしました')
            return redirect(url_for('show_todolists'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('ログアウトしました')
    return redirect(url_for('show_todolists'))


@app.errorhandler(404)
def non_existant_route(error):
   return redirect(url_for('login'))


@app.route('/')
@login_required
def show_todolists():

    todolists = TodoList.query.order_by(TodoList.id.desc()).all()

    todolistdatas = []
    for todolist in todolists:
        num = Todo.query.filter(Todo.list_id == todolist.id).count()
        checked_num = Todo.query.filter(Todo.list_id == todolist.id,Todo.is_checked == True).count()

        todos = Todo.query.filter(Todo.list_id == todolist.id,Todo.is_checked == False)

        deadline = datetime.datetime(9999,1,1,1,1)
        for todo in todos:
            if deadline > todo.deadline:
                deadline = todo.deadline
        if deadline == datetime.datetime(9999,1,1,1,1):
            deadline = '-'
        else:
            deadline = '~' + deadline.strftime("%Y/%m/%d")

        todolistdata = {
            "id" : todolist.id,
            "name": todolist.name,
            "num": num,
            "checked_num": checked_num,
            "dead_line" : deadline
        }
        todolistdatas.append(todolistdata)

    return render_template('/index.html', todolistdatas=todolistdatas)


@app.route('/addlist', methods=['POST'])
def add_list():
    todolist = TodoList(
        name=request.form['listname']
    )
    # DBにデータ書き込み
    db.session.add(todolist)
    try:
        db.session.commit()
        flash('新しくToDoリストが作成されました')
    except exc.SQLAlchemyError:
        flash('ToDoリスト名が既に存在しています')
    return redirect(url_for('show_todolists'))


@app.route('/detail/<int:id>', methods=['GET'])
@login_required
def show_detail(id):
    todos = Todo.query.filter(Todo.list_id == id)
    list_name = TodoList.query.filter(TodoList.id == id).first().name
    return render_template('detail.html', todos=todos, list_id=id,list_name=list_name)


@app.route('/addtodo', methods=['POST'])
@login_required
def add_todo():
    todo = Todo(
        name=request.form['todoname'],
        deadline=datetime.datetime.strptime(request.form['deadline'], '%Y-%m-%d'),
        list_id=request.form['listid']
    )

    # DBにデータ書き込み
    db.session.add(todo)
    try:
        db.session.commit()
        flash('新しくToDoが作成されました')
    except exc.SQLAlchemyError:
        flash('ToDo名が既に存在しています')

    todos = Todo.query.filter(Todo.list_id == request.form['listid'])
    list_name = TodoList.query.filter(TodoList.id == request.form['listid']).first().name

    return render_template('detail.html', todos=todos, list_id=request.form['listid'], list_name=list_name)


@app.route('/check', methods=['POST'])
@login_required
def check():

    todo = Todo.query.get(request.form['todoid'])
    todo.is_checked = not todo.is_checked

    db.session.merge(todo)
    db.session.commit()
    todos = Todo.query.filter(Todo.list_id == request.form['listid'])
    list_name = TodoList.query.filter(TodoList.id == request.form['listid']).first().name
    return render_template('detail.html', todos=todos, list_id=request.form['listid'],list_name=list_name)

@app.route('/search')
@login_required
def show_search():
    return render_template('/search.html')


@app.route('/dosearch', methods=['POST'])
@login_required
def do_search():
    todos = Todo.query.filter(Todo.name.like('%' + request.form['searchname'] + '%')).order_by(Todo.created_at.desc())
    todo_search_data = []
    for todo in todos:
        todolist = TodoList.query.filter(TodoList.id == todo.list_id).first()
        list_name = todolist.name
        result = {
            "todo":todo,
            "list_name":list_name
        }
        todo_search_data.append(result)

    todo_search_count = Todo.query.filter(Todo.name.like('%' + request.form['searchname'] + '%')).count()

    todo_search = {
        "data": todo_search_data,
        "count":todo_search_count
    }

    todolist_searchresults = TodoList.query.filter(TodoList.name.like('%' + request.form['searchname'] + '%')).order_by(TodoList.created_at.desc())
    todolist_searchresults_count = TodoList.query.filter(TodoList.name.like('%' + request.form['searchname'] + '%')).count()

    todolist_search = {
        "results":todolist_searchresults,
        "count":todolist_searchresults_count
    }

    return render_template('/search_result.html',todo_search=todo_search,todolist_search=todolist_search)