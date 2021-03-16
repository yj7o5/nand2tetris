#!/usr/bin/env python3

from parser import Parser
from code_writer import CodeGen

import sys
import os

assert (len(sys.argv) > 1)

def get_source_files(path, is_dir):
    files = []
    if is_dir:
        path = path.rstrip("/")
        for file in os.listdir(path):
            if file.endswith(".vm"):
                files.append(f"{path}/{file}")
    else:

        assert path.endswith(".vm"), f"invalid file; expected .vm file"

        files.append(path)

    return files

def get_output_file(path, is_dir):
    filename = None
    if is_dir:
        name = path.split("/")[-1]
        filename = f"{path}/{name}.asm"
    else:
        filename = path.replace(".vm", ".asm").strip()
    return filename


def compile_file(src, gen):
    parser = Parser(open(src))

    src_filename = src.split("/")[-1].replace(".vm", "")
    code_gen.set_file_name(src_filename)

    while parser.has_more_commands():
        parser.advance()

        cmd_type = parser.command_type()

        if cmd_type == Parser.C_ARITHMETIC:
            code_gen.write_arithmetic(parser.arg1())

        if cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP:
            code_gen.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

        if cmd_type == Parser.C_LABEL:
            code_gen.write_label(parser.arg1())

        if cmd_type == Parser.C_IF:
            code_gen.write_if(parser.arg1())

        if cmd_type == Parser.C_GOTO:
            code_gen.write_goto(parser.arg1())

        if cmd_type == Parser.C_FUNCTION:
            code_gen.write_func(parser.arg1(), parser.arg2())

        if cmd_type == Parser.C_RETURN:
            code_gen.write_return()

        if cmd_type == Parser.C_CALL:
            code_gen.write_call(parser.arg1(), parser.arg2())

path = sys.argv[1]

is_dir = os.path.isdir(path)
output_filename = get_output_file(path, is_dir)
source_files = get_source_files(path, is_dir)

with open(output_filename, "w") as outputfile:
    code_gen = CodeGen(outputfile)

    sys_file = next(filter(lambda x: x.endswith("Sys.vm"), source_files), None)

    if sys_file:
        compile_file(sys_file, code_gen)

    source_files = filter(lambda x: x != sys_file, source_files)

    for source_file in source_files:
        compile_file(source_file, code_gen)

        parser = Parser(open(source_file))

print(f"\033[92m\033[1mCompiled file\033[0m: {output_filename}")

