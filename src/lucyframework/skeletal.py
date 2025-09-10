"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from typing import Optional
from collections.abc import Iterator

from dataclasses import dataclass
from time import perf_counter
from math import pi, cos, fmod

import pygame


@dataclass
class CoreTransform:
    """
    Core world transform of the skeletal system.
    """

    position: pygame.Vector2
    angle: float = 0.0
    scale: float = 1.0


@dataclass
class Bone:
    """
    Bone structure.

    This is the building block of skeletal animations.
    """

    name: str
    parent: Optional["CoreTransform | Bone"]
    local_length: float
    local_angle: float
    local_angle_saved: float = 0.0

    @property
    def start(self) -> pygame.Vector2:
        """ Start position of the bone in world space. """
        
        if isinstance(self.parent, Bone):
            return self.parent.end
        
        elif isinstance(self.parent, CoreTransform):
            return self.parent.position

    @property
    def end(self) -> pygame.Vector2:
        """ End position of the bone in world space. """
        return self.start + pygame.Vector2(self.length, 0.0).rotate(self.angle)
    
    @property
    def center(self) -> pygame.Vector2:
        """ Center position of the bone in world space. """
        return self.start + pygame.Vector2(self.length * 0.5, 0.0).rotate(self.angle)
    
    @property
    def length(self) -> float:
        """ Length of the bone scaled to world space. """

        return self.local_length * self._gather_core_scale()
    
    @property
    def angle(self) -> float:
        """ Angle of the bone transformed to world space. """
        return self.local_angle + self.parent.angle
    
    def _gather_core_scale(self) -> float:
        if isinstance(self.parent, Bone):
            return self.parent._gather_core_scale()

        elif isinstance(self.parent, CoreTransform):
            return self.parent.scale


@dataclass
class BoneAnimationKeyframe:
    time: float
    angle: Optional[float]
    length: Optional[float]

@dataclass
class BoneAnimation:
    bone: Bone
    keyframes: list[BoneAnimationKeyframe]


EASE_IN_OUT_SINE = lambda x: -(cos(x * pi) - 1) / 2

def lerp_angle(a: float, b: float, t: float) -> float:
    """
    Linearly interpolates between two angles (in degrees),
    choosing the shortest path around the circle.
    """
    diff = (b - a + 180) % 360 - 180  # range [-180, 180)
    return a + diff * t


class SkeletalAnimation:
    """
    TODO
    """

    def __init__(self, skeleton_data: dict, animations_data: dict) -> None:
        """
        Parameters
        ----------
        skeleton_data
            Base bone structure data.
        animations_data
            Animations data with bone transform keyframes. 
        """

        self.core = CoreTransform(pygame.Vector2(0.0, 0.0), 0.0)

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

        self.animations: dict[str, list[BoneAnimation]] = {}

        for animation_name in animations_data:
            animation_data = animations_data[animation_name]
            self.animations[animation_name] = list()

            for bone_name in animation_data:
                bone = self.bones[bone_name]

                keyframes = []
                for keyframe_data in animation_data[bone_name]:
                    keyframes.append(
                        BoneAnimationKeyframe(
                            keyframe_data["time"],
                            keyframe_data.get("angle"),
                            keyframe_data.get("length")
                        )
                    )

                self.animations[animation_name].append(
                    BoneAnimation(
                        bone,
                        keyframes
                    )
                )

        self.is_started = False
        self.current_animation = ""
        self.duration = 0.0
        self.transition_duration = 0.2
        self.__start_time = 0.0
        self.__transition_start_time = 0.0
        self.is_looping = False
        self.reverse_on_each_loop = False
        self.reverse = False
        self.previous_animation = ""
        self.transition = False

        self.time_scale = 1.0

        self.__flipped = False

    @property
    def flipped(self) -> bool:
        return self.__flipped
    
    @flipped.setter
    def flipped(self, new_value: bool) -> None:
        if self.__flipped == new_value:
            return

        self.__flipped = new_value        
        self._flip()

    def _flip(self) -> None:
        self.core.angle = 180 - self.core.angle

        for bone_name, bone in self.iter_bones():
           bone.local_angle = 0 - bone.local_angle
           bone.local_angle_saved = bone.local_angle

        for animation in self.animations:
            for bone_animation in self.animations[animation]:
                for keyframe in bone_animation.keyframes:
                    keyframe.angle = 0 - keyframe.angle
    
    def iter_bones(self) -> Iterator[tuple[str, Bone]]:
        """ Iterate over bones. """

        for bone_name in self.bones:
            bone = self.bones[bone_name]

            yield (bone_name, bone)

    def play(self,
            animation: str,
            duration: float,
            loop: bool = False,
            force: bool = False,
            transition: bool = False,
            reverse: bool = False,
            reverse_on_each_loop: bool = False
            ) -> None:
        """
        Start playing the animation.

        Parameters
        ----------
        animation
            Animation name to play.
        duration
            Duration in seconds on how long to play the animation for.
        loop
            Loop the animation once it's finished?
        force
            Force restart the animation.
        transition
            Smooth blending between two animations.
        reverse
            Play the animation reversed.
        reverse_on_each_loop
            Reverse the animation back and forth each loop.
        """
        
        if not self.is_started or force or transition:
            self.is_started = True
            self.transition = transition
            self.old_start_time = self.__start_time
            self.transition_t = (perf_counter() - self.old_start_time)
            self.old_time_scale = self.time_scale
            self.transition_reverse = self.reverse
            self.old_duration = self.duration
            if transition:
                self.__transition_start_time = perf_counter()
            else:
                self.__start_time = perf_counter()
            self.is_looping = loop
            self.previous_animation = self.current_animation
            self.current_animation = animation
            self.duration = duration
            self.reverse = reverse
            self.reverse_on_each_loop = reverse_on_each_loop

            if transition:
                for bone_name, bone in self.iter_bones():
                    bone.local_angle_saved = bone.local_angle

    def stop(self) -> None:
        """ Stop playing the current animation. """
        self.is_started = False

    def update(self) -> None:
        """ Update the skeletal animation. """

        if not self.is_started:
            return

        now = perf_counter()
        start_time = self.__transition_start_time if self.transition else self.__start_time
        t0 = now - start_time
        if not self.transition:
            t0 *= self.time_scale
        animation = self.animations[self.current_animation]

        duration = self.transition_duration if self.transition else self.duration

        if self.reverse:
            t = duration - t0
        else:
            t = t0

        #transition0_t = self.transition_t * self.old_time_scale
        future_start_time = now - fmod(self.transition_duration, self.duration / self.time_scale)
        future_t = now - future_start_time
        future_t *= self.time_scale

        transition1_t = future_t

        #transition1_t = fmod(self.transition_duration, self.duration / self.time_scale)
        t1_reversed = False
        #if self.transition_reverse:
        #    transition0_t = self.old_duration - transition0_t
        #if (round(self.transition_duration / self.duration)-0) % 2 == 1:
        #    transition1_t = self.duration*self.time_scale - transition1_t
            #transition1_t = self.duration- transition1_t
        #    t1_reversed = True

        if t0 >= duration:
            if self.transition:
                self.transition = False
                self.__start_time = perf_counter() - fmod(self.transition_duration, self.duration / self.time_scale)
                self.reverse = t1_reversed

                self.update()

            elif self.is_looping:
                self.__start_time = now

                if self.reverse_on_each_loop:
                    self.reverse = not self.reverse

                self.update()

            else:
                self.stop()
            
            return

        for bone_animation in animation:
            bone = bone_animation.bone

            if self.transition:
                animation_prev = self.animations[self.previous_animation]
                for bone_animation_prev in animation_prev:
                    bone_prev = bone_animation_prev.bone
                    if bone_prev.name == bone.name:
                        break

                #a0k0, a0k1 = self._get_keyframes(bone_animation_prev.keyframes, transition0_t)
                a1k0, a1k1 = self._get_keyframes(bone_animation.keyframes, transition1_t)

                #alpha0 = (transition0_t - a0k0.time) / (a0k1.time - a0k0.time)
                #alpha0 = EASE_IN_OUT_SINE(alpha0)
                #angle0 = lerp_angle(a0k0.angle, a0k1.angle, alpha0)

                angle0 = bone.local_angle_saved

                alpha1 = (transition1_t - a1k0.time) / (a1k1.time - a1k0.time)
                alpha1 = EASE_IN_OUT_SINE(alpha1)
                angle1 = lerp_angle(a1k0.angle, a1k1.angle, alpha1)

                t = (now - start_time) / (self.transition_duration * 1.0)
                t = EASE_IN_OUT_SINE(t)

                bone.local_angle = lerp_angle(angle0, angle1, t)
            else:
                k0, k1 = self._get_keyframes(bone_animation.keyframes, t)

                alpha = (t - k0.time) / (k1.time - k0.time)
                alpha = EASE_IN_OUT_SINE(alpha)

                if k0.angle is not None and k1.angle is not None:
                    bone.local_angle = lerp_angle(k0.angle, k1.angle, alpha)

    def _get_keyframes(self,
            keyframes: list[BoneAnimationKeyframe],
            t: float
            ) -> tuple[BoneAnimationKeyframe, BoneAnimationKeyframe]:
        """ Get the nearest two keyframes around the current animation time """

        for i in range(len(keyframes) - 1):
            k0, k1 = keyframes[i], keyframes[i + 1]
            if k0.time <= t <= k1.time:
                return k0, k1

        # Should never reach here
        #raise Exception("HOW DID THE CODE REACH HERE")

        return keyframes[-2], keyframes[-1]
    
    def _get_blending_keyframes(self,
            keyframes_new: list[BoneAnimationKeyframe],
            keyframes_old: list[BoneAnimationKeyframe],
            t: float
            ) -> tuple[BoneAnimationKeyframe, BoneAnimationKeyframe]:
        
        n = min(len(keyframes_old), len(keyframes_new))

        for i in range(n - 1):
            k0, k1 = keyframes_old[i], keyframes_new[i + 1]
            if k0.time <= t <= k1.time:
                return k0, k1
            
        return keyframes_old[-2], keyframes_new[-1]