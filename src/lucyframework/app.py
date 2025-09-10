"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import asyncio
import platform
from pathlib import Path

import pygame

from lucyframework.input import InputManager
from lucyframework.profiler import Profiler
from lucyframework.scene import Scene
from lucyframework.models import VSyncMode
from lucyframework.platform import is_web, get_cpu_info
from lucyframework.path import source_path
from lucyframework.common import DISPLAY_RESOLUTIONS


class App:
    """
    Top-level application class.
    """

    def __init__(self,
            window_size: tuple[int, int],
            target_fps: int = 60,
            vsync_mode: VSyncMode = VSyncMode.NONE,
            clear_color: pygame.typing.ColorLike = (0, 0, 0),
            opengl: bool = False
            ) -> None:
        """
        Parameters
        ----------
        window_size
            Window resolution in pixels.
        target_fps
            Target cap FPS used for the clock, pass 0 to remove the cap.
        vsync_mode
            Vertical sync mode to use at window creation.
        clear_color
            Color to fill the display each frame.
        opengl
            Create the display with OpenGL flags.
        """
        pygame.init()

        self.events = []
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.fps = self.target_fps
        self.dt = 0.0
        self.dt_cap = 0.25
        self.is_running = False

        self.master_volume = 1.0

        self.input = InputManager()

        display_info = pygame.display.Info()
        self.monitor_width = display_info.current_w
        self.monitor_height = display_info.current_h

        self.__window_title = ""

        self.vsync_mode = vsync_mode
        self.clear_color = clear_color
        self.window_width, self.window_height = window_size
        self.create_window(opengl=opengl)

        self.scenes = {}
        self.__current_scene = ""

        self.profiler = Profiler()
        self.profiler.register("fps")
        self.profiler.register("frame")
        self.profiler.register("render")
        self.profiler.register("update")

        # Version & hardware info
        self.python_version = platform.python_version()
        self.pygame_version = pygame.version.ver
        self.sdl_version = ".".join((str(v) for v in pygame.get_sdl_version()))

        self.platform = ("Desktop", "Web")[is_web()]
        self.cpu_info = get_cpu_info()

    @property
    def window_title(self) -> str:
        """ Window title text. """
        return self.__window_title
    
    @window_title.setter
    def window_title(self, new_title: str) -> None:
        self.__window_title = new_title
        pygame.display.set_caption(self.__window_title)

    @property
    def window_frect(self) -> pygame.FRect:
        """ Window dimensions as an FRect. """
        return pygame.FRect(0.0, 0.0, self.window_width, self.window_height)
    
    @property
    def window_rect(self) -> pygame.FRect:
        """ Window dimensions as a Rect. """
        return pygame.Rect(0, 0, self.window_width, self.window_height)

    def create_window(self, opengl: bool = False) -> None:
        """
        Create window with the current resolution.
        
        Parameters
        ----------
        opengl
            Create the display with OpenGL flags.
        """

        flags = 0
        if opengl: flags = pygame.OPENGL | pygame.DOUBLEBUF
        
        self.display = pygame.display.set_mode(
            (self.window_width, self.window_height),
            vsync=self.vsync_mode.value,
            flags=flags
        )

    @property
    def aspect_ratio(self) -> float:
        """ Current aspect ratio of the resolution. """
        return self.window_width / self.window_height
    
    def set_icon(self, filepath: Path | str) -> None:
        """
        Set window icon.
        
        Parameters
        ----------
        filepath
            Path to the icon.
        """
        pygame.display.set_icon(pygame.image.load(source_path(filepath)))

    def get_monitor_aspect_ratio(self) -> str:
        """ Get aspect ratio of the monitor. """

        monitor_tuple = (self.monitor_width, self.monitor_height)

        if monitor_tuple in DISPLAY_RESOLUTIONS["16:9"]:
            return "16:9"
        
        elif monitor_tuple in DISPLAY_RESOLUTIONS["4:3"]:
            return "4:3"

    def get_usable_resolutions(self) -> dict:
        """ Get available resolutions for the current monitor. """

        resolutions = {"16:9": [], "4:3": []}

        for res in DISPLAY_RESOLUTIONS["16:9"]:
            if res[0] <= self.monitor_width and res[1] <= self.monitor_height:
                resolutions["16:9"].append(res)

        for res in DISPLAY_RESOLUTIONS["4:3"]:
            if res[0] <= self.monitor_width and res[1] <= self.monitor_height:
                resolutions["4:3"].append(res)

        return resolutions
    
    def get_max_resolution(self, aspect_ratio: str) -> tuple[int, int]:
        """
        Get maximum usable resolution on the monitor.
        
        Parameters
        ----------
        aspect_ratio
            Aspect ratio of the monitor.
            Use `get_monitor_aspect_ratio`
        """

        resolutions = self.get_usable_resolutions()

        return resolutions[aspect_ratio][-1]

    @property
    def scene(self) -> Scene:
        """ Current active scene. """
        return self.scenes[self.__current_scene]
    
    @scene.setter
    def scene(self, scene_name: str) -> None:
        previous = self.__current_scene
        if previous:
            self.scenes[previous].deactivated()
        
        self.__current_scene = scene_name
        self.scenes[self.__current_scene].activated(previous)
    
    def add_scene(self, scene: Scene):
        """
        Add a scene to the application.

        Parameters
        ----------
        scene
            Scene class to add.
        """
        scene_ = scene()
        self.scenes[scene_.__class__.__name__] = scene_

    def stop(self) -> None:
        """ Stop the application. """
        self.is_running = False

    def run(self) -> None:
        """ Run the application. """

        self.is_running = True

        while self.is_running:
            self.tick()
        
        pygame.quit()

    async def run_async(self) -> None:
        """ Run the application asynchronously for web. """

        self.is_running = True

        while self.is_running:
            self.tick()

            await asyncio.sleep(0)

        pygame.quit()

    def tick(self) -> None:
        """ One game frame. """

        with self.profiler.profile("frame"):

            self.dt = self.clock.tick(self.target_fps) * 0.001
            if (self.dt > self.dt_cap): self.dt = self.dt_cap
            self.fps = self.clock.get_fps()
            if self.fps == float("inf"): self.fps = 0 # Prevent OverflowError for rendering
            self.profiler.accumulate("fps", self.fps)

            with self.profiler.profile("update"):
                self.__update()

            with self.profiler.profile("render"):
                self.__render()

    def __update(self) -> None:
        """ Update the game frame. """

        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                self.stop()

        self.input.update(self.events)

        self.scene.update()

        for entity in self.scene.entities:
            entity.update()

    def __render(self) -> None:
        """ Render the game frame. """

        self.display.fill(self.clear_color)

        self.scene.render_before()

        for entity in self.scene.entities:
            entity.render()

        self.scene.render_after()

        pygame.display.flip()