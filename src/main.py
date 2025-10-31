from src.common.config import LOGGING_CONFIG

import logging
import sys
from pathlib import Path

import typer
from typer import Typer, Context

from src.dependencies.container import Container
from src.enums.file_mode import FileReadMode
from src.services.console_service import ConsoleService

from typing import Annotated

app = Typer()

_initialized = False

def get_container(ctx: Context) -> Container:
    container = ctx.obj
    if not isinstance(container, Container):
        raise RuntimeError("DI container is not initialized")
    return container


@app.callback()
def main(ctx: Context):
    global _initialized
    if not _initialized:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger(__name__)
        # logger.info(app.command())
        ctx.obj = Container(
            console_service=ConsoleService(logger=logger),
        )
        _initialized = True
    #print(ctx.obj.console_service._currentPath)


@app.command()
def shell(ctx: Context):
    """
    Launch interactive mode
    """
    print("Интерактивная мини-оболочка с командами. \nВыход: exit, quit")

    container: Container = get_container(ctx)
    while True:
        try:
            command: str = input(f"{str(container.console_service._currentPath)} ")
            if command in ["exit", "quit"]:
                break
            app(command.split(), standalone_mode=False)
        except OSError as e:
            typer.echo(e)
        except KeyboardInterrupt:
            break


@app.command()
def ls(
    ctx: Context,
    path: Annotated[str, typer.Argument(
        ..., exists=False, readable=False, help="File to print"
    )] = '.',                                                        # default - current folder.
    l: bool = False
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
        content = container.console_service.ls(path, l)
        sys.stdout.writelines(content)
    except OSError as e:
        typer.echo(e)


@app.command()
def cat(
    ctx: Context,
    filename: Path = typer.Argument(
        ..., exists=False, readable=False, help="File to print"
    ),
    mode: bool = typer.Option(False, "--bytes", "-b", help="Read as bytes"),
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
        mode = FileReadMode.bytes if mode else FileReadMode.string
        data = container.console_service.cat(
            filename,
            mode=mode,
        )
        if isinstance(data, bytes):
            sys.stdout.buffer.write(data)
        else:
            sys.stdout.write(data)
    except OSError as e:
        typer.echo(e)


@app.command()
def cd(
    ctx: Context,
    path: str           # str?
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

@app.command()
def cp(
    ctx: Context,
    file: str,           # str?
    path: str
):
    """
    Copy file to destination
    :param ctx:   typer context object for imitating di container
    :param file:  path of the file to be copied 
    :param path:  destination path
    :return:
    """
    try:
        container: Container = get_container(ctx)
        container.console_service.cp(file, path)
    except OSError as e:
        typer.echo(e)


if __name__ == "__main__":
    app()
    main()


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