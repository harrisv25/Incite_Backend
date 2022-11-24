from flask import Flask, jsonify
from flask_login import LoginManager

# import dogs blueprint
from resources.tests import tests

# import user blueprint
from resources.user import user

# import all variables and methods from models.py file
import models

from flask_cors import CORS
CORS(tests, origins=['http://localhost:3000'], supports_credentials=True)

#cors for users
CORS(user, origins=['http://localhost:3000'], supports_credentials=True)

# will show error messages
DEBUG=True 

#port to run the app
PORT=8000 

#invoke our login manager before running app
login_manager = LoginManager()

#instantiating Flask class to make an app
app = Flask(__name__) 

#our secret key and session setup info
app.secret_key = "LJAKLJLKJJLJKLSDJLKJASD" # Need this to encode the session
login_manager.init_app(app) # set up the sessions on the app

@login_manager.user_loader 
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

#use this blueprint of the app to handle anything related to tests
app.register_blueprint(tests, url_prefix='/api/v1/tests')

#use this blueprint to handle users
app.register_blueprint(user, url_prefix='/api/v1/user')

#this is like an app.listen -- goes at bottom
if __name__ == '__main__':
    # when we start app, set up db+ tables like in models.py
    models.initialize()
    app.run(debug=DEBUG, port=PORT)