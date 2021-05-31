from datetime import datetime
from pytz import timezone
from infa8lo import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

def date_now():
	return datetime.now(timezone('Europe/Warsaw'))

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.String(20), unique=True, nullable=False)
	passwd = db.Column(db.String(128), nullable=False)
	uid = db.Column(db.Integer, nullable=False, default=5500)
	gid = db.Column(db.Integer, nullable=False, default=5500)
	homedir = db.Column(db.String(32), nullable=False)
	shell = db.Column(db.String(20), nullable=False, default="/bin/false")
	count = db.Column(db.Integer, nullable=False, default=0)
	accessed = db.Column(db.DateTime, nullable=False, default="1000-10-10 00:00:00")
	modified = db.Column(db.DateTime, nullable=False, default="1000-10-10 00:00:00")
	grade = db.Column(db.String(10), nullable=False, default="brak")

	def __repr__(self):
		return f"User('{self.userid}', '{self.grade}')"

class Groups(db.Model):
	groupname = db.Column(db.String(20), nullable=False, unique=True)
	gid = db.Column(db.Integer, primary_key=True)
	members = db.Column(db.String(256), nullable=False, default="")

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	created = db.Column(db.DateTime, nullable=False, default=date_now)
	title = db.Column(db.String(64), nullable=False, default="Tytuł")
	content = db.Column(db.String(1024), nullable=False, default="Tekst ...")

	def __repr__(self):
		return f"Post('{self.title}', '{self.created}')"

class Grades(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	grade = db.Column(db.String(10), nullable=False, unique=True)

class Config(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	option = db.Column(db.String(32), nullable=False, unique=True)
	value = db.Column(db.String(1024), nullable=False)

class Links(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32), nullable=False, unique=True)
	address = db.Column(db.String(64), nullable=False)
