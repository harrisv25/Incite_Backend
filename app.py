from flask import Flask, render_template, request, jsonify, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS, cross_origin
import sys
from config import *

app = Flask(__name__)
CORS(app, origins=[REACT_APP_FRONTEND_URL], expose_headers=["Content-Type", "X-CSRFToken"], supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Phareo25!Vahj1234@localhost/incite_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context()


db =SQLAlchemy(app)

class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    date_joined = db.Column(db.Date, default=datetime.utcnow)

class Test(db.Model):
    __tablename__='tests'
    id=db.Column(db.Integer, primary_key=True)
    tname = db.Column(db.String(40))
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
        
#works to an extent
@app.route('/')
def index():
    tests = Test.query.all()
    # data = jsonify([test.to_json() for test in tests])
    return jsonify([test.to_json() for test in tests])
    # return render_template('index.html')

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
def delete_test(test_id):
    test = Test.query.get(test_id)
    db.session.delete(test)
    db.session.commit()
    return redirect(url_for('/'))





        


if __name__ == '__main__':
    app.run(debug=True)
     