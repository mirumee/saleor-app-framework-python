class BaseWorkerError(Exception):
    def __init__(self, detail, message):
        self.detail = detail
        self.mesage = message


class TransientError(BaseWorkerError):
    """
    Error that can be solved in time, like any connectivity errors, in case
    of a transient error the worker will hald and retry to handle the failing
    event
    """


class NonTransientError(BaseWorkerError):
    """
    Error that will never be solved, like a malformet payload error, those errors
    can be handled by a deadletter callback. The worker will not be halted in
    the case of a non-transient error.
    """


class UnrecognizedEventPayload(NonTransientError):
    pass
