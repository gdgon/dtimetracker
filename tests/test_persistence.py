from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Project
import pytest


@pytest.fixture
def test_sqlite():
    s = SQLitePersistence.init_db()
    p1 = Project("A Project")
    p2 = Project("B Project")
    p3 = Project("C Project")
    s.create_project(p1)
    s.create_project(p2)
    s.create_project(p3)
    return s


def test_can_get_projects(test_sqlite):
    s = test_sqlite
    projects = s.get_projects()

    assert len(projects) == 3
    assert projects[0].name == "A Project"
    assert projects[1].name == "B Project"
    assert projects[2].name == "C Project"

    s.delete_db()


def test_can_update_project(test_sqlite):
    s = test_sqlite
    projects = s.get_projects()
    s.update_project(projects[0], "Renamed Project")
    projects = s.get_projects()
    assert projects[0].name == "Renamed Project"

    s.delete_db()
