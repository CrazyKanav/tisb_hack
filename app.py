from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_session import Session


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hack.db"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False, )
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'User{self.id} {self.firstname}'

# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/')
def index():
    return render_template("index.html", name=session.get("name"))

@app.route('/register', methods=["POST"])
def register():
  firstname = request.form.get("firstname")
  lastname = request.form.get("lastname")
  age = request.form.get("age")
  email = request.form.get("email")
  password = request.form.get("password")

  if not firstname or (not lastname) or (not age):
    return render_template("failure.html", msg="Form not filled properly")

  user = User.query.filter_by(email=email).first()
  if user:
    return render_template("failure.html", msg="Email already has a account made")

  user = User(firstname=firstname, 
              lastname=lastname,
              age=age,
              email=email,
              password=password)
  db.session.add(user)
  db.session.commit()

  session["name"] = firstname

  return redirect(url_for("index"))

@app.route('/login', methods=["GET", "POST"])
def login():
  if request.method == "POST":
    user = User.query.filter_by(email=request.form.get("email").first())
    if user.password == request.form.get("password"):
      pass

@app.route('/logout')
def logout():
  pass


if __name__ == "__main__":
  db.create_all()
  app.run(debug=True)