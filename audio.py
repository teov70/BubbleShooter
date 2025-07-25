import pygame
import random
from config import *

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = TRACKS
        self.playlist_len = len(TRACKS)
        self.track_num = 0
        self.loop = -1
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        self.pop_sounds = [pygame.mixer.Sound(p) for p in POP_SOUND_PATHS]
        for s in self.pop_sounds:
            s.set_volume(0.5)

        self.plop_sound = pygame.mixer.Sound(PLOP_SOUND_PATH)
        self.plop_sound.set_volume(1)

        self.click_sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
        self.click_sound.set_volume(0.5)

        self.NEXT_EVENT = pygame.USEREVENT + 1          # unique id
        pygame.mixer.music.set_endevent(self.NEXT_EVENT)

    # effect helpers ------------------------------------
    def play_pop(self):
        random.choice(self.pop_sounds).play()

    def play_plop(self):
        self.plop_sound.play()

    def play_click(self):
        self.click_sound.play()

    # music controls ------------------------------------

    def is_paused(self):
        return not pygame.mixer.music.get_busy()

    def toggle(self):
        pygame.mixer.music.pause() if pygame.mixer.music.get_busy() else pygame.mixer.music.unpause()

    def toggle_loop(self):
        self.loop = -1 if self.loop == 0 else 0

    def next(self):
        self.track_num = (self.track_num + 1) % self.playlist_len
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()
    def previous(self):
        self.track_num = (self.track_num - 1) % self.playlist_len
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()

    def replay(self):
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()


