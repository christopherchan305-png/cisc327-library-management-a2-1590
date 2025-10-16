import os
from datetime import date, timedelta, datetime
import sqlite3
import library_service as svc
from database import (
    init_database, add_sample_data, insert_book, insert_borrow_record,
    update_book_availability, get_db_connection, get_book_by_id,
    get_patron_borrowed_books, update_borrow_record_return_date, get_all_books
)

def _fresh_db(tmp_path):
    os.chdir(tmp_path)
    init_database()

def test_return_no_active_borrow(tmp_path):
    _fresh_db(tmp_path)
    ok = insert_book("X", "A", "1234567890123", 1, 1)
    assert ok

    ok, msg, fee = svc.return_book_by_patron("123456", 1)
    assert not ok and "No active borrow" in msg and fee == 0.0


def test_return_on_time_no_fee(tmp_path):
    _fresh_db(tmp_path)
    insert_book("Clean Code", "Martin", "1234567890123", 1, 1)
    borrow_date = date.today() - timedelta(days=14)
    due_date = date.today()
    insert_borrow_record("123456", 1, borrow_date, due_date)
    update_book_availability(1, -1)

    ok, msg, fee = svc.return_book_by_patron("123456", 1)
    assert ok and fee == 0.0
    b = get_book_by_id(1)
    assert b["available_copies"] == 1 


def test_return_late_with_fee(tmp_path):
    _fresh_db(tmp_path)
    insert_book("Pragmatic Programmer", "Hunt", "1234567890123", 1, 1)
    borrow_date = date.today() - timedelta(days=24)
    due_date = date.today() - timedelta(days=10)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    update_book_availability(1, -1)

    ok, msg, fee = svc.return_book_by_patron("123456", 1)
    assert ok and round(fee,2) == 6.5  
