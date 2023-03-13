"""
Модуль описывает Репозиторий, находящийся на диске
"""
import sqlite3
import datetime
import typing
from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T
from bookkeeper.models.expense import Expense

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments


class SQLiteRepository(AbstractRepository[T]):
    """
    Класс орисывающий работу с таблицей из SQL БД находящейся на диске
    атрибуты:
        путь к файлу
        название таблицы
        поля таблицы
        типы полей
    Поддерживает те же методы, что и в абстрактном репозитории
    """

    def __init__(self,
                 db_file: str,
                 table_name: str,
                 fields: tuple[str, ...],
                 types: tuple[str, ...],
                 row_type: typing.Type[T]
                 ) -> None:
        if not isinstance(db_file, str):
            raise TypeError("DB address should be str")
        if ".db" not in db_file:
            raise ValueError("DB should be .db file")
        self.db_file: str = db_file
        self.table_name: str = table_name
        self.fields: tuple[str] = fields
        self.row_type: typing.Type[T] = row_type
        with sqlite3.connect(db_file) as con:
            cur = con.cursor()
        columns = [f"{col} {t}" for col, t in zip(fields, types)]
        names = ', '.join(columns)
        create_table = f"CREATE TABLE IF NOT EXISTS {self.table_name} ( {names} );"
        cur.execute(create_table)
        last_id: int = cur.execute(
            f"SELECT MAX({self.fields[0]}) FROM {self.table_name}"
        ).fetchone()[0]
        self.next_id: int = 1
        if last_id is not None:
            self.next_id = int(last_id) + 1
        con.close()

    def add(self, obj: T) -> int:
        """
        Добавить элемент в репизиторий.
        Объект должен иметь атрибут pk - primary key
        """
        obj.pk = self.next_id
        self.next_id += 1
        names = ', '.join(self.fields)
        place = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        query = f'INSERT OR IGNORE INTO {self.table_name} ({names}) VALUES ({place})'
        cur.execute(query, values)
        con.commit()
        con.close()
        return obj.pk

    def get_by_pk(self, pk: int) -> T | None:
        """
        Получить элемент репозитория по pk - primary key
        Если элемента с pk нет в БД, возвращает None
        """
        if not isinstance(pk, int):
            raise TypeError("Can get row only by int pk")
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
        query = "SELECT * FROM " + str(self.table_name) + " WHERE pk = " + str(pk)
        res = cursor.execute(query).fetchone()
        conn.close()
        obj = self.row_type()
        try:
            for name, value in zip(self.fields, res):
                setattr(obj, name, value)
        except TypeError:
            return None
        return obj

    def get_all(self,
                where: dict[str, Any] | None = None,
                columns: tuple[str, ...] = ()
                ) -> list[T]:
        """
        Получить все данные полей - columns по некоторому условию - where
        """
        query = ""
        if len(columns) == 0:
            query += "SELECT * FROM " + str(self.table_name)
        else:
            columns_names = ', '.join(columns)
            query = f"SELECT {columns_names} FROM {str(self.table_name)} "
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
        if where is not None:
            query_cond_list = []
            for field in where.keys():
                query_cond_list.append(field + " = " + str(where.get(field)))
            query += " WHERE " + ' && '.join(query_cond_list)
        res = cursor.execute(query).fetchall()
        conn.close()
        data = []
        for row in res:
            obj = self.row_type()
            for name, value in zip(self.fields, row):
                setattr(obj, name, value)
            data.append(obj)
        return data

    def update_by_pk(self, obj: T) -> None:
        """
        Обновить данные в строке репозитория имеющий pk объекта obj.
        Новые данные, которые нужно записать хранятся в других атрибутах объекта obj
        """
        if not isinstance(obj.pk, int):
            raise TypeError("Can update row only by int pk")
        names = '=? , '.join(self.fields)
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        query = f'UPDATE {self.table_name} SET {names} =? WHERE pk = {obj.pk}'
        cur.execute(query, values)
        con.commit()
        con.close()
        return

    def delete_by_pk(self, pk: int) -> None:
        """
        Удатить строку имеющую pk
        """
        if not isinstance(pk, int):
            raise TypeError("Can update row only by int pk")
        if pk < 0:
            raise ValueError("pk must be positive")
        with sqlite3.connect(self.db_file) as con:
            if not isinstance(pk, int):
                raise TypeError("Can get row only by int pk")
        cur = con.cursor()
        query = "DELETE FROM " + self.table_name + " WHERE pk = " + str(pk)
        cur.execute(query)
        con.commit()
        con.close()

    def show_all(self) -> None:
        """
        Распечатать все строки репозитория
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
        cur.execute("SELECT * FROM " + self.table_name)
        for x in (cur.fetchall()):
            print(x)
        con.close()

    def delete_all(self) -> None:
        """
        Удалить все элементы репозитория.
        Сама таблица не удаляется!
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
        cur.execute("DELETE FROM " + self.table_name)
        # self.next_id = 1
        con.commit()
        con.close()

    def get_join(self, table_1: str, table_2: str, columns: tuple[str, ...],
                 field_table_1: str, field_table_2: str) -> list[list[str]]:
        """
        Получить данные полей coloumns из таблицы 1 объединённой со 2
            при совпадающих данных в полях field_table_1 и field_table_2
        columns - поля
        table1 - имя 1 таблицы
        table1 - имя 2 таблицы
        field_table_1 - поле 1 таблицы
        field_table_2 - поле 2 таблицы
        """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
        names = ', '.join(columns)
        query = f"SELECT {names} " \
                f"FROM {table_1}" \
                f" JOIN {table_2}" \
                f" ON {table_1}.{field_table_1} = {table_2}.{field_table_2}"
        cur.execute(query)
        return cur.fetchall()

    def get_cat_expense_data_day(self) -> list[list[str | float]]:
        """
        Получить расходы сгруппированных по категориям за день
        Реализована ТОЛЬКО для передачи даныых в виджет table_cat_expenses!
        table_cat_expenses - таблица расходов по категориям,
        См MainWindow в app_interface.py
        """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
        today = datetime.datetime.today().date().strftime('%d-%m-%Y')

        query = f"SELECT categories_table.name, SUM(expense_table.amount) " \
                f"FROM categories_table JOIN expense_table" \
                f" WHERE categories_table.pk = expense_table.category" \
                f" AND expense_table.expense_date LIKE '{today}%'" \
                f" GROUP BY categories_table.name"
        cur.execute(query)
        return cur.fetchall()

    def get_cat_expense_data_month(self) -> list[list[str | float]]:
        """
        Получить расходы сгруппированных по категориям за месяц
        Реализована ТОЛЬКО для передачи даныых в виджет table_cat_expenses!
        table_cat_expenses - таблица расходов по категориям,
        См MainWindow в app_interface.py
        """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
        today = datetime.datetime.today().date().strftime('%m-%Y')

        query = f"SELECT categories_table.name, SUM(expense_table.amount)" \
                f"FROM categories_table JOIN expense_table" \
                f" WHERE categories_table.pk = expense_table.category" \
                f" AND expense_table.expense_date LIKE '%-{today}%'" \
                f"GROUP BY categories_table.name"
        cur.execute(query)
        return cur.fetchall()


class DataExpenseRow:
    """
    Класс описывающий тип строки репозитория
    Проверка на правильный тип полей
    названия полей совпадают с названиями колонок репозитория
    """

    def __init__(self, expense: Expense = Expense()) -> None:
        self.pk = int(expense.pk)
        self.expense_date = expense.expense_date.strftime('%d-%m-%Y %H:%M')

        if not isinstance(expense.category, int):
            raise TypeError("Only int category allowed")
        self.category = expense.category

        if expense.amount < 0:
            raise ValueError("Only positive amount allowed")
        if not isinstance(expense.amount, float | int):
            raise TypeError("Only float or int allowed")
        self.amount = expense.amount

        if not isinstance(expense.comment, str):
            raise TypeError("Only str commentary allowed")
        self.comment = expense.comment

        self.added_date = expense.added_date.strftime('%d-%m-%Y %H:%M')

    def display(self) -> None:
        """
        Вывод на экран
        """
        print("pk: ", self.pk, '\n',
              "added_date: ", self.added_date, '\n',
              "expense_date: ", self.expense_date, '\n',
              "amount: ", self.amount, '\n',
              "category: ", self.category, '\n',
              "comment: ", self.comment, '\n',
              )
        return None
