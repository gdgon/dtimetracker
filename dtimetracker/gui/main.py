import tkinter as tk
from tkinter import ttk
from dtimetracker.core import Session
from .sessions import SessionsWindow
from .projects import ProjectsWindow
from .reports import ReportsWindow
from datetime import datetime, timedelta, date
from os.path import dirname, join
from dtimetracker.persistence import SQLitePersistence


class App(tk.Tk):
    def init_widgets(self):
        # indicator
        self.indicator_text_var = tk.StringVar(self, value="Not tracking")
        self.indicator = ttk.Label(self, textvariable=self.indicator_text_var)
        self.indicator.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

        # project selector
        self.project_selector_var = tk.StringVar()
        project_selector = ttk.OptionMenu(
            self,
            self.project_selector_var)
        project_selector.grid(column=0, row=1, columnspan=2, padx=5, pady=5)
        self.project_menu = project_selector['menu']

        # button stop/stop
        self.toggle_button_text_var = tk.StringVar(self, value="Start")
        toggle_button = ttk.Button(
            self, textvariable=self.toggle_button_text_var,
            command=self.clicked_toggle_button)
        toggle_button.grid(column=0, row=2, columnspan=2, padx=5, pady=5)

        # today
        today_label = ttk.Label(self, text="Today")
        today_label.grid(column=0, row=3, padx=5, pady=5)

        self.today_time_var = tk.StringVar()
        today_time = ttk.Label(self, textvariable=self.today_time_var)
        today_time.grid(column=1, row=3)

        # this week
        week_label = ttk.Label(self, text="This week")
        week_label.grid(column=0, row=4, padx=5, pady=5)

        self.week_time_var = tk.StringVar()
        week_time = ttk.Label(self, textvariable=self.week_time_var)
        week_time.grid(column=1, row=4, padx=5, pady=5)

        # this month
        month_label = ttk.Label(self, text="This month")
        month_label.grid(column=0, row=5, padx=5, pady=5)

        self.month_time_var = tk.StringVar()
        month_time = ttk.Label(self, textvariable=self.month_time_var)
        month_time.grid(column=1, row=5, padx=5, pady=5)

        # button projects
        projects_button = ttk.Button(
            self, text="Projects", command=lambda: ProjectsWindow(self))
        projects_button.grid(column=0, row=6, columnspan=2, padx=5, pady=5)

        # button sessions
        sessions_button = ttk.Button(
            self, text="Sessions", command=lambda: SessionsWindow(self))
        sessions_button.grid(column=0, row=7, columnspan=2, padx=5, pady=5)

        # button reports
        reports_button = ttk.Button(
            self, text="Reports", command=lambda: ReportsWindow(self))
        reports_button.grid(column=0, row=8, columnspan=2, padx=5, pady=5)

    def __init__(self):
        super().__init__()
        # self.geometry("300x400")
        self.title('dtimetracker')
        # self.set_theme('awdark')

        # vars
        self.is_tracking = tk.BooleanVar(self, value=False)
        self.selected_project = None

        self.init_widgets()
        self.set_project_optionmenu_default()
        self.populate_project_optionmenu()

    def set_theme(self, theme):
        project_root = dirname(dirname(__file__))
        theme_path = join(project_root, 'awthemes-10.4.0')
        print(theme_path)
        self.tk.call('lappend', 'auto_path', theme_path)
        self.tk.call('package', 'require', theme)

        style = ttk.Style()
        style.theme_use(theme)
        # self.configure(bg='#33393B')

    def set_project_optionmenu_default(self):
        project_names = SQLitePersistence.get_project_names()
        if (self.selected_project is None
                and project_names):

            self.project_selector_var.set(project_names[0])
            self.clicked_project(project_names[0])

    def populate_project_optionmenu(self):
        project_names = SQLitePersistence.get_project_names()

        if not project_names:
            return

        for project_name in project_names:
            self.project_menu.add_command(
                label=project_name,
                command=lambda n=project_name: self.clicked_project(n))

    def _get_total_duration_string(self, start, end):
        sessions = SQLitePersistence.get_sessions(
            self.selected_project.id, start, end)
        total_time = Session.compute_total_duration(sessions)

        hours_str = str(total_time[0]).zfill(2)
        minutes_str = str(total_time[1]).zfill(2)
        time_str = f"{hours_str}:{minutes_str}"

        return time_str

    def clicked_project(self, project_name):
        self.project_selector_var.set(project_name)
        self.selected_project = SQLitePersistence.get_project_by_name(
            self.project_selector_var.get())

        open_session = SQLitePersistence.get_open_session(
            self.selected_project.id)
        if open_session:
            self.is_tracking.set(True)
        else:
            self.is_tracking.set(False)

        self.update()

    def update(self, *args):
        if self.selected_project is None:
            return

        self.update_project_option_menu()
        self.update_session_summaries()
        self.update_track_status()

    def update_project_option_menu(self):
        # delete options in optionmenu
        self.project_menu.delete(0, 'end')

        project_names = SQLitePersistence.get_project_names()
        # update selected project if the current selected was deleted
        if self.project_selector_var.get() not in project_names:
            self.project_selector_var.set(project_names[0])

        self.populate_project_optionmenu()

    def clicked_toggle_button(self):
        if self.is_tracking.get():
            session = SQLitePersistence.get_open_session(
                self.selected_project.id)
            session.stop()
            SQLitePersistence.update_session(session)
        else:
            SQLitePersistence.create_session(self.selected_project.id)

        new_status = not self.is_tracking.get()
        self.is_tracking.set(new_status)

        self.update_track_status()

    def update_track_status(self):
        if self.is_tracking.get():
            self.toggle_button_text_var.set("Stop")
            self.indicator_text_var.set("Tracking")
        else:
            self.toggle_button_text_var.set("Start")
            self.indicator_text_var.set("Not tracking")

    def update_session_summaries(self):
        # update_today
        start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59)
        time_str = self._get_total_duration_string(start, end)
        self.today_time_var.set(time_str)

        # update_week)
        start = date.today() - timedelta(days=date.today().weekday())
        end = datetime.now().replace(hour=23, minute=59, second=59)
        time_str = self._get_total_duration_string(start, end)
        self.week_time_var.set(time_str)

        # update_moth)
        start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        end = datetime.now()
        time_str = self._get_total_duration_string(start, end)
        self.month_time_var.set(time_str)
