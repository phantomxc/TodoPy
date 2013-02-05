TodoPy
======

# Python Todo Servers
If you've ever used a "RESTful" API and thought it would be awesome to create your own, you're in the right place. This project's goal is to show you how easy it can be to accomplish just that in [Python](http://www.python.org/) with the most popular libraries.

Inspired by the popular [TodoMVC](http://addyosmani.github.com/todomvc/), I would like to thank [Addy Osmani](https://github.com/addyosmani) for allowing me to use his interface utilizing the [Backbone.js](http://documentcloud.github.com/backbone) library. (My favorite...)

### Server Examples included:

- [web.py](http://webpy.org/) : (pip install web.py | easy&#95;install web.py)
- [Twisted Web](http://twistedmatrix.com/) : (pip install Twisted)
- [Flask](http://flask.pocoo.org/) : (pip install Flask)

## Data Storage

All of the servers in this project require [sqlite3](http://docs.python.org/2/library/sqlite3.html) library to be installed. 

## Starting the servers 

All of the servers can be located in their respective directories inside `./servers/`. Start the server by running the following command.

```
$ python main.py
http://0.0.0.0:8080/
```

browse to `http://localhost:8080` view the server in action. 

# Server API SPEC

* `create → POST`
* `read → GET`
* `update → PUT`
* `delete → DELETE`

GET ALL TODOS
------------

* `GET /todos/` will return all available todos.
    
```json    
[ 
    {
        "id":547201,
        "title":"Take out the trash",
        "completed":true
    },
    {
        "id":547202,
        "title":"Play HoN",
        "completed":false,
    }
]
```

GET SINGLE TODO
------------

* `GET /todos/547201` will return the todo with the specified ID.
    
```json    
{
    "id":547201,
    "title":"Take out the trash",
    "completed":true
}
```


CREATE TODO
--------------

* `POST /todos/` will create a new todo from the parameters passed.

```json    
{
    "title":"Write HoN Bot",
}
```
    
This must return 201 Created, with the current JSON representation of the todo if the creation was a success.


UPDATE TODO
--------------

* `PUT /todos/547202` will update the todo from the parameters passed.

```json    
{
    "completed":true
}
```

This must return 200 OK if the update was a success along with the current JSON representation of the todo.


DELETE TODO
--------------
    
* `DELETE /todos/547202` will delete the todo specified and return 204 No Content if that was successful
