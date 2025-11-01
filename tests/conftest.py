"""
conftest.py - это файл, где хранятся общие фикстуры

Он автоматически подхватывается pytest (его не нужно импортировать)

Если conftest.py положить в корне tests/, то все тесты в этой папке смогут использовать объявленные там фикстуры.
"""

from logging import Logger
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src.services.console_service import ConsoleService

"""
Fixture - это функция, которая подготавливает контекст для теста:
создаёт объект, настраивает окружение, делает моки, создаёт временные файлы и т.п.

Фикстура вызывается автоматически, достаточно просто указать её имя в параметрах теста.
"""

# "Я подготовил логгер в качестве фикстуры, 
# потому что мне не столь важно, какой логгер у меня будет" - Самир
@pytest.fixture
def logger(mocker: MockerFixture) -> Logger:
    return mocker.Mock()

# Сборка конкретного сервиса
@pytest.fixture
def service(logger: Logger):
    return ConsoleService(logger)

# Патчим Path (pathlib)
@pytest.fixture
def fake_pathlib_path_class(mocker: MockerFixture) -> Mock:
    mock_path_cls = mocker.patch("src.services.console_service.Path")
    return mock_path_cls