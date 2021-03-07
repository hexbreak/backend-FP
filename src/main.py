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
from models import db, User, Platform, Highlights, NowPlaying, FavoriteList, Liked, Disliked
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
            raise APIException('User ID not found', status_code=404)
        if 'about' in body:
            user1.about = body['about']
        if 'image' in body:
            user1.image = body['image']
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

@app.route('/user/<int:user_id>/addfav', methods=['POST'])
def obtain_favorites(user_id):

    body = request.get_json()
    
    if body is None:
        raise APIException("Body is empty, need: game_name & game_id.", status_code=400)
    if 'game_name' not in body:
        raise APIException("Missing game_name.", status_code=400)
    if 'game_id' not in body:
        raise APIException("Missing game_id.", status_code=400)
    
    favoritelist1 = FavoriteList(user_id=user_id, game_id=body['game_id'], game_name=body['game_name'])
    db.session.add(favoritelist1)
    db.session.commit()
    response_body = favoritelist1.serialize()

    print("/ print test for /", favoritelist1.serialize())

    return jsonify(response_body), 200


# # WIP - Filter Genre with id
# @app.route('/user/<int:user_id>/genre', methods=['GET'])
# def filter_first_name(user_id):

#     body = request.get_json()

#     result = db.session.query(Backlog).filter(Backlog.user_id == user_id)
#     all_backlog = list(map(lambda x: x.serialize(), result))
#     general_list = []

#     for x in all_backlog:
#         if x['game_genre'] != "":
#             general_list.append(x['game_genre'])

#     if general_list is None:
#         raise APIException('You should not be seeing this. Check the route for errors.', status_code=400)

#     return jsonify(general_list), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)