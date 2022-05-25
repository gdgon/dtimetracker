import tkinter as tk
from tkinter import ttk, messagebox
from dtimetracker.persistence import SQLitePersistence
from .child import ChildWindow


class ProjectsWindow(ChildWindow):
    def init_widgets(self, root):
        self.subframe = self.init_scrollbar(row=1, column=0)['subframe']
        self.project_row_dict = {}

        # New project button
        new_project_button = ttk.Button(
            self, text="New project", command=lambda: NewProjectWindow(self))
        new_project_button.grid(column=0, row=0, padx=5, pady=5)

    def __init__(self, root):
        super().__init__(root)
        self.title("Projects")
        self.init_widgets(root)
        self.update()

    def update(self):
        projects = SQLitePersistence.get_projects()

        # Delete project rows
        if self.project_row_dict:
            for key in self.project_row_dict:
                self.project_row_dict[key].destroy()

        if not projects:
            return

        # populate rows
        self.project_row_dict = {}
        for project in projects:
            row_num = len(self.project_row_dict)
            self.project_row_dict[project.id] = ProjectRow(
                self.subframe, self, row_num, project)


class ProjectRow():
    def __init__(self, root, toplevel, row_number, project):
        self.toplevel = toplevel
        # Project row
        #   project name
        self.project_name_label = ttk.Label(root, text=project.name)
        self.project_name_label.grid(column=0, row=row_number, padx=5, pady=5)

        # project status
        if SQLitePersistence.get_open_session(project.id):
            label_text = "Tracking"
        else:
            label_text = "Stopped"

        self.project_status_label = ttk.Label(root, text=label_text)
        self.project_status_label.grid(
            column=1, row=row_number, padx=5, pady=5)

        #   rename project
        self.rename_project_button = ttk.Button(
            root, text="Rename", command=lambda: RenameProjectWindow(self))
        self.rename_project_button.grid(
            column=2, row=row_number, padx=5, pady=5)

        #   delete project
        self.delete_project_button = ttk.Button(
            root, text="Delete", command=lambda: self.delete_project(project))
        self.delete_project_button.grid(
            column=3, row=row_number, padx=5, pady=5)

    def destroy(self):
        self.project_name_label.destroy()
        self.project_status_label.destroy()
        self.rename_project_button.destroy()
        self.delete_project_button.destroy()
        del self

    def delete_project(self, project):
        answer = messagebox.askyesno(
            "Delete project",
            "Delete this project and all logged sessions? This is irreversible!",  # NOQA
            icon='warning')

        if answer:
            SQLitePersistence.delete_project(project)
            self.toplevel.update()


class NewProjectWindow(ChildWindow):
    def __init__(self, root):
        super().__init__(root)
        self.title("New project")
        self.root = root

        self.project_name = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self.project_name)
        name_entry.grid(column=0, row=0, padx=5, pady=5, columnspan=2)

        ok_button = ttk.Button(self, text="Ok", command=self.new_project)
        ok_button.grid(column=0, row=1, padx=5, pady=5)

        cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        cancel_button.grid(column=1, row=1, padx=5, pady=5)

    def new_project(self):
        name = self.project_name.get()
        SQLitePersistence.create_project(name)
        self.destroy()
        self.update()
        self.root.update()

    def cancel(self):
        self.destroy()
        self.update()
        self.root.update()


class RenameProjectWindow(ChildWindow):
    def __init__(self, root):
        super().__init__(root)
        self.title("Rename project")
        self.project_name = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self.project_name)
        name_entry.grid(column=0, row=0, padx=5, pady=5, columnspan=2)

        ok_button = ttk.Button(self, text="Ok", command=self.rename)
        ok_button.grid(column=0, row=1, padx=5, pady=5)

        cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        cancel_button.grid(column=1, row=1, padx=5, pady=5)

    def rename(self):
        return self.project_name

    def cancel(self):
        return None
