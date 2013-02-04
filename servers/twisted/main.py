from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.web.server import NOT_DONE_YET
from twisted.web.static import File
import json



class DataModel:

    def __init__(self, connection_pool):
        self.connection_pool = connection_pool


    def getAll(self):
        """
        Get a list of all the todos.
        """
        def interaction(c):
            c.execute('select id, title, completed from todos order by id')
            return c.fetchall()
        d = self.connection_pool.runInteraction(interaction)
        return d.addCallback(self._toList)


    def create(self, title):
        """
        Create a new todo.
        
        @param title: Title of todo.
        
        @return: The created todo.
        """
        def interaction(c):
            c.execute('insert into todos (title, completed) values (?, ?)',
                      (title, False))
            todo_id = c.lastrowid
            c.execute('select id, title, completed from todos where id = ?', (todo_id,))
            return c.fetchone()
        d = self.connection_pool.runInteraction(interaction)
        return d.addCallback(self._toDict)


    def get(self, todo_id):
        """
        Get a single todo
        """
        def interaction(c):
            c.execute('select id, title, completed from todos where id = ?',
                      (todo_id,))
            return c.fetchone()
        d = self.connection_pool.runInteraction(interaction)
        return d.addCallback(self._toDict)


    def update(self, todo_id, data):
        parts = []
        args = []
        if 'title' in data:
            parts.append('title = ?')
            args.append(data['title'])
        if 'completed' in data:
            parts.append('completed = ?')
            args.append(data['completed'])
        
        args.append(todo_id)
        
        def interaction(c):
            c.execute('update todos set %s where id = ?' % (', '.join(parts),), tuple(args))
            c.execute('select id, title, completed from todos where id = ?', (todo_id,))
            return c.fetchone()
        d = self.connection_pool.runInteraction(interaction)
        return d.addCallback(self._toDict)


    def delete(self, todo_id):
        def interaction(c):
            c.execute('delete from todos where id = ?', (todo_id,))
        return self.connection_pool.runInteraction(interaction)


    def _toList(self, rows):
        return [self._toDict(x) for x in rows]


    def _toDict(self, row):
        return {
            'id': row[0],
            'title': row[1],
            'completed': bool(row[2]),
        }



class JsonDeferredResource(Resource):


    def render(self, request):
        result = Resource.render(self, request)
        result.addCallback(self.finishRequest, request)
        return NOT_DONE_YET


    def finishRequest(self, data, request):
        request.setHeader('Content-type', 'application/json')
        request.write(json.dumps(data).encode('utf-8'))
        request.finish()



class Todos(JsonDeferredResource):


    def __init__(self, db):
        Resource.__init__(self)
        # because people expect /todos and /todos/ to be the same thing
        self.putChild('', self)
        self.db = db


    def getChild(self, path, request):
        return Todo(self.db, int(path))


    def render_GET(self, request):
        return self.db.getAll()


    def render_POST(self, request):
        data = json.loads(request.content.read())
        return self.db.create(data['title'])



class Todo(JsonDeferredResource):


    def __init__(self, db, todo_id):
        Resource.__init__(self)
        # because people expect /todos/1 and /todos/1/ to be the same thing
        self.putChild('', self)
        self.db = db
        self.todo_id = todo_id


    def render_GET(self, request):
        return self.db.get(self.todo_id)


    def render_PUT(self, request):
        data = json.loads(request.content.read())
        return self.db.update(self.todo_id, data)


    def render_DELETE(self, request):
        return self.db.delete(self.todo_id)



def run(port, sqlite_conn, index_html, static_root):
    #--------------------------------------------------------------------------
    # log to stdout
    #--------------------------------------------------------------------------
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    
    #--------------------------------------------------------------------------
    # database
    #--------------------------------------------------------------------------
    from twisted.enterprise import adbapi
    pool = adbapi.ConnectionPool('sqlite3', sqlite_conn, check_same_thread=False,
                                 cp_min=1, cp_max=1)
    data_model = DataModel(pool)
    
    #--------------------------------------------------------------------------
    # url/resource mapping
    #--------------------------------------------------------------------------
    root = Resource()
    root.putChild('', File(index_html))
    root.putChild('static', File(static_root))
    root.putChild('todos', Todos(data_model))
    
    #--------------------------------------------------------------------------
    # serve it
    #--------------------------------------------------------------------------
    from twisted.internet import reactor
    from twisted.web.server import Site
    site = Site(root)
    site.displayTracebacks = False
    reactor.listenTCP(port, site)
    reactor.run()  
    


if __name__ == '__main__':
    run(8080, '../../todos.db', '../../html/index.html', '../../static')
