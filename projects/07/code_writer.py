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
        if cmd in ("neg", "not"):
            self._emit_unary(cmd)

        elif cmd in ("add", "sub", "and", "or"):
            self._emit_binary(cmd)

        elif cmd in ("lt", "gt", "eq"):
            self._emit_comparison(cmd)

        else:
            raise Exception(f"unexpected arithmentic command: {cmd}")

    def write_push_pop(self, cmd_type, segment, index):
        assert(cmd_type == Parser.C_PUSH or cmd_type == Parser.C_POP)

        if segment == "constant":
            self._emit_constant(index)

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

        if op == "neg":
            self.write_push_pop(Parser.C_PUSH, "constant", 2**16)
            self._emit_binary("sub")

    def _emit_binary(self, op):
        d = {"add": "+", "sub": "-", "and": "&", "or": "|"}
        op = d[op]

        self._emit_pop("D")
        self._emit_decrement("SP")
        self._emit(f"""
A=M
M=M{op}D""")
        self._emit_increment("SP")

    cmp_map = {"eq": "JEQ", "lt": "JLT", "gt": "JGT"}
    def _get_cmp_label(self, c):
        cmp = CodeGen.cmp_map[c]
        self.cmp_counters[cmp] += 1

        label = f"LABEL_{cmp}_{self.cmp_counters[cmp]}"
        return label

    def _emit_comparison(self, cmp):
        jmp = CodeGen.cmp_map[cmp]
        label = self._get_cmp_label(cmp)

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
({label})
@-1
D=A
@SP
A=M
M=D""")
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
