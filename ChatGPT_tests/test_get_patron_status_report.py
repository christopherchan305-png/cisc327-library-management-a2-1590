from datetime import date, timedelta
import types
import library_service as svc

def test_status_report_with_two_active_and_history_count(monkeypatch):
    # Two active borrows; make one overdue by 3 days.
    today = date.today()
    active = [
        {"book_id": 1, "due_date": today - timedelta(days=3)},  # overdue 3 -> $1.50
        {"book_id": 2, "due_date": today + timedelta(days=5)},  # not overdue -> $0
    ]
    monkeypatch.setattr(svc, "get_patron_borrowed_books", lambda pid: active)

    # Mock fee helper for determinism
    def fake_fee(pid, bid):
        if bid == 1:
            return {"fee_amount": 1.5, "days_overdue": 3, "status": "ok"}
        return {"fee_amount": 0.0, "days_overdue": 0, "status": "ok"}
    monkeypatch.setattr(svc, "calculate_late_fee_for_book", fake_fee)

    # Fake DB connection for history count
    class Row(dict): pass
    class Conn:
        def execute(self, sql, params):
            # pretend there are 7 total records historically
            return types.SimpleNamespace(fetchone=lambda: Row({"c": 7}))
        def close(self): pass

    monkeypatch.setattr(svc, "get_db_connection", lambda: Conn())

    report = svc.get_patron_status_report("123456")

    assert report["patron_id"] == "123456"
    assert report["number_currently_borrowed"] == 2
    assert report["borrowing_history_count"] == 7
    assert abs(report["total_late_fees_owed"] - 1.5) < 1e-6

    # each item has required fields
    assert {k for k in report["currently_borrowed"][0].keys()} == {"book_id", "due_date", "late_fee_accrued"}
