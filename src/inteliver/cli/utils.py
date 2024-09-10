from pathlib import Path

import yaml
from art import text2art
from colorama import Fore, Style
from loguru import logger

from inteliver.version import __template_version__, __version__


def print_inteliver_logo():
    version_colored = (
        Fore.WHITE
        + Style.BRIGHT
        + "\nversion: "
        + Style.RESET_ALL
        + Fore.MAGENTA
        + Style.BRIGHT
        + "v"
        + __version__
        + Style.RESET_ALL
    )
    template_version_colored = (
        Fore.GREEN + Style.BRIGHT + "v" + __template_version__ + Style.RESET_ALL
    )
    project_name = """inteliver\n"""

    logo = (
        Fore.CYAN
        + Style.BRIGHT
        + text2art(project_name, font="tarty1")
        + Style.RESET_ALL
    )
    print(f"{version_colored} 🚀")
    print(logo)
