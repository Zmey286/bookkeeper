"""Module for repository factory.
"""

from abc import ABC, abstractmethod
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class AbsRepoFactory(ABC):
    """Represents abstract repository factory.
    """
    @abstractmethod
    def get_ctg(self) -> AbstractRepository[Category]:
        """Returns AbstractRepository for Category
        """

    @abstractmethod
    def get_bgt(self) -> AbstractRepository[Budget]:
        """Returns AbstractRepository for Category
        """

    @abstractmethod
    def get_exp(self) -> AbstractRepository[Expense]:
        """Returns AbstractRepository for Category
        """


class RepositoryFactory(AbsRepoFactory):
    """Represents SQLiteRepository repository factory.
    """
    def get_ctg(self) -> AbstractRepository[Category]:
        """Returns SQLiteRepository for Category
        """
        return SQLiteRepository[Category]("databases/ui_client.db", Category)

    def get_bgt(self) -> AbstractRepository[Budget]:
        """Returns SQLiteRepository for Category
        """
        return SQLiteRepository[Budget]("databases/ui_client.db", Budget)

    def get_exp(self) -> AbstractRepository[Expense]:
        """Returns SQLiteRepository for Category
        """
        return SQLiteRepository[Expense]("databases/ui_client.db", Expense)
