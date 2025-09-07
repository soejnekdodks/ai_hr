from enum import Enum


class InterviewState(str, Enum):
    OPEN = "open"
    FINISHED = "finished"
    CLOSED = "closed"
