import tkinter as tk
from tkinter import ttk
from dtimetracker.persistence import SQLitePersistence
from dtimetracker.core import Session
from .child import ChildWindow
from datetime import datetime, date, time, timedelta
from tkcalendar import Calendar


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
            command=lambda: EditSessionWindow(self.toplevel, session))
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
    def __init__(self, root, session):
        super().__init__(root)

        self.session = session
        self.root = root

        # start
        start_label = ttk.Label(self, text="Start")
        start_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # start date
        self.start_date_var = tk.StringVar()
        self.start_date_var.set(session.start.strftime("%x"))

        self.start_text_var = tk.StringVar(value=self.start_date_var.get())

        start_button = ttk.Button(
            self,
            textvariable=self.start_text_var,
            command=lambda: CalendarWindow(
                self,
                self.start_date_var,
                self.start_text_var))
        start_button.grid(row=2, column=1, padx=5, pady=5)

        # start time
        self.start_hour_string_var = tk.StringVar()
        self.start_hour_string_var.trace(
            "w", lambda name, index, mode: self.update_duration())
        self.start_min_string_var = tk.StringVar()
        self.start_min_string_var.trace(
            "w", lambda name, index, mode: self.update_duration())

        start_h = str(session.start.hour).zfill(2)
        start_m = str(session.start.minute).zfill(2)

        self.start_hour_string_var.set(start_h)
        self.start_min_string_var.set(start_m)

        start_time_picker = TimePicker(
            self,
            self.start_hour_string_var,
            self.start_min_string_var)
        start_time_picker.grid(row=2, column=2)

        # end label
        end_label = ttk.Label(self, text="End")
        end_label.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        # end date
        self.end_date_var = tk.StringVar()

        if session.end:
            self.end_date_var.set(session.end.strftime("%x"))
        else:
            self.end_date_var.set(date.today().strftime("%x"))

        self.end_text_var = tk.StringVar(value=self.end_date_var.get())

        end_button = ttk.Button(
            self,
            textvariable=self.end_text_var,
            command=lambda: CalendarWindow(
                self,
                self.end_date_var,
                self.end_text_var))
        end_button.grid(row=4, column=1, padx=5, pady=5)

        # end time
        self.end_hour_string_var = tk.StringVar()
        self.end_hour_string_var.trace(
            "w", lambda name, index, mode: self.update_duration())
        self.end_min_string_var = tk.StringVar()
        self.end_min_string_var.trace(
            "w", lambda name, index, mode: self.update_duration())

        end_h = ""
        end_m = ""

        if session.end:
            end_h = str(session.end.hour).zfill(2)
            end_m = str(session.end.minute).zfill(2)

        self.end_hour_string_var.set(end_h)
        self.end_min_string_var.set(end_m)

        end_time_picker = TimePicker(
            self,
            self.end_hour_string_var,
            self.end_min_string_var)
        end_time_picker.grid(row=4, column=2)

        # duration label
        duration_label = ttk.Label(self, text="Duration")
        duration_label.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        # duration
        duration = ""
        if session.end:
            duration = str(session.get_pretty_duration())
        else:
            duration = "Open"

        self.duration_time_label = ttk.Label(self, text=duration)
        self.duration_time_label.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

        # ok button
        ok_button = ttk.Button(self, text="Ok", command=self.clicked_ok)
        ok_button.grid(row=7, column=1, padx=5, pady=5)

        # cancel button
        cancel_button = ttk.Button(
            self,
            text="Cancel",
            command=self.clicked_cancel)
        cancel_button.grid(row=7, column=2, padx=5, pady=5)

    def clicked_ok(self):
        self.update()
        self.root.update()
        self.destroy()

    def clicked_cancel(self):
        self.destroy()

    def update(self):
        tmp_s = self.make_session_from_input()
        self.session.start = tmp_s.start
        self.session.end = tmp_s.end
        SQLitePersistence.update_session(self.session)

        # duration
        self.update_duration()

    def make_session_from_input(self):
        # TODO: PUT validation here
        start_date = datetime.strptime(self.start_date_var.get(), "%x").date()

        start_hour = 0
        if self.start_hour_string_var.get():
            start_hour = int(self.start_hour_string_var.get())

        start_min = 0
        if self.start_min_string_var.get():
            start_min = int(self.start_min_string_var.get())

        dt_start = datetime.combine(
            start_date,
            time(start_hour, start_min))

        end_date = datetime.strptime(self.end_date_var.get(), "%x").date()

        end_hour = 0
        if self.end_hour_string_var.get():
            end_hour = int(self.end_hour_string_var.get())

        end_min = 0
        if self.end_min_string_var.get():
            end_min = int(self.end_min_string_var.get())

        dt_end = datetime.combine(
            end_date,
            time(end_hour, end_min))

        s = Session(0)
        s.start = dt_start
        s.end = dt_end

        return s


    def update_duration(self):

        s = self.make_session_from_input()

        duration = str(s.get_pretty_duration())

        self.duration_time_label.config(
            text=duration)


    def validate_hour(self, value):
        if value == "":
            return True

        try:
            int(value)
        except ValueError:
            return False

        v = int(value)

        if v >= 0 and v < 24:
            self.update_duration()
            return True
        else:
            return False

    def validate_minute(self, value):
        if value == "":
            return True

        try:
            int(value)
        except ValueError:
            return False

        v = int(value)

        if v >= 0 and v < 60:
            self.update_duration()
            return True
        else:
            return False

class CalendarWindow(ChildWindow):
    def __init__(self, root, date_var, date_text_var):
        super().__init__(root)

        self.date_var = date_var
        self.date_text_var = date_text_var

        d = datetime.strptime(date_var.get(), "%x")
        self.cal = Calendar(self, selectmode="day", day=d.day,
                            month=d.month, year=d.year)
        self.cal.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        ok_button = ttk.Button(self, text="Ok", command=self.clicked_ok)
        ok_button.grid(row=2, column=1, padx=5, pady=5)

        cancel_button = ttk.Button(
            self, text="Cancel", command=self.clicked_cancel)
        cancel_button.grid(row=2, column=2, padx=5, pady=5)

    def clicked_ok(self):
        date = str(self.cal.get_date())
        self.date_var.set(date)
        self.date_text_var = self.format_date_var()
        self.destroy()

    def clicked_cancel(self):
        self.destroy()

    def format_date_var(self):
        d = datetime.strptime(self.date_var.get(), "%x").date()
        s = d.strftime("%b %d, %Y")
        self.root.update()
        self.date_text_var.set(s)


class TimePicker(tk.Frame):
    def __init__(self, root, hour_string, min_string):
        super().__init__(root)
        hour_vcmd = (root.register(root.validate_hour), '%P')
        self.hour_entry = ttk.Entry(
            self,
            validate='key',
            validatecommand = hour_vcmd,
            textvariable=hour_string,
            width=3)
        self.hour_entry.grid(row=1, column=1, padx=5, pady=5)

        colon = ttk.Label(self, text=":")
        colon.grid(row=1, column=2)

        minute_vcmd = (root.register(root.validate_minute), '%P')
        self.min_entry = ttk.Entry(
            self,
            validate='key',
            validatecommand=minute_vcmd,
            textvariable=min_string,
            width=3)
        self.min_entry.grid(row=1, column=3, padx=5, pady=5)


class ReportsWindow(ChildWindow):
    def __init__(self, root):
        super().__init__(root)


class MakeCSVWindow(ChildWindow):
    def __init__(self, root):
        super().__init__(root)


class CustomDateSelectionWindow(ChildWindow):
    def __init__(self, root):
        super().__init__(root)
