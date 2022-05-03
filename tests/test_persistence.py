from datetime import datetime, timedelta
from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Project, Session


def init_sqlite():
    SQLitePersistence.delete_db()
    SQLitePersistence.init_db()


def init_projects():
    p1 = Project("A Project")
    p2 = Project("B Project")
    p3 = Project("C Project")
    SQLitePersistence.create_project(p1)
    SQLitePersistence.create_project(p2)
    SQLitePersistence.create_project(p3)


def init_sessions():
    projects = SQLitePersistence.get_projects()

    session1 = Session(projects[0].id)
    session1.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=3))
    session1.end = session1.start + timedelta(hours=6, minutes=30, seconds=20)

    session2 = Session(projects[0].id)
    session2.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=2))
    session2.end = session2.start + timedelta(hours=6, minutes=20, seconds=20)

    session3 = Session(projects[0].id)
    session3.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=1))
    session3.end = session3.start + timedelta(hours=8, minutes=30, seconds=20)

    session4 = Session(projects[1].id)
    session4.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=3))
    session4.end = (session4.start
                    + timedelta(days=1, hours=8, minutes=30, seconds=20))

    session5 = Session(projects[1].id)
    session5.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=1))
    session5.end = session5.start + timedelta(hours=8, minutes=30)

    SQLitePersistence.create_session(session1)
    SQLitePersistence.create_session(session2)
    SQLitePersistence.create_session(session3)
    SQLitePersistence.create_session(session4)
    SQLitePersistence.create_session(session5)


def test_can_get_projects():
    init_sqlite()
    init_projects()

    projects = SQLitePersistence.get_projects()

    assert len(projects) == 3
    assert projects[0].name == "A Project"
    assert projects[1].name == "B Project"
    assert projects[2].name == "C Project"


def test_can_get_project_by_id():
    init_sqlite()
    init_projects()

    project = SQLitePersistence.get_project(2)

    assert project.name == "B Project"


def test_can_update_project():
    init_sqlite()
    init_projects()

    projects = SQLitePersistence.get_projects()
    SQLitePersistence.update_project(projects[0], "Renamed Project")
    projects = SQLitePersistence.get_projects()

    assert projects[0].name == "Renamed Project"


def test_can_delete_project():
    init_sqlite()
    init_projects()

    projects_before_delete = SQLitePersistence.get_projects()
    del_project = projects_before_delete[0]

    SQLitePersistence.delete_project(del_project)

    projects_after_delete = SQLitePersistence.get_projects()

    assert len(projects_before_delete) == 3
    assert len(projects_after_delete) == 2
    assert del_project.name != projects_after_delete[0].name
    assert del_project.name != projects_after_delete[1].name


def test_can_create_sessions_with_correct_start_time():
    init_sqlite()
    init_projects()

    project = SQLitePersistence.get_projects()[0]
    session = Session(project.id)
    session = SQLitePersistence.create_session(session)

    assert session.start == datetime.now().replace(microsecond=0)


def test_can_get_sessions():
    init_sqlite()
    init_projects()
    init_sessions()

    projects = SQLitePersistence.get_projects()

    start = datetime.now().replace(microsecond=0) - timedelta(days=2)
    end = datetime.now()
    project0_sessions = SQLitePersistence.get_sessions(projects[0].id, start, end)

    assert len(project0_sessions) == 2
