document.addEventListener('DOMContentLoaded', function() {
    // Toggle between login and register forms on index page
    const showRegisterFormBtn = document.getElementById('showRegisterForm');
    const showLoginFormBtn = document.getElementById('showLoginForm');
    
    if (showRegisterFormBtn && showLoginFormBtn) {
        showRegisterFormBtn.addEventListener('click', function() {
            document.querySelector('.login-container').style.display = 'none';
            document.querySelector('.register-container').style.display = 'block';
        });
        
        showLoginFormBtn.addEventListener('click', function() {
            document.querySelector('.login-container').style.display = 'block';
            document.querySelector('.register-container').style.display = 'none';
        });
    }
    
    // Admin book management - populate update form
    const updateButtons = document.querySelectorAll('.update-book-btn');
    
    if (updateButtons) {
        updateButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.getAttribute('data-id');
                
                // Fetch book details via API
                fetch(`/api/books/${bookId}`)
                    .then(response => response.json())
                    .then(book => {
                        // Populate update form
                        document.getElementById('update_book_id').value = book.id;
                        document.getElementById('update_title').value = book.title;
                        document.getElementById('update_author').value = book.author;
                        document.getElementById('update_category').value = book.category;
                        document.getElementById('update_quantity').value = book.quantity;
                        
                        // Show update form and hide add form
                        document.getElementById('updateBookForm').style.display = 'block';
                        document.getElementById('addBookForm').style.display = 'none';
                    })
                    .catch(error => {
                        console.error('Error fetching book details:', error);
                        alert('Error loading book details');
                    });
            });
        });
    }
    
    // Cancel update button
    const cancelUpdateBtn = document.getElementById('cancelUpdate');
    
    if (cancelUpdateBtn) {
        cancelUpdateBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('updateBookForm').style.display = 'none';
            document.getElementById('addBookForm').style.display = 'block';
        });
    }
    
    // Setup delete book confirmation
    const deleteButtons = document.querySelectorAll('.delete-book-btn');
    
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.getAttribute('data-id');
                const bookTitle = this.getAttribute('data-title');
                
                if (confirm(`Are you sure you want to delete "${bookTitle}"?`)) {
                    document.getElementById('delete_book_id').value = bookId;
                    document.getElementById('deleteBookForm').submit();
                }
            });
        });
    }
    
    // Setup borrow button functionality
    const borrowButtons = document.querySelectorAll('.borrow-book-btn');
    
    if (borrowButtons) {
        borrowButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.getAttribute('data-id');
                document.getElementById('borrow_book_id').value = bookId;
                document.getElementById('borrowBookForm').submit();
            });
        });
    }
});
