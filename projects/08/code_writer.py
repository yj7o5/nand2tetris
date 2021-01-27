#!/usr/bin/env python3

from parser import Parser

"""
Handles emitting of raw assembly code for the VM instructions as given by the parser
"""

class CodeGen:
    REG_SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "Temp"}
    OPERATORS = {"add": "+", "sub": "-", "and": "&", "or": "|"}
    CONIDTIONALS = {"eq": "JEQ", "lt": "JLT", "gt": "JGT"}

    def __init__(self):
        self.output = None
        self.cmp_counters = {"JEQ": 0, "JGT": 0, "JLT": 0}

    def set_file_name(self, name):
        self.close()

        if not name.endswith(".asm"):
            raise Exception("output file name must of type \"asm\"")

        self.output = open(name, "w")
        self._curr_filename = name.split("/")[-1].replace(".asm", "")

    def write_init(self):
        pass

    def write_label(self, label):
        self._emit(f"""
({label})""")

    def write_goto(self, label):
        self._emit(f"""
@{label}
0;JMP""")

    def write_if(self, label):
        self._emit_pop("D")
        self._emit(f"""
@{label}
D;JNE""")

    def write_call(self, func_name, argc):
        pass

    def write_return(self):
        pass

    def write_func(self, func_name, localc):
        pass

    def write_arithmetic(self, cmd):
        unary = ("neg", "not")
        binary = ("add", "sub", "and", "or")
        compares = ("lt", "gt", "eq")

        assert cmd in unary or cmd in binary or cmd in compares

        if cmd in unary:
            self._emit_unary(cmd)

        if cmd in binary:
            self._emit_binary(cmd)

        if cmd in compares:
            self._emit_comparison(cmd)

    def write_push_pop(self, cmd_type, segment, index):
        assert cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP

        if segment == "constant":
            self._emit_constant(index)
        else:
            if cmd_type == Parser.C_PUSH:
                self._emit_push_segment(segment, index)
            else:
                self._emit_pop_segment(segment, index)

    def _emit_push_segment(self, segment, index):
        # load the value into the D register
        if segment == "static":
            # load the value at location {index} into the D register
            self._emit(f"""
@{self._curr_filename}.{index}
D=M""")

        elif segment == "pointer":
            assert index == 0 or index == 1

            segment = "this" if index == 0 else "that"
            reg = CodeGen.REG_SEGMENTS[segment]

            # load the value at register "this" or "that" into D register
            self._emit(f"""
@{reg}
D=M""")

        else:

            reg = CodeGen.REG_SEGMENTS[segment]

            if reg == "Temp":
                reg = index+5
                # load the value at register {index} + offset into D
                self._emit(f"""
@{reg}
D=M""")

            else:
                # load the value from segment {index} and store in D register
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

        # bump the SP pointer
        self._emit_increment("SP")

    def _emit_pop_segment(self, segment, index):
        if segment == "static":
            self._emit_pop("D")
            self._emit(f"""
@{self._curr_filename}.{index}
M=D""")

        elif segment == "pointer":
            assert index == 0 or index == 1

            segment = "this" if index == 0 else "that"
            reg = CodeGen.REG_SEGMENTS[segment]

            # pop stack value into D register
            self._emit_pop("D")

            # set the desire pointer register value to D
            self._emit(f"""
@{reg}
M=D""")

        else:
            reg = CodeGen.REG_SEGMENTS[segment]

            if reg != "Temp":
                # store segment {index} in R13
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

    def _emit_binary(self, op):
        op = CodeGen.OPERATORS[op]

        self._emit_pop("D")
        self._emit_decrement("SP")
        self._emit(f"""
A=M
M=M{op}D""")
        self._emit_increment("SP")

    def _get_cmp_label(self, c):
        cmp = CodeGen.CONIDTIONALS[c]
        self.cmp_counters[cmp] += 1

        label = f"LABEL_{cmp}_{self.cmp_counters[cmp]}"
        return label

    def _emit_comparison(self, cmp):
        jmp = CodeGen.CONIDTIONALS[cmp]
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
