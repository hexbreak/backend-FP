from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    backlogs = db.relationship('Backlog', backref='user', lazy=True)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    profile_avatar = db.Column(db.String(250), unique=False, nullable=False)
    joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "backlogs": list(map(lambda x: x.serialize(), self.backlogs)),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "username": self.username,
            "profile_avatar": self.profile_avatar,
            "joined": self.joined,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

class ProgressionStatus(enum.Enum):
    NEW = 1
    PROGRESSING = 2
    FINISHED = 3
    COMPLETED = 4

class Backlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.String(250), unique=True, nullable=False)
    game_name = db.Column(db.String(250), unique=True, nullable=False)
    game_platform = db.Column(db.String(250), unique=True, nullable=False)
    game_notes = db.Column(db.String(500), unique=False, default=False, nullable=False)
    progress_status = db.Column(db.Enum(ProgressionStatus))

    def __repr__(self):
        return '<Backlog %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "game_name": self.game_name,
            "game_platform": self.game_platform,
            "game_notes": self.game_notes,
            "progress_status": self.progress_status # Must convert to JSON in order to avoid any crashes with the GET method.
        }

class NowPlaying(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_backlog_id = db.Column(db.Integer, db.ForeignKey('backlog.id'), nullable=False)
    game_id = db.Column(db.String(250), unique=True, nullable=False)
    game_name = db.Column(db.String(250), unique=True, nullable=False)
    comment = db.Column(db.String(250), unique=False, nullable=False)

    def __repr__(self):
        return '<NowPlaying %r>' % self.game_name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "game_name": self.game_name,
            "comment": self.comment
        }

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_backlog_id = db.Column(db.Integer, db.ForeignKey('backlog.id'), nullable=False)
    game_id = db.Column(db.String(250), unique=True, nullable=False)
    game_genre = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.game_genre

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "game_genre": self.game_genre
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.String(250), unique=True, nullable=False)
    game_name = db.Column(db.String(250), unique=True, nullable=False)
    list_name = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return '<Favorites %r>' % self.game_name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "game_name": self.game_name
        }

class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    about_box = db.Column(db.String(500), unique=False, nullable=False)

    def __repr__(self):
        return '<AboutMe %r>' % self.about_box

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "about_box": self.about_box
        }