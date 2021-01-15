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
        self.prog_dirs = ["add", "max", "rect", "pong"]

    def test_programs(self):
        # dir is keyword so lets avoid overriding
        for _dir in self.prog_dirs:
            test_files = [file for file in os.listdir(_dir) if file.endswith(".asm")]

            for file in test_files:
                path_to_file = f"{_dir}/{file}"


                assembler = Assembler()
                with open(path_to_file, "r") as program:
                    actual = assembler.assemble(program)

                run_builtin_assembler(path_to_file)
                expected = read_builtin_output(path_to_file)

                actual_lines = actual.split("\n")
                expected_lines = expected.split("\n")

                a, e = len(actual_lines), len(expected_lines)
                self.assertEqual(a, e, f"lines should match {a} != {e}")

                matches = list(zip(expected_lines, actual_lines))

                for i in range(len(matches)):
                    (expected, actual) = matches[i]
                    self.assertEqual(expected, actual, f"should match line {(i+1)} of {(file)}")

    def tearDown(self):
        # dir is keyword so lets avoid overriding
        for _dir in self.prog_dirs:
            files = [file for file in os.listdir(_dir) if file.endswith(".hack")]
            for file in files:
                os.remove(f"{_dir}/{file}")

if __name__ == "__main__":
    unittest.main()
