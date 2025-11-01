import os.path
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

# def test_cp_for_folder(service: ConsoleService, fs: FakeFilesystem):
#     dir1: str = os.path.join(service._current_path, "data1")
#     dir2: str = os.path.join(service._current_path, "data2")
#     fs.create_dir(dir1)
#     fs.create_dir(dir2)

#     service.cp("data1", "data2", True)

#     assert Path.exists(Path(os.path.join(dir1, dir2)))
    
def test_rm(service: ConsoleService, fs: FakeFilesystem):
    dir: str = os.path.join(service._current_path, "data")
    file: str = os.path.join(service._current_path, "file.txt")
    fs.create_dir(dir)
    fs.create_file(file)
    
    service.rm("data", True, confirm='y')
    service.rm("file.txt", confirm='y')
    
    assert not fs.exists(dir) and not fs.exists(file)
    
# def test_rm_parent(service: ConsoleService, fs: FakeFilesystem):
#     fs.create_dir(service._current_path)
    
#     with pytest.raises(OSError, match="Removing parent directory is forbidden"):
#         service.rm("/")
        
    # with pytest.raises(OSError, match="Removing parent directory is forbidden"):
    #     service.rm("./../")
        
    




