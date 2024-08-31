class UnmappedData(Exception):
    """Given data doesn't match provided data mapping schema"""

    pass


class WrongGraphContext(Exception):
    """Migration attempted in wrong context (e.g. nodes instead of edges)"""

    pass


class MultipleTransformations(Exception):
    """Multiple transformations given for same set of input fields"""

    pass


class ConflictingConversionFactors(Exception):
    """Multiple different conversion factors given for same migration"""

    pass
