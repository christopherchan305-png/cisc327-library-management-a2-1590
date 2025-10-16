import types
from datetime import date, timedelta
import library_service as svc

def test_return_invalid_patron_id(monkeypatch):
    ok, msg, fee = svc.return_book_by_patron("12A456", 1)
    assert not ok and "6 digits" in msg and fee == 0.0

def test_return_no_active_borrow(monkeypatch):
    # get_book_by_id: book exists
    monkeypatch.setattr(svc, "get_book_by_id", lambda bid: {"id": bid, "title": "X", "available_copies": 0, "total_copies": 1})
    # patron has no active borrows
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: [])
    ok, msg, fee = svc.return_book_by_patron("123456", 1)
    assert not ok and "No active borrow" in msg and fee == 0.0

def test_return_on_time_no_fee(monkeypatch):
    # Book exists
    monkeypatch.setattr(svc, "get_book_by_id", lambda bid: {"id": bid, "title": "Clean Code", "available_copies": 0, "total_copies": 1})
    # Patron has an active borrow for this book (due today)
    due = date.today()
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: [{"book_id": 1, "due_date": due}])

    # Fee helper returns 0
    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0.0, "days_overdue": 0, "status": "ok"})

    # Track DB updates
    called = {"returned": None, "avail": None}
    def fake_mark_return(pid, bid, d): called["returned"] = (pid, bid, d)
    def fake_update_avail(bid, delta): called["avail"] = (bid, delta)

    monkeypatch.setattr(svc, "update_borrow_record_return_date", fake_mark_return)
    monkeypatch.setattr(svc, "update_book_availability", fake_update_avail)

    ok, msg, fee = svc.return_book_by_patron("123456", 1)
    assert ok and fee == 0.0 and "Returned successfully" in msg
    assert called["returned"][0] == "123456" and called["returned"][1] == 1
    assert called["avail"] == (1, +1)

def test_return_late_with_fee(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", lambda bid: {"id": bid, "title": "Pragmatic Programmer", "available_copies": 0, "total_copies": 1})
    # Active borrow present
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: [{"book_id": 2, "due_date": date.today() - timedelta(days=10)}])
    # Fee helper says $6.50 (7*0.5 + 3*1.0)
    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 6.5, "days_overdue": 10, "status": "ok"})
    monkeypatch.setattr(svc, "update_borrow_record_return_date", lambda pid, bid, d: None)
    monkeypatch.setattr(svc, "update_book_availability", lambda bid, delta: None)

    ok, msg, fee = svc.return_book_by_patron("123456", 2)
    assert ok and abs(fee - 6.5) < 1e-6 and "late fee $6.50" in msg
