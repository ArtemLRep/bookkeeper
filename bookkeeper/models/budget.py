"""
Модуль описывающий объект бюджет
"""
from dataclasses import dataclass


@dataclass
class Budget:
    """
    Запланированный Бюджет на период
    period - период
    budget - сумма
    pk - id записи в БД
    """
    period: str = 'day'
    budget: float = 0
    amount: float = 0
    pk: int = 0

    def make_table_row(self) -> list[float]:
        """
        Переводит объект Budget в строку для таблицы бюджета
        """
        return [self.budget, self.amount, self.budget - self.amount]
