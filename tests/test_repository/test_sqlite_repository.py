from bookkeeper.repository.sqlite_repository import SQLiteRepository

import pytest
from datetime import datetime


@pytest.fixture
def custom_class():
    class Custom():
        pk: int = 0
        name: str = "TEST"
        value: int = 42
        date: datetime = datetime.now()
        real: float = 5.0

        def __str__(self) -> str:
            return f'pk={self.pk} name={self.name} value={self.value}'

        def __eq__(self, other) -> bool:
            return self.pk == other.pk and self.name == other.name and self.value == other.value

    return Custom


@pytest.fixture
def repo(custom_class):
    return SQLiteRepository("databases/test_database.db", custom_class)


def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None

def test_update(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    obj.name = "NOTTEST"
    assert repo.get(pk) != obj
    repo.update(obj)
    assert repo.get(pk) == obj


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(-1)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, custom_class):
    repo.delete_all()
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    repo.delete_all()
    objects = []
    for i in range(5):
        o = custom_class()
        o.name = 'test'
        o.value = i
        repo.add(o)
        objects.append(o)

    assert repo.get_all({'value': 0}) == [objects[0]]
    assert repo.get_all({'name': 'test'}) == objects
