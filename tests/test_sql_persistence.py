from datetime import datetime, timedelta
from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Project, Session
# from unittest.mock


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
    session1 = Session(1)
    session1.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=3))
    session1.end = session1.start + timedelta(hours=6, minutes=30, seconds=20)

    session2 = Session(1)
    session2.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=2))
    session2.end = session2.start + timedelta(hours=6, minutes=20, seconds=20)

    session3 = Session(1)
    session3.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=1))
    session3.end = session3.start + timedelta(hours=8, minutes=30, seconds=20)

    session4 = Session(2)
    session4.start = (datetime.now().replace(microsecond=0)
                      - timedelta(days=3))
    session4.end = (session4.start
                    + timedelta(days=1, hours=8, minutes=30, seconds=20))

    session5 = Session(2)
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


def test_get_project_returns_none():
    init_sqlite()
    init_projects()

    assert SQLitePersistence.get_project(999) is None


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

    project = SQLitePersistence.get_project(1)
    SQLitePersistence.delete_project(project)

    assert SQLitePersistence.get_project(project.id) is None


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
    project0_sessions = SQLitePersistence.get_sessions(
        projects[0].id, start, end)

    assert len(project0_sessions) == 2


def test_get_session_returns_none():
    init_sqlite()
    init_projects()
    init_sessions()

    assert SQLitePersistence.get_session(999) is None


def test_can_get_session_by_id():
    init_sqlite()
    init_projects()
    init_sessions()

    s = SQLitePersistence.get_session(4)

    # TODO: Mock datetime.now to something predictable

    assert s.project_id == 2


def test_can_update_session():
    init_sqlite()
    init_projects()
    init_sessions()

    old_session = SQLitePersistence.get_session(1)

    new_start = datetime.now().replace(microsecond=0) - timedelta(days=3)
    new_end = new_start + timedelta(hours=5)
    new_project_id = 2

    SQLitePersistence.update_session(
        Session(
            new_project_id,
            id=old_session.id,
            start=new_start,
            end=new_end
        )
    )

    new_session = SQLitePersistence.get_session(old_session.id)

    assert new_session.project_id == new_project_id
    assert new_session.start == new_start
    assert new_session.end == new_end


def test_can_delete_session():
    init_sqlite()
    init_projects()
    init_sessions()

    s = SQLitePersistence.get_session(1)
    SQLitePersistence.delete_session(s)

    assert SQLitePersistence.get_session(s.id) is None


def test_get_open_session_works():
    init_sqlite()
    init_projects()
    init_sessions()

    s = SQLitePersistence.get_session(2)
    s.end = None
    SQLitePersistence.update_session(s)
    result = SQLitePersistence.get_open_session(1)
    assert result.id == s.id
    assert result.project_id == s.project_id
    assert result.start == s.start

    s.end = s.start + timedelta(hours=8)
    SQLitePersistence.update_session(s)
    assert SQLitePersistence.get_open_session(1) is None
