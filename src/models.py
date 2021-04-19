from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    user_games = db.relationship('Backlog', backref='user', lazy=True)
    user_platforms = db.relationship('Platform', backref='user', lazy=True)
    genres_liked = db.relationship('GenreLike', backref='user', lazy=True)
    genres_disliked = db.relationship('GenreDislike', backref='user', lazy=True)
    tags_liked = db.relationship('TagLike', backref='user', lazy=True)
    tags_disliked = db.relationship('TagDislike', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "user_games": list(map(lambda x: x.serialize(), self.user_games)),
            "user_platforms": list(map(lambda x: x.serialize(), self.user_platforms)),
            "genres_liked": list(map(lambda x: x.serialize(), self.genres_liked)),
            "genres_disliked": list(map(lambda x: x.serialize(), self.genres_disliked)),
            "tags_liked": list(map(lambda x: x.serialize(), self.tags_liked)),
            "tags_disliked": list(map(lambda x: x.serialize(), self.tags_disliked))
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

class Backlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(250), unique=False, nullable=True)
    game_id = db.Column(db.String(120), unique=False, nullable=True)
    game_image = db.Column(db.String(120), unique=False, nullable=True)
    game_status = db.Column(db.String(30), unique=False, nullable=True)

    def __repr__(self):
        return '<Backlog %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_name": self.game_name,
            "game_id": self.game_id,
            "game_image": self.game_image,
            "game_status": self.game_status
        }

class GenreLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genre_name = db.Column(db.String(50), unique=False, nullable=True)
    genre_id = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<GenreLike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "genre_name": self.genre_name,
            "genre_id": self.genre_id
        }

class GenreDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genre_name = db.Column(db.String(50), unique=False, nullable=True)
    genre_id = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<GenreDislike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "genre_name": self.genre_name,
            "genre_id": self.genre_id
        }

class TagLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_name = db.Column(db.String(50), unique=False, nullable=True)
    tag_id = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<TagLike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tag_name": self.tag_name,
            "tag_id": self.tag_id
        }

class TagDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_name = db.Column(db.String(50), unique=False, nullable=True)
    tag_id = db.Column(db.String(50), unique=False, nullable=True)

    def __repr__(self):
        return '<TagDislike %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tag_name": self.tag_name,
            "tag_id": self.tag_id       
        }