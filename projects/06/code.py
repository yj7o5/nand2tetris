def dest(mneumonic):
    dst, _, _ = _destruct(mneumonic)
    ins = 0

    if dst:
        if "M" in dst:
            ins |= 0x1
        elif "D" in dst:
            ins |= 0x2
        elif "A" in dst:
            ins |= 0x8

    return bin(ins).replace("0b", "").rjust(3, "0")

def comp(mneumonic):
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

    _, cmp, _ = _destruct(mneumonic)

    return instructions[cmp]


def jump(mneumonic):
    _, _, jmp = _destruct(mneumonic)

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

def _destruct(mneumonic):
    mneumonic = mneumonic.strip("")
    """
    if _dest_ is empty, the "=" is omitted
    if _jump_ is empty, the ";" is omitted
    """
    if not "=" in mneumonic:
        p = mneumonic.split(";")
        return (None, p[0].strip(), p[1].strip())
    else:
        p = mneumonic.split("=")
        return (p[0].strip(), p[1].strip(), None)
