from dtimetracker.gui.main import App
from tests.test_sql_persistence import init_sqlite, init_projects, init_sessions

if __name__ == "__main__":
    init_sqlite()
    init_projects()
    init_sessions()

    app = App()
    app.update()
    app.mainloop()
