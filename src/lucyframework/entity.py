"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lucyframework.scene import Scene


class Entity:
    """
    Base entity class.

    Entity is the simplest game object updated and rendered each frame in a scene.
    """

    def __init__(self, scene: "Scene") -> None:
        """
        Parameters
        ----------
        scene
            Scene to add the entity automatically on initialization.
        """
        self.scene = scene
        self.scene.add_entity(self)

    def kill(self) -> None:
        """ Remove the entity from the scene. """
        self.scene.remove_entity(self)

    def update(self) -> None:
        """
        Entity update callback.
        
        You can implement this method in your subclass.
        """

    def render(self) -> None:
        """
        Entity render callback.
        
        You can implement this method in your subclass.
        """