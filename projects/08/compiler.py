#!/usr/bin/env python3

from parser import Parser
from code_writer import CodeGen

import sys
import os

assert (len(sys.argv) > 1)

path = sys.argv[1]

output_filename = None
source_files = None

if os.path.isdir(path):
    path = path.rstrip("/")

    source_files = [(path + "/" + file) for file in os.listdir(path) if file.endswith(".vm")]

    assert len(source_files) > 0, f"path contains no .vm files: {path}"

    name = path.split("/")[-1]
    output_filename = f"{path}/{name}.asm"

else:

    assert path.endswith(".vm"), f"invalid file; expected .vm file"

    source_files = [path]
    output_filename = path.replace(".vm", ".asm").strip()

with open(output_filename, "w") as outputfile:
    code_gen = CodeGen(outputfile)

    if any([file.endswith("Sys.vm") for file in source_files]):
        code_gen.write_init()

    for source_file in source_files:
        parser = Parser(open(source_file))

        src_filename = source_file.split("/")[-1].replace(".vm", "")
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

print(f"\033[92m\033[1mCompiled file\033[0m: {output_filename}")
