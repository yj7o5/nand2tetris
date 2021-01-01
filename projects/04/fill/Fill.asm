// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(INIT)
    @offset
    M=0

(LOOP)
    @offset
    D=M
    @8192
    D=D-A
    @INIT
    D;JGT

    @24576
    D=M

    @BLACK
    D;JGT

    @WHITE
    0;JMP

(BLACK)
    @SCREEN
    D=A
    @offset
    A=D+M
    M=1

    @offset
    M=M+1
    
    @LOOP
    0;JMP

(WHITE)
    @SCREEN
    D=A
    @offset
    A=D+M
    M=0

    @offset
    M=M+1

    @LOOP
    0;JMP
