import json
from flask import request
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from initialise import Initialise
from flask import Flask
from flask import render_template

app = Flask(__name__)
init = Initialise()
app = init.db(app)

db = SQLAlchemy(app)


def hateoas(id):
    return [
        {
            "rel": "self",
            "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
            "method": "GET"
        },
        {
            "rel": "update",
            "resource": "http://127.0.0.1:8000/v1/users" + str(id),
            "method": "PATCH"
        },
        {
            "rel": "update",
            "resource": "http://127.0.0.1:8000/v1/users" + str(id),
            "method": "DELETE"
        }
    ]


@app.route('/')
def welcome():
    # Flask way of sending ./templates/index.html.
    return render_template("index.html")
