import os
import logging
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bookbank.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Imports below to avoid circular imports
from models import User, Book, BorrowedBook
from forms import LoginForm, RegisterForm, AddBookForm, ReturnBookForm, BorrowBookForm

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Import routes after app is created
from routes import *

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@bookbank.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created")
    
    # Add some sample books if they don't exist
    if Book.query.count() == 0:
        sample_books = [
            Book(title="The Great Gatsby", author="F. Scott Fitzgerald", category="Novel", quantity=5, available_quantity=5),
            Book(title="To Kill a Mockingbird", author="Harper Lee", category="Novel", quantity=3, available_quantity=3),
            Book(title="1984", author="George Orwell", category="Novel", quantity=4, available_quantity=4),
            Book(title="The Hobbit", author="J.R.R. Tolkien", category="Story", quantity=2, available_quantity=2),
            Book(title="Naruto Vol. 1", author="Masashi Kishimoto", category="Anime", quantity=3, available_quantity=3),
            Book(title="Sapiens: A Brief History of Humankind", author="Yuval Noah Harari", category="History", quantity=2, available_quantity=2)
        ]
        db.session.add_all(sample_books)
        db.session.commit()
        logger.info("Sample books created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
