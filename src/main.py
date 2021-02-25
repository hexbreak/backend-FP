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
from models import db, User, Backlog, Favorites, AboutMe
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

# WIP - Find out how to get filter working for Genres
@app.route('/user/<int:user_id>/genre', methods=['GET'])
def filter_first_name(user_id):

    body = request.get_json()

    result = db.session.query(Backlog).filter(Backlog.user_id == user_id)
    all_backlog = list(map(lambda x: x.serialize(), result))
    general_list = []

    for x in all_backlog:
        if x['game_genre'] != "":
            general_list.append(x['game_genre'])

    if general_list is None:
        raise APIException('You should not be seeing this. Check the route for errors.', status_code=400)

    return jsonify(general_list), 200

# Login & Update / id
@app.route('/user/<int:user_id>', methods=['PUT', 'GET'])
def obtain_user_id(user_id):

    body = request.get_json()

    if request.method == 'PUT':
        user1 = User.query.get(user_id)
        user1.username = body['username']
        db.session.commit()
        return jsonify(user1.serialize()), 200

    if request.method == 'GET':
        user1 = User.query.get(user_id)
        return jsonify(user1.serialize()), 200

    return 'Invalid Method', 404

# Get / username
@app.route('/user/<username>', methods=['GET'])
def obtain_username(username):

    body = request.get_json()

    get_user = User.query.filter_by(username=username)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404)
    response_body = list(map(lambda x: x.serialize(), get_user))
    return jsonify(response_body), 200
    
    return jsonify(response_body), 200


# Obtain & Update Backlog_ID's from a User_ID
@app.route('/user/<int:user_id>/backlog/<int:backlog_id>', methods=['PUT', 'GET'])
def get_backlog_id(user_id, backlog_id):

    body = request.get_json()

    if request.method == 'PUT':
        putbacklog = Backlog.query.get(backlog_id)
        if putbacklog is None:
            raise APIException('Backlog ID not found', status_code=404)
        if 'game_id' in body:
            putbacklog.game_id = body['game_id']
        if 'game_name' in body:
            putbacklog.game_name = body['game_name']
        if 'game_platform' in body:
            putbacklog.game_platform = body['game_platform']
        if 'game_genre' in body:
            putbacklog.game_genre = body['game_genre']
        if 'game_notes' in body:
            putbacklog.game_notes = body['game_notes']
        if 'progress_status' in body:
            putbacklog.progress_status = body['progress_status']
        if 'now_playing' in body:
            putbacklog.now_playing = body['now_playing']
        db.session.commit()
        return jsonify(putbacklog.serialize()), 200

        # eventually remmove the if statements for what the user cannot update/change.

    if request.method == 'GET':
        getbacklog = Backlog.query.get(backlog_id)
        return jsonify(getbacklog.serialize()), 200

    return "Ok!", 200

# Create User Account
@app.route('/user', methods=['POST'])
def post_user():

    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'username' not in body:
        raise APIException('You need to specify the username', status_code=400)
    if 'email' not in body:
        raise APIException('You need to specify the email', status_code=400)
    if 'password' not in body:
        raise APIException('You need to type down a new password', status_code=400)
    if 'first_name' not in body:
        raise APIException('You need to specify the first name', status_code=400)
    if 'last_name' not in body:
        raise APIException('You need to specify the last name', status_code=400)
    if 'profile_avatar' not in body:
        raise APIException('You need to link a avatar for the profile', status_code=400)

    user1 = User(username=body['username'], email=body['email'], password=body['password'], first_name=body['first_name'], last_name=body['last_name'], profile_avatar=body['profile_avatar'])
    db.session.add(user1)
    db.session.commit()

    return jsonify(user1.serialize()), 200

# Create new Backlog_ID for a User_ID
@app.route('/user/<int:user_id>/backlog', methods=['POST'])
def post_backlog(user_id):

    user1 = User.query.get(user_id) 
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'game_id' not in body:
        raise APIException('You need to specify the game id', status_code=400)
    if 'game_name' not in body:
        raise APIException('You need to specify the game name', status_code=400)
    if 'game_platform' not in body:
        raise APIException('You need to specify the game platform', status_code=400)
    if 'game_genre' not in body:
        raise APIException('You need to specify the game genre', status_code=400)
    if 'game_tags' not in body:
        raise APIException('You need to specify the game tags', status_code=400)
    if 'game_notes' not in body:
        raise APIException('You need to specify the game notes', status_code=400)
    if 'progress_status' not in body:
        raise APIException('You need to specify the progress status', status_code=400)
    if 'now_playing' not in body:
        raise APIException('You need to specify true or false for now playing', status_code=400)

    backlog1 = Backlog(user_id=user_id, game_id=body['game_id'], game_name=body['game_name'], game_platform=body['game_platform'], game_genre=body['game_genre'], game_tags=body['game_tags'], game_notes=body['game_notes'], progress_status=body['progress_status'], now_playing=body['now_playing'])
    db.session.add(backlog1)
    db.session.commit()

    print(backlog1)

    return jsonify(backlog1.serialize()), 200

# Delete a Backlog_ID from a User_ID
@app.route('/user/<int:user_id>/backlog/<int:backlog_id>', methods=['DELETE'])
def delete_backlog(user_id, backlog_id):

    remove_backlog = Backlog.query.get(backlog_id)
    if remove_backlog is None:
        raise APIException('Backlog ID not found', status_code=404)
    db.session.delete(remove_backlog)
    db.session.commit()

    print(remove_backlog)

    return "Backlog ID deleted.", 200

# Delete a User_ID's Favorite_ID
@app.route('/favorites', methods=['DELETE'])
def delete_favorite():

    remove_favorite = Favorites.query.get(favorites_id)

    if remove_favorite is None:
        raise APIEXception('Favorite list is not found.', status_code=404)
    
    db.session.delete(remove_favorite)
    db.session.commit()

    return "Favorite list has been removed", 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)