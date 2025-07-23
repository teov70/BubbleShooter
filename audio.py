import pygame
import random
from config import *

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = TRACKS
        self.playlist_len = len(TRACKS)
        self.track_num = 0
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=0)

        self.pop_sounds = [pygame.mixer.Sound(p) for p in POP_SOUND_PATHS]
        for s in self.pop_sounds:
            s.set_volume(0.5)

        self.plop_sound = pygame.mixer.Sound(PLOP_SOUND_PATH)
        self.plop_sound.set_volume(1)

        self.NEXT_EVENT = pygame.USEREVENT + 1          # unique id
        pygame.mixer.music.set_endevent(self.NEXT_EVENT)

    # effect helpers ------------------------------------
    def play_pop(self):
        random.choice(self.pop_sounds).play()

    def play_plop(self):
        self.plop_sound.play()

    # music controls ------------------------------------
    def pause(self):  pygame.mixer.music.pause()
    def resume(self): pygame.mixer.music.unpause()

    def is_paused(self):
        return not pygame.mixer.music.get_busy()

    def toggle(self):
        pygame.mixer.music.pause() if pygame.mixer.music.get_busy() else pygame.mixer.music.unpause()

    def next(self):
        self.track_num = (self.track_num + 1) % self.playlist_len
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()
    def previous(self):
        self.track_num = (self.track_num - 1) % self.playlist_len
        pygame.mixer.music.load(self.playlist[self.track_num])
        pygame.mixer.music.play()


