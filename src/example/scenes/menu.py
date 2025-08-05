"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import pygame

from lucyframework.scene import Scene

from example import shared


class Menu(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.font = pygame.Font(None, 50)

    def deactivated(self) -> None:
        print("Menu scene is deactivated.")

    def activated(self, previous_scene: str) -> None:
        print(f"Menu scene is active! Previous was {previous_scene}.")

    def update(self) -> None:
        shared.app.window_title = f"Example app  -  fps: {round(shared.app.profiler['fps'].avg, 1)}"

        if shared.app.input.key_pressed("escape"):
            shared.app.stop()

        if shared.app.input.key_pressed("space"):
            shared.app.scene = "Game"

    def render_before(self) -> None:
        text_surf = self.font.render("Welcome!", True, (255, 255, 255))
        shared.app.display.blit(
            text_surf,
            (
                shared.app.window_width * 0.5 - text_surf.get_width() * 0.5,
                shared.app.window_height * 0.5 - text_surf.get_height() * 0.5
            )
        )