from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3
import os
from .core import Project, Session


class PersistenceBaseClass(ABC):

    @classmethod
    @abstractmethod
    def get_projects(cls):
        pass

    @classmethod
    @abstractmethod
    def create_project(cls, project):
        pass

    @classmethod
    @abstractmethod
    def update_project(cls, project, new_name):
        pass

    @classmethod
    @abstractmethod
    def delete_project(cls, project):
        pass

    @classmethod
    @abstractmethod
    def get_sessions(cls, project, from_, to):
        pass

    @classmethod
    @abstractmethod
    def create_session(cls, session):
        pass

    @classmethod
    @abstractmethod
    def update_session(cls, session):
        pass

    @classmethod
    @abstractmethod
    def delete_session(cls, session):
        pass


class SQLitePersistence(PersistenceBaseClass):
    _db_name = "dtimetracker.db"
    _con = None

    @classmethod
    def _get_connection(cls):
        if SQLitePersistence._con is None:
            con = sqlite3.connect(SQLitePersistence._db_name)
            SQLitePersistence._con = con
            return SQLitePersistence._con
        else:
            return SQLitePersistence._con

    @classmethod
    def _create_tables(cls):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        create_projects_query = """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
        """

        create_sessions_table_query = """
            CREATE TABLE sessions (
                id INTEGER PRIMARY KEY,
                start TEXT    NOT NULL,
                end TEXT,
                project_id  INTEGER NOT NULL,
                FOREIGN KEY (project_id)
                REFERENCES projects (id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            );
        """

        cur.execute(create_projects_query)
        cur.execute(create_sessions_table_query)

    @classmethod
    def init_db(cls):
        SQLitePersistence._create_tables()
        return SQLitePersistence

    @classmethod
    def delete_db(cls):
        con = SQLitePersistence._get_connection()
        con.close()
        if os.path.exists(SQLitePersistence._db_name):
            os.remove(SQLitePersistence._db_name)
            SQLitePersistence._con = None

    @classmethod
    def get_projects(cls):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM projects;")
        results = cur.fetchall()

        projects = []
        for result in results:
            p = Project(name=result[1], id=result[0])
            projects.append(p)

        return projects

    @classmethod
    def get_project(cls, project_id):
        query = "SELECT * FROM projects WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (project_id,))
        result = cur.fetchone()

        project = Project(name=result[1], id=result[0])

        return project

    @classmethod
    def create_project(cls, project):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO projects (name) VALUES (?) """,
            (project.name,)
        )

        project.id = cur.lastrowid
        return project

    @classmethod
    def update_project(cls, project, new_name):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(
            """
                UPDATE projects
                SET name = ?
                WHERE id = ?;
            """,
            (new_name, project.id)
        )

    @classmethod
    def delete_project(cls, project):
        query = "DELETE FROM projects WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(query, (project.id,))

    @classmethod
    def create_session(cls, session):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        start = datetime.strftime(session.start, "%F")

        if session.end is not None:
            end = datetime.strftime(session.end, "%F")
            cur.execute(
                """INSERT INTO sessions (start, end, project_id) VALUES (?, ?, ?) """,
                (start, end, session.project_id))
        else:
            cur.execute(
                """INSERT INTO sessions (start, project_id) VALUES (?, ?) """,
                (start, session.project_id)
            )

        session.id = cur.lastrowid
        return session

    @classmethod
    def get_session(cls, session_id):
        query = "SELECT * FROM session WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (session_id,))
        result = cur.fetchone()

        session = Session(
            result[3],
            id=result[0],
            start=datetime.strptime(result[1], "%F"),
            end=datetime.strptime(result[2], "%F")
        )

        return session

    @classmethod
    def get_sessions(cls, project_id, from_, to):
        query = """
            SELECT * FROM sessions WHERE
            project_id = ?
            AND start BETWEEN ? AND ?
        """

        query_from = from_.strftime("%F")
        query_to = to.strftime("%F")

        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (project_id, query_from, query_to))

        results = cur.fetchall()

        sessions = []
        for result in results:
            s = Session(
                result[3],
                id=result[0],
                start=datetime.strptime(result[1], '%Y-%m-%d'),
                end=datetime.strptime(result[2], '%Y-%m-%d'),
            )

            sessions.append(s)

        return sessions
