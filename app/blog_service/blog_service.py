from flask import Flask
from datetime import datetime
from dotenv import dotenv_values
from blog_models import db, BlogPost
from flask import request, jsonify, abort
from flask_redis import FlaskRedis
from flask_jwt_extended import JWTManager, jwt_manager, jwt_required
import json
import sys




#	Create a dictionary from the .env stuff
private_stuff = dotenv_values('.env')

# init Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = private_stuff['SQLALCHEMY_DATABASE_URI']
app.config['REDIS_URL'] = private_stuff['REDIS_URL']


redis_store = FlaskRedis(app)
db.init_app(app)
jwt = JWTManager(app)



# This will only create the tables once.
with app.app_context():
	db.create_all()

# create - Blog Post, works.
@app.route("/post", methods=["POST"])
@jwt_required()
def create_post():

    if request.method == "POST":
        # Required parameters for a blog post
        required_params = ['title', 'content', 'author']
        blog_content = {}

        # Check if all required parameters are present in the request
        if all(param in request.form for param in required_params):
            # Gather required info from the request
            blog_content = {param: request.form[param] for param in required_params}
            
            # Create the post
            new_post = BlogPost(**blog_content)
            db.session.add(new_post)
            db.session.commit()
            db.session.refresh(new_post)

            # Cache the new post
            post_data = {
                'id': new_post.id,
                'title': new_post.title,
                'content': new_post.content,
                'author': new_post.author,
                'date_posted': new_post.date_posted.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
            }
            redis_store.set(f"post:{new_post.id}", json.dumps(post_data), ex=3600)  # Cache the new post, expire in 1 hour


            # Prepare response data
            response_data = {
                'id': new_post.id,
                'date_posted': new_post.date_posted,
                # **blog_content
            }
            return jsonify(response_data), 201
        else:
            return abort(400)
    else:
        return abort(404)

# Read - post 
@app.route("/post/<int:post_id>", methods=["GET"])
@jwt_required()
def get_post(post_id):
    # Check if the post is cached
    cached_post = redis_store.get(f"post:{post_id}")
    if cached_post:
        # Deserialize the cached post from JSON string to a dictionary
        cached_post_dict = json.loads(cached_post)
        return jsonify({"message": "Response received from cache", "data": cached_post_dict}), 200
    
    # If not cached, query the database
    post = BlogPost.query.get(post_id)
    if post is not None:
        # Convert datetime objects to strings
        post_data = post.to_json()
        post_data['date_posted'] = post_data['date_posted'].strftime("%Y-%m-%d %H:%M:%S")
        post_data['last_edit'] = post_data['last_edit'].strftime("%Y-%m-%d %H:%M:%S")

        # Serialize the post to a JSON string before caching it
        post_json = json.dumps(post_data)
        # Cache the post for future requests
        redis_store.set(f"post:{post_id}", post_json, ex=3600)  # expire in 1 hour
        return jsonify({"message": "Response received from database", "data": post_data}), 200
    else:
      
      post = BlogPost.query.get(post_id)
      if post is not None:
            return jsonify(post.to_json()), 200
      else:
           return abort(403)
           
# Update - blog Post
@app.route("/post/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    required_params = ['title', 'content', 'author']

    # Retrieve the post to update
    post = BlogPost.query.get(post_id)
    if post is None:
        return abort(403)

    # Validate request data
    if not all(param in request.json for param in required_params):
        return abort(400)

    # Update post attributes
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.last_edit = datetime.utcnow()

    # Commit changes to database
    db.session.commit()

    # Return updated post data
    return jsonify(post.to_json()), 201
            
# Delete - post post
@app.route("/post/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    # Retrieve the post to delete
    post = BlogPost.query.get(post_id)
    if post is None:
        return abort(404)

    # Delete the post from the cache if it exists
    cached_post = redis_store.get(f"post:{post_id}")
    if cached_post:
        redis_store.delete(f"post:{post_id}")
    
    # Delete the post
    db.session.delete(post)
    db.session.commit()

    # Return success message
    return jsonify({'result': True}), 200

@app.errorhandler(400)
def bad_request(error):
     return jsonify({"Error" : "Bad Request, Validation Error: Missing required Fields"}), 400

@app.errorhandler(403)
def bad_request(error):
     return jsonify({'error': 'Post Not found'}), 403

# ErrorHandler - endpoint not found (404)
@app.errorhandler(404)
def page_not_found(error):
	return "<h1>404</h1><p>Oops, It looks like the page you're looking for cannot be found.", 404

if __name__=='__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = None
        # run if called.
        app.run(port=private_stuff['PORT'] if port is None else port , debug=True)