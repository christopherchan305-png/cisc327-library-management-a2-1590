import library_service as svc

def test_search_title_and_author_partial_case_insensitive(monkeypatch):
    books = [
        {"title": "The Pragmatic Programmer", "author": "Hunt", "isbn": "1234567890123"},
        {"title": "Clean Code", "author": "Martin", "isbn": "1234567890124"},
    ]
    monkeypatch.setattr(svc, "get_all_books", lambda: books)

    # title partial, case-insensitive
    res = svc.search_books_in_catalog("prag", "title")
    assert len(res) == 1 and res[0]["title"].startswith("The Prag")

    # author partial
    res = svc.search_books_in_catalog("mart", "author")
    assert len(res) == 1 and res[0]["author"] == "Martin"

def test_search_isbn_exact_only_13_digits(monkeypatch):
    books = [{"title": "Book A", "author": "AA", "isbn": "1234567890123"}]
    monkeypatch.setattr(svc, "get_all_books", lambda: books)

    assert svc.search_books_in_catalog("1234567890123", "isbn")[0]["title"] == "Book A"
    assert svc.search_books_in_catalog("123456789012", "isbn") == []      # too short
    assert svc.search_books_in_catalog("123456789012X", "isbn") == []     # non-numeric
    assert svc.search_books_in_catalog("", "title") == []                 # empty query
    assert svc.search_books_in_catalog("abc", "wtf") == []                # invalid type
