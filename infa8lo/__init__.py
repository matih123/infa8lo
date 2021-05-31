from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json

with open('config//file//path') as config_file:
	config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')

app.config['RECAPTCHA_USE_SSL'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = config.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = config.get('RECAPTCHA_PRIVATE_KEY')
app.config['RECAPTCHA_OPTIONS'] = {'theme':'black'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Zaloguj się aby zobaczyć tę stronę.'
login_manager.login_message_category = 'info'

# Try connecting to db, if failed create tables
from infa8lo.models import Config, Posts, Users, Links
from infa8lo.sha512 import Hash
try:
	Config.query.all()
except:
	db.create_all()
	logowanie = Config(option="logowanie", value="false")
	rejestracja = Config(option="rejestracja", value="false")
	todo = Config(option="todo", value="Nie ma nic do zrobienia.")
	test_post = Posts(title="Testowy post", content="Testowy post, utworzony automatycznie przy pierwszym uruchomieniu aplikacji. Można usunąć!")
	admin_user = Users(userid='admin8lo', passwd=Hash(config.get('DEFAULT_ADMIN_PASSWORD')).toStore, homedir='/srv/users', grade='brak')
	astrofiz = Links(name="astrofiz.pl", address="http://astrofiz.pl/")
	db.session.add(logowanie)
	db.session.add(rejestracja)
	db.session.add(todo)
	db.session.add(test_post)
	db.session.add(admin_user)
	db.session.add(astrofiz)
	db.session.commit()

# Startapp
from infa8lo import routes
