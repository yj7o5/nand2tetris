#!/usr/bin/env python3

from parser import Parser

"""
Handles emitting of raw assembly code for the VM instructions as given by the parser
Not the most wonderful looking piece of code :|

# TODO: modularize such that read/write to a segment from a location / to a location is abstract
"""

class CodeGen:
    REG_SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "Temp"}
    OPERATORS = {"add": "+", "sub": "-", "and": "&", "or": "|"}
    CONIDTIONALS = {"eq": "JEQ", "lt": "JLT", "gt": "JGT"}

    def __init__(self, outstream):
        self.output = None
        self.cmp_counters = {"JEQ": 0, "JGT": 0, "JLT": 0}
        self._ret_count = 0
        self._current_func = None
        self.output = outstream

    def set_file_name(self, name):
        self._curr_filename = name

    def get_next_ret_label(self):
        self._ret_count += 1
        return f"""return_address_{self._ret_count}"""

    def write_init(self):
        self._set_register("SP", 0x100)

        self.write_call("Sys.init", 0)
        pass

    def _get_label(self, label):
        return label if self._current_func == None else f"{self._current_func}${label}"

    def write_label(self, label):
        # each label generates a funcName$label symbol
        label = self._get_label(label)
        self._emit(f"""
({label})""")

    def write_goto(self, label):
        label = self._get_label(label)
        self._emit(f"""
@{label}
0;JMP""")

    def write_if(self, label):
        label = self._get_label(label)
        self._emit_pop("D")
        self._emit(f"""
@{label}
D;JNE""")

    def write_call(self, func_name, argc):
        # call f n
        # - push return-address, LCL, ARG, THIS, THAT
        # - ARG = SP - n - 5
        # - LCL = SP
        # - goto f
        # (return-address) label

        ret_label = self.get_next_ret_label()
        # push return-address
        # self._set_register_pointer("SP", ret_label)
        self._emit(f"""
@{ret_label}
D=A
@SP
A=M
M=D""")
        self._emit_increment("SP")

        # push LCL
        self._set_register_pointer("SP", "LCL")
        self._emit_increment("SP")

        # push ARG
        self._set_register_pointer("SP", "ARG")
        self._emit_increment("SP")

        # push THIS
        self._set_register_pointer("SP", "THIS")
        self._emit_increment("SP")

        # push THAT
        self._set_register_pointer("SP", "THAT")
        self._emit_increment("SP")

        # set ARG = SP-n-5
        self._emit(f"""
@SP
D=M
@{argc}
D=D-A
@5
D=D-A
@ARG
M=D""")

        # set LCL = SP
        self._emit(f"""
@SP
D=M
@LCL
M=D""")

        # self.write_goto(func_name)
        self._emit(f"""
@{func_name}
0;JMP""")

        # self.write_label(ret_label)
        self._emit(f"""
({ret_label})""")

    def write_return(self):
        """
        restoring segments for caller function
        """
        # FRAME = LCL - store in R13 register
        self._emit(f"""
@LCL
D=M
@R13
M=D""")

        # RET = *(FRAME - 5) - store in R14 register
        self._emit_set_reg("R14", 5)

        # *ARG = pop()
        self._emit_pop("D")
        self._emit(f"""
@ARG
A=M
M=D""")

        # SP = ARG+1
        self._emit(f"""
@ARG
D=M+1
@SP
M=D""")

        # THAT = *(FRAME - 1)
        self._emit_set_reg("THAT", 1)

        # THIS = *(FRAME - 2)
        self._emit_set_reg("THIS", 2)

        # ARG = *(FRAME - 3)
        self._emit_set_reg("ARG", 3)

        # LCL = *(FRAME - 4)
        self._emit_set_reg("LCL", 4)

        # goto RET
        self._emit(f"""
@R14
A=M
0;JMP""")


    def _emit_set_reg(self, register, frame_offset):
        self._emit(f"""
@{frame_offset}
D=A
@R13
D=M-D
A=D
D=M
@{register}
M=D""")

    def write_func(self, name, localc):
        self._current_func = name

        # generate (FunctionName) label
        self._emit(f"""
({name})""")
        # init local segments to 0
        for _ in range(localc):
            self._emit(f"""
@SP
A=M
M=0""")
            self._emit_increment("SP")

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

    def _set_register(self, register, value):
        self._emit(f"""
@{value}
D=A
@{register}
M=D""")

    def _set_register_pointer(self, register, pointer):
        self._emit(f"""
@{pointer}
D=M
@{register}
A=M
M=D""")

    def _emit(self, code):
        if not self.output:
            raise Exception("no output file defined")
        self.output.write(code)
