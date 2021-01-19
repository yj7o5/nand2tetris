#!/usr/bin/env python3

from parser import Parser
from code_writer import CodeGen

code_gen = CodeGen()
code_gen.set_file_name("./StackArithmetic/StackTest/StackTest.asm")

parser = Parser(open("./StackArithmetic/StackTest/StackTest.vm"))

while parser.has_more_commands():
    parser.advance()

    cmd_type = parser.command_type()

    if cmd_type == Parser.C_ARITHMETIC:
        code_gen.write_arithmetic(parser.arg1())

    if cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP:
        code_gen.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

code_gen.close()
