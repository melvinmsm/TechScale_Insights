from sqlalchemy import Integer, String, TEXT, DATETIME
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from datetime import datetime


# All models inherit this.
class Base(DeclarativeBase):
	# nothing to do here.
	pass


# This is imported into the main file.
db = SQLAlchemy(model_class=Base)


# Blog post needs author, title, body, date
class BlogPost(db.Model):
	__tablename__ = "blogpost"
	id = mapped_column(Integer, primary_key=True)
	title = mapped_column(String(100), nullable=False)
	content = mapped_column(TEXT, nullable=False)
	author = mapped_column(String(50), nullable=False)
	date_posted = mapped_column(DATETIME, default=datetime.utcnow)

	last_edit = db.Column(db.DateTime, nullable=True)
	
	def __init__(self, title, content, author):
		self.title = title
		self.content = content
		self.author = author
		self.date_posted = datetime.utcnow()
		self.last_edit = self.date_posted

	# This is a string rep of the object
	def __repr__(self):
		# just tell us about this post.
		return f"Post('Title: {self.title}', Date Posted: '{self.date_posted}', Author: '{self.author}')"
	
	def to_json(self):
		return {
			'id' : self.id,
			'title' : self.title,
			'content' : self.content,
			'author' : self.author,
			'date_posted' : self.date_posted,
			'last_edit' : self.last_edit
		}
