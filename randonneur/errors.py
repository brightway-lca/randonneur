class ValidationError(BaseException):
    """Input data is invalid"""

    pass


class UnmappedData(BaseException):
    """Given data doesn't match provided data mapping schema"""

    pass
