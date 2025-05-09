from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, HiddenField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class AddBookForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('Story', 'Story'), 
        ('Novel', 'Novel'),
        ('Anime', 'Anime/Manga'),
        ('Biography', 'Biography'),
        ('Motivational', 'Motivational'),
        ('History', 'History'),
        ('Educational', 'Educational')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Book')

class UpdateBookForm(FlaskForm):
    book_id = HiddenField('Book ID')
    title = StringField('Book Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('Story', 'Story'), 
        ('Novel', 'Novel'),
        ('Anime', 'Anime/Manga'),
        ('Biography', 'Biography'),
        ('Motivational', 'Motivational'),
        ('History', 'History'),
        ('Educational', 'Educational')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Update Book')

class DeleteBookForm(FlaskForm):
    book_id = HiddenField('Book ID', validators=[DataRequired()])
    submit = SubmitField('Delete Book')

class BorrowBookForm(FlaskForm):
    book_id = HiddenField('Book ID', validators=[DataRequired()])
    submit = SubmitField('Borrow Now')

class ReturnBookForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    book_title = StringField('Book Title', validators=[DataRequired()])
    return_date = DateField('Return Date', default=datetime.today, validators=[DataRequired()])
    remarks = StringField('Remarks (Optional)', validators=[Optional()])
    damage_report = TextAreaField('Damage Report (if any)', validators=[Optional()])
    submit = SubmitField('Submit Return')

class SearchBookForm(FlaskForm):
    search_term = StringField('Search', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('Story', 'Story'), 
        ('Novel', 'Novel'),
        ('Anime', 'Anime/Manga'),
        ('Biography', 'Biography'),
        ('Motivational', 'Motivational'),
        ('History', 'History'),
        ('Educational', 'Educational')
    ], validators=[Optional()])
    submit = SubmitField('Search')
