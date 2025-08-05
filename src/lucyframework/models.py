"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from enum import Enum


class VSyncMode(Enum):
    """
    Vertical sync enum.

    Fields
    ------
    NONE
        No vertical sync.
    CONSTANT
        Regular vsync, display is synced with monitor's refresh rate.
    ADAPTIVE
        OpenGL's adaptive sync mode.
    """
    NONE = 0
    CONSTANT = 1
    ADAPTIVE = -1