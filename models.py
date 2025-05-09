from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with borrowed books
    borrowed_books = db.relationship('BorrowedBook', backref='borrower', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with borrowed books
    borrowed_records = db.relationship('BorrowedBook', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)
    fine_amount = db.Column(db.Float, default=0.0)
    damage_report = db.Column(db.Text, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

    def __init__(self, user_id, book_id, days=14, **kwargs):
        super(BorrowedBook, self).__init__(user_id=user_id, book_id=book_id, **kwargs)
        self.due_date = datetime.utcnow() + timedelta(days=days)
    
    def calculate_fine(self):
        """Calculate fine if book is returned late"""
        if not self.is_returned:
            return 0.0
        
        # Convert return_date to datetime if it's a date object
        from datetime import datetime
        return_date = self.return_date
        if not isinstance(return_date, datetime):
            # Convert date to datetime for proper comparison
            return_date = datetime.combine(return_date, datetime.min.time())
        
        if return_date > self.due_date:
            # Calculate days overdue
            days_overdue = (return_date - self.due_date).days
            # Fine rate: $1 per day
            fine_amount = days_overdue * 1.0
            return fine_amount
        return 0.0
    
    def update_fine(self):
        """Update the fine amount based on return date"""
        self.fine_amount = self.calculate_fine()
    
    def is_overdue(self):
        """Check if the book is overdue"""
        if not self.is_returned and datetime.utcnow() > self.due_date:
            return True
        return False
        
    def __repr__(self):
        status = "Returned" if self.is_returned else "Borrowed"
        return f'<BorrowedBook {self.book_id} by User {self.user_id} - {status}>'
