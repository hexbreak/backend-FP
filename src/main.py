"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Platform, Backlog, GenreLike, GenreDislike, TagLike, TagDislike
import datetime
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "game-finder"  # Change this!
jwt = JWTManager(app)
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

@app.route("/register", methods=["POST"])
def register():
    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not email:
        return "Missing email", 400
    if not username:
        return "Missing username", 400
    if not password:
        return "Missing password", 400

    newUser = User(email=email, username=username, password=password)
    db.session.add(newUser)
    db.session.commit()

    return jsonify(newUser.serialize()), 200

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():

    credentials = request.json
    username = credentials.get("username", None)
    password = credentials.get("password", None)
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return jsonify("Invalid email or password."), 400

    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=username, expires_delta=expires)
    response = { "user_id": user.id, "token": access_token }

    return jsonify(response)

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    print(current_user)
    return jsonify(logged_in_as=current_user), 200

# This get method grabs EVERYTHING we have collected from the Users.
@app.route('/users', methods=['GET'])
def get_all_users():

    allusers = User.query.all()
    response_body = list(map(lambda x: x.serialize(), allusers))

    if response_body is None:
        raise APIException('You should not be seeing this. Check the route for errors.', status_code=400)

    return jsonify(response_body), 200

# Get Username by Username
@app.route('/user/<username>', methods=['GET'])
def obtain_username(username):

    body = request.get_json()
    get_user = User.query.filter_by(username=username)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404)
    response_body = list(map(lambda x: x.serialize(), get_user))
    
    return jsonify(response_body), 200

# Get User by ID
@app.route('/user/<int:user_id>', methods=['GET'])
def id_username(user_id):

    body = request.get_json()
    get_user = User.query.get(user_id)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404) 
    response_body = get_user.serialize()
    
    return jsonify(response_body), 200

# Backlog Post (Add) / Get (Obtain)
@app.route('/user/<int:user_id>/backlog', methods=['POST', 'GET'])
def get_backlog(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addbacklog = Backlog(user_id=user_id, game_name=body['game_name'], game_id=body['game_id'], game_image=body['game_image'])
        db.session.add(addbacklog)
        db.session.commit()
        response_body = addbacklog.serialize()
        
        return jsonify(response_body), 200

    if request.method == 'GET':
        getbacklog = Backlog.query.filter_by(user_id=user_id)
        response_body = list(map(lambda x: x.serialize(), getbacklog))

        return jsonify(response_body), 200

    return "Ok!", 200

# Backlog PUT (Update), DELETE (Remove)
@app.route('/user/<int:user_id>/backlog/<int:id>', methods=['PUT', 'DELETE'])
def new_backlog(user_id, id):

    body = request.get_json()

    if request.method == 'PUT':
        updatebacklog = Backlog.query.get(id)
        if updatebacklog is None:
            raise APIException('ID not found', status_code=404)
        if "game_name" in body:
            updatebacklog.game_name = body["game_name"]
        if "game_id" in body:
            updatebacklog.game_id = body["game_id"]
        if "game_image" in body:
            updatebacklog.game_image = body["game_image"]
        db.session.commit()
        response_body = updatebacklog.serialize()

        return jsonify(response_body), 200
    
    if request.method == 'DELETE':
        deletebacklog = Backlog.query.get(id)
        if deletebacklog is None:
            raise APIException('ID not found', status_code=404)
        db.session.delete(deletebacklog)
        db.session.commit()

        return jsonify('Deletion Successful'), 200

# Platforms POST (Add), GET (Obtain)
@app.route('/user/<int:user_id>/platforms', methods=['POST', 'GET'])
def addget_platform(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addplatform = Platform(user_id=user_id, platform_name=body['platform_name'], platform_id=body['platform_id'])
        db.session.add(addplatform)
        db.session.commit()
        response_body = addplatform.serialize()

        return jsonify(response_body), 200
    
    if request.method == 'GET':
        getplatforms = db.session.query(Platform).filter(Platform.user_id == user_id)
        response_body = list(map(lambda x: x.serialize(), getplatforms))

        return jsonify(response_body), 200

    return "All Good!", 200

# Platforms DELETE (Remove)
@app.route('/user/<int:user_id>/platforms/<int:id>', methods=['DELETE'])
def remove_platform(user_id, id):

    body = request.get_json()

    removeplatform = Platform.query.get(id)
    if removeplatform is None:
        raise APIException('ID not found', status_code=404)
    db.session.delete(removeplatform)
    db.session.commit()

    return jsonify('Deletion Successful'), 200

# GenreLike POST (Add) / GET (Obtain)
@app.route('/user/<int:user_id>/genrelikes', methods=['POST', 'GET'])
def addget_genrelikes(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addlike = GenreLike(user_id=user_id, name=body['name'], genre_id=body['genre_id'])
        db.session.add(addlike)
        db.session.commit()
        response_body = addlike.serialize()

        return jsonify(response_body), 200

    if request.method == 'GET':
        getlikedlist = GenreLike.query.filter_by(user_id=user_id)
        response_body = list(map(lambda x: x.serialize(), getlikedlist))

        return jsonify(response_body), 200

    return "Ok!", 200

# GenreLike DELETE (Remove)
@app.route('/user/<int:user_id>/degl/<int:id>', methods=['DELETE'])
def remove_genrelikes(user_id, id):

    body = request.get_json()

    removelike = GenreLike.query.get(id)
    if removelike is None:
        raise APIException('ID not found', status_code=404)
    db.session.delete(removelike)
    db.session.commit()

    return jsonify('Deletion successful'), 200

# GenreDislike POST (Add) / GET (Obtain)
@app.route('/user/<int:user_id>/genredislikes', methods=['POST', 'GET'])
def addget_genredislikes(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addislike = GenreDislike(user_id=user_id, name=body['name'], genre_id=body['genre_id'])
        db.session.add(addislike)
        db.session.commit()
        response_body = addislike.serialize()

        return jsonify(response_body), 200

    if request.method == 'GET':
        getdislikedlist = GenreDislike.query.filter_by(user_id=user_id)
        response_body = list(map(lambda x: x.serialize(), getdislikedlist))

        return jsonify(response_body), 200

    return "Ok!", 200

# GenreDislike DELETE (Remove)
@app.route('/user/<int:user_id>/degd/<int:id>', methods=['DELETE'])
def remove_genredislikes(user_id, id):

    body = request.get_json()

    removedislike = GenreDislike.query.get(id)
    if removedislike is None:
        raise APIException('ID not found', status_code=404)
    db.session.delete(removedislike)
    db.session.commit()

    return jsonify('Deletion successful'), 200

# TagLike POST (Add) / GET (Obtain)
@app.route('/user/<int:user_id>/taglike', methods=['POST', 'GET'])
def postget_taglike(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addlike = TagLike(user_id=user_id, name=body['name'], tag_id=body['tag_id'])
        db.session.add(addlike)
        db.session.commit()
        response_body = addlike.serialize()

        return jsonify(response_body), 200

    if request.method == 'GET':
        getlikedlist = TagLike.query.filter_by(user_id=user_id)
        response_body = list(map(lambda x: x.serialize(), getlikedlist))

        return jsonify(response_body), 200

    return "Ok!", 200

# TagLike DELETE (Remove)
@app.route('/user/<int:user_id>/detl/<int:id>', methods=['DELETE'])
def remove_taglikes(user_id, id):

    body = request.get_json()

    removetag = TagLike.query.get(id)
    if removetag is None:
        raise APIException('ID not found', status_code=404)
    db.session.delete(removetag)
    db.session.commit()

    return jsonify('Deletion successful'), 200

# TagDislike POST (Add) / GET (Obtain)
@app.route('/user/<int:user_id>/tagdislike', methods=['POST', 'GET'])
def postget_tagdislikes(user_id):

    body = request.get_json()

    if request.method == 'POST':
        addislike = TagDislike(user_id=user_id, name=body['name'], tag_id=body['tag_id'])
        db.session.add(addislike)
        db.session.commit()
        response_body = addislike.serialize()

        return jsonify(response_body), 200

    if request.method == 'GET':
        getdislikedlist = TagDislike.query.filter_by(user_id=user_id)
        response_body = list(map(lambda x: x.serialize(), getdislikedlist))

        return jsonify(response_body), 200

    return "Ok!", 200

# TagDislike DELETE (Remove)
@app.route('/user/<int:user_id>/detd/<int:id>', methods=['DELETE'])
def remove_tagdislikes(user_id, id):

    body = request.get_json()

    removetag = TagDislike.query.get(id)
    if removetag is None:
        raise APIException('ID not found', status_code=404)
    db.session.delete(removetag)
    db.session.commit()

    return jsonify('Deletion successful'), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)