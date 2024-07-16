from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String, Boolean
from werkzeug.security import check_password_hash



# All models inherit this.
class Base(DeclarativeBase):
	# nothing to do here.
	pass


# This is imported into the main file.
db = SQLAlchemy(model_class=Base)


# User Model 
class User(db.Model):
    __tablename__ = "user_permissions"
    email = mapped_column(String(100), primary_key=True, nullable=False, unique=True)
    password = mapped_column(String(255), nullable=False)
    is_admin = mapped_column(Boolean, nullable=False)

    def __init__( self, arg_dic ):
        self.email= arg_dic['email']
        self.password = arg_dic['password']
        self.is_admin = arg_dic['is_admin']

    # This is a string rep of the object
    def __repr__(self):
        # just tell us about this post.
        return f"User('Email Adress: { self.email }', 'is Admin { self.is_admin }', )"
    
    def check_password(self, pword):
        print("Checking Password....")
        return check_password_hash(self.password, pword)

    # Package it up for shipping
    def to_json(self):
        return jsonify({
            'email' : self.email,
            'is_admin': self.is_admin
        })


