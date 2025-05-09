import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_

from app import app, db
from models import User, Book, BorrowedBook
from forms import (LoginForm, RegisterForm, AddBookForm, UpdateBookForm, 
                  DeleteBookForm, BorrowBookForm, ReturnBookForm, SearchBookForm)

logger = logging.getLogger(__name__)

# Home page - Login/Register
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    login_form = LoginForm()
    register_form = RegisterForm()
    
    if login_form.validate_on_submit() and 'login' in request.form:
        username = login_form.username.data
        password = login_form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    if register_form.validate_on_submit() and 'register' in request.form:
        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
        else:
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
    
    return render_template('index.html', login_form=login_form, register_form=register_form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for the dashboard
    total_books = Book.query.count()
    available_books = sum([book.available_quantity for book in Book.query.all()])
    borrowed_count = BorrowedBook.query.filter_by(user_id=current_user.id, is_returned=False).count()
    overdue_count = 0
    
    # Check for overdue books
    borrowed_books = BorrowedBook.query.filter_by(user_id=current_user.id, is_returned=False).all()
    for book in borrowed_books:
        if book.is_overdue():
            overdue_count += 1
    
    # Get recent activity (last 5 transactions)
    recent_activity = BorrowedBook.query.order_by(BorrowedBook.borrow_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          total_books=total_books,
                          available_books=available_books,
                          borrowed_count=borrowed_count,
                          overdue_count=overdue_count,
                          recent_activity=recent_activity,
                          is_admin=current_user.is_admin)

# Available Books
@app.route('/available_books', methods=['GET', 'POST'])
@login_required
def available_books():
    search_form = SearchBookForm()
    query = Book.query.filter(Book.available_quantity > 0)
    
    if search_form.validate_on_submit():
        # Handle search
        search_term = search_form.search_term.data
        category = search_form.category.data
        
        if search_term:
            query = query.filter(or_(
                Book.title.ilike(f'%{search_term}%'),
                Book.author.ilike(f'%{search_term}%')
            ))
        
        if category:
            query = query.filter_by(category=category)
    
    books = query.all()
    return render_template('available_books.html', books=books, search_form=search_form)

# Borrow Books
@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow_books():
    search_form = SearchBookForm()
    borrow_form = BorrowBookForm()
    query = Book.query.filter(Book.available_quantity > 0)
    
    if search_form.validate_on_submit():
        # Handle search
        search_term = search_form.search_term.data
        category = search_form.category.data
        
        if search_term:
            query = query.filter(or_(
                Book.title.ilike(f'%{search_term}%'),
                Book.author.ilike(f'%{search_term}%')
            ))
        
        if category:
            query = query.filter_by(category=category)
    
    books = query.all()
    
    if borrow_form.validate_on_submit():
        book_id = borrow_form.book_id.data
        book = Book.query.get_or_404(book_id)
        
        # Check if book is available
        if book.available_quantity <= 0:
            flash('Sorry, this book is not available for borrowing', 'danger')
            return redirect(url_for('borrow_books'))
        
        # Check if user already has this book
        existing_borrow = BorrowedBook.query.filter_by(
            user_id=current_user.id, 
            book_id=book_id,
            is_returned=False
        ).first()
        
        if existing_borrow:
            flash('You have already borrowed this book and not returned it yet', 'warning')
            return redirect(url_for('borrow_books'))
        
        # Create borrowed book record
        borrowed_book = BorrowedBook(
            user_id=current_user.id,
            book_id=book_id
        )
        
        # Update book available quantity
        book.available_quantity -= 1
        
        db.session.add(borrowed_book)
        db.session.commit()
        
        flash(f'Successfully borrowed: {book.title}', 'success')
        return redirect(url_for('borrowed_history'))
    
    return render_template('borrow.html', books=books, search_form=search_form, borrow_form=borrow_form)

# Return Books
@app.route('/return', methods=['GET', 'POST'])
@login_required
def return_book():
    form = ReturnBookForm()
    
    if form.validate_on_submit():
        username = form.username.data
        book_title = form.book_title.data
        return_date = form.return_date.data
        remarks = form.remarks.data
        damage_report = form.damage_report.data
        
        # First verify the user exists
        user = User.query.filter_by(username=username).first()
        if not user:
            flash(f'User {username} not found', 'danger')
            return redirect(url_for('return_book'))
        
        # Find the book by title
        book = Book.query.filter(Book.title.ilike(f'%{book_title}%')).first()
        if not book:
            flash(f'Book "{book_title}" not found', 'danger')
            return redirect(url_for('return_book'))
        
        # Check if this book was borrowed by the user
        borrowed_record = BorrowedBook.query.filter_by(
            user_id=user.id,
            book_id=book.id,
            is_returned=False
        ).first()
        
        if not borrowed_record:
            flash(f'No borrowed record found for {username} and book "{book_title}"', 'danger')
            return redirect(url_for('return_book'))
        
        # Update the borrowed record
        borrowed_record.is_returned = True
        borrowed_record.return_date = return_date
        borrowed_record.remarks = remarks
        borrowed_record.damage_report = damage_report
        
        # Calculate and update fine if applicable
        borrowed_record.update_fine()
        
        # Update book availability
        book.available_quantity += 1
        
        db.session.commit()
        
        # Show success message with fine information
        if borrowed_record.fine_amount > 0:
            flash(f'Book returned successfully. A fine of ${borrowed_record.fine_amount:.2f} has been applied due to late return.', 'warning')
        else:
            flash('Book returned successfully!', 'success')
        
        return redirect(url_for('borrowed_history'))
    
    return render_template('return.html', form=form)

# Borrowed History
@app.route('/borrowed_history')
@login_required
def borrowed_history():
    # For admin, show all records if requested
    show_all = request.args.get('show_all', False) and current_user.is_admin
    
    if show_all:
        borrowed_books = BorrowedBook.query.order_by(BorrowedBook.borrow_date.desc()).all()
    else:
        borrowed_books = BorrowedBook.query.filter_by(user_id=current_user.id).order_by(BorrowedBook.borrow_date.desc()).all()
    
    return render_template('borrowed_history.html', borrowed_books=borrowed_books, show_all=show_all)

# Admin Books Management
@app.route('/admin/books', methods=['GET', 'POST'])
@login_required
def admin_books():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    add_form = AddBookForm()
    update_form = UpdateBookForm()
    delete_form = DeleteBookForm()
    search_form = SearchBookForm()
    
    # Handle search
    query = Book.query
    if search_form.validate_on_submit():
        search_term = search_form.search_term.data
        category = search_form.category.data
        
        if search_term:
            query = query.filter(or_(
                Book.title.ilike(f'%{search_term}%'),
                Book.author.ilike(f'%{search_term}%')
            ))
        
        if category:
            query = query.filter_by(category=category)
    
    books = query.all()
    
    # Handle add book form
    if add_form.validate_on_submit() and 'add' in request.form:
        new_book = Book(
            title=add_form.title.data,
            author=add_form.author.data,
            category=add_form.category.data,
            quantity=add_form.quantity.data,
            available_quantity=add_form.quantity.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f'Book "{new_book.title}" added successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    # Handle update book form
    if update_form.validate_on_submit() and 'update' in request.form:
        book_id = update_form.book_id.data
        book = Book.query.get_or_404(book_id)
        
        # Calculate the change in available copies based on quantity change
        quantity_diff = update_form.quantity.data - book.quantity
        
        # Update the book
        book.title = update_form.title.data
        book.author = update_form.author.data
        book.category = update_form.category.data
        book.quantity = update_form.quantity.data
        book.available_quantity = max(0, book.available_quantity + quantity_diff)
        
        db.session.commit()
        flash(f'Book "{book.title}" updated successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    # Handle delete book form
    if delete_form.validate_on_submit() and 'delete' in request.form:
        book_id = delete_form.book_id.data
        book = Book.query.get_or_404(book_id)
        
        # Check if any copies are currently borrowed
        borrowed_count = BorrowedBook.query.filter_by(book_id=book_id, is_returned=False).count()
        
        if borrowed_count > 0:
            flash(f'Cannot delete book "{book.title}" as {borrowed_count} copies are currently borrowed', 'danger')
        else:
            db.session.delete(book)
            db.session.commit()
            flash(f'Book "{book.title}" deleted successfully!', 'success')
        
        return redirect(url_for('admin_books'))
    
    return render_template('admin_books.html', 
                          add_form=add_form, 
                          update_form=update_form,
                          delete_form=delete_form,
                          search_form=search_form,
                          books=books)

# API endpoint to get book details for update
@app.route('/api/books/<int:book_id>', methods=['GET'])
@login_required
def get_book_details(book_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'category': book.category,
        'quantity': book.quantity
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message="Server error"), 500
