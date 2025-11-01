# import logging
from logging import Logger
import os
import shutil
from os import path
import time
from pathlib import Path
from typing import Literal

from src.enums.file_mode import FileReadMode


import platform

import stat

# from zipfile import ZipFile

from typing import Callable


class ConsoleService():
    def __init__(self, logger: Logger, set_path_function: Callable[[Path], None]):
        self._logger = logger
        self._current_path: Path = Path('')
        self.set_path_main: Callable[[Path], None] = set_path_function

        self._current_path_file = Path('src/services/curpath.txt')
        # Current directory is written to file curpath.txt
        current_path_file_data = self._current_path_file.read_text(encoding="utf-8")
        try:
            self.check_path_exists(Path(current_path_file_data))
        except OSError:
            current_path_file_data = ''

        if current_path_file_data == '':
            self._current_path = Path(path.abspath('.'))
            self._current_path_file.write_text(path.abspath('.'))
        else:
            self._current_path = Path(current_path_file_data)
        self.set_path_main(self._current_path)

    def check_path_exists(self, path, path_type: str = "Folder"):
        """
        Check path existence, raise error
        :param path: path to check
        :path_type: type of path - should be "Folder" or "File". "Folder" by default. It'll be written in error log: "Folder/File not found: {path}"
        """
        if not path.exists():
            msg: str = f"{path_type} not found: {path}"
            self._logger.error(msg)
            raise FileNotFoundError(msg)

    def handle_path(self, pathname: str, isDir: bool = False, checkType: bool = False) -> Path:
        path_type: str = 'Folder' if isDir else 'File'

        pathname = os.path.join(self._current_path, pathname)
        path: Path = Path(os.path.normpath(pathname))
        self.check_path_exists(path, path_type)

        msg: str = ""
        if checkType:
            if isDir and not path.is_dir():
                msg = f"You entered {path} is not a directory"
                self._logger.error(msg)
                raise NotADirectoryError(msg)
            elif not isDir and path.is_dir(follow_symlinks=True):
                msg = f"You entered {path} is not a file"
                self._logger.error(msg)
                raise IsADirectoryError(msg)
        return path

    def ls(self, pathname: str, long: bool = False) -> list[str]:
        path = self.handle_path(pathname, True, True)
        self._logger.info(f"Listing {path}")
        if long:

            # permissions = stat.filemode(file_stat.st_mode)
            if platform.system() == "Windows":
                 return [f"{stat.filemode(os.stat(entry.absolute()).st_mode)}\t{entry.stat().st_size}\t{time.ctime(entry.stat().st_atime)}\t{entry.name}" + "\n" for entry in path.iterdir()]
            return [f"{stat.filemode(os.stat(entry.absolute()).st_mode)}\t{entry.owner()}\t{entry.group()}\t{entry.stat().st_size}\t{time.ctime(entry.stat().st_atime)}\t{entry.name}" + "\n" for entry in path.iterdir()]
        return [entry.name + "\n" for entry in path.iterdir()]

    def cat(
        self,
        filename: str,
        mode: Literal[FileReadMode.string, FileReadMode.bytes] = FileReadMode.string,
    ) -> str | bytes:
        path: Path = self.handle_path(filename, checkType=True)
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
            pathname: str
):
        path: Path
        if pathname == '..':
            path = self._current_path.parent
        elif pathname == '~':
            path = Path().home()
        else:
            path = self.handle_path(pathname, True, True)

        self._logger.info(f"Changed directory to {path}")
        self._current_path = path
        self.set_path_main(self._current_path)
        self._current_path_file.write_text(str(path))

    def cp(
            self,
            filename: str,
            pathname: str,
            r: bool = False
):
        file: Path = self.handle_path(filename)
        path: Path = self.handle_path(pathname, True)

        try:
            if r:
                if not file.is_dir():
                    msg = "Use 'cp' without '--r' to copy file"
                    self._logger.error(msg)
                    raise OSError(msg)
                shutil.copytree(file, os.path.join(path, file.name), dirs_exist_ok=True, symlinks=True)
            else:
                if file.is_dir():
                    msg = "Use '--r' to copy directory"
                    self._logger.error(msg)
                    raise OSError(msg)
                shutil.copy2(file, path)
        except Exception as e:
            self._logger.error(e)
            raise OSError(e) # Русские буквы...

        self._logger.info(f"Copied {file} to {path}")

    def mv(
            self,
            filename: str,
            pathname: str,
):
        file: Path = self.handle_path(filename)
        path: Path = self.handle_path(pathname, True)

        shutil.move(file, path)

        self._logger.info(f"Moved {file} to {path}")

    def rm(
            self,
            filename: str,
            r: bool = False
):
        file: Path = self.handle_path(filename)

        if self._current_path.is_relative_to(file):
            msg = "Removing parent directory is forbidden"
            self._logger.error(msg)
            raise OSError(msg)

        confirm: str = input(f"Are you sure you want to remove {file}? y/n ")
        if confirm != 'y':
            print("Cancel")
            return


        try:
            if file.is_dir():
                shutil.rmtree(file)
            else:
                os.remove(file)
        except Exception as e:
            self._logger.error(e)
            raise OSError(e) # Русские буквы...

        self._logger.info(f"Removed {file}")

    def zip(
            self,
            folder: str,
            archive: str = ''
    ):
        ...

        # new_zip = ZipFile(f"metanit.zip", "w")
