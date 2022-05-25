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
    def get_project_names(cls):
        projects = SQLitePersistence.get_projects()
        project_names = []
        for project in projects:
            project_names.append(project.name)
        return project_names

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
                name TEXT NOT NULL UNIQUE
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

        con.commit()

    @classmethod
    def init_db(cls):
        SQLitePersistence._create_tables()
        return SQLitePersistence

    @classmethod
    def delete_db(cls):
        con = SQLitePersistence._get_connection()
        con.commit()
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

        if result is None:
            return None
        else:
            project = Project(name=result[1], id=result[0])
            return project

    @classmethod
    def get_project_by_name(cls, project_name):
        query = "SELECT * FROM projects WHERE name = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (project_name,))
        result = cur.fetchone()

        if result is None:
            return None
        else:
            project = Project(name=result[1], id=result[0])
            return project

    @classmethod
    def create_project(cls, project_name):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO projects (name) VALUES (?) """,
            (project_name,)
        )
        con.commit()

        p = Project(name=project_name, id=cur.lastrowid)
        return p

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
        con.commit()

    @classmethod
    def delete_project(cls, project):
        query = "DELETE FROM projects WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(query, (project.id,))
        con.commit()

    @classmethod
    def create_session(cls, project_id, start_=None, end_=None):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        start = None
        if start_ is None:
            start = (datetime.now()
                     .replace(microsecond=0)
                     .strftime("%Y-%m-%d %H:%M:%S"))
        else:
            start = (start_
                     .replace(microsecond=0)
                     .strftime("%Y-%m-%d %H:%M:%S"))

        if end_ is None:
            cur.execute(
                """INSERT INTO sessions (start, project_id) VALUES (?, ?) """,
                (start, project_id)
            )
        else:
            end = datetime.strftime(end_, "%Y-%m-%d %H:%M:%S")
            cur.execute(
                """INSERT INTO sessions (start, end, project_id)
                    VALUES (?, ?, ?) """,
                (start, end, project_id))

        id = cur.lastrowid
        con.commit()
        return SQLitePersistence.get_session(id)

    @classmethod
    def get_session(cls, session_id):
        query = "SELECT * FROM sessions WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (session_id,))
        result = cur.fetchone()

        if result is None:
            return None
        else:
            return Session.from_sql_result(result)

    @classmethod
    def get_sessions(cls, project_id, from_, to):
        query = """
            SELECT * FROM sessions WHERE
            project_id = ?
            AND start BETWEEN ? AND ?
        """

        query_from = from_.strftime("%Y-%m-%d %H:%M:%S")
        query_to = to.strftime("%Y-%m-%d %H:%M:%S")

        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        cur.execute(query, (project_id, query_from, query_to))

        results = cur.fetchall()

        sessions = []
        for result in results:
            s = Session.from_sql_result(result)
            sessions.append(s)

        return sessions

    @classmethod
    def update_session(cls, updated_session):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        updated_start = updated_session.start.strftime("%Y-%m-%d %H:%M:%S")

        updated_end = ""

        if updated_session.end is None:
            updated_end = None
        else:
            updated_end = updated_session.end.strftime("%Y-%m-%d %H:%M:%S")

        query = """
            UPDATE sessions
            SET project_id = ?, start = ?, end = ?
            WHERE id = ?;
        """

        values = (updated_session.project_id, updated_start,
                  updated_end, updated_session.id)

        cur.execute(query, values)
        con.commit()

    @classmethod
    def delete_session(cls, session):
        query = "DELETE FROM sessions WHERE id = ?;"
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(query, (session.id,))
        con.commit()

    @classmethod
    def get_open_session(cls, project_id):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()

        query = """
            SELECT * FROM sessions WHERE
            project_id = ?
            AND end IS NULL;
        """

        cur.execute(query, (project_id,))

        result = cur.fetchone()

        if result is None:
            return None
        else:
            return Session.from_sql_result(result)
