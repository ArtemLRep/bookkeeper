"""
Модуль тестирования репозитория расходов
"""
from bookkeeper.repository.sqlite_repository import SQLiteRepository, DataExpenseRow
from bookkeeper.models.expense import Expense
import datetime
import pytest
import os

date_time_str = '2020-08-30 08:15:28'
date_format = '%d-%m-%Y %H:%M'
date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


@pytest.fixture()
def repo():
    fields = ('pk', 'added_date', 'expense_date', 'category', 'amount', 'comment')
    types = ('INTEGER PRIMARY KEY', 'TIMESTAMP', 'TIMESTAMP', 'TEXT', 'REAL', 'TEXT')
    return SQLiteRepository("test_db.db", "TestTable", fields, types, DataExpenseRow)


'''Success Tests'''


def test_success_add(repo):
    row1 = DataExpenseRow(Expense(expense_date=date, category=1, amount=10))
    assert repo.add(row1) is 1
    row2 = DataExpenseRow(Expense(expense_date=date, category=2, amount=100))
    assert repo.add(row2) is 2
    row3 = DataExpenseRow(Expense(expense_date=date, category=3, amount=1000))
    assert repo.add(row3) is 3


def test_success_get_by_pk(repo):
    assert repo.get_by_pk(1)


def first_col_is_pk(repo):
    row1 = repo.get_by_pk(1)
    assert isinstance(row1[0], int)


def test_success_get_all(repo):
    assert len(repo.fields) != 0


def test_success_update(repo):
    row1 = DataExpenseRow(Expense(pk=1, expense_date=date, category=3, amount=1000))
    assert repo.update_by_pk(row1) is None


def test_success_delete(repo):
    assert repo.delete_by_pk(1) is None


'''WRONG TESTS'''


@pytest.mark.xfail
def test_wrong_db_init_str():
    wrong_repo = SQLiteRepository("test", "table_name")


'''Testing Wrong Expense Date'''


@pytest.mark.xfail
def test_add_wrong_date_type_int(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=5, expense_date=10, amount=100))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_date_type_str(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=5, expense_date="date", amount=100))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_date_type_float(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=5, expense_date=10.9, amount=100))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_date_type_none(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=5, expense_date=None, amount=100))
    assert repo.add(row)


'''Testing Wrong Category'''


@pytest.mark.xfail
def test_add_wrong_category_type_float(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=10.9, expense_date=date, amount=100))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_category_type_str(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category="cat", expense_date=date, amount=100))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_category_type_none(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=None, expense_date=date, amount=100))
    assert repo.add(row)


'''Testing Wrong Amount'''


@pytest.mark.xfail
def test_add_wrong_amount_type_str(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=10, expense_date=date, amount='100'))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_amount_less_than_zero(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=10, expense_date=date, amount=-10))
    assert repo.add(row)


@pytest.mark.xfail
def test_add_wrong_amount_type_none(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=10, expense_date=date, amount=None))
    assert repo.add(row)


'''Testing Wrong Commentary'''


@pytest.mark.xfail
def test_add_wrong_comment_type_int(repo):
    row = DataExpenseRow(Expense(pk=repo.next_id, category=10, expense_date=date, amount=1000, comment=100))
    assert repo.add(row)


'''Testing Getting By Wrong pk Type'''


@pytest.mark.xfail
def test_fail_get_by_pk_wrong_pk_less_than_zero(repo):
    assert repo.get_by_pk(-1)


@pytest.mark.xfail
def test_fail_get_by_pk_wrong_pk_type_float(repo):
    assert repo.get_by_pk(10.5)


@pytest.mark.xfail
def test_fail_get_by_pk_wrong_pk_type_str(repo):
    assert repo.get_by_pk("pk")


@pytest.mark.xfail
def test_fail_get_by_pk_wrong_pk_type_none(repo):
    assert repo.get_by_pk(None)


'''Getting Data Test'''


@pytest.mark.xfail
def test_fail_get_all(repo):
    assert len(repo.fields) == 0


'''Update Data Test'''


@pytest.mark.xfail
def test_fail_update_wrong_pk_less_than_zero(repo):
    row = DataExpenseRow(Expense(pk=-1, category=10, expense_date=date, amount=1000))
    assert repo.update_by_pk(row)


@pytest.mark.xfail
def test_fail_update_wrong_pk_type_none(repo):
    row = DataExpenseRow(Expense(pk=None, category=10, expense_date=date, amount=1000))
    assert repo.update_by_pk(row)


@pytest.mark.xfail
def test_fail_update_wrong_pk_type_str(repo):
    row = DataExpenseRow(Expense(pk="pk", category=10, expense_date=date, amount=1000))
    assert repo.update_by_pk(row)


@pytest.mark.xfail
def test_fail_update_wrong_pk_type_float(repo):
    row = DataExpenseRow(Expense(pk=10.9, category=10, expense_date=date, amount=1000))
    assert repo.update_by_pk(row)


'''Delete By Wrong pk'''


@pytest.mark.xfail
def test_fail_delete_by_pk_wrong_pk_less_than_zero(repo):
    assert repo.delete_by_pk(-1) is None


@pytest.mark.xfail
def test_fail_delete_by_pk_wrong_pk_type_float(repo):
    assert repo.delete_by_pk(10.5) is None


@pytest.mark.xfail
def test_fail_delete_by_pk_wrong_pk_type_str(repo):
    assert repo.delete_by_pk("pk") is None


@pytest.mark.xfail
def test_fail_delete_by_pk_wrong_pk_type_none(repo):
    assert repo.get_by_pk(None) is None


def test_remove():
    os.remove("test_db.db")
