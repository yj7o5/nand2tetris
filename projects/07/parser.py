#!/usr/bin/env python3

"""
Handles parsing of .vm files. Ideally, should have a lexer but an overkill for thethe actual task at hand
"""

class Parser:
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8

    def __init__(self, lines):
        self._command = None
        self._commands = []
        while (line := lines.readline()) != "":
            line = self._prune(line)
            if line:
                self._commands.append(line)

    def _prune(self, line):
        line = line.strip("\n")
        if "//" in line:
            line = line[0:line.index("//")]
        return line.strip()

    def has_more_commands(self):
        return len(self._commands) > 0

    def advance(self):
        if not self.has_more_commands():
            return

        self._command = self._commands.pop(0)

    def command_type(self):
        cmd = self._command

        arth_cmds = ("add", "sub", "neg", "eq", "lt", "gt", "and", "or", "not")
        write_cmds = ("push", "pop")

        assert((cmd in arth_cmds) or (cmd in write_cmds), "unrecognized command: %s" % cmd)

        if cmd in arth_cmds:
            return Parser.C_ARITHMETIC

        if "push" in cmd:
            return Parser.C_PUSH

        if "pop" in cmd:
            return Parser.C_POP

    def arg1(self):
        cmd = self._command
        cmd_type = self.command_type()

        assert(cmd_type != Parser.C_RETURN)

        if cmd_type == Parser.C_ARITHMETIC:
            return cmd

        return cmd.split(" ")[1]

    def arg2(self):
        cmd_type = self.command_type()

        assert(cmd_type in [Parser.C_PUSH, Parser.C_POP, Parser.C_FUNCTION, Parser.C_CALL])

        cmd = self._command
        return int(cmd.split(" ")[-1])
