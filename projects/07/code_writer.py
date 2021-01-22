#!/usr/bin/env python3

from parser import Parser

class CodeGen:
    def __init__(self):
        self.output = None
        self.cmp_counters = {"JEQ": 0, "JGT": 0, "JLT": 0}

    def set_file_name(self, name):
        self.close()

        if not name.endswith(".asm"):
            raise Exception("output file name must of type \"asm\"")

        self.output = open(name, "w")

    def write_arithmetic(self, cmd):
        unary = ("neg", "not")
        binary = ("add", "sub", "and", "or")
        compares = ("lt", "gt", "eq")

        assert(cmd in unary or cmd in binary or cmd in compares)

        if cmd in unary:
            self._emit_unary(cmd)

        if cmd in binary:
            self._emit_binary(cmd)

        if cmd in compares:
            self._emit_comparison(cmd)

    def write_push_pop(self, cmd_type, segment, index):
        assert(cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP)

        if segment == "constant":
            self._emit_constant(index)
        else:
            if cmd_type == Parser.C_PUSH:
                self._emit_push_segment(segment, index)
            else:
                self._emit_pop_segment(segment, index)

    segment_keywords = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "Temp"}
    def _emit_push_segment(self, segment, index):
        reg = CodeGen.segment_keywords[segment]

        if reg == "Temp":
            reg = index+5
            # take value from temp and store in D register
            self._emit(f"""
@{reg}
D=M""")

        else:
            # take value from segment[index] and store in D register
            self._emit(f"""
@{reg}
A=M
D=A
@{index}
A=A+D
D=M""")

        # push onto stack value stored in D register
        self._emit(f"""
@SP
A=M
M=D""")

        self._emit_increment("SP")

    def _emit_pop_segment(self, segment, index):
        reg = CodeGen.segment_keywords[segment]

        if reg != "Temp":
            # store segment[index] in R13
            self._emit(f"""
@{reg}
A=M
D=A
@{index}
D=A+D
@R13
M=D""")

        # pop stack value into D
        self._emit_pop("D")

        if reg == "Temp":
            reg = index + 5
            # for Temp registers
            self._emit(f"""
@{reg}
M=D""")
        else:
            # update segment[index] value
            self._emit(f"""
@R13
A=M
M=D""")

    def _emit_decrement(self, reg):
        self.output.write(f"""
@{reg}
M=M-1""")

    def _emit_increment(self, reg):
        self.output.write(f"""
@{reg}
M=M+1""")

    def _emit_pop(self, register):
        r = register
        self._emit_decrement("SP")
        self._emit(f"""
A=M
{r}=M""")

    def _emit_unary(self, op):

        if op == "not":
            self._emit_decrement("SP")
            self._emit(f"""
A=M
M=!M""")
            self._emit_increment("SP")

        if op == "neg":
            self._emit_pop("D")
            self._emit(f"""
M=!D
M=M+1""")
            self._emit_increment("SP")

    arithmentic_keywords = {"add": "+", "sub": "-", "and": "&", "or": "|"}
    def _emit_binary(self, op):
        op = CodeGen.arithmentic_keywords[op]

        self._emit_pop("D")
        self._emit_decrement("SP")
        self._emit(f"""
A=M
M=M{op}D""")
        self._emit_increment("SP")

    jump_keywords = {"eq": "JEQ", "lt": "JLT", "gt": "JGT"}
    def _get_cmp_label(self, c):
        cmp = CodeGen.jump_keywords[c]
        self.cmp_counters[cmp] += 1

        label = f"LABEL_{cmp}_{self.cmp_counters[cmp]}"
        return label

    def _emit_comparison(self, cmp):
        jmp = CodeGen.jump_keywords[cmp]
        label = self._get_cmp_label(cmp)
        exit_label = f"{label}_EXIT"

        self._emit_binary("sub")
        self._emit_decrement("SP")
        self._emit(f"""
A=M
D=M
@{label}
D;{jmp}
@0
D=A
@SP
A=M
M=D
@{exit_label}
0;JMP
({label})
@0
D=!A
@SP
A=M
M=D
({exit_label})""")
        self._emit_increment("SP")

    def _emit_constant(self, number):
        self.output.write(f"""
@{number}
D=A
@SP
A=M
M=D""")
        self._emit_increment("SP")

    def _emit(self, code):
        self.output.write(code)

    def close(self):
        if self.output:
            self.output.close()

        self.output = None
