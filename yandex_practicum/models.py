from __future__ import annotations

import pydantic


class Lesson(pydantic.BaseModel):
    id: str
    name: str
    has_access: bool
    is_homework: bool
    completion_time: int


class Course(pydantic.BaseModel):
    id: str
    name: str
    preview: str = pydantic.Field(alias='result_picture')
    lessons: list[Lesson] = pydantic.Field(alias='topics')

    @classmethod
    def parse_lessons(
        cls,
        topics_data: list[dict[str, list[dict[str, str | bool | int]]]],
    ) -> list[Lesson]:
        return [
            Lesson(**lesson_data)
            for topic_data in topics_data
            for lesson_data in topic_data['lessons']
        ]

    @pydantic.validator('lessons', pre=True)
    def check_lessons(
        cls,  # noqa: N805
        topics: list[dict[str, list[dict[str, str]]]],
    ) -> list[Lesson]:
        return cls.parse_lessons(topics)


class Profession(pydantic.BaseModel):
    id: str = pydantic.Field(alias='profession_id')
    name: str = pydantic.Field(alias='profession_name')
    slug: str = pydantic.Field(alias='profession_slug')
    courses: list[Course] | None = None
