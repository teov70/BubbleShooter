import pygame
import random
from config import TRACKS, POP_SOUND_PATHS, PLOP_SOUND_PATH, CLICK_SOUND_PATH

class AudioManager:
    NEXT_EVENT = pygame.USEREVENT + 1
    def __init__(self):
        """Initialise mixer; enter silent mode on failure."""
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print("Audio disabled:", e)
            self.enabled = False
            return

        self.enabled: bool = True
        self.playlist = TRACKS
        self.playlist_len = len(self.playlist)
        self.track_num = 0
        self.loop: bool = True

        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.set_endevent(self.NEXT_EVENT)
        self.play_current()

        self.pop_sounds = [pygame.mixer.Sound(p) for p in POP_SOUND_PATHS]
        for s in self.pop_sounds:
            s.set_volume(0.5)

        self.plop_sound = pygame.mixer.Sound(PLOP_SOUND_PATH); self.plop_sound.set_volume(1)
        self.click_sound = pygame.mixer.Sound(CLICK_SOUND_PATH); self.click_sound.set_volume(0.5)

    @staticmethod
    def _safe(func):
        """Decorator: skip call if audio disabled."""
        def wrapper(self: "AudioManager", *a, **kw):
            if self.enabled:
                return func(self, *a, **kw)
        return wrapper
    
    @_safe
    def play_current(self):
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()

    
    # effect helpers ------------------------------------
    @_safe
    def play_pop(self):
        random.choice(self.pop_sounds).play()

    @_safe
    def play_plop(self):
        self.plop_sound.play()

    @_safe
    def play_click(self):
        self.click_sound.play()

    # music controls ------------------------------------
    @_safe
    def is_paused(self):
        return not pygame.mixer.music.get_busy()

    @_safe
    def toggle(self):
        pygame.mixer.music.pause() if pygame.mixer.music.get_busy() else pygame.mixer.music.unpause()

    @_safe
    def toggle_loop(self):
        self.loop = not self.loop

    @_safe
    def next(self):
        self.track_num = (self.track_num + 1) % self.playlist_len
        self.play_current()
    
    @_safe
    def previous(self):
        self.track_num = (self.track_num - 1) % self.playlist_len
        self.play_current()

    @_safe
    def replay(self):
        self.play_current()

    def __del__(self) -> None:
        if getattr(self, "enabled", False):
            pygame.mixer.quit()

