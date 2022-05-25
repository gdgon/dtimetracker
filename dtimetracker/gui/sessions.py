import tkinter as tk
from tkinter import ttk
from dtimetracker.persistence import SQLitePersistence
from .child import ChildWindow
from datetime import datetime, date, time, timedelta


class SessionsWindow(ChildWindow):
    def init_widgets(self):
        # project selector
        project_label = tk.Label(self, text="Project")
        project_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)

        self.project_selector_var = tk.StringVar()
        project_selector = ttk.OptionMenu(
            self,
            self.project_selector_var)
        project_selector.grid(column=1, row=0, columnspan=3, padx=5, pady=5)
        self.project_menu = project_selector['menu']

        # time selector
        time_label = tk.Label(self, text="Scope")
        time_label.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)

        self.time_name_var = tk.StringVar()
        time_selector = ttk.OptionMenu(
            self,
            self.time_name_var)
        time_selector.grid(column=1, row=1, columnspan=3, padx=5, pady=5)
        self.time_menu = time_selector['menu']

        subframe = self.init_scrollbar(
            row=4, column=0, columnspan=4)['subframe']

        # header
        #   Start
        start_label = ttk.Label(subframe, text="Start")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        #   End
        end_label = ttk.Label(subframe, text="End")
        end_label.grid(row=0, column=1, padx=5, pady=5)
        #   Duration
        duration_label = ttk.Label(subframe, text="Duration")
        duration_label.grid(row=0, column=2, padx=5, pady=5)
        #   Sort
        sort_label = ttk.Label(subframe, text="sort")
        sort_label.grid(row=0, column=3, padx=5, pady=5)

    def __init__(self, root):
        super().__init__(root)
        self.init_widgets()
        self.selected_project = None
        self.selected_time_string = ''

        self.set_project_optionmenu_default()
        self.set_time_optionmenu_default()
        self.update()

    def set_project_optionmenu_default(self):
        project_names = SQLitePersistence.get_project_names()

        if (project_names
                and not self.selected_project):
            self.project_selector_var.set(project_names[0])
            self.selected_project = SQLitePersistence.get_project_by_name(
                                        project_names[0])

    def set_time_optionmenu_default(self):
        if not self.selected_time_string:
            self.time_name_var.set("Today")

    def update(self):
        self.update_project_optionmenu()
        self.update_time_optionmenu()
        self.update_session_rows()

    def update_session_rows(self):
        start, end = self.get_date_range()
        print(start)
        print(end)
        print()
        sessions = SQLitePersistence.get_sessions(
            self.selected_project.id, start, end)
        row_num = 1

        if not hasattr(self, "session_row_dict"):
            self.session_row_dict = {}

        # Delete existing rows
        for key in self.session_row_dict:
            self.session_row_dict[key].destroy()

        for session in sessions:
            self.session_row_dict[session.id] = SessionRow(
                self.subframe, self, row_num, session)
            row_num += 1

    def clicked_project(self, project_name):
        self.selected_project = SQLitePersistence.get_project_by_name(
            project_name)
        self.project_selector_var.set(self.selected_project.name)
        self.update()

    def update_project_optionmenu(self):
        self.project_menu.delete(0, 'end')

        project_names = SQLitePersistence.get_project_names()
        # update selected project if the current selected was deleted
        if self.project_selector_var.get() not in project_names:
            self.project_selector_var.set(project_names[0])

        self.populate_project_optionmenu()

    def populate_project_optionmenu(self):
        project_names = SQLitePersistence.get_project_names()

        for project_name in project_names:
            self.project_menu.add_command(
                label=project_name,
                command=lambda n=project_name: self.clicked_project(n))

    def update_time_optionmenu(self):
        self.time_menu.delete(0, 'end')
        self.populate_time_optionmenu()

    def clicked_time(self, time_string):
        self.selected_time_string = time_string
        self.time_name_var.set(time_string)
        self.update()

    def populate_time_optionmenu(self):
        time_strings = (
            "Today",
            "Yesterday",
            "This week",
            "Last week",
            "This month",
            "Last month",
            "Last 7 days",
            "Last 30 days",
            # "Custom"
        )

        for ts in time_strings:
            self.time_menu.add_command(
                label=ts,
                command=lambda ts=ts: self.clicked_time(ts))

    def get_date_range(self):
        match self.time_name_var.get():
            case "Today":
                start = date.today()
                end = datetime.combine(date.today(), time(23, 59, 59, 999))
                return (start, end)
            case "Yesterday":
                yesterday = date.today() - timedelta(days=1)
                end = datetime.combine(yesterday, time(23, 59, 59, 999))
                return (yesterday, end)
            case "This week":
                today = date.today()
                last_monday = today - timedelta(days=today.weekday())
                end = datetime.combine(today, time(23, 59, 59, 999))
                return (last_monday, end)
            case "Last week":
                today = date.today()
                last_second_monday = (today
                                      - timedelta(days=today.weekday())
                                      - timedelta(days=7))
                end = (datetime.combine(last_second_monday,
                                        time(23, 59, 59, 999))
                       + timedelta(days=6))
                return (last_second_monday, end)
            case "This month":
                today = date.today()
                first_of_month = (today.replace(day=1))
                end = datetime.combine(today, time(23, 59, 59, 999))
                return (first_of_month, end)
            case "Last month":
                today = date.today()
                first_of_this_month = (today.replace(day=1))
                first_of_last_month = (
                    first_of_this_month -
                    timedelta(
                        days=1)).replace(
                    day=1)
                end_of_last_month = (
                    datetime.combine(first_of_this_month, time())
                    - timedelta(microseconds=1))

                return (first_of_last_month, end_of_last_month)
            case "Last 7 days":
                today = date.today()
                start = today - timedelta(days=6)
                end = datetime.combine(start, time(23, 59, 59, 999))
                return (start, end)
            case "Last 30 days":
                today = date.today()
                start = today - timedelta(days=29)
                end = datetime.combine(today, time(23, 59, 59, 999))
                return (start, end)
            # case "Custom":
                # result = CustomDateSelectionWindow()
                # print(result)


class SessionRow():
    def __init__(self, root, toplevel, row_number, session):
        self.toplevel = toplevel
        # Session row
        #   Start
        self.start_label = ttk.Label(
            root, text=session.start.strftime("%b %d, %H:%M"))
        self.start_label.grid(row=row_number, column=0, padx=5, pady=5)
        #   End
        end_string = ""
        if session.end:
            end_string = session.end.strftime("%b %d, %H:%M")
        else:
            end_string = "Open"
        self.end_label = ttk.Label(root,
                                   text=end_string)
        self.end_label.grid(row=row_number, column=1, padx=5, pady=5)
        #   Duration
        self.duration_label = ttk.Label(
            root, text=str(session.get_pretty_duration()))
        self.duration_label.grid(row=row_number, column=2, padx=5, pady=5)
        #   Edit
        self.edit_label = ttk.Button(
            root,
            text="Edit",
            command=lambda: EditSessionWindow(self))
        self.edit_label.grid(row=row_number, column=3, padx=5, pady=5)
        #   Delete
        self.delete_label = ttk.Button(
            root,
            text="Delete",
            command=lambda: self.deleteSession(session))
        self.delete_label.grid(row=row_number, column=4, padx=5, pady=5)

    def destroy(self):
        self.start_label.destroy()
        self.end_label.destroy()
        self.duration_label.destroy()
        self.edit_label.destroy()
        self.delete_label.destroy()
        del self

    def deleteSession(self, session):
        SQLitePersistence.delete_session(session)
        self.toplevel.update()


class EditSessionWindow(ChildWindow):
    def __init__(rootself, root):
        super().__init__(root)


class ReportsWindow(ChildWindow):
    def __init__(rootself, root):
        super().__init__(root)


class MakeCSVWindow(ChildWindow):
    def __init__(rootself, root):
        super().__init__(root)


class CustomDateSelectionWindow(ChildWindow):
    def __init__(rootself, root):
        super().__init__(root)
