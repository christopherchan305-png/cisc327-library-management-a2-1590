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
from database import (
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date
)

def test_status_report_two_active_plus_history():
    insert_book("T1", "A1", "1234567890123", 1, 1)  
    insert_book("T2", "A2", "1234567890124", 1, 1)  

    today = date.today()
    insert_borrow_record("123456", 1, today - timedelta(days=17), today - timedelta(days=3))
    update_book_availability(1, -1)
    insert_borrow_record("123456", 2, today - timedelta(days=9), today + timedelta(days=5))
    update_book_availability(2, -1)

    insert_book("T3", "A3", "1234567890125", 1, 1)  
    for i in range(5):
        insert_borrow_record("123456", 3, today - timedelta(days=40+i), today - timedelta(days=26+i))
        update_borrow_record_return_date("123456", 3, today - timedelta(days=25-i))

    report = svc.get_patron_status_report("123456")
    assert report["number_currently_borrowed"] == 2
    assert report["borrowing_history_count"] >= 7  
    assert abs(report["total_late_fees_owed"] - 1.5) < 1e-6
    assert {k for k in report["currently_borrowed"][0].keys()} == {"book_id", "due_date", "late_fee_accrued"}
