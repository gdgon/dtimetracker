from datetime import datetime
import math


class Project:
    def __init__(self, name):
        self.id = None
        self.name = name


class Session:
    def __init__(self, project):
        self.id = None
        self.project = project
        self.start = datetime.now().replace(microsecond=0)
        self.end = None

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
