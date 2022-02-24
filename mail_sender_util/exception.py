class MailSenderException(Exception):
    def __init__(self, error_msg: str, error_code: int) -> None:
        super().__init__(error_msg)
        self.error_code = error_code


class TLSVersionMissingExcpetion(MailSenderException):
    pass


class TLSVersionNotSupported(MailSenderException):
    pass


class MissingParameter(MailSenderException):
    pass
