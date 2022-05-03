from dtimetracker.core import Project, Session
from datetime import datetime, timedelta
import pytest

def test_can_edit_project_name():
    p = Project("Test Project")
    p.name = "Renamed Project"
    assert p.name == "Renamed Project"


@pytest.fixture
def test_project():
    p = Project("Test Project")
    p.id = 1
    return p

def test_can_create_session(test_project):
    s = Session(test_project)
    t = datetime.now().replace(microsecond=0)
    assert s.start == t


def test_can_compute_ended_session(test_project):
    expected_hours = 3
    expected_minutes = 33

    test_start_time = (
        datetime.now().replace(microsecond=0)
        - timedelta(hours=expected_hours)
        - timedelta(minutes=expected_minutes)
    )
    test_end_time = datetime.now().replace(microsecond=0)

    s = Session(test_project)
    s.start = test_start_time
    s.end = test_end_time

    computed = s.compute_duration()
    assert computed == (expected_hours, expected_minutes)


def test_can_compute_open_session(test_project):
    expected_hours = 3
    expected_minutes = 33

    test_start_time = (
        datetime.now().replace(microsecond=0)
        - timedelta(hours=expected_hours)
        - timedelta(minutes=expected_minutes)
    )

    s = Session(test_project)
    s.start = test_start_time

    computed = s.compute_duration()
    assert computed == (expected_hours, expected_minutes)
