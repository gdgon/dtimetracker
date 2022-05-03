from datetime import datetime
import math


class Project:
    def __init__(self, name="Project", id=None):
        self.id = id
        self.name = name


class Session:
    def __str__(self):
        return f'{self.id}, {self.project_id}, {self.start}, {self.end}'

    def __init__(self, project_id, id=None, start=None, end=None):
        self.id = id
        self.project_id = project_id

        if start is None:
            self.start = datetime.now().replace(microsecond=0)
        else:
            self.start = start

        self.end = end

    def end(self):
        self.end = datetime.now().replace(microsecond=0)

    # Returns a 2-ple with total hours and minutes
    def compute_duration(self):
        hours = 0
        minutes = 0

        if self.end is None:
            now = datetime.now().replace(microsecond=0)
            hours, minutes = self._compute_time_difference(self.start, now)

        elif type(self.end) == datetime:
            hours, minutes = self._compute_time_difference(
                self.start, self.end)

        return (max(hours, 0), max(minutes, 0))

    def _compute_time_difference(self, start, end):
        difference = end - start
        hours = math.floor(difference.total_seconds()/3600)
        minutes = (difference.total_seconds() % 3600) / 60

        return (hours, minutes)

    def project_has_no_open_sessions(project):
        pass
