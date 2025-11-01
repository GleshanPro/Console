from pathlib import Path
from unittest.mock import Mock

import pytest

from pytest_mock import MockerFixture

from src.services.console_service import ConsoleService

import os


def test_ls_called_for_nonexisted_folder(
    service: ConsoleService, fake_pathlib_path_class: Mock, mocker: MockerFixture
):
    # Arrange
    fake_path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    fake_path_object.exists.return_value = False
    nonexistent_path: str = "/nonexistent"
    fake_pathlib_path_class.return_value = fake_path_object

    # Act
    # pytest, в строчке выпадет ошибка, проверь, что это FileNotFoundError
    with pytest.raises(FileNotFoundError):
        service.ls(nonexistent_path)

    # Assert
    asserted_path: str = str(Path(os.path.join(service._current_path, nonexistent_path)))
    fake_pathlib_path_class.assert_called_with(asserted_path) # проверь, что передаём в Path этот путь
    fake_path_object.exists.assert_called_once() # проверь, что exists был вызван


def test_ls_called_for_file(
    service: ConsoleService,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    # Arrange
    path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_object.exists.return_value = True
    path_object.is_dir.return_value = False
    not_a_directory_file: str = "file.txt"
    fake_pathlib_path_class.return_value = path_object

    with pytest.raises(NotADirectoryError):
        service.ls(not_a_directory_file)

    asserted_path: str = os.path.join(service._current_path, not_a_directory_file)
    fake_pathlib_path_class.assert_called_with(asserted_path)
    path_object.exists.assert_called_once()


def test_ls_called_for_existing_directory(
    service: ConsoleService,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):

    path_obj = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_obj.exists.return_value = True
    path_obj.is_dir.return_value = True

    entry = mocker.Mock()
    entry.name = "file.txt"
    path_obj.iterdir.return_value = [entry]

    fake_pathlib_path_class.return_value = path_obj

    # Act
    result = service.ls("/fake/dir")

    # Assert
    asserted_path: str = str(Path(os.path.join(service._current_path, "/fake/dir")))
    fake_pathlib_path_class.assert_called_once_with(asserted_path)
    path_obj.exists.assert_called_once_with()
    path_obj.is_dir.assert_called_once_with()
    path_obj.iterdir.assert_called_once_with()
    assert result == ["file.txt\n"]
    
    
def test_long(service: ConsoleService):
    service.ls('.', long=True)