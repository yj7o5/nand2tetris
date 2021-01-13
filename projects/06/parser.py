#!/usr/bin/env python3

import code as Code

class CommandType:
    A_COMMAND = "a_command"
    C_COMMAND = "c_command"
    L_COMMAND = "l_command"

class Parser:

    def __init__(self, input_stream):
        self._command = None

        self._commands = []

        while (line := input_stream.readline()) != "":
            self._commands.append(line.strip("\n").strip())

    def hasMoreCommands(self):
        return bool(len(self._commands))

    def advance(self):
        if not self.hasMoreCommands():
            return

        self._command = self._commands.pop(0)

        while self._comment(self._command) or self._whitespace(self._command):
            self._command = self._commands.pop(0)

    def _comment(self, cmd):
        if cmd == None:
            return False

        return cmd.strip().startswith("//")

    def _whitespace(self, cmd):
        if cmd == None:
            return False

        return cmd.strip() == ""

    def command_type(self):
        cmd = self._command

        if cmd.startswith("@"):
            return CommandType.A_COMMAND
        elif cmd.startswith("("):
            return CommandType.L_COMMAND
        else:
            return CommandType.C_COMMAND

    def symbol(self):
        c_type = self.command_type()
        cmd = self._command[1:] if c_type == CommandType.A_COMMAND else self._command[1:-1]

        return int(cmd) if cmd.isnumeric() else cmd

    def dest(self):
        return Code.dest(self._command)

    def comp(self):
        return Code.comp(self._command)

    def jump(self):
        return Code.jump(self._command)
