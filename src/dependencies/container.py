from dataclasses import dataclass
from logging import Logger

from src.services.console_service import ConsoleService


@dataclass
class Container:
    console_service: ConsoleService
