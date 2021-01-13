#!/usr/bin/env python3

import re

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

    def _check_command(self, type):
        if self.command_type() != type:
            raise Exception(f"cannot call for non {type} instructions")

    def dest(self):
        self._check_command(CommandType.C_COMMAND)

        dst, _, _ = self._parse_command(self._command)
        ins = 0

        if dst:
            if "M" in dst:
                ins |= 0x1
            elif "D" in dst:
                ins |= 0x2
            elif "A" in dst:
                ins |= 0x8

        return bin(ins).replace("0b", "").rjust(3, "0")

    def comp(self):
        self._check_command(CommandType.C_COMMAND)

        _, cmp, _ = self._parse_command(self._command)

        instructions = {
            "0":    "0101010",
            "1":    "0111111",
            "-1":   "0111010",
            "D":    "0001100",
            "A":    "0110000",
            "M":    "1110000",
            "!D":   "0001101",
            "!A":   "0110001",
            "!M":   "1110001",
            "-D":   "0001111",
            "-A":   "0110011",
            "-M":   "1110011",
            "D+1":  "0011111",
            "A+1":  "0110111",
            "M+1":  "1110111",
            "D-1":  "0001110",
            "A-1":  "0110010",
            "M-1":  "1110010",
            "D+A":  "0000010",
            "D+M":  "1000010",
            "D-A":  "0010011",
            "D-M":  "1010011",
            "A-D":  "0000111",
            "M-D":  "1000111",
            "D&A":  "0000000",
            "D&M":  "1000000",
            "D|A":  "0010101",
            "D|M":  "1010101"
        }

        return instructions[cmp]

    def jump(self):
        self._check_command(CommandType.C_COMMAND)

        _, _, jmp = self._parse_command(self._command)

        nojump = "000"
        instructions = {
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }

        return instructions[jmp] if jmp in instructions else nojump

    def _parse_command(self, cmd):
        cmd = cmd.strip("")
        """
        if _dest_ is empty, the "=" is omitted
        if _jump_ is empty, the ";" is omitted
        """
        if not "=" in cmd:
            p = cmd.split(";")
            return (None, p[0].strip(), p[1].strip())
        else:
            p = cmd.split("=")
            return (p[0].strip(), p[1].strip(), None)
