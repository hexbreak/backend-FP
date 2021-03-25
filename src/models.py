from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    about = db.Column(db.String(1000), unique=False, nullable=True)
    image = db.Column(db.String(500), unique=False, nullable=True)
    favorite = db.relationship('FavoriteList', backref='user', lazy=True)
    platforms = db.relationship('Platform', backref='user', lazy=True)
    game_progression = db.relationship('Highlights', backref='user', lazy=True)
    playing = db.relationship('NowPlaying', backref='user', lazy=True)
    liked = db.relationship('TagLike', backref='user', lazy=True)
    disliked = db.relationship('TagDislike', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "about": self.about,
            "image": self.image,
            "favorite": list(map(lambda x: x.serialize(), self.favorite)),
            "platforms": list(map(lambda x: x.serialize(), self.platforms)),
            "game_progression": list(map(lambda x: x.serialize(), self.game_progression)),
            "playing": list(map(lambda x: x.serialize(), self.playing)),
            "liked": list(map(lambda x: x.serialize(), self.liked)),
            "disliked": list(map(lambda x: x.serialize(), self.disliked))
        }

class Platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform_name = db.Column(db.String(120), unique=False, nullable=True)
    platform_id = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Platform %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform_name": self.platform_name,
            "platform_id": self.platform_id
        }

class Highlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(120), unique=False, nullable=True)
    game_id = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Highlights %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_name": self.game_name,
            "game_id": self.game_id,
        }

class NowPlaying(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(250), unique=False, nullable=True)
    game_id = db.Column(db.String(120), unique=False, nullable=True)
    notes = db.Column(db.String(500), unique=False, nullable=True)

    def __repr__(self):
        return '<NowPlaying %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_name": self.game_name,
            "game_id": self.game_id,
            "notes": self.notes
        }

class FavoriteList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(250), unique=False, nullable=True)
    game_id = db.Column(db.String(120), unique=False, nullable=True)
    game_image = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<FavoriteList %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_name": self.game_name,
            "game_id": self.game_id,
            "game_image": self.game_image
        }

class TagLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<TagLike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
        }

class TagDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<TagDislike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
        }  