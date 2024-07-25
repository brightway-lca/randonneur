class ValidationError(Exception):
    """Input data is invalid"""

    pass


class UnmappedData(Exception):
    """Given data doesn't match provided data mapping schema"""

    pass


class WrongGraphContext(Exception):
    """Migration attempted in wrong context (e.g. nodes instead of edges)"""

    pass
