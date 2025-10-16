import os
import pytest
from database import init_database

@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    os.chdir(tmp_path)
    init_database()
    yield

from datetime import date, timedelta
import library_service as svc
from database import insert_book, insert_borrow_record, update_book_availability

def test_no_active_borrow():
    insert_book("X", "A", "1234567890123", 1, 1)
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["status"].startswith("error")

def test_fee_5_days_overdue():
    insert_book("X", "A", "1234567890123", 1, 1)
    borrow_date = date.today() - timedelta(days=19)
    due_date = date.today() - timedelta(days=5)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    update_book_availability(1, -1)

    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["status"] == "ok"
    assert r["days_overdue"] == 5
    assert abs(r["fee_amount"] - 2.5) < 1e-6

def test_fee_9_days_overdue():
    insert_book("Y", "B", "1234567890124", 1, 1)
    borrow_date = date.today() - timedelta(days=23)
    due_date = date.today() - timedelta(days=9)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    update_book_availability(1, -1)
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["days_overdue"] == 9
    assert abs(r["fee_amount"] - 5.5) < 1e-6

def test_fee_cap_15():
    insert_book("Z", "C", "1234567890125", 1, 1)
    borrow_date = date.today() - timedelta(days=80)
    due_date = date.today() - timedelta(days=66)
    insert_borrow_record("123456", 1, borrow_date, due_date)
    update_book_availability(1, -1)
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["fee_amount"] == 15.0
