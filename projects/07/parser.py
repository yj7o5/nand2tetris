"""
Handles parsing of .vm files
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

    def __init__(self):
        pass

    def has_more_commands(self):
        pass

    def command_type(self):
        pass

    def arg1(self):
        pass

    def arg2(self):
        pass
