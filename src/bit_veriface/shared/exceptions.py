class ApplicationException(Exception):
    """Exception raised for errors in the application layer.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error occurred in application layer"):
        self.message = message
        super().__init__(self.message)


class RepositoryException(Exception):
    """Exception raised for errors in the repository layer.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error occurred in repository operation"):
        self.message = message
        super().__init__(self.message)


class DbRepositoryException(RepositoryException):
    """Exception raised for errors in the repository layer.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error occurred in repository operation"):
        self.message = message
        super().__init__(self.message)


class FileRepositoryException(RepositoryException):
    """Exception raised for errors in the repository layer.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error occurred in repository operation"):
        self.message = message
        super().__init__(self.message)


class ServiceException(Exception):
    """Exception raised for errors in the service layer.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error occurred in service operation"):
        self.message = message
        super().__init__(self.message)
