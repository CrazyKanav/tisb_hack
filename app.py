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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    bio = db.Column(db.String, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))

    user = relationship("User", back_populates="teacher")
    subject = relationship("Subject", back_populates="teacher")

class Subject(db.Model):
  __tablename__ = 'subjects'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  subject_name = db.Column(db.String, nullable=False)

  def __repr__(self):
    return f"{self.subject_name}"
  teacher = relationship("Teacher", back_populates="subject")

def check_teacher(user):
  if user.teacher:
    return True
  else:
    return False

def get_subjects():
  subjects = Subject.query.all()
  return subjects



@app.route('/signup_teacher', methods=["GET", "POST"])
def signup_teacher():
    if request.method == "POST":
        # Check if the user is logged in
        if session["name"] == None:
            return render_template("failure.html", msg="You need to log in to become a teacher", send_to_home=True)

        # Retrieve additional data for teacher profile
        bio = request.form.get("bio")
        qualifications = request.form.get("qualifications")
        subject = request.form.get("subject") # get the subject 
        
        # Fetch the logged-in user
        user_name = session['name']
        user = User.query.filter_by(firstname=user_name).first()
        print(user)

        subject_id = Subject.query.filter_by(subject_name=subject).first()
        
        # Create a new teacher profile associated with the logged-in user
        new_teacher = Teacher(user=user, bio=bio, qualifications=qualifications, subject=subject_id)
        db.session.add(new_teacher)
        db.session.commit()

        # Set a cookie indicating that the user is a teacher
        session['is_teacher'] = True

        return redirect(url_for("index"))
    else:
      if session['name'] == None:
          return render_template("failure.html", msg="You need to log in to become a teacher", send_to_home=True)
      try:
        if session['is_teacher'] == True:
          return render_template("failure.html" , msg="Already a teacher", send_to_home=True)
        else:
          # Fetch all available subjects
          subjects = get_subjects()
          print(subjects)
          return render_template("signup_teacher.html", subjects=subjects)
      except KeyError: # to make sure if the value shows an error 
        session["is_teacher"] = False
        return render_template("signup_teacher.html")

@app.route('/')
def index():
  # try:
    # print(session["name"])
    try:
      user = User.query.filter_by(firstname=session["name"]).first()
    except KeyError:
      session["name"] = None
      user =  None
    # return render_template("index.html", name=user, teacher=session.get("is_teacher"))
    return render_template("index.html", user=user, teacher=session.get("is_teacher"))

@app.route('/register', methods=["POST", "GET"])
def register():
  if request.method == "POST":
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
  else:
    return render_template("signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():
  if request.method == "POST":
    user = User.query.filter_by(email=request.form.get("email")).first()
    print(user)
    if user == None:
      return render_template("failure.html", msg="email id does not have a user", send_to_home=True)
    else:
      if user.password == request.form.get("password"):
        session["name"] = user.firstname
        return redirect(url_for("index"))
      
      return render_template("failure.html", msg="password wrong", send_to_home=True)
  else:
    return render_template("index.html")

@app.route('/logout')
def logout():
  session["name"] = None
  session["is_teacher"] = None
  return redirect(url_for("index"))

@app.route('/search', methods=["GET", "POST"])
def search():
  if request.method == "GET":
    subjects = get_subjects()
    teachers = None
    return render_template("search.html", teachers=teachers, subjects=subjects)
  else:
    subject_name = request.form.get("subject")
    subject = Subject.query.filter_by(subject_name=subject_name).first()
    teachers = Teacher.query.filter_by(subject=subject).all()
    subjects = get_subjects()
    return render_template("search.html", teachers=teachers, subject=subject, subjects=subjects)

if __name__ == "__main__":
  app.run(debug=True)