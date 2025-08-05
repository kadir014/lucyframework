"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from lucyframework.entity import Entity
    

class Scene:
    """
    Base scene class.

    A scene is a basic state managing all entities.
    """

    def __init__(self) -> None:
        self.camera = pygame.Vector2(0)

        self.entities = []

    def add_entity(self, entity: "Entity") -> None:
        """ Add entity to the scene. """
        self.entities.append(entity)

    def remove_entity(self, entity: "Entity") -> None:
        """ Remove entity from the scene. """
        self.entities.remove(entity)

    def activated(self, previous_scene: str) -> None:
        """
        Scene activated callback.
        
        You can implement this method in your subclass.

        Parameters
        ----------
        previous_scene
            Name of the previous scene, empty if none.
        """

    def deactivated(self) -> None:
        """
        Scene deactivated.
        
        You can implement this method in your subclass.
        """

    def update(self) -> None:
        """
        Scene update callback, this is called before updating all entities.
        
        You can implement this method in your subclass.
        """

    def render_before(self) -> None:
        """
        Scene render callback before drawing entities.
        
        You can implement this method in your subclass.
        """

    def render_after(self) -> None:
        """
        Scene render callback after drawing entities.
        
        You can implement this method in your subclass.
        """