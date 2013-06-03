from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from models import Todos
import json

def pretty_todo(todo):
    """
    Make the todo completed value a bool since that is what backbone is expecting
    """
    if todo.completed:
        todo.completed = True
    else:
        todo.completed = False

    return todo.completed


def ugly_completed(arg):
    """
    Turn true and false back to 1 or 0
    """
    if arg:
        return 1
    return 0


def main(request):
    """
    Return the main page
    """
    return render_to_response('index.html')


def jsonifyTodo(todo):
    ret = {}
    ret['id'] = todo.id
    ret['title'] = todo.title
    ret['completed'] = pretty_todo(todo)

    return json.dumps(ret)


@csrf_exempt
def todos(request, todo_id=None):
    """
    GET: return all the Todos
    POST: create a new todo
    """
    if request.method == 'GET':
        if todo_id:
            # find the specific todo and return it
            todo = Todos.objects.get(id=todo_id)
            return HttpResponse(status=200, content=jsonifyTodo(todo), mimetype='application/json')
        
        else:
            todos = Todos.objects.all()
            ret_data = []
            for todo in todos:
                pretty_todo(todo)
                ret_data.append({
                    'id': todo.id,
                    'title': todo.title,
                    'completed': todo.completed
                })

            return HttpResponse(json.dumps(ret_data), mimetype='application/json')
    
    elif request.method == 'POST':
        # create a new todo
        data = json.loads(request.body)
        new_todo = Todos()
        new_todo.title = data['title']
        new_todo.completed = ugly_completed(data['completed'])
        new_todo.save()

        return HttpResponse(status=201, content=jsonifyTodo(new_todo))


    elif request.method == 'PUT':
        # mark the todo as completed
        data = json.loads(request.body)
        todo = Todos.objects.get(id=todo_id)
        todo.completed = ugly_completed(data['completed'])
        todo.save()

        return HttpResponse(status=200, content=jsonifyTodo(todo))


    elif request.method == 'DELETE':
        # delete the todo
        todo = Todos.objects.get(id=todo_id)
        todo.delete()

        return HttpResponse(status=204)
