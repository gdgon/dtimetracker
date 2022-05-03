from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Project


def init_sqlite():
    SQLitePersistence.delete_db()
    SQLitePersistence.init_db()
    p1 = Project("A Project")
    p2 = Project("B Project")
    p3 = Project("C Project")
    SQLitePersistence.create_project(p1)
    SQLitePersistence.create_project(p2)
    SQLitePersistence.create_project(p3)


def test_can_get_projects():
    init_sqlite()
    projects = SQLitePersistence.get_projects()

    SQLitePersistence.delete_db()

    assert len(projects) == 3
    assert projects[0].name == "A Project"
    assert projects[1].name == "B Project"
    assert projects[2].name == "C Project"


def test_can_update_project():
    init_sqlite()
    projects = SQLitePersistence.get_projects()
    SQLitePersistence.update_project(projects[0], "Renamed Project")
    projects = SQLitePersistence.get_projects()

    SQLitePersistence.delete_db()

    assert projects[0].name == "Renamed Project"

def test_can_delete_project():
    init_sqlite()

    projects_before_delete = SQLitePersistence.get_projects()
    del_project = projects_before_delete[0]

    SQLitePersistence.delete_project(del_project)

    projects_after_delete = SQLitePersistence.get_projects()

    SQLitePersistence.delete_db()

    assert len(projects_before_delete) == 3
    assert len(projects_after_delete) == 2
    assert del_project.name != projects_after_delete[0].name
    assert del_project.name != projects_after_delete[1].name
