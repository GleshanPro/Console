import logging
from logging import Logger
import os, shutil
from os import PathLike, path
import time
from pathlib import Path
from typing import Literal

from src.enums.file_mode import FileReadMode

import typer

import platform

import stat


class ConsoleService():
    def __init__(self, logger: Logger, set_path_function: callable):
        self._logger = logger
        self._current_path: Path = Path('')
        self.set_path_main = set_path_function

        self._current_path_file = Path('src/services/curpath.txt')
        # Current directory is written to file curpath.txt
        current_path_file_data = self._current_path_file.read_text(encoding="utf-8")
        try:
            self.check_path_exists(Path(current_path_file_data))
        except OSError:
            current_path_file_data = ''
            
        if current_path_file_data == '':
            self._current_path = path.curdir
            self._current_path_file.write_text(str(Path().resolve()))
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

    def handle_path(self, path: str, isDir: bool = None) -> Path:
        path_type: str = 'Folder' if isDir else 'File' 

        path = os.path.join(self._current_path, path)
        path = Path(os.path.normpath(path))
        self.check_path_exists(path, path_type)
        
        if isDir != None:
            if isDir and not path.is_dir():
                msg: str = f"You entered {path} is not a directory"
                self._logger.error(msg)
                raise NotADirectoryError(msg)
            if not isDir and path.is_dir(follow_symlinks=True):
                msg: str = f"You entered {path} is not a file"
                self._logger.error(msg)
                raise IsADirectoryError(msg)
        return path

    def ls(self, path: PathLike[str] | str, l: bool = False) -> list[str]:
        path = self.handle_path(path, True)
        self._logger.info(f"Listing {path}")
        if l:
            
            # permissions = stat.filemode(file_stat.st_mode)
            if platform.system() == "Windows":
                 return [f"{stat.filemode(os.stat(entry.absolute()).st_mode)}\t{entry.stat().st_size}\t{time.ctime(entry.stat().st_atime)}\t{entry.name}" + "\n" for entry in path.iterdir()]
            return [f"{stat.filemode(os.stat(entry.absolute()).st_mode)}\t{entry.owner()}\t{entry.group()}\t{entry.stat().st_size}\t{time.ctime(entry.stat().st_atime)}\t{entry.name}" + "\n" for entry in path.iterdir()]
        return [entry.name + "\n" for entry in path.iterdir()]

    def cat(
        self,
        filename: PathLike[str] | str,
        mode: Literal[FileReadMode.string, FileReadMode.bytes] = FileReadMode.string,
    ) -> str | bytes:
        path = self.handle_path(filename, False)
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
            path = self._current_path.parent
        elif path == '~':
            path = Path().home()
        else:
            path = self.handle_path(path, True)

        self._logger.info(f"Changed directory to {path}")
        self._current_path = path
        self.set_path_main(self._current_path)
        self._current_path_file.write_text(str(path))

    def cp(
            self, 
            filename: PathLike[str] | str,
            path: PathLike[str] | str,
            r: bool = False
):
        filename, path = self.handle_path(filename), self.handle_path(path, True)
        
        print("filename: ", filename)
        print("path to (destination): ", path)
        
        try:
            if r:
                # print(os.path.join(path, filename))
                # os.mkdir(os.path.join(path, Path(filename).name))
                shutil.copytree(filename, os.path.join(path, filename), dirs_exist_ok=True)
            else:
                shutil.copy2(filename, path)
        except Exception as e:
            self._logger.error(e)
            raise OSError(e) # Русские буквы...
        
        
        self._logger.info(f"Copied {filename} to {path}")
    
    def mv(
            self, 
            filename: PathLike[str] | str,
            path: PathLike[str] | str,
):
        filename, path = self.handle_path(filename), self.handle_path(path, True)
        
        shutil.move(filename, path) 
        
        self._logger.info(f"Moved {filename} to {path}")
        
    def rm(
            self, 
            filename: PathLike[str] | str,
            r: bool = False
):
        filename = self.handle_path(filename)
        
        try:
            if filename.is_dir():
                shutil.rmtree(filename)
            else:
                os.remove(filename)
        except Exception as e:
            self._logger.error(e)
            raise OSError(e) # Русские буквы...
        
        self._logger.info(f"Removed {filename}")
