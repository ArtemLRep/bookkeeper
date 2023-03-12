"""
Модуль реализующий Presenter
"""
import datetime
import typing

from PySide6.QtWidgets import QMenu, QMessageBox, QHeaderView
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QCursor

from bookkeeper.view.app_interface import MainWindow, ExpenseTableModel
from bookkeeper.view.app_interface import BudgetModel, CatExpenseModel
from bookkeeper.repository.sqlite_repository import SQLiteRepository, DataExpenseRow
from bookkeeper.models.category import Category
from bookkeeper.repository.abstract_repository import T
from bookkeeper.utils import read_tree
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.models.category import get_category_pk_by_name


class Presenter:
    """
    Реализация Presenter
    Входные параметры:
        repo_expense - репозиторий расходов
        repo_categories - репозиторий категорий
        repo_budget - репозиторий бюджета
    Атрибуты:
        repo_expenses - репозиторий для хранения расходов
        repo_categories - репозиторий для хранения категорий
        repo_budget - репозиторий для хранения бюджета
        expense_data - данные в таблице на листе Expenses.
                   Сюда записываются отредактированные пользователем ячейки
                   Затем строки расходов сохранятся в репозиторий
                   Реализован только для возможности редактирования таблицы как в Excel
        main_window - окно приложения

    """

    def __init__(self,
                 repo_expense: SQLiteRepository[T],
                 repo_categories: SQLiteRepository[T],
                 repo_budget: SQLiteRepository[T],
                 ) -> None:
        self.repo_expense = repo_expense
        self.repo_budget = repo_budget
        self.repo_categories = repo_categories

        self.expense_data = self.expense_data_init()
        budget_data = self.budget_data_init()
        data = [Budget.make_table_row(row) for row in budget_data]
        self.main_window = MainWindow(self.expense_data, data)
        self.main_window.category.text_box.setText(
            read_categories(self.category_data_init())
        )

        self.main_window.set_line_category(self.category_data_init())
        self.day_expense_by_cat()
        self.main_window.budget.table_cat_expenses.horizontalHeader(). \
            setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.main_window.budget.table_cat_expenses.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.main_window.budget.table_cat_expenses.verticalHeader().setVisible(False)

        self.main_window.category.edit_button. \
            clicked.connect(self.commit_categories)  # type: ignore[attr-defined]
        self.main_window.expense.add_button. \
            clicked.connect(self.add_expense_row)  # type: ignore[attr-defined]
        self.main_window.budget.change_button. \
            clicked.connect(self.change_budget)  # type: ignore[attr-defined]

        self.main_window.expense.expense_table. \
            setContextMenuPolicy(Qt.CustomContextMenu)  # type: ignore[attr-defined]

        self.main_window.expense.expense_table. \
            customContextMenuRequested. \
            connect(self.table_menu)  # type: ignore[attr-defined]

        self.main_window.budget.cat_day_expense_button. \
            clicked.connect(self.day_expense_by_cat)  # type: ignore[attr-defined]
        self.main_window.budget.cat_month_expense_button. \
            clicked.connect(self.month_expense_by_cat)  # type: ignore[attr-defined]

    def expense_data_init(self) -> list[list[str]]:
        """
        Метод для инициализации данных таблицы расходов(вкладка Expenses)
        """
        table_name = self.repo_expense.table_name
        columns = (f'{table_name}.pk', 'expense_date', 'amount', 'name', 'comment')
        data_from_repo = self.repo_expense.get_join(
            self.repo_expense.table_name,
            self.repo_categories.table_name,
            field_table_1="category",
            field_table_2="pk",
            columns=columns
        )
        data_to_expense_table = [list(x) for x in data_from_repo]
        now = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        if len(data_to_expense_table) == 0:
            data_to_expense_table = [
                ['0', now, '1500', 'food', 'Example!!']
            ]
        return data_to_expense_table

    def budget_data_init(self) -> list[Budget]:
        """
        Метод для инициализации данных таблицы бюджета (вкладка Budget)
        Обновляет поле amount
        """
        day_expense = self.get_day_expense()
        if (self.repo_budget.get_by_pk(1)) is None:
            self.repo_budget.add(Budget(period="day", budget=0, amount=day_expense))
        day_budget = (self.repo_budget.get_by_pk(1))
        self.repo_budget.update_by_pk(
            Budget(pk=1, budget=day_budget.budget, amount=day_expense, period="day")
        )

        week_expense = self.get_week_expense()
        if (self.repo_budget.get_by_pk(2)) is None:
            self.repo_budget.add(Budget(period="week", budget=0, amount=week_expense))
        week_budget = (self.repo_budget.get_by_pk(2))
        self.repo_budget.update_by_pk(
            Budget(pk=2, budget=week_budget.budget, amount=week_expense, period="week")
        )

        month_expense = self.get_month_expense()
        if (self.repo_budget.get_by_pk(3)) is None:
            self.repo_budget.add(
                Budget(period="month", budget=0, amount=month_expense)
            )
        month_budget = (self.repo_budget.get_by_pk(3))
        self.repo_budget.update_by_pk(
            Budget(pk=3, budget=month_budget.budget, amount=month_expense, period="month")
        )

        day_budget = (self.repo_budget.get_by_pk(1))
        week_budget = (self.repo_budget.get_by_pk(2))
        month_budget = (self.repo_budget.get_by_pk(3))
        return [
            day_budget,
            week_budget,
            month_budget
        ]

    def category_data_init(self) -> list[Category]:
        """
        Метод для инициализации списка категорий
        """
        not_stated = 'Not stated'
        if len(self.repo_categories.get_all()) == 0:
            self.repo_categories.add(Category(
                name=not_stated,
                parent=None
            ))
        return [
            Category(pk=cat.pk, name=cat.name, parent=cat.parent)
            for cat in self.repo_categories.get_all()
        ]

    def day_expense_by_cat(self) -> None:
        """
        Передача данных о расходах за день в таблицу расходы по категориям(вкладка Budget)
        Активируется при запуске приложения, изменении таблицы расходов и
        при нажатии кнопки day во вкладке(Budget)
        """
        data = self.repo_expense.get_cat_expense_data_day()
        if len(data) == 0:
            data = [
                ['food ', '1500']
            ]
        model = CatExpenseModel(data)
        self.main_window.budget.table_cat_expenses.setModel(model)

        self.main_window.budget.cat_day_expense_button.setStyleSheet(
            'QPushButton {background-color: darkGray; color: black;}'
        )
        self.main_window.budget.cat_month_expense_button.setStyleSheet(
            'QPushButton {background-color: white; color: black;}'
        )
        return None

    def month_expense_by_cat(self) -> None:
        """
        Передача данных о расходах за день в таблицу расходы по категориям(вкладка Budget)
        Активируется при нажатии кнопки month во вкладке Budget
        """
        data = self.repo_expense.get_cat_expense_data_month()
        if len(data) == 0:
            data = [
                ['food', '1500']
            ]
        model = CatExpenseModel(data)
        self.main_window.budget.table_cat_expenses.setModel(model)

        self.main_window.budget.cat_month_expense_button.setStyleSheet(
            'QPushButton {background-color: darkGray; color: black;}'
        )
        self.main_window.budget.cat_day_expense_button.setStyleSheet(
            'QPushButton {background-color white: green; color: black;}'
        )
        return None

    def get_day_expense(self) -> float:
        """
        Возвращает расходы за текущий день
        """
        today = datetime.datetime.today().date()
        day_expense = sum(
            (float(row[2]) for row in self.expense_data
             if datetime.datetime.strptime(row[1], '%d-%m-%Y %H:%M').date() == today
             ))
        return day_expense

    def get_week_expense(self) -> float:
        """
        Возвращает расходы за текущую неделю
        """
        today = datetime.datetime.today().date()
        week_expense = 0
        for row in self.expense_data:
            row_date = datetime.datetime.strptime(row[1], '%d-%m-%Y %H:%M')
            row_year = row_date.date().year
            row_week = row_date.date().isocalendar().week
            today_week = today.isocalendar().week
            if row_year == today.year \
                    and today_week == row_week:
                week_expense += float(row[2])

        return week_expense

    def get_month_expense(self) -> float:
        """
        Возвращает расходы за текущий месяц
        """
        today = datetime.datetime.today().date()
        month_expense = 0
        for row in self.expense_data:
            row_date = datetime.datetime.strptime(row[1], '%d-%m-%Y %H:%M')
            if today.year == row_date.date().year \
                    and today.month == row_date.date().month:
                month_expense += float(row[2])
        return month_expense

    def change_budget(self) -> None:
        """
        Меняет бюджет при нажатии кнопки "chage budget" во вкладке Budget
        Записывает данные о бюджете за период в репозиторий repo_budget
        """
        day_budget = self.main_window.budget.line_day_budget.text()
        if not amount_right_input(self.main_window, day_budget):
            return None
        week_budget = self.main_window.budget.line_week_budget.text()
        if not amount_right_input(self.main_window, week_budget):
            return None
        month_budget = self.main_window.budget.line_month_budget.text()
        if not amount_right_input(self.main_window, month_budget):
            return None
        self.repo_budget.delete_all()
        self.repo_budget.next_id = 1
        self.repo_budget.add(
            Budget(period="day", budget=float(day_budget)
                   ))
        self.repo_budget.add(
            Budget(period="week", budget=float(week_budget))
        )
        self.repo_budget.add(
            Budget(period="month", budget=float(month_budget))
        )
        budget_data = self.budget_data_init()
        data = [Budget.make_table_row(row) for row in budget_data]
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)
        return None

    def update_expense_cat(self, new_cat_pk: int, old_cat_pk: int) -> None:
        """
        Обновляет id категории в репозитории расходов:
        У всех расходов с category == old_cat_pk, category меняется на new_cat_pk
        """
        for row in self.repo_expense.get_all():
            expense_date = datetime.datetime.strptime(row.expense_date, '%d-%m-%Y %H:%M')
            if float(row.category) == old_cat_pk:
                self.repo_expense.update_by_pk(DataExpenseRow(
                    (Expense(
                        pk=row.pk,
                        expense_date=expense_date,
                        category=new_cat_pk,
                        amount=row.amount,
                        comment=row.comment
                    ))))
        return None

    def commit_categories(self) -> None:
        """
        Меняет список категорий:
        Активируется при нажатии кнопки "commit changes" во вкладке Category list
        """
        not_stated = 'Not stated'
        cat_text = self.main_window.category.text_box.toPlainText()
        data = cat_text.splitlines()

        have_same_categories = same_categories_check(self.main_window, data)
        if not have_same_categories:
            self.main_window.category.text_box.setText(
                read_categories(self.category_data_init())
            )
            return None

        old_data = self.category_data_init()
        self.repo_categories.delete_all()
        self.repo_categories.add(
            Category(name=not_stated, parent=None)
        )

        Category.create_from_tree(read_tree(data), self.repo_categories)
        update_data: list[Category] = self.category_data_init()
        for old_cat_row in old_data:
            has_same_name = False
            for new_cat_row in update_data:
                if new_cat_row.name == 'Not stated':
                    continue
                if old_cat_row.name == new_cat_row.name:
                    has_same_name = True
                    self.update_expense_cat(
                        new_cat_pk=new_cat_row.pk,
                        old_cat_pk=old_cat_row.pk
                    )
            if not has_same_name:
                category_data = self.category_data_init()
                pk = get_category_pk_by_name(not_stated, category_data)
                self.update_expense_cat(new_cat_pk=pk, old_cat_pk=old_cat_row.pk)
        self.main_window.set_line_category(self.category_data_init())

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        self.day_expense_by_cat()

        return None

    def table_menu(self) -> None:
        """
        Меню Delete row|Update cell строки расходов.
        Срабатывает при нажатии правой кнопки мыши в ячейке/ах таблицы расходов
        вкладка(Expenses)
        """
        selected = self.main_window.expense.expense_table.selectedIndexes()
        if not selected:
            return
        menu = QMenu()
        delete_act = menu.addAction('Delete row')
        update_table_act = menu.addAction('Update cell')
        delete_act.triggered.connect(  # type: ignore[attr-defined]
            lambda: self.remove_row(selected))
        update_table_act.triggered.connect(  # type: ignore[attr-defined]
            lambda: self.update_cell(selected))
        menu.exec_(QCursor.pos())

    def remove_row(self,
                   indexes: list[typing.Union[QModelIndex, QPersistentModelIndex]]
                   ) -> None:
        """
        Удаление сроки таблицы расходов.
        Срабатывае при нажатии кнопки "Delete row". См table_menu
        """
        rows = set(index.row() for index in indexes)
        for row in rows:
            self.repo_expense.delete_by_pk(int(self.expense_data[row][0]))

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = [Budget.make_table_row(row) for row in budget_data]
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)

        self.day_expense_by_cat()

    def update_cell(self,
                    indexes: list[typing.Union[QModelIndex, QPersistentModelIndex]]
                    ) -> None:
        """
        Обновление выделенных ячеек.
        Срабатывае при нажатии кнопки "Update cell". См table_menu
        """
        rows = list(index.row() for index in indexes)
        columns = list(index.column() for index in indexes)
        for row, col in zip(rows, columns):
            if check_correct_update(
                    self.main_window,
                    row, col,
                    self.expense_data,
                    self.category_data_init()
            ):
                new_expense_row = get_expense_row_by_row_number(
                    row,
                    self.category_data_init(),
                    self.expense_data
                )
                self.repo_expense.update_by_pk(new_expense_row)

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = [Budget.make_table_row(row) for row in budget_data]
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)

        self.day_expense_by_cat()

    def add_expense_row(self) -> None:
        """
        Добавляет в репозиторий новую запись, обновляет таблицу во вкладке(Expense)
        Активируется при нажатии кнопки "Add expense" во вкладке Categories
        """
        text_date = self.main_window.expense.line_date.text()
        amount = self.main_window.expense.line_amount.text()
        category = self.main_window.expense.line_category.currentText()
        comment = self.main_window.expense.line_comment.text()
        if not amount_right_input(self.main_window, amount):
            return None
        if not date_right_input(self.main_window, text_date):
            return None
        date = datetime.datetime.strptime(text_date, '%d-%m-%Y %H:%M')
        category_data = self.category_data_init()
        pk = [x for i, x in enumerate(category_data) if x.name == category]
        row = Expense(amount=float(amount), category=pk[0].pk,
                      expense_date=date, comment=comment)
        self.repo_expense.add(DataExpenseRow(row))
        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = [Budget.make_table_row(row) for row in budget_data]
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)

        self.day_expense_by_cat()

        return None


def get_expense_row_by_row_number(
        row_num: int,
        category_data: list[Category],
        expense_data: list[list[str]]) -> DataExpenseRow:
    """
    Получить строку расходов по номеру в таблице расходов на вкладке Expenses
    """
    date = expense_data[row_num][1]
    date_expense = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M')
    expense = Expense(
        pk=int(expense_data[row_num][0]),
        expense_date=date_expense,
        amount=float(expense_data[row_num][2]),
        category=get_category_pk_by_name(expense_data[row_num][3], category_data),
        comment=expense_data[row_num][4]
    )
    return DataExpenseRow(expense)


def get_subcategories(cat: Category, category_data: list[Category]) -> list[Category]:
    """
    Получить список подкатегорий
    """
    sub_cat_pk = [data.pk for data in category_data if cat.pk == data.parent]
    sub_cat = [x for x in category_data if x.pk in sub_cat_pk]
    return sub_cat


def print_sub_cat(sub_cat: Category,
                  space_num: int,
                  category_data: list[Category]) -> str:
    """
    формирует строку в виде дерева из подкатегорий
    """
    cat_string = space_num * '\t' + f'{sub_cat.name} \n'
    sub_sub_cat = get_subcategories(sub_cat, category_data)
    for sub in sub_sub_cat:
        cat_string += print_sub_cat(sub, space_num + 1, category_data)
    return cat_string


def read_categories(category_data: list[Category]) -> str:
    """
    Формирует строку в виде дерева из списка категорий
    """
    cat_string = ''
    not_stated = 'Not stated'
    for cat in category_data:
        if cat.name == not_stated:
            continue
        if cat.parent is None:
            cat_string += f'{cat.name} \n'
            space_num = 1
            for sub_cat in get_subcategories(cat, category_data):
                cat_string += print_sub_cat(sub_cat, space_num, category_data)
        else:
            continue
    return cat_string


def date_right_input(main_window: MainWindow, date: str) -> bool:
    """
    Проверка на правильное заполнение поля %date
    date приводится к виду %d-%m-%Y %H:%M
    """
    try:
        datetime.datetime.strptime(date, '%d-%m-%Y %H:%M')
        return True
    except ValueError:
        QMessageBox.critical(main_window, 'Error', f"Date {date} is incorrect")
        return False


def amount_right_input(main_window: MainWindow, amount: str) -> bool:
    """
    Проверка на оправилньное заполнение поля amount:
        type(amount) is float
        amount >= 0
    """
    try:
        float(amount)
    except ValueError:
        error_message = f"Amount {amount} should be a number"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    if float(amount) < 0:
        error_message = f"Amount {amount} should be positive"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    return True


def same_categories_check(main_window: MainWindow, categories: list[str]) -> bool:
    """
    Проверка на одиновые категории
    """
    new_categories = []
    for i, cat in enumerate(categories):
        cat = cat.strip()
        cat = cat.lstrip()
        if not cat == '':
            new_categories.append(cat)
    same_categories = [x for i, x in enumerate(new_categories)
                       if i != new_categories.index(x)]
    if len(same_categories) != 0:
        QMessageBox.critical(main_window, 'Error', "SameCategories")
        return False
    return True


def category_right_input(
        main_window: MainWindow,
        new_cat_name: str,
        category_data: list[Category]) -> bool:
    """
    Проверка на правильное заполнение списка категорий
    """
    cat_data = [category.name for category in category_data]
    if new_cat_name in cat_data:
        return True
    error_message = f"Category {new_cat_name} is not in category list"
    QMessageBox.critical(main_window, 'Error', error_message)
    return False


def check_correct_update(main_window: MainWindow,
                         row: int, col: int,
                         expense_data: list[list[str]],
                         category_data: list[Category]) -> bool:
    """
    Проверка на правильное обновление ячеек в таблице расходов:
        правильное заполнение поля date,
        првильное заполнение amount,
        правильное заполнение category
    """
    if expense_data[row][0] == '0':
        error_message = "It is an example! Try App by yourself :)"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    new_data_cell = expense_data[row][col]
    if col == 1:
        return date_right_input(main_window, new_data_cell)
    if col == 2:
        if not amount_right_input(main_window, new_data_cell):
            return False
    if col == 3:
        return category_right_input(main_window, new_data_cell, category_data)
    return True
