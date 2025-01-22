import argparse
import sys
from pathlib import Path

import numpy as np
import pygame

import rom
from cpu import CPU
from display import Display
from keyboard import Keyboard
from sound import Sound


fontset = np.array([
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
], dtype=np.uint8)


def parse_args():
    parser = argparse.ArgumentParser(description="Chip-8 Emulator")
    parser.add_argument("rom", type=Path, help="ROM file to load")
    parser.add_argument("--scale", type=int, default=10, help="Screen scale factor (10 by default)")
    parser.add_argument("--clock-speed", type=int, default=500, help="CPU clock speed in Hz (500 Hz by default)")
    return parser.parse_args()


def main():

    args = parse_args()
    rom_path = Path(args.rom)

    if not rom_path.exists():
        print(f"ROM file not found: {str(rom_path)}")
        sys.exit(1)
    elif not rom_path.is_file():
        print(f"Invalid ROM file: {str(rom_path)}")
        sys.exit(1)

    display = Display(args.scale)
    keyboard = Keyboard()
    sound = Sound()
    cpu = CPU(display, keyboard, sound)

    cpu.load_fontset(fontset)

    try:
        rom_data = rom.read_rom(rom_path)
    except rom.RomSizeExceededError as e:
        print(f"ROM size exceeded: {repr(e)}")
        sys.exit(1)

    cpu.load_rom(rom_data)

    clock = pygame.time.Clock()
    TIMER_INTERVAL = 1000 / 60  # millisecond, 60Hz

    # For CPU timers update
    last_timer_update = pygame.time.get_ticks()  # millisecond

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit...")
                running = False
            keyboard.handle_key_event(event)

        # Update CPU timers
        current_time = pygame.time.get_ticks()  # millisecond
        if current_time - last_timer_update >= TIMER_INTERVAL:
            cpu.update_timers()
            last_timer_update = current_time

        # Fetch, decode, and execute an instruction
        inst = cpu.fetch_instruction()
        cpu.decode_and_execute(inst)
        display.update_screen()

        # Limit CPU Clock
        clock.tick(args.clock_speed)

    pygame.quit()


if __name__ == "__main__":
    main()
