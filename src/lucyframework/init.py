"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import os
from pathlib import Path
import argparse


PYPROJECT_TEMPLATE = """
[project]
name = "{project}"
description = "{desc}"
version = "{version}"
readme = "README.md"
classifiers = [
    "Topic :: Games/Entertainment",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: pygame",
]
dependencies = [
    "pygame-ce",
    "lucyframework",
]
requires-python = ">=3.10"

[project.scripts]
{project}_main = "{project}.__main__:main"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
""".strip()

MAIN_TEMPLATE = """
import pygame
import lucyframework as lucyfw

from {project} import shared
from {project}.scenes.game import Game


def main() -> None:
    app = lucyfw.App(
        (1280, 720),
        target_fps=240,
        vsync_mode=lucyfw.VSyncMode.CONSTANT
    )
    shared.app = app

    app.add_scene(Game)

    app.scene = "Game"

    app.run()


if __name__ == "__main__":
    main()
""".strip()

SCENE_TEMPLATE = """
import pygame
import lucyframework as lucyfw

from {project} import shared


class Game(lucyfw.Scene):
    def __init__(self) -> None:
        super().__init__()

        self.font = pygame.Font(None, 35)

    def update(self) -> None:
        if shared.app.input.key_pressed("escape"):
            shared.app.stop()

    def render_before(self) -> None:
        text_surf = self.font.render(
            "There supposed to be a game here.",
            True,
            (255, 255, 255)
        )
        shared.app.display.blit(
            text_surf,
            (
                shared.app.window_width * 0.5 - text_surf.get_width() * 0.5,
                shared.app.window_height * 0.5 - text_surf.get_height() * 0.5
            )
        )
""".strip()

SHARED_TEMPLATE = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lucyframework import App


app: App | None = None
"""


def mkdir(path: Path) -> None:
    """
    Create directory if not exists.
    
    Parameters
    ----------
    path
        Path to directory
    """

    if os.path.exists(path):
        return
    
    os.mkdir(path)
    print(f"Succesfully created '{path.absolute()}'")


def write(path: Path, content: str, overwrite: bool = False) -> None:
    """
    Create & write to a file.

    Parameters
    ----------
    path
        Path to file
    content
        Content to write
    overwrite
        Overwrite existing file?
    """

    if not overwrite and os.path.exists(path):
        return
    
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
        print(f"Succesfully wrote to '{path.absolute()}'")


def init() -> None:
    """
    Initialize a template lucyframework project.
    """

    parser = argparse.ArgumentParser(
        prog="init",
        description="Initialize a Pygame lucyframework project"
    )

    parser.add_argument(
        "--overwrite",
        help="Overwrite existing files.",
        action="store_true"
    )

    args = parser.parse_args()

    BASE = Path.cwd()

    project_name = BASE.name.lower().strip().replace(" ", "_").replace(".", "_")

    pyproject = PYPROJECT_TEMPLATE
    pyproject = pyproject.replace("{project}", project_name)
    pyproject = pyproject.replace("{desc}", "Pygame game project with lucyframework")
    pyproject = pyproject.replace("{version}", "0.0.1")
    write(BASE / "pyproject.toml", pyproject, args.overwrite)

    mkdir(BASE / "src")
    mkdir(BASE / "src" / project_name)
    mkdir(BASE / "src" / project_name / "scenes")

    main = MAIN_TEMPLATE
    main = main.replace("{project}", project_name)
    write(BASE / "src" / project_name / "__main__.py", main, args.overwrite)

    scene = SCENE_TEMPLATE
    scene = scene.replace("{project}", project_name)
    write(BASE / "src" / project_name / "scenes" / "game.py", scene, args.overwrite)

    shared = SHARED_TEMPLATE
    write(BASE / "src" / project_name / "shared.py", shared, args.overwrite)

    cmd = f"$ uv run {project_name}_main"
    print(
        "\n"
        f"··───────··\n"
        "\n"
        "Your Pygame template project using lucyframework is all set up!\n"
        "\n"
        "You can run your app using:\n"
        f"╭─{'─'*len(cmd)}─╮\n"
        f"│ {cmd} │\n"
        f"╰─{'─'*len(cmd)}─╯\n"
        "\n"
        "Or you can change the entry script name in pyproject.toml file.\n"
        "Have fun developing! 😊"
    )


if __name__ == "__main__":
    init()