"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from lucyframework.app import App
from lucyframework.entity import Entity
from lucyframework.models import VSyncMode
from lucyframework.scene import Scene


__version__ = "0.1.0"


__all__ = (
    __version__,
    "App",
    "Entity",
    "VSyncMode",
    "Scene",
)