import os.path
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

def test_cp(service: ConsoleService, fs: FakeFilesystem):
    dir1: str = os.path.join(service._current_path, "data1")
    dir2: str = os.path.join(service._current_path, "data2")
    file: str = os.path.join(service._current_path, "file.txt")
    fs.create_dir(dir1)
    fs.create_dir(dir2)
    fs.create_file(file, contents="test")

    service.cp("data2", "data1", True)
    service.cp("file.txt", "data1")
    assert fs.exists(os.path.join(service._current_path, "data1", "data2"))
    assert fs.exists(os.path.join(service._current_path, "data1", "file.txt"))
    
def test_cp_folder_needs_r(service: ConsoleService, fs: FakeFilesystem):
    dir1: str = os.path.join(service._current_path, "data1")
    dir2: str = os.path.join(service._current_path, "data2")
    fs.create_dir(dir1)
    fs.create_dir(dir2)

    with pytest.raises(OSError, match="Use '-r' to copy directory"):
        service.cp("data1", "data2")
        
    
def test_cp_file_needs_no_r(service: ConsoleService, fs: FakeFilesystem):
    file: str = os.path.join(service._current_path, "file.txt")
    dir: str = os.path.join(service._current_path, "data")
    fs.create_dir(dir)
    fs.create_file(file)
    
    with pytest.raises(OSError, match="Use 'cp' without '-r' to copy file"):
        service.cp("file.txt", "data", True)




