from enum import Enum


class SortDirection(Enum):
    """
    Python class that saves sorting-direction constans values. Can be reused in handler functions, sorting, filters, etc.
    """

    ASC = "ASC"
    DESC = "DESC"
