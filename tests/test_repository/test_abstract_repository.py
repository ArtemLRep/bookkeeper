from bookkeeper.repository.abstract_repository import AbstractRepository

import pytest


def test_cannot_create_abstract_repository():
    with pytest.raises(TypeError):
        AbstractRepository()


def test_can_create_subclass():
    class Test(AbstractRepository):
        def add(self, obj): pass
        def get_by_pk(self, pk): pass
        def get_all(self, where=None): pass
        def update_by_pk(self, obj): pass
        def delete_by_pk(self, pk): pass

    t = Test()
    assert isinstance(t, AbstractRepository)
