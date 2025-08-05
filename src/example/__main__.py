"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from lucyframework.app import App
from lucyframework.models import VSyncMode

from example import shared
from example.scenes.menu import Menu
from example.scenes.game import Game


def main() -> None:
    app = App((1280, 720), target_fps=0, vsync_mode=VSyncMode.CONSTANT)
    shared.app = app

    app.add_scene(Menu)
    app.add_scene(Game)

    app.scene = "Menu"

    app.run()


if __name__ == "__main__":
    main()