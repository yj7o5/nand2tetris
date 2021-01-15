#!/usr/bin/env python3

import os
from parser import Parser
from symbol_table import SymbolTable

class Assembler:
    def __init__(self):
        self.symboltable = SymbolTable()

    def assemble(self, code):
        self._resolve_symbols(code)

        return "\n".join(self._translate(code))

    def _resolve_symbols(self, input_code):
        input_code.seek(0)
        parser = Parser(input_code)

        address = 0
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type != Parser.L_COMMAND:
                address += 1
            else:
                symbol = parser.symbol()
                self.symboltable.addEntry(symbol, address)

    def _translate(self, input_code):
        input_code.seek(0)
        parser = Parser(input_code)

        variable_address = 16
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == Parser.L_COMMAND:
                continue

            if cmd_type == Parser.C_COMMAND:
                instruction = f'111{parser.comp()}{parser.dest()}{parser.jump()}'

            else:
                symbol = parser.symbol()

                if symbol.isnumeric():
                    n = int(symbol)
                elif self.symboltable.contains(symbol):
                    n = self.symboltable.getaddress(symbol)
                else:
                    n = variable_address
                    self.symboltable.addEntry(symbol, variable_address)
                    variable_address += 1

                instruction = f"{n:016b}"

            yield instruction
