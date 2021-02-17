from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@flask-db/users"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

handler = Manager(app)
handler.add_command("db", MigrateCommand)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128))
    identity_number = db.Column(db.Integer())


if __name__ == "__main__":
    handler.run()
