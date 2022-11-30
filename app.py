from flask import (
Flask, 
render_template, 
request, 
jsonify, 
redirect, 
url_for, 
Blueprint,
g)
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS, cross_origin
import sys
from config import *
from flask import session
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import func
from playhouse.shortcuts import model_to_dict
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm.attributes import flag_modified

app = Flask(__name__)
CORS(app, origins=[REACT_APP_FRONTEND_URL], expose_headers=["Content-Type", "X-CSRFToken"], supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Phareo25!Vahj1234@localhost/incite_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.app_context()
app.config['SECRET_KEY'] = login_secret_key
# app.secret_key = login_secret_key

db =SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__='users'
    id= db.Column(db.Integer, primary_key=True)
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    date_joined = db.Column(db.Date, default=datetime.utcnow)
    # answers=db.Column(ARRAY(db.Integer), nullable = False, default=[])
    answers = db.Column(db.PickleType(), nullable = False, default = {})
    # role = db.Column(db.String(50), defualt="user")
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    def to_json(self):
        return {
            'id' : self.id,
            'username' : self.username, 
            'email' : self.email,
            'date_joined' : self.date_joined,
            'answers' : self.answers
        }


#add a number of people answered section
class Question(db.Model):
    __tablename__='questions'
    id=db.Column(db.Integer, primary_key=True)
    prompt=db.Column(db.Text)
    answers=db.Column(ARRAY(db.String), nullable = False)
    popanswers=db.Column(ARRAY(db.Integer), nullable = False, default=[])
    def __init__(self, prompt, answers):
        self.prompt = prompt
        self.answers = answers
    def to_json(self):
        return {
            'id' : self.id,
            'prompt' : self.prompt, 
            'answers' : self.answers
        }
        
with app.app_context():
    db.create_all()
    
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'
login_manager.session_protection = "strong"
login_serializer = URLSafeTimedSerializer(app.secret_key)


@login_manager.user_loader
@cross_origin(supports_credentials=True)
def load_user(user_id):
    print(user_id, file=sys.stderr) #This isn't printing anything. I am not sure this route is being hit
    return User.query.get(user_id)

#works to an extent
@app.route('/')
@cross_origin(supports_credentials=True)
def index():
    if current_user.is_authenticated:
        print(current_user.username, file=sys.stderr)
    else:
        print('not', file=sys.stderr)
    questions = Question.query.all()
    # [print(t.tname, file=sys.stderr) for t in tests]
    return jsonify([q.to_json() for q in questions])


#This works From react
@app.route('/addTest', methods = ['POST'])
@cross_origin(supports_credentials=True)
def addTest():
    payload = request.get_json()
    print(REACT_APP_FRONTEND_URL+'/', file=sys.stderr)
    tname = payload['tname']
    desc = payload['desc']
    test=Test(tname, desc)
    db.session.add(test)
    db.session.commit( )
    return redirect(REACT_APP_FRONTEND_URL, code=302)

#This works From react
@app.route('/addQuestion/<int:user_id>', methods = ['POST'])
@cross_origin(supports_credentials=True)
def addQuestion(user_id):
    payload = request.get_json()
    print(payload, file=sys.stderr)
    prompt = payload['prompt']
    answers = payload['answers']
    answers = [a['answer'] for a in answers]
    question=Question(prompt, answers)
    db.session.add(question)
    db.session.commit( )
    return jsonify(1)


@app.route('/ViewQuestion/<int:user_id>', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def ViewQuestion(user_id):
    question = Question.query.order_by(func.random()).first()
    print( question, file=sys.stderr)
    return jsonify(question.to_json())

@app.route('/AnswerQuestion', methods = ['POST'])
@cross_origin(supports_credentials=True)
def AnswerQuestion():
    payload = request.get_json()
    # print('woow', file=sys.stderr)
    user_id = payload['user_id']
    question_id = payload['question_id']
    answer = payload['answer']['index']
    #update
    user = db.session.query(User).filter(User.id==user_id).first()
    user.answers[question_id] = answer
    # print(user.answers, file=sys.stderr)
    flag_modified(user, "answers")
    db.session.merge(user)
    db.session.flush()
    db.session.commit()
    question = db.session.query(Question).filter(Question.id==question_id).first()
    question.popanswers.append(answer)
    flag_modified(question, "popanswers")
    db.session.merge(question)
    db.session.flush()
    db.session.commit()
    return jsonify(user.answers)
    # return jsonify(1)
    

@app.route('/LoadQuestion/<int:user_id>', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def LoadQuestion(user_id):
    payload = request.get_json()
    print(payload, file=sys.stderr)
    questions = []
    answers = []
    percent = []
    user = db.session.query(User).filter(User.id==user_id).first()
    # print(user.answers, file=sys.stderr)
    for q in payload['answers']:
        question = db.session.query(Question).filter(Question.id==q).first()
        questions.append(question.prompt)
        answers.append(question.answers)
        percent.append(round(question.popanswers.count(str(user.answers[question.id]))/len(question.popanswers), 2))
    # print(percent, file=sys.stderr)
    return jsonify([questions, answers, percent])


@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def delete_test(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(1)


@app.route('/Profile/<int:user_id>', methods=['GET', 'POST'])
# @login_required
@cross_origin(supports_credentials=True)
def Profile(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_json())


@app.route('/Login', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def Login():
    if request.method == 'POST':
        session.pop('user_id', None)
        session['username'] = request.get_json()['username']
        session['password'] = request.get_json()['password']
        user = db.session.query(User).filter(User.username==session['username']).first()
        if user and user.password == session['password']:
            session['user_id'] = user.id
            login_user(user, remember=True, force=True)
            print(current_user, file=sys.stderr) #This successfully prints out a user
            return jsonify(current_user.id)
        else:
            return jsonify(-99999)
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''
#This works From react
@app.route('/Register', methods = ['POST'])
@cross_origin(supports_credentials=True)
def Register():
    payload = request.get_json()
    # print(payload, file=sys.stderr)
    username = payload['username']
    email = payload['email']
    password = payload['password']
    check = db.session.query(User).filter(User.username==username).first()
    if not check:
        echeck = db.session.query(User).filter(User.email==email).first()
        if not echeck:
            user=User(username, email, password)
            db.session.add(user)
            db.session.commit( )
            return jsonify(1)
        else:
            return jsonify(-1)
    else:
        return jsonify(0)
        # return redirect(REACT_APP_FRONTEND_URL, code=302)

# @app.route('/logout')
# @cross_origin(supports_credentials=True)
# def logout():
#     # remove the username from the session if it's there
#     session.pop('username', None)
#     return redirect(url_for('index'))




        


if __name__ == '__main__':
    app.run(debug=True)
     