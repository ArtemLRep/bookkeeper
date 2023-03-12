"""
Модуль точки входа. Запускает приложение
"""
import sys
from PySide6.QtWidgets import QApplication
from bookkeeper.presenter import Presenter
from bookkeeper.repository.sqlite_repository import DataExpenseRow
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SQLiteRepository

repo_expense_columns = ('pk', 'added_date', 'expense_date',
                        'category', 'amount', 'comment')
repo_expense_types = ('INTEGER PRIMARY KEY', 'TIMESTAMP',
                      'TIMESTAMP', 'TEXT', 'REAL', 'TEXT')

repo_cat_columns = ("pk", "name", "parent")
repo_cat_types = ("INTEGER PRIMARY KEY", "TEXT", "INTEGER")

repo_budget_columns = ("pk", "period", "budget", "amount")
repo_budget_types = ("INTEGER PRIMARY KEY", "TEXT", "REAL", "REAL")

repo_expense = SQLiteRepository("test_presenter_db.db", "expense_table",
                                repo_expense_columns, repo_expense_types, DataExpenseRow)
repo_categories = SQLiteRepository("test_presenter_db.db", "categories_table",
                                   repo_cat_columns, repo_cat_types, Category)
repo_budget = SQLiteRepository("test_presenter_db.db", "budget_table",
                               repo_budget_columns, repo_budget_types, Budget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    presenter: Presenter = Presenter(repo_expense, repo_categories, repo_budget)
    presenter.main_window.show()
    app.exec()
else:
    pass
