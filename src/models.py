from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    profile_avatar = db.Column(db.String(250), unique=False, nullable=False)
    joined = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "username": self.username,
            "profile_avatar": self.profile_avatar,
            "joined": self.joined,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

class NowPlaying(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.String(250), unique=True, nullable=False)
    game_name = db.Column(db.String(250), unique=True, nullable=False)
    comment = db.Column(db.String(250), unique=False, nullable=False)

    def __repr__(self):
        return '<NowPlaying %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "game_name": self.game_name,
            "comment": self.comment
        }
