import os.path
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

def test_cd_for_nonexisted_folder(service: ConsoleService, fs: FakeFilesystem):
    # Arrange
    dir: str = os.path.join(service._current_path, "data")    # Моя программа устроена так, что пути всегда хранятся в абсолютном формате
    fs.create_dir(dir)
    fs.create_dir(os.path.join(dir, "existing"))

    # Act
    with pytest.raises(FileNotFoundError):
        service.cd(
            pathname=os.path.join(dir, "nonexisting")
        )

def test_cd_for_file(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    file: str = os.path.join(dir, "existing.txt")
    fs.create_dir(dir)
    fs.create_file(file, contents="test")

    with pytest.raises(NotADirectoryError):
        service.cd(file)
        
def test_cd_for_folder(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    fs.create_dir(dir)

    service._current_path_file = Path.joinpath(service._current_path, "curpath.txt")    # Подменяю _current_path (можно сказать мокаю, наверное?) чтобы он не пытался искать файл curpath.txt чёрт знает где
    service.cd("data")
    result = service._current_path

    assert result == Path(dir)
    
# def test_cd_parent(service: ConsoleService, fs: FakeFilesystem):
#     parent = service._current_path.parent

#     service._current_path_file = Path.joinpath(service._current_path, "curpath.txt")
#     service.cd("..")
#     result = service._current_path

#     assert result == parent
    


