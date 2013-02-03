from flask import Flask, render_template, send_from_directory, g, request, Response
import jinja2
import sqlite3
import json


app = Flask(__name__)

#------------------
# CONFIG
#------------------

# Set a custom template directory
app.jinja_loader = jinja2.FileSystemLoader('../../html/')

# Set database availabbility to the app
DATABASE = '../../todos.db'

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

#------------------
# HELPERS
#------------------
def query_db(query, args=(), one=False):
    """
    This was taken from the Flask documentation and lets you work with a simple object
    """
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def clean_todo(todo):
    """
    Update the todos completed field to a JSON compatible boolean
    returns the todo
    """
    if todo['completed']:
        todo['completed'] = True
    else:
        todo['completed'] = False
    return todo


def return_json(d):
    ret = json.dumps(d)
    return Response(ret, status=200, mimetype='application/json')


#------------------
# HANDLERS
#------------------
@app.route('/')
def return_index():
    return render_template('index.html')

@app.route('/todos/', methods=['GET', 'POST'])
def get_create_todos():
    if request.method == 'GET':
        todos = []
        for todo in query_db('select * from todos'):
            todo = clean_todo(todo)
            todos.append(todo)

        return return_json(todos)





@app.route('/todos/<todo>', methods=['GET', 'PUT', 'DELETE'])
def get_update_todo(todo):
    return

# Only way I could figure out how to redirect the static files
@app.route('/static/assets/<path:filename>')
def send_assets(filename):
    return send_from_directory('../../static/assets/', filename)

@app.route('/static/js/<path:filename>')
def send_js(filename):
    return send_from_directory('../../static/js/', filename)

if __name__ == '__main__':
    app.run(debug=True)


