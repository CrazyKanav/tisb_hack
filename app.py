from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hack.db"

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'Student {self.firstname}'

@app.route('/')
def hello():
    return render_template("index.html")