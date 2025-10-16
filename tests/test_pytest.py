import pytest
import sqlite3
import os
from datetime import datetime, timedelta

from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)

from database import init_database, add_sample_data


"Test for R1"
class TestAddBookToCatalog:
    
    def test_correct(self):
        success, message = add_book_to_catalog("A", "A", "1234567890123", 2)
        assert success == True
        assert "successfully added" in message.lower()
    
    def test_emptytitle(self):
        success, message = add_book_to_catalog("", "B", "1234567890123", 2)
        assert success == False
        assert "Title is required" in message

    def test_noauthor(self):
        success, message = add_book_to_catalog("D", "", "1234567890123", 2)
        assert success == False
        assert "Author is required" in message

    def test_titletoolong(self):
        long_title = "A" * 201 
        success, message = add_book_to_catalog(long_title, "E", "1234567890123", 2)
        assert success == False
        assert "Title must be less than 200 characters." in message

    def test_authortoolong(self):
        long_author = "A" * 101  # 101 characters
        success, message = add_book_to_catalog("E", long_author, "1234567890123", 2)
        assert success == False
        assert "Author must be less than 100 characters." in message

    def test_isbntooshort(self):
        success, message = add_book_to_catalog("E", "E", "123456789", 2)
        assert success == False
        assert "13 digits" in message

    def test_isbntoolong(self):
        success, message = add_book_to_catalog("E", "E", "12345678901234", 2)
        assert success == False
        assert "13 digits" in message

    def test_isbnalphabet(self):
        success, message = add_book_to_catalog("E", "E", "123456789012A", 2)
        assert success == False
        assert "13 digits" in message

    def test_zerocopies(self):
        success, message = add_book_to_catalog("E", "E", "1234567890123", 0)
        assert success == False
        assert "Total copies must be a positive integer." in message

    def test_isbnduplicate(self):
        success, message = add_book_to_catalog("E", "E", "9780451524935", 2)
        assert success == False
        assert "A book with this ISBN already exists." in message


"Test for R3"
class TestBorrowBookByPatron:

    def test_book_correct(self):
        expected_due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        success, message = borrow_book_by_patron("123456", 1)
    
        assert success == True
        assert f'Successfully borrowed "The Great Gatsby". Due date: {expected_due_date}.' in message

    def test_book_idshort(self):
        success, message = borrow_book_by_patron("12345", 1)
        assert success == False
        assert "Invalid patron ID. Must be exactly 6 digits." in message

    def test_book_idlong(self):
        success, message = borrow_book_by_patron("1234567", 1)
        assert success == False
        assert "Invalid patron ID. Must be exactly 6 digits." in message

    def test_book_idalphabet(self):
        success, message = borrow_book_by_patron("12345A", 1)
        assert success == False
        assert "Invalid patron ID. Must be exactly 6 digits." in message

    def test_book_fake(self):
        success, message = borrow_book_by_patron("123456", 99999)
        assert success == False
        assert "Book not found." in message

    def test_book_notavailable(self):
        success, message = borrow_book_by_patron("123456", 3)
        assert success == False
        assert "This book is not available." in message

    def test_book_limit(self):
        add_book_to_catalog("E", "E", "1234567890123", 2)
        for book_id in range(5):
            borrow_book_by_patron("123456", 4)
        
        success, message = borrow_book_by_patron("123456", 2)
        assert success == False
        assert "You have reached the borrowing limit of 5 books." in message



"Test for R4"
class TestReturnBookByPatron:
    def test_return_book_not_implemented(self):
        success, message = return_book_by_patron("123456", 1)
        assert success == False
        assert "Book return functionality is not yet implemented." in message

"Test for R6"
class TestCalculateLateFeeForBook:
    def test_calculate_late_fee_not_implemented(self):
        result = calculate_late_fee_for_book("123456", 1)
        assert isinstance(result, dict)
        assert result == {}

"Test for R6"
class TestSearchBooksInCatalog:
    def test_search_by_title_not_implemented(self):
        results = search_books_in_catalog("Python", "title")
        assert isinstance(results, list)
        assert results == []
        
"Test for R7"
class TestGetPatronStatusReport:
    def test_patron_status_not_implemented(self):
        report = get_patron_status_report("123456")
        assert isinstance(report, dict)
        assert report == {}
