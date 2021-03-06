import json
from http import HTTPStatus

from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from database.initialise import Initialise
from database.migration import Users
from validation.validation import IDSchema
from validation.validation import UserSchema

flask_app = Flask(__name__)
init = Initialise()
flask_app = init.db(flask_app)
db = SQLAlchemy(flask_app)

user_schema = UserSchema()
id_schema = IDSchema()


def hateoas(id):
    return [
        {
            "rel": "self",
            "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
            "method": "GET"
        },
        {
            "rel": "update",
            "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
            "method": "PATCH"
        },
        {
            "rel": "update",
            "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
            "method": "DELETE"
        }
    ]


@flask_app.route('/')
def welcome():
    # Flask way of sending ./templates/index.html.
    return render_template("index.html")


@flask_app.route('/v1/users', methods=['POST'])
def post_user_details():
    try:
        user_data = request.get_json()
        errors = user_schema.validate(user_data)
        if errors:
            return json.dumps(str(errors)), HTTPStatus.BAD_REQUEST
        insert_user(user_data)
        return response('Added')
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


# This decouples the HTTP request from the functionality
def insert_user(user_data):
    sql = text('INSERT INTO users (name, surname, identity_number) VALUES (:name, :surname, :identity_number)')
    return execute(sql, user_data)


@flask_app.route('/v1/users/<user_id>', methods=["GET"])
def get_user_details(user_id):
    try:
        result = get_user(user_id)
        return response({"name": result.name, "surname": result.surname, "identity_number": result.identity_number,
                         "links": hateoas(user_id)})
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


def get_user(user_id):
    user_data = {}
    user_data['id_num'] = user_id
    sql = text('SELECT * FROM users WHERE id=:id_num')
    return execute(sql, user_data).fetchone()


@flask_app.route('/v1/users/<user_id>', methods=['PATCH'])
def patch_user_details(user_id):
    user_data = request.get_json()
    try:
        user_data['id'] = user_id
        update_user(user_data)
        return response({
            "id": user_id,
            "links": hateoas(user_id)
        })
    except Exception as e:
        return json.dumps("Failed. " + str(e)), HTTPStatus.NOT_FOUND


# This decouples the HTTP request from the functionality
def update_user(user_data):
    update_string = ""
    for key in user_data:
        update_string += key + "=:" + key + ','
    update_string = update_string[:-1]
    sql = text('UPDATE users SET ' + update_string + ' WHERE id = :id')
    return execute(sql, user_data)


@flask_app.route('/v1/users/<user_id>', methods=['DELETE'])
def delete_user_details(user_id):
    try:
        result = delete_user(user_id)
        response('Deleted')
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


def delete_user(user_id):
    user_data = {"id_num": user_id}
    sql = text('DELETE FROM users WHERE id=:id_num')
    return execute(sql, user_data)


# Decouples the database from the app logic (can switch from MySQL to Mongo)
def execute(sql, data):
    return db.engine.execute(sql, data)


# Decouples return type from app logic (e.g. can switch from JSON to XML)
def response(message):
    return json.dumps(message), HTTPStatus.OK


# V2 -------------------------------------------------------------------------------------------------------------------

@flask_app.route('/v2/users/<user_id>', methods=['GET'])
def get_user_details_orm(user_id):
    try:
        result = db.session.query(Users).filter_by(id=user_id).first()
        return json.dumps(
            {
                "name": result.name,
                "surname": result.surname,
                "identity_number": result.identity_number,
                "links": hateoas(user_id)
            }
        ), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed to retrieve record. ' + str(e)), HTTPStatus.NOT_FOUND


@flask_app.route('/v2/users', methods=['POST'])
def post_user_details_orm():
    try:
        data = request.get_json()
        user = Users(name=data['name'], surname=data['surname'], identity_number=data['identity_number'])
        db.session.add(user)
        db.session.commit()
        return json.dumps({"id": user.id, "links": hateoas(user.id)}), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


@flask_app.route('/v2/users/<user_id>', methods=['PATCH'])
def patch_user_details_orm(user_id):
    try:
        data = request.get_json()
        user = db.session.query(Users).filter_by(id=user_id).update(data)
        db.session.commit()
        return json.dumps(
            {
                "id": user_id,
                "links": hateoas(user_id)
            }
        )
    except Exception as e:
        return json.dumps("Failed. " + str(e)), HTTPStatus.NOT_FOUND


@flask_app.route('/v2/users/<user_id>', methods=['DELETE'])
def delete_user_details_orm(user_id):
    try:
        user = db.session.query(Users).filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return json.dumps('Deleted'), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND
