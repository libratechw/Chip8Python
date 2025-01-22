import numpy as np
import pygame


class Display:
    def __init__(self, scale: int = 10):
        self.WIDTH = 64
        self.HEIGHT = 32
        self.scale = scale
        self.screen_buffer = np.zeros((self.WIDTH, self.HEIGHT), dtype=np.uint8)
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH * self.scale, self.HEIGHT * self.scale))
        pygame.display.set_caption("Chip-8 Emulator")

    def clear_screen(self):
        self.screen_buffer.fill(0)

    def update_screen(self):
        pixels = np.zeros((self.WIDTH * self.scale, self.HEIGHT * self.scale), dtype=np.uint8)
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                if self.screen_buffer[x, y]:
                    pixels[
                        x * self.scale : (x + 1) * self.scale, y * self.scale : (y + 1) * self.scale
                    ] = 255

        # Create a surface from the array
        surface = pygame.surfarray.make_surface(pixels)
        self.screen.blit(surface, (0, 0))

        pygame.display.flip()

    def draw_sprite(self, x, y, sprite):
        """
        Draw_sprite draws a sprite on the screen buffer at the given x and y coordinates.
        Returns True if there is a collision, False otherwise.
        """
        collision = False

        for byte_index, sprite_byte in enumerate(sprite):
            for bit_index in range(8):
                px = (x + bit_index) % self.WIDTH
                py = (y + byte_index) % self.HEIGHT
                sprite_bit = (sprite_byte >> (7 - bit_index)) & 1

                if self.screen_buffer[px, py] & sprite_bit:
                    collision = True

                self.screen_buffer[px, py] ^= sprite_bit

        return collision
