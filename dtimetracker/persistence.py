from abc import ABC, abstractmethod
import sqlite3
import os
from .core import Project


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
    def get_sessions(cls, project_id, from_, to):
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
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """
        )

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
            p = Project(result[1])
            p.id = result[0]
            projects.append(p)

        return projects

    @classmethod
    def create_project(cls, project):
        con = SQLitePersistence._get_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO projects (name) VALUES (?) """,
            (project.name,)
        )

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
