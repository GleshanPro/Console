import logging
from logging import Logger
import os
from os import PathLike, path
import time
from pathlib import Path
from typing import Literal

from src.enums.file_mode import FileReadMode

import typer


class ConsoleService():
    def __init__(self, logger: Logger):
        self._logger = logger
        self._currentPath: Path = Path('')

        self._currentPathFile = Path('src/services/curpath.txt')
        # Current directory is written to file curpath.txt
        currentPathFileData = self._currentPathFile.read_text(encoding="utf-8")

        if currentPathFileData == '':
            self._currentPath = path.curdir
            self._currentPathFile.write_text(str(Path().resolve()))
        else:
            self._currentPath = Path(currentPathFileData)
            
            

    def handlePath(self, path: str, isDir: bool = False) -> str:
        path_type: str = 'Folder' if isDir else 'File' 

        path = Path(os.path.join(self._currentPath, path))
        if not path.exists():
            self._logger.error(f"{path_type} not found: {path}")
            raise FileNotFoundError(path)
        if isDir and not path.is_dir():
            self._logger.error(f"You entered {path} is not a directory")
            raise NotADirectoryError(path)
        if not isDir and path.is_dir(follow_symlinks=True):
            self._logger.error(f"You entered {path} is not a file")
            raise IsADirectoryError(path)
        return path

    def ls(self, path: PathLike[str] | str, l: bool = False) -> list[str]:
        path = self.handlePath(path, True)
        self._logger.info(f"Listing {path}")
        if l:
            return [f"{entry.owner()}\t{entry.group()}\t{entry.stat().st_size}\t{time.ctime(entry.stat().st_atime)}\t{entry.name}" + "\n" for entry in path.iterdir()]
        return [entry.name + "\n" for entry in path.iterdir()]

    def cat(
        self,
        filename: PathLike[str] | str,
        mode: Literal[FileReadMode.string, FileReadMode.bytes] = FileReadMode.string,
    ) -> str | bytes:
        path = self.handlePath(filename)
        try:
            self._logger.info(f"Reading file {filename} in mode {mode}")
            match mode:
                case FileReadMode.string:
                    return path.read_text(encoding="utf-8")
                case FileReadMode.bytes:
                    return path.read_bytes()
        except OSError as e:
            self._logger.exception(f"Error reading {filename}: {e}")
            raise

    def cd(
            self, 
            path: PathLike[str] | str
):
        if path == '..':
            path = self._currentPath.parent
        elif path == '~':
            path = Path().home()
        else:
            path = self.handlePath(path, True)

        self._logger.info(f"Changed directory to {path}")
        self._currentPath = path
        self._currentPathFile.write_text(str(path))

    def cp(
            self, 
            file: PathLike[str] | str,
            path: PathLike[str] | str,
):
        file, path = self.handlePath(file), self.handlePath(path, True)
        
        ...
        
        self._logger.info(f"Copied {file} to {path}")
