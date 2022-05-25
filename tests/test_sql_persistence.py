from datetime import datetime, timedelta, date
from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Project, Session
# from unittest.mock


def init_sqlite():
    SQLitePersistence.delete_db()
    SQLitePersistence.init_db()


def init_projects():
    SQLitePersistence.create_project("A Project")
    SQLitePersistence.create_project("B Project")
    SQLitePersistence.create_project("C Project")
    SQLitePersistence.create_project("D Project")
    SQLitePersistence.create_project("E Project")


def init_sessions():
    start = (datetime.now().replace(microsecond=0)
             - timedelta(days=3))
    end = start + timedelta(hours=6, minutes=30, seconds=20)
    SQLitePersistence.create_session(1, start, end)

    start = (datetime.now().replace(microsecond=0)
             - timedelta(days=2))
    end = start + timedelta(hours=6, minutes=20, seconds=20)
    SQLitePersistence.create_session(1, start, end)

    start = (datetime.now().replace(microsecond=0)
             - timedelta(days=1))
    end = start + timedelta(hours=8, minutes=30, seconds=20)
    SQLitePersistence.create_session(1, start, end)

    ## Project 2
    start = (datetime.now().replace(microsecond=0)
             - timedelta(days=3))
    end = (start
           + timedelta(days=1, hours=8, minutes=30, seconds=20))
    SQLitePersistence.create_session(2, start, end)

    start = (datetime.now().replace(microsecond=0)
             - timedelta(days=1))
    end = start + timedelta(hours=8, minutes=30)
    SQLitePersistence.create_session(2, start, end)

    ## Project 4
    start = (
        datetime.now().replace(hour=0, minute=15, second=0, microsecond=0))
    end = start + timedelta(hours=4, minutes=10, seconds=10)
    SQLitePersistence.create_session(4, start, end)

    start = (
        datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        - timedelta(days=1))
    end = start + timedelta(hours=4, minutes=10, seconds=10)
    SQLitePersistence.create_session(4, start, end)

    start = end + timedelta(hours=2)
    end = start + timedelta(hours=3, minutes=30)
    SQLitePersistence.create_session(4, start, end)

    start = (
        datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        - timedelta(days=2))
    end = start + timedelta(hours=8, minutes=20, seconds=10)
    SQLitePersistence.create_session(4, start, end)

    start = (
        datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        - timedelta(days=10))
    end = start + timedelta(hours=8, minutes=20, seconds=10)
    SQLitePersistence.create_session(4, start, end)

    start = (
        datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        - timedelta(days=15))
    end = start + timedelta(hours=8, minutes=20, seconds=10)
    SQLitePersistence.create_session(4, start, end)

    start = (
        datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    SQLitePersistence.create_session(5, start, None)


def test_can_get_projects():
    init_sqlite()
    init_projects()

    projects = SQLitePersistence.get_projects()

    assert projects[0].name == "A Project"
    assert projects[1].name == "B Project"
    assert projects[2].name == "C Project"


def test_can_get_project_by_id():
    init_sqlite()
    init_projects()

    project = SQLitePersistence.get_project(2)

    assert project.name == "B Project"


def test_can_get_project_by_name():
    init_sqlite()
    init_projects()
    init_sessions()

    project_name = SQLitePersistence.get_project_by_name("B Project").name
    assert project_name == "B Project"


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


# def test_can_create_sessions_with_correct_start_time():
    # init_sqlite()
    # init_projects()

    # project = SQLitePersistence.get_projects()[0]
    # session = SQLitePersistence.create_session(project.id, )

    # assert session.start == datetime.now().replace(microsecond=0)


def test_can_get_sessions():
    init_sqlite()
    init_projects()
    init_sessions()

    projects = SQLitePersistence.get_projects()

    start = date.today() - timedelta(days=2)
    end = datetime.now().replace(hour=23, minute=59, second=59)
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


def test_can_compute_total_session_duration():
    init_sqlite()
    init_projects()
    init_sessions()

    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    sessions = SQLitePersistence.get_sessions(1, start_date, end_date)

    result = Session.compute_total_duration(sessions)
    assert result == (21, 21, 0)
