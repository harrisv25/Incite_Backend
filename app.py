from flask import Flask, render_template, request, jsonify, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS, cross_origin
import sys
from config import *
from flask import session

app = Flask(__name__)
CORS(app, origins=[REACT_APP_FRONTEND_URL], expose_headers=["Content-Type", "X-CSRFToken"], supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Phareo25!Vahj1234@localhost/incite_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.app_context()
app.secret_key = login_secret_key

db =SQLAlchemy(app)

class User(db.Model):
    __tablename__='users'
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    date_joined = db.Column(db.Date, default=datetime.utcnow)
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
        }

class Test(db.Model):
    __tablename__='tests'
    id=db.Column(db.Integer, primary_key=True)
    tname = db.Column(db.String(40), unique=True)
    desc=db.Column(db.Text)
    def __init__(self, tname, desc):
        self.tname = tname
        self.desc = desc
    def to_json(self):
        return {
            'id' : self.id,
            'tname' : self.tname, 
            'desc' : self.desc
        }
        
with app.app_context():
    db.create_all()

#works to an extent
@app.route('/')
@cross_origin(supports_credentials=True)
def index():
    tests = Test.query.all()
    # [print(t.tname, file=sys.stderr) for t in tests]
    return jsonify([test.to_json() for test in tests])


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


@app.route('/delete/<int:test_id>', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def delete_test(test_id):
    test = Test.query.get(test_id)
    db.session.delete(test)
    db.session.commit()
    return redirect(url_for('/'))


@app.route('/Profile/<int:user_id>', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def Profile(user_id):
    user = User.query.get(user_id)
    print(user.to_json(), file=sys.stderr)
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
            # print(session['user_id'] == None, file=sys.stderr)
            return jsonify(session['user_id'])
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
    #Need to check if name is avaiable to register
    user=User(username, email, password)
    db.session.add(user)
    db.session.commit( )
    return redirect(REACT_APP_FRONTEND_URL, code=302)

@app.route('/logout')
@cross_origin(supports_credentials=True)
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))




        


if __name__ == '__main__':
    app.run(debug=True)
     