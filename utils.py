# utils.py
import pygame

def load_bubble_surfaces(color_pairs):
    return {
        color: pygame.image.load(f"assets/sprites/bubble_{name}.png").convert_alpha()
        for color, name in color_pairs
    }