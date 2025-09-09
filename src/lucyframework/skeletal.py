"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from typing import Optional
from collections.abc import Iterator

from dataclasses import dataclass

import pygame


@dataclass
class CoreBone:
    """
    Core bone structure.
    
    This is a single node which only stores the world transform of a skeletal system.
    """

    position: pygame.Vector2
    angle: float


@dataclass
class Bone:
    """
    Bone structure with local and world transforms.

    This is the building block of skeletal animations.
    """

    name: str
    parent: Optional["CoreBone | Bone"]
    length: float
    local_angle: float

    @property
    def start(self) -> pygame.Vector2:
        """ Start position of the bone in world space. """
        
        if isinstance(self.parent, Bone):
            return self.parent.end
        
        elif isinstance(self.parent, CoreBone):
            return self.parent.position

    @property
    def end(self) -> pygame.Vector2:
        """ End position of the bone in world space. """
        return self.start + pygame.Vector2(self.length, 0.0).rotate(self.angle)
    
    @property
    def center(self) -> pygame.Vector2:
        """ Center position of the bone in world space. """
        return self.start +  pygame.Vector2(self.length * 0.5, 0.0).rotate(self.angle)
    
    @property
    def angle(self) -> float:
        """ Angle of the bone in world space. """

        if isinstance(self.parent, Bone):
            return self.local_angle + self.parent.angle
        
        elif isinstance(self.parent, CoreBone):
            return self.local_angle + self.parent.angle


class SkeletalAnimation:
    """
    TODO
    """

    def __init__(self, skeleton_data: dict) -> None:
        """
        Parameters
        ----------
        skeleton_data
            Base bone structure data.
        """
        self.core = CoreBone(pygame.Vector2(0.0, 0.0), 0.0)

        self.bones: dict[str, Bone] = {}

        for bone_name in skeleton_data:
            bone_data = skeleton_data[bone_name]

            self.bones[bone_name] = (
                Bone(
                    bone_name,
                    bone_data["parent"],
                    bone_data["length"],
                    bone_data["angle"]
                )
            )

        # Fill the parents with actual Bone data
        for bone_name in self.bones:
            bone = self.bones[bone_name]

            if bone.parent is None:
                continue

            elif bone.parent == "core":
                bone.parent = self.core

            else:
                bone.parent = self.bones[bone.parent]
    
    def iter_bones(self) -> Iterator[tuple[str, Bone]]:
        """ Iterate over bones. """

        for bone_name in self.bones:
            bone = self.bones[bone_name]

            yield (bone_name, bone)