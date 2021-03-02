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


@app.route('/v1/users', methods=['POST'])
def post_user_details():
    try:
        data = request.get_json()
        sql = text('INSERT INTO users (name, surname, identity_number) VALUES (:name, :surname, :id_num)')
        result = db.engine.execute(
            sql,
            name=data['name'],
            surname=data['surname'],
            id_num=data['identity_number']
        )
        return json.dumps({"id": result.lastrowid, "links": hateoas(result.lastrowid)})
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v1/users/<user_id>', methods=["GET"])
def get_user_detais(user_id):
    try:
        sql = text('SELECT * FROM users WHERE id=:id_num')
        result = db.engine.execute(sql, id_num=user_id).fetchone()
        return json.dumps({"name": result.name, "surname": result.surname, "identity_number": result.identity_number,
                           "links": hateoas(user_id)}), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v1/users/<user_id>', methods=['PATCH'])
def patch_user_details(user_id):
    data = request.get_json()
    for key in data:
        update_string = key + "=:" + key + ','
        update_string = update_string[:-1]
    try:
        data['id'] = user_id
        sql = text('UPDATE users SET ' + update_string + ' WHERE id = :id')
        result = db.engine.execute(sql, data)
        return json.dumps(
            {
                "id": user_id,
                "links": hateoas(user_id)
            }
        )
    except Exception as e:
        return json.dumps("Failed. " + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v1/users/<user_id>', methods=['DELETE'])
def delete_user_details(user_id):
    try:
        sql = text('DELETE FROM users WHERE id=:id_num')
        result = db.engine.execute(sql, id_num=user_id)
        return json.dumps('Deleted'), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


# V2 -------------------------------------------------------------------------------------------------------------------

@app.route('/v2/users/<user_id>', methods=['GET'])
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


@app.route('/v2/users', methods=['POST'])
def post_user_details_orm():
    try:
        data = request.get_json()
        user = Users(name=data['name'], surname=data['surname'], identity_number=data['identity_number'])
        db.session.add(user)
        db.session.commit()
        return json.dumps({"id": user.id, "links": hateoas(user.id)}), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v2/users/<user_id>', methods=['PATCH'])
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


@app.route('/v2/users/<user_id>', methods=['DELETE'])
def delete_user_details_orm(user_id):
    try:
        user = db.session.query(Users).filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return json.dumps('Deleted'), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND
