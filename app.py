from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
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

    # student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete-orphan")

    teacher = relationship("Teacher", uselist=False, back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'User{self.id} {self.firstname}'

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    bio = db.Column(db.String, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)

    user = relationship("User", back_populates="teacher")

# login_manager = LoginManager()
# login_manager.init_app(app)
    

# session["name"] = None

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
    return render_template("failure.html", msg="Form not filled properly", send_to_home=True)

  user = User.query.filter_by(email=email).first()
  if user:
    return render_template("failure.html", msg="Email already has a account made", send_to_home=True)

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
    user = User.query.filter_by(email=request.form.get("email")).first()
    print(user)
    if user == None:
      return render_template("failure.html", msg="email id does not have a user")
    else:
      if user.password == request.form.get("password"):
        session["name"] = user.firstname
        return redirect(url_for("index"))
      
      return render_template("failure.html", msg="password wrong")
  else:
    try:
      if session["name"]:
          return redirect(url_for("index"))
      else:
        return render_template("login.html")
    except KeyError:
      return render_template("failure.html", msg="Account not made yet, go register", send_to_home=True)

@app.route('/logout')
def logout():
  session["name"] = None
  return redirect(url_for("index"))

@app.route('/test')
def test():
   return render_template("test.html")

if __name__ == "__main__":
  app.run(debug=True)