#!/usr/bin/env python3

from io import StringIO
from parser import Parser
from assembler import Assembler

import os
import subprocess
import unittest

def run_builtin_assembler(file):
    cmd = ["../../tools/Assembler.sh", file]
    subprocess.check_call(cmd)

def read_builtin_output(file):
    file = file.replace(".asm", ".hack")
    with open(file) as resource:
        content = resource.read()
    return content.strip()

class AssemblerTest(unittest.TestCase):
    def setUp(self):
        # self.prog_dirs = ["add", "./max", "./pong", "./rect"]
        self.prog_dirs = ["add", "max", "rect", "pong"]

    def test_programs(self):
        for _dir in self.prog_dirs:
            test_files = [file for file in os.listdir(_dir) if file.endswith(".asm")]

            for file in test_files:

                path_to_file = f"{_dir}/{file}"

                run_builtin_assembler(path_to_file)

                assembler = Assembler()

                with open(path_to_file, "r") as program:
                    actual = assembler.assemble(program)

                expected = read_builtin_output(path_to_file)

                actual_lines = actual.split("\n")
                expected_lines = expected.split("\n")

                matches = list(zip(expected_lines, actual_lines))

                for i in range(len(matches)):
                    (expected, actual) = matches[i]
                    self.assertEqual(expected, actual, f"should match line {(i+1)} of {(file)}")

    def tearDown(self):
        for _dir in self.prog_dirs:
            files = [file for file in os.listdir(_dir) if file.endswith(".hack")]
            for file in files:
                os.remove(f"{_dir}/{file}")

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

            self.assertEqual(parser.command_type(), Parser.C_COMMAND, "should be C type command")

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
        self.assertEqual(parser.command_type(), Parser.A_COMMAND, "should be A type command")

        parser.advance()
        self.assertEqual(parser.command_type(), Parser.A_COMMAND, "should be A type command")

    def test_parser_symbol_less(self):
        code = StringIO("""
            (LOOP)
            (END)
        """)

        parser = Parser(code)

        parser.advance()
        self.assertEqual(parser.command_type(), Parser.L_COMMAND, "should be L type command")

        parser.advance()
        self.assertEqual(parser.command_type(), Parser.L_COMMAND, "should be L type command")

if __name__ == "__main__":
    unittest.main()
