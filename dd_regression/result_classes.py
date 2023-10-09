"""This file contains the classes for the results of running the property based test oracle."""


class Passed:
    """The property based tests passed."""
    def __init__(self):
        pass

    def __repr__(self):
        return "| Pass |"

class Failed:
    """The property based tests failed."""
    def __init__(self):
        pass

    def __repr__(self):
        return "| Fail |"

class Inconclusive:
    """The property based tests are inconclusive."""
    def __init__(self):
        pass

    def __repr__(self):
        return "| Inconclusive |"
