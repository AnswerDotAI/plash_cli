import os
from dataclasses import dataclass

from fasthtml.common import *
from fastlite import database

app, rt = fast_app()

@dataclass  
class Todo:
    id: int
    title: str
    completed: bool = False

db = database("data/prod.db" if os.getenv("PLASH_PRODUCTION") else "data/dev.db")
todos = db.create(Todo, transform=True)

def render_todo(todo):
    return Li(
        Input(type="checkbox", checked=todo.completed, 
              hx_post=f"/toggle/{todo.id}", hx_target=f"#todo-{todo.id}", hx_swap="outerHTML"),
        Span(todo.title, style="text-decoration: line-through" if todo.completed else ""),
        id=f"todo-{todo.id}"
    )

@rt
def index():
    return Titled("Todo List",
        Form(
            Input(name="title", placeholder="Add a new todo", required=True),
            Button("Add", type="submit"),
            hx_post="/add", hx_target="#todos", hx_swap="beforeend",
            hx_on__after_request="this.reset()"
        ),
        Ul(*[render_todo(todo) for todo in todos()], id="todos")
    )

@rt
def add(title: str):
    new_todo = todos.insert(Todo(title=title))
    return render_todo(new_todo)

@rt("/toggle/{idx}")  
def toggle(idx: int):
    todo = todos[idx]
    todo.completed = not todo.completed
    todos.update(todo)
    return render_todo(todo)

serve()