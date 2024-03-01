"""
series module
"""


class Series:
    """
    Series defines the structure for series data
    """

    def __init__(self, name: str, tags: dict, columns: list, values: list[dict]):
        self.name = name
        self.tags = tags
        self.columns = columns
        self.values = values
