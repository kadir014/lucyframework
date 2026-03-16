"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

import asyncio
import platform
from pathlib import Path
from time import time

import pygame
import miniprofiler

from lucyframework.input import InputManager
from lucyframework.scene import Scene
from lucyframework.models import VSyncMode
from lucyframework.platform import is_web, get_cpu_info
from lucyframework.path import resolve
from lucyframework.common import DISPLAY_RESOLUTIONS


class App:
    """
    Top-level application class.

    Attributes
    ----------
    target_fps
        Targeted FPS cap
    dt_cap
        Maximum deltatime in seconds
    master_volume
        Global volume multiplier in range [0, 1]
    input
        Input manager
    monitor_width
        Current monitor width in pixels
    monitor_height
        Current monitor height in pixels
    window_width
        Current window width in pixels
    window_height
        Current window height in pixels
    vsync_mode
        Current window vsync mode
    clear_color
        Current clear color
    scenes
        A dictionary of scene names and scene instances
    profiler
        Frame profiler
    """

    def __init__(self,
            window_size: tuple[int, int],
            target_fps: float = 60.0,
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
        self._clock = pygame.time.Clock()

        self.target_fps = target_fps
        self.dt_cap = 0.25

        self._events: list[pygame.Event] = []
        self._fps = self.target_fps
        self._dt = 0.0
        self._is_running = False
        self._start_time = 0.0
        self._time = 0.0

        self.master_volume = 1.0

        self.input = InputManager()

        display_info = pygame.display.Info()
        self.monitor_width = display_info.current_w
        self.monitor_height = display_info.current_h

        self._window_title = ""

        self.vsync_mode = vsync_mode
        self.clear_color = clear_color
        self.window_width, self.window_height = window_size
        self.create_window(opengl=opengl)

        self.scenes: dict[str, Scene] = {}
        self._current_scene = ""

        self.profiler = miniprofiler.Profiler(60)

    @property
    def events(self) -> list[pygame.Event]:
        """ Events polled in the current frame. """
        return self._events
    
    @property
    def fps(self) -> float:
        """ Current FPS. """
        return self._fps
    
    @property
    def dt(self) -> float:
        """ Current delta time in seconds. """
        return self._dt
    
    @property
    def is_running(self) -> bool:
        """ Is the app currently running? """
        return self._is_running
    
    @property
    def time(self) -> float:
        """ Elapsed time since app started running in seconds. """
        return self._time

    @property
    def window_title(self) -> str:
        """ Window title text. """
        return self._window_title
    
    @window_title.setter
    def window_title(self, new_title: str) -> None:
        self._window_title = new_title
        pygame.display.set_caption(self._window_title)

    @property
    def window_frect(self) -> pygame.FRect:
        """ Window geometry as an FRect. """
        pos = pygame.display.get_window_position()
        return pygame.FRect(pos[0], pos[1], self.window_width, self.window_height)
    
    @property
    def window_rect(self) -> pygame.FRect:
        """ Window geometry as a Rect. """
        rect = self.window_frect
        return pygame.Rect(rect.x, rect.y, rect.w, rect.h)

    def create_window(self, opengl: bool = False) -> None:
        """
        Create window with the current resolution.
        
        Parameters
        ----------
        opengl
            Create the display with OpenGL flags.
        """

        flags = 0
        if opengl:
            flags = pygame.OPENGL | pygame.DOUBLEBUF
        
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
        pygame.display.set_icon(pygame.image.load(resolve(filepath)))

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
            Aspect ratio of the monitor, use `get_monitor_aspect_ratio`
        """

        resolutions = self.get_usable_resolutions()

        return resolutions[aspect_ratio][-1]

    @property
    def scene(self) -> Scene:
        """ Current active scene. """
        return self.scenes[self._current_scene]
    
    @scene.setter
    def scene(self, scene_name: str) -> None:
        previous = self._current_scene
        if previous:
            self.scenes[previous].deactivated(scene_name)
        
        self._current_scene = scene_name
        self.scenes[self._current_scene].activated(previous)
    
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
        self._is_running = False

    def run(self) -> None:
        """ Run the application. """

        self._is_running = True
        self._start_time = time()

        while self._is_running:
            self.tick()
        
        pygame.quit()

    async def run_async(self) -> None:
        """ Run the application asynchronously for web. """

        self._is_running = True
        self._start_time = time()

        while self._is_running:
            self.tick()

            await asyncio.sleep(0)

        pygame.quit()

    def tick(self) -> None:
        """ One game frame. """

        with self.profiler.profile("frame"):

            self._dt = self._clock.tick(self.target_fps) * 0.001
            self._dt = min(self._dt, self.dt_cap)

            self._fps = self._clock.get_fps()
            # Prevent OverflowError for rendering
            if self._fps == float("inf"): self._fps = 0

            self._time = time() - self._start_time

            with self.profiler.profile("update"):
                self._update()

            with self.profiler.profile("render"):
                self._render()

    def _update(self) -> None:
        """ Update the game frame. """

        self._events = pygame.event.get()

        for event in self._events:
            if event.type == pygame.QUIT:
                self.stop()

        self.input.update(self.events)

        self.scene.update()

        for entity in self.scene.entities:
            entity.update()

    def _render(self) -> None:
        """ Render the game frame. """

        self.display.fill(self.clear_color)

        self.scene.render_before()

        for entity in self.scene.entities:
            entity.render()

        self.scene.render_after()

        pygame.display.flip()

    @staticmethod
    def get_version_info() -> dict[str, str]:
        """
        Get version information about currnet platform.

        The returned dictionary contains these fields:
        ----------------------------------------------
        python
            Python version (major.minor.patch)
        pygame
            Pygame-CE version (major.minor.patch)
        sdl
            SDL version (major.minor.patch)
        platform
            Whether the app is running on desktop or web
        cpu
            CPU information dict, see `get_cpu_info` for details
        """

        python_version = platform.python_version()
        pygame_version = pygame.version.ver
        sdl_version = ".".join((str(v) for v in pygame.get_sdl_version()))

        curr_platform = ("Desktop", "Web")[is_web()]
        cpu_info = get_cpu_info()

        return {
            "python": python_version,
            "pygame": pygame_version,
            "sdl": sdl_version,
            "platform": curr_platform,
            "cpu": cpu_info
        }