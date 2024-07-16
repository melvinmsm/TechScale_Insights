
from ast import arg
from flask import jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DATETIME, true


# All models inherit this.
class Base(DeclarativeBase):
	# nothing to do here.
	pass


# This is imported into the main file.
db = SQLAlchemy(model_class=Base)


# User Model - password handeled in auth model.
class User(db.Model):
	__tablename__ = "user_info"
	id = mapped_column(Integer, primary_key=True)
	email_address = mapped_column(String(100), nullable=False, unique=True)
	user_name = mapped_column(String(100), nullable=False, unique=True)
	password = mapped_column(String(255), nullable=False)
	first_name = mapped_column(String(100), nullable=True)
	last_name = mapped_column(String(100), nullable=True)
	token = mapped_column(String(255), nullable=True)
	date_created = mapped_column(DATETIME, default=datetime.utcnow)

	def __init__( self, arg_dic ):
		self.email_address = arg_dic['email']
		self.user_name = arg_dic['username']
		self.password = arg_dic['password']
		self.first_name = arg_dic['first_name']
		self.last_name = arg_dic['last_name']
		# Managed by class
		self.date_created = datetime.utcnow()

	# This is a string rep of the object
	def __repr__(self):
		# just tell us about this post.
		return f"User( 'ID: {self.id}', 'Email Adress: { self.email_address }', 'First Name: { self.first_name }', 'Last Name: { self.last_name }', )"

	def check_password(self, pword):
		print("Checking Password....")
		return check_password_hash(self.password, pword)

    # Package it up for shipping
	def serialize(self):
		return {
			'id' : self.id,
			'username' : self.user_name,
			'email' : self.email_address,
			'first' : self.first_name,
			'last' : self.last_name,
			'created' : self.date_created,
		}
