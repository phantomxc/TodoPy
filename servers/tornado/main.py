import os

import tornado.ioloop
import tornado.web

import sqlite3
import json

class MainHandler(tornado.web.RequestHandler):
    """
    Handle serving the html page
    """
    def get(self):
        self.render("../../html/index.html")


class TodoHandler(tornado.web.RequestHandler):
    """
    Handle any of the Todo urls
    """

    def initialize(self):
        """
        This is not where this should go but for convenience I did it...
        """
        self.db = sqlite3.connect('../../todos.db')


    def queryDB(self, query, args=(), one=False):
        """
        lets you work with a simple object.
        """
        cur = self.db.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
            for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def todoByID(self, tid):
        """
        Return a single todo by it's ID
        """
        return self.queryDB('SELECT * FROM todos WHERE id = ?', (tid,), one=True)


    def decode(self, data):
        return json.loads(data)


    def clean(self, todo):
        """
        Convert 0 and 1 stored in the db to Bools
        """
        if todo['completed']:
            todo['completed'] = True
        else:
            todo['completed'] = False
        return todo
        

    def returnJSON(self, data):
        """
        Return JSON from an object.
        """
        return json.dumps(data)
        

    def get(self, tid):
        """
        Return a specific todo if one is provided otherwise all of them
        """
        if tid:
            t = self.todoByID(tid)
            self.write(self.returnJSON(self.clean(t)))
        else:
            todos = [self.clean(todo) for todo in self.queryDB('SELECT * FROM todos')]
            self.write(self.returnJSON(todos))
            

    def post(self, *args):
        """
        Create a new todo
        """
        data = self.decode(self.request.body)
        cur = self.db.execute('INSERT INTO todos (title, completed) VALUES (?, ?)', (data['title'], False))
        tid = cur.lastrowid
        self.db.commit()

        t = self.todoByID(tid)
        self.write(self.returnJSON(self.clean(t)))

    def put(self, tid):
        """
        Update a specific todo
        """
        data = self.decode(self.request.body)
        cur = self.db.execute('UPDATE todos SET completed = ?, title = ? WHERE id = ?',
            (data['completed'], data['title'], data['id']))
        self.db.commit()

        t = self.todoByID(data['id'])
        self.write(self.returnJSON(self.clean(t)))

    def delete(self, tid):
        """
        Delete a specific todo
        """
        cur = self.db.execute('DELETE FROM todos WHERE id = ?', (tid))
        self.db.commit()

        self.write(self.returnJSON('{"":""}'))


# Set the path to the static files
settings = {
    "static_path":os.path.join(os.path.dirname(__file__), "../../static/")
}

# create our application
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/todos/(.*)", TodoHandler)
], **settings)

if __name__ == "__main__":
    # Launch the application
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
