from twisted.web.static import File
from klein import Klein

import sqlite3
import json


def return_json(data, request):
    """
    Helper to return json
    """
    request.setHeader('Content-Type', 'application/json')
    return json.dumps(data)

        
class Todos(object):

    app = Klein()

    def __init__(self):
        self.db = sqlite3.connect('../../todos.db')


    def queryDB(self, query, args=(), one=False):
        """
        lets you work with a simple object.
        """
        cur = self.db.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
            for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv


    def clean(self, todo):
        """
        Update the todos completed field to a JSON compatible boolean
        returns the todo
        """
        if todo['completed']:
            todo['completed'] = True
        else:
            todo['completed'] = False
        return todo


    @app.route('/')
    def index(self, request):
        """
        Render index
        """
        return File("../../html/")


    @app.route('/static/', branch=True)
    def static(self, request):
        """
        Handle static files
        """
        return File("../../static/")


    @app.route('/todos/', methods=['GET'])
    def allTodos(self, request):
        """
        Handle listing all todos
        """
        todos = []
        for todo in self.queryDB('SELECT * FROM todos'):
            todo = self.clean(todo)
            todos.append(todo)

        return return_json(todos, request)


    @app.route('/todos/', methods=['POST'])
    def createTodo(self, request):
        """
        Create a new todo
        """
        data = json.loads(request.content.read())
        cur = self.db.execute('INSERT INTO todos (title, completed) VALUES (?, ?)', (data['title'], False))
        tid = cur.lastrowid
        self.db.commit()

        t = self.queryDB('SELECT * FROM todos WHERE id = ?', (tid,), one=True)
        t = self.clean(t)
        return return_json(t, request)


    @app.route('/todos/<int:todo>', methods=['GET'])
    def getTodo(self, request, todo):
        """
        Get a specific todo
        """
        t = self.queryDB('SELECT * FROM todos WHERE id = ?', (todo,), one=True)
        t = self.clean(t)
        return return_json(t, request)

    
    @app.route('/todos/<int:todo>', methods=['PUT'])
    def updateTodo(self, request, todo):
        """
        Update a specific todo
        """
        data = json.loads(request.content.read())
        cur = self.db.execute('UPDATE todos SET completed = ?, title = ? WHERE id = ?', (data['completed'], data['title'], data['id']))
        self.db.commit()

        t = self.queryDB('SELECT * FROM todos WHERE id = ?', (data['id'],), one=True)
        t = self.clean(t)
        return return_json(t, request)


    @app.route('/todos/<int:todo>', methods=['DELETE'])
    def deleteTodo(self, request, todo):
        """
        Handle listing, updating, deleting one todo
        """
        cur = self.db.execute('DELETE FROM todos WHERE id = ?', (todo,))
        self.db.commit()

        return return_json({}, request)

    
if __name__ == '__main__':
    todos = Todos()
    todos.app.run('localhost', 8080)
