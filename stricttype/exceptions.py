
class ValidationError(Exception):

    def __init__(self, field, message):
        self.field = field
        super(ValidationError, self).__init__(message)
