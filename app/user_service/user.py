from urllib import response
from flask import Flask, jsonify, request
import requests
from sqlalchemy import select
from dotenv import dotenv_values
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash
from models import db, User
import sys


# grab .env vars
private_stuff = dotenv_values('.env')

# create the app.
app = Flask(__name__)
for key in private_stuff:
    app.config[key] = private_stuff[key]

# Initialize the database with the app.
db.init_app(app)
jwt = JWTManager(app)

# Create the tables if they dont exist already.
with app.app_context():
     db.create_all()

def _get_token(params):
    # create request
    url = 'http://127.0.0.1:5000/create'
    myobj = {'email' : params['email'], 'password' : params['password'], 'is_admin' : params['is_admin'], 'source' : 'user_service'}
    _re = requests.post(url, json = myobj)
    return _re.json()


# Create - User
# This wants form data, not json.
@app.route('/user', methods=["POST"])
def create_user():
      # Seems redundant, cant even get here if it isnt a post request.
      if request.method == "POST":
            # make sure everything is here.
            # start with a list of all thats required
            required_params = [ 'email', 'username', 'first_name', 'last_name' ]

            # Look through params and make a dictionary if all is well.
            user_params = {}
            if all(param in request.form for param in required_params):
                # hash incoming
                hashed_password = generate_password_hash(request.form['password'])
                print(f'Hashed Password: {hashed_password}')
                # gather everything.
                user_params = {param : request.form[param] for param in required_params}
                user_params['is_admin'] = True
                user_params['password'] = hashed_password
                user_params['source'] = "user_service"
                # Now check that email and username are unique.
                email = db.session.execute(select(User.email_address).where(User.email_address == user_params['email']))
                username = db.session.execute(select(User.user_name).where(User.user_name == user_params['username']))

                if (email is not email.mappings().all()) or (username is not username.mappings().all()):
                    # this means both are unique so make the user. grab a token.
                    new_user = User(user_params)
                    # Create the user.
                    db.session.add(new_user)
                    db.session.commit()
                    db.session.refresh(new_user)
                else:
                    # if youre here it means someone already has that username or email.
                    return jsonify(error='Account Already exists..'), 400
                # here we created the user, need to get token
                token = _get_token(user_params)                
                #Prepare response
                response_data = { 'user' : new_user.serialize(), 'token' : token['token']}
                return jsonify(response_data), 201
            else:
                  return jsonify(error='Missing Required Fields'), 400
      else:
           return jsonify(error='Bad Request'), 400

# Read - User
# opens token, gets reqested user if it exists, makes sure you can access this person. if all is well sends it back.
@app.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    # get id from token
    token_info = get_jwt_identity()
    # Grabs the user from the db, if not returns 404.
    user = db.get_or_404(User, user_id)
    # little security, only want to return this to itself or an admin
    if bool(token_info['is_admin']) or user.email_address == token_info['email']:
         return jsonify(user.serialize())
    return jsonify(error="UnAuthorized, you can only look at your own stuff"), 401

# Update - User
# checks token, checks params, checks email matches or is_admin if its good updates the user.
@app.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
     token_info = get_jwt_identity()
     required_params = ['first_name', 'last_name', 'user_name']
     if all(param in request.json for param in required_params):
        # grab the user.
        user = get_user(user_id)
        if bool(token_info['is_admin']) or token_info['email'] == user.email_address:       
            user.first_name = request.json.get('first_name')
            user.last_name = request.json.get('last_name')
            db.session.commit()
            return jsonify(user.serialize()), 201 # success
        else:
            return jsonify(error="Missing a parameter!"), 400

# Delete - User
@app.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
     if bool(get_jwt_identity()['is_admin']):
        # get the user
        user = db.session.get(user_id)
        if user is None:
            return jsonify(error='Bad User ID'), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify({'result' : True}), 200
     else:
         return jsonify(error='Its Unclear what happened'), 400

# List of required error handlers

# Bad Request Error
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify(error=str(error)), 400

# Unauthorized Action Error
@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return jsonify(error=str(error)), 401

# Forbidden Error
@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    return jsonify(error=str(error)), 403

# Page Not Found Error
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 Page Not Found errors."""
    return jsonify(error=str(error)), 404

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error errors."""
    return jsonify(error=str(error)), 500

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = None
    # run if called.
    app.run(port=private_stuff['PORT'] if port is None else port , debug=True)