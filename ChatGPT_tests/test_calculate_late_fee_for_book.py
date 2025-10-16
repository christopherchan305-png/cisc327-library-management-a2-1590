from datetime import date, timedelta
import library_service as svc

def _make_active(due):
    return [{"book_id": 1, "due_date": due}]

def test_no_active_borrow(monkeypatch):
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: [])
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["status"].startswith("error")

def test_fee_5_days_overdue(monkeypatch):
    today = date.today()
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: _make_active(today - timedelta(days=5)))
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["status"] == "ok"
    assert r["days_overdue"] == 5
    assert abs(r["fee_amount"] - 2.5) < 1e-6  # 5 * 0.50

def test_fee_9_days_overdue(monkeypatch):
    today = date.today()
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: _make_active(today - timedelta(days=9)))
    r = svc.calculate_late_fee_for_book("123456", 1)
    # 7*0.5 + 2*1.0 = 5.5
    assert r["days_overdue"] == 9
    assert abs(r["fee_amount"] - 5.5) < 1e-6

def test_fee_cap_15(monkeypatch):
    today = date.today()
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: _make_active(today - timedelta(days=60)))
    r = svc.calculate_late_fee_for_book("123456", 1)
    assert r["fee_amount"] == 15.0
