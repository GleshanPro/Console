import os.path
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

def test_mv(service: ConsoleService, fs: FakeFilesystem):
    dir1: str = os.path.join(service._current_path, "data1")
    dir2: str = os.path.join(service._current_path, "data2")
    fs.create_dir(dir1)
    fs.create_dir(dir2)

    service.mv("data2", "data1")
    assert fs.exists(os.path.join(service._current_path, "data1", "data2"))
    assert not fs.exists(os.path.join(dir2))
    
