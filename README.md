# CHIP-8 Emulator

A simple CHIP-8 emulator in Python, developed as a personal learning project.

## Requirements

- Python 3.x (Tested with Python 3.12.8)
- NumPy (for CPU registers emulation)
- Pygame (for display and input handling)

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/libratechw/Chip8Python.git
    ```
2. Navigate to the project directory:
    ```sh
    cd Chip8Python
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the emulator, use the following command:
```sh
python main.py <path_to_rom>
```
Replace `<path_to_rom>` with the path to the CHIP-8 ROM file you want to run.

You can also specify additional options:

- `--scale`: Screen scale factor (default is 10)
- `--clock-speed`: CPU clock speed in Hz (default is 500 Hz)

Example:
```sh
python main.py roms/pong.ch8 --scale 15 --clock-speed 600
```

## License

MIT License.

## Acknowledgements

- [Cowgod's Chip-8 Technical Reference v1.0](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
- [Cowgod's Chip-8 Technical Reference v1.0 (Japanese Version)](https://yukinarit.github.io/cowgod-chip8-tech-reference-ja/)
