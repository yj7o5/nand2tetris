#!/usr/bin/env python3

from io import StringIO
from parser import Parser, CommandType

import unittest

class TestParser(unittest.TestCase):
    def test_parser_assignment_commands(self):
        code = StringIO("""
            // some comments
            M=1
            M=0
            D=M
            D=D-A
            D;JGT
            D=M
            M=D+M
            D=M
            M=D+M
            M=M+1
            0;JMP
        """)
        instructions = [
            "0111111001000",
            "0101010001000",
            "1110000010000",
            "0010011010000",
            "0001100000001",
            "1110000010000",
            "1000010001000",
            "1110000010000",
            "1000010001000",
            "1110111001000",
            "0101010000111"
        ]

        parser = Parser(code)

        for ins in instructions:
            (cmp, dst, jmp) = (ins[0:7], ins[7:10], ins[10:13])
            parser.advance()

            self.assertEqual(parser.command_type(), CommandType.C_COMMAND, "should be C type command")

            self.assertEqual(parser.comp(), cmp, f"{parser._command} comp mismatch")
            self.assertEqual(parser.dest(), dst, f"{parser._command} dest mismatch")
            self.assertEqual(parser.jump(), jmp, f"{parser._command} jump mismatch")

    def test_parser_symbols(self):
        code = StringIO("""
                @i
                @END
        """)

        parser = Parser(code)

        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.A_COMMAND, "should be A type command")

        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.A_COMMAND, "should be A type command")

    def test_parser_symbol_less(self):
        code = StringIO("""
            (LOOP)
            (END)
        """)

        parser = Parser(code)

        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.L_COMMAND, "should be L type command")

        parser.advance()
        self.assertEqual(parser.command_type(), CommandType.L_COMMAND, "should be L type command")

if __name__ == "__main__":
    unittest.main()
