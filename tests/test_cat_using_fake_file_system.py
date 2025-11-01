import os.path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService


def test_cat_for_nonexisted_file(service: ConsoleService, fs: FakeFilesystem):
    # Arrange
    dir: str = os.path.join(service._current_path, "data")    # Моя программа устроена так, что пути всегда хранятся в абсолютном формате
    fs.create_dir(dir)
    fs.create_file(os.path.join(dir, "existing.txt"), contents="test")

    # Act
    with pytest.raises(FileNotFoundError):
        service.cat(
            filename=os.path.join(dir, "nonexisting.txt"), mode=FileReadMode.string
        )


def test_cat_for_folder(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    fs.create_dir(dir)
    fs.create_file(os.path.join(dir, "existing.txt"), contents="test")

    with pytest.raises(IsADirectoryError):
        service.cat(dir, mode=FileReadMode.string)


def test_cat_file_with_text(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    fs.create_dir(dir)
    content = "test"
    path = os.path.join(dir, "existing.txt")
    fs.create_file(path, contents=content)

    result = service.cat(path, mode=FileReadMode.string)

    assert result == content


def test_cat_file_with_bytes(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    fs.create_dir(dir)
    content = b"test"
    path = os.path.join(dir, "existing.txt")
    fs.create_file(path, contents=content)

    result = service.cat(path, mode=FileReadMode.bytes)
    assert result == content