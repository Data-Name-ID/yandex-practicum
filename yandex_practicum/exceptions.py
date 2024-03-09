class AuthorizationError(Exception):
    def __init__(self) -> None:
        super().__init__(
            (
                'Invalid login or password or 2FA is enabled '
                '(https://id.yandex.ru/security/enter-methods).'
            ),
        )


class APIExceptionError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f'Error: {code}. Message: {message}')
