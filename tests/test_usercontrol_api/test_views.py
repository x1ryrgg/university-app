import pytest
from usercontrol_api.models import *


@pytest.fixture
def delete_groups():
    Group.objects.all().delete()

@pytest.fixture
def insert_group():
    Group.objects.create(
        name_group='test',
        age_group=2,
        students=[
            {"name": "Danil", "age": 20, "group": 1},
            {"name": "Juan", "age": 30, "group": 1},
        ]
    )


@pytest.mark.django_db
def test_add_students(delete_groups, insert_group):
    assert Group.objects.all().count() == 1
