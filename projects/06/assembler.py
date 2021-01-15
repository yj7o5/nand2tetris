#!/usr/bin/env python3

import os
from parser import Parser

class Assembler:
    def __init__(self):
        self.symbols = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 0x4000,
            "KBD": 0x6000
        }

        for i in range(0, 16):
            reg = f"R{i}"
            self.symbols[reg] = i

    def assemble(self, file):
        self._resolve_symbols(file)

        return "\n".join(self._translate(file))

    # first pass resolve symbols
    def _resolve_symbols(self, input_stream):
        input_stream.seek(0)
        parser = Parser(input_stream)

        addr = 0
        while parser.hasMoreCommands():
            parser.advance()

            if parser.command_type() == Parser.L_COMMAND:
                symbol = parser.symbol()
                self.symbols[symbol] = addr
                addr -= 1

            addr += 1

    def _translate(self, input_stream):
        input_stream.seek(0)
        parser = Parser(input_stream)

        var_offset = 16
        while parser.hasMoreCommands():
            parser.advance()
            type = parser.command_type()

            if type == Parser.L_COMMAND:
                continue

            if type == Parser.C_COMMAND:
                instruction = f'111{parser.comp()}{parser.dest()}{parser.jump()}'
            else:
                symbol = parser.symbol()

                if symbol.isnumeric():
                    n = int(symbol)
                elif symbol in self.symbols:
                    n = self.symbols[symbol]
                else:
                    n = var_offset
                    self.symbols[symbol] = n
                    var_offset += 1

                instruction = f"{n:016b}"

            yield instruction
