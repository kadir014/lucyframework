"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import pygame

from lucyframework.scene import Scene

from example import shared


class Game(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.font = pygame.Font(None, 35)

    def deactivated(self) -> None:
        print("Game scene is deactivated.")

    def activated(self, previous_scene: str) -> None:
        print(f"Game scene is active! Previous was {previous_scene}.")

    def update(self) -> None:
        if shared.app.input.key_pressed("escape"):
            shared.app.stop()

    def render_before(self) -> None:
        text_surf = self.font.render("There supposed to be a game here.", True, (255, 255, 255))
        shared.app.display.blit(
            text_surf,
            (
                shared.app.window_width * 0.5 - text_surf.get_width() * 0.5,
                shared.app.window_height * 0.5 - text_surf.get_height() * 0.5
            )
        )