from pathlib import Path


class RomSizeExceededError(Exception):
    pass


def read_rom(filename: Path) -> bytes:
    """Reads a ROM file and returns its contents as bytes."""
    MAX_ROM_SIZE = 3584

    with open(filename, "rb") as f:
        rom_data = f.read()
        if len(rom_data) > MAX_ROM_SIZE:
            raise RomSizeExceededError(f"ROM size exceeded {MAX_ROM_SIZE} bytes")
        return rom_data
