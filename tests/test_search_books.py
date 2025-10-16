import os
import pytest
from database import init_database

@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    os.chdir(tmp_path)
    init_database()
    yield

import library_service as svc
from database import insert_book

def test_search_title_and_author_partial_case_insensitive():
    insert_book("The Pragmatic Programmer", "Hunt", "1234567890123", 2, 2)
    insert_book("Clean Code", "Martin", "1234567890124", 1, 1)

    res = svc.search_books_in_catalog("prag", "title")
    assert len(res) == 1 and res[0]["title"].startswith("The Prag")

    res = svc.search_books_in_catalog("mart", "author")
    assert len(res) == 1 and res[0]["author"] == "Martin"

def test_search_isbn_exact_only_13_digits():
    insert_book("Book A", "AA", "1234567890123", 1, 1)

    assert svc.search_books_in_catalog("1234567890123", "isbn")[0]["title"] == "Book A"
    assert svc.search_books_in_catalog("123456789012", "isbn") == []
    assert svc.search_books_in_catalog("123456789012X", "isbn") == []
    assert svc.search_books_in_catalog("", "title") == []
    assert svc.search_books_in_catalog("abc", "wtf") == []
