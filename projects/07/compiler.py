#!/usr/bin/env python3

from parser import Parser
from code_writer import CodeGen

import sys

DEFAULT_FILEPATH = "./MemoryAccess/PointerTest/PointerTest.vm"

def get_io_file():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILEPATH

    assert path.endswith(".vm")

    output_path = path.replace(".vm", ".asm").strip()

    return (path, output_path)

(_input_file, _output_file) = get_io_file()

code_gen = CodeGen()
code_gen.set_file_name(_output_file)

parser = Parser(open(_input_file))

while parser.has_more_commands():
    parser.advance()

    cmd_type = parser.command_type()

    if cmd_type == Parser.C_ARITHMETIC:
        code_gen.write_arithmetic(parser.arg1())

    if cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP:
        code_gen.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

code_gen.close()
