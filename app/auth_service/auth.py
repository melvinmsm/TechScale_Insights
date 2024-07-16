from flask import Flask, jsonify, request, make_response
from dotenv import dotenv_values
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from flask_jwt_extended import create_access_token, JWTManager
from datetime import datetime, timedelta
from flask_redis import FlaskRedis
import sys



# grab .env vars
private_stuff = dotenv_values('.env')
# create the app.
app = Flask(__name__)
# Config. app
app.config['SECRET_KEY'] = private_stuff['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = private_stuff['SQLALCHEMY_DATABASE_URI']
app.config['JWT_ALGORITHM'] = private_stuff['JWT_ALGORITHM']
app.config['REDIS_URL'] = private_stuff['REDIS_URL']

redis_store = FlaskRedis(app)

db.init_app(app)
jwt=JWTManager(app)
with app.app_context(): 
     db.create_all()


#to login user already present and generate token
@app.route('/login', methods=['POST'])
def login():
    data=request.get_json()
    email=data.get("email")
    password=data.get("password")
    # Check if the email exists in the database
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404

    # Check if the password is correct
    if user.password != password:
        return jsonify({"message": "Incorrect password"}), 401
    
    # Check if token is cached
    cached_token = redis_store.get(email)
    if cached_token:
        return jsonify({"message": "Login successful", "token": cached_token.decode(), "from_cache": "True"}), 200


    # Generate a token based on the email and whether the user is an admin
    token = generateToken(email, user.is_admin)
    # Cache the token
    redis_store.set(email, token, ex=3600)  # expire in 1 hour

    return jsonify({"message": "Login successful", "token": token, "from_cache": "False"}), 200


#to store user credentials and appropriate permission level
@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    email=data.get("email")
    password=data.get("password")
    is_admin=data.get("is_admin")
    #added source so that only credentials passed by user_service micro-service 
    #are provided a token
    source=data.get("source")
    if(email and password and source=="user_service"): 
         #provide data as a dictionary
         new_user = User(arg_dic={'email': email,'password': password,'is_admin': is_admin})
         db.session.add(new_user)
         db.session.commit()

         token=generateToken(email, is_admin)

         return jsonify({"message": "User created successfully", "token": token}), 201
    else:
         return jsonify({"message": "Invalid request parameters"}), 400


#generates token based on email, and permission (is_admin= True/False)
def generateToken(email, is_admin):
    data = {
    'email': email,
    'is_admin': is_admin
    }
    timeout = timedelta(seconds=3600)  # 1 hour
    access_token = create_access_token(identity=data, expires_delta=timeout)

    return access_token


if __name__=='__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = None
    # run if called.
    app.run(port=private_stuff['PORT'] if port is None else port , debug=True)