from typing import Callable

import numpy as np

from display import Display
from keyboard import Keyboard
from sound import Sound


class CPU:
    def __init__(self, display: Display, keyboard: Keyboard, sound: Sound):
        self.memory = np.zeros(4096, dtype=np.uint8)
        self.v = np.zeros(16, dtype=np.uint8)
        self.ip = np.uint16(0)
        self.dt = np.uint8(0)
        self.st = np.uint8(0)
        self.pc = np.uint16(0x200)
        self.sp = np.uint8(0)
        self.stack = np.zeros(16, dtype=np.uint16)
        self.display = display
        self.keyboard = keyboard
        self.sound = sound

        self.first_mapping: dict[int, Callable[[int], None]] = {
            0x0: self.decode_0,
            0x1: self.decode_1,
            0x2: self.decode_2,
            0x3: self.decode_3,
            0x4: self.decode_4,
            0x5: self.decode_5,
            0x6: self.decode_6,
            0x7: self.decode_7,
            0x8: self.decode_8,
            0x9: self.decode_9,
            0xA: self.decode_A,
            0xB: self.decode_B,
            0xC: self.decode_C,
            0xD: self.decode_D,
            0xE: self.decode_E,
            0xF: self.decode_F,
        }

    def load_rom(self, rom_data: bytes):
        """Load the ROM data into memory starting at 0x200"""
        self.memory[0x200 : 0x200 + len(rom_data)] = np.frombuffer(rom_data, dtype=np.uint8)

    def load_fontset(self, fontset: np.ndarray):
        """Load the fontset into memory starting at 0x000"""
        self.memory[0x000:0x050] = fontset

    def fetch_instruction(self) -> int:
        """Fetch the next instruction from memory"""
        inst = (int(self.memory[self.pc]) << 8) | int(self.memory[self.pc + 1])
        self.pc += 2
        return inst

    def decode_and_execute(self, inst: int):
        """Decode and execute the instruction"""
        op_code = (inst & 0xF000) >> 12
        decode_func = self.first_mapping.get(op_code)
        if decode_func:
            decode_func(inst)
        else:
            print(f"Unknown opcode: {inst:04X}")

    def update_timers(self):
        """Update the delay and sound timers"""
        if self.dt > 0:
            self.dt -= 1
        if self.st > 0:
            self.st -= 1
            self.sound.play_beep()
        else:
            self.sound.stop_beep()

    def decode_0(self, inst: int):
        """00E0 - CLS or 00EE - RET"""
        if inst == 0x00E0:
            # 00E0 - CLS: Clear the screen
            self.display.clear_screen()

        elif inst == 0x00EE:
            # 00EE - RET: Return from a subroutine
            self.pc = self.stack[self.sp]
            self.sp -= 1

        else:
            print(f"Unknown opcode: {inst:04X}")

    def decode_1(self, inst: int):
        """1nnn - JP addr: Jump to location nnn"""
        self.pc = np.uint16(inst & 0x0FFF)

    def decode_2(self, inst: int):
        """2nnn - CALL addr: Call subroutine at nnn"""
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = np.uint16(inst & 0x0FFF)

    def decode_3(self, inst: int):
        """3xkk - SE Vx, byte: Skip next instruction if Vx = kk"""
        x = (inst & 0x0F00) >> 8
        kk = inst & 0x00FF
        if self.v[x] == kk:
            self.pc += 2

    def decode_4(self, inst: int):
        """4xkk - SNE Vx, byte: Skip next instruction if Vx != kk"""
        x = (inst & 0x0F00) >> 8
        kk = inst & 0x00FF
        if self.v[x] != kk:
            self.pc += 2

    def decode_5(self, inst: int):
        """5xy0 - SE Vx, Vy: Skip next instruction if Vx = Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2

    def decode_6(self, inst: int):
        """6xkk - LD Vx, byte: Set Vx = kk"""
        x = (inst & 0x0F00) >> 8
        kk = inst & 0x00FF
        self.v[x] = np.uint8(kk)

    def decode_7(self, inst: int):
        """7xkk - ADD Vx, byte: Set Vx = Vx + kk"""
        x = (inst & 0x0F00) >> 8
        kk = inst & 0x00FF
        self.v[x] += kk

    def decode_8_0(self, inst: int):
        """8xy0 - LD Vx, Vy: Set Vx = Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[x] = self.v[y]

    def decode_8_1(self, inst: int):
        """8xy1 - OR Vx, Vy: Set Vx = Vx OR Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[x] |= self.v[y]

    def decode_8_2(self, inst: int):
        """8xy2 - AND Vx, Vy: Set Vx = Vx AND Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[x] &= self.v[y]

    def decode_8_3(self, inst: int):
        """8xy3 - XOR Vx, Vy: Set Vx = Vx XOR Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[x] ^= self.v[y]

    def decode_8_4(self, inst: int):
        """8xy4 - ADD Vx, Vy: Set Vx = Vx + Vy, set VF = carry"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[0xF] = ((self.v[x] + self.v[y]) < self.v[x]).astype(np.uint8)
        self.v[x] += self.v[y]

    def decode_8_5(self, inst: int):
        """8xy5 - SUB Vx, Vy: Set Vx = Vx - Vy, set VF = NOT borrow"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[0xF] = (self.v[x] > self.v[y]).astype(np.uint8)
        self.v[x] -= self.v[y]

    def decode_8_6(self, inst: int):
        """8xy6 - SHR Vx {, Vy}: Set Vx = Vx SHR 1"""
        x = (inst & 0x0F00) >> 8
        self.v[0xF] = self.v[x] & 0x1
        self.v[x] >>= 1

    def decode_8_7(self, inst: int):
        """8xy7 - SUBN Vx, Vy: Set Vx = Vy - Vx, set VF = NOT borrow"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        self.v[0xF] = (self.v[y] > self.v[x]).astype(np.uint8)
        self.v[x] = self.v[y] - self.v[x]

    def decode_8_E(self, inst: int):
        """8xyE - SHL Vx {, Vy}: Set Vx = Vx SHL 1, set VF = carry"""
        x = (inst & 0x0F00) >> 8
        self.v[0xF] = (self.v[x] & 0b1000_0000) >> 7
        self.v[x] <<= 1

    def decode_8(self, inst: int):
        """8xy* - Arithmetic instructions"""
        eight_mapping = {
            0x0: self.decode_8_0,
            0x1: self.decode_8_1,
            0x2: self.decode_8_2,
            0x3: self.decode_8_3,
            0x4: self.decode_8_4,
            0x5: self.decode_8_5,
            0x6: self.decode_8_6,
            0x7: self.decode_8_7,
            0xE: self.decode_8_E,
        }
        decode_func = eight_mapping.get(inst & 0x000F)
        if decode_func:
            decode_func(inst)
        else:
            print(f"Unknown opcode: {inst:04X}")

    def decode_9(self, inst: int):
        """9xy0 - SNE Vx, Vy: Skip next instruction if Vx != Vy"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2

    def decode_A(self, inst: int):
        """Annn - LD I, addr: Set I = nnn"""
        nnn = inst & 0x0FFF
        self.ip = np.uint16(nnn)

    def decode_B(self, inst: int):
        """Bnnn - JP V0, addr: Jump to location nnn + V0"""
        nnn = inst & 0x0FFF
        self.pc = nnn + np.uint16(self.v[0])

    def decode_C(self, inst: int):
        """Cxkk - RND Vx, byte: Set Vx = random byte AND kk"""
        x = (inst & 0x0F00) >> 8
        kk = inst & 0x00FF
        self.v[x] = np.uint8(np.random.randint(0, 256) & kk)

    def decode_D(self, inst: int):
        """Dxyn - DRW Vx, Vy, nibble: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision"""
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        n = inst & 0x000F

        vx = self.v[x]
        vy = self.v[y]
        self.v[0xF] = 0

        sprite = [self.memory[self.ip + i] for i in range(n)]
        if self.display.draw_sprite(vx, vy, sprite):
            self.v[0xF] = 1

    def decode_E(self, inst: int):
        """Ex** - Keyboard instructions"""
        x = (inst & 0x0F00) >> 8
        if inst & 0x00FF == 0x9E:
            # Ex9E - SKP Vx: Skip next instruction if key with the value of Vx is pressed
            if self.keyboard.is_key_pressed(self.v[x]):
                self.pc += 2
        elif inst & 0x00FF == 0xA1:
            # ExA1 - SKNP Vx: Skip next instruction if key with the value of Vx is not pressed
            if not self.keyboard.is_key_pressed(self.v[x]):
                self.pc += 2

    def decode_F_07(self, inst: int):
        """Fx07 - LD Vx, DT: Set Vx = delay timer value"""
        x = (inst & 0x0F00) >> 8
        self.v[x] = self.dt

    def decode_F_0A(self, inst: int):
        """Fx0A - LD Vx, K: Wait for a key press, store the value of the key in Vx"""
        x = (inst & 0x0F00) >> 8
        self.v[x] = self.keyboard.wait_for_key_press()

    def decode_F_15(self, inst: int):
        """Fx15 - LD DT, Vx: Set delay timer = Vx"""
        x = (inst & 0x0F00) >> 8
        self.dt = self.v[x]

    def decode_F_18(self, inst: int):
        """Fx18 - LD ST, Vx: Set sound timer = Vx"""
        x = (inst & 0x0F00) >> 8
        self.st = self.v[x]

    def decode_F_1E(self, inst: int):
        """Fx1E - ADD I, Vx: Set I = I + Vx"""
        x = (inst & 0x0F00) >> 8
        self.ip += self.v[x]

    def decode_F_29(self, inst: int):
        """Fx29 - LD F, Vx: Set I = location of sprite for digit Vx"""
        x = (inst & 0x0F00) >> 8
        self.ip = np.uint16(self.v[x] * 5)

    def decode_F_33(self, inst: int):
        """Fx33 - LD B, Vx: Store BCD representation of Vx in memory locations I, I+1, and I+2"""
        x = (inst & 0x0F00) >> 8
        vx = self.v[x]
        self.memory[self.ip] = vx // 100
        self.memory[self.ip + 1] = (vx // 10) % 10
        self.memory[self.ip + 2] = vx % 10

    def decode_F_55(self, inst: int):
        """Fx55 - LD [I], Vx: Store registers V0 through Vx in memory starting at location I"""
        x = (inst & 0x0F00) >> 8
        self.memory[self.ip : self.ip + x + 1] = self.v[0 : x + 1]

    def decode_F_65(self, inst: int):
        """Fx65 - LD Vx, [I]: Read registers V0 through Vx from memory starting at location I"""
        x = (inst & 0x0F00) >> 8
        self.v[0 : x + 1] = self.memory[self.ip : self.ip + x + 1]

    def decode_F(self, inst: int):
        """Fx** - Miscellaneous instructions"""
        f_mapping = {
            0x07: self.decode_F_07,
            0x0A: self.decode_F_0A,
            0x15: self.decode_F_15,
            0x18: self.decode_F_18,
            0x1E: self.decode_F_1E,
            0x29: self.decode_F_29,
            0x33: self.decode_F_33,
            0x55: self.decode_F_55,
            0x65: self.decode_F_65,
        }
        decode_func = f_mapping.get(inst & 0x00FF)
        if decode_func:
            decode_func(inst)
        else:
            print(f"Unknown opcode: {inst:04X}")
