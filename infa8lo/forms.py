from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError, Email
from wtforms.fields.html5 import EmailField
from infa8lo.models import Users, Grades, Links
from infa8lo.sha512 import Hash
from infa8lo.folder import Folder
from flask_login import current_user
import os

class LoginForm(FlaskForm):
	username = StringField('Nazwa użytkownika', validators=[DataRequired()])
	password = PasswordField('Hasło', validators=[DataRequired()])
	remember = BooleanField('Zapamiętaj mnie')
	submit = SubmitField('Zaloguj się')

class RegisterForm(FlaskForm):

	try:
		grades_query = Grades.query.all()
	except:
		grades_query = []
	grades_all = []
	for x in grades_query:
		grades_all.append(x.grade)
	grades_all.sort()
	grades_all.insert(0, "brak")
	grades_tuples = []
	for x in grades_all:
		if not os.path.exists(f'/srv/users/{x}'):
			try:
				Folder.create(f'/srv/users/{x}', 33, 33, 0o755)
			except:
				pass

		grades_tuples.append((x,x))

	username = StringField('Nazwa użytkownika', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=15, message="Min = 3 znaki, Max = 15 znaków."), 
										Regexp('^[a-zA-Z0-9]*$', message="Dozwolone tylko litery i cyfry.")])

	grade = SelectField('Klasa', choices=grades_tuples, validators=[
										DataRequired(message="Pole wymagane.")])

	password = PasswordField('Hasło', validators=[
										DataRequired(message="Pole wymagane.")])

	confirm_password = PasswordField('Powtórz hasło', validators=[
										DataRequired(message="Pole wymagane."), 
										EqualTo('password', message="Hasła nie są identyczne.")])

	submit = SubmitField('Zarejestruj się')

	def validate_username(self, username):
		user = Users.query.filter_by(userid=username.data).first()
		if user:
			raise ValidationError('Nazwa użytkownika jest zajęta.')

class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('Obecne hasło', validators=[
										DataRequired(message="Pole wymagane.")])
	password = PasswordField('Nowe hasło', validators=[
										DataRequired(message="Pole wymagane.")])
	confirm_password = PasswordField('Powtórz hasło', validators=[
										DataRequired(message="Pole wymagane."), 
										EqualTo('password', message="Hasła nie są identyczne.")])
	submit = SubmitField('Zmień hasło')

	def validate_old_password(self, old_password):
		user = Users.query.filter_by(userid=current_user.userid).first()
		if user.passwd != Hash(old_password.data).toStore:
			raise ValidationError('Podano błędne stare hasło.')

class AddPostForm(FlaskForm):
	title = StringField('Tytuł', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=64, message="Min = 3 znaki, Max = 64 znaki.")])
	content = TextAreaField('Treść', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=1024, message="Min = 3 znaki, Max = 1024 znaki.")])
	post_submit = SubmitField('Zamieść post')

class AddLinkForm(FlaskForm):
	name = StringField('Nazwa', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=32, message="Min = 3 znaki, Max = 32 znaki.")])
	address = StringField('Adres', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=64, message="Min = 3 znaki, Max = 64 znaki.")])
	link_submit = SubmitField('Dodaj link')

	def validate_name(self, name):
		link = Links.query.filter_by(name=name.data).first()
		if link:
			raise ValidationError('Podany link już istnieje.')

class ChangeConfigForm(FlaskForm):
	login = BooleanField('Logowanie')
	register = BooleanField('Rejestracja')
	config_submit = SubmitField('Zapisz zmiany')

class ChangeTodoForm(FlaskForm):
	todo_content = TextAreaField('Do zrobienia', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=1024, message="Min = 3 znaki, Max = 1024 znaki.")])
	todo_submit = SubmitField('Zapisz zmiany')

class ResetPasswordForm(FlaskForm):
	username = StringField('Nazwa użytkownika', validators=[DataRequired(message="Pole wymagane.")])
	password_submit = SubmitField('Resetuj hasło')

	def validate_username(self, username):
		if username.data == "admin8lo":
			raise ValidationError('Nie można zresetować hasła administratorowi.')

		user = Users.query.filter_by(userid=username.data).first()
		if not user:
			raise ValidationError('Nie ma takiego użytkownika.')

class SendEmailForm(FlaskForm):
	mail_from = EmailField('Twój adres email', validators=[
										DataRequired(message="Pole wymagane."), 
										Email(message="Podaj poprawny adres email.")])
	mail_title = StringField('Tytuł wiadomości', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=256, message="Min = 3 znaki, Max = 256 znaków.")])
	mail_content = TextAreaField('Treść wiadomości', validators=[
										DataRequired(message="Pole wymagane."), 
										Length(min=3, max=1024, message="Min = 3 znaki, Max = 1024 znaki.")])
	mail_recaptcha = RecaptchaField()
	mail_submit = SubmitField('Wyślij')

class CreateDatabaseForm(FlaskForm):
	db_password = PasswordField('Nowe hasło do bazy danych', validators=[
										DataRequired(message="Pole wymagane.")])
	db_confirm_password = PasswordField('Powtórz hasło do bazy danych', validators=[
										DataRequired(message="Pole wymagane."), 
										EqualTo('db_password', message="Hasła nie są identyczne.")])
	db_submit = SubmitField('Utwórz bazę danych')