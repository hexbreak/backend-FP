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

# Get / username
@app.route('/user/<username>', methods=['GET'])
def obtain_username(username):

    body = request.get_json()
    get_user = User.query.filter_by(username=username)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404)
    response_body = list(map(lambda x: x.serialize(), get_user))
    
    return jsonify(response_body), 200

# Get / username
@app.route('/user/<int:user_id>', methods=['GET'])
def id_username(user_id):

    body = request.get_json()
    get_user = User.query.get(user_id)
    if get_user is None:
        raise APIException('Username does not exist.', status_code=404) 
    response_body = get_user.serialize()
    
    return jsonify(response_body), 200

@app.route('/user/<int:user_id>/backlog/<int:id>', methods=['POST', 'PUT', 'DELETE'])
def new_backlog(user_id, id):

    body = request.get_json()

    if request.method == 'POST':
        addbacklog = Backlog(user_id=user_id, game_name=body['game_name'], game_id=body['game_id'], game_image=body['game_image'])
        db.session.add(addbacklog)
        db.session.commit()
        response_body = addbacklog.serialize()
        
        return jsonify(response_body), 200

    if request.method == 'PUT':
        updatebacklog = Backlog.query.get(id)
        updatebacklog.game_name = body["game_name"]
        updatebacklog.game_id = body["game_id"]
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
        
# PUT method for new listing for all tables
@app.route('/user/<int:user_id>', methods=['PUT'])
def post_editprofile(user_id):

    body = request.get_json()
    print("// body", body)
    if body is None:
        raise APIException("Body is empty", status_code=404)

    for i in range(3):
        addplatform = Platform(user_id=user_id, platform_name=body['platforms'][i]['platform_name'], platform_id=body['platforms'][i]['platform_id'])
        db.session.add(addplatform)
    db.session.commit()

    for i in range(3):
        addplaying = NowPlaying(user_id=user_id, game_name=body['playing'][i]['game_name'], game_id=body['playing'][i]['game_id'], notes=body['playing'][i]['notes'], game_image=body['playing'][i]['game_image'])
        db.session.add(addplaying)
    db.session.commit()

    for i in range(9):
        addgameprogression = Highlights(user_id=user_id, 
        game_name=body['game_progression'][i]['game_name'], game_id=body['game_progression'][i]['game_id'])
        db.session.add(addgameprogression)
    db.session.commit()

    for i in range(2):
        addlike = TagLike(user_id=user_id, name=body['liked'][i]['name'], tag_id=body['liked'][i]['tag_id'])
        db.session.add(addlike)
    db.session.commit()

    for i in range(2):
        addislike = TagDislike(user_id=user_id, name=body['disliked'][i]['name'], tag_id=body['disliked'][i]['tag_id'])
        db.session.add(addislike)
    db.session.commit()

    obtainUser = User.query.get(user_id)
    response_body = obtainUser.serialize()

    return jsonify(response_body)

    # Back up Duplicate code if loop ever stops working
    # addplatform1 = Platform(user_id=user_id, platform_name=body['platforms'][0]['platform_name'], platform_id=body['platforms'][0]['platform_id'])
    # db.session.add(addplatform1)
    # db.session.commit()

# testing purposes / PUT for adding new Now Playing
@app.route('/user/<int:user_id>/newplay', methods=['PUT'])
def add_newplay(user_id):

    body = request.get_json()

    addplay1 = NowPlaying(user_id=user_id, game_name=body['game_name'], game_id=body['game_id'], notes=body['notes'], game_image=body['game_image'])
    db.session.add(addplay1)
    db.session.commit()

    response_body = addplay1.serialize()

    print("/PRINT-ADD/", response_body)

    return jsonify(response_body), 200

# testing purposes / GET for grabbing any updated change to Now Playing
@app.route('/user/<int:user_id>/getplay', methods=['GET'])
def get_nowplay(user_id):

    body = request.get_json()
    obtainplay = NowPlaying.query.filter_by(user_id=user_id)
    response_body = list(map(lambda x: x.serialize(), obtainplay))
    print("/PRINT-GET/", response_body)

    return jsonify(response_body), 200

# testing purposes / PUT for updating a game already in Now Playing
@app.route('/user/<int:user_id>/editplay/<int:id>', methods=['PUT'])
def edit_newplay(user_id, id):
    
    body = request.get_json()
    editplay = NowPlaying.query.get(id)
    editplay.game_name = body["game_name"]
    editplay.game_id = body["game_id"]
    editplay.game_image = body["game_image"]
    editplay.notes = body["notes"]
    db.session.commit()
    posteditplay = NowPlaying.query.filter_by(user_id=user_id)
    response_body = list(map(lambda x: x.serialize(), posteditplay))

    print("/PRINT-EDIT/", response_body)

    return jsonify(response_body), 200

# testing purposes / DELETE for removing one game from Now Playing
@app.route('/user/<int:user_id>/deleteplay/<int:id>', methods=['DELETE'])
def delete_newplay(user_id, id):

    body = request.get_json()
    deleteplay = NowPlaying.query.get(id)
    db.session.delete(deleteplay)
    db.session.commit()
    postdeleteplay = NowPlaying.query.filter_by(user_id=user_id)
    response_body = list(map(lambda x: x.serialize(), postdeleteplay))
    print("/PRINT-DELETE/", response_body)

    return jsonify(response_body), 200

# Add a game for playing with username
@app.route('/user/<username>/nplay', methods=['POST'])
def adduser_playing(username):

    body = request.get_json()

    if body is None:
        raise APIException("Body is empty, need: game_name & game_id.", status_code=404)
    if 'game_name' not in body:
        raise APIException("Missing game_name.", status_code=404)
    if 'game_id' not in body:
        raise APIException("Missing game_id", status_code=404)
    if 'notes' not in body:
        raise APIException("Missing notes, leave an empty string.", status_code=404)
    
    nowplaying1 = NowPlaying(username=username, game_name=body['game_name'], game_id=body['game_id'], notes=body['notes'])
    db.session.add(nowplaying1)
    db.session.commit()
    response_body = nowplaying1.serialize()

    print("/ print test for /", response_body)

    return jsonify(response_body), 200

# Add a game to favorites
@app.route('/user/<int:user_id>/fav', methods=['POST', 'GET'])
def addget_fav(user_id):

    body = request.get_json()
    
    if request.method == 'POST':
        if body is None:
            raise APIException("Body is empty, need: game_name, game_image & game_id.", status_code=400)
        if 'game_name' not in body:
            raise APIException("Missing game_name.", status_code=400)
        if 'game_id' not in body:
            raise APIException("Missing game_id.", status_code=400)
        if 'game_image' not in body:
            raise APIException("Missing background_image", status_code=404)

        favoritelist1 = FavoriteList(user_id=user_id, game_id=body['game_id'], game_name=body['game_name'], game_image=body['game_image'])
        db.session.add(favoritelist1)
        db.session.commit()
        response_body = favoritelist1.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body), 200
    
    if request.method == 'GET':
        get_fav = db.session.query(FavoriteList).filter(FavoriteList.user_id == user_id)
        response_body = list(map(lambda x: x.serialize(), get_fav))
        # fav_list = []

        # for x in response_body:
        #     if x['game_name'] != "":
        #         fav_list.append(x['game_name']) # prints an array list of game names only.

        return jsonify(response_body), 200
    
    return "Ok!", 200

# Delete a game from favorite list
@app.route('/user/<int:user_id>/fav/<int:favoritelist_id>', methods=['PUT','DELETE'])
def putdel_fav(user_id, favoritelist_id):

    body = request.get_json()

    if request.method == 'PUT':
        put_fav = FavoriteList.query.get(favoritelist_id)
        if put_fav is None:
            raise APIException("Body is empty, need: game_name & game_id", status_code=404)
        if 'game_name' in body:
            put_fav.game_name = body['game_name']
        if 'game_id' in body:
            put_fav.game_id = body['game_id']
        if 'game_image' in body:
            put_fav.game_image = body['game_image']
        db.session.commit()
        response_body = put_fav.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body), 200
    
    if request.method == 'DELETE':
        remove_favorite = FavoriteList.query.get(favoritelist_id)
        if remove_favorite is None:
            raise APIException ('Game not found in Favorite List', status_code=404)
        db.session.delete(remove_favorite)
        db.session.commit()

        new_list = FavoriteList.query.all()
        response_body = list(map(lambda x: x.serialize(), new_list))
        
        print("/ print test for /", response_body)

        return jsonify(response_body), 200
    
    return "Ok!", 200

@app.route('/user/<int:user_id>/delfav/<int:favoritelist_id>', methods=['DELETE'])
def delete_favorite(user_id, favoritelist_id):

    remove_favorite = FavoriteList.query.get(favoritelist_id)
    if remove_favorite is None:
        raise APIException ('Game not found in Favorite List', status_code=404)
    db.session.delete(remove_favorite)
    db.session.commit()

    new_list = FavoriteList.query.all()
    response_body = list(map(lambda x: x.serialize(), new_list))
    
    print("/ print test for /", response_body)

    return jsonify(response_body), 200


# Add / Get Platforms
@app.route('/user/<int:user_id>/plat', methods=['POST', 'GET'])
def add_platform(user_id):

    body = request.get_json()

    if request.method == 'POST':
        if body is None:
            raise APIException("Body is empty, need: platform_name & platform_id", status_code=404)
        if 'platform_name' not in body:
            raise APIException("Missing platform_name", status_code=404)
        if 'platform_id' not in body:
            raise APIException("Missing platform_id", status_code=404)
        
        platform1 = Platform(user_id=user_id, platform_name=body['platform_name'], platform_id=body['platform_id'])
        db.session.add(platform1)
        db.session.commit()
        response_body = platform1.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body)
    
    if request.method == 'GET':
        get_plat = db.session.query(Platform).filter(Platform.user_id == user_id)
        response_body = list(map(lambda x: x.serialize(), get_plat))
        plat_list = []

        for x in response_body:
            if x['platform_name'] != "":
                plat_list.append(x['platform_name'])

        return jsonify(plat_list), 200
    
    return "Ok!", 200
        

# Update / Delete Platforms
@app.route('/user/<int:user_id>/plat/<int:plat_id>', methods=['PUT', 'DELETE'])
def putdel_platform(user_id, plat_id):

    body = request.get_json()

    if request.method == 'PUT':
        put_plat = Platform.query.get(plat_id)
        if put_plat is None:
            raise APIException("Body is empty, need: platform_name & platform_id", status_code=404)
        if 'platform_name' in body:
            put_plat.platform_name = body['platform_name']
        if 'platform_id' in body:
            put_plat.platform_id = body['platform_id']
        db.session.commit()
        response_body = put_plat.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body), 200

    if request.method == 'DELETE':
        del_plat = Platform.query.get(plat_id)
        if del_plat is None:
            raise APIException("Platform not found.", status_code=404)
        db.session.delete(del_plat)
        db.session.commit()

        plat_list = Platform.query.all()
        response_body = list(map(lambda x: x.serialize(), plat_list))
        
        print("/ print test for /", response_body)

        return jsonify(response_body), 200
    
    return "Ok!", 200

# Post / Get a game in Highlights
@app.route('/user/<int:user_id>/hl', methods=['POST', 'GET'])
def postget_highlight(user_id):

    body = request.get_json()

    if request.method == 'POST':
        if body is None:
            raise APIException("Body is empty, need: game_name & game_id", status_code=404)
        if 'game_name' not in body:
            raise APIException("Missing game_name", status_code=404)
        if 'game_id' not in body:
            raise APIException("Missing game_id", status_code=404)
        
        highlight1 = Highlights(user_id=user_id, game_name=body['game_name'], game_id=body['game_id'])
        db.session.add(highlight1)
        db.session.commit()
        response_body = highlight1.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body)
    
    if request.method == 'GET':
        get_hl = db.session.query(Highlights).filter(Highlights.user_id == user_id)
        response_body = list(map(lambda x: x.serialize(), get_hl))
        hl_list = []

        for x in response_body:
            if x['game_name'] != "":
                hl_list.append(x['game_name'])

        return jsonify(hl_list), 200

    return "Ok!", 200

# Update / Delete Platforms
@app.route('/user/<int:user_id>/hl/<int:hl_id>', methods=['PUT', 'DELETE'])
def putdel_highlight(user_id, hl_id):

    body = request.get_json()

    if request.method == 'PUT':
        put_hl = Highlights.query.get(hl_id)
        if put_hl is None:
            raise APIException("Body is empty, need: platform_name & platform_id", status_code=404)
        if 'game_name' in body:
            put_hl.game_name = body['game_name']
        if 'game_id' in body:
            put_hl.game_id = body['game_id']
        db.session.commit()
        response_body = put_hl.serialize()

        print("/ print test for /", response_body)

        return jsonify(response_body), 200

    if request.method == 'DELETE':
        del_hl = Highlights.query.get(hl_id)
        if del_hl is None:
            raise APIException("Game not found.", status_code=404)
        db.session.delete(del_hl)
        db.session.commit()

        hl_list = Highlights.query.all()
        response_body = list(map(lambda x: x.serialize(), hl_list))
        
        print("/ print test for /", response_body)

        return jsonify(response_body), 200
    
    return "Ok!", 200

# Add a tag to liked tags
@app.route('/user/<int:user_id>/like', methods=['POST'])
def addtags_like(user_id):

    body = request.get_json()

    if body is None:
        raise APIException("Body is empty, need: tag_name & tag_id.", status_code=400)
    if 'tag_name' not in body:
        raise APIException("Missing tag_name.", status_code=400)
    if 'tag_id' not in body:
        raise APIException("Missing tag_id.", status_code=400)

    liked1 = Liked(user_id=user_id, tag_name=body['tag_name'], tag_id=body['tag_id'])
    db.session.add(liked1)
    db.session.commit()
    response_body = liked1.serialize()

    print("/ print test for /", response_body)

    return jsonify(response_body), 200

# Get Liked tags listed in array
@app.route('/user/<int:user_id>/like', methods=['GET'])
def gettags_liked(user_id):

    body = request.get_json()

    get_likes = db.session.query(Liked).filter(Liked.user_id == user_id)
    response_body = list(map(lambda x: x.serialize(), get_likes))
    likes_list = []

    for x in response_body:
        if x['tag_name'] != "":
            likes_list.append(x['tag_name'])

    return jsonify(likes_list), 200

# Delete a Liked tag
@app.route('/user/<int:user_id>/like/<int:liked_id>', methods=['DELETE'])
def deltags_liked(user_id, liked_id):

    del_like = Liked.query.get(liked_id)
    if del_like is None:
        raise APIException ('Tag not found in Liked Tags', status_code=404)
    db.session.delete(del_like)
    db.session.commit()

    tag_list = Liked.query.all()
    response_body = list(map(lambda x: x.serialize(), tag_list))
    
    print("/ print test for /", response_body)

    return jsonify(response_body), 200

# Add a tag to disliked tags
@app.route('/user/<int:user_id>/dislike', methods=['POST'])
def addtags_dislike(user_id):

    body = request.get_json()

    if body is None:
        raise APIException("Body is empty, need: tag_name & tag_id.", status_code=400)
    if 'tag_name' not in body:
        raise APIException("Missing tag_name.", status_code=400)
    if 'tag_id' not in body:
        raise APIException("Missing tag_id.", status_code=400)

    dislike1 = Disliked(user_id=user_id, tag_name=body['tag_name'], tag_id=body['tag_id'])
    db.session.add(dislike1)
    db.session.commit()
    response_body = dislike1.serialize()

    print("/ print test for /", response_body)

    return jsonify(response_body)

# Get Disliked tags listed in array
@app.route('/user/<int:user_id>/dislike', methods=['GET'])
def gettags_disliked(user_id):

    body = request.get_json()

    get_dislikes = db.session.query(Disliked).filter(Disliked.user_id == user_id)
    response_body = list(map(lambda x: x.serialize(), get_dislikes))
    dislikes_list = []

    for x in response_body:
        if x['tag_name'] != "":
            dislikes_list.append(x['tag_name'])

    return jsonify(dislikes_list), 200

# Delete a Disliked tag
@app.route('/user/<int:user_id>/disliked/<int:disliked_id>', methods=['DELETE'])
def deltags_dislike(user_id, disliked_id):

    del_dislike = Disliked.query.get(disliked_id)
    if del_dislike is None:
        raise APIException ('Tag not found in Disliked Tags', status_code=404)
    db.session.delete(del_dislike)
    db.session.commit()

    tag_list = Disliked.query.all()
    response_body = list(map(lambda x: x.serialize(), tag_list))
    
    print("/ print test for /", response_body)

    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)