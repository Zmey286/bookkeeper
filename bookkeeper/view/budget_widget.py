"""
Widget of budget table
"""

from typing import Any, Callable
from abc import ABC, abstractmethod

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (QWidget, QTableWidgetItem, QMessageBox)
from bookkeeper.view.presenters import BudgetPresenter
from bookkeeper.repository.repository_factory import RepositoryFactory
from bookkeeper.models.budget import Budget


class AbstractItem(ABC):
    """Class represents abstract widget item.
    """
    @abstractmethod
    def get_value(self) -> None | float:
        """Returns converted value or None, if convertion is impossible.
        """

    @abstractmethod
    def update(self, bgt: Budget) -> None:
        """Sets new budget.
        """

    @abstractmethod
    def get(self) -> Budget:
        """Returns budget.
        """


class LimitDayItem(QTableWidgetItem):
    """Class represents Item with Day settings.
    """
    __metaclass__ = AbstractItem

    def __init__(self, bgt: Budget):
        super().__init__()
        self.update(bgt)

    def get_value(self) -> None | float:
        """Returns converted value or None, if convertion is impossible.
        """
        try:
            return float(self.text())
        except ValueError:
            return None

    def update(self, bgt: Budget) -> None:
        """Sets new budget.
        """
        self.bgt = bgt
        self.setText(str(round(self.bgt.amount, 2)))

    def get(self) -> Budget:
        """Returns budget.
        """
        return self.bgt


class LimitWeekItem(QTableWidgetItem):
    """Class represents Item with Week settings.
    """
    __metaclass__ = AbstractItem

    def __init__(self, bgt: Budget):
        super().__init__()
        self.update(bgt)

    def get_value(self) -> None | float:
        """Returns converted value or None, if convertion is impossible.
        """
        try:
            return float(self.text()) / 7
        except ValueError:
            return None

    def update(self, bgt: Budget) -> None:
        """Sets new budget.
        """
        self.bgt = bgt
        self.setText(str(round(self.bgt.amount * 7, 2)))

    def get(self) -> Budget:
        """Returns budget.
        """
        return self.bgt


class LimitMonthItem(QTableWidgetItem):
    """Class represents Item with Month settings.
    """
    __metaclass__ = AbstractItem

    def __init__(self, bgt: Budget):
        super().__init__()
        self.update(bgt)

    def get_value(self) -> None | float:
        """Returns converted value or None, if convertion is impossible.
        """
        try:
            return float(self.text()) / 30
        except ValueError:
            return None

    def update(self, bgt: Budget) -> None:
        """Sets new budget.
        """
        self.bgt = bgt
        self.setText(str(round(self.bgt.amount * 30, 2)))

    def get(self) -> Budget:
        """Returns budget.
        """
        return self.bgt


class BudgetWidget(QWidget):
    """Class represents Budget Widget.
    """
    bgt_getter: Callable[[], Budget]
    bgt_modifier: Callable[[Budget], None]
    exp_getter: Callable[[], list[float]]

    def __init__(self, exp_presenter: Any) -> None:
        super().__init__()
        self.exp_presenter = exp_presenter

        layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Бюджет")
        layout.addWidget(message)

        self.expenses_table = QtWidgets.QTableWidget(2, 3)
        self.expenses_table.setColumnCount(2)
        self.expenses_table.setRowCount(3)
        self.expenses_table.setHorizontalHeaderLabels("Сумма "
                                                      "Бюджет ".split())
        self.expenses_table.setVerticalHeaderLabels("День "
                                                    "Неделя "
                                                    "Месяц ".split())

        resize = QtWidgets.QHeaderView.ResizeToContents  # type: ignore[attr-defined]
        stretch = QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, resize)
        header.setSectionResizeMode(1, stretch)

        for i in range(3):
            lost_item = QtWidgets.QTableWidgetItem()
            lost_item.setFlags(lost_item.flags() &
                               ~QtCore.Qt.ItemIsEditable)  # type: ignore[attr-defined]
            self.expenses_table.setItem(i, 0, lost_item)

        bgt: Budget = Budget(1)
        self.expenses_table.setItem(0, 1, LimitDayItem(bgt))
        self.expenses_table.setItem(1, 1, LimitWeekItem(bgt))
        self.expenses_table.setItem(2, 1, LimitMonthItem(bgt))
        self.sign = self.expenses_table.itemChanged  # type: ignore[attr-defined]
        self.sign.connect(self.edit_bgt_event)

        layout.addWidget(self.expenses_table)
        self.setLayout(layout)

        self.presenter = BudgetPresenter(self, RepositoryFactory())

        expenses = self.exp_getter()
        bgt = self.bgt_getter()

        self.update_expenses(expenses)
        self.update_budget(bgt)

    def register_bgt_getter(self, handler: Callable[[], Budget]) -> None:
        """Registers bgt_getter.
        """
        self.bgt_getter = handler

    def register_bgt_modifier(self, handler: Callable[[Budget], None]) -> None:
        """Registers bgt_modifier.
        """
        self.bgt_modifier = handler

    def register_exp_getter(self, handler: Callable[[], list[float]]) -> None:
        """Registers exp_getter.
        """
        self.exp_getter = handler

    def edit_bgt_event(self, bgt_item: AbstractItem) -> None:
        """Event to process editing budget.

        Args:
            bgt_item (AbstractItem): Budget to edit.
        """
        value = bgt_item.get_value()
        if value is None:
            QMessageBox.critical(self, 'Ошибка', 'Используйте только числа.')
        else:
            bgt_item.get().amount = value
            self.bgt_modifier(bgt_item.get())

        self.update_budget(bgt_item.get())

    def update_expenses(self, exps: list[float]) -> None:
        """Updates table records responsible for expenses.

        Args:
            exps (list[float]): expenses to set.
        """
        self.sign.disconnect()
        assert len(exps) == 3
        for i, exp in enumerate(exps):
            self.expenses_table.item(i, 0).setText(str(round(exp, 2)))
        self.sign.connect(self.edit_bgt_event)

    def update_budget(self, bgt: Budget) -> None:
        """Updates table records responsible for budget.

        Args:
            bgt (Budget): budget to set.
        """
        self.sign.disconnect()
        for i in range(3):
            bitem = self.expenses_table.item(i, 1)
            assert isinstance(bitem, (LimitDayItem, LimitMonthItem, LimitWeekItem))
            bitem.update(bgt)
        self.sign.connect(self.edit_bgt_event)

    def retrieve_exp(self) -> None:
        """Gets expenses from ExpensesWidget and updates expenses.
        """
        self.update_expenses(self.exp_getter())
