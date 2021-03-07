"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Platform, Highlights, NowPlaying, FavoriteList
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# This get method grabs EVERYTHING we have collected from the Users.
@app.route('/users', methods=['GET'])
def get_all_users():

    allusers = User.query.all()
    response_body = list(map(lambda x: x.serialize(), allusers))

    if response_body is None:
        raise APIException('You should not be seeing this. Check the route for errors.', status_code=400)

    return jsonify(response_body), 200

# Login & Update / id
@app.route('/user/<int:user_id>', methods=['PUT', 'GET'])
def obtain_user_id(user_id):

    body = request.get_json()

    if request.method == 'PUT':
        user1 = User.query.get(user_id)
        if user1 is None:
            raise APIException('Backlog ID not found', status_code=404)
        if 'first_name' in body:
            user1.first_name = body['first_name']
        if 'last_name' in body:
            user1.last_name = body['last_name']
        if 'profile_avatar' in body:
            user1.profile_avatar = body['profile_avatar']
        db.session.commit()
        return jsonify(user1.serialize()), 200

    if request.method == 'GET':
        user1 = User.query.get(user_id)
        return jsonify(user1.serialize()), 200

    return 'Should look good', 200

# Get / username
@app.route('/user/<username>', methods=['GET'])
def obtain_username(username):

    body = request.get_json()
    get_user = User.query.filter_by(username=username)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404)
    response_body = list(map(lambda x: x.serialize(), get_user))
    
    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)