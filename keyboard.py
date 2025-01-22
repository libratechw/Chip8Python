import pygame


class Keyboard:
    def __init__(self):
        self.key_map = {
            pygame.K_1: 0x1,
            pygame.K_2: 0x2,
            pygame.K_3: 0x3,
            pygame.K_4: 0xC,
            pygame.K_q: 0x4,
            pygame.K_w: 0x5,
            pygame.K_e: 0x6,
            pygame.K_r: 0xD,
            pygame.K_a: 0x7,
            pygame.K_s: 0x8,
            pygame.K_d: 0x9,
            pygame.K_f: 0xE,
            pygame.K_z: 0xA,
            pygame.K_x: 0x0,
            pygame.K_c: 0xB,
            pygame.K_v: 0xF,
        }
        self.keys_pressed = [False] * 16

    def is_key_pressed(self, key_code: int) -> bool:
        return self.keys_pressed[key_code]

    def wait_for_key_press(self) -> int:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in self.key_map:
                        chip8_key = self.key_map[event.key]
                        return chip8_key
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_map:
                chip8_key = self.key_map[event.key]
                self.keys_pressed[chip8_key] = True
        elif event.type == pygame.KEYUP:
            if event.key in self.key_map:
                chip8_key = self.key_map[event.key]
                self.keys_pressed[chip8_key] = False
