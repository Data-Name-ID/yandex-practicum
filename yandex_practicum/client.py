from __future__ import annotations

import enum
import http
import json
import pathlib

import requests
import requests.utils

import yandex_practicum.exceptions
import yandex_practicum.models


class YandexEndpoint(enum.Enum):
    AUTH = 'https://passport.yandex.ru/passport?mode=auth'
    ACCOUNTS = 'https://api.passport.yandex.ru/all_accounts'


class APIEndpoint(enum.Enum):
    ME = 'https://practicum.yandex.ru/api/users/me/'
    PROFESSION = 'https://practicum.yandex.ru/api/v2/profiles/{slug}/'


class Client(requests.Session):
    def __init__(
        self,
        login: str,
        password: str,
        dump_file: str | None = None,
    ) -> None:
        super().__init__()

        pathlib.Path('cookies').mkdir(parents=True, exist_ok=True)
        cookies_dump = pathlib.Path('cookies', dump_file or f'{login}.json')

        if cookies_dump.exists():
            with cookies_dump.open('r') as f:
                self.cookies.update(json.load(f))

            return

        self.post(
            YandexEndpoint.AUTH.value,
            data={'login': login, 'passwd': password},
        )

        if not self.is_authorized():
            raise yandex_practicum.exceptions.AuthorizationError

        with cookies_dump.open('w') as f:
            json.dump(requests.utils.dict_from_cookiejar(self.cookies), f)

    def is_authorized(self) -> bool:
        return self.get(YandexEndpoint.ACCOUNTS.value).text != '{}'

    def request(self, *args, **kwargs) -> requests.Response:
        response = super().request(*args, **kwargs)

        if response.status_code != http.HTTPStatus.OK:
            error_message = (
                response.json()
                .get('errors', {})
                .get('message', 'Unknown error.')
            )
            raise yandex_practicum.exceptions.APIExceptionError(
                response.status_code,
                error_message,
            )

        return response

    def get_professions(self) -> list[yandex_practicum.models.Profession]:
        professions = []
        for item in (
            self.get(APIEndpoint.ME.value).json().get('subscriptions', [])
        ):
            profession = yandex_practicum.models.Profession.model_validate(
                item,
            )
            profession.courses = self.get_courses(profession)
            professions.append(profession)

        return professions

    def get_courses(
        self,
        profession: yandex_practicum.models.Profession,
    ) -> list[yandex_practicum.models.Course]:
        return [
            yandex_practicum.models.Course.model_validate(lesson)
            for lesson in self.get(
                APIEndpoint.PROFESSION.value.format(slug=profession.slug),
            )
            .json()
            .get('courses', [])
        ]
