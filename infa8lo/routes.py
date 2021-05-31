from flask import render_template, url_for, flash, redirect, request, abort
from infa8lo.models import Users, Groups, Posts, Grades, Config, Links, load_user
from infa8lo.forms import LoginForm, RegisterForm, ChangePasswordForm, AddPostForm, AddLinkForm, ChangeConfigForm, ChangeTodoForm, ResetPasswordForm, SendEmailForm, CreateDatabaseForm
from infa8lo.sha512 import Hash
from infa8lo.folder import Folder
from infa8lo.email import Email
from infa8lo import app, db
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
import subprocess
import random
import string
import os

################
##### HOME #####
################
@app.route("/", methods=['GET', 'POST'])
def home():
	page = request.args.get('strona', 1, type=int)
	try:
		posts = Posts.query.order_by(Posts.created.desc()).paginate(page=page, per_page=5)
		links = Links.query.all()
	except:
		posts = []
		links = []

	# If logged as admin
	if current_user.is_authenticated:
		if current_user.userid == "admin8lo":
			post_form = AddPostForm()
			config_form = ChangeConfigForm()
			password_form = ResetPasswordForm()
			todo_form = ChangeTodoForm()
			link_form = AddLinkForm()

			if post_form.post_submit.data and post_form.validate_on_submit():
				post_form = Posts(title=post_form.title.data, content=post_form.content.data)
				db.session.add(post_form)
				db.session.commit()
				flash('Dodano post.', 'success')
				return redirect(url_for('home'))

			if config_form.config_submit.data and config_form.validate_on_submit():
				Config.query.filter_by(option="logowanie").first().value = "true" if config_form.login.data else "false"
				Config.query.filter_by(option="rejestracja").first().value = "true" if config_form.register.data else "false"
				db.session.commit()
				flash('Edytowano ustawienia.', 'success')
				return redirect(url_for('home'))
			else:
				config_form.login.data = True if Config.query.filter_by(option="logowanie").first().value == "true" else False
				config_form.register.data = True if Config.query.filter_by(option="rejestracja").first().value == "true" else False

			if password_form.password_submit.data and password_form.validate_on_submit():
				username = password_form.username.data
				password = ''
				chars = list(string.ascii_uppercase) + ['1','2','3','4','5','6','7','8','9','0']
				for i in range(6):
					password+=str(random.choice(chars))

				user = Users.query.filter_by(userid=username).first()
				user.passwd = Hash(password).toStore
				db.session.commit()

				flash(f'Zresetowano hasło użytkownika {username}. Nowe hasło: {password}', 'success')
				return redirect(url_for('home'))

			if todo_form.todo_submit.data and todo_form.validate_on_submit():
				Config.query.filter_by(option="todo").first().value = todo_form.todo_content.data
				db.session.commit()

				flash(f'Zapisano do zrobienia.', 'success')
				return redirect(url_for('home'))
			else:
				todo_form.todo_content.data = Config.query.filter_by(option="todo").first().value

			if link_form.link_submit.data and link_form.validate_on_submit():
				link_form = Links(name=link_form.name.data, address=link_form.address.data)
				db.session.add(link_form)
				db.session.commit()
				flash('Dodano link.', 'success')
				return redirect(url_for('home'))

			return render_template("admin.html", posts=posts, links=links, post_form=post_form, config_form=config_form, password_form=password_form, todo_form=todo_form, link_form=link_form)

	return render_template("home.html", posts=posts, links=links)

###################
##### KONTAKT #####
###################
@app.route("/kontakt", methods=['GET', 'POST'])
def contact():

	form = SendEmailForm()
	if form.validate_on_submit():
		flash('Email został wysłany.', 'success')

		email = Email(sender="a@infa8lo.pl", password="", server="mail.infa8lo.pl", author_email=form.mail_from.data, author_domain="infa8lo.pl")
		email.send(receiver="illbeback@onet.pl", subject=form.mail_title.data, text=form.mail_content.data)

		return redirect(url_for('contact'))

	return render_template("contact.html", form=form)

#####################
##### LOGOWANIE #####
#####################
@app.route("/logowanie", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	# Check canLogin option in config
	try:
		canLogin = Config.query.filter_by(option="logowanie").first().value
	except:
		canLogin = "false"
	if canLogin != "true":
		flash('Logowanie obecnie jest wyłączone.', 'danger')
		return redirect(url_for('home'))

	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(userid=form.username.data).first()
		
		if user and (Hash(form.password.data).toStore == user.passwd):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'Zalogowano jako {form.username.data}.', 'success')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		
		else:
			flash('Błędny login lub hasło.', 'danger')
	return render_template("login.html", form=form)

#######################
##### REJESTRACJA #####
#######################
@app.route("/rejestracja", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	# Check canRegister option in config
	try:
		canRegister = Config.query.filter_by(option="rejestracja").first().value
	except:
		canRegister = "false"
	if canRegister != "true":
		flash('Rejestracja obecnie jest wyłączona.', 'danger')
		return redirect(url_for('home'))

	form = RegisterForm()
	if form.validate_on_submit() and canRegister == "true":

		username = form.username.data
		grade = form.grade.data
		grades_query = Grades.query.all()
		grades_all = []
		for x in grades_query:
			grades_all.append(x.grade)
		if grade not in grades_all:
			grade = 'brak'

		hashedPassword = Hash(form.password.data).toStore
		homeDirectory = f'/srv/users/{grade}/{username}'
		new_user = Users(userid=username, passwd=hashedPassword, homedir=homeDirectory, grade=grade)
		db.session.add(new_user)
		db.session.commit()

		try:
			Folder.create(homeDirectory, 5500, 5500, 0o777)
			Folder.create(f"{homeDirectory}/Lekcje", 5500, 5500, 0o755)
			Folder.create(f"{homeDirectory}/Zadania", 5500, 5500, 0o755)

			with open(f"{homeDirectory}/index.html", 'w') as f:
				f.write('Pusta strona użytkownika. Wgraj pliki przez ftp!')
			os.chmod(f"{homeDirectory}/index.html", 0o777)
		except:
			pass

		flash(f'Konto dla {form.username.data} zostało utworzone. Proszę się zalogować.', 'success')
		return redirect(url_for('login'))
	return render_template("register.html", form=form)

###################
##### WYLOGUJ #####
###################
@app.route("/wyloguj")
def logout():
	logout_user()
	flash('Wylogowano.', 'info')
	return redirect(url_for('home'))

#################
##### KONTO #####
#################
@app.route("/konto", methods=['GET', 'POST'])
@login_required
def account():

	pass_form = ChangePasswordForm()
	createdb_form = CreateDatabaseForm()

	# Check if user has database
	engine = create_engine(f'{app.config["SQLALCHEMY_DATABASE_URI"][:-8]}baza_{current_user.userid}')
	if not database_exists(engine.url):
		user_has_db = False
	else:
		user_has_db = True

	if pass_form.submit.data and pass_form.validate_on_submit():

		user = Users.query.filter_by(userid=current_user.userid).first()
		user.passwd = Hash(form.password.data).toStore
		db.session.commit()

		flash(f'Hasło dla {current_user.userid} zostało zmienione. Proszę się zalogować przy użyciu nowego hasła.', 'success')
		logout_user()
		return redirect(url_for('login'))

	if createdb_form.db_submit.data and createdb_form.validate_on_submit():

		if not user_has_db:
			create_database(engine.url)
			sql = text(f'CREATE USER "{current_user.userid}"@"localhost" IDENTIFIED BY "{createdb_form.db_password.data}";')
			result = db.engine.execute(sql)
			sql = text(f'GRANT ALL PRIVILEGES ON baza_{current_user.userid}.* TO "{current_user.userid}"@"localhost";')
			result = db.engine.execute(sql)

			flash(f'Utworzono bazę danych i użytkownika.', 'success')

		else:
			flash(f'Baza danych już istnieje.', 'danger')

		return redirect(url_for('account'))

	return render_template("account.html", pass_form=pass_form, createdb_form=createdb_form, user_has_db=user_has_db)

#####################
##### USUN POST #####
#####################
@app.route("/usun-post/<int:post_id>", methods=['POST'])
def delete_post(post_id):

	if current_user.is_authenticated:
		if current_user.userid == "admin8lo":
			post = Posts.query.get_or_404(post_id)
			db.session.delete(post)
			db.session.commit()
			flash('Usunięto post.', 'success')
			return redirect(url_for('home'))
	abort(403)

#####################
##### USUN LINK #####
#####################
@app.route("/usun-link/<int:link_id>", methods=['POST'])
def delete_link(link_id):

	if current_user.is_authenticated:
		if current_user.userid == "admin8lo":
			link = Links.query.get_or_404(link_id)
			db.session.delete(link)
			db.session.commit()
			flash('Usunięto link.', 'success')
			return redirect(url_for('home'))
	abort(403)

###########################
##### RESTART APACHE2 #####
###########################
@app.route("/restart-apache", methods=['GET'])
def restart_apache():

	if current_user.is_authenticated:
		if current_user.userid == "admin8lo":

			try:
				subprocess.Popen(["sudo", "/etc/init.d/apache2", "restart"])
				return 0

			except:
				flash('Nie udało się zrestartować apache.', 'danger')
				return redirect(url_for('home'))

	abort(403)