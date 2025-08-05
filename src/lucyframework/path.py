"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import sys
import os
from pathlib import Path


def pyinstaller_path() -> str:
    """
    If the project is frozen using PyInstaller, return the bundled app path.
    """

    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    
    else:
        return os.getcwd()


def cxfreeze_path() -> str:
    """
    If the project is frozen using cx_Freeze, return the bundled app path.
    """

    if getattr(sys, "frozen", False):
        return sys.executable

    else:
        return os.getcwd()


def source_path(*children) -> str:
    """
    Get absolute path of a source file (code, asset, etc..) regardless of
    OS and used freezer (PyInstaller & cx_Freeze).

    GAME_USED_FREEZER should be set to identify used freezer.
    """

    if os.environ["GAME_USED_FREEZER"] == "pyinstaller":
        base_path = pyinstaller_path()

    elif os.environ["GAME_USED_FREEZER"] == "cxfreeze":
        base_path = cxfreeze_path()

    else: base_path = os.getcwd()

    return str((Path(base_path) / Path(*children)).resolve())