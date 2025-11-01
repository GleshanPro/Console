from src.common.config import LOGGING_CONFIG

import logging
import sys
from pathlib import Path

import typer # type: ignore
from typer import Typer, Context

from src.dependencies.container import Container
from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

from typing import Annotated

app = Typer()

_current_path: Path
_shell_mode: bool = False

def set_path(new_path: Path):
    """
    Used in ConsoleService to deliver current path to main to show it in shell.
    """
    global _current_path
    _current_path = new_path


def get_container(ctx: Context) -> Container:
    container = ctx.obj
    if not isinstance(container, Container):
        raise RuntimeError("DI container is not initialized")
    return container


@app.callback()
def main(ctx: Context):
    global _shell_mode

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    command = " ".join(sys.argv[1:])
    if not _shell_mode:
        logger.info(command)
    ctx.obj = Container(
        console_service=ConsoleService(logger=logger, set_path_function=set_path),
    )


@app.command()
def shell(ctx: Context):
    """
    Launch interactive mode
    """
    print("Интерактивная мини-оболочка с командами. \nВыход: exit, quit")

    global _current_path, _shell_mode
    container: Container = get_container(ctx)

    _current_path = container.console_service._current_path
    _shell_mode = True

    logger = container.console_service._logger
    while True:
        try:
            command_input: str = input(f"{str(_current_path)} ")
            if command_input in ["exit", "quit"]:
                break
            
            command_params: list[str] = []
            param: str = ''
            open_quotations: bool = False
            for c in command_input:
                if c in ('"', "'"):
                    open_quotations = not open_quotations
                    continue
                elif c == ' ' and not open_quotations:
                    command_params.append(param)
                    param = ''
                    continue
                param += c
            command_params.append(param)

            logger.info(command_input)
            try:
                app(command_params, standalone_mode=False)
            except Exception as e:
                typer.echo(e)
                logger.error(e)
            
        except OSError as e:
            typer.echo(e)
        except KeyboardInterrupt:
            break


@app.command(help="List all files in a directory")
def ls(
    ctx: Context,
    path: Annotated[str, typer.Argument(
        ..., exists=False, readable=False, help="File to print"
    )] = '.',                                                        # default - current folder.
    long: Annotated[bool, typer.Option("--long", "-l", help="Detailed file listing")] = False
) -> None:
    """
    List all files in a directory.
    :param ctx:   typer context object for imitating di container
    :param path:  path to directory to list
    :param l:     get detailed description of files
    :return: content of directory
    """
    try:
        container: Container = get_container(ctx)
        content = container.console_service.ls(path, long)
        sys.stdout.writelines(content)
    except OSError as e:
        typer.echo(e)


@app.command(help="Cat a file")
def cat(
    ctx: Context,
    filename: str = typer.Argument(
        ..., exists=False, readable=False, help="File to print"
    ),
    mode: Annotated[bool, typer.Option("--bytes, -b", help="Read as bytes")] = False
):
    """
    Cat a file
    :param ctx: typer context object for imitating di container
    :param filename: Filename to cat
    :param mode: Mode to read the file in
    :return:
    """
    try:
        container: Container = get_container(ctx)
        mode_param = FileReadMode.bytes if mode else FileReadMode.string
        data = container.console_service.cat(
            filename,
            mode=mode_param,
        )
        if isinstance(data, bytes):
            sys.stdout.buffer.write(data)
        else:
            sys.stdout.write(data)
    except OSError as e:
        typer.echo(e)


@app.command(help="Change directory")
def cd(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Destination directory")]
):
    """
    Change directory
    :param ctx:   typer context object for imitating di container
    :param path:  path to directory to change
    :return:
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.cd(path)
    except OSError as e:
        typer.echo(e)

@app.command(help="Copy file to destination")
def cp(
    ctx: Context,
    filename: Annotated[str, typer.Argument(help="File path")],
    path: Annotated[str, typer.Argument(help="Destination directory")],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Recursive folder copy")] = False
):
    """
    Copy file to destination
    :param ctx:   typer context object for imitating di container
    :param filename:  path of the file to be copied
    :param path:  destination path
    :param r:     option of recursive copy
    :return:
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.cp(filename, path, recursive)
    except OSError as e:
        typer.echo(e)

@app.command(help="Move file to destination")
def mv(
    ctx: Context,
    filename: Annotated[str, typer.Argument(help="File path")],
    path: Annotated[str, typer.Argument(help="Destination directory")],
):
    """
    Move file to destination
    :param ctx:   typer context object for imitating di container
    :param filename:  path of the file to be moved
    :param path:  destination path
    :return:
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.mv(filename, path)
    except OSError as e:
        typer.echo(e)

@app.command(help="Remove file")
def rm(
    ctx: Context,
    filename: Annotated[str, typer.Argument(help="File path")],
    r: Annotated[bool, typer.Option("--recursive, -r", help="Recursive folder deletion")] = False
):
    """
    Remove file
    :param ctx:   typer context object for imitating di container
    :param filename: path of the file to be removed
    :param r: recursive remove of direction
    :return:
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.rm(filename, r)
    except OSError as e:
        typer.echo(e)


@app.command(help="Archive folder to .zip")
def zip(
    ctx: Context,
    folder: Annotated[str, typer.Argument(help="Path of folder to be archived")],
    archive: Annotated[str, typer.Argument(help="Name of archive to be created")]
):
    """
    Zip folder
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.zip(folder, archive)
    except OSError as e:
        typer.echo(e)


if __name__ == "__main__":
    app()


# Заметки
""" ENV VARS
You could create an env var MY_NAME with
terminal> export MY_NAME="Wade Wilson"

Create an env var MY_NAME in line for this program call
terminal> MY_NAME="Wade Wilson" python main.py

import os
name = os.getenv("MY_NAME", "World")  # second arg is default, it's set if not provided

"""
""" RICH
from rich import print

data = {...}

print(data) - красиво выводит, с цветами

print("[bold red]Alert![/bold red] [green]Portal gun[/green] shooting! :boom:")

---

from rich.console import Console
from rich.table import Table

console = Console()

def main():
    table = Table("Name", "Item")
    table.add_row("Rick", "Portal Gun")
    table.add_row("Morty", "Plumbus")
    console.print(table)


"""
