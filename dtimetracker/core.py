from datetime import datetime
import math


class Project:
    def __init__(self, name="Project", id=None):
        self.id = id
        self.name = name


class Session:
    @classmethod
    def from_sql_result(cls, result):
        s = Session(
            result[3],
            id=result[0],
            start=datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S'),
            end=None
        )

        if result[2] is not None:
            s.end = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")

        return s

    def __str__(self):
        return (f'sid: {self.id}, pid: {self.project_id}, start: {self.start}, end: {self.end}')  # NOQA

    def __init__(self, project_id, id=None, start=None, end=None):
        self.id = id
        self.project_id = project_id
        self.start = start
        self.end = end

    def stop(self):
        self.end = datetime.now().replace(microsecond=0)

    # Returns a 2-ple with total hours and minutes
    def compute_duration(self):
        hours = 0
        minutes = 0

        if self.end is None:
            now = datetime.now().replace(microsecond=0)
            hours, minutes = self._compute_time_difference(self.start, now)

        elif isinstance(self.end, datetime):
            hours, minutes = self._compute_time_difference(
                self.start, self.end)

        return (max(hours, 0), max(minutes, 0))


    def get_pretty_duration(self):
        hours, minutes = self.compute_duration()
        return str(hours) + ":" + str(math.floor(minutes))

    def _compute_time_difference(self, start, end):
        difference = end - start
        hours = math.floor(difference.total_seconds()/3600)
        minutes = (difference.total_seconds() % 3600) / 60

        return (hours, minutes)

    @classmethod
    def compute_total_duration(cls, sessions):
        total_hours = 0
        total_minutes = 0
        total_seconds = 0

        for session in sessions:
            d = session.compute_duration()
            total_hours += d[0]
            total_minutes += d[1]

        if total_minutes >= 60:
            total_hours += total_minutes // 60
            total_minutes = total_minutes % 60

        if total_seconds >= 60:
            total_minutes += total_seconds // 60
            total_seconds = total_seconds % 60

        return (int(total_hours), int(total_minutes), int(total_seconds))
